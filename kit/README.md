# Plebum Dominium

**Take absolute ownership of your Bitcoin with a zero-trust, at-home self-custody setup designed to outlive any third party.**

This folder is the complete Plebum Dominium kit: hold your own Bitcoin keys without buying a company-made hardware signer. The live site is [plebumbtc.io](https://plebumbtc.io).

The biggest threat in Bitcoin custody is a **single point of failure**: one vendor, one device, one tool, one house. A key generated with sufficient entropy in an airgapped environment is the foundation. After that key exists, you *may* export it onto a trusted hardware wallet for signing. If you put more than one key on hardware, use **different vendors**.

You generate entropy with casino dice, convert it on **offline Tails**, build a **2-of-3 native SegWit (P2WSH)** wallet in Sparrow, check the same math in Electrum and Ian Coleman BIP39, then stamp the three seeds on titanium and store them in three places.

The presentation teaches the *why*. The print packet and scripts are what you take to a closed-door table.

The biggest threat in Bitcoin custody is a **single point of failure**: one vendor, one device, one tool, one house. A key generated with sufficient entropy in an airgapped environment is the foundation. After that key exists, you *may* export it onto a trusted hardware wallet for signing. If you put more than one key on hardware, use **different vendors**.

You generate entropy with casino dice, convert it on **offline Tails**, build a **2-of-3 native SegWit (P2WSH)** wallet in Sparrow, check the same math in Electrum and Ian Coleman BIP39, then stamp the three seeds on titanium and store them in three places.

The presentation teaches the *why*. The print packet and scripts are what you take to a closed-door table.

## What this stack is

| Layer | Choice |
|---|---|
| Entropy | 5 casino d6, keep faces 1–4 (two fair bits), reroll 5–6 |
| Offline OS | Tails USB, networking **Disabled** every boot. Optional: radio-less laptop (Wi-Fi card removed) |
| Coordinator | Sparrow Wallet (verified `.tar.gz`) |
| Second check | Electrum + local Ian Coleman BIP39 HTML |
| Wallet | 2-of-3 P2WSH, path `m/48'/0'/0'/2'` |
| Backup | Three titanium stamp plates, one seed each |
| Split | Three distant locations; descriptor is not a third seed |
| Optional later | Export a finished seed onto hardware for signing; multi-vendor if more than one key |

## How to use these files at home

1. Read this README, then watch **01_Slides.pptx**.
2. Print **02_Print_Packet.pdf**. It is the same set as the handouts on the site: Terms, then 03, 05, 04, 06, 07, 08, 09, 11, 12, 13, and 14. **Handouts_No_Cover.pdf** is that set without the contents page.
3. On a trusted online computer, download official Tails, Sparrow, Electrum, and Ian Coleman BIP39. Verify hashes and signatures. Copy only verified files to a clean data USB.
4. Verify **bip39_dice_converter.py** against **VERIFY.md** *before* you run it. If the hash differs, stop.
5. Work **03_Checklist.pdf** in order, with Tails networking off whenever a seed is in memory.
6. On the online computer, put the official downloads next to **verify_downloads.py**. Run `python3 verify_downloads.py`. A mismatch means delete that file.
7. Test with dust in and dust out. Move savings only after both rehearsals succeed.
8. Stamp plates, restore at least one seed from metal, then split locations. Log *places* in **10_Recovery.xlsx**, never the words.
9. Blind the wallet map with **11_Encryption.pdf**. Leave **12_Inheritance.pdf** where a spouse can find it. No seed words on that page.

**House rules.** No photos of seeds, plates, or word-bearing screens. No seed on a machine that has had a network up in that session. Never load two seeds in one Tails boot. If verification fails, stop.

## Files

### Presentation and packet

| File | What it is | What it outlines |
|---|---|---|
| **00_Project_Overview.pdf** | One-page team overview | Stack, kit map, house rules, QR to the live site (`plebumbtc.io`) |
| **01_Slides.pptx** | 25-slide Plebum Dominium presentation | Single point of failure; airgapped entropy as the foundation; optional multi-vendor hardware later; 2-of-3; titanium and geography |
| **02_Print_Packet.pdf** | The full printable packet | Same handouts as the site menu, in this order: Terms, 03, 05, 04, 06, 07, 08, 09, 11, 12, 13, 14 |
| **Handouts_No_Cover.pdf** | Those handouts without the contents page | Print this when the contents page is not needed |

### Handouts (also inside the print packet)

| File | What it is | What it outlines |
|---|---|---|
| **Terms.pdf** | Terms | The words used in this guide |
| **03_Checklist.pdf** | Project Overview | Materials, the work in order, and the house rules |
| **05_Verify.pdf** | Check the files | Tails, Sparrow 2.5.5, Electrum, the Ian Coleman page, and the dice converter |
| **04_Airgap.pdf** | Two boots | Tails is the offline computer. Networking is set to Disabled |
| **06_Dice.pdf** | Make the three keys | Faces 1 through 4, plus the recording grid |
| **07_Sparrow.pdf** | Build the 2-of-3 | Sparrow 2.5.5. One seed per boot |
| **08_Signing.pdf** | Practice spend | A small amount, two signatures, then broadcast |
| **09_Titanium.pdf** | Metal and the map | Three titanium plates. StampSeed is the recommended kit. Three places |
| **11_Encryption.pdf** | Hide the wallet map | The passphrase that opens the map is not a seed |
| **12_Inheritance.pdf** | If I am gone | Two plates and the map. The words are never typed into a phone |
| **13_FAQ.pdf** | If you get stuck | The questions that stop the work |
| **14_Speaker.pdf** | If someone challenges it | The hard questions, and the answers that are true |

## Materials needed

- One computer that boots from USB.
- Run ./verify_kit.sh before the data USB.
- Tails USB. Second USB for files only.
- Five casino dice. Pencil. Paper grids.
- Three 24-word titanium plates.
- **11_Encryption.pdf** before the map is stored.
- **12_Inheritance.pdf** printed for a spouse.

## Download the kit

- **verify_kit.sh** checks the pinned SHA-256 hashes. A missing required file fails too. Not signatures.
- chmod +x verify_kit.sh then double-click it.
- Pinned versions only. A mismatch means delete that file.
- **11_Encryption.pdf** blinds the wallet map.
- **12_Inheritance.pdf** is the letter for heirs.
- **02_Print_Packet.pdf** is sheets 03–09. Sheets 11 and 12 stay separate.

### Recovery log and converter

| File | What it is | What it outlines |
|---|---|---|
| **10_Recovery.xlsx** | Location and recovery workbook | Where plates and the descriptor live; rehearsal dates; txids of test spends. **Do not put seed words in this file** |
| **bip39_dice_converter.py** | Offline dice-bits → BIP39 24-word converter | Standard-library only. Extra bits are SHA-256’d down to 256. First instruction in the file is: verify the file |
| **verify_downloads.py** | Offline hash check for the other downloads | Calls the audit inside the dice converter |
| **verify_kit.sh** | Desktop launcher for the hash audit | Checks pinned SHA-256 hashes. Does not check signatures |
| **VERIFY.md** | How to check the kit scripts | Published SHA-256 for the scripts. Dummy-bits test for the converter |

### Other

| File | What it is |
|---|---|
| **AGENTS.md** | Short project brief used when this kit is edited |
| **README.md** | This file |

## Official software (get these yourself)

Do not follow a random video’s shortened link. Bookmark the project’s own site:

- Tails: official Tails website (ISO + signing key)
- Sparrow Wallet: official Sparrow website (Linux `.tar.gz` + hash/signature)
- Electrum: official Electrum website
- Ian Coleman BIP39: official GitHub repo; save the HTML and open it **offline**
- BIP39 English wordlist: `bitcoin/bips` `bip-0039/english.txt` (to compare the converter’s list)

## Converter hash

After any edit to `bip39_dice_converter.py`, recompute:

```bash
sha256sum bip39_dice_converter.py
```

The digest must match **VERIFY.md**. If it does not, do not run that copy.

Current published values are kept only in `VERIFY.md` so this README does not go stale if the script changes again.
