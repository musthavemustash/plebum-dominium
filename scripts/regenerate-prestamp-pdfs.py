#!/usr/bin/env python3
"""Regenerate pre-stamp PDFs for independent provenance verification.

This script regenerates the 17 kit PDFs WITHOUT stamping, for use in
CI provenance verification (Option A). The verifier hashes these
regenerated PDFs itself and compares against the manifest's
content_sha256 values.

Usage:
    python3 scripts/regenerate-prestamp-pdfs.py --out <dir>

The output directory will contain the 17 unstamped PDFs.
Does NOT modify kit/ or require stamping tools.

This is the same generation logic used by release.py Stage C,
but isolated for independent verification.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

def main():
    ap = argparse.ArgumentParser(
        description="Regenerate pre-stamp PDFs for provenance verification")
    ap.add_argument("--out", required=True,
                    help="Output directory for unstamped PDFs")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    repo_root = Path(__file__).resolve().parent.parent
    env = os.environ.copy()
    # build-kit-pdfs.py respects KIT_PDF_OUT for output directory
    env["KIT_PDF_OUT"] = str(out)
    # Deterministic builds: fixed timestamp for reproducible PDFs.
    # Must match the value used in release.py Stage C and CI.
    env["SOURCE_DATE_EPOCH"] = "0"

    print(f"[regenerate] Generating pre-stamp PDFs to {out}", flush=True)

    # 0. Rebuild docs/ from content/ to ensure input parity with release.py
    # Stage B. The release job rebuilds docs/ before generating PDFs; the
    # regenerate job must do the same, otherwise PDFs are built from
    # different HTML inputs and hashes will not match.
    # (Simplified Stage B: build.py + restore verify-file.html)
    import shutil
    verify_path = repo_root / "docs" / "verify-file.html"
    verify_backup = None
    if verify_path.exists():
        verify_backup = out / "verify-file.html.bak"
        shutil.copy2(verify_path, verify_backup)
        print(f"[regenerate] backed up docs/verify-file.html", flush=True)

    print(f"[regenerate] Rebuilding docs/ via build.py...", flush=True)
    r = subprocess.run(
        [sys.executable, "scripts/build.py", "--base", "/"],
        cwd=str(repo_root), env=env, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[regenerate] FATAL: build.py failed", file=sys.stderr)
        print(r.stderr[-1000:], file=sys.stderr)
        sys.exit(1)

    if verify_backup and not verify_path.exists():
        shutil.copy2(verify_backup, verify_path)
        print(f"[regenerate] restored docs/verify-file.html", flush=True)

    # Generate the 16 sheet PDFs (build-kit-pdfs.py outputs to KIT_PDF_OUT)
    r = subprocess.run(
        [sys.executable, "scripts/build-kit-pdfs.py"],
        cwd=str(repo_root), env=env, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[regenerate] FATAL: build-kit-pdfs.py failed", file=sys.stderr)
        print(r.stderr[-1000:], file=sys.stderr)
        sys.exit(1)

    # Generate the fire card (15_Fire_Card.pdf)
    # build-fire-card.py accepts --out
    r = subprocess.run(
        [sys.executable, "scripts/build-fire-card.py",
         "--out", str(out / "15_Fire_Card.pdf")],
        cwd=str(repo_root), env=env, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[regenerate] FATAL: build-fire-card.py failed", file=sys.stderr)
        print(r.stderr[-1000:], file=sys.stderr)
        sys.exit(1)

    # Generate the print packet (02_Print_Packet.pdf)
    # build-print-packet.py accepts --out for the main variant
    r = subprocess.run(
        [sys.executable, "scripts/build-print-packet.py",
         "--out", str(out / "02_Print_Packet.pdf")],
        cwd=str(repo_root), env=env, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[regenerate] FATAL: build-print-packet.py failed", file=sys.stderr)
        print(r.stderr[-1000:], file=sys.stderr)
        sys.exit(1)

    # NOTE: Presentation_Handouts.pdf is a static asset (not generated from
    # source). It exists only as kit-b64/kit/Presentation_Handouts.pdf.b64.
    # Independent regeneration (Option A) does not apply to it. The verifier
    # skips provenance for this file; file hash verification still applies.

    # Verify we got the expected 16 PDFs (17 total minus static Presentation_Handouts.pdf)
    pdfs = sorted(out.glob("*.pdf"))
    print(f"[regenerate] Generated {len(pdfs)} PDFs", flush=True)
    for p in pdfs:
        print(f"  {p.name} ({p.stat().st_size} bytes)")

    # Define exact expected set of 16 regenerable PDFs
    EXPECTED_REGENERABLE = {
        "00_Project_Overview.pdf", "02_Print_Packet.pdf", "03_Checklist.pdf",
        "04_Airgap.pdf", "05_Verify.pdf", "06_Dice.pdf", "07_Sparrow.pdf",
        "08_Signing.pdf", "09_Titanium.pdf", "11_Encryption.pdf",
        "12_Inheritance.pdf", "13_FAQ.pdf", "14_Speaker.pdf",
        "15_Fire_Card.pdf", "Handouts_No_Cover.pdf", "Terms.pdf",
    }
    actual_names = {p.name for p in pdfs}
    missing = EXPECTED_REGENERABLE - actual_names
    extra = actual_names - EXPECTED_REGENERABLE
    if missing or extra:
        print(f"[regenerate] FATAL: PDF inventory mismatch", file=sys.stderr)
        if missing:
            print(f"  Missing: {sorted(missing)}", file=sys.stderr)
        if extra:
            print(f"  Extra: {sorted(extra)}", file=sys.stderr)
        sys.exit(1)

    print("[regenerate] DONE", flush=True)

if __name__ == "__main__":
    main()
