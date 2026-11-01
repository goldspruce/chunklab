# 🔬 Forensic Case Study: How Each Platform Handles Textbook Question 2
### *A Dual-Benchmark Architectural Autopsy of S₀, S₁, S₂, S₃, and Long-Context Caching on Thermal Velocity & Equipartition Theory*

> **Subject Item**: Textbook Question 2 (`q02` / `SQA_02`)  
> **Source Canon**: Howard C. Berg, *Random Walks in Biology* (Princeton University Press, 1993), Chapter 1, Page 2  
> **Ground Truth Physics**: By the equipartition theorem, $\frac{1}{2}m\langle v_x^2\rangle = \frac{1}{2}kT \implies v_{\text{rms}} = \sqrt{kT/m}$. Because $v_{\text{rms}} \propto \sqrt{T}$, **lowering temperature decreases thermal velocity**.  
> **Evaluated Protocols**:  
> 1. **Method 1: The Original Sanity Engine Benchmark (`run_eval.py`)** — 3-Way Deductive Hypothesis Verification (`SUPPORTED`, `REFUTED`, `INSUFFICIENT`).  
> 2. **Method 2: The Allen Institute ScholarQA Benchmark (`run_scholarqa_bakeoff.py`)** — Forensic Quote Attribution & Citation Bluffing Audit.

---

## 1. The Benchmark Problem: Question 2

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 THE TARGET TEST ITEM                                   │
├───────────────────────┬────────────────────────────────────────────────────────────────┤
│ Hypothesis (q02)      │ "Lowering the temperature of an aqueous solution increases the │
│                       │  root-mean-square thermal velocity of dissolved proteins like  │
│                       │  lysozyme."                                                    │
├───────────────────────┼────────────────────────────────────────────────────────────────┤
│ Ground Truth Verdict  │ REFUTED (v_rms is proportional to sqrt(T); lowering T lowers v)│
├───────────────────────┼────────────────────────────────────────────────────────────────┤
│ ScholarQA Query       │ "According to equipartition theory, what is the thermal        │
│ (SQA_02)              │  kinetic energy per spatial degree of freedom for microscopic  │
│                       │  particles in aqueous suspension, and how does thermal         │
│                       │  velocity scale with temperature?"                             │
├───────────────────────┼────────────────────────────────────────────────────────────────┤
│ Verbatim Source Text  │ "A particle at absolute temperature T has, on the average,     │
│ (Berg 1993, p. 2)     │  a kinetic energy associated with movement along each axis of  │
│                       │  kT/2, where k is Boltzmann's constant."                       │
│                       │                                                                │
│                       │ "From this relationship we compute the mean-square velocity,   │
│                       │  (V,2> = k1/m," [Raw OCR text scanning ⟨v²⟩ = kT/m]            │
└───────────────────────┴────────────────────────────────────────────────────────────────┘
```

---

## 2. Complete Dual-Method Scorecard on Question 2

The table below contrasts all five platforms across both benchmark methodologies:

| Evaluation Dimension | Metric Source | $S_0$ (Raw Frontier LLM) | $S_1$ (BM25 Chunker) | $S_2$ (Relational DB) | $S_3$ (Causal Graph) | $S_{\text{cached}}$ (Gemini Long Context) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Method 1: Retrieval Call** | `run_eval.py` | None (`hits = []`) | BM25 on raw chunks | SQLite FTS5 proposition join | Causal graph path traversal | Slice prompt caching (90 pages) |
| **Method 1: Context Payload** | `run_eval.py` | **0w** | 270w | **388w** | 473w | 14,653w *(38× bloat)* |
| **Method 1: Reader Verdict** | `run_eval.py` | `insufficient` | `refuted` | `refuted` | `refuted` | `refuted` |
| **Method 1: Verdict Status** | `run_eval.py` | ⚠️ **Abstained (Safe)**| ✅ **Pass (Correct)** | ✅ **Pass (Correct)** | ✅ **Pass (Correct)** | ✅ **Pass (Correct)** |
| **Method 1: Page Recall** | `run_eval.py` | 0.00 | **1.00** | **1.00** | **1.00** | **1.00** |
| **Method 2: Citations Made** | `run_scholarqa_bakeoff.py`| 2 citations | 1 citation | **2 citations** | **2 citations** | 2 citations |
| **Method 2: Gate 1 Snapping**| `run_scholarqa_bakeoff.py`| ❌ **Fail (0/2 Fake)** | ✅ **Pass (1/1 Real)** | ✅ **Pass (2/2 Real)** | ✅ **Pass (2/2 Real)** | ✅ **Pass (2/2 Real)** |
| **Method 2: Gate 2 Entailment**| `run_scholarqa_bakeoff.py`| ❌ **Fail (0% Sound)** | ✅ **Pass (100% Sound)**| ✅ **Pass (100% Sound)**| ✅ **Pass (100% Sound)**| ✅ **Pass (100% Sound)**|
| **Method 2: Bluffing Status**| `run_scholarqa_bakeoff.py`| ❌ **Fail (100% Bluff)**| ✅ **Pass (0% Bluff)** | ✅ **Pass (0% Bluff)** | ✅ **Pass (0% Bluff)** | ✅ **Pass (0% Bluff)** |
| **Method 2: Context Footprint**| `run_scholarqa_bakeoff.py`| **0w** | 270w | **318w (Dense truth)** | 821w | 10,789w *(34× bloat)* |
| **Method 2: Latency** | `run_scholarqa_bakeoff.py`| 3.8s | **1.8s** | **1.8s** | 4.2s | 12.4s |

---

## 3. Platform 1: $S_0$ (Raw Frontier LLM) — The Un-Augmented Baseline

$S_0$ operates with **0 words of context** across both benchmarks.

* **Method 1 Performance (`run_eval.py`)**:
  - Received: The hypothesis with empty context.
  - Action: Following the prompt instruction to never guess without evidence, $S_0$ responded `"insufficient"`. It demonstrated **calibrated abstention**, refusing to invent facts.
* **Method 2 Performance (`run_scholarqa_bakeoff.py`)**:
  - Received: The open mechanism query with the mandate: *"For every claim, cite the literature and provide a VERBATIM quote."*
  - Action: Under pressure to provide citations with 0 retrieval context, it entered **active hallucination mode**. It generated two formal citations quoting *Berg (1993)* and *Pathria (2011)*.
  - Forensic Snapping Audit: Both quotes failed physical disk verification (**100% Citation Bluffing**).

---

## 4. Platform 2: $S_1$ (BM25 Sliding Chunker) — The Lucky Co-Location

* **Method 1 Performance (`run_eval.py`)**:
  - Retrieval: `apply_budget(s1, hypothesis, max_words=400)`.
  - Result: BM25 matched Chunk #12 (270 words) because "temperature", "aqueous", "solution", and "lysozyme" occurred together on Page 2.
  - Verdict: Correctly answered `refuted` (`is_correct: true`).
* **Method 2 Performance (`run_scholarqa_bakeoff.py`)**:
  - Retrieval: Pulled top 4 chunks.
  - Quote Verification: Successfully verified 1 quote on disk at Berg p. 2 `[1204, 1360]`.
  - Structural Vulnerability: BM25 succeeded here only because the derivation in *Berg* is exceptionally short. When a derivation spans 400 words, sliding chunks split the premise from the conclusion.

---

## 5. Platform 3: $S_2$ (Relational Proposition DB) — The Pareto Winner

* **Method 1 Performance (`run_eval.py`)**:
  - Retrieval: Structured SQLite FTS5 query filtering atomic claims on `temperature`, `velocity`, and `lysozyme`.
  - Context Delivered: Exactly **388 words** covering propositions `c2`, `c3`, and `c4`.
  - Verdict: Output `refuted` with 100% precision.
* **Method 2 Performance (`run_scholarqa_bakeoff.py`)**:
  - Citations: Generated 2 formal citations.
  - Gate 1 Snapping: Both snapped to exact physical byte coordinates `[1204, 1360]` and `[1361, 1430]`.
  - Gate 2 Entailment: Both claims were strictly proved by the quotes (**0.0% Citation Bluffing**).
  - Efficiency: Required only **318 context words** and completed in **1.8s**.

---

## 6. Platform 4: $S_3$ (Causal Claim Graph) — The Safety Gate

* **Method 1 Performance (`run_eval.py`)**:
  - Retrieval: Traversed directed causal path: `Temperature -> Kinetic Energy (kT/2) -> Mean-Square Velocity (kT/m)`.
  - Context Delivered: **473 words**.
  - Verdict: Output `refuted` (`is_correct: true`).
* **Method 2 Performance (`run_scholarqa_bakeoff.py`)**:
  - Robustness to OCR: Scanned text contained OCR noise `(V,2> = k1/m,` (reading $kT/m$ as $k1/m$). Because $S_3$ stores normalized semantic edges alongside raw text, it correctly deduced the temperature scaling without stumbling on the OCR typo.
  - Veracity: **100% Verified**, **0.0% Bluffing**.

---

## 7. Platform 5: $S_{\text{cached}}$ (Gemini Long Context) — The Brute-Force Bloat

* **Method 1 Performance (`run_eval.py`)**:
  - Context Delivered: **14,653 words** (pre-loaded 90-page textbook window).
  - Verdict: Output `refuted` (`is_correct: true`). Because Page 2 was near the beginning of the context slice, attention did not suffer from attention dilution.
* **Method 2 Performance (`run_scholarqa_bakeoff.py`)**:
  - Citations: 2 verified citations.
  - The Cost: Consumed **10,789 words** per query—**34× more tokens** than $S_2$. On multi-chapter derivations located deeper in the book, this brute-force approach collapsed.
