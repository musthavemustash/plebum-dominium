# Project Operating Procedures — Plebumbtc.io / Plebum Dominium

**Scope:** These procedures apply to every change in this repository, including hotfixes, styling, copy, tools, packaging, CI, and deployment.

The standing project documents are `AGENTS.md` (this file), `PROJECT_VISION.md`, `SATCHEL_WORK_PROTOCOL.md`, `RELEASE_POLICY.md`, and `REGRESSION_LEDGER.md`. Contributors consult them at the start of each work session. They record persistent project constraints, not suggestions. Where an agent platform supports project-level memory or custom instructions, these documents are suitable for loading there. A prior conversation summary is not a substitute for the current documents.

## Mission and safety

- The project builds a **beginner-accessible, trustworthy, independent at-home Bitcoin self-custody educational guide**. It teaches risks and recovery, not false confidence. Readers should understand *why* each step exists.
- The project supports both current paths: **One Key + Passphrase** and **Three Keys / 2-of-3**. Their security models are never silently merged; distinct recovery requirements are never hidden; a multisig spending threshold is never presented as sufficient recovery information.
- **Offline-first and privacy-respecting operation:** no collection, transmission, logging, analytics, storage, or third-party delivery of seed words, passphrases, private keys, secrets, descriptors, recovery data, or demo inputs. No new cloud account, wallet connection, tracker, CDN, remote font, remote script, or external API is added without explicit human approval and a documented security review. Static local assets and progressive enhancement are preferred.
- Browser signals such as `navigator.onLine`, `file://`, airplane mode, or a UI indicator are never presented as evidence of an air gap. Limitations are described accurately. The project never promises perfect security, guaranteed recovery, true deletion, or crypto interoperability that has not been demonstrated.
- Reproducible educational examples and demonstrations use **clearly labeled fictional data only**. Real wallet secrets are never requested or exposed. Readers are warned that lost passphrases, incomplete multisig reconstruction data, and untested recovery can mean irreversible loss.

## No-regression rules

- The verified crypto baseline is frozen: **34 Python + 25 JavaScript tests** as of the 2026-11-02 audited archive. The baseline commit is recorded and re-proven against the current repository; a static count is not treated as proof of correctness over time. Cryptographic calculation code is changed only to correct an independently reproducible defect, with added tests and explicit review. Tests are never weakened, deleted, skipped, renamed, or faked to make CI green.
- Every corrected defect gains the narrowest practical **automated regression test**, plus a record in `REGRESSION_LEDGER.md` explaining the prevention. For non-automatable risks, a manual acceptance step and owner are documented.
- Both paths, printed documents, the offline kit, and the website stay aligned. HTML-without-JavaScript reading, accessibility, keyboard operation, print clarity, and real recovery cautions are preserved.
- Checksum correctness and packaging are **release blockers** (see `RELEASE_POLICY.md`). A published fingerprint is never patched by hand as a substitute for fixing its generator.

## Stop conditions

- **Release rule:** no observed clean build + independent verifier + protected deployment means no release. The 59 crypto tests alone do not constitute a release gate.
- If a tool is unavailable or a requirement cannot be verified, the status is reported as **BLOCKED / NOT VERIFIED**. Missing proof is never replaced with confidence language. Nothing is published after a failing or skipped check.
- Releases are never published from a cached `main` ZIP, an unverified mutable archive, or a source tree of unknown commit. Artifact freshness is never inferred from timestamps or filenames.
- Changes to CI bypass permissions, branch rules, source-of-truth generators, or security-critical behavior are proposed for human approval, never made silently.

## Required work report format

Each completed task is reported with:

1. **Intent** — the user outcome and which custody paths are affected.
2. **Scope / impact** — exact files, source of truth, impacted generated artifacts, risk level.
3. **Work performed** — changed files and tests added or updated.
4. **Evidence** — commands, exit codes, immutable Git commit, build artifact hashes, CI links/logs, and screenshots only when actually captured.
5. **Status** — DONE (verified), PARTIAL, BLOCKED, or NOT VERIFIED; unresolved items and next steps.

When requirements conflict, the priority order is: safety and a working recovery path first, then explicit owner direction, then project policy. Protections are not removed unilaterally to meet a deadline. Clarification is requested only when a genuinely consequential choice is blocked; otherwise work proceeds transparently.
