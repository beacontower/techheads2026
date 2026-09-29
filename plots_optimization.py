#!/usr/bin/env python3
"""
"Why you can't brute-force it" optimization visual for the TechHeads 2026 talk.

Renders an illustrative Pyomo-style constrained-optimization formulation for
real-time district-heating control: minimise energy in, subject to the physics
you can't break (demand satisfaction, minimum differential pressure at the far
end, thermal balance with pipe delay, plant ramp limits). The point: the
constraints ARE the value — it's a small, bounded, solvable problem, not a
black box.

It's a static figure (not runnable code), deliberately schematic. Not the
actual proprietary formulation — an honest illustration of the problem class.

    python plots_optimization.py

Output: figures/fig_optimization.png   (Glaze palette)
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

RED = "#D91F22"; DARK = "#1E1C1D"; GREY = "#7F7F7F"; CMT = "#6E7781"
CODEBG = "#F7F7F5"

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE / "figures"

LINES = [
    ("# decide setpoints for every substation, every step", CMT),
    ("m = ConcreteModel()", DARK),
    ("m.q = Var(nodes, steps, domain=NonNegativeReals)   # heat delivered", DARK),
    ("m.Ts = Var(nodes, steps, bounds=(T_min, T_max))    # supply temp", DARK),
    ("", DARK),
    ("# objective: least energy in, over the whole horizon", CMT),
    ("m.cost = Objective(", DARK),
    ("    expr = sum(pump[n,t] + loss(Ts[n,t]) for n,t in NxT),", DARK),
    ("    sense = minimize)", DARK),
    ("", DARK),
    ("# subject to  \u2014  the physics you cannot break", RED),
    ("m.demand   = Constraint(...)   # every consumer stays warm", DARK),
    ("m.pressure = Constraint(...)   # dp >= dp_min at the far end", DARK),
    ("m.thermal  = Constraint(...)   # heat balance + pipe delay", DARK),
    ("m.ramp     = Constraint(...)   # plant moves slowly", DARK),
]


def build():
    fig, ax = plt.subplots(figsize=(11, 6.2))
    ax.set_xlim(0, 100); ax.set_ylim(0, 62); ax.axis("off")
    ax.add_patch(FancyBboxPatch((1, 1), 98, 52,
                 boxstyle="round,pad=0.4,rounding_size=1.2",
                 fc=CODEBG, ec="#E2E0D8", lw=1.2))
    ax.text(1, 58.2, "The real problem: minimise energy, respect the physics",
            fontsize=15, fontweight="bold", color=DARK)

    mono = dict(family="DejaVu Sans Mono", fontsize=11.5)
    y = 49.5
    for text, col in LINES:
        if text:
            ax.text(4, y, text, color=col, va="top", **mono)
        y -= 3.05 if text else 1.4

    ax.add_patch(FancyBboxPatch((70, 30), 27, 20,
                 boxstyle="round,pad=0.4,rounding_size=1", fc="#FCEBEB", ec=RED, lw=1.4))
    ax.text(83.5, 46.5, "Why not brute force?", ha="center",
            fontsize=12, fontweight="bold", color=DARK)
    for i, t in enumerate(["The constraints ARE", "the value. A black box",
                           "ignores them; physics", "doesn't. So we solve",
                           "the bounded problem \u2014", "small, cheap, trusted."]):
        ax.text(72, 42.5 - i * 2.3, t, fontsize=10.5, color=DARK, va="top")

    ax.text(1, -1.2, "Constrained optimisation over a digital twin of the "
            "network (illustrative Pyomo formulation). Small, physics-based, "
            "solvable \u2014 not a black box.", fontsize=9, color=GREY)

    plt.tight_layout(pad=0.3)
    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / "fig_optimization.png"
    plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[ok  ] {out}")


if __name__ == "__main__":
    build()
