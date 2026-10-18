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
