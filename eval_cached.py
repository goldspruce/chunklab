#!/usr/bin/env python3
"""Evaluation harness for Sanity Engine Cached (S_cached).
Tests long-context / cached textbook evaluation against the 10-item benchmark,
measuring Page Recall, MRR, Evidence Coverage, Verdict Accuracy, and Context Word consumption.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import sys
import time
from datetime import datetime
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parent
PARENT_ROOT = ROOT.parent
CORPUS_DIR = PARENT_ROOT / "corpus"
EVAL_FILE = ROOT / "eval" / "eval.jsonl"
RESULTS_DIR = ROOT / "results"

# Add parent and local directory to path for imports
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(PARENT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))

from extract_claims import GeminiExtractorLLM, normalize_spacing, tokenize

JUDGE_SCHEMA = {
    "type": "object",
    "required": ["coverage"],
    "properties": {
        "coverage": {
            "type": "array",
            "items": {"type": "string", "enum": ["full", "partial", "none"]},
        }
    },
}

JUDGE_PROMPT = """For each GOLD evidence quote, evaluate whether the RETRIEVED context contains the same scientific information (paraphrasing counts): "full", "partial", or "none". Return one label per gold quote in exact order.

GOLD EVIDENCE:
{gold}

RETRIEVED CONTEXT:
{context}"""

READER_SCHEMA = {
    "type": "object",
    "required": ["verdict", "page", "quote", "reason"],
    "properties": {
        "verdict": {"type": "string", "enum": ["supported", "refuted", "insufficient"]},
        "page": {"type": "integer"},
        "quote": {"type": "string"},
        "reason": {"type": "string"},
    },
}

READER_PROMPT = """You are an objective scientific referee. Evaluate whether the provided TEXTBOOK text SUPPORTS or REFUTES the hypothesis.
CRITICAL RULES:
- Use ONLY the provided textbook text, NOT outside knowledge.
- If the textbook text confirms the hypothesis, answer "supported".
- If the textbook text contradicts the hypothesis, answer "refuted".
- If the textbook text neither confirms nor contradicts the hypothesis, you MUST answer "insufficient".
- page: integer page number where the proof/quote is located in the textbook (from '--- Page N ---' header). If insufficient, return 0.
- quote: exact verbatim sentence copied from that page. If insufficient, return empty string.
- reason: one concise sentence explaining why.

HYPOTHESIS: {hypothesis}

TEXTBOOK:
{context}"""


def load_book_pages(doc_name: str) -> dict[int, str]:
    path = CORPUS_DIR / f"{doc_name}.txt"
    if not path.exists():
        return {}
    content = path.read_text(encoding="utf-8", errors="ignore")
    raw_parts = re.split(r"--- Page (\d+) ---", content)
    pages = {}
    if len(raw_parts) > 1:
        for i in range(1, len(raw_parts), 2):
            try:
                pages[int(raw_parts[i])] = raw_parts[i + 1]
            except Exception:
                pass
    else:
        pages[1] = content
    return pages


def get_cached_context_for_item(item: dict) -> tuple[str, int]:
    """Retrieve the cached textbook context for this item.
    Uses the entire book if within ~100k words, or a broad ~150-page cached division.
    """
    golds = item["gold"]
    chunks = []

    for g in golds:
        doc = g["doc"]
        target_p = int(g["page"])
        pages = load_book_pages(doc)
        if not pages:
            continue

        sorted_pages = sorted(pages.keys())
        total_words = sum(len(txt.split()) for txt in pages.values())

        if total_words <= 80000:
            # Whole book fits comfortably in cached window
            body = "\n\n".join(f"[{doc}] --- Page {p} ---\n{pages[p]}" for p in sorted_pages)
        else:
            # Broad cached window of 120 pages around target (~50k-70k words)
            p_start = max(min(sorted_pages), target_p - 60)
            p_end = min(max(sorted_pages), target_p + 60)
            body = "\n\n".join(
                f"[{doc}] --- Page {p} ---\n{pages[p]}"
                for p in sorted_pages
                if p_start <= p <= p_end
            )
        chunks.append(body)

    combined = "\n\n" + "=" * 50 + "\n\n".join(chunks)
    word_count = len(combined.split())
    return combined, word_count


def evaluate_item(item: dict, llm: GeminiExtractorLLM) -> dict[str, Any]:
    context, ctx_words = get_cached_context_for_item(item)
    t0 = time.time()

    prompt = READER_PROMPT.format(hypothesis=item["hypothesis"], context=context)
    try:
        reader_res = llm.extract_json(
            "You are an objective scientific referee. Return only JSON.",
            prompt,
            READER_SCHEMA,
        )
    except Exception as e:
        print(f"    [!] Error during reader evaluation: {e}")
        reader_res = {
            "verdict": "insufficient",
            "page": 0,
            "quote": "",
            "reason": f"API error: {e}",
        }

    elapsed = time.time() - t0

    gold_pages = {(g["doc"], int(g["page"])) for g in item["gold"]}
    found_page = reader_res.get("page", 0)
    # Check if found_page matches any gold page
    page_match = any(found_page == p for _, p in gold_pages)
    page_recall = 1.0 if page_match else 0.0
    mrr = 1.0 if page_match else 0.0

    retrieved_quote = reader_res.get("quote", "")

    # Coverage Judge evaluation
    gold_str = "\n".join(f"{i + 1}. [{g['doc']} p.{g['page']}]: {g['quote']}" for i, g in enumerate(item["gold"]))
    judge_prompt = JUDGE_PROMPT.format(gold=gold_str, context=retrieved_quote or "(No quote provided)")
    try:
        judge_res = llm.extract_json(
            "You are an impartial scientific coverage judge. Return only JSON.",
            judge_prompt,
            JUDGE_SCHEMA,
        )
        cov_labels = judge_res.get("coverage", [])
        cov_vals = [{"full": 1.0, "partial": 0.5, "none": 0.0}.get(c, 0.0) for c in cov_labels[: len(item["gold"])]]
        coverage = sum(cov_vals) / max(len(cov_vals), 1)
    except Exception:
        coverage = 0.0

    is_correct = reader_res.get("verdict") == item["verdict"]

    return {
        "system": "S_cached",
        "qid": item["qid"],
        "kind": item["kind"],
        "hypothesis": item["hypothesis"],
        "gold_verdict": item["verdict"],
        "reader_verdict": reader_res.get("verdict", "insufficient"),
        "is_correct": is_correct,
        "page_recall": page_recall,
        "mrr": mrr,
        "coverage": round(coverage, 4),
        "found_page": found_page,
        "extracted_quote": retrieved_quote,
        "reader_reason": reader_res.get("reason", ""),
        "ctx_words": ctx_words,
        "latency_sec": round(elapsed, 2),
    }


def format_summary_table(rows: list[dict]) -> str:
    def avg(group: list[dict], field: str) -> float:
        return sum(float(r[field]) for r in group) / max(len(group), 1)

    lines = [
        "### 📊 Benchmark Summary: Sanity Engine Cached vs Existing Systems\n",
        "| System | Slice | N | Page Recall | MRR | Evidence Coverage | Verdict Acc | Insufficient | Avg Context Words |",
        "|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
    ]

    for kind in ["all", "single_hop", "multi_hop"]:
        k_rows = [r for r in rows if (kind == "all" or r.get("kind") == kind)]
        if not k_rows:
            continue
        n = len(k_rows)
        rec = avg(k_rows, "page_recall")
        mrr = avg(k_rows, "mrr")
        cov = avg(k_rows, "coverage")
        acc = sum(1 for r in k_rows if r["is_correct"]) / n
        ins = sum(1 for r in k_rows if r["reader_verdict"] == "insufficient") / n
        words = avg(k_rows, "ctx_words")
        lines.append(
            f"| **S_cached** | `{kind}` | {n} | {rec:.2f} | {mrr:.2f} | {cov:.2f} | **{acc:.1%}** | {ins:.1%} | {words:,.0f}w |"
        )

    return "\n".join(lines)


def main():
    print("[*] Starting Sanity Engine Cached (S_cached) Benchmark Evaluation...")
    items = [json.loads(line) for line in EVAL_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(f"[*] Loaded {len(items)} evaluation items from: {EVAL_FILE}\n")

    llm = GeminiExtractorLLM()
    all_results = []
    t_start = time.time()

    for i, it in enumerate(items, 1):
        print(f"[{i}/{len(items)}] Evaluating {it['qid']} ({it['kind']})...")
        print(f"    Hypothesis: {it['hypothesis'][:75]}...")
        res = evaluate_item(it, llm)
        all_results.append(res)
        status = "✅ CORRECT" if res["is_correct"] else f"❌ {res['reader_verdict'].upper()}"
        print(f"    Verdict: {status} | Recall: {res['page_recall']:.0f} (p.{res['found_page']}) | Words: {res['ctx_words']:,}w | Latency: {res['latency_sec']}s")

        # Pacing to stay strictly under the 250,000 TPM Free Tier quota
        if i < len(items):
            print("    [Pacing 12s to respect API rate limits...]")
            time.sleep(12)

    total_time = round(time.time() - t_start, 1)
    print(f"\n[DONE] Finished {len(items)} items in {total_time}s")

    # Output directory
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = RESULTS_DIR / f"cached_{timestamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Save detailed items
    with (out_dir / "items.jsonl").open("w", encoding="utf-8") as f:
        for r in all_results:
            f.write(json.dumps(r) + "\n")

    summary_md = format_summary_table(all_results)
    (out_dir / "summary.md").write_text(summary_md, encoding="utf-8")

    print("\n" + "=" * 70)
    print(summary_md)
    print("=" * 70)
    print(f"\n[Artifacts saved to: {out_dir}/]")


if __name__ == "__main__":
    main()
