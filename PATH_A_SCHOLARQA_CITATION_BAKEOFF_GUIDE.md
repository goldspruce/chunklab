# Path A: ScholarQABench Citation Hallucination & Veracity Bake-Off

**Evaluation Specification & Experimental Design**  
*Benchmarking Citation Truthfulness, Hallucination Rates, and Logical Entailment*  
*Date: October 2026*

---

## 1. Executive Overview & The Problem

In 2024–2026, researchers at the Allen Institute for AI and the University of Washington introduced **ScholarQABench** (*OpenScholar*). Their headline finding exposed a fundamental vulnerability of commercial frontier models:

> **Frontier LLMs (such as GPT-4o and Claude 3.5 Sonnet) hallucinate scientific citations 78% to 90% of the time.**  
> They invent plausible-sounding author names, fabricate DOIs, and misattribute real experimental findings to support their claims.

**Path A** directly evaluates this failure mode by running a head-to-head bake-off between:
1. **Raw Frontier LLMs (Gemini 3.8 Flash):** Operating purely from parametric memory.
2. **Sanity Engine $S_2$ (Relational Claims DB):** Operating over structured, character-offset anchored claims.
3. **Sanity Engine $S_3$ (Claim Graph):** Operating over connected causal relations and entity bridges.
4. **Sanity Engine Cached ($S_{\text{cached}}$):** Operating over full, unchunked cached textbook contexts.

---

## 2. Experimental Design: The 4-Arm Comparison

```
                         THE 4-ARM CITATION BAKE-OFF
                         
       [ Expert Scientific Query from ScholarQA / Physical Literature ]
                                     │
      ┌─────────────────┬────────────┴────┬─────────────────┐
      ▼                 ▼                 ▼                 ▼
[ Arm 1: Raw LLM ]  [ Arm 2: S2 ]     [ Arm 3: S3 ]    [ Arm 4: S_cached ]
(Pure Parametric)   (Relational DB)   (Claim Graph)    (Full Long-Context)
      │                 │                 │                 │
      └─────────────────┴────────────┬────┴─────────────────┘
                                     │
                                     ▼
                  [ The 2-Gate Veracity Gauntlet ]
                  
                  Gate 1: verify_quote() (Text Veracity)
                  • Snaps quote to exact character offset in corpus.
                  • Label: "verified" vs. "hallucinated / failed".
                  
                  Gate 2: auto_entail() (Logical Entailment)
                  • Does the quote logically prove the claim?
                  • Label: "supports" vs. "partly" vs. "not" (bluffing).
                                     │
                                     ▼
                  [ Metrics Output ]
                  1. Citation Hallucination Rate (% Failed)
                  2. Citation Veracity Rate (% Verified)
                  3. Citation Entailment Rate (% Logically Sound)
                  4. Context Word Consumption & Latency
```

---

## 3. The 3 Core Evaluation Metrics

### Metric 1: Citation Hallucination Rate (%)
* **Definition:** The percentage of cited quotes/sources that **do not exist** word-for-word in the actual scientific literature.
* **Calculation:**  
  $$\text{Hallucination Rate} = \frac{\text{Failed Citations}}{\text{Total Citations Generated}} \times 100\%$$
* **Expected Result:**
  * Raw Frontier LLMs: **$\sim 80\%\text{ to }90\%$** hallucination.
  * Sanity Engine $S_2 / S_3$: **$0.0\%$** hallucination (mathematically anchored to disk).

### Metric 2: Citation Bluffing Rate (`auto_entail: not`)
* **Definition:** The percentage of real, existing quotes cited by the model that **do not logically support the claim being made**.
* **Why it matters:** An AI can cite a real sentence from Feynman, but if that sentence discusses Clausius-Clapeyron vapor pressure while the claim is about acoustic reflection, it is **citation bluffing**.

### Metric 3: Context Words & Efficiency
* **Definition:** How many words/tokens were consumed to produce the verified answer.
  * $S_2$: $\approx 350\text{ words}$
  * $S_3$: $\approx 390\text{ words}$
  * $S_{\text{cached}}$: $\approx 30,000\text{ to }90,000\text{ words}$
  * Raw LLM: $0\text{ context words}$ (pure parametric memory)

---

## 4. Test Queries Across Canonical Science

The benchmark tests core scientific mechanisms across physics, neuroscience, biophysics, biochemistry, and information theory:

1. **Acoustic Wave Boundary Reflection:** Impedance ratio mismatch reflection at a solid-gas boundary.
2. **Thermal Equipartition Kinetics:** Molecular kinetic energy scaling and Brownian drift at low Reynolds numbers.
3. **Neuronal Resting Membrane Dynamics:** Potassium conductance and Nernst equilibrium potentials.
4. **Bioenergetic Free Energy Coupling:** Phosphoanhydride bond cleavage in endergonic reactions.
5. **Channel Capacity Limits:** Shannon-Hartley log scaling against noise power.

---

## 5. Summary Table Template

| System | Citations Generated | Veracity Rate (% Real) | Hallucination Rate (% Fake) | Entailment Rate (% Sound) | Bluffing Rate (% Irrelevant) | Avg Context Words |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Raw Frontier LLM** | — | Low (< 25%) | **High (> 75%)** | Low | High | 0w |
| **Sanity Engine $S_2$** | — | **100.0%** | **0.0%** | High | Low | ~350w |
| **Sanity Engine $S_3$** | — | **100.0%** | **0.0%** | High | Low | ~390w |
| **$S_{\text{cached}}$** | — | Moderate (~50%) | Moderate (~50%) | Moderate | Moderate | ~50,000w |
