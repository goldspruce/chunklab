"""Shared utilities for chunklab: paths, text processing, BM25, and page loading."""
from __future__ import annotations
import glob
import math
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PARENT_ROOT = ROOT.parent
DATA_DIR = ROOT / "data"
CORPUS_DIR = PARENT_ROOT / "corpus"
DATA_DIR.mkdir(exist_ok=True)


def _load_dotenv():
    """Load .env from parent or root workspace directory."""
    for env_path in [ROOT / ".env", PARENT_ROOT / ".env"]:
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"").split("#")[0].strip()
                    if k and k not in os.environ:
                        os.environ[k] = v


_load_dotenv()

STOPWORDS = set(
    "a an the and or but if because as what when where how all any both each few more most "
    "other some such no nor not only own same so than too very can will just should now "
    "of in to for with on at by from up about into over after is are was were be been being "
    "have has had do does did this that these those it its".split()
)


def tokenize(text: str) -> list[str]:
    """Extract lowercase alphanumeric tokens, filtering out basic stopwords."""
    if not text:
        return []
    words = re.findall(r"[a-z0-9_]+", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 1]


def norm_entity(entity: str) -> str:
    """Normalize scientific entity names: lowercase, strip, and crude singularization."""
    e = entity.lower().strip()
    return re.sub(r"(?<=[a-z]{3})s$", "", e)


class BM25:
    """In-memory BM25 index with configurable k1 and b parameters."""

    def __init__(self, corpus: list[str], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = len(corpus)
        self.tokenized_corpus = [tokenize(doc) for doc in corpus]
        self.doc_lens = [len(doc) for doc in self.tokenized_corpus]
        self.avg_doc_len = sum(self.doc_lens) / max(self.corpus_size, 1)

        self.df = {}
        for doc in self.tokenized_corpus:
            for token in set(doc):
                self.df[token] = self.df.get(token, 0) + 1


def clean_for_quote_match(text: str) -> str:
    """Normalize text for quote matching:
    - Lowercase
    - Normalize smart quotes & unicode hyphens
    - De-hyphenate line break splits (e.g. 'disequil -\\nibrating' -> 'disequilibrating')
    - Strip punctuation and collapse whitespace
    """
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[\u2018\u2019]", "'", text)
    text = re.sub(r"[\u201c\u201d]", '"', text)
    text = re.sub(r"(\w+)\s*-\s*\n\s*(\w+)", r"\1\2", text)
    text = re.sub(r"-\s*\n\s*", "", text)
    text = re.sub(r"[^\w\s]", " ", text)
    return " ".join(text.split())


def quote_snapping_verify(
    quote: str,
    corpus_chunks: list[str],
    min_words: int = 4,
    shingle_size: int = 6,
    shingle_match_ratio: float = 0.5,
) -> bool:
    """Verify whether a candidate quote exists on physical disk, with Quote Snapping:
    1. Exact cleaned substring check across corpus chunks.
    2. Ellipsis-aware subsegment verification (if model used '...').
    3. Shingle-based fuzzy token alignment to accommodate OCR artifacts & minor omission.
    """
    if not quote or not corpus_chunks:
        return False

    # Handle ellipsis joins
    if "..." in quote:
        sub_quotes = [q.strip() for q in quote.split("...") if len(q.strip().split()) >= 3]
        if sub_quotes:
            return all(quote_snapping_verify(sq, corpus_chunks, min_words=min_words) for sq in sub_quotes)

    cq = clean_for_quote_match(quote)
    words = cq.split()
    if len(words) < min_words:
        return False

    # Pass 1: Direct substring check on cleaned corpus chunks
    for chunk in corpus_chunks:
        c_chunk = clean_for_quote_match(chunk)
        if cq in c_chunk:
            return True

    # Pass 2: Shingle-based sliding window match (Quote Snapping)
    if len(words) <= shingle_size:
        return False

    shingles = [" ".join(words[i : i + shingle_size]) for i in range(len(words) - shingle_size + 1)]
    if not shingles:
        return False

    for chunk in corpus_chunks:
        c_chunk = clean_for_quote_match(chunk)
        hits = sum(1 for s in shingles if s in c_chunk)
        if (hits / len(shingles)) >= shingle_match_ratio:
            return True

    return False


    def idf(self, token: str) -> float:
        freq = self.df.get(token, 0)
        return math.log(1.0 + (self.corpus_size - freq + 0.5) / (freq + 0.5))

    def top(self, query: str, k: int = 10) -> list[tuple[int, float]]:
        """Return top-k matching documents as (doc_index, score) pairs, score > 0."""
        q_tokens = tokenize(query)
        if not q_tokens or not self.corpus_size:
            return []

        scores = []
        for idx, doc in enumerate(self.tokenized_corpus):
            if not doc:
                continue
            doc_len = self.doc_lens[idx]
            score = 0.0
            for token in q_tokens:
                freq = doc.count(token)
                if not freq:
                    continue
                idf_val = self.idf(token)
                num = freq * (self.k1 + 1.0)
                denom = freq + self.k1 * (1.0 - self.b + self.b * (doc_len / max(self.avg_doc_len, 1e-6)))
                score += idf_val * (num / denom)
            if score > 0:
                scores.append((idx, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:k]


def load_pages(corpus_dir: Path | str | None = None) -> list[dict]:
    """Load text pages from textbook txt files containing '--- Page N ---' markers.

    Returns a list of dicts:
        {"doc": doc_name, "page": page_num, "section": section_name, "text": page_text}
    """
    cdir = Path(corpus_dir) if corpus_dir else CORPUS_DIR
    pages = []

    for file_path in sorted(cdir.glob("*.txt")):
        doc_name = file_path.stem
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        raw_parts = re.split(r"--- Page (\d+) ---", content)
        if len(raw_parts) > 1:
            for i in range(1, len(raw_parts), 2):
                try:
                    p_num = int(raw_parts[i])
                    p_text = raw_parts[i + 1].strip()
                    if p_text:
                        # Extract first header line if available as section hint
                        lines = [l.strip() for l in p_text.splitlines() if l.strip()]
                        section = lines[0][:80] if lines else doc_name
                        pages.append({
                            "doc": doc_name,
                            "page": p_num,
                            "section": section,
                            "text": p_text
                        })
                except Exception:
                    continue
        else:
            # Fallback if no page markers
            pages.append({
                "doc": doc_name,
                "page": 1,
                "section": doc_name,
                "text": content.strip()
            })

    return pages
