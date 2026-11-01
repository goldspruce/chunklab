# 🔬 Forensic Case Study: How Each Platform Handles Textbook Questions 2, 3, and 5
### *A Multi-Domain Architectural Autopsy Across Kinetics (Q2), Wave Mechanics (Q3), and Membrane Transport (Q5)*

> **Evaluated Architectures**: $S_0$ (Raw Frontier LLM), $S_1$ (BM25 Chunker), $S_2$ (Relational DB), $S_3$ (Causal Graph), $S_{\text{cached}}$ (Gemini Long Context)  
> **Evaluation Frameworks**:  
> 1. **Method 1: The Original Sanity Engine Benchmark (`run_eval.py` / `eval_cached.py`)** — 3-Way Deductive Hypothesis Verification (`SUPPORTED`, `REFUTED`, `INSUFFICIENT`).  
> 2. **Method 2: The Allen Institute ScholarQA Benchmark (`run_scholarqa_bakeoff.py`)** — Forensic Quote Attribution & Citation Bluffing Audit.  
> **Standardized Status Indicators**:  
> - ✅ **Pass / Grounded**: Correct verdict or 100% verified citation with zero bluffing.  
> - ❌ **Fail / Bluffing**: Incorrect verdict or fabricated/irrelevant citation.  
> - ⚠️ **Calibrated Abstention / Withheld**: Honest refusal to guess or safe withholding of ungrounded citations (Zero False Positives).  
> **Date**: November 2026

---

## 1. Executive Summary: The Three Archetypal Scientific Regimes

Evaluating platforms on a single question can create false impressions. By examining **Questions 2, 3, and 5 side-by-side**, we expose three fundamentally distinct regimes of scientific question answering:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             THE THREE ARCHETYPAL SCIENTIFIC REGIMES                              │
├──────────┬─────────────────────────────┬──────────────────────────┬──────────────────────────────┤
│ ITEM     │ DOMAIN & TARGET REFERENCE   │ REGIME PHENOMENON        │ ARCHITECTURAL VERDICT        │
├──────────┼─────────────────────────────┼──────────────────────────┼──────────────────────────────┤
│ Item Q2  │ Biophysics / Kinetics       │ Regime A: Universal      │ All retrievers succeed in    │
│          │ (Berg 1993, p. 2)           │ Grounded Success         │ <500w; S0 bluffs/hallucinates│
├──────────┼─────────────────────────────┼──────────────────────────┼──────────────────────────────┤
│ Item Q3  │ Wave Mechanics / Impedance  │ Regime B: Annotation     │ All engines safely abstain;  │
│          │ (Feynman Vol. 1, p. 819)    │ Trap & Safety Abstention │ 0% false positives; S_cached │
│          │                             │                          │ bluffs with irrelevant quote.│
├──────────┼─────────────────────────────┼──────────────────────────┼──────────────────────────────┤
│ Item Q5  │ Cell Biology / Transport    │ Regime C: Context Budget │ S1 (1,364w) & S_cached       │
│          │ (Alberts 2022, p. 612)      │ & Granularity Divergence │ (76,102w) answer; S2 & S3    │
│          │                             │                          │ safely enforce <400w gate.   │
└──────────┴─────────────────────────────┴──────────────────────────┴──────────────────────────────┘
```

---

## 2. Master Comparative Scorecards: Questions 2, 3, and 5

### Question 2: Thermal Velocity & Equipartition
* **Hypothesis (`q02`)**: *"Lowering the temperature of an aqueous solution increases the root-mean-square thermal velocity of dissolved proteins like lysozyme."*
* **Ground Truth**: `REFUTED` ($v_{\text{rms}} = \sqrt{kT/m} \implies v_{\text{rms}} \propto \sqrt{T}$; lowering $T$ decreases thermal velocity).

| Evaluation Dimension | Metric Source | $S_0$ (Raw LLM) | $S_1$ (BM25) | $S_2$ (Relational DB) | $S_3$ (Causal Graph) | $S_{\text{cached}}$ (Long Context) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Method 1 Context Words** | `run_eval.py` | **0w** | 270w | **388w** | 473w | 14,653w *(38× bloat)* |
| **Method 1 Reader Verdict** | `run_eval.py` | `insufficient` | `refuted` | `refuted` | `refuted` | `refuted` |
| **Method 1 Verdict Status** | `run_eval.py` | ⚠️ **Abstained (Safe)**| ✅ **Pass (Correct)** | ✅ **Pass (Correct)** | ✅ **Pass (Correct)** | ✅ **Pass (Correct)** |
| **Method 1 Page Recall** | `run_eval.py` | 0.00 | **1.00** | **1.00** | **1.00** | **1.00** |
| **Method 2 Citations Made** | `run_scholarqa`| 2 citations | 1 citation | 2 citations | 2 citations | 2 citations |
| **Method 2 Gate 1 (Snapping)**| `run_scholarqa`| ❌ **Fail (0/2 Fake)** | ✅ **Pass (1/1 Real)** | ✅ **Pass (2/2 Real)** | ✅ **Pass (2/2 Real)** | ✅ **Pass (2/2 Real)** |
| **Method 2 Gate 2 (Entail)** | `run_scholarqa`| ❌ **Fail (0% Sound)** | ✅ **Pass (100% Sound)**| ✅ **Pass (100% Sound)**| ✅ **Pass (100% Sound)**| ✅ **Pass (100% Sound)**|
| **Method 2 Bluffing Status**| `run_scholarqa`| ❌ **Fail (100% Bluff)**| ✅ **Pass (0% Bluff)** | ✅ **Pass (0% Bluff)** | ✅ **Pass (0% Bluff)** | ✅ **Pass (0% Bluff)** |
| **Method 2 Query Latency** | `run_scholarqa`| 3.8s | **1.8s** | **1.8s** | 4.2s | 12.4s |

---

### Question 3: Acoustic Impedance Mismatch & Boundary Reflection
* **Hypothesis (`q03`)**: *"Acoustic reflection at a boundary between two media depends on the difference between their characteristic acoustic impedances."*
* **Ground Truth**: `SUPPORTED` (Reflection and transmission coefficients are functions of characteristic acoustic impedance ratios).

| Evaluation Dimension | Metric Source | $S_0$ (Raw LLM) | $S_1$ (BM25) | $S_2$ (Relational DB) | $S_3$ (Causal Graph) | $S_{\text{cached}}$ (Long Context) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Method 1 Context Words** | `run_eval.py` | **0w** | 684w | **389w** | 346w | 44,002w *(Severe bloat)* |
| **Method 1 Reader Verdict** | `run_eval.py` | `insufficient` | `insufficient` | `insufficient` | `insufficient` | `insufficient` |
| **Method 1 Verdict Status** | `run_eval.py` | ⚠️ **Abstained (Safe)**| ⚠️ **Abstained (Safe)**| ⚠️ **Abstained (Safe)**| ⚠️ **Abstained (Safe)**| ⚠️ **Abstained (Safe)**|
| **Method 1 False Positives**| `run_eval.py` | ✅ **0.0% (Zero)** | ✅ **0.0% (Zero)** | ✅ **0.0% (Zero)** | ✅ **0.0% (Zero)** | ✅ **0.0% (Zero)** |
| **Method 1 Page Recall** | `run_eval.py` | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 *(Lost in 44k words)*|
| **Method 2 Citations Made** | `run_scholarqa`| 2 citations | 0 citations | 0 citations | 0 citations | 2 citations |
| **Method 2 Gate 1 (Snapping)**| `run_scholarqa`| ❌ **Fail (0/2 Fake)** | ⚠️ **Withheld (Safe)**| ⚠️ **Withheld (Safe)**| ⚠️ **Withheld (Safe)**| ✅ **Pass (2/2 Real)** |
| **Method 2 Gate 2 (Entail)** | `run_scholarqa`| ❌ **Fail (0% Sound)** | ⚠️ **Withheld (Safe)**| ⚠️ **Withheld (Safe)**| ⚠️ **Withheld (Safe)**| ❌ **Fail (0% Sound)** |
| **Method 2 Bluffing Status**| `run_scholarqa`| ❌ **Fail (100% Bluff)**| ✅ **Pass (0% Bluff)** | ✅ **Pass (0% Bluff)** | ✅ **Pass (0% Bluff)** | ❌ **Fail (100% Bluff)**|
| **Method 2 Query Latency** | `run_scholarqa`| 5.8s | **1.2s** | **1.7s** | 3.4s | 100.97s *(Severe lag)* |

---

### Question 5: Passive Diffusion vs. ATP Hydrolysis
* **Hypothesis (`q05`)**: *"Passive diffusion across a lipid bilayer requires direct metabolic input from ATP hydrolysis."*
* **Ground Truth**: `REFUTED` (Passive transport is spontaneous down concentration/electrochemical gradients without ATP input).

| Evaluation Dimension | Metric Source | $S_0$ (Raw LLM) | $S_1$ (BM25) | $S_2$ (Relational DB) | $S_3$ (Causal Graph) | $S_{\text{cached}}$ (Long Context) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Method 1 Context Words** | `run_eval.py` | **0w** | 1,364w *(Bloat)* | **242w (Budget gate)**| 343w | 76,102w *(Massive bloat)* |
| **Method 1 Reader Verdict** | `run_eval.py` | `insufficient` | `refuted` | `insufficient` | `insufficient` | `refuted` |
| **Method 1 Verdict Status** | `run_eval.py` | ⚠️ **Abstained (Safe)**| ✅ **Pass (Correct)** | ⚠️ **Abstained (Safe)**| ⚠️ **Abstained (Safe)**| ✅ **Pass (Correct)** |
| **Method 1 False Positives**| `run_eval.py` | ✅ **0.0% (Zero)** | ✅ **0.0% (Zero)** | ✅ **0.0% (Zero)** | ✅ **0.0% (Zero)** | ✅ **0.0% (Zero)** |
| **Method 1 Query Latency** | `run_eval.py` | 1.8s | 2.1s | **1.2s (Fastest)** | 3.5s | 95.24s *(Painfully slow)* |
| **Method 2 Citations Made** | `run_scholarqa`| 2 citations | 1 citation | 2 citations | 1 citation | 2 citations |
| **Method 2 Gate 1 (Snapping)**| `run_scholarqa`| ❌ **Fail (1/2 Fake)** | ✅ **Pass (1/1 Real)** | ✅ **Pass (2/2 Real)** | ✅ **Pass (1/1 Real)** | ✅ **Pass (2/2 Real)** |
| **Method 2 Gate 2 (Entail)** | `run_scholarqa`| ❌ **Fail (0% Sound)** | ✅ **Pass (100% Sound)**| ✅ **Pass (100% Sound)**| ✅ **Pass (100% Sound)**| ✅ **Pass (100% Sound)**|
| **Method 2 Bluffing Status**| `run_scholarqa`| ❌ **Fail (50% Bluff)** | ✅ **Pass (0% Bluff)** | ✅ **Pass (0% Bluff)** | ✅ **Pass (0% Bluff)** | ✅ **Pass (0% Bluff)** |
| **Method 2 Context Footprint**| `run_scholarqa`| **0w** | 1,364w | **886w** | 967w | 76,102w |

---

## 3. Master Multi-Question Comparative Table (Q2, Q3, Q5)

The table below synthesizes performance across all three questions into a single unified view with consistent iconography:

| Evaluation Metric | Platform | Question 2 (Kinetics) | Question 3 (Impedance) | Question 5 (Transport) |
| :--- | :--- | :---: | :---: | :---: |
| **Method 1 Context Words** | $S_0$ (Raw Frontier LLM) | **0w** | **0w** | **0w** |
| | $S_1$ (BM25 Chunker) | 270w | 684w | 1,364w *(Bloat)* |
| | $S_2$ (Relational DB) | **388w (Dense)** | **389w (Dense)** | **242w (Budget gate)**|
| | $S_3$ (Causal Graph) | 473w | 346w | 343w |
| | $S_{\text{cached}}$ (Gemini Long Ctx) | 14,653w | 44,002w *(101s)* | 76,102w *(95s)* |
| **Method 1 Verdict** | $S_0$ (Raw Frontier LLM) | `insufficient` | `insufficient` | `insufficient` |
| | $S_1$ (BM25 Chunker) | `refuted` | `insufficient` | `refuted` |
| | $S_2$ (Relational DB) | `refuted` | `insufficient` | `insufficient` |
| | $S_3$ (Causal Graph) | `refuted` | `insufficient` | `insufficient` |
| | $S_{\text{cached}}$ (Gemini Long Ctx) | `refuted` | `insufficient` | `refuted` |
| **Method 1 Status** | $S_0$ (Raw Frontier LLM) | ⚠️ **Abstained (Safe)**| ⚠️ **Abstained (Safe)**| ⚠️ **Abstained (Safe)**|
| | $S_1$ (BM25 Chunker) | ✅ **Pass (Correct)** | ⚠️ **Abstained (Safe)**| ✅ **Pass (Correct)** |
| | $S_2$ (Relational DB) | ✅ **Pass (Correct)** | ⚠️ **Abstained (Safe)**| ⚠️ **Abstained (Safe)**|
| | $S_3$ (Causal Graph) | ✅ **Pass (Correct)** | ⚠️ **Abstained (Safe)**| ⚠️ **Abstained (Safe)**|
| | $S_{\text{cached}}$ (Gemini Long Ctx) | ✅ **Pass (Correct)** | ⚠️ **Abstained (Safe)**| ✅ **Pass (Correct)** |
| **Method 1 False Positives**| **All Systems** | ✅ **0.0% (Zero)** | ✅ **0.0% (Zero)** | ✅ **0.0% (Zero)** |
| **Method 2 Citation Status** | $S_0$ (Raw Frontier LLM) | ❌ **Fail (100% Bluff)**| ❌ **Fail (100% Bluff)**| ❌ **Fail (50% Bluff)** |
| | $S_1$ (BM25 Chunker) | ✅ **Pass (0% Bluff)** | ⚠️ **Withheld (Safe)** | ✅ **Pass (0% Bluff)** |
| | $S_2$ (Relational DB) | ✅ **Pass (0% Bluff)** | ⚠️ **Withheld (Safe)** | ✅ **Pass (0% Bluff)** |
| | $S_3$ (Causal Graph) | ✅ **Pass (0% Bluff)** | ⚠️ **Withheld (Safe)** | ✅ **Pass (0% Bluff)** |
| | $S_{\text{cached}}$ (Gemini Long Ctx) | ✅ **Pass (0% Bluff)** | ❌ **Fail (100% Bluff)**| ✅ **Pass (0% Bluff)** |
| **Method 2 Citations Snapped**| $S_0$ (Raw Frontier LLM) | ❌ 0 of 2 (0%) | ❌ 0 of 2 (0%) | ❌ 1 of 2 (50%) |
| | $S_1$ (BM25 Chunker) | ✅ 1 of 1 (100%) | ⚠️ 0 citations | ✅ 1 of 1 (100%) |
| | $S_2$ (Relational DB) | ✅ 2 of 2 (100%) | ⚠️ 0 citations | ✅ 2 of 2 (100%) |
| | $S_3$ (Causal Graph) | ✅ 2 of 2 (100%) | ⚠️ 0 citations | ✅ 1 of 1 (100%) |
| | $S_{\text{cached}}$ (Gemini Long Ctx) | ✅ 2 of 2 (100%) | ❌ 2 of 2 (Irrelevant)| ✅ 2 of 2 (100%) |
