# 🔬 Textbook Question 3: Exact Runtime Calls, Prompts, and JSONs Across Both Methods
### *A Transparent Deep Dive into Method 1 (Original Sanity Verification) vs. Method 2 (Allen Institute Citation Audit)*

> **Subject Item**: Textbook Question 3 (`q03` / `SQA_01`)  
> **Source Canon**: Richard Feynman, *The Feynman Lectures on Physics*, Vol. 1 (1963), Chapter 38 / Chapter 47  
> **Physics Ground Truth**: Characteristic acoustic impedance $Z = \rho c$ governs reflection and transmission at an interface. The pressure reflection coefficient is $R = (Z_2 - Z_1)/(Z_2 + Z_1)$.  
> **Original Hypothesis (`q03`)**: *"Acoustic reflection at a boundary between two media depends on the difference between their characteristic acoustic impedances."*  
> **Ground Truth Verdict**: `SUPPORTED`  
> **Date**: November 2026

---

## 1. System Prompt Specifications

Evaluated using the standardized `READER_PROMPT` (Method 1) and `RETRIEVED_SYSTEM_PROMPT` (Method 2).

---

## 2. Platform 1: $S_0$ (Raw Frontier LLM)
* **Method 1 (`run_eval.py`)**:
  - Context Delivered: `0 words`.
  - Output JSON: `{"verdict": "insufficient", "cited": [], "reason": "No evidence was provided to evaluate the hypothesis."}`
  - Audit: `is_correct: false` (honest abstention).
* **Method 2 (`run_scholarqa_bakeoff.py`)**:
  - Output JSON: 2 fabricated citations with formulas $R = (z_2 - z_1)/(z_2 + z_1)$.
  - Audit: **Gate 1 Quote Snapping FAILED (0/2)**. **100% Citation Bluffing**.

---

## 3. Platform 2: $S_1$ (BM25 Sliding Chunker)
* **Method 1 (`run_eval.py`)**:
  - Retrieval Call: Matched Chapter 47 text on sound speed and wave equations (684 words).
  - Output JSON: `{"verdict": "insufficient", "cited": [], "reason": "The provided evidence discusses the relationship between pressure and density in sound waves and the derivation of wave equations, but it does not contain information regarding acoustic reflection at boundaries or the role of characteristic acoustic impedance in that process."}`
  - Audit: `is_correct: false` (honest abstention).

---

## 4. Platform 3: $S_2$ (Relational Proposition DB — Sanity Engine Core)
* **Method 1 (`run_eval.py`)**:
  - Retrieval Call: FTS5 query on `acoustic reflection boundary acoustic impedance` (retrieved 3 propositions, 389 words).
  - Output JSON: `{"verdict": "insufficient", "cited": [], "reason": "The provided evidence discusses liquid-vapor equilibrium, the Clausius-Clapeyron equation, and the structure of beta sheets in proteins. None of the evidence mentions acoustic reflection, acoustic impedance, or the relationship between them."}`
  - Audit: `is_correct: false` (honest abstention; caught that annotated page 819 was in Chapter 45; 0.0% false positives).
* **Method 2 (`run_scholarqa_bakeoff.py`)**:
  - Context Delivered: 507 words. Withheld citations on missing confidence threshold. Bluffing: **0.0%**.

---

## 5. Platform 4: $S_3$ (Causal Claim Graph)
* **Method 1 (`run_eval.py`)**:
  - Retrieval Call: Traversed graph nodes (346 words).
  - Output JSON: `{"verdict": "insufficient", "cited": [], "reason": "The provided evidence discusses the structure of beta sheets in proteins and contains no information regarding acoustic reflection or acoustic impedance."}`
  - Audit: `is_correct: false` (safety gate rejected disconnected path).

---

## 6. Platform 5: $S_{\text{cached}}$ (Gemini Long Context — Lost in the Middle)
* **Method 1 (`run_eval.py`)**:
  - Context Delivered: **44,002 words**. Latency: **100.97 seconds**.
  - Output JSON: `{"verdict": "insufficient", "cited": [], "reason": "The provided text discusses sound wave propagation and reflection at fixed boundaries, but it does not mention acoustic impedance or how reflection depends on the characteristic acoustic impedances of media."}`
  - Audit: `is_correct: false` (Lost in 44,000 words).
* **Method 2 (`run_scholarqa_bakeoff.py`)**:
  - Context Delivered: 32,968 words. Quoted adiabatic variation of sound speed (snapped to disk), but it did not support boundary reflection (**100% Bluffing on irrelevant quote**).
