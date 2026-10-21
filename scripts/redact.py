#!/usr/bin/env python3
"""Irreversibly black out, blur or pixelate regions of a screenshot.

Use it for: inbox rows unrelated to the case, card numbers, full e-mail
addresses, phone numbers, other people's names, avatars, tokens, etc.

Examples
--------
  # Two rectangles, solid black (default)
  python3 redact.py in.png out.png --rect 40,210,1180,262 --rect 40,262,1180,314

  # Whole-width rows (handy for inbox lists): y1,y2 pairs
  python3 redact.py inbox.png inbox-redacted.png --band 300,352 --band 404,456

  # Pixelate instead of black, with a small label on each box
  python3 redact.py in.png out.png --rect 10%,40%,60%,45% --mode pixelate --label "redacted"

  # Automatic: OCR the image and black out every match of a regex
  # (needs `pip install pytesseract` + the tesseract binary; optional)
  python3 redact.py in.png out.png --ocr "\\b\\d{4}\\b" --ocr "[\\w.+-]+@[\\w-]+\\.[\\w.]+"

  # From a JSON spec: {"mode": "black", "rects": ["x1,y1,x2,y2", ...], "bands": ["y1,y2"]}
  python3 redact.py in.png out.png --spec redact.json

Coordinates are pixels (or percentages such as "12.5%") of the input image.
Black is the safest mode: blur/pixelate of small text can sometimes be reversed.
The output is always re-encoded from pixels, so no hidden original data remains
inside the image file (EXIF/metadata is dropped as well).
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (Image, ImageDraw, load_font, load_spec, parse_box,  # noqa: E402
                     parse_color, parse_coord, save_image)

try:
    from PIL import ImageFilter
except ImportError:  # pragma: no cover
    ImageFilter = None


def build_parser():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input")
    p.add_argument("output")
    p.add_argument("--spec", help="JSON with keys: mode, color, pad, label, rects[], bands[], ocr[]")
    p.add_argument("--rect", action="append", default=[], metavar="X1,Y1,X2,Y2",
                   help="rectangle to redact. Repeatable.")
    p.add_argument("--band", action="append", default=[], metavar="Y1,Y2",
                   help="full-width horizontal strip to redact (e.g. one inbox row). Repeatable.")
    p.add_argument("--band-x", default=None, metavar="X1,X2",
                   help="limit every --band to this horizontal span (e.g. skip a sidebar)")
    p.add_argument("--ocr", action="append", default=[], metavar="REGEX",
                   help="redact every OCR word/line matching REGEX (optional dependency)")
    p.add_argument("--mode", choices=["black", "fill", "blur", "pixelate"], default=None,
                   help="black (default), fill (use --color), blur, pixelate")
    p.add_argument("--color", default=None, help="fill colour for --mode fill (e.g. '#d0d0d0')")
    p.add_argument("--pad", type=int, default=None, help="grow every region by N px (default 2)")
    p.add_argument("--label", default=None, help="small text drawn on each redaction, e.g. 'redacted'")
    p.add_argument("--quality", type=int, default=92)
    return p


def _ocr_boxes(img, patterns):
    try:
        import pytesseract
    except ImportError:
        sys.exit("--ocr needs: python3 -m pip install --user pytesseract (and the tesseract binary)")
    data = pytesseract.image_to_data(img.convert("L"), output_type=pytesseract.Output.DICT)
    regs = [re.compile(p) for p in patterns]
    boxes = []
    # word level
    words = []
    for i, txt in enumerate(data["text"]):
        if not txt.strip():
            continue
        words.append((data["block_num"][i], data["par_num"][i], data["line_num"][i], txt,
                      data["left"][i], data["top"][i], data["width"][i], data["height"][i]))
        if any(r.search(txt) for r in regs):
            boxes.append((data["left"][i], data["top"][i],
                          data["left"][i] + data["width"][i], data["top"][i] + data["height"][i]))
    # line level (catches matches that span several words)
    lines = {}
    for b, pa, ln, txt, l, t, w, h in words:
        lines.setdefault((b, pa, ln), []).append((txt, l, t, w, h))
    for items in lines.values():
        text = " ".join(i[0] for i in items)
        for r in regs:
            for m in r.finditer(text):
                pos, hit = 0, []
                for txt, l, t, w, h in items:
                    start, end = pos, pos + len(txt)
                    if start < m.end() and end > m.start():
                        hit.append((l, t, l + w, t + h))
                    pos = end + 1
                if hit:
                    boxes.append((min(h[0] for h in hit), min(h[1] for h in hit),
                                  max(h[2] for h in hit), max(h[3] for h in hit)))
    return boxes


def redact(img, regions, mode="black", color=None, pad=2, label=None):
    img = img.convert("RGB")
    W, H = img.size
    draw = ImageDraw.Draw(img)
    fill = parse_color(color, (0, 0, 0)) if mode == "fill" else (0, 0, 0)
    for (x1, y1, x2, y2) in regions:
        x1, y1 = max(0, x1 - pad), max(0, y1 - pad)
        x2, y2 = min(W, x2 + pad), min(H, y2 + pad)
        if x2 <= x1 or y2 <= y1:
            continue
        if mode in ("black", "fill"):
            draw.rectangle([x1, y1, x2 - 1, y2 - 1], fill=fill)
        else:
            crop = img.crop((x1, y1, x2, y2))
            if mode == "pixelate":
                bw, bh = max(1, (x2 - x1) // 16), max(1, (y2 - y1) // 16)
                crop = crop.resize((bw, bh), Image.BILINEAR).resize((x2 - x1, y2 - y1), Image.NEAREST)
            else:
                crop = crop.filter(ImageFilter.GaussianBlur(radius=max(8, (y2 - y1) // 2)))
            img.paste(crop, (x1, y1))
        if label:
            f = load_font(max(10, min(22, (y2 - y1) * 0.5)), "bold")
            l, t, r, b = draw.textbbox((0, 0), label, font=f)
            if r - l < x2 - x1 and b - t < y2 - y1:
                tx = x1 + ((x2 - x1) - (r - l)) // 2 - l
                ty = y1 + ((y2 - y1) - (b - t)) // 2 - t
                draw.text((tx, ty), label, font=f,
                          fill=(255, 255, 255) if mode in ("black",) else (0, 0, 0))
    return img


def main(argv=None):
    args = build_parser().parse_args(argv)
    spec = load_spec(args.spec)
    src = Image.open(args.input)
    src.load()
    W, H = src.size
    mode = args.mode or spec.get("mode", "black")
    pad = args.pad if args.pad is not None else int(spec.get("pad", 2))
    label = args.label if args.label is not None else spec.get("label")
    color = args.color or spec.get("color")

    regions = []
    for r in list(spec.get("rects", [])) + args.rect:
        regions.append(parse_box(r, (W, H)))
    band_x = args.band_x or spec.get("band_x")
    bx1, bx2 = 0, W
    if band_x:
        a, b = str(band_x).split(",")
        bx1, bx2 = parse_coord(a, W), parse_coord(b, W)
    for band in list(spec.get("bands", [])) + args.band:
        y1, y2 = [parse_coord(v, H) for v in str(band).split(",")]
        regions.append((bx1, min(y1, y2), bx2, max(y1, y2)))
    patterns = list(spec.get("ocr", [])) + args.ocr
    if patterns:
        found = _ocr_boxes(src, patterns)
        found = sorted(set(found))
        print("ocr: %d region(s) matched" % len(found))
        regions += found
    if not regions:
        sys.exit("nothing to redact: give --rect, --band, --ocr or --spec")

    out = redact(src, regions, mode=mode, color=color, pad=pad, label=label)
    save_image(out, args.output, args.quality)
    print("wrote %s: %d region(s) redacted with mode=%s" % (args.output, len(regions), mode))
    for r in regions:
        print("  region x1=%d y1=%d x2=%d y2=%d" % r)


if __name__ == "__main__":
    main()
