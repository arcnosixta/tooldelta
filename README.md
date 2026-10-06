# ToolDelta

**See what an MCP update will break before your agent finds out.**

An offline MCP contract diff for code reviews and CI. Compare saved `tools/list`
catalogs, understand incompatible changes, and review declared capability drift.

[Русский](README.ru.md) · [Compatibility rules](docs/CONTRACTS.md) ·
[Sample report](docs/assets/demo.md) · [Contributing](CONTRIBUTING.md)

![ToolDelta interactive report: 4 breaking, 3 review, 3 informational changes](docs/assets/report.png)

**Zero runtime dependencies · Python 3.11+ · Windows / macOS / Linux · MIT**

## Try it in 30 seconds

From this checkout, no install or network access needed:

```sh
python -m tooldelta demo
python -m tooldelta demo --format html -o reports/demo.html --fail-on none
```

Open `reports/demo.html` in your browser. Or open the ready-made
[docs/assets/demo.html](docs/assets/demo.html) locally after cloning.
The HTML report has filters, search, expandable before/after values, and JSON export.
It loads no fonts, scripts, analytics, or other external resources.

The demo intentionally exits **1** with the default gate. It catches:

```text
4 breaking | 3 review | 3 info

[BREAKING] list_projects removed
[BREAKING] search_documents: limit maximum 100 -> 25
[BREAKING] search_documents: workspace_id is now required
[BREAKING] search_documents: response enum added "partial"
[REVIEW]   read_file: readOnlyHint true -> false
[REVIEW]   read_file: destructiveHint false -> true
[REVIEW]   read_file: description changed
```

## Why ToolDelta?

A server update can keep the same tool name while requiring another argument,
tightening a limit, or returning a new enum value your agent cannot handle.
Plain JSON diffs bury those changes in formatting. ToolDelta groups them by
compatibility impact and tells a reviewer what to update.

- **Directional checks.** Narrower inputs can reject existing calls. Wider outputs
  can violate an existing consumer's contract. Both directions are checked.
- **Explicit uncertainty.** `$ref`, composition, pattern and other unsupported
  semantics are marked for review, even when unchanged.
- **Reproducible reports.** Stable sorting, SHA-256 catalog identities, no timestamps.
- **Local by construction.** Reads JSON only. Never starts a server, makes a tool
  call, resolves references, or sends a catalog anywhere.

ToolDelta is an alpha contract-review tool. Findings describe local schema changes;
they are not a proof of complete compatibility or a security verdict. Server
annotations are untrusted hints, not enforced permissions.

## Install from source

```sh
python -m pip install .
tooldelta --version
```

Or use `python -m tooldelta` directly in the checkout. Installation may download
the build backend; running ToolDelta has no network requirements. The package has
not been published to PyPI; do not assume a similarly named package is this project.

## Compare your own tools

Save the complete `tools/list` result from your existing MCP client or integration
test before and after a server change. ToolDelta does not collect it for you.
Merge paginated responses into one catalog: partial results with `nextCursor`
are rejected. Compare one server at a time; names must be unique within a catalog.

```sh
tooldelta snapshot captured-tools.json -o baseline.json
tooldelta diff baseline.json candidate.json
tooldelta diff baseline.json candidate.json --format markdown -o reports/review.md
tooldelta diff baseline.json candidate.json --format json --fail-on review
tooldelta diff baseline.json candidate.json --format html -o reports/review.html
```

Accepted JSON forms: `[{tool}, ...]`, `{"tools": [...]}`, and the JSON-RPC envelope
`{"jsonrpc":"2.0","result":{"tools":[...]}}`. Input and optional output schemas
must be object schemas with `"type": "object"` at their root, as specified by MCP.
Nested boolean schemas are supported. UTF-8 (including BOM), up to 8 MiB and
64 nesting levels per input. Duplicate keys and names are errors.

Reports contain catalog metadata and before/after values. Inspect them before
sharing: descriptions, examples and defaults may themselves contain sensitive data.
Existing outputs require `--force` to replace; input catalogs cannot be overwritten.

## CI gates

| Exit | Meaning |
| --- | --- |
| `0` | No finding reached the selected threshold |
| `1` | Findings reached the selected threshold; report is still produced |
| `2` | Invalid input, missing file, or report write error |

Default `--fail-on review` blocks both breaking changes and unresolved review items.
Use `--fail-on breaking` to allow review findings, `--fail-on info` to block any
reported item, or `--fail-on none` to only generate a report. Unsupported constructs
remain review findings even in identical catalogs. Thresholds change the exit code,
not the contents of the report. `argparse` usage errors also exit 2.

In a pipeline where ToolDelta is already installed from a trusted source:

```sh
tooldelta diff baseline.json candidate.json --format markdown -o reports/review.md
```

The gate fails on relevant changes. Configure your artifact upload step to run even
when the gate fails so reviewers can read the report. A full integration example
is in [docs/CI.md](docs/CI.md).

## Python API

```python
from tooldelta.catalog import load_catalog
from tooldelta.diff import compare

old = load_catalog("baseline.json")
new = load_catalog("candidate.json")
report = compare({"tools": list(old.values())}, {"tools": list(new.values())})
print(report.counts)
print(report.to_dict())
```

The API does not mutate inputs. `schema_version: 1` identifies the JSON report
shape. Catalogs are hashed with tool and object keys sorted; array order is retained.
Moving tools or reformatting JSON does not change their hash. Reordering an enum
may change the hash while leaving compatibility findings unchanged.

## Develop

```sh
python -m unittest discover -v
python -m pip install build
python -m build
```

Optional browser checks use Playwright, a development dependency:

```sh
python -m pip install . playwright
python -m playwright install chromium
python scripts/check_report.py
```

CI is configured to run tests and installed-package smoke checks on Windows,
macOS and Linux with Python 3.11 and 3.14, plus build and browser checks on Linux.
Only Windows / Python 3.12 / Edge has been verified locally so far.

## Scope and next steps

See [the exact rules and limitations](docs/CONTRACTS.md). Composite schemas,
reference resolution, runtime behavior, output data validation and prompt-injection
detection are outside this release. Contradictory or redundant constraints can
produce conservative false positives; no-change results do not prove safety.

Next priorities: real-world catalog fixtures, fewer redundant findings, and
well-specified multi-server reports. Propose a sanitized failing case in an issue.
If ToolDelta helps your reviews, a star makes the project easier to discover.

[Market research, in Russian](docs/MARKET.ru.md) records the original hypothesis and
competitors, including MCP Sentinel and Snyk Agent Scan. We do not claim that
offline diffing proves safety, or that this project will earn a particular number of stars.
