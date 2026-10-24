# Chunklab for Sanity Engine

**Chunklab** is an advanced textbook chunking and evidence-retrieval framework engineered for scientific hypothesis stress-testing.

Based on the research in [`michaelraspuzzi/chunklab`](https://github.com/michaelraspuzzi/chunklab) and tailored specifically for **Sanity Engine**, this repository provides three unified retrieval topologies sharing an identical lexical baseline, designed to maximize evidence density and solve cross-textbook synthesis.

---

## The Three Retrieval Systems

All three systems expose the unified `BaseRetriever` interface:
```python
search(query: str, k: int = 5) -> list[Hit]
```
where each `Hit` object is fully polymorphic—supporting both dict-like access (`hit['text']`, `hit['pages']`) and tuple unpacking (`src, text, score = hit`).

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

## Repository Structure

```text
chunklab/
├── common.py           # Text tokenization, entity normalization, BM25 algorithm, page loader
├── retrieval.py        # BaseRetriever, PlainChunks (S1), ClaimsDB (S2), ClaimGraph (S3), Hit
├── test_retrieval.py   # Test suite verifying polymorphism, FTS5, and cross-book graph activation
├── data/               # SQLite indices and claims cache (ignored by git)
└── README.md
```

---

## Running the Verification Tests

```bash
# From workspace root
.venv/bin/python chunklab/test_retrieval.py
```
