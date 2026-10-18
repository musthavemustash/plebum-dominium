07 · Plebum Dominium

# Build the 2-of-3

Three public keys go in. No seed ever touches this build. What comes out is the wallet map — it can watch the money, never spend it.

You will boot Tails four times: once per seed to copy its public key, then once more with no seed to build the vault.

## What is required

- The data USB with the checked Sparrow file (sparrowwallet-2.5.5-x86_64.tar.gz)
- The three paper seeds. Only one comes out per boot.

## Step 1 · Boot Tails. Networking stays off.

::fig networking

The entire sheet happens with networking Disabled. Check it on every boot.

## Step 2 · Open the terminal. Launch Sparrow.

::fig terminal

Type these four lines, one at a time. Wait for the prompt to come back after each.

```
$ cd ~/Desktop
$ tar -xvf sparrowwallet-2.5.5-x86_64.tar.gz
$ cd Sparrow
$ ./bin/Sparrow
```

Wait 15–30 seconds. Sparrow opens. Type exactly — spaces count. If a line turns red, stop.

## Step 3 · New wallet: 2 of 3, native Segwit.

::fig wallet-settings

File → New Wallet. Pick Multi Signature, Native Segwit, 2 of 3. The path must read m/48'/0'/0'/2'. Anything else — stop.

## Step 4 · Keystore 1: Seed 1 in, public key out.

::fig seed-to-xpub

Keystore 1 → New or Imported Software Wallet → type Seed 1's 24 words. Export the xpub. Save it to the data USB as s1-xpub.txt. Close Sparrow. Shut down. Wait for a dark screen.

## Step 5 · Twice more. One seed per boot.

::fig three-boots

Boot again for Seed 2 → s2-xpub.txt. Shut down. Boot again for Seed 3 → s3-xpub.txt. Shut down.

## Step 6 · Fresh boot. No seed. Build the vault.

::fig build-vault

Boot Tails again — do not type any seed. New wallet → Multi Signature → Native Segwit → 2 of 3 → import the three xpub files. Confirm the path. Export the output descriptor to the data USB. That file is the wallet map.

## Step 7 · Watch-only on the everyday computer.

::fig watch-only

On the everyday computer, open Sparrow and import the map as a watch-only wallet. It can see the money. It can never spend it.

## Stop if

- The path doesn't read m/48'/0'/0'/2' — stop, don't type a different path.
- Networking is on at any point — stop.
- You're tempted to type a second seed without shutting down — stop. One seed per boot.

Next. Practice spend. A small payment goes out and comes back before the plates are stamped.[← Make the keys](/handouts/dice)[Practice spend →](/handouts/signing)
