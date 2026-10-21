"""Shared helpers for annotate.py, redact.py and grid.py (Python 3.8+, Pillow)."""
import json
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont  # noqa: F401
except ImportError:  # pragma: no cover
    sys.exit("Pillow is required:  python3 -m pip install --user Pillow")

_FONT_CANDIDATES = {
    "regular": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "DejaVuSans.ttf",
        "Arial.ttf",
    ],
    "bold": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "DejaVuSans-Bold.ttf",
        "Arial Bold.ttf",
    ],
}


def load_font(size, weight="regular", path=None):
    """Return a TrueType font of `size` px; fall back gracefully."""
    size = max(8, int(size))
    for cand in ([path] if path else []) + _FONT_CANDIDATES[weight]:
        try:
            return ImageFont.truetype(cand, size)
        except (OSError, IOError):
            continue
    try:  # Pillow >= 10.1 can scale the built-in font
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def parse_color(value, default=(0, 0, 0)):
    """Accept '#rrggbb', '#rrggbbaa', 'r,g,b' or a CSS colour name."""
    if value is None:
        return default
    if isinstance(value, (list, tuple)):
        return tuple(int(v) for v in value)
    value = str(value).strip()
    if "," in value:
        return tuple(int(v) for v in value.split(","))
    from PIL import ImageColor
    return ImageColor.getrgb(value)


def parse_coord(token, total):
    """'120' -> 120 px; '12.5%' -> 12.5 % of `total` px."""
    token = str(token).strip()
    if token.endswith("%"):
        return int(round(float(token[:-1]) / 100.0 * total))
    return int(round(float(token)))


def parse_box(text, size):
    """'x1,y1,x2,y2' (px or %) -> normalised (x1, y1, x2, y2) clamped to image."""
    w, h = size
    if isinstance(text, (list, tuple)):
        parts = list(text)
    else:
        parts = [p for p in str(text).replace(" ", "").split(",") if p != ""]
    if len(parts) != 4:
        raise ValueError("box needs 4 numbers x1,y1,x2,y2, got %r" % (text,))
    x1, x2 = parse_coord(parts[0], w), parse_coord(parts[2], w)
    y1, y2 = parse_coord(parts[1], h), parse_coord(parts[3], h)
    x1, x2 = sorted((max(0, min(w, x1)), max(0, min(w, x2))))
    y1, y2 = sorted((max(0, min(h, y1)), max(0, min(h, y2))))
    return x1, y1, x2, y2


def split_label(arg):
    """'x1,y1,x2,y2:Label text' -> ('x1,y1,x2,y2', 'Label text')."""
    if ":" in arg:
        coords, label = arg.split(":", 1)
        return coords, label.strip() or None
    return arg, None


def load_spec(path):
    if not path:
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save_image(img, out_path, quality=92):
    ext = os.path.splitext(out_path)[1].lower()
    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    if ext in (".jpg", ".jpeg"):
        img.convert("RGB").save(out_path, quality=quality, subsampling=0, optimize=True)
    elif ext == ".webp":
        img.save(out_path, quality=quality)
    else:
        img.save(out_path, optimize=True)
    return out_path


def wrap_text(draw, text, font, max_width):
    """Greedy word wrap by rendered pixel width; keeps explicit newlines."""
    lines = []
    for para in str(text).split("\n"):
        words = para.split(" ")
        cur = ""
        for word in words:
            trial = word if not cur else cur + " " + word
            if draw.textlength(trial, font=font) <= max_width or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines
