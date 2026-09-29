#!/usr/bin/env python3
"""
Generate the QR code for the closing "See for yourself" slide.

Points at the public repo for the talk (slides, open datasets, plotting code,
and the reports behind the claims). Update URL to the real repo before the talk.

    pip install qrcode pillow
    python make_qr.py

Output: figures/qr_repo.png
"""

from pathlib import Path
import qrcode

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE / "figures"

URL = "https://github.com/beacontower/techheads2026"
DARK = "#1E1C1D"


def build():
    qr = qrcode.QRCode(box_size=12, border=2,
                       error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(URL)
    qr.make(fit=True)
    img = qr.make_image(fill_color=DARK, back_color="white")
    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / "qr_repo.png"
    img.save(out)
    print(f"[ok  ] {out}  ->  {URL}")


if __name__ == "__main__":
    build()
