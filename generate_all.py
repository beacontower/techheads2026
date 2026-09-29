#!/usr/bin/env python3
"""
Download everything obtainable and generate every figure for the talk.

Runs the fetchers, then the plot scripts, in order. Each step is isolated: if
one dataset can't be fetched (e.g. Ecobee is behind a data-use agreement and
must be downloaded by hand), the rest still run. A summary at the end says what
was produced and what was skipped.

    python generate_all.py

Prerequisites:  pip install pandas matplotlib openpyxl requests certifi
"""

from pathlib import Path
import runpy
import sys
import traceback

HERE = Path(__file__).resolve().parent
FIGS = HERE / "figures"

# (label, module, kind)  kind: "fetch" or "plot"
STEPS = [
    ("XAI4HEAT download", "get_data", "fetch"),
    ("XAI4HEAT figures (real-time + scatter)", "plots", "plot"),
    ("Energy-meter figure", "plots_meter", "plot"),
    ("Swedish Ei download", "get_data_se", "fetch"),
    ("Swedish grid-size distribution", "plots_se", "plot"),
    ("National-impact comparison", "plots_impact", "plot"),
    ("Brute-force optimization visual", "plots_optimization", "plot"),
    ("Danish smart-meter download", "get_data_dk", "fetch"),
    ("Danish variance + chaos figures", "plots_variance", "plot"),
    ("Ecobee prepare (manual download)", "get_data_ecobee", "fetch"),
    ("Ecobee indoor-temp figures", "plots_ecobee", "plot"),
    ("Problem-domain schematic", "plots_domain", "plot"),
]


def run(module: str):
    runpy.run_path(str(HERE / f"{module}.py"), run_name="__main__")


def main():
    done, skipped = [], []
    for label, module, kind in STEPS:
        print(f"\n=== {label}  ({module}.py) ===")
        try:
            run(module)
            done.append(label)
        except SystemExit as e:
            # fetchers exit with a message when a manual download is needed
            print(f"[skip] {label}: {e}")
            skipped.append(label)
        except Exception:
            print(f"[skip] {label}: unexpected error")
            traceback.print_exc()
            skipped.append(label)

    print("\n" + "=" * 60)
    print("Done. Figures in", FIGS)
    if FIGS.exists():
        for p in sorted(FIGS.glob("*.png")):
            print("  ", p.name)
    if skipped:
        print("\nSkipped (data not available / needs manual step):")
        for s in skipped:
            print("  -", s)
        print("\nEcobee must be downloaded by hand — see get_data_ecobee.py.")


if __name__ == "__main__":
    main()
