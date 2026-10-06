"""Record a short, real browser walkthrough for the project's release."""

import argparse
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import expect, sync_playwright

from check_demo import ROOT, QuietHandler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser-path")
    parser.add_argument("--output", type=Path, default=ROOT / "docs/assets/demo.webm")
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT / "build/demo")))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            options = {"headless": True}
            if args.browser_path:
                options["executable_path"] = args.browser_path
            browser = p.chromium.launch(**options)
            context = browser.new_context(viewport={"width": 1280, "height": 960},
                                          record_video_dir=str(ROOT / "reports/video"),
                                          record_video_size={"width": 1280, "height": 960})
            page = context.new_page()
            page.goto(f"http://127.0.0.1:{server.server_port}")
            frame = page.frame_locator("#report")
            expect(frame.locator("#breaking-count")).to_have_text("4")

            def caption(text, duration=3500):
                page.evaluate("""text => {
                    let node=document.getElementById('recording-caption');
                    if(!node){node=document.createElement('div');node.id='recording-caption';node.style.cssText='position:fixed;bottom:22px;left:50%;transform:translateX(-50%);max-width:90vw;padding:14px 22px;border:1px solid #5b7c65;border-radius:9px;background:#17261ff2;color:#d9fbe3;font:16px Segoe UI,system-ui;z-index:99999;text-align:center;box-shadow:0 8px 28px #0008';document.body.append(node);}
                    node.textContent=text;
                }""", text)
                page.wait_for_timeout(duration)

            caption("ToolDelta · review MCP contract changes before updating your agent")
            frame.get_by_role("button", name="Breaking", exact=True).click()
            frame.locator(".change").filter(has_text="workspace_id").locator("summary").click()
            caption("A new required argument can reject existing calls.")
            frame.get_by_role("button", name="Review", exact=True).click()
            frame.locator(".change").filter(has_text="readOnlyHint").locator("summary").click()
            caption("Declared behavior changed. Review the server's actual behavior.")
            page.get_by_role("button", name="Real server update").click()
            expect(frame.locator("#before-label")).to_have_text("Filesystem 2025.1.14")
            caption("Actual catalogs · MCP Filesystem Server 2025.1.14 → 2026.8.31")
            frame.get_by_role("button", name="Breaking", exact=True).click()
            frame.locator(".change summary").click()
            caption('paths: [] no longer satisfies the new minItems: 1 contract.', 4500)
            page.get_by_role("button", name="Compare your catalogs", exact=True).click()
            page.get_by_role("button", name="Use sample files").click()
            expect(page.locator("#status")).to_contain_text("Sample catalogs loaded")
            caption("Choose your own JSON catalogs. Their contents stay on your device.", 4000)
            page.get_by_role("button", name="Compare catalogs", exact=True).click()
            expect(page.locator("#status")).to_contain_text("Comparison complete", timeout=120000)
            caption("Same Python engine as the CLI. Try it without an account.", 4000)
            video = page.video
            context.close()
            args.output.parent.mkdir(parents=True, exist_ok=True)
            video.save_as(str(args.output))
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    print(f"Saved actual browser walkthrough: {args.output}")


if __name__ == "__main__":
    main()
