"""Polymorphic retrieval module implementing three chunking and index topologies:
1. S1_plain: Plain sliding/paragraph chunks + BM25 (baseline)
2. S2_relational: Relational SQLite claims DB with FTS5 and entity boosting
3. S3_graph: Claim-Evidence graph with relation links & cross-book spreading activation
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path
from typing import Any

try:
    from .common import BM25, CORPUS_DIR, DATA_DIR, load_pages, norm_entity, tokenize
except ImportError:
    from common import BM25, CORPUS_DIR, DATA_DIR, load_pages, norm_entity, tokenize


class Hit:
    """Unified search result compatible with both dict access (hit['text'])
    and tuple unpacking (src, text, score = hit).
    """

    def __init__(
        self,
        id: str,
        doc: str,
        pages: list[int],
        section: str,
        text: str,
        score: float,
        extra: dict[str, Any] | None = None,
    ):
        self.id = id
        self.doc = doc
        self.source = doc
        self.pages = sorted(list(set(pages)))
        self.section = section or ""
        self.text = text
        self.score = float(score)
        self.extra = extra or {}

    def __getitem__(self, key: Any) -> Any:
        if isinstance(key, int):
            if key == 0:
                return self.source
            elif key == 1:
                return self.text
            elif key == 2:
                return self.score
            raise IndexError(f"Hit index out of range: {key}")
        if key == "source":
            return self.source
        if hasattr(self, key):
            return getattr(self, key)
        if key in self.extra:
            return self.extra[key]
        raise KeyError(key)

    def __contains__(self, key: str) -> bool:
        return hasattr(self, key) or key in self.extra

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "doc": self.doc,
            "source": self.source,
            "pages": self.pages,
            "section": self.section,
            "text": self.text,
            "score": round(self.score, 4),
            **self.extra,
        }

    def __iter__(self):
        """Allows unpacking: src, text, score = hit"""
        yield self.source
        yield self.text
        yield self.score

    def __repr__(self) -> str:
        return f"<Hit id={self.id} doc={self.doc} pages={self.pages} score={self.score:.2f}>"


class BaseRetriever(ABC):
    """Abstract interface for all retrieval systems."""

    name: str

    @abstractmethod
    def search(self, query: str, k: int = 5) -> list[Hit]:
        """Search the corpus and return up to k ranked Hit objects."""
        pass

    @property
    def chunks(self) -> list[tuple[str, str]]:
        """List of (source/doc, text) pairs for quote verification across corpus."""
        return []


# ====================================================================== S1: Plain Chunks
class PlainChunks(BaseRetriever):
    """System 1: Paragraph-aware sliding text windows with BM25.
    Preserves paragraph integrity so verbatim quotes and formulas are not sliced mid-sentence.
    """

    name = "S1_plain"

    def __init__(
        self,
        corpus_dir: Path | str | None = None,
        chunk_words: int = 180,
        pages: list[dict] | None = None,
    ):
        self.chunk_words = chunk_words
        self._chunk_objs = []
        raw_pages = pages if pages is not None else load_pages(corpus_dir)

        by_doc = defaultdict(list)
        for p in raw_pages:
            by_doc[p["doc"]].append(p)

        for doc, doc_pages in by_doc.items():
            buf_paras = []
            buf_pages = set()
            buf_words = 0
            curr_section = doc_pages[0].get("section", "")

            for p in doc_pages:
                page_paras = [para.strip() for para in p["text"].split("\n\n") if para.strip()]
                for para in page_paras:
                    para_len = len(para.split())
                    buf_paras.append(para)
                    buf_pages.add(p["page"])
                    buf_words += para_len

                    if buf_words >= self.chunk_words:
                        self._chunk_objs.append({
                            "id": f"{doc}#{len(self._chunk_objs) + 1}",
                            "doc": doc,
                            "pages": sorted(list(buf_pages)),
                            "section": curr_section,
                            "text": "\n\n".join(buf_paras),
                        })
                        # Keep last paragraph for sliding overlap
                        buf_paras = [buf_paras[-1]] if len(buf_paras) > 1 else []
                        buf_pages = {p["page"]} if buf_paras else set()
                        buf_words = len(buf_paras[0].split()) if buf_paras else 0

            if buf_paras:
                self._chunk_objs.append({
                    "id": f"{doc}#{len(self._chunk_objs) + 1}",
                    "doc": doc,
                    "pages": sorted(list(buf_pages)),
                    "section": curr_section,
                    "text": "\n\n".join(buf_paras),
                })

        self.bm25 = BM25([c["text"] for c in self._chunk_objs])

    @property
    def chunks(self) -> list[tuple[str, str]]:
        return [(c["doc"], c["text"]) for c in self._chunk_objs]

    def search(self, query: str, k: int = 5) -> list[Hit]:
        matches = self.bm25.top(query, k=k)
        hits = []
        for idx, score in matches:
            c = self._chunk_objs[idx]
            hits.append(
                Hit(
                    id=c["id"],
                    doc=c["doc"],
                    pages=c["pages"],
                    section=c["section"],
                    text=c["text"],
                    score=score,
                )
            )
        return hits


# ====================================================================== S2: Relational DB
S2_SCHEMA = """
CREATE TABLE IF NOT EXISTS claims(
    claim_id INTEGER PRIMARY KEY,
    doc TEXT,
    page INT,
    section TEXT,
    claim TEXT,
    type TEXT,
    subject TEXT,
    predicate TEXT,
    object TEXT,
    conditions TEXT
);

CREATE TABLE IF NOT EXISTS evidence(
    evidence_id INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_id INT REFERENCES claims(claim_id),
    text TEXT,
    type TEXT,
    quantity TEXT,
    verbatim INT DEFAULT 1
);

CREATE TABLE IF NOT EXISTS entities(
    entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS claim_entities(
    claim_id INT REFERENCES claims(claim_id),
    entity_id INT REFERENCES entities(entity_id)
);

CREATE TABLE IF NOT EXISTS claim_links(
    src INT REFERENCES claims(claim_id),
    dst INT REFERENCES claims(claim_id),
    relation TEXT
);

CREATE VIRTUAL TABLE IF NOT EXISTS claims_fts USING fts5(
    claim,
    triple,
    conditions,
    evidence,
    entities,
    section,
    content='',
    tokenize='porter'
);

CREATE INDEX IF NOT EXISTS idx_ce_entity ON claim_entities(entity_id);
CREATE INDEX IF NOT EXISTS idx_ev_claim ON evidence(claim_id);
"""


# ====================================================================== JIT Manager
class JITManager:
    """Just-In-Time claim extractor that monitors queries, identifies missing textbook pages,
    and extracts claims on-the-fly to populate the local database.
    """

    def __init__(
        self,
        corpus_dir: Path | str | None = None,
        claims_file: Path | str | None = None,
        llm: Any = None,
    ):
        self.corpus_dir = Path(corpus_dir) if corpus_dir else CORPUS_DIR
        self.claims_file = Path(claims_file) if claims_file else DATA_DIR / "claims.jsonl"
        self._llm = llm
        self._s1: PlainChunks | None = None
        self._pages: list[dict] | None = None

    def get_llm(self) -> Any:
        if self._llm is None:
            try:
                from .extract_claims import GeminiExtractorLLM
                self._llm = GeminiExtractorLLM()
            except Exception:
                try:
                    from extract_claims import GeminiExtractorLLM
                    self._llm = GeminiExtractorLLM()
                except Exception:
                    self._llm = None
        return self._llm

    def find_missing_pages(
        self,
        query: str,
        indexed_pages: set[tuple[str, int]],
        max_candidates: int = 2,
    ) -> list[dict]:
        """Find the top textbook pages matching query that have not yet been extracted."""
        if self._s1 is None:
            self._pages = load_pages(self.corpus_dir)
            self._s1 = PlainChunks(pages=self._pages)

        hits = self._s1.search(query, k=6)
        candidates = []
        seen = set()

        for h in hits:
            for p_num in h.pages:
                key = (h.doc, int(p_num))
                if key not in indexed_pages and key not in seen:
                    p_obj = next((p for p in self._pages if p["doc"] == h.doc and p["page"] == p_num), None)
                    if p_obj:
                        candidates.append(p_obj)
                        seen.add(key)
                        if len(candidates) >= max_candidates:
                            return candidates
        return candidates

    def extract_and_persist(self, pages: list[dict], log=print) -> list[dict]:
        """Extract claims from pages on the fly, append to claims.jsonl, and return new claims."""
        if not pages:
            return []

        llm = self.get_llm()
        if not llm:
            return []

        try:
            from .extract_claims import process_window, make_windows
        except ImportError:
            from extract_claims import process_window, make_windows

        windows = make_windows(pages, window_size=2)
        new_claims = []

        for win in windows:
            doc = win[0]["doc"]
            p_start = win[0]["page"]
            log(f"⚡ [JIT Auto-Extract] Extracting claims on-the-fly for {doc} (p. {p_start})...")
            try:
                extracted = process_window(win, llm=llm, cache=True)
                new_claims.extend(extracted)
            except Exception as e:
                log(f"  [!] JIT extraction failed for {doc}: {e}")

        if new_claims:
            existing_lines = 0
            if self.claims_file.exists():
                try:
                    existing_lines = len(self.claims_file.read_text(encoding="utf-8").splitlines())
                except Exception:
                    existing_lines = 0

            self.claims_file.parent.mkdir(parents=True, exist_ok=True)
            with self.claims_file.open("a", encoding="utf-8") as f:
                for i, c in enumerate(new_claims):
                    c["gid"] = existing_lines + i + 1
                    f.write(json.dumps(c) + "\n")
            log(f"⚡ [JIT Complete] Saved {len(new_claims)} new claims locally to {self.claims_file.name}!")

        return new_claims


class ClaimsDB(BaseRetriever):
    """System 2: Relational SQLite database with FTS5 search.
    Scores claims via full-text search, boosts by entity overlap, and joins out to evidence rows.
    """

    name = "S2_relational"

    def __init__(
        self,
        db_path: Path | str | None = None,
        claims: list[dict] | None = None,
        claims_file: Path | str | None = None,
        auto_jit: bool = True,
        corpus_dir: Path | str | None = None,
    ):
        self.auto_jit = auto_jit
        self.corpus_dir = Path(corpus_dir) if corpus_dir else CORPUS_DIR
        self.claims_file = Path(claims_file) if claims_file else (DATA_DIR / "claims.jsonl")
        self.jit = JITManager(corpus_dir=self.corpus_dir, claims_file=self.claims_file) if auto_jit else None

        if db_path is None or str(db_path) == ":memory:":
            self.db = sqlite3.connect(":memory:")
        else:
            self.db_path = Path(db_path)
            self.db_path.unlink(missing_ok=True)
            self.db = sqlite3.connect(self.db_path)

        self.db.executescript(S2_SCHEMA)

        rows = []
        if claims is not None:
            rows = claims
        elif self.claims_file.exists():
            rows = [json.loads(line) for line in self.claims_file.read_text(encoding="utf-8").splitlines() if line.strip()]

        if rows:
            self._ingest_claims(rows)

    def _ingest_claims(self, rows: list[dict]):
        ents: dict[str, int] = {}
        # Ensure every claim has a global gid
        for i, r in enumerate(rows):
            r["gid"] = r.get("gid", i + 1)

        key = {(r.get("window", ""), r["id"]): r["gid"] for r in rows if "id" in r}

        for r in rows:
            g = r["gid"]
            self.db.execute(
                "INSERT OR REPLACE INTO claims VALUES (?,?,?,?,?,?,?,?,?,?)",
                (
                    g,
                    r.get("doc", ""),
                    int(r.get("page", 1)),
                    r.get("section", ""),
                    r.get("claim", ""),
                    r.get("type", "claim"),
                    r.get("subject", ""),
                    r.get("predicate", ""),
                    r.get("object", ""),
                    r.get("conditions", ""),
                ),
            )

            for ev in r.get("evidence", []):
                self.db.execute(
                    "INSERT INTO evidence(claim_id, text, type, quantity, verbatim) VALUES (?,?,?,?,?)",
                    (
                        g,
                        ev.get("text", ""),
                        ev.get("type", "evidence"),
                        ev.get("quantity", ""),
                        int(ev.get("verbatim", 1)),
                    ),
                )

            for e in {norm_entity(ent) for ent in r.get("entities", []) if ent}:
                if e not in ents:
                    cur = self.db.execute("INSERT OR IGNORE INTO entities(name) VALUES (?)", (e,))
                    row_id = cur.lastrowid
                    if not row_id or row_id == 0:
                        row_id = self.db.execute("SELECT entity_id FROM entities WHERE name=?", (e,)).fetchone()[0]
                    ents[e] = row_id
                self.db.execute("INSERT INTO claim_entities VALUES (?,?)", (g, ents[e]))

            for link in r.get("links", []):
                target = link.get("target")
                tgt_gid = key.get((r.get("window", ""), target)) if isinstance(target, int) else None
                if tgt_gid is not None and tgt_gid != g:
                    self.db.execute(
                        "INSERT INTO claim_links VALUES (?,?,?)",
                        (g, tgt_gid, link.get("relation", "supports")),
                    )

            ev_text = " ".join(ev.get("text", "") for ev in r.get("evidence", []))
            ent_text = " ".join(r.get("entities", []))
            triple_text = f"{r.get('subject', '')} {r.get('predicate', '')} {r.get('object', '')}"

            self.db.execute(
                "INSERT INTO claims_fts(rowid, claim, triple, conditions, evidence, entities, section) VALUES (?,?,?,?,?,?,?)",
                (
                    g,
                    r.get("claim", ""),
                    triple_text,
                    r.get("conditions", ""),
                    ev_text,
                    ent_text,
                    r.get("section", ""),
                ),
            )

        self.db.commit()

    @property
    def chunks(self) -> list[tuple[str, str]]:
        rows = self.db.execute(
            "SELECT c.doc, c.claim || ' ' || COALESCE(e.text, '') FROM claims c LEFT JOIN evidence e ON c.claim_id = e.claim_id"
        ).fetchall()
        return [(r[0], r[1]) for r in rows]

    def _query_entities(self, query: str) -> list[int]:
        toks = tokenize(query)
        if not toks:
            return []
        marks = ",".join("?" * len(toks))
        cursor = self.db.execute(
            f"SELECT entity_id FROM entities WHERE name IN ({marks})", [norm_entity(t) for t in toks]
        )
        return [row[0] for row in cursor.fetchall()]

    def _do_search(self, query: str, k: int = 5) -> list[Hit]:
        toks = tokenize(query)
        if not toks:
            return []

        clean_q = " OR ".join(f'"{t}"' for t in toks)
        score: dict[int, float] = {}

        try:
            for rowid, rank in self.db.execute(
                "SELECT rowid, rank FROM claims_fts WHERE claims_fts MATCH ? ORDER BY rank LIMIT 40",
                (clean_q,),
            ):
                score[rowid] = -float(rank)
        except sqlite3.OperationalError:
            # Fallback if query terms have syntax issues
            return []

        # Boost by entity co-occurrence
        q_ents = self._query_entities(query)
        if q_ents and score:
            marks = ",".join("?" * len(q_ents))
            for cid, count in self.db.execute(
                f"SELECT claim_id, COUNT(*) FROM claim_entities WHERE entity_id IN ({marks}) GROUP BY claim_id",
                q_ents,
            ):
                if cid in score:
                    score[cid] *= 1.0 + 0.25 * count

        ranked = sorted(score.keys(), key=lambda c: -score[c])[:k]
        hits = []
        for cid in ranked:
            c_row = self.db.execute(
                "SELECT doc, page, section, claim, type, conditions FROM claims WHERE claim_id=?",
                (cid,),
            ).fetchone()
            if not c_row:
                continue
            doc, page, section, claim, ctype, cond = c_row
            ev_rows = self.db.execute(
                "SELECT type, text, quantity FROM evidence WHERE claim_id=?", (cid,)
            ).fetchall()

            text_parts = [f"CLAIM [{ctype.upper()}]: {claim}"]
            if cond:
                text_parts.append(f" (Conditions: {cond})")
            for etype, etext, equant in ev_rows:
                q_str = f" [{equant}]" if equant else ""
                text_parts.append(f"\n  • EVIDENCE [{etype.upper()}]{q_str}: {etext}")

            hits.append(
                Hit(
                    id=f"c{cid}",
                    doc=doc,
                    pages=[page],
                    section=section,
                    text="".join(text_parts),
                    score=score[cid],
                )
            )

        return hits

    def search(self, query: str, k: int = 5) -> list[Hit]:
        hits = self._do_search(query, k)
        should_jit = (len(hits) < k) or (not hits) or (hits and hits[0].score < 2.5)
        if should_jit and self.jit:
            try:
                indexed_pages = set(self.db.execute("SELECT DISTINCT doc, page FROM claims").fetchall())
                missing = self.jit.find_missing_pages(query, indexed_pages, max_candidates=2)
                if missing:
                    new_claims = self.jit.extract_and_persist(missing)
                    if new_claims:
                        self._ingest_claims(new_claims)
                        hits = self._do_search(query, k)
            except Exception:
                pass
        return hits


# ====================================================================== S3: Claim Graph
class ClaimGraph(BaseRetriever):
    """System 3: Claim-Evidence Graph with spreading activation retrieval.
    Nodes: atomic claims with their evidence.
    Edges:
      1. Explicit claim->claim relations (supports, explains, derives_from, qualifies, contradicts)
      2. Shared rare entities (2 <= occurrence <= 12) spanning across textbooks.
    """

    name = "S3_graph"

    REL_WEIGHTS = {
        "supports": 1.0,
        "explains": 0.95,
        "derives_from": 0.90,
        "contradicts": 1.0,
        "qualifies": 0.85,
        "example_of": 0.70,
        "entity": 0.40,
    }

    def __init__(
        self,
        claims: list[dict] | None = None,
        claims_file: Path | str | None = None,
        auto_jit: bool = True,
        corpus_dir: Path | str | None = None,
    ):
        self.auto_jit = auto_jit
        self.corpus_dir = Path(corpus_dir) if corpus_dir else CORPUS_DIR
        self.claims_file = Path(claims_file) if claims_file else (DATA_DIR / "claims.jsonl")
        self.jit = JITManager(corpus_dir=self.corpus_dir, claims_file=self.claims_file) if auto_jit else None

        rows = []
        if claims is not None:
            rows = claims
        elif self.claims_file.exists():
            rows = [json.loads(line) for line in self.claims_file.read_text(encoding="utf-8").splitlines() if line.strip()]

        for i, r in enumerate(rows):
            r["gid"] = r.get("gid", i + 1)

        self.claims = {r["gid"]: r for r in rows}
        self.adj = defaultdict(list)  # gid -> [(neighbor_gid, relation)]

        # Map window-local IDs to global IDs
        key = {(r.get("window", ""), r["id"]): r["gid"] for r in rows if "id" in r}

        for r in rows:
            g = r["gid"]
            for link in r.get("links", []):
                target = link.get("target")
                tgt_gid = key.get((r.get("window", ""), target)) if isinstance(target, int) else None
                if tgt_gid is not None and tgt_gid != g:
                    rel = link.get("relation", "supports")
                    self.adj[g].append((tgt_gid, rel))
                    self.adj[tgt_gid].append((g, rel))

        # Build rare entity bridges across books
        by_ent = defaultdict(set)
        for r in rows:
            for ent in r.get("entities", []):
                normed = norm_entity(ent)
                if normed:
                    by_ent[normed].add(r["gid"])

        for ent, gids in by_ent.items():
            if 2 <= len(gids) <= 12:  # Rare concepts only; filters out "energy" or "cell"
                gid_list = list(gids)
                for i in range(len(gid_list)):
                    for j in range(i + 1, len(gid_list)):
                        a, b = gid_list[i], gid_list[j]
                        self.adj[a].append((b, "entity"))
                        self.adj[b].append((a, "entity"))

        # Lexical BM25 index over claim + triple + evidence + entities
        corpus_texts = []
        self.gid_order = []
        for gid, r in self.claims.items():
            ev_str = " ".join(ev.get("text", "") for ev in r.get("evidence", []))
            ent_str = " ".join(r.get("entities", []))
            full_text = f"{r.get('claim', '')} {r.get('subject', '')} {r.get('object', '')} {ent_str} {ev_str}"
            corpus_texts.append(full_text)
            self.gid_order.append(gid)

        self.bm25 = BM25(corpus_texts)

    def _add_claims_to_graph(self, new_rows: list[dict]):
        if not new_rows:
            return
        start_gid = max(self.claims.keys(), default=0) + 1
        for i, r in enumerate(new_rows):
            r["gid"] = r.get("gid", start_gid + i)
            self.claims[r["gid"]] = r

        key = {(r.get("window", ""), r["id"]): r["gid"] for r in new_rows if "id" in r}
        for r in new_rows:
            g = r["gid"]
            for link in r.get("links", []):
                target = link.get("target")
                tgt_gid = key.get((r.get("window", ""), target)) if isinstance(target, int) else None
                if tgt_gid is not None and tgt_gid != g:
                    rel = link.get("relation", "supports")
                    self.adj[g].append((tgt_gid, rel))
                    self.adj[tgt_gid].append((g, rel))

        by_ent = defaultdict(set)
        for r in self.claims.values():
            for ent in r.get("entities", []):
                normed = norm_entity(ent)
                if normed:
                    by_ent[normed].add(r["gid"])

        for ent, gids in by_ent.items():
            if 2 <= len(gids) <= 12:
                gid_list = list(gids)
                for i in range(len(gid_list)):
                    for j in range(i + 1, len(gid_list)):
                        a, b = gid_list[i], gid_list[j]
                        if (b, "entity") not in self.adj[a]:
                            self.adj[a].append((b, "entity"))
                            self.adj[b].append((a, "entity"))

        corpus_texts = []
        self.gid_order = []
        for gid, r in self.claims.items():
            ev_str = " ".join(ev.get("text", "") for ev in r.get("evidence", []))
            ent_str = " ".join(r.get("entities", []))
            full_text = f"{r.get('claim', '')} {r.get('subject', '')} {r.get('object', '')} {ent_str} {ev_str}"
            corpus_texts.append(full_text)
            self.gid_order.append(gid)

        self.bm25 = BM25(corpus_texts)

    @property
    def chunks(self) -> list[tuple[str, str]]:
        out = []
        for r in self.claims.values():
            ev = " ".join(e.get("text", "") for e in r.get("evidence", []))
            out.append((r.get("doc", ""), f"{r.get('claim', '')} {ev}"))
        return out

    def _format_claim(self, r: dict) -> str:
        ctype = r.get("type", "claim").upper()
        res = f"[{ctype}] {r.get('claim', '')}"
        cond = r.get("conditions", "")
        if cond:
            res += f" (Conditions: {cond})"
        for ev in r.get("evidence", []):
            etype = ev.get("type", "evidence").upper()
            q = f" [{ev['quantity']}]" if ev.get("quantity") else ""
            res += f"\n    • EVIDENCE [{etype}]{q}: {ev.get('text', '')}"
        return res

    def _do_search(self, query: str, k: int = 5) -> list[Hit]:
        matches = self.bm25.top(query, k=20)
        if not matches:
            return []

        top_score = matches[0][1]
        activation: dict[int, float] = defaultdict(float)

        # 1. Initialize seed activation from BM25
        for idx, score in matches:
            gid = self.gid_order[idx]
            activation[gid] += score / max(top_score, 1e-6)

        # 2. Spread activation 1 hop across graph relations
        for idx, score in matches:
            gid = self.gid_order[idx]
            seed_power = score / max(top_score, 1e-6)
            for neighbor, rel in self.adj[gid]:
                weight = self.REL_WEIGHTS.get(rel, 0.5)
                activation[neighbor] += 0.5 * seed_power * weight

        ranked_gids = sorted(activation.keys(), key=lambda g: -activation[g])
        hits: list[Hit] = []
        visited = set()

        for g in ranked_gids:
            if g in visited:
                continue
            visited.add(g)
            r = self.claims[g]

            # Collect strongest causal chain (non-entity)
            chain = []
            for nb, rel in self.adj[g]:
                if rel != "entity" and nb not in visited and nb in self.claims:
                    chain.append((nb, rel))
                    if len(chain) >= 2:
                        break

            visited.update(nb for nb, _ in chain)

            text_lines = ["CLAIM " + self._format_claim(r)]
            pages = [r.get("page", 1)]
            extra_refs = []

            for nb, rel in chain:
                nb_r = self.claims[nb]
                rel_label = rel.upper().replace("_", " ")
                text_lines.append(
                    f"\n  <- {rel_label} ({nb_r.get('doc', '')} p.{nb_r.get('page', 1)}): "
                    + self._format_claim(nb_r)
                )
                if nb_r.get("doc") == r.get("doc"):
                    pages.append(nb_r.get("page", 1))
                else:
                    extra_refs.append((nb_r.get("doc", ""), nb_r.get("page", 1)))

            hits.append(
                Hit(
                    id=f"g{g}",
                    doc=r.get("doc", ""),
                    pages=pages,
                    section=r.get("section", ""),
                    text="".join(text_lines),
                    score=activation[g],
                    extra={"extra_refs": extra_refs},
                )
            )

            if len(hits) == k:
                break

        return hits

    def search(self, query: str, k: int = 5) -> list[Hit]:
        hits = self._do_search(query, k)
        should_jit = (len(hits) < k) or (not hits) or (hits and hits[0].score < 0.5)
        if should_jit and self.jit:
            try:
                indexed_pages = {(r.get("doc", ""), int(r.get("page", 1))) for r in self.claims.values()}
                missing = self.jit.find_missing_pages(query, indexed_pages, max_candidates=2)
                if missing:
                    new_claims = self.jit.extract_and_persist(missing)
                    if new_claims:
                        self._add_claims_to_graph(new_claims)
                        hits = self._do_search(query, k)
            except Exception:
                pass
        return hits


# ====================================================================== Factory
def get_retriever(
    name: str = "s1",
    corpus_dir: Path | str | None = None,
    chunk_words: int = 180,
    claims_path: Path | str | None = None,
    auto_jit: bool = True,
) -> BaseRetriever:
    """Instantiate a retriever by name ('s1', 's2', 's3') with automatic claim resolution."""
    mode = str(name).lower().strip()

    if "s2" in mode or "relational" in mode:
        candidates = [
            Path(claims_path) if claims_path else None,
            DATA_DIR / "claims.jsonl",
            DATA_DIR / "real_claims.jsonl",
            DATA_DIR / "test_claims.jsonl",
        ]
        chosen = next((p for p in candidates if p and p.exists() and p.stat().st_size > 0), None)
        if chosen:
            return ClaimsDB(claims_file=chosen, auto_jit=auto_jit, corpus_dir=corpus_dir)
        target_file = Path(claims_path) if claims_path else (DATA_DIR / "claims.jsonl")
        if auto_jit:
            target_file.parent.mkdir(parents=True, exist_ok=True)
            if not target_file.exists():
                target_file.touch()
            return ClaimsDB(claims_file=target_file, auto_jit=True, corpus_dir=corpus_dir)
        raise FileNotFoundError(
            "System 2 (ClaimsDB) requires a claims database. None found in chunklab/data/. "
            "Please run: python chunklab/extract_claims.py"
        )

    if "s3" in mode or "graph" in mode:
        candidates = [
            Path(claims_path) if claims_path else None,
            DATA_DIR / "claims.jsonl",
            DATA_DIR / "real_claims.jsonl",
            DATA_DIR / "test_claims.jsonl",
        ]
        chosen = next((p for p in candidates if p and p.exists() and p.stat().st_size > 0), None)
        if chosen:
            return ClaimGraph(claims_file=chosen, auto_jit=auto_jit, corpus_dir=corpus_dir)
        target_file = Path(claims_path) if claims_path else (DATA_DIR / "claims.jsonl")
        if auto_jit:
            target_file.parent.mkdir(parents=True, exist_ok=True)
            if not target_file.exists():
                target_file.touch()
            return ClaimGraph(claims_file=target_file, auto_jit=True, corpus_dir=corpus_dir)
        raise FileNotFoundError(
            "System 3 (ClaimGraph) requires a claims database. None found in chunklab/data/. "
            "Please run: python chunklab/extract_claims.py"
        )

    # Default to S1 Plain Chunks
    return PlainChunks(corpus_dir=corpus_dir, chunk_words=chunk_words)

