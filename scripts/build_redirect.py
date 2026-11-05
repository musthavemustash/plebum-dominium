#!/usr/bin/env python3
"""Build and verify the temporary production maintenance site."""
import html
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "dist" / "redirect-site"
TARGET = "https://musthavemustash.github.io/plebum-dominium-test/"
STAGING = ["beyond.html","choose-path.html","descriptor-demo.html","descriptor-tool.html","dice-converter-demo.html","dice-converter.html","dice-rolls.html","diceware-mapper.html","diceware.html","downloads.html","fingerprint-checker.html","handouts/airgap.html","handouts/briefing.html","handouts/checklist-easy.html","handouts/checklist-one.html","handouts/checklist.html","handouts/dice-easy.html","handouts/dice-one.html","handouts/dice.html","handouts/encryption.html","handouts/faq-easy.html","handouts/faq-one.html","handouts/faq.html","handouts/fire-card-one.html","handouts/fire-card.html","handouts/inheritance-easy.html","handouts/inheritance-one.html","handouts/inheritance.html","handouts/signing.html","handouts/single-sig.html","handouts/sparrow.html","handouts/terms.html","handouts/testnet.html","handouts/threat-model-easy.html","handouts/threat-model-one.html","handouts/threat-model.html","handouts/titanium-easy.html","handouts/titanium-one.html","handouts/titanium.html","handouts/two-devices.html","handouts/verify.html","index.html","kit/hash_checker.html","new-to-bitcoin.html","news.html","passphrase-demo.html","path-risks.html","paths/one/airgap.html","paths/one/checklist.html","paths/one/choose-path.html","paths/one/dice.html","paths/one/faq.html","paths/one/fire-card.html","paths/one/index.html","paths/one/inheritance.html","paths/one/single-sig.html","paths/one/terms.html","paths/one/threat-model.html","paths/one/titanium.html","paths/one/verify.html","paths/three/airgap.html","paths/three/briefing.html","paths/three/checklist.html","paths/three/choose-path.html","paths/three/dice.html","paths/three/encryption.html","paths/three/faq.html","paths/three/fire-card.html","paths/three/index.html","paths/three/inheritance.html","paths/three/signing.html","paths/three/sparrow.html","paths/three/terms.html","paths/three/testnet.html","paths/three/threat-model.html","paths/three/titanium.html","paths/three/verify.html","previews/dice-animation-light.html","previews/eff-animation-light.html","previews/geo-fig-light.html","previews/metal-animation-light.html","previews/signing-animation-light.html","previews/splash-light.html","previews/step-fig-wrapper-light.html","previews/step1-demo-light.html","previews/tails-demo-light.html","previews/terminal-figs-light.html","previews/verify-signature-light.html","quorum-demo.html","step1-demo.html","tails-demo.html","test-notes.html","test-the-site.html","trade-trust-for-difficulty.html","verify-bundle-demo.html","verify-file.html"]

def page(destination):
    escaped = html.escape(destination, quote=True)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Plebum Dominium · Maintenance</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="{escaped}">
<meta property="og:title" content="Plebum Dominium · Maintenance">
<meta property="og:description" content="Plebum Dominium is undergoing maintenance. Visit the test site to preview the updates.">
<meta property="og:image" content="{TARGET}assets/img/staging-review-card-v1.png">
<meta name="twitter:card" content="summary_large_image">
<style>body{{max-width:40rem;margin:12vh auto;padding:1rem;background:#f6f3ec;color:#35251b;font:18px/1.6 system-ui}}a{{color:#70411f}}.visit{{display:inline-block;padding:.7rem 1rem;background:#8a5a2a;color:#fff;text-decoration:none;border-radius:8px}}.visit:focus-visible{{outline:3px solid #35251b;outline-offset:4px}}.note{{font-size:.9rem;color:#594739}}</style>
</head><body><h1>Plebum Dominium is undergoing maintenance.</h1>
<p>We’re updating the site. You can preview the changes and share feedback on the test site.</p>
<p><a class="visit" href="{escaped}">Visit the test site →</a></p>
<p class="note">The test site is for public review. Use public test data only.</p>
</body></html>'''

def main():
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)
    paths = {p.relative_to(ROOT / "docs").as_posix() for p in (ROOT / "docs").rglob("*.html")}
    paths.update(["index.html", "404.html", "fingerprint-checker.html", "verify-file.html"])
    for path in sorted(paths):
        destination = TARGET + (path if path in STAGING and path != "index.html" else "")
        out = OUTPUT / path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(destination), encoding="utf-8")
    (OUTPUT / "CNAME").write_text("plebumbtc.io\n")
    (OUTPUT / ".nojekyll").touch()
    (OUTPUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
    for path in OUTPUT.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix == ".html":
            source = path.read_text()
            assert '<meta http-equiv="refresh"' not in source
            assert 'location.replace(' not in source
            assert 'href="' + TARGET in source
            assert 'Plebum Dominium is undergoing maintenance.' in source
            assert "<input" not in source and "<form" not in source
        else:
            assert path.relative_to(OUTPUT).as_posix() in {"CNAME", ".nojekyll", "robots.txt"}
    print("Validated", len(paths), "maintenance pages. No production tools or downloads in artifact.")

if __name__ == "__main__":
    main()
