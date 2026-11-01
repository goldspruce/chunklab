# Underlying Engines Explained in Simple Terms: Quote Snapping vs. Entailment

**Sanity Engine & ScholarQA Verification Methodology**  
*Document Version: 1.0.0 — November 1, 2026*  
*Author: Sanity Engine Core Architecture Team*

---

## The Technical Line in the Comparison Table

In the comparison table between Quote Snapping and Entailment, the row **"Underlying Engine"** states:

| Verification Gate | Technical Description of Underlying Engine |
| :--- | :--- |
| **Gate 1: Quote Snapping** | `Deterministic Python / RegEx, 6-word shingle hashing (≥ 50%)` |
| **Gate 2: Entailment** | `Adversarial NLI LLM Critic (T=0.0), Closed-World Prompt` |

Here is what every piece of that technical shorthand means, translated into plain English with simple real-world analogies.

---

## Part 1: Gate 1 Engine — Quote Snapping
`Deterministic Python / RegEx, 6-word shingle hashing (≥ 50%)`

### 1. Deterministic Python (Zero AI, Zero Hallucination Risk)
- **What it means**: This is regular, traditional computer programming code—like a calculator or a basic `Ctrl + F` search.
- **Why it matters**: It does **not** use an AI model, neural network, or predictive weights to find quotes. 
- **The benefit**: A regular Python script cannot "imagine" or hallucinate words. If you run it 10,000 times, it will give the exact same answer 10,000 times. It simply opens the textbook text files stored on the physical hard drive and inspects the characters.

### 2. RegEx (Regular Expressions / Text Cleanup Squeegee)
- **What it means**: "RegEx" is short for Regular Expressions—a standard tool used by programmers to find and transform text patterns.
- **The problem it solves**: Real textbooks scanned into computers have annoying visual and formatting quirks:
  - Hyphenated words split across line breaks (e.g., `ther-` at the end of line 12 and `mal` at the start of line 13).
  - Fancy curly quotes (`“ ”` or `‘ ’`) instead of plain quotes (`" '`).
  - Extra double spaces, tabs, or hidden formatting characters.
- **How it works**: RegEx acts like a digital squeegee before matching begins. It removes punctuation, converts `ther- \n mal` back into `thermal`, and normalizes all whitespace. This ensures a real quote isn't falsely marked as "fake" just because of an OCR line break.

### 3. 6-Word Shingle Hashing (Roof Shingle Overlap)
- **What is a "shingle"?** Think of asphalt shingles on a house roof: each shingle overlaps the one next to it so no water leaks through.
- **The problem with exact matching**: If an AI provides a 25-word quote from a textbook, but an OCR scanner accidentally read the letter `l` as the number `1` in one word, a naive 100% exact match will fail and claim the quote is fake.
- **How shingling works**:
  Instead of checking the whole 25-word sentence as one giant block, the algorithm chops the sentence into overlapping 6-word windows ("shingles"):
  - **Window 1**: Words 1, 2, 3, 4, 5, 6
  - **Window 2**: Words 2, 3, 4, 5, 6, 7
  - **Window 3**: Words 3, 4, 5, 6, 7, 8
  - ...and so on.

### 4. The "≥ 50%" Rule (Fuzzy Snapping)
- The algorithm searches the entire textbook on disk for these 6-word shingles.
- If **at least 50% of the shingles** match consecutively inside a single passage in the book, the algorithm concludes:
  *"This is unmistakably the exact passage the author wrote—it's just got minor OCR noise or a missing comma."*
- It then **"snaps"** the quote to its true, exact byte coordinates (`[start_character, end_character]`) in the physical textbook file.

---

## Part 2: Gate 2 Engine — Entailment
`Adversarial NLI LLM Critic (T=0.0), Closed-World Prompt`

### 1. Adversarial (A Harsh, Skeptical Grader)
- **What it means**: Most AI assistants are prompted to be helpful, polite, and agreeable. If a student's answer is close, a polite AI will give them the benefit of the doubt.
- **How an "Adversarial" critic differs**: This prompt explicitly instructs the AI judge to act like a harsh, skeptical peer-reviewer looking for any logical flaw or exaggeration. It is deliberately instructed **not** to be generous and to actively look for cases where the model is trying to bluff.

### 2. NLI (Natural Language Inference)
- **What it means**: NLI is the formal computer science term for pure deductive logic between sentences:
  $$\text{Premise (The Quote)} \implies \text{Hypothesis (The Claim)}$$
- **The test**: If the premise is true, does the hypothesis *logically have to be true*?
  - *Example A*:
    - **Quote**: *"The animal is an adult Golden Retriever."*
    - **Claim**: *"The animal is a dog."* $\implies$ **Supports (Entailed!)**
  - *Example B (Citation Bluffing)*:
    - **Quote**: *"The animal is an adult Golden Retriever."*
    - **Claim**: *"The animal is afraid of thunderstorms."* $\implies$ **Not Supported!** (Even if many dogs fear thunder, the quote itself does not say that!).

### 3. LLM Critic at Temperature Zero ($T = 0.0$)
- **What Temperature ($T$) means**: In Large Language Models, temperature controls creativity and randomness:
  - $T = 0.7$ or $1.0$: The model is creative, poetic, and will give slightly different answers every time you ask.
  - $T = 0.0$ (Zero Temperature): All randomness and creativity are completely turned off. The model strictly picks the single most probable, mathematically certain word at every step.
- **Why $T = 0.0$ is required**: A legal or scientific referee must never be creative. If you run the audit today, next week, or next year, it must return the exact same verdict.

### 4. Closed-World Prompt ("Do Not Use Outside Knowledge")
- **The problem**: Frontier LLMs have memorized vast amounts of physics and biology. If an AI referee uses its own background memory, it might see a student make a true scientific claim with a completely unrelated quote, and say:
  *"Well, the quote didn't prove it, but I learned in college that this claim is actually true, so I will pass it."*
  That defeats the entire point of checking citations!
- **How the Closed-World Prompt works**:
  The referee is put into a "sealed mental chamber" with the prompt:
  > *"You are given ONLY the claim and the quote. You are strictly forbidden from using any outside knowledge. If the words in the quote do not explicitly prove the claim on their own, you must answer 'not supported'."*
- This forces the system to catch **Citation Bluffing** every single time.

---

## Summary Cheat Sheet

| Technical Phrase | Plain English Meaning | Real-World Analogy |
| :--- | :--- | :--- |
| **Deterministic Python** | Non-AI code running on your CPU | A calculator or spreadsheet formula |
| **RegEx** | Automated cleanup of OCR line breaks and formatting | A squeegee cleaning dirt off a window |
| **6-Word Shingle (≥ 50%)** | Overlapping 6-word puzzle pieces matching the book | Fingerprint matching that handles smudges |
| **Adversarial Critic** | An AI prompted to be skeptical, not helpful | A strict DMV inspector or peer reviewer |
| **NLI (Inference)** | Strict deductive logic: Quote $\implies$ Claim | A courtroom lawyer proving an exact fact |
| **$T = 0.0$** | Zero randomness / zero creativity | A digital scale that always reads the same weight |
| **Closed-World Prompt** | Judge is blind to everything except the quote | A jury juror told to ignore rumors and look only at Exhibit A |
