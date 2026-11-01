# Why Gate 1 (Snapping) and Gate 2 (Entailment) Are Displayed Separately in the ScholarQA Scorecards

**Methodological Architecture & Forensic Decomposition**  
*Document Version: 1.0.0 — November 1, 2026*  
*Author: Sanity Engine Core Architecture Team*

---

## 1. Direct Answer: They ARE Both Part of the Allen Method

**You are 100% correct: Quote Snapping and Entailment are both integral stages of Method 2 (the Allen Institute ScholarQA methodology).**

Notice the exact labels in the first column of the scorecard table:
- **`Method 2 Gate 1 (Snapping)`**
- **`Method 2 Gate 2 (Entail)`**

They are not separate evaluation methods. Rather, the Allen Institute audit decomposes citation trustworthiness into a **sequential two-gate gauntlet**:

$$\text{Method 2 (ScholarQA Veracity)} = \underbrace{\text{Gate 1 (Quote Snapping)}}_{\text{Did the author write these words?}} \ \land \ \underbrace{\text{Gate 2 (Entailment)}}_{\text{Does this quote prove the claim?}}$$

---

## 2. Why Are They Displayed in Separate Rows / Columns?

If the table simply reported a single combined "Pass/Fail" metric for Method 2, it would conceal the most important scientific finding of the entire benchmark: **the difference between a Hallucinated Citation and a Citation Bluff.**

```
                     METHOD 2: THE ALLEN INSTITUTE FORENSIC AUDIT
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
     GATE 1: QUOTE SNAPPING                           GATE 2: ENTAILMENT
   (Physical Grounding on Disk)                      (Logical Deduction)
                  │                                               │
  Did the model synthesize a fake quote           Did the model paste a real quote
       from parametric memory?                   that is completely irrelevant?
                  │                                               │
         FAILURE DETECTED:                               FAILURE DETECTED:
    ❌ "Citation Hallucination"                      ❌ "Citation Bluffing"
  (e.g., S0 unassisted on Q2 & Q3)             (e.g., S_cached on Q3 Page 848)
```

---

## 3. The Two Completely Different Failure Modes Caught

By splitting Gate 1 and Gate 2 in the table, you can immediately identify **which disease** an AI platform suffers from:

### Failure Mode A: The "Hallucinator" ($S_0$ Unassisted Frontier Model)
- **Gate 1 (Snapping)**: **❌ FAIL (0/2 Real)**
- **Gate 2 (Entail)**: **❌ FAIL (0% Sound)**
- *What happened*: The model operated from memory. It invented a quote that looked authoritative but never existed in the book. It failed at Gate 1, so Gate 2 was impossible.

### Failure Mode B: The "Bluffer" ($S_{\text{cached}}$ Gemini Long-Context on Question 3)
- **Gate 1 (Snapping)**: **✅ PASS (2/2 Real)**
- **Gate 2 (Entail)**: **❌ FAIL (Citation Bluffing)**
- *What happened*: The model had 50,000 words in context. It successfully copied a real 30-word sentence from Page 848 defining sound velocity ($c = \sqrt{1 / \rho \beta_S}$).
- **Gate 1 passed 100%** because the quote physically exists in the book.
- But the model attached that sound speed equation to a claim about *acoustic boundary impedance reflection*.
- **Gate 2 caught the bluff red-handed.** The referee rejected it because sound speed does not prove boundary reflection coefficients.

If Gate 1 and Gate 2 were merged into a single generic "Method 2" score, you would never know that $S_{\text{cached}}$ committed academic citation fraud with genuine textbook text!

---

## 4. Summary Table

| Metric in Method 2 | Question Answered | What a "FAIL" Means | Real Benchmark Example |
| :--- | :--- | :--- | :--- |
| **Gate 1: Quote Snapping** | *"Are these words physically on disk?"* | **The quote is synthetic / fabricated.** | $S_0$ fabricating quotes from Berg & Feynman |
| **Gate 2: Entailment** | *"Does the quote logically prove the claim?"* | **The quote is real, but it's a citation bluff.** | $S_{\text{cached}}$ citing sound speed for boundary reflection |
| **Combined Method 2** | *"Is the claim verifiably true & grounded?"* | **The claim cannot be trusted.** | Requires passing BOTH Gate 1 and Gate 2 |
