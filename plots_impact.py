#!/usr/bin/env python3
"""
National-impact comparison figure for the TechHeads 2026 talk.

Answers "what if we cut waste across all of Sweden?" at three savings rates,
expressed as multiples of Kalmar's yearly district-heating output — same
energy type, so it's an honest like-for-like comparison (no thermal-vs-
electrical conversion).

    python plots_impact.py

Output: figures/fig_national_impact.png   (Glaze palette)

Numbers (edit in CONFIG):
  Sweden delivered DH: 50.4 TWh (Energimyndigheten, final 2024 statistics).
  Kalmar anchor: Moskogen CHP plant ~360 GWh/year heat (Kalmar Energi, own
    published facilities figure). This is production at the main plant, the
    most defensible single public number; delivered-to-customer differs
    slightly. If you obtain Kalmar Energi's official delivered figure, set
    KALMAR_GWH to that and update the source line.
  Rates: 3% (conservative), 5% (mid), 7.3% (our winter pilot result). Not
    every grid has the same headroom — we target small and mid-size grids.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

RED = "#D91F22"; DARK = "#1E1C1D"; GREY = "#7F7F7F"; LGREY = "#BFBFBF"

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE / "figures"

# ---- CONFIG ----
SE_GWH = 50400          # Sweden delivered DH, GWh/year (Energimyndigheten 2024)
KALMAR_GWH = 360        # Kalmar Moskogen plant heat, GWh/year (Kalmar Energi)
ROWS = [(3, "conservative"), (5, "mid"), (7.3, "our winter pilot")]
SOURCE = ("Sweden: 53.0 TWh produced, 50.4 TWh delivered (Energimyndigheten 2024). "
          "Moskogen plant ~360 GWh/year, Kalmar Energi.")
# ----------------


def build():
    fig, ax = plt.subplots(figsize=(10.5, 5.6))
    ax.set_xlim(0, 100); ax.set_ylim(0, 62); ax.axis("off")

    ax.text(2, 58, "What if we cut waste across all of Sweden?",
            fontsize=17, fontweight="bold", color=DARK)
    ax.text(2, 56.8, "Sweden delivers ~50 TWh of district heating a year \u2014 and ~2.6 TWh never even reaches",
            fontsize=11.5, color=DARK)
    ax.text(2, 53.3, "customers, lost in the pipes. Trim a few percent more of the waste, without burning anything new:",
            fontsize=11.5, color=DARK)

    y0, rh = 40, 9.5
    for i, (r, lab) in enumerate(ROWS):
        y = y0 - i * rh
        saved = SE_GWH * r / 100
        mult = saved / KALMAR_GWH
        focus = (i == 0)
        fc = "#FCEBEB" if focus else "#F7F7F5"
        ec = RED if focus else LGREY
        ax.add_patch(FancyBboxPatch((2, y), 96, rh - 1.4,
                     boxstyle="round,pad=0.2,rounding_size=1", fc=fc, ec=ec, lw=1.5))
        ax.text(9, y + (rh - 1.4) / 2, f"{r:g}%", ha="center", va="center",
                fontsize=20, fontweight="bold", color=RED if focus else DARK)
        ax.text(9, y + 1.3, lab, ha="center", va="center", fontsize=8, color=GREY)
        ax.text(34, y + (rh - 1.4) / 2, f"{saved:,.0f} GWh / year",
                ha="center", va="center", fontsize=15, color=DARK)
        ax.text(52, y + (rh - 1.4) / 2, "\u2248", ha="center", va="center",
                fontsize=16, color=GREY)
        ax.text(75, y + (rh - 1.4) / 2, f"{mult:.0f}\u00d7", ha="center",
                va="center", fontsize=22, fontweight="bold",
                color=RED if focus else DARK)
        ax.text(75, y + 1.3, "Moskogen\u2019s yearly output", ha="center",
                va="center", fontsize=8.5, color=GREY)

    ax.text(2, 4.5, "Not every grid has the same headroom \u2014 we target small "
            "and mid-size grids, where the potential is greatest.",
            fontsize=9.5, color=DARK, style="italic")
    ax.text(2, 1.2, SOURCE, fontsize=8, color=GREY)

    plt.tight_layout(pad=0.3)
    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / "fig_national_impact.png"
    plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[ok  ] {out}")


if __name__ == "__main__":
    build()
