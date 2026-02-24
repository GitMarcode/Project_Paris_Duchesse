from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import pulp

from .data import build_paris_duchesse_instance
from .model_q5_penalized import build_penalized_lp


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lambda", dest="lam", type=float, default=100.0)
    parser.add_argument("--out-dir", type=Path, default=Path("outputs_q5"))
    parser.add_argument("--prune-arcs", action="store_true", default=True)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)

    inst = build_paris_duchesse_instance()
    prob, vars_ = build_penalized_lp(inst, lam=args.lam, prune_arcs=args.prune_arcs)

    # HiGHS solver (for speed + duals)
    solver = pulp.HiGHS(msg=True)
    status = prob.solve(solver)

    obj = float(pulp.value(prob.objective))
    print("Status:", pulp.LpStatus[status])
    print("Objective:", obj)

    # Compute move count and L1 deviation from solution (should match PDF: moves=38, L1=52 for lam=100)
    move_count = sum(var.value() for (p, i, j, s), var in vars_.x.items() if i != j)
    l1_dev = sum(var.value() for var in vars_.t.values())

    move_count = float(move_count)
    l1_dev = float(l1_dev)

    print("Move count term:", move_count)
    print("L1 deviation term:", l1_dev)
    print("Decomposed objective:", move_count + args.lam * l1_dev)

    # Export y
    y_rows = []
    for (p, i, s), var in vars_.y.items():
        val = var.value()
        if val is None:
            continue
        if abs(val) > 1e-9:
            y_rows.append({"phase": p, "office": i, "service": s, "y": float(val)})
    pd.DataFrame(y_rows).sort_values(["phase", "office", "service"]).to_csv(args.out_dir / "y_solution.csv", index=False)

    # Export true moves x (i != j)
    x_rows = []
    for (p, i, j, s), var in vars_.x.items():
        val = var.value()
        if val is None or abs(val) <= 1e-9:
            continue
        if i != j:
            x_rows.append({"transition": p, "from": i, "to": j, "service": s, "x": float(val)})
    pd.DataFrame(x_rows).sort_values(["transition", "from", "to", "service"]).to_csv(args.out_dir / "x_true_moves.csv", index=False)

    # Export t
    t_rows = []
    for (p, i, s), var in vars_.t.items():
        val = var.value()
        if val is None:
            continue
        if abs(val) > 1e-9:
            t_rows.append({"phase": p, "office": i, "service": s, "t": float(val)})
    pd.DataFrame(t_rows).sort_values(["phase", "office", "service"]).to_csv(args.out_dir / "t_abs_deviation.csv", index=False)

    # Per-phase L1 distances (as in PDF)
    per_phase = []
    for p in inst.phases:
        phase_l1 = sum(vars_.t[(p, i, s)].value() or 0.0 for i in inst.offices for s in inst.services)
        per_phase.append({"phase": p, "l1_to_final": float(phase_l1)})
    pd.DataFrame(per_phase).to_csv(args.out_dir / "per_phase_l1.csv", index=False)

    # Per-transition move counts
    per_tr = []
    for p in inst.transitions:
        tr_moves = sum(var.value() or 0.0 for (pp, i, j, s), var in vars_.x.items() if pp == p and i != j)
        per_tr.append({"transition": f"{p}->{p+1}", "moves": float(tr_moves)})
    pd.DataFrame(per_tr).to_csv(args.out_dir / "per_transition_moves.csv", index=False)

    # Summary
    (args.out_dir / "summary.txt").write_text(
        "\n".join(
            [
                f"Status: {pulp.LpStatus[status]}",
                f"Objective: {obj}",
                f"Move count: {move_count}",
                f"L1 deviation: {l1_dev}",
                f"Lambda: {args.lam}",
                f"Move + lam*L1: {move_count + args.lam * l1_dev}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print("Wrote outputs to", args.out_dir)
    print("Expected (PDF for lam=100): objective=5238, moves=38, L1=52")


if __name__ == "__main__":
    main()
