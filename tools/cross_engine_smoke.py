#!/usr/bin/env python3
"""Cross-engine layout and accessible reading checks; no device-specific claims."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from visual_smoke import BASE, PAGES, layout_errors

OUT = Path("artifacts/cross-engine")

def main():
    failures = []
    with sync_playwright() as pw:
        for name in ("webkit", "firefox"):
            browser = getattr(pw, name).launch()
            for width, height in ((320, 568), (390, 844), (768, 1024), (1440, 900)):
                ctx = browser.new_context(viewport={"width": width, "height": height}, has_touch=width < 768, reduced_motion="reduce")
                page = ctx.new_page()
                for key, path in PAGES.items():
                    page.goto(BASE + path, wait_until="networkidle")
                    page.locator("main").wait_for(state="visible")
                    page.evaluate("document.fonts.ready")
                    failures.extend(layout_errors(page, key, width, name))
                    if not page.locator("main h1").is_visible():
                        failures.append(f"{name}/{key}@{width}: main heading missing")
                    if width in (390,1440):
                        output = OUT / name / f"{key}-{width}.png"
                        output.parent.mkdir(parents=True, exist_ok=True)
                        page.screenshot(path=str(output))
                    # Mobile controls are not dependent on hover.
                    for selector in (".site-nav a", ".paper-actions .button", ".identity-actions .button"):
                        for el in page.locator(selector).all():
                            rect = el.bounding_box()
                            if rect is None or rect["height"] < 40:
                                failures.append(f"{name}/{key}@{width}: small or invisible target {selector}")
                ctx.close()
            browser.close()
    if failures:
        print("\n".join(failures))
        raise SystemExit(1)
    print("Cross-engine layout checks passed: 48 page/viewport combinations across WebKit and Firefox.")

if __name__ == "__main__":
    main()
