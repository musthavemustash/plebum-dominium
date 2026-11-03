# Project Vision — Plebum Dominium / Plebumbtc.io

**Status:** Living project charter. This document collects previously expressed project goals. It does not authorize new product commitments; consequential product changes require the owner's approval.

## Promise to the reader

A person with limited technical background can **understand, evaluate, prepare, practice, and independently verify** a Bitcoin self-custody setup without surrendering secrets to a website, trusting a status indicator, or being nudged into a complexity level they cannot recover from.

**The goal is educated independence, not maximum complexity.** The guide explains what the reader protects against, what can fail, how recovery works, and when to stop or seek independent verification. It teaches procedures, not ritual.

## The two distinct paths

### One Key + Passphrase

- The guide clearly teaches the relationship between seed words, the optional BIP39 passphrase, wallet reconstruction, and storage separation.
- A missing or misspelled passphrase can produce a different wallet. Recovery instructions are protected from ambiguity; seed words alone are never implied to guarantee access.
- Demonstrations use fictional data, and the cost of the simpler setup is stated explicitly without disparaging readers who choose it.

### Three Keys / 2-of-3

- The guide explains the signing quorum, physical separation, recovery tradeoffs, and the additional operational burden.
- **Two signing keys do not necessarily reconstruct a wallet without the correct descriptor/wallet-map information.** Wallet-map preservation and restoration are taught; distinct threats and recovery prerequisites are made visible.
- Multisig protections are not exaggerated, and the cost of setup errors and long-term inheritance complexity is not hidden.

## Learning and design principles

- Plain language first; progressive disclosure for technical depth. One clear action per step, accompanied by consequences and verification.
- A cohesive, warm-paper reading experience with legible dark demonstration panels; coherent path cues (blue = One Key; green = Three Keys) where already established. Contrast, accessibility, and print legibility are not sacrificed for visual novelty.
- Educational thoroughness is preserved while pages stay concise, scannable, and approachable. Neutral, truthful language is used over fear, sensationalism, or hype.
- Demo tools are clearly illustrative, client-only, with no real secrets, no server-side calculations, and no hidden network dependency.
- Privacy and offline operation are architectural constraints, not marketing claims. A website cannot certify the surrounding computer's isolation.
- Keyboard navigation, screen readers, low-motion preferences, responsive viewports, low-bandwidth situations, print use, and no-JS browsing are respected.
- Incremental, reversible changes with narrow scope and measured before/after outcomes are preferred. Bounded issues are fixed directly rather than triggering full redesigns.

## Security truthfulness

- Accuracy outranks reassuring copy. The project distinguishes what is verified by automated tests, what is independently verified, and what is untested (e.g., physical device workflows, actual air gap, testnet spend/recovery, third-party crypto interoperability).
- Actual user mnemonics, passphrases, xprvs, seeds, descriptors, or other wallet-recovery material are never requested, processed in telemetry, stored, or transmitted. Demonstrations use created and labeled nonsecret sample material.
- `navigator.onLine` is not treated as a connectivity or security proof. Guaranteed erasure, safe clipboard use, and secure browser memory are not claimed.
- Security guidance and critical parameters stay consistent across HTML, PDFs, downloads, and the offline package. Both paths are reviewed when either changes.

## Definition of an excellent release

A beginner can navigate both custody paths and understand the tradeoffs; offline users can open the extracted guide and use linked local resources; the final files match the verified fingerprints; the tests demonstrate that prior bugs cannot reappear unnoticed; and the exact built revision and remaining unverified areas are documented.

## Changes requiring owner sign-off

- Altering recommended custody threat models or recovery instructions.
- New secret-handling behavior, network calls, third-party dependencies, analytics, authentication, or wallet connections.
- Changing crypto algorithms, entropy procedures, or security-relevant defaults.
- Changing the live-site domain/canonical origin, deployment mechanism, branch protection, or what counts as a releasable build.
- Removing user-facing steps/pages, supporting material, or security warnings merely to simplify UX.
