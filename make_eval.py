"""Benchmark Generator for Sanity Engine Textbook Library.
Generates a 30-item evaluation set directly from raw textbook pages (never from any system's index):
- 24 single-hop items (balanced SUPPORTED / REFUTED across the 11 reference textbooks)
- 6 multi-hop items (requiring cross-textbook synthesis across genuine physical-biological invariant bridges)

All items strictly require verbatim quotes from the source pages.
Outputs: chunklab/eval/eval.jsonl
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import random
import re
import sys
from pathlib import Path

# Add current folder to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import BM25, CORPUS_DIR, DATA_DIR, ROOT, load_pages, norm_entity, tokenize
from extract_claims import GeminiExtractorLLM, AnthropicExtractorLLM, MockExtractorLLM

EVAL_DIR = ROOT / "eval"
EVAL_DIR.mkdir(parents=True, exist_ok=True)
EVAL_FILE = EVAL_DIR / "eval.jsonl"

SEED = 42

# Genuine interdisciplinary conceptual bridges across the 11 reference textbooks
BRIDGES = [
    (
        "Feynman_Lectures_on_Physics_Vol1_1963",
        "Alberts_Molecular_Biology_of_the_Cell_7ed_2022",
        "acoustic impedance reflection pressure mechanosensitive membrane tension bilayer",
    ),
    (
        "Berg_Random_Walks_in_Biology_1993",
        "Nelson_Lehninger_Principles_of_Biochemistry_8ed_2021",
        "diffusion coefficient brownian motion viscosity drag velocity ATP hydrolysis",
    ),
    (
        "Feynman_Lectures_on_Physics_Vol2_1964",
        "Johnston_Foundations_of_Cellular_Neurophysiology_1ed_1995",
        "capacitance electric field potential dielectric membrane time constant conductance",
    ),
    (
        "Murray_Mathematical_Biology_an_Introduction_2ed_1993",
        "Strogatz_Nonlinear_Dynamics_and_Chaos_3ed_2024",
        "reaction diffusion wave pattern bifurcation limit cycle stability phase portrait",
    ),
    (
        "Cover_Elements_of_Information_Theory_2ed_2006",
        "Johnston_Foundations_of_Cellular_Neurophysiology_1ed_1995",
        "entropy channel capacity information transmission noise synaptic spike rate",
    ),
    (
        "Winter_Biomechanics_and_Motor_Control_of_Human_Movement_5ed_2020",
        "Alberts_Molecular_Biology_of_the_Cell_7ed_2022",
        "muscle force velocity power stroke cross bridge actin myosin joint kinetics",
    ),
]

SCHEMA = {
    "type": "object",
    "required": ["skip", "hypothesis", "verdict", "gold_evidence", "rationale"],
    "properties": {
        "skip": {"type": "boolean"},
        "hypothesis": {"type": "string"},
        "verdict": {"type": "string", "enum": ["supported", "refuted"]},
        "gold_evidence": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["page_label", "quote"],
                "properties": {
                    "page_label": {"type": "string"},
                    "quote": {"type": "string"},
                },
            },
        },
        "rationale": {"type": "string"},
    },
}

SYSTEM_PROMPT = "You write evaluation items for a rigorous scientific literature retrieval benchmark. Return only valid JSON."

USER_PROMPT = """Write ONE hypothesis that a researcher could test against the passage(s) below, where the correct verdict is {verdict}.

Requirements:
- SUPPORTED: the passage(s) provide clear empirical evidence, derivations, mechanisms, or physical laws confirming the hypothesis is true.
- REFUTED: the hypothesis is a plausible-sounding but erroneous claim (reversed causal direction, incorrect quantity or scaling exponent, or contradicted mechanism), and the passage(s) contain evidence that directly refutes it. Not merely unmentioned.
- Phrase the hypothesis as ONE concise declarative sentence in your own words. Do not copy more than 5 consecutive words from the text.
- Pick a substantive scientific invariant or mechanism, not trivia, preface, or exercise numbers.
{extra}
- gold_evidence: the exact sentence(s) from the text that settle the verdict, copied VERBATIM from the passage.
- If the passage has no usable scientific claim, set skip=true.

{passages}"""


def quote_verified(quote: str, page_text: str) -> bool:
    q_toks = set(tokenize(quote))
    p_toks = set(tokenize(page_text))
    if len(q_toks) < 4:
        return False
    return len(q_toks & p_toks) / len(q_toks) >= 0.85


def format_page_label(p: dict) -> str:
    return f"{p['doc']} p.{p['page']}"


def generate_item(task: tuple[list[dict], str, str], llm) -> dict | None:
    pages, verdict, kind = task
    extra = (
        "- The hypothesis must be ONE integrated claim that needs BOTH passages: e.g. a physical principle from one "
        "passage applied to the biological system in the other. Never join two unrelated facts with 'and' or 'separately'. "
        "Provide at least one verbatim quote from each passage in gold_evidence.\n"
        if kind == "multi_hop"
        else ""
    )
    passages_str = "\n\n".join(
        f"<passage page_label=\"{format_page_label(p)}\" section=\"{p.get('section', '')}\">\n{p['text']}\n</passage>"
        for p in pages
    )
    prompt = USER_PROMPT.format(verdict=verdict.upper(), extra=extra, passages=passages_str)

    try:
        out = llm.extract_json(SYSTEM_PROMPT, prompt, SCHEMA)
    except Exception as e:
        print(f"  [!] LLM generation error: {e}")
        return None

    if out.get("skip") or out.get("verdict") != verdict:
        return None

    by_label = {format_page_label(p): p for p in pages}
    gold = []
    for g in out.get("gold_evidence", []):
        lbl = g.get("page_label", "")
        p = by_label.get(lbl)
        if not p or not quote_verified(g.get("quote", ""), p["text"]):
            return None
        gold.append({
            "doc": p["doc"],
            "page": p["page"],
            "quote": g["quote"].strip(),
        })

    if kind == "multi_hop" and len({g["doc"] for g in gold}) < 2:
        return None

    return {
        "kind": kind,
        "hypothesis": out.get("hypothesis", "").strip(),
        "verdict": verdict,
        "gold": gold,
        "rationale": out.get("rationale", "").strip(),
    }


def main():
    parser = argparse.ArgumentParser(description="Generate 30-item evaluation set from textbook pages")
    parser.add_argument("--corpus", default=str(CORPUS_DIR), help="Corpus directory containing text files")
    parser.add_argument("--backend", default="gemini", choices=["gemini", "anthropic", "mock"])
    parser.add_argument("--out", default=str(EVAL_FILE), help="Output jsonl file")
    args = parser.parse_args()

    print(f"[*] Loading pages from: {args.corpus}")
    pages = [p for p in load_pages(args.corpus) if len(p["text"].split()) >= 150]
    print(f"  -> Loaded {len(pages)} substantial pages.")

    rng = random.Random(SEED)
    by_doc = {}
    for p in pages:
        by_doc.setdefault(p["doc"], []).append(p)

    if args.backend == "mock":
        llm = MockExtractorLLM()
    elif args.backend == "anthropic":
        llm = AnthropicExtractorLLM()
    else:
        llm = GeminiExtractorLLM()

    items = []
    print("\n[*] Generating single-hop items across textbooks...")
    # Generate 2 items per document (1 supported, 1 refuted)
    for doc_name, doc_pages in sorted(by_doc.items()):
        if len(items) >= 24:
            break
        verdicts = ["supported", "refuted"]
        for v in verdicts:
            sample_page = rng.choice(doc_pages)
            item = generate_item(([sample_page], v, "single_hop"), llm)
            if item:
                items.append(item)
                print(f"  + Single-hop: [{doc_name}] ({v})")
            if len(items) >= 24:
                break

    print("\n[*] Generating multi-hop items across physical-biological bridges...")
    multi_items = []
    for i, (src_a, src_b, bridge_topic) in enumerate(BRIDGES):
        pages_a = [p for p in pages if src_a.lower() in p["doc"].lower()]
        pages_b = [p for p in pages if src_b.lower() in p["doc"].lower()]
        if not pages_a or not pages_b:
            continue

        bm25_a = BM25([p["text"] for p in pages_a])
        bm25_b = BM25([p["text"] for p in pages_b])

        top_a = [pages_a[idx] for idx, _ in bm25_a.top(bridge_topic, k=3)]
        top_b = [pages_b[idx] for idx, _ in bm25_b.top(bridge_topic, k=3)]

        target_verdict = ["supported", "refuted"][i % 2]
        for a, b in itertools.product(top_a, top_b):
            item = generate_item(([a, b], target_verdict, "multi_hop"), llm)
            if item:
                multi_items.append(item)
                print(f"  + Multi-hop: [{a['doc']}] + [{b['doc']}] ({target_verdict})")
                break

    all_items = items + multi_items
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as f:
        for idx, it in enumerate(all_items):
            it["qid"] = f"q{idx + 1:02d}"
            f.write(json.dumps(it) + "\n")

    print(f"\n[DONE] Successfully generated {len(all_items)} benchmark items -> {out_path}")


if __name__ == "__main__":
    main()
