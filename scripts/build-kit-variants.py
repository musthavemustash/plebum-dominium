#!/usr/bin/env python3
"""Build path-variant kit PDFs from the variant site pages (preview + push).

The base kit builder (scripts/build-kit-pdfs.py) renders every PDF from
the full-program base page, so the handouts never reflected the One device or
One key and a passphrase paths. This script renders the same sheets from the variant
pages (docs/handouts/*-easy.html, *-one.html) with the same converter,
so the handouts carry the same copy as the variant pages. It also
builds the One device and One key and a passphrase bundles by concatenating the path's PDFs.

Variant PDFs (from variant pages):
  titanium, checklist, dice, faq, threat-model (One device and One key and a passphrase),
  fire-card (One key and a passphrase only, via scripts/build-fire-card.py --path one),
  single-sig (base page; it is One-key native, no variant exists).

Bundles (path order; the fire card stays a separate file, as in the
full bundle, because it prints at true credit-card size):
  One device: terms, threat-model-easy, checklist-easy, verify, airgap,
    dice-easy, titanium-easy, faq-easy (8 sheets)
  One: terms, threat-model-one, checklist-one, verify, airgap,
    dice-one, titanium-one, faq-one, single-sig (9 sheets)

QR codes in variant PDFs point at the variant pages, not the base
pages, so a scan lands on the path-correct sheet.

Usage:
  /tmp/pdfenv/bin/python scripts/build-kit-variants.py \
      --sourcedir /tmp/handout-build/plebum-dominium/docs \
      --outdir preview-handouts/
  /tmp/pdfenv/bin/python scripts/build-kit-variants.py \
      --outdir kit/   (push-time; then stamp + VERIFY + .b64)

Output is UNSTAMPED. Do NOT stamp previews: stamp-pdfs.py skips its
VERIFY update when any file is already stamped, and a stamped file
re-stamps on the next run. Stamp once, at push time.
"""
import argparse
import importlib.util
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BASE = "https://plebumbtc.io"

# (variant page under docs/, output PDF, converter base slug)
VARIANTS = [
    ("handouts/titanium-easy.html", "09_Titanium-easy.pdf", "titanium"),
    ("handouts/titanium-one.html", "09_Titanium-one.pdf", "titanium"),
    ("handouts/checklist-easy.html", "03_Checklist-easy.pdf", "checklist"),
    ("handouts/checklist-one.html", "03_Checklist-one.pdf", "checklist"),
    ("handouts/dice-easy.html", "06_Dice-easy.pdf", "dice"),
    ("handouts/dice-one.html", "06_Dice-one.pdf", "dice"),
    ("handouts/faq-easy.html", "13_FAQ-easy.pdf", "faq"),
    ("handouts/faq-one.html", "13_FAQ-one.pdf", "faq"),
    ("handouts/threat-model-easy.html", "Before_You_Begin-easy.pdf",
     "threat-model"),
    ("handouts/threat-model-one.html", "Before_You_Begin-one.pdf",
     "threat-model"),
    # Single-sig is One-key native; its base page is already path-correct.
    ("handouts/single-sig.html", "16_Single_Sig.pdf", "single-sig"),
]

# Base sheets rendered unstamped for the bundles (caps match the kit).
BASE_SHEETS = [
    ("handouts/terms.html", "Terms.pdf", "terms", "TERMS"),
    ("handouts/verify.html", "05_Verify.pdf", "verify", "CHECK THE FILES"),
    ("handouts/airgap.html", "04_Airgap.pdf", "airgap", "TWO BOOTS"),
]

EASY_BUNDLE = ["Terms.pdf", "Before_You_Begin-easy.pdf",
               "03_Checklist-easy.pdf", "05_Verify.pdf", "04_Airgap.pdf",
               "06_Dice-easy.pdf", "09_Titanium-easy.pdf", "13_FAQ-easy.pdf"]
ONE_BUNDLE = ["Terms.pdf", "Before_You_Begin-one.pdf",
              "03_Checklist-one.pdf", "05_Verify.pdf", "04_Airgap.pdf",
              "06_Dice-one.pdf", "09_Titanium-one.pdf", "13_FAQ-one.pdf",
              "16_Single_Sig.pdf"]


def load_kit_builder():
    spec = importlib.util.spec_from_file_location(
        "build_kit_pdfs", os.path.join(HERE, "build-kit-pdfs.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_pdf(bk, docsdir, page_rel, outfile, base_slug, caps, outdir):
    from pypdf import PdfReader
    article = bk.parse_article(os.path.join(docsdir, page_rel))
    prev, center, nxt, meta, h1 = bk.extract_furniture(article)
    if caps is None:
        caps = h1.upper()
    page_name = os.path.basename(page_rel)

    def make_story():
        conv = bk.Converter(base_slug)
        body = conv.convert(article)
        story = []
        if center or prev or nxt:
            story.append(bk.bar_flowable(prev, center, nxt))
            story.append(bk.Spacer(1, 9))
        if h1:
            story.append(bk.Paragraph(bk.esc(h1), bk.sTitle))
        mf = bk.meta_flowable(meta)
        if mf is not None:
            story.append(mf)
            story.append(bk.Spacer(1, 7))
        story.extend(body)
        return story

    url = f"{BASE}/handouts/{page_name}"
    path = os.path.join(outdir, outfile)
    doc = bk.SheetDoc(path, caps, url)
    doc._total_pages = 1
    doc.build(make_story())
    total = len(PdfReader(path).pages)
    doc = bk.SheetDoc(path, caps, url)
    doc._total_pages = total
    doc.build(make_story())
    print(f"{page_rel}: {total} pages -> {outfile}")
    return path


def build_bundle(paths, out):
    from pypdf import PdfReader, PdfWriter
    w = PdfWriter()
    for p in paths:
        for page in PdfReader(p).pages:
            w.add_page(page)
    with open(out, "wb") as fh:
        w.write(fh)
    print(f"bundle: {len(PdfReader(out).pages)} pages -> "
          f"{os.path.basename(out)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sourcedir",
                    default=os.path.join(ROOT, "docs"))
    ap.add_argument("--outdir", default=os.path.join(ROOT, "kit"))
    args = ap.parse_args()
    bk = load_kit_builder()
    os.makedirs(args.outdir, exist_ok=True)
    built = {}
    for page_rel, outfile, base_slug in VARIANTS:
        built[outfile] = build_pdf(bk, args.sourcedir, page_rel, outfile,
                                   base_slug, None, args.outdir)
    with tempfile.TemporaryDirectory() as tmp:
        base_paths = {}
        for page_rel, outfile, base_slug, caps in BASE_SHEETS:
            base_paths[outfile] = build_pdf(bk, args.sourcedir, page_rel,
                                            outfile, base_slug, caps, tmp)
        lookup = dict(built)
        lookup.update(base_paths)
        build_bundle([lookup[n] for n in EASY_BUNDLE],
                     os.path.join(args.outdir, "Handouts_No_Cover-easy.pdf"))
        build_bundle([lookup[n] for n in ONE_BUNDLE],
                     os.path.join(args.outdir, "Handouts_No_Cover-one.pdf"))
    print("done.")


if __name__ == "__main__":
    main()
