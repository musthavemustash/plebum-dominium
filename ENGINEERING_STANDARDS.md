# Plebumbtc.io — Software Engineering & Development Standards

**Document type:** Project engineering reference  
**Scope:** Architecture, security, correctness, user experience, build integrity, and maintainability  
**Status:** Proposed project standards for owner review  
**Purpose:** A descriptive account of the qualities and verification criteria of the Plebumbtc.io software.

> **Foundational principle:** Reliability matters more than novelty. Clarity matters more than cleverness. Verification matters more than assurances.

## 1. Engineering philosophy

Plebumbtc.io is an educational resource for independent Bitcoin self-custody. The software reflects the values expressed in the educational material: independence, transparency, simplicity, resilience, and personal responsibility.

The engineering objective is a dependable, understandable system that supports the complete educational experience without unnecessary technical complexity. Visitors should encounter tools that behave as described, consistent online and printed instructions, and essential resources that continue to work without an internet connection where supported.

Software quality is part of the educational experience. Verifiable behavior—not strong claims or polished appearance alone—provides the foundation for trust.

## 2. Simple, understandable architecture

A static-first architecture is well suited to this project. Standard HTML, CSS, and JavaScript can support rich interactive education without requiring continuous server-side operation. Architecture decisions balance functionality against their maintenance, privacy, compatibility, and security costs.

The codebase has these characteristics:

- **Minimal dependencies.** External libraries are limited to those with a clear benefit and manageable security and maintenance implications.
- **Separation of concerns.** Educational content, presentation, interactive demonstrations, cryptographic utilities, and build tooling have distinct responsibilities.
- **Reusable patterns.** Shared navigation, layouts, styles, accessibility behavior, and instructional components remain consistent across custody paths.
- **Portable content.** Core guides and references are accessible without dependence on a proprietary service or one development framework.
- **Documented assumptions.** Critical behaviors do not rely on hidden conventions or a single contributor's memory.

A future maintainer should be able to understand the structure of the repository and the purpose of its components without reconstructing years of conversational history.

## 3. Security as an architectural principle

The project teaches practices where misunderstanding or software mistakes can lead to irreversible financial loss. The codebase therefore distinguishes clearly between educational demonstrations and tools that affect operational security.

### Sensitive information

The educational website does not need visitors' real wallet recovery phrases, private keys, or BIP39 passphrases. Interactive demonstrations use clearly labeled fictional examples. Any supported local-only tool has a documented data-handling model that accurately describes its limitations.

### Reduced attack surface

Dependencies, third-party scripts, network calls, permissions, analytics, and privileged features are limited to what is necessary. Security-sensitive operations are isolated from unrelated presentation logic where practical.

### Clear security boundaries

A browser application is not equivalent to a hardware wallet, independently verified offline operating system, or proven air-gapped computer. Browser network signals, including `navigator.onLine`, do not prove isolation from networks. User-facing wording reflects this distinction.

### Established standards

Cryptographic behavior corresponds to applicable Bitcoin standards and independent reference implementations. New cryptographic primitives are not an architectural goal. Standard algorithms, vetted implementations, and known test vectors are preferred wherever suitable.

Security claims remain specific, evidence-based, and proportional to the tests actually performed.

## 4. Correctness and independent verification

Security-sensitive calculations have defined inputs, outputs, error conditions, and expected reference results. Verification encompasses normal operation, edge cases, malformed inputs, and relevant failure conditions.

The testing model includes:

- **Unit tests** for calculations, validation, and individual functions.
- **Integration tests** for interactions between utilities, user interfaces, and local resources.
- **Reference-vector tests** using published standards and independently implemented results.
- **Regression tests** for previously observed defects.
- **End-to-end exercises** for complete instructional and recovery workflows in appropriate, safe practice environments.
- **Negative tests** for invalid values, corrupt assets, incorrect checksums, missing dependencies, and unsafe assumptions.

Agreement between two copies of the same implementation is not necessarily independent verification. The existing 59-test cryptographic baseline is an important historical benchmark, not a complete security certification or a substitute for further testing.

Test results describe the exact revision and artifact set examined, along with any limitations.

## 5. Offline-first functionality

Offline operation is a core product capability. The offline guide is a complete distribution experience rather than a byproduct of zipping up online files.

The supported offline experience includes working local navigation, required styles and scripts, printable handouts, downloads, instructional demonstrations, and clear opening instructions. Each custody path is represented consistently with its online counterpart.

Local-file behavior differs from ordinary HTTPS browsing. Browser restrictions involving `file://` URLs, modules, fetch requests, and cross-origin policies are relevant to the supported offline workflow. Tests are based on the actual method visitors are expected to use, including extraction and direct opening when that is the stated procedure.

A browser indicating “offline” is not proof that a device is isolated or safe for handling real secrets. The interface explains exactly what has and has not been verified.

## 6. One authoritative source of truth

Every published artifact has an identifiable canonical source. Web pages, PDFs, utilities, offline packages, and verification records do not evolve as unrelated copies of the same material.

The repository distinguishes:

1. **Source materials:** Authoritative code, educational content, templates, configuration, and build definitions.
2. **Generated materials:** PDFs, bundles, manifests, and distributable packages derived from those sources.
3. **Published releases:** A versioned set of final artifacts tied to a specific revision.

For any one release, identical utility files have identical bytes wherever they are distributed. Shared educational instructions are consistent across page, PDF, and offline forms, subject to clearly documented presentation differences.

The distinction between authored material and generated output is visible in the repository structure and developer documentation.

## 7. Reproducible builds and release integrity

Release integrity connects the code that was reviewed with the files visitors actually receive. A source-code test result is insufficient when a published archive contains stale or different bytes.

The build process has a defined dependency order: canonical source and content are finalized; derived documents and utilities are generated; fingerprints and manifests are calculated from the **final bytes**; distribution packages are assembled; and the exact resulting artifacts undergo independent verification.

For example, a PDF's **File SHA-256** is calculated from its final complete file. A separately defined **Content SHA-256** has a documented generation method and is not silently replaced with the complete-file hash. Self-referential manifests or stamped content are handled with an explicit, stable procedure rather than circular recalculation.

Release verification establishes:

- The exact source commit and build inputs.
- Successful applicable tests for that revision.
- Matching PDF fingerprints and accurate manifest columns.
- Canonical utility identity across source, tools bundle, and published links.
- Consistent downloadable package contents.
- Functional offline asset references and navigation.
- Absence of unintended nested or self-including distribution archives.
- A validated final artifact collection, rather than merely a validated working directory.

A SHA-256 match checks integrity relative to an expected value; it does not independently prove publisher identity. Authenticity also depends on obtaining verified release information through a trusted channel, such as authenticated publishing or an appropriately verified signature.

A release is considered verified only when the final distributed artifacts pass the defined checks.

## 8. Regression prevention and continuous integration

Past defects are durable engineering evidence. Significant regressions are documented with symptoms, cause where known, affected artifacts, corrective changes, and a repeatable prevention test where practical.

Historically observed categories include:

- Stale or incorrect PDF file fingerprints.
- Confusion between full-file and separately defined content hashes.
- Tools bundles containing a different revision of a utility than the site.
- Incorrect published utility checksums.
- Offline packages missing linked resources, CSS, or demonstrations.
- Root-relative links that fail when the offline site is opened from disk.
- Self-inclusion or nesting of generated ZIP packages.
- Malformed JavaScript in legacy or less frequently used pages.
- Security wording that overstates what network-status checks establish.

Automated integration evaluates both application behavior and final release integrity. Tests include controlled negative scenarios—for example, a corrupted PDF fingerprint, missing offline asset, or broken script—to demonstrate that the release checks return failure instead of a misleading success.

Normal publication is conditioned on passing the defined required checks. A report of success without corresponding execution evidence is not equivalent to a verified release.

## 9. Maintainable, readable code

Long-term maintainability is a first-class engineering property. Clear names, focused functions, small testable modules, explicit invariants, and modest abstractions make the code easier to inspect and safer to change.

Comments explain rationale, security assumptions, non-obvious constraints, and intentional tradeoffs rather than restating obvious syntax. Security-sensitive functions have understandable validation and failure behavior.

Unused code, obsolete pages, duplicated implementations, stale generated copies, and conflicting documentation are maintenance risks. Historical material that remains published has an explicit purpose and receives the same basic validity checks as current pages, or is deliberately retired with preserved redirects or archival context when appropriate.

Dependencies and runtime assumptions are inventoried and reviewed as they age.

## 10. User experience and accessibility

The software's internal clarity should support a clear visitor experience. The two custody paths remain distinct while sharing coherent design patterns and predictable navigation.

Accessible semantic markup, keyboard operability, screen-reader compatibility, meaningful error messages, readable typography, sufficient contrast, and reduced-motion support form part of normal quality expectations.

Mobile layouts, print layouts, expandable explanations, diagrams, and interactive exercises retain essential security information. Critical warnings do not disappear behind visual effects or inaccessible controls.

Demonstrations make fictional data obvious. Loading states, unavailable features, validation errors, and browser limitations are communicated plainly. A visual confirmation never implies that an unperformed security check succeeded.

The overall design supports a calm, concise reading experience with deeper detail available where meaningful, including the established warm-paper reading surfaces and focused dark demonstration panels.

## 11. Privacy and data minimization

Plebumbtc.io's implementation reflects its self-sovereignty mission. Core educational access does not depend on accounts, tracking, or unnecessary disclosure of personal information.

External scripts, third-party embeds, background requests, and telemetry receive particular scrutiny. Locally hosted assets are preferred where practical, especially for core offline functions.

Any network requirement has a clear purpose and an accurate visitor-facing explanation. Claims about privacy are consistent with actual network behavior and can be checked with suitable browser and network inspection.

## 12. Documentation and long-term sustainability

Project knowledge belongs in version-controlled documentation that remains accessible to future contributors. Important design decisions, security assumptions, tool limitations, build commands, dependencies, regression history, and release verification criteria are documented alongside the relevant code.

The site should remain understandable and reproducible without access to one developer's conversation history, a specific AI coding agent's memory, or an undocumented local machine.

Documentation evolves with functionality and test coverage. Published user instructions, technical references, printed materials, and repository documentation describe the same current behavior.

## 13. Controlled change and review

Changes to security-sensitive logic, custody-path instructions, offline packaging, or release generation carry greater review risk than isolated visual refinements. The review process is proportionate to the possible consequences of a mistake.

A complete change record identifies its scope, rationale, affected artifacts, relevant test results, and any remaining limitations. The distinction between **implemented**, **tested**, **independently verified**, and **released** remains explicit.

Changes in cryptographic behavior receive reference-vector checks and focused review. Changes in educational material receive consistency and recovery-path review. Changes in distribution packaging receive artifact-level integrity checks.

Design improvements do not silently change custody semantics or weaken an established safeguard. Scope expansion and changes in risk assumptions remain visible decisions rather than incidental side effects.

## 14. Release evidence and accountability

Release status is based on reproducible records. Useful evidence includes the exact commit identifier, build environment or pinned dependencies, executed test commands, exit statuses, relevant logs, artifact inventory, and final SHA-256 fingerprints.

The release record distinguishes successful checks from checks not performed. An unresolved test is not represented as a pass. A successful push, local build, or cryptographic unit test does not automatically establish that a downloadable release is consistent.

Automated deployment controls serve as the final enforcement mechanism for the checks that can be automated. Human review remains appropriate for security interpretation, educational clarity, and real-world recovery exercises that cannot be fully reduced to code.

## 15. The long-term quality standard

A mature Plebumbtc.io release exhibits five connected properties:

1. **Understandable:** Visitors can follow the material and distinguish demonstrations from operational security procedures.
2. **Correct:** Important calculations and instructions agree with established standards and independent checks.
3. **Private:** Educational access does not unnecessarily expose visitor data or wallet secrets.
4. **Portable:** Essential resources remain available in a documented, tested offline form.
5. **Verifiable:** Final published artifacts are traceable, internally consistent, and subject to enforceable release checks.

The project's technical goal is not zero change or a promise of perfect security. It is a maintainable system in which important assumptions are explicit, mistakes are detectable, recurring defects become less likely, and improvements can be trusted because they are verified.

---

### Document boundary

This document describes **project architecture, engineering practices, and acceptance criteria**. It is not an executable build script, a CI configuration, a claim of completed verification, or an instruction to override any AI tool's safety controls. Implementation details and deployment enforcement are separate repository artifacts subject to normal review.
