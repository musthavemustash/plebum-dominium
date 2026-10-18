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
import html as htmlmod

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

# (slug, number, title) in workflow order
SHEETS = [
    ("terms", "T", "Terms"),
    ("checklist", "03", "Checklist"),
    ("airgap", "04", "Two boots"),
    ("verify", "05", "Check the files"),
    ("dice", "06", "Make the three keys"),
    ("sparrow", "07", "Build the 2-of-3"),
    ("signing", "08", "Practice spend"),
    ("titanium", "09", "Metal and the map"),
    ("encryption", "11", "Hide the wallet map"),
    ("inheritance", "12", "If I am gone"),
    ("faq", "13", "If you get stuck"),
    ("briefing", "14", "Tough questions"),
]
SLUG_TO_IDX = {slug: i for i, (slug, _, _) in enumerate(SHEETS)}


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
        m = re.match(r"^(#{1,3})\s+(.*)$", stripped)
        if m:
            close_list()
            level = len(m.group(1))
            text = m.group(2)
            anchor = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
            out.append(f'<h{level} id="{anchor}">{inline(text)}</h{level}>')
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
    return html


# ---------------------------------------------------------------- templates
def load_template():
    with open("templates/base.html") as f:
        return f.read()


def sidebar_html(active_slug):
    items = []
    for slug, num, title in SHEETS:
        cls = "active" if slug == active_slug else ""
        items.append(
            f'<li><a href="{BASE}handouts/{slug}.html" class="{cls}" data-sheet="{slug}">'
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
                   "Geography: three plates in three places — one fire cannot finish you."),
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


def sheet_diagram(slug):
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
        tpl.replace("{{title}}", f"{num} · {title} — {SITE_NAME}")
        .replace("{{base}}", BASE)
        .replace("{{kicker}}", f"{num} · Plebum Dominium")
        .replace("{{heading}}", esc(title))
        .replace("{{sidebar}}", sidebar_html(slug))
        .replace("{{toc}}", toc_html(rendered))
        .replace("{{content}}", sheet_diagram(slug) + rendered)
        .replace("{{prev}}", prev_link)
        .replace("{{next}}", next_link)
        .replace("{{is_home}}", "")
    )
    return page


# ---------------------------------------------------------------- home sections
def home_section(name):
    with open(f"templates/{name}.html") as f:
        return f.read().replace("{BASE}", BASE)


def build_home():
    with open("content/index.md") as f:
        src = f.read()
    tpl = load_template()
    # homepage uses a custom cards layout; keep the scraped intro, drop chrome junk
    cards = []
    stages = [
        ("Get ready", [("terms", "T"), ("checklist", "03"), ("airgap", "04"), ("verify", "05")]),
        ("Make the keys", [("dice", "06"), ("sparrow", "07")]),
        ("Prove it works", [("signing", "08")]),
        ("Lock it in metal", [("titanium", "09"), ("encryption", "11")]),
        ("Plan for others", [("inheritance", "12")]),
        ("Reference", [("faq", "13"), ("briefing", "14")]),
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
        '<div class="coin" aria-hidden="true"><span>\u20bf</span></div>'
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
        '<div class="keyring" aria-label="Animation: any two of the three keys open the lock">'
        '<div class="keys" aria-hidden="true">'
        '<span class="key key-a">A</span><span class="key key-b">B</span><span class="key key-c">C</span>'
        "</div>"
        '<div class="lockwrap" aria-hidden="true"><div class="shackle"></div><div class="lockbody">2-of-3</div></div>'
        '<p class="keyring-caption"><strong>Any two keys</strong> open it. One alone cannot.</p>'
        "</div></div>"
        .replace("{BASE}", BASE)
        + home_section("home-why")
        + home_section("home-process")
        + "\n".join(cards)
        + home_section("home-rules")
        + home_section("home-resources")
    )
    page = (
        tpl.replace("{{title}}", f"{SITE_NAME} — {SITE_TAGLINE}")
        .replace("{{base}}", BASE)
        .replace("{{kicker}}", SITE_TAGLINE)
        .replace("{{heading}}", SITE_NAME)
        .replace("{{sidebar}}", sidebar_html("__home__"))
        .replace("{{toc}}", "")
        .replace("{{content}}", content)
        .replace("{{prev}}", "")
        .replace("{{next}}", "")
        .replace("{{is_home}}", "home")
    )
    return page


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
    # static assets
    shutil.copytree("assets", "docs/assets")
    # kit downloads
    shutil.copytree("kit", "docs/kit")
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
