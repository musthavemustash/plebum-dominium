#!/usr/bin/env python3
"""Build kit/15_Fire_Card.pdf: the wallet-sized recovery card (243 x 153 pt).

The card is the one kit file that must never lead a finder back to the
guide: it carries no QR code and no web address anywhere, including its
stamp footer (scripts/stamp-pdfs.py stamps this file with a domain-free
footer variant). Type sizes and positions are fitted to the published
card's own text geometry (pdftotext -bbox of the original), so a rebuild
matches the card readers already have. Build it unstamped, then stamp:

  /tmp/pdfenv/bin/python scripts/build-fire-card.py
  # then stamp just this file (see stamp-pdfs.py) and refresh VERIFY.md

Needs reportlab (same /tmp/pdfenv venv as the other PDF scripts).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
ROOT = os.path.join(os.path.dirname(__file__), "..")
os.chdir(ROOT)

from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

W, H = 243, 153
BG = HexColor("#14110d")
COPPER = HexColor("#c4a484")
CREAM = HexColor("#efe9dc")
MUTED = HexColor("#9b9384")
X = 14  # left margin


def txt(c, x, y, text, font, size, color, tracking=0):
    """Draw one string with explicit character spacing. Every draw sets the
    spacing (0 by default): the PDF Tc operator otherwise leaks from a
    letterspaced line into everything drawn after it."""
    t = c.beginText(x, y)
    t.setFont(font, size)
    t.setCharSpace(tracking)
    t.setFillColor(color)
    t.textOut(text)
    c.drawText(t)


def borders(c):
    c.setFillColor(BG)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setStrokeColor(COPPER)
    c.setLineWidth(1.2)
    c.roundRect(3, 3, W - 6, H - 6, 6, stroke=1, fill=0)
    c.setLineWidth(0.5)
    c.roundRect(7, 7, W - 14, H - 14, 4, stroke=1, fill=0)


def page1(c):
    borders(c)
    txt(c, X, 129, "PLEBUM DOMINIUM", "Times-Bold", 13, COPPER)
    txt(c, X, 118, "RECOVERY", "Helvetica-Bold", 6.5, MUTED, tracking=1.8)
    c.setStrokeColor(COPPER)
    c.setLineWidth(0.6)
    c.line(X, 108, W - X, 108)
    txt(c, X, 93, "2 plates + wallet map + this card = your bitcoin.",
        "Helvetica-Bold", 8.2, CREAM)
    txt(c, X, 82, "The plates are useless without the map.", "Helvetica", 7.6, CREAM)
    txt(c, X, 72, "The map is useless without two plates.", "Helvetica", 7.6, CREAM)
    txt(c, X, 56, "Derivation path: ", "Courier", 7.2, MUTED)
    from reportlab.pdfbase.pdfmetrics import stringWidth
    w = stringWidth("Derivation path: ", "Courier", 7.2)
    txt(c, X + w, 56, "m/48'/0'/0'/2'", "Courier", 7.2, CREAM)
    txt(c, X, 46, "(not a secret - it is how the wallet is shaped)",
        "Helvetica-Oblique", 6.4, COPPER)
    c.showPage()


def dotted_row(c, y, label, dots_from):
    txt(c, X, y, label, "Helvetica", 8, MUTED)
    c.setStrokeColor(COPPER)
    c.setLineWidth(1.1)
    c.setDash(0.1, 2.4)
    c.setLineCap(1)  # round caps turn the dash pattern into dots
    c.line(dots_from, y - 1, W - X, y - 1)
    c.setDash()
    c.setLineCap(0)


def page2(c):
    borders(c)
    txt(c, X, 131, "WHERE THINGS ARE", "Helvetica-Bold", 6.8, COPPER, tracking=1.9)
    rows = [
        (116, "Plate A:", 50),
        (101, "Plate B:", 50),
        (86, "Plate C:", 50.5),
        (71, "Wallet map:", 64),
        (56, "Passphrase paper:", 89),
    ]
    for y, label, dots_from in rows:
        dotted_row(c, y, label, dots_from)
    txt(c, X, 40, "Full instructions: the inheritance sheet. This card is the map's map.",
        "Helvetica-Oblique", 6.4, MUTED)
    c.showPage()


def main():
    out = "kit/15_Fire_Card.pdf"
    c = canvas.Canvas(out, pagesize=(W, H))
    page1(c)
    page2(c)
    c.save()
    print(f"built {out} (unstamped; stamp it with the domain-free footer)")


if __name__ == "__main__":
    main()
