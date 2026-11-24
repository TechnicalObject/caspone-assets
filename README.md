# caspone-assets

Logos and icons for the casp.one homelab, served at **https://img.casp.one**.

- Latest file: `https://img.casp.one/<path>`, e.g. `https://img.casp.one/caspone/logo-light.svg`
- Browse: every folder has a generated listing, e.g. `https://img.casp.one/caspone/`
- Frozen versions: tag a commit (`git tag 2026-11-24 && git push --tags`) and that
  snapshot is served at `https://img.casp.one/v/<tag>/<path>`; `/v/` lists all tags.

Pushes to `main` and new tags rebuild the site with `.github/workflows/pages.yml`
(build script: `scripts/build_site.py`). Run the script locally to preview `_site/`.
