Independent At-Home Bitcoin Self-Custody

# Plebum Dominium

(PLAY-boom doh-MIN-ee-oom)

Absolute Ownership by the Common People

“Pleb” is an everyday Bitcoiner. “Dominium” is Latin for absolute ownership. This site is for the Bitcoiner who wants to build a secure, self-custody Bitcoin wallet from the ground up, bypassing the need for a company, an app, or a custodian to manage or store access to their funds.

This guide instructs users how to generate entropy with dice, import it into verified software, and create a 2-of-3 multisig wallet stamped into titanium. Hardware wallets and signers are completely optional.

The process leaves no trace. It utilizes Tails OS, an operating system run entirely from a USB drive that is designed to forget all activity upon shutdown.

Plebum Dominium is a goal, not a product. This is an educational tool designed to guide more people toward true, homemade self-custody.[How to use this site](/how-to)[Download one page preview](/kit/00_Project_Overview.pdf)PLEBUM // AUTOPLAY_TIMELINEM1 / M6Play sequence

### 00 // Sovereignty, Handmade

Three keys are made at home, and any two of them can move the coins. No company has to agree before a payment is made. Hardware wallets and signers are completely optional.

### 01 // Create Randomness

Casino dice are rolled by hand, and the faces that are kept become the randomness the keys are built from. That randomness is made offline, where a program cannot supply it.01010110010101010100110101010101011001101010101010101101⚄⚂

### 02 // Go Offline

The calculations are kept off the internet. The computer is booted from a USB drive into Tails, an operating system that forgets the session when the machine shuts down.AIR_GAPPED

### 03 // Double-Blind Check

Two separate programs have to take the same input and produce the same public keys. If they disagree, the result is not trusted.APP_A // SPARROW [OK]APP_B // ELECTRUM [OK]✓

### Match Verified

When both programs print the same result, the keys can be treated as correct. That agreement is the check, and it happens before anything is stamped into metal.

### 04 // Geographic Dispersion

The three keys are stamped into titanium and kept in three separate places. One plate by itself is not enough to spend the long-term fund.🏰🏰🏰‹PLAY SEQUENCE›[Why this guide](#why)[Start the presentation](/deck?n=1)[Presentation handouts](/kit/Presentation_Handouts.pdf)[Download the guide](/kit/02_Print_Packet.pdf)

Why this guide

## Eliminate single points of failure

This guide is used to do that securely and privately, eliminating single points of failure such as:

- One seed that can spend by itself
- An app or an exchange
- One place
- One device, one company
- A photo, a note, or a password manager

Before the first roll

## Materials needed[Checklist](/handouts/checklist)

### On the table

- Five casino dice whose faces can be read
- A pencil and the recording grid
- Established private setting

### One computer

- First boot stays on the network and only watches
- Second boot is Tails, with networking off
- A second USB carries only files that have already been checked

### Files, from their own sites

- Tails
- Sparrow 2.5.5 (required version)
- Electrum
- Ian Coleman page
- Dice converter
[Official downloads page](/resources#official-files)

### Metal

- Three titanium plates, one seed on each
- [StampSeed](https://www.stampseed.com/products/titanium-seed-stamping-kit)is the recommended kit. One plate is included. Two more are purchased.
- [Cryptotag](https://cryptotag.io/products/zeus-starter-kit/)is the other option. The kit includes two plates, so one more is purchased. The two methods are not mixed.
- Three places, far enough apart that losing one does not lose all three keys

[Click here to learn more about inheritance](/inheritance)Sheets in the packet[Download the guide](/kit/02_Print_Packet.pdf)

- [TTermsThese are the words used in this guide, and what they mean.](/handouts/terms)
- [03Checklist](/handouts/checklist)
- [05Check the filesTails, Sparrow 2.5.5, Electrum, the Ian Coleman page, and the dice converter are checked before anything is copied.](/handouts/verify)
- [04Two bootsTails is installed on one USB. Networking is set to Disabled. The other USB carries only files that have already been checked.](/handouts/airgap)
- [06Make the three keysFaces 1 through 4 are kept. The computer is shut down between keys. Two programs have to print the same words.](/handouts/dice)
- [07Build the 2-of-3Sparrow 2.5.5 is the required version. One seed is loaded per boot, and the wallet is built only after no seed is loaded.](/handouts/sparrow)
- [08Practice spendA small amount comes in. The first seed signs, the computer shuts down, the second seed signs, and then the payment is broadcast.](/handouts/signing)
- [09Metal and the mapThree titanium plates are required, with one seed stamped on each plate. StampSeed is the recommended kit. The plates are kept in three places.](/handouts/titanium)
- [11Hide the wallet mapThe wallet map is encrypted with descriptor_obfuscator.py. The passphrase that opens it is not a seed.](/handouts/encryption)
- [12If I am goneTwo plates and the map are required. The words are never typed into a phone.](/handouts/inheritance)
- [13If you get stuckThese are the questions that stop the work, and the answers that let it continue.](/handouts/faq)
- [14If someone challenges itThese are the hard questions, and the answers that are actually true.](/handouts/briefing)

## OptionalHardware signers

- [SeedSigner](https://seedsigner.com)
- [Foundation Passport](https://foundation.xyz)
- [Blockstream Jade](https://blockstream.com/jade/)
- [BitBox02](https://bitbox.swiss)
- [Krux](https://selfcustody.github.io/krux/)

Stop

## Verify the files before going offline

The files have to pass the signature check before the computer is taken offline. A bad signature means the file is deleted. The work does not continue with that file.[Verify package integrity](/verify-software)

## The Process From Start to Finish1Two bootsThe same computer is used twice. The first boot stays on the network and only watches. The second boot is Tails, and the network is off.

![The same computer, first with the network on, then booted from a Tails USB with networking off](/preview/diagram-02_two_boots.png?v=5)

2Check filesThe files have to come from each project's own site, and two programs have to agree before the work continues.

- 

Their own sites

Downloaded from the project that publishes them.
- 

Hash and signature

If either check fails, the file is deleted.
- 

Two tools

The same 24 words have to appear in two programs.
- 

Then the USB

Checked before the data USB is trusted.
- [Official files](/resources)[Verify package integrity](/verify-software)
3Make keysCasino dice make the randomness. Faces 1 through 4 are kept, faces 5 and 6 are rolled again, and the result is three separate lists of 24 words.

![Dice faces 1 through 4 kept, 5 and 6 thrown again](/preview/diagram-03_dice.png?v=4)

How the checksum is checked

- Two tools have to print the same 24 words. If they differ, the work stops.
- A list that will not open is a stop. Word 24 is not changed to force it.
- Word 24 is the check. It is not invented.
4Two of threeThe wallet needs any two of the three keys before it can spend. One key by itself cannot move the long-term fund.

![Three keys around a vault that needs two signatures](/preview/diagram-04_two_of_three.png?v=4)

5Practice spendA small amount is received, two keys sign the payment, and that same small amount is sent out before any savings are moved.

![Unsigned payment, first signature, second signature, broadcast](/preview/diagram-05_spend_path.png?v=4)

6Metal + mapThe three keys are stamped into titanium and kept at three addresses. The wallet map travels with the record of those places, and the map is not another key.

![Three houses each holding one plate](/preview/diagram-06_split_map.png)

The home plate

- The plate alone opens a small wallet. That is not the fund.
- The same words plus a passphrase are for spending. The passphrase is not stamped on the plate.
- The home plate plus one other plate is the long-term fund.

[Learn more about decoy wallet strategies here](/decoy)

[Click here to learn more about inheritance](/inheritance)7House rulesThe house rules are the limits of the method. A convenience is not allowed to break one of them.

![Five house rules](/preview/diagram-07_house_rules.png?v=5)

The bench names for this same method

- Tails, networking set to Disabled
- 2-of-3 native SegWit, path m/48'/0'/0'/2'
- An unsigned payment file is a PSBT
- The wallet map is an output descriptor
- Faces 1 through 4 are kept
Terms[Print one page](/handouts/terms)

**entropy**

Entropy is the randomness that is made with the dice, and it is the material the 24 words are built from.

**airgap / Tails, networking off**

It is critical that each key is made on a computer that is offline. Tails OS is installed on one of the two USB drives. It can be booted on any computer, and it is designed to forget the session when the machine shuts down. When Tails is booted, networking is set to Disabled.

**2-of-3 native SegWit (P2WSH)**

This is a wallet that needs any two of three keys before it can spend. One key by itself cannot move the long-term fund.

**m/48'/0'/0'/2'**

This is the path Sparrow fills in for this kind of wallet. It is confirmed on the screen, and it is not typed from memory.

**PSBT**

A PSBT is an unsigned payment file that is carried on the USB drive. The seed stays on the offline computer.

**descriptor / xpub**

The descriptor is the wallet map, and an xpub is a public watch key. Either one can watch the money, and neither one can spend it.

**BIP39**

BIP39 is the standard list of 2,048 words that a seed is written in. This process uses 24 of those words.

**hash**

These files are downloaded from their original sources. The fingerprint on that source has to match the fingerprint the computer prints for the saved file. If the lines do not match, the file is deleted.

**signature**

A signature is the project confirming the file. If the signature fails, the file is deleted and downloaded again.

**zero-trust**

Zero-trust means a company’s word is not accepted for a download or for a key. Two tools have to agree.

## Downloads[Download the guide](/kit/02_Print_Packet.pdf)[Presentation handouts](/kit/Presentation_Handouts.pdf)[Download the whole kit](/kit/Plebum_Dominium_kit.zip)[Download the source](/Plebum_Dominium_source.zip)

[verify_kit.sh](/kit/verify_kit.sh)checks the pinned SHA-256 fingerprints of the files in the kit. It does not check signatures, so that check still has to be done separately.Individual files

- [00_Project_Overview.pdfThis is the one-page overview, and the QR code opens the live site.](/kit/00_Project_Overview.pdf)
- [01_Slides.pptxThis is the original Plebum Dominium presentation.](/kit/01_Slides.pptx)
- [02_Print_Packet.pdfFor the person doing the work. Checklist, files, keys, spend, plates, and inheritance.](/kit/02_Print_Packet.pdf)
- [Presentation_Handouts.pdfPresentation handouts. These sheets follow the slides.](/kit/Presentation_Handouts.pdf)
- [Handouts_No_Cover.pdfThe same working sheets, without the cover page.](/kit/Handouts_No_Cover.pdf)
- [Terms.pdfThese are the words used in this guide, and what they mean.](/kit/Terms.pdf)
- [03_Checklist.pdfMaterials, the work in order, and the house rules.](/kit/03_Checklist.pdf)
- [04_Airgap.pdfTails is the offline computer. Networking is set to Disabled. The other USB carries only files that have already been checked.](/kit/04_Airgap.pdf)
- [05_Verify.pdfTails, Sparrow 2.5.5, Electrum, the Ian Coleman page, and the dice converter are checked before anything is copied.](/kit/05_Verify.pdf)
- [06_Dice.pdfFaces 1 through 4 are kept. The computer is shut down between keys. Two programs have to print the same words.](/kit/06_Dice.pdf)
- [07_Sparrow.pdfSparrow 2.5.5 is the required version. One seed is loaded per boot, and the wallet is built only after no seed is loaded.](/kit/07_Sparrow.pdf)
- [08_Signing.pdfA small amount comes in. The first seed signs, the computer shuts down, the second seed signs, and then the payment is broadcast.](/kit/08_Signing.pdf)
- [09_Titanium.pdfThree titanium plates are required, with one seed stamped on each plate. StampSeed is the recommended kit. The plates are kept in three places.](/kit/09_Titanium.pdf)
- [11_Encryption.pdfThe wallet map is encrypted with descriptor_obfuscator.py. The passphrase that opens it is not a seed.](/kit/11_Encryption.pdf)
- [12_Inheritance.pdfTwo plates and the map are required. The words are never typed into a phone.](/kit/12_Inheritance.pdf)
- [13_FAQ.pdfThese are the questions that stop the work, and the answers that let it continue.](/kit/13_FAQ.pdf)
- [14_Speaker.pdfThese are the hard questions, and the answers that are actually true.](/kit/14_Speaker.pdf)
- [verify_downloads.pyThis script is run offline. The file is kept only if the check passes.](/kit/verify_downloads.py)
- [verify_kit.shThis script checks fingerprints only, and it does not check signatures.](/kit/verify_kit.sh)
- [10_Recovery.xlsxThis workbook records places and rehearsal dates, and it never records the seed words.](/kit/10_Recovery.xlsx)
- [descriptor_obfuscator.pyThis tool encrypts the wallet map with GPG on Tails. The passphrase is not a seed, and it is not stamped on a plate.](/kit/descriptor_obfuscator.py)
- [bip39_dice_converter.pyThis converter is used only while offline, and its fingerprint is checked against VERIFY.md first.](/kit/bip39_dice_converter.py)
- [VERIFY.mdThis file publishes the SHA-256 fingerprints for the scripts.](/kit/VERIFY.md)
- [README.mdThis file is the map of the kit and the house rules.](/kit/README.md)
