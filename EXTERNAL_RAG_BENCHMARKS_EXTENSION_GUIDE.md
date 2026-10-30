# Extending Sanity Engine & Chunklab: External Scientific RAG Benchmarks

**Strategic Evaluation Roadmap & Comparative Analysis**  
*Evaluating Sanity Engine Against Frontier Scientific Retrieval Standards*  
*Date: October 2026*

---

## 1. Executive Summary

This guide outlines three concrete, actionable evaluation pathways to extend testing beyond our 10-item canonical textbook suite. It analyzes the methodologies, strengths, weaknesses, and resource requirements of testing Sanity Engine ($S_1, S_2, S_3, S_{\text{cached}}$) against published academic standards:

1. **Path A (ScholarQABench):** The **Citation Hallucination & Bluffing Test** (measuring deterministic quote verification against GPT-4o's 78–90% hallucination rate).
2. **Path B (LitQA2 from FutureHouse):** The **Deep Body-Text Retrieval Test** (testing zero-contamination retrieval against the public benchmark behind *PaperQA2*).
3. **Path C (2026 Academic Chunking Bake-Off):** The **Large-Scale Canonical Corpus Test** (scaling our internal benchmark to 50 multi-hop items across 4.5M words of foundational textbooks).

---

## 2. Side-by-Side Comparison Matrix

| Evaluation Dimension | Path A: ScholarQABench | Path B: LitQA2 (FutureHouse) | Path C: 2026 Chunking Bake-Off |
|---|:---:|:---:|:---:|
| **Core Research Question** | Does the system hallucinate citations or bluff? | Can the system find answers buried deep in text? | Which chunking architecture optimizes context density? |
| **Primary Metric** | **Citation Hallucination Rate** (%) | **Zero-Leakage Retrieval Accuracy** (%) | **Page Recall vs. Word Count Efficiency** |
| **Domain Scope** | Physics, CS, Biomedicine, Neuroscience | Molecular Biology, Genetics, Chemistry | Foundational Physics, Math, Biology, Mechanics |
| **Corpus Type** | Millions of Open-Access ArXiv / PMC Papers | Open-Access Biology / Chemistry Papers | **11 Reference Graduate Treatises (~4.5M words)** |
| **Public Recognition** | Very High (Allen Institute / UW) | **Highest (Nature / FutureHouse / PaperQA2)** | High (2026 Academic RAG Studies) |
| **Setup Complexity** | Moderate (requires PDF/PMC ingestion) | Moderate (Hugging Face dataset + PDFs) | **Low (Immediate; runs on existing corpus)** |
| **API Cost & Quota Risk** | Moderate | Low | **Near Zero (Runs local offline SQLite/Graph)** |

---

## 3. In-Depth Analysis of Each Benchmark Path

---

### Path A: ScholarQABench (The Citation Hallucination Test)

#### Background & Significance
Introduced by Akari Asai et al. (*OpenScholar*, Allen Institute for AI / University of Washington), ScholarQABench consists of **2,967 expert-written scientific queries** spanning physics, computer science, biomedicine, and neuroscience. 

The headline finding of the benchmark was alarming: **frontier models like GPT-4o hallucinated citations 78% to 90% of the time**, frequently inventing authors, misattributing findings, or citing real papers that do not support the claim.

#### Methodology in Sanity Engine
1. Select a 30–50 query multi-disciplinary slice of ScholarQABench.
2. Run each query through two arms:
   * **Arm 1 (Frontier LLMs):** Raw GPT-4o, Claude 3.5 Sonnet, and Gemini 3.8 Flash.
   * **Arm 2 (Sanity Engine):** $S_2$ (Relational Claims) and $S_3$ (Claim Graph) with active `verify_quote()` and `auto_entail`.
3. Evaluate every citation using two automated, deterministic gates:
   * **Veracity Gate (`verify_quote`):** Does the cited sentence exist verbatim at an exact character offset on disk?
   * **Entailment Gate (`auto_entail`):** Does the cited quote logically support or refute the objection, or is the AI bluffing?

#### Pros (+)
* **Directly Proves Sanity Engine's Core Mission:** Provides hard, peer-reviewed quantitative proof of the "Zero-Hallucination Invariant." You can make a verifiable claim: *"Where raw frontier LLMs hallucinate citations 80%+ of the time, Sanity Engine achieves 0.0% citation hallucination via character-offset anchoring."*
* **Exposes Citation Bluffing:** Tests not just whether quotes exist, but whether they are logically relevant (`auto-entail`).
* **Multi-Disciplinary:** Spans physics, biomedicine, and neuroscience simultaneously.

#### Cons (-)
* **Requires Paper Ingestion:** Source texts are individual journal papers (PDFs/PMC XML), requiring an ingestion pipeline to download and parse PDFs into text.
* **Open-Ended Answers:** Evaluating long-form scientific answers requires an automated LLM-as-a-judge scoring harness.

---

### Path B: LitQA2 (Deep Body-Text Retrieval Benchmark)

#### Background & Significance
Developed by FutureHouse and Oxford (*"Language agents achieve superhuman synthesis of scientific knowledge"*, arXiv:2409.13740 / *PaperQA2*), LitQA2 consists of **248 multiple-choice questions** specifically designed so that:
1. The answer appears **only in the body text** of a paper (never in the abstract, title, or introduction).
2. The fact ideally appears **only once** in the entire published scientific literature.

This design completely defeats models that rely on pre-training memorization or superficial abstract search.

#### Methodology in Sanity Engine
1. Pull a 25–30 question biological/chemical slice from Hugging Face (`futurehouse/lab-bench`).
2. Download the corresponding open-access papers and ingest them into Chunklab.
3. Run the exact 5-system bake-off:
   * $S_0$ (None — Negative Control)
   * $S_1$ (Plain Chunks BM25)
   * $S_2$ (Relational Claims DB)
   * $S_3$ (Claim Graph)
   * $S_{\text{cached}}$ (Gemini Long Context)
4. Score Page/Section Recall, Evidence Coverage, and Accuracy.

#### Pros (+)
* **The Gold Standard for Scientific RAG:** LitQA2 is the recognized academic benchmark in frontier scientific AI (used to benchmark PaperQA2). Demonstrating results on LitQA2 provides instant credibility.
* **Guaranteed Zero Pre-Training Leakage:** If a model gets a question right, it *must* have retrieved the exact paragraph.
* **Deterministic Scoring:** Multiple-choice format means scoring is binary, fast, and free from judge bias.

#### Cons (-)
* **Narrower Domain Scope:** Strongly focused on molecular biology, genetics, and pharmacology; lacks the physics, wave mechanics, and dynamical systems present in Sanity Engine's textbooks.
* **Fragmented Corpus:** Evaluates isolated research papers rather than cohesive, multi-chapter foundational treatises.

---

### Path C: 2026 Academic Chunking Strategies Bake-Off

#### Background & Significance
Recent 2026 academic studies (*FloTorch Benchmark*, *HiCBench*, and *Chunking Strategies on Academic Texts*, arXiv:2607.01852) demonstrated that standard "semantic chunking" often underperforms fixed chunking by up to 15% on long academic theses, while blowing up context window usage.

Chunklab was built specifically to resolve this dilemma: proving that **relational propositional extraction ($S_2$)** outperforms both fixed chunking ($S_1$) and raw context caching ($S_{\text{cached}}$).

#### Methodology in Sanity Engine
1. Scale our curated evaluation suite from 10 items to **50 items** using [`chunklab/make_eval.py`](file:///Users/rhl/Documents/Sanity_Engine/chunklab/make_eval.py).
2. Curate **20 multi-hop cross-disciplinary items** spanning all 11 reference textbooks:
   * *Feynman Vol 1 & 2* (Wave mechanics, electromagnetism, thermodynamics)
   * *Alberts & Lehninger* (Cell biology, membrane transport, bioenergetics)
   * *Kreyszig, Murray, Strogatz* (Differential equations, bifurcation theory, reaction-diffusion)
   * *Johnston, Winter, Cover, Berg* (Neurophysiology, biomechanics, information theory, diffusion)
3. Benchmark fixed sliding windows (512 vs. 180 words) against relational claims ($S_2$) and graph spreading activation ($S_3$).

#### Pros (+)
* **Immediate & Zero Friction:** Uses our existing, verified 4.5M-word corpus. No external scraping, no broken PDF parsers, no external API quota bottlenecks.
* **Tests Deep Multi-Hop Physics/Biology Synthesis:** Specifically evaluates cross-disciplinary analogies (e.g. wave diffraction limits applied to ultrasound arrays).
* **100% Local & Free:** Can be run completely offline using SQLite and local graph algorithms, eliminating Gemini API rate-limit stalls.

#### Cons (-)
* **Internally Curated Dataset:** While constructed following strict LitQA2 rules (body-text grounding, verbatim quote verification), it is our own benchmark dataset rather than a publicly hosted third-party leaderboard.

---

## 4. Strategic Recommendations

| Goal / Audience | Recommended Path | Why |
|---|:---:|---|
| **Pitching Investors / Commercial IP** | **Path A (ScholarQABench)** | Proves that raw LLMs hallucinate citations 80%+ of the time, while Sanity Engine guarantees 0% hallucination. |
| **Academic Publication / Peer Review** | **Path B (LitQA2)** | Matches the exact benchmark used by FutureHouse / PaperQA2, giving immediate comparability. |
| **Engineering & Product Optimization** | **Path C (50-Item Chunklab Suite)** | Maximizes our existing 11 reference textbooks, tests multi-hop physics bridges, and runs offline in seconds. |

---

## 5. Implementation Roadmap

### Step 1: Immediate Scaling (Path C)
* Run `make_eval.py` to expand `eval.jsonl` to 30–50 items across all 11 textbooks.
* Verify gold quotes against disk with `quote_verified()`.
* Generate the updated 50-item benchmark summary table.

### Step 2: The Citation Hallucination Bake-Off (Path A)
* Ingest 25 expert questions from ScholarQABench.
* Run raw GPT-4o / Claude / Gemini side-by-side with Sanity Engine $S_2$.
* Compute exact hallucination and bluffing percentages.

### Step 3: Public Benchmark Validation (Path B)
* Download the open-access slice of LitQA2 from Hugging Face.
* Ingest papers into Chunklab and evaluate retrieval recall.
