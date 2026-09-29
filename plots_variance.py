#!/usr/bin/env python3
"""
Variance-vs-grid-size figures from the Danish smart-heat-meter dataset
(3,021 residential buildings, hourly). Fetch it first with get_data_dk.py.

The point: a single building's heat demand is noisy; pooling many buildings
smooths the *relative* variability. If buildings were independent, the
coefficient of variation of the pooled mean would fall like 1/sqrt(N). Real
buildings share weather, so the curve flattens onto a correlated floor above
the 1/sqrt(N) ideal — which is exactly why big grids are easy to forecast and
small grids are not.

Produces:
  1. fig_variance_vs_n.png    - CoV of pooled demand vs number of buildings,
                               with the 1/sqrt(N) reference line
  2. fig_one_vs_many.png      - a few single-building weeks (jagged) vs the
                               all-building mean (smooth)

Notes on the data
-----------------
Each meter's CSV has a cumulative 'Energi 1 Varmeenergi' (kWh) column and a
clean hourly 'RoundedReadTime'. Hourly demand = hourly difference of the
cumulative counter. Column names are Danish; see COLS below. The loader is
defensive about the exact folder layout inside the zip — it globs for CSVs
under data_dk/ and groups by meter if several meters share one file.
"""

from pathlib import Path
import glob

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ---------------------------------------------------------------- CONFIG ----
RED = "#D91F22"
DARK = "#1E1C1D"
GREY = "#7F7F7F"
GRID = "#E7E6E6"
BLUE = "#1C6DD0"
MUTED = "#BFBFBF"

HERE = Path(__file__).resolve().parent
DK_DIR = HERE / "data_dk"
OUT_DIR = HERE / "figures"

# how many buildings to load (None = all 3,021; loading fewer is much faster
# while you iterate — a few hundred already shows the curve clearly)
MAX_BUILDINGS = 800

# week to show in the one-vs-many plot, and how many single buildings to draw
WEEK_START = "2019-01-14"
WEEK_END = "2019-01-21"
N_SINGLE = 6

# N values at which to evaluate the variance curve
N_GRID = [1, 2, 3, 5, 8, 13, 20, 30, 50, 80, 130, 200, 320, 500, 800]

# Danish column names in the raw CSVs
COL_METER = "MeterID"
COL_ENERGY = "Energi 1 Varmeenergi"   # cumulative heat energy, kWh
COL_TIME = "RoundedReadTime"          # clean hourly timestamp, dd-mm-YYYY HH:MM:SS
# ---------------------------------------------------------------------------


def _load_one_csv(path: str) -> pd.DataFrame:
    use = [COL_METER, COL_ENERGY, COL_TIME]
    df = pd.read_csv(path, usecols=lambda c: c in use, low_memory=False)
    df[COL_TIME] = pd.to_datetime(df[COL_TIME], format="%d-%m-%Y %H:%M:%S",
                                  errors="coerce")
    df = df.dropna(subset=[COL_TIME])
    return df


def load_demand_matrix(max_buildings: int | None = MAX_BUILDINGS) -> pd.DataFrame:
    """Return a wide DataFrame: index = hourly timestamp, columns = meter id,
    values = hourly heat demand (kWh) from the differenced cumulative counter."""
    csvs = sorted(glob.glob(str(DK_DIR / "**" / "*.csv"), recursive=True))
    if not csvs:
        raise SystemExit(f"No CSVs under {DK_DIR}. Run get_data_dk.py first.")

    series = {}
    for path in csvs:
        raw = _load_one_csv(path)
        for mid, g in raw.groupby(COL_METER):
            g = g.sort_values(COL_TIME)
            s = (g.set_index(COL_TIME)[COL_ENERGY]
                   .resample("1h").last())
            demand = s.diff()                       # cumulative -> hourly
            demand = demand[(demand >= 0) & (demand < demand.quantile(0.999) * 5)]
            if demand.notna().sum() > 24 * 30:      # keep meters with >1 month
                series[int(mid)] = demand
            if max_buildings and len(series) >= max_buildings:
                break
        if max_buildings and len(series) >= max_buildings:
            break

    wide = pd.DataFrame(series).sort_index()
    print(f"[data] {wide.shape[1]} buildings, {wide.shape[0]} hourly steps")
    return wide


def fig_variance_vs_n(wide: pd.DataFrame) -> Path:
    """Coefficient of variation of the pooled mean demand vs N buildings."""
    # normalise each building to its own mean so buildings of different sizes
    # are comparable, then the pooled mean is an average of unit-mean series
    norm = wide / wide.mean()
    cols = [c for c in norm.columns]
    rng = np.random.default_rng(42)

    ns, covs = [], []
    for n in N_GRID:
        if n > len(cols):
            break
        # average CoV over several random subsets of size n
        vals = []
        for _ in range(30):
            pick = rng.choice(cols, size=n, replace=False)
            pooled = norm[pick].mean(axis=1).dropna()
            vals.append(pooled.std() / pooled.mean())
        ns.append(n)
        covs.append(np.mean(vals))

    ns = np.array(ns)
    covs = np.array(covs)
    ideal = covs[0] / np.sqrt(ns)      # 1/sqrt(N) anchored at N=1

    fig, ax = plt.subplots(figsize=(8.6, 5.4))
    ax.loglog(ns, covs, "o-", color=RED, lw=2.2, ms=6, label="Actual (shared weather)")
    ax.loglog(ns, ideal, "--", color=BLUE, lw=2.0, label="If independent: 1/\u221aN")
    ax.set_xlabel("Number of buildings pooled", fontsize=12, color=DARK)
    ax.set_ylabel("Relative variability of demand\n(coefficient of variation)",
                  fontsize=12, color=DARK)
    ax.set_title("Bigger grids are smoother \u2014 up to a floor",
                 fontsize=14, color=DARK, fontweight="bold", loc="left", pad=10)
    ax.grid(which="both", color=GRID, lw=0.7)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    ax.legend(frameon=False, fontsize=10)
    fig.text(0.005, 0.005,
             "Hourly heat demand, 3,021 Danish residential buildings (Aalborg). "
             "Schaffer et al. 2022, Zenodo 6563114.",
             fontsize=8, color=GREY)
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / "fig_variance_vs_n.png"
    plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[ok  ] {out}")
    return out


def fig_one_vs_many(wide: pd.DataFrame) -> Path:
    """A few single buildings (jagged) vs the all-building mean (smooth)."""
    w = wide.loc[WEEK_START:WEEK_END]
    norm = w / wide.mean()             # unit-mean so they share a scale

    fig, ax = plt.subplots(figsize=(11, 4.6))
    cols = list(norm.columns)
    for c in cols[:N_SINGLE]:
        ax.plot(norm.index, norm[c], color=MUTED, lw=0.9, alpha=0.9)
    ax.plot([], [], color=MUTED, lw=1.2, label=f"{N_SINGLE} single buildings")
    mean_all = norm.mean(axis=1)
    ax.plot(mean_all.index, mean_all, color=RED, lw=2.6,
            label=f"Mean of {norm.shape[1]} buildings")

    ax.set_ylabel("Heat demand  (\u00d7 own average)", fontsize=12, color=DARK)
    ax.set_title("One building is chaos; the grid is calm",
                 fontsize=15, color=DARK, fontweight="bold", loc="left", pad=12)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %-d"))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.legend(frameon=False, fontsize=10, loc="upper right")
    fig.text(0.005, 0.005,
             "Hourly heat demand, normalised per building. Danish residential "
             "buildings (Aalborg). Schaffer et al. 2022, Zenodo 6563114.",
             fontsize=8, color=GREY)
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / "fig_one_vs_many.png"
    plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[ok  ] {out}")
    return out


def main():
    wide = load_demand_matrix()
    fig_one_vs_many(wide)
    fig_variance_vs_n(wide)
    print("[done] figures in", OUT_DIR)


if __name__ == "__main__":
    main()
