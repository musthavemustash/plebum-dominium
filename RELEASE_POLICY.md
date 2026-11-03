# Release Policy — Plebumbtc.io / Plebum Dominium

**Enforcement note:** Actual enforcement lives in CI and the publishing mechanism, not in this prose. The release-pipeline implementation defines the detailed architecture; this file is the durable, repo-local policy record.

## Release acceptance criteria

A release may be labeled **VERIFIED** only when a gate has evaluated the **exact final bytes** destined for deployment, returned exit code **0**, and the deployment job is structurally dependent on that gate succeeding. Any other outcome is reported as **REJECTED / BLOCKED / NOT VERIFIED**. The 59 crypto tests are necessary but not sufficient.

## The supported pipeline

1. Pin a complete, immutable 40-character source commit SHA; use a clean checkout and staging directory. Dirty, cached, or stale state is rejected.
2. Generate canonical HTML/CSS/JS/tool source assets. Both custody paths and the crypto baseline are preserved.
3. Generate PDFs and define the exact **pre-stamp Content SHA-256 provenance**. Stamp PDFs and compute **File SHA-256 on finished PDF bytes**. The two columns are never conflated. If content provenance is missing, certification fails (or the field is explicitly marked unverifiable, blocking releases that claim full content-hash verification).
4. Build the tools bundle from the same final canonical tool bytes; compare each packaged member against source. No edits occur after packaging.
5. Generate `VERIFY.md`, the public checker/fingerprints, and all metadata from one authoritative computed manifest, with verified sizes and digests. Manually maintained duplicate hash tables are avoided.
6. Build the offline package **last**, from staged verified files, with all local assets, linked kits, handouts, and demos; its own ZIP, stale ZIPs, `.pyc` files, caches, logs, and secrets are excluded. Internal links are rewritten relative to the extracted files. External destinations are not rewritten, and new network dependencies are not introduced.
7. Produce the top-level release manifest **outside** archives, with immutable SHA, artifact filenames, sizes, hashes, and toolchain versions. A ZIP's own hash is never embedded inside itself.
8. In a new clean checkout or isolated verifier, extract the final artifacts and check their bytes, navigation, and expected behaviors. Re-hash immediately before deployment. Exactly the verified bytes are promoted; nothing is regenerated after gate success.

## Minimum release gate (all required)

- Python test suite exits 0 with the expected baseline test inventory; JS suite exits 0 with the expected inventory; no skipped or disabled checks without approved rationale.
- All 17 kit PDF File SHA-256 values match the actual shipped PDF bytes. Content hashes have independently traceable pre-stamp inputs and separate verification status.
- All published utility hashes and sizes agree across every printed/HTML manifest, source, and distribution package. Tools-bundle members are byte-identical to canonical source (except an allowed bundle-only README).
- The offline ZIP contains all referenced pages, assets, and downloads, including `assets/css/guide-steps.css`, `assets/js/guide-demos.js`, `descriptor-demo.html`, `passphrase-demo.html`, and required `kit/` resources.
- No offline internal root-relative links; no broken internal targets; no nested offline ZIP; no unexpected remote runtime assets or network requests.
- Syntax checks on **all shipped JavaScript**, including inline scripts in legacy pages. JSON-LD is not executable JS. Console/runtime browser smoke checks cover both paths with network blocked, on a clean extracted offline ZIP. Browser checks are not claimed unless actually run.
- HTML, PDF, download, and offline variants agree on security-critical facts, disclaimers, and recovery requirements.
- Independent verification of the final release manifest, complete file list, and final artifact hashes; no changes after the gate.
- **Failure-injection test:** one PDF, one bundled tool, one manifest entry, one offline link, one shipped JS script, and one crypto test are intentionally corrupted in isolated test builds. Each case must produce a nonzero gate exit and block deployment. The good baseline is restored between cases. Production is never mutated for testing.

## Publish-path enforcement

- GitHub Actions checks alone do not stop deployment when GitHub Pages publishes directly from a branch. Branch-based Pages can publish an unreviewed direct push. The project requires maintainer-approved protected-branch/PR configuration plus a workflow-artifact Pages deployment design (or equivalent) in which `deploy` has `needs: build-and-gate` and cannot run on failure.
- Other production write paths are disallowed, or documented as non-disableable with enforcement marked incomplete. Bypass and permission changes require owner approval.
- Silent fallback to mutable archives, manual checksum edits, or previous distribution files is prohibited.

## Required release evidence

- Full source SHA; commit and CI run links/locations; actual build and gate commands with exit codes.
- Hash and size of the site package, tools bundle, and offline ZIP; the 17/17 PDF table; utility byte-equality evidence; offline smoke-test findings; exact changes shipped.
- Tested failure-injection scenarios with explicit proof that a failed gate prevents deployment.
- Areas that remain unverifiable: physical air-gapping, OpenPGP/GnuPG interoperability, hardware workflows, complete testnet recovery, and other out-of-scope tests. Proof is never invented.

**Hard rule: no green, independently observed final-artifact gate means no release.**
