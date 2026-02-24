from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import pulp

from .data import Instance, Office, Phase, Service, Transition


@dataclass
class PenalizedVars:
    y: Dict[Tuple[Phase, Office, Service], pulp.LpVariable]
    x: Dict[Tuple[Transition, Office, Office, Service], pulp.LpVariable]
    t: Dict[Tuple[Phase, Office, Service], pulp.LpVariable]


def build_penalized_lp(instance: Instance, lam: float = 100.0, prune_arcs: bool = True) -> tuple[pulp.LpProblem, PenalizedVars]:
    """
    Penalized LP P_lam:

    min  sum_{p=0..4,s,i,j!=i} x[p,i,j,s]  + lam * sum_{p=0..5,i,s} t[p,i,s]

    s.t.
      FO: y[p,i,s] = sum_j x[p,i,j,s]
      FI: y[p+1,j,s] = sum_i x[p,i,j,s]
      CAP: sum_s y[p,i,s] <= cap
      UNAV: y[p,i,s] = 0 if i not in V[p]
      BC: y[0,i,s]=y0[i,s], y[5,i,s]=yF[i,s]
      ABS linearization:
        y[p,i,s] - t[p,i,s] <= yF[i,s]
        -y[p,i,s] - t[p,i,s] <= -yF[i,s]
      x,y,t >= 0
    """
    prob = pulp.LpProblem(f"ParisDuchesse_Penalized_LP_lambda{lam:g}", pulp.LpMinimize)

    y: Dict[Tuple[Phase, Office, Service], pulp.LpVariable] = {}
    for p in instance.phases:
        for i in instance.offices:
            for s in instance.services:
                y[(p, i, s)] = pulp.LpVariable(f"y_p{p}_{i}_{s}", lowBound=0, cat="Continuous")

    t: Dict[Tuple[Phase, Office, Service], pulp.LpVariable] = {}
    for p in instance.phases:
        for i in instance.offices:
            for s in instance.services:
                t[(p, i, s)] = pulp.LpVariable(f"t_p{p}_{i}_{s}", lowBound=0, cat="Continuous")

    x: Dict[Tuple[Transition, Office, Office, Service], pulp.LpVariable] = {}
    for p in instance.transitions:
        for i in instance.offices:
            for j in instance.offices:
                for s in instance.services:
                    if prune_arcs:
                        if i not in instance.V[p] or j not in instance.V[p + 1]:
                            continue
                    x[(p, i, j, s)] = pulp.LpVariable(f"x_p{p}_{i}_to_{j}_{s}", lowBound=0, cat="Continuous")

    # Objective decomposition
    move_term = pulp.lpSum(
        var for (p, i, j, s), var in x.items() if i != j
    )
    dev_term = pulp.lpSum(t.values())
    prob += move_term + lam * dev_term, "moves_plus_lambda_L1_deviation"

    # FO
    for p in instance.transitions:
        for i in instance.offices:
            for s in instance.services:
                outgoing = [x[(p, i, j, s)] for j in instance.offices if (p, i, j, s) in x]
                prob += (y[(p, i, s)] - pulp.lpSum(outgoing) == 0), f"FO_p{p}_{i}_{s}"

    # FI
    for p in instance.transitions:
        for j in instance.offices:
            for s in instance.services:
                incoming = [x[(p, i, j, s)] for i in instance.offices if (p, i, j, s) in x]
                prob += (y[(p + 1, j, s)] - pulp.lpSum(incoming) == 0), f"FI_p{p}_{j}_{s}"

    # CAP
    for p in instance.phases:
        for i in instance.offices:
            prob += (pulp.lpSum(y[(p, i, s)] for s in instance.services) <= instance.cap), f"CAP_p{p}_{i}"

    # UNAV
    for p in instance.phases:
        for i in instance.offices:
            if i in instance.V[p]:
                continue
            for s in instance.services:
                prob += (y[(p, i, s)] == 0), f"UNAV_p{p}_{i}_{s}"

    # BC
    for i in instance.offices:
        for s in instance.services:
            prob += (y[(0, i, s)] == instance.y0[(i, s)]), f"BC0_{i}_{s}"
            prob += (y[(5, i, s)] == instance.yF[(i, s)]), f"BC5_{i}_{s}"

    # ABS linearization for |y - yF|
    for p in instance.phases:
        for i in instance.offices:
            for s in instance.services:
                yF = instance.yF[(i, s)]
                # y - t <= yF   <=>  y - t - yF <= 0
                prob += (y[(p, i, s)] - t[(p, i, s)] <= yF), f"ABS_pos_p{p}_{i}_{s}"
                # -y - t <= -yF <=> -y - t + yF <= 0
                prob += (-y[(p, i, s)] - t[(p, i, s)] <= -yF), f"ABS_neg_p{p}_{i}_{s}"

    return prob, PenalizedVars(y=y, x=x, t=t)
