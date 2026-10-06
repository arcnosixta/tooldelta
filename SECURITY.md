# Security policy

ToolDelta 0.2.x is alpha software. It inspects saved JSON metadata only, does not
execute MCP tools, and does not certify safety. Its HTML and JSON reports can
contain sensitive values present in a catalog. Review them before sharing.

Input files should be treated as untrusted. Maintain size and depth limits,
duplicate-key rejection, safe HTML payload embedding, and textContent-based DOM
rendering. Never introduce automatic reference fetching or server execution.

For vulnerabilities in ToolDelta (for example HTML script execution), use
[GitHub private vulnerability reporting](https://github.com/arcnosixta/tooldelta/security/advisories/new),
which is enabled for this repository. There is no project-specific private inbox.
Do not file a public issue containing a real credential or a confidential catalog.

The browser demo downloads a pinned Pyodide runtime from jsDelivr and our source
engine from GitHub Pages. Catalog contents stay in browser memory and a temporary
WASM filesystem, cleaned after comparison. Downloaded reports may contain catalog
metadata. The separate opt-in development capture script launches only the server
command explicitly provided by its operator; the CLI comparator never launches servers.
