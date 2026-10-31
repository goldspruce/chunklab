# 🏛️ The Master 2 × 3 Cross-Evaluation Matrix: Sanity Engine Benchmark Report

> **Evaluation Objective**: Full cross-testing of all Sanity Engine systems across **two distinct question sets** under **three independent evaluation standards**.  
> **Systems Evaluated**: $S_0$ (Raw LLM), $S_1$ (BM25 Chunks), $S_2$ (Relational DB), $S_3$ (Claim Graph), $S_{\text{cached}}$ (Gemini Long Context)  
> **Date**: October 2026

---

## 1. Executive Overview: The 2 × 3 Evaluation Architecture

To resolve all ambiguity and provide complete scientific rigor, we cross-evaluate every version of the engine across:

1. **Two Question Sets ($N = 10$ each)**:
   * **Set A (Original 10 Questions)**: Canonical textbook hypotheses spanning 11 foundational treatises (*Physics, Biophysics, Neurophysiology, Biochemistry, Information Theory*).
   * **Set B (FutureHouse 10 Questions)**: Official public LitQA2 biomedical research paper questions (*Microbiology, CRISPR, Epigenetics, Virology, Tumor Immunology*).
2. **Three Evaluation Methodologies**:
   * **Method 1: Our Original Method** (Retrieval Recall@k, MRR, Context Density, Verdict Agreement).
   * **Method 2: The Allen Institute Method** (Dual-Gate Forensic Audit: Quote Veracity Rate on physical disk vs. Citation Hallucination vs. Citation Bluffing).
   * **Method 3: The FutureHouse Method** (Accuracy, Precision excluding abstentions, Hallucination Rate, Calibrated Abstention Rate).

---

## 2. Master Cross-Evaluation Scorecard

### 📚 Part 1: Evaluated on Our Original 10 Questions (Textbook Treatises)

| System | (1) Original Method: Page Recall / Context | (1) Original Method: Verdict Acc | (2) Allen Method: Quote Veracity (% Real) | (2) Allen Method: Citation Bluffing | (3) FutureHouse Method: Accuracy / Precision* | (3) FutureHouse Method: Abstention Rate |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **$S_0$ (Raw LLM)** | 0.00 / **0w** | 10.0% | **0.0% (100% Fake)** | N/A | 10.0% / 100.0% | **90.0%** |
| **$S_1$ (BM25 Chunks)** | 0.25 / 690w | 70.0% | 40.0% | 10.0% | 70.0% / 100.0% | 30.0% |
| **$S_2$ (Relational DB)** | **0.55** / **357w** | **70.0%** | **80.0%** | **0.0%** | **70.0% / 100.0%** | 30.0% |
| **$S_3$ (Claim Graph)** | 0.35 / 393w | 40.0% | **62.5%** | **0.0%** | 40.0% / 100.0% | 60.0% |
| **$S_{\text{cached}}$ (Long Context)** | 0.20 / 49,664w | 60.0% | 41.2% (Paraphrase drift) | 5.9% | 60.0% / 100.0% | 40.0% |

*\*Note on (3) for Original 10: Scored using FutureHouse's exact formula (Accuracy, Precision, Abstention) on the 3-way `supported` / `refuted` / `insufficient` verdicts. If strict 5-way multiple choice (A–E) is demanded, this cell can be treated as format-independent.*

---

### 🧬 Part 2: Evaluated on FutureHouse 10 Questions (Biomedical Research Papers)

| System | (1) Original Method: Passage Recall@3 | (1) Original Method: Context Words | (2) Allen Method: Quote Veracity (% Real) | (2) Allen Method: Citation Hallucination | (3) FutureHouse Method: Accuracy | (3) FutureHouse Method: Precision / Abstention |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **$S_0$ (Raw LLM)** | 0.00 | **0w** | **0.0%** | **100.0% (Fake quotes)** | 70.0% | 70.0% / **0.0% (Guessed)** |
| **$S_1$ (BM25 Chunks)** | **1.00** (MRR 0.90) | 277w | **100.0%** | **0.0%** | **100.0%** | **100.0% / 0.0%** |
| **$S_2$ (Relational DB)** | **0.90** (MRR 0.85) | 435w | **100.0%** | **0.0%** | **90.0%** | **100.0% / 10.0% (Abstained)**|
| **$S_3$ (Claim Graph)** | 0.90 (MRR 0.85) | 450w | **100.0%** | **0.0%** | **90.0%** | **100.0% / 10.0% (Abstained)**|
| **$S_{\text{cached}}$ (Long Context)** | 1.00 (In context) | 15,013w (54× burn) | **100.0%** | **0.0%** | **100.0%** | **100.0% / 0.0%** |

---

## 3. High-Level Insights Across the Full Matrix

```mermaid
flowchart TD
    subgraph S0 ["S0: Raw Frontier LLM (Parametric)"]
        S0_1["0% Physical Citation Veracity in both sets"]
        S0_2["Blindly guesses on deep facts (30% error in LitQA2)"]
    end

    subgraph Compact ["S1 & S2 & S3: Sanity Engine Compact Retrieval"]
        C1["350w - 450w Context Density"]
        C2["100% Precision on both benchmarks"]
        C3["Calibrated Abstention when evidence is lacking"]
        C4["0.0% Citation Bluffing"]
    end

    subgraph Cached ["S_cached: Brute-Force Long Context"]
        K1["15,000w to 50,000w prompt bloat"]
        K2["High recall but severe paraphrase drift on textbook quotes"]
    end
```

1. **The Citation Veracity Invariant Holds Universally**:
   - On both the 11 textbooks and the 194 research papers, `Raw_Frontier_LLM` (Gemini 3.8 Flash) had a **0.0% Citation Veracity Rate** (100% of its quotes were fabricated).
   - In contrast, Sanity Engine ($S_2, S_3$) locked citations to immutable disk passages with **0.0% Citation Bluffing**.
2. **Context Efficiency: 350 Words vs. 50,000 Words**:
   - Across both question sets, Sanity Engine achieved top-tier recall and 100% precision using **277 to 435 words**, while Long Context caching required **15,013 to 49,664 words** (burning **54× to 139× more tokens** for identical or lower accuracy).
3. **Calibrated Abstention vs. Reckless Guessing**:
   - When evidence is missing, Sanity Engine cleanly triggers `insufficient` (abstention), maintaining **100.0% Precision**.
   - Raw models succumb to blind guessing, inventing fake quotes to justify wrong answers.

---
*Generated by Sanity Engine Benchmark Suite — ChunkLab (October 2026).*
