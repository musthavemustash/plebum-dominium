07 · Plebum Dominium

# Build the 2-of-3

> [!WARNING]
> Never enter seed words on an online computer.

Three public keys go into Sparrow, and no seed ever touches this build. What comes out is the wallet map, which can watch the money and never spend it.

You will boot Tails four times: once per seed to copy its public key, then once more with no seed to build the vault.

Files used: Sparrow 2.5.5. Tails 7.15.1 or later 7.x (verified). Electrum 4.8.3 for the cross-check.

## What is required

- The data USB with the checked Sparrow file (sparrowwallet-2.5.5-x86_64.tar.gz)
- The three paper seeds. Only one comes out per boot.

## Step 1 · Boot Tails. Networking stays off.

::fig sparrow/networking

The entire sheet happens with networking Disabled. Check it on every boot.

## Step 2 · Open the terminal. Launch Sparrow.

::fig sparrow/terminal

Type these four lines, one at a time. Wait for the prompt to come back after each.

```
$ cd ~/Desktop
$ tar -xvf sparrowwallet-2.5.5-x86_64.tar.gz
$ cd Sparrow
$ ./bin/Sparrow
```

Wait 15 to 30 seconds. Sparrow opens. Type exactly. Spaces count. If a line turns red, stop.

## Step 3 · New wallet: 2 of 3, native Segwit.

::shot sparrow/wallet-settings

File → New Wallet. Pick Multi Signature, Native Segwit, 2 of 3. The path must read m/48'/0'/0'/2'. Anything else: stop.

## Step 4 · Keystore 1: Seed 1 in, public key out.

::fig sparrow/seed-to-xpub

Keystore 1 → New or Imported Software Wallet → type Seed 1's 24 words. Export the xpub. Save it to the data USB as s1-xpub.txt. Close Sparrow. Shut down. Wait for a dark screen.

## Step 5 · Twice more. One seed per boot.

::fig sparrow/three-boots

Boot again for Seed 2 → s2-xpub.txt. Shut down. Boot again for Seed 3 → s3-xpub.txt. Shut down.

## Step 6 · Fresh boot. No seed. Build the vault.

::shot sparrow/build-vault

Boot Tails again. Do not type any seed. New wallet → Multi Signature → Native Segwit → 2 of 3 → import the three xpub files. Confirm the path. Export the output descriptor to the data USB. That file is the wallet map.

> [!STOP] **Confirm the first address on a second screen.**
>
> Sparrow built your wallet from your seeds. But if malware sat on the build machine, it could show you **an address it controls** while you trust it. A second screen the malware can't reach closes that hole. **Do not fund the wallet until this matches.**
>
> **1 · Build in Sparrow.** Finish the 2-of-3 build on the airgapped machine as usual. Write down the **first receiving address** it shows. Write the full string, not the QR code.
>
> **2 · Cross-check in Electrum.** Rebuild the same 2-of-3 in Electrum offline from the same seeds and compare the first address. This catches entry mistakes.
>
> **3 · NEW: Display it on a second device.** Load the wallet as **watch-only** (xpubs / wallet descriptor only, never seeds) on your phone or a second computer. Compare the first receiving address **character for character**. If all three agree, the coordinator didn't lie. If anything differs, stop and rebuild.

## Step 7 · Watch-only on the everyday computer.

::fig sparrow/watch-only

On the everyday computer, open Sparrow and import the map as a watch-only wallet. It can see the money. It can never spend it.

## Stop if

- The path doesn't read m/48'/0'/0'/2': stop. Don't type a different path.
- Networking is on at any point: stop.
- You're tempted to type a second seed without shutting down: stop. One seed per boot.

Next, Practice spend.[← Make the keys](/handouts/dice)[Practice spend →](/handouts/signing)
