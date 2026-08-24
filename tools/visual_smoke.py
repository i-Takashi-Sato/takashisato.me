#!/usr/bin/env python3
"""Layout-focused visual smoke test for the public archive.

Catches catastrophic regressions (horizontal overflow, collapsed titles/rows/content)
and emits screenshots for manual review. It deliberately does not bless pixels: the
archive remains editorially reviewed, while CI blocks structural breakage.
"""
from __future__ import annotations

import os
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = os.environ.get("VISUAL_BASE_URL", "http://127.0.0.1:4173")
OUT = Path(os.environ.get("VISUAL_OUT", "artifacts/visual-smoke"))
PAGES = {
    "home": "/",
    "papers": "/papers/",
    "about": "/about.html",
    "part1": "/papers/part1.html",
    "part2": "/papers/part2.html",
    "part3": "/papers/part3.html",
}
VIEWPORTS = {
    "320": (320, 568),
    "390": (390, 844),
    "768": (768, 1024),
    "1440": (1440, 900),
    "1920": (1920, 1080),
}


def layout_errors(page, name: str, width: int, suffix: str) -> list[str]:
    metrics = page.evaluate(
        """() => {
          const vw = innerWidth;
          const offenders = [...document.querySelectorAll('body *')]
            .map(el => {
              const r = el.getBoundingClientRect();
              return {
                node: `${el.tagName.toLowerCase()}${el.id ? '#' + el.id : ''}${el.classList.length ? '.' + [...el.classList].slice(0,3).join('.') : ''}`,
                left: Math.round(r.left * 10) / 10,
                right: Math.round(r.right * 10) / 10,
                width: Math.round(r.width * 10) / 10,
                overflow: Math.max(0, r.right - vw, -r.left)
              };
            })
            .filter(x => x.overflow > 3 && x.width > 0)
            .sort((a,b) => b.overflow - a.overflow)
            .slice(0, 8);
          return {
            innerWidth: vw,
            scrollWidth: document.documentElement.scrollWidth,
            h1: [...document.querySelectorAll('main h1')].map(x => x.getBoundingClientRect().width),
            rows: [...document.querySelectorAll('.sequence-row')].map(x => x.getBoundingClientRect().width),
            titles: [...document.querySelectorAll('.sequence-title')].map(x => x.getBoundingClientRect().width),
            content: [...document.querySelectorAll('.content')].map(x => x.getBoundingClientRect().width),
            hero: [...document.querySelectorAll('.paper-hero')].map(x => x.getBoundingClientRect().width),
            offenders
          };
        }"""
    )
    errors: list[str] = []
    prefix = f"{name}@{width}/{suffix}"
    if metrics["scrollWidth"] > metrics["innerWidth"] + 3:
        errors.append(f"{prefix}: horizontal overflow {metrics}")
    if not metrics["h1"] or min(metrics["h1"]) < (118 if width <= 390 else 180):
        errors.append(f"{prefix}: collapsed h1 {metrics}")
    row_floor = width * (0.78 if width <= 390 else 0.55)
    if metrics["rows"] and min(metrics["rows"]) < row_floor:
        errors.append(f"{prefix}: collapsed sequence row {metrics}")
    title_floor = 110 if width <= 390 else 220
    if metrics["titles"] and min(metrics["titles"]) < title_floor:
        errors.append(f"{prefix}: collapsed sequence title {metrics}")
    content_floor = 250 if width <= 390 else 340
    if metrics["content"] and min(metrics["content"]) < content_floor:
        errors.append(f"{prefix}: collapsed reading column {metrics}")
    if metrics["hero"] and min(metrics["hero"]) < width * 0.78:
        errors.append(f"{prefix}: collapsed paper hero {metrics}")
    return errors


def run_context(
    browser,
    *,
    js: bool,
    suffix: str,
    viewports: dict[str, tuple[int, int]],
    pages: dict[str, str],
    errors: list[str],
) -> None:
    for vp_name, (width, height) in viewports.items():
        context = browser.new_context(viewport={"width": width, "height": height}, java_script_enabled=js)
        page = context.new_page()
        for name, path in pages.items():
            page.goto(BASE + path, wait_until="networkidle" if js else "domcontentloaded")
            page.locator("main").wait_for(state="visible")
            # Measure the actual runtime before manipulating reveal state.
            errors.extend(layout_errors(page, name, width, suffix))
            if js:
                # A full-page screenshot does not scroll each section through the
                # IntersectionObserver. Reveal after measurement so the artifact is
                # useful for editorial review without weakening the structural test.
                page.evaluate("document.querySelectorAll('[data-reveal]').forEach(x => x.classList.add('is-visible'))")
                out = OUT / f"{name}-{vp_name}.png"
                out.parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(out), full_page=True)
        context.close()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        run_context(browser, js=True, suffix="js", viewports=VIEWPORTS, pages=PAGES, errors=errors)
        # Progressive-enhancement contract: representative mobile/desktop pages must
        # remain structurally readable without JavaScript.
        run_context(
            browser,
            js=False,
            suffix="nojs",
            viewports={"390": VIEWPORTS["390"], "1440": VIEWPORTS["1440"]},
            pages={"home": "/", "papers": "/papers/", "part1": "/papers/part1.html", "part3": "/papers/part3.html"},
            errors=errors,
        )
        browser.close()
    if errors:
        print(f"Visual smoke found {len(errors)} structural regression(s):")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print(f"Visual smoke passed: {len(PAGES) * len(VIEWPORTS)} JS views + representative no-JS views")


if __name__ == "__main__":
    main()
