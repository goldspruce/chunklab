# 🔬 Forensic Case Study: How Each Platform Handles Textbook Question 5
### *An Architectural Autopsy of S₀, S₁, S₂, S₃, and Long-Context Caching on Passive Transport & ATP Hydrolysis*

> **Subject Item**: Textbook Question 5 (`q05` / `SQA_05`)  
> **Source Canon**: Bruce Alberts et al., *Molecular Biology of the Cell*, 7th ed. (2022), Chapter 11, Page 612  
> **Ground Truth Biology**: Passive transport across cellular membranes is driven entirely by concentration and electrochemical gradients; it does not require metabolic energy input from ATP hydrolysis. Therefore, the claim that passive diffusion requires direct ATP hydrolysis is false.  
> **Original Hypothesis (`q05`)**: *"Passive diffusion across a lipid bilayer requires direct metabolic input from ATP hydrolysis."*  
> **Ground Truth Verdict**: `REFUTED`  
> **Date**: November 2026

---

## 1. Complete Side-by-Side Dual-Method Table for Question 5

| Evaluation Dimension | Metric Source | $S_0$ (Raw Frontier LLM) | $S_1$ (BM25 Chunker) | $S_2$ (Relational DB) | $S_3$ (Causal Graph) | $S_{\text{cached}}$ (Gemini Long Context) |
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

## 2. Key Takeaways on Question 5

1. **The Context Budget Divergence**:
   - $S_1$ (BM25) and $S_{\text{cached}}$ (Long Context) successfully answered `refuted` because they pulled **massive context windows**: 1,364 words for $S_1$ and a staggering **76,102 words** for $S_{\text{cached}}$.
   - $S_2$ and $S_3$ strictly enforced their $<400$-word context safety budget. $S_2$ retrieved 4 propositions (242 words) defining diffusion as thermal Brownian motion. Because the explicit refutation of ATP hydrolysis was ranked in proposition #5 (just past the 242-word cutoff), $S_2$ safely refused to extrapolate and returned `insufficient`.
2. **Economic & Latency Cost**:
   - $S_{\text{cached}}$ consumed **76,102 words** and took **95.24 seconds** per query.
   - $S_2$ completed in **1.2 seconds** with **242 words**. A slight adjustment to the context budget ($\sim 600\text{ words}$) delivers the ATP refutation while consuming **99.2% fewer tokens than Long Context**.
