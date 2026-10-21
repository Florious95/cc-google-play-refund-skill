#!/usr/bin/env python3
"""Generate a FICTIONAL inbox screenshot used by the demo (no real data)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from _common import Image, ImageDraw, load_font  # noqa: E402

ROWS = [
    ("Google Play", "Your Google Play Order Receipt from Jan 5, 2026", "Order GPA.0000-1111-2222-33333 Claude Max ...", "Jan 5", True),
    ("Weekly Deals", "50% off garden furniture this weekend only", "Don't miss out on our biggest sale ...", "Jan 5", False),
    ("Anthropic", "Your account has been suspended", "An internal investigation of suspicious signals ...", "Jan 5", True),
    ("Google Play", "Your Claude by Anthropic subscription will be canceled", "No refunds will be issued (Refund Policy) ...", "Jan 5", True),
    ("Alex (friend)", "Dinner on Friday?", "Hey! Are we still on for Friday at 7 ...", "Jan 6", False),
    ("City Bank", "Your January statement is ready", "Statement for account ending 4242 ...", "Jan 7", False),
    ("Anthropic Support", "Re: Refund request for Google Play order", "we are unable to issue a refund for your subscription ...", "Jan 9", True),
    ("Travel Co", "Your trip itinerary", "Booking reference XY12Z ...", "Jan 9", False),
]


def main(out=os.path.join(HERE, "sample-inbox.png")):
    W, H = 1280, 130 + 56 * len(ROWS) + 40
    img = Image.new("RGB", (W, H), "#f6f8fc")
    d = ImageDraw.Draw(img)
    fb, fr, fs = load_font(17, "bold"), load_font(16), load_font(14)
    # fake browser chrome with address bar + clock
    d.rectangle([0, 0, W, 44], fill="#dee1e6")
    d.rounded_rectangle([90, 8, 980, 36], radius=14, fill="white")
    d.text((110, 14), "https://mail.google.com/mail/u/0/#search/claude", font=fr, fill="#202124")
    d.text((1060, 14), "Mon, Jan 12  09:41 (UTC+8)", font=fs, fill="#202124")
    d.text((24, 54), "Search results  -  jane.doe@example.com (fictional demo account)", font=fb, fill="#202124")
    y = 130
    for sender, subj, snip, date, _rel in ROWS:
        d.rectangle([20, y, W - 20, y + 54], fill="white", outline="#e0e0e0")
        d.text((44, y + 17), sender, font=fb, fill="#202124")
        d.text((250, y + 17), subj, font=fb, fill="#202124")
        sw = d.textlength(subj, font=fb)
        d.text((250 + sw + 12, y + 18), "- " + snip, font=fr, fill="#5f6368")
        d.rectangle([W - 120, y + 2, W - 22, y + 52], fill="white")
        d.text((W - 90, y + 17), date, font=fb, fill="#202124")
        y += 56
    img.save(out)
    print("wrote", out)
    return [(130 + 56 * i, 130 + 56 * i + 54) for i, r in enumerate(ROWS) if not r[4]]


if __name__ == "__main__":
    print("unrelated row bands:", main())
