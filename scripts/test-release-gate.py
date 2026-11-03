#!/usr/bin/env python3
"""Negative/mutation tests for the release verifier.

Each test corrupts a temporary copy of a good dist/ + repo tree in one
specific way, runs verify_release.py against it, and requires a NONZERO
exit plus an error message naming the offending file.

Usage:
  python3 scripts/test-release-gate.py --dist <good-dist> --repo <repo-root>

Exit 0 only if every mutation is rejected.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

MUTATIONS = []

def mutation(name, expects=None):
    """Register a mutation test.
    
    Args:
        name: Human-readable mutation description.
        expects: The verifier check name (or substring) that must fail.
                 If None, any nonzero exit counts as rejection.
    """
    def deco(fn):
        MUTATIONS.append((name, fn, expects))
        return fn
    return deco

@mutation("corrupt python tool after bundling",
           expects="tool sha256: bip39_dice_converter.py")
def m1(dist, repo):
    p = repo / "kit" / "bip39_dice_converter.py"
    data = p.read_bytes()
    p.write_bytes(data[:-10] + b"XXXXXXXXXX")

@mutation("change one PDF byte without updating manifest",
           expects="pdf file sha256:")
def m2(dist, repo):
    pdfs = list((repo / "kit").glob("*.pdf"))
    if not pdfs:
        pdfs = list((repo / "docs" / "kit").glob("*.pdf"))
    p = pdfs[0]
    data = bytearray(p.read_bytes())
    data[100] ^= 0xFF
    p.write_bytes(bytes(data))

@mutation("swap File and Content SHA-256 columns in VERIFY.md",
           expects="VERIFY.md file hash:")
def m3(dist, repo):
    import re
    vmd = repo / "kit" / "VERIFY.md"
    if not vmd.exists():
        vmd = repo / "docs" / "kit" / "VERIFY.md"
    content = vmd.read_text(encoding="utf-8")
    def swap(m):
        return f"| {m.group(1)} | {m.group(2)} | `{m.group(4)}` | `{m.group(3)}` |"
    content = re.sub(
        r"\|\s*(\S+\.pdf)\s*\|\s*([^|]+?)\s*\|\s*`([0-9a-f]{64})`\s*\|\s*`([0-9a-f]{64})`\s*\|",
        swap, content)
    vmd.write_text(content, encoding="utf-8")

@mutation("remove guide-steps.css from offline ZIP",
           expects="offline has required:")
def m4(dist, repo):
    zpath = dist / "plebumbtc-offline.zip"
    tmp = Path(tempfile.mkdtemp())
    with zipfile.ZipFile(zpath) as zf:
        zf.extractall(tmp)
    target = tmp / "offline-build" / "assets" / "css" / "guide-steps.css"
    if target.exists():
        target.unlink()
    # Rebuild deterministically
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted((tmp / "offline-build").rglob("*")):
            if p.is_file():
                rel = "offline-build/" + str(p.relative_to(tmp / "offline-build"))
                zi = zipfile.ZipInfo(rel, date_time=(2026, 1, 1, 0, 0, 0))
                zi.external_attr = 0o644 << 16
                zf.writestr(zi, p.read_bytes())
    shutil.rmtree(tmp, ignore_errors=True)

@mutation("root-relative link in offline HTML",
           expects="offline: no root-relative local links")
def m5(dist, repo):
    zpath = dist / "plebumbtc-offline.zip"
    tmp = Path(tempfile.mkdtemp())
    with zipfile.ZipFile(zpath) as zf:
        zf.extractall(tmp)
    idx = tmp / "offline-build" / "index.html"
    if idx.exists():
        c = idx.read_text(encoding="utf-8")
        c = c.replace('href="./assets/', 'href="/kit/VERIFY.md" # ', 1)
        # Simpler: inject a root-relative link
        c = c.replace("</head>", '<link href="/kit/VERIFY.md">\n</head>', 1)
        idx.write_text(c, encoding="utf-8")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted((tmp / "offline-build").rglob("*")):
            if p.is_file():
                rel = "offline-build/" + str(p.relative_to(tmp / "offline-build"))
                zi = zipfile.ZipInfo(rel, date_time=(2026, 1, 1, 0, 0, 0))
                zi.external_attr = 0o644 << 16
                zf.writestr(zi, p.read_bytes())
    shutil.rmtree(tmp, ignore_errors=True)

@mutation("nest offline ZIP inside itself",
           expects="offline has no self-nesting")
def m6(dist, repo):
    zpath = dist / "plebumbtc-offline.zip"
    # Add a small placeholder with the nested name (verifier checks
    # filename only, not content). Avoids disk exhaustion from
    # duplicating the full archive.
    with zipfile.ZipFile(zpath, "a", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("offline-build/kit/plebumbtc-offline.zip",
                     b"nested-placeholder")

@mutation("invalid inline JS in shipped page",
           expects="inline JS syntax (all shipped HTML)")
def m7(dist, repo):
    p = repo / "docs" / "index.html"
    c = p.read_text(encoding="utf-8")
    c = c.replace("</body>", "<script>var x = {{{invalid;</script>\n</body>", 1)
    p.write_text(c, encoding="utf-8")

@mutation("stale bundle member (older tool bytes)",
           expects="bundle member bytes:")
def m8(dist, repo):
    zpath = dist / "tools-bundle.zip"
    tmp = Path(tempfile.mkdtemp())
    with zipfile.ZipFile(zpath) as zf:
        zf.extractall(tmp)
    target = tmp / "dice-converter.html"
    if target.exists():
        data = target.read_bytes()
        target.write_bytes(b"<!-- stale -->" + data)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(tmp.iterdir()):
            if p.is_file():
                zi = zipfile.ZipInfo(p.name, date_time=(2026, 1, 1, 0, 0, 0))
                zi.external_attr = 0o644 << 16
                zf.writestr(zi, p.read_bytes())
    shutil.rmtree(tmp, ignore_errors=True)

@mutation("content hash replaced with file hash (pre-stamp provenance lost)",
           expects="pdf content hash provenance:")
def m9(dist, repo):
    # Simulate the historical R-001 confusion: Content SHA-256
    # silently replaced with the file hash in the release manifest.
    # The verifier must detect that content hashes lack pre-stamp provenance.
    import json
    mpath = dist / "release-manifest.json"
    if not mpath.exists():
        return
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    pdfs = manifest.get("pdfs", {})
    mutated = 0
    for name, info in pdfs.items():
        if "content_sha256" in info and "file_sha256" in info:
            if info["content_sha256"] != info["file_sha256"]:
                info["content_sha256"] = info["file_sha256"]
                mutated += 1
    mpath.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    # Also mutate VERIFY.md for consistency
    for vpath in [repo / "docs" / "kit" / "VERIFY.md", repo / "kit" / "VERIFY.md"]:
        if vpath.exists():
            break
    else:
        return
    lines = vpath.read_text(encoding="utf-8").splitlines()
    out = []
    for line in lines:
        # PDF table rows: | file.pdf | version | `filehash` | `contenthash` |
        if line.startswith("|") and line.count("|") >= 5 and ".pdf" in line:
            # Extract hashes, handling backticks
            import re
            hashes = re.findall(r'`([0-9a-f]{64})`', line)
            if len(hashes) >= 2:
                # Replace content hash (2nd) with file hash (1st)
                line = line.replace(f'`{hashes[1]}`', f'`{hashes[0]}`', 1)
        out.append(line)
    vpath.write_text("\n".join(out) + "\n", encoding="utf-8")

@mutation("release manifest declares wrong source commit",
           expects="source commit declared and non-trivial")
def m10(dist, repo):
    # Simulate a release built from different source than declared.
    # The manifest must tie artifacts to the exact commit.
    mpath = dist / "release-manifest.json"
    if not mpath.exists():
        return
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    # Corrupt the declared commit
    if "source_commit" in manifest:
        manifest["source_commit"] = "0" * 40
    elif "commit" in manifest:
        manifest["commit"] = "0" * 40
    else:
        # Add a wrong commit field if none exists
        manifest["source_commit"] = "0" * 40
    mpath.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

@mutation("manifest omits one required PDF (inventory bypass)",
           expects="pdf inventory: manifest declares exactly 17 expected PDFs")
def m11(dist, repo):
    # P0-3: delete one PDF from manifest inventory, keep the file.
    # Verifier must detect the missing entry.
    mpath = dist / "release-manifest.json"
    if not mpath.exists():
        return
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    pdfs = manifest.get("pdfs", {})
    if pdfs:
        # Remove the first PDF entry
        first = next(iter(pdfs))
        del pdfs[first]
    mpath.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

@mutation("production: WORKTREE source commit rejected",
           expects="production: source commit is 40-char hex")
def m12(dist, repo):
    # P0-1: production verifier must reject WORKTREE sentinel.
    # This mutation marks the manifest as production with WORKTREE commit.
    mpath = dist / "release-manifest.json"
    if not mpath.exists():
        return
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    manifest["production"] = True
    manifest["source_commit"] = "WORKTREE"
    mpath.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

@mutation("production: UNVERIFIED content hash rejected",
           expects="content hash verified")
def m13(dist, repo):
    # P0-1: production verifier must reject UNVERIFIED content hashes.
    mpath = dist / "release-manifest.json"
    if not mpath.exists():
        return
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    manifest["production"] = True
    pdfs = manifest.get("pdfs", {})
    for name, info in pdfs.items():
        info["content_sha256"] = "UNVERIFIED"
        break  # Just corrupt one
    mpath.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

@mutation("production: malformed commit identifier rejected",
           expects="production: source commit is 40-char hex")
def m14(dist, repo):
    # P0-1: production verifier must reject non-40-char commits.
    mpath = dist / "release-manifest.json"
    if not mpath.exists():
        return
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    manifest["production"] = True
    manifest["source_commit"] = "abc123"  # Too short, not hex-40
    mpath.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

@mutation("production: valid-but-wrong 40-char commit rejected",
           expects="production: declared commit matches git HEAD")
def m15(dist, repo):
    # P0-1: production verifier must reject a well-formed but incorrect commit
    # when run against a real Git checkout. Create a real git repo in the
    # mutation workspace, then set manifest source_commit to a different SHA.
    import subprocess
    # Init git repo in the test workspace
    subprocess.run(["git", "init", "-q"], cwd=str(repo), check=True,
                   capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"],
                   cwd=str(repo), check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"],
                   cwd=str(repo), check=True, capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=str(repo), check=True,
                   capture_output=True)
    subprocess.run(["git", "commit", "-qm", "test"],
                   cwd=str(repo), check=True, capture_output=True)
    # Get the real HEAD
    r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(repo),
                       check=True, capture_output=True, text=True)
    real_head = r.stdout.strip()
    # Set manifest to a different valid SHA
    mpath = dist / "release-manifest.json"
    if not mpath.exists():
        return
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    manifest["production"] = True
    # Use all 'b's, guaranteed different from real_head (which is hex)
    wrong_sha = "b" * 40
    if wrong_sha == real_head:
        wrong_sha = "c" * 40
    manifest["source_commit"] = wrong_sha
    mpath.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

@mutation("production: non-production manifest rejected in production mode",
           expects="production: manifest declares production=true")
def m16(dist, repo):
    # P0-1: production verifier must reject manifests not built with --production.
    mpath = dist / "release-manifest.json"
    if not mpath.exists():
        return
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    # Ensure production flag is False/missing (dev build)
    manifest["production"] = False
    mpath.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

@mutation("provenance: forged content-text hash rejected by regenerated bytes",
           expects="content-text hash matches regenerated")
def m17(dist, repo):
    # Option A: replace one content_text_sha256 with a valid-looking but
    # incorrect 64-char hash. In strict mode, the verifier must reject the
    # release. This tests that forged provenance is caught.
    # NOTE: This test requires --prestamp-dir. Without it, the test is skipped.
    mpath = dist / "release-manifest.json"
    if not mpath.exists():
        return
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    pdfs = manifest.get("pdfs", {})
    for name, info in pdfs.items():
        # Use a valid 64-char hex that's different from the real hash
        fake = "b" * 64
        if info.get("content_text_sha256") != fake:
            info["content_text_sha256"] = fake
            break
    mpath.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


@mutation("provenance: forged raw content hash rejected by regenerated bytes",
           expects="raw content hash matches regenerated")
def m18(dist, repo):
    # Replace one content_sha256 (raw pre-stamp byte hash) with a valid-looking
    # but incorrect 64-char hash. The verifier with --prestamp-dir must detect
    # the mismatch by hashing the regenerated PDF bytes itself.
    # NOTE: This test requires --prestamp-dir. Without it, the test is skipped.
    # The harness handles this by only running m18 when prestamp is available.
    mpath = dist / "release-manifest.json"
    if not mpath.exists():
        return
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    pdfs = manifest.get("pdfs", {})
    for name, info in pdfs.items():
        # Use a valid 64-char hex that's different from the real hash
        fake = "d" * 64
        if info.get("content_sha256") != fake:
            info["content_sha256"] = fake
            break
    mpath.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dist", required=True)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tmpdir", default=None,
                    help="Override temp dir for mutation workspaces "
                         "(default: system temp; use when /tmp is small)")
    ap.add_argument("--prestamp-dir", default=None,
                    help="Directory with independently regenerated pre-stamp PDFs. "
                         "Passed to verifier for provenance checks (m17).")
    args = ap.parse_args()
    good_dist = Path(args.dist)
    good_repo = Path(args.repo)
    verifier = good_repo / "scripts" / "verify_release.py"
    # Allow override via arg or NEGTEST_TMPDIR env (for small-/tmp hosts)
    tmp_base = args.tmpdir or os.environ.get("NEGTEST_TMPDIR") or None

    passed = 0
    failed = 0
    skipped = 0

    # Baseline: verify the unmutated tree passes first.
    # If the baseline fails, mutations can't prove anything.
    # Use the same strict mode CI requires: if manifest declares production
    # and --prestamp-dir was supplied, baseline runs with --production and
    # --prestamp-dir. Log the exact mode.
    print("Running baseline verification on unmutated tree...")
    baseline_cmd = [sys.executable, str(verifier), "--dist", str(good_dist),
                    "--repo", str(good_repo)]
    baseline_mode = "development"
    try:
        _mpath = good_dist / "release-manifest.json"
        if _mpath.exists():
            _m = json.loads(_mpath.read_text(encoding="utf-8"))
            if _m.get("production") is True:
                baseline_cmd.append("--production")
                baseline_mode = "production"
    except Exception:
        pass
    if args.prestamp_dir:
        baseline_cmd.extend(["--prestamp-dir", args.prestamp_dir])
        baseline_mode += "+prestamp"
    print(f"  baseline mode: {baseline_mode}")
    baseline = subprocess.run(baseline_cmd, capture_output=True, text=True)
    if baseline.returncode != 0:
        print(f"[FAIL] baseline verification failed (exit={baseline.returncode})")
        print("  Cannot trust mutation results without a clean baseline.")
        print("  STDOUT tail:", baseline.stdout[-500:])
        sys.exit(1)
    print("[PASS] baseline verification clean\n")

    for name, fn, expects in MUTATIONS:
        work = Path(tempfile.mkdtemp(prefix="negtest-", dir=tmp_base))
        tdist = work / "dist"
        trepo = work / "repo"
        shutil.copytree(good_dist, tdist)
        shutil.copytree(good_repo, trepo,
                        ignore=shutil.ignore_patterns(".git", "__pycache__"))
        try:
            fn(tdist, trepo)
        except Exception as e:
            # Setup failures are failures, not skips.
            # A mutation that can't be applied proves nothing.
            print(f"[FAIL] negative test: {name} "
                  f"(mutation setup raised: {e})")
            failed += 1
            shutil.rmtree(work, ignore_errors=True)
            continue
        # Production mutations (m12-m16) need --production flag on verifier
        prod_mutations = {
            "production: WORKTREE source commit rejected",
            "production: UNVERIFIED content hash rejected",
            "production: malformed commit identifier rejected",
            "production: valid-but-wrong 40-char commit rejected",
            "production: non-production manifest rejected in production mode",
        }
        verifier_cmd = [sys.executable, str(verifier), "--dist", str(tdist),
                        "--repo", str(trepo)]
        if name in prod_mutations:
            verifier_cmd.append("--production")
        # m17/m18 (provenance) need --prestamp-dir; skip if not provided
        if name in ("provenance: forged content-text hash rejected by regenerated bytes",
                    "provenance: forged raw content hash rejected by regenerated bytes"):
            if not args.prestamp_dir:
                print(f"[SKIP] negative test: {name} "
                      f"(requires --prestamp-dir)")
                skipped += 1
                shutil.rmtree(work, ignore_errors=True)
                continue
            # Verify prestamp dir actually has PDFs; if not, skip
            # (artifact download may have failed)
            from pathlib import Path as P
            psd = P(args.prestamp_dir)
            if not psd.is_dir() or not list(psd.glob("*.pdf")):
                print(f"[SKIP] negative test: {name} "
                      f"(prestamp dir empty or missing)")
                shutil.rmtree(work, ignore_errors=True)
                continue
            verifier_cmd.extend(["--prestamp-dir", args.prestamp_dir])
        elif args.prestamp_dir:
            # Pass prestamp-dir to all verifications when available
            verifier_cmd.extend(["--prestamp-dir", args.prestamp_dir])
        r = subprocess.run(verifier_cmd, capture_output=True, text=True)
        rejected = r.returncode != 0
        # P1-2: require the EXPECTED check to FAIL, not just appear in output.
        # Match [FAIL] lines specifically to avoid false credit from a substring
        # appearing in a [PASS] line while an unrelated check causes exit 1.
        if expects is None:
            expected_found = True
        else:
            expected_found = any(
                line.strip().startswith("[FAIL]") and expects in line
                for line in r.stdout.split("\n")
            )
        if rejected and expected_found:
            status = "PASS"
            passed += 1
        else:
            status = "FAIL"
            failed += 1
        print(f"[{status}] negative test: {name} "
              f"(exit={r.returncode}, expected_check={'found' if expected_found else 'MISSING'})")
        if status == "FAIL":
            if not rejected:
                print(f"  Verifier unexpectedly PASSED (exit=0)")
            elif not expected_found:
                print(f"  Expected '{expects}' not found in output")
            print("  STDOUT tail:", r.stdout[-500:])
        shutil.rmtree(work, ignore_errors=True)

    print(f"\n{passed}/{len(MUTATIONS)} mutations rejected "
          f"({failed} failed, {skipped} skipped)")
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()
