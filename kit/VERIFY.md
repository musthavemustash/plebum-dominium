# How to verify `bip39_dice_converter.py`

Do not trust this file because it was emailed or downloaded. Check the hash, then read the logic, then test with dummy bits. Only then use it offline with real dice entropy.

## File identity

```
File:     bip39_dice_converter.py
Size:     37905 bytes
SHA-256:  a0442625d3f9a1268ef94556b94eb8e3e056378ea0b2accafcc865ddf5a12ea3
```

## Wallet map tool

```
File:     descriptor_obfuscator.py
Size:     5520 bytes
SHA-256:  0d7f5044657d30954f9232ab297436ab9892776906cbe3f614db938c35350eb9
```

Linux / macOS / Tails:

```bash
sha256sum descriptor_obfuscator.py
```

The hash must match exactly:

```
0d7f5044657d30954f9232ab297436ab9892776906cbe3f614db938c35350eb9
```

If it does not match, stop. Do not run that copy. The tool calls GPG with AES-256. It does not contain a cipher of its own.

## 1. Confirm you have the same bytes

Linux / macOS / Tails:

```bash
sha256sum bip39_dice_converter.py
```

Windows PowerShell:

```powershell
Get-FileHash .\bip39_dice_converter.py -Algorithm SHA256
```

The hash must match exactly:

```
a0442625d3f9a1268ef94556b94eb8e3e056378ea0b2accafcc865ddf5a12ea3
```

If it does not match, stop. Do not run that copy.

## 2. Read the only code that matters

The long middle of the file is the official BIP39 English wordlist (2048 words).  
The conversion logic is at the bottom:

- `clean_binary()`
- `binary_to_bytes()`
- `generate_mnemonic()`

Confirm these behaviors:

- Input is only `0` and `1`
- Fewer than 256 bits is rejected
- More than 256 bits is reduced with `SHA-256`
- Checksum is the first 8 bits of `SHA-256(entropy)`
- The 264 bits are split into 24 groups of 11 bits
- `len(WORDLIST) == 2048`
- Word 0 is `abandon`, word 2047 is `zoo`

Official wordlist for comparison:

https://github.com/bitcoin/bips/blob/master/bip-0039/english.txt

## 3. Known test (no real seed)

Run:

```bash
python3 bip39_dice_converter.py
```

Paste 256 zeros and press Enter:

```
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
```

A correct 24-word BIP39 result for all-zero entropy ends with **art**.

Cross-check the same 256 bits in an **offline** copy of Ian Coleman BIP39:

- Entropy type: Binary `[0-1]`
- Mnemonic length: 24 words (or raw 256-bit entropy)

The words must match.

## 4. Check the other downloads

`verify_downloads.py` is a separate file. It does not change this converter.

```
File:     verify_downloads.py
Size:     356 bytes
SHA-256:  8b819c8325cfb61e680de50cd04d37c04ad3c3d2bc3e46425ee732c54971cd45
```

```bash
sha256sum verify_downloads.py
python3 verify_downloads.py
```

It checks Tails, Sparrow, Electrum, and the Ian Coleman page in the current directory. A mismatch means delete that file.

## 5. Extra bits note

If you paste **more than 256 bits**, this script hashes the bit-string-as-bytes with SHA-256 and uses that 256-bit digest.

Ian Coleman’s “24 Words” mode may hash extra entropy differently. For an apples-to-apples match with Ian Coleman, use **exactly 256 bits**.

## 6. Real use

- Hash the file first
- Run it only on an offline machine (Tails recommended)
- Never type a real seed or real dice bits into an online computer
- Write the 24 words on paper or metal
- Destroy scratch notes of the raw bits

<!-- BEGIN GENERATED: PDF FINGERPRINTS (scripts/stamp-pdfs.py) -->

## Handout PDF fingerprints

Every downloadable handout is stamped in its footer with its version,
build date, and a Content SHA-256 — the hash of the handout's content
before the footer was stamped on. Match the number printed on a paper
copy to the Content SHA-256 below to confirm the copy is the handout as
published. The File SHA-256 is the hash of the PDF file itself, exactly
as served:

| File | Version | File SHA-256 | Content SHA-256 |
| --- | --- | --- | --- |
| 00_Project_Overview.pdf | 2026.10.20 | `a4d7c2d98bc4e46c2415efb62211cab7f7562ea16b5e5da4e0d1b6218b092799` | `fafc377ca7ba7910de0100d4f5ebe83081384030fb80b9bdcbacc05eb84dc816` |
| 02_Print_Packet.pdf | 2026.10.20 | `f4b69de7dc87d6fc9d053c86204da5677d76444f2e29437699ad5d4c1d8a5176` | `626b97ec79b9966c3017866938c184d8d9cf34a3f6727526183b59e076932032` |
| 03_Checklist.pdf | 2026.10.20 | `5a499c257b62c3e195abf290a4277645f57146333ceea33ae9a3df52d2ac608d` | `57505199ffc21b9cfc7fcb84b96d59c9cd8f20e769ae766befc09211f5724208` |
| 04_Airgap.pdf | 2026.10.20 | `2dd0d1bac9a4617d794a9bcc95ac2ba84786a5d614a7bdc5261cc6dd9b90b5ed` | `ce37fdbcd7cb4fc4f8a00adb63f7092d1f7bfc457bf15e8c3f1071d593b87bb9` |
| 05_Verify.pdf | 2026.10.20 | `e9defd12534b1567b2b08c5c9d5f5fa6ab6a06ea0dde5f1b254755b51478bc5b` | `1858702a9b5739d997097d329581aa236a1b71f88604b905d0b938bed2e0c92e` |
| 06_Dice.pdf | 2026.10.20 | `4b1c67b10a9c969388af72461ab5a0484a4b6529213b3b325b50b6d39334a60a` | `6a4299295c0354c111d8285e7ca9b4b8a1cf4519760611be571f511cfa49bd8b` |
| 07_Sparrow.pdf | 2026.10.20 | `e3a62ba5a726bc1dfbcd0ebbda83bf902b322bf729b029802f9e87b1068c44c6` | `7548d84e93c663627376f095080a0b4beb4bcce823b4d78056d09ff775597544` |
| 08_Signing.pdf | 2026.10.20 | `986ebfe5b56d0a192f03a13c254e876c930c15da920337e92bd647667a494a51` | `bfd25cfd2e21e48debae0ac142c41431667a4be87db7b0782f5a5855b0a4bbc2` |
| 09_Titanium.pdf | 2026.10.20 | `637bf789d0cbc07569336bb1ec9d1b4c4bdd2ed32900b30376d67054c085fefd` | `11c0b436583c628fafedd5ec08a74984b79f780db314a893db7a190216e7a7c5` |
| 11_Encryption.pdf | 2026.10.20 | `ffa7780b01f96efd17917bf28645681747dd241d9a61d3931afd01ae3b8cc3e7` | `1a7460ea3a4f462a8c485967ea780f20722f825c169ab880319fb9f913e67e86` |
| 12_Inheritance.pdf | 2026.10.20 | `7b98ba4047024747decd4c0e6558cedd756ddc28af6dfb443f2b7210b452fdc6` | `1beacf153829b0d75832137c1144e1b3938de476e729cea011f757e6a33abec0` |
| 13_FAQ.pdf | 2026.10.20 | `96d7d67f78339cb5fe744524487093aafa6a1e51db118bb8106fe18d88211e94` | `f8dd3c6d3e5daf8c9a37ea4bcd2cc3aa1a8d5383e8eb038c33ae711b85ef7c79` |
| 14_Speaker.pdf | 2026.10.20 | `946306081d61081958de2fd98873f6069918615ae306934b8e301eb6389aa605` | `b6e79f937ff6f6625fa41335612f294e298d22b4e08fe0ca175cf8fed2f4edc8` |
| 15_Fire_Card.pdf | 2026.10.20 | `bd0aa763e6e591fb68cb9d6ac1ead28ea73f72bd7fa92d10ce78eee26c990a06` | `2cc7a8bdb3a9c1c87d5f1beddf75218deec9726b1b3f74dad3ee6e665d6e12bc` |
| Handouts_No_Cover.pdf | 2026.10.20 | `900ca5193e946964b0f142eb28fd80faf44c3ec76516bc2d6788b15d78aff93d` | `fa2ef82fa441d6236af69eb7680f50492461eb473ddc110d0f9220d46db5e80d` |
| Presentation_Handouts.pdf | 2026.10.20 | `ae85734aaa22b7b337060f6aa6fb30506e5f90f1c364581b2cc0a4a1230338fc` | `65183c56fd85b2e15e20cdb655c037dfbefdca1727cdead8277f4992184f7bcd` |
| Terms.pdf | 2026.10.20 | `6657b7603146193183efc12c80d5f0aeea2535d1b442bb151652c6fa8a20fa57` | `21a286921c3caa6ed0f56b29793b6ac50408b8b5891f40182ae866d3e4f5ad4c` |

<!-- END GENERATED: PDF FINGERPRINTS -->

<!-- BEGIN GENERATED: PAGE FINGERPRINTS (scripts/build.py) -->

## Sheet page fingerprints

Each sheet page on plebumbtc.io is rendered from a fixed source. The
fingerprint below is the SHA-256 of that sheet's rendered content — the
overview card and the article body, without the site header and footer.
If a copy of a sheet does not hash to the value printed here, it is not
the sheet as published.

| Sheet | Page | SHA-256 |
| --- | --- | --- |
| T · Terms | handouts/terms.html | `c684927c453e47bdaef12ebbf9174f39979c0e4e0b117d34fb831076efd0767f` |
| 02 · Before you begin | handouts/threat-model.html | `7987ee0282f845c17153992cf8b628c95c32b1b74c7749e786be62b3083500a2` |
| 03 · Checklist | handouts/checklist.html | `bf46b1373f871dc7f668163437be894da6c1ab85078b934206ac964af17095c0` |
| 05 · Check the files | handouts/verify.html | `c7e8cbc6a9c8f8586085dcc92210e61948aecdd6db6dcdc64c758fb1a6229a0e` |
| 04 · Two boots | handouts/airgap.html | `9adb4baac558d5bc63f6f22916ef3fe6ae8f8c9632e7368d39fe0cbb16476dfc` |
| 06 · Make the three keys | handouts/dice.html | `3cb72488d6c5742d419b5aeb866f9030fa94896cf9361bdcaf4d2fa56c543c2f` |
| 07 · Build the 2-of-3 | handouts/sparrow.html | `9b7e60f912013133a06088cf1c168cb27bf2d5ba476cf5a13653edb522276678` |
| 10 · Rehearse on testnet | handouts/testnet.html | `b247ac6003c18ced41ea695c3e4bd1fed42a868d2e8d3847518403e16edfd877` |
| 08 · Practice spend | handouts/signing.html | `c7eab6aacccb3fc4f2ab1ccc55b615076c176ac3581b22cb8f61836fa11e6af5` |
| 09 · Metal and the map | handouts/titanium.html | `ec1bf8c57d4aeecb941f9be61167338c331b9db7df6a7b898e4bbd20c0392152` |
| 11 · Hide the wallet map | handouts/encryption.html | `598c2e35c8894c7b23d82469cb1c164fc11f2aad55a468b049b9ce2a15609bf3` |
| 12 · If I am gone | handouts/inheritance.html | `f1b8b72910cb10355583aa845f4d4c1daed7bc6f159058b26658b525f8ec6091` |
| 13 · If you get stuck | handouts/faq.html | `9bf8364e9b5bcb3bfc198092d99b94dda5e8722f4aea676e3566a33400ae2107` |
| 14 · Tough questions | handouts/briefing.html | `f9fd3a48c8ffad1d6a9a7fa01c27db544b058b09f11a20fb8dd5720b9e0bc555` |
| 15 · Recovery card | handouts/fire-card.html | `b3c34105fdd9dfcbee5b0a42a986119ecffdd2c7ccaa0ed827c5bbe82b39be38` |

<!-- END GENERATED: PAGE FINGERPRINTS -->
