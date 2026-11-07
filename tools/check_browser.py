#!/usr/bin/env python3
"""Run browser fixtures through the normal UI. This is not iPhone acceptance."""
import argparse
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chrome", default="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    args = parser.parse_args()
    output = ROOT / ".work/browser"
    output.mkdir(parents=True, exist_ok=True)
    (output / "report.json").write_text(json.dumps({"status": "pending", "checks": [], "limitations": ["no device acceptance"]}) + "\n")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        parser.exit(2, "BLOCKED: Playwright is not installed; no browser was downloaded\n")
    site = ROOT / ".work/switchboard/site"
    if not (site / "app.js").is_file():
        parser.exit(2, "BLOCKED: build the example first\n")
    server = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(QuietHandler, directory=str(site)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    checks = []
    try:
        with sync_playwright() as p:
            launch = {"headless": True}
            if Path(args.chrome).is_file():
                launch["executable_path"] = args.chrome
            browser = p.chromium.launch(**launch)
            page = browser.new_page(viewport={"width": 1280, "height": 1000})
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            url = f"http://127.0.0.1:{server.server_port}"
            page.goto(url)
            page.get_by_role("button", name="Start campaign").click()
            page.keyboard.press("ArrowRight")
            assert page.locator("#door-state").inner_text() == "Door open"
            page.get_by_role("button", name="Save in browser").click()
            for _ in range(3):
                page.keyboard.press("ArrowRight")
            assert "Board complete" in page.locator("#status").inner_text()
            page.get_by_role("button", name="Load saved game").click()
            assert page.locator("#moves").inner_text() == "1"
            page.get_by_role("button", name="Undo", exact=True).click()
            assert page.locator("#moves").inner_text() == "0"
            assert page.locator("#door-state").inner_text() == "Door closed"
            checks.append("normal UI completion, save/load and undo")
            page.get_by_role("button", name="Start campaign").click()
            routes = json.loads((ROOT / "examples/recovery-puzzle/routes.json").read_text())["routes"]
            for route in routes:
                for action in route["actions"]:
                    page.keyboard.press("Arrow" + action.title())
                if route["board"] < 6:
                    assert "Board complete" in page.locator("#status").inner_text()
                    page.get_by_role("button", name="Next board", exact=True).click()
            assert "Campaign complete" in page.locator("#status").inner_text()
            checks.append("normal UI: all six campaign routes and final transition")
            page.get_by_role("button", name="Start campaign").click()
            page.get_by_role("button", name="Switch, column 3, row 2", exact=True).click()
            assert page.locator("#moves").inner_text() == "1"
            with page.expect_download() as pending:
                page.get_by_role("button", name="Export save", exact=True).click()
            pending.value.save_as(str(output / "exported-save.txt"))
            page.keyboard.press("ArrowRight")
            page.locator("#import").set_input_files(str(output / "exported-save.txt"))
            page.wait_for_function("document.querySelector('#moves').textContent === '1'")
            page.get_by_role("button", name="Undo", exact=True).click()
            assert page.locator("#moves").inner_text() == "0"
            checks.append("normal UI: adjacent pointer action and export/import with undo")
            previous = page.evaluate("localStorage.getItem('paga.switchboard.v1')")
            page.evaluate("""() => { window.realSet = Storage.prototype.setItem;
                Storage.prototype.setItem = function(k,v) { if(k==='paga.switchboard.v1') throw new DOMException('full','QuotaExceededError'); return window.realSet.call(this,k,v); }; }""")
            page.get_by_role("button", name="Save in browser").click()
            assert "previous save is preserved" in page.locator("#status").inner_text()
            assert page.evaluate("localStorage.getItem('paga.switchboard.v1')") == previous
            page.evaluate("() => { Storage.prototype.setItem = window.realSet; }")
            checks.append("fixture: quota error preserves previous save")
            page.evaluate("localStorage.setItem('paga.switchboard.v1','damaged')")
            page.get_by_role("button", name="Load saved game").click()
            assert "current game is unchanged" in page.locator("#status").inner_text()
            assert page.locator("#moves").inner_text() == "0"
            checks.append("fixture: damaged browser save rejected")
            page.get_by_role("button", name="Start campaign").click()
            page.keyboard.press("ArrowRight")
            page.screenshot(path=str(output / "desktop.png"), full_page=True)
            context = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
            mobile = context.new_page()
            mobile.goto(url)
            mobile.get_by_role("button", name="Start campaign").tap()
            mobile.get_by_role("button", name="Move right", exact=True).tap()
            assert mobile.locator("#moves").inner_text() == "1"
            assert mobile.evaluate("document.documentElement.scrollWidth <= innerWidth")
            mobile.screenshot(path=str(output / "touch-emulation.png"), full_page=True)
            checks.append("touch emulation: normal button input and no horizontal overflow")
            for key in ("#save", "#load", "#export", "#campaign"):
                assert mobile.locator(key).evaluate("e => e.getBoundingClientRect().height >= 44")
            assert not errors, errors
            report = {"status": "passed", "checks": checks, "browser": browser.version,
                      "evidence_class": "browser automation and controlled fixtures",
                      "limitations": ["touch emulation is not an actual iPhone", "audio was not reviewed by a listener", "not a blinded recovery result"]}
            (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    print(f"PASS: {len(checks)} browser checks (actual iPhone and listening gates remain open)")

if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        if isinstance(exc, SystemExit) and exc.code in (None, 0):
            raise
        target = ROOT / ".work/browser/report.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        status = "interrupted" if isinstance(exc, KeyboardInterrupt) else "blocked" if isinstance(exc, SystemExit) and exc.code == 2 else "failed"
        target.write_text(json.dumps({"status": status, "error": str(exc), "limitations": ["no device acceptance"]}, indent=2) + "\n")
        raise
