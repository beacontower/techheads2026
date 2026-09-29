#!/usr/bin/env python3
"""
Fetch Energimarknadsinspektionen's (Ei) open district-heating statistics:
"Levererad värme per prisområde" — sold heat per price area (network) — from
which the Swedish grid-size distribution is built by plots_se.py.

Source (open, no copyright restrictions):
  Ei "Tekniska uppgifter - fjärrvärme", file "Levererad värme per prisområde".
  Catalogued on Sveriges dataportal (DCAT-AP), dataset family 174_*.
  Landing: https://ei.se/om-oss/statistik-och-oppna-data/tekniska-uppgifter---fjarrvarme

Ei's download URLs carry an opaque hash that changes when they republish, so
this script resolves the *current* file URL at runtime via the dataportal
metadata API instead of hardcoding it. If that lookup fails (API shape change,
no network), it prints exactly where to grab the file by hand.

    python get_data_se.py

Puts the .xlsx at  data_se/ei_levererad_varme_per_prisomrade.xlsx
"""

from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
SE_DIR = HERE / "data_se"
OUT_XLSX = SE_DIR / "ei_levererad_varme_per_prisomrade.xlsx"

# dataportal.se search API — find the Ei "levererad värme per prisområde" file.
SEARCH_API = ("https://admin.dataportal.se/store/9/search?"
              "q=levererad+v%C3%A4rme+per+prisomr%C3%A5de&type=dataset&limit=5")
LANDING = "https://ei.se/om-oss/statistik-och-oppna-data/tekniska-uppgifter---fjarrvarme"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def _get(url, binary=False):
    try:
        import requests
        r = requests.get(url, headers={"User-Agent": UA}, timeout=60)
        r.raise_for_status()
        return r.content if binary else r.text
    except ImportError:
        import ssl, urllib.request
        try:
            import certifi
            ctx = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, context=ctx, timeout=60) as r:
            return r.read() if binary else r.read().decode("utf-8", "replace")


def _resolve_xlsx_url() -> str | None:
    """Ask the dataportal API for the current .xlsx accessURL, best effort."""
    try:
        raw = _get(SEARCH_API)
        data = json.loads(raw)
    except Exception as e:
        print(f"[warn] dataportal lookup failed: {e}")
        return None
    # Walk the response for any .xlsx URL whose context mentions 'levererad'.
    hits = []
    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, str) and o.lower().endswith(".xlsx"):
            hits.append(o)
    walk(data)
    for u in hits:
        if "leverer" in u.lower() or "varme" in u.lower() or "prisomr" in u.lower():
            return u
    return hits[0] if hits else None


def _instructions():
    return (
        "Could not resolve the Ei file automatically. Grab it by hand (one file,\n"
        "no login):\n"
        f"  1. Open {LANDING}\n"
        "  2. Download 'Levererad värme per prisområde' (xlsx, ~0.8 MB)\n"
        f"  3. Save it as  {OUT_XLSX}\n"
        "  4. Re-run:  python get_data_se.py   (it will just verify)\n"
        "  (If 'requests' is missing:  pip install requests certifi)")


def download():
    SE_DIR.mkdir(exist_ok=True)
    if OUT_XLSX.exists() and OUT_XLSX.stat().st_size > 100_000:
        print(f"[skip] {OUT_XLSX} already present")
        return
    url = _resolve_xlsx_url()
    if not url:
        sys.exit(_instructions())
    print(f"[get ] {url}")
    try:
        OUT_XLSX.write_bytes(_get(url, binary=True))
    except Exception as e:
        print(f"[warn] download failed: {e}")
        sys.exit(_instructions())
    print(f"[ok  ] saved to {OUT_XLSX}")


if __name__ == "__main__":
    download()
    print("Now run:  python plots_se.py")
