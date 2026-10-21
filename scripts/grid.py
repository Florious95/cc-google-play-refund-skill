#!/usr/bin/env python3
"""Overlay a labelled pixel grid on a COPY of an image, to read coordinates
for redact.py / annotate.py. Never send the grid image as an exhibit.

  python3 grid.py screenshot.png /tmp/screenshot.grid.png --step 50
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import Image, ImageDraw, load_font, save_image  # noqa: E402


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input")
    p.add_argument("output")
    p.add_argument("--step", type=int, default=50, help="grid spacing in px (default 50)")
    a = p.parse_args(argv)
    img = Image.open(a.input).convert("RGB")
    W, H = img.size
    over = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    f = load_font(max(10, a.step // 4), "bold")
    for x in range(0, W, a.step):
        major = x % (a.step * 2) == 0
        d.line([x, 0, x, H], fill=(255, 0, 255, 140 if major else 70), width=1)
        if major:
            d.text((x + 2, 2), str(x), font=f, fill=(200, 0, 200, 255))
    for y in range(0, H, a.step):
        major = y % (a.step * 2) == 0
        d.line([0, y, W, y], fill=(0, 160, 255, 140 if major else 70), width=1)
        if major:
            d.text((2, y + 2), str(y), font=f, fill=(0, 110, 220, 255))
    out = Image.alpha_composite(img.convert("RGBA"), over).convert("RGB")
    save_image(out, a.output)
    print("wrote %s (%dx%d, step %d)" % (a.output, W, H, a.step))


if __name__ == "__main__":
    main()
