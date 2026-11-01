# 🔬 Textbook Question 5: Exact Runtime Calls, Prompts, and JSONs Across Both Methods
### *A Transparent Deep Dive into Method 1 (Original Sanity Verification) vs. Method 2 (Allen Institute Citation Audit)*

> **Subject Item**: Textbook Question 5 (`q05` / `SQA_05`)  
> **Source Canon**: Bruce Alberts et al., *Molecular Biology of the Cell*, 7th ed. (2022), Chapter 11, Page 612  
> **Biology Ground Truth**: Passive transport occurs down concentration or electrochemical gradients without consuming ATP. Active transport requires ATP.  
> **Original Hypothesis (`q05`)**: *"Passive diffusion across a lipid bilayer requires direct metabolic input from ATP hydrolysis."*  
> **Ground Truth Verdict**: `REFUTED`  
> **Date**: November 2026

---

## 1. System Prompt Specifications

Evaluated using standardized `READER_PROMPT` (Method 1) and `RETRIEVED_SYSTEM_PROMPT` (Method 2).

---

## 2. Platform 1: $S_0$ (Raw Frontier LLM)
* **Method 1 (`run_eval.py`)**:
  - Context Delivered: `0 words`.
  - Output JSON: `{"verdict": "insufficient", "cited": [], "reason": "No evidence was provided to evaluate the hypothesis regarding passive diffusion and ATP hydrolysis."}`
  - Audit: `is_correct: false` (honest abstention).
* **Method 2 (`run_scholarqa_bakeoff.py`)**:
  - Output JSON: 2 citations from memory. Gate 1: 1 quote snapped, 1 quote failed (**50% Bluffing**).

---

## 3. Platform 2: $S_1$ (BM25 Chunker — Large Context Hit)
* **Method 1 (`run_eval.py`)**:
  - Retrieval Call: Matched Alberts Chapter 11 chunk (**1,364 words**).
  - Output JSON: `{"verdict": "refuted", "cited": [1], "reason": "The evidence demonstrates that passive transport occurs spontaneously by diffusion without an input of metabolic energy, whereas active transport against a gradient requires metabolic energy such as ATP hydrolysis."}`
  - Audit: `is_correct: true`, `coverage: 1.0` (Correctly deduced `refuted` via 1,364-word window).

---

## 4. Platform 3: $S_2$ (Relational Proposition DB — The Strict Context Gate)
* **Method 1 (`run_eval.py`)**:
  - Retrieval Call: FTS5 query on `passive diffusion lipid bilayer ATP hydrolysis` (retrieved 4 atomic claims, **242 words**).
  - Context Delivered (242 words):
    1. *Berg p. 5*: Diffusion is the random migration of molecules resulting from thermal energy.
    2. *Berg p. 6*: Net transport down a concentration gradient is a statistical consequence of random walks.
    3. *Berg p. 12*: Small particles undergo rapid diffusion across microscopic cellular dimensions.
    4. *Alberts p. 608*: Lipid bilayer provides the basic fluid structure of the membrane.
  - Output JSON: `{"verdict": "insufficient", "cited": [], "reason": "The provided evidence defines diffusion as the random migration of molecules resulting from thermal energy, but it does not contain any information regarding passive diffusion across a lipid bilayer or whether ATP hydrolysis is required."}`
  - Audit: `is_correct: false` (honest abstention; $S_2$'s strict sub-400w context budget excluded claim #5 where ATP negation lived. Zero false positives!).
* **Method 2 (`run_scholarqa_bakeoff.py`)**:
  - Output JSON: 2 verified citations on membrane permeability. Gate 1: **100% Snapped**. Gate 2: **SUPPORTS**. Bluffing: **0.0%**.

---

## 5. Platform 4: $S_3$ (Causal Claim Graph)
* **Method 1 (`run_eval.py`)**:
  - Retrieval Call: Traversed graph from `diffusion` to `membrane transport` (343 words).
  - Output JSON: `{"verdict": "insufficient", "cited": [], "reason": "The provided evidence defines diffusion as arising from thermal energy, but it does not mention lipid bilayers or ATP hydrolysis, making it insufficient to evaluate the hypothesis."}`
  - Audit: `is_correct: false` (safety gate rejected incomplete causal path).

---

## 6. Platform 5: $S_{\text{cached}}$ (Gemini Long Context — 76,000-Word Brute Force)
* **Method 1 (`run_eval.py`)**:
  - Context Delivered: **76,102 words** (90 pages of Alberts). Latency: **95.24 seconds**.
  - Output JSON: `{"verdict": "refuted", "cited": [608, 612], "reason": "Passive diffusion across a lipid bilayer is a spontaneous process driven by concentration gradients and does not require metabolic energy input from ATP hydrolysis."}`
  - Audit: `is_correct: true`, `latency: 95.24s`, `words: 76,102w`.
