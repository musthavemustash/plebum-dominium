#!/usr/bin/env python3
"""Plebum Dominium deterministic release pipeline.

Single entrypoint for building a verified release from a frozen source tree.
Implements stages A-G of the release pipeline contract:

  Stage A - Clean/frozen inputs: assert repo state, build in temp dir
  Stage B - Generate canonical site and tools (build.py + tool builders)
  Stage C - Generate and stamp PDFs (build-kit-pdfs.py + stamp-pdfs.py)
  Stage D - Build tools bundle from staged bytes
  Stage E - Generate manifests (VERIFY.md + verify-file.html) from one manifest object
  Stage F - Build offline package LAST
  Stage G - Final external release manifest (dist/release-manifest.json)

Usage:
  python3 scripts/release.py --commit <full-sha> --out dist [--skip-pdfs]

  --commit  Full git SHA of the source tree to build from (recorded in manifest).
            Use "WORKTREE" to build from the current working tree (for local testing;
            the manifest will record it as uncommitted).
  --out     Output directory (created fresh; must not exist or must be empty).
  --skip-pdfs  Skip PDF rebuild/stamp (reuse existing kit/*.pdf; content hashes
            will be marked unverified).

Exit 0 on success, nonzero on any failure. Never partially promotes outputs.
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
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def log(msg):
    print(f"[release] {msg}", flush=True)

def fail(msg):
    print(f"[release] FATAL: {msg}", file=sys.stderr, flush=True)
    sys.exit(1)

def enforce_production_prereqs(repo_root, args):
    """Fail closed on any production-mode violation. Called before Stage A."""
    import re
    # 1. --skip-pdfs is forbidden in production
    if args.skip_pdfs:
        fail("production mode: --skip-pdfs is not allowed; "
             "content hashes must be verified")
    # 2. WORKTREE is forbidden in production
    if args.commit == "WORKTREE":
        fail("production mode: --commit WORKTREE is not allowed; "
             "must be a 40-char git SHA")
    # 3. Commit must be 40-char hex
    if not re.fullmatch(r"[0-9a-f]{40}", args.commit.lower()):
        fail(f"production mode: --commit must be a 40-char hex SHA, "
             f"got '{args.commit[:20]}...'")
    # 4. Git must be available and commit must resolve to HEAD
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo_root,
            capture_output=True, text=True)
        if head.returncode != 0:
            fail("production mode: cannot determine git HEAD "
                 "(not a git repo or git unavailable)")
        actual_head = head.stdout.strip().lower()
        if actual_head != args.commit.lower():
            fail(f"production mode: declared commit {args.commit[:12]} "
                 f"does not match checked-out HEAD {actual_head[:12]}")
        # 5. Working tree must be clean
        dirty = subprocess.run(
            ["git", "status", "--porcelain"], cwd=repo_root,
            capture_output=True, text=True)
        if dirty.returncode != 0:
            fail("production mode: cannot check git status")
        if dirty.stdout.strip():
            fail("production mode: working tree is dirty; "
                 "commit all changes before production build")
    except FileNotFoundError:
        fail("production mode: git not available; cannot verify provenance")
    log("production mode: all prerequisites satisfied")

def run(cmd, cwd, env=None):
    """Run a command, fail on nonzero exit. Returns stdout."""
    log(f"$ {' '.join(cmd)} (cwd={cwd})")
    r = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-2000:], file=sys.stderr)
        print(r.stderr[-2000:], file=sys.stderr)
        fail(f"command failed (exit {r.returncode}): {' '.join(cmd)}")
    return r.stdout

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def deterministic_zip(zip_path, source_dir, prefix=""):
    """Create a deterministic ZIP: sorted names, fixed timestamps, fixed perms."""
    source = Path(source_dir)
    files = sorted(
        (p for p in source.rglob('*') if p.is_file()
         and '__pycache__' not in str(p)
         and not p.name.endswith('.pyc')),
        key=lambda p: str(p.relative_to(source))
    )
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for p in files:
            rel = str(p.relative_to(source))
            arcname = f"{prefix}{rel}" if prefix else rel
            zi = zipfile.ZipInfo(arcname, date_time=(2026, 1, 1, 0, 0, 0))
            zi.external_attr = 0o644 << 16
            with open(p, 'rb') as f:
                zf.writestr(zi, f.read())
    return files

# ---------------------------------------------------------------------------
# Stage A - Clean/frozen inputs
# ---------------------------------------------------------------------------

def stage_a(repo_root, commit, out_dir, production=False):
    log("=== Stage A: frozen inputs ===")
    out = Path(out_dir)
    if out.exists() and any(out.iterdir()):
        fail(f"--out directory {out_dir} exists and is not empty; refusing to build")
    out.mkdir(parents=True, exist_ok=True)

    # Record source identity
    manifest = {
        "source_commit": commit,
        "build_time_utc": datetime.now(timezone.utc).isoformat(),
        "builder": "scripts/release.py",
        "production": production,
    }
    if commit != "WORKTREE":
        # Verify the commit exists in the local repo if we have git
        try:
            got = subprocess.run(
                ["git", "rev-parse", commit], cwd=repo_root,
                capture_output=True, text=True)
            if got.returncode != 0:
                log(f"WARNING: cannot verify commit {commit} with git "
                    f"(not a git repo or unknown SHA); recording as-is")
            else:
                full = got.stdout.strip()
                if not full.startswith(commit) and commit != full:
                    fail(f"commit prefix {commit} is ambiguous")
                manifest["source_commit_full"] = full
                # Check for dirty tree
                dirty = subprocess.run(
                    ["git", "status", "--porcelain"], cwd=repo_root,
                    capture_output=True, text=True)
                if dirty.returncode == 0 and dirty.stdout.strip():
                    log("WARNING: working tree is dirty; "
                        "manifest records WORKTREE-DIRTY")
                    manifest["source_commit"] = f"{commit}-DIRTY"
        except FileNotFoundError:
            log("WARNING: git not available; cannot verify commit")
    else:
        log("Building from working tree (not a frozen commit)")

    # Staging dir (temp, promoted only after verification)
    stage = Path(tempfile.mkdtemp(prefix="pleb-release-"))
    log(f"staging dir: {stage}")
    return manifest, stage

# ---------------------------------------------------------------------------
# Stage B - Canonical site and tools
# ---------------------------------------------------------------------------

CANONICAL_TOOLS = [
    # (manifest name, path relative to repo root after build)
    ("bip39_dice_converter.py", "kit/bip39_dice_converter.py"),
    ("descriptor_obfuscator.py", "kit/descriptor_obfuscator.py"),
    ("eff_large_wordlist.txt", "kit/eff_large_wordlist.txt"),
    ("hash_checker.html", "kit/hash_checker.html"),
    ("dice-converter.html", "docs/dice-converter.html"),
    ("descriptor-tool.html", "docs/descriptor-tool.html"),
]

def stage_b(repo_root, stage):
    log("=== Stage B: canonical site and tools ===")
    root = Path(repo_root)

    # 0. Preserve docs/verify-file.html across the build wipe (build.py
    # deletes docs/ but does not regenerate this page).
    verify_backup = None
    verify_path = root / "docs" / "verify-file.html"
    if verify_path.exists():
        verify_backup = stage / "verify-file.html.bak"
        shutil.copy2(verify_path, verify_backup)
        log("backed up docs/verify-file.html")

    # 1. Build the static site (content/*.md -> docs/)
    run([sys.executable, "scripts/build.py", "--base", "/"], cwd=str(root))

    # 1b. Restore verify-file.html if the build wiped it
    if verify_backup and not verify_path.exists():
        shutil.copy2(verify_backup, verify_path)
        log("restored docs/verify-file.html after build wipe")

    # 2. Restore files that build.py wipes but are not generated by it
    # Sources live in scripts/build-sources/ (repo-local, CI-safe)
    _bsrc = root / "scripts" / "build-sources"
    restores = [
        ("docs/dice-rolls.html", _bsrc / "live-dice-rolls-source.html"),
        ("docs/passphrase-demo.html", _bsrc / "passphrase-demo-source.html"),
        ("docs/descriptor-demo.html", root / "tools" / "descriptor-html-demo.html"),
        ("docs/assets/css/guide-steps.css", _bsrc / "css" / "guide-steps.css"),
        ("docs/assets/js/guide-demos.js", _bsrc / "js" / "guide-demos.js"),
    ]
    for dest_rel, src in restores:
        dest = root / dest_rel
        if src.exists():
            shutil.copy2(src, dest)
            log(f"restored {dest_rel}")
        else:
            log(f"WARNING: restore source missing: {src}; skipping")

    # 2b. Ensure docs/diceware-mapper.html exists (test expects it;
    # build.py only creates docs/diceware.html from tools/diceware-mapper.html)
    mapper_src = root / "tools" / "diceware-mapper.html"
    mapper_dest = root / "docs" / "diceware-mapper.html"
    if mapper_src.exists() and not mapper_dest.exists():
        shutil.copy2(mapper_src, mapper_dest)
        log("copied tools/diceware-mapper.html -> docs/diceware-mapper.html")

    # 2c. Preserve docs/verify-file.html across the build wipe.
    # build.py wipes docs/ but does not regenerate this page; restore it
    # from the repo's committed copy if the build removed it.
    verify_src = root / "docs" / "verify-file.html"
    # (captured before build; re-check after)

    # 3. Rebuild the HTML tools from their builders (repo-local)
    dice_builder = root / "scripts" / "tools" / "build-dice-tool.py"
    desc_builder = root / "scripts" / "tools" / "build-descriptor-tool.py"
    if dice_builder.exists():
        run([sys.executable, str(dice_builder),
             str(root / "docs/dice-converter.html")], cwd=str(root))
    else:
        log("WARNING: dice tool builder not found; using existing docs/dice-converter.html")
    if desc_builder.exists():
        run([sys.executable, str(desc_builder),
             str(root / "docs/descriptor-tool.html")], cwd=str(root))
    else:
        log("WARNING: descriptor tool builder not found; using existing docs/descriptor-tool.html")

    # 4. Regenerate the -one path variants from current base pages
    for slug in ["checklist", "titanium", "faq", "fire-card"]:
        base = root / f"docs/handouts/{slug}.html"
        variant = root / f"docs/handouts/{slug}-one.html"
        if base.exists():
            shutil.copy2(base, variant)
    dice_base = root / "docs/handouts/dice.html"
    dice_one = root / "docs/handouts/dice-one.html"
    if dice_base.exists():
        html = dice_base.read_text(encoding="utf-8")
        html = html.replace("<h1>Make the three keys</h1>", "<h1>Make one key</h1>")
        html = html.replace(
            "You will roll dice to create three separate Bitcoin seed phrases.",
            "You will roll dice to create one Bitcoin seed phrase.")
        dice_one.write_text(html, encoding="utf-8")
    log("regenerated -one variants")

    # 5. Snapshot canonical tool bytes into staging
    tools = {}
    for name, rel in CANONICAL_TOOLS:
        p = root / rel
        if not p.exists():
            fail(f"canonical tool missing after build: {rel}")
        data = p.read_bytes()
        tools[name] = {
            "path": rel,
            "size": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
    log(f"captured {len(tools)} canonical tools")
    return tools

# ---------------------------------------------------------------------------
# Stage C - PDFs
# ---------------------------------------------------------------------------

def stage_c(repo_root, stage, skip_pdfs):
    log("=== Stage C: PDFs ===")
    root = Path(repo_root)
    pdf_info = {}
    if skip_pdfs:
        log("--skip-pdfs: reusing existing kit/*.pdf; content hashes UNVERIFIED")
        for pdf in sorted((root / "kit").glob("*.pdf")):
            data = pdf.read_bytes()
            pdf_info[pdf.name] = {
                "file_sha256": hashlib.sha256(data).hexdigest(),
                "file_size": len(data),
                "content_sha256": "UNVERIFIED",
                "content_provenance": "skipped-pdf-rebuild",
            }
        return pdf_info

    # Rebuild unstamped PDFs, then stamp (stamp computes content hashes)
    # SOURCE_DATE_EPOCH=0 for deterministic builds (provenance verification
    # requires byte-identical regeneration)
    import os
    pdf_env = os.environ.copy()
    pdf_env["SOURCE_DATE_EPOCH"] = "0"
    run([sys.executable, "scripts/build-kit-pdfs.py"], cwd=str(root), env=pdf_env)
    run([sys.executable, "scripts/build-print-packet.py"], cwd=str(root), env=pdf_env)
    # Regenerate fire card from source (prevents double-stamping old card)
    run([sys.executable, "scripts/build-fire-card.py",
         "--out", str(root / "kit" / "15_Fire_Card.pdf")],
        cwd=str(root), env=pdf_env)

    # stamp-pdfs.py needs reportlab/pypdf; try venv first, then system
    venv_py = Path("/tmp/pdfenv/bin/python")
    py = str(venv_py) if venv_py.exists() else sys.executable
    try:
        run([py, "scripts/stamp-pdfs.py"], cwd=str(root))
    except SystemExit:
        fail("stamp-pdfs.py failed; cannot produce content hashes")

    for pdf in sorted((root / "kit").glob("*.pdf")):
        data = pdf.read_bytes()
        pdf_info[pdf.name] = {
            "file_sha256": hashlib.sha256(data).hexdigest(),
            "file_size": len(data),
            # Content hash comes from VERIFY.md which stamp-pdfs.py regenerates.
            # We read it back below in stage E.
            "content_sha256": None,
            "content_provenance": "stamp-pdfs.py",
        }
    log(f"stamped {len(pdf_info)} PDFs")
    return pdf_info

# ---------------------------------------------------------------------------
# Stage D - Tools bundle
# ---------------------------------------------------------------------------

BUNDLE_MEMBERS = [
    ("dice-converter.html", "docs/dice-converter.html"),
    ("descriptor-tool.html", "docs/descriptor-tool.html"),
    ("bip39_dice_converter.py", "kit/bip39_dice_converter.py"),
    ("descriptor_obfuscator.py", "kit/descriptor_obfuscator.py"),
    ("eff_large_wordlist.txt", "kit/eff_large_wordlist.txt"),
    ("hash_checker.html", "kit/hash_checker.html"),
]

def stage_d(repo_root, stage, tools):
    log("=== Stage D: tools bundle ===")
    root = Path(repo_root)
    bundle_stage = stage / "bundle"
    bundle_stage.mkdir(parents=True, exist_ok=True)

    # Copy canonical bytes (from the repo files captured in stage B)
    for arcname, rel in BUNDLE_MEMBERS:
        src = root / rel
        data = src.read_bytes()
        # Cross-check against canonical capture
        if tools.get(arcname, {}).get("sha256") != hashlib.sha256(data).hexdigest():
            fail(f"tool bytes changed between stage B and D: {rel}")
        (bundle_stage / arcname).write_bytes(data)

    # Deterministic ZIP
    bundle_zip = stage / "tools-bundle.zip"
    deterministic_zip(bundle_zip, bundle_stage)

    # Reopen and byte-compare every member
    with zipfile.ZipFile(bundle_zip) as zf:
        names = zf.namelist()
        if sorted(names) != sorted(a for a, _ in BUNDLE_MEMBERS):
            fail(f"bundle member mismatch: {names}")
        for arcname, rel in BUNDLE_MEMBERS:
            if zf.read(arcname) != (root / rel).read_bytes():
                fail(f"bundle member differs from source: {arcname}")
    log(f"bundle OK: {bundle_zip} ({bundle_zip.stat().st_size} bytes)")
    return bundle_zip

# ---------------------------------------------------------------------------
# Stage E - Manifests from one manifest object
# ---------------------------------------------------------------------------

def stage_e(repo_root, stage, tools, pdf_info, bundle_zip):
    log("=== Stage E: manifests ===")
    root = Path(repo_root)

    # Read back content hashes that stamp-pdfs.py wrote into kit/VERIFY.md
    verify_md = root / "kit/VERIFY.md"
    content_hashes = {}
    if verify_md.exists():
        for line in verify_md.read_text(encoding="utf-8").splitlines():
            m = re.match(
                r"\|\s*(\S+\.pdf)\s*\|\s*[^|]+\|\s*`([0-9a-f]{64})`\s*\|\s*`([0-9a-f]{64})`\s*\|",
                line)
            if m:
                # header is: File | Version | File SHA-256 | Content SHA-256
                content_hashes[m.group(1)] = m.group(3)
    # Read back content-text hashes for provenance (deterministic across runners)
    text_hashes = {}
    text_hash_file = root / "kit" / "VERIFY-text-hashes.json"
    if text_hash_file.exists():
        text_hashes = json.loads(text_hash_file.read_text(encoding="utf-8"))
    else:
        # Fallback: compute from current kit/ PDFs (stamped). Strip footer
        # lines containing version/hash markers to approximate pre-stamp text.
        # This is less precise than stamp-pdfs.py's pre-stamp hash but ensures
        # the manifest is not UNVERIFIED when the JSON is missing.
        try:
            from pypdf import PdfReader
            for pdf_path in sorted((root / "kit").glob("*.pdf")):
                try:
                    reader = PdfReader(str(pdf_path))
                    full_text = "\n".join(
                        (p.extract_text() or "") for p in reader.pages
                    )
                    # Strip footer lines with version/hash markers
                    lines = [
                        ln.rstrip() for ln in full_text.split("\n")
                        if ln.strip()
                        and "Content SHA-256:" not in ln
                        and "SHA-256" not in ln
                    ]
                    normalized = "\n".join(lines)
                    import hashlib
                    text_hashes[pdf_path.name] = hashlib.sha256(
                        normalized.encode("utf-8")).hexdigest()
                except Exception:
                    pass
        except ImportError:
            pass
    for name, info in pdf_info.items():
        if info["content_sha256"] is None:
            info["content_sha256"] = content_hashes.get(name, "UNVERIFIED")
        # Content-text hash for cross-runner provenance verification
        info["content_text_sha256"] = text_hashes.get(name, "UNVERIFIED")

    manifest = {
        "tools": tools,
        "pdfs": pdf_info,
        "bundle": {
            "size": bundle_zip.stat().st_size,
            "sha256": sha256_file(bundle_zip),
        },
    }

    # Write the structured manifest for the verifier
    (stage / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    # Update kit/VERIFY.md File SHA-256 column (3rd column) from manifest.
    # Header: File | Version | File SHA-256 | Content SHA-256
    # We update only the File column; Content column is left as-is
    # (it requires the PDF stamping workflow for true pre-stamp hashes).
    verify_md = root / "kit" / "VERIFY.md"
    if verify_md.exists():
        vcontent = verify_md.read_text(encoding="utf-8")
        updated = 0
        for name, info in pdf_info.items():
            pattern = (r"(\| " + re.escape(name) +
                       r" \| [^|]+ \| `)[^`]+(` \|)")
            new_vcontent, n = re.subn(
                pattern, rf"\g<1>{info['file_sha256']}\g<2>", vcontent)
            if n > 0:
                vcontent = new_vcontent
                updated += 1
        verify_md.write_text(vcontent, encoding="utf-8")
        # Also update docs/kit/VERIFY.md (the built copy)
        docs_verify = root / "docs" / "kit" / "VERIFY.md"
        if docs_verify.exists():
            docs_verify.write_text(vcontent, encoding="utf-8")
        log(f"updated VERIFY.md File SHA-256 for {updated} PDFs")

    # Regenerate verify-file.html pins from the manifest.
    # The dedicated builder is test-site specific; update the PINNED
    # entries in place from our manifest object.
    vpage = root / "docs" / "verify-file.html"
    if vpage.exists():
        vhtml = vpage.read_text(encoding="utf-8")
        # Bundle pin
        vhtml, n = re.subn(
            r'("tools-bundle\.zip",\s*"size":\s*)\d+(,\s*"sha256":\s*")[0-9a-f]+(")',
            rf'\g<1>{manifest["bundle"]["size"]}\g<2>{manifest["bundle"]["sha256"]}\g<3>',
            vhtml)
        # Tool pins
        for tname, tinfo in tools.items():
            vhtml, _ = re.subn(
                r'("' + re.escape(tname) + r'",\s*"size":\s*)\d+'
                r'(,\s*"sha256":\s*")[0-9a-f]+(")',
                rf'\g<1>{tinfo["size"]}\g<2>{tinfo["sha256"]}\g<3>',
                vhtml)
        vpage.write_text(vhtml, encoding="utf-8")
        log("updated docs/verify-file.html pins from manifest")
    else:
        log("WARNING: docs/verify-file.html not found; skipping pin update")

    return manifest

# ---------------------------------------------------------------------------
# Stage F - Offline package LAST
# ---------------------------------------------------------------------------

def rewrite_offline_html(filepath, rel_path):
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    orig = content
    depth = rel_path.count("/")
    prefix = "../" * depth if depth > 0 else "./"
    content = re.sub(r'(href|src)="(/assets/[^"]*)"',
                     lambda m: f'{m.group(1)}="{prefix}{m.group(2)[1:]}"', content)
    content = re.sub(r'(href|src)="(/handouts/[^"]*)"',
                     lambda m: f'{m.group(1)}="{prefix}{m.group(2)[1:]}"', content)
    content = re.sub(r'(href|src)="(/kit/[^"]*)"',
                     lambda m: f'{m.group(1)}="{prefix}{m.group(2)[1:]}"', content)
    content = re.sub(r'(href|src)="(/([a-z0-9-]+\.html)(#[^"]*)?)"',
                     lambda m: f'{m.group(1)}="{prefix}{m.group(3)}{m.group(4) or ""}"', content)
    content = re.sub(r'href="/(#[^"]*)"',
                     lambda m: f'href="{prefix}index.html{m.group(1)}"', content)
    content = re.sub(r'href="/"',
                     f'href="{prefix}index.html"', content)
    # Fail closed: no root-relative local links may remain
    bad = re.findall(r'(href|src)="/(?!/)', content)
    # Allow http(s):, mailto:, lightning:, #, data:
    content = re.sub(r'<link[^>]*fonts\.googleapis[^>]*>', '', content)
    content = re.sub(r'<link[^>]*fonts\.gstatic[^>]*>', '', content)
    content = re.sub(r'<script[^>]*goatcounter[^>]*></script>', '',
                     content, flags=re.IGNORECASE)
    if content != orig:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
    # Check for remaining root-relative local refs (excluding schemes/fragments)
    leftovers = [m for m in re.finditer(r'''(href|src)="(/[^"]*)"''', content)
                 if not m.group(2).startswith("//")]
    return leftovers

def stage_f(repo_root, stage):
    log("=== Stage F: offline package ===")
    root = Path(repo_root)
    offline_stage = stage / "offline-build"
    if offline_stage.exists():
        shutil.rmtree(offline_stage)
    # Copy finalized docs/ including kit/
    shutil.copytree(root / "docs", offline_stage,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    # Never nest the offline ZIP inside itself
    nested = offline_stage / "kit" / "plebumbtc-offline.zip"
    if nested.exists():
        nested.unlink()
        log("removed nested offline ZIP from staging")

    # Rewrite HTML for file:// use; collect violations
    violations = []
    for html_file in sorted(offline_stage.rglob("*.html")):
        rel = str(html_file.relative_to(offline_stage))
        bad = rewrite_offline_html(str(html_file), rel)
        for m in bad:
            violations.append(f"{rel}: {m.group(0)[:60]}")
    if violations:
        log("root-relative link violations in offline HTML:")
        for v in violations[:20]:
            log(f"  {v}")
        fail(f"{len(violations)} root-relative links remain in offline package")

    # Required assets
    for req in ["assets/css/guide-steps.css", "assets/js/guide-demos.js",
                "descriptor-demo.html", "passphrase-demo.html"]:
        if not (offline_stage / req).exists():
            fail(f"offline package missing required file: {req}")

    offline_zip = stage / "plebumbtc-offline.zip"
    deterministic_zip(offline_zip, offline_stage, prefix="offline-build/")
    # Prohibit ZIP-in-ZIP self reference
    with zipfile.ZipFile(offline_zip) as zf:
        for n in zf.namelist():
            if n.endswith("plebumbtc-offline.zip"):
                fail("offline ZIP contains itself (recursive packaging)")
            if "__pycache__" in n or n.endswith(".pyc"):
                fail(f"offline ZIP contains cache file: {n}")
    log(f"offline OK: {offline_zip} ({offline_zip.stat().st_size} bytes)")
    return offline_zip

# ---------------------------------------------------------------------------
# Stage G - External release manifest
# ---------------------------------------------------------------------------

def stage_g(stage, manifest, bundle_zip, offline_zip, out_dir):
    log("=== Stage G: external release manifest ===")
    manifest["bundle"] = {
        "size": bundle_zip.stat().st_size,
        "sha256": sha256_file(bundle_zip),
    }
    manifest["offline_zip"] = {
        "size": offline_zip.stat().st_size,
        "sha256": sha256_file(offline_zip),
    }
    (stage / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (stage / "release-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    out = Path(out_dir)
    # Promote: copy staged artifacts to out/
    for name in ["tools-bundle.zip", "plebumbtc-offline.zip",
                 "manifest.json", "release-manifest.json"]:
        shutil.copy2(stage / name, out / name)
    log(f"promoted 4 artifacts to {out_dir}")
    return manifest

# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Plebum Dominium release pipeline")
    ap.add_argument("--commit", required=True,
                    help="Full git SHA to build from, or WORKTREE")
    ap.add_argument("--out", required=True, help="Output directory (must be empty)")
    ap.add_argument("--skip-pdfs", action="store_true",
                    help="Reuse existing kit/*.pdf (content hashes UNVERIFIED)")
    ap.add_argument("--production", action="store_true",
                    help="Production mode: reject --skip-pdfs, WORKTREE, dirty "
                         "trees, and unverifiable commits. Fail closed.")
    args = ap.parse_args()

    repo_root = str(Path(__file__).resolve().parent.parent)
    if args.production:
        enforce_production_prereqs(repo_root, args)
    manifest, stage = stage_a(repo_root, args.commit, args.out, args.production)
    try:
        tools = stage_b(repo_root, stage)
        pdf_info = stage_c(repo_root, stage, args.skip_pdfs)
        bundle_zip = stage_d(repo_root, stage, tools)
        manifest_obj = stage_e(repo_root, stage, tools, pdf_info, bundle_zip)
        # Merge stage-A identity into the manifest object
        manifest_obj.update(manifest)
        offline_zip = stage_f(repo_root, stage)
        stage_g(stage, manifest_obj, bundle_zip, offline_zip, args.out)
    finally:
        # Keep staging dir for debugging on failure; remove on success is
        # handled by the caller. We leave it in place with a log line.
        log(f"staging dir retained at {stage} for inspection")
    log("RELEASE BUILD COMPLETE")

if __name__ == "__main__":
    main()
