# Use ToolDelta in CI

Keep a reviewed baseline catalog in the repository. Produce a **complete**
candidate catalog in your own integration tests or existing MCP client. ToolDelta
does not start a server or fetch tools. Compare one server per invocation.

Install ToolDelta from a trusted reviewed source or built wheel. Until the public
repository and PyPI package are published, do not copy an assumed package name
or an invented action identifier into a workflow.

This example assumes your pipeline has already installed ToolDelta, produced
`candidate.json` and checked out `baseline.json`:

```yaml
- name: Review MCP drift
  run: >-
    python -m tooldelta diff baseline.json candidate.json
    --format markdown --output reports/review.md --fail-on review
- name: Upload the report even if the gate failed
  if: always()
  uses: actions/upload-artifact@b7c566a772e6b6bfb58ed0dc250532a479d7789f # v6
  with:
    name: mcp-contract-review
    path: reports/review.md
```

Run with `contents: read`; no issue-comment or other write token is needed.
Exit 1 blocks a change at the selected threshold while preserving the report.
Exit 2 is a data or I/O error and must also fail the job. Avoid `|| true` or
`continue-on-error` for a gate you intend to enforce.

For an HTML-only review artifact use `--format html`. Each invocation produces
one format. If generating several reports into reused paths, choose unique
filenames or explicitly use `--force`. The input files remain protected.

Update the baseline only after reviewing changes, migrations and relevant
integration tests. Treat it as a contract checkpoint, not a trusted server
signature. Hashes identify metadata, not running server code.

The project's own [.github/workflows/ci.yml](../.github/workflows/ci.yml) tests
Windows/macOS/Linux on Python 3.11 and 3.14. A separate Linux job builds artifacts
and runs real-browser report checks. Actions are pinned to upstream commit
hashes resolved on 2026-10-06; Dependabot is configured to propose updates.
