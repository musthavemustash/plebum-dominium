10 · Plebum Dominium

# Rehearse on testnet

Before any plate exists, do the **entire flow with play money**: build the 2-of-3, receive, sign with two keys, shut down between sessions, broadcast. **The clicks are identical to mainnet.** Mistakes here cost nothing and teach everything.

> [!WARNING] **Testnet coins are worthless.** They cannot be sold, converted, or spent as real bitcoin. That is the point: there is nothing at stake except your learning. Do not "test" with real bitcoin.

Files used: Sparrow 2.5.5.

## The rehearsal

1. **Get testnet coins from a faucet.** Make a testnet address in Sparrow (network: `testnet`), paste it into a faucet, wait for confirmation. This is the only step that touches the internet with your test wallet. Fine, it's worthless.
2. **Build the 2-of-3 in Sparrow on testnet.** Generate three **throwaway** test seeds. Roll dice if you like the ritual, but these get discarded afterward. Import them into Sparrow, build the 2-of-3, **verify the first receiving address on a second screen** (same as the mainnet sheet).
3. **Receive the faucet coins.** Send the tBTC to your test wallet's first receiving address. Watch the transaction confirm. This is your first look at how receive works, on coins that don't matter.
4. **Two-key sign with a shutdown between.** Build a small spend, sign with key 1, **shut the machine down**, boot fresh, sign with key 2, broadcast. This is the exact airgap shutdown ritual the mainnet practice spend demands. Rehearse it here where a forgotten step costs nothing.
5. **Broadcast and confirm.** Send the test coins onward (back to the faucet if it accepts returns, or to a second test address you control). Watch it confirm on a testnet block explorer. You just completed the whole loop.

> [!STOP] **Rule:** never reuse test seeds on mainnet. When the rehearsal is done, the test seeds are burned. They do not get stamped, written down, or kept.

## Graduate when

You built, received, two-key-signed across a shutdown, and broadcast, without the sheet open. If any step felt shaky, repeat it on testnet. **The plates come after you're bored of succeeding on testnet.**
