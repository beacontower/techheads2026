#!/usr/bin/env python3
"""
Prepare the Ecobee "Donate Your Data" indoor-temperature dataset.

Luo & Hong, "Ecobee Donate Your Data 1,000 homes in 2017", LBNL / PNNL BBD.
DOI: 10.25584/ecobee/1854924
Landing: https://www.osti.gov/biblio/1854924  ->  https://bbd.labworks.org/ds/bbd/ecobee

  ~1,000 US single-family homes (CA, TX, NY, IL), full-year 2017,
  5-minute resolution, including INDOOR temperature at the thermostat.

Why a separate, download-assisted script
----------------------------------------
The data sits behind PNNL's Building Data (BBD) portal, which is a JavaScript
app with a data-use agreement — there is no clean direct download URL to script
against. So: grab it once in a browser, drop the archive here, and this script
verifies/extracts it. Everything downstream (plots_ecobee.py) then runs offline.

Steps
-----
1. Open https://bbd.labworks.org/ds/bbd/ecobee  (via https://www.osti.gov/biblio/1854924)
2. Accept the data-use agreement and download the dataset archive.
3. Put the downloaded file here:
       data_ecobee/ecobee_dyd_2017.zip     (a .tar.gz is fine too)
4. Run:  python get_data_ecobee.py         # extracts + sanity-checks
5. Then: python plots_ecobee.py

This keeps provenance honest: it's US thermostat data, used as a general
"indoor temperature is chaotic per home, orderly in aggregate" illustration —
not district heating, and not RACE-specific.
"""

from pathlib import Path
import sys
import tarfile
import zipfile

HERE = Path(__file__).resolve().parent
EC_DIR = HERE / "data_ecobee"
CANDIDATES = ["ecobee_dyd_2017.zip", "ecobee_dyd_2017.tar.gz",
              "ecobee.zip", "ecobee.tar.gz"]
LANDING = "https://www.osti.gov/biblio/1854924"
PORTAL = "https://bbd.labworks.org/ds/bbd/ecobee"


def _find_archive() -> Path | None:
    EC_DIR.mkdir(exist_ok=True)
    for name in CANDIDATES:
        p = EC_DIR / name
        if p.exists() and p.stat().st_size > 1_000_000:
            return p
    # any zip/tar the user dropped in with a different name
    for p in list(EC_DIR.glob("*.zip")) + list(EC_DIR.glob("*.tar.gz")):
        if p.stat().st_size > 1_000_000:
            return p
    return None


def _instructions() -> str:
    return (
        "No Ecobee archive found. This dataset is behind a data-use agreement,\n"
        "so it can't be fetched automatically. Do this once:\n\n"
        f"  1. Open {LANDING}\n"
        f"     (it links to the BBD portal: {PORTAL})\n"
        "  2. Accept the agreement and download the dataset archive.\n"
        f"  3. Save it here:  {EC_DIR / 'ecobee_dyd_2017.zip'}\n"
        "  4. Re-run:  python get_data_ecobee.py\n")


def extract(archive: Path):
    marker = EC_DIR / "_extracted"
    if marker.exists():
        print(f"[skip] already extracted under {EC_DIR}")
        return
    print(f"[extract] {archive.name} -> {EC_DIR}")
    if archive.suffix == ".zip":
        with zipfile.ZipFile(archive) as z:
            z.extractall(EC_DIR)
    else:
        with tarfile.open(archive) as t:
            t.extractall(EC_DIR)
    marker.write_text("ok\n")
    print("[ok  ] extracted")


def report():
    csvs = list(EC_DIR.glob("**/*.csv"))
    print(f"[data] found {len(csvs)} CSV files under {EC_DIR}")
    if csvs:
        # peek at the first data-looking CSV's header
        for p in csvs:
            head = p.read_text(errors="replace").splitlines()[:1]
            if head and ("Thermostat_Temperature" in head[0] or "DateTime" in head[0]):
                print(f"[cols] {p.name}: {head[0][:200]}")
                break


if __name__ == "__main__":
    arch = _find_archive()
    if not arch:
        sys.exit(_instructions())
    extract(arch)
    report()
    print("Now run:  python plots_ecobee.py")
