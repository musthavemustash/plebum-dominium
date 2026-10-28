16 · Plebum Dominium

# One key, done right

The destination of this guide is the 2-of-3 build: three keys, three places, no single point of failure. In the full build, this sheet is also the spending wallet that lives on Plate A: Seed 1 plus a passphrase, for spending money while savings sit in the vault.

Files used: Sparrow 2.5.5 for the watch-only wallet.

::fig single-sig/two-doors

- **The seed phrase is the wallet.** The device only signs.
- **One rule:** the words go into the device itself, during recovery, and nowhere else. Never a website, never an app, never a form from an email. No hardware company will ever ask for your seed phrase. If a message asks, the message is the attack, no matter how official it looks.

## Step 1 · Grade your seed.

- Was the seed made on the device itself, or in an app?
- Has it ever been typed, photographed, or stored in any digital form (a notes app, a photo, a cloud drive, a password manager)?
- Do you hold it on paper or metal, in a place only you know?

- Any wrong answer: the seed counts as exposed. Step 2 is not optional.
- No seed yet (coins on an exchange): also Step 2.
- Clean seed (born on the device, never copied anywhere digital): Step 3.
- A device bought used, or from a marketplace seller, is not a signer. It is a suspect. Buy from the maker's own shop.

## Step 2 · Exposed seed: port over.

::fig single-sig/port-flow

- Word 24 is a checksum. It is never invented. If the two tools disagree, stop.
- Write the 24 words on paper, then type them into the device on the device itself,* in its own restore menu, on its own screen. Then shut everything down.
- No program on a computer does the restore, not Sparrow, not Electrum, and not a text field in a companion app. If a device needs its companion app to start the restore (BitBox App for a BitBox02, Blockstream Green for a Jade), the app only opens the connection. The words still go in on the device, never typed into the computer.
- In the 2-of-3 build the airgapped boot signs, in Sparrow or Electrum. On this sheet the device signs. You boot your trusted online computer for Sparrow, and Sparrow meets the device afterward, in Step 6, as the watch-only wallet that builds transactions for the device to sign.
- The fresh seed has now lived in exactly two places: the offline boot, which forgot it, and the device.
- Steps 4 and 5 come before any coins move.
- The old device stays on as the signer, and the old seed retires.

^* A device adds trust in its maker: the firmware on it, the chip inside it, and the shop it came from. The trade buys something real. A key the everyday computer never holds cannot be stolen by malware on that computer, and the device screen shows every address before you sign.

::fig single-sig/restore-flow

## Step 3 · Clean seed: upgrade in place.

- Keep the seed. Nothing about it changes.
- The work is everything around it: passphrase (Step 4), metal (Step 5), watch-only (Step 6).
- Go straight to Step 4.

## Step 4 · Add a passphrase.

::anim single-sig/passphrase-dice

- A passphrase is one more secret, not a word or short phrase you choose, entered on the device after the seed. Roll five dice, look the number up in the EFF Long Wordlist, write down the word, and repeat to at least six words.
- On this sheet it is required. One seed in one place is why: a plate found or stolen without the passphrase opens an empty wallet.
- Forgotten passphrase: the coins are gone, and nobody can reset it.
- Handed to a scammer along with the words: it stops nothing. Words and passphrase are never kept together and never given to anyone.
- Write the passphrase on paper. Keep that paper in a different place from the plate. Never write it on the plate.
- Keep a small spending balance in the wallet without the passphrase. A plate found under pressure has something to show, and it is not your savings.
- Prove it works: note the first receiving address of the passphrase wallet. The restore check in Step 5 must bring back that same address. If it does not, no real money moves.

> [!NOTE] The 2-of-3 build in this guide uses no passphrase, on purpose. Do not add one there. Three keys in three places already do the work. This sheet is one key, so the passphrase carries weight here that it never has to carry in the vault.

## Step 5 · Stamp it in metal.

- One seed, one plate, stamped the way [Metal and the map](/handouts/titanium) teaches.
- Read the finished plate back, word by word, against the paper.
- Restore check: wipe the device or use a second one, restore from the plate plus the passphrase, confirm the Step 4 address comes back.
- Destroy the seed paper only when the restore checks out.
- The passphrase paper is not destroyed. It lives in its own place, apart from the plate.

## Step 6 · Watch-only, and the first coins.

::fig single-sig/watch-only-flow

- Build the watch-only wallet in Sparrow from the public key the device exports. It sees balances and builds transactions. It cannot spend.
- Verify the first receiving address on the device screen before anything is sent to it. If the two screens disagree, stop.
- From an exchange: withdraw to the verified address. A small amount first if the exchange lets you split it. Confirm it lands. Then withdraw the rest.
- From an old software wallet: send a small test amount to the verified address. Confirm it lands. Then send the rest.
- When the old wallet reads zero and the move has confirmed, destroy the old seed paper. It protects nothing now, and a live-looking seed in a drawer only confuses the people who find it later.

## Know the limits

- One seed is one point of failure.
- A fire where the plate sleeps ends this wallet. The passphrase paper surviving somewhere else does not rebuild it.
- Theft of the plate plus the passphrase paper ends it.
- A word copied wrong and never restore-checked ends it.
- This sheet beats an exchange account and it beats a seed in a phone. The distance between that and the vault is real.
- Graduate when the stack grows, or when the amount would hurt to lose. The 2-of-3 build starts at the [Checklist](/handouts/checklist). The dice, the metal, the watch-only habit, and the one rule about the words all carry over.
- For the people after you: an heir needs the plate, the passphrase paper, and one plain note that says what they are and which device can restore them. [If I am gone](/handouts/inheritance) shows how that note should read: plain words, no Bitcoin knowledge assumed, a small test send first.

## Stop if

- The device, an app, or a website asks you to type the words into a computer or a phone: stop. That is the scam, wearing the device's clothes.
- The two dice tools print different words: stop. Do not pick the one you like better.
- A restored wallet shows a different address than the one you noted: stop. No coins move.
- Anyone asks for your words or your passphrase, for any reason, in any message: stop. The answer is no, forever.

Next. When you are ready for the vault:[← Before you begin](/handouts/threat-model)[Build the 2-of-3 →](/handouts/sparrow)
