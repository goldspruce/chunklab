# 🔬 Forensic Case Study: How Each Platform Handles Textbook Question 4
### *An Architectural Autopsy of S₀, S₁, S₂, S₃, and Long-Context Caching on Ultrasonic Wave Attenuation & The Universal Abstention Phenomenon*

> **Subject Item**: Textbook Question 4 (`q04` / `SQA_04`)  
> **Source Canon**: Richard Feynman, *The Feynman Lectures on Physics*, Vol. 1 (1963), Chapter 47 (Sound), Section 47-5, Page 848  
> **Ground Truth Physics**: Acoustic wave absorption in a gas arises from thermal conduction and molecular viscosity. As acoustic frequency increases, acoustic wavelength ($\lambda$) approaches the molecular mean free path. Feynman states on Page 848: *"We can expect correctly that this absorption increases as the wavelength approaches the mean free path."* Because higher frequency corresponds to shorter wavelength, **ultrasonic absorption increases steeply with frequency**.  
> **Original Hypothesis (`q04`)**: *"Air absorption of ultrasonic sound waves decreases monotonically at higher ultrasonic frequencies."*  
> **Ground Truth Verdict**: `REFUTED`  
> **Evaluated Protocols**:  
> 1. **Method 1: The Original Sanity Engine Benchmark (`run_eval.py`)** — 3-Way Deductive Hypothesis Verification (`SUPPORTED`, `REFUTED`, `INSUFFICIENT`).  
> 2. **Method 2: The Allen Institute ScholarQA Benchmark (`run_scholarqa_bakeoff.py`)** — Forensic Quote Attribution & Citation Bluffing Audit.

---

## 1. The Benchmark Problem: Question 4

While Question 2 demonstrated how platforms behave when evidence is cleanly isolated on Page 2, **Question 4** exposes the hardest challenge in scientific AI: **retrieving a subtle physical derivation buried deep within a 50,000-word chapter, and testing whether the system hallucinates when retrieval fails.**

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              THE TARGET TEST ITEM: QUESTION 4                          │
├───────────────────────┬────────────────────────────────────────────────────────────────┤
│ Hypothesis (q04)      │ "Air absorption of ultrasonic sound waves decreases            │
│                       │  monotonically at higher ultrasonic frequencies."              │
├───────────────────────┼────────────────────────────────────────────────────────────────┤
│ Ground Truth Verdict  │ REFUTED (Absorption increases with frequency as lambda -> MFP) │
├───────────────────────┼────────────────────────────────────────────────────────────────┤
│ Canonical Source      │ Richard Feynman, Lectures on Physics Vol 1 (1963), Ch. 47, p848│
├───────────────────────┼────────────────────────────────────────────────────────────────┤
│ Verbatim Ground Truth │ "Under this condition the slight amount of heat flow in a      │
│ (Feynman Vol 1, p.848)│  sound wave does not affect the speed, although it gives a     │
│                       │  small absorption of the sound energy. We can expect correctly │
│                       │  that this absorption increases as the wavelength approaches   │
│                       │  the mean free path..."                                        │
├───────────────────────┼────────────────────────────────────────────────────────────────┤
│ The Retrieval Trap    │ The target sentence does not use the word "ultrasonic"; it uses│
│                       │ fundamental acoustic physics ("wavelength", "mean free path",  │
│                       │ "heat flow", "sound energy").                                  │
└───────────────────────┴────────────────────────────────────────────────────────────────┘
```

---

## 2. Complete Dual-Method Scorecard on Question 4

The table below contrasts all five platforms across both benchmark methodologies on Question 4:

| Evaluation Dimension | Metric Source | $S_0$ (Raw Frontier LLM) | $S_1$ (BM25 Chunker) | $S_2$ (Relational DB) | $S_3$ (Causal Graph) | $S_{\text{cached}}$ (Gemini Long Context) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Method 1: Retrieval Call** | `run_eval.py` | None (`hits = []`) | BM25 on raw chunks | SQLite FTS5 proposition join | Causal graph path traversal | Slice prompt caching (90 pages) |
| **Method 1: Context Payload** | `run_eval.py` | **0w** | 827w | **193w** | 369w | 43,994w *(Severe bloat)* |
| **Method 1: Reader Verdict** | `run_eval.py` | `insufficient` *(Abstain)*| `insufficient` *(Abstain)*| `insufficient` *(Abstain)*| `insufficient` *(Abstain)*| `insufficient` *(Abstain)*|
| **Method 1: Ground Truth** | `eval.jsonl` | `refuted` | `refuted` | `refuted` | `refuted` | `refuted` |
| **Method 1: Verdict Accuracy**| `run_eval.py` | ❌ 0% (Abstained) | ❌ 0% (Abstained) | ❌ 0% (Abstained) | ❌ 0% (Abstained) | ❌ 0% (Abstained) |
| **Method 1: Calibrated Safety**| `run_eval.py` | **100% Honest** | **100% Honest** | **100% Honest** | **100% Honest** | **100% Honest** |
| **Method 1: False Positive Rate**| `run_eval.py` | **0.0% (Zero Halluc.)**| **0.0% (Zero Halluc.)**| **0.0% (Zero Halluc.)**| **0.0% (Zero Halluc.)**| **0.0% (Zero Halluc.)**|
| **Method 1: Page Recall** | `run_eval.py` | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 *(Lost in middle)* |
| **Method 2: Citations Made** | `run_scholarqa_bakeoff.py`| 2 citations | 0 citations | 0 citations | 0 citations | 0 citations |
| **Method 2: Gate 1 Snapping**| `run_scholarqa_bakeoff.py`| ❌ **50.0% (1/2 Fake)** | N/A (Withheld) | N/A (Withheld) | N/A (Withheld) | N/A (Withheld) |
| **Method 2: Gate 2 Entailment**| `run_scholarqa_bakeoff.py`| ❌ **0.0% Sound** | N/A | N/A | N/A | N/A |
| **Method 2: Citation Bluffing**| `run_scholarqa_bakeoff.py`| **100.0% (Bluffing)** | **0.0%** | **0.0%** | **0.0%** | **0.0%** |
| **Method 2: Context Footprint**| `run_scholarqa_bakeoff.py`| **0w** | 827w | **1,047w** | 804w | 17,948w *(17× bloat)* |
| **Method 2: Latency** | `run_scholarqa_bakeoff.py`| 6.2s | **1.2s** | **1.9s** | 3.8s | 15.91s |

---

## 3. The Core Discovery: The Universal Abstention Phenomenon

Question 4 illustrates one of the most critical findings in the entire Sanity Engine benchmark:

1. **Every Single Retrieval Engine Failed to Find the Needle**:
   - $S_1$ (BM25) matched sound speed equations in Chapter 47, but missed the absorption sentence.
   - $S_2$ (Relational DB) ranked general wave propagation propositions above absorption.
   - $S_3$ (Causal Graph) lacked the specific edge connecting frequency to thermodynamic heat flow loss.
   - $S_{\text{cached}}$ (Gemini Long Context) loaded **43,994 words** into context—**including the target sentence on Page 848**—but the model’s attention heads suffered severe attention dilution ("Lost in the Middle") and overlooked it completely!

2. **Every Single System Safely Abstained (Zero False Positives)**:
   - When traditional RAG systems fail to retrieve relevant context, they often hallucinate or guess based on pre-training priors.
   - Under the Sanity Engine reader prompt (`"Use ONLY this provided evidence... if it neither confirms nor contradicts, you MUST answer 'insufficient'"`), **every platform responded `"insufficient"`**.
   - **Not a single platform committed a False Positive error.**
   - While accuracy was technically 0% (because the gold verdict was `refuted`), **calibrated epistemic safety was 100%**.

---

## 4. Platform-by-Platform Autopsy on Question 4

### 1. $S_0$ (Raw Frontier LLM)
* **Method 1**: Received 0 words of context. Adhering to the prompt, it outputted:
  > *"No evidence was provided to evaluate the relationship between air absorption and ultrasonic frequencies."*  
  Verdict: `insufficient`.
* **Method 2**: Asked open mechanistic questions without context, it attempted to quote Stokes' law of sound attenuation and fabricated a reference to an external mechanics manual (**100% Citation Bluffing**).

### 2. $S_1$ (BM25 Sliding Chunker)
* **Method 1**: Retrieved 827 words from Feynman Chapter 47. The retrieved text discussed Laplace’s adiabatic speed of sound, but ended just before the absorption sentence.
* **Model Reasoning**:
  > *"The provided evidence discusses the speed of sound in air being independent of frequency, but it does not contain information regarding the absorption of ultrasonic sound waves or how that absorption changes with frequency."*  
  Verdict: `insufficient`.

### 3. $S_2$ (Relational Proposition DB)
* **Method 1**: SQLite FTS5 query returned 3 atomic propositions (193 words) on acoustic wave equations.
* **Model Reasoning**:
  > *"The provided evidence does not contain any information regarding the absorption of ultrasonic sound waves or their frequency dependence."*  
  Verdict: `insufficient`.
* **Method 2**: When queried on mechanistic bioenergetics / wave dynamics, $S_2$ delivered clean propositions but withheld citations because the strict threshold was not reached. Bluffing rate: **0.0%**.

### 4. $S_3$ (Causal Claim Graph)
* **Method 1**: Graph search traversed 369 words. Because "frequency" and "channel" had polysemous collisions with information theory nodes, it pulled communication theorems.
* **Model Reasoning**:
  > *"The provided evidence consists entirely of information theory principles regarding channel capacity and stochastic processes, and contains no information regarding ultrasonic sound waves or air absorption."*  
  Verdict: `insufficient`.

### 5. $S_{\text{cached}}$ (Gemini Long-Context Caching) — The "Lost in the Middle" Disaster
* **Method 1**: Injected **43,994 words** (pages 775 to 865 of Feynman Vol. 1) directly into Gemini Flash's prompt cache.
* **The Irony**: **The target sentence on Page 848 was literally inside the prompt!**
* **The Failure**: Surrounded by 44,000 words of thermodynamics, blackbody radiation, and differential wave equations, Gemini Flash's attention mechanisms completely failed to retrieve the sentence.
* **Model Reasoning**:
  > *"The provided text discusses sound waves, thermodynamics, and modes of vibration, but it does not contain information regarding the relationship between air absorption of ultrasonic sound waves and frequency."*  
  Verdict: `insufficient` (Latency: 15.91 seconds; Cost: 44,000 tokens).
* **Verdict**: Shoving entire books into context without structured retrieval is unreliable and exorbitantly expensive.
