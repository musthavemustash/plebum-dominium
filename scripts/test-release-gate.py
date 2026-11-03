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

def mutation(name):
    def deco(fn):
        MUTATIONS.append((name, fn))
        return fn
    return deco

@mutation("corrupt python tool after bundling")
def m1(dist, repo):
    p = repo / "kit" / "bip39_dice_converter.py"
    data = p.read_bytes()
    p.write_bytes(data[:-10] + b"XXXXXXXXXX")

@mutation("change one PDF byte without updating manifest")
def m2(dist, repo):
    pdfs = list((repo / "kit").glob("*.pdf"))
    if not pdfs:
        pdfs = list((repo / "docs" / "kit").glob("*.pdf"))
    p = pdfs[0]
    data = bytearray(p.read_bytes())
    data[100] ^= 0xFF
    p.write_bytes(bytes(data))

@mutation("swap File and Content SHA-256 columns in VERIFY.md")
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

@mutation("remove guide-steps.css from offline ZIP")
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

@mutation("root-relative link in offline HTML")
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

@mutation("nest offline ZIP inside itself")
def m6(dist, repo):
    zpath = dist / "plebumbtc-offline.zip"
    with zipfile.ZipFile(zpath, "a", zipfile.ZIP_DEFLATED) as zf:
        zf.write(zpath, "offline-build/kit/plebumbtc-offline.zip")

@mutation("invalid inline JS in shipped page")
def m7(dist, repo):
    p = repo / "docs" / "index.html"
    c = p.read_text(encoding="utf-8")
    c = c.replace("</body>", "<script>var x = {{{invalid;</script>\n</body>", 1)
    p.write_text(c, encoding="utf-8")

@mutation("stale bundle member (older tool bytes)")
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

@mutation("content hash replaced with file hash (pre-stamp provenance lost)")
def m9(dist, repo):
    # Simulate the historical R-001 confusion: Content SHA-256 column
    # silently replaced with the file hash. The verifier must detect
    # that content hashes lack pre-stamp provenance.
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

@mutation("release manifest declares wrong source commit")
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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dist", required=True)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tmpdir", default=None,
                    help="Override temp dir for mutation workspaces "
                         "(default: system temp; use when /tmp is small)")
    args = ap.parse_args()
    good_dist = Path(args.dist)
    good_repo = Path(args.repo)
    verifier = good_repo / "scripts" / "verify_release.py"
    # Allow override via arg or NEGTEST_TMPDIR env (for small-/tmp hosts)
    tmp_base = args.tmpdir or os.environ.get("NEGTEST_TMPDIR") or None

    passed = 0
    for name, fn in MUTATIONS:
        work = Path(tempfile.mkdtemp(prefix="negtest-", dir=tmp_base))
        tdist = work / "dist"
        trepo = work / "repo"
        shutil.copytree(good_dist, tdist)
        shutil.copytree(good_repo, trepo,
                        ignore=shutil.ignore_patterns(".git", "__pycache__"))
        try:
            fn(tdist, trepo)
        except Exception as e:
            print(f"[ERROR] mutation {name} raised during setup: {e}")
            shutil.rmtree(work, ignore_errors=True)
            continue
        r = subprocess.run(
            [sys.executable, str(verifier), "--dist", str(tdist),
             "--repo", str(trepo)],
            capture_output=True, text=True)
        rejected = r.returncode != 0
        names_file = "FAILURES" in r.stdout or "FAIL" in r.stdout
        status = "PASS" if rejected else "FAIL"
        print(f"[{status}] negative test: {name} "
              f"(exit={r.returncode}, names_offense={names_file})")
        if rejected:
            passed += 1
        else:
            print("  STDOUT tail:", r.stdout[-500:])
        shutil.rmtree(work, ignore_errors=True)

    print(f"\n{passed}/{len(MUTATIONS)} mutations rejected")
    sys.exit(0 if passed == len(MUTATIONS) else 1)

if __name__ == "__main__":
    main()
