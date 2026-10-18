# Deploying plebumbtc.io from GitHub

GitHub Pages hosts the site for free, straight from this repo. One-time setup,
about 10 minutes.

## 1. Create the repo

1. Go to https://github.com/new
2. Name it `plebum-dominium` (any name works), **Public**, no README/license/gitignore
   (the repo already has everything).
3. Click **Create repository**.

## 2. Push this code

On any computer with git:

```bash
cd plebum-dominium
git remote add origin https://github.com/YOUR-USERNAME/plebum-dominium.git
git branch -M main
git push -u origin main
```

(Replace `YOUR-USERNAME` with your GitHub username.)

## 3. Turn on GitHub Pages

1. In the repo: **Settings → Pages**.
2. Under **Build and deployment**, set **Source** to **Deploy from a branch**.
3. Set **Branch** to `main` and folder to **`/docs`**. Save.
4. Wait ~1 minute. The site appears at `https://YOUR-USERNAME.github.io/plebum-dominium/`.

## 4. Point plebumbtc.io at it

In your DNS provider (wherever plebumbtc.io's nameservers live):

**Apex domain** (`plebumbtc.io`) — four A records:

| Host | Type | Value |
|---|---|---|
| `@` | A | `185.199.108.153` |
| `@` | A | `185.199.109.153` |
| `@` | A | `185.199.110.153` |
| `@` | A | `185.199.111.153` |

**www** — one CNAME:

| Host | Type | Value |
|---|---|---|
| `www` | CNAME | `YOUR-USERNAME.github.io.` |

Then in the repo: **Settings → Pages → Custom domain**, enter `plebumbtc.io`,
Save, and tick **Enforce HTTPS** once the certificate is issued (up to ~1 hour).

The `docs/CNAME` file in this repo already contains `plebumbtc.io`, so the
custom domain survives every rebuild.

> **Do not switch DNS until the new site is verified** on the
> `github.io` address (step 3). Keep the old site live until the new one
> checks out — then flip DNS.

## 5. The ongoing workflow

```bash
# edit sheets in content/handouts/
python3 scripts/apply-fixes.py   # optional, idempotent
python3 scripts/build.py         # regenerate docs/
git add -A && git commit -m "describe the change" && git push
```

GitHub Pages rebuilds automatically on every push (~1 minute). No builder,
no credits, no AI in the loop unless you want one.

## 6. plebumdominium.org

That domain currently serves the old site. Either point it at the same Pages
site (add it as a second custom domain is not supported — instead redirect it
at your DNS provider to `https://plebumbtc.io`), or leave it until the
canonical move is confirmed. A 301 redirect to plebumbtc.io is the goal.
