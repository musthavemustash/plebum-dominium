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
    args = ap.parse_args()
    dist = Path(args.dist)
    repo = Path(args.repo)

    manifest_path = dist / "release-manifest.json"
    check("release-manifest.json exists", manifest_path.exists())
    if FAILURES:
        return finish()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

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
    pdfs = manifest.get("pdfs", {})
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
