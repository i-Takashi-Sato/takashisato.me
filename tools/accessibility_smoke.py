#!/usr/bin/env python3
"""Automated WCAG smoke audit for the public research archive.

Runs axe-core against every primary public route at representative mobile and
desktop widths. Critical/serious violations and browser page errors block CI;
moderate/minor findings are printed for review without creating false precision.
"""
from __future__ import annotations

import os
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = os.environ.get("QUALITY_BASE_URL", "http://127.0.0.1:4173")
AXE = Path(os.environ.get("AXE_PATH", "node_modules/axe-core/axe.min.js"))
PAGES = {
    "home": "/",
    "papers": "/papers/",
    "author": "/about.html",
    "part1": "/papers/part1.html",
    "part2": "/papers/part2.html",
    "part3": "/papers/part3.html",
}
VIEWPORTS = {
    "mobile": (390, 844),
    "desktop": (1440, 900),
}
WCAG_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]
BLOCKING_IMPACTS = {"critical", "serious"}


def main() -> int:
    if not AXE.exists():
        raise SystemExit(f"axe-core payload not found: {AXE}")

    blocking: list[str] = []
    advisory: list[str] = []
    page_errors: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", args=["--no-sandbox", "--disable-dev-shm-usage"])
        for viewport_name, (width, height) in VIEWPORTS.items():
            context = browser.new_context(
                viewport={"width": width, "height": height},
                reduced_motion="reduce",
            )
            page = context.new_page()
            current = {"name": ""}

            def record_page_error(exc) -> None:
                page_errors.append(f"{current['name']}@{viewport_name}: {exc}")

            page.on("pageerror", record_page_error)
            for name, path in PAGES.items():
                current["name"] = name
                page.goto(BASE + path, wait_until="networkidle")
                page.locator("main").wait_for(state="visible")
                page.add_script_tag(path=str(AXE))
                result = page.evaluate(
                    """async (tags) => await axe.run(document, {
                      runOnly: {type: 'tag', values: tags},
                      resultTypes: ['violations']
                    })""",
                    WCAG_TAGS,
                )
                for violation in result.get("violations", []):
                    nodes = violation.get("nodes", [])
                    targets = [" > ".join(node.get("target", [])) for node in nodes[:4]]
                    detail = (
                        f"{name}@{viewport_name}: {violation.get('id')} "
                        f"[{violation.get('impact')}] {violation.get('help')} "
                        f"targets={targets}"
                    )
                    if violation.get("impact") in BLOCKING_IMPACTS:
                        blocking.append(detail)
                    else:
                        advisory.append(detail)
            context.close()
        browser.close()

    if advisory:
        print("Axe advisory findings:")
        for item in advisory:
            print(f"- {item}")
    if page_errors:
        print("Browser page errors:")
        for item in page_errors:
            print(f"- {item}")
        blocking.extend(page_errors)
    if blocking:
        print(f"Accessibility gate failed with {len(blocking)} blocking finding(s):")
        for item in blocking:
            print(f"- {item}")
        return 1

    print(f"Accessibility gate passed: {len(PAGES) * len(VIEWPORTS)} axe audits, no serious/critical WCAG violations or page errors.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
