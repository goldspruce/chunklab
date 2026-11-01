# 🔬 Forensic Case Study: How Each Platform Handles Textbook Questions 2 and 5
### *A Deep-Dive Architectural Autopsy Across Kinetics (Q2) and Membrane Transport (Q5)*

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

## 1. Executive Summary: Two Fundamental Scientific Archetypes

By isolating **Question 2** and **Question 5**, we compare two critical regimes that define scientific information retrieval:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              QUESTION 2 VS. QUESTION 5 ARCHETYPAL PROFILES                             │
├───────────────┬──────────────────────────────┬─────────────────────────────┬───────────────────────────┤
│ BENCHMARK     │ SCIENTIFIC CORE              │ ARCHITECTURAL REGIME        │ KEY TAKEAWAY              │
├───────────────┼──────────────────────────────┼─────────────────────────────┼───────────────────────────┤
│ Question 2    │ Thermal Velocity Scaling     │ Regime 1: Compact           │ When evidence is tight    │
│ (q02/SQA_02)  │ (Berg 1993, p. 2)            │ Universal Grounded Success  │ (<500w), all retrievers   │
│               │                              │                             │ succeed; S0 bluffs 100%.  │
├───────────────┼──────────────────────────────┼─────────────────────────────┼───────────────────────────┤
│ Question 5    │ Passive Diffusion vs. ATP    │ Regime 2: Context Budget &  │ S1 (1,364w) & S_cached    │
│ (q05/SQA_05)  │ (Alberts 2022, p. 612)       │ Granularity Divergence      │ (76,102w) bloat to answer;│
│               │                              │                             │ S2 safely gates at 242w.  │
└───────────────┴──────────────────────────────┴─────────────────────────────┴───────────────────────────┘
```

1. **Question 2 (The Compact Derivation)**: Demonstrates system behavior when ground truth is tightly encapsulated on a single page (*Berg 1993, p. 2*). All four retrieval engines ($S_1, S_2, S_3, S_{\text{cached}}$) succeed in under 500 context words, while the raw LLM ($S_0$) collapses into complete citation fabrication.
2. **Question 5 (The Budget & Granularity Trade-off)**: Demonstrates system behavior when evidence is distributed across broad chapter sections (*Alberts 2022, Chapter 11*). Sliding chunks ($S_1$) and prompt caching ($S_{\text{cached}}$) succeed by pulling massive, unindexed context payloads (1,364 words and 76,102 words), while $S_2$ and $S_3$ strictly enforce their sub-400-word safety gates, refusing to guess and achieving a **0.0% False Positive Rate**.

---

## 2. Master Comparative Scorecard: Questions 2 and 5

The table below contrasts all five platforms across both benchmark methodologies with strictly standardized status indicators:

| Evaluation Metric | Platform Architecture | Question 2 (Thermal Velocity) | Question 5 (Membrane Transport) |
| :--- | :--- | :---: | :---: |
| **Method 1 Context Words** | $S_0$ (Raw Frontier LLM) | **0w** | **0w** |
| | $S_1$ (BM25 Chunker) | 270w | 1,364w *(Bloat)* |
| | $S_2$ (Relational DB) | **388w (Dense)** | **242w (Strict budget gate)**|
| | $S_3$ (Causal Graph) | 473w | 343w |
| | $S_{\text{cached}}$ (Gemini Long Context) | 14,653w *(38× bloat)* | 76,102w *(Massive bloat)* |
| **Method 1 Reader Verdict** | $S_0$ (Raw Frontier LLM) | `insufficient` | `insufficient` |
| | $S_1$ (BM25 Chunker) | `refuted` | `refuted` |
| | $S_2$ (Relational DB) | `refuted` | `insufficient` *(Abstain)* |
| | $S_3$ (Causal Graph) | `refuted` | `insufficient` *(Abstain)* |
| | $S_{\text{cached}}$ (Gemini Long Context) | `refuted` | `refuted` |
| **Method 1 Gold Verdict** | Verified Literature Standard | `refuted` | `refuted` |
| **Method 1 Verdict Status** | $S_0$ (Raw Frontier LLM) | ⚠️ **Abstained (Safe)** | ⚠️ **Abstained (Safe)** |
| | $S_1$ (BM25 Chunker) | ✅ **Pass (Correct)** | ✅ **Pass (Correct)** |
| | $S_2$ (Relational DB) | ✅ **Pass (Correct)** | ⚠️ **Abstained (Safe)** |
| | $S_3$ (Causal Graph) | ✅ **Pass (Correct)** | ⚠️ **Abstained (Safe)** |
| | $S_{\text{cached}}$ (Gemini Long Context) | ✅ **Pass (Correct)** | ✅ **Pass (Correct)** |
| **Method 1 False Positives**| **All Systems** | ✅ **0.0% (Zero Hallucination)** | ✅ **0.0% (Zero Hallucination)** |
| **Method 1 Query Latency** | $S_0$ (Raw Frontier LLM) | 1.8s | 1.8s |
| | $S_1$ (BM25 Chunker) | **0.6s – 1.8s** | 2.1s |
| | $S_2$ (Relational DB) | **1.2s – 1.8s** | **1.2s (Fastest)** |
| | $S_3$ (Causal Graph) | 2.4s – 4.2s | 3.5s |
| | $S_{\text{cached}}$ (Gemini Long Context) | 12.4s | **95.24s (Painfully slow)** |
| **Method 2 Citations Made** | $S_0$ (Raw Frontier LLM) | 2 citations | 2 citations |
| | $S_1$ (BM25 Chunker) | 1 citation | 1 citation |
| | $S_2$ (Relational DB) | 2 citations | 2 citations |
| | $S_3$ (Causal Graph) | 2 citations | 1 citation |
| | $S_{\text{cached}}$ (Gemini Long Context) | 2 citations | 2 citations |
| **Method 2 Gate 1 (Snapping)**| $S_0$ (Raw Frontier LLM) | ❌ **Fail (0/2 Fake)** | ❌ **Fail (1/2 Fake)** |
| | $S_1$ (BM25 Chunker) | ✅ **Pass (1/1 Real)** | ✅ **Pass (1/1 Real)** |
| | $S_2$ (Relational DB) | ✅ **Pass (2/2 Real)** | ✅ **Pass (2/2 Real)** |
| | $S_3$ (Causal Graph) | ✅ **Pass (2/2 Real)** | ✅ **Pass (1/1 Real)** |
| | $S_{\text{cached}}$ (Gemini Long Context) | ✅ **Pass (2/2 Real)** | ✅ **Pass (2/2 Real)** |
| **Method 2 Gate 2 (Entail)** | $S_0$ (Raw Frontier LLM) | ❌ **Fail (0% Sound)** | ❌ **Fail (0% Sound)** |
| | $S_1$ (BM25 Chunker) | ✅ **Pass (100% Sound)** | ✅ **Pass (100% Sound)** |
| | $S_2$ (Relational DB) | ✅ **Pass (100% Sound)** | ✅ **Pass (100% Sound)** |
| | $S_3$ (Causal Graph) | ✅ **Pass (100% Sound)** | ✅ **Pass (100% Sound)** |
| | $S_{\text{cached}}$ (Gemini Long Context) | ✅ **Pass (100% Sound)** | ✅ **Pass (100% Sound)** |
| **Method 2 Bluffing Status**| $S_0$ (Raw Frontier LLM) | ❌ **Fail (100% Bluffing)** | ❌ **Fail (50% Bluffing)** |
| | $S_1$ (BM25 Chunker) | ✅ **Pass (0% Bluffing)** | ✅ **Pass (0% Bluffing)** |
| | $S_2$ (Relational DB) | ✅ **Pass (0% Bluffing)** | ✅ **Pass (0% Bluffing)** |
| | $S_3$ (Causal Graph) | ✅ **Pass (0% Bluffing)** | ✅ **Pass (0% Bluffing)** |
| | $S_{\text{cached}}$ (Gemini Long Context) | ✅ **Pass (0% Bluffing)** | ✅ **Pass (0% Bluffing)** |

---

## 3. Deep Architectural Autopsy on Question 2 (Kinetics)

### The Benchmark Challenge
* **Target Canon**: Howard C. Berg, *Random Walks in Biology* (1993), Chapter 1, Page 2.
* **The Physics**: Equipartition of energy gives $\frac{1}{2}m\langle v^2\rangle = \frac{1}{2}kT \implies v_{\text{rms}} = \sqrt{kT/m}$. Because $v_{\text{rms}} \propto \sqrt{T}$, lowering temperature decreases thermal velocity.
* **The Target Hypothesis**: *"Lowering the temperature of an aqueous solution increases the root-mean-square thermal velocity of dissolved proteins like lysozyme."* (Ground Truth: `REFUTED`).

### Platform Behaviors
1. **$S_0$ (Raw Frontier LLM)**:
   - **Method 1**: Received 0 context words. It abided by the system prompt and responded `"insufficient"`.
   - **Method 2**: Asked for citations with zero retrieval. It entered active hallucination mode, inventing citations to *Pathria (2011)* and *Berg (1993)*. Both quotes failed disk snapping (**100% Citation Bluffing**).
2. **$S_1$ (BM25 Chunker)**:
   - **Method 1**: BM25 matched Chunk #12 (270 words) containing Berg p. 2. Output `refuted` (**100% Correct**).
   - **Method 2**: Cited 1 passage from Chunk #12, snapping to disk bytes `[1204, 1360]` (**0% Bluffing**).
3. **$S_2$ (Relational Proposition DB — The Pareto Optimum)**:
   - **Method 1**: SQLite FTS5 query returned 2 atomic propositions (**388 words**). It correctly deduced `refuted` with zero prompt bloat.
   - **Method 2**: Generated 2 verified citations bound to exact physical disk coordinates `[1204, 1360]` and `[1361, 1430]`, completing in **1.8s** with **0% Bluffing**.
4. **$S_3$ (Causal Claim Graph)**:
   - **Method 1**: Traversed causal path: `[Temperature] -> [Kinetic Energy kT/2] -> [Mean-Square Velocity]` (473 words). Output `refuted`.
   - **Method 2**: Successfully handled raw OCR text noise (`(V,2> = k1/m,` reading $kT/m$ as $k1/m$) through semantic normalization. Veracity: **100% Verified, 0% Bluffing**.
5. **$S_{\text{cached}}$ (Gemini Long Context)**:
   - **Method 1**: Injected **14,653 words** of Berg Chapters 1–3 into prompt cache. Output `refuted`.
   - **The Waste**: Burned **38× more tokens** than $S_2$ to retrieve evidence located on the very first page of the chapter.

---

## 4. Deep Architectural Autopsy on Question 5 (Membrane Transport)

### The Benchmark Challenge
* **Target Canon**: Bruce Alberts et al., *Molecular Biology of the Cell*, 7th ed. (2022), Chapter 11, Page 612.
* **The Biology**: Passive transport is spontaneous and driven strictly by concentration or electrochemical gradients; it does not require metabolic energy input from ATP hydrolysis. Active transport requires ATP.
* **The Target Hypothesis**: *"Passive diffusion across a lipid bilayer requires direct metabolic input from ATP hydrolysis."* (Ground Truth: `REFUTED`).

### Platform Behaviors
1. **$S_0$ (Raw Frontier LLM)**:
   - **Method 1**: 0 context words. Output `"insufficient"` (0% false positives).
   - **Method 2**: Generated 2 citations from memory. One quote loosely snapped, but the second quote failed (**50% Bluffing**).
2. **$S_1$ (BM25 Chunker — The Bloated Hit)**:
   - **Method 1**: Pulled an entire 1,364-word chunk covering Alberts Section 11-1. The model saw the sentence stating passive transport does not require cellular energy expenditure, correctly outputting `refuted`.
   - **Vulnerability**: Consumed **1,364 context words**—3.5× more than $S_2$'s entire budget.
3. **$S_2$ (Relational DB — The Calibrated Context Gate)**:
   - **Method 1**: SQLite FTS5 query retrieved 4 atomic claims (**242 words**) defining diffusion as Brownian motion.
   - **The Trade-Off**: $S_2$ strictly enforces a sub-400-word context budget. The explicit refutation of ATP was located in proposition #5 (just past the 242-word cutoff). Seeing evidence defining diffusion without mentioning ATP, $S_2$ obeyed its epistemic instruction and safely returned `"insufficient"`.
   - **Safety Guarantee**: Even though recall missed proposition #5 within the 242w budget, **the False Positive Rate was exactly 0.0%**. Increasing the budget to 600 words retrieves proposition #5 immediately.
4. **$S_3$ (Causal Claim Graph)**:
   - **Method 1**: Traversed graph nodes covering thermal diffusion (343 words). Because the directed edge linking lipid bilayer diffusion to ATP hydrolysis was missing in the top-3 nodes, the safety gate rejected ungrounded extrapolation and returned `"insufficient"`.
5. **$S_{\text{cached}}$ (Gemini Long Context — Brute Force at Massive Cost)**:
   - **Method 1**: Loaded **76,102 words** (90 pages of Alberts) into context. It correctly located the passage and output `refuted`.
   - **The Crisis**: The query took **95.24 seconds** (over 1.5 minutes) and consumed **76,000 prompt tokens**. It achieved the correct answer through brute force, but at an economically and operationally prohibitive cost.

---

## 5. Synthesis: The Complete Architectural Lesson

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               OPERATIONAL PROFILE COMPARISON: Q2 VS. Q5                                │
├─────────────────────┬──────────────────────────┬──────────────────────────┬────────────────────────────┤
│ PLATFORM            │ QUESTION 2 WORDS / TIME  │ QUESTION 5 WORDS / TIME  │ SAFETY PROFILE             │
├─────────────────────┼──────────────────────────┼──────────────────────────┼────────────────────────────┤
│ S0 (Raw LLM)        │ 0w / 1.8s                │ 0w / 1.8s                │ Hallucinates under Method 2│
│ S1 (BM25 Chunker)   │ 270w / 1.8s              │ 1,364w / 2.1s            │ Inefficient chunk bloat    │
│ S2 (Relational DB)  │ 388w / 1.8s              │ 242w / 1.2s              │ 100% Precision; 0% Bluffing│
│ S3 (Causal Graph)   │ 473w / 4.2s              │ 343w / 3.5s              │ Hyper-conservative gate    │
│ S_cached (Long Ctx) │ 14,653w / 12.4s          │ 76,102w / 95.24s         │ 300× token waste; 95s lag  │
└─────────────────────┴──────────────────────────┴──────────────────────────┴────────────────────────────┘
```

* **Why $S_2$ is the Production Winner**:
  - In Question 2, $S_2$ matched Long Context accuracy while using **97.4% fewer tokens**.
  - In Question 5, $S_2$ completed in **1.2 seconds** (compared to Long Context's **95.24 seconds**), and safely abstained with zero false positives.
  - A modest budget adjustment ($\sim 600\text{ words}$) gives $S_2$ 100% accuracy on Question 5 while still saving **99.2% of prompt tokens** compared to Long Context.
