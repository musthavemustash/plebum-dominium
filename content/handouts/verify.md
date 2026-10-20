05 · Plebum Dominium

# Check the files

Every file gets checked before the computer goes offline. A file that fails is deleted. No exceptions — a compromised file compromises the funds.

> [!WARNING] **Is this the real site?** These instructions only protect you on **plebumbtc.io**. Before you trust them: check the address bar — the domain must read exactly `plebumbtc.io`, no extra words, no lookalikes. Click the lock icon and confirm the certificate belongs to plebumbtc.io. Anyone can copy these pages; only the real domain gets the real updates. If anything looks wrong, stop — verify through a second channel before continuing.

## What is required

- The downloads from the checklist: Tails 7.13, Sparrow 2.5.5, Electrum 4.8.2, the Ian Coleman page, and the dice converter from this kit.

## Step 1 · Download only from the real sites.

::fig verify/download-sources

Sparrow must be 2.5.5 exactly. A newer download will not match — that is a stop, not an upgrade. The dice converter is the one file this site provides; its fingerprint is in VERIFY.md.

## Step 2 · Compare the fingerprint. Every character.

::fig verify/compare-hash

Windows: PowerShell → Get-FileHash. Mac: Terminal → shasum -a 256. Paste the result next to the fingerprint published on the project's own site.

## Step 3 · Check the signature. Want: "Good signature".

::fig verify/check-signature

Import the signing key, confirm its fingerprint, then verify. The "not certified" warning is normal on first import. What matters: the line says Good signature and the fingerprint matches.

Sparrow signing key fingerprint: D4D0D3202FC06849A257B38DE94618334C674B40. Electrum (ThomasV): 6694D8DE7BE8EE5631BED9502BD5824B7F9470E6.

## Step 4 · Run the kit check.

::fig verify/kit-check

Put the downloads next to verify_kit.sh and run it. It checks the pinned fingerprints. One failure — the work stops.

## Later · Two tools must agree. Every time.

::fig verify/two-tools-agree

Same dice bits → same 24 words in both tools. Same seed → same first addresses in Sparrow and Electrum. The wallet map shows those same addresses. Before signing, both tools show the same destination, amount, change, and fee. If they differ — stop.

## Stop if

- A fingerprint differs by one character — delete the file.
- The signature isn't Good — delete the file.
- The two tools disagree — stop.

Next. Two boots. Flash Tails only after this page is done.[← Checklist](/handouts/checklist)[Two boots →](/handouts/airgap)
