from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import pulp

from .data import Instance, Office, Phase, Service, Transition


@dataclass
class ModelVars:
    y: Dict[Tuple[Phase, Office, Service], pulp.LpVariable]
    x: Dict[Tuple[Transition, Office, Office, Service], pulp.LpVariable]


def build_q2_lp(instance: Instance, prune_arcs: bool = True) -> tuple[pulp.LpProblem, ModelVars]:
    """
    Q1/Q2 LP relaxation:
      min sum_{p,s,i,j} c_ij x[p,i,j,s], with c_ij = 1 if i!=j else 0
      s.t. FO/FI/CAP/UNAV/BC and x,y >= 0
    """
    prob = pulp.LpProblem("ParisDuchesse_Q2_LP", pulp.LpMinimize)

    # Variables y[p,i,s] for all phases/offices/services (even if unavailable; then forced to 0 by UNAV)
    y: Dict[Tuple[Phase, Office, Service], pulp.LpVariable] = {}
    for p in instance.phases:
        for i in instance.offices:
            for s in instance.services:
                y[(p, i, s)] = pulp.LpVariable(f"y_p{p}_{i}_{s}", lowBound=0, cat="Continuous")

    # Variables x[p,i,j,s] for transitions
    x: Dict[Tuple[Transition, Office, Office, Service], pulp.LpVariable] = {}
    for p in instance.transitions:
        for i in instance.offices:
            for j in instance.offices:
                for s in instance.services:
                    if prune_arcs:
                        # Keep only arcs from available offices at p to available offices at p+1
                        if i not in instance.V[p] or j not in instance.V[p + 1]:
                            continue
                    x[(p, i, j, s)] = pulp.LpVariable(f"x_p{p}_{i}_to_{j}_{s}", lowBound=0, cat="Continuous")

    # Objective: moves only when i != j
    prob += pulp.lpSum(
        (0 if i == j else 1) * var
        for (p, i, j, s), var in x.items()
    ), "total_moves"

    # FO: y[p,i,s] - sum_j x[p,i,j,s] = 0
    for p in instance.transitions:
        for i in instance.offices:
            for s in instance.services:
                outgoing = [x[(p, i, j, s)] for j in instance.offices if (p, i, j, s) in x]
                prob += (y[(p, i, s)] - pulp.lpSum(outgoing) == 0), f"FO_p{p}_{i}_{s}"

    # FI: y[p+1,j,s] - sum_i x[p,i,j,s] = 0
    for p in instance.transitions:
        for j in instance.offices:
            for s in instance.services:
                incoming = [x[(p, i, j, s)] for i in instance.offices if (p, i, j, s) in x]
                prob += (y[(p + 1, j, s)] - pulp.lpSum(incoming) == 0), f"FI_p{p}_{j}_{s}"

    # CAP: sum_s y[p,i,s] <= cap
    for p in instance.phases:
        for i in instance.offices:
            prob += (
                pulp.lpSum(y[(p, i, s)] for s in instance.services) <= instance.cap
            ), f"CAP_p{p}_{i}"

    # UNAV: y[p,i,s] = 0 for i not in V[p]
    for p in instance.phases:
        for i in instance.offices:
            if i in instance.V[p]:
                continue
            for s in instance.services:
                prob += (y[(p, i, s)] == 0), f"UNAV_p{p}_{i}_{s}"

    # Boundary conditions
    for i in instance.offices:
        for s in instance.services:
            prob += (y[(0, i, s)] == instance.y0[(i, s)]), f"BC0_{i}_{s}"
            prob += (y[(5, i, s)] == instance.yF[(i, s)]), f"BC5_{i}_{s}"

    return prob, ModelVars(y=y, x=x)
