11 · Plebum Dominium

# Hide the wallet map

The map can watch the money, but it cannot spend. Anyone who can read it can see the balance, so it never sits around as plain text.

## What is required

- The wallet map on the data USB, called map.txt only while you work.
- descriptor_obfuscator.py from the kit. Checked before it's copied.
- A passphrase. Not a seed, not the decoy passphrase, never stamped on a plate.
- Generate the passphrase with real dice: [Diceware passphrase mapper](/diceware.html). Download the page and run it in an offline Tails session, never in an everyday browser.
- Tails, networking Disabled. Not the everyday computer.

## Step 1 · Boot Tails. Copy the tool and the map.

::fig encryption/encrypt-setup

Boot Tails, networking Disabled. Copy the tool and map.txt to the Desktop.

## Step 2 · Run the tool. Choose E. Enter the passphrase.

::fig encryption/encrypt-run

Open the terminal. Run the tool. Choose E. Paste the wallet map. Enter the passphrase. It is not a seed.

```
$ python3 descriptor_obfuscator.py
```

## Step 3 · Copy the locked file. Delete the plain one.

::fig encryption/encrypt-distribute

Copy map.txt.gpg to two USB drives. Delete map.txt from the Desktop and the USB. Empty the trash.

## Step 4 · Write the passphrase on paper. Twice.

::fig encryption/passphrase-paper

Two copies, two separate places. This paper is a single point of failure for every encrypted copy of the map. Treat it like a plate.

## Step 5 · Prove it opens. Check the first address.

::fig encryption/encrypt-verify

On a later offline boot, choose D. The map must open, and the first address must match what you wrote down. If a plain copy was ever made, encrypt it again, then delete the plain one.

If the passphrase is lost, the coins aren't gone, as long as all three plates still exist. Three seeds rebuild the map exactly. Two seeds cannot. Write the path m/48'/0'/0'/2' on the inheritance sheet. It is not a secret.

## Stop if

- You want the xpubs on paper "just in case": that's a leak. Stop.
- You want to invent a homemade cipher: stop. Use the tool.
- The passphrase is a seed or is stamped on a plate: start over with a different one.

Next. If I am gone. That page is for a spouse. It does not contain words.[← Metal and the map](/handouts/titanium)[If I am gone →](/handouts/inheritance)
