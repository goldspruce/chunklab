# Master Comparative Scorecards: Method 1 vs. Method 2 (All 10 Questions)

**Separated Overall Percentage (%) Scorecards Across 5 Scientific AI Architectures**  
*Evaluated across 10 Cross-Disciplinary Questions (12,320 Canonical Textbook Chunks)*  
*Document Version: 1.0.0 — November 1, 2026*  
*Author: Sanity Engine Core Architecture Team*

---

## Executive Overview

To provide total methodological clarity, this document separates the 10-question benchmark evaluation into two independent scorecards:
1. **Table 1: Method 1 (Scientific Inquiry & Hypothesis Verification)** — Evaluates whether the system correctly proves, refutes, or abstains on closed scientific hypotheses, measuring page recall and token efficiency.
2. **Table 2: Method 2 (Allen Institute ScholarQA Forensic Audit)** — Evaluates physical citation grounding, measuring quote snapping veracity, citation hallucination, and citation bluffing.

---

## Table 1: Method 1 Scorecard — Scientific Inquiry & Hypothesis Verification (Overall %)

*Task: Closed-system verification of 10 complex multi-step hypotheses across graduate physics, biophysics, neurophysiology, and biochemistry treatises.*

| Platform / Architecture | Verdict Accuracy (%) | Correct Verifications | Target Page Recall (%) | Avg Context Words | Token Efficiency vs Cached | Avg Latency | Calibrated Abstention Rate (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$S_0$: Raw Frontier LLM** *(Parametric Memory)* | **10.0%** | 1 / 10 | **0.0%** | **0w** | Baseline ($1.0\times$) | 8.7s | **0.0%** *(Guessed blindly)* |
| **$S_1$: BM25 Sliding Chunks** *(Traditional RAG)* | **70.0%** | 7 / 10 | **25.0%** | **690w** | $72\times$ reduction | 3.2s | **0.0%** |
| **$S_2$: Relational Claims DB** *(Sanity Engine)* | **70.0%** | 7 / 10 | **55.0%** | **357w** | **$139\times$ reduction** | **2.1s** | **0.0%** *(High precision)* |
| **$S_3$: Causal Claim Graph** *(Sanity Engine)* | **40.0%** | 4 / 10 | **35.0%** | **393w** | **$126\times$ reduction** | 5.4s | **60.0%** *(Honest abstention)* |
| **$S_{\text{cached}}$: Long-Context Model** *(Cached Window)* | **60.0%** | 6 / 10 | **20.0%** | **49,664w** | Burn baseline ($139\times$ burn) | 4.1s | **0.0%** |

### Key Method 1 Takeaways:
- **Accuracy Leader**: $S_2$ and $S_1$ tied for the highest classification accuracy (**70.0%**).
- **Efficiency Champion**: $S_2$ achieved 70.0% accuracy using only **357 context words** per query, delivering a **$139\times$ token reduction** compared to $S_{\text{cached}}$ (49,664 words).
- **Calibrated Abstention**: $S_3$'s 40.0% accuracy reflects strict epistemic discipline: whenever an explicit multi-hop causal edge was missing between textbook chapters, it returned `insufficient information` (60.0% abstention) rather than guessing.

---

## Table 2: Method 2 Scorecard — Allen Institute ScholarQA Forensic Audit (Overall %)

*Task: Open research queries evaluated via physical disk character matching (Quote Snapping) and adversarial closed-world NLI referee (Entailment).*

| Platform / Architecture | Total Citations | Verified Citations | Quote Veracity (Snapped) (%) | Citation Hallucination (%) | Claim Entailment (%) | Citation Bluffing (%) | Truth Density (Claims / 1k Context) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$S_0$: Raw Frontier LLM** *(Parametric Memory)* | 18 | 2 | **11.1%** | **88.9%** | **11.1%** | **88.9%** | $\infty$ *(Zero context)* |
| **$S_1$: BM25 Sliding Chunks** *(Traditional RAG)* | 8 | 6 | **75.0%** | **25.0%** | **75.0%** | **0.0%** | 1.09 claims / 1k words |
| **$S_2$: Relational Claims DB** *(Sanity Engine)* | 8 | 6 | **75.0%** | **25.0%** | **75.0%** | **0.0%** | **2.10 claims / 1k words** |
| **$S_3$: Causal Claim Graph** *(Sanity Engine)* | 8 | 7 | **87.5%** | **12.5%** | **87.5%** | **0.0%** | **2.23 claims / 1k words** |
| **$S_{\text{cached}}$: Long-Context Model** *(Cached Window)* | 17 | 16 | **94.1%** | **5.9%** | **88.2%** | **5.9%** | 0.04 claims / 1k words |

### Key Method 2 Takeaways:
- **Parametric Hallucination Collapse**: Without retrieval, $S_0$ fabricates **88.9%** of its citations out of thin air, committing **88.9% Citation Bluffing**.
- **Sanity Engine Zero-Bluffing Invariant**: Both $S_2$ and $S_3$ achieved **0.0% Citation Bluffing**. Every quote verified on physical disk strictly and logically entailed the claim.
- **Truth Density Leader**: $S_3$ (2.23) and $S_2$ (2.10) delivered over **$50\times$ higher truth density** per ingested token than long-context caching (0.04 claims per 1k words).
- **Bluffing in Long-Context**: Despite having entire books in context, $S_{\text{cached}}$ committed **5.9% Citation Bluffing** by misattributing authentic equations to unrelated mechanisms (e.g. Question 3).

---

## Architectural Verdict Summary

$$\begin{aligned}
\text{Best Scientific Accuracy (Method 1)} &\longrightarrow \mathbf{S_2 \text{ Relational DB}} \ (70.0\%) \\
\text{Highest Physical Veracity (Method 2)} &\longrightarrow \mathbf{S_{\text{cached}} \ (94.1\%)} \ \text{and} \ \mathbf{S_3 \text{ Claim Graph}} \ (87.5\%) \\
\text{Lowest Citation Bluffing Rate} &\longrightarrow \mathbf{S_1, S_2, S_3} \ (\mathbf{0.0\% \ Bluffing}) \\
\text{Maximum Truth per Token} &\longrightarrow \mathbf{S_3} \ (2.23) \ \text{and} \ \mathbf{S_2} \ (2.10 \ \text{claims / 1k words})
\end{aligned}$$
