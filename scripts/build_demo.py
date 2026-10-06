"""Build public demo assets using the same Python engine as the CLI."""

from pathlib import Path
import shutil
import sys
import tomllib
import zipfile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from mcp_tooldelta.catalog import load_catalog
from mcp_tooldelta.diff import compare
from mcp_tooldelta.render import render


def build(output: Path):
    output.mkdir(parents=True, exist_ok=True)
    for name in ("index.html", "app.css", "app.js", "worker.js", "favicon.svg"):
        shutil.copyfile(ROOT / "web" / name, output / name)
    (output / ".nojekyll").write_text("", encoding="utf-8")
    shutil.copytree(ROOT / "mcp_tooldelta/examples", output / "examples", dirs_exist_ok=True)
    shutil.copyfile(ROOT / "docs/assets/report.png", output / "report.png")
    shutil.copyfile(ROOT / "LICENSE", output / "LICENSE")
    video = ROOT / "docs/assets/demo.webm"
    if video.exists():
        shutil.copyfile(video, output / "demo.webm")
    pairs = [("sample", ROOT / "mcp_tooldelta/examples", "before.json", "after.json", "workspace v1.4", "workspace v1.5"),
             ("filesystem", ROOT / "examples/filesystem", "2025.1.14.json", "2026.8.31.json", "Filesystem 2025.1.14", "Filesystem 2026.8.31")]
    for name, directory, before, after, old_label, new_label in pairs:
        a, b = load_catalog(directory / before), load_catalog(directory / after)
        report = compare({"tools": list(a.values())}, {"tools": list(b.values())})
        (output / (name + ".html")).write_text(render(report, "html", old_label, new_label), encoding="utf-8")
    with zipfile.ZipFile(output / "engine.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        license_info = zipfile.ZipInfo("LICENSE", date_time=(2026, 1, 1, 0, 0, 0))
        license_info.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(license_info, (ROOT / "LICENSE").read_text(encoding="utf-8").encode("utf-8"))
        for relative in ("__init__.py", "catalog.py", "diff.py", "render.py", "templates/report.html"):
            path = "mcp_tooldelta/" + relative
            info = zipfile.ZipInfo(path, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, (ROOT / path).read_text(encoding="utf-8").encode("utf-8"))
    (output / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://arcnosixta.github.io/tooldelta/sitemap.xml\n", encoding="utf-8")
    (output / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://arcnosixta.github.io/tooldelta/</loc></url></urlset>\n', encoding="utf-8")
    version = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    print(f"Built ToolDelta {version} demo at {output}")


if __name__ == "__main__":
    build(ROOT / "build/demo")
