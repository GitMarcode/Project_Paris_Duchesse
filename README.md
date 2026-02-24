# Office Relocation Optimization (Université Paris–Duchesse)
**Large-scale Linear Programming (LP)** for multi-phase office relocations with **primal/dual analysis** and a **penalized objective** that keeps intermediate phases close to the final layout.

This project models a 6-phase renovation schedule across 5 wings (A–E). **18 people**, grouped into **5 services** (P, S, O, T, M), must be reassigned to offices across phases while respecting **office availability** and **capacity (2 seats per office)** and minimizing relocations.

## Problem in one sentence
Find a feasible phase-by-phase relocation plan that **minimizes the total number of moves**, and (optionally) trades off moves vs. staying close to the **final target layout**.

---

## Model (service-based multi-commodity flow)
We aggregate individuals by **service** and use a **multi-commodity flow over time**.

### Sets
- Offices: \(I=\{A1,A2,B1,B2,B3,C1,C2,D1,D2,D3,E1,E2\}\) (12 offices)
- Services: \(\mathcal S=\{P,S,O,T,M\}\) (5 services)
- Phases: \(P=\{0,1,2,3,4,5\}\)
- Transitions: \(T=\{0,1,2,3,4\}\) (move from phase \(p\) to \(p+1\))

### Decision variables (LP relaxation)
- \(y^p_{i,s}\ge 0\): number of occupants of service \(s\) in office \(i\) at phase \(p\)
- \(x^p_{i\to j,s}\ge 0\): flow of service \(s\) moved from office \(i\) at phase \(p\) to office \(j\) at phase \(p+1\)

### Core constraints
- **Flow-out**: \(y^p_{i,s} = \sum_j x^p_{i\to j,s}\)
- **Flow-in**: \(y^{p+1}_{j,s} = \sum_i x^p_{i\to j,s}\)
- **Capacity**: \(\sum_s y^p_{i,s} \le 2\)
- **Unavailability**: \(y^p_{i,s}=0\) if office \(i\notin V_p\)
- **Boundary conditions**: phase 0 and phase 5 match the given initial/final service counts

---

## Objectives implemented in code

### Q2 — Move-only LP
Minimize the total number of moves:
\[
\min \sum_{p=0}^4\sum_s\sum_{i\ne j} x^p_{i\to j,s}
\]
Expected (from the report): **OPT = 30** (LP relaxation).

### Q5 — Penalized LP \(P_\lambda\) (implemented, default \(\lambda=100\))
We also penalize deviation from the final configuration using an \(L_1\) term:
\[
\min \underbrace{\sum_{p=0}^4\sum_s\sum_{i\ne j} x^p_{i\to j,s}}_{\#\text{moves}}
\;+\;
\lambda\underbrace{\sum_{p=0}^5\sum_{i,s} |y^p_{i,s}-y^F_{i,s}|}_{\sum_p\|z^p-z^F\|_1}
\]
We linearize \(|\cdot|\) using slack variables \(t^p_{i,s}\ge 0\).

Expected for \(\lambda=100\) (from the report):
- **OPT\_{100} = 5238**
- moves \(= 38\)
- total \(L_1\) deviation \(= 52\)
- decomposition: \(5238 = 38 + 100 \times 52\)

---

## Repository contents
- `ProjectMDS/Project_MDS_Bennat_Bessy_Mabrouk.pdf` — full report (math formulation, solutions, dual/KKT discussion)
- `ProjectMDS/solutionMDS/` — exported primal/dual solutions from the report (CSV)
- `src/` — PuLP + HiGHS implementation (reproducible)

---

## Reproducibility (Python)

### Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Solve Q5 (penalized LP, lambda=100)
```bash
python -m src.solve_q5 --lambda 100 --out-dir outputs_q5
```

Outputs:
- `outputs_q5/y_solution.csv` — allocations \(y^p_{i,s}\)
- `outputs_q5/x_true_moves.csv` — moves with \(i\ne j\)
- `outputs_q5/t_abs_deviation.csv` — deviation slacks \(t^p_{i,s}\)
- `outputs_q5/per_phase_l1.csv` — per-phase \(L_1\) distance to final layout
- `outputs_q5/per_transition_moves.csv` — moves per transition
- `outputs_q5/summary.txt` — objective decomposition check

### (Optional) Solve Q2 (move-only LP)
If you also added the Q2 scripts:
```bash
python -m src.solve_q2 --out-dir outputs_q2
```

---

## Why this project is relevant (internship-ready signals)
- Large-scale LP with a clean flow formulation (multi-commodity over time)
- Strong duality / KKT reasoning in the report
- Penalized objective to explore trade-offs (moves vs. trajectory stability)
- Fully reproducible solve pipeline with a modern LP solver (HiGHS)

---

## Authors
- Marwane Bennat — https://github.com/GitMarcode  
- (Add teammates here)

## License
MIT — see `LICENSE`.
