"""Build a versioned, reproducible agent skill archive without the Python engine."""

from pathlib import Path
import tomllib
import zipfile

ROOT = Path(__file__).resolve().parent.parent


def build(output: Path) -> Path:
    version = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    entries = {
        "mcp-tooldelta/SKILL.md": (ROOT / "skills/mcp-tooldelta/SKILL.md").read_bytes(),
        "mcp-tooldelta/LICENSE": (ROOT / "LICENSE").read_bytes(),
    }
    output.mkdir(parents=True, exist_ok=True)
    target = output / f"mcp-tooldelta-skill-{version}.zip"
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in entries.items():
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content)
    return target


if __name__ == "__main__":
    print(f"Built agent skill at {build(ROOT / 'dist')}")
