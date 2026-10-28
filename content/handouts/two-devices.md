17 · Plebum Dominium

# Two devices and one dice key

- A 2-of-3 wallet. Two keys live on hardware devices from different makers. The third key is a dice seed that no device ever made.
- No one device, one maker, or one place can move the fund alone.
- **The seed phrase is the wallet.** The device only signs.
- **One rule:** the words go into the device itself, during recovery, and nowhere else. Never a website, never an app, never a form from an email.

Files used: Sparrow 2.5.5.

::fig track-b/keys

## Step 1 · Buy two devices, two makers.

- One Jade from Blockstream&rsquo;s own shop. One BitBox from BitBox&rsquo;s own shop. Not two of the same box.
- A device bought used, or from a marketplace seller, is not a signer. Do not trust it to hold anything.
- Check the device before it holds anything: the maker&rsquo;s own verification, the seals, the screen. A reseller device from 2026 taught this lesson with real money.

## Step 2 · Make the dice key.

- Roll it on an offline boot, the way [Make the three keys](/handouts/dice) teaches. Five dice, faces 1 to 4. Two tools must print the same 24 words.
- Never let a device roll its own entropy for this stack. The dice key is the key no maker touched.
- Write the 24 words on paper. They become a plate in Step 4.

## Step 3 · Build the 2-of-3 in Sparrow.

- Import the public keys from both devices and the dice key. Sparrow builds the wallet. It cannot spend.
- Verify the first receiving address on a device screen before anything is sent to it. If the screens disagree, stop.

## Step 4 · Back it all up in metal.

- Stamp the dice seed on its own plate, the way [Metal and the map](/handouts/titanium) teaches.
- Each device seed gets its own backup, on metal or on the maker&rsquo;s own backup device, kept apart from the other keys.
- Three keys, three places. If one place burns, the other two keys still open the fund.

## Step 5 · Hide the wallet map.

- Encrypt the descriptor the way [Hide the wallet map](/handouts/encryption) teaches. The map alone tells a finder nothing.
- Store the map apart from every key.

## Step 6 · Practice spend, then real coins.

- Send a small amount in. Spend it with the two devices.
- Spend it once with a device and the dice key, through the offline boot, so you know that path works before it matters.
- Confirm each spend lands. Then move the rest.

::fig track-b/signing

## Know the limits

- Two devices from two makers still trust firmware. The dice key is what breaks that trust: it takes two makers failing together, plus the dice key, to move the fund.
- Two devices stored in one place fail together. Geography is not optional.
- The dice key&rsquo;s offline signing is the hardest step on this sheet. Practice it on testnet first, or with a small amount, before it carries real money.
- For the people after you: an heir needs any two keys plus the map. The [If I am gone](/handouts/inheritance) sheet walks them through it, with the dice plate standing in for one plate.

## Stop if

- A device comes from a reseller, a marketplace, or a link in a message: stop.
- Both devices come from the same maker: stop. One maker failing takes both keys.
- Anyone asks for your words, for any reason, in any message: stop. They get no answer.
