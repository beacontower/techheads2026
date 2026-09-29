#!/usr/bin/env python3
"""
Energy-meter figure for the TechHeads 2026 talk.

Shows the cumulative heat-energy "meter" for one substation over a full season:
it only ever ticks upward, and the slope tracks the season — flat in summer
(hot water only), steep in winter (space heating on). This is the entry point
to the data story: every grid already owns this.

Reconstructed cleanly from delivered power (energy = power x dt), so there's no
data-cleaning tangent — just the honest cumulative. Fetch the data first with
get_data.py.

    python plots_meter.py

Output: figures/fig_energy_meter.png   (Glaze palette)
"""

from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

RED = "#D91F22"; DARK = "#1E1C1D"; GREY = "#7F7F7F"; GRID = "#E7E6E6"

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
OUT_DIR = HERE / "figures"

SUBSTATION = "L4"
SEASON_START = "2023-08-01"
SEASON_END = "2024-04-04"


def build():
    csv = DATA_DIR / f"TPS_Lamela_{SUBSTATION}.csv"
    if not csv.exists():
        raise SystemExit(f"Missing {csv}. Run:  python get_data.py {SUBSTATION}")
    df = pd.read_csv(csv)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime").reset_index(drop=True)
    w = df[(df["datetime"] >= SEASON_START)
           & (df["datetime"] < SEASON_END)][["datetime", "power"]].copy()

    # cumulative energy from power: MWh = kW * h / 1000. Cap dt so a data gap
    # doesn't create a fake jump.
    dt_h = w["datetime"].diff().dt.total_seconds().div(3600).clip(upper=1.0).fillna(0)
    w["cum"] = (w["power"].fillna(0).clip(lower=0) * dt_h).div(1000).cumsum()

    fig, ax = plt.subplots(figsize=(11, 5.0))
    ax.plot(w["datetime"], w["cum"], color=RED, lw=2.4)
    ax.set_ylabel("Cumulative heat delivered  [MWh]", fontsize=12, color=DARK)
    ax.set_title("An energy meter only ticks upward \u2014 steeper when it\u2019s cold",
                 fontsize=15, color=DARK, fontweight="bold", loc="left", pad=12)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    ax.grid(color=GRID, lw=0.8)

    def yat(d):
        return w[w["datetime"] <= d]["cum"].iloc[-1]

    ax.annotate("summer: nearly flat\n(hot water only)",
                xy=(mdates.date2num(pd.Timestamp("2023-09-10")),
                    yat(pd.Timestamp("2023-09-10"))),
                xytext=(mdates.date2num(pd.Timestamp("2023-08-08")), 250),
                fontsize=10.5, color=GREY,
                arrowprops=dict(arrowstyle="->", color=GREY))
    ax.annotate("winter: steep\n(space heating on)",
                xy=(mdates.date2num(pd.Timestamp("2024-01-01")),
                    yat(pd.Timestamp("2024-01-01"))),
                xytext=(mdates.date2num(pd.Timestamp("2023-10-15")), 470),
                fontsize=10.5, color=RED,
                arrowprops=dict(arrowstyle="->", color=RED))
    fig.text(0.005, 0.005,
             "Cumulative heat energy over one season. "
             f"XAI4HEAT open dataset (Ni\u0161, Serbia), substation {SUBSTATION}, "
             "Aug 2023\u2013Apr 2024.",
             fontsize=8, color=GREY)
    plt.tight_layout(rect=[0, 0.03, 1, 1])

    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / "fig_energy_meter.png"
    plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[ok  ] {out}  (final {w['cum'].iloc[-1]:.0f} MWh)")


if __name__ == "__main__":
    build()
