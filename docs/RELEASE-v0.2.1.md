# ToolDelta 0.2.1 — additional-property fixes and an agent skill

Release preparation; these artifacts have not yet been published.

This patch fixes two cases where additionalProperties schemas produced no findings
and adds a portable skill for agents reviewing saved MCP tool catalogs.

## Changes

- Schema-valued additionalProperties is inspected even when unchanged. Unsupported
  keywords such as pattern and nested references now retain manual-review findings.
- Numeric and boolean values in additionalProperties const/enum are distinct:
  changing const: 1 to const: true is reported as potentially breaking.
  Equivalent numbers such as 1 and 1.0 still produce no compatibility finding.
- The mcp-tooldelta agent skill explains CLI setup, baseline/candidate direction,
  exit codes, migration actions, and the limits of static comparison.
- Three regression tests bring the Python suite to 36 tests.

JSON report schema v1 and CLI options are unchanged. CI using the default review
threshold can now fail on unsupported additional-property constraints that were
previously skipped. Inspect those findings before updating the baseline.

## Prepared artifacts

- `mcp_tooldelta-0.2.1-py3-none-any.whl` — Python engine and CLI.
- `mcp_tooldelta-0.2.1.tar.gz` — source distribution, including the skill source.
- `mcp-tooldelta-skill-0.2.1.zip` — skill instructions and MIT license; no engine.
- `SHA256SUMS-0.2.1.txt` — SHA-256 checksums of the three artifacts.

## Install and try

Use Python 3.11+ in your chosen environment. After downloading the wheel:

```sh
python -m pip install ./mcp_tooldelta-0.2.1-py3-none-any.whl
python -m mcp_tooldelta --version
python -m mcp_tooldelta demo --fail-on none
```

Extract the skill ZIP and install the mcp-tooldelta folder using your agent's
supported skill installation mechanism. Ensure the Python engine is available
in the environment used by that agent. Ask it to compare two complete saved
tools/list catalogs and explain breaking changes and unresolved review items.

The engine has zero runtime dependencies and compares catalogs offline.
This remains alpha software: unsupported semantics require review, annotations
are untrusted hints, and no findings is not proof of complete compatibility.

## Validation

36 Python tests passed. The wheel was built from the sdist and installed with
no dependencies into a clean environment; isolated JSON/HTML output and the
console entry point passed. Standalone report and live Pyodide checks passed
in headless Edge. The versioned skill ZIP was verified to be reproducible.
Details are recorded in [VALIDATION.md](VALIDATION.md).
