#!/usr/bin/env python3
"""Build the Plebum Dominium print packet (10 pages, US Letter).

Rebuilt from the live site content with print-friendly vector illustrations,
proper headers/footers, per-page QR codes, and real page numbers.

Usage: python3 scripts/build-print-packet.py
Output: kit/02_Print_Packet.pdf
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Flowable, KeepTogether, HRFlowable,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing

PAGE_W, PAGE_H = letter
MARGIN = 0.7 * inch
GOLD = colors.HexColor("#9a5f0a")
INK = colors.HexColor("#1c1917")
MUTED = colors.HexColor("#57534e")
RULE = colors.HexColor("#d6d3d1")

BASE = "https://plebumbtc.io"

# ---------------------------------------------------------------- styles
sTitle = ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=20,
                        leading=24, textColor=INK, spaceAfter=4)
sH1 = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=13,
                     leading=16, textColor=INK, spaceBefore=10, spaceAfter=4)
sH2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=10.5,
                     leading=13, textColor=GOLD, spaceBefore=8, spaceAfter=3)
sBody = ParagraphStyle("body", fontName="Helvetica", fontSize=9.5,
                       leading=13.5, textColor=INK, spaceAfter=3)
sSmall = ParagraphStyle("small", fontName="Helvetica", fontSize=8.5,
                        leading=11.5, textColor=MUTED, spaceAfter=2)
sBullet = ParagraphStyle("bullet", parent=sBody, leftIndent=14,
                         bulletIndent=5, spaceAfter=2)
sCode = ParagraphStyle("code", fontName="Courier", fontSize=8.5,
                       leading=11.5, textColor=INK, leftIndent=8, spaceAfter=1)
sTerm = ParagraphStyle("term", fontName="Helvetica-Bold", fontSize=9.5,
                       leading=12.5, textColor=INK, spaceBefore=5, spaceAfter=0)
sDef = ParagraphStyle("def", fontName="Helvetica", fontSize=9,
                      leading=12, textColor=MUTED, spaceAfter=2)
sQ = ParagraphStyle("q", fontName="Helvetica-Bold", fontSize=9.5,
                    leading=12.5, textColor=INK, spaceBefore=7, spaceAfter=1)
sA = ParagraphStyle("a", fontName="Helvetica", fontSize=9,
                    leading=12.5, textColor=INK, spaceAfter=2)


def bullets(items):
    return [Paragraph(f"<bullet>&bull;</bullet> {t}", sBullet) for t in items]


def stopbox(text):
    t = Table([[Paragraph(f"<b>STOP.</b> {text}", sBody)]],
              colWidths=[PAGE_W - 2 * MARGIN - 12])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fef2f2")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#b91c1c")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return [Spacer(1, 6), t, Spacer(1, 6)]


# ------------------------------------------------------- illustrations
class BootsDrawing(Flowable):
    """Two laptops with a shutdown arrow between them (B/W line art)."""
    def __init__(self, width):
        super().__init__()
        self.width = width
        self.height = 1.9 * inch

    def wrap(self, aW, aH):
        return (self.width, self.height)

    def draw(self):
        c = self.canv
        c.saveState()
        c.setStrokeColor(INK)
        c.setFillColor(INK)
        c.setLineWidth(1.2)
        lap_w, lap_h = 2.0 * inch, 1.15 * inch
        y = 0.45 * inch
        x1 = 0.3 * inch
        x2 = self.width - 0.3 * inch - lap_w
        for x, label, sub in ((x1, "BOOT 1", "network on"),
                             (x2, "BOOT 2", "networking off")):
            # laptop body
            c.rect(x, y, lap_w, lap_h, stroke=1, fill=0)
            # screen
            c.rect(x + 0.12 * inch, y + 0.22 * inch, lap_w - 0.24 * inch,
                   lap_h - 0.34 * inch, stroke=1, fill=0)
            c.setFont("Helvetica-Bold", 8)
            c.drawCentredString(x + lap_w / 2, y + lap_h / 2 - 2, label)
            c.setFont("Helvetica", 7)
            c.setFillColor(MUTED)
            c.drawCentredString(x + lap_w / 2, y + lap_h / 2 - 13, sub)
            c.setFillColor(INK)
            # base
            c.rect(x - 0.12 * inch, y - 0.1 * inch, lap_w + 0.24 * inch,
                   0.1 * inch, stroke=1, fill=0)
        # arrow between
        ax1 = x1 + lap_w + 0.12 * inch
        ax2 = x2 - 0.12 * inch
        midy = y + lap_h / 2
        c.setLineWidth(1.5)
        c.line(ax1, midy, ax2 - 8, midy)
        c.line(ax2 - 8, midy, ax2 - 16, midy - 5)
        c.line(ax2 - 8, midy, ax2 - 16, midy + 5)
        c.setFont("Helvetica-Bold", 7.5)
        c.setFillColor(GOLD)
        c.drawCentredString((ax1 + ax2) / 2, midy + 12, "THEN SHUT DOWN")
        c.restoreState()


class LockDrawing(Flowable):
    """2-of-3: three key circles feeding a lock."""
    def __init__(self, width):
        super().__init__()
        self.width = width
        self.height = 1.7 * inch

    def wrap(self, aW, aH):
        return (self.width, self.height)

    def draw(self):
        c = self.canv
        c.saveState()
        c.setStrokeColor(INK)
        c.setLineWidth(1.2)
        cy = 0.85 * inch
        r = 0.32 * inch
        xs = [1.3 * inch, 2.6 * inch, 3.9 * inch]
        for i, x in enumerate(xs):
            c.circle(x, cy, r, stroke=1, fill=0)
            c.setFont("Helvetica-Bold", 9)
            c.drawCentredString(x, cy - 3, f"KEY {chr(65 + i)}")
        # lock body
        lx, ly, lw, lh = 5.3 * inch, cy - 0.28 * inch, 0.85 * inch, 0.56 * inch
        c.rect(lx, ly, lw, lh, stroke=1, fill=0)
        c.arc(lx + 0.12 * inch, ly + lh - 0.1 * inch, lx + lw - 0.12 * inch,
              ly + lh + 0.3 * inch, startAng=180, extent=180)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(lx + lw / 2, ly + lh / 2 - 3, "LOCK")
        # connector lines run between circles, never through them
        for i in range(len(xs) - 1):
            c.line(xs[i] + r, cy, xs[i + 1] - r, cy)
        c.line(xs[-1] + r, cy, lx, cy)
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(GOLD)
        c.drawCentredString(3.25 * inch, 0.25 * inch,
                            "ANY TWO KEYS OPEN IT — ONE ALONE CANNOT")
        c.restoreState()


class SignFlowDrawing(Flowable):
    """PSBT journey: build -> seed 1 -> seed 2 -> broadcast."""
    def __init__(self, width):
        super().__init__()
        self.width = width
        self.height = 1.6 * inch

    def wrap(self, aW, aH):
        return (self.width, self.height)

    def draw(self):
        c = self.canv
        c.saveState()
        steps = [
            ("WATCH-ONLY", "build unsigned"),
            ("SEED 1", "sign offline"),
            ("SEED 2", "sign offline"),
            ("ONLINE", "broadcast"),
        ]
        n = len(steps)
        bw = 1.45 * inch
        bh = 0.75 * inch
        gap = (self.width - n * bw) / (n - 1)
        y = 0.55 * inch
        c.setStrokeColor(INK)
        c.setLineWidth(1.2)
        for i, (top, sub) in enumerate(steps):
            x = i * (bw + gap)
            c.rect(x, y, bw, bh, stroke=1, fill=0)
            c.setFont("Helvetica-Bold", 8)
            c.setFillColor(INK)
            c.drawCentredString(x + bw / 2, y + bh / 2 + 4, top)
            c.setFont("Helvetica", 7)
            c.setFillColor(MUTED)
            c.drawCentredString(x + bw / 2, y + bh / 2 - 9, sub)
            if i < n - 1:
                c.setStrokeColor(INK)
                x1 = x + bw
                x2 = x + bw + gap
                my = y + bh / 2
                c.line(x1, my, x2 - 7, my)
                c.line(x2 - 7, my, x2 - 13, my - 4)
                c.line(x2 - 7, my, x2 - 13, my + 4)
        c.setFont("Helvetica-Oblique", 7.5)
        c.setFillColor(MUTED)
        c.drawCentredString(self.width / 2, 0.22 * inch,
                            "full shutdown between each signing")
        c.restoreState()


class PlatesDrawing(Flowable):
    """Three plates in three places + the map envelope."""
    def __init__(self, width):
        super().__init__()
        self.width = width
        self.height = 1.6 * inch

    def wrap(self, aW, aH):
        return (self.width, self.height)

    def draw(self):
        c = self.canv
        c.saveState()
        c.setStrokeColor(INK)
        c.setLineWidth(1.2)
        pw, ph = 1.3 * inch, 0.8 * inch
        y = 0.6 * inch
        places = [("HOME", "plate A"), ("PLACE 2", "plate B"), ("PLACE 3", "plate C")]
        for i, (place, plate) in enumerate(places):
            x = 0.15 * inch + i * (pw + 0.3 * inch)
            c.rect(x, y, pw, ph, stroke=1, fill=0)
            c.setFont("Helvetica-Bold", 8)
            c.setFillColor(INK)
            c.drawCentredString(x + pw / 2, y + ph / 2 + 4, place)
            c.setFont("Helvetica", 7)
            c.setFillColor(MUTED)
            c.drawCentredString(x + pw / 2, y + ph / 2 - 9, plate)
        # map envelope gets the remaining width
        ex = 0.15 * inch + 3 * (pw + 0.3 * inch) + 0.15 * inch
        ew = self.width - ex - 0.15 * inch
        c.setStrokeColor(GOLD)
        c.rect(ex, y, ew, ph, stroke=1, fill=0)
        c.line(ex, y + ph, ex + ew / 2, y + ph / 2)
        c.line(ex + ew, y + ph, ex + ew / 2, y + ph / 2)
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(GOLD)
        c.drawCentredString(ex + ew / 2, y + ph / 2 + 4, "MAP")
        c.setFont("Helvetica", 7)
        c.drawCentredString(ex + ew / 2, y + ph / 2 - 9, "encrypted")
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(GOLD)
        c.drawCentredString(self.width / 2, 0.25 * inch,
                            "HEIR NEEDS ANY TWO PLATES + THE MAP")
        c.restoreState()


# ------------------------------------------------------- header/footer
QR_SIZE = 0.62 * inch
PAGE_URLS = {}  # filled per page


def header_footer(canvas, doc):
    canvas.saveState()
    page_num = canvas.getPageNumber()
    sheet = PAGE_URLS.get(page_num, ("", BASE + "/"))
    sheet_name, url = sheet
    # header
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(GOLD)
    canvas.drawString(MARGIN, PAGE_H - 0.55 * inch, "PLEBUM DOMINIUM")
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(MARGIN + 1.35 * inch, PAGE_H - 0.55 * inch,
                      f"·  {sheet_name}")
    # QR top-right, clear of text
    qr = QrCodeWidget(url)
    qr.barWidth = QR_SIZE
    qr.barHeight = QR_SIZE
    d = Drawing(QR_SIZE, QR_SIZE)
    d.add(qr)
    d.drawOn(canvas, PAGE_W - MARGIN - QR_SIZE, PAGE_H - 0.78 * inch)
    canvas.setFont("Helvetica", 6.5)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - 0.88 * inch,
                           "scan for the full sheet")
    # rule
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.75)
    canvas.line(MARGIN, PAGE_H - 0.95 * inch, PAGE_W - MARGIN, PAGE_H - 0.95 * inch)
    # footer
    canvas.setFont("Helvetica-Oblique", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(MARGIN, 0.55 * inch,
                      "Stop if a check fails. Do not skip ahead.")
    canvas.setFont("Helvetica", 7.5)
    canvas.drawRightString(PAGE_W - MARGIN, 0.55 * inch,
                           f"Page {page_num} of 10")
    canvas.restoreState()


# ------------------------------------------------------- page builders
def p_overview():
    PAGE_URLS[1] = ("PRINT PACKET", BASE + "/")
    return [
        Paragraph("Print packet", sTitle),
        Paragraph("The handouts, in the order of the work. "
                  "These are the same sheets as on the site — condensed for paper. "
                  "If a check fails, the work stops.", sBody),
        Spacer(1, 4),
        Paragraph("The sheets, in order", sH1),
        *bullets([
            "<b>Terms</b> — the words used in this guide.",
            "<b>Checklist</b> — everything gathered before the first boot.",
            "<b>Check the files</b> — fingerprints and signatures before going offline.",
            "<b>Two boots</b> — one computer, two boots; Tails with networking Disabled, no persistent storage.",
            "<b>Dice</b> — five casino dice make the randomness; 256 bits exactly.",
            "<b>Build the 2-of-3</b> — Sparrow 2.5.5. Export xpubs, build the wallet map.",
            "<b>Practice spend</b> — a dust payment, two signatures, then broadcast.",
            "<b>Metal and the map</b> — three titanium plates, three places.",
            "<b>Hide the wallet map</b> — encrypted. The passphrase is not a seed.",
            "<b>If I am gone</b> — the inheritance sheet for the heir.",
            "<b>Tough questions</b> — the challenges, answered straight.",
        ]),
        *stopbox("A failed check is not a delay. Delete the file, fix the step, "
                 "start that sheet over."),
        Paragraph("House rules", sH1),
        *bullets([
            "No photos of seeds, plates, or screens. Ever.",
            "The everyday computer is watch-only. It never holds a seed.",
            "Hardware wallets are optional — they never create the keys.",
        ]),
    ]


def p_terms():
    PAGE_URLS[2] = ("TERMS", BASE + "/handouts/terms")
    terms = [
        ("entropy", "The randomness made with the dice. It is the material the 24 words are built from."),
        ("airgap / Tails", "Each key is made on a computer that is offline. Tails runs from a USB stick and forgets the session at shutdown."),
        ("networking off", "Tails booted with networking Disabled. No Wi-Fi, no cable, no Bluetooth."),
        ("2-of-3 native SegWit (P2WSH)", "A wallet that needs any two of three keys before it can spend. One key alone cannot move the fund."),
        ("m/48'/0'/0'/2'", "The path Sparrow follows for this kind of wallet. It is confirmed on screen, never typed from memory."),
        ("PSBT", "An unsigned payment file carried on the USB stick. The seed stays on the offline computer."),
        ("descriptor / xpub", "The descriptor is the wallet map; an xpub is a public watch key. Either one can watch the money — neither can spend it."),
        ("BIP39", "The standard list of 2,048 words a seed is written in. Word 24 is a checksum — it is never invented."),
        ("hash", "The fingerprint of a download. The fingerprint on the source must match the one the computer prints, or the file is deleted."),
        ("signature", "A signature is the project confirming the file. If the signature fails, the file is deleted and downloaded again."),
        ("zero-trust", "Nobody's word is accepted for a download or a key. Two tools must agree."),
        ("watch-only", "A wallet that can see balances and build payments but holds no seed and cannot sign."),
    ]
    left, right = [], []
    for i, (t, d) in enumerate(terms):
        cell = [Paragraph(t, sTerm), Paragraph(d, sDef)]
        (left if i % 2 == 0 else right).append(cell)
    rows = []
    for i in range(max(len(left), len(right))):
        l = left[i] if i < len(left) else [Paragraph("", sDef)]
        r = right[i] if i < len(right) else [Paragraph("", sDef)]
        rows.append([l, r])
    tbl = Table(rows, colWidths=[3.55 * inch, 3.55 * inch])
    tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return [
        Paragraph("Terms", sTitle),
        Paragraph("The words used in this guide, and what they mean.", sBody),
        Spacer(1, 4),
        tbl,
    ]


def p_checklist():
    PAGE_URLS[3] = ("CHECKLIST", BASE + "/handouts/checklist")
    return [
        Paragraph("Checklist & file checks", sTitle),
        Paragraph("Everything gathered and verified before the first boot.", sBody),
        Paragraph("Materials", sH1),
        *bullets([
            "Two USB sticks: one for Tails, one for the checked files.",
            "Three titanium plates — one seed each, three separate places. "
            "StampSeed kit holds one plate (buy two more); Cryptotag holds two (buy one more). Never mix methods.",
            "Five casino dice, paper, pen. A metal stamp set.",
            "The everyday computer — watch-only. It never holds a seed.",
        ]),
        Paragraph("Downloads — pinned, from official sources only", sH1),
        *bullets([
            "<b>Tails 7.13.</b> On its own USB. Networking Disabled. No persistent storage.",
            "<b>Sparrow 2.5.5 — exact.</b> A newer download that does not match is a stop, not an upgrade.",
            "<b>Electrum 4.8.2.</b> The second tool that must agree.",
            "<b>The Ian Coleman page</b> (bip39-standalone.html). Open it only while offline.",
            "<b>The dice converter.</b> Its fingerprint is in VERIFY.md.",
        ]),
        Paragraph("Verify before going offline", sH1),
        *bullets([
            "Hash, then signature, on every file. A failure means delete the file and stop.",
            "The GPG warning “not certified with a trusted signature” is expected — the fingerprint match is the check.",
            "Run the kit's verify script: it checks fingerprints first, then signatures. One failure and the kit is not copied.",
        ]),
        *stopbox("A download that does not match is a stop, not an upgrade."),
    ]


def p_airgap():
    PAGE_URLS[4] = ("AIRGAP", BASE + "/handouts/airgap")
    w = PAGE_W - 2 * MARGIN
    return [
        Paragraph("The airgap: two boots", sTitle),
        Paragraph("One computer, two completely separate lives. "
                  "Nothing carries over between them except files you choose to move.", sBody),
        Spacer(1, 6),
        BootsDrawing(w),
        Spacer(1, 4),
        Paragraph("Boot 1 — this computer, network on", sH2),
        *bullets([
            "Verify the downloaded files. Build the watch-only wallet.",
            "Build payments here. This machine never sees a seed.",
        ]),
        Paragraph("Then: full shutdown", sH2),
        *bullets([
            "Power all the way off. Not sleep, not hibernate — off.",
        ]),
        Paragraph("Boot 2 — the Tails USB, networking Disabled", sH2),
        *bullets([
            "Tails borrows the hardware and forgets everything at shutdown.",
            "No persistent storage. One seed in memory at a time.",
            "Full shutdown again before the next seed.",
        ]),
        *stopbox("If Tails ever shows networking on, stop. Reboot with it Disabled."),
    ]


def p_dice():
    PAGE_URLS[5] = ("DICE", BASE + "/handouts/dice")
    story = [
        Paragraph("Dice recording sheet", sTitle),
        Paragraph("Five dice per shake. Write <b>00</b> for 1, <b>01</b> for 2, "
                  "<b>10</b> for 3, <b>11</b> for 4. Leave a cell blank if that die was 5 or 6. "
                  "26 shakes ≈ 260 bits — stop at exactly <b>256 bits</b>. "
                  "Do not photograph this sheet. Destroy it after the 24 words are stamped and verified.", sBody),
        Spacer(1, 4),
    ]
    # header line: seed / date / reader / checker
    hdr = Table([
        [Paragraph("<b>Seed #</b> ___ &nbsp;&nbsp; <b>Date</b> __________ &nbsp;&nbsp; "
                   "<b>Reader</b> __________ &nbsp;&nbsp; <b>Checker</b> __________", sSmall)]
    ], colWidths=[PAGE_W - 2 * MARGIN])
    hdr.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.75, RULE),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story += [hdr, Spacer(1, 6)]
    # grid: 26 shakes x 5 dice + bits
    cols = ["#", "Die 1", "Die 2", "Die 3", "Die 4", "Die 5", "Bits this shake"]
    widths = [0.35 * inch] + [0.85 * inch] * 5 + [1.95 * inch]
    data = [[Paragraph(f"<b>{c}</b>", sSmall) for c in cols]]
    for i in range(1, 27):
        data.append([Paragraph(str(i), sSmall)] + [Paragraph("", sSmall)] * 6)
    grid = Table(data, colWidths=widths, rowHeights=[0.22 * inch] + [0.24 * inch] * 26)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.5, RULE),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1c1917")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]
    for r in range(1, 27, 2):
        style.append(("BACKGROUND", (0, r), (-1, r), colors.HexColor("#faf7f2")))
    grid.setStyle(TableStyle(style))
    story += [grid, Spacer(1, 4),
              Paragraph("Running bit count (filled pairs × 2): ______ &nbsp;&nbsp; "
                        "Target: <b>256</b> (aim 320–400 shakes of margin, then trim to 256). "
                        "The converter and the offline Ian Coleman page must print identical 24 words.", sSmall)]
    return story


def p_sparrow():
    PAGE_URLS[6] = ("BUILD THE 2-OF-3", BASE + "/handouts/sparrow")
    w = PAGE_W - 2 * MARGIN
    return [
        Paragraph("Build the 2-of-3", sTitle),
        Paragraph("Sparrow 2.5.5. One boot per seed — then a fresh boot with no seed to build the wallet.", sBody),
        Spacer(1, 4),
        LockDrawing(w),
        Spacer(1, 2),
        Paragraph("One boot per seed", sH2),
        *bullets([
            "Boot Tails. Enter seed 1 (typed from the stamped plate, never pasted). Export its <b>xpub</b>. Full shutdown.",
            "Repeat for seed 2. Full shutdown. Repeat for seed 3. Full shutdown.",
            "One seed in memory at a time. Never two.",
        ]),
        Paragraph("Then a fresh boot with no seed", sH2),
        *bullets([
            "Import the three xpubs. Set the script type to <b>native SegWit (P2WSH)</b>.",
            "Confirm the path reads <b>m/48'/0'/0'/2'</b> on screen.",
            "Export the <b>output descriptor</b> — the wallet map. This is the watch-only file.",
            "Cross-check: the first addresses must match in Electrum with no seed. Two tools agree, or the work stops.",
        ]),
        *stopbox("An address mismatch between Sparrow and Electrum is a stop. Do not fund it."),
    ]


def p_signing():
    PAGE_URLS[7] = ("PRACTICE SPEND", BASE + "/handouts/signing")
    w = PAGE_W - 2 * MARGIN
    return [
        Paragraph("Practice spend", sTitle),
        Paragraph("A dust payment first — small amount, two signatures, then broadcast. "
                  "Only after the practice spend confirms does savings money move.", sBody),
        Spacer(1, 4),
        SignFlowDrawing(w),
        Spacer(1, 2),
        Paragraph("The signing ceremony", sH2),
        *bullets([
            "<b>Online:</b> the watch-only wallet builds the payment and exports the unsigned PSBT file.",
            "<b>Offline, seed 1:</b> boot Tails, enter seed 1, sign the file. Full shutdown.",
            "<b>Offline, seed 2:</b> fresh boot, enter seed 2, sign the file. Full shutdown.",
            "<b>Online:</b> broadcast the twice-signed file. Wait for confirmation.",
        ]),
        Paragraph("Why two shutdowns", sH2),
        *bullets([
            "Each seed lives in memory alone. A shutdown is the eraser — nothing carries over.",
            "The signed file is the only thing that travels, on the USB stick.",
        ]),
        *stopbox("If a signature fails to verify, stop. Rebuild the file — do not force it."),
    ]


def p_titanium():
    PAGE_URLS[8] = ("METAL AND THE MAP", BASE + "/handouts/titanium")
    return [
        Paragraph("Metal and the map", sTitle),
        Paragraph("Paper is not the backup. Three titanium plates — one seed each, three separate places.", sBody),
        Paragraph("The plates", sH2),
        *bullets([
            "One plate per seed. Three plates, three places — never two in the same place.",
            "StampSeed kit holds one plate (buy two more). Cryptotag holds two (buy one more). Never mix methods.",
            "Stamp in an unhurried, private setting. No camera in the room.",
        ]),
        Paragraph("What goes on each plate", sH2),
        *bullets([
            "Plate A: seed 1 only. Plate B: seed 2 only. Plate C: seed 3 only.",
            "<b>No passphrase on the 2-of-3.</b> The plates hold words, nothing else.",
            "The derivation path (m/48'/0'/0'/2') goes on the inheritance sheet — it is not a secret.",
        ]),
        Paragraph("The plate that stays home", sH2),
        *bullets([
            "The home plate doubles as a small decoy single-sig wallet. Leave a little in it.",
            "Its passphrase lives on paper, somewhere else — never on the plate.",
            "Read every plate back, then do a restore check, before the paper is destroyed.",
        ]),
        *stopbox("Paper is destroyed only after the restore check passes. Not before."),
    ]


def p_inheritance():
    PAGE_URLS[9] = ("HIDE THE MAP · IF I AM GONE", BASE + "/handouts/encryption")
    w = PAGE_W - 2 * MARGIN
    return [
        Paragraph("Hide the map · If I am gone", sTitle),
        Spacer(1, 2),
        PlatesDrawing(w),
        Spacer(1, 2),
        Paragraph("The wallet map is encrypted", sH2),
        *bullets([
            "The output descriptor is encrypted with the site's tool (real AES-256).",
            "The passphrase is <b>a single point of failure</b>: back it up on paper in <b>two separate places</b>, away from the plates and USBs.",
            "<b>Two plates + a readable map</b> spends. <b>Three plates</b> rebuild the map exactly.",
            "Two plates + only-encrypted maps + a lost passphrase does <b>not</b> spend. A homemade cipher is not used.",
        ]),
        Paragraph("The inheritance sheet", sH2),
        *bullets([
            "The heir needs any two plates plus the map.",
            "They buy a Jade from Blockstream's shop and a BitBox from BitBox's shop — one plate per device.",
            "Words are never typed into a phone or a website. A small test send comes first.",
        ]),
        *stopbox("The map passphrase on paper, twice, away from everything else — or the map is a brick."),
    ]


def p_briefing():
    PAGE_URLS[10] = ("TOUGH QUESTIONS", BASE + "/handouts/briefing")
    qa = [
        ("The words were typed on a laptop — isn't that the thing we never do?",
         "On Tails, with networking off, from a full shutdown. Tails runs from memory and forgets the session. "
         "A captured keylogger still cannot spend: the fund needs two keys, and the seeds are never typed on the same boot."),
        ("Why not start with a SeedSigner?",
         "A SeedSigner is a signer that can be added later. It is not how the keys are made. "
         "The randomness is dice; the computer is offline and airgapped. That is the letter for heirs: one plate in a hole, one plate in a fire safe."),
        ("Dice versus a hardware random generator?",
         "Dice are inspectable — you can watch the randomness happen. A chip's RNG is a black box you must trust. "
         "The guide chooses the thing you can verify with your own eyes."),
        ("The map passphrase is lost — are the coins gone?",
         "That passphrase hides the map; it does not spend. Two plates plus a readable map still spends. "
         "Three plates rebuild the map exactly. But two plates with only encrypted maps and a lost passphrase does not — "
         "which is why the passphrase paper exists in two places."),
        ("Someone finds one plate — what do they have?",
         "Twenty-four words and no map. One key cannot move a 2-of-3 fund. "
         "They would need a second plate and the map — or the passphrase papers and the encrypted map."),
        ("Why no passphrase on the multisig itself?",
         "A passphrase on the 2-of-3 turns three independent keys into one shared secret with three copies. "
         "The security is the separation: any two plates, three places, no single thing to find."),
    ]
    story = [
        Paragraph("Tough questions", sTitle),
        Paragraph("The challenges people raise against this method — answered straight.", sBody),
    ]
    for q, a in qa:
        story += [Paragraph(q, sQ), Paragraph(a, sA)]
    story += [Spacer(1, 8),
              Paragraph("The full guide, the kit, and the videos live at plebumbtc.io. "
                        "This packet is the paper companion — the site is the reference.", sSmall)]
    return story


BUILDERS = [p_overview, p_terms, p_checklist, p_airgap, p_dice,
            p_sparrow, p_signing, p_titanium, p_inheritance, p_briefing]


def main():
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "kit", "02_Print_Packet.pdf")
    doc = SimpleDocTemplate(
        out, pagesize=letter,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=1.15 * inch, bottomMargin=0.8 * inch,
        title="Plebum Dominium — Print Packet",
        author="Plebum Dominium",
    )
    story = []
    for i, build in enumerate(BUILDERS):
        if i > 0:
            # page break is implicit: each builder starts a new page
            from reportlab.platypus import PageBreak
            story.append(PageBreak())
        story.extend(build())
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    import subprocess
    n = subprocess.run(["pdfinfo", out], capture_output=True,
                       text=True).stdout
    for line in n.splitlines():
        if line.startswith("Pages:"):
            print("built", out, "->", line.strip())


if __name__ == "__main__":
    main()
