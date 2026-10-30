# Guide to the Benchmark Metrics Table

**Sanity Engine & Chunklab Scientific Evaluation Suite**  
*Reference Guide for Evaluating Scientific Retrieval & Context Architectures*

---

## The Benchmark Summary Table

```
| System | Slice | N | Page Recall | MRR | Evidence Coverage | Verdict Acc | Insufficient | Avg Context Words |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
```

This table evaluates how effectively an AI system retrieves scientific proof from canonical textbooks to adjudicate complex hypotheses, comparing retrieval-augmented approaches against raw controls and full-context caching.

---

## 1. `System` (Retrieval & Context Architecture)

Defines the mechanism used to search, package, and provide textbook evidence to the evaluating model:

* **$S_0$ (None — Negative Control):**  
  Passes **zero notes** ($0\text{ words}$) to the reader. Tests whether an LLM can cheat by using pre-training memory. A score of $0\%$ accuracy and $100\%$ insufficient confirms the benchmark questions cannot be guessed without external evidence.
* **$S_1$ (Plain Chunks BM25):**  
  The standard industry RAG baseline. Slices textbooks into sliding windows of ~180 words and retrieves raw, unmodified narrative paragraphs using classical BM25 keyword matching.
* **$S_2$ (Relational Claims DB):**  
  Deconstructs textbooks into atomic scientific claims, Subject-Predicate-Object triples, and character-offset verbatim quotes stored in SQLite FTS5 with entity boosting.
* **$S_3$ (Claim Graph):**  
  Models claims as nodes in an in-memory knowledge graph. Traverses causal relations (`supports`, `contradicts`, `derives_from`) and rare entity bridges using spreading activation.
* **$S_{\text{cached}}$ (Gemini Long Context):**  
  The brute-force context caching baseline. Eliminates chunking and passes full textbooks or broad 150-page sections (15,000 to 120,000 words) directly into the model's active context window.

---

## 2. `Slice` (Question Complexity Tier)

Categorizes the benchmark questions by reasoning depth:

* **`single_hop` (8 questions):**  
  The answer and proof reside on a single page in one specific textbook (e.g., Berg p. 2 on bacterial drift vs. diffusion).
* **`multi_hop` (2 questions):**  
  Harder questions requiring the synthesis of two distinct disciplines across different books (e.g., connecting Feynman's acoustic wave impedance equation to Alberts's cell membrane impedance values).
* **`all` (10 questions):**  
  The aggregate average across all benchmark items.

---

## 3. `N` (Sample Size)

The number of test items evaluated in that slice:
* $N = 10$ for `all`
* $N = 8$ for `single_hop`
* $N = 2$ for `multi_hop`

---

## 4. `Page Recall` (Did We Find the Target Page?)

* **Range:** $0.00$ to $1.00$ ($0\%$ to $100\%$) | **Higher is better**
* **Mathematical Definition:**
  $$\text{Page Recall} = \frac{|\text{Retrieved Pages} \cap \text{Gold Pages}|}{|\text{Gold Pages}|}$$
* **What it means in plain English:**  
  Did the search engine pull the actual textbook page where the ground truth is written?
* **Benchmark Results:**
  * **$S_2 = 0.62$ (single-hop):** Located the exact target page over $62\%$ of the time.
  * **$S_1 = 0.25$:** Missed the target page $75\%$ of the time because narrative textbook boilerplate diluted keyword matching.
  * **$S_{\text{cached}} = 0.20$:** Suffered from "page drift" across 50,000 words, frequently citing adjacent chapters (e.g., citing p. 44 instead of p. 78 in Johnston).

---

## 5. `MRR` (Mean Reciprocal Rank — How High on the List?)

* **Range:** $0.00$ to $1.00$ | **Higher is better**
* **Mathematical Definition:**
  $$\text{MRR} = \frac{1}{\text{Rank of First Correct Page}}$$
* **What it means in plain English:**  
  Was the correct page placed at the very top of the search results, or was it buried down the list?
  * If the right page is rank **#1** $\rightarrow \text{MRR} = 1.0$
  * If the right page is rank **#2** $\rightarrow \text{MRR} = 0.5$
  * If the right page is rank **#3** $\rightarrow \text{MRR} = 0.33$
  * If not found $\rightarrow \text{MRR} = 0.0$
* **Benchmark Results:**
  * **$S_2 = 0.55$ / $0.56$:** When $S_2$ finds the right page, it places it at or near rank #1 or #2.

---

## 6. `Evidence Coverage` (Did the Text Contain the Proof?)

* **Range:** $0.00$ to $1.00$ ($0\%$ to $100\%$) | **Higher is better**
* **What it measures:**  
  Evaluated by an independent, automated **Coverage Judge LLM**. The judge inspects the retrieved text and checks whether it contains the exact scientific proof from the gold quote:
  * **`full` ($1.0$):** The complete quantitative proof is present.
  * **`partial` ($0.5$):** The general concept is mentioned, but missing specific numbers or boundary conditions.
  * **`none` ($0.0$):** The proof is completely absent.
* **Why it matters:**  
  Page Recall only checks if you opened the right page number; Evidence Coverage verifies that you actually clipped the *smoking-gun sentence*.

---

## 7. `Verdict Acc` (Verdict Accuracy — Did the AI Get the Answer Right?)

* **Range:** $0.0\%$ to $100.0\%$ | **Higher is better**
* **What it measures:**  
  The percentage of questions where the **Blind Reader LLM** reached the correct scientific conclusion (`supported` vs. `refuted`).
* **Ground Rule:**  
  The Blind Reader receives *only* the retrieved context (with zero outside knowledge allowed).
* **Benchmark Results:**
  * **$S_2 = 70.0\%$:** Achieved the highest accuracy on the benchmark (and **$100.0\%$** on multi-hop questions).
  * **$S_1 = 70.0\%$:** Matched 70% accuracy, but overshot the context budget by nearly double.
  * **$S_{\text{cached}} = 60.0\%$:** Scored lower despite receiving entire textbook sections.
  * **$S_0 = 0.0\%$ (single-hop):** Proves the reader cannot guess without notes.

---

## 8. `Insufficient` (The Anti-Hallucination Guardrail)

* **Range:** $0.0\%$ to $100.0\%$
* **What it measures:**  
  How often the Blind Reader responded:  
  *"The provided text does not contain enough evidence to make a definitive ruling"* (`insufficient`).
* **Why it matters:**  
  In scientific verification, **admitting you don't know is vastly superior to hallucinating an answer**.
* **Benchmark Results:**
  * For $S_0$, this was **$100.0\%$** on single-hop items, proving zero hallucination.
  * For $S_{\text{cached}}$, this rose to **$40.0\%$** because the model got lost in 50,000+ words and failed to locate the proof.

---

## 9. `Avg Context Words` (Context Density & Cost)

* **What it measures:**  
  The average word count handed to the reader LLM per query.
* **Why it is the decisive efficiency metric:**  
  The target context budget was **400 words**.
  * **$S_2 = 357\text{ words}$:** Respected the budget while reaching 70% accuracy (and on multi-hop, achieved 100% accuracy in just **132 words**).
  * **$S_1 = 690\text{ words}$:** Overshot the budget by $72\%$ because narrative paragraphs cannot be cleanly divided.
  * **$S_{\text{cached}} = 49,664\text{ words}$:** Consumed **$139\times$ more context** per question, blowing up token costs and slowing down latency to over 100 seconds per query.
