"""Optional real-browser verification; Playwright is a development-only dependency."""

import argparse
import json
from pathlib import Path
import tempfile

from playwright.sync_api import expect, sync_playwright

from tooldelta.cli import main
from tooldelta.diff import compare
from tooldelta.render import render


def check():
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser-path", help="Use a local Chromium/Edge executable")
    parser.add_argument("--screenshot", type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as directory, sync_playwright() as playwright:
        root = Path(directory)
        demo = root / "demo.html"
        assert main(["demo", "--format", "html", "-o", str(demo), "--fail-on", "none"]) == 0
        options = {"headless": True}
        if args.browser_path:
            options["executable_path"] = args.browser_path
        browser = playwright.chromium.launch(**options)
        page = browser.new_page(viewport={"width": 1360, "height": 1060}, device_scale_factor=1)
        errors, network = [], []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("request", lambda request: network.append(request.url) if request.url.startswith(("http:", "https:")) else None)
        page.goto(demo.as_uri())
        expect(page.locator(".change")).to_have_count(10)
        expect(page.locator("#breaking-count")).to_have_text("4")
        if args.screenshot:
            args.screenshot.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(args.screenshot))
        page.get_by_role("button", name="Breaking", exact=True).click()
        expect(page.locator(".change")).to_have_count(4)
        page.get_by_role("button", name="Review", exact=True).click()
        expect(page.locator(".change")).to_have_count(3)
        page.get_by_role("button", name="All changes", exact=True).click()
        page.get_by_role("searchbox").fill("workspace_id")
        expect(page.locator(".change")).to_have_count(2)
        page.get_by_role("searchbox").fill("no-such-tool")
        expect(page.locator(".empty")).to_have_text("No changes match these filters.")
        page.get_by_role("searchbox").fill("")
        page.locator(".change summary").first.click()
        expect(page.locator(".change[open] .action")).to_be_visible()
        with page.expect_download() as event:
            page.get_by_role("button", name="Export report as JSON").click()
        download_path = root / "download.json"
        event.value.save_as(download_path)
        assert json.loads(download_path.read_text(encoding="utf-8"))["summary"]["breaking"] == 4
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        attack = '</script><script>window.__attacked = 1</script><img src="https://example.invalid/x">'
        malicious = root / "untrusted.html"
        malicious.write_text(render(compare([], [{"name": attack, "inputSchema": {"type": "object"}}]), "html", attack, attack), encoding="utf-8")
        page.goto(malicious.as_uri())
        expect(page.locator(".tool-name")).to_have_text(attack)
        assert page.evaluate("window.__attacked === undefined")
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        empty = root / "empty.html"
        empty.write_text(render(compare([], []), "html"), encoding="utf-8")
        page.goto(empty.as_uri())
        expect(page.locator(".empty")).to_have_text("No changes detected in the supported contract subset.")
        assert not errors, errors
        assert not network, network
        browser.close()
    print("Browser checks passed: filters, search, details, download, mobile layout, untrusted strings, empty state, no network.")


if __name__ == "__main__":
    check()
