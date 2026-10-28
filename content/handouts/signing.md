08 · Plebum Dominium

# Practice spend

> [!WARNING]
> Never enter seed words on an online computer.

The practice spend uses a small amount, enough to pay a fee and no more. Write the destination, amount, and fee on paper before anything is exported, and read those notes again before each signature.

Files used: Sparrow 2.5.5. Tails 7.15.1 or later 7.x (verified).

## Step 1 · Build the spend (online, watch-only).

::fig signing/build-spend

Open watch-only Sparrow. Send tab: destination, amount, fee. Finalize for signing. Export tx-unsigned.psbt to the data USB.

## Step 2 · Seed 1 signs (Tails, networking off).

::fig signing/seed1-signs

Boot Tails, networking disabled. Restore Seed 1 only. Open tx-unsigned.psbt, confirm the fields against the paper, sign. Export tx-partial-s1.psbt. Full shutdown.

## Step 3 · Seed 2 signs (fresh boot).

::fig signing/seed2-signs

Fresh Tails boot. Restore Seed 2 only. Open tx-partial-s1.psbt. Confirm the first signature and that the spend is unchanged. Sign. Export tx-signed.psbt. Full shutdown.

## Step 4 · Broadcast (online computer).

::fig signing/broadcast

Watch-only Sparrow: open the fully signed file, confirm the fields are unchanged, broadcast. Record the txid in the recovery workbook.

Keys on hardware later? Generate the seed on airgapped Tails first, then import the finished 24 words. Never let the device roll its own entropy for this stack. Two keys on two brands (Foundation Passport, Blockstream Jade, BitBox02, SeedSigner/Krux; official shops only). Never three of the same box.

## Stop if

- The fields don't match the paper note: stop.
- Sparrow and Electrum disagree about the file: do not sign.
- Test with a small amount first. Always.

Next, Metal and the map.[← Build the 2-of-3](/handouts/sparrow)[Metal and the map →](/handouts/titanium)
