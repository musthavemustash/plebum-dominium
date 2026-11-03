## Outcome and path impact
- [ ] Change explained in plain language with affected custody path(s): One Key + Passphrase / Three Keys / both
- [ ] Potential recovery, privacy, accessibility, no-JS, print, and offline impacts reviewed

## Evidence and checks
- [ ] Exact source commit SHA and changed canonical source files given
- [ ] Regression test added for any fixed defect; ledger updated (or manual verification rationale given)
- [ ] Python crypto suite executed successfully (baseline 34, or documented approved inventory change)
- [ ] JavaScript crypto suite executed successfully (baseline 25, or documented approved inventory change)
- [ ] Generated distributions checked (not just source)
- [ ] PDF file/content hash distinction maintained; final PDF bytes independently checked
- [ ] Tool fingerprints, sizes, and bundle members consistent
- [ ] Offline ZIP extracted, link/download integrity verified, both paths tested, no nested offline ZIP
- [ ] All shipped executable JavaScript checked, including inline scripts
- [ ] Reproducible clean checkout / immutable SHA recorded
- [ ] **Final-artifact release gate exits 0 and deployment job depends on it** (required for release PR)
- [ ] Failure-injection test evidence exists for gate changes (required for gate changes)
- [ ] Explicit remaining NOT VERIFIED areas listed

## Approval and release decision
- [ ] Maintainer approval requested for crypto, secret-handling, domain, new network dependencies, CI bypass, branch protection, or deployment changes
- [ ] No release unless the complete gate and protected publish path demonstrably pass

**Status:** VERIFIED / PARTIAL / BLOCKED / NOT VERIFIED
**Source SHA:**
**Gate run / logs:**
**Artifacts SHA-256 + size:**
**Remaining limitations:**
