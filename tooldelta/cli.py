"""Scriptable CLI with deterministic reports and review gates."""

from __future__ import annotations

import argparse
from importlib.resources import files
import json
import os
from pathlib import Path
import sys
import tempfile

from . import __version__
from .catalog import CatalogError, load_catalog, normalize_catalog
from .diff import compare
from .render import render


def _write(path: Path, content: str, force: bool, inputs: list[Path]) -> None:
    resolved = path.resolve()
    if any(resolved == source.resolve() for source in inputs):
        raise CatalogError("Output must not overwrite an input catalog.")
    if path.exists() and not force:
        raise CatalogError("Output already exists. Choose another path or use --force.")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(content)
        if force:
            os.replace(temporary, path)
        else:
            # Exclusive creation also prevents accidental overwrite if another process wins the race.
            with path.open("x", encoding="utf-8", newline="\n") as handle:
                handle.write(temporary.read_text(encoding="utf-8"))
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _report_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--format", choices=("text", "json", "markdown", "html"), default="text")
    parser.add_argument("-o", "--output", type=Path, help="Write a report instead of stdout")
    parser.add_argument("--force", action="store_true", help="Allow overwriting an existing output file")
    parser.add_argument("--fail-on", choices=("breaking", "review", "info", "none"), default="review",
                        help="Exit 1 at or above this severity (default: review)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tooldelta", description="Offline MCP contract diffs. Never connects to servers or executes tools.")
    parser.add_argument("--version", action="version", version=f"ToolDelta {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)
    diff = commands.add_parser("diff", help="Compare two complete saved tools/list catalogs")
    diff.add_argument("before", type=Path)
    diff.add_argument("after", type=Path)
    _report_options(diff)
    demo = commands.add_parser("demo", help="Compare bundled fixtures: no setup, credentials, or network")
    _report_options(demo)
    snapshot = commands.add_parser("snapshot", help="Normalize a saved catalog into a reviewable baseline")
    snapshot.add_argument("catalog", type=Path)
    snapshot.add_argument("-o", "--output", type=Path, required=True)
    snapshot.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "snapshot":
            tools = load_catalog(args.catalog)
            content = json.dumps({"tools": list(tools.values())}, ensure_ascii=False, indent=2) + "\n"
            _write(args.output, content, args.force, [args.catalog])
            print(f"Saved normalized baseline with {len(tools)} tools.", file=sys.stderr)
            return 0
        inputs = []
        if args.command == "demo":
            data = files("tooldelta").joinpath("examples")
            before = normalize_catalog(json.loads(data.joinpath("before.json").read_text(encoding="utf-8")))
            after = normalize_catalog(json.loads(data.joinpath("after.json").read_text(encoding="utf-8")))
            labels = ("workspace v1.4", "workspace v1.5")
        else:
            inputs = [args.before, args.after]
            before, after = load_catalog(args.before), load_catalog(args.after)
            labels = (args.before.name, args.after.name)
        report = compare({"tools": list(before.values())}, {"tools": list(after.values())})
        content = render(report, args.format, *labels)
        if args.output:
            _write(args.output, content, args.force, inputs)
            print("Report written. " + ", ".join(f"{count} {level}" for level, count in report.counts.items()), file=sys.stderr)
        else:
            # Windows consoles may not be configured for UTF-8. Files always are.
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(errors="backslashreplace")
            sys.stdout.write(content)
        return int(report.fails(args.fail_on))
    except (CatalogError, OSError, ValueError) as exc:
        print(f"tooldelta: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
