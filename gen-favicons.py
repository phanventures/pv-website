#!/usr/bin/env python3
"""Generate the phanventures.com favicon set.

Phan Ventures has no logo mark; the site is a text wordmark over the pride gradient.
The favicon is that identity at tile scale: the site's 155deg gradient under the same
dark overlay, with a white Inter Black monogram. Rounded corners, transparent outside.

    python3 gen-favicons.py            # writes favicon-16/32.png, apple-touch-icon.png,
                                       # icon-192/512.png, favicon.ico
"""
import math, os, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.expanduser("~/Library/Fonts/Inter.ttf")
STOPS = [(0.00, "#6D28D9"), (0.20, "#1D4ED8"), (0.38, "#0891B2"),
         (0.55, "#059669"), (0.74, "#D97706"), (1.00, "#DC2626")]
ANGLE, OVERLAY, RADIUS = 155, 0.18, 0.22
TEXT = sys.argv[1] if len(sys.argv) > 1 else "PV"

def hexrgb(h): return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))

def gradient(size):
    """CSS linear-gradient(155deg, ...) on a size x size canvas."""
    a = math.radians(ANGLE)
    dx, dy = math.sin(a), -math.cos(a)            # CSS: 0deg = up, clockwise
    half = (abs(size * dx) + abs(size * dy)) / 2  # gradient line half-length
    cx = cy = size / 2
    im = Image.new("RGB", (size, size))
    px = im.load()
    for y in range(size):
        for x in range(size):
            t = (((x - cx) * dx + (y - cy) * dy) / half + 1) / 2
            t = min(1.0, max(0.0, t))
            for (t0, c0), (t1, c1) in zip(STOPS, STOPS[1:]):
                if t <= t1:
                    f = 0 if t1 == t0 else (t - t0) / (t1 - t0)
                    r0, r1 = hexrgb(c0), hexrgb(c1)
                    px[x, y] = tuple(int(r0[i] + (r1[i] - r0[i]) * f) for i in range(3))
                    break
    return im

def tile(size, base):
    im = base.resize((size, size), Image.LANCZOS).convert("RGBA")
    im = Image.alpha_composite(im, Image.new("RGBA", im.size, (0, 0, 0, int(255 * OVERLAY))))
    # monogram: fill ~62% of the tile width, optically centred on cap height
    font = ImageFont.truetype(FONT, size)
    font.set_variation_by_name("Black")
    target = size * (0.62 if len(TEXT) > 1 else 0.50)
    lo, hi = 4, size
    while hi - lo > 1:
        mid = (lo + hi) // 2
        f = ImageFont.truetype(FONT, mid); f.set_variation_by_name("Black")
        l, t, r, b = f.getbbox(TEXT)
        (lo, hi) = (mid, hi) if (r - l) <= target else (lo, mid)
    font = ImageFont.truetype(FONT, lo); font.set_variation_by_name("Black")
    l, t, r, b = font.getbbox(TEXT)
    d = ImageDraw.Draw(im)
    d.text(((size - (r - l)) / 2 - l, (size - (b - t)) / 2 - t), TEXT, font=font, fill=(255, 255, 255, 255))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1], radius=int(size * RADIUS), fill=255)
    im.putalpha(mask)
    return im

if __name__ == "__main__":
    base = gradient(512)
    out = sys.argv[2] if len(sys.argv) > 2 else ROOT
    os.makedirs(out, exist_ok=True)
    for name, px in [("favicon-16.png", 16), ("favicon-32.png", 32),
                     ("apple-touch-icon.png", 180), ("icon-192.png", 192), ("icon-512.png", 512)]:
        tile(px, base).save(os.path.join(out, name))
    tile(256, base).save(os.path.join(out, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
    print(f"favicons written to {out} with monogram {TEXT!r}")
