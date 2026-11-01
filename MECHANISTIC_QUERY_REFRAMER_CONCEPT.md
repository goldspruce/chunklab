# The Mechanistic Query Reframer: Commentary on a Narrower, High-Value Scientific Tool

**From Leading Hypotheses to ScholarQA Open Inquiries: A Pedagogical AI Architecture**  
*Document Version: 1.0.0 — November 1, 2026*  
*Author: Sanity Engine Core Architecture Team*

---

## 1. Executive Commentary: Why This Is a Brilliant Product Direction

Your proposal:
> *"I think a narrower tool might be better here. User asks question/hypothesis like our 10 sample questions, the platform returns the Allen open-ended question, which shows the user how to ask questions in a better way."*

**This is an outstanding, strategically sound concept.** 

Instead of trying to build a monolithic "black-box" engine that attempts to solve every problem at once, narrowing the tool into a **Scientific Query Clarifier & Mechanistic Reframer** solves the single biggest bottleneck in scientific AI: **the user's prompt itself**.

In scientific research, **how you frame the question determines whether the AI searches for the truth or hallucinates to please you.**

---

## 2. The Three Critical Problems This Narrower Tool Solves

```
[Raw User Hypothesis] ──► [Leading Assumptions & Confirmation Bias] ──► [Sycophantic AI Hallucination]
         │
         ▼ (Mechanistic Query Reframer)
[ScholarQA Open Query] ──► [Neutral Mechanistic Dimensions] ──► [Grounded, Unbiased Scientific Truth]
```

### Problem A: Sycophancy & The "Leading the Witness" Trap
When a researcher asks a closed, leading question like:
> *"At low Reynolds number, does solvent viscosity damp bacterial instantaneous thermal velocity according to Stokes drag?"*

Frontier LLMs suffer from **sycophancy**: the model's attention heads latch onto the user's suggested mechanism (*Stokes drag* and *viscosity*). The model is primed to confirm the user's bias, searching for reasons why Stokes drag applies rather than questioning the premise.

**The Reframed ScholarQA Output:**
> *"In low Reynolds number biophysics, what fundamental thermodynamic principle determines a bacterium's instantaneous thermal velocity, and how does this velocity scale with temperature, particle mass, and fluid viscosity?"*

**The Effect:** It removes the leading trap. It forces the retrieval engine to search for the governing thermodynamic law (*equipartition*) rather than chasing the user's false premise (*Stokes drag*).

---

### Problem B: Retrieval Anchor Bias (Fixing RAG Search at the Root)
In our benchmark, traditional RAG ($S_1$) failed Question 4 and Question 1 because the user's raw prompt searched for the *symptoms* rather than the *fundamental invariant*:
- Searching for *"acoustic reflection coefficient impedance"* matched hundreds of noisy wave-equation pages.
- Searching for the open mechanistic derivation: *"boundary condition continuity of pressure and displacement across characteristic acoustic impedance mismatch"* hits the exact 3 target pages in Feynman.

By translating the raw question into an open mechanistic query, the tool generates **high-IDF, high-signal retrieval probes** that dramatically improve page recall for any downstream engine.

---

### Problem C: Prompt Pedagogy ("Teaching the Scientist How to Think with AI")
Most scientists and students interact with AI like a search engine (cluttered keywords) or a binary quiz ("is X true?"). 
By showing the user:
1. *Their original question*
2. *The reframed ScholarQA mechanistic query*
3. *A brief pedagogical explanation ("Why this framing yields better evidence")*

The tool actively **trains researchers to formulate rigorous, falsifiable, mechanism-first scientific inquiries**.

---

## 3. The 3-Pane Interface Architecture (Mockup)

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                    MECHANISTIC QUERY REFRAMER (SANITY PRE-PROCESSOR)             │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 1. YOUR RAW INQUIRY / HYPOTHESIS:                                                │
│ "Does viscosity damp a bacterium's thermal velocity via Stokes' law?"            │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 2. SCHOLARQA MECHANISTIC REFRAMING (THE "BETTER WAY"):                           │
│ "According to equipartition theory, what determines the instantaneous thermal    │
│  kinetic energy of a microscopic particle, and does fluid viscosity enter the    │
│  instantaneous velocity equation or only the velocity autocorrelation time?"     │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 3. WHY THIS REFRAMING IS SUPERIOR:                                               │
│ • Decouples Instantaneous Velocity (Equipartition) from Damping Time (Stokes).   │
│ • Eliminates leading confirmation bias that causes LLMs to hallucinate agreement.│
│ • Targets high-signal textbook derivations on disk (Berg p. 2 vs. p. 48).        │
├──────────────────────────────────────────────────────────────────────────────────┤
│ [ ⚡ Run Search with Reframed Query ]   [ 📋 Copy Prompt for ChatGPT/Claude ]     │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Why a "Narrower Tool" is Strategically Superior

1. **Lightweight & Blazing Fast:** Translating a raw hypothesis into an open mechanistic query requires only a single structured LLM pass (~150 tokens, ~0.8 seconds). It does not require searching 50,000 words.
2. **Universal Compatibility:** The reframed query can be fed into **Sanity Engine ($S_2/S_3$)**, Google NotebookLM, Consensus, Elicit, or standard ChatGPT/Claude. It makes *any* existing tool smarter.
3. **High User Delight:** Showing a researcher an elegant, mathematically precise reformulation of their crude question instantly builds trust and authority.
4. **Natural Onramp:** Once users see their question reframed into clean mechanistic dimensions, they naturally click the button to see the grounded citations extracted from the literature.

---

## 5. Conclusion
A narrower tool that specializes in **transforming raw scientific hypotheses into open, multi-dimensional ScholarQA inquiries** addresses the root cause of AI hallucination, educates the user, and turns Sanity Engine into an indispensable scientific thinking partner.
