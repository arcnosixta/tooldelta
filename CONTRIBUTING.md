# Contributing

Help ToolDelta explain real MCP contract drift with less noise. A small,
sanitized pair of catalogs is more useful than a broad feature request.

## Local development

Python 3.11+ is required. The runtime and unit tests use only the standard library.

```sh
python -m unittest discover -v
python -m tooldelta demo --format html -o reports/demo.html --fail-on none
```

To test distribution artifacts:

```sh
python -m pip install build
python -m build
python -m pip install --force-reinstall dist/tooldelta-0.1.0-py3-none-any.whl
python -I -m tooldelta demo --fail-on none
```

`-I` excludes the checkout from import resolution, so the smoke test actually
checks the installed package and its bundled examples/templates.

## Optional browser verification

```sh
python -m pip install . playwright
python -m playwright install chromium
python scripts/check_report.py
```

To use an existing Windows Edge installation:

```powershell
python scripts/check_report.py --browser-path "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
```

The check covers filters, search, expanded values, downloaded JSON, mobile
overflow, untrusted HTML strings, empty catalogs, JavaScript errors and external
requests. Use `--screenshot docs/assets/report.png` to refresh the README image.
Playwright and the build frontend are development-only dependencies.

## Good first contributions

- Add a sanitized fixture that exposes a noisy or missing comparison.
- Improve a finding's next step with a concrete migration example.
- Document collecting a complete tools/list catalog in an existing MCP client.
- Propose a well-bounded schema rule and show both input and output directions.

Keep production code dependency-free and offline. Keep unsupported semantics
visible as review findings. Preserve stable report sorting. Do not silently
discard unknown keywords or start a server to inspect a catalog. For new rules,
add meaningful regression tests and update docs/CONTRACTS.md.

Use a focused pull request: the observed problem, resulting behavior, and checks
performed. Commit messages may be English or Russian. Report security issues
using the process in [SECURITY.md](SECURITY.md).
