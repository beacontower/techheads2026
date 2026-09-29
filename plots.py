#!/usr/bin/env python3
"""
Generate the XAI4HEAT figures for the TechHeads 2026 talk.

Both come from the XAI4HEAT raw SCADA CSV (fetch it first with get_data.py):
  1. fig_realtime_jan.png          - one substation, a winter week (15-min)
  2. fig_heat_vs_outdoor_temp.png  - hourly heat vs outdoor temp + fitted line

The Swedish grid-size distribution lives in plots_se.py (built from Ei open
data); the variance/chaos figures live in plots_variance.py; the domain
schematic in plots_domain.py. Run generate_all.py to do everything at once.

All use the Glaze palette. Tweak the CONFIG block and re-run:  python plots.py

The real-time plot uses a January week so the outdoor temperature shows a
strong natural swing and the substation runs more or less continuously (the
April data was bursty). The scatter drops idle/standby hours (< 100 kW) and
>2.5 sigma outliers, then fits a straight line (colder -> more heat).

Dataset columns, for reference:
  datetime, t_out (outdoor), t_ref (target),
  t1_supply / t1_return (primary flow temps, DH network side),
  t2_supply / t2_return (secondary flow temps, building side),
  energy (cumulative MWh counter), power (delivered kW).
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")            # file output only; drop this line to show windows
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ---------------------------------------------------------------- CONFIG ----
SUBSTATION = "L4"

# Glaze palette + one contrasting colour for the fit line
RED = "#D91F22"
DARK = "#1E1C1D"
GREY = "#7F7F7F"
GRID = "#E7E6E6"
BLUE = "#1C6DD0"     # fit line — deliberately different from the data colour

# real-time window: a continuous winter week with a big outdoor-temp swing
RT_START = "2024-01-08"
RT_END = "2024-01-14"

# scatter: broad winter span for density
SEASON_START = "2023-12-01"
SEASON_END = "2024-03-01"

MIN_POWER_KW = 100      # drop idle / standby hours below this
OUTLIER_SIGMA = 2.5     # drop points this far from the first-pass fit, then refit

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
OUT_DIR = HERE / "figures"
# ---------------------------------------------------------------------------


def load(substation: str = SUBSTATION) -> pd.DataFrame:
    csv = DATA_DIR / f"TPS_Lamela_{substation}.csv"
    if not csv.exists():
        raise SystemExit(f"Missing {csv}. Run:  python get_data.py {substation}")
    df = pd.read_csv(csv)
    df["datetime"] = pd.to_datetime(df["datetime"])
    return df.sort_values("datetime").reset_index(drop=True)


def fig_realtime(df: pd.DataFrame) -> Path:
    """Winter week: heat power vs outdoor temperature, nothing smoothed."""
    w = df[(df["datetime"] >= RT_START) & (df["datetime"] <= RT_END)].copy()

    fig, ax1 = plt.subplots(figsize=(11, 4.6))
    ax1.plot(w["datetime"], w["power"], color=RED, lw=1.1, label="Heat delivered (kW)")
    ax1.fill_between(w["datetime"], 0, w["power"], color=RED, alpha=0.12)
    ax1.set_ylabel("Heat power  [kW]", color=DARK, fontsize=12)
    ax1.tick_params(axis="y", labelcolor=DARK)
    ax1.set_ylim(0, 900)

    ax2 = ax1.twinx()
    ax2.plot(w["datetime"], w["t_out"], color=DARK, lw=1.8, label="Outdoor temp (\u00b0C)")
    ax2.set_ylabel("Outdoor temp  [\u00b0C]", color=DARK, fontsize=12)
    ax2.tick_params(axis="y", labelcolor=DARK)
    ax2.set_ylim(-10, 15)

    ax1.set_title("One building, one sensor \u2014 six days in January",
                  fontsize=15, color=DARK, fontweight="bold", loc="left", pad=12)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %-d"))
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    ax1.spines["top"].set_visible(False)
    ax2.spines["top"].set_visible(False)
    ax1.grid(axis="y", color=GRID, lw=0.8)

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="upper right", frameon=False, fontsize=10)
    fig.text(0.005, 0.005,
             f"Raw SCADA, XAI4HEAT open dataset (Ni\u0161, Serbia), substation "
             f"{SUBSTATION}. Nothing removed or smoothed.",
             fontsize=8, color=GREY)
    plt.tight_layout(rect=[0, 0.03, 1, 1])

    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / "fig_realtime_jan.png"
    plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[ok  ] {out}  ({len(w)} points)")
    return out


def fig_scatter(df: pd.DataFrame) -> Path:
    """Hourly heat vs outdoor temp, filtered, with a fitted line."""
    season = df[(df["datetime"] >= SEASON_START)
                & (df["datetime"] < SEASON_END)].copy().set_index("datetime")
    hourly = season[["power", "t_out"]].resample("1h").mean().dropna()

    d = hourly[hourly["power"] >= MIN_POWER_KW].copy()
    x, y = d["t_out"].values, d["power"].values
    m, b = np.polyfit(x, y, 1)
    resid = y - (m * x + b)
    keep = np.abs(resid) <= OUTLIER_SIGMA * resid.std()
    d = d[keep]
    x, y = d["t_out"].values, d["power"].values
    m, b = np.polyfit(x, y, 1)          # refit on the cleaned set
    print(f"[fit ] power = {m:.1f} * t_out + {b:.1f}  (n={len(d)})")

    fig, ax = plt.subplots(figsize=(8.4, 5.4))
    ax.scatter(x, y, s=12, color=RED, alpha=0.30, edgecolors="none",
               label="Hourly means")
    xs = np.linspace(x.min(), x.max(), 100)
    ax.plot(xs, m * xs + b, color=BLUE, lw=2.6, label=f"Fit: {m:.0f} kW/\u00b0C")

    ax.set_xlabel("Outdoor temperature  [\u00b0C]   (hourly average)",
                  fontsize=12, color=DARK)
    ax.set_ylabel("Heat delivered  [kW]   (hourly average)",
                  fontsize=12, color=DARK)
    ax.set_title("A clear trend emerges from the noise",
                 fontsize=13.5, color=DARK, fontweight="bold", loc="left", pad=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(color=GRID, lw=0.8)
    ax.legend(frameon=False, fontsize=10, loc="upper right")
    fig.text(0.005, 0.005,
             f"Hourly averages, {SEASON_START} to {SEASON_END}. Points below "
             f"{MIN_POWER_KW} kW and >{OUTLIER_SIGMA}\u03c3 outliers removed. "
             f"XAI4HEAT, substation {SUBSTATION}.",
             fontsize=8, color=GREY)
    plt.tight_layout(rect=[0, 0.02, 1, 1])

    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / "fig_heat_vs_outdoor_temp.png"
    plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[ok  ] {out}")
    return out


def main():
    df = load()
    print(f"[data] {len(df)} rows, {df['datetime'].min()} -> {df['datetime'].max()}")
    fig_realtime(df)
    fig_scatter(df)
    print("[done] figures in", OUT_DIR)


if __name__ == "__main__":
    main()
