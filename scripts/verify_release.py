#!/usr/bin/env python3
"""Independent release verifier for Plebum Dominium.

Fail-closed: exits nonzero on ANY failed assertion, printing an actionable
error naming the offending file. Checks:

  1. Crypto regression suites (34 Python + 25 JS), by exit status
  2. Every manifest.json entry: file exists, size + SHA-256 match final bytes
  3. PDF File SHA-256 for all listed PDFs; content-hash provenance check
  4. Tools-bundle members byte-identical to canonical sources
  5. Offline ZIP: required assets, no self-nesting, no caches,
     no root-relative local links, offline tools equal canonical bytes
     (except documented HTML link rewrites)
  6. verify-file.html pins match final artifact bytes
  7. All shipped inline JS parses (node --check on extracted scripts)
  8. VERIFY.md File SHA-256 column matches manifest

Usage:
  python3 scripts/verify_release.py --dist <dir> --repo <repo-root>

Exit 0 only if every check passes.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

FAILURES = []

def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name}" + (f" -- {detail}" if detail and not cond else ""),
          flush=True)
    if not cond:
        FAILURES.append(f"{name}: {detail}")

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(65536), b''):
            h.update(c)
    return h.hexdigest()

def run(cmd, cwd):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dist", required=True, help="Release dist/ dir from release.py")
    ap.add_argument("--repo", required=True, help="Repo root the release was built from")
    ap.add_argument("--production", action="store_true",
                    help="Production mode: reject UNVERIFIED hashes, non-40-char "
                         "commits, and commits not matching git HEAD. Fail closed.")
    ap.add_argument("--prestamp-dir", default=None,
                    help="Directory with independently regenerated pre-stamp PDFs. "
                         "When provided, verifier hashes each PDF itself: raw "
                         "SHA-256 of bytes compared against manifest content_sha256, "
                         "and normalized text hash compared against manifest "
                         "content_text_sha256 (Option A provenance).")
    args = ap.parse_args()
    dist = Path(args.dist)
    repo = Path(args.repo)
    production = args.production

    manifest_path = dist / "release-manifest.json"
    check("release-manifest.json exists", manifest_path.exists())
    if FAILURES:
        return finish()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    # --- 0. Production-mode provenance gates (fail closed, run first) ---
    if production:
        # a0. Production requires independent provenance input
        check("production: --prestamp-dir required",
              args.prestamp_dir is not None,
              "production verifier requires --prestamp-dir for independent provenance")
        # a. Manifest must declare production build
        check("production: manifest declares production=true",
              manifest.get("production") is True,
              "release was not built in production mode")
        # b. No UNVERIFIED content hashes allowed (both file and text hashes)
        pdfs_p = manifest.get("pdfs", {})
        for pname, pinfo in pdfs_p.items():
            cs = pinfo.get("content_sha256", "")
            check(f"production: {pname} content hash verified",
                  cs not in ("UNVERIFIED", None, ""),
                  f"content_sha256={cs}")
            # Content-text hash for cross-runner provenance (skip static assets)
            if pname != "Presentation_Handouts.pdf":
                cts = pinfo.get("content_text_sha256", "")
                check(f"production: {pname} content-text hash verified",
                      cts not in ("UNVERIFIED", None, ""),
                      f"content_text_sha256={cts}")
        # c. Source commit must be 40-char hex
        declared = manifest.get("source_commit") or ""
        check("production: source commit is 40-char hex",
              bool(re.fullmatch(r"[0-9a-f]{40}", declared.lower())),
              f"got '{declared[:20]}...'")
        # d. Declared commit must match checked-out HEAD
        try:
            head = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=str(repo),
                capture_output=True, text=True)
            if head.returncode != 0:
                check("production: git HEAD available", False,
                      "cannot determine git HEAD")
            else:
                actual = head.stdout.strip().lower()
                check("production: declared commit matches git HEAD",
                      actual == declared.lower(),
                      f"declared={declared[:12]} head={actual[:12]}")
        except FileNotFoundError:
            check("production: git available", False, "git not found")
        if FAILURES:
            return finish()

    # --- 1. Crypto suites (exit status, not just text) ---
    rc, out, err = run([sys.executable, "tests/test-crypto.py"], cwd=str(repo))
    m = re.search(r"(\d+)\s+passed", out)
    passed = int(m.group(1)) if m else -1
    check("python crypto suite: exit 0", rc == 0, f"exit={rc}")
    check("python crypto suite: 34 passed", passed == 34, f"got {passed}")

    rc, out, err = run(["node", "tests/test-crypto-js.js"], cwd=str(repo))
    m = re.search(r"(\d+)\s+passed", out)
    passed = int(m.group(1)) if m else -1
    check("js crypto suite: exit 0", rc == 0, f"exit={rc}")
    check("js crypto suite: 25 passed", passed == 25, f"got {passed}")

    # --- 2/4. Tools: manifest entries match final bytes ---
    tools = manifest.get("tools", {})
    check("manifest has 6 tools", len(tools) == 6, f"got {len(tools)}")
    for name, info in tools.items():
        p = repo / info["path"]
        check(f"tool exists: {name}", p.exists())
        if p.exists():
            check(f"tool size: {name}",
                  p.stat().st_size == info["size"],
                  f"manifest={info['size']} actual={p.stat().st_size}")
            check(f"tool sha256: {name}",
                  sha256_file(p) == info["sha256"],
                  f"manifest={info['sha256'][:12]} actual={sha256_file(p)[:12]}")

    # --- Bundle ---
    bundle = dist / "tools-bundle.zip"
    check("tools-bundle.zip exists in dist", bundle.exists())
    bman = manifest.get("bundle", {})
    if bundle.exists():
        check("bundle size matches manifest",
              bundle.stat().st_size == bman.get("size"),
              f"manifest={bman.get('size')} actual={bundle.stat().st_size}")
        check("bundle sha256 matches manifest",
              sha256_file(bundle) == bman.get("sha256"))
        with zipfile.ZipFile(bundle) as zf:
            for name, info in tools.items():
                try:
                    member = zf.read(name)
                except KeyError:
                    check(f"bundle member present: {name}", False, "missing")
                    continue
                check(f"bundle member bytes: {name}",
                      hashlib.sha256(member).hexdigest() == info["sha256"],
                      "member differs from canonical source")

    # --- 3. PDFs ---
    # P0-3: exact 17-PDF inventory, independent of manifest entries
    EXPECTED_PDFS = {
        "00_Project_Overview.pdf", "02_Print_Packet.pdf", "03_Checklist.pdf",
        "04_Airgap.pdf", "05_Verify.pdf", "06_Dice.pdf", "07_Sparrow.pdf",
        "08_Signing.pdf", "09_Titanium.pdf", "11_Encryption.pdf",
        "12_Inheritance.pdf", "13_FAQ.pdf", "14_Speaker.pdf",
        "15_Fire_Card.pdf", "Handouts_No_Cover.pdf",
        "Presentation_Handouts.pdf", "Terms.pdf",
    }
    pdfs = manifest.get("pdfs", {})
    check("pdf inventory: manifest declares exactly 17 expected PDFs",
          set(pdfs.keys()) == EXPECTED_PDFS,
          f"missing={EXPECTED_PDFS - set(pdfs.keys())} "
          f"extra={set(pdfs.keys()) - EXPECTED_PDFS}")

    # --- 3b. Provenance: independently regenerated pre-stamp hashes (Option A) ---
    # When --prestamp-dir is provided, the verifier extracts text from each
    # regenerated PDF ITSELF and compares the text hash against the manifest's
    # content_text_sha256. Text hashes are deterministic across runners,
    # unlike full PDF file hashes (which differ due to metadata).
    #
    # STRICT MODE (2026-11-03): Text-hash comparison is deterministic, so
    # mismatches fail the gate. This verifies content integrity without
    # requiring byte-identical PDF generation.
    PROVENANCE_STRICT = True
    if args.prestamp_dir:
        prestamp = Path(args.prestamp_dir)
        check("provenance: prestamp dir exists", prestamp.is_dir(),
              f"not found: {prestamp}")
        # Presentation_Handouts.pdf is a static asset, not generated from source.
        # Independent regeneration (Option A) does not apply; skip provenance.
        # File hash verification still applies via the standard PDF checks.
        PROVENANCE_SKIP = {"Presentation_Handouts.pdf"}
        # Content-text hash: deterministic across runners. Extract text from
        # regenerated PDF, normalize, and hash. This verifies content integrity
        # without requiring byte-identical PDF generation.
        def _text_hash(pdf_path):
            from pypdf import PdfReader
            reader = PdfReader(str(pdf_path))
            full_text = "\n".join(
                (page.extract_text() or "") for page in reader.pages
            )
            normalized = "\n".join(
                line.rstrip() for line in full_text.split("\n") if line.strip()
            )
            return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        if prestamp.is_dir():
            for name, info in pdfs.items():
                if name in PROVENANCE_SKIP:
                    continue
                ppath = prestamp / name
                check(f"provenance: regenerated {name} exists", ppath.exists())
                if not ppath.exists():
                    continue
                # Raw byte hash: SHA-256 of regenerated pre-stamp PDF bytes.
                # This authenticates the published content_sha256 (the hash printed
                # in the PDF footer). Requires byte-identical regeneration.
                expected_raw = info.get("content_sha256", "")
                if expected_raw not in ("UNVERIFIED", None, ""):
                    actual_raw = sha256_file(ppath)
                    check(f"provenance: {name} raw content hash matches regenerated",
                          actual_raw == expected_raw,
                          f"manifest={expected_raw[:12]} regenerated={actual_raw[:12]}")
                # Content-text hash: deterministic across runners. Extract text from
                # regenerated PDF, normalize, and hash. This verifies content
                # semantics as an additional diagnostic check.
                expected = info.get("content_text_sha256", "")
                if expected in ("UNVERIFIED", None, ""):
                    # Skip UNVERIFIED in dev mode; production already rejected these
                    continue
                actual = _text_hash(ppath)
                if PROVENANCE_STRICT:
                    check(f"provenance: {name} content-text hash matches regenerated",
                          actual == expected,
                          f"manifest={expected[:12]} regenerated={actual[:12]}")
                elif actual != expected:
                    # Advisory: log but don't fail
                    print(f"[ADVISORY] provenance: {name} content-text hash "
                          f"mismatch (manifest={expected[:12]} "
                          f"regenerated={actual[:12]}).", flush=True)
    for name, info in pdfs.items():
        p = repo / "kit" / name
        if not p.exists():
            p = repo / "docs" / "kit" / name
        check(f"pdf exists: {name}", p.exists())
        if p.exists():
            check(f"pdf file sha256: {name}",
                  sha256_file(p) == info["file_sha256"],
                  f"manifest={info['file_sha256'][:12]} actual={sha256_file(p)[:12]}")
    # Content-hash provenance: must not equal file hash unless marked UNVERIFIED
    for name, info in pdfs.items():
        cs = info.get("content_sha256", "")
        if cs not in ("UNVERIFIED", None, ""):
            check(f"pdf content hash provenance: {name}",
                  cs != info["file_sha256"],
                  "content hash equals file hash (fabricated)")

    # PDF text extraction: security-critical wording must appear across the PDF set
    # Uses pypdf (already a release dependency). Collection-level check:
    # each canary must appear in at least one PDF (deletion detection).
    try:
        from pypdf import PdfReader
        pdf_canaries = {
            "2-of-3": "multisig threshold",
            "descriptor": "descriptor concept",
        }
        # Extract text from all PDFs
        all_pdf_text = ""
        pdf_count = 0
        for name in pdfs:
            p = repo / "kit" / name
            if not p.exists():
                p = repo / "docs" / "kit" / name
            if not p.exists():
                continue
            try:
                reader = PdfReader(str(p))
                for page in reader.pages:
                    all_pdf_text += page.extract_text() or ""
                pdf_count += 1
            except Exception as e:
                check(f"pdf text extraction: {name}", False, str(e)[:100])
        if pdf_count > 0:
            for needle, label in pdf_canaries.items():
                found = needle in all_pdf_text
                check(f"pdf collection text [{label}]",
                      found,
                      f"'{needle}' found in {pdf_count} PDFs" if found
                      else f"'{needle}' MISSING from all {pdf_count} PDFs")
    except ImportError:
        check("pdf text extraction (pypdf available)", False,
              "pypdf not installed; cannot verify PDF text")

    # --- 6. verify-file.html pins ---
    vpage = repo / "docs" / "verify-file.html"
    if vpage.exists():
        html = vpage.read_text(encoding="utf-8")
        for name, info in tools.items():
            check(f"verify page pins tool: {name}",
                  info["sha256"] in html, "hash not found in page")
        check("verify page pins bundle",
              bman.get("sha256", "") in html, "bundle hash not found")
    else:
        check("docs/verify-file.html exists", False)

    # --- VERIFY.md File SHA-256 column ---
    vmd = repo / "kit" / "VERIFY.md"
    if not vmd.exists():
        vmd = repo / "docs" / "kit" / "VERIFY.md"
    if vmd.exists():
        rows = {}
        for line in vmd.read_text(encoding="utf-8").splitlines():
            m = re.match(
                r"\|\s*(\S+\.pdf)\s*\|\s*[^|]+\|\s*`([0-9a-f]{64})`\s*\|\s*`([0-9a-f]{64})`\s*\|",
                line)
            if m:
                rows[m.group(1)] = m.group(2)  # File SHA-256 = 3rd column
        for name, info in pdfs.items():
            check(f"VERIFY.md file hash: {name}",
                  rows.get(name) == info["file_sha256"],
                  f"page={str(rows.get(name))[:12]} manifest={info['file_sha256'][:12]}")
    else:
        check("kit/VERIFY.md exists", False)

    # --- Publishable site: exact artifact bytes, not stale tracked docs/ ---
    site = dist / "site"
    check("publishable site exists", site.is_dir())
    if site.is_dir():
        for name, info in tools.items():
            relative = Path(info["path"])
            published = site / relative.relative_to("docs") if relative.parts[0] == "docs" else site / relative
            check(f"published tool: {name}", published.is_file())
            if published.is_file():
                check(f"published tool size: {name}",
                      published.stat().st_size == info["size"])
                check(f"published tool hash: {name}",
                      sha256_file(published) == info["sha256"])
        for name, info in pdfs.items():
            published = site / "kit" / name
            check(f"published PDF: {name}", published.is_file())
            if published.is_file():
                check(f"published PDF hash: {name}",
                      sha256_file(published) == info["file_sha256"])
        for filename, entry in [
            ("tools-bundle.zip", bman),
            ("plebumbtc-offline.zip", manifest.get("offline_zip", {})),
        ]:
            published = site / "kit" / filename
            check(f"published archive: {filename}", published.is_file())
            if published.is_file():
                check(f"published archive hash: {filename}",
                      sha256_file(published) == entry.get("sha256"))
        published_manifest = site / "kit" / "release-manifest.json"
        check("published release manifest exists", published_manifest.is_file())
        if published_manifest.is_file():
            check("published release manifest exact bytes",
                  published_manifest.read_bytes() == manifest_path.read_bytes())
        published_page = site / "verify-file.html"
        check("published verification page exists", published_page.is_file())
        if published_page.is_file():
            html = published_page.read_text(encoding="utf-8")
            for name, info in tools.items():
                check(f"published pin: {name}", info["sha256"] in html)
            check("published bundle pin", bman.get("sha256", "") in html)
        published_verify = site / "kit" / "VERIFY.md"
        check("published VERIFY.md exists", published_verify.is_file())
        if published_verify.is_file():
            content = published_verify.read_text(encoding="utf-8")
            for name, info in pdfs.items():
                check(f"published PDF fingerprint: {name}",
                      info["file_sha256"] in content)

    # --- 5. Offline ZIP ---
    offline = dist / "plebumbtc-offline.zip"
    check("offline ZIP exists in dist", offline.exists())
    oman = manifest.get("offline_zip", {})
    if offline.exists():
        check("offline size matches manifest",
              offline.stat().st_size == oman.get("size"))
        check("offline sha256 matches manifest",
              sha256_file(offline) == oman.get("sha256"))
        tmp = Path(tempfile.mkdtemp(prefix="verify-offline-"))
        with zipfile.ZipFile(offline) as zf:
            names = zf.namelist()
            check("offline has no self-nesting",
                  not any(n.endswith("plebumbtc-offline.zip") for n in names))
            check("offline has no caches",
                  not any("__pycache__" in n or n.endswith(".pyc") for n in names))
            for req in ["offline-build/assets/css/guide-steps.css",
                        "offline-build/assets/js/guide-demos.js",
                        "offline-build/descriptor-demo.html",
                        "offline-build/passphrase-demo.html"]:
                check(f"offline has required: {req}", req in names)
            zf.extractall(tmp)
        # No root-relative local links in offline HTML
        bad_links = []
        for html_file in sorted((tmp / "offline-build").rglob("*.html")):
            content = html_file.read_text(encoding="utf-8")
            for m in re.finditer(r'''(href|src)="(/[^"]*)"''', content):
                if not m.group(2).startswith("//"):
                    bad_links.append(
                        f"{html_file.relative_to(tmp)}: {m.group(0)[:50]}")
        check("offline: no root-relative local links", not bad_links,
              f"{len(bad_links)} violations" + (
                  f" e.g. {bad_links[0]}" if bad_links else ""))
        # Offline tools equal canonical bytes (HTML tools may differ only by
        # link rewrites; compare the Python tools and wordlist exactly)
        for name in ["bip39_dice_converter.py", "descriptor_obfuscator.py",
                     "eff_large_wordlist.txt"]:
            op = tmp / "offline-build" / "kit" / name
            if op.exists() and name in tools:
                check(f"offline tool bytes: {name}",
                      sha256_file(op) == tools[name]["sha256"])
        shutil.rmtree(tmp, ignore_errors=True)

    # --- 7. Inline JS syntax across shipped HTML ---
    tmpd = Path(tempfile.mkdtemp(prefix="verify-js-"))
    js_failures = []
    html_files = sorted((repo / "docs").rglob("*.html"))
    for html_file in html_files:
        content = html_file.read_text(encoding="utf-8")
        for i, m in enumerate(
                re.finditer(r"<script(?![^>]*src=)[^>]*>(.*?)</script>",
                            content, re.DOTALL | re.IGNORECASE)):
            js = m.group(1).strip()
            if not js or "application/ld+json" in m.group(0):
                continue
            jf = tmpd / f"s{i}.js"
            jf.write_text(js, encoding="utf-8")
            rc, _, err = run(["node", "--check", str(jf)], cwd=str(tmpd))
            if rc != 0:
                js_failures.append(f"{html_file.relative_to(repo)}: {err[:100]}")
    check("inline JS syntax (all shipped HTML)", not js_failures,
          f"{len(js_failures)} failures" + (
              f" e.g. {js_failures[0]}" if js_failures else ""))
    shutil.rmtree(tmpd, ignore_errors=True)

    # --- R-009: cross-format consistency of security-critical facts ---
    # Security-critical strings must appear consistently across HTML sheets.
    # (PDF text extraction is out of scope for this static check; the HTML
    # sheets are the source of truth that PDFs are built from.)
    critical_strings = {
        "multisig threshold wording": "2-of-3",
        "descriptor concept present": "descriptor",
        "no-real-secrets warning": "Never type the words into",
    }
    for label, needle in critical_strings.items():
        found_in = []
        for html_file in sorted((repo / "docs" / "handouts").glob("*.html")):
            # Skip orphaned legacy variants for this check
            if "easy" in html_file.name:
                continue
            try:
                if needle in html_file.read_text(encoding="utf-8"):
                    found_in.append(html_file.name)
            except Exception:
                pass
        check(f"cross-format consistency: {label}",
              len(found_in) > 0,
              f"'{needle}' found in {len(found_in)} sheets")

    # --- Immutability: dist files unchanged since manifest ---
    check("dist bundle hash stable",
          sha256_file(bundle) == manifest["bundle"]["sha256"] if bundle.exists() else False)
    check("dist offline hash stable",
          sha256_file(offline) == manifest["offline_zip"]["sha256"] if offline.exists() else False)

    # --- Source-commit provenance: manifest must declare a real commit ---
    declared = manifest.get("source_commit") or manifest.get("commit") or ""
    # A 40-zero placeholder or empty value means the provenance was destroyed
    check("source commit declared and non-trivial",
          bool(declared) and declared != "0" * 40 and len(declared) >= 7,
          f"declared commit: {declared[:12] if declared else '(missing)'}...")

    return finish()

def finish():
    print()
    if FAILURES:
        print(f"VERIFY FAILED: {len(FAILURES)} failing assertion(s)")
        for f in FAILURES:
            print(f"  - {f}")
        sys.exit(1)
    print("VERIFY PASSED: all assertions green")
    sys.exit(0)

if __name__ == "__main__":
    main()
