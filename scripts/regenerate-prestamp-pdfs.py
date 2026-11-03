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

    print(f"[regenerate] Generating pre-stamp PDFs to {out}", flush=True)

    # Generate the 16 sheet PDFs (build-kit-pdfs.py outputs to KIT_PDF_OUT)
    r = subprocess.run(
        [sys.executable, "scripts/build-kit-pdfs.py"],
        cwd=str(repo_root), env=env, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[regenerate] FATAL: build-kit-pdfs.py failed", file=sys.stderr)
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

    # Verify we got the expected 17 PDFs
    pdfs = sorted(out.glob("*.pdf"))
    print(f"[regenerate] Generated {len(pdfs)} PDFs", flush=True)
    for p in pdfs:
        print(f"  {p.name} ({p.stat().st_size} bytes)")

    if len(pdfs) != 17:
        print(f"[regenerate] WARNING: expected 17 PDFs, got {len(pdfs)}",
              file=sys.stderr)

    print("[regenerate] DONE", flush=True)

if __name__ == "__main__":
    main()
