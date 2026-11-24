#!/usr/bin/env python3
"""Build the img.casp.one site into _site/.

- Copies every asset from the current checkout to the site root
  (stable URLs such as /caspone/logo-light.svg).
- Copies each git tag's assets to /v/<tag>/ so older versions stay
  reachable at fixed URLs.
- Writes an index.html listing into every folder so the site can be browsed.
"""
import html
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_site"
SKIP = {".git", ".github", "scripts", "_site", "README.md", ".gitignore", ".DS_Store"}
IMAGE_EXT = {".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".avif"}


def copy_tree(src: Path, dst: Path) -> None:
    for item in src.iterdir():
        if item.name in SKIP or item.name.startswith("."):
            continue
        if item.is_dir():
            copy_tree(item, dst / item.name)
        else:
            dst.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dst / item.name)


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], check=True,
                          capture_output=True, text=True).stdout


def export_tags() -> list[str]:
    tags = [t for t in git("tag", "--sort=-creatordate").split() if t]
    for tag in tags:
        tmp = OUT / ".tmp-export"
        shutil.rmtree(tmp, ignore_errors=True)
        tmp.mkdir(parents=True)
        archive = subprocess.run(["git", "-C", str(ROOT), "archive", tag],
                                 check=True, capture_output=True).stdout
        subprocess.run(["tar", "-x", "-C", str(tmp)], input=archive, check=True)
        copy_tree(tmp, OUT / "v" / tag)
        shutil.rmtree(tmp)
        (OUT / "v" / tag / "CNAME").unlink(missing_ok=True)
    return tags


def human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
:root{{color-scheme:light dark;--bg:#fafafa;--fg:#1a1a1a;--muted:#6b6b6b;--card:#fff;--line:#e4e4e4;--chk:#eee}}
@media (prefers-color-scheme:dark){{:root{{--bg:#141414;--fg:#ececec;--muted:#9a9a9a;--card:#1e1e1e;--line:#2e2e2e;--chk:#2a2a2a}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif}}
main{{max-width:1100px;margin:0 auto;padding:24px 16px}}
h1{{font-size:20px;margin:0 0 4px}} .crumbs a{{color:inherit}} p.muted{{color:var(--muted);margin:0 0 20px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:12px}}
a.card{{display:flex;flex-direction:column;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden;color:inherit;text-decoration:none}}
a.card:hover{{border-color:var(--muted)}}
.thumb{{height:120px;display:flex;align-items:center;justify-content:center;font-size:34px;
background-image:conic-gradient(var(--chk) 25%,transparent 0 50%,var(--chk) 0 75%,transparent 0);background-size:16px 16px}}
.thumb img{{max-width:90%;max-height:100px}}
.meta{{padding:8px 10px;font-size:13px;word-break:break-all}} .meta span{{display:block;color:var(--muted);font-size:12px}}
</style></head><body><main>
<h1 class="crumbs">{crumbs}</h1>
<p class="muted">{note}</p>
<div class="grid">{items}</div>
</main></body></html>
"""


def write_index(folder: Path, tags: list[str]) -> None:
    rel = folder.relative_to(OUT)
    parts = [] if str(rel) == "." else list(rel.parts)
    crumbs = ['<a href="/">img.casp.one</a>']
    for i, p in enumerate(parts):
        crumbs.append(f'<a href="/{"/".join(parts[:i+1])}/">{html.escape(p)}</a>')
    items = []
    if parts:
        items.append('<a class="card" href="../"><div class="thumb">↩</div><div class="meta">..<span>up</span></div></a>')
    entries = sorted(folder.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    for e in entries:
        if e.name in ("index.html", "CNAME") or e.name.startswith("."):
            continue
        name = html.escape(e.name)
        if e.is_dir():
            label = "versions" if not parts and e.name == "v" else "folder"
            items.append(f'<a class="card" href="{name}/"><div class="thumb">📁</div>'
                         f'<div class="meta">{name}/<span>{label}</span></div></a>')
        else:
            thumb = (f'<img src="{name}" alt="" loading="lazy">'
                     if e.suffix.lower() in IMAGE_EXT else "📄")
            items.append(f'<a class="card" href="{name}"><div class="thumb">{thumb}</div>'
                         f'<div class="meta">{name}<span>{human(e.stat().st_size)}</span></div></a>')
    if not parts:
        note = ("Latest assets. Older versions live under /v/&lt;tag&gt;/."
                if tags else "Latest assets. Tag a commit to keep a fixed copy under /v/&lt;tag&gt;/.")
    elif parts[0] == "v" and len(parts) == 1:
        note = "Each folder is a frozen copy of the repository at that git tag."
    else:
        note = ""
    (folder / "index.html").write_text(PAGE.format(
        title="/" + "/".join(parts) if parts else "img.casp.one",
        crumbs=" / ".join(crumbs), note=note, items="".join(items)), encoding="utf-8")


def main() -> int:
    shutil.rmtree(OUT, ignore_errors=True)
    OUT.mkdir()
    copy_tree(ROOT, OUT)
    shutil.copy2(ROOT / "CNAME", OUT / "CNAME")
    tags = export_tags()
    (OUT / ".nojekyll").touch()
    for dirpath, _, _ in os.walk(OUT):
        write_index(Path(dirpath), tags)
    print(f"Built {OUT} with {len(tags)} tagged version(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
