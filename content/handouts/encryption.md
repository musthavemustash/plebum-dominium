11 · Plebum Dominium

# Hide the wallet map

The wallet map exists before this work, and it is not left in a drawer as plain text. The map can watch the money. It cannot spend. Anyone who can read it can see the balance, so it is encrypted. The passphrase that opens the file is not a seed, and it is not a plate.

## What is required

- The wallet map from the 2-of-3, on the data USB. It is called map.txt only while the work is happening.
- [descriptor_obfuscator.py](/kit/descriptor_obfuscator.py). This is the tool. It calls GPG. It does not invent a cipher. It is checked before it is copied onto the drive.
- A passphrase that can be remembered and also written down. It is not one of the 24-word lists. It is not the decoy passphrase. It is not stamped on a plate.
- Tails, with networking set to Disabled. This is not done on the everyday computer.

## The steps

1. 01 · Tails is booted. Networking is set to Disabled. The tool and map.txt are copied to the Desktop. The map is not opened on a phone.
2. 02 · Terminal is opened. The tool is run. E is chosen. The wallet map is pasted. The passphrase is entered. That passphrase is not a seed.
3. 03 · The tool writes map.txt.gpg. That file is copied to two USB drives. map.txt is deleted from the Desktop and from the USB. The trash is emptied.
4. 04 · The passphrase is written on paper. That paper is kept away from the plates and away from the USB drives.
5. 05 · On a later offline boot, D is chosen. The map has to open, and the first address has to match what was written down. If a plain copy was made, it is encrypted again. The plain copy is deleted.

```
$ cd ~/Desktop$ python3 descriptor_obfuscator.py
```

## Stop if

- The xpubs are not written on paper “just in case.”
- A letter code or a homemade cipher is not invented. The tool above is the one that is used.
- The passphrase is not one of the seeds, and it is not stamped on a plate. A different passphrase is chosen, and the work is started over.

If this passphrase is lost, the coins are not gone — as long as all three plates still exist. Three seeds rebuild the map exactly. Two seeds cannot: the third key's xpub cannot be derived from the other two. Treat this passphrase paper with the same care as a plate. It is a single point of failure for every encrypted copy of the map — back it up in two separate places, away from the plates and the USB drives. The path is m/48'/0'/0'/2'. Write that path on the inheritance sheet. It is not a secret.

Next. If I am gone. That page is for a spouse. It does not contain words.[← Metal and the map](/handouts/titanium)[If I am gone →](/handouts/inheritance)
