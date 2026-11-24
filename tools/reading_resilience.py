#!/usr/bin/env python3
"""Reading-resilience stress probes, separate from automated WCAG conformance claims."""
from __future__ import annotations

import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from visual_smoke import BASE, PAGES

OUT = Path("artifacts/visual-smoke/resilience")
CASES = (
    ("landscape", (844, 390), {}),
    ("reflow", (320, 768), {}),
    ("large-text", (390, 844), {}),
    ("forced-colors", (390, 844), {"forced_colors": "active"}),
    ("font-unavailable", (390, 844), {}),
    ("script-unavailable", (390, 844), {"java_script_enabled": False}),
    ("print", (794, 1123), {}),
)
MEASURE = """() => {
  const root = document.documentElement;
  const head = document.querySelector('main h1');
  const outside = [...document.querySelectorAll('main h1,main h2,main h3,main p,main a[href],main dt,main dd')]
    .filter(el => el.getClientRects().length && getComputedStyle(el).visibility !== 'hidden')
    .map(el => {
      const r = el.getBoundingClientRect();
      return {tag: el.tagName, text: el.textContent.trim().slice(0,100),
              left: Math.round(r.left), right: Math.round(r.right),
              width: Math.round(r.width)};
    }).filter(r => r.width > 0 && (r.left < -3 || r.right > innerWidth + 3)).slice(0,12);
  const brand = document.querySelector('.header-inner .brand');
  const nav = document.querySelector('.header-inner .site-nav');
  const b = brand?.getBoundingClientRect(), n = nav?.getBoundingClientRect();
  const headerOverlap = !!(b && n && b.width && n.width &&
    Math.min(b.right,n.right)-Math.max(b.left,n.left)>1 &&
    Math.min(b.bottom,n.bottom)-Math.max(b.top,n.top)>1);
  const headerOutside = [...document.querySelectorAll('.header-inner .brand,.header-inner .site-nav a')]
    .filter(el => el.getClientRects().length)
    .map(el => el.getBoundingClientRect())
    .some(r => r.width > 0 && (r.left < -3 || r.right > innerWidth + 3));
  return {viewport: innerWidth, scrollWidth: root.scrollWidth,
          heading: head?.textContent.trim() || '', outside, headerOverlap, headerOutside};
}"""


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    failures = []
    records = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for mode, (width, height), options in CASES:
            context = browser.new_context(
                viewport={"width": width, "height": height},
                reduced_motion="reduce", **options,
            )
            if mode == "font-unavailable":
                context.route("**/*", lambda route: route.abort() if route.request.resource_type == "font" else route.continue_())
            page = context.new_page()
            for name, route in PAGES.items():
                prefix = f"{mode}/{name}"
                problems = []
                page.goto(BASE + route, wait_until="networkidle")
                if mode == "large-text":
                    # Deliberate root-font stress, not a claim of native browser zoom equivalence.
                    page.evaluate("document.documentElement.style.setProperty('font-size','200%','important')")
                if mode == "print":
                    page.emulate_media(media="print")
                page.evaluate("document.fonts.ready")
                if not page.locator("main h1").is_visible():
                    problems.append("main heading is not visible")
                metrics = page.evaluate(MEASURE)
                if mode != "print" and metrics["scrollWidth"] > metrics["viewport"] + 3:
                    problems.append("document horizontal overflow")
                if mode != "print" and metrics["outside"]:
                    problems.append("visible reading element extends outside viewport")
                if mode != "print" and metrics["headerOverlap"]:
                    problems.append("brand and navigation overlap")
                if mode != "print" and metrics["headerOutside"]:
                    problems.append("header reading target extends outside viewport")
                if name.startswith("part") and mode != "print":
                    for selector in ('main a[href*="papers.ssrn.com"]', 'main a[href*="/pdf/v6.2/"]'):
                        if not any(link.is_visible() for link in page.locator(selector).all()):
                            problems.append("missing visible research route: " + selector)
                if mode == "reflow":
                    page.keyboard.press("Tab")
                    if page.evaluate("document.activeElement?.classList.contains('skip-link')") is not True:
                        problems.append("first keyboard target is not the skip link")
                    else:
                        page.keyboard.press("Enter")
                        if page.evaluate("location.hash") != "#main":
                            problems.append("skip link did not navigate to main")
                if mode == "print":
                    page.emulate_media(media="screen")
                records.append({"mode": mode, "page": name, "metrics": metrics, "problems": problems})
                if problems:
                    failures.extend(f"{prefix}: {problem}" for problem in problems)
                if problems or mode == "large-text":
                    page.screenshot(path=str(OUT / f"{mode}-{name}.png"), full_page=True)
            context.close()
        browser.close()
    (OUT / "report.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for failure in failures:
        print(failure)
    print(f"Reading-resilience probes: {len(records)} page/mode combinations, {len(failures)} findings.")
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
