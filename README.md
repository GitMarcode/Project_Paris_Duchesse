# Office Relocation Optimization (Université Paris–Duchesse) — Large-Scale Linear Programming

Operations Research project addressing **office relocation during a multi-phase renovation** at Université Paris–Duchesse.

The problem is modeled as a **large-scale Linear Program (LP)** and analyzed through:
- **Primal + dual** formulations
- Verification of **strong duality** and **KKT conditions**
- Interpretation of **shadow prices** (dual variables) to extract operational insights

## Business context
During renovation phases, teams must be temporarily relocated while respecting:
- limited office capacities,
- multi-phase consistency constraints (who is where at each phase),
- operational feasibility requirements.

**Goal:** minimize the **total operational cost**, with an emphasis on **move minimization** across phases.

## Model (high level)
- **Decision variables:** assignment / flow variables describing how people (or teams) are allocated and moved across offices and phases.
- **Objective:** minimize the number/cost of moves (and possible penalties, depending on the formulation).
- **Constraints (typical):**
  - capacity constraints per office/zone,
  - flow conservation / phase-to-phase consistency,
  - required assignment equalities,
  - bounds and feasibility constraints.

## Solve + validation
This project:
- solves the **primal** LP and the corresponding **dual** problem,
- checks **strong duality** (primal optimum = dual optimum),
- verifies **KKT conditions** (incl. complementary slackness),
- uses dual variables to interpret **shadow prices**, e.g.:
  - which capacity constraints are the most binding,
  - where additional temporary capacity would reduce cost the most.

## Where to find the full details
- Final report (model + results + interpretation):  
  `ProjectMDS/Project_MDS_Bennat_Bessy_Mabrouk.pdf`
- Assignment statement/specification:  
  `ProjectMDS/ProjectMDS_sujet.pdf`
- Exported solutions (CSV):  
  `ProjectMDS/solutionMDS/`

## Repository structure
- `ProjectMDS/`
  - `ProjectMDS_sujet.pdf`
  - `Project_MDS_Bennat_Bessy_Mabrouk.pdf`
  - `solutionMDS/` — primal/dual solutions and indicators (CSV)

## Authors
- Marwane Bennat
- Mohy Mabrouk
- Alexis Bessy

## License
MIT — see `LICENSE`.
