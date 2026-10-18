# Plebum Dominium — website source

The source for **plebumbtc.io**: a step-by-step guide to building a DIY Bitcoin
2-of-3 multisig wallet from dice, verified software, and titanium.

This repo is the cure for builder-dependence. The site is plain Markdown files
turned into static HTML by a small Python script. No AI builder, no credits,
no framework to keep alive.

## The workflow (no Grok needed)

1. **Edit** the Markdown in `content/` (sheets) or `content/handouts/`.
2. **Apply known fixes** (optional, idempotent):
   `python3 scripts/apply-fixes.py`
3. **Build**: `python3 scripts/build.py` → the site appears in `docs/`.
4. **Preview**: `python3 scripts/build.py --serve` → http://localhost:8000
5. **Commit & push**. GitHub Pages serves `docs/` (see DEPLOY.md).

## What's where

| Path | What it is |
|---|---|
| `content/index.md` | Homepage source (currently hand-built in `build.py`; see note) |
| `content/handouts/*.md` | The 12 bench sheets, in Markdown |
| `kit/` | Downloadable kit: PDFs, `.py` tools, `VERIFY.md`, xlsx |
| `assets/css/` | `main.css` (design system), `print.css` (bench-sheet printing) |
| `assets/js/main.js` | Enhancement only: drawer, copy buttons, scrollspy, check-off |
| `assets/img/` | Diagrams, favicon |
| `templates/base.html` | The HTML shell every page is wrapped in |
| `scripts/scrape.py` | One-time importer from the live site (kept for reference) |
| `scripts/apply-fixes.py` | Applies the audit fixes to `content/` (safe to re-run) |
| `scripts/build.py` | Builds `content/` + `templates/` → `docs/` |
| `docs/` | **Generated.** Never edit by hand; rebuild instead. |
| `FIXES.md` | Log of every fix applied and why |
| `DEPLOY.md` | GitHub + Pages + DNS setup, step by step |

## Content conventions

- One `#` H1 per sheet (the template adds the number kicker).
- `## Stop if` followed by a bullet list becomes the red **STOP** callout automatically.
- `## What is required` followed by a list becomes the **You need** box automatically.
- Extra callouts anywhere: `> [!WARNING]` / `> [!TIP]` / `> [!NOTE]` / `> [!STOP]`
  (blockquote lines after the marker belong to the callout).
- Terminal commands go in fenced code blocks — they get a **Copy** button.
- Keep lines under ~70 characters of prose width; the CSS caps the column.

## Design rules (from the research brief)

1. One action per numbered step; bold every UI label, filename, and command.
2. Every sheet: number pill → You-need box → steps → Verify checkpoint → Stop-if → Next sheet.
3. Four callouts only: Stop / Warning / Tip / Note. A fifth is a design bug.
4. Body 17px / 1.65 / ≤72ch, left-aligned. Links amber, underline on hover.
5. Desktop: sticky numbered sidebar + scrollspy TOC. Mobile: drawer + bottom bar, 44px targets.
6. Print stylesheet is mandatory: each sheet starts on a fresh Letter page; steps and callouts never split.
7. Zero-JS baseline: everything reads with JavaScript disabled.

## Homepage note

`content/index.md` is currently a leftover from the scrape. The live homepage
(`docs/index.html`) is assembled in `scripts/build.py::build_home()` from the
sheet list. If the homepage needs real prose editing, move that content into
`content/index.md` and teach `build_home()` to render it — a 20-line change.
