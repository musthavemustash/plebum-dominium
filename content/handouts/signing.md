08 · Plebum Dominium

# Practice spend

A small amount is used, enough to pay a fee, and not savings. The destination, the amount, and the fee are written on paper before the file is exported. Those notes are read again before each signature. The first seed signs on Tails. The computer is shut down fully. The second seed signs on a new boot. Then the payment is broadcast.

## Step 1 — Build the spend (online watch-only)

1. 01 · Watch-only Sparrow is opened. The receive history is checked again so the wallet is the right one.
2. 02 · Send tab: destination, amount, fee. Read every field against a written note.
3. 03 · Finalize for signing. Export tx-unsigned.psbt to the data USB.

## Step 2 — First signature (Tails session 1, or hardware A)

1. 01 · Boot Tails, networking disabled. Do not unlock Persistent Storage. Launch verified Sparrow. Or unlock hardware wallet A that already holds Seed 1.
2. 02 · Restore Seed 1 only (Tails) — or confirm Seed 1 is the only key on that device. Open tx-unsigned.psbt. Confirm fields. Sign.
3. 03 · Export tx-partial-s1.psbt. Full shutdown of Tails, or unplug the hardware signer.

## Step 3 — Second signature (Tails session 2, or hardware B)

1. 01 · Fresh Tails boot, networking disabled. Do not unlock Persistent Storage. Restore Seed 2 only. Or unlock hardware wallet B from a different vendor.
2. 02 · Open tx-partial-s1.psbt. Confirm the first signature and unchanged spend. Sign.
3. 03 · Export tx-signed.psbt. Full shutdown.

## Step 4 — Broadcast (online computer)

1. 01 · Watch-only Sparrow: File → Open Transaction → fully signed file.
2. 02 · Confirm fully signed and fields unchanged. Broadcast. Record the txid in the recovery workbook — not in this site.

## If a key is later put on hardware

- Generate the seed on airgapped Tails first. Import the finished 24 words. Do not let the device roll its own entropy for this stack.
- Multi-vendor examples (not a ranking): Foundation Passport, Blockstream Jade, BitBox02, SeedSigner / Krux. Official shops only.
- Two keys on two brands. Never three of the same box. A bricked vendor is one lost key — plates and geography still hold the wallet.
- If Sparrow and Electrum disagree about the PSBT, stop. Do not sign. Test with a small amount first.

Next. The plates are stamped next. A plate is not stamped until a small payment has gone out and come back.[← Build the 2-of-3](/handouts/sparrow)[Metal and the map →](/handouts/titanium)
