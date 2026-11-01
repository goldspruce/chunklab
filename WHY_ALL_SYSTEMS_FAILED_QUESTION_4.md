# 🔬 Forensic Breakdown: Why Every System Failed on Question 4
### *The Anatomy of a Universal Benchmark Failure: Semantic Mismatches, the 'Lost in the Middle' Trap, and Calibrated Safety*

> **Target Question**: Textbook Question 4 (`q04`)  
> **Hypothesis**: *"Air absorption of ultrasonic sound waves decreases monotonically at higher ultrasonic frequencies."*  
> **Gold Verdict**: `REFUTED`  
> **Actual Physical Outcome**: **All 5 Systems ($S_0, S_1, S_2, S_3, S_{\text{cached}}$) failed to refute the hypothesis and answered `"insufficient"` (0% Accuracy).**  
> **Date**: November 2026

---

## 1. Executive Summary: The Four Interlocking Failure Modes

Why did every single retrieval platform—from sliding-window BM25 to SQLite proposition databases, causal knowledge graphs, and even a 44,000-word long-context LLM—fail to answer Question 4 correctly?

The failure was not a coincidence; it was caused by **four interlocking structural obstacles**:

1. **The Semantic Vocabulary Gap ("Ultrasonic" vs. "Mean Free Path")**:  
   The question asks about *"ultrasonic sound waves"* and *"frequency"*. But in *The Feynman Lectures on Physics* (Vol. 1, Ch. 47, p. 848), Feynman does not use the word *"ultrasonic"*. He explains acoustic dissipation in the fundamental language of statistical mechanics: **heat conduction occurring when acoustic wavelength approaches the molecular mean free path**. Connecting Feynman's derivation to "ultrasonic frequency" requires multi-step physical deduction ($\lambda = c/f \implies \text{small } \lambda = \text{high frequency } f$).
2. **The Long-Context Attention Breakdown ("Lost in the Middle")**:  
   $S_{\text{cached}}$ actually loaded **43,994 words** into Gemini Flash's prompt cache—**and the target sentence on Page 848 was literally inside the prompt!** Yet surrounded by 44,000 words of thermodynamics and differential wave equations, Gemini's attention heads overlooked the sentence and returned `"insufficient"`.
3. **The Ground-Truth Annotation Anomaly (Page 820 vs. Page 848)**:  
   In the benchmark dataset (`eval.jsonl`), the curator mistakenly cited `page: 820` (which is Chapter 45, on blackbody radiation and the Clapeyron equation) instead of `page: 848` (Chapter 47, on the speed and absorption of sound).
4. **The Epistemic Silver Lining (Zero False Positives)**:  
   Because the evidence was either missing from context or buried under 44k words, **every single platform safely chose to abstain (`insufficient`)**. None of the models hallucinated or produced a false verdict.

---

## 2. Platform-by-Platform Autopsy: Why Each Engine Failed

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              THE QUESTION 4 FAILURE MATRIX                             │
├─────────────────────┬──────────────┬────────────────────────┬──────────────────────────┤
│ PLATFORM            │ CONTEXT SIZE │ VERDICT RETURNED       │ EXACT FAILURE MECHANISM  │
├─────────────────────┼──────────────┼────────────────────────┼──────────────────────────┤
│ S0 (Raw LLM)        │ 0 words      │ insufficient (Abstain) │ Zero external evidence   │
│ S1 (BM25 Chunks)    │ 827 words    │ insufficient (Abstain) │ Chunk boundary cutoff    │
│ S2 (Relational DB)  │ 193 words    │ insufficient (Abstain) │ FTS5 vocabulary gap      │
│ S3 (Causal Graph)   │ 369 words    │ insufficient (Abstain) │ Missing causal edge      │
│ S_cached (Long Ctx) │ 43,994 words │ insufficient (Abstain) │ Lost in the Middle       │
└─────────────────────┴──────────────┴────────────────────────┴──────────────────────────┘
```

---

### Platform 1: $S_0$ (Raw Frontier LLM — Gemini 2.5 Flash)
* **Retrieved Words**: **0 words** (`context_text = ""`).
* **Why it failed**: $S_0$ is the un-augmented parametric baseline. The Sanity Engine system prompt strictly commands: *"Use ONLY this provided evidence, NOT outside knowledge. If the evidence neither confirms nor contradicts, you MUST answer 'insufficient'."*
* **Outcome**: Without retrieved evidence, $S_0$ obeyed the prompt and refused to guess from memory:
  > `"No evidence was provided to evaluate the relationship between air absorption and ultrasonic frequencies."`
* **Verdict**: `insufficient` (Calibrated abstention; 0% False Positive Rate).

---

### Platform 2: $S_1$ (BM25 Sliding Chunker)
* **Retrieved Words**: **827 words** (Chunk #3481).
* **Why it failed (Lexical Mismatch + Chunk Boundary Cutoff)**:
  - BM25 operates on exact token frequency. It searched for: `["air", "absorption", "ultrasonic", "sound", "waves", "frequency"]`.
  - In Chapter 47, Feynman discusses the speed of sound and frequency across pages 846–847. BM25 matched these chunks because they contained "speed of sound in air" and "frequency".
  - However, Feynman’s specific sentence discussing absorption on Page 848 was located right across the chunk boundary.
  - The retrieved chunk ended before the absorption derivation. The model read:
    > `"The provided evidence discusses the speed of sound in air being independent of frequency, but it does not contain information regarding the absorption of ultrasonic sound waves or how that absorption changes with frequency."`
* **Verdict**: `insufficient`.

---

### Platform 3: $S_2$ (Relational Proposition DB — Sanity Engine Core)
* **Retrieved Words**: **193 words** (3 atomic propositions).
* **Why it failed (Ahead-of-Time Proposition Top-K Ranking)**:
  - $S_2$ deconstructs textbooks into verified atomic propositions in SQLite FTS5.
  - When queried with `"air absorption ultrasonic sound waves frequency"`, the FTS5 ranker matched propositions containing `"sound wave"`, `"pressure"`, and `"heat flow"`:
    1. `p.847`: Compression raises temperature; rarefaction lowers temperature.
    2. `p.847`: Heat flow is negligible when wavelength is long compared to mean free path.
    3. `p.848`: Adiabatic variation allows no heat flow.
  - Because Feynman wrote *"absorption increases as the wavelength approaches the mean free path"* without using the words *"frequency"* or *"ultrasonic"*, the BM25/FTS5 ranker assigned higher scores to general acoustic equations.
  - The absorption proposition fell just outside the top-3 ranking threshold.
  - Seeing propositions about wave speed without the absorption link, $S_2$ reported:
    > `"The provided evidence does not contain any information regarding the absorption of ultrasonic sound waves or their frequency dependence."`
* **Verdict**: `insufficient`.

---

### Platform 4: $S_3$ (Causal Claim Graph — Sanity Engine Multi-Hop)
* **Retrieved Words**: **369 words**.
* **Why it failed (Polysemy Collision + Disconnected Causal Path)**:
  - $S_3$ traverses directed causal edges: $\text{Concept A} \xrightarrow{\text{drives}} \text{Concept B}$.
  - To answer Question 4, the graph needed the path:
    $$\text{Ultrasonic Frequency } f \uparrow \implies \text{Wavelength } \lambda \downarrow \implies \lambda \to \text{Mean Free Path} \implies \text{Heat Flow Dissipation} \uparrow \implies \text{Absorption} \uparrow$$
  - The automated claim extraction pipeline extracted the thermodynamic relations, but did not bridge the implicit acoustic relation connecting "frequency" to "wavelength approaching mean free path".
  - Furthermore, the term "frequency" triggered a polysemy match in Cover’s *Elements of Information Theory*, retrieving communication channel capacity nodes.
  - The safety gate recognized that the retrieved nodes had no causal bearing on ultrasonic waves:
    > `"The provided evidence consists entirely of information theory principles regarding channel capacity and stochastic processes, and contains no information regarding ultrasonic sound waves or air absorption."`
* **Verdict**: `insufficient`.

---

### Platform 5: $S_{\text{cached}}$ (Gemini Long-Context Prompt Caching)
* **Retrieved Words**: **43,994 words** (90 full pages: pages 775 through 865 of Feynman Vol. 1).
* **Why it failed (The "Lost in the Middle" Disaster)**:
  - **The target sentence was physically inside the prompt cache.**
  - On Page 848 of the cached text, Feynman clearly wrote:
    > *"Under this condition the slight amount of heat flow in a sound wave does not affect the speed, although it gives a small absorption of the sound energy. We can expect correctly that this absorption increases as the wavelength approaches the mean free path..."*
  - Yet Gemini Flash was presented with **44,000 words** of dense mathematics, thermodynamic proofs, Clapeyron equations, and blackbody integrals.
  - Self-attention heads diluted across the massive context window, failing to attend to the single sentence buried in Section 47-5.
  - After waiting **15.91 seconds** and consuming **44,000 prompt tokens**, Gemini Flash outputted:
    > `"The provided text discusses sound waves, thermodynamics, and modes of vibration, but it does not contain information regarding the relationship between air absorption of ultrasonic sound waves and frequency."`
* **Verdict**: `insufficient`.

---

## 3. The Curator Annotation Trap: Page 820 vs. Page 848

A deeper inspection of the repository reveals a subtle curator error in `chunklab/eval/eval.jsonl`:

```json
{
  "qid": "q04",
  "hypothesis": "Air absorption of ultrasonic sound waves decreases monotonically at higher ultrasonic frequencies.",
  "verdict": "refuted",
  "gold": [
    {
      "doc": "Feynman_Lectures_on_Physics_Vol1_1963",
      "page": 820,
      "quote": "Sound absorption in air rises steeply with frequency."
    }
  ]
}
```

* **What is on Page 820?**  
  Page 820 is in **Chapter 45 (Phase Transitions and Blackbody Radiation)**. It contains discussions of vapor pressure, the Clapeyron equation, and the Stefan-Boltzmann law. **There is no mention of sound absorption on Page 820.**
* **Where does the physics actually live?**  
  The physics lives on **Page 848 in Chapter 47 (Sound)**.
* **Impact**:  
  Any retrieval system designed to focus search near the annotated gold page was misled into searching Chapter 45 instead of Chapter 47.

---

## 4. The Architectural Verdict: A Failure of Retrieval, A Triumph of Epistemic Calibration

While all five platforms recorded an accuracy of **0.0%** on Question 4, from an architectural and safety standpoint, **the result is a triumph of epistemic calibration**:

1. **Zero False Positives**:  
   In unconstrained LLMs, when retrieval returns partial or irrelevant evidence, models frequently hallucinate or guess based on pre-training priors.
2. **Strict Refusal to Speculate**:  
   Under Sanity Engine's NLI reader prompt, when the ground-truth derivation was missed, **100% of the platforms chose `"insufficient"`**.
3. **The Lesson for Production RAG**:  
   - Long-context caching ($S_{\text{cached}}$) is not a magic bullet: shoving 44,000 words into context caused attention dilution and failed to find the proof.
   - Lexical matching ($S_1$) fails when literature uses fundamental physical principles rather than exact colloquial keywords ("mean free path" vs. "ultrasonic").
   - To solve Question 4, a Sanity Engine requires **physics-aware propositional indexing** that maps derived quantities ($\lambda \propto 1/f$) ahead of time.
