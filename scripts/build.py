#!/usr/bin/env python3
"""Build the static site: content/*.md -> docs/ (GitHub Pages serves docs/).

Usage: python3 scripts/build.py [--serve]
  --serve  build, then serve docs/ on http://localhost:8000 for preview.

No dependencies beyond Python 3. Everything is generated; edit the
Markdown in content/, re-run this script, commit, push.
"""
import os
import re
import shutil
import sys
import hashlib
import html as htmlmod
import json
from html.parser import HTMLParser

ROOT = os.path.join(os.path.dirname(__file__), "..")
os.chdir(ROOT)

# Base path for all absolute URLs. GitHub Pages project sites live under a
# subpath (/plebum-dominium/); the custom domain serves from root (/).
#   preview:  python3 scripts/build.py --base /plebum-dominium/
#   custom domain: python3 scripts/build.py --base /
BASE = "/plebum-dominium/"
if "--base" in sys.argv:
    BASE = sys.argv[sys.argv.index("--base") + 1]
    if not BASE.endswith("/"):
        BASE += "/"

SITE_URL = "https://plebumbtc.io"
SITE_NAME = "Plebum Dominium"
SITE_TAGLINE = "Independent At-Home Bitcoin Self-Custody"
# Lightning address for the footer donate button.
LIGHTNING_ADDRESS = "musthavemoresats@speed.app"
from datetime import date as _bdate
LAST_UPDATED = _bdate.today().strftime("%B %-d, %Y")
# Scrolling news ticker at the top of the homepage: (headline, month) pairs
# in newest-first order, matching the entries on the News page. Update this
# list when a new entry lands.
# Ticker headlines: (headline, date, link target, extra class). The first
# item is the permanent Start here action; the rest link to their article
# on news.html. Keep the CSS loop time near 20 seconds per headline when
# this list grows.
NEWS_TICKER = [
    ("New to Bitcoin? Start here →", "", "#new-to-bitcoin", "ticker-action"),
    ("Coinbase vendor breach exposes customer contact data", "Oct 2026", "news.html#coinbase-amplitude", ""),
    ("Keystone breach exposes customer shipping addresses", "Oct 2026", "news.html#keystone-breach", ""),
    ("State Bank of India: 3,897 customer records on the dark web", "Oct 2026", "news.html#sbi-breach", ""),
    ("South Korea: hacking incidents at seven banks linked to one attacker", "Oct 2026", "news.html#south-korea-banks", ""),
    ("Two hardware failures in one year", "Oct 2026", "news.html#two-hardware-failures", ""),
    ("Russia closes the exchange off-ramp", "Oct 2026", "news.html#russia-off-ramp", ""),
    ("FTX collapses, $8 billion in customer funds missing", "Nov 2022", "news.html#ftx", ""),
    ("Ledger breach exposes 272,000 customer addresses", "Jul 2020", "news.html#ledger-breach", ""),
    ("QuadrigaCX dies with its founder, $190 million locked away", "Jan 2019", "news.html#quadrigacx", ""),
    ("Mt. Gox loses 850,000 bitcoin", "Feb 2014", "news.html#mt-gox", ""),
]
# On-chain Bitcoin address for the footer donate button.
ONCHAIN_ADDRESS = "bc1qcmvj7c79gyjrcg3zu5pxnp4mav54846epktyma4n6v8jsud2fhqsczmngw"
# GoatCounter site code for private visitor counts. Empty = no tracking.
# When set, fill in the code (the part before .goatcounter.com) after creating
# the site at goatcounter.com; the dashboard is private by default (no badge).
GOATCOUNTER_CODE = "plebumbtc"

# (slug, number, title) in workflow order
SHEETS = [
    ("terms", "T", "Terms"),
    ("threat-model", "02", "Before you begin"),
    ("checklist", "03", "Checklist"),
    ("verify", "05", "Check the files"),
    ("airgap", "04", "Two boots"),
    ("dice", "06", "Make the three keys"),
    ("sparrow", "07", "Build the 2-of-3"),
    ("testnet", "10", "Rehearse on testnet"),
    ("signing", "08", "Practice spend"),
    ("titanium", "09", "Metal and the map"),
    ("encryption", "11", "Hide the wallet map"),
    ("inheritance", "12", "If I am gone"),
    ("faq", "13", "If you get stuck"),
    ("briefing", "14", "Tough questions"),
    ("fire-card", "15", "Recovery card"),
    ("single-sig", "16", "One key, done right"),
    ("two-devices", "17", "Two devices and one dice key"),
]
SLUG_TO_IDX = {slug: i for i, (slug, _, _) in enumerate(SHEETS)}

# which paths include each sheet. easy = words into one trusted
# device, one = one key plus a passphrase, full = the 2-of-3 program as written.
SHEET_PATHS = {
    "terms": ["easy", "one", "full"],
    "threat-model": ["easy", "one", "full"],
    "checklist": ["easy", "one", "full"],
    "verify": ["easy", "one", "full"],
    "airgap": ["easy", "one", "full"],
    "dice": ["easy", "one", "full"],
    "sparrow": ["full"],
    "testnet": ["full"],
    "signing": ["full"],
    "titanium": ["easy", "one", "full"],
    "encryption": ["full"],
    "inheritance": ["easy", "one", "full"],
    "faq": ["easy", "one", "full"],
    "briefing": ["full"],
    "fire-card": ["one", "full"],
    "single-sig": ["one", "full"],
    "two-devices": ["full"],
}



# (time, difficulty, needs, steps) for the iFixit-style overview card on each sheet
SHEET_META = {
    "terms":        ("10 min", "Easy", ["Nothing, just read"], "10 terms"),
    "threat-model": ("15 min", "Easy", ["Pen and paper"], "1 worksheet"),
    "checklist":    ("30 min + shopping", "Moderate", ["This sheet", "A budget for the kit"], "11 items"),
    "verify":       ("30 min", "Careful", ["The downloaded files", "Two verification tools"], "7 sections"),
    "airgap":       ("45 min", "Careful", ["Everyday computer", "Tails USB"], "4 sections"),
    "dice":         ("30-45 min", "Moderate", ["5 dice", "Paper and pen", "The worksheet"], "4 sections"),
    "sparrow":      ("45-60 min", "Careful", ["The three paper keys", "Verified Sparrow"], "9 sections"),
    "testnet":      ("30 min", "Moderate", ["Sparrow", "Free testnet coins"], "2 sections"),
    "signing":      ("45 min", "Careful", ["Two seeds", "Tails USB", "A small test amount"], "5 sections"),
    "titanium":     ("1-2 hours", "Moderate", ["Titanium plates", "Metal stamp set", "The paper keys"], "4 sections"),
    "encryption":   ("30 min", "Careful", ["descriptor_obfuscator.py (verified)", "A dice passphrase"], "7 sections"),
    "inheritance":  ("1 hour", "Moderate", ["Your finished kit", "Your trusted person"], "6 sections"),
    "faq":          ("10 min", "Easy", ["Nothing, find your question"], "7 questions"),
    "briefing":     ("15 min", "Easy", ["Nothing, read and discuss"], "6 questions"),
    "fire-card":    ("15 min", "Easy", ["Printer", "Scissors"], "3 steps"),
    "single-sig":   ("1-2 hours", "Careful", ["Your hardware wallet", "Titanium plates", "Pen and paper"], "8 sections"),
    "two-devices":  ("1-2 hours", "Moderate", ["Two hardware devices", "5 dice", "Titanium plates"], "8 sections"),
}


# Where each "You will need" item is sourced or checked. Items not listed
# here stay plain text (household items, outputs of the reader's own work).
NEED_LINKS = {
    "5 dice": "handouts/checklist.html",
    "Paper and pen": "handouts/checklist.html",
    "Pen and paper": "handouts/checklist.html",
    "Everyday computer": "handouts/checklist.html",
    "Tails USB": "handouts/checklist.html",
    "Titanium plates": "handouts/checklist.html",
    "Metal stamp set": "handouts/checklist.html",
    "The downloaded files": "handouts/verify.html",
    "Two verification tools": "handouts/verify.html",
    "Verified Sparrow": "handouts/verify.html",
    "Sparrow": "handouts/verify.html",
    "descriptor_obfuscator.py (verified)": "handouts/verify.html",
    "The three paper keys": "handouts/dice.html",
    "The paper keys": "handouts/dice.html",
    "Two seeds": "handouts/dice.html",
    "The worksheet": "downloads.html",
}


def need_html(item, slug=None):
    target = NEED_LINKS.get(item)
    # A need sourced on this very sheet stays plain text: linking to the
    # page the reader is already on looks like a dead link.
    if target and target != f"handouts/{slug}.html":
        return f'<a href="{BASE}{target}">{esc(item)}</a>'
    return esc(item)


def step_banner_html(slug):
    """Top banner: 'Step N of M · Title' with prev/next links, from SHEETS order."""
    idx = SLUG_TO_IDX[slug]
    n, m = idx + 1, len(SHEETS)
    _, _, title = SHEETS[idx]
    parts = [f'<nav class="step-banner" aria-label="Sheet {n} of {m}">']
    if idx > 0:
        s, pn, pt = SHEETS[idx - 1]
        parts.append(
            f'<a class="step-nav" href="{BASE}handouts/{s}.html" rel="prev">'
            f"&larr; {pn} &middot; {esc(pt)}</a>"
        )
    else:
        parts.append('<span class="step-nav step-none" aria-hidden="true"></span>')
    parts.append(
        f'<span class="step-pos"><strong>Step {n} of {m}</strong> · {esc(title)}</span>'
    )
    if idx < len(SHEETS) - 1:
        s, nn, nt = SHEETS[idx + 1]
        parts.append(
            f'<a class="step-nav" href="{BASE}handouts/{s}.html" rel="next">'
            f"{nn} &middot; {esc(nt)} &rarr;</a>"
        )
    else:
        parts.append('<span class="step-nav step-none" aria-hidden="true"></span>')
    parts.append("</nav>")
    return "".join(parts)


def step_pos_html(slug):
    """Bottom-row position label: 'Step N of M · Title'."""
    idx = SLUG_TO_IDX[slug]
    _, _, title = SHEETS[idx]
    return (
        f'<span class="step-pos-bottom"><strong>Step {idx + 1} of {len(SHEETS)}</strong>'
        f" · {esc(title)}</span>"
    )


def header_card_html(slug):
    """iFixit-style overview card: time, difficulty, steps, you-will-need."""
    time, diff, needs, steps = SHEET_META[slug]
    diff_cls = {"Easy": "diff-easy", "Moderate": "diff-moderate", "Careful": "diff-careful"}[diff]
    needs_html = " &middot; ".join(need_html(x, slug) for x in needs)
    return (
        '<section class="sheet-meta" aria-label="Sheet overview">'
        f'<div class="meta-item"><span class="meta-label">Time</span>'
        f'<span class="meta-val">{esc(time)}</span></div>'
        f'<div class="meta-item"><span class="meta-label">Difficulty</span>'
        f'<span class="meta-val {diff_cls}">{diff}</span></div>'
        f'<div class="meta-item"><span class="meta-label">Steps</span>'
        f'<span class="meta-val">{esc(steps)}</span></div>'
        f'<div class="meta-item meta-needs"><span class="meta-label">You will need</span>'
        f'<span class="meta-val">{needs_html}</span></div>'
        "</section>"
    )


# ---------------------------------------------------------------- Markdown
def esc(s):
    return htmlmod.escape(s)


def inline(md):
    """Inline Markdown: code, bold, italic, links, images."""
    md = esc(md)
    md = re.sub(r"`([^`]+)`", r"<code>\1</code>", md)
    md = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", md)
    md = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", md)
    md = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1" loading="lazy">', md)
    md = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', md)
    # site-absolute paths must respect the base path (project pages live under a subpath)
    md = re.sub(r'(href|src)="/(?!/)', rf"\1=\"{BASE}", md)
    return md


CALLOUTS = {
    "STOP": ("stop", "Stop"),
    "WARNING": ("warning", "Warning"),
    "TIP": ("tip", "Tip"),
    "NOTE": ("note", "Note"),
}


def render_markdown(src):
    """Minimal Markdown renderer for the sheet content."""
    lines = src.split("\n")
    out = []
    i = 0
    in_code = False
    in_list = None  # 'ul' or 'ol'
    in_callout = None
    callout_buf = []

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>" if in_list == "ul" else "</ol>")
            in_list = None

    def close_callout():
        nonlocal in_callout, callout_buf
        if in_callout:
            cls, label = CALLOUTS[in_callout]
            body = "".join(callout_buf)
            out.append(
                f'<aside class="callout callout-{cls}" role="note">'
                f'<p class="callout-label">{label}</p>{body}</aside>'
            )
            in_callout, callout_buf = None, []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            close_list(); close_callout()
            in_code = not in_code
            out.append("<pre><code>" if in_code else "</code></pre>")
            i += 1
            continue
        if in_code:
            out.append(esc(line) + "\n")
            i += 1
            continue

        # callout syntax: > [!STOP] ... (blockquote lines following belong to it)
        m = re.match(r"^>\s*\[!(STOP|WARNING|TIP|NOTE)\]\s*(.*)$", stripped)
        if m:
            close_list(); close_callout()
            in_callout = m.group(1)
            rest = m.group(2).strip()
            if rest:
                callout_buf.append(f"<p>{inline(rest)}</p>")
            i += 1
            continue
        if in_callout:
            if stripped.startswith(">"):
                callout_buf.append(f"<p>{inline(stripped[1:].strip())}</p>")
                i += 1
                continue
            elif stripped == "":
                i += 1
                continue
            else:
                close_callout()
                # fall through to normal handling of this line

        if not stripped:
            close_list()
            i += 1
            continue
        if stripped == "---":
            close_list()
            out.append("<hr>")
            i += 1
            continue
        m = re.match(r"^::anim\s+([a-z0-9-]+)/([a-z0-9-]+)$", stripped)
        if m:
            close_list(); close_callout()
            try:
                with open(f"templates/{m.group(1)}-figs/{m.group(2)}.html") as f:
                    anim = f.read()
                out.append(anim)
            except FileNotFoundError:
                out.append(f'<!-- missing animation {m.group(1)}/{m.group(2)} -->')
            i += 1
            continue
        m = re.match(r"^::fig\s+([a-z0-9-]+)/([a-z0-9-]+)$", stripped)
        if m:
            close_list(); close_callout()
            try:
                with open(f"templates/{m.group(1)}-figs/{m.group(2)}.svg") as f:
                    svg = f.read()
                out.append(f'<figure class="step-fig">{svg}</figure>')
            except FileNotFoundError:
                out.append(f'<!-- missing figure {m.group(1)}/{m.group(2)} -->')
            i += 1
            continue
        m = re.match(r"^::shot\s+([a-z0-9-]+)/([a-z0-9-]+)$", stripped)
        if m:
            close_list(); close_callout()
            try:
                with open(f"templates/{m.group(1)}-shots/{m.group(2)}.html") as f:
                    shot = f.read().replace("{BASE}", BASE)
                out.append(shot)
            except FileNotFoundError:
                out.append(f'<!-- missing shot {m.group(1)}/{m.group(2)} -->')
            i += 1
            continue
        m = re.match(r"^(#{1,3})\s+(.*)$", stripped)
        if m:
            close_list()
            level = len(m.group(1))
            text = m.group(2)
            anchor = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
            out.append(f'<h{level} id="{anchor}">{inline(text)}</h{level}>')
            i += 1
            continue
        m = re.match(r"^\^\*\s+(.*)$", stripped)
        if m:
            close_list()
            out.append(f'<p class="footnote">* {inline(m.group(1))}</p>')
            i += 1
            continue
        m = re.match(r"^[-*]\s+(.*)$", stripped)
        if m:
            if in_list != "ul":
                close_list(); out.append("<ul>"); in_list = "ul"
            out.append(f"<li>{inline(m.group(1))}</li>")
            i += 1
            continue
        m = re.match(r"^(\d+)[.)]\s+(.*)$", stripped)
        if m:
            if in_list != "ol":
                close_list(); out.append("<ol>"); in_list = "ol"
            out.append(f"<li>{inline(m.group(2))}</li>")
            i += 1
            continue
        if stripped.startswith("> "):
            close_list()
            out.append(f"<blockquote><p>{inline(stripped[2:])}</p></blockquote>")
            i += 1
            continue
        # paragraph: gather continuation lines
        close_list()
        para = [stripped]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(
            r"^(#{1,3}\s|[-*]\s|\d+[.)]\s|```|>|---$)", lines[i].strip()
        ):
            para.append(lines[i].strip())
            i += 1
        out.append(f"<p>{inline(' '.join(para))}</p>")

    close_list(); close_callout()
    return "\n".join(out)


def post_process(html):
    """Sheet-level transforms: '## Stop if' -> STOP callout, '## What is required' -> you-need box."""
    # "Stop if" section: <h2 id="stop-if">...</h2> followed by <ul>...</ul> -> callout
    def stop_repl(m):
        items = m.group(1)
        return (
            '<aside class="callout callout-stop" role="alert">'
            '<p class="callout-label">Stop if</p>'
            f"{items}</aside>"
        )
    html = re.sub(
        r'<h2 id="stop-if">Stop if</h2>\s*(<ul>.*?</ul>)',
        stop_repl, html, flags=re.S,
    )
    # "What is required" -> you-need box
    def need_repl(m):
        items = m.group(1)
        return (
            '<section class="you-need"><p class="you-need-label">What is required</p>'
            f"{items}</section>"
        )
    html = re.sub(
        r'<h2 id="what-is-required">What is required</h2>\s*((?:<ul>.*?</ul>|<p>.*?</p>\s*)+)',
        need_repl, html, flags=re.S,
    )
    # Tails terminal demo in encryption Step 2: iframe on screen, Step 2 figure print only.
    def demo_repl(m):
        return (
            m.group(1)
            + '\n<div class="demo-embed"><iframe src="'
            + BASE
            + 'tails-demo.html" title="Tails terminal demo" loading="lazy"></iframe>'
            + '<p class="demo-fullscreen"><a href="'
            + BASE
            + 'tails-demo.html">Open the demo full screen</a></p></div>'
            + '\n<figure class="step-fig print-only">'
            + m.group(2)
            + '</figure>'
        )
    html = re.sub(
        r'(<h2 id="step-2-run-the-tool-choose-e-enter-the-passphrase">.*?</h2>)\s*<figure class="step-fig">(.*?)</figure>',
        demo_repl, html, flags=re.S,
    )
    # Step 1 networking demo in encryption Step 1: iframe on screen, Step 1 figure stays on screen too.
    def step1_demo_repl(m):
        return (
            m.group(1)
            + '\n<div class="demo-embed"><iframe src="'
            + BASE
            + 'step1-demo.html" title="Step 1 networking demo" loading="lazy"></iframe>'
            + '<p class="demo-fullscreen"><a href="'
            + BASE
            + 'step1-demo.html">Open the demo full screen</a></p></div>'
            + '\n<figure class="step-fig">'
            + m.group(2)
            + '</figure>'
        )
    html = re.sub(
        r'(<h2 id="step-1-boot-tails-copy-the-tool-and-the-map">.*?</h2>)\s*<figure class="step-fig">(.*?)</figure>',
        step1_demo_repl, html, flags=re.S,
    )
    # path toggle at the end of Before you begin and the dice sheet.
    if 'id="where-are-your-coins-right-now"' in html:
        with open("templates/path-toggle-before.html") as f:
            html += "\n" + f.read().replace("{BASE}", BASE)
    if 'id="practice-grid"' in html:
        with open("templates/path-toggle-dice.html") as f:
            html += "\n" + f.read().replace("{BASE}", BASE)
    return html


# ---------------------------------------------------------------- templates
# Per-page search descriptions (meta description / og / twitter), written in
# the guide's plain voice. One per page: sheets keyed by slug, plus the
# standalone pages.
HOME_DESCRIPTION = ("Plebum Dominium: build a DIY Bitcoin 2-of-3 multisig wallet "
                    "from dice, verified software, and titanium. No company, no custodian.")
DESCRIPTIONS = {
    "terms": "The words this Bitcoin self-custody guide uses (seed, multisig, airgap, descriptor, wallet map), defined in plain language before you start.",
    "threat-model": "Before you begin: the threats a DIY Bitcoin wallet must survive: theft, fire and flood, your own mistakes, scams, and death. And one question: where are your coins right now?",
    "checklist": "Everything to gather before building a DIY Bitcoin 2-of-3 multisig wallet: five dice, titanium plates, two USB drives, and the free software, with prices.",
    "verify": "Check every downloaded file before it touches your keys: SHA-256 hashes and GPG signatures for Tails, Sparrow, Electrum, and the dice tools, step by step.",
    "airgap": "One computer, used twice: an offline Tails boot that holds the seeds, and an everyday watch-only boot that never touches them.",
    "dice": "Make three Bitcoin seed keys from five casino dice: roll 256 bits of entropy, turn them into 24 words, and cross-check them with two independent tools.",
    "sparrow": "Build the 2-of-3 multisig wallet in Sparrow: import the xpubs from your three dice keys, create the wallet, and export the descriptor, your wallet map.",
    "testnet": "Rehearse the whole multisig build on Bitcoin testnet with worthless coins first, so the real run holds no surprises.",
    "signing": "Practice a spend from your 2-of-3 wallet: build the transaction on the watch-only computer, sign it offline with two seeds, then broadcast.",
    "titanium": "Stamp each seed onto its own titanium plate and store the three plates in three separate places, so no single fire, flood, or theft can take your Bitcoin.",
    "encryption": "Encrypt your wallet map (the descriptor) with GPG AES-256 and a dice passphrase, so the map alone tells a finder nothing.",
    "inheritance": "If you are gone: plain-language instructions that let your heir rebuild the wallet from any two titanium plates and the map. No Bitcoin knowledge assumed.",
    "faq": "Stuck mid-build? Answers to the common problems: word lists that don\u2019t match, files that fail verification, checksum errors, and what to do next.",
    "briefing": "Tough questions about DIY Bitcoin self-custody, asked straight: death, fire, mistakes, theft. And the honest answers this guide is built on.",
    "fire-card": "The wallet-sized recovery card: tells your family the wallet exists, what to find, and who to call first. Kept in a wallet or with your will.",
    "single-sig": "The spending wallet that lives on Plate A: Seed 1 plus a passphrase, for spending money while savings sit in the vault.",
    "two-devices": "A 2-of-3 wallet built from two hardware devices and one dice key. No one device, one maker, or one place moves the fund alone.",
    "downloads": "Download the Plebum Dominium kit: every handout as a printable PDF, the full print packet, the recovery card, and the file fingerprints to verify them.",
    "beyond": "Beyond the kit: what to do once your DIY 2-of-3 multisig wallet is built, rehearsed, and funded: maintenance, reviews, and further reading.",
    "news": "News that makes the case for holding your own Bitcoin keys: exchange freezes, closed off-ramps, and custody failures, collected as they happen.",
}

# Sheets whose body is a procedure get HowTo schema; the two Q&A sheets get
# FAQPage schema. Steps/questions are extracted from the rendered body, so
# the schema can never drift from the words on the page.
HOWTO_SHEETS = {"checklist", "verify", "airgap", "dice", "sparrow", "testnet",
                "signing", "titanium", "encryption", "inheritance", "fire-card",
                "single-sig", "two-devices"}
FAQ_SHEETS = {"faq", "briefing"}


def _text_of(fragment):
    txt = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", htmlmod.unescape(txt)).strip()


def _schema_tag(data):
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return f'<script type="application/ld+json">{payload}</script>'


def howto_schema(slug, title, rendered):
    heads = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', rendered, re.S)
    steps = [{"@type": "HowToStep", "position": i + 1, "name": _text_of(h),
              "url": f"https://plebumbtc.io/handouts/{slug}.html#{hid}"}
             for i, (hid, h) in enumerate(heads)]
    if len(steps) < 2:
        return ""
    return _schema_tag({
        "@context": "https://schema.org", "@type": "HowTo",
        "name": title, "description": DESCRIPTIONS[slug], "step": steps})


class _QAExtractor(HTMLParser):
    """Pull (question, answer-text) pairs out of <div class="qa"> blocks."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pairs = []
        self._depth = 0
        self._cur = None
        self._in_h3 = False

    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get("class", "")
        if tag == "div" and "qa" in cls.split():
            self._cur = {"q": "", "a": []}
            self._depth = 1
        elif self._cur is not None and tag == "div":
            self._depth += 1
        if self._cur is not None and tag == "h3":
            self._in_h3 = True

    def handle_endtag(self, tag):
        if self._cur is not None and tag == "h3":
            self._in_h3 = False
        if self._cur is not None and tag == "div":
            self._depth -= 1
            if self._depth == 0:
                q = re.sub(r"\s+", " ", self._cur["q"]).strip()
                a = re.sub(r"\s+", " ", " ".join(self._cur["a"])).strip()
                if q and a:
                    self.pairs.append((q, a))
                self._cur = None

    def handle_data(self, data):
        if self._cur is None:
            return
        if self._in_h3:
            self._cur["q"] += data
        else:
            self._cur["a"].append(data)


def faq_schema(rendered):
    ex = _QAExtractor()
    ex.feed(rendered)
    if len(ex.pairs) < 2:
        return ""
    return _schema_tag({
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a}}
                       for q, a in ex.pairs]})


def sheet_schema(slug, title, rendered):
    if slug in HOWTO_SHEETS:
        return howto_schema(slug, title, rendered)
    if slug in FAQ_SHEETS:
        return faq_schema(rendered)
    return ""


def website_schema():
    return _schema_tag({
        "@context": "https://schema.org", "@type": "WebSite",
        "name": SITE_NAME, "url": "https://plebumbtc.io/",
        "description": HOME_DESCRIPTION})


def ticker_html():
    """Slow headlines bar above the header. One readable set plus hidden
    repeats, so the loop scrolls seamlessly and screen readers hear each
    headline once. Each item links to its own article on news.html, except
    the permanent Start here action. The price span beside the label is
    filled by JavaScript when it can fetch a price, and stays hidden when
    it cannot."""
    def item(head, date, href, cls):
        cls_attr = "ticker-item" + (f" {cls}" if cls else "")
        date_html = f' <span class="ticker-date">{esc(date)}</span>' if date else ""
        return (
            f'<a class="{cls_attr}" href="{BASE}{href}">{esc(head)}{date_html}</a>'
            '<span class="ticker-sep" aria-hidden="true">·</span>'
        )
    items = "".join(item(*entry) for entry in NEWS_TICKER)
    hidden = f'<span class="ticker-set" aria-hidden="true">{items}</span>'
    return (
        '<div class="news-ticker" aria-label="Latest news">'
        f'<a class="ticker-label" href="{BASE}news.html">News</a>'
        '<span class="ticker-price" id="ticker-price" hidden></span>'
        '<div class="ticker-viewport"><div class="ticker-track">'
        f'<span class="ticker-set">{items}</span>'
        f"{hidden}{hidden}{hidden}"
        "</div></div></div>"
    )


def load_template(with_ticker=False):
    with open("templates/base.html") as f:
        return f.read().replace("{{ticker}}", ticker_html() if with_ticker else "")


def analytics_html():
    """Private GoatCounter snippet (dashboard only, no public badge). Empty code = nothing."""
    if not GOATCOUNTER_CODE:
        return ""
    code = GOATCOUNTER_CODE.strip()
    return (
        f'<script data-goatcounter="https://{code}.goatcounter.com/count" '
        'async src="//gc.zgo.at/count.js"></script>'
    )


def sidebar_html(active_slug):
    items = []
    for slug, num, title in SHEETS:
        cls = "active" if slug == active_slug else ""
        items.append(
            f'<li data-paths="{" ".join(SHEET_PATHS.get(slug, ["full"]))}"><a href="{BASE}handouts/{slug}.html" class="{cls}" data-sheet="{slug}">'
            f'<span class="sheet-num">{num}</span>'
            f'<span class="sheet-title">{esc(title)}</span>'
            f'<span class="sheet-check" aria-hidden="true">✓</span>'
            f"</a></li>"
        )
    return "\n".join(items)


def toc_html(rendered):
    heads = re.findall(r'<h2 id="([^"]+)">([^<]+)</h2>', rendered)
    if not heads:
        return ""
    items = "".join(
        f'<li><a href="#{hid}" data-toc="{hid}">{esc(text)}</a></li>'
        for hid, text in heads
    )
    return f"<nav class=\"toc\" aria-label=\"On this sheet\"><p>On this sheet</p><ul>{items}</ul></nav>"


def prev_next(active_slug):
    idx = SLUG_TO_IDX[active_slug]
    prev_link, next_link = "", ""
    if idx > 0:
        s, n, t = SHEETS[idx - 1]
        prev_link = f'<a class="prevnext prev" href="{BASE}handouts/{s}.html"><span>← {n} · {esc(t)}</span></a>'
    if idx < len(SHEETS) - 1:
        s, n, t = SHEETS[idx + 1]
        next_link = f'<a class="prevnext next" href="{BASE}handouts/{s}.html"><span>{n} · {esc(t)} →</span></a>'
    return prev_link, next_link


# diagrams that belong to specific sheets (file, caption).
# airgap uses the animated two-boots loop instead of the static PNG.
# signing uses the animated filling-file loop instead of the static PNG.
# dice uses the animated three-shakes loop instead of the static PNG.
# titanium uses the animated three-plates loop instead of the static PNG.
# sparrow uses inline step figures instead of the static PNG.
SHEET_DIAGRAMS = {
    "encryption": ("diagram-06_split_map.png",
                   "Geography: three plates in three places. No single point of failure."),
}


def airgap_animation():
    return (
        '<div class="boots-anim" role="img" aria-label="Animation: Boot 1 builds the payment online, '
        "the machine shuts down, Boot 2 signs offline on Tails.\">"
        '<div class="boot boot1">'
        '<div class="boot-label">Boot 1 · Network on</div>'
        "<h4>This computer</h4>"
        "<p>Watches balances. Builds a payment. Never holds a seed.</p>"
        '<div class="laptop"><div class="screen">Network on</div></div>'
        "<ul><li>Verify files</li><li>Watch-only wallet</li><li>Export unsigned file</li></ul>"
        "</div>"
        '<div class="then">then<br>shut down</div>'
        '<div class="boot boot2">'
        '<div class="boot-label">Boot 2 · Networking off</div>'
        "<h4>Tails USB</h4>"
        "<p>This stick is the offline computer. It borrows the hardware, then forgets.</p>"
        '<div class="laptop"><div class="screen">Networking off</div></div>'
        "<ul><li>One seed in memory</li><li>Sign the file</li><li>Full shutdown after</li></ul>"
        "</div></div>"
    )


def signing_animation():
    with open("templates/signing-animation.html") as f:
        return f.read()


def dice_animation():
    with open("templates/dice-animation.html") as f:
        return f.read()


def titanium_animation():
    with open("templates/metal-animation.html") as f:
        return f.read()


def encryption_geography():
    # Responsive replacement for the old wide PNG: real text at readable
    # sizes, three cards in a row on desktop, stacked on mobile.
    cards = [
        ("HOUSE 1", "Plate A", "Seed 1 only", "Home safe / fire box",
         "Wallet map lives here too", "(the map is not a third seed)"),
        ("HOUSE 2", "Plate B", "Seed 2 only", "Different building, different risk",
         "A copy of the map may sit here", ""),
        ("HOUSE 3", "Plate C", "Seed 3 only", "Another town or trusted party",
         "Do not park Seed 1 or 2 here", ""),
    ]
    parts = ['<div class="geo-fig" role="img" aria-label="Geography: 3 seeds, secured separately in 3 different locations. No single point of failure.">']
    parts.append('<p class="geo-kicker">Geography</p>')
    parts.append('<p class="geo-head">3 seeds, secured separately in 3 different locations</p>')
    parts.append('<div class="geo-cards">')
    for house, plate, seed, place, mapline, note in cards:
        parts.append(
            '<div class="geo-card">'
            f'<p class="geo-house">{house}</p>'
            f'<p class="geo-plate">{plate}</p>'
            f'<p class="geo-detail">{seed}</p>'
            f'<p class="geo-detail">{place}</p>'
            f'<p class="geo-map">{mapline}</p>'
            + (f'<p class="geo-note">{note}</p>' if note else '')
            + '</div>'
        )
    parts.append('</div></div>')
    img, caption = SHEET_DIAGRAMS["encryption"]
    return (f'<figure class="sheet-diagram">{"".join(parts)}'
            f'<figcaption>{esc(caption)}</figcaption></figure>')


def sheet_diagram(slug):
    if slug == "encryption":
        return encryption_geography()
    if slug == "airgap":
        return airgap_animation()
    if slug == "signing":
        return signing_animation()
    if slug == "dice":
        return dice_animation()
    if slug == "titanium":
        return titanium_animation()
    if slug not in SHEET_DIAGRAMS:
        return ""
    img, caption = SHEET_DIAGRAMS[slug]
    return (
        f'<figure class="sheet-diagram">'
        f'<img src="{BASE}assets/img/{img}" alt="{esc(caption)}" loading="lazy">'
        f"<figcaption>{esc(caption)}</figcaption></figure>"
    )


def build_sheet(slug, num, title):
    custom = f"templates/sheets/{slug}.html"
    if os.path.exists(custom):
        # fully custom sheet body (approved preview HTML); diagram still prepended
        with open(custom) as f:
            rendered = f.read()
    else:
        with open(f"content/handouts/{slug}.md") as f:
            src = f.read()
        # strip the scraped "NN · Plebum Dominium" kicker and duplicate H1 (template adds them)
        src = re.sub(r"^[^\n]*Plebum Dominium\n\n", "", src, count=1)
        src = re.sub(r"^# .+\n\n", "", src, count=1)
        # strip prev/next links at the end (template adds them)
        src = re.sub(r"\[.+?\]\((/handouts/[^)]+)\)\[.+?\]\((/handouts/[^)]+)\)\s*$", "", src)
        src = re.sub(r"\[[^\]]+\]\(/handouts/[^)]+\)", "", src)
        rendered = post_process(render_markdown(src))
    tpl = load_template()
    prev_link, next_link = prev_next(slug)
    page = (
        tpl.replace("{{title}}", f"{num} · {title} · {SITE_NAME}")
        .replace("{{base}}", BASE)
        .replace("{{kicker}}", f"{num} · Plebum Dominium")
        .replace("{{heading}}", esc(title))
        .replace("{{sidebar}}", sidebar_html(slug))
        .replace("{{toc}}", toc_html(rendered))
        .replace("{{content}}", sheet_diagram(slug) + rendered)
        # fingerprint the rendered content (card + diagram + body) for VERIFY.md
        .replace("{{prev}}", prev_link)
        .replace("{{next}}", next_link)
        .replace("{{stepbanner}}", step_banner_html(slug))
        .replace("{{steppos}}", step_pos_html(slug))
        .replace("{{headercard}}", header_card_html(slug))
        .replace("{{is_home}}", "")
        .replace("{{lightning_address}}", LIGHTNING_ADDRESS)
        .replace("{{onchain_address}}", ONCHAIN_ADDRESS)
        .replace("{{canonical}}", f"https://plebumbtc.io/handouts/{slug}.html")
        .replace("{{description}}", DESCRIPTIONS[slug])
        .replace("{{schema}}", sheet_schema(slug, title, rendered))
        .replace("{{last_updated}}", LAST_UPDATED)
        .replace("{{analytics}}", analytics_html())
    )
    fp_src = header_card_html(slug) + sheet_diagram(slug) + rendered
    PAGE_FINGERPRINTS[slug] = hashlib.sha256(fp_src.encode("utf-8")).hexdigest()
    SEARCH_INDEX.append({
        "slug": slug, "num": num, "title": title,
        "url": f"{BASE}handouts/{slug}.html",
        "text": strip_text(fp_src),
    })
    return page


def build_downloads():
    tpl = load_template()
    with open("templates/downloads.html") as f:
        rendered = f.read().replace("{BASE}", BASE)
    page = (
        tpl.replace("{{title}}", f"Downloads · {SITE_NAME}")
        .replace("{{base}}", BASE)
        .replace("{{kicker}}", "Plebum Dominium")
        .replace("{{heading}}", "Downloads")
        .replace("{{sidebar}}", sidebar_html("__downloads__"))
        .replace("{{toc}}", "")
        .replace("{{content}}", rendered)
        .replace("{{prev}}", "")
        .replace("{{next}}", "")
        .replace("{{stepbanner}}", "")
        .replace("{{steppos}}", "")
        .replace("{{headercard}}", "")
        .replace("{{is_home}}", "")
        .replace("{{lightning_address}}", LIGHTNING_ADDRESS)
        .replace("{{onchain_address}}", ONCHAIN_ADDRESS)
        .replace("{{canonical}}", "https://plebumbtc.io/downloads.html")
        .replace("{{description}}", DESCRIPTIONS["downloads"])
        .replace("{{schema}}", "")
        .replace("{{last_updated}}", LAST_UPDATED)
        .replace("{{analytics}}", analytics_html())
    )
    return page


def build_beyond():
    tpl = load_template()
    with open("templates/beyond.html") as f:
        rendered = f.read().replace("{BASE}", BASE)
    page = (
        tpl.replace("{{title}}", f"Beyond the kit · {SITE_NAME}")
        .replace("{{base}}", BASE)
        .replace("{{kicker}}", "Plebum Dominium")
        .replace("{{heading}}", "Beyond the kit")
        .replace("{{sidebar}}", sidebar_html("__beyond__"))
        .replace("{{toc}}", "")
        .replace("{{content}}", rendered)
        .replace("{{prev}}", "")
        .replace("{{next}}", "")
        .replace("{{stepbanner}}", "")
        .replace("{{steppos}}", "")
        .replace("{{headercard}}", "")
        .replace("{{is_home}}", "")
        .replace("{{lightning_address}}", LIGHTNING_ADDRESS)
        .replace("{{onchain_address}}", ONCHAIN_ADDRESS)
        .replace("{{canonical}}", "https://plebumbtc.io/beyond.html")
        .replace("{{description}}", DESCRIPTIONS["beyond"])
        .replace("{{schema}}", "")
        .replace("{{last_updated}}", LAST_UPDATED)
        .replace("{{analytics}}", analytics_html())
    )
    return page


def build_news():
    tpl = load_template()
    with open("templates/news.html") as f:
        rendered = f.read().replace("{BASE}", BASE)
    for m in re.finditer(r'<article[^>]*id="([^"]+)"[^>]*>(.*?)</article>', rendered, re.S):
        aid, body = m.group(1), m.group(2)
        hm = re.search(r"<h2>(.*?)</h2>", body, re.S)
        if hm:
            SEARCH_INDEX.append({
                "slug": "news-" + aid, "num": "News",
                "title": strip_text(hm.group(1)),
                "url": f"{BASE}news.html#{aid}",
                "text": strip_text(body),
            })
    page = (
        tpl.replace("{{title}}", f"News · {SITE_NAME}")
        .replace("{{base}}", BASE)
        .replace("{{kicker}}", "Plebum Dominium")
        .replace("{{heading}}", "News")
        .replace("{{sidebar}}", sidebar_html("__news__"))
        .replace("{{toc}}", "")
        .replace("{{content}}", rendered)
        .replace("{{prev}}", "")
        .replace("{{next}}", "")
        .replace("{{stepbanner}}", "")
        .replace("{{steppos}}", "")
        .replace("{{headercard}}", "")
        .replace("{{is_home}}", "news")
        .replace("{{lightning_address}}", LIGHTNING_ADDRESS)
        .replace("{{onchain_address}}", ONCHAIN_ADDRESS)
        .replace("{{canonical}}", "https://plebumbtc.io/news.html")
        .replace("{{description}}", DESCRIPTIONS["news"])
        .replace("{{schema}}", "")
        .replace("{{last_updated}}", LAST_UPDATED)
        .replace("{{analytics}}", analytics_html())
    )
    return page



def build_path_risks():
    tpl = load_template()
    with open("templates/path-risks.html") as f:
        rendered = f.read().replace("{BASE}", BASE)
    page = (
        tpl.replace("{{title}}", f"Risks of your path · {SITE_NAME}")
        .replace("{{base}}", BASE)
        .replace("{{kicker}}", "Plebum Dominium")
        .replace("{{heading}}", "Risks of your path")
        .replace("{{sidebar}}", sidebar_html("__risks__"))
        .replace("{{toc}}", "")
        .replace("{{content}}", rendered)
        .replace("{{prev}}", "")
        .replace("{{next}}", "")
        .replace("{{stepbanner}}", "")
        .replace("{{steppos}}", "")
        .replace("{{headercard}}", "")
        .replace("{{is_home}}", "")
        .replace("{{lightning_address}}", LIGHTNING_ADDRESS)
        .replace("{{onchain_address}}", ONCHAIN_ADDRESS)
        .replace("{{canonical}}", "https://plebumbtc.io/path-risks.html")
        .replace("{{description}}", "The risks of the path you picked: One device, One key and a passphrase, or Three keys.")
        .replace("{{schema}}", "")
        .replace("{{last_updated}}", LAST_UPDATED)
        .replace("{{analytics}}", analytics_html())
    )
    return page


# ---------------------------------------------------------------- home sections
def home_section(name):
    with open(f"templates/{name}.html") as f:
        return f.read().replace("{BASE}", BASE)


def build_home():
    with open("content/index.md") as f:
        src = f.read()
    tpl = load_template(with_ticker=True)
    # homepage uses a custom cards layout; keep the scraped intro, drop chrome junk
    cards = []
    stages = [
        ("Get ready", [("threat-model", "02"), ("terms", "T"), ("checklist", "03"), ("verify", "05"), ("airgap", "04")]),
        ("Make the keys", [("dice", "06"), ("sparrow", "07")]),
        ("Prove it works", [("testnet", "10"), ("signing", "08")]),
        ("Lock it in metal", [("titanium", "09"), ("encryption", "11")]),
        ("Plan for others", [("inheritance", "12")]),
        ("Reference", [("faq", "13"), ("briefing", "14"), ("fire-card", "15")]),
    ]
    lookup = {s: (n, t) for s, n, t in SHEETS}
    for stage, slugs in stages:
        items = "".join(
            f'<a class="card" href="{BASE}handouts/{s}.html">'
            f'<span class="card-num">{lookup[s][0]}</span>'
            f'<span class="card-title">{esc(lookup[s][1])}</span></a>'
            for s, _ in slugs
        )
        cards.append(f'<section class="stage"><h2>{stage}</h2><div class="cards">{items}</div></section>')
    content = (
        '<div class="hero"><p class="hero-kicker">Independent At-Home Bitcoin Self-Custody</p>'
        '<div class="hero-title-row">'
        '<div class="coin" aria-hidden="true"><div class="coin-inner"><span class="coin-face coin-front">\u20bf</span><span class="coin-face coin-back"><img src="{BASE}assets/img/logo-pleb-key-coin.svg" alt=""></span></div></div>'
        f"<h1>{SITE_NAME}</h1>"
        "</div>"
        '<p class="hero-pron">(PLAY-boom doh-MIN-ee-oom)</p>'
        '<p class="hero-sub">Absolute Ownership by the Common People</p>'
        "<p>\u201cPleb\u201d is an everyday Bitcoiner. \u201cDominium\u201d is Latin for absolute ownership. "
        "This site is for the Bitcoiner who wants to build a secure, self-custody Bitcoin wallet from the ground up, "
        "bypassing the need for a company, an app, or a custodian to manage or store access to their funds.</p>"
        "<p>This guide shows you how to generate entropy with dice, import it into verified software, "
        "and stamp a 2-of-3 multisig wallet into titanium. Hardware wallets are completely optional.</p>"
        '<p><a class="btn" href="{BASE}handouts/terms.html">Start with the terms</a> '
        '<a class="btn btn-ghost" href="{BASE}kit/02_Print_Packet.pdf">Download the print packet</a></p>'
        '<div class="keyring path-hidden" id="keyring-easy" aria-label="Tap the key to open the lock">'
        '<p class="keyring-try">Try it: tap the key.</p>'
        '<div class="keys">'
        '<button type="button" class="key key-easy" aria-pressed="false">Key</button>'
        "</div>"
        '<div class="lockwrap" id="keyring-easy-lock"><div class="shackle"></div><div class="lockbody">1 key</div></div>'
        '<p class="keyring-caption" id="keyring-easy-caption"><strong>One key</strong> opens it. That key is the whole wallet.</p>'
        '<p class="keyring-caption" id="keyring-easy-desc">Tap the key to see it open.</p>'
        '<button type="button" class="keyring-reset" id="keyring-easy-reset" hidden>Reset</button>'
        "</div>"
        '<div class="keyring path-hidden" id="keyring-one" aria-label="Tap the key and the paper to open the lock">'
        '<p class="keyring-try">Try it: tap the key, then tap the paper.</p>'
        '<div class="keys">'
        '<button type="button" class="key key-one" aria-pressed="false">Key</button><button type="button" class="paper paper-one" aria-pressed="false">Paper</button>'
        "</div>"
        '<div class="lockwrap" id="keyring-one-lock"><div class="shackle"></div><div class="lockbody">Key + paper</div></div>'
        '<p class="keyring-caption" id="keyring-one-caption"><strong>Key plus paper</strong> open it. Neither alone can.</p>'
        '<p class="keyring-caption" id="keyring-one-desc">Select the key and the paper to see what opens.</p>'
        '<button type="button" class="keyring-reset" id="keyring-one-reset" hidden>Reset</button>'
        "</div>"
        '<div class="keyring" id="keyring-full" aria-label="Tap any two of the three keys to open the lock">'
        '<p class="keyring-try">Try it: tap a key, then tap a second key.</p>'
        '<div class="keys">'
        '<button type="button" class="key key-a" aria-pressed="false">A</button><button type="button" class="key key-b" aria-pressed="false">B</button><button type="button" class="key key-c" aria-pressed="false">C</button>'
        "</div>"
        '<div class="lockwrap" id="keyring-full-lock"><div class="shackle"></div><div class="lockbody">2-of-3</div></div>'
        '<p class="keyring-caption" id="keyring-full-caption"><strong>Any two keys</strong> open it. One alone cannot.</p>'
        '<p class="keyring-caption" id="keyring-full-desc">Select keys to see if the descriptor is needed.</p>'
        '<button type="button" class="keyring-reset" id="keyring-full-reset" hidden>Reset</button>'
        "</div></div>"
        .replace("{BASE}", BASE)
        + home_section("home-why")
        + home_section("home-process")
        + home_section("path-toggle-home")
        + "\n".join(cards)
        + home_section("home-rules")
        + home_section("home-resources")
    )
    page = (
        tpl.replace("{{title}}", f"{SITE_NAME} · {SITE_TAGLINE}")
        .replace("{{base}}", BASE)
        .replace("{{kicker}}", SITE_TAGLINE)
        .replace("{{heading}}", SITE_NAME)
        .replace("{{sidebar}}", sidebar_html("__home__"))
        .replace("{{toc}}", "")
        .replace("{{content}}", content)
        .replace("{{prev}}", "")
        .replace("{{next}}", "")
        .replace("{{stepbanner}}", "")
        .replace("{{steppos}}", "")
        .replace("{{headercard}}", "")
        .replace("{{is_home}}", "home")
        .replace("{{lightning_address}}", LIGHTNING_ADDRESS)
        .replace("{{onchain_address}}", ONCHAIN_ADDRESS)
        .replace("{{canonical}}", "https://plebumbtc.io/")
        .replace("{{description}}", HOME_DESCRIPTION)
        .replace("{{schema}}", website_schema())
        .replace("{{last_updated}}", LAST_UPDATED)
        .replace("{{analytics}}", analytics_html())
    )
    return page


PAGE_FINGERPRINTS = {}

# Ask the guide search index: one entry per sheet plus one per news
# article, with the full page text. Written to docs/assets/ by main().
SEARCH_INDEX = []


def strip_text(html):
    """Rendered page HTML to plain searchable text."""
    text = re.sub(r"<[^>]+>", " ", html)
    text = htmlmod.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def update_verify_page_fingerprints():
    """Regenerate the sheet-page fingerprint table inside kit/VERIFY.md."""
    path = "kit/VERIFY.md"
    with open(path) as f:
        text = f.read()
    begin = "<!-- BEGIN GENERATED: PAGE FINGERPRINTS (scripts/build.py) -->"
    end = "<!-- END GENERATED: PAGE FINGERPRINTS -->"
    lines = [
        begin,
        "",
        "## Sheet page fingerprints",
        "",
        "Each sheet page on plebumbtc.io is rendered from a fixed source. The",
        "fingerprint below is the SHA-256 of that sheet's rendered content: the",
        "overview card and the article body, without the site header and footer.",
        "If a copy of a sheet does not hash to the value printed here, it is not",
        "the sheet as published.",
        "",
        "| Sheet | Page | SHA-256 |",
        "| --- | --- | --- |",
    ]
    for slug, num, title in SHEETS:
        lines.append(
            f"| {num} \u00b7 {title} | handouts/{slug}.html | `{PAGE_FINGERPRINTS.get(slug, '')}` |"
        )
    lines += ["", end]
    block = "\n".join(lines)
    if begin in text:
        text = re.sub(re.escape(begin) + r".*?" + re.escape(end),
                      lambda m: block, text, flags=re.S)
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    with open(path, "w") as f:
        f.write(text)
    print("  kit/VERIFY.md (page fingerprints)")


def main():
    shutil.rmtree("docs", ignore_errors=True)
    os.makedirs("docs/handouts", exist_ok=True)
    # sheets
    for slug, num, title in SHEETS:
        html = build_sheet(slug, num, title)
        with open(f"docs/handouts/{slug}.html", "w") as f:
            f.write(html)
        print(f"  handouts/{slug}.html")
    # home
    with open("docs/index.html", "w") as f:
        f.write(build_home())
    print("  index.html")
    # downloads
    with open("docs/downloads.html", "w") as f:
        f.write(build_downloads())
    print("  downloads.html")
    # beyond the kit
    with open("docs/beyond.html", "w") as f:
        f.write(build_beyond())
    print("  beyond.html")
    # news
    with open("docs/news.html", "w") as f:
        f.write(build_news())
    print("  news.html")
    # risks of your path 
    with open("docs/path-risks.html", "w") as f:
        f.write(build_path_risks())
    print("  path-risks.html")
    # diceware passphrase mapper (standalone tool page, ships as-is)
    shutil.copy("tools/diceware-mapper.html", "docs/diceware.html")
    print("  diceware.html")
    shutil.copy("tools/tails-python-demo.html", "docs/tails-demo.html")
    print("  tails-demo.html")
    shutil.copy("tools/step1-networking-demo.html", "docs/step1-demo.html")
    print("  step1-demo.html")
    shutil.copy("tools/quorum-demo.html", "docs/quorum-demo.html")
    print("  quorum-demo.html")
    # static assets
    shutil.copytree("assets", "docs/assets")
    # search index for Ask the guide: sheets plus news articles, full text
    with open("docs/assets/search-index.json", "w") as f:
        json.dump(SEARCH_INDEX, f, ensure_ascii=False)
    print(f"  assets/search-index.json ({len(SEARCH_INDEX)} entries)")
    # VERIFY.md page fingerprints (must run before the kit copy)
    update_verify_page_fingerprints()
    # kit downloads
    shutil.copytree("kit", "docs/kit")
    # robots.txt + sitemap.xml (generated so the sitemap never drifts)
    from datetime import date as _date
    _today = _date.today().isoformat()
    _site = "https://plebumbtc.io"
    _pages = ["/", "/downloads.html", "/beyond.html", "/news.html", "/diceware.html"] + [
        f"/handouts/{slug}.html" for slug, _, _ in SHEETS
    ]
    with open("docs/robots.txt", "w") as f:
        f.write("User-agent: *\nAllow: /\n\nSitemap: https://plebumbtc.io/sitemap.xml\n")
    print("  robots.txt")
    _sm = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for _p in _pages:
        _sm.append(f"  <url><loc>{_site}{_p}</loc><lastmod>{_today}</lastmod></url>")
    _sm.append("</urlset>")
    with open("docs/sitemap.xml", "w") as f:
        f.write("\n".join(_sm) + "\n")
    print("  sitemap.xml")
    # GitHub Pages: skip Jekyll; CNAME only for custom-domain builds (base "/").
    # The github.io preview must NOT have it, or Pages redirects to the domain.
    open("docs/.nojekyll", "w").close()
    if BASE == "/":
        with open("docs/CNAME", "w") as f:
            f.write("plebumbtc.io\n")
    elif os.path.exists("docs/CNAME"):
        os.remove("docs/CNAME")
    print("done -> docs/")


if __name__ == "__main__":
    main()
    if "--serve" in sys.argv:
        import http.server, functools
        h = functools.partial(http.server.SimpleHTTPRequestHandler, directory="docs")
        print("serving http://localhost:8000")
        http.server.ThreadingHTTPServer(("127.0.0.1", 8000), h).serve_forever()
