# How to verify `bip39_dice_converter.py`

Do not trust this file because it was emailed or downloaded. Check the hash, then read the logic, then test with dummy bits. Only then use it offline with real dice entropy.

## File identity

```
File:     bip39_dice_converter.py
Size:     37896 bytes
SHA-256:  7a14a2044eb90c45114336329e91fcdd9d98362fabdbdeadbc190b4478800330
```

## Wallet map tool

```
File:     descriptor_obfuscator.py
Size:     5519 bytes
SHA-256:  5667d356e1e3d62c6fc222cbec40191fbd4b45e84290a77b0d54b138ddea113c
```

Linux / macOS / Tails:

```bash
sha256sum descriptor_obfuscator.py
```

The hash must match exactly:

```
5667d356e1e3d62c6fc222cbec40191fbd4b45e84290a77b0d54b138ddea113c
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
7a14a2044eb90c45114336329e91fcdd9d98362fabdbdeadbc190b4478800330
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
| 00_Project_Overview.pdf | 2026.10.21 | `5bc3ce429e0c9c0d1a37b2fea14716a6b7d118658153a626fc9f406828a803b3` | `fafc377ca7ba7910de0100d4f5ebe83081384030fb80b9bdcbacc05eb84dc816` |
| 02_Print_Packet.pdf | 2026.10.21 | `67973213b8ccb86183bc38b07f1df26d10f11d55f911c52e0c0ee99e9848e43d` | `626b97ec79b9966c3017866938c184d8d9cf34a3f6727526183b59e076932032` |
| 03_Checklist.pdf | 2026.10.21 | `1a0b5c67c2e5079e608b95a003a7c27940bca88000f9d742231f773ae8201a40` | `57505199ffc21b9cfc7fcb84b96d59c9cd8f20e769ae766befc09211f5724208` |
| 04_Airgap.pdf | 2026.10.21 | `26f9a2208a34fc3ffb06064d622eb27bf102b6b7b286ec4d27927c2c3c330f5d` | `ce37fdbcd7cb4fc4f8a00adb63f7092d1f7bfc457bf15e8c3f1071d593b87bb9` |
| 05_Verify.pdf | 2026.10.21 | `f4c5e987039656b9e7a375d6c10d8dc298422f72cedda70c6ee5145c7921873c` | `1858702a9b5739d997097d329581aa236a1b71f88604b905d0b938bed2e0c92e` |
| 06_Dice.pdf | 2026.10.21 | `7447cd801b28a75a44d4fa16247b765c06200e39c6608767679a28387394044e` | `6a4299295c0354c111d8285e7ca9b4b8a1cf4519760611be571f511cfa49bd8b` |
| 07_Sparrow.pdf | 2026.10.21 | `e9911d757829cf2f6616946efe202ca164fe2b1dba1fc412a5d237c0d3239702` | `7548d84e93c663627376f095080a0b4beb4bcce823b4d78056d09ff775597544` |
| 08_Signing.pdf | 2026.10.21 | `ab25d32165bbaa43b74330f134a33a580344b1b7a156cd7a86fd8167ab2f46f9` | `bfd25cfd2e21e48debae0ac142c41431667a4be87db7b0782f5a5855b0a4bbc2` |
| 09_Titanium.pdf | 2026.10.21 | `9f7c52f41fc21746a2f29e2c3d622e0518fc44d49ba648becd12792e884f688f` | `11c0b436583c628fafedd5ec08a74984b79f780db314a893db7a190216e7a7c5` |
| 11_Encryption.pdf | 2026.10.21 | `56267d225b289f06efcbff7584352b8ed2b2b210bc8c64026959e4c75d46a631` | `1a7460ea3a4f462a8c485967ea780f20722f825c169ab880319fb9f913e67e86` |
| 12_Inheritance.pdf | 2026.10.21 | `c2d01ab90188fd39fff64e5f53119ff045d8716ccd0a0efa5108915b846abf91` | `1beacf153829b0d75832137c1144e1b3938de476e729cea011f757e6a33abec0` |
| 13_FAQ.pdf | 2026.10.21 | `2f5d2cde0dd5f20d1f8a801635bf75d44a94a433ee6d82b8f491b82b915e5540` | `f8dd3c6d3e5daf8c9a37ea4bcd2cc3aa1a8d5383e8eb038c33ae711b85ef7c79` |
| 14_Speaker.pdf | 2026.10.21 | `88729d6627d31f2949c164dc52b4b93b71f66f357f2f2019c5afe8fc16e2df3f` | `b6e79f937ff6f6625fa41335612f294e298d22b4e08fe0ca175cf8fed2f4edc8` |
| 15_Fire_Card.pdf | 2026.10.21 | `a61a86722dbb28250be4bba33f61bbc0ee773ff1656bdff46d580e73b3b0b97e` | `2cc7a8bdb3a9c1c87d5f1beddf75218deec9726b1b3f74dad3ee6e665d6e12bc` |
| Handouts_No_Cover.pdf | 2026.10.21 | `1e180c308fb607e83c24616c60c2531904949d18077685fd037df6d31293abae` | `fa2ef82fa441d6236af69eb7680f50492461eb473ddc110d0f9220d46db5e80d` |
| Presentation_Handouts.pdf | 2026.10.21 | `88107caaf87744f8915be38e9421075a51fc9e1533ed1537905721b6a4381659` | `65183c56fd85b2e15e20cdb655c037dfbefdca1727cdead8277f4992184f7bcd` |
| Terms.pdf | 2026.10.21 | `e086c21d89d8cad99eaddc532fea402bf93f0bc2d0f8308fb6e466b052b15cbb` | `21a286921c3caa6ed0f56b29793b6ac50408b8b5891f40182ae866d3e4f5ad4c` |

<!-- END GENERATED: PDF FINGERPRINTS -->

<!-- BEGIN GENERATED: PAGE FINGERPRINTS (scripts/build.py) -->

## Sheet page fingerprints

Each sheet page on plebumbtc.io is rendered from a fixed source. The
fingerprint below is the SHA-256 of that sheet's rendered content: the
overview card and the article body, without the site header and footer.
If a copy of a sheet does not hash to the value printed here, it is not
the sheet as published.

| Sheet | Page | SHA-256 |
| --- | --- | --- |
| T · Terms | handouts/terms.html | `b8cd3f0e715d906b4892449fc20f39a1893cccddf010bb1875faf3a95ca163d7` |
| 02 · Before you begin | handouts/threat-model.html | `b5576314b2867a3240ee2ba5f7f0324b11f6fea4191ded3a99970367185f211f` |
| 03 · Checklist | handouts/checklist.html | `66960f4b47d24f1538ed0e2b9fd045046c4ede0513f9687c2f38ba69b3bf4b37` |
| 05 · Check the files | handouts/verify.html | `f280a7b205fe50df83bbe8992b39ab0cccea04604eacb99dd05a32022f96772d` |
| 04 · Two boots | handouts/airgap.html | `1a334f2d1b6ec2e3c0549cb11f795e65eaf28445caeb45bfa3caea25481e21e8` |
| 06 · Make the three keys | handouts/dice.html | `d841d07a07f95fe96e044ae7d8a57532c07900e9ecca561b712968486c15ff8e` |
| 07 · Build the 2-of-3 | handouts/sparrow.html | `c9b0c69a7c5b6f9a23d9d8aed6dd40e16eaa02ca63ce86c81d89c22c1162a814` |
| 10 · Rehearse on testnet | handouts/testnet.html | `875bf83d2fa45c19b43a2e117fdf953754de4562e5b4248961d8afa0fdd1e308` |
| 08 · Practice spend | handouts/signing.html | `2094e66ca495fde23cce018eb9a7b7a90c70af3af448e31297d9afdd14d31629` |
| 09 · Metal and the map | handouts/titanium.html | `dd06c383957f21fb4904f650c225d346248d44feb1ea125c3bcfd7d75357d415` |
| 11 · Hide the wallet map | handouts/encryption.html | `39dfb405a0fd0c23d4f9c5e18407e872988655c7eb2aa651e80bdcf060f8fe4c` |
| 12 · If I am gone | handouts/inheritance.html | `df0573fa189e8ada8a69dfe3f187af4aef97cb5e2994af2092db873c92edfe70` |
| 13 · If you get stuck | handouts/faq.html | `607e158b216088def686b767ca7223823b8e917a9baa6a349fcbc9870f6d2f84` |
| 14 · Tough questions | handouts/briefing.html | `bb530f0c2470a074377e8992b1db7dd7799225da2cd1982f3d574c3ff6894f09` |
| 15 · Recovery card | handouts/fire-card.html | `d4230f3ed58045c168be869cb0b8b6113c20f0caf55f3fb7269506e8c0db3b25` |

<!-- END GENERATED: PAGE FINGERPRINTS -->
