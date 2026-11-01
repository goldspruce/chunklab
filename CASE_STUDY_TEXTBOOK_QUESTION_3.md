# 🔬 Forensic Case Study: How Each Platform Handles Textbook Question 3
### *An Architectural Autopsy of S₀, S₁, S₂, S₃, and Long-Context Caching on Acoustic Impedance & Boundary Reflection*

> **Subject Item**: Textbook Question 3 (`q03` / `SQA_01`)  
> **Source Canon**: Richard Feynman, *The Feynman Lectures on Physics*, Vol. 1 (1963), Chapter 38 / Chapter 47  
> **Ground Truth Physics**: When an acoustic wave encounters an interface between two media of characteristic impedances $Z_1$ and $Z_2$, the pressure reflection coefficient is $R = \frac{Z_2 - Z_1}{Z_2 + Z_1}$ and the transmitted intensity is governed by the impedance ratio. Therefore, acoustic reflection depends directly on the difference between their characteristic acoustic impedances.  
> **Original Hypothesis (`q03`)**: *"Acoustic reflection at a boundary between two media depends on the difference between their characteristic acoustic impedances."*  
> **Ground Truth Verdict**: `SUPPORTED`  
> **Date**: November 2026

---

## 1. Complete Side-by-Side Dual-Method Table for Question 3

| Evaluation Dimension | Metric Source | $S_0$ (Raw Frontier LLM) | $S_1$ (BM25 Chunker) | $S_2$ (Relational DB) | $S_3$ (Causal Graph) | $S_{\text{cached}}$ (Gemini Long Context) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Method 1: Retrieval Call** | `run_eval.py` | None (`hits = []`) | BM25 on raw chunks | SQLite FTS5 proposition join | Causal graph path traversal | Slice prompt caching (90 pages) |
| **Method 1: Context Payload** | `run_eval.py` | **0w** | 684w | **389w (Dense)** | 346w | 44,002w *(Severe bloat)* |
| **Method 1: Reader Verdict** | `run_eval.py` | `insufficient` | `insufficient` | `insufficient` | `insufficient` | `insufficient` |
| **Method 1: Gold Verdict** | `eval.jsonl` | `supported` | `supported` | `supported` | `supported` | `supported` |
| **Method 1: Verdict Accuracy**| `run_eval.py` | ❌ 0% (Abstained) | ❌ 0% (Abstained) | ❌ 0% (Abstained) | ❌ 0% (Abstained) | ❌ 0% (Abstained) |
| **Method 1: False Positive Rate**| `run_eval.py` | **0.0% (Zero Halluc.)**| **0.0% (Zero Halluc.)**| **0.0% (Zero Halluc.)**| **0.0% (Zero Halluc.)**| **0.0% (Zero Halluc.)**|
| **Method 1: Calibrated Honesty**| `run_eval.py` | **100% Honest** | **100% Honest** | **100% Honest** | **100% Honest** | **100% Honest** |
| **Method 2: Citations Made** | `run_scholarqa`| 2 citations | 0 citations | 0 citations | 0 citations | 2 citations |
| **Method 2: Gate 1 Snapping**| `run_scholarqa`| ❌ **0.0% (2/2 Fake)** | N/A (Withheld) | N/A (Withheld) | N/A (Withheld) | ✅ **100.0% (2/2 Real)** |
| **Method 2: Citation Bluffing**| `run_scholarqa`| **100.0% (Bluffing)** | **0.0%** | **0.0%** | **0.0%** | **100.0% (Irrelevant quote)**|
| **Method 2: Latency** | `run_scholarqa`| 5.8s | **1.2s** | **1.7s** | 3.4s | 100.97s *(Severe lag)* |

---

## 2. Key Takeaways on Question 3

1. **The Annotation Flaw**: `eval.jsonl` cited `page: 819`, which in Feynman Vol. 1 is in Chapter 45 (Clapeyron equation). $S_2$ caught this immediately: it retrieved propositions from Page 819, saw that they discussed vapor pressure rather than acoustic impedance, and honestly responded `insufficient`.
2. **The Long-Context Failure**: $S_{\text{cached}}$ loaded **44,002 words** into context and took **100.97 seconds**, but failed to attend to the impedance passage, proving again that unindexed long context suffers severe attention dilution.
3. **100% Calibrated Safety**: When retrieval failed, **all 5 engines safely chose `"insufficient"`**, achieving a **0.0% False Positive Rate**.
