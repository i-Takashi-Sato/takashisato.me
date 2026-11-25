#!/usr/bin/env python3
"""Observe actual public-browser behavior, not just local HTML or HTTPS bytes."""
from pathlib import Path
from urllib.parse import urlsplit
import json
from playwright.sync_api import sync_playwright
from verify_live import SITE

PAGES = ("/", "/papers/", "/papers/part1.html", "/papers/part2.html",
         "/papers/part3.html", "/about.html")
OUT = Path("artifacts/public-browser")
ORIGIN = urlsplit(SITE).netloc

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    observations, errors = [], []
    with sync_playwright() as pw:
        for engine in ("chromium", "webkit", "firefox"):
            browser = getattr(pw, engine).launch()
            for width, height, js in ((390, 844, True), (1440, 900, True), (390, 844, False)):
                context = browser.new_context(viewport={"width": width, "height": height},
                    java_script_enabled=js, reduced_motion="reduce", service_workers="block")
                page = context.new_page()
                for index, path in enumerate(PAGES):
                    external, failures, exceptions, policies = set(), [], [], []
                    def request(req):
                        if urlsplit(req.url).scheme in ("http", "https") and urlsplit(req.url).netloc != ORIGIN:
                            external.add(urlsplit(req.url).netloc)
                    def response(res):
                        if res.status >= 400 and urlsplit(res.url).netloc == ORIGIN:
                            failures.append(f"{res.status} {urlsplit(res.url).path}")
                    def console(msg):
                        if msg.type == "error" and ("Content Security Policy" in msg.text or "CSP" in msg.text):
                            policies.append(msg.text[:300])
                    def page_error(exc):
                        exceptions.append(exc)
                    page.on("request", request)
                    page.on("response", response)
                    page.on("pageerror", page_error)
                    page.on("console", console)
                    tag = f"{engine}-{width}-{'js' if js else 'nojs'}-{index}"
                    try:
                        res = page.goto(SITE + path, wait_until="load", timeout=30000)
                        page.locator("main h1").wait_for(state="visible", timeout=10000)
                        page.evaluate("document.fonts.ready")
                        if res is None or res.status != 200 or urlsplit(page.url).path != path:
                            errors.append(f"{tag}: canonical navigation failed")
                        if page.evaluate("document.documentElement.scrollWidth > innerWidth + 1"):
                            errors.append(f"{tag}: horizontal overflow")
                        if path.startswith("/papers/part"):
                            page.locator('.paper-hero a[href="#abstract"]').click(timeout=5000)
                            if urlsplit(page.url).fragment != "abstract" or not page.locator("#abstract").is_visible():
                                errors.append(f"{tag}: abstract navigation failed")
                        if path == "/papers/":
                            page.locator('a[href="#japanese"]').click(timeout=5000)
                            if urlsplit(page.url).fragment != "japanese" or page.locator("#japanese .record-row").count() != 3:
                                errors.append(f"{tag}: Japanese navigation failed")
                        if width == 390 and js:
                            page.screenshot(path=str(OUT / (tag + ".png")))
                    except Exception as exc:
                        errors.append(f"{tag}: {type(exc).__name__}: {str(exc)[:200]}")
                    finally:
                        page.remove_listener("request", request)
                        page.remove_listener("response", response)
                        page.remove_listener("pageerror", page_error)
                        page.remove_listener("console", console)
                    cookies = [c["name"] for c in context.cookies()]
                    try:
                        storage = page.evaluate("() => ({local: Object.keys(localStorage), session: Object.keys(sessionStorage)})")
                    except Exception as exc:
                        storage = {"local": [], "session": [], "unavailable": True}
                        errors.append(f"{tag}: storage observation unavailable: {type(exc).__name__}")
                    record = {"case": tag, "path": path, "external_hosts": sorted(external),
                        "failed_responses": failures, "page_errors": [str(e)[:200] for e in exceptions],
                        "policy_errors": policies, "cookie_names": cookies, "storage_keys": storage}
                    observations.append(record)
                    if external or failures or exceptions or policies or storage["local"] or storage["session"]:
                        errors.append(f"{tag}: unexpected request, runtime failure, policy violation or browser storage")
                context.close()
            browser.close()
    report = {"scope": "54 public-browser cases; no external link navigation, physical devices or screen readers",
              "observations": observations, "errors": errors}
    (OUT / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(f"{len(observations)} public-browser cases; {len(errors)} findings")
    for error in errors:
        print(error)
    if errors:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
