#!/usr/bin/env python3
"""Apply the audit fixes to content/ (idempotent - safe to re-run).

Usage: python3 scripts/apply-fixes.py
Each fix is logged; already-applied fixes are skipped.
Run scripts/build.py afterwards to regenerate the site.

Fix list (from the Oct 2026 bench-test audit):
  FIX-1  encryption.md: the "two plates can rebuild the map" claim is
         cryptographically false - rewrite the passphrase-loss guidance.
  FIX-2  verify.md: exact download URLs, signing-key fingerprints, and a
         note about the expected GPG trust warning.
  FIX-3  dice.md: roll exactly 256 bits (extra bits make the two-tool
         check fail spuriously); replace the interactive grid blob with
         a pointer to the printed grid.
"""
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
os.chdir(ROOT)

applied, skipped = [], []


def fix(path, name, old, new, count=1):
    with open(path) as f:
        src = f.read()
    if new in src:
        skipped.append(name)
        return
    if src.count(old) != count:
        print(f"!! {name}: expected {count} occurrence(s), found {src.count(old)} - NOT applied")
        return
    with open(path, "w") as f:
        f.write(src.replace(old, new))
    applied.append(name)


def fix_re(path, name, pattern, new, sentinel):
    with open(path) as f:
        src = f.read()
    if sentinel in src:
        skipped.append(name)
        return
    src2, n = re.subn(pattern, new, src, flags=re.S)
    if n != 1:
        print(f"!! {name}: expected 1 match, found {n} - NOT applied")
        return
    with open(path, "w") as f:
        f.write(src2)
    applied.append(name)


ENC = "content/handouts/encryption.md"
fix(
    ENC,
    "FIX-1 passphrase-loss guidance",
    "If this passphrase is lost, the coins are not gone. Two plates can rebuild the map. "
    "The path is m/48'/0'/0'/2'. Write that path on the inheritance sheet. It is not a secret.",
    "If this passphrase is lost, the coins are not gone \u2014 as long as all three plates still exist. "
    "Three seeds rebuild the map exactly. Two seeds cannot: the third key's xpub cannot be derived from the other two. "
    "Treat this passphrase paper with the same care as a plate. It is a single point of failure for every encrypted copy "
    "of the map \u2014 back it up in two separate places, away from the plates and the USB drives. "
    "The path is m/48'/0'/0'/2'. Write that path on the inheritance sheet. It is not a secret.",
)

VER = "content/handouts/verify.md"
fix(
    VER,
    "FIX-2 exact download locations",
    "[Verify package integrity](/verify-software)\n",
    """[Verify package integrity](/verify-software)

## Exact download locations

- **Sparrow:** `https://github.com/sparrowwallet/sparrow/releases/download/2.5.5/sparrowwallet-2.5.5-x86_64.tar.gz`, plus `sparrow-2.5.5-manifest.txt` and `sparrow-2.5.5-manifest.txt.asc` from the same release page. Import the signing key with `curl https://keybase.io/craigraw/pgp_keys.asc | gpg --import` and confirm the fingerprint `D4D0D3202FC06849A257B38DE94618334C674B40`.
- **Electrum:** `https://download.electrum.org/4.8.2/Electrum-4.8.2.tar.gz` plus the `.asc` signature file. Import the signing key from `https://raw.githubusercontent.com/spesmilo/electrum/master/pubkeys/ThomasV.asc` and confirm the fingerprint `6694D8DE7BE8EE5631BED9502BD5824B7F9470E6`.
- **Ian Coleman:** do not use the browser's save-as on the live page \u2014 that yields a different file. Download `bip39-standalone.html` from `https://github.com/iancoleman/bip39/releases/latest` and compare its SHA-256 against the PGP-signed hash printed on that release page.

Expect this warning from `gpg --verify` on a first import: "WARNING: This key is not certified with a trusted signature!" That is normal. What matters is the line above it: `Good signature`, and the fingerprint matching the one published above.
""",
)

DICE = "content/handouts/dice.md"
fix(
    DICE,
    "FIX-3a exactly 256 bits",
    "Write only 0 and 1. At least 256 bits are required. More is fine. The extra bits are folded down.",
    "Write only 0 and 1. Roll exactly 256 bits \u2014 128 pairs, about 32 shakes \u2014 then stop. "
    "More bits do not add security (everything folds down to 256), and extra bits make the two tools below disagree, "
    "which stops the work for no reason.",
)
fix_re(
    DICE,
    "FIX-3b practice grid note",
    r"## Practice grid.*?(\nNext\. The 2-of-3 is built next\.)",
    "## Practice grid\n\nUse the printed recording grid in the bench sheet PDF \u2014 each seed needs about 32 shakes for 256 bits. "
    "Count the pairs as you go and stop at 128.\n\\1",
    sentinel="printed recording grid in the bench sheet PDF",
)

print(f"applied: {len(applied)}, skipped (already present): {len(skipped)}")
for name in applied:
    print(f"  + {name}")
for name in skipped:
    print(f"  = {name}")
if not applied and not skipped:
    sys.exit("nothing to do?")
