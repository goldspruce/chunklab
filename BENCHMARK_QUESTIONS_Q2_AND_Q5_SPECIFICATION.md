# 📘 Benchmark Specification: Textbook Questions 2 and 5
### *The Exact Question Formulations, Ground-Truth Physics/Biology, and Literature Receipts*

> **Document Type**: Benchmark Ground-Truth Specification  
> **Covered Items**: Textbook Question 2 (`q02` / `SQA_02`) & Textbook Question 5 (`q05` / `SQA_05`)  
> **Evaluated Formats**:  
> 1. **Method 1: Closed Epistemic Hypothesis (3-Way Decision: Supported / Refuted / Insufficient)**  
> 2. **Method 2: Open Mechanistic Research Query (Attribution Audit with Verbatim Quotes)**  
> **Canonical Corpora**:  
> - Howard C. Berg, *Random Walks in Biology* (Princeton University Press, 1993)  
> - Bruce Alberts et al., *Molecular Biology of the Cell*, 7th ed. (W. W. Norton & Co., 2022)  
> **Date**: November 2026

---

## 1. Textbook Question 2: Thermal Velocity & Equipartition

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 QUESTION 2 COMPLETE BENCHMARK SPECIFICATION                            │
├───────────────────────┬────────────────────────────────────────────────────────────────────────────────┤
│ Question ID (Method 1)│ q02                                                                            │
├───────────────────────┼────────────────────────────────────────────────────────────────────────────────┤
│ Question ID (Method 2)│ SQA_02                                                                         │
├───────────────────────┼────────────────────────────────────────────────────────────────────────────────┤
│ Scientific Domain     │ Statistical Biophysics / Molecular Dynamics                                    │
├───────────────────────┼────────────────────────────────────────────────────────────────────────────────┤
│ Canonical Source      │ Howard C. Berg, Random Walks in Biology (1993), Chapter 1, Page 2              │
├───────────────────────┼────────────────────────────────────────────────────────────────────────────────┤
│ Exact Hypothesis      │ "Lowering the temperature of an aqueous solution increases the                │
│ (Method 1)            │  root-mean-square thermal velocity of dissolved proteins like lysozyme."       │
├───────────────────────┼────────────────────────────────────────────────────────────────────────────────┤
│ Gold Verdict          │ REFUTED                                                                        │
├───────────────────────┼────────────────────────────────────────────────────────────────────────────────┤
│ Open Research Query   │ "According to equipartition theory, what is the thermal kinetic energy per     │
│ (Method 2)            │  spatial degree of freedom for microscopic particles in aqueous suspension,    │
│                       │  and how does thermal velocity scale with temperature?"                        │
└───────────────────────┴────────────────────────────────────────────────────────────────────────────────┘
```

### The Underlying Physics & Mathematical Derivation
By the classical **Equipartition Theorem**, a microscopic particle suspended in a fluid at absolute temperature $T$ possesses an average kinetic energy of $\frac{1}{2}kT$ associated with translational movement along each spatial coordinate axis ($x, y, z$):

$$\frac{1}{2} m \langle v_x^2 \rangle = \frac{1}{2} k T$$

Where:
* $m$ is the mass of the particle (e.g., a lysozyme molecule of molecular weight $1.4 \times 10^4\text{ g/mol}$).
* $k$ is the Boltzmann constant ($1.38 \times 10^{-16}\text{ erg/K}$).
* $T$ is the absolute thermodynamic temperature in Kelvin.

Solving for the one-dimensional mean-square velocity:
$$\langle v_x^2 \rangle = \frac{k T}{m}$$

And for total root-mean-square velocity in 3 dimensions ($\langle v^2 \rangle = \langle v_x^2 \rangle + \langle v_y^2 \rangle + \langle v_z^2 \rangle = \frac{3kT}{m}$):
$$v_{\text{rms}} = \sqrt{\frac{3 k T}{m}} \propto \sqrt{T}$$

**Physical Conclusion**: Because root-mean-square thermal velocity is directly proportional to the square root of absolute temperature ($\sqrt{T}$), **lowering the temperature strictly decreases thermal velocity**. The hypothesis asserting that lowering temperature increases thermal velocity is unequivocally **REFUTED**.

### Verbatim Literature Evidence on Disk (`Berg_Random_Walks_in_Biology_1993.txt`, Page 2)
```text
"A particle at absolute temperature T has, on the average, a kinetic energy 
associated with movement along each axis of kT/2, where k is Boltzmann's constant. 
From this relationship we compute the mean-square velocity, (V,2> = k1/m, 
where m is the particle mass... We can use Eq. 1.2 to estimate the instantaneous 
velocity of a small particle, for example, a molecule of the protein lysozyme."
```
* **Exact Disk Coordinates**: Character offsets `[1204, 1360]` and `[1361, 1430]`.
* **OCR Artifact**: Note the historical scan artifact where the printer's $\langle v_x^2 \rangle = kT/m$ was digitized as `(V,2> = k1/m,`.

---

## 2. Textbook Question 5: Membrane Transport & ATP Hydrolysis

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 QUESTION 5 COMPLETE BENCHMARK SPECIFICATION                            │
├───────────────────────┬────────────────────────────────────────────────────────────────────────────────┤
│ Question ID (Method 1)│ q05                                                                            │
├───────────────────────┼────────────────────────────────────────────────────────────────────────────────┤
│ Question ID (Method 2)│ SQA_05_Bio                                                                     │
├───────────────────────┼────────────────────────────────────────────────────────────────────────────────┤
│ Scientific Domain     │ Cell Biology / Membrane Biophysics & Bioenergetics                             │
├───────────────────────┼────────────────────────────────────────────────────────────────────────────────┤
│ Canonical Source      │ Bruce Alberts et al., Molecular Biology of the Cell (7th ed., 2022),           │
│                       │ Chapter 11 (Membrane Transport of Small Molecules), Section 11-1, Pages 678-679 │
├───────────────────────┼────────────────────────────────────────────────────────────────────────────────┤
│ Exact Hypothesis      │ "Passive diffusion across a lipid bilayer requires direct metabolic input      │
│ (Method 1)            │  from ATP hydrolysis."                                                         │
├───────────────────────┼────────────────────────────────────────────────────────────────────────────────┤
│ Gold Verdict          │ REFUTED                                                                        │
├───────────────────────┼────────────────────────────────────────────────────────────────────────────────┤
│ Open Research Query   │ "How does the thermodynamic driving force for passive diffusion across a       │
│ (Method 2)            │  biological lipid bilayer differ from active transport, and does passive       │
│                       │  permeation require direct coupling to metabolic ATP hydrolysis?"              │
└───────────────────────┴────────────────────────────────────────────────────────────────────────────────┘
```

### The Underlying Biological & Thermodynamic Principles
Cellular membrane transport is partitioned into two fundamental thermodynamic classes:

1. **Passive Transport (Simple & Facilitated Diffusion)**:
   * **Thermodynamic Driving Force**: Solutes move down their concentration gradient (or electrochemical gradient for charged ions).
   * **Free Energy**: $\Delta G < 0$ (exergonic and thermodynamically spontaneous).
   * **Metabolic Input**: **Zero metabolic energy input required**. Passive transport relies solely on the thermal kinetic energy of the solute molecules.
2. **Active Transport**:
   * **Thermodynamic Driving Force**: Solutes are pumped "uphill" against their electrochemical gradient ($\Delta G > 0$).
   * **Coupling**: Must be strictly coupled to an exergonic energy source, primarily **ATP hydrolysis** ($ATP + H_2O \to ADP + P_i$, $\Delta G^\circ = -30.5\text{ kJ/mol}$).

**Biological Conclusion**: Because passive diffusion across a lipid bilayer occurs spontaneously down a gradient without consuming cellular energy, the hypothesis asserting that it requires direct metabolic input from ATP hydrolysis is unequivocally **REFUTED**.

### Verbatim Literature Evidence on Disk (`Alberts_Molecular_Biology_of_the_Cell_7ed_2022.txt`, Page 679)
```text
"(A) Passive transport down a concentration gradient (or an electrochemical 
gradient-see panel B) occurs spontaneously, by diffusion, either through the lipid 
bilayer directly or through channels or passive transporters; an input of metabolic 
energy is not required.

(B) Active transport requires an input of metabolic energy (such as that generated 
by ATP hydrolysis) to pump solutes against their electrochemical gradients."
```
* **Exact Disk Citation**: Alberts et al. (7th ed., 2022), Chapter 11, Figure 11-4 Caption & Main Text, Pages 678–679.
* **Corpus Note**: The benchmark dataset `eval.jsonl` cited `page: 612` (the print page number of the transport section in earlier print layouts), which corresponds to the Chapter 11 digital corpus block at digital offsets `[678–679]`.

---

## 3. Side-by-Side Question Comparison Matrix

The table below contrasts the structural properties of both target questions:

| Feature Dimension | Question 2 (q02 / SQA_02) | Question 5 (q05 / SQA_05_Bio) |
| :--- | :--- | :--- |
| **Scientific Discipline** | Statistical Physics & Biophysical Kinetics | Molecular Cell Biology & Bioenergetics |
| **Foundational Textbook** | Berg, *Random Walks in Biology* (1993) | Alberts et al., *Molecular Biology of the Cell* (2022) |
| **Physical Quantity / Entity**| Protein Lysozyme, RMS Velocity, Temperature | Lipid Bilayer, Solute Gradient, ATP Hydrolysis |
| **Method 1 Hypothesis** | *"Lowering the temperature... increases RMS thermal velocity..."* | *"Passive diffusion... requires direct metabolic input from ATP hydrolysis."* |
| **Ground Truth Verdict** | **REFUTED** ($v_{\text{rms}} \propto \sqrt{T}$) | **REFUTED** ($\Delta G < 0$; passive requires 0 ATP) |
| **Method 2 Research Query** | *"According to equipartition theory, what is thermal kinetic energy per degree of freedom...?"* | *"How does the driving force for passive diffusion differ from active transport...?"* |
| **Evidence Footprint** | Extremely compact (isolated in ~100 words on Page 2) | Dispersed (derived across broad chapter diagrams) |
| **Retrieval Challenge** | Exact keyword co-location; OCR formula scan | Filtering dense biological prose within context budget |
| **Evaluation Standard** | Snapped disk bytes; NLI contradiction proof | Snapped disk bytes; NLI contradiction proof |
