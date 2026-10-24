16 · Plebum Dominium

# One key, done right

The destination of this guide is the 2-of-3 build: three keys, three places, no single point of failure. Two kinds of readers need something else first. The first holds coins in a phone app or on an exchange, with a seed that has touched the internet. The second owns a hardware wallet and believes the device is the vault. It is not. **The seed phrase is the wallet.** The device only signs.

One rule applies to every step that follows. The words go into the device itself, during recovery, and nowhere else. Never a website, never an app, never a form from an email. No hardware company will ever ask for your seed phrase. If a message asks, the message is the attack, no matter how official it looks.

## Step 1 · Grade your seed.

Three questions. Answer honestly; the next step depends on it.

- Was the seed made on the hardware device itself, or in an app?
- Has it ever been typed, photographed, or stored in any digital form: a notes app, a photo, a cloud drive, a password manager?
- Do you hold it on paper or metal, in a place only you know?

Any wrong answer means the seed counts as exposed, and Step 2 is not optional. No seed at all yet (your coins sit on an exchange) also starts at Step 2. A clean seed, born on the device and never copied anywhere digital, goes to Step 3.

One more check. A device bought used, or from a marketplace seller, is not a signer. It is a suspect. Buy hardware from the maker's own shop, or do not trust it with a seed.

## Step 2 · Exposed seed: port over.

Make a fresh seed the offline way, then move the coins onto it. The old device stays on as the signer, and the old seed retires.

First, [Check the files](/handouts/verify): every tool verified before it touches a key. Then boot the offline computer the way [Two boots](/handouts/airgap) teaches: Tails, networking disabled, no Persistent Storage. Make one key exactly the way [Make the three keys](/handouts/dice) makes three: five dice, faces 1 to 4 kept, 5 and 6 rolled again, and the converter and the offline word page must print the same 24 words. If they disagree, stop. Word 24 is a checksum. It is never invented.

Write the 24 words on paper. Then restore them onto your hardware device, entering every word on the device itself. Shut everything down. The fresh seed has now lived in exactly two places: the offline boot, which forgot it, and the device. Step 4 and Step 5 come before any coins move.

## Step 3 · Clean seed: upgrade in place.

Your seed was born on the device and never left it. Keep it. Nothing about the seed changes. The work is everything around it: the passphrase in Step 4, metal instead of paper in Step 5, and the watch-only wallet in Step 6. Go straight to Step 4.

## Step 4 · Add a passphrase.

A passphrase is one more secret, a word or short phrase you choose, entered on the device after the seed. The same 24 words with a passphrase open a different wallet than the same words without one. On this sheet the passphrase is required, and here is why: this wallet has one seed in one place. A plate found or stolen without the passphrase opens an empty wallet. The passphrase is what stands between a found plate and your coins.

Two warnings come with it. A forgotten passphrase loses the coins as surely as a lost seed, and nobody can reset it. A passphrase handed to a scammer along with the words stops nothing, which is why the words and the passphrase are never kept together and never given to anyone. Write the passphrase on paper. Keep that paper in a different place from the plate. Never write the passphrase on the plate itself.

The same seed without the passphrase opens a different, nearly empty wallet. Keep a small spending balance there. A plate found under pressure has something to show, and it is not your savings.

Then prove it works. Note the first receiving address of the passphrase wallet (Step 6 shows how to see it). Later, the restore check in Step 5 confirms the same address comes back from the words plus the passphrase. If it does not, no real money moves until it does.

> [!NOTE] The 2-of-3 build in this guide uses no passphrase, on purpose. Do not add one there. Three keys in three places already do the work. This sheet is one key, so the passphrase carries weight here that it never has to carry in the vault.

## Step 5 · Stamp it in metal.

One seed, one plate, stamped the way [Metal and the map](/handouts/titanium) teaches. Read the finished plate back, word by word, against the paper. Then run the restore check: wipe the device or use a second one, restore from the plate plus the passphrase, and confirm the address from Step 4 comes back. Only when the restore checks out do you destroy the paper the seed was written on. The passphrase paper is not destroyed. It lives in its own place, apart from the plate.

## Step 6 · Watch-only, and the first coins.

On your everyday computer, build a watch-only wallet in Sparrow from the public key the device exports. The watch-only wallet sees balances and builds transactions. It cannot spend. Verify the first receiving address on the device screen before anything is sent to it. If the two screens disagree, stop.

Then the coins, in this order:

- From an exchange: withdraw to the verified address. A small amount first if the exchange lets you split it. Confirm it lands. Then withdraw the rest.
- From an old software wallet: send a small test amount to the verified address. Confirm it lands. Then send the rest. When the old wallet reads zero and the move has confirmed, destroy the old seed paper. It protects nothing now, and a live-looking seed in a drawer only confuses the people who find it later.
- Signing from here on: the watch-only computer builds the spend, the device signs it, the watch-only computer broadcasts. The seed never touches the everyday computer.

## Know the limits

One seed is one point of failure. A fire where the plate sleeps ends this wallet; the passphrase paper surviving somewhere else does not rebuild it. Theft of the plate plus the passphrase paper ends it. Your own mistake, a word copied wrong and never restore-checked, ends it. This sheet beats an exchange account and it beats a seed in a phone, and it is honest about the distance between that and the vault.

Graduate when the stack grows, or when the amount would hurt to lose. The 2-of-3 build starts at the [Checklist](/handouts/checklist), and everything learned here carries over: the dice, the metal, the watch-only habit, the one rule about the words.

For the people after you: an heir needs the plate, the passphrase paper, and one plain note that says what they are and which device can restore them. [If I am gone](/handouts/inheritance) shows how that note should read: plain words, no Bitcoin knowledge assumed, a small test send first.

## Stop if

- The device, an app, or a website asks you to type the words into a computer or a phone: stop. That is the scam, wearing the device's clothes.
- The two dice tools print different words: stop. Do not pick the one you like better.
- A restored wallet shows a different address than the one you noted: stop. No coins move.
- Anyone asks for your words or your passphrase, for any reason, in any message: stop. The answer is no, forever.

Next. When you are ready for the vault:[← Before you begin](/handouts/threat-model)[Build the 2-of-3 →](/handouts/sparrow)
