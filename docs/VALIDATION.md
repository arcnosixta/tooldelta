# Local validation — 2026-10-06

The initial 0.1 checks below were verified on Windows with Python 3.12.10.
Hosted CI has since passed on Linux, macOS and Windows with Python 3.11/3.14.

| Check | Result |
| --- | --- |
| `python -m unittest discover -v` | 29 tests passed |
| Bounds regression matrix | 40 directional checks inside one test passed |
| UTF-8 process output under `PYTHONIOENCODING=cp1251` | Russian + emoji JSON parsed correctly |
| CLI exit gates and protected writes | Passed |
| `python -m build` | sdist and wheel built successfully; wheel built from sdist |
| Install `dist/tooldelta-0.1.0-py3-none-any.whl` | Passed in local .venv |
| `python -I -m tooldelta demo` with JSON/HTML output | Installed package and bundled assets worked |
| Installed `tooldelta` entry point | Passed |
| Real-browser report test in headless Edge | Passed |
| Filters, search, expanded changes, downloaded JSON | Passed |
| 390px mobile viewport and long untrusted tool names | No horizontal page overflow |
| HTML script-injection fixture and empty report | Passed; no injected script execution |
| Browser JavaScript errors / HTTP(S) requests during report check | None |

The demo reports 4 breaking, 3 review and 3 info findings. Its default exit 1 is
intentional. Use `--fail-on none` to render an artifact without failing the gate.

GitHub Actions is configured for Python 3.11 / 3.14 on Linux, macOS and Windows,
and for build/browser checks on Linux with Python 3.12. The first hosted run was
triggered by publishing [arcnosixta/tooldelta](https://github.com/arcnosixta/tooldelta).
Current results are available in [GitHub Actions](https://github.com/arcnosixta/tooldelta/actions/workflows/ci.yml).

See [CONTRIBUTING.md](../CONTRIBUTING.md) for repeatable commands. Development
dependencies (`build`, Playwright) live in the local ignored `.venv`; the package
declares no runtime dependencies. Built distributions live in ignored `dist/`.

## Version 0.2 validation

- 33 Python tests, including captured real MCP metadata and noise regressions, passed.
- Real browser-worker comparison matches CLI results (4 breaking / 3 review / 3 info).
- Repeated identical inputs, duplicate-key errors, 8 MiB limit, malicious strings
  and 390px layout passed in headless Edge.
- Full browser-context HTTP(S) traffic consists only of static GET requests to
  the demo and pinned Pyodide assets; no catalog uploads.
- PyPI naming conflict checked: new distribution `mcp-tooldelta`, module `mcp_tooldelta`.
- New wheel verified to contain the new namespace and templates/examples without
  the legacy tooldelta namespace; installed without dependencies in a clean venv.
- Isolated `python -I -m mcp_tooldelta` and `mcp-tooldelta` console entry point passed.
- Public GitHub Pages deployment succeeded and returned HTTP 200.

The preceding commands using `tooldelta` describe historical version 0.1.
Use the 0.2 names in the current README. Latest hosted CI results are linked above.

## Version 0.2.1 release preparation — 2026-10-10

- Previous skill/fix commit `08759b0`: hosted
  [CI](https://github.com/arcnosixta/tooldelta/actions/runs/38033755179) and
  [Public demo](https://github.com/arcnosixta/tooldelta/actions/runs/38033755223)
  both completed successfully.
- 36 Python unit/CLI tests passed locally on Windows / Python 3.12.
- Wheel and sdist built successfully; the wheel was built from the sdist.
- The wheel installed with `--no-deps --no-index` into a fresh virtual environment.
  Isolated `python -I -m mcp_tooldelta` reported 0.2.1 and produced the expected
  JSON demo counts and HTML report; the console entry point also reported 0.2.1.
- The wheel declares no runtime dependencies and contains no legacy namespace.
- The sdist includes the skill source; the standalone versioned ZIP contains
  exactly SKILL.md and the MIT license. Two builds produced identical ZIP bytes.
- Both headless Edge checks passed: standalone report behavior and live Pyodide
  comparison, including downloads, invalid JSON, limits, mobile layout, malicious
  catalog strings, and absence of catalog uploads.

These are preparation checks, not a claim that 0.2.1 is publicly released.
