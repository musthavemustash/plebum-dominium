# Fix log

Every change applied by `scripts/apply-fixes.py`, with the reason. The script
is idempotent — re-running it never double-applies.

## FIX-1 — Passphrase-loss guidance (encryption sheet) — CRITICAL

**Was:** "If this passphrase is lost, the coins are not gone. Two plates can
rebuild the map."

**Problem:** Cryptographically false. Two seeds cannot reconstruct the third
key's xpub, so without a readable map the descriptor and all addresses are
unrecoverable. Proven empirically in the Oct 2026 bench test.

**Now:** States that three plates rebuild the map exactly, two cannot, and the
passphrase paper is a single point of failure that must be backed up in two
separate places away from plates and USBs.

## FIX-2 — Exact download locations (verify sheet)

**Problem:** The sheet named files but not where to get them or how to check
signatures; a user had to hunt for correct URLs.

**Now:** Exact URLs for the Sparrow release assets, the Electrum tarball, and
the Ian Coleman GitHub release (not browser save-as), plus both PGP key
fingerprints (`D4D0D320…4B40`, `6694D8DE…70E6`) and a note that the GPG
"not certified with a trusted signature" warning is expected — what matters is
`Good signature` plus a matching fingerprint.

## FIX-3 — Exactly 256 bits of dice entropy (dice sheet)

**Was:** "At least 256 bits are required. More is fine. The extra bits are
folded down." (The practice grid suggested 320–400.)

**Problem:** With more than 256 bits, the converter and the Ian Coleman page
hash the extra entropy differently, so the mandatory "two tools must agree"
check fails spuriously and the user stalls.

**Now:** Roll exactly 256 bits (128 pairs, ~32 shakes) and stop. No security is
lost — everything folds to 256 bits anyway. The interactive practice grid
(which doesn't survive as static content) is replaced with a pointer to the
printed grid in the bench-sheet PDF.
