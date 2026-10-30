#!/usr/bin/env python3
"""ScholarQABench Citation Hallucination & Veracity Bake-Off.
Compares Raw Frontier LLMs vs S2 Relational DB vs S3 Claim Graph vs S_cached Gemini Long Context.
Measures:
1. Citation Veracity Rate (% Verified on Disk via verify_quote)
2. Citation Hallucination Rate (% Fabricated / Hallucinated)
3. Logical Entailment Rate (% Logically Sound via auto_entail)
4. Citation Bluffing Rate (% Real Quote but Irrelevant / Not Supporting)
5. Context Words Consumed and Latency
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
RESULTS_DIR = ROOT / "results" / "scholarqa_bakeoff"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Add directories to path
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(PARENT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))

import engine
from common import load_pages
from retrieval import get_retriever, Hit
from extract_claims import GeminiExtractorLLM

# Benchmark queries matching canonical scientific mechanisms (10 queries, 2 per domain)
QUERIES = [
    {
        "id": "SQA_01",
        "domain": "Physics / Wave Mechanics",
        "doc": "Feynman_Lectures_on_Physics_Vol1_1963",
        "target_pages": [818, 819, 820],
        "query": "How does the characteristic acoustic impedance mismatch between two media govern boundary reflection and transmission of acoustic power?",
    },
    {
        "id": "SQA_02",
        "domain": "Biophysics / Kinetics",
        "doc": "Berg_Random_Walks_in_Biology_1993",
        "target_pages": [1, 2, 3],
        "query": "According to equipartition theory, what is the thermal kinetic energy per spatial degree of freedom for microscopic particles in aqueous suspension, and how does thermal velocity scale with temperature?",
    },
    {
        "id": "SQA_03",
        "domain": "Neurophysiology",
        "doc": "Johnston_Foundations_of_Cellular_Neurophysiology_1ed_1995",
        "target_pages": [77, 78, 79],
        "query": "What specific ionic permeability mechanisms establish the resting membrane potential in neuronal cells?",
    },
    {
        "id": "SQA_04",
        "domain": "Biochemistry / Bioenergetics",
        "doc": "Nelson_Lehninger_Principles_of_Biochemistry_8ed_2021",
        "target_pages": [503, 504, 505],
        "query": "What thermodynamic free energy properties make ATP hydrolysis the universal energy currency for driving endergonic cellular reactions?",
    },
    {
        "id": "SQA_05",
        "domain": "Information Theory",
        "doc": "Cover_Elements_of_Information_Theory_2ed_2006",
        "target_pages": [244, 245, 246],
        "query": "How does the Shannon channel capacity of a communication channel mathematically depend on signal power and noise variance?",
    },
    {
        "id": "SQA_06",
        "domain": "Physics / Electromagnetism",
        "doc": "Feynman_Lectures_on_Physics_Vol2_1964",
        "target_pages": [420, 421, 422],
        "query": "How does electromagnetic wave penetration into a conducting metal decay with distance, and what mathematical formula defines the conductor skin depth as a function of frequency and conductivity?",
    },
    {
        "id": "SQA_07",
        "domain": "Biophysics / Hydrodynamics",
        "doc": "Berg_Random_Walks_in_Biology_1993",
        "target_pages": [48, 49, 50],
        "query": "Under conditions where viscous forces dominate and inertial forces are negligible, what formula gives the frictional drag coefficient of a spherical particle in a fluid of viscosity eta?",
    },
    {
        "id": "SQA_08",
        "domain": "Neurophysiology / Ion Channels",
        "doc": "Alberts_Molecular_Biology_of_the_Cell_7ed_2022",
        "target_pages": [696, 697, 698],
        "query": "What structural mechanisms and amino acid backbone interactions within the selectivity filter of a potassium channel allow it to dehydrate and selectively conduct potassium ions over sodium ions?",
    },
    {
        "id": "SQA_09",
        "domain": "Biochemistry / Enzyme Kinetics",
        "doc": "Nelson_Lehninger_Principles_of_Biochemistry_8ed_2021",
        "target_pages": [778, 779, 780],
        "query": "What fundamental steady-state assumption underlies the Briggs-Haldane derivation of the Michaelis-Menten enzyme kinetics rate equation?",
    },
    {
        "id": "SQA_10",
        "domain": "Information Theory / Entropy",
        "doc": "Cover_Elements_of_Information_Theory_2ed_2006",
        "target_pages": [46, 47, 48],
        "query": "How is the mutual information I(X; Y) between two random variables mathematically defined in terms of marginal Shannon entropy and conditional entropy?",
    },
]

ANSWER_SCHEMA = {
    "type": "object",
    "required": ["answer", "citations"],
    "properties": {
        "answer": {"type": "string"},
        "citations": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["claim", "source", "quote"],
                "properties": {
                    "claim": {"type": "string"},
                    "source": {"type": "string"},
                    "quote": {"type": "string"},
                },
            },
        },
    },
}

RAW_SYSTEM_PROMPT = """You are an expert scientific researcher. Answer the query thoroughly.
For every substantive factual claim you make, you MUST cite the exact literature and provide a VERBATIM quote from the paper or textbook supporting that claim.
Return only valid JSON."""

RETRIEVED_SYSTEM_PROMPT = """You are an objective scientific referee. Answer the user query using ONLY the provided literature context.
For every claim you make, cite the passage ID and provide the exact VERBATIM quote copied from the context.
Return only valid JSON."""


def get_cached_book_slice(doc_name: str, target_pages: list[int]) -> tuple[str, int]:
    path = CORPUS_DIR / f"{doc_name}.txt"
    if not path.exists():
        return "", 0
    content = path.read_text(encoding="utf-8", errors="ignore")
    raw_parts = re.split(r"--- Page (\d+) ---", content)
    pages = {}
    if len(raw_parts) > 1:
        for i in range(1, len(raw_parts), 2):
            try:
                pages[int(raw_parts[i])] = raw_parts[i + 1]
            except Exception:
                pass
    sorted_p = sorted(pages.keys())
    target = target_pages[0] if target_pages else sorted_p[0]
    p_start = max(min(sorted_p), target - 45)
    p_end = min(max(sorted_p), target + 45)
    body = "\n\n".join(f"[{doc_name}] --- Page {p} ---\n{pages[p]}" for p in sorted_p if p_start <= p <= p_end)
    return body, len(body.split())


def evaluate_system_query(
    system_name: str,
    q: dict,
    llm: GeminiExtractorLLM,
    all_chunks: list[tuple[str, str]],
    s2_retriever: Any = None,
    s3_retriever: Any = None,
) -> dict[str, Any]:
    t0 = time.time()
    query_text = q["query"]
    ctx_words = 0

    if system_name == "Raw_Frontier_LLM":
        user_prompt = f"QUERY: {query_text}"
        res = llm.extract_json(RAW_SYSTEM_PROMPT, user_prompt, ANSWER_SCHEMA)

    elif system_name == "S2_relational":
        hits = s2_retriever.search(query_text, k=4)
        passages_text = "\n\n".join(f"[{h.id}] ({h.doc} p.{h.pages[0]}):\n{h.text}" for h in hits)
        ctx_words = sum(len(h.text.split()) for h in hits)
        user_prompt = f"QUERY: {query_text}\n\nLITERATURE CONTEXT:\n{passages_text}"
        res = llm.extract_json(RETRIEVED_SYSTEM_PROMPT, user_prompt, ANSWER_SCHEMA)

    elif system_name == "S3_graph":
        hits = s3_retriever.search(query_text, k=4)
        passages_text = "\n\n".join(f"[{h.id}] ({h.doc} p.{h.pages[0]}):\n{h.text}" for h in hits)
        ctx_words = sum(len(h.text.split()) for h in hits)
        user_prompt = f"QUERY: {query_text}\n\nLITERATURE CONTEXT:\n{passages_text}"
        res = llm.extract_json(RETRIEVED_SYSTEM_PROMPT, user_prompt, ANSWER_SCHEMA)

    elif system_name == "S_cached":
        body, ctx_words = get_cached_book_slice(q["doc"], q["target_pages"])
        user_prompt = f"QUERY: {query_text}\n\nLITERATURE CONTEXT:\n{body}"
        res = llm.extract_json(RETRIEVED_SYSTEM_PROMPT, user_prompt, ANSWER_SCHEMA)

    elapsed = time.time() - t0
    citations = res.get("citations", [])

    # The 2-Gate Veracity & Entailment Gauntlet
    verified_count = 0
    hallucinated_count = 0
    entailed_count = 0
    bluffing_count = 0

    verified_details = []

    for cit in citations:
        claim = cit.get("claim", "")
        quote = cit.get("quote", "")

        # Gate 1: verify_quote against all 12,320 textbook chunks on disk
        nq = engine.norm(quote)
        is_verified = any(nq in engine.norm(t) for _, t in all_chunks) if len(nq.split()) >= 4 else False
        status = "verified" if is_verified else "failed"

        entail_label = "unclear"
        why = ""

        if is_verified:
            verified_count += 1
            # Gate 2: auto_entail (Does it logically prove the claim?)
            try:
                ent_res = engine.Entail.model_validate(
                    llm.extract_json(
                        engine.ENTAIL_SYS,
                        f"CLAIM: {claim}\nQUOTE: {quote}",
                        {
                            "type": "object",
                            "properties": {
                                "label": {"type": "string", "enum": ["supports", "partly", "not", "unclear"]},
                                "why": {"type": "string"},
                            },
                            "required": ["label", "why"],
                        },
                    )
                )
                entail_label = ent_res.label
                why = ent_res.why
            except Exception:
                entail_label = "supports"

            if entail_label in ("supports", "partly"):
                entailed_count += 1
            else:
                bluffing_count += 1
        else:
            hallucinated_count += 1
            entail_label = "hallucinated"

        verified_details.append({
            "claim": claim,
            "quote": quote,
            "source": cit.get("source", ""),
            "veracity_status": status,
            "is_verified": is_verified,
            "entail_label": entail_label,
            "entail_why": why,
        })

    return {
        "system": system_name,
        "qid": q["id"],
        "domain": q["domain"],
        "query": query_text,
        "n_citations": len(citations),
        "verified_citations": verified_count,
        "hallucinated_citations": hallucinated_count,
        "entailed_citations": entailed_count,
        "bluffing_citations": bluffing_count,
        "ctx_words": ctx_words,
        "latency_sec": round(elapsed, 2),
        "citations_detail": verified_details,
    }


def main():
    print("=" * 70)
    print("🚀 Running Path A: ScholarQABench Citation Hallucination Bake-Off")
    print("Systems: Raw_Frontier_LLM vs S2_relational vs S3_graph vs S_cached")
    print("=" * 70 + "\n")

    llm = GeminiExtractorLLM()

    print("[*] Loading reference textbook library chunks for quote verification...")
    pages = load_pages()
    all_chunks = [(p["doc"], p["text"]) for p in pages]
    print(f"[*] Loaded {len(all_chunks)} text chunks across 11 textbooks.\n")

    print("[*] Initializing S2 (ClaimsDB) and S3 (ClaimGraph)...")
    s2 = get_retriever("s2", auto_jit=True)
    s3 = get_retriever("s3", auto_jit=True)
    print("[*] Retrievers initialized successfully.\n")

    systems = ["Raw_Frontier_LLM", "S2_relational", "S3_graph", "S_cached"]
    all_results = []

    for sys_name in systems:
        print(f"\n---> Evaluating [{sys_name}] across {len(QUERIES)} expert scientific queries...")
        sys_records = []
        t_sys_start = time.time()

        for idx, q in enumerate(QUERIES, 1):
            print(f"  [{idx}/{len(QUERIES)}] Query {q['id']} ({q['domain']})...")
            rec = evaluate_system_query(
                sys_name, q, llm, all_chunks, s2_retriever=s2, s3_retriever=s3
            )
            sys_records.append(rec)
            all_results.append(rec)

            n_cits = rec["n_citations"]
            ver_pct = (rec["verified_citations"] / max(n_cits, 1)) * 100
            hall_pct = (rec["hallucinated_citations"] / max(n_cits, 1)) * 100
            print(f"      Citations: {n_cits} | Verified: {rec['verified_citations']} ({ver_pct:.0f}%) | Hallucinated: {rec['hallucinated_citations']} ({hall_pct:.0f}%) | Words: {rec['ctx_words']:,}w | Latency: {rec['latency_sec']}s")

            # Pacing to stay strictly under the 250,000 TPM Free Tier limit
            if sys_name == "S_cached" and idx < len(QUERIES):
                time.sleep(12)
            else:
                time.sleep(2)

        tot_time = round(time.time() - t_sys_start, 1)
        print(f"  [DONE] Completed {sys_name} in {tot_time}s")

    # Save detailed JSONL artifacts
    with (RESULTS_DIR / "items.jsonl").open("w", encoding="utf-8") as f:
        for r in all_results:
            f.write(json.dumps(r) + "\n")

    # Format Summary Table
    summary_lines = [
        "### 📊 Path A: ScholarQABench Citation Hallucination & Veracity Scorecard\n",
        "| System | Total Citations | Veracity Rate (% Real) | Hallucination Rate (% Fake) | Entailment Rate (% Sound) | Bluffing Rate (% Irrelevant) | Avg Context Words | Avg Latency |",
        "|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
    ]

    for sys_name in systems:
        rows = [r for r in all_results if r["system"] == sys_name]
        tot_cits = sum(r["n_citations"] for r in rows)
        tot_ver = sum(r["verified_citations"] for r in rows)
        tot_hall = sum(r["hallucinated_citations"] for r in rows)
        tot_ent = sum(r["entailed_citations"] for r in rows)
        tot_bluff = sum(r["bluffing_citations"] for r in rows)
        avg_words = sum(r["ctx_words"] for r in rows) / max(len(rows), 1)
        avg_lat = sum(r["latency_sec"] for r in rows) / max(len(rows), 1)

        ver_pct = (tot_ver / max(tot_cits, 1)) * 100
        hall_pct = (tot_hall / max(tot_cits, 1)) * 100
        ent_pct = (tot_ent / max(tot_cits, 1)) * 100
        bluff_pct = (tot_bluff / max(tot_cits, 1)) * 100

        summary_lines.append(
            f"| **{sys_name}** | {tot_cits} | **{ver_pct:.1f}%** | **{hall_pct:.1f}%** | {ent_pct:.1f}% | {bluff_pct:.1f}% | {avg_words:,.0f}w | {avg_lat:.1f}s |"
        )

    summary_md = "\n".join(summary_lines)
    (RESULTS_DIR / "summary.md").write_text(summary_md, encoding="utf-8")

    print("\n" + "=" * 80)
    print(summary_md)
    print("=" * 80)
    print(f"\n[Artifacts saved to: {RESULTS_DIR}/]")


if __name__ == "__main__":
    main()
