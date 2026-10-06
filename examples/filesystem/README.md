# A real MCP Filesystem Server contract update

Captured from the official
[`@modelcontextprotocol/server-filesystem`](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem)
package on 2026-10-06. These are actual `tools/list` responses, not handcrafted
tool schemas. Compare the saved snapshots offline:

```sh
python -m mcp_mcp-tooldelta diff examples/filesystem/2025.1.14.json examples/filesystem/2026.8.31.json
```

Result with ToolDelta's supported rules: **1 breaking, 45 review, 41 info**.
The counts include metadata, hints and unsupported semantics; they are not a
count of vulnerabilities. [Full report](report.md).

## The concrete compatibility change

`read_multiple_files.inputSchema.properties.paths` gained `minItems: 1`.
The baseline schema accepts an empty array; the candidate schema requires at
least one path. An existing caller that emits `{"paths": []}` no longer satisfies
the declared input contract. This was established from metadata; no file-reading
tool was called to test runtime behavior.

The catalog also grew from 11 to 14 tools, adding `read_text_file`,
`read_media_file` and `list_directory_with_sizes`. New declared behavior hints,
structured output schemas and changed descriptions deserve review. None of this
demonstrates malicious intent, a server vulnerability, or an actual permission
change. A compatibility change can be intentional and reasonable.

## Capture provenance and dependencies

[provenance.json](provenance.json) records exact package versions, upstream git
commits, npm tarball integrity strings, schema-related dependency versions,
protocol versions and SHA-256 hashes of the saved files. The capture used Node
24.21.0 and an empty allowed workspace. It sent `initialize`,
`notifications/initialized` and `tools/list`, including pagination handling.
It never sent `tools/call` or granted access to personal directories.

The old package does not declare its directly imported Zod version. A fresh
install with current peer resolution hoisted Zod 4.6.5 with zod-to-json-schema
3.25.2, producing mostly incomplete input schemas. That unmodified capture is
preserved as [2025.1.14-unpinned.json](2025.1.14-unpinned.json); ToolDelta rejects
it because the root object type is missing. This is not the comparison baseline.

To obtain a meaningful legacy baseline, Zod **3.23.8** and zod-to-json-schema
**3.23.5** were explicitly pinned in its separate installation. The server
package and its code were not edited. This dependency choice is part of the
reproduction, not a claim about what all current vanilla installations emit.

## Reproduce manually

With Node/npm installed, in separate development directories:

```sh
npm install --prefix reports/fs-old --ignore-scripts --no-audit --no-fund @modelcontextprotocol/server-filesystem@2025.1.14 zod@3.23.8 zod-to-json-schema@3.23.5
npm install --prefix reports/fs-new --ignore-scripts --no-audit --no-fund @modelcontextprotocol/server-filesystem@2026.8.31
```

Create an empty directory `reports/fixture-workspace`. Then run the explicitly
selected servers through the opt-in development capture script:

```sh
python scripts/capture_mcp_catalog.py --output reports/old.json -- node reports/fs-old/node_modules/@modelcontextprotocol/server-filesystem/dist/index.js reports/fixture-workspace
python scripts/capture_mcp_catalog.py --output reports/new.json -- node reports/fs-new/node_modules/@modelcontextprotocol/server-filesystem/dist/index.js reports/fixture-workspace
python -m mcp_mcp-tooldelta diff reports/old.json reports/new.json
```

Future transitive resolutions may differ; check the provenance dependency
versions if reproducing. Saved fixtures and the regression tests require no
Node, npm, server execution, or network access.

## Attribution

Tool names, descriptions and schemas originate from the MCP servers project.
The original upstream license notices for the corresponding commits are
preserved as [LICENSE-2025.txt](LICENSE-2025.txt) and
[LICENSE-2026.txt](LICENSE-2026.txt). These third-party metadata fixtures retain
their upstream notices; ToolDelta's own code is MIT licensed. No affiliation
with or endorsement by the upstream authors is implied.
