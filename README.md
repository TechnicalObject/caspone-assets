# caspone-assets

Logos and icons for the casp.one homelab, served at **https://media.casp.one**.

- Latest file: `https://media.casp.one/<path>`, e.g. `https://media.casp.one/caspone/logo-light.svg`
- Browse: every folder has a generated listing, e.g. `https://media.casp.one/caspone/`
- Frozen versions: tag a commit (`git tag 2026-11-24 && git push --tags`) and that
  snapshot is served at `https://media.casp.one/v/<tag>/<path>`; `/v/` lists all tags.

Pushes to `main` and new tags rebuild the site with `.github/workflows/pages.yml`
(build script: `scripts/build_site.py`). Run the script locally to preview `_site/`.
