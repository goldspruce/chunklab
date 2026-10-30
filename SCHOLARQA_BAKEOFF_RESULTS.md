# 🔬 ScholarQABench Citation Hallucination Bake-Off: Complete 10-Query Results & Analysis

> **Evaluation Suite**: Path A — ScholarQABench Citation Veracity & Grounding Bake-Off  
> **Benchmark Corpus**: 12,320 Canonical Textbook Chunks across Physics, Biophysics, Neurophysiology, Biochemistry, and Information Theory  
> **Queries Evaluated**: 10 Expert Mechanism Queries (2 per foundational science)  
> **Systems Evaluated**: `Raw_Frontier_LLM` (Parametric Gemini 3.8 Flash), `S2_relational`, `S3_graph`, `S_cached` (Long-Context Cached Gemini 3.8 Flash)  
> **Deterministic Verification**: Exact character-offset quote verification (`verify_quote()`) + LLM claim-quote entailment verification (`auto_entail()`)

---

## 1. Executive Summary & The 10-Query Scorecard

In scientific literature synthesis, commercial frontier models routinely hallucinate citations and commit citation bluffing. To test this under the Allen Institute for AI auditing standard, we ran a **10-query cross-disciplinary gauntlet** evaluating **51 total citations** against all 12,320 textbook chunks on disk.

### The 10-Query ScholarQABench Scorecard

| System | Total Citations | Veracity Rate (% Real) | Hallucination Rate (% Fake) | Entailment Rate (% Sound) | Bluffing Rate (% Irrelevant) | Avg Context Words | Avg Latency |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **`Raw_Frontier_LLM`** | 18 | **0.0%** | **100.0%** | 0.0% | 0.0% | 0w | 8.7s |
| **`S2_relational`** | 8 | **37.5%** | **62.5%** | 37.5% | **0.0%** | 886w | 2.1s |
| **`S3_graph`** | 8 | **62.5%** | **37.5%** | 62.5% | **0.0%** | 967w | 5.4s |
| **`S_cached`** | 17 | **41.2%** | **58.8%** | 35.3% | **5.9%** | 26,904w | 4.1s |

---

## 2. Key Insights from the 10-Query Suite

```mermaid
flowchart TD
    subgraph Raw_LLM ["Raw Frontier LLM (Parametric)"]
        R1["Generates 18 Citations"] --> R2["0% Real Quotes (18 of 18 Fake)"]
        R2 --> R3["100.0% Citation Hallucination Rate"]
        R3 --> R4["Zero character offset matches across 12,320 pages"]
    end

    subgraph Cached ["S_cached (Long-Context ~27k words)"]
        C1["Generates 17 Citations"] --> C2["41.2% Verbatim Quotes"]
        C2 --> C3["58.8% Paraphrased / Altered Quotes"]
        C3 --> C4["5.9% Citation Bluffing"]
    end

    subgraph Sanity_Engines ["Sanity Engine (S2 & S3)"]
        S1["Retrieves Targeted Chunks (~900w)"] --> S2["Up to 62.5% Verbatim Grounding"]
        S2 --> S3["0.0% Citation Bluffing (Sound Attribution)"]
        S3 --> S4["Deterministic quote snapping to disk offsets"]
    end
```

### 1. The 100% Parametric Hallucination Baseline
Across 10 diverse queries, **`Raw_Frontier_LLM` emitted 18 citations and fabricated 100% of them**:
- It cited authentic textbooks (*Kinsler Acoustics*, *Pathria Statistical Mechanics*, *Purves Neuroscience*, *Jackson Classical Electrodynamics*, *Cornish-Bowden Fundamentals of Enzyme Kinetics*).
- However, **not a single quote existed verbatim in the literature**. Every quote was synthesized on the fly from parametric memory.

### 2. Sanity Engine's Zero-Bluffing Invariant
Both $S_2$ and $S_3$ maintained a **0.0% Citation Bluffing Rate**:
- Every quote verified on disk was **100% logically sound** and directly entailed the claim.
- $S_3$ achieved **62.5% Veracity Rate** while consuming only **967 context words** per query (a **28× token reduction** compared to long-context caching).

### 3. Long-Context Paraphrase Penalty
Even when $S_{\text{cached}}$ was fed ~26,904 words per query, **58.8% of its citations failed exact verification**:
- LLMs inherently reword, contract, or adjust phrasing rather than copying character-for-character.
- $S_{\text{cached}}$ also exhibited **5.9% Citation Bluffing**, misattributing equations in biophysics.

---

## 3. Query Breakdown (All 10 Queries)

| ID | Domain | Reference Work | Citations Tested | Verified Quotes | Key Mechanism Evaluated |
|:---:|:---|:---|:---:|:---:|:---|
| **`SQA_01`** | **Physics** | *Feynman Vol. 1* (p. 818) | 2 | $S_{\text{cached}}$: 0, Raw: 0 | Acoustic boundary impedance mismatch |
| **`SQA_02`** | **Biophysics** | *Berg* (p. 2) | 2 | $S_2$: 2, $S_3$: 2, $S_{\text{cached}}$: 2 | Equipartition energy ($kT/2$) & Brownian velocity |
| **`SQA_03`** | **Neurophysiology** | *Johnston & Wu* (p. 77) | 4 | $S_3$: 1, $S_{\text{cached}}$: 1 | GHK resting membrane potential equation |
| **`SQA_04`** | **Biochemistry** | *Lehninger* (p. 503) | 0 | Abstained across engines | ATP hydrolysis free energy coupling |
| **`SQA_05`** | **Information Theory** | *Cover & Thomas* (p. 244) | 1 | $S_{\text{cached}}$: 1 | Shannon channel capacity $C = \frac{1}{2}\log(1+P/N)$ |
| **`SQA_06`** | **Physics** | *Feynman Vol. 2* (p. 421) | 2 | Raw: 0, $S_{\text{cached}}$: 0 | Conductor skin depth $\delta = \sqrt{2/\omega\mu\sigma}$ |
| **`SQA_07`** | **Biophysics** | *Berg* (p. 48) | 1 | Raw: 0, $S_{\text{cached}}$: 0 | Low Reynolds number Stokes drag $f = 6\pi\eta a$ |
| **`SQA_08`** | **Neurophysiology** | *Alberts* (p. 698) | 3 | $S_2$: 1, $S_3$: 2 | Potassium channel selectivity filter carbonyl oxygens |
| **`SQA_09`** | **Biochemistry** | *Lehninger* (p. 779) | 1 | $S_{\text{cached}}$: 1 | Briggs-Haldane steady-state $d[ES]/dt \approx 0$ |
| **`SQA_10`** | **Information Theory** | *Cover & Thomas* (p. 47) | 2 | $S_{\text{cached}}$: 2 | Mutual information identity $I(X; Y) = H(X) - H(X|Y)$ |

---

## 4. Architectural Comparison

| Dimension | `Raw_Frontier_LLM` | `S2_relational` | `S3_graph` | `S_cached` |
|---|:---:|:---:|:---:|:---:|
| **Citation Veracity** | **0.0%** | 37.5% | **62.5%** | 41.2% |
| **Citation Bluffing** | 0.0% (all fake) | **0.0%** | **0.0%** | **5.9%** |
| **Context Words** | 0w | 886w | 967w | **26,904w** |
| **API Cost Multiplier** | $1.0\times$ | $2.2\times$ | $2.5\times$ | **$30.4\times$** |
| **Average Latency** | 8.7s | **2.1s** | 5.4s | 4.1s |

---
*Generated by Sanity Engine Benchmark Suite — ChunkLab (October 2026).*
