#!/usr/bin/env python3
"""
Problem-domain explainer schematic for the TechHeads 2026 talk.

Draws the "what makes district heating hard" anchor diagram: a slow plant, a
heat-storing / limit-bound pipe network, and many small consumers (one of them
the worst-off "critical" one that must always be satisfied), plus the four
properties that make control hard. This is a standalone schematic, not built
from any dataset — it sets up the four data plots that follow it in the deck.

Output: figures/fig_problem_domain.png   (Glaze palette, matches the others)

    python plots_domain.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

RED = "#D91F22"; DARK = "#1E1C1D"; GREY = "#7F7F7F"; GRID = "#E7E6E6"
AMBER = "#BA7517"; BLUE = "#1C6DD0"; LGREY = "#BFBFBF"

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE / "figures"


def build():
    fig, ax = plt.subplots(figsize=(11, 6.2))
    ax.set_xlim(0, 110); ax.set_ylim(0, 62); ax.axis("off")

    def box(x, y, w, h, fc, ec, title, sub=None, tc=None, bold=True):
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                     boxstyle="round,pad=0.3,rounding_size=1.2", fc=fc, ec=ec, lw=1.5))
        tcol = tc or DARK
        if sub:
            ax.text(x + w / 2, y + h * 0.60, title, ha="center", va="center",
                    fontsize=13, fontweight="bold" if bold else "normal", color=tcol)
            ax.text(x + w / 2, y + h * 0.28, sub, ha="center", va="center",
                    fontsize=10.5, color=tcol)
        else:
            ax.text(x + w / 2, y + h / 2, title, ha="center", va="center",
                    fontsize=13, fontweight="bold" if bold else "normal", color=tcol)

    def arrow(x1, y1, x2, y2, color=GREY, lw=1.6):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                     mutation_scale=14, color=color, lw=lw, shrinkA=0, shrinkB=0))

    ax.text(2, 59, "One slow system, many demanding consumers",
            fontsize=15, fontweight="bold", color=DARK)

    box(2, 40, 18, 13, "#FCEBEB", RED, "Plant", "slow to react", tc="#791F1F")

    ax.add_patch(FancyBboxPatch((30, 26), 22, 28,
                 boxstyle="round,pad=0.3,rounding_size=1.2", fc="#F1EFE8", ec=GREY, lw=1.5))
    ax.text(41, 47.5, "Pipe network", ha="center", va="center",
            fontsize=13, fontweight="bold", color=DARK)
    ax.text(41, 43.5, "stores heat,", ha="center", va="center", fontsize=10.5, color=DARK)
    ax.text(41, 40.8, "bound by limits", ha="center", va="center", fontsize=10.5, color=DARK)

    cons_y = [47, 40, 33]
    for cy in cons_y:
        box(64, cy, 20, 5.5, "#E6F1FB", BLUE, "consumer", None, tc="#0C447C", bold=False)
    box(64, 25, 20, 6.2, "#B5D4F4", BLUE, "critical", "worst-off, far end", tc="#042C53")

    arrow(20, 46.5, 29.5, 45)
    ax.text(24.5, 48.5, "supply", ha="center", fontsize=10.5, color=GREY)
    for cy in cons_y:
        arrow(52, 42, 63.5, cy + 2.7, color=LGREY, lw=1.3)
    arrow(52, 38, 63.5, 28, color=BLUE, lw=1.6)
    ax.text(74, 22.5, "must keep every one satisfied", ha="center", fontsize=10.5, color=GREY)

    ax.plot([2, 108], [18, 18], color=GRID, lw=1)
    ax.text(2, 15, "What makes it hard", fontsize=15, fontweight="bold", color=DARK)

    facets = [("Slow", "minutes to hours", "#FCEBEB", RED, "#791F1F"),
              ("Weather-driven", "but only loosely", "#FAEEDA", AMBER, "#633806"),
              ("Chaotic", "per consumer", "#E6F1FB", BLUE, "#0C447C"),
              ("Constrained", "hard physical limits", "#F1EFE8", GREY, DARK)]
    fx = 2; fw = 25; gap = 2.3
    for (t, s, fc, ec, tc) in facets:
        box(fx, 3, fw, 8, fc, ec, t, s, tc=tc)
        fx += fw + gap

    plt.tight_layout(pad=0.4)
    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / "fig_problem_domain.png"
    plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[ok  ] {out}")


if __name__ == "__main__":
    build()
