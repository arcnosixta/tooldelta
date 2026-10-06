# Security policy

ToolDelta 0.1.x is alpha software. It inspects saved JSON metadata only, does not
execute MCP tools, and does not certify safety. Its HTML and JSON reports can
contain sensitive values present in a catalog. Review them before sharing.

Input files should be treated as untrusted. Maintain size and depth limits,
duplicate-key rejection, safe HTML payload embedding, and textContent-based DOM
rendering. Never introduce automatic reference fetching or server execution.

For vulnerabilities in ToolDelta (for example HTML script execution), use GitHub
private vulnerability reporting once the repository owner enables it. If no
private channel is available, open an issue requesting one without publishing
secrets or exploit details. There is no project-specific private inbox yet.
Do not file a public issue containing a real credential or a confidential catalog.

The owner should enable private reporting before promoting the public release.
