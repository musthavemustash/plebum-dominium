# Homepage preview link — 2026-11-04

Owner explicitly requested a production homepage link to the staging site, choosing a preview link instead of an automatic redirect. This is limited authorization for that link, not promotion of staging content.

Base: daa161dd87d1268e106474e0d7ac51a978fac07d.

Canonical homepage generator: scripts/build.py. Tracked docs/index.html receives only the matching notice; unrelated pre-existing generator/output drift is not included in this change. Both paths retain existing navigation. No new script, runtime request, wallet behavior, or automatic redirect.

Checks: generator output contains the same notice as tracked homepage; diff whitespace check passes; Python crypto 34 passed / 0 failed; JavaScript crypto 25 passed / 0 failed. These are static checks, not browser or custody certification. The notice uses existing responsive callout styles and a standard no-JS anchor. Physical mobile layout is not verified.

Publication requires the existing protected release-gate workflow to pass. Do not bypass it. CI and deployment outcome are recorded on the pull request.
