14 · Plebum Dominium

# Tough questions

These are the questions people use to poke a hole in the method. The answer is only what is true. A step that is not on the sheets is not added.

## You typed the seed words on a laptop. Isn't that exposed?

Yes — typed, on Tails, with networking off, one seed per boot, then a full shutdown. Tails runs from memory and forgets the session. That does not stop a hardware keylogger. But one captured seed still cannot spend: the fund needs two keys. Never type two seeds on the same boot.

## Why not just start with a SeedSigner or a hardware wallet?

A signer can be added later. It is not how these keys are made. The randomness is dice. The computer is ordinary and offline. The inheritance sheet is not a signer guide — it is the letter for heirs: one plate in a Jade, one plate in a BitBox.

## Is dice randomness weaker than a hardware wallet's RNG?

No. 256 bits is 256 bits, whatever made them. Casino dice are a randomness source you can watch with your own eyes — no chip to trust, no firmware to audit.

## If the map passphrase is lost, are the coins gone?

Not if all three plates still exist — three seeds rebuild the map exactly. But two seeds cannot: the third key cannot be derived from the other two. So a lost passphrase plus only two plates means the addresses are unrecoverable. Back up the passphrase paper in two separate places, away from the plates and the USB drives. The path is 2-of-3, native SegWit, m/48'/0'/0'/2'. Write that path on the inheritance sheet. It is not a secret.

## What if someone finds one plate?

They cannot spend. One key alone opens nothing — that is the point of 2-of-3. But do not keep two plates in the same drawer: two plates in one place is the whole lock in one place.

## Shouldn't I add a passphrase to the multisig for extra security?

No. The security here comes from distribution, not from one more secret. A passphrase on the 2-of-3 is a single point of failure wearing a disguise: lose it and two plates are not enough. The home plate can carry a small decoy single-sig with its own optional passphrase — that is a separate choice, on the metal sheet.

That is the whole method. Everything else is commentary.[← If you get stuck](/handouts/faq)
