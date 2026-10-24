# Chunklab for Sanity Engine

**Chunklab** is an advanced textbook chunking and evidence-retrieval framework engineered for scientific hypothesis stress-testing.

Based on the research in [`michaelraspuzzi/chunklab`](https://github.com/michaelraspuzzi/chunklab) and tailored specifically for **Sanity Engine**, this repository provides three unified retrieval topologies sharing an identical lexical baseline, designed to maximize evidence density and solve cross-textbook synthesis.

---

## The Three Retrieval Systems

All three systems expose the unified `BaseRetriever` interface:
```python
search(query: str, k: int = 5) -> list[Hit]
```
where each `Hit` object is fully polymorphic—supporting both dict-like access (`hit['text']`, `hit['pages']`) and tuple unpacking (`src, text, score = hit`) for zero-friction integration with Sanity Engine.

### 1. System 1: `PlainChunks` (Baseline)
- Paragraph-aware sliding text windows (default ~180 words) with overlap.
- Preserves paragraph integrity so mathematical derivations and sentences are not severed mid-thought.
- Fast in-memory BM25 lexical scoring over the 11 reference textbooks.

### 2. System 2: `ClaimsDB` (Relational Claims Database)
- SQLite database with an FTS5 full-text search index (`claims_fts`).
- Schema stores atomic claims, subject-predicate-object triples, parameter `conditions`, `entities`, and `evidence` (with equation / experiment categorization).
- Retrieval combines FTS rank with entity co-occurrence boosting (`1 + 0.25 * n`), joining out to each claim's evidence rows.

### 3. System 3: `ClaimGraph` (Claim–Evidence Directed Graph)
- In-memory knowledge network over atomic claims.
- **Edges:**
  - Explicit relations: `supports`, `explains`, `derives_from`, `qualifies`, `contradicts`.
  - Rare shared-entity bridges: connects claims across distinct textbooks that share rare concepts ($2 \le \text{count} \le 12$).
- **Retrieval:** Seed claims found via BM25, followed by spreading activation along weighted relation edges. Returns seeds bundled with their upstream evidence chains.

---

## Extraction with Veracity Guarantees

Unlike general RAG pipelines that allow paraphrased summaries, Sanity Engine requires string-exact quote verification in code (`verify_quote()`).
[`extract_claims.py`](extract_claims.py) enforces automated substring anchoring:
- Quotes are verified and snapped to the exact character offset in the source textbook page.
- Parameter regimes and assumptions are cleanly isolated into `conditions`.
- Mathematical quantities and units are extracted into `quantity`.

```bash
# Run claim extraction over a specific book
.venv/bin/python chunklab/extract_claims.py --doc Berg --windows 5 --backend gemini
```

---

## 4-Tier Benchmark & Evaluation Suite

Adapted from Chunklab's evaluation harness, the benchmark tests systems under controlled context reading budgets (e.g. 400 words vs. 1500 words):
1. **Budgeted Context:** Hard ceiling on words passed to the reader.
2. **Page Recall & MRR:** Deterministic ground-truth checks against gold pages.
3. **Evidence Coverage Judge:** LLM evaluation against gold quotes.
4. **Blind Reader Verdict:** LLM reader deciding `SUPPORTED` / `REFUTED` / `INSUFFICIENT` without seeing ground truth.
5. **S0 Control:** Confirms reader answers `insufficient` when context is empty (zero parametric memory leakage).

```bash
# Run full benchmark across all 4 systems
.venv/bin/python chunklab/run_eval.py S0_none S1_plain S2_relational S3_graph --budget 400

# Generate a new 30-item evaluation set
.venv/bin/python chunklab/make_eval.py --backend gemini
```

---

## Repository Structure

```text
chunklab/
├── common.py           # Text tokenization, entity normalization, BM25 algorithm, page loader
├── retrieval.py        # BaseRetriever, PlainChunks (S1), ClaimsDB (S2), ClaimGraph (S3), Hit
├── extract_claims.py   # Claim & evidence extraction with verbatim substring quote anchoring
├── make_eval.py        # 30-item benchmark generator across cross-book invariant bridges
├── run_eval.py         # 4-tier benchmark runner with budgeted reader & S0 control
├── test_retrieval.py   # Unit test suite verifying polymorphism, FTS5, and graph spreading
├── eval/               # Curated evaluation sets (eval.jsonl)
├── data/               # SQLite indices and claims cache (ignored by git)
└── README.md
```
