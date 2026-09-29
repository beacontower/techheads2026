#!/usr/bin/env python3
"""
Swedish district-heating grid-size distribution, built from Ei open data.

Reads "Levererad värme per prisområde" (fetch it with get_data_se.py), takes
the sold-heat figure per network for the latest year, buckets networks by
annual delivery, and plots the count per size class. The story: there are
~500 DH systems in Sweden and most of them are small.

    python plots_se.py

Output: figures/fig_grid_sizes.png   (Glaze palette)

Size classes (GWh/year) follow the banding used in Swedish DH reporting:
  1-10, 11-30, 31-90, 91-200, 201-500, >500

The Ei workbook has one row per price area (network) and one column of sold
heat; sheet and column names vary year to year, so the loader searches for a
"levererad/såld värme" column in MWh or GWh. If the file can't be parsed, it
falls back to the last-known published counts so a figure still renders (and
says so in the caption).
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------------------------------------------------------- CONFIG ----
RED = "#D91F22"; DARK = "#1E1C1D"; GREY = "#7F7F7F"; GRID = "#E7E6E6"
MUTED = "#BFBFBF"

HERE = Path(__file__).resolve().parent
SE_DIR = HERE / "data_se"
OUT_DIR = HERE / "figures"
XLSX = SE_DIR / "ei_levererad_varme_per_prisomrade.xlsx"

# size-class edges in GWh/year, and their labels
EDGES = [1, 10, 30, 90, 200, 500, np.inf]
LABELS = ["1\u201310", "11\u201330", "31\u201390", "91\u2013200", "201\u2013500", ">500"]
FOCUS = 2                      # highlight the smallest N classes in red
SMALL_THRESHOLD_GWH = 30       # for the "X of Y networks deliver <= 30 GWh" note

# fallback counts if the workbook can't be parsed (Ei 2023 via Fastighetsägarna)
FALLBACK_COUNTS = [107, 85, 68, 42, 24, 25]
FALLBACK_NOTE = ("Source: Energimarknadsinspektionen 2023 (utilities\u2019 annual "
                 "reports), via Fastighet\u00e4garna \u201cB\u00e4st i klassen 2025\u201d.")
# ---------------------------------------------------------------------------


def _find_heat_series(xlsx: Path):
    """Best-effort: return a Series of sold heat per network in GWh/year."""
    xl = pd.ExcelFile(xlsx)
    best = None
    for sheet in xl.sheet_names:
        for header in (0, 1, 2, 3):
            try:
                df = xl.parse(sheet, header=header)
            except Exception:
                continue
            for col in df.columns:
                name = str(col).lower()
                if ("levererad" in name or "s\u00e5ld" in name or "sald" in name) \
                        and ("v\u00e4rme" in name or "varme" in name):
                    s = pd.to_numeric(df[col], errors="coerce").dropna()
                    s = s[s > 0]
                    if len(s) > 100:            # looks like one row per network
                        # unit guess: MWh if median is huge, else GWh
                        unit_gwh = s / 1000.0 if s.median() > 2000 else s
                        if best is None or len(unit_gwh) > len(best):
                            best = unit_gwh
    return best


def load_counts():
    """Return (counts, note). Parse Ei file if possible, else fallback."""
    if XLSX.exists():
        try:
            heat = _find_heat_series(XLSX)
            if heat is not None and len(heat) > 100:
                cut = pd.cut(heat, bins=EDGES, labels=LABELS, right=True)
                counts = [int((cut == lab).sum()) for lab in LABELS]
                note = ("Source: Energimarknadsinspektionen, "
                        "\u201clevererad v\u00e4rme per prisomr\u00e5de\u201d (open data). "
                        f"{sum(counts)} networks.")
                return counts, note
        except Exception as e:
            print(f"[warn] could not parse {XLSX.name}: {e}")
    print("[info] using fallback published counts")
    return FALLBACK_COUNTS, FALLBACK_NOTE


def fig_grid_sizes():
    counts, note = load_counts()
    colors = [RED if i < FOCUS else MUTED for i in range(len(counts))]
    focus_total = sum(counts[:FOCUS])
    total = sum(counts)

    fig, ax = plt.subplots(figsize=(9.2, 5.0))
    bars = ax.bar(LABELS, counts, color=colors, width=0.72)
    for bar, c in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, c + max(counts) * 0.015, str(c),
                ha="center", va="bottom", fontsize=11, color=DARK, fontweight="bold")

    ax.set_xlabel("Annual heat delivered  [GWh]", fontsize=12, color=DARK)
    ax.set_ylabel("Number of networks", fontsize=12, color=DARK)
    ax.set_title("Most Swedish district heating grids are small",
                 fontsize=15, color=DARK, fontweight="bold", loc="left", pad=12)
    ax.set_ylim(0, max(counts) * 1.15)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.tick_params(labelsize=11)
    ax.annotate(f"{focus_total} of {total} networks\ndeliver \u2264 "
                f"{SMALL_THRESHOLD_GWH} GWh",
                xy=(1.7, max(counts) * 0.87),
                fontsize=11, color=RED, fontweight="bold", ha="left", va="center")
    fig.text(0.005, 0.005, note, fontsize=8, color=GREY)
    plt.tight_layout(rect=[0, 0.03, 1, 1])

    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / "fig_grid_sizes.png"
    plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[ok  ] {out}  (counts={counts})")
    return out


if __name__ == "__main__":
    fig_grid_sizes()
