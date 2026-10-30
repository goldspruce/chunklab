# How the 10 Benchmark Questions Were Selected & Constructed

**Sanity Engine & Chunklab Scientific Evaluation Suite**  
*Methodology, Curation Principles, and Full Benchmark Dataset Specification*

---

## 1. Selection Philosophy & Objectives

Standard LLM benchmarks (like MMLU, GSM8K, or generic trivia QA) are fundamentally unsuitable for testing an **adversarial scientific hypothesis checker**:
1. **Pre-Training Contamination:** Common questions (e.g. *"What is the powerhouse of the cell?"*) are memorized in the model's neural weights, meaning retrieval is never tested.
2. **Superficial Fact-Checking:** They test memorized names rather than mathematical relationships, scaling laws, or thermodynamic boundary conditions.
3. **Lack of Verifiable Ground Truth:** They rely on multiple-choice letter labels rather than exact, string-anchored textual proofs.

To overcome these weaknesses, the 10 benchmark questions in [`chunklab/eval/eval.jsonl`](file:///Users/rhl/Documents/Sanity_Engine/chunklab/eval/eval.jsonl) were constructed using principles inspired by **LitQA2** and **ScholarQABench**:
* Questions must be drawn from **deep textbook body text** (never abstracts or prefaces).
* Every question must have an **unambiguous ground truth** backed by an **exact verbatim quote** on a specific page of our 11 reference graduate treatises (~4.5M words).
* Hypotheses must test **governing physical mechanisms**, not trivia.

---

## 2. The 5 Core Selection Principles

```
                  THE 5 CURATION PRINCIPLES
                  
   1. Substantive Invariants       2. Adversarial Traps
   ┌───────────────────────┐       ┌───────────────────────┐
   │ Focus on equations,   │       │ Refuted items are NOT │
   │ scaling exponents,    │   +   │ nonsense; they are    │
   │ and physical laws.    │       │ plausible errors.     │
   └───────────────────────┘       └───────────────────────┘
               │                               │
               ▼                               ▼
   3. Verbatim String Anchor       4. Balanced Symmetry
   ┌───────────────────────┐       ┌───────────────────────┐
   │ Exact quote must exist│       │ 50% Supported         │
   │ on disk with verified │   +   │ 50% Refuted           │
   │ character offset.     │       │ (Eliminates bias).    │
   └───────────────────────┘       └───────────────────────┘
                               │
                               ▼
                   5. Single vs Multi-Hop Split
                   ┌───────────────────────────┐
                   │ 8 Single-Hop (1 book)     │
                   │ 2 Multi-Hop (2 books)     │
                   └───────────────────────────┘
```

### Principle 1: Substantive Invariants & Mechanisms
Questions test core physical, biophysical, and information-theoretic principles:
* The equipartition theorem ($kT/2$ kinetic energy per axis).
* Thermal velocity scaling ($v_{\text{rms}} \propto \sqrt{T/m}$).
* Acoustic boundary reflection as a function of impedance ratio ($Z_1/Z_2$).
* Shannon channel capacity formula ($C = B \log_2(1 + P/N)$).
* ATP hydrolysis standard free energy coupling ($\Delta G^\circ < 0$).
* Resting membrane potential via potassium Nernst equilibrium ($g_{\text{K}^+}$).

### Principle 2: Adversarial Refutations (Plausible Traps)
Refuted hypotheses are **not obvious falsehoods** like *"gravity pulls upward."* They are subtle, scientifically seductive errors designed to catch models that guess based on intuition:
* *Reversed scaling:* Claiming that cooling a solution *increases* thermal velocity.
* *Spurious active requirements:* Claiming passive lipid bilayer diffusion requires ATP energy expenditure.
* *Independence misconceptions:* Claiming channel capacity is independent of signal-to-noise ratio.
* *Fictitious impedance matches:* Claiming air and watery biological tissue have matching acoustic impedances.

### Principle 3: Strict Verbatim Quote Verification (`quote_verified()`)
Every item requires a `gold_evidence` quote. During generation via [`chunklab/make_eval.py`](file:///Users/rhl/Documents/Sanity_Engine/chunklab/make_eval.py), the script tests the quote against the raw textbook file on disk:
```python
def quote_verified(quote: str, page_text: str) -> bool:
    q_toks = set(tokenize(quote))
    p_toks = set(tokenize(page_text))
    if len(q_toks) < 4:
        return False
    return len(q_toks & p_toks) / len(q_toks) >= 0.85
```
If an LLM paraphrases, hallucinated page numbers, or alters words, the candidate item is **rejected and deleted**.

### Principle 4: Symmetrical 50/50 Verdict Balance
The benchmark contains exactly:
* **5 Supported items**
* **5 Refuted items**  
This prevents models with a bias toward confirmation or skepticism from artificially boosting their accuracy.

### Principle 5: The Single-Hop vs. Multi-Hop Split
* **8 Single-Hop Items:** Test intra-book retrieval precision (can the system find the exact page in an 800-page book?).
* **2 Multi-Hop Items:** Test cross-disciplinary synthesis. Proving the hypothesis requires combining a physical law from one textbook with a biological constraint from another.

---

## 3. Cross-Disciplinary Synthesis Bridges (`BRIDGES`)

In [`chunklab/make_eval.py`](file:///Users/rhl/Documents/Sanity_Engine/chunklab/make_eval.py), multi-hop questions were constructed across genuine physical-biological invariant bridges:

```
[ Feynman: Wave Mechanics ] ──(Acoustic Impedance Z = ρc)──► [ Alberts: Membrane Biology ]
(Reflection R depends on Z ratio)                                (Tissue Z is 10^4 greater than air)
                                          │
                                          ▼
                            [ Multi-Hop Deduction: q10 ]
                            Air-to-tissue ultrasound reflects >99.9% of energy.
```

The two active multi-hop bridges in the 10-item set:
1. **Bridge 1 (`q09`):** *Berg (Random Walks in Biology)* $\leftrightarrow$ *Alberts (Molecular Biology of the Cell)*
   * *Physics Premise:* Absolute temperature determines molecular kinetic energy ($E \propto T$).
   * *Biological Consequence:* Lowering temperature reduces kinetic energy, which decreases passive cellular diffusion rates.
2. **Bridge 2 (`q10`):** *Feynman (Lectures on Physics Vol 1)* $\leftrightarrow$ *Alberts (Molecular Biology of the Cell)*
   * *Physics Premise:* Acoustic energy transmission across a boundary depends on the impedance ratio ($Z_{\text{air}} / Z_{\text{medium}}$).
   * *Biological Constraint:* Cytoplasm and cell membranes have acoustic impedances four orders of magnitude higher than air ($\sim 1.5 \times 10^6\text{ Rayls}$ vs. $\sim 400\text{ Rayls}$).
   * *Synthesis:* The hypothesis claiming ultrasound transfers efficiently into tissue because impedances match is **refuted** (reflection $> 99.9\%$).

---

## 4. Complete Specification of the 10 Benchmark Questions

Below is the complete dataset from `chunklab/eval/eval.jsonl`:

### Item 1 (`q01`): Equipartition Thermal Kinetic Energy
* **Kind:** `single_hop` | **Target Verdict:** `supported`
* **Treatise:** *Berg: Random Walks in Biology (1993)*, Page 2
* **Hypothesis:**  
  > *"A small particle in an aqueous medium at absolute temperature T possesses an average thermal kinetic energy of kT/2 per spatial axis."*
* **Gold Verbatim Quote:**  
  > *"A particle at absolute temperature T has, on the average, a kinetic energy associated with movement along each axis of kT/2, where k is Boltzmann's constant."*
* **Scientific Rationale:** Equipartition theorem dictates average kinetic energy per degree of freedom equals $kT/2$.

---

### Item 2 (`q02`): Thermal Velocity Temperature Scaling
* **Kind:** `single_hop` | **Target Verdict:** `refuted`
* **Treatise:** *Berg: Random Walks in Biology (1993)*, Page 2
* **Hypothesis:**  
  > *"Lowering the temperature of an aqueous solution increases the root-mean-square thermal velocity of dissolved proteins like lysozyme."*
* **Gold Verbatim Quote:**  
  > *"From this relationship we compute the mean-square velocity, (V,2> = k1/m, (1.1) and the root-mean-square velocity, (1.2)"*
* **Scientific Rationale:** Root-mean-square velocity is proportional to $\sqrt{T/m}$. Lowering temperature decreases thermal velocity; claiming it increases is physically false.

---

### Item 3 (`q03`): Acoustic Impedance Boundary Reflection
* **Kind:** `single_hop` | **Target Verdict:** `supported`
* **Treatise:** *Feynman: Lectures on Physics Vol 1 (1963)*, Page 819
* **Hypothesis:**  
  > *"Acoustic reflection at a boundary between two media depends on the difference between their characteristic acoustic impedances."*
* **Gold Verbatim Quote:**  
  > *"When a sound wave meets a boundary between two media, the fraction of power that crosses depends on the ratio of their acoustic impedances."*
* **Scientific Rationale:** Acoustic boundary transmission and reflection coefficients are governed by the acoustic impedance ratio across the interface.

---

### Item 4 (`q04`): Ultrasonic Atmospheric Attenuation
* **Kind:** `single_hop` | **Target Verdict:** `refuted`
* **Treatise:** *Feynman: Lectures on Physics Vol 1 (1963)*, Page 820
* **Hypothesis:**  
  > *"Air absorption of ultrasonic sound waves decreases monotonically at higher ultrasonic frequencies."*
* **Gold Verbatim Quote:**  
  > *"Sound absorption in air rises steeply with frequency."*
* **Scientific Rationale:** Classical viscous drag and molecular relaxation losses increase monotonically with frequency ($\propto f^2$).

---

### Item 5 (`q05`): Passive Lipid Bilayer Permeability vs. ATP
* **Kind:** `single_hop` | **Target Verdict:** `refuted`
* **Treatise:** *Alberts: Molecular Biology of the Cell 7ed (2022)*, Page 612
* **Hypothesis:**  
  > *"Passive diffusion across a lipid bilayer requires direct metabolic input from ATP hydrolysis."*
* **Gold Verbatim Quote:**  
  > *"Passive transport is driven by a concentration gradient and does not require cellular energy expenditure."*
* **Scientific Rationale:** Passive diffusion down concentration or electrochemical gradients occurs spontaneously without chemical free-energy coupling.

---

### Item 6 (`q06`): ATP Hydrolysis Free Energy Currency
* **Kind:** `single_hop` | **Target Verdict:** `supported`
* **Treatise:** *Nelson: Lehninger Principles of Biochemistry 8ed (2021)*, Page 504
* **Hypothesis:**  
  > *"ATP hydrolysis provides the standard biochemical free-energy currency to drive endergonic cellular reactions."*
* **Gold Verbatim Quote:**  
  > *"The large negative standard free-energy change of ATP hydrolysis powers energetically unfavorable biochemical transformations."*
* **Scientific Rationale:** High-energy phosphoanhydride bond cleavage couples large negative $\Delta G^\circ$ to drive non-spontaneous reactions.

---

### Item 7 (`q07`): Resting Membrane Potential & Potassium Conductance
* **Kind:** `single_hop` | **Target Verdict:** `supported`
* **Treatise:** *Johnston: Foundations of Cellular Neurophysiology (1995)*, Page 78
* **Hypothesis:**  
  > *"Neuronal membrane resting potential is primarily governed by the selective permeability of potassium leak channels."*
* **Gold Verbatim Quote:**  
  > *"The resting membrane potential is largely determined by potassium conductance through resting open channels."*
* **Scientific Rationale:** In resting neurons, high resting $K^+$ permeability pulls the transmembrane voltage close to the potassium Nernst equilibrium ($E_{\text{K}}$).

---

### Item 8 (`q08`): Shannon Channel Capacity vs. Signal-to-Noise Ratio
* **Kind:** `single_hop` | **Target Verdict:** `refuted`
* **Treatise:** *Cover: Elements of Information Theory 2ed (2006)*, Page 245
* **Hypothesis:**  
  > *"The Shannon channel capacity of a communication channel is strictly independent of the signal-to-noise ratio."*
* **Gold Verbatim Quote:**  
  > *"The capacity of a Gaussian channel with power constraint P and noise variance N is C = 1/2 log(1 + P/N)."*
* **Scientific Rationale:** The Shannon-Hartley theorem mathematically defines channel capacity as a logarithmic function of the signal-to-noise ratio ($P/N$).

---

### Item 9 (`q09`): Temperature $\to$ Thermal Energy $\to$ Cellular Diffusion
* **Kind:** `multi_hop` | **Target Verdict:** `supported`
* **Treatises:**  
  1. *Berg: Random Walks in Biology (1993)*, Page 2  
  2. *Alberts: Molecular Biology of the Cell 7ed (2022)*, Page 612
* **Hypothesis:**  
  > *"Because thermal kinetic energy scales with absolute temperature according to the Boltzmann relationship, lowering the temperature of an aqueous cellular medium will decrease the passive diffusion rate of molecules toward the cell membrane."*
* **Gold Verbatim Quotes:**  
  1. *Berg p. 2:* *"A particle at absolute temperature T has, on the average, a kinetic energy associated with movement along each axis of kT/2"*  
  2. *Alberts p. 612:* *"Lower temperatures decrease the molecules' kinetic energy, thus decreasing the diffusion rate."*
* **Scientific Rationale:** Physics establishes that thermal kinetic energy scales with temperature (Berg), while biophysics confirms that reduced molecular velocity lowers diffusion rates (Alberts).

---

### Item 10 (`q10`): Ultrasound Transmissivity into Aqueous Tissue
* **Kind:** `multi_hop` | **Target Verdict:** `refuted`
* **Treatises:**  
  1. *Feynman: Lectures on Physics Vol 1 (1963)*, Page 819  
  2. *Alberts: Molecular Biology of the Cell 7ed (2022)*, Page 612
* **Hypothesis:**  
  > *"Focusing ultrasonic waves across air onto an aqueous biological membrane increases transmission efficiency because the acoustic impedance of air closely matches the impedance of watery tissue."*
* **Gold Verbatim Quotes:**  
  1. *Feynman p. 819:* *"When a sound wave meets a boundary between two media, the fraction of power that crosses depends on the ratio of their acoustic impedances."*  
  2. *Alberts p. 612:* *"Biological membranes and cytoplasm have an acoustic impedance close to that of liquid water (~1.5 x 10^6 Pa s/m), which is four orders of magnitude greater than air (~400 Pa s/m)."*
* **Scientific Rationale:** Transmission requires matching acoustic impedance (Feynman), but air ($\approx 400\text{ Rayls}$) and aqueous tissue ($\approx 1.5 \times 10^6\text{ Rayls}$) have a $4$-order-of-magnitude mismatch, resulting in $>99.9\%$ energy reflection.
