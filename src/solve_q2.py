from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import pulp

from .data import build_paris_duchesse_instance
from .model_q2_lp import build_q2_lp


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("outputs_q2"))
    parser.add_argument("--prune-arcs", action="store_true", default=True)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)

    inst = build_paris_duchesse_instance()
    prob, vars_ = build_q2_lp(inst, prune_arcs=args.prune_arcs)

    # Solver: CBC by default (bundled with PuLP sometimes). For duals, prefer HiGHS later.
    solver = pulp.PULP_CBC_CMD(msg=True)
    status = prob.solve(solver)

    print("Status:", pulp.LpStatus[status])
    print("Objective (moves):", pulp.value(prob.objective))

    # Export y
    y_rows = []
    for (p, i, s), var in vars_.y.items():
        val = var.value()
        if val is None:
            continue
        if abs(val) > 1e-9:
            y_rows.append({"phase": p, "office": i, "service": s, "y": float(val)})
    pd.DataFrame(y_rows).sort_values(["phase", "office", "service"]).to_csv(args.out_dir / "y_solution.csv", index=False)

    # Export x (moves)
    x_rows = []
    for (p, i, j, s), var in vars_.x.items():
        val = var.value()
        if val is None:
            continue
        if abs(val) > 1e-9:
            x_rows.append({"transition": p, "from": i, "to": j, "service": s, "x": float(val), "moved": int(i != j)})
    pd.DataFrame(x_rows).sort_values(["transition", "from", "to", "service"]).to_csv(args.out_dir / "x_solution.csv", index=False)

    # NOTE about duals:
    # PuLP does not guarantee dual values with all solvers.
    # We'll add a HiGHS-based version if you want shadow prices exported automatically.

    summary = args.out_dir / "summary.txt"
    summary.write_text(
        f"Status: {pulp.LpStatus[status]}\nObjective(moves): {pulp.value(prob.objective)}\n",
        encoding="utf-8",
    )
    print("Wrote outputs to", args.out_dir)


if __name__ == "__main__":
    main()
