#!/usr/bin/env python3
"""One-time scraper: fetch plebumbtc.io pages and convert article HTML to Markdown.

Usage: python3 scripts/scrape.py
Writes content/index.md and content/handouts/*.md (faithful to the live site;
fixes are applied separately by scripts/apply-fixes.py).
"""
import re
import html as htmlmod
import urllib.request
from html.parser import HTMLParser

BASE = "https://plebumbtc.io"
PAGES = [
    ("", "content/index.md"),
    ("handouts/checklist", "content/handouts/checklist.md"),
    ("handouts/airgap", "content/handouts/airgap.md"),
    ("handouts/verify", "content/handouts/verify.md"),
    ("handouts/dice", "content/handouts/dice.md"),
    ("handouts/sparrow", "content/handouts/sparrow.md"),
    ("handouts/signing", "content/handouts/signing.md"),
    ("handouts/titanium", "content/handouts/titanium.md"),
    ("handouts/encryption", "content/handouts/encryption.md"),
    ("handouts/inheritance", "content/handouts/inheritance.md"),
    ("handouts/faq", "content/handouts/faq.md"),
    ("handouts/terms", "content/handouts/terms.md"),
    ("handouts/briefing", "content/handouts/briefing.md"),
]

SKIP_CLASSES = ("no-print",)  # UI chrome (download buttons etc.)


class MDConverter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.out = []
        self.skip_depth = 0
        self.in_pre = False
        self.in_style_script = 0
        self.list_stack = []  # 'ul' or ('ol', counter)
        self._href_stack = []

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script"):
            self.in_style_script += 1
            return
        if self.in_style_script:
            return
        attrs = dict(attrs)
        cls = attrs.get("class", "")
        if tag == "div" and any(s in cls for s in SKIP_CLASSES):
            self.skip_depth += 1
            return
        if self.skip_depth:
            return
        if tag in ("h1", "h2", "h3"):
            self.out.append("\n\n" + "#" * int(tag[1]) + " ")
        elif tag == "p":
            self.out.append("\n\n")
        elif tag == "ul":
            self.list_stack.append("ul")
            self.out.append("\n")
        elif tag == "ol":
            self.list_stack.append(["ol", 0])
            self.out.append("\n")
        elif tag == "li":
            depth = len(self.list_stack)
            if self.list_stack and self.list_stack[-1] == "ul":
                self.out.append("\n" + "  " * (depth - 1) + "- ")
            elif self.list_stack:
                self.list_stack[-1][1] += 1
                n = self.list_stack[-1][1]
                self.out.append("\n" + "  " * (depth - 1) + f"{n}. ")
            else:
                self.out.append("\n- ")
        elif tag == "pre":
            self.in_pre = True
            self.out.append("\n\n```\n")
        elif tag == "code" and not self.in_pre:
            self.out.append("`")
        elif tag == "a":
            self.out.append("[")
            self._href_stack.append(attrs.get("href", ""))
        elif tag in ("strong", "b"):
            self.out.append("**")
        elif tag in ("em", "i"):
            self.out.append("*")
        elif tag == "img":
            alt = attrs.get("alt", "")
            src = attrs.get("src", "")
            self.out.append(f"\n\n![{alt}]({src})\n\n")
        elif tag == "blockquote":
            self.out.append("\n\n> ")
        elif tag == "hr":
            self.out.append("\n\n---\n\n")
        elif tag == "br":
            self.out.append("\n")
        elif tag == "dl":
            self.out.append("\n")
        elif tag == "dt":
            self.out.append("\n\n**")
        elif tag == "dd":
            self.out.append("**\n\n")

    def handle_endtag(self, tag):
        if tag in ("style", "script"):
            self.in_style_script = max(0, self.in_style_script - 1)
            return
        if self.in_style_script:
            return
        if tag == "div" and self.skip_depth:
            self.skip_depth -= 1
            return
        if self.skip_depth:
            return
        if tag in ("ul", "ol"):
            if self.list_stack:
                self.list_stack.pop()
            self.out.append("\n")
        elif tag == "pre":
            self.in_pre = False
            self.out.append("\n```\n")
        elif tag == "code" and not self.in_pre:
            self.out.append("`")
        elif tag == "a" and self._href_stack:
            href = self._href_stack.pop()
            self.out.append(f"]({href})")
        elif tag in ("strong", "b"):
            self.out.append("**")
        elif tag in ("em", "i"):
            self.out.append("*")
        elif tag in ("h1", "h2", "h3", "p", "li"):
            pass  # closings need no marker

    def handle_data(self, data):
        if self.skip_depth or self.in_style_script:
            return
        if self.in_pre:
            self.out.append(data)
        else:
            # collapse whitespace but keep single spaces
            text = re.sub(r"\s+", " ", data)
            if text.strip():
                # fix link text: we opened "[href](" at start; need "[text](href)"
                self.out.append(text)

    def get_markdown(self):
        md = "".join(self.out)
        md = re.sub(r"\n{3,}", "\n\n", md)
        # drop empty links
        md = re.sub(r"\[\s*\]\([^)]*\)", "", md)
        return md.strip() + "\n"


def fetch(path):
    req = urllib.request.Request(BASE + "/" + path, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def extract_article(html, path):
    if path == "":
        # homepage: content lives in <main>, not a single <article>
        m = re.search(r'<main[^>]*>(.*?)</main>', html, re.S)
        if not m:
            raise ValueError("no <main> found")
        return m.group(1)
    m = re.search(r"<article[^>]*>(.*?)</article>", html, re.S)
    if not m:
        raise ValueError("no <article> found")
    return m.group(1)


def main():
    import os
    os.chdir(os.path.join(os.path.dirname(__file__), ".."))
    for path, dest in PAGES:
        print(f"fetching /{path} -> {dest}")
        html = fetch(path)
        art = extract_article(html, path)
        conv = MDConverter()
        conv.feed(art)
        md = conv.get_markdown()
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w") as f:
            f.write(md)
    print("done.")


if __name__ == "__main__":
    main()
