#!/usr/bin/env python3
"""
Fetch the Danish smart-heat-meter dataset (3,021 residential buildings, hourly).

Schaffer et al., "Three years of hourly data from 3021 smart heat meters
installed in Danish residential buildings", Nature Scientific Data (2022).
Zenodo: https://doi.org/10.5281/zenodo.6563114  (CC BY 4.0)

The download is a single ~3.3 GB zip. This script streams it to ./data_dk/
and unzips it. Run once; it skips if already present.

    python get_data_dk.py

Zenodo sometimes 403s plain urllib requests, so this uses `requests` with a
browser User-Agent when available, tries both URL forms, and supports resume.
If you'd rather just grab it by hand, download this file in a browser and drop
it at data_dk/denmark_smart_heat_meters.zip, then re-run to unzip:
  https://zenodo.org/records/6563114
"""

from pathlib import Path
import zipfile

HERE = Path(__file__).resolve().parent
DK_DIR = HERE / "data_dk"
ZIP_PATH = DK_DIR / "denmark_smart_heat_meters.zip"
FILE_KEY = "3_years_3021_smart_heat_meters_residential_denmark.zip"
EXPECTED_BYTES = 3_270_000_000     # ~3.27 GB; used only as a sanity floor

# Zenodo serves these two forms; the /records/ one is usually more permissive.
URLS = [
    f"https://zenodo.org/records/6563114/files/{FILE_KEY}?download=1",
    f"https://zenodo.org/api/records/6563114/files/{FILE_KEY}/content",
]
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def _ssl_ctx():
    import ssl
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def _download_requests(url: str, resume_from: int) -> bool:
    import requests
    headers = {"User-Agent": UA}
    if resume_from:
        headers["Range"] = f"bytes={resume_from}-"
    with requests.get(url, headers=headers, stream=True, timeout=60,
                      allow_redirects=True) as r:
        if r.status_code not in (200, 206):
            print(f"       [{r.status_code}] {url}")
            return False
        total = int(r.headers.get("Content-Length", 0)) + resume_from
        mode = "ab" if resume_from and r.status_code == 206 else "wb"
        got = resume_from if mode == "ab" else 0
        with open(ZIP_PATH, mode) as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
                got += len(chunk)
                if total:
                    print(f"\r       {got/1e9:5.2f} / {total/1e9:5.2f} GB", end="")
        print()
        return ZIP_PATH.stat().st_size >= EXPECTED_BYTES


def _download_urllib(url: str) -> bool:
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, context=_ssl_ctx(), timeout=60) as r, \
            open(ZIP_PATH, "wb") as f:
        total = int(r.headers.get("Content-Length", 0)); got = 0
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk); got += len(chunk)
            if total:
                print(f"\r       {got/1e9:5.2f} / {total/1e9:5.2f} GB", end="")
    print()
    return ZIP_PATH.stat().st_size >= EXPECTED_BYTES


def download():
    DK_DIR.mkdir(exist_ok=True)
    if ZIP_PATH.exists() and ZIP_PATH.stat().st_size >= EXPECTED_BYTES:
        print(f"[skip] {ZIP_PATH} already present")
        return

    resume_from = ZIP_PATH.stat().st_size if ZIP_PATH.exists() else 0
    have_requests = False
    try:
        import requests  # noqa: F401
        have_requests = True
    except Exception:
        pass

    for url in URLS:
        print(f"[get ] {url}\n       (~3.3 GB, this will take a while)")
        try:
            ok = (_download_requests(url, resume_from) if have_requests
                  else _download_urllib(url))
            if ok:
                print(f"[ok  ] saved to {ZIP_PATH}")
                return
        except Exception as e:
            print(f"       failed: {e}")
        resume_from = 0  # don't resume across a different URL

    raise SystemExit(
        "Could not download automatically (Zenodo may be blocking or rate-"
        "limiting). Download it in a browser and place it here:\n"
        f"  {ZIP_PATH}\nfrom  https://zenodo.org/records/6563114\n"
        "then re-run this script to unzip.\n"
        "(If 'requests' is missing:  pip install requests certifi)")


def unzip():
    marker = DK_DIR / "01_Data"
    if marker.exists():
        print(f"[skip] already extracted to {marker}")
        return
    print(f"[unzip] {ZIP_PATH} -> {DK_DIR}")
    with zipfile.ZipFile(ZIP_PATH) as z:
        z.extractall(DK_DIR)
    print("[ok  ] extracted")


if __name__ == "__main__":
    download()
    unzip()
    print("Now run:  python plots_variance.py")
