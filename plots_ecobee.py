#!/usr/bin/env python3
"""
Indoor-temperature figures from the Ecobee "Donate Your Data" dataset
(~1,000 US single-family homes, 2017, 5-minute). Prepare it first with
get_data_ecobee.py (download-assisted; behind a data-use agreement).

The point (a "how to think about energy" building block): indoor temperature
in one home is chaotic — setbacks, manual overrides, occupancy, solar gain —
but averaged across many homes it settles into a calm, orderly signal. Same
lesson as the heat-demand variance plots, on the comfort side of the meter.

Honest framing for the talk: this is US thermostat data, not district heating.
Use it as a general domain-understanding illustration, not a RACE result.

Produces:
  1. fig_ecobee_one_vs_many.png   - a few single homes (jagged) vs the mean
  2. fig_ecobee_variance_vs_n.png - CoV of pooled indoor temp vs N homes

Data schema (per-home CSV, Ecobee DYD):
  DateTime, Thermostat_Temperature (indoor, deg F), T_ctrl, T_stp_heat,
  T_stp_cool, T_out (outdoor, deg F), plus runtime columns. Column names can
  vary slightly between DYD exports, so the loader matches them flexibly.
  The dataset is in Fahrenheit; everything here is converted to Celsius.
"""

from pathlib import Path
import glob
import re

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
EC_DIR = HERE / "data_ecobee"
OUT_DIR = HERE / "figures"

MAX_HOMES = 400            # None = all; fewer is faster while iterating
WEEK_START = "2017-01-09"  # a winter week
WEEK_END = "2017-01-16"
N_SINGLE = 6
N_GRID = [1, 2, 3, 5, 8, 13, 20, 30, 50, 80, 130, 200, 320, 400]

# flexible column matching (DYD exports vary a little)
TIME_PAT = re.compile(r"date", re.I)
INDOOR_PAT = re.compile(r"(thermostat_temperature|indoor|^t_ctrl$|zone.*temp)", re.I)
# ---------------------------------------------------------------------------


def _f_to_c(x):
    return (x - 32.0) * 5.0 / 9.0


def _pick_col(cols, pat):
    for c in cols:
        if pat.search(c):
            return c
    return None


def load_indoor_matrix(max_homes=MAX_HOMES) -> pd.DataFrame:
    """Wide DataFrame: index = 5-min (resampled hourly) timestamp,
    columns = home id, values = indoor temperature in Celsius."""
    csvs = sorted(glob.glob(str(EC_DIR / "**" / "*.csv"), recursive=True))
    if not csvs:
        raise SystemExit(f"No CSVs under {EC_DIR}. Run get_data_ecobee.py first.")

    series = {}
    for path in csvs:
        try:
            df = pd.read_csv(path, low_memory=False)
        except Exception:
            continue
        tcol = _pick_col(df.columns, TIME_PAT)
        icol = _pick_col(df.columns, INDOOR_PAT)
        if not tcol or not icol:
            continue
        t = pd.to_datetime(df[tcol], errors="coerce")
        v = pd.to_numeric(df[icol], errors="coerce")
        s = pd.Series(_f_to_c(v).values, index=t).dropna()
        if len(s) < 24 * 30:            # need >~1 month of data
            continue
        s = s.resample("1h").mean()     # calm the 5-min noise a touch to hourly
        home_id = Path(path).stem
        series[home_id] = s
        if max_homes and len(series) >= max_homes:
            break

    wide = pd.DataFrame(series).sort_index()
    print(f"[data] {wide.shape[1]} homes, {wide.shape[0]} hourly steps")
    return wide


def fig_one_vs_many(wide: pd.DataFrame) -> Path:
    w = wide.loc[WEEK_START:WEEK_END]

    fig, ax = plt.subplots(figsize=(11, 4.6))
    for c in list(w.columns)[:N_SINGLE]:
        ax.plot(w.index, w[c], color=MUTED, lw=0.9, alpha=0.9)
    ax.plot([], [], color=MUTED, lw=1.2, label=f"{N_SINGLE} single homes")
    mean_all = w.mean(axis=1)
    ax.plot(mean_all.index, mean_all, color=RED, lw=2.6,
            label=f"Mean of {w.shape[1]} homes")

    ax.set_ylabel("Indoor temperature  [\u00b0C]", fontsize=12, color=DARK)
    ax.set_title("One home swings; the crowd holds steady",
                 fontsize=15, color=DARK, fontweight="bold", loc="left", pad=12)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %-d"))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.legend(frameon=False, fontsize=10, loc="upper right")
    fig.text(0.005, 0.005,
             "Indoor temperature, hourly. Ecobee Donate Your Data, ~1,000 US "
             "homes, 2017. Luo & Hong, OSTI 1854924.",
             fontsize=8, color=GREY)
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / "fig_ecobee_one_vs_many.png"
    plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[ok  ] {out}")
    return out


def fig_variance_vs_n(wide: pd.DataFrame) -> Path:
    # for temperature, absolute spread (std in degrees) is the natural measure
    cols = list(wide.columns)
    rng = np.random.default_rng(42)
    ns, stds = [], []
    for n in N_GRID:
        if n > len(cols):
            break
        vals = []
        for _ in range(30):
            pick = rng.choice(cols, size=n, replace=False)
            pooled = wide[pick].mean(axis=1).dropna()
            vals.append(pooled.std())
        ns.append(n)
        stds.append(np.mean(vals))
    ns = np.array(ns); stds = np.array(stds)
    ideal = stds[0] / np.sqrt(ns)

    fig, ax = plt.subplots(figsize=(8.6, 5.4))
    ax.loglog(ns, stds, "o-", color=RED, lw=2.2, ms=6, label="Actual (shared weather)")
    ax.loglog(ns, ideal, "--", color=BLUE, lw=2.0, label="If independent: 1/\u221aN")
    ax.set_xlabel("Number of homes pooled", fontsize=12, color=DARK)
    ax.set_ylabel("Spread of indoor temperature  [\u00b0C]", fontsize=12, color=DARK)
    ax.set_title("Averaging calms the crowd \u2014 up to a floor",
                 fontsize=14, color=DARK, fontweight="bold", loc="left", pad=10)
    ax.grid(which="both", color=GRID, lw=0.7)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    ax.legend(frameon=False, fontsize=10)
    fig.text(0.005, 0.005,
             "Indoor temperature, hourly. Ecobee Donate Your Data, ~1,000 US "
             "homes, 2017. Luo & Hong, OSTI 1854924.",
             fontsize=8, color=GREY)
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / "fig_ecobee_variance_vs_n.png"
    plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[ok  ] {out}")
    return out


def main():
    wide = load_indoor_matrix()
    fig_one_vs_many(wide)
    fig_variance_vs_n(wide)
    print("[done] figures in", OUT_DIR)


if __name__ == "__main__":
    main()
