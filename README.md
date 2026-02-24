# Office Relocation Optimization (Université Paris–Duchesse) — Large-Scale Linear Programming

Optimization project addressing **office relocation during a multi-phase renovation** at Université Paris–Duchesse.
The problem is modeled as a **large-scale linear program (LP)**, solved in **primal and dual** form, with verification of **strong duality** and **KKT conditions**, and interpretation of **shadow prices** to extract operational insights.

## Business context
During renovation phases, teams must be temporarily relocated while respecting:
- limited office capacities,
- move/assignment constraints across phases,
- operational feasibility requirements,
- cost/penalty trade-offs (moves, deviations, unmet preferences, etc.).

Goal: produce a **feasible relocation plan per phase** while minimizing the total operational cost/penalty.

## Model (high-level)
- **Decision variables**: assignment / flow variables describing how people (or teams) are allocated/moved across offices and phases.
- **Objective**: minimize total cost (e.g., moves + penalties for constraint violations/deviations).
- **Constraints** (typical):
  - capacity constraints per office/area,
  - flow conservation / phase-to-phase consistency,
  - equality constraints for required allocations,
  - bounds and feasibility constraints.

## Solve + validation
- Solve the **primal** LP and the associated **dual** problem.
- Verify:
  - **Strong duality** (primal objective equals dual objective at optimality),
  - **KKT conditions** (complementary slackness + feasibility).
- Use the dual variables to interpret **shadow prices**:
  - quantify the marginal value of relaxing a capacity/equality constraint,
  - identify the most critical bottlenecks in the renovation plan.

## Results & insights (from the report)
See the full write-up:
- `ProjectMDS/Project_MDS_Bennat_Bessy_Mabrouk.pdf`

Example insights supported by dual analysis:
- which capacities are the tightest and how costly they are (shadow prices),
- which constraints drive the solution structure,
- where additional temporary capacity would reduce cost the most.

## Repository contents
- `ProjectMDS/ProjectMDS_sujet.pdf` — assignment statement / specification
- `ProjectMDS/Project_MDS_Bennat_Bessy_Mabrouk.pdf` — final report (model + solution + analysis)
- `ProjectMDS/solutionMDS/` — exported primal/dual solutions and indicators (CSV)

## Authors
- Marwane Bennat — https://github.com/GitMarcode  
- (Add teammates here)

## License
MIT — see `LICENSE`.
