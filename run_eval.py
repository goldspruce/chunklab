"""Automated Benchmark Harness for Chunklab & Sanity Engine.
Scores retrieval systems across 4 evaluation layers under controlled reading budgets:
  1. Budgeted context enforcement (e.g. 400 words vs. 1500 words)
  2. Page Recall & MRR (Deterministic ground-truth hits)
  3. Evidence Coverage Judge (LLM evaluation against gold quotes)
  4. Blind Reader Verdict (LLM reader deciding SUPPORTED / REFUTED / INSUFFICIENT)
  5. S0 Control (No-retrieval baseline verifying zero parametric memory leakage)

Usage:
  .venv/bin/python chunklab/run_eval.py [S0_none S1_plain S2_relational S3_graph] [--budget 400]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any

# Add current folder to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import DATA_DIR, ROOT, tokenize
from retrieval import BaseRetriever, ClaimGraph, ClaimsDB, PlainChunks, Hit
from extract_claims import GeminiExtractorLLM, AnthropicExtractorLLM, MockExtractorLLM

RESULTS_DIR = ROOT / "results"
EVAL_FILE = ROOT / "eval" / "eval.jsonl"


# ====================================================================== S0: Negative Control
class NoRetrieval(BaseRetriever):
    """Control system passing zero retrieved context to test memory leakage."""

    name = "S0_none"

    def search(self, query: str, k: int = 5) -> list[Hit]:
        return []


def get_system_map(claims_file: Path | str | None = None, auto_jit: bool = False) -> dict[str, Any]:
    c_file = claims_file
    if not c_file:
        for p in [DATA_DIR / "claims.jsonl", DATA_DIR / "real_claims.jsonl", DATA_DIR / "test_claims.jsonl"]:
            if p.exists() and p.stat().st_size > 0:
                c_file = p
                break

    return {
        "S0_none": lambda: NoRetrieval(),
        "S1_plain": lambda: PlainChunks(),
        "S2_relational": lambda: ClaimsDB(claims_file=c_file, auto_jit=auto_jit),
        "S3_graph": lambda: ClaimGraph(claims_file=c_file, auto_jit=auto_jit),
    }


# ====================================================================== LLM Prompts & Schemas
READER_SCHEMA = {
    "type": "object",
    "required": ["verdict", "cited", "reason"],
    "properties": {
        "verdict": {"type": "string", "enum": ["supported", "refuted", "insufficient"]},
        "cited": {"type": "array", "items": {"type": "integer"}},
        "reason": {"type": "string"},
    },
}

READER_PROMPT = """Decide whether the evidence below SUPPORTS or REFUTES the hypothesis.
CRITICAL RULES:
- Use ONLY this provided evidence, NOT outside knowledge.
- If the evidence neither confirms nor contradicts the hypothesis, you MUST answer "insufficient".
- cited: the [numbers] of the evidence items you relied on (e.g. [1, 2]).

HYPOTHESIS: {hypothesis}

EVIDENCE:
{context}"""

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


def count_words(text: str) -> int:
    return len(text.split()) if text else 0


def apply_budget(system: BaseRetriever, query: str, max_words: int) -> tuple[list[Hit], int]:
    """Retrieve items from system until cumulative word count reaches budget."""
    hits = []
    used_words = 0
    all_hits = system.search(query, k=25)

    for h in all_hits:
        w = count_words(h.text)
        if hits and (used_words + w > max_words):
            break
        hits.append(h)
        used_words += w

    return hits, used_words


def score_item(item: dict, hits: list[Hit], ctx: str, llm: Any) -> dict[str, Any]:
    gold_pages = {(g["doc"], int(g["page"])) for g in item["gold"]}
    found_pages = set()
    first_hit_rank = None

    for rank, h in enumerate(hits, 1):
        h_pages = {(h.doc, p) for p in h.pages}
        if "extra_refs" in h:
            h_pages |= {(doc, p) for doc, p in h["extra_refs"]}
        match = h_pages & gold_pages
        if match:
            found_pages |= match
            if first_hit_rank is None:
                first_hit_rank = rank

    page_recall = len(found_pages) / max(len(gold_pages), 1)
    mrr = (1.0 / first_hit_rank) if first_hit_rank else 0.0

    # Blind Reader evaluation
    reader_input = READER_PROMPT.format(hypothesis=item["hypothesis"], context=ctx or "(No context provided)")
    try:
        reader_res = llm.extract_json("You are an objective scientific evidence reader. Return only JSON.", reader_input, READER_SCHEMA)
    except Exception:
        reader_res = {"verdict": "insufficient", "cited": [], "reason": "Evaluation timeout or error"}

    # Coverage Judge evaluation
    gold_str = "\n".join(f"{i + 1}. [{g['doc']} p.{g['page']}]: {g['quote']}" for i, g in enumerate(item["gold"]))
    judge_input = JUDGE_PROMPT.format(gold=gold_str, context=ctx or "(No context provided)")
    try:
        judge_res = llm.extract_json("You are an impartial scientific coverage judge. Return only JSON.", judge_input, JUDGE_SCHEMA)
        cov_labels = judge_res.get("coverage", [])
        cov_vals = [{"full": 1.0, "partial": 0.5, "none": 0.0}.get(c, 0.0) for c in cov_labels[: len(item["gold"])]]
        coverage = sum(cov_vals) / max(len(cov_vals), 1)
    except Exception:
        coverage = 0.0

    is_correct = reader_res.get("verdict") == item["verdict"]

    return {
        "page_recall": round(page_recall, 4),
        "mrr": round(mrr, 4),
        "coverage": round(coverage, 4),
        "reader_verdict": reader_res.get("verdict", "insufficient"),
        "is_correct": is_correct,
        "reader_reason": reader_res.get("reason", ""),
    }


def format_summary_table(rows: list[dict], budget: int) -> str:
    def avg(group: list[dict], field: str) -> float:
        return sum(float(r[field]) for r in group) / max(len(group), 1)

    systems = sorted(list({r["system"] for r in rows}))
    lines = [
        f"### 📊 Benchmark Summary (Context Budget: {budget} words)\n",
        "| System | Slice | N | Page Recall | MRR | Evidence Coverage | Verdict Acc | Insufficient | Avg Context Words |",
        "|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
    ]

    for sys_name in systems:
        sys_rows = [r for r in rows if r["system"] == sys_name]
        for kind in ["all", "single_hop", "multi_hop"]:
            k_rows = [r for r in sys_rows if (kind == "all" or r.get("kind") == kind)]
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
                f"| **{sys_name}** | `{kind}` | {n} | {rec:.2f} | {mrr:.2f} | {cov:.2f} | **{acc:.1%}** | {ins:.1%} | {words:.0f}w |"
            )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Run 4-tier benchmark evaluation over Chunklab retrieval systems")
    parser.add_argument("systems", nargs="*", default=["S0_none", "S1_plain", "S2_relational", "S3_graph"],
                        help="Systems to evaluate")
    parser.add_argument("--budget", type=int, default=400, help="Max words of context passed to reader")
    parser.add_argument("--eval", default=str(EVAL_FILE), help="Path to eval.jsonl")
    parser.add_argument("--backend", default="mock", choices=["gemini", "anthropic", "mock"])
    parser.add_argument("--claims", default=None, help="Path to claims.jsonl file for S2 and S3")
    parser.add_argument("--jit", action="store_true", help="Enable Just-In-Time extraction during evaluation")
    parser.add_argument("--out", default=None, help="Output results directory")
    args = parser.parse_args()

    eval_path = Path(args.eval)
    if not eval_path.exists():
        print(f"Error: Eval file not found at {eval_path}. Run make_eval.py first.")
        sys.exit(1)

    items = [json.loads(line) for line in eval_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(f"[*] Loaded {len(items)} evaluation items from: {eval_path}")

    # Set up LLM backend
    if args.backend == "mock":
        llm = MockExtractorLLM()
    elif args.backend == "anthropic":
        llm = AnthropicExtractorLLM()
    else:
        llm = GeminiExtractorLLM()

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = Path(args.out) if args.out else RESULTS_DIR / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    system_factories = get_system_map(args.claims, auto_jit=args.jit)
    all_results = []

    print(f"[*] Starting benchmark evaluation (Budget: {args.budget} words)...")

    for sys_name in args.systems:
        if sys_name not in system_factories:
            print(f"  [!] Unknown system: {sys_name}, skipping.")
            continue

        print(f"\n---> Evaluating [{sys_name}]...")
        t0 = time.time()
        system = system_factories[sys_name]()
        build_time = time.time() - t0

        for it in items:
            hits, used_words = apply_budget(system, it["hypothesis"], args.budget)
            ctx = "\n\n".join(
                f"[{i + 1}] ({h.doc} p.{','.join(map(str, h.pages))} | {h.section})\n{h.text}"
                for i, h in enumerate(hits)
            )

            scores = score_item(it, hits, ctx, llm)
            row = {
                "system": sys_name,
                "qid": it["qid"],
                "kind": it["kind"],
                "hypothesis": it["hypothesis"],
                "gold_verdict": it["verdict"],
                "ctx_words": used_words,
                "n_hits": len(hits),
                **scores,
            }
            all_results.append(row)

        elapsed = time.time() - t0
        print(f"     Finished {len(items)} items in {elapsed:.1f}s (Init: {build_time:.1f}s)")

    # Save detailed items
    with (out_dir / "items.jsonl").open("w", encoding="utf-8") as f:
        for r in all_results:
            f.write(json.dumps(r) + "\n")

    # Generate and save summary
    summary_md = format_summary_table(all_results, args.budget)
    (out_dir / "summary.md").write_text(summary_md, encoding="utf-8")

    print("\n" + "=" * 65)
    print(summary_md)
    print("=" * 65)
    print(f"\n[DONE] Full benchmark artifacts saved to: {out_dir}/")


if __name__ == "__main__":
    main()
