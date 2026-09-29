#!/usr/bin/env python3
"""
Download the XAI4HEAT open district-heating SCADA dataset.

Fetches the raw CSV for one substation into ./data/. Plotting lives in
plots.py — run that to (re)generate the figures once the data is present.

Data source (open, CC BY 4.0):
  Cvetkovic, Zdravkovic, Ignjatovic. "XAI4HEAT SCADA Dataset 2024."
  Mendeley Data, V1 (2024). doi:10.17632/2mwc6x6kwb.1
  Mirror with raw CSVs: https://github.com/xai4heat/xai4heat

Usage:
    python get_data.py            # fetches substation L4 by default
    python get_data.py L8         # or any of L4, L8, L12, L17, L22
"""

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"

RAW_URL = (
    "https://raw.githubusercontent.com/xai4heat/xai4heat/"
    "main/datasets/raw/TPS%20Lamela%20{sub}.csv"
)
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def _fetch(url: str) -> bytes:
    """Fetch bytes, using requests if available, else urllib with certifi.
    Handles the python.org macOS 'CERTIFICATE_VERIFY_FAILED' case."""
    try:
        import requests
        r = requests.get(url, headers={"User-Agent": UA}, timeout=60)
        r.raise_for_status()
        return r.content
    except ImportError:
        import ssl
        import urllib.request
        try:
            import certifi
            ctx = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, context=ctx, timeout=60) as r:
            return r.read()


def download(substation: str = "L4") -> Path:
    DATA_DIR.mkdir(exist_ok=True)
    out = DATA_DIR / f"TPS_Lamela_{substation}.csv"
    if out.exists():
        print(f"[skip] {out} already present")
        return out
    url = RAW_URL.format(sub=substation)
    print(f"[get ] {url}")
    try:
        out.write_bytes(_fetch(url))
    except Exception as e:
        raise SystemExit(
            f"Download failed: {e}\n"
            "If this is an SSL certificate error on macOS python.org Python, run:\n"
            "  /Applications/Python\\ 3.14/Install\\ Certificates.command\n"
            "or:  pip install requests certifi")
    print(f"[ok  ] saved to {out}")
    return out


if __name__ == "__main__":
    sub = sys.argv[1] if len(sys.argv) > 1 else "L4"
    download(sub)
    print("Now run:  python plots.py")
