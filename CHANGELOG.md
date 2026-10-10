# Changelog

## 0.2.1 — prepared for release

- Compare schema-valued additionalProperties even when unchanged, preserving
  review findings for unsupported nested keywords.
- Detect boolean versus numeric const/enum changes in additionalProperties.
- Portable agent skill for local MCP contract review, with a separately installed
  Python engine and a versioned ZIP built by scripts/build_skill.py.

## 0.2.0 — 2026-10-06

- Public browser demo: sample, real server update, and local comparison of custom catalogs.
- The browser runs the same Python comparison engine through pinned Pyodide 0.29.3.
- Captured official Filesystem Server catalogs, provenance and a real minItems regression.
- Less noise for boolean additional-property policy changes and implicit zero cardinalities.
- Package renamed to `mcp-tooldelta`, module to `mcp_tooldelta`, CLI to `mcp-tooldelta`
  because the PyPI name `tooldelta` belongs to a different project.
- GitHub Pages deployment, live-browser regression checks and downloadable release artifacts.

Upgrading from the local 0.1 package: use a fresh virtual environment and the
new command/module names. Repository URLs and JSON report schema v1 are unchanged.

## 0.1.0 — 2026-10-06

Initial alpha, prepared locally; not published to PyPI.

- Offline diffs for arrays, tools objects and complete JSON-RPC tools/list results.
- Directional input/output compatibility checks and conservative review findings.
- Text, JSON, Markdown and interactive self-contained HTML reports.
- Normalized baselines, deterministic SHA-256 fingerprints and CI exit gates.
- Bundled demo, strict JSON loading, limits and input overwrite protection.
- English and Russian docs, regression tests and GitHub Actions configuration.
