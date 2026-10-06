# Local validation — 2026-10-06

Verified on Windows with Python 3.12.10. These are local results, not a claim
that hosted CI has already run.

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
and for build/browser checks on Linux with Python 3.12. Those hosted checks are
pending the first push to a public or private remote.

See [CONTRIBUTING.md](../CONTRIBUTING.md) for repeatable commands. Development
dependencies (`build`, Playwright) live in the local ignored `.venv`; the package
declares no runtime dependencies. Built distributions live in ignored `dist/`.
