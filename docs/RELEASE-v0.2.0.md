# ToolDelta 0.2.0 — try MCP contract diffs in your browser

**[Live demo](https://arcnosixta.github.io/tooldelta/)** ·
[Repository](https://github.com/arcnosixta/tooldelta) ·
[Real captured case](https://github.com/arcnosixta/tooldelta/tree/main/examples/filesystem)

[Watch the recorded browser walkthrough](https://arcnosixta.github.io/tooldelta/demo.webm).

Compare saved MCP tool catalogs before changing a server. ToolDelta checks input
and output contracts in the correct compatibility direction, explains findings,
and produces text, JSON, Markdown and interactive HTML reports.

## What's new

- Browser comparison using the **same Python engine**, with Pyodide in a worker.
  Custom catalog contents remain on your device. The first comparison downloads
  the pinned browser runtime from jsDelivr; pre-generated examples need no runtime.
- A real catalog update from the official Filesystem Server, **2025.1.14 → 2026.8.31**.
  `read_multiple_files.paths` gained `minItems: 1`; empty arrays no longer satisfy
  that declared input schema. Provenance and dependency pinning are documented.
- Fewer noisy findings for boolean additional-property relaxation and implicit
  zero minLength/minItems/minProperties.
- GitHub Pages demo, 33 Python tests, real-browser regression checks, and hosted
  tests on Linux/macOS/Windows with Python 3.11 and 3.14.

## Install the wheel

Use a fresh Python 3.11+ virtual environment and the attached wheel:

```sh
python -m venv .venv
# Activate the virtual environment using your shell's normal command.
python -m pip install https://github.com/arcnosixta/tooldelta/releases/download/v0.2.0/mcp_tooldelta-0.2.0-py3-none-any.whl
mcp-tooldelta demo
```

The demo intentionally exits 1 because it contains changes requiring review.
Use `mcp-tooldelta demo --fail-on none` when you only want to see the output.
The installed CLI has **zero runtime dependencies** and works offline.

## Naming and migration

The distribution and command are **`mcp-tooldelta`**, the import/module namespace
is **`mcp_tooldelta`**. The PyPI name `tooldelta` belongs to an unrelated project.
This project is not published to PyPI; use these assets or the official source.
If you used the earlier local 0.1 build, use a fresh environment and the new names.
The repository address and JSON report schema v1 stay the same.

## Limits and feedback

This is an alpha review tool, not a complete JSON Schema inclusion checker or
a security certificate. Unsupported semantics require review; declared behavior
hints are untrusted. Findings can be conservative. The real captured case reports
1 breaking, 45 review and 41 informational findings, not 87 vulnerabilities.

Please share a sanitized pair of catalogs that produces a missing or noisy finding
in [the issue tracker](https://github.com/arcnosixta/tooldelta/issues/new/choose).
Do not include credentials, confidential descriptions or private data.
