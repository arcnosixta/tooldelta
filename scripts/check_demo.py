"""Verify the public demo, including the actual WASM Python comparison engine."""

from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parent.parent


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def check():
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser-path")
    parser.add_argument("--screenshot", type=Path)
    parser.add_argument("--record", type=Path)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT / "build/demo")))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f"http://127.0.0.1:{server.server_port}"
    try:
        with sync_playwright() as p:
            options = {"headless": True}
            if args.browser_path:
                options["executable_path"] = args.browser_path
            browser = p.chromium.launch(**options)
            context_options = {"viewport": {"width": 1360, "height": 1060}, "accept_downloads": True}
            if args.record:
                args.record.mkdir(parents=True, exist_ok=True)
                context_options["record_video_dir"] = str(args.record)
                context_options["record_video_size"] = {"width": 1360, "height": 1060}
            context = browser.new_context(**context_options)
            page = context.new_page()
            errors, requests = [], []
            page.on("pageerror", lambda e: errors.append(str(e)))
            context.on("request", lambda req: requests.append((req.method, req.url)))
            page.goto(origin)
            report = page.frame_locator("#report")
            expect(report.locator("#breaking-count")).to_have_text("4")
            if args.screenshot:
                args.screenshot.parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(args.screenshot))
            page.get_by_role("button", name="Real server update").click()
            expect(report.locator("#before-label")).to_have_text("Filesystem 2025.1.14")
            page.get_by_role("button", name="Compare your catalogs", exact=True).click()
            page.get_by_role("button", name="Use sample files").click()
            expect(page.locator("#status")).to_contain_text("Sample catalogs loaded")
            page.get_by_role("button", name="Compare catalogs", exact=True).click()
            expect(page.locator("#status")).to_contain_text("Comparison complete", timeout=120000)
            expect(report.locator("#breaking-count")).to_have_text("4")
            expect(report.locator(".change")).to_have_count(10)
            with page.expect_download() as event:
                page.get_by_role("button", name="Download JSON", exact=True).click()
            result = json.loads(Path(event.value.path()).read_text(encoding="utf-8"))
            assert result["summary"] == {"breaking": 4, "review": 3, "info": 3}, result["summary"]
            # Warm runtime: identical inputs must clear previous changes.
            fixture = ROOT / "tooldelta/examples/before.json"
            page.locator("#before-file").set_input_files(fixture)
            page.locator("#after-file").set_input_files(fixture)
            page.get_by_role("button", name="Compare catalogs", exact=True).click()
            expect(page.locator("#status")).to_contain_text("Comparison complete", timeout=30000)
            expect(report.locator(".empty")).to_contain_text("No changes detected")
            # Invalid catalogs should produce useful errors, not a false clean result.
            page.locator("#after-file").set_input_files({"name": "bad.json", "mimeType": "application/json", "buffer": b'{"tools":[],"tools":[]}'})
            page.get_by_role("button", name="Compare catalogs", exact=True).click()
            expect(page.locator("#error")).to_contain_text("Duplicate JSON object key", timeout=30000)
            page.locator("#after-file").set_input_files({"name": "huge.json", "mimeType": "application/json", "buffer": b' ' * (8 * 1024 * 1024 + 1)})
            page.get_by_role("button", name="Compare catalogs", exact=True).click()
            expect(page.locator("#error")).to_contain_text("at most 8 MiB")
            # Names and catalog strings are data, never HTML or Python code.
            attack = '</script><script>window.__attacked=1</script>'
            malicious = json.dumps({"tools": [{"name": attack, "inputSchema": {"type": "object"}}]}).encode()
            page.locator("#before-file").set_input_files({"name": "empty.json", "mimeType": "application/json", "buffer": b'[]'})
            page.locator("#after-file").set_input_files({"name": "untrusted.json", "mimeType": "application/json", "buffer": malicious})
            page.get_by_role("button", name="Compare catalogs", exact=True).click()
            expect(page.locator("#status")).to_contain_text("Comparison complete", timeout=30000)
            expect(report.locator(".tool-name")).to_have_text(attack)
            assert page.evaluate("window.__attacked===undefined")
            page.set_viewport_size({"width": 390, "height": 844})
            assert page.evaluate("document.documentElement.scrollWidth<=innerWidth")
            assert not errors, errors
            assert all(method == "GET" for method, _ in requests), requests
            assert all(url.startswith((origin, "https://cdn.jsdelivr.net/pyodide/", "blob:", "about:")) for _, url in requests), requests
            context.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    print("Live demo passed: real Pyodide engine, shared counts, identical inputs, invalid JSON, size limit, untrusted content, mobile layout, no catalog uploads.")


if __name__ == "__main__":
    check()
