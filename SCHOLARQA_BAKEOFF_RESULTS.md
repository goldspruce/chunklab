# 🔬 ScholarQABench Citation Hallucination Bake-Off: Complete Results & Analysis

> **Evaluation Suite**: Path A — ScholarQABench Citation Veracity & Grounding Bake-Off  
> **Benchmark Corpus**: 12,320 Canonical Textbook Chunks across Physics, Biophysics, Neurophysiology, Biochemistry, and Information Theory  
> **Systems Evaluated**: `Raw_Frontier_LLM` (Parametric Gemini 3.8 Flash), `S2_relational`, `S3_graph`, `S_cached` (Long-Context Cached Gemini 3.8 Flash)  
> **Deterministic Verification**: Exact character-offset quote verification (`verify_quote()`) + LLM claim-quote entailment verification (`auto_entail()`)

---

## 1. Executive Summary & The Scorecard

In scientific RAG, the primary failure mode is **citation hallucination** and **citation bluffing**:
- **Citation Hallucination**: An LLM fabricates or alters quotes and paper references that do not exist verbatim in the source literature.
- **Citation Bluffing**: An LLM cites an authentic source or quote, but the cited text fails to logically entail the asserted factual claim.

To quantify this, we ran the **Path A: ScholarQABench Citation Bake-Off** across 5 expert-level queries spanning 5 domains, comparing pure parametric generation against Sanity Engine's retrieval architectures and long-context cached prompting.

### The Path A Scorecard

| System | Total Citations | Veracity Rate (% Real) | Hallucination Rate (% Fake) | Entailment Rate (% Sound) | Bluffing Rate (% Irrelevant) | Avg Context Words | Avg Latency |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **`Raw_Frontier_LLM`** | 9 | **0.0%** | **100.0%** | 0.0% | 0.0% | 0w | 1.7s |
| **`S2_relational`** | 5 | **80.0%** | **20.0%** | 80.0% | 0.0% | 715w | 8.7s |
| **`S3_graph`** | 5 | **60.0%** | **40.0%** | 60.0% | 0.0% | 841w | 1.5s |
| **`S_cached`** | 9 | **44.4%** | **55.6%** | 33.3% | 11.1% | 22,832w | 3.7s |

---

## 2. Key Findings

```mermaid
flowchart TD
    subgraph Raw_LLM ["Raw Frontier LLM (Parametric)"]
        R1["Generates 9 Citations"] --> R2["0% Real Quotes (100% Hallucinated)"]
        R2 --> R3["Plausible sounding authors, titles, & math"]
        R3 --> R4["Zero character offset matches on disk"]
    end

    subgraph Cached ["S_cached (Long-Context 23k words)"]
        C1["Generates 9 Citations"] --> C2["44.4% Exact Verbatim Quotes"]
        C2 --> C3["55.6% Paraphrased / Altered Quotes"]
        C3 --> C4["11.1% Citation Bluffing (Irrelevant/Contradictory)"]
    end

    subgraph Sanity_Engines ["Sanity Engine (S2 & S3)"]
        S1["Retrieves Targeted Chunks (~750w)"] --> S2["60%–80% Exact Verbatim Quotes"]
        S2 --> S3["0% Citation Bluffing"]
        S3 --> S4["Deterministic quote snapping to disk offsets"]
    end
```

### 1. Raw Frontier LLMs Suffer 100% Citation Hallucination
When prompted to produce academic claims backed by exact citations and verbatim quotes, **Gemini 3.8 Flash failed on 9 out of 9 citations (100% hallucination rate)**. 
- The generated quotes sounded authoritative, fluent, and technically accurate (e.g., citing *Kinsler et al., Fundamentals of Acoustics* or *Pathria & Beale, Statistical Mechanics*).
- However, **none of these quotes existed verbatim in the canonical literature**. The model synthesized plausible quotes from its parametric memory, demonstrating why ungrounded LLMs cannot be trusted for academic attribution.

### 2. Context Caching Does Not Solve Citation Hallucination (55.6% Failure)
Feeding entire textbook sections (~22,832 words per query) into $S_{\text{cached}}$ improved verbatim grounding compared to the raw model (achieving 44.4% veracity), but **55.6% of its citations still failed exact verification**:
- Even with the text in-context, LLMs have an intrinsic propensity to **summarize, paraphrase, or slightly mutate sentences** rather than reproducing exact character-for-character quotes.
- $S_{\text{cached}}$ also exhibited **citation bluffing (11.1%)**: in query `SQA_02`, it quoted an equation from Berg (1993) but misattributed the formula $k_1/m$ to root-mean-square velocity instead of mean-square velocity.

### 3. Sanity Engine Delivers Verifiable Grounding (80% Veracity, 0% Bluffing)
$S_2$ (Relational DB) achieved an **80.0% verbatim veracity rate** and an **80.0% logical entailment rate** with **0% citation bluffing**:
- Context size remained compact (~715 words), reducing hallucination surface area by **32×** compared to cached long context.
- Citations produced by $S_2$ and $S_3$ snap deterministically to source chunk IDs (`c2`, `c66`) and page numbers, enabling instant cryptographic or offset verification.

---

## 3. Query-by-Query Deep Dive & Concrete Examples

### Query `SQA_01` (Physics / Wave Mechanics)
> *"How does the characteristic acoustic impedance mismatch between two media govern boundary reflection and transmission of acoustic power?"*

* **`Raw_Frontier_LLM`**:
  * *Claim*: Pressure reflection coefficient depends on impedance difference divided by sum.
  * *Hallucinated Quote*: `"The pressure reflection coefficient R is given by R = (z2 - z1) / (z2 + z1)..."`
  * *Hallucinated Source*: *Kinsler, L. E. et al. (2000). Fundamentals of Acoustics.*
  * *Veracity Gate*: **FAILED (0 matches across 12,320 chunks)**.
* **`S_cached`**:
  * Attempted to quote Feynman Vol 1 on adiabatic sound speed, but paraphrased the text:
  * *Veracity Gate*: **FAILED (Paraphrased text rather than exact quote)**.
* **`S2_relational` / `S3_graph`**:
  * Recognized insufficient explicit acoustic impedance boundary claims in the local sample index and refrained from hallucinating false citations.

---

### Query `SQA_02` (Biophysics / Equipartition Theorem)
> *"According to equipartition theory, what is the thermal kinetic energy per spatial degree of freedom for microscopic particles in aqueous suspension, and how does thermal velocity scale with temperature?"*

* **`Raw_Frontier_LLM`**:
  * Cited Pathria & Beale (2011) and Atkins Physical Chemistry (2014) with fabricated quotes.
  * *Veracity Gate*: **FAILED (100% Hallucination)**.
* **`S2_relational`**:
  * *Claim*: Average kinetic energy per spatial degree of freedom is $kT/2$.
  * *Verbatim Quote*: `"A particle at absolute temperature T has, on the average, a kinetic energy associated with movement along each axis of kT/2, where k is Boltzmann's constant."`
  * *Source*: Howard Berg, *Random Walks in Biology (1993)*, p. 2 (Chunk `c2`).
  * *Veracity Gate*: **VERIFIED (Exact disk match, 100% Entailed)**.
* **`S_cached`**:
  * Successfully quoted Berg for $kT/2$, but bluffed on the second citation by conflating mean-square and root-mean-square derivations.

---

### Query `SQA_03` (Neurophysiology / Resting Membrane Potential)
> *"What specific ionic permeability mechanisms establish the resting membrane potential in neuronal cells?"*

* **`Raw_Frontier_LLM`**:
  * Fabricated quotes from Kandel *Principles of Neural Science* and Purves *Neuroscience*.
  * *Veracity Gate*: **FAILED**.
* **`S2_relational`**:
  * Generated 3 citations from Johnston & Wu and Alberts:
  * Quote 1: `"However, switch-ing off the pump does not abolish the major component of the resting potential, which is generated by the K+ equilibrium mechanism just described."` -> **VERIFIED**.
  * Quote 2: `"...the more permeable the membrane for a given ion, the more strongly the membrane potential tends to be driven toward the equilibrium value for that ion."` -> **VERIFIED**.
  * Veracity: **66.7%**, Entailment: **100% of verified quotes**.
* **`S3_graph`**:
  * Linked claim graph edges directly to Johnston & Wu (1995) p. 77:
  * Quote: `"The total membrane current in figure 3.4 can be written as I = lc + IK + INU + Icu"` -> **VERIFIED**.

---

### Query `SQA_05` (Information Theory / Shannon Capacity)
> *"How does the Shannon channel capacity of a communication channel mathematically depend on signal power and noise variance?"*

* **`Raw_Frontier_LLM`**:
  * Fabricated quote from Shannon's 1948 Bell System paper: `"The capacity C of a channel of band W perturbed by white thermal noise power N is given by C = W log(1 + P/N)..."`
  * *Veracity Gate*: **FAILED**.
* **`S_cached`**:
  * Directly cited Cover & Thomas (2006) with verbatim equations from the 26,000-word context window:
  * Quote: `I(X ;Y) = h(Y) − h(Z) (9.14) ≤ 1/2 log 2πe(P + N) − 1/2 log 2πeN (9.15) = 1/2 log(1 + P/N). (9.16)`
  * *Veracity Gate*: **VERIFIED (Exact disk match, 100% Entailed)**.

---

## 4. Architectural Comparison & Trade-Offs

| Metric | Raw Frontier LLM | Sanity Engine Relational ($S_2$) | Sanity Engine Graph ($S_3$) | Sanity Engine Cached ($S_{\text{cached}}$) |
|---|:---:|:---:|:---:|:---:|
| **Citation Veracity** | 0.0% | **80.0%** | 60.0% | 44.4% |
| **Citation Bluffing** | N/A (all fake) | **0.0%** | **0.0%** | 11.1% |
| **Token Consumption** | ~400 tokens | ~900 tokens | ~1,100 tokens | **~29,000 tokens** |
| **API Cost Ratio** | $1\times$ | $2.2\times$ | $2.5\times$ | **$32.5\times$** |
| **Query Latency** | 1.7s | 8.7s | **1.5s** | 3.7s |
| **Traceability** | None (Parametric) | Exact chunk ID (`c2`) | Exact graph node | Page/Window range |

---

## 5. Strategic Recommendations

1. **Enforce Quote Snapping on Long Context**:
   When using long-context cached models ($S_{\text{cached}}$), never trust quotes emitted by the model without a secondary deterministic regex or fuzzy-matcher pass that snaps the quote to the nearest exact character slice in the cached text.
2. **Combine $S_3$ Graph with JIT Extraction**:
   $S_3$ provides the lowest latency (1.5s) and structural claim verification. Feeding JIT-extracted claim triples directly to verification yields high veracity while maintaining sub-2-second response times.
3. **ScholarQABench as Continuous CI**:
   Run `chunklab/run_scholarqa_bakeoff.py` as a regression test before releasing prompt or retrieval updates to prevent citation drift.

---
*Generated by Sanity Engine Benchmark Suite — ChunkLab (October 2026).*
