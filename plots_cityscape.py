#!/usr/bin/env python3
"""
Atmospheric dimmed-city dusk background for the closing "The city breathes" slide.

Generates a layered city skyline at dusk — silhouetted buildings with dimmed
warm window lights and fog lifting from the base, dark sky at top for text.
Fully generated (no photo, no licensing issue), tuned to the Glaze deck's mood.
Reproducible via the fixed RNG seed.

    python plots_cityscape.py

Output: figures/fig_cityscape.png   (16:9, dark)
"""

from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mp

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE / "figures"
SEED = 11
W, H = 13.333, 7.5


def build():
    rng = np.random.default_rng(SEED)
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")

    # sky gradient: deep dusk blue -> warm dark grey near horizon
    grad = np.linspace(0, 1, 256).reshape(-1, 1)
    top = np.array([0x10, 0x13, 0x1A]); bot = np.array([0x2A, 0x26, 0x22])
    sky = (top[None, :] * (1 - grad) + bot[None, :] * grad) / 255.0
    sky = np.repeat(sky[:, None, :], 2, axis=1)
    ax.imshow(sky, extent=[0, W, 0, H], aspect="auto", origin="upper", zorder=0)

    def layer(base_y, max_h, color, alpha, lit):
        x = 0
        while x < W:
            bw = rng.uniform(0.5, 1.3)
            bh = rng.uniform(max_h * 0.35, max_h)
            ax.add_patch(mp.Rectangle((x, base_y), bw, bh, color=color, alpha=alpha,
                                      zorder=1, ec="none"))
            if lit:
                nx = max(1, int(bw / 0.16)); ny = max(1, int(bh / 0.22))
                for ix in range(nx):
                    for iy in range(ny):
                        if rng.random() < 0.28:
                            wx = x + 0.06 + ix * 0.16; wy = base_y + 0.08 + iy * 0.22
                            if wx < x + bw - 0.05 and wy < base_y + bh - 0.1:
                                glow = rng.uniform(0.25, 0.6)
                                ax.add_patch(mp.Rectangle((wx, wy), 0.07, 0.11,
                                    color=(1.0, 0.82, 0.45), alpha=glow * alpha,
                                    zorder=2, ec="none"))
            x += bw + rng.uniform(0.03, 0.15)

    layer(1.2, 3.2, (0.22, 0.25, 0.32), 0.45, lit=False)  # far, fog-lightened
    layer(0.7, 3.9, (0.13, 0.14, 0.18), 0.7, lit=True)    # mid
    layer(0.0, 3.2, (0.05, 0.05, 0.07), 0.95, lit=True)   # front, darkest

    for _ in range(60):
        fy = rng.uniform(0.0, 3.6)
        a = max(0, 0.05 * (1 - fy / 3.6))
        ax.add_patch(mp.Rectangle((0, fy), W, rng.uniform(0.15, 0.5),
                     color=(0.75, 0.78, 0.82), alpha=a, zorder=3, ec="none"))
    ax.add_patch(mp.Rectangle((0, 0), W, 1.8, color=(0.6, 0.64, 0.7),
                 alpha=0.10, zorder=3, ec="none"))

    # subtle top vignette for text legibility
    vg = np.zeros((256, 256, 4))
    ys = np.linspace(0, 1, 256)[:, None]
    vg[..., 3] = 0.35 * (1 - ys)
    ax.imshow(vg, extent=[0, W, 0, H], aspect="auto", origin="upper", zorder=4)

    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / "fig_cityscape.png"
    plt.savefig(out, dpi=150, facecolor="#10131A")
    plt.close(fig)
    print(f"[ok  ] {out}")


if __name__ == "__main__":
    build()
