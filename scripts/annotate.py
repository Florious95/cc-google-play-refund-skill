#!/usr/bin/env python3
"""Add an English exhibit banner and callouts (boxes, arrows, notes) to a screenshot.

The banner is added OUTSIDE the original pixels (the canvas grows), so the
original screenshot content is never covered by the caption.

Examples
--------
  # Banner only
  python3 annotate.py in.png out.png \
      --title "Exhibit 3 - Google Play: subscription cancelled" \
      --caption "Received 2026-01-05 14:07 UTC+8 (06:07 UTC), 52 minutes after the purchase in Exhibit 1."

  # Banner + a highlight box with a label + an arrow
  python3 annotate.py in.png out.png --title "Exhibit 5 - Developer refusal" \
      --box "120,340,980,420:Refusal sentence" \
      --arrow "1100,200,990,380:Date 2026-01-09 10:12 UTC+8"

  # Everything from a JSON spec (see examples/demo-spec.json)
  python3 annotate.py in.png out.png --spec spec.json

Coordinates are pixels of the INPUT image (before the banner is added);
any value may also be a percentage, e.g. "10%,20%,90%,30%".
Use grid.py first if you need to read coordinates off the image.
"""
import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (Image, ImageDraw, load_font, load_spec, parse_box,  # noqa: E402
                     parse_color, parse_coord, save_image, split_label, wrap_text)

DEFAULTS = {
    "banner_bg": "#FFF3B0",
    "banner_fg": "#000000",
    "banner_rule": "#B49600",
    "callout": "#E0201B",
    "position": "top",
}


def build_parser():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="source image (png/jpg/webp)")
    p.add_argument("output", help="output image; extension decides the format")
    p.add_argument("--spec", help="JSON file with any of: title, caption, position, "
                   "boxes[{box,label,label_pos,color}], arrows[{from_to,label,color}], "
                   "notes[{x,y,text,color}], callout, banner_bg, banner_fg. CLI flags override/add to it.")
    p.add_argument("--title", help="bold banner headline, e.g. 'Exhibit 2 - Ban notice'")
    p.add_argument("--caption", action="append", default=[],
                   help="banner body line(s); repeatable. Put exact time + timezone here.")
    p.add_argument("--position", choices=["top", "bottom"], help="banner side (default top)")
    p.add_argument("--box", action="append", default=[], metavar="X1,Y1,X2,Y2[:LABEL]",
                   help="outline a region; optional label drawn above it. Repeatable.")
    p.add_argument("--label-pos", choices=["above", "below"], default="above",
                   help="where --box labels go relative to the box (default above)")
    p.add_argument("--arrow", action="append", default=[], metavar="X1,Y1,X2,Y2[:LABEL]",
                   help="arrow from (x1,y1) to head at (x2,y2); label at the tail. Repeatable.")
    p.add_argument("--note", action="append", default=[], metavar="X,Y:TEXT",
                   help="free text label with a white backing at (x,y). Repeatable.")
    p.add_argument("--color", help="callout colour (default #E0201B)")
    p.add_argument("--banner-bg", help="banner background (default #FFF3B0)")
    p.add_argument("--banner-fg", help="banner text colour (default black)")
    p.add_argument("--font", help="path to a .ttf/.otf font to use for all text")
    p.add_argument("--scale", type=float, default=None,
                   help="text/line scale factor (default: image width / 1200)")
    p.add_argument("--max-width", type=int, default=None,
                   help="downscale output to at most this width in px (keeps aspect)")
    p.add_argument("--quality", type=int, default=92, help="JPEG/WebP quality (default 92)")
    return p


def _merge(args):
    spec = load_spec(args.spec)
    cfg = dict(DEFAULTS)
    cfg.update({k: v for k, v in spec.items() if k in DEFAULTS})
    cfg["title"] = args.title or spec.get("title")
    caps = spec.get("caption", [])
    if isinstance(caps, str):
        caps = [caps]
    cfg["caption"] = list(caps) + list(args.caption)
    if args.position:
        cfg["position"] = args.position
    if args.color:
        cfg["callout"] = args.color
    if args.banner_bg:
        cfg["banner_bg"] = args.banner_bg
    if args.banner_fg:
        cfg["banner_fg"] = args.banner_fg
    boxes = [dict(b) for b in spec.get("boxes", [])]
    for raw in args.box:
        coords, label = split_label(raw)
        boxes.append({"box": coords, "label": label, "label_pos": args.label_pos})
    arrows = [dict(a) for a in spec.get("arrows", [])]
    for raw in args.arrow:
        coords, label = split_label(raw)
        arrows.append({"from_to": coords, "label": label})
    notes = [dict(n) for n in spec.get("notes", [])]
    for raw in args.note:
        coords, text = split_label(raw)
        x, y = coords.split(",")
        notes.append({"x": x, "y": y, "text": text or ""})
    cfg.update(boxes=boxes, arrows=arrows, notes=notes)
    return cfg


def _label(draw, xy, text, font, fg, pad, anchor_above=True, img_size=None):
    """Draw text on an opaque white plate; keeps it inside the image."""
    x, y = xy
    l, t, r, b = draw.textbbox((0, 0), text, font=font)
    tw, th = r - l, b - t
    if anchor_above:
        y = y - th - 2 * pad
    if img_size:
        W, H = img_size
        x = max(0, min(W - tw - 2 * pad, x))
        y = max(0, min(H - th - 2 * pad, y))
    draw.rectangle([x, y, x + tw + 2 * pad, y + th + 2 * pad], fill="white", outline=fg,
                   width=max(1, pad // 3))
    draw.text((x + pad - l, y + pad - t), text, font=font, fill=fg)


def _arrow(draw, p1, p2, color, width):
    draw.line([p1, p2], fill=color, width=width)
    ang = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    head = width * 5
    left = (p2[0] - head * math.cos(ang - math.pi / 7), p2[1] - head * math.sin(ang - math.pi / 7))
    right = (p2[0] - head * math.cos(ang + math.pi / 7), p2[1] - head * math.sin(ang + math.pi / 7))
    draw.polygon([p2, left, right], fill=color)


def annotate(cfg, src, font_path=None, scale=None):
    img = Image.open(src)
    img = img.convert("RGBA" if img.mode in ("RGBA", "LA", "P") else "RGB").convert("RGB")
    W, H = img.size
    s = scale or max(0.5, W / 1200.0)
    color = parse_color(cfg["callout"])
    lw = max(2, int(round(4 * s)))
    pad = max(4, int(round(8 * s)))
    f_label = load_font(22 * s, "bold", font_path)

    draw = ImageDraw.Draw(img)
    for b in cfg["boxes"]:
        x1, y1, x2, y2 = parse_box(b["box"], (W, H))
        draw.rectangle([x1, y1, x2, y2], outline=parse_color(b.get("color"), color), width=lw)
        if b.get("label"):
            below = b.get("label_pos", "above") == "below"
            _label(draw, (x1, (y2 + lw) if below else (y1 - lw)), b["label"], f_label,
                   parse_color(b.get("color"), color), pad, not below, (W, H))
    for a in cfg["arrows"]:
        x1, y1, x2, y2 = [parse_coord(v, W if i % 2 == 0 else H)
                          for i, v in enumerate(str(a["from_to"]).split(","))]
        c = parse_color(a.get("color"), color)
        _arrow(draw, (x1, y1), (x2, y2), c, lw)
        if a.get("label"):
            _label(draw, (x1, y1), a["label"], f_label, c, pad, y2 >= y1, (W, H))
    for n in cfg["notes"]:
        x, y = parse_coord(n["x"], W), parse_coord(n["y"], H)
        _label(draw, (x, y), n["text"], f_label, parse_color(n.get("color"), color), pad, False,
               (W, H))

    if not cfg["title"] and not cfg["caption"]:
        return img

    f_title = load_font(34 * s, "bold", font_path)
    f_cap = load_font(24 * s, "regular", font_path)
    bpad = int(round(22 * s))
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    maxw = W - 2 * bpad
    t_lines = wrap_text(tmp, cfg["title"], f_title, maxw) if cfg["title"] else []
    c_lines = []
    for c in cfg["caption"]:
        c_lines += wrap_text(tmp, c, f_cap, maxw)
    t_lh = int(f_title.size * 1.3) if hasattr(f_title, "size") else 40
    c_lh = int(f_cap.size * 1.4) if hasattr(f_cap, "size") else 30
    gap = int(round(8 * s)) if t_lines and c_lines else 0
    bh = 2 * bpad + t_lh * len(t_lines) + gap + c_lh * len(c_lines)

    out = Image.new("RGB", (W, H + bh), "white")
    top = cfg["position"] == "top"
    by = 0 if top else H
    out.paste(img, (0, bh if top else 0))
    d = ImageDraw.Draw(out)
    d.rectangle([0, by, W, by + bh], fill=parse_color(cfg["banner_bg"]))
    rule_y = by + bh - 1 if top else by
    d.line([0, rule_y, W, rule_y], fill=parse_color(cfg["banner_rule"]), width=max(2, int(3 * s)))
    y = by + bpad
    fg = parse_color(cfg["banner_fg"])
    for line in t_lines:
        d.text((bpad, y), line, font=f_title, fill=fg)
        y += t_lh
    y += gap
    for line in c_lines:
        d.text((bpad, y), line, font=f_cap, fill=(30, 30, 30))
        y += c_lh
    return out


def main(argv=None):
    args = build_parser().parse_args(argv)
    cfg = _merge(args)
    out = annotate(cfg, args.input, args.font, args.scale)
    if args.max_width and out.width > args.max_width:
        ratio = args.max_width / float(out.width)
        out = out.resize((args.max_width, int(out.height * ratio)), Image.LANCZOS)
    save_image(out, args.output, args.quality)
    print("wrote %s (%dx%d, %d bytes)" % (args.output, out.width, out.height,
                                          os.path.getsize(args.output)))


if __name__ == "__main__":
    main()
