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
| 00_Project_Overview.pdf | 2026.10.21 | `302559ce5fa92523d7c9741a9f6750bcebb63696d948480371748da7d3d5304a` | `bf8fac59b05e1186ac2d819fb4a9cf16d4f325a7b41e1e04a59950fec7a565c4` |
| 02_Print_Packet.pdf | 2026.10.21 | `abeedbb78815501cbeb0efb1b9c9bc9a77e53a08d61f4218157593eeff0646e9` | `5789e6cca41b35e53d2d95fb9c754f83dc7793798671c5f18ddf0d052568dbda` |
| 03_Checklist.pdf | 2026.10.21 | `dbc4a4c9f13e9f85e3a010d8d7e864b044c7d4e02710f92bb85dc2c76c849674` | `8a3bf59d0431bad69fd2d5b7412db9eaa6d8ca6f185d46068ae0e9d1dc096eb0` |
| 04_Airgap.pdf | 2026.10.21 | `fe0e1abb9d94b3250bf0ac34a1d2ecd38ada62b086b3dd49c3352184ad00d710` | `f3a0611b1d209b37709fde8f90fbe0bb78f1f4a3c5023064c1efa40326de5e74` |
| 05_Verify.pdf | 2026.10.21 | `2a92f82ec475090cd895e55a4428993f0f367ceb9cf1dc90eac2f4415045632b` | `6f95f6ac9efeefc1ae40c7066e561fda11de1e26928ae160fa7563c6298eef36` |
| 06_Dice.pdf | 2026.10.21 | `e462c05b3d9ebf95fa87cb9646a7e7d733458a9326395b1ddfcf502a8bbf52ed` | `80a86e52b74be5fd38e2510e3b3619f60e83345a6fa58c31a837d4e31f6ffc23` |
| 07_Sparrow.pdf | 2026.10.21 | `458849618cd31e65b287a023e0ce2f51993197542adab0c5ac49ee20112ece04` | `3195ede4fd9dd1018b0bf6c7c33cc837fb8afabe3e2129d3a0e1e3f2d9f36b99` |
| 08_Signing.pdf | 2026.10.21 | `3d913660f02997fab1c4e1b15119f3c3af8dcbdbdaa6d2ce64dcfbcea9d94aab` | `ccff78d819eec20407abcb1b1b79132a371af848745fb94dfbd95a76d7eda22e` |
| 09_Titanium.pdf | 2026.10.21 | `fa0e9f1f9e4385d21979ab6257ab39f1d95412ef23eb9d652434e60e7bd7412c` | `3756e087a22f915f33b4a46953ae0227316c35df7311dcdf59741e1d6563f2ba` |
| 11_Encryption.pdf | 2026.10.25 | `a2d4a42c65e3c9dbf558669ff9b2beff720b711733de37ebaf9c7b17fb9a5f1e` | `1ca733cf74ddc3f3f308579dcd2d7a9a97c64be5b7c3132728f434e4a5789985` |
| 12_Inheritance.pdf | 2026.10.21 | `bc6b6f093401aa61bf72c879816f4895a60ba100cd8f5178e0810ce2d94a55ea` | `620da36df5d5c9d50a1ca62fd2d2abc7e79df405d8edb4da549880eff0cd8af5` |
| 13_FAQ.pdf | 2026.10.21 | `d7ea94053b706f6ed68adbb4dc7ce529f5b49d7497a9d290eaa4abf9280d8493` | `fc5ba25be0c80a0624408103437ed86348c6cbc487f4084e1323ac13119da59d` |
| 14_Speaker.pdf | 2026.10.21 | `1fe1670e66b87a43f109230a894cbfc8c7424ff2431d9f2f8ca29da5076a21fd` | `1b2cabb828b26d58cbb7e89a3ffd4a2784cddce6c5bcae842dc8be8adb72a62d` |
| 15_Fire_Card.pdf | 2026.10.22 | `c7a148b74ee1d399c9f53d44ca8c26e450ad04383817230ee4b64dac55bc3673` | `6733a4881aa932acb01cd5a5b49fc86997b56f83a15c8f36be1d32d31445ab29` |
| Handouts_No_Cover.pdf | 2026.10.25 | `2bcf7994747963c9fe137bce983c8e3ef2f0146ba4d2b4d904f6e2e7dbe9608a` | `e6d569158ce499b7b93d7ecaaac9efab3bab9dce2af2ec37f640bd0ae3eb8bbb` |
| Presentation_Handouts.pdf | 2026.10.21 | `88107caaf87744f8915be38e9421075a51fc9e1533ed1537905721b6a4381659` | `65183c56fd85b2e15e20cdb655c037dfbefdca1727cdead8277f4992184f7bcd` |
| Terms.pdf | 2026.10.21 | `a49eb0ac1c8cd59a71fe79e172afa18160a6b28f4019c99667a50a8136a7a2f8` | `054f08a39adce730c61c38c6a253f24a7660e9d71c4dff03d942837ff6058cba` |

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
| T · Terms | handouts/terms.html | `49da64e16d95706815ceea06962d66acb3c23a62b8d8ce0a4bce3b936a78954d` |
| 02 · Before you begin | handouts/threat-model.html | `bacd9c9213cda4efed982bcb124e8049a25861fa7bb58f836d2739e04466fa50` |
| 03 · Checklist | handouts/checklist.html | `4a7d3a43aecc9dca20b5137f8fa5e7cc758bafb6fd9c3f7e99de70625ed3f349` |
| 05 · Check the files | handouts/verify.html | `ee4368fcd91e2d1fa7655e94da00e5dc26cd9fb1c3cdeeed6a6149123be854f3` |
| 04 · Two boots | handouts/airgap.html | `9b112f0e317547d79018044e5898ebbe28c5e79001264853f06de6c340209eaa` |
| 06 · Make the three keys | handouts/dice.html | `5f4c5d9c00d5594d382e053d1eaa18935d5ce04ddb1ef155de55f5c99c321933` |
| 07 · Build the 2-of-3 | handouts/sparrow.html | `94b419d15ffb206fbc0c6a62b5e54fbcc1f77e6f426cb5b507959e21251536e7` |
| 10 · Rehearse on testnet | handouts/testnet.html | `001aac211888cfcf2e20b5927a82ddacfc4dfccd2029baf797a364487d1092cc` |
| 08 · Practice spend | handouts/signing.html | `88ac333cb85a8883de95b925df9265d358441053367bb4d18f95d8a7ca4bca76` |
| 09 · Metal and the map | handouts/titanium.html | `e9e19cc75067cdc4d2886fb989fda16d03dd3e6c81193ff4bb8ad5fa32676459` |
| 11 · Hide the wallet map | handouts/encryption.html | `e7150fefcdf567028f50a038a30e4467464d130bce6f5c129e48602ddde00f83` |
| 12 · If I am gone | handouts/inheritance.html | `45db9a52518535aa1dbe5153bce3ff883db0e325e16228cc4859051155bf22e3` |
| 13 · If you get stuck | handouts/faq.html | `0739027e80e92554839ea936c7c32b6194074d2776e63abe32f65afd304f2565` |
| 14 · Tough questions | handouts/briefing.html | `b543f80e025167342dce45f5f44b46f652d8bb71b37d01634484a1cb0079085a` |
| 15 · Recovery card | handouts/fire-card.html | `d4230f3ed58045c168be869cb0b8b6113c20f0caf55f3fb7269506e8c0db3b25` |
| 16 · One key, done right | handouts/single-sig.html | `0c51310be2b54f079fb880611d97681e3306b0b4ad6ebdf172c41fee8d5ab3f9` |
| 17 · Two devices and one dice key | handouts/two-devices.html | `86207cc621107f27d5e18b2b46d682d290a2093a9874c83f68afbbcc8b48fa53` |

<!-- END GENERATED: PAGE FINGERPRINTS -->
