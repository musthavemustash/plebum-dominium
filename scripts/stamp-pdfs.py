#!/usr/bin/env python3
"""Stamp every kit PDF with a version + build-date + content-hash footer,
and regenerate the handout-PDF fingerprint table in kit/VERIFY.md.

The printed "Content SHA-256" is the SHA-256 of the PDF *before* stamping
the content itself. VERIFY.md lists both that content hash and the hash
of the stamped file exactly as published, so a paper copy (via its printed
content hash) and a downloaded file (via its file hash) can each be checked.

Also refreshes the base64 snapshots in kit-b64/kit/ (the decode workflow
serves those), including VERIFY.md.b64.

Needs reportlab + pypdf:
  python3 -m venv /tmp/pdfenv && /tmp/pdfenv/bin/pip install reportlab pypdf
  /tmp/pdfenv/bin/python scripts/stamp-pdfs.py

Re-run safety: a PDF whose first page already carries a stamp is skipped.
To re-stamp after a content rebuild, run this on the fresh unstamped PDFs
(the normal build order is: rebuild PDFs -> stamp -> build.py -> push).
"""
import base64
import hashlib
import io
import os
import re
import sys
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
ROOT = os.path.join(os.path.dirname(__file__), "..")
os.chdir(ROOT)

from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter

TODAY = date.today()
VERSION = TODAY.strftime("%Y.%m.%d")
BUILT_LONG = TODAY.strftime("%B %d, %Y")
BUILT_SHORT = TODAY.strftime("%b %d, %Y")
INK = HexColor("#6f6a5f")

BEGIN = "<!-- BEGIN GENERATED: PDF FINGERPRINTS (scripts/stamp-pdfs.py) -->"
END = "<!-- END GENERATED: PDF FINGERPRINTS -->"


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def overlay_pdf(width, height, content_hash):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(width, height))
    c.setFillColor(INK)
    if width >= 400:
        c.setFont("Helvetica", 6.5)
        c.drawCentredString(
            width / 2, 20,
            f"Plebum Dominium \u00b7 plebumbtc.io \u00b7 Version {VERSION} \u00b7 Built {BUILT_LONG}")
        c.setFont("Courier", 6)
        c.drawCentredString(width / 2, 10.5, f"Content SHA-256: {content_hash}")
    else:
        c.setFont("Helvetica", 5.5)
        c.drawCentredString(
            width / 2, 17,
            f"plebumbtc.io \u00b7 Version {VERSION} \u00b7 Built {BUILT_SHORT}")
        c.setFont("Courier", 5)
        c.drawCentredString(width / 2, 10, f"SHA-256 {content_hash}")
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


def stamp(path):
    with open(path, "rb") as f:
        raw = f.read()
    content_hash = sha256_bytes(raw)
    reader = PdfReader(io.BytesIO(raw))
    first_text = reader.pages[0].extract_text() or ""
    if "Content SHA-256:" in first_text or f"Version {VERSION}" in first_text:
        return None  # already stamped
    overlays = {}
    writer = PdfWriter()
    for page in reader.pages:
        w = float(page.mediabox.width)
        h = float(page.mediabox.height)
        key = (round(w), round(h))
        if key not in overlays:
            overlays[key] = overlay_pdf(w, h, content_hash)
        page.merge_page(overlays[key])
        added = writer.add_page(page)
        # merge_page leaves the merged stream uncompressed; recompress per
        # page via the writer's own page object (pypdf 6 API; there is no
        # writer-level call; a missing method must fail loudly, it
        # silently bloated every stamp once)
        added.compress_content_streams(level=9)
    writer.compress_identical_objects()
    out = io.BytesIO()
    writer.write(out)
    stamped = out.getvalue()
    with open(path, "wb") as f:
        f.write(stamped)
    return {
        "file": os.path.basename(path),
        "version": VERSION,
        "file_hash": sha256_bytes(stamped),
        "content_hash": content_hash,
    }


def refresh_b64(name):
    src = os.path.join("kit", name)
    dst = os.path.join("kit-b64", "kit", name + ".b64")
    with open(src, "rb") as f:
        data = f.read()
    with open(dst, "wb") as f:
        f.write(base64.encodebytes(data))


def update_verify(rows):
    path = "kit/VERIFY.md"
    with open(path) as f:
        text = f.read()
    lines = [
        BEGIN,
        "",
        "## Handout PDF fingerprints",
        "",
        "Every downloadable handout is stamped in its footer with its version,",
        "build date, and a Content SHA-256: the hash of the handout's content",
        "before the footer was stamped on. Match the number printed on a paper",
        "copy to the Content SHA-256 below to confirm the copy is the handout as",
        "published. The File SHA-256 is the hash of the PDF file itself, exactly",
        "as served:",
        "",
        "| File | Version | File SHA-256 | Content SHA-256 |",
        "| --- | --- | --- | --- |",
    ]
    for r in sorted(rows, key=lambda r: r["file"]):
        lines.append(
            f"| {r['file']} | {r['version']} | `{r['file_hash']}` | `{r['content_hash']}` |")
    lines += ["", END]
    block = "\n".join(lines)
    if BEGIN in text:
        text = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END),
                      lambda m: block, text, flags=re.S)
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    with open(path, "w") as f:
        f.write(text)


def main():
    pdfs = sorted(f for f in os.listdir("kit") if f.endswith(".pdf"))
    rows, skipped = [], []
    for name in pdfs:
        r = stamp(os.path.join("kit", name))
        if r is None:
            skipped.append(name)
            # keep any existing VERIFY row by re-reading the stamped file's
            # footer hash is not possible; report instead
            print(f"  SKIP (already stamped): {name}")
        else:
            rows.append(r)
            refresh_b64(name)
            print(f"  stamped {name}: content {r['content_hash'][:12]}…")
    if rows:
        # Merge with rows for skipped files is not attempted: if some files
        # were skipped, leave VERIFY's PDF table untouched and say so.
        if skipped:
            print("Some PDFs were already stamped; VERIFY PDF table NOT updated.")
        else:
            update_verify(rows)
            refresh_b64("VERIFY.md")
            print("  kit/VERIFY.md (PDF fingerprints) + b64 snapshots refreshed")
    print(f"done: {len(rows)} stamped, {len(skipped)} skipped")


if __name__ == "__main__":
    main()
