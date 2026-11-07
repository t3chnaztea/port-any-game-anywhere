#!/usr/bin/env python3
"""Normal-input browser checks of the pinned Fifteen reproduction, not device acceptance."""
import argparse
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import json
from pathlib import Path
import threading
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=ROOT / ".work/fifteen/site")
    parser.add_argument("--chrome", default="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    args = parser.parse_args()
    from playwright.sync_api import sync_playwright
    if not (args.site / "fifteen.wasm").is_file():
        parser.exit(2, "BLOCKED: build the pinned browser target first\n")
    output = ROOT / ".work/fifteen-browser"
    output.mkdir(parents=True, exist_ok=True)
    report = {"status": "running", "checks": [], "evidence_class": "automated-gameplay",
              "limitations": ["not a native-reference comparison", "not actual iPhone acceptance", "not a full51-claim acceptance"]}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    server = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(args.site)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=args.chrome, headless=True)
            page = browser.new_page(viewport={"width": 1000, "height": 900})
            page.set_default_timeout(5000)
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            base = f"http://127.0.0.1:{server.server_port}/fifteen.html"
            game_id = "4x4:1,2,3,4,5,6,7,8,9,10,11,12,13,14,0,15"
            def load(identifier=game_id):
                # A fragment-only goto does not restart the upstream WASM main.
                # Its source consumes the game ID only during document startup.
                page.goto("about:blank")
                page.goto(base + "#" + quote(identifier, safe=":,"))
                page.locator("#puzzle").wait_for(state="visible")
                page.locator("#puzzlecanvas").focus()
            def status(expected):
                try:
                    page.wait_for_function("text => document.querySelector('#statusbar').textContent === text", arg=expected)
                except Exception:
                    report["status_mismatch"] = {"expected": expected, "observed": page.locator("#statusbar").inner_text()}
                    raise
            def menu():
                page.locator("#gamemenu > ul > li > div").first.hover()
            def save_text():
                menu()
                page.locator("#save").click()
                link = page.locator("#dlgform a[download]")
                value = link.get_attribute("href").split(",", 1)[1]
                from urllib.parse import unquote
                text = unquote(value)
                page.locator("#dlgform input[value='OK']").click()
                return text
            load()
            status("Moves: 0")
            page.keyboard.press("ArrowLeft")
            status("COMPLETED! Moves: 1")
            page.screenshot(path=str(output / "completed.png"), full_page=True)
            page.locator("#undo").click()
            status("Moves: 0")
            page.locator("#redo").click()
            status("COMPLETED! Moves: 1")
            report["checks"].append("fixed game ID: keyboard completion, undo and redo")
            load("4x4:1,2,3,4,5,6,7,8,9,10,11,12,13,0,14,15")
            box = page.locator("#puzzlecanvas").bounding_box()
            # The source defines border=tile/2 and a4x4 grid within a5tile canvas.
            page.mouse.click(box["x"] + box["width"] * .8, box["y"] + box["height"] * .8)
            status("COMPLETED! Moves: 2")
            report["checks"].append("normal pointer: aligned row moves two tiles")
            load()
            for key in ["ArrowRight", "ArrowDown", "ArrowLeft"]:
                page.keyboard.press(key)
            status("Moves: 3")
            page.locator("#undo").click()
            status("Moves: 2")
            before = save_text()
            assert "STATEPOS" in before and "NSTATES" in before
            saved = output / "pending-redo.sav"
            saved.write_text(before)
            page.reload()
            page.locator("#puzzle").wait_for(state="visible")
            menu()
            with page.expect_file_chooser() as pending:
                page.locator("#load").click()
            pending.value.set_files(str(saved))
            status("Moves: 2")
            page.locator("#redo").click()
            status("Moves: 3")
            page.locator("#undo").click()
            status("Moves: 2")
            assert save_text() == before
            report["checks"].append("cold page load: full save including pending redo round-trips byte for byte")
            assert not errors, errors
            report.update(status="passed", browser=browser.version,
                          artifacts={name: hashlib.sha256((args.site / name).read_bytes()).hexdigest()
                                     for name in ["fifteen.html", "fifteen.js", "fifteen.wasm"]})
            browser.close()
    except BaseException as exc:
        report.update(status="interrupted" if isinstance(exc, KeyboardInterrupt) else "failed", error=str(exc))
        raise
    finally:
        (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        server.shutdown()
        server.server_close()
    print(f"PASS: {len(report['checks'])} Fifteen browser routes (full device acceptance remains open)")

if __name__ == "__main__":
    main()
