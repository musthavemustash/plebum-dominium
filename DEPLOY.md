# Temporary redirect to the test site

plebumbtc.io currently publishes only redirect pages to
https://musthavemustash.github.io/plebum-dominium-test/ .

The maintainer requested this on November 5, 2026 while the original site
and fingerprint-checker availability were under review. This is an explicit
temporary retirement of the production guide and its downloads.

GitHub Pages publishes the artifact built by scripts/build_redirect.py.
It contains redirect HTML, the custom-domain CNAME, robots.txt and .nojekyll.
Matching guide and tool paths go to their staging counterparts. Unknown paths
go through 404.html to the staging homepage. Historical kit files, scripts and
archives are excluded from the deployed artifact.

These are immediate HTML/JavaScript redirects because GitHub Pages does not
provide per-site HTTP redirect rules here. Visitors without JavaScript also
get a meta refresh and a direct link.

Production source files remain in Git for review. Restoring the previous
release deployment requires a separate maintainer-approved change. The last
production commit before retirement was 353cc62a7c0f685dd199e4e89dc486ff230111ae.

The historical deployment instructions follow.

# Deploying plebumbtc.io from GitHub

> **Release safety notice (November 2026):** The legacy "Deploy from a branch"
> instructions below publish tracked `docs/`, which is **not** the
> verified release output. The release pipeline now builds a separate
> `dist/site/` tree, with a manifest and verified ZIPs, but the current
> GitHub Actions workflow does **not** deploy that tree. Do not describe
> the public site as release-verified until a GitHub Pages artifact
> deployment job is added and validated. The required job must depend on
> `release-gate`, upload **only** `dist/site/` using
> `actions/upload-pages-artifact`, then deploy with `actions/deploy-pages`.
> Switch Pages Source to **GitHub Actions** only as part of that tested
> migration. Keep the existing deployment running until the replacement
> is proven. Verify served downloads against `kit/release-manifest.json`
> after deployment; a successful build alone is not proof of served bytes.
>
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
