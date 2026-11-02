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
Size:     8456 bytes
SHA-256:  35f8807c72241bcbe97318f7ffa4e4c6e211df180e67f85656e0429520466589
```

Linux / macOS / Tails:

```bash
sha256sum descriptor_obfuscator.py
```

The hash must match exactly:

```
35f8807c72241bcbe97318f7ffa4e4c6e211df180e67f85656e0429520466589
```

If it does not match, stop. Do not run that copy. The tool calls GPG with AES-256. It does not contain a cipher of its own.

## Hash checker page

```
File:     hash_checker.html
Size:     4747 bytes
SHA-256:  0e32bb36a531b02072c9d982697210554455e5c4955486629ea332106f68a816
```

A single page from this kit that works out a file's SHA-256 in the browser, for the check in section 1 without the command line. Its own fingerprint is the block above, so it can be checked the same way as the tools.

## EFF Long Wordlist

```
File:     eff_large_wordlist.txt
Size:     108800 bytes
SHA-256:  addd35536511597a02fa0a9ff1e5284677b8883b83e986e43f15a3db996b903e
```

The EFF Long Wordlist, 7,776 words, one per five digit dice number from 11111 to 66666. Source: eff.org. Roll five dice, read the faces left to right, look the number up, write down the word, repeat to at least six words.

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

### The same check without the command line

Open `hash_checker.html` from this kit in any browser and drop the file on it. The page works out the SHA-256 on your own machine and shows it. Paste the hash from this file next to it and the page tells you whether they match. Nothing is uploaded: the math runs in the browser tab, and the page works with the internet disconnected.

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
build date, and a Content SHA-256: the hash of the handout's content
before the footer was stamped on. Match the number printed on a paper
copy to the Content SHA-256 below to confirm the copy is the handout as
published. The File SHA-256 is the hash of the PDF file itself, exactly
as served:

| File | Version | File SHA-256 | Content SHA-256 |
| --- | --- | --- | --- |
| 00_Project_Overview.pdf | 2026.10.21 | `302559ce5fa92523d7c9741a9f6750bcebb63696d948480371748da7d3d5304a` | `2972a97e363a7cecf2318d8f37f3dfae6eb43c13323aaef3bbdb77b68cd89c06` |
| 02_Print_Packet.pdf | 2026.10.27 | `bab6a24ae54d06f804727a742ddd7f31afa68bd46e47dc3152d57d1264de39a8` | `f970ab92eb8086dcbabbe44a7f4b39404250fa6b353a1cd58f7caa3cd002f511` |
| 03_Checklist.pdf | 2026.10.21 | `dbc4a4c9f13e9f85e3a010d8d7e864b044c7d4e02710f92bb85dc2c76c849674` | `a2f0b13ba69db578f82da2a28dae07783b35e7fd2f859073237ad0113b160ff4` |
| 04_Airgap.pdf | 2026.10.21 | `fe0e1abb9d94b3250bf0ac34a1d2ecd38ada62b086b3dd49c3352184ad00d710` | `fe0e1abb9d94b3250bf0ac34a1d2ecd38ada62b086b3dd49c3352184ad00d710` |
| 05_Verify.pdf | 2026.10.21 | `2a92f82ec475090cd895e55a4428993f0f367ceb9cf1dc90eac2f4415045632b` | `b5c36855913714ccf26ec9b96d8b4e682be94e9312861a4e1eb32f970e3aa4f9` |
| 06_Dice.pdf | 2026.10.27 | `fb742dc0c79c007981096eb7b101ae76e47c532c14b85faaf6cf86687ba1e05e` | `fb742dc0c79c007981096eb7b101ae76e47c532c14b85faaf6cf86687ba1e05e` |
| 07_Sparrow.pdf | 2026.10.21 | `458849618cd31e65b287a023e0ce2f51993197542adab0c5ac49ee20112ece04` | `458849618cd31e65b287a023e0ce2f51993197542adab0c5ac49ee20112ece04` |
| 08_Signing.pdf | 2026.10.21 | `3d913660f02997fab1c4e1b15119f3c3af8dcbdbdaa6d2ce64dcfbcea9d94aab` | `c369d6028c0147bd32b79ae75f8a20fe914eef777619656c10660df01a9f5a98` |
| 09_Titanium.pdf | 2026.10.21 | `fa0e9f1f9e4385d21979ab6257ab39f1d95412ef23eb9d652434e60e7bd7412c` | `a8d71eda788b2cb811c29eee646b84be8955e46a81c9863ef116cd031d10e5f5` |
| 11_Encryption.pdf | 2026.10.25 | `a2d4a42c65e3c9dbf558669ff9b2beff720b711733de37ebaf9c7b17fb9a5f1e` | `a2d4a42c65e3c9dbf558669ff9b2beff720b711733de37ebaf9c7b17fb9a5f1e` |
| 12_Inheritance.pdf | 2026.10.21 | `bc6b6f093401aa61bf72c879816f4895a60ba100cd8f5178e0810ce2d94a55ea` | `bc6b6f093401aa61bf72c879816f4895a60ba100cd8f5178e0810ce2d94a55ea` |
| 13_FAQ.pdf | 2026.10.21 | `d7ea94053b706f6ed68adbb4dc7ce529f5b49d7497a9d290eaa4abf9280d8493` | `8d1ef0d08389066b83ce3b2cb53c04cbbc3c7d9f4729947549f8ab8c5c721065` |
| 14_Speaker.pdf | 2026.10.21 | `1fe1670e66b87a43f109230a894cbfc8c7424ff2431d9f2f8ca29da5076a21fd` | `1fe1670e66b87a43f109230a894cbfc8c7424ff2431d9f2f8ca29da5076a21fd` |
| 15_Fire_Card.pdf | 2026.10.22 | `c7a148b74ee1d399c9f53d44ca8c26e450ad04383817230ee4b64dac55bc3673` | `c7a148b74ee1d399c9f53d44ca8c26e450ad04383817230ee4b64dac55bc3673` |
| Handouts_No_Cover.pdf | 2026.10.27 | `47cc4ffa23a3c89010304cd24690f6b1efe71f3b2a00db4e60bdcbdb828bbb57` | `47cc4ffa23a3c89010304cd24690f6b1efe71f3b2a00db4e60bdcbdb828bbb57` |
| Presentation_Handouts.pdf | 2026.10.21 | `88107caaf87744f8915be38e9421075a51fc9e1533ed1537905721b6a4381659` | `88107caaf87744f8915be38e9421075a51fc9e1533ed1537905721b6a4381659` |
| Terms.pdf | 2026.10.21 | `a49eb0ac1c8cd59a71fe79e172afa18160a6b28f4019c99667a50a8136a7a2f8` | `a49eb0ac1c8cd59a71fe79e172afa18160a6b28f4019c99667a50a8136a7a2f8` |

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
| 01 · Before you begin | handouts/threat-model.html | `ff9ff8095a51f983eebe6424bff54cf2bb9c4dbab959f9eaaf9ff33f71f37409` |
| 03 · Terms | handouts/terms.html | `4269bf3ad8f08ab0edfdb6c5fd0425d364e78278341ff38f1e9be895f65d380e` |
| 04 · Checklist | handouts/checklist.html | `967eb35acb4ad9e561a0adfc1ddf868d5095277025f2592b81345e209f14eef5` |
| 05 · Two boots | handouts/airgap.html | `2f1d2b1892833d035c0593d7905cc37bf27230e37920d5457ce11ce8bafe705d` |
| 06 · Check the files | handouts/verify.html | `a8c7e5c2368170583cc48e0ed65d77a6811cf3c51d7122b6dabef01a608d80c2` |
| 07 · Make the three keys | handouts/dice.html | `a90a17ce20580c10621b2b7af3898369ffeef25061eb266464353675a27e0c0d` |
| 08 · Build the 2-of-3 | handouts/sparrow.html | `a2ddb8d0668f3f94fe4ce82018667943bf0f0c33ecbd3a82ab6e3e711f047e51` |
| 09 · Practice spend | handouts/signing.html | `3d57ded0af8e05092b599a2d76752d96ccdc00a9511f72b9155e519f9f0fb521` |
| 10 · Metal and the map | handouts/titanium.html | `ae1b32352ea13dbd9849e795df4f55bee811fb1a22babd8e0089d0db7e583225` |
| 11 · Rehearse on testnet | handouts/testnet.html | `243e442908b0a2cc7b445908efa3b38f4b2af038fd201f1cab0ede3f6b4c2d58` |
| 12 · Hide the wallet map | handouts/encryption.html | `f00ae8498b440f6d0245a714d1367b8d6cb2fc60e0eeaa288dd32205f5ba9160` |
| 13 · If I am gone | handouts/inheritance.html | `cac0785bf13cb301a26ab82e30a9c3dbc62b1bc04634264437eea5435fd57d06` |
| 14 · If you get stuck | handouts/faq.html | `e118711468121eb27abec4fabdbf2fd1b6da5bb19947d0693faae666bf9d94bf` |
| 15 · Tough questions | handouts/briefing.html | `4e5f7021dc406a015b1e54f3614d509822c85699a996ad5a3c11718538e9f74d` |
| 16 · Recovery card | handouts/fire-card.html | `6bab93689006f2805a4ebf1f06234b3164993129f8062f83ee9bf788a0f0f538` |
| 17 · One key, done right | handouts/single-sig.html | `57ca85a49701c7220518a3bb4525cd0b307b17b0db82a33d5b5b3fd57422ba3e` |
| 18 · Two devices and one dice key | handouts/two-devices.html | `10da4155e313a2e053f5d3d9899fe8dc9cee37d2970ded91c88dc4580f0dfc79` |

<!-- END GENERATED: PAGE FINGERPRINTS -->
