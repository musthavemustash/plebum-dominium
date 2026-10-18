05 · Plebum Dominium

# Check the files

The files have to be verified before the computer is taken offline. A file that fails this check is deleted. These files must be downloaded from their original sources. Tails, Sparrow 2.5.5, Electrum, and the Ian Coleman page are not supplied by this site. The dice converter is the one file this site provides. A compromised file compromises the funds.

## The files this kit checks

- Tails 7.13. The file is tails-amd64-7.13.img or tails-amd64-7.13.iso. From tails.net only. Wait until that page says the check passed.
- Sparrow 2.5.5. For Tails, sparrowwallet-2.5.5-x86_64.tar.gz. A newer download will not match. That is a stop, not an upgrade. The Windows or Mac installer is only for the computer that watches.
- Electrum 4.8.2. The file is electrum-4.8.2-x86_64.AppImage. From electrum.org. Not a look-alike page.
- Ian Coleman. Save bip39-standalone.html from the official GitHub repo. Open it only while offline.
- The dice converter is already in this kit. Its fingerprint is in VERIFY.md.
[Verify package integrity](/verify-software)

## Exact download locations

- **Sparrow:** `https://github.com/sparrowwallet/sparrow/releases/download/2.5.5/sparrowwallet-2.5.5-x86_64.tar.gz`, plus `sparrow-2.5.5-manifest.txt` and `sparrow-2.5.5-manifest.txt.asc` from the same release page. Import the signing key with `curl https://keybase.io/craigraw/pgp_keys.asc | gpg --import` and confirm the fingerprint `D4D0D3202FC06849A257B38DE94618334C674B40`.
- **Electrum:** `https://download.electrum.org/4.8.2/Electrum-4.8.2.tar.gz` plus the `.asc` signature file. Import the signing key from `https://raw.githubusercontent.com/spesmilo/electrum/master/pubkeys/ThomasV.asc` and confirm the fingerprint `6694D8DE7BE8EE5631BED9502BD5824B7F9470E6`.
- **Ian Coleman:** do not use the browser's save-as on the live page — that yields a different file. Download `bip39-standalone.html` from `https://github.com/iancoleman/bip39/releases/latest` and compare its SHA-256 against the PGP-signed hash printed on that release page.

Expect this warning from `gpg --verify` on a first import: "WARNING: This key is not certified with a trusted signature!" That is normal. What matters is the line above it: `Good signature`, and the fingerprint matching the one published above.

## Compare the fingerprint

One window is opened, one line is pasted, and the result is compared to the fingerprint on the project’s own site. Every character. One difference means the file is deleted.

Windows. Start menu, PowerShell.

```
$ cd $ Get-FileHash .\filename -Algorithm SHA256
```

cd is typed, then a space, then the folder is dragged in. Enter is pressed. The second line is pasted with the real file name.

Mac. Spotlight, Terminal.

```
$ cd $ shasum -a 256 filename
```

## Then the kit check

The downloads are placed next to verify_kit.sh. It checks the pinned fingerprints. It does not check signatures. One failure means the work stops. That file is not copied.

```
$ chmod +x verify_kit.sh$ ./verify_kit.sh
```

## Later, two tools must agree

- The same dice bits have to print the same 24 words in the converter and on the offline Ian Coleman page.
- The same seed has to show the same first addresses in Sparrow and Electrum. If they differ, the work stops.
- The wallet map, imported with no seed, has to show those same addresses.
- Before a payment is signed, both tools have to show the same destination, amount, change, and fee.

Next. Two boots. Flash Tails only after this page is done.[← Checklist](/handouts/checklist)[Two boots →](/handouts/airgap)
