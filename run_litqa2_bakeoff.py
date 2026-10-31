#!/usr/bin/env python3
"""LitQA2 (FutureHouse LAB-Bench) Deep Body-Text Retrieval Bake-Off.
Compares Raw Frontier LLMs vs S1 BM25 vs S2 Relational Propositions vs S_cached Long Context.
Measures:
1. Accuracy: Correct / Total Questions
2. Precision: Correct / (Correct + Incorrect) [Excluding Insufficient Info]
3. Hallucination / Error Rate: Incorrect Choices / Total Questions
4. Abstention Rate: Insufficient Info Chosen / Total Questions
5. Context Words Consumed and Latency
"""
from __future__ import annotations

import json
import os
import pathlib
import random
import re
import sys
import time
from datetime import datetime
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parent
PARENT_ROOT = ROOT.parent
DATA_DIR = ROOT / "data"
LITQA_DIR = DATA_DIR / "litqa2"
RESULTS_DIR = ROOT / "results" / "litqa2_bakeoff"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Add directories to path
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(PARENT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))

from common import BM25, tokenize, quote_snapping_verify, norm_entity
from extract_claims import GeminiExtractorLLM

import string
CHOICE_LETTERS = list(string.ascii_uppercase)

ANSWER_SCHEMA = {
    "type": "object",
    "required": ["choice", "reasoning"],
    "properties": {
        "choice": {"type": "string", "description": "The single capital letter of the selected choice, e.g. 'A', 'B', 'C', 'D', 'E'"},
        "reasoning": {"type": "string", "description": "Brief 1-2 sentence justification for this choice"},
        "verbatim_quote": {"type": "string", "description": "Exact quote copied verbatim from the provided literature supporting the choice, or empty if none"},
    },
}

RAW_SYSTEM_PROMPT = """You are an expert scientific researcher taking a rigorous biomedical literature exam (LitQA2).
Select the single best answer choice for the question.
If the literature you know does not provide definitive, verifiable evidence for the exact factual claim, you MUST choose the option for 'Insufficient information to determine from the literature'.
Do NOT guess. Random guessing on scientific facts is heavily penalized as hallucination.
Return only valid JSON."""

RETRIEVED_SYSTEM_PROMPT = """You are an objective scientific referee taking a rigorous biomedical literature exam (LitQA2).
Answer the multiple choice question using ONLY the provided literature passages.
If the provided literature does NOT contain explicit, verifiable evidence to determine the answer, you MUST choose the option for 'Insufficient information to determine from the literature'.
Do NOT make assumptions beyond the text.
Return only valid JSON."""


def load_litqa2_dataset() -> tuple[list[dict], list[dict]]:
    import pandas as pd
    parquet_path = LITQA_DIR / "litqa2.parquet"
    if not parquet_path.exists():
        raise FileNotFoundError(f"Missing {parquet_path}. Download it first.")

    df = pd.read_parquet(parquet_path)
    valid_df = df[df["key-passage"].notna() & (df["key-passage"].str.strip() != "")].copy()

    # Build corpus of all key passages across the 194 items
    corpus = []
    for idx, row in valid_df.iterrows():
        p_text = str(row["key-passage"]).strip()
        corpus.append({
            "id": f"passage_{idx}",
            "item_id": str(row["id"]),
            "sources": list(row["sources"]) if hasattr(row["sources"], "__iter__") else [str(row["sources"])],
            "text": p_text,
        })

    # Pick 10 diverse benchmark questions across biology, genetics, immunology, pharmacology
    test_items = []
    sample_indices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]  # First 10 diverse items
    for s_idx in sample_indices:
        r = valid_df.iloc[s_idx]
        ideal = str(r["ideal"]).strip()
        distractors = [str(d).strip() for d in list(r["distractors"]) if str(d).strip()]
        
        # Build shuffled deterministic options
        rng = random.Random(s_idx + 42)
        all_options = [ideal] + distractors
        rng.shuffle(all_options)
        
        # Append "Insufficient information" as last option
        insufficient_text = "Insufficient information to determine from the literature / I don't know"
        all_options.append(insufficient_text)

        choice_map = {}
        ideal_letter = None
        insufficient_letter = None
        options_text_list = []
        for l_idx, opt_text in enumerate(all_options):
            letter = CHOICE_LETTERS[l_idx]
            choice_map[letter] = opt_text
            options_text_list.append(f"({letter}) {opt_text}")
            if opt_text == ideal:
                ideal_letter = letter
            elif opt_text == insufficient_text:
                insufficient_letter = letter

        test_items.append({
            "idx": s_idx + 1,
            "id": str(r["id"]),
            "question": str(r["question"]).strip(),
            "ideal": ideal,
            "distractors": distractors,
            "key_passage": str(r["key-passage"]).strip(),
            "sources": list(r["sources"]) if hasattr(r["sources"], "__iter__") else [str(r["sources"])],
            "options": choice_map,
            "options_formatted": "\n".join(options_text_list),
            "ideal_letter": ideal_letter,
            "insufficient_letter": insufficient_letter,
        })

    return test_items, corpus


def run_litqa_query(
    system_name: str,
    item: dict,
    corpus: list[dict],
    bm25_index: BM25,
    llm: GeminiExtractorLLM,
    cached_corpus_text: str = "",
) -> dict:
    q_text = item["question"]
    opts_text = item["options_formatted"]
    ideal_letter = item["ideal_letter"]
    insufficient_letter = item["insufficient_letter"]

    ctx_text = ""
    ctx_words = 0

    if system_name == "Raw_Frontier_LLM":
        system_prompt = RAW_SYSTEM_PROMPT
        user_prompt = f"Scientific Question:\n{q_text}\n\nOptions:\n{opts_text}\n\nSelect the best choice:"
    elif system_name == "S1_bm25":
        # Retrieve top 3 passages using BM25
        top_hits = bm25_index.top(q_text, k=3)
        retrieved_passages = [f"[{corpus[idx]['id']}]:\n{corpus[idx]['text']}" for idx, _ in top_hits]
        ctx_text = "\n\n---\n\n".join(retrieved_passages)
        ctx_words = len(ctx_text.split())
        system_prompt = RETRIEVED_SYSTEM_PROMPT
        user_prompt = f"Provided Literature Passages:\n{ctx_text}\n\nScientific Question:\n{q_text}\n\nOptions:\n{opts_text}\n\nSelect the best choice:"
    elif system_name == "S2_relational":
        # Relational Proposition matching: find passages matching key question entities
        q_tokens = set(tokenize(q_text))
        scored = []
        for p in corpus:
            p_tokens = set(tokenize(p["text"]))
            overlap = len(q_tokens.intersection(p_tokens))
            if overlap > 0:
                scored.append((overlap, p))
        scored.sort(key=lambda x: x[0], reverse=True)
        top_rel = [f"[{p['id']} - Entity Overlap {sc}]:\n{p['text']}" for sc, p in scored[:3]]
        ctx_text = "\n\n---\n\n".join(top_rel)
        ctx_words = len(ctx_text.split())
        system_prompt = RETRIEVED_SYSTEM_PROMPT
        user_prompt = f"Relational Literature Evidence:\n{ctx_text}\n\nScientific Question:\n{q_text}\n\nOptions:\n{opts_text}\n\nSelect the best choice:"
    elif system_name == "S_cached":
        # Full long-context cache of all 194 scientific paper passages (~24k words)
        ctx_text = cached_corpus_text
        ctx_words = len(ctx_text.split())
        system_prompt = RETRIEVED_SYSTEM_PROMPT
        user_prompt = f"Complete Scientific Literature Library:\n{ctx_text}\n\nScientific Question:\n{q_text}\n\nOptions:\n{opts_text}\n\nSelect the best choice:"
    else:
        raise ValueError(f"Unknown system: {system_name}")

    t0 = time.time()
    try:
        res = llm.extract_json(system=system_prompt, user=user_prompt, schema=ANSWER_SCHEMA)
    except Exception as e:
        print(f"    [!] Error during LLM extraction: {e}")
        res = {"choice": insufficient_letter, "reasoning": f"Exception encountered: {e}", "verbatim_quote": ""}
    latency = round(time.time() - t0, 2)

    raw_choice = str(res.get("choice", "")).strip().upper()
    # Extract leading letter if model output e.g. "A)" or "Choice B"
    match = re.search(r"\b([A-I])\b", raw_choice)
    choice = match.group(1) if match else raw_choice[:1]

    # Evaluate classification
    is_correct = (choice == ideal_letter)
    is_abstained = (choice == insufficient_letter)
    is_hallucination = (not is_correct) and (not is_abstained)

    raw_quote = str(res.get("verbatim_quote", "")).strip()
    corpus_texts = [p["text"] for p in corpus]
    is_quote_verified = quote_snapping_verify(raw_quote, corpus_texts) if raw_quote else False
    is_bluffing = is_correct and (not is_quote_verified) and bool(raw_quote)

    return {
        "system": system_name,
        "item_idx": item["idx"],
        "item_id": item["id"],
        "question": q_text,
        "ideal_answer": item["ideal"],
        "ideal_letter": ideal_letter,
        "chosen_letter": choice,
        "chosen_text": item["options"].get(choice, "Unknown"),
        "is_correct": is_correct,
        "is_abstained": is_abstained,
        "is_hallucination": is_hallucination,
        "reasoning": res.get("reasoning", ""),
        "verbatim_quote": raw_quote,
        "is_quote_verified": is_quote_verified,
        "is_bluffing": is_bluffing,
        "ctx_words": ctx_words,
        "latency_sec": latency,
    }


def main():
    print("=" * 75)
    print("🔬 Running Path B: FutureHouse LitQA2 Deep Body-Text Retrieval Bake-Off")
    print("Systems: Raw_Frontier_LLM vs S1_bm25 vs S2_relational vs S_cached")
    print("=" * 75 + "\n")

    print("[*] Loading LitQA2 dataset from Hugging Face parquet cache...")
    test_items, corpus = load_litqa2_dataset()
    print(f"[*] Loaded {len(test_items)} test items and {len(corpus)} body-text paper passages.\n")

    print("[*] Building BM25 index over LitQA2 literature passages...")
    corpus_texts = [p["text"] for p in corpus]
    bm25_index = BM25(corpus_texts)
    print("[*] BM25 index built successfully.\n")

    print("[*] Preparing cached long-context library (~24,000 words)...")
    cached_corpus_text = "\n\n====================\n\n".join(
        f"[Paper Passage ID: {p['id']} | Sources: {', '.join(p['sources'])}]\n{p['text']}" for p in corpus
    )
    cached_words = len(cached_corpus_text.split())
    print(f"[*] Cached long context library compiled: {cached_words} words across {len(corpus)} papers.\n")

    llm = GeminiExtractorLLM()

    systems = ["Raw_Frontier_LLM", "S1_bm25", "S2_relational", "S_cached"]
    all_results = []

    for sys_name in systems:
        print(f"\n{'='*25} Evaluating System: {sys_name} {'='*25}")
        for item in test_items:
            print(f"  -> Q{item['idx']}: {item['question'][:65]}...")
            res = run_litqa_query(
                system_name=sys_name,
                item=item,
                corpus=corpus,
                bm25_index=bm25_index,
                llm=llm,
                cached_corpus_text=cached_corpus_text,
            )
            status = "✅ CORRECT" if res["is_correct"] else ("⚠️ ABSTAINED" if res["is_abstained"] else "❌ HALLUCINATED")
            print(f"     Choice: {res['chosen_letter']} ({status}) | Latency: {res['latency_sec']}s | Ctx: {res['ctx_words']}w")
            all_results.append(res)
            
            # Pacing to respect Gemini free-tier rate limits
            if sys_name == "S_cached":
                time.sleep(12.0)
            else:
                time.sleep(2.0)

    # Save detailed JSONL
    items_out = RESULTS_DIR / "items.jsonl"
    with open(items_out, "w", encoding="utf-8") as f:
        for r in all_results:
            f.write(json.dumps(r) + "\n")
    print(f"\n[+] Saved detailed query outputs to {items_out}")

    # Compute Aggregate FutureHouse Scorecard
    scorecard = []
    for sys_name in systems:
        sub = [r for r in all_results if r["system"] == sys_name]
        n_total = len(sub)
        n_correct = sum(1 for r in sub if r["is_correct"])
        n_abstained = sum(1 for r in sub if r["is_abstained"])
        n_hallucinated = sum(1 for r in sub if r["is_hallucination"])

        accuracy = (n_correct / n_total) * 100.0 if n_total > 0 else 0.0
        answered = n_correct + n_hallucinated
        precision = (n_correct / answered) * 100.0 if answered > 0 else 0.0
        hallucination_rate = (n_hallucinated / n_total) * 100.0 if n_total > 0 else 0.0
        abstention_rate = (n_abstained / n_total) * 100.0 if n_total > 0 else 0.0
        avg_ctx = sum(r["ctx_words"] for r in sub) / max(n_total, 1)
        avg_lat = sum(r["latency_sec"] for r in sub) / max(n_total, 1)

        quotes_cited = [r for r in sub if bool(r.get("verbatim_quote"))]
        n_quotes = len(quotes_cited)
        n_verified = sum(1 for r in quotes_cited if r.get("is_quote_verified"))
        n_bluffs = sum(1 for r in sub if r.get("is_bluffing"))

        veracity = (n_verified / n_quotes * 100.0) if n_quotes > 0 else 0.0
        bluff_rate = (n_bluffs / n_total * 100.0) if n_total > 0 else 0.0

        scorecard.append({
            "System": sys_name,
            "N": n_total,
            "Correct": n_correct,
            "Hallucinated": n_hallucinated,
            "Abstained": n_abstained,
            "Accuracy": f"{accuracy:.1f}%",
            "Precision": f"{precision:.1f}%",
            "Veracity": f"{veracity:.1f}%",
            "Bluffing": f"{bluff_rate:.1f}%",
            "Hallucination Rate": f"{hallucination_rate:.1f}%",
            "Abstention Rate": f"{abstention_rate:.1f}%",
            "Avg Ctx Words": f"{int(avg_ctx):,}w",
            "Avg Latency": f"{avg_lat:.2f}s",
        })

    # Render Markdown Table
    summary_md = RESULTS_DIR / "summary.md"
    md_lines = [
        "### 📊 Path B: FutureHouse LitQA2 Deep Body-Text Retrieval Scorecard (With Quote Snapping)\n",
        "| System | Total (N) | Correct | Accuracy (%) | Precision (%) | Quote Veracity (Snapped) | Citation Bluffing (%) | Abstention Rate (%) | Avg Context Words | Avg Latency |",
        "|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
    ]
    for row in scorecard:
        md_lines.append(
            f"| **{row['System']}** | {row['N']} | {row['Correct']} | **{row['Accuracy']}** | **{row['Precision']}** | **{row['Veracity']}** | **{row['Bluffing']}** | {row['Abstention Rate']} | {row['Avg Ctx Words']} | {row['Avg Latency']} |"
        )

    summary_content = "\n".join(md_lines) + "\n"
    summary_md.write_text(summary_content, encoding="utf-8")
    print(f"[+] Saved scorecard summary to {summary_md}\n")
    print(summary_content)


if __name__ == "__main__":
    main()
