#!/usr/bin/env python3
"""Build the Plebum Dominium kit sheet PDFs (reportlab, US Letter).

Rebuilt 2026-10-21 to replace the lost generator. Renders each sheet from
the BUILT site pages (docs/handouts/*.html, docs/index.html) so the PDFs
always carry the same copy as the site: header with QR on every page,
black step bar + meta table on page 1, animations and figures replaced by
their static print equivalents.

Usage: python3 scripts/build-kit-pdfs.py [slug ...]
Output: kit/*.pdf (unstamped; run scripts/stamp-pdfs.py afterwards)
"""
import os
import re
import sys
from html.parser import HTMLParser

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table,
    TableStyle, KeepTogether, HRFlowable, Flowable,
)
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
KIT = os.path.join(ROOT, "kit")
PAGE_W, PAGE_H = letter
MARGIN = 50
FRAME_W = PAGE_W - 2 * MARGIN

INK = colors.HexColor("#1c1917")
MUTED = colors.HexColor("#57534e")
COPPER = colors.HexColor("#8a5a2a")
TAN = colors.HexColor("#ece2d0")
TANBG = colors.HexColor("#faf5ea")
DARK = colors.HexColor("#161411")
CODEBG = colors.HexColor("#f5f2ec")
REDBG = colors.HexColor("#fef2f2")
RED = colors.HexColor("#b91c1c")
BORDER = colors.HexColor("#c9bda6")
BASE = "https://plebumbtc.io"

# ---------------------------------------------------------------- styles
sTitle = ParagraphStyle("title", fontName="Times-Bold", fontSize=20,
                        leading=24, textColor=INK, spaceAfter=6)
sH2 = ParagraphStyle("h2", fontName="Times-Bold", fontSize=13.5,
                     leading=17, textColor=COPPER, spaceBefore=11,
                     spaceAfter=4)
sH3 = ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=10.5,
                     leading=14, textColor=INK, spaceBefore=8, spaceAfter=3)
sBody = ParagraphStyle("body", fontName="Helvetica", fontSize=10,
                       leading=14.6, textColor=INK, spaceAfter=6)
sBodySmall = ParagraphStyle("bodys", parent=sBody, fontSize=9.6,
                            leading=13.8)
sBullet = ParagraphStyle("bullet", parent=sBody, leftIndent=13,
                         bulletIndent=4, spaceAfter=3)
sNum = ParagraphStyle("num", parent=sBody, leftIndent=17, firstLineIndent=0,
                      bulletIndent=4, spaceAfter=3)
sTerm = ParagraphStyle("term", fontName="Helvetica-Bold", fontSize=10,
                       leading=13.5, textColor=INK, spaceBefore=5,
                       spaceAfter=0)
sDef = ParagraphStyle("def", fontName="Helvetica", fontSize=10,
                      leading=14, textColor=INK, spaceAfter=4)
sCode = ParagraphStyle("code", fontName="Courier", fontSize=8.6,
                       leading=12, textColor=INK)
sCaption = ParagraphStyle("caption", fontName="Helvetica", fontSize=7.4,
                          leading=10, textColor=MUTED, alignment=TA_CENTER,
                          spaceBefore=3, spaceAfter=8)
sCallout = ParagraphStyle("callout", parent=sBody, fontSize=9.8,
                          leading=14.2, spaceAfter=3)
sCalloutLabel = ParagraphStyle("calloutlabel", fontName="Helvetica-Bold",
                               fontSize=8, leading=11, textColor=COPPER,
                               spaceAfter=2)
sBar = ParagraphStyle("bar", fontName="Helvetica", fontSize=8.2,
                      leading=11, textColor=colors.white)
sBarC = ParagraphStyle("barc", parent=sBar, alignment=TA_CENTER)
sBarR = ParagraphStyle("barr", parent=sBar, alignment=TA_RIGHT)
sMetaL = ParagraphStyle("metal", fontName="Helvetica-Bold", fontSize=7.4,
                        leading=10, textColor=INK)
sMetaV = ParagraphStyle("metav", fontName="Helvetica", fontSize=9.2,
                        leading=12, textColor=INK)
sLede = ParagraphStyle("lede", parent=sBody, fontName="Helvetica-Oblique",
                       fontSize=10.4, leading=15)
sFigText = ParagraphStyle("figtext", fontName="Helvetica", fontSize=9.4,
                          leading=13.6, textColor=INK, spaceAfter=2)
sFigMono = ParagraphStyle("figmono", fontName="Courier", fontSize=8.8,
                          leading=12.6, textColor=INK, spaceAfter=2)

LOG = []


def log(msg):
    LOG.append(msg)
    print("  ..", msg)


# ------------------------------------------------------------ page frame
def make_header_footer(title_caps, url):
    def hf(canvas, doc):
        canvas.saveState()
        # header
        canvas.setFillColor(INK)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.drawString(MARGIN, PAGE_H - 38, "PLEBUM DOMINIUM")
        bw = canvas.stringWidth("PLEBUM DOMINIUM", "Helvetica-Bold", 8)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(MARGIN + bw + 5, PAGE_H - 38, "·  " + title_caps)
        # QR top-right
        qr = QrCodeWidget(url)
        qr.barWidth = 44
        qr.barHeight = 44
        d = Drawing(44, 44)
        d.add(qr)
        d.drawOn(canvas, PAGE_W - MARGIN - 44, PAGE_H - 58)
        canvas.setFont("Helvetica", 6)
        canvas.setFillColor(MUTED)
        canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - 66,
                               "scan for the full sheet")
        # footer
        canvas.setFont("Helvetica-Oblique", 7.5)
        canvas.drawString(MARGIN, 36,
                          "Stop if a check fails. Do not skip ahead.")
        canvas.setFont("Helvetica", 7.5)
        canvas.drawRightString(PAGE_W - MARGIN, 36,
                               f"Page {doc.page} of {doc._total_pages}")
        canvas.restoreState()
    return hf


class SheetDoc(BaseDocTemplate):
    _total_pages = 1

    def __init__(self, path, title_caps, url):
        super().__init__(path, pagesize=letter,
                         leftMargin=MARGIN, rightMargin=MARGIN,
                         topMargin=80, bottomMargin=50,
                         title=f"Plebum Dominium · {title_caps}",
                         author="Plebum Dominium")
        frame = Frame(MARGIN, 50, FRAME_W, PAGE_H - 80 - 50, id="main",
                      leftPadding=0, rightPadding=0, topPadding=0,
                      bottomPadding=0)
        hf = make_header_footer(title_caps, url)
        self.addPageTemplates([PageTemplate(id="sheet", frames=[frame],
                                            onPage=hf)])


# ------------------------------------------------------------- mini DOM
class Node:
    __slots__ = ("tag", "attrs", "children")

    def __init__(self, tag, attrs):
        self.tag = tag
        self.attrs = dict(attrs)
        self.children = []  # mixed: Node and str, in document order

    @property
    def cls(self):
        return self.attrs.get("class", "")

    def has_class(self, name):
        return name in self.cls.split()

    def iter(self):
        yield self
        for c in self.children:
            if isinstance(c, Node):
                yield from c.iter()

    def find_all(self, pred):
        return [n for n in self.iter() if pred(n)]

    def text_content(self):
        parts = []
        for c in self.children:
            parts.append(c if isinstance(c, str) else c.text_content())
        return "".join(parts)


VOID = {"br", "img", "hr", "meta", "link", "input", "path", "circle",
        "rect", "line", "polyline", "polygon", "use", "stop", "ellipse"}


class TreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("root", {})
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs)
        self.stack[-1].children.append(n)
        if tag not in VOID:
            self.stack.append(n)

    def handle_startendtag(self, tag, attrs):
        self.stack[-1].children.append(Node(tag, attrs))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        if data:
            self.stack[-1].children.append(data)


def parse_article(path):
    raw = open(path, encoding="utf-8").read()
    tb = TreeBuilder()
    tb.feed(raw)
    arts = tb.root.find_all(lambda n: n.tag == "article")
    if arts:
        return arts[0]
    mains = tb.root.find_all(lambda n: n.tag == "main")
    return mains[0] if mains else tb.root


# ------------------------------------------------------- inline markup
def esc(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def inline(node):
    """Node -> reportlab Paragraph markup (mixed content, in order)."""
    out = []
    for c in node.children:
        if isinstance(c, str):
            out.append(esc(c))
            continue
        if c.tag in ("strong", "b"):
            out.append(f"<b>{inline(c)}</b>")
        elif c.tag in ("em", "i"):
            out.append(f"<i>{inline(c)}</i>")
        elif c.tag == "code":
            out.append(f'<font face="Courier" size="8.6">{inline(c)}</font>')
        elif c.tag == "br":
            out.append("<br/>")
        elif c.tag == "a":
            out.append(inline(c))
        else:
            out.append(inline(c))
    return "".join(out)


def plain_text(node):
    return re.sub(r"\s+", " ", node.text_content()).strip()


# ------------------------------------------------------------ diagrams
class PanelRow(Flowable):
    """Dark boxes in a row with arrows between, plus a caption."""

    def __init__(self, boxes, caption=None, width=FRAME_W, box_h=54):
        super().__init__()
        self.boxes = boxes  # [(title, [sub lines])]
        self.caption = caption
        self.width = width
        self.box_h = box_h

    def wrap(self, aW, aH):
        h = self.box_h + (14 if self.caption else 4)
        return (self.width, h)

    def draw(self):
        c = self.canv
        c.saveState()
        n = len(self.boxes)
        arrow_w = 22 if n > 1 else 0
        bw = (self.width - arrow_w * (n - 1)) / n
        y = 14 if self.caption else 4
        for i, (title, subs) in enumerate(self.boxes):
            x = i * (bw + arrow_w)
            c.setFillColor(DARK)
            c.roundRect(x, y, bw, self.box_h, 5, stroke=0, fill=1)
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 8.6)
            c.drawCentredString(x + bw / 2, y + self.box_h - 17, title)
            c.setFont("Helvetica", 7.6)
            c.setFillColor(colors.HexColor("#c9c2b4"))
            ly = y + self.box_h - 30
            for s in subs:
                c.drawCentredString(x + bw / 2, ly, s)
                ly -= 11
            if i < n - 1:
                ax = x + bw + 3
                ay = y + self.box_h / 2
                c.setStrokeColor(INK)
                c.setFillColor(INK)
                c.setLineWidth(1.4)
                c.line(ax, ay, ax + arrow_w - 7, ay)
                c.line(ax + arrow_w - 7, ay, ax + arrow_w - 13, ay - 4)
                c.line(ax + arrow_w - 7, ay, ax + arrow_w - 13, ay + 4)
        if self.caption:
            c.setFont("Helvetica", 7.4)
            c.setFillColor(MUTED)
            c.drawCentredString(self.width / 2, 2, self.caption)
        c.restoreState()


def code_panel(lines, width=FRAME_W):
    paras = [Paragraph(esc(l) if l else "&nbsp;", sCode) for l in lines]
    inner = [[paras[0]]] if len(paras) == 1 else [[p] for p in paras]
    t = Table(inner, colWidths=[width - 14])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CODEBG),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#ddd5c4")),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return t


def callout_table(label, body_flowables, stop=False):
    bg = REDBG if stop else TANBG
    bd = RED if stop else BORDER
    rows = []
    if label:
        lab = ParagraphStyle("cl", parent=sCalloutLabel,
                             textColor=RED if stop else COPPER)
        rows.append([Paragraph(esc(label.upper()), lab)])
    for f in body_flowables:
        rows.append([f])
    t = Table(rows, colWidths=[FRAME_W - 16])
    style = [
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.8, bd),
        ("LINEBELOW", (0, 0), (-1, 0), 0, bg),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    t.setStyle(TableStyle(style))
    return [Spacer(1, 3), t, Spacer(1, 7)]


# ------------------------------------------------------- sheet registry
# slug -> (header caps, output pdf, page path under docs/)
SHEETS = {
    "terms": ("TERMS", "Terms.pdf", "handouts/terms.html"),
    "checklist": ("CHECKLIST", "03_Checklist.pdf", "handouts/checklist.html"),
    "verify": ("CHECK THE FILES", "05_Verify.pdf", "handouts/verify.html"),
    "airgap": ("TWO BOOTS", "04_Airgap.pdf", "handouts/airgap.html"),
    "dice": ("MAKE THE THREE KEYS", "06_Dice.pdf", "handouts/dice.html"),
    "sparrow": ("BUILD THE 2-OF-3", "07_Sparrow.pdf", "handouts/sparrow.html"),
    "signing": ("PRACTICE SPEND", "08_Signing.pdf", "handouts/signing.html"),
    "titanium": ("METAL AND THE MAP", "09_Titanium.pdf",
                 "handouts/titanium.html"),
    "encryption": ("HIDE THE WALLET MAP", "11_Encryption.pdf",
                   "handouts/encryption.html"),
    "inheritance": ("IF I AM GONE", "12_Inheritance.pdf",
                    "handouts/inheritance.html"),
    "faq": ("IF YOU GET STUCK", "13_FAQ.pdf", "handouts/faq.html"),
    "briefing": ("TOUGH QUESTIONS", "14_Speaker.pdf",
                 "handouts/briefing.html"),
    "overview": ("PROJECT OVERVIEW", "00_Project_Overview.pdf", "index.html"),
}
BUNDLE_ORDER = ["terms", "checklist", "verify", "airgap", "dice", "sparrow",
                "signing", "titanium", "encryption", "inheritance", "faq",
                "briefing"]

SKIP_CLASSES = {"kicker", "prevnext-row", "newbie-banner", "sheet-head",
                "step-banner", "sheet-meta", "copy-btn", "site-footer",
                "donate-row"}


def extract_furniture(article):
    """Pull (bar_prev, bar_center_html, bar_next, meta pairs, h1) from DOM."""
    bar_prev = bar_next = ""
    bar_center = ""
    banner = article.find_all(lambda n: n.has_class("step-banner"))
    if banner:
        b = banner[0]
        navs = [n for n in b.children
                if isinstance(n, Node) and n.has_class("step-nav")]
        pos = b.find_all(lambda n: n.has_class("step-pos"))
        if pos:
            bar_center = inline(pos[0])
        texts = [plain_text(n) for n in navs]
        for t in texts:
            if t.startswith("←") or "·" in t and t.endswith(""):
                pass
        if len(texts) >= 2:
            bar_prev, bar_next = texts[0], texts[-1]
        elif len(texts) == 1:
            bar_next = texts[0]
    meta = []
    msec = article.find_all(lambda n: n.has_class("sheet-meta"))
    if msec:
        for item in msec[0].find_all(lambda n: n.has_class("meta-item")):
            lab = item.find_all(lambda n: n.has_class("meta-label"))
            val = item.find_all(lambda n: n.has_class("meta-val"))
            if lab and val:
                meta.append((plain_text(lab[0]), plain_text(val[0])))
    h1s = article.find_all(lambda n: n.tag == "h1")
    h1 = plain_text(h1s[0]) if h1s else ""
    return bar_prev, bar_center, bar_next, meta, h1


def bar_flowable(prev, center_html, nxt):
    row = [[Paragraph(esc(prev), sBar),
            Paragraph(center_html, sBarC),
            Paragraph(esc(nxt), sBarR)]]
    t = Table(row, colWidths=[FRAME_W * 0.30, FRAME_W * 0.40, FRAME_W * 0.30])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#111111")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def meta_flowable(meta):
    if not meta:
        return None
    labels = [Paragraph(esc(l), sMetaL) for l, _ in meta]
    values = [Paragraph(esc(v), sMetaV) for _, v in meta]
    widths = [FRAME_W * w for w in (0.19, 0.17, 0.13, 0.51)][:len(meta)]
    rest = FRAME_W - sum(widths)
    if rest and widths:
        widths[-1] += rest
    t = Table([labels, values], colWidths=widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TAN),
        ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#ddd2bd")),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


# ------------------------------------------------------------- diagrams
# (slug, figure index) -> flowables. Filled in from the old PDFs' artwork.
def diagram_airgap_boots():
    return [PanelRow([
        ("BOOT 1 · ONLINE", ["WATCH · NEVER A SEED"]),
        ("BOOT 2 · TAILS", ["1 SEED", "NETWORK OFF · THEN SHUT DOWN"]),
    ], caption="SAME COMPUTER · SHUT DOWN FULLY BETWEEN"), Spacer(1, 4)]


DIAGRAMS = {
    ("airgap", 1): diagram_airgap_boots,
}

# (slug) -> flowables replacing the animation block. Handcrafted statics;
# anything not listed uses the generic DOM text flattening below.
STATICS = {}


def flatten_anim(node, slug):
    """Generic static: the animation's own text, flattened in order."""
    out = []
    lines = []

    def gather(n):
        t = plain_text(n)
        if t:
            lines.append(t)

    for child in node.children:
        if not isinstance(child, Node):
            continue
        if child.tag in ("ol", "ul"):
            items = [plain_text(li) for li in child.children
                     if isinstance(li, Node) and li.tag == "li"]
            for i, t in enumerate(items, 1):
                if t:
                    lines.append(f"{i}. {t}" if child.tag == "ol" else t)
        elif child.find_all(lambda n: n.tag in ("ol", "ul")):
            gather(child)
        else:
            gather(child)
    seen = set()
    for t in lines:
        if t in seen:
            continue
        seen.add(t)
        style = sFigMono if re.search(r"[01]{2,}", t) else sFigText
        out.append(Paragraph(esc(t), style))
    if out:
        log(f"{slug}: animation flattened to {len(out)} text lines")
    return [Spacer(1, 2)] + out + [Spacer(1, 4)]


# ------------------------------------------------------------ converter
BLOCK_TAGS = {"p", "h1", "h2", "h3", "h4", "h5", "ul", "ol", "dl", "pre",
              "table", "blockquote", "hr", "figure", "section", "div",
              "aside", "article", "main", "li", "dt", "dd"}


class Converter:
    def __init__(self, slug):
        self.slug = slug
        self.fig_index = 0

    def gap(self, out, pts):
        """Per-sheet air: the sparrow sheet runs longer, like the original."""
        if self.slug == "sparrow" and pts:
            out.append(Spacer(1, pts))

    def convert(self, article):
        out = []
        self.blocks(article, out)
        return out

    def blocks(self, node, out):
        for child in node.children:
            if isinstance(child, str):
                if child.strip():
                    out.append(Paragraph(esc(child.strip()), sBody))
            else:
                self.block(child, out)

    def block(self, node, out):
        cls = set(node.cls.split())
        if cls & SKIP_CLASSES:
            return
        if node.has_class("callout"):
            out.extend(self.callout(node))
            return
        if any(c.endswith("-anim") or c == "anim" for c in cls):
            out.extend(self.animation(node))
            return
        tag = node.tag
        if tag == "h1":
            return  # title drawn by the builder
        if tag == "h2":
            st = sH3 if self.slug == "checklist" else sH2
            out.append(Paragraph(inline(node), st))
            self.gap(out, 10)
        elif tag == "h3":
            txt = inline(node)
            if self.slug in ("faq", "briefing") \
                    and not plain_text(node).startswith("Q:"):
                txt = "Q: " + txt
            out.append(Paragraph(txt, sH3))
        elif tag == "h4":
            out.append(Paragraph(inline(node), sH3))
        elif tag == "p":
            if plain_text(node):
                st = sLede if node.has_class("lede") else sBody
                out.append(Paragraph(inline(node), st))
                self.gap(out, 1.6)
        elif tag in ("ul", "ol"):
            out.extend(self.listing(node, ordered=(tag == "ol")))
        elif tag == "dl":
            self.dlist(node, out)
        elif tag == "pre":
            txt = node.text_content().strip("\n")
            lines = [l.rstrip() for l in txt.split("\n")]
            out.append(code_panel(lines))
            out.append(Spacer(1, 6))
            self.gap(out, 6)
        elif tag == "figure" or node.has_class("sheet-diagram") \
                or node.has_class("fig"):
            out.extend(self.figure(node))
            self.gap(out, 12)
        elif tag == "svg":
            out.extend(self.figure(node))
        elif tag == "table":
            out.append(self.table(node))
            out.append(Spacer(1, 6))
        elif tag == "blockquote":
            inner = []
            self.blocks(node, inner)
            for f in inner:
                if isinstance(f, Paragraph):
                    f.style = ParagraphStyle(
                        "bq", parent=f.style, leftIndent=14,
                        fontName="Helvetica-Oblique")
                out.append(f)
        elif tag == "hr":
            out.append(HRFlowable(width="100%", thickness=0.6, color=BORDER,
                                  spaceBefore=4, spaceAfter=8))
        elif tag == "img":
            log(f"{self.slug}: skipped an image")
        elif tag in ("div", "section", "article", "main", "span"):
            if not node.find_all(lambda n: n.tag in BLOCK_TAGS) \
                    and plain_text(node):
                out.append(Paragraph(inline(node), sBody))
            else:
                self.blocks(node, out)
        elif tag in ("dt",):
            out.append(Paragraph(inline(node), sTerm))
        elif tag in ("dd",):
            out.append(Paragraph(inline(node), sDef))
        else:
            self.blocks(node, out)

    def listing(self, node, ordered, depth=0):
        out = []
        style = ParagraphStyle(f"lst{depth}", parent=sBullet,
                               leftIndent=13 + depth * 14)
        nstyle = ParagraphStyle(f"nlst{depth}", parent=sNum,
                                leftIndent=17 + depth * 14)
        idx = 0
        for li in node.children:
            if not isinstance(li, Node) or li.tag != "li":
                continue
            idx += 1
            nested = [c for c in li.children
                      if isinstance(c, Node) and c.tag in ("ul", "ol")]
            clone_text = inline(li)
            # inline() includes nested list text; acceptable for flat lists,
            # but strip nested markup by rebuilding without nested lists:
            if nested:
                li2 = Node("li", {})
                li2.children = [c for c in li.children
                                if isinstance(c, str)
                                or c.tag not in ("ul", "ol")]
                clone_text = inline(li2)
            if plain_text(li):
                if ordered:
                    out.append(Paragraph(clone_text, nstyle,
                                         bulletText=f"{idx}."))
                elif self.slug == "checklist":
                    out.append(Paragraph(clone_text, style, bulletText=""))
                else:
                    out.append(Paragraph(clone_text, style,
                                         bulletText="•"))
            for sub in nested:
                out.extend(self.listing(sub, ordered=(sub.tag == "ol"),
                                        depth=depth + 1))
        return out

    def dlist(self, node, out):
        for n in node.iter():
            if n.tag == "dt":
                out.append(Paragraph(inline(n), sTerm))
            elif n.tag == "dd":
                out.append(Paragraph(inline(n), sDef))

    def callout(self, node):
        label = ""
        body = []
        for child in node.children:
            if not isinstance(child, Node):
                continue
            if child.has_class("callout-label"):
                label = plain_text(child)
            elif child.tag == "p":
                if plain_text(child):
                    body.append(Paragraph(inline(child), sCallout))
            else:
                sub = []
                self.block(child, sub)
                body.extend(sub)
        if not body and plain_text(node):
            body.append(Paragraph(inline(node), sCallout))
        stop = node.has_class("callout-stop")
        return callout_table(label, body, stop=stop)

    def animation(self, node):
        if self.slug in STATICS:
            return STATICS[self.slug]()
        return flatten_anim(node, self.slug)

    def figure(self, node):
        self.fig_index += 1
        key = (self.slug, self.fig_index)
        if key in DIAGRAMS:
            return DIAGRAMS[key]()
        # fallback: the figure's own text in a light panel + caption
        texts = []
        for t in node.find_all(lambda n: n.tag == "text"):
            s = plain_text(t)
            if s:
                texts.append(s)
        cap = ""
        caps = node.find_all(lambda n: n.tag == "figcaption"
                             or n.has_class("fig-caption")
                             or n.has_class("caption"))
        if caps:
            cap = plain_text(caps[0])
        log(f"{self.slug}: figure {self.fig_index} fallback "
            f"({len(texts)} svg texts, caption={cap[:40]!r})")
        if not cap and sum(len(x) for x in texts) < 30:
            return []  # decorative icon/badge, not a content figure
        out = []
        if texts:
            joined = " · ".join(texts)
            joined = re.sub(r"(?<=[./_-])", "\u200b", joined)
            paras = [Paragraph(esc(joined), sFigText)]
            t = Table([[paras[0]]], colWidths=[FRAME_W - 32])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), TANBG),
                ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            out.append(t)
        if cap:
            out.append(Paragraph(esc(cap), sCaption))
        return out

    def table(self, node):
        rows = []
        header = False
        for tr in node.find_all(lambda n: n.tag == "tr"):
            cells = [c for c in tr.children
                     if isinstance(c, Node) and c.tag in ("td", "th")]
            if not cells:
                continue
            if any(c.tag == "th" for c in cells):
                header = True
            row = []
            for c in cells:
                st = ParagraphStyle("th", parent=sBodySmall,
                                    fontName="Helvetica-Bold") \
                    if c.tag == "th" else sBodySmall
                row.append(Paragraph(inline(c), st))
            rows.append(row)
        if not rows:
            return Spacer(1, 1)
        ncols = max(len(r) for r in rows)
        widths = [FRAME_W / ncols] * ncols
        t = Table(rows, colWidths=widths, repeatRows=1 if header else 0)
        style = [
            ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
            ("INNERGRID", (0, 0), (-1, -1), 0.4,
             colors.HexColor("#ddd2bd")),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]
        if header:
            style.append(("BACKGROUND", (0, 0), (-1, 0), TAN))
        t.setStyle(TableStyle(style))
        return t


# ---------------------------------------------------------------- build
OUTDIR = os.environ.get("KIT_PDF_OUT", KIT)


def build_sheet(slug):
    caps, outfile, rel = SHEETS[slug]
    article = parse_article(os.path.join(DOCS, rel))
    prev, center, nxt, meta, h1 = extract_furniture(article)

    def make_story():
        if slug == "overview":
            return overview_story(article)
        conv = Converter(slug)
        body = conv.convert(article)
        story = []
        if center or prev or nxt:
            story.append(bar_flowable(prev, center, nxt))
            story.append(Spacer(1, 9))
        if h1:
            story.append(Paragraph(esc(h1), sTitle))
        mf = meta_flowable(meta)
        if mf is not None:
            story.append(mf)
            story.append(Spacer(1, 7))
        story.extend(body)
        return story

    url = BASE + "/" if slug == "overview" else \
        f"{BASE}/handouts/{slug}.html"
    path = os.path.join(OUTDIR, outfile)
    # two passes with FRESH flowables each time (reportlab flowables are
    # single-use): the footer needs the total page count
    from pypdf import PdfReader
    doc = SheetDoc(path, caps, url)
    doc._total_pages = 1
    doc.build(make_story())
    total = len(PdfReader(path).pages)
    doc = SheetDoc(path, caps, url)
    doc._total_pages = total
    doc.build(make_story())
    print(f"{slug}: {total} pages -> {outfile}")
    return path


def build_bundle(paths_by_slug):
    from pypdf import PdfReader, PdfWriter
    w = PdfWriter()
    for slug in BUNDLE_ORDER:
        for page in PdfReader(paths_by_slug[slug]).pages:
            w.add_page(page)
    out = os.path.join(OUTDIR, "Handouts_No_Cover.pdf")
    with open(out, "wb") as fh:
        w.write(fh)
    print(f"bundle: {len(PdfReader(out).pages)} pages -> Handouts_No_Cover.pdf")
    return out


def main():
    slugs = sys.argv[1:] or list(SHEETS)
    os.makedirs(OUTDIR, exist_ok=True)
    built = {}
    for slug in slugs:
        built[slug] = build_sheet(slug)
    if all(s in built for s in BUNDLE_ORDER) and \
            set(slugs) == set(SHEETS):
        build_bundle(built)



# ------------------------------------------------- dark panel flowables
class DarkPanel(Flowable):
    """One dark rounded panel with centered lines, plus a caption."""

    def __init__(self, lines, caption=None, width=FRAME_W * 0.62,
                 mono=False, align="center", min_h=0, line_gap=13):
        super().__init__()
        self.lines = lines  # [(text, bold)] or [text]
        self.caption = caption
        self.width = width
        self.mono = mono
        self.align = align
        self.min_h = min_h
        self.line_gap = line_gap

    def _norm(self):
        out = []
        for l in self.lines:
            if isinstance(l, tuple):
                out.append(l)
            else:
                out.append((l, False))
        return out

    def wrap(self, aW, aH):
        n = len(self._norm())
        self._h = max(self.min_h,
                      16 + n * self.line_gap) + (14 if self.caption else 4)
        return (self.width, self._h)

    def draw(self):
        c = self.canv
        c.saveState()
        lines = self._norm()
        ph = self._h - (14 if self.caption else 4)
        x = (FRAME_W - self.width) / 2
        c.setFillColor(DARK)
        c.roundRect(x, self._h - ph, self.width, ph, 6, stroke=0, fill=1)
        block_h = (len(lines) - 1) * self.line_gap + 10
        ty = self._h - (14 if self.caption else 4) - (ph - block_h) / 2 - 8
        for text, bold in lines:
            if self.mono:
                c.setFont("Courier-Bold" if bold else "Courier", 8.6)
            else:
                c.setFont("Helvetica-Bold" if bold else "Helvetica", 8.8)
            c.setFillColor(colors.white)
            if self.align == "left":
                c.drawString(x + 14, ty, text)
            else:
                c.drawCentredString(x + self.width / 2, ty, text)
            ty -= self.line_gap
        if self.caption:
            c.setFont("Helvetica", 7.4)
            c.setFillColor(MUTED)
            c.drawCentredString(FRAME_W / 2, 2, self.caption)
        c.restoreState()


class TerminalPanel(Flowable):
    """Dark panel, mono lines left-aligned (a terminal window)."""

    def __init__(self, lines, caption=None, width=FRAME_W * 0.78,
                 line_gap=12.6):
        super().__init__()
        self.lines = lines
        self.caption = caption
        self.width = width
        self.line_gap = line_gap

    def wrap(self, aW, aH):
        self._h = 18 + len(self.lines) * self.line_gap \
            + (14 if self.caption else 4)
        return (self.width, self._h)

    def draw(self):
        c = self.canv
        c.saveState()
        ph = self._h - (14 if self.caption else 4)
        x = (FRAME_W - self.width) / 2
        c.setFillColor(DARK)
        c.roundRect(x, self._h - ph, self.width, ph, 6, stroke=0, fill=1)
        # window dots
        for i, col in enumerate(("#e0655a", "#e0a458", "#7fb069")):
            c.setFillColor(colors.HexColor(col))
            c.circle(x + 12 + i * 11, self._h - 11, 3, stroke=0, fill=1)
        ty = self._h - 30
        for text in self.lines:
            green = text.startswith("$")
            c.setFont("Courier", 8.4)
            c.setFillColor(colors.HexColor("#9ece8a") if green
                           else colors.HexColor("#e8e2d4"))
            c.drawString(x + 14, ty, text)
            ty -= self.line_gap
        if self.caption:
            c.setFont("Helvetica", 7.4)
            c.setFillColor(MUTED)
            c.drawCentredString(FRAME_W / 2, 2, self.caption)
        c.restoreState()


def DP(lines, caption=None, **kw):
    return [DarkPanel(lines, caption=caption, **kw), Spacer(1, 4)]


def TP(lines, caption=None, **kw):
    return [TerminalPanel(lines, caption=caption, **kw), Spacer(1, 4)]


def PR(boxes, caption=None, box_h=54):
    return [PanelRow(boxes, caption=caption, box_h=box_h), Spacer(1, 4)]


# ------------------------------------------------------- diagram registry
DIAGRAMS.update({
    # ---- verify
    ("verify", 1): lambda: PR([
        ("Tails", ["tails.net ✓"]), ("Sparrow", ["github.com ✓"]),
        ("Electrum", ["electrum.org ✓"]), ("Ian Coleman", ["github.com ✓"])],
        caption="NOT A LOOK-ALIKE PAGE · NOT FROM THIS SITE "
                "(EXCEPT THE DICE CONVERTER)"),
    ("verify", 2): lambda: PR([
        ("FILE", ["a3f9…c41d", "your computer computes this"]),
        ("PROJECT'S OWN SITE", ["compare with the fingerprint"])],
        caption="EVERY CHARACTER MATCHES ✓ · ONE DIFFERS = DELETE"),
    ("verify", 3): lambda: TP([
        "$ gpg --verify sparrow-2.5.5-manifest.txt.asc",
        "gpg: Good signature",
        "gpg: WARNING: This key is not certified with a trusted signature!"],
        caption="THAT WARNING IS NORMAL. "
                "THE FINGERPRINT MATCH IS WHAT MATTERS"),
    ("verify", 4): lambda: TP([
        "$ ./verify_kit.sh",
        "tails-amd64-7.13.img … PASS",
        "sparrowwallet-2.5.5 … PASS",
        "dice-converter … PASS"]),
    ("verify", 5): lambda: PR([
        ("DICE CONVERTER", ["abandon ability …", "… art"]),
        ("IAN COLEMAN (OFFLINE)", ["abandon ability …", "… art"])],
        caption="SAME BITS → SAME WORDS · SAME SEED → SAME ADDRESSES · "
                "SAME PAYMENT DETAILS"),
    # ---- airgap figure 2 (figure 1 registered earlier)
    ("airgap", 2): lambda: PR([
        ("TAILS USB", ["checked file → written", "with official installer"]),
        ("DATA USB", ["only checked files", "labeled DATA"])],
        caption="NO PERSISTENT STORAGE. THE DRIVE STAYS AMNESIC"),
    # ---- sparrow
    ("sparrow", 1): lambda: DP([("NETWORKING", True), ("DISABLED ✓", False)],
                               caption="IF THE NETWORK IS ON: STOP",
                               width=FRAME_W * 0.66, min_h=88, line_gap=16),
    ("sparrow", 2): lambda: TP([
        "$ cd ~/Desktop",
        "$ tar -xvf sparrowwallet-2.5.5-x86_64.tar.gz",
        "$ cd Sparrow",
        "$ ./bin/Sparrow"], line_gap=15),
    ("sparrow", 3): lambda: DP([
        ("New Wallet", True), ("✓ Multi Signature", False),
        ("✓ Native Segwit", False), ("✓ 2 of 3", False),
        ("m/48'/0'/0'/2'", False)], width=FRAME_W * 0.66, min_h=104,
        line_gap=15),
    ("sparrow", 4): lambda: PR([
        ("SEED 1", ["24 words"]),
        ("SPARROW", ["s1-xpub.txt", "xpub6C...9f2k", "→ data USB"])],
        caption="THEN: CLOSE · SHUT DOWN · DARK SCREEN", box_h=64),
    ("sparrow", 5): lambda: PR([
        ("SEED 2", ["→ s2-xpub.txt"]), ("SEED 3", ["→ s3-xpub.txt"])],
        caption="NEVER CONTINUE FROM THE PREVIOUS BOOT", box_h=64),
    ("sparrow", 6): lambda: DP([
        ("s1-xpub · s2-xpub · s3-xpub", False),
        ("2-of-3 · m/48'/0'/0'/2'", True),
        ("MAP: descriptor", False)],
        caption="NO SEED IS TYPED ON THIS BOOT", min_h=72, line_gap=15),
    ("sparrow", 7): lambda: DP([("WATCH ONLY", True),
                                ("THIS COMPUTER NEVER HOLDS A SEED", False)],
                               min_h=64, line_gap=15),
    # ---- signing
    ("signing", 1): lambda: PR([
        ("WATCH ONLY", []), ("SEND", []), ("tx-unsigned.psbt", [])],
        caption="READ EVERY FIELD AGAINST THE PAPER NOTE"),
    ("signing", 2): lambda: PR([
        ("TAILS", ["network off", "SEED 1 only"]),
        ("tx-unsigned → tx-partial-s1", [])],
        caption="THEN: FULL SHUTDOWN"),
    ("signing", 3): lambda: PR([
        ("TAILS", ["fresh boot", "SEED 2 only"]),
        ("tx-partial-s1 → tx-signed ✓✓", [])],
        caption="THEN: FULL SHUTDOWN"),
    ("signing", 4): lambda: PR([
        ("WATCH ONLY", []), ("BROADCAST", ["txid → workbook"])]),
    # ---- encryption
    ("encryption", 2): lambda: PR([
        ("TAILS", ["network off"]),
        ("DESKTOP", ["obfuscator.py", "map.txt"])],
        caption="NEVER OPEN THE MAP ON A PHONE"),
    ("encryption", 3): lambda: TP([
        "$ python3 descriptor_obfuscator.py",
        "[E]ncrypt / [D]ecrypt? E",
        "Paste wallet map: wsh(sortedmulti(2,…))",
        "Passphrase: ••••••••••",
        "wrote map.txt.gpg ✓"]),
    ("encryption", 4): lambda: PR([
        ("map.txt.gpg", ["locked"]), ("USB 1 · USB 2", ["copies"]),
        ("map.txt", ["delete it"])],
        caption="EMPTY THE TRASH"),
    ("encryption", 5): lambda: PR([
        ("PASSPHRASE", ["place #1"]), ("PASSPHRASE", ["place #2"])],
        caption="AWAY FROM THE PLATES · AWAY FROM THE USBs"),
    ("encryption", 6): lambda: TP([
        "[E]ncrypt / [D]ecrypt? D (later offline boot)",
        "Passphrase: ••••••••••",
        "first address: bc1q…7x2k",
        "✓ MATCHES"]),
    # ---- inheritance
    ("inheritance", 1): lambda: PR([
        ("PLATE A", ["find it"]), ("PLATE B", ["find it"]),
        ("MAP", ["decrypt it"])],
        caption="TWO PLATES + THE MAP. LEAVE THE THIRD PLATE WHERE IT IS"),
})


# --------------------------------------------------------- anim statics
def static_dice():
    out = [Spacer(1, 2)]
    for bits in ("11", "01 00 10 01 01", "11 11 00 10 00 10", "00 01", "10"):
        out.append(Paragraph(esc(bits), sFigMono))
    out.append(Spacer(1, 3))
    out.append(Paragraph("256-BIT STRING", ParagraphStyle(
        "d1", parent=sFigText, fontName="Helvetica-Bold")))
    out.append(Paragraph("11 00 10 01 01 01 11 00 10 11 00 10 00 01 10",
                         sFigMono))
    out.append(Paragraph("…keep rolling…&nbsp; 256 / 256 BITS", sFigText))
    out.append(Spacer(1, 4))
    return out


def static_airgap():
    out = [Spacer(1, 2)]
    out.append(Paragraph("<b>Boot 1 · Network on</b>", sFigText))
    out.append(Paragraph(
        "Watches balances. Builds a payment. Never holds a seed.", sFigText))
    for b in ("Verify files", "Watch-only wallet", "Export unsigned file"):
        out.append(Paragraph(esc(b), sBullet, bulletText="•"))
    out.append(Paragraph("then", sFigText))
    out.append(Paragraph("shut down", sFigText))
    out.append(Paragraph("<b>Boot 2 · Networking off</b>", sFigText))
    out.append(Paragraph(
        "This stick is the offline computer. It borrows the hardware, "
        "then forgets.", sFigText))
    out.append(Paragraph("Networking off", sFigText))
    for b in ("One seed in memory", "Sign the file", "Full shutdown after"):
        out.append(Paragraph(esc(b), sBullet, bulletText="•"))
    out.append(Spacer(1, 4))
    return out


def static_signing():
    legend = [
        "Create. Watch-only builds the transaction. "
        "The file is an empty outline.",
        "Seed 1 signs. The file fills halfway. 1 of 2.",
        "Shutdown. The file stops at the red line: full shutdown, "
        "new session, then crosses deliberately.",
        "Seed 2 signs. The file fills whole. 2 of 2.",
        "Broadcast. Up and right, across the airgap. "
        "The twice-signed file goes out.",
    ]
    out = [Spacer(1, 2)]
    out.append(Paragraph("SHUTDOWN · NEW SESSION", sFigText))
    out.append(Paragraph("CREATE TRANSACTION", sFigText))
    out.append(Paragraph("BROADCAST TRANSACTION", sFigText))
    out.append(Spacer(1, 2))
    for i, t in enumerate(legend, 1):
        out.append(Paragraph(esc(t), sNum, bulletText=f"{i}."))
    out.append(Spacer(1, 4))
    return out


def static_titanium():
    out = [Spacer(1, 2)]
    for s in ("S1", "S2", "S3"):
        out.append(Paragraph(s, sFigText))
    out.append(Paragraph("THREE PLATES THREE PLACES", ParagraphStyle(
        "t1", parent=sFigText, fontName="Helvetica-Bold")))
    out.append(Spacer(1, 4))
    return out


STATICS.update({
    "dice": static_dice,
    "airgap": static_airgap,
    "signing": static_signing,
    "titanium": static_titanium,
})


# ------------------------------------------------------------- overview
sOvKick = ParagraphStyle("ovkick", fontName="Helvetica", fontSize=9.5,
                         leading=13, textColor=MUTED, spaceAfter=10)
sOvTitle = ParagraphStyle("ovtitle", fontName="Times-Bold", fontSize=25,
                          leading=29, textColor=INK, spaceAfter=2)
sOvPron = ParagraphStyle("ovpron", fontName="Helvetica-Oblique",
                         fontSize=10, leading=14, textColor=MUTED,
                         spaceAfter=3)
sOvSub = ParagraphStyle("ovsub", fontName="Helvetica-Bold", fontSize=11.5,
                        leading=15, textColor=COPPER, spaceAfter=8)
sStepT = ParagraphStyle("stept", fontName="Helvetica-Bold", fontSize=10,
                        leading=13.5, textColor=INK, spaceBefore=6,
                        spaceAfter=1)


def _section_with_h2(root, text):
    for sec in root.find_all(lambda n: n.tag == "section"):
        for h in sec.find_all(lambda n: n.tag == "h2"):
            if plain_text(h) == text:
                return sec
    return None


def _first(root, pred):
    hits = root.find_all(pred)
    return hits[0] if hits else None


def overview_story(root):
    story = []
    hero = _first(root, lambda n: n.tag == "section"
                  and n.find_all(lambda x: x.tag == "h1"))
    kick = _first(root, lambda n: n.has_class("kicker"))
    if kick is not None:
        story.append(Paragraph(esc(plain_text(kick)), sOvKick))
    h1 = _first(root, lambda n: n.tag == "h1")
    story.append(Paragraph(esc(plain_text(h1)), sOvTitle))
    pron = _first(root, lambda n: n.has_class("hero-pron"))
    if pron is not None:
        story.append(Paragraph(esc(plain_text(pron)), sOvPron))
    sub = _first(root, lambda n: n.has_class("hero-sub"))
    if sub is not None:
        story.append(Paragraph(esc(plain_text(sub)), sOvSub))
    # hero intro paragraphs: the plain <p>s between the tagline and the
    # why section, in document order (the hero is not a <section> here)
    seen_sub = sub is None
    for n in root.iter():
        if sub is not None and n is sub:
            seen_sub = True
            continue
        if not seen_sub:
            continue
        if n.tag == "h2":
            break
        if n.tag == "p" and not n.cls:
            t = plain_text(n)
            if t and "Start with the terms" not in t:
                story.append(Paragraph(inline(n), sBody))
    # why section
    why = _section_with_h2(root, "Eliminate single points of failure")
    if why is not None:
        wk = _first(why, lambda n: n.has_class("why-kicker"))
        h2 = _first(why, lambda n: n.tag == "h2")
        joined = plain_text(h2)
        if wk is not None:
            joined = (f"{plain_text(wk)}: "
                      + joined[0].lower() + joined[1:])
        story.append(Paragraph(esc(joined), sH2))
        for p in why.find_all(lambda n: n.tag == "p"):
            if not p.cls and plain_text(p):
                story.append(Paragraph(inline(p), sBody))
                break
        threats = _first(why, lambda n: n.has_class("threats"))
        if threats is not None:
            for li in threats.children:
                if isinstance(li, Node) and li.tag == "li":
                    t = re.sub(r"^[^A-Za-z]+", "", plain_text(li))
                    story.append(Paragraph(esc(t), sBullet, bulletText="•"))
    # process section
    proc = _section_with_h2(root, "The process, start to finish")
    if proc is not None:
        story.append(Paragraph("The process, start to finish", sH2))
        ssub = _first(proc, lambda n: n.has_class("section-sub"))
        if ssub is not None:
            story.append(Paragraph(inline(ssub), sBody))
        steps = []
        pending = None
        for n in proc.iter():
            if n.tag == "h3":
                t = plain_text(n)
                opt = ""
                for sp in n.find_all(lambda x: x.tag == "span"):
                    st = plain_text(sp)
                    if st and t.endswith(st):
                        t = t[: -len(st)].strip()
                        opt = f" ({st})"
                pending = (t + opt)
            elif n.tag == "p" and pending is not None and not n.cls:
                steps.append((pending, inline(n)))
                pending = None
        for i, (title, desc) in enumerate(steps, 1):
            story.append(Paragraph(f"{i}. {esc(title)}", sStepT))
            story.append(Paragraph(desc, sBody))
    # house rules
    rules = _section_with_h2(root, "House rules")
    if rules is not None:
        story.append(Paragraph("House rules", sH2))
        ssub = _first(rules, lambda n: n.has_class("section-sub"))
        if ssub is not None:
            story.append(Paragraph(inline(ssub), sBody))
        pending = None
        for n in rules.iter():
            if n.tag == "h3":
                pending = plain_text(n)
            elif n.tag == "p" and pending is not None and not n.cls:
                story.append(Paragraph(
                    f"<b>{esc(pending)}</b>: {inline(n)}", sBullet,
                    bulletText="•"))
                pending = None
    return story

if __name__ == "__main__":
    main()
