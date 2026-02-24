from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple


Office = str
Service = str
Phase = int
Transition = int


@dataclass(frozen=True)
class Instance:
    offices: List[Office]
    services: List[Service]
    phases: List[Phase]            # P = {0..5}
    transitions: List[Transition]  # T = {0..4}
    cap: int

    V: Dict[Phase, Set[Office]]  # availability sets V_p

    # boundary conditions: y0[i,s], yF[i,s]
    y0: Dict[Tuple[Office, Service], float]
    yF: Dict[Tuple[Office, Service], float]


def build_paris_duchesse_instance() -> Instance:
    I = ["A1", "A2", "B1", "B2", "B3", "C1", "C2", "D1", "D2", "D3", "E1", "E2"]
    # Use the PDF notation: P, S, O, T, M
    S = ["P", "S", "O", "T", "M"]
    P = [0, 1, 2, 3, 4, 5]
    T = [0, 1, 2, 3, 4]
    cap = 2

    V0 = {"A1", "A2", "B1", "B2", "B3", "C1", "C2", "D1", "D2", "D3"}  # no E yet
    V1 = (V0 | {"E1", "E2"}) - {"B1", "B2", "B3"}
    V2 = (V0 | {"E1", "E2"}) - {"D1", "D2", "D3"}
    V3 = (V0 | {"E1", "E2"}) - {"C1", "C2"}
    V4 = (V0 | {"E1", "E2"}) - {"A1", "A2"}
    V5 = set(I)
    V = {0: V0, 1: V1, 2: V2, 3: V3, 4: V4, 5: V5}

    y0: Dict[Tuple[Office, Service], float] = {(i, s): 0.0 for i in I for s in S}
    yF: Dict[Tuple[Office, Service], float] = {(i, s): 0.0 for i in I for s in S}

    # Initial allocation (phase 0)
    y0[("A1", "P")] = 2
    y0[("A2", "P")] = 2
    y0[("B1", "O")] = 1
    y0[("B1", "M")] = 1
    y0[("B2", "S")] = 2
    y0[("B3", "O")] = 1
    y0[("B3", "T")] = 1
    y0[("C1", "T")] = 2
    y0[("C2", "S")] = 2
    y0[("D1", "T")] = 1
    y0[("D2", "M")] = 1
    y0[("D3", "M")] = 2

    # Final allocation (phase 5)
    yF[("A1", "P")] = 2
    yF[("A2", "P")] = 2
    yF[("B1", "M")] = 1
    yF[("B2", "M")] = 2
    yF[("B3", "M")] = 1
    yF[("C1", "S")] = 2
    yF[("C2", "S")] = 2
    yF[("D1", "T")] = 1
    yF[("D2", "T")] = 2
    yF[("D3", "T")] = 1
    yF[("E1", "O")] = 1
    yF[("E2", "O")] = 1

    return Instance(
        offices=I,
        services=S,
        phases=P,
        transitions=T,
        cap=cap,
        V=V,
        y0=y0,
        yF=yF,
    )
