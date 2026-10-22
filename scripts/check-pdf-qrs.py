#!/usr/bin/env python3
"""Build-time QR self-check for the kit PDFs.

Decodes every QR code stamped into the kit PDFs (rendered at 200 dpi with
pdftoppm, decoded with zxing) and checks:
  - every sheet PDF carries a QR on page 1, and it decodes to that sheet's
    own page on plebumbtc.io;
  - every QR anywhere in the kit decodes to a plebumbtc.io URL (no strays);
  - the recovery card (15_Fire_Card.pdf) carries NO QR and never prints the
    site domain in its text, so a found card does not lead back to the guide.

Run after build-kit-pdfs.py and stamp-pdfs.py. Exit code 1 on any failure.
Requires: pdftoppm (poppler), and the pdf venv packages zxing-cpp + numpy.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import zxingcpp
from PIL import Image

KIT = Path(sys.argv[1] if len(sys.argv) > 1 else "kit")
BASE = "https://plebumbtc.io"

# Sheet PDFs whose page-1 QR must point at their own page.
SHEET_URLS = {
    "00_Project_Overview.pdf": f"{BASE}/",
    "03_Checklist.pdf": f"{BASE}/handouts/checklist.html",
    "04_Airgap.pdf": f"{BASE}/handouts/airgap.html",
    "05_Verify.pdf": f"{BASE}/handouts/verify.html",
    "06_Dice.pdf": f"{BASE}/handouts/dice.html",
    "07_Sparrow.pdf": f"{BASE}/handouts/sparrow.html",
    "08_Signing.pdf": f"{BASE}/handouts/signing.html",
    "09_Titanium.pdf": f"{BASE}/handouts/titanium.html",
    "11_Encryption.pdf": f"{BASE}/handouts/encryption.html",
    "12_Inheritance.pdf": f"{BASE}/handouts/inheritance.html",
    "13_FAQ.pdf": f"{BASE}/handouts/faq.html",
    "14_Speaker.pdf": f"{BASE}/handouts/briefing.html",
    "Terms.pdf": f"{BASE}/handouts/terms.html",
}
# PDFs where any QR found must still be a plebumbtc.io URL.
LOOSE_PDFS = ["02_Print_Packet.pdf", "Handouts_No_Cover.pdf", "Presentation_Handouts.pdf"]
NO_QR_PDFS = ["15_Fire_Card.pdf"]


def decode_qrs(pdf: Path) -> list[str]:
    """All QR payloads in the PDF, in page order."""
    found: list[str] = []
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(
            ["pdftoppm", "-png", "-r", "200", str(pdf), str(Path(td) / "p")],
            check=True, capture_output=True,
        )
        for img_path in sorted(Path(td).glob("p-*.png")):
            img = Image.open(img_path).convert("RGB")
            for code in zxingcpp.read_barcodes(np.array(img)):
                found.append(code.text)
    return found


def first_page_qrs(pdf: Path) -> list[str]:
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(
            ["pdftoppm", "-png", "-r", "200", "-f", "1", "-l", "1", str(pdf), str(Path(td) / "p")],
            check=True, capture_output=True,
        )
        found = []
        for img_path in sorted(Path(td).glob("p-*.png")):
            img = Image.open(img_path).convert("RGB")
            found += [c.text for c in zxingcpp.read_barcodes(np.array(img))]
        return found


def pdf_text(pdf: Path) -> str:
    out = subprocess.run(["pdftotext", str(pdf), "-"], check=True, capture_output=True)
    return out.stdout.decode("utf-8", "replace")


def main() -> int:
    failures = []
    for name, want in SHEET_URLS.items():
        pdf = KIT / name
        if not pdf.exists():
            failures.append(f"{name}: missing")
            continue
        first = first_page_qrs(pdf)
        if want not in first:
            failures.append(f"{name}: page 1 QR decodes to {first}, expected {want}")
        for url in decode_qrs(pdf):
            if not url.startswith(BASE + "/") and url != BASE + "/":
                failures.append(f"{name}: stray QR payload {url!r}")
    for name in LOOSE_PDFS:
        pdf = KIT / name
        if not pdf.exists():
            failures.append(f"{name}: missing")
            continue
        for url in decode_qrs(pdf):
            if not url.startswith(BASE):
                failures.append(f"{name}: stray QR payload {url!r}")
    for name in NO_QR_PDFS:
        pdf = KIT / name
        if not pdf.exists():
            failures.append(f"{name}: missing")
            continue
        qrs = decode_qrs(pdf)
        if qrs:
            failures.append(f"{name}: must carry no QR, found {qrs}")
        text = pdf_text(pdf)
        if "plebumbtc.io" in text or "plebumdominium.org" in text:
            failures.append(f"{name}: prints the site domain in its text")
    if failures:
        print("QR SELF-CHECK FAILED:")
        for f in failures:
            print(" -", f)
        return 1
    print(f"QR self-check passed: {len(SHEET_URLS)} sheet QRs verified, "
          f"{len(LOOSE_PDFS)} loose PDFs clean, recovery card has no QR and no domain.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
