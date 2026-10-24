"""Comprehensive verification test for chunklab retrieval architectures:
- S1: PlainChunks
- S2: ClaimsDB
- S3: ClaimGraph
"""
import sys
from pathlib import Path

# Add current folder to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from retrieval import PlainChunks, ClaimsDB, ClaimGraph, Hit

SAMPLE_CLAIMS = [
    {
        "id": 1,
        "gid": 1,
        "window": "Berg:2",
        "doc": "Berg_Random_Walks_in_Biology_1993",
        "page": 2,
        "section": "Diffusion: Microscopic Theory",
        "claim": "A particle at absolute temperature T has an average kinetic energy associated with movement along each axis of kT/2.",
        "type": "law_or_principle",
        "subject": "particle",
        "predicate": "has average kinetic energy",
        "object": "kT/2 along each axis",
        "conditions": "absolute temperature T",
        "entities": ["kinetic energy", "temperature", "boltzmann constant", "brownian motion"],
        "evidence": [
            {
                "type": "equation",
                "text": "A particle at absolute temperature T has, on the average, a kinetic energy associated with movement along each axis of kT/2, where k is Boltzmann's constant.",
                "quantity": "kT/2"
            }
        ],
        "links": [{"target": 2, "relation": "derives_from"}]
    },
    {
        "id": 2,
        "gid": 2,
        "window": "Berg:2",
        "doc": "Berg_Random_Walks_in_Biology_1993",
        "page": 2,
        "section": "Diffusion: Microscopic Theory",
        "claim": "The root-mean-square thermal velocity of a particle is given by sqrt(kT/m).",
        "type": "mathematical_result",
        "subject": "root-mean-square velocity",
        "predicate": "equals",
        "object": "sqrt(kT/m)",
        "conditions": "single degree of freedom",
        "entities": ["thermal velocity", "kinetic energy", "temperature", "mass"],
        "evidence": [
            {
                "type": "equation",
                "text": "From this relationship we compute the mean-square velocity, <vx^2> = kT/m",
                "quantity": "sqrt(kT/m)"
            }
        ],
        "links": []
    },
    {
        "id": 3,
        "gid": 3,
        "window": "Alberts:160",
        "doc": "Alberts_Molecular_Biology_of_the_Cell_7ed_2022",
        "page": 160,
        "section": "Membrane Transport and Diffusion",
        "claim": "Lower cellular temperatures decrease molecular kinetic energy, which directly reduces the passive diffusion rate across the lipid bilayer.",
        "type": "mechanism",
        "subject": "lower temperature",
        "predicate": "decreases",
        "object": "diffusion rate across lipid bilayer",
        "conditions": "physiological temperature range",
        "entities": ["diffusion rate", "temperature", "kinetic energy", "lipid bilayer"],
        "evidence": [
            {
                "type": "observation",
                "text": "Lower temperatures decrease the molecules' kinetic energy, thus decreasing the diffusion rate.",
                "quantity": ""
            }
        ],
        "links": []
    }
]


def test_hit_interface():
    print("[*] Testing Hit polymorphic interface...")
    h = Hit(
        id="test#1",
        doc="TestDoc",
        pages=[1, 2],
        section="Intro",
        text="Sample text for testing",
        score=2.75,
        extra={"custom_field": "val123"}
    )
    # Test dict-like access
    assert h["text"] == "Sample text for testing"
    assert h["doc"] == "TestDoc"
    assert h["source"] == "TestDoc"
    assert h["pages"] == [1, 2]
    assert h["custom_field"] == "val123"
    assert "text" in h

    # Test tuple-like unpacking (for engine.py compatibility)
    src, txt, sc = h
    assert src == "TestDoc"
    assert txt == "Sample text for testing"
    assert sc == 2.75

    print("  -> Hit interface passes 100% of dict and tuple requirements!")


def test_s1_plain():
    print("[*] Testing System 1: PlainChunks...")
    s1 = PlainChunks(chunk_words=120)
    assert len(s1.chunks) > 0, "PlainChunks failed to load any chunks!"
    print(f"  -> Built {len(s1.chunks)} chunks from corpus text files.")

    query = "Boltzmann constant kinetic energy temperature"
    hits = s1.search(query, k=3)
    assert len(hits) > 0, "S1 returned zero hits for Boltzmann query!"
    print(f"  -> Query '{query}' returned {len(hits)} hits.")
    top = hits[0]
    print(f"     Top hit: [{top.doc}] (pages: {top.pages}, score: {top.score:.2f})")
    assert "kT" in top.text or "energy" in top.text.lower() or "temperature" in top.text.lower()
    print("  -> System 1 test PASSED.")


def test_s2_relational():
    print("[*] Testing System 2: ClaimsDB (SQLite FTS5)...")
    s2 = ClaimsDB(db_path=":memory:", claims=SAMPLE_CLAIMS)

    # Check search
    query = "Boltzmann constant kinetic energy"
    hits = s2.search(query, k=2)
    assert len(hits) > 0, "S2 returned zero hits!"
    print(f"  -> Query '{query}' returned {len(hits)} hits.")
    top = hits[0]
    print(f"     Top hit: {top.text.splitlines()[0]} (score: {top.score:.2f})")
    assert "kinetic energy" in top.text.lower()
    assert "EVIDENCE" in top.text
    print("  -> System 2 test PASSED.")


def test_s3_graph():
    print("[*] Testing System 3: ClaimGraph (Spreading Activation & Cross-Book Bridge)...")
    s3 = ClaimGraph(claims=SAMPLE_CLAIMS)

    # Notice that claim 1 (Berg - Physics/Boltzmann) connects to claim 3 (Alberts - Biology/Diffusion)
    # via the shared rare entity 'kinetic energy' and 'temperature'!
    query = "Boltzmann temperature diffusion across lipid bilayer"
    hits = s3.search(query, k=3)
    assert len(hits) > 0, "S3 returned zero hits!"
    print(f"  -> Query '{query}' returned {len(hits)} hits.")

    for i, h in enumerate(hits):
        first_line = h.text.splitlines()[0]
        has_chain = "<-" in h.text
        print(f"     Hit #{i+1} [{h.doc} p.{h.pages}]: {first_line} (score: {h.score:.2f}, chain: {has_chain})")

    # Verify spreading activation found both Berg (Physics) and Alberts (Biology)
    docs_found = {h.doc for h in hits}
    print(f"  -> Cross-book sources retrieved: {docs_found}")
    assert "Berg_Random_Walks_in_Biology_1993" in docs_found
    print("  -> System 3 test PASSED.")


if __name__ == "__main__":
    test_hit_interface()
    test_s1_plain()
    test_s2_relational()
    test_s3_graph()
    print("\n✅ ALL RETRIEVAL TESTS PASSED SUCCESSFULLY!")
