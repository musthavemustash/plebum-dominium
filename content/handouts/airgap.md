04 · Plebum Dominium

# Two boots

One computer, used twice. The first boot watches the wallet and broadcasts finished payments — it never holds a seed. The second boot is the Tails USB: networking off, exactly one seed, then a full shutdown. The seed lives in memory only. Shutdown wipes it.

::fig airgap/two-boots

## What "airgapped" means here

Yes:

- Networking Disabled on the Tails welcome screen, before the desktop.
- Files cross on the data USB — payment files, the map, checked programs.
- The online computer stays watch-only.

Not airgapped:

- Turning networking off after Sparrow opened.
- Unplugging a disk that was online yesterday.
- A photo of a seed. A password manager, printer, or cloud note as backup.

## Prepare the two USBs

::fig airgap/two-usbs

Download Tails only from the official site. Check the signature and checksum before writing. Write it with the official installer, label it TAILS. Do not create Persistent Storage — skip the passphrase. The data USB gets only files that already passed the checks.

## Every offline session

1. Boot the Tails drive. Networking Disabled. Don't unlock Persistent Storage.
2. Copy only the file that session needs from the data USB.
3. Do the work: convert dice, restore one seed, sign one file, or export the map.
4. Copy the result back to the data USB. Shut down fully — dark screen before the drive comes out.

## Stop if

- Two seeds in one session — never.
- Networking turns on while a seed is in memory — that session is burned.
- Tails offers Persistent Storage — don't create it, don't unlock it.

Stronger (optional): a dedicated old laptop with the Wi-Fi card physically pulled. Ethernet never plugged. The Tails file is still checked, networking still Disabled, data USB still clean — the stick remains the only wire.

Next. The three keys are made next. A word is not written until Tails is running with networking turned off.[← Check the files](/handouts/verify)[Make the three keys →](/handouts/dice)
