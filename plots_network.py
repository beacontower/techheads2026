#!/usr/bin/env python3
"""
Illustrative district-heating network graph for the TechHeads 2026 talk.

Generates a tree-topology DH network: a central heat plant, thick transport
trunks radiating out, thinner distribution pipes branching down to consumer
nodes at the leaves. This is the canonical DH structure in the literature
(central plant -> transport -> distribution); see e.g. tree-shaped case
studies for Zemun (Serbia), Ebbw Vale (Wales), and Finnish small towns, and
the meshed Verbier benchmark (Boghetti & Kämpf 2023).

It is a generated illustration, not real network data — captioned as such.
Reproducible via the fixed RNG seed.

    python plots_network.py

Output: figures/fig_network.png   (Glaze palette)
"""

from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RED = "#D91F22"; DARK = "#1E1C1D"; GREY = "#7F7F7F"; PIPE = "#C23B3B"; LEAF = "#5B8DB8"

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE / "figures"

SEED = 7
N_TRUNKS = 5
DEPTH = 3


def build():
    rng = np.random.default_rng(SEED)
    nodes = []   # (x, y, kind)
    edges = []   # (i, j, is_transport)

    def add(x, y, kind):
        nodes.append((x, y, kind))
        return len(nodes) - 1

    plant = add(0, 0, "plant")

    def grow(parent, angle, length, depth, transport):
        px, py, _ = nodes[parent]
        jitter = rng.normal(0, 0.10)
        x = px + length * np.cos(angle + jitter)
        y = py + length * np.sin(angle + jitter)
        idx = add(x, y, "junction" if depth > 0 else "consumer")
        edges.append((parent, idx, transport))
        if depth == 0:
            return
        n_branch = rng.integers(2, 4)
        spread = 0.7 if transport else 1.1
        for k in range(n_branch):
            a = (angle + spread * ((k - (n_branch - 1) / 2) / max(1, n_branch - 1)) * 1.6
                 + rng.normal(0, 0.15))
            grow(idx, a, length * rng.uniform(0.55, 0.8), depth - 1, transport and k == 0)

    for t in range(N_TRUNKS):
        a = 2 * np.pi * t / N_TRUNKS + rng.normal(0, 0.2)
        grow(plant, a, 1.6, DEPTH, transport=True)

    fig, ax = plt.subplots(figsize=(9.5, 7.2))
    ax.axis("off"); ax.set_aspect("equal")

    for i, j, tr in edges:
        x1, y1, _ = nodes[i]; x2, y2, _ = nodes[j]
        ax.plot([x1, x2], [y1, y2], color=PIPE, lw=3.2 if tr else 1.4,
                alpha=0.9 if tr else 0.6, solid_capstyle="round", zorder=1)

    for x, y, kind in nodes:
        if kind == "plant":
            ax.scatter([x], [y], s=680, color=DARK, zorder=4, marker="s")
            ax.scatter([x], [y], s=250, color=RED, zorder=5, marker="s")
        elif kind == "consumer":
            ax.scatter([x], [y], s=26, color=LEAF, zorder=3,
                       edgecolors="white", linewidths=0.5)
        else:
            ax.scatter([x], [y], s=9, color=PIPE, zorder=2)

    ax.text(0, -0.42, "Heat plant", ha="center", va="top",
            fontsize=12, fontweight="bold", color=DARK)
    ax.text(0.01, 0.99, "One plant, branching out to every consumer",
            transform=ax.transAxes, fontsize=15, fontweight="bold", color=DARK, va="top")
    ncons = sum(1 for _, _, k in nodes if k == "consumer")
    fig.text(0.005, 0.01,
             f"Illustrative tree-topology district heating network ({ncons} consumers), "
             "the canonical DH structure in the literature (central plant \u2192 transport \u2192 distribution).",
             fontsize=8, color=GREY)
    plt.tight_layout()

    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / "fig_network.png"
    plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[ok  ] {out}  ({ncons} consumers)")


if __name__ == "__main__":
    build()
