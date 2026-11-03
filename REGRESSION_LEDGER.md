# Regression Ledger — Plebumbtc.io / Plebum Dominium

**Purpose:** No defect is fixed twice without adding the least costly reliable test that prevents recurrence. Historical observations below come from the `plebumbtc-main-site-20261102-1910.zip` archive audit (an audit of a supplied archive, not a verified description of the live repository at any later date). Current repository state is rechecked with evidence before any status changes.

| ID | Observed failure / permanent lesson | Preventing test / enforcement | 2026-11-02 19:10 baseline |
|---|---|---|---|
| R-001 | 7 of 17 published PDF **File SHA-256** entries stale; separate PDF pre-stamp **Content SHA-256** previously conflated | Build after stamping; independently recompute 17 file hashes and verify content provenance | OPEN at archive audit; recheck |
| R-002 | Python BIP39 converter differed between canonical file, `tools-bundle.zip`, offline ZIP and public fingerprints | Re-open bundles, compare bytes to canonical source and manifest; all identifiers must match | OPEN at archive audit; recheck |
| R-003 | Offline ZIP had missing assets, missing `kit/` files and earlier nested copies of itself | Assemble offline ZIP last; assert contents and forbid self-nesting/caches | Some omissions fixed in 19:10; final verification pending |
| R-004 | 134 root-relative HTML links in extracted offline guide | Static resolver and browser `file://` smoke tests for both paths | OPEN at archive audit; recheck |
| R-005 | `threat-model-one.html` and `threat-model-easy.html` shipped malformed inline JavaScript | Compile every executable inline script and JS asset, including orphaned pages | OPEN at archive audit; recheck |
| R-006 | Browser indicators inferred network isolation from `navigator.onLine` | Static checks + reviewed claims; air gap is never certified from browser state | **FIXED** 2026-11-02: `navigator.onLine` removed as blocking signal from both tools; protocol-only status (http/https blocks, file:// shows honest warning); local commit, tools rebuilt |
| R-007 | Stale package blamed on mutable/cached repository ZIP | Full commit SHA; clean checkout; verify final bytes, no mutable `main` ZIP inputs | Architectural risk, enforcement needed |
| R-008 | Cryptographic tests passed while release artifacts were inconsistent | Independent final-artifact gate + negative failure-injection proof and deploy dependency | Gate not demonstrated in supplied archive |
| R-009 | Printed/offline/HTML security-critical information risks diverging across variants | Cross-format consistency checks and review of both paths | **MITIGATED** 2026-11-02: canary check added to `verify_release.py` (critical strings verified present across HTML sheets); full PDF text extraction still manual |

## Rules for updates

- An entry is added when a new defect is discovered (linking the precise input, environment, failure, and root cause as known).
- Status values: **OPEN**, **FIXED (commit + test evidence)**, **NOT VERIFIED**, or **ACCEPTED RISK (owner decision)**. A passing agent response is not evidence.
- An item moves to FIXED only when an automated regression test and/or verified manual acceptance record demonstrates the actual final-distribution issue is resolved.
- History is never erased to make the dashboard look clean. Resolution or recurrence notes are appended with commit and date. Artifact SHA-256 values are not hardcoded as timeless rules; they are recomputed against each release.

## Entry template

```
ID / Date / affected paths:
Problem and user impact:
Reproduction and root cause (if known):
Prevention: specific test / check and where it runs:
Fix commit and final artifact evidence:
Current status / human acceptance if required:
```
