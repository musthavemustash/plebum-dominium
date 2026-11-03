# Work Session Protocol — Plebumbtc.io / Plebum Dominium

## Session start

1. Consult `AGENTS.md`, `PROJECT_VISION.md`, `RELEASE_POLICY.md`, and `REGRESSION_LEDGER.md`. Confirm the project scope and both custody paths.
2. Inspect `git status`, the current full commit SHA, relevant generator scripts, workflow files, and `docs/` / `tests/`. Previous documented blockers are read as historical record and rechecked before being relied upon.
3. Identify the real source-of-truth file(s). Generated outputs (`docs/kit/*.zip`, `VERIFY.md`, final PDFs, hashed artifacts) are never hand-edited to fix a generator defect.
4. Describe the user-visible outcome, threat-model impact, files to change, impacted derived files, and verification plan. Trivial edits are described briefly.

## During work

- Changes stay minimal, reviewable, and auditable. Each logical change ships with its regression test.
- When shared pages, CSS, JS, or explanatory guidance change, both One Key + Passphrase and Three Keys / 2-of-3 are explicitly checked for regressions.
- Privacy, no-JS fallback, progressive enhancement, keyboard/accessibility, and printable offline materials are preserved.
- On an audit finding, a test is added to prevent recurrence, `REGRESSION_LEDGER.md` is updated, and the fixing commit is cited. Cases requiring human or physical testing are recorded as such.
- **Work is not marked done because a file was edited or pushed.** Only observable output from the correct repository SHA and release artifacts counts.

## Before completion

- Targeted checks and both crypto suites run; an actual clean release build and gate run precede any publishing task. The exact command and observed exit code are recorded.
- Generated distributions are inspected, not just the source directory: downloadable ZIP member bytes, manifest hashes, HTML syntax, link resolution, and offline end-to-end behavior.
- For non-release tasks, source-level verification is clearly distinguished from release-ready verification.
- If the release gate is not implemented or fails, the outcome is reported as `NO RELEASE` with a precisely scoped reason. "All clear" or "ready" is not stated without gate evidence.

## Work report format (factual evidence, not optimistic language)

```
TASK: <goal>
SOURCE COMMIT: <full SHA or NOT VERIFIED>
FILES CHANGED: <paths>
REGRESSIONS ADDED: <tests>
CHECKS: <command> -> <exit code + results; or NOT RUN with reason>
ARTIFACTS: <paths + SHA-256 + size; or NOT PRODUCED>
DEPLOY GATE: PASS | FAIL | NOT IMPLEMENTED | NOT VERIFIED
DEPLOYMENT: NOT ATTEMPTED | BLOCKED | DEPLOYED (with real proof)
KNOWN LIMITS / NEXT ACTION: <concrete facts>
```

## If project instructions are overlooked

- Project policy is loaded by agent tooling **and** checked by code review and CI. If a platform does not read `AGENTS.md`, its contents are copied into that platform's supported project-wide instructions with links to these repository files. A one-off chat prompt is not relied upon.
- A memory note cannot enforce CI; releases are enforced through workflow dependencies, branch protections/rulesets, and a separate verifier of final bytes.
