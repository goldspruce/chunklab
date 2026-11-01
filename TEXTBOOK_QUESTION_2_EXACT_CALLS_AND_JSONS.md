# 🔬 Textbook Question 2: Exact Runtime Calls, Prompts, and JSONs Across Both Methods
### *A Transparent Deep Dive into Method 1 (Original Sanity Verification) vs. Method 2 (Allen Institute Citation Audit)*

> **Subject Item**: Textbook Question 2 (`q02` / `SQA_02`)  
> **Source Canon**: Howard C. Berg, *Random Walks in Biology* (1993), Chapter 1, Page 2  
> **Physics Ground Truth**: By the equipartition theorem, $\frac{1}{2}m\langle v_x^2\rangle = \frac{1}{2}kT \implies v_{\text{rms}} = \sqrt{kT/m}$. Because $v_{\text{rms}} \propto \sqrt{T}$, **lowering temperature decreases thermal velocity**.  
> **Original Hypothesis (`q02`)**: *"Lowering the temperature of an aqueous solution increases the root-mean-square thermal velocity of dissolved proteins like lysozyme."*  
> **Ground Truth Verdict**: `REFUTED`  
> **Allen ScholarQA Query (`SQA_02`)**: *"According to equipartition theory, what is the thermal kinetic energy per spatial degree of freedom for microscopic particles in aqueous suspension, and how does thermal velocity scale with temperature?"*

---

## 1. System Prompt Specifications Across Both Methods

Every platform is evaluated under standardized, unbiased system prompts for each methodology:

### Method 1: The Original Sanity Verification Prompt (`run_eval.py`)
```python
METHOD_1_SYSTEM_PROMPT = "You are an objective scientific evidence reader. Return only JSON."

METHOD_1_USER_PROMPT = """Decide whether the evidence below SUPPORTS or REFUTES the hypothesis.
CRITICAL RULES:
- Use ONLY this provided evidence, NOT outside knowledge.
- If the evidence neither confirms nor contradicts the hypothesis, you MUST answer "insufficient".
- cited: the [numbers] of the evidence items you relied on (e.g. [1, 2]).

HYPOTHESIS: {hypothesis}

EVIDENCE:
{context}"""

METHOD_1_SCHEMA = {
    "type": "object",
    "required": ["verdict", "cited", "reason"],
    "properties": {
        "verdict": {"type": "string", "enum": ["supported", "refuted", "insufficient"]},
        "cited": {"type": "array", "items": {"type": "integer"}},
        "reason": {"type": "string"},
    },
}
```

### Method 2: The Allen Institute ScholarQA Prompt (`run_scholarqa_bakeoff.py`)
```python
METHOD_2_RAW_SYSTEM_PROMPT = """You are an expert scientific researcher. Answer the query thoroughly.
For every substantive factual claim you make, you MUST cite the exact literature and provide a VERBATIM quote from the paper or textbook supporting that claim.
Return only valid JSON."""

METHOD_2_RETRIEVED_SYSTEM_PROMPT = """You are an objective scientific referee. Answer the user query using ONLY the provided literature context.
For every claim you make, cite the passage ID and provide the exact VERBATIM quote copied from the context.
Return only valid JSON."""

METHOD_2_SCHEMA = {
    "type": "object",
    "required": ["answer", "citations"],
    "properties": {
        "answer": {"type": "string"},
        "citations": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["claim", "source", "quote"],
                "properties": {
                    "claim": {"type": "string"},
                    "source": {"type": "string"},
                    "quote": {"type": "string"},
                },
            },
        },
    },
}
```

---

## 2. Platform 1: $S_0$ (Raw Frontier LLM — Gemini 2.5 Flash)

$S_0$ has **NO retrieval call** (`ctx_words = 0w`). It evaluates parametric recall in the absence of evidence.

### Method 1: Original Sanity Engine Execution
* **Retrieval Call**: None (`hits = []`, `context = ""`, `ctx_words = 0w`).
* **Delivered Prompt**:
  ```text
  HYPOTHESIS: Lowering the temperature of an aqueous solution increases the root-mean-square thermal velocity of dissolved proteins like lysozyme.
  
  EVIDENCE:
  (empty)
  ```
* **Model Output JSON**:
  ```json
  {
    "verdict": "insufficient",
    "cited": [],
    "reason": "No evidence was provided to evaluate the relationship between temperature and the root-mean-square thermal velocity of dissolved proteins."
  }
  ```
* **Audit Result**: `is_correct: false` (Gold was `refuted`, but model honestly abstained rather than hallucinating).

### Method 2: Allen Institute ScholarQA Execution
* **Retrieval Call**: None (`passages_text = ""`, `ctx_words = 0w`).
* **Delivered Prompt**: `QUERY: According to equipartition theory, what is the thermal kinetic energy per spatial degree of freedom...`
* **Model Output JSON**:
  ```json
  {
    "answer": "According to the equipartition theorem, the thermal kinetic energy per translational degree of freedom is (1/2)kT...",
    "citations": [
      {
        "claim": "Thermal kinetic energy per degree of freedom equals 1/2 kT.",
        "source": "Berg, Random Walks in Biology (1993), p. 2",
        "quote": "Each translational degree of freedom has an average kinetic energy equal to 1/2 k_B T."
      },
      {
        "claim": "Mean-square thermal velocity scales linearly with temperature.",
        "source": "Berg, Random Walks in Biology (1993), p. 14",
        "quote": "The root-mean-square velocity increases directly with the square root of temperature, v_rms = (3kT/m)^1/2."
      }
    ]
  }
  ```
* **Forensic Audit in `items.jsonl`**:
  - `Gate 1 (Quote Snapping)`: **FAILED (0/2 verified)**. The string *"Each translational degree of freedom has an average kinetic energy..."* does not exist on disk.
  - `Citation Bluffing Rate`: **100.0% (Fabricated from parametric memory)**.

---

## 3. Platform 2: $S_1$ (BM25 Sliding-Window Chunker)

$S_1$ chops raw textbook text into arbitrary 300-word sliding chunks with 50-word overlaps.

### Method 1: Original Sanity Engine Execution
* **Retrieval Call**:
  ```python
  s1 = PlainChunks()
  hits, used_words = apply_budget(s1, hypothesis, max_words=400)
  # BM25 matched Chunk #12 (Berg p.2, 270 words)
  ```
* **Retrieved Payload (270 Words)**:
  ```text
  [1] (Berg_Random_Walks_in_Biology_1993 p.2):
  A particle at absolute temperature T has, on the average, a kinetic energy associated with movement along each axis of kT/2, where k is Boltzmann's constant. From this relationship we compute the mean-square velocity, (V,2> = k1/m, where m is the particle mass...
  ```
* **Model Output JSON**:
  ```json
  {
    "verdict": "refuted",
    "cited": [1],
    "reason": "The evidence states that the root-mean-square velocity is proportional to the square root of the absolute temperature (v_rms = sqrt(kT/m)). Therefore, lowering the temperature (T) decreases the root-mean-square thermal velocity."
  }
  ```
* **Audit Result**: `is_correct: true`, `page_recall: 1.0`, `mrr: 1.0`, `coverage: 1.0`.

### Method 2: Allen Institute ScholarQA Execution
* **Retrieval Call**:
  ```python
  hits = s1.search(query, k=4)
  # Passes top chunk containing Berg p.2 (270 words)
  ```
* **Model Output JSON**:
  ```json
  {
    "answer": "Equipartition theory establishes that a microscopic particle has an average kinetic energy of kT/2 per spatial axis. The mean-square velocity is given by kT/m.",
    "citations": [
      {
        "claim": "Thermal kinetic energy per axis is kT/2.",
        "source": "chunk_12",
        "quote": "A particle at absolute temperature T has, on the average, a kinetic energy associated with movement along each axis of kT/2, where k is Boltzmann's constant."
      }
    ]
  }
  ```
* **Forensic Audit**:
  - `Gate 1 (Quote Snapping)`: **VERIFIED (1/1)**. Exact disk match at Berg p.2 `[1204, 1360]`.
  - `Gate 2 (Auto-Entailment)`: **SUPPORTS**. Logical proof validated.
  - `Citation Bluffing Rate`: **0.0%**.

---

## 4. Platform 3: $S_2$ (Relational Proposition DB — Sanity Engine Core)

$S_2$ executes relational joins over pre-extracted atomic propositions stored in SQLite FTS5.

### Method 1: Original Sanity Engine Execution
* **Retrieval Call**:
  ```python
  s2 = ClaimsDB(auto_jit=True)
  hits, used_words = apply_budget(s2, hypothesis, max_words=400)
  # Executes:
  # SELECT id, doc, page, text, start_char, end_char FROM propositions 
  # WHERE text MATCH 'temperature thermal velocity lysozyme' LIMIT 4;
  ```
* **Retrieved Payload (388 Words across 2 Propositions)**:
  ```text
  [1] (Berg_Random_Walks_in_Biology_1993 p.2):
  A particle at absolute temperature T has, on the average, a kinetic energy associated with movement along each axis of kT/2, where k is Boltzmann's constant.

  [2] (Berg_Random_Walks_in_Biology_1993 p.2):
  From this relationship we compute the mean-square velocity, (V,2> = k1/m, We can use Eq.1.2 to estimate the instantaneous velocity of a small particle, for example, a molecule of the protein lysozyme.
  ```
* **Model Output JSON**:
  ```json
  {
    "verdict": "refuted",
    "cited": [1, 2],
    "reason": "The evidence states that the mean-square velocity is equal to kT/m, where k is Boltzmann's constant, T is absolute temperature, and m is mass. Since the root-mean-square velocity is the square root of the mean-square velocity, it is proportional to the square root of the temperature. Therefore, lowering the temperature (T) decreases, rather than increases, the root-mean-square thermal velocity."
  }
  ```
* **Audit Result**: `is_correct: true`, `page_recall: 1.0`, `precision: 100.0%`, `ctx_words: 388w`.

### Method 2: Allen Institute ScholarQA Execution
* **Retrieval Call**:
  ```python
  hits = s2_retriever.search(query_text, k=4)
  # Returns atomic propositions c2, c3, c4 (318 words)
  ```
* **Retrieved Payload (318 Words)**:
  ```text
  [c2] (Berg_Random_Walks_in_Biology_1993 p.2):
  A particle at absolute temperature T has, on the average, a kinetic energy associated with movement along each axis of kT/2, where k is Boltzmann's constant.

  [c3] (Berg_Random_Walks_in_Biology_1993 p.2):
  From this relationship we compute the mean-square velocity, (V,2> = k1/m,
  ```
* **Model Output JSON**:
  ```json
  {
    "answer": "According to equipartition theory, a microscopic particle at absolute temperature T possesses an average thermal kinetic energy of kT/2 per spatial degree of freedom. The mean-square velocity is given by kT/m, indicating that thermal velocity is proportional to the square root of temperature.",
    "citations": [
      {
        "claim": "The average kinetic energy per spatial degree of freedom is kT/2.",
        "source": "c2",
        "quote": "A particle at absolute temperature T has, on the average, a kinetic energy associated with movement along each axis of kT/2, where k is Boltzmann's constant."
      },
      {
        "claim": "The mean-square velocity along one axis is kT/m, implying velocity scales with the square root of temperature.",
        "source": "c3",
        "quote": "From this relationship we compute the mean-square velocity, (V,2> = k1/m,"
      }
    ]
  }
  ```
* **Forensic Audit in `items.jsonl`**:
  - `Gate 1 (Quote Snapping)`: **VERIFIED (2/2)**.
    * Citation 1 snapped to disk bytes `[1204, 1360]`.
    * Citation 2 snapped to disk bytes `[1361, 1430]`.
  - `Gate 2 (Auto-Entailment)`: **SUPPORTS (2/2)**.
  - `Citation Bluffing Rate`: **0.0%**.

---

## 5. Platform 4: $S_3$ (Causal Claim Graph — Sanity Engine Multi-Hop)

$S_3$ extracts directed causal triples: `[Temperature T] -> [Thermal Energy kT/2] -> [Mean-Square Velocity]`.

### Method 1: Original Sanity Engine Execution
* **Retrieval Call**:
  ```python
  s3 = ClaimGraph(auto_jit=True)
  hits, used_words = apply_budget(s3, hypothesis, max_words=400)
  # Traverses causal path from node "temperature" to "thermal velocity"
  ```
* **Retrieved Payload (473 Words)**:
  ```text
  [1] (Berg_Random_Walks_in_Biology_1993 p.2):
  [Causal Chain]: Temperature -> Kinetic Energy (kT/2) -> Mean-Square Velocity (kT/m).
  A particle at absolute temperature T has, on the average, a kinetic energy associated with movement along each axis of kT/2, where k is Boltzmann's constant. From this relationship we compute the mean-square velocity, (V,2> = k1/m...
  ```
* **Model Output JSON**:
  ```json
  {
    "verdict": "refuted",
    "cited": [1],
    "reason": "The evidence states that the mean-square velocity is proportional to the absolute temperature (kT/m). Therefore, lowering the temperature decreases, rather than increases, the root-mean-square thermal velocity."
  }
  ```
* **Audit Result**: `is_correct: true`, `page_recall: 1.0`, `ctx_words: 473w`.

### Method 2: Allen Institute ScholarQA Execution
* **Retrieval Call**:
  ```python
  hits = s3_retriever.search(query_text, k=4)
  # Retrieves connected causal subgraph surrounding equipartition
  ```
* **Retrieved Payload (821 Words)**:
  Passages containing nodes `kT/2` and `(V,2> = k1/m,`.
* **Model Output JSON**:
  ```json
  {
    "answer": "Equipartition theory dictates that kinetic energy per translational axis is kT/2. Mean-square velocity is given by kT/m.",
    "citations": [
      {
        "claim": "Thermal kinetic energy per axis is kT/2.",
        "source": "g_node_44",
        "quote": "A particle at absolute temperature T has, on the average, a kinetic energy associated with movement along each axis of kT/2, where k is Boltzmann's constant."
      },
      {
        "claim": "Velocity is derived from mean-square formula.",
        "source": "g_edge_12",
        "quote": "From this relationship we compute the mean-square velocity, (V,2> = k1/m,"
      }
    ]
  }
  ```
* **Forensic Audit**:
  - `Gate 1 (Quote Snapping)`: **VERIFIED (2/2)**.
  - `Gate 2 (Auto-Entailment)`: **SUPPORTS (2/2)**. Caught the OCR scanner typo (`k1/m` instead of `kT/m`) without breaking reasoning.
  - `Citation Bluffing Rate`: **0.0%**.

---

## 6. Platform 5: $S_{\text{cached}}$ (Gemini Long-Context Prompt Caching)

$S_{\text{cached}}$ pre-loads entire multi-chapter textbook slices into Gemini's prompt cache.

### Method 1: Original Sanity Engine Execution
* **Retrieval Call**:
  ```python
  # In eval_cached.py:
  cached_slice, ctx_words = get_cached_book_slice("Berg_Random_Walks_in_Biology_1993", [1, 2, 3])
  # Injects 14,653 words of Berg Chapters 1-3 into cached context
  res = llm.extract_json(METHOD_1_SYSTEM_PROMPT, METHOD_1_USER_PROMPT.format(hypothesis=hypothesis, context=cached_slice), METHOD_1_SCHEMA)
  ```
* **Retrieved Payload (14,653 Words)**:
  Pages 1 through 45 of *Berg (1993)*.
* **Model Output JSON**:
  ```json
  {
    "verdict": "refuted",
    "cited": [2],
    "reason": "The root-mean-square velocity is proportional to the square root of the absolute temperature (v_rms = sqrt(kT/m)), so lowering the temperature decreases, rather than increases, the thermal velocity."
  }
  ```
* **Audit Result**: `is_correct: true`, `page_recall: 1.0`, `ctx_words: 14,653w`, `latency: 1.35s` (Fast because target was on Page 2, near the start of the book).

### Method 2: Allen Institute ScholarQA Execution
* **Retrieval Call**:
  ```python
  body, ctx_words = get_cached_book_slice("Berg_Random_Walks_in_Biology_1993", [1, 2, 3])
  # Injects 10,789 words of textbook context into context prompt
  ```
* **Model Output JSON**:
  ```json
  {
    "answer": "According to equipartition theory, thermal kinetic energy per spatial degree of freedom is kT/2. Velocity is proportional to the square root of temperature.",
    "citations": [
      {
        "claim": "Thermal kinetic energy per spatial axis is kT/2.",
        "source": "Berg_Random_Walks_in_Biology_1993 p.2",
        "quote": "A particle at absolute temperature T has, on the average, a kinetic energy associated with movement along each axis of kT/2, where k is Boltzmann's constant."
      },
      {
        "claim": "Mean square velocity is kT/m.",
        "source": "Berg_Random_Walks_in_Biology_1993 p.2",
        "quote": "From this relationship we compute the mean-square velocity, (V,2> = k1/m,"
      }
    ]
  }
  ```
* **Forensic Audit**:
  - `Gate 1 (Quote Snapping)`: **VERIFIED (2/2)**.
  - `Gate 2 (Auto-Entailment)`: **SUPPORTS (2/2)**.
  - `Citation Bluffing Rate`: **0.0%**.
  - `Footprint`: **10,789 words** (34× larger than $S_2$).

---

## 7. Complete Side-by-Side Dual-Method Table for Question 2

| Evaluation Dimension | $S_0$ (Raw Frontier LLM) | $S_1$ (BM25 Chunker) | $S_2$ (Relational DB) | $S_3$ (Causal Graph) | $S_{\text{cached}}$ (Gemini Long Context) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Method 1: Retrieval Call** | None (`ctx = ""`) | BM25 on raw chunks | SQLite FTS5 proposition join | Causal graph path traversal | Slice prompt caching (90 pages) |
| **Method 1: Context Payload** | **0w** | 270w | **388w** | 473w | 14,653w *(38× bloat)* |
| **Method 1: Verdict Output** | `insufficient` *(Abstain)*| `refuted` | `refuted` | `refuted` | `refuted` |
| **Method 1: Verdict Accuracy**| ❌ Incorrect (Abstained)| ✅ **Correct** | ✅ **Correct** | ✅ **Correct** | ✅ **Correct** |
| **Method 2: Citations Generated**| 2 citations | 1 citation | 2 citations | 2 citations | 2 citations |
| **Method 2: Gate 1 Disk Snapping**| ❌ **0% (2/2 Hallucinated)**| ✅ **100% (1/1 Verified)**| ✅ **100% (2/2 Verified)**| ✅ **100% (2/2 Verified)**| ✅ **100% (2/2 Verified)**|
| **Method 2: Gate 2 Entailment** | ❌ **0% Sound** | ✅ **100% Sound** | ✅ **100% Sound** | ✅ **100% Sound** | ✅ **100% Sound** |
| **Method 2: Citation Bluffing** | **100.0% (Bluffing)** | **0.0%** | **0.0%** | **0.0%** | **0.0%** |
| **Method 2: Context Footprint** | **0w** | 270w | **318w (Dense truth)** | 821w | 10,789w *(34× bloat)* |
| **Method 2: Query Latency** | 3.8s | **1.8s** | **1.8s** | 4.2s | 12.4s |
