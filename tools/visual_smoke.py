#!/usr/bin/env python3
"""Layout and semantic-interaction smoke tests for the public archive.

The suite blocks structural regressions and violations of the research-instrument
contract. It intentionally does not approve taste by screenshot diff: visual output
is still reviewed editorially from the uploaded artifacts.
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
    "430": (430, 932),
    "768": (768, 1024),
    "1024": (1024, 768),
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


def _style_snapshot(page, selector: str) -> dict[str, str]:
    return page.locator(selector).evaluate(
        """el => {
          const s = getComputedStyle(el);
          return {
            transform: s.transform,
            translate: s.translate,
            opacity: s.opacity,
            viewTransitionName: s.viewTransitionName || ''
          };
        }"""
    )


def _pseudo_snapshot(page, selector: str, pseudo: str = "::after") -> dict[str, str]:
    return page.locator(selector).evaluate(
        """(el, pseudo) => {
          const s = getComputedStyle(el, pseudo);
          return {
            width: s.width,
            left: s.left,
            right: s.right,
            opacity: s.opacity,
            transform: s.transform
          };
        }""",
        pseudo,
    )


def _px(value: str) -> float:
    return float(value[:-2]) if value.endswith("px") else 0.0


def semantic_motion_errors(page, name: str, width: int) -> list[str]:
    """Assert geometry describes the paper's research state rather than decoration."""
    if name not in {"part1", "part2", "part3"} or width < 768:
        return []

    apparatus = page.locator('.paper-apparatus')
    if apparatus.count() != 1:
        return [f"{name}@{width}/js: missing paper apparatus"]

    page.evaluate("scrollTo(0,0)")
    page.wait_for_timeout(80)
    frame_before = _style_snapshot(page, '.paper-apparatus')
    trace_before = _style_snapshot(page, '.paper-apparatus i:first-of-type')

    page.evaluate("scrollTo(0, Math.round(innerHeight * 0.55))")
    page.wait_for_timeout(180)
    frame_after = _style_snapshot(page, '.paper-apparatus')
    trace_after = _style_snapshot(page, '.paper-apparatus i:first-of-type')

    page.evaluate("scrollTo(0,0)")
    page.wait_for_timeout(80)

    prefix = f"{name}@{width}/js"

    if name == "part1":
        if frame_after["transform"] != frame_before["transform"]:
            return [f"{prefix}: measurement datum moved ({frame_before} -> {frame_after})"]
        if trace_after["translate"] != trace_before["translate"]:
            return [f"{prefix}: measurement trace drifted ({trace_before} -> {trace_after})"]
        return []

    if name == "part2":
        errors: list[str] = []
        if frame_after["transform"] != frame_before["transform"]:
            errors.append(
                f"{prefix}: procedural frame moved; only capacity traces may drift "
                f"({frame_before} -> {frame_after})"
            )
        if (
            trace_after["translate"] == trace_before["translate"]
            and trace_after["opacity"] == trace_before["opacity"]
        ):
            errors.append(
                f"{prefix}: internal capacity trace did not drift "
                f"({trace_before} -> {trace_after})"
            )
        return errors

    if frame_after["transform"] == frame_before["transform"]:
        return [
            f"{prefix}: accountable-exit apparatus did not contract "
            f"({frame_before} -> {frame_after})"
        ]
    return []


def transition_identity_errors(page, name: str, width: int) -> list[str]:
    """The same semantic instrument should carry identity across paper entrances."""
    if width != 1440:
        return []

    if name == "papers":
        expected = {
            '1': 'part-i-instrument',
            '2': 'part-ii-instrument',
            '3': 'part-iii-instrument',
        }
        errors: list[str] = []
        for part, transition_name in expected.items():
            selector = f'.research-map-node[data-part="{part}"] .map-glyph'
            actual = _style_snapshot(page, selector)["viewTransitionName"]
            if actual != transition_name:
                errors.append(
                    f"papers@1440/js: {selector} transition identity {actual!r}; "
                    f"expected {transition_name!r}"
                )
        return errors

    expected_by_page = {
        "part1": "part-i-instrument",
        "part2": "part-ii-instrument",
        "part3": "part-iii-instrument",
    }
    expected = expected_by_page.get(name)
    if not expected:
        return []
    actual = _style_snapshot(page, '.paper-apparatus')["viewTransitionName"]
    return [] if actual == expected else [
        f"{name}@1440/js: paper apparatus transition identity {actual!r}; expected {expected!r}"
    ]


def anchor_offset_errors(page, name: str, width: int) -> list[str]:
    """Sticky archive chrome must not cover in-document research targets."""
    if name not in {"part1", "part2", "part3"} or width != 1440:
        return []

    links = page.locator('.toc a[href^="#"]')
    if links.count() < 2:
        return [f"{name}@1440/js: insufficient TOC links for anchor test"]
    href = links.nth(1).get_attribute("href")
    if not href:
        return [f"{name}@1440/js: missing TOC href for anchor test"]

    page.evaluate(
        """selector => {
          document.documentElement.style.scrollBehavior = 'auto';
          document.querySelector(selector)?.scrollIntoView({block:'start'});
        }""",
        href,
    )
    page.wait_for_timeout(60)
    geometry = page.evaluate(
        """selector => {
          const target = document.querySelector(selector);
          const header = document.querySelector('.site-header');
          return {
            top: target?.getBoundingClientRect().top ?? -1,
            headerBottom: header?.getBoundingClientRect().bottom ?? 0
          };
        }""",
        href,
    )
    page.evaluate(
        """() => {
          scrollTo(0,0);
          document.documentElement.style.removeProperty('scroll-behavior');
        }"""
    )
    if geometry["top"] < geometry["headerBottom"] + 8:
        return [f"{name}@1440/js: anchor target hidden by sticky header {geometry}"]
    return []


def terminal_settle_errors(page, name: str, width: int) -> list[str]:
    """Part III must visibly spend energy and close at the footer, not open into spectacle."""
    if name != "part3" or width != 1440:
        return []

    page.evaluate("document.documentElement.style.scrollBehavior='auto'; scrollTo(0,0)")
    page.wait_for_timeout(50)
    line_before = _pseudo_snapshot(page, '.footer-wordmark')
    nav_before = _style_snapshot(page, '.series-nav')

    page.evaluate("scrollTo(0, document.documentElement.scrollHeight - innerHeight)")
    page.wait_for_timeout(120)
    line_after = _pseudo_snapshot(page, '.footer-wordmark')
    nav_after = _style_snapshot(page, '.series-nav')
    ending = float(page.evaluate(
        "getComputedStyle(document.documentElement).getPropertyValue('--ending') || '0'"
    ))
    ending_class = page.evaluate("document.documentElement.classList.contains('is-ending')")

    page.evaluate(
        """() => {
          scrollTo(0,0);
          document.documentElement.style.removeProperty('scroll-behavior');
        }"""
    )

    errors: list[str] = []
    if ending < .95 or not ending_class:
        errors.append(f"part3@1440/js: terminal state did not engage ending={ending}")
    if _px(line_before["width"]) <= 0 or _px(line_after["width"]) > _px(line_before["width"]) * .12:
        errors.append(
            f"part3@1440/js: closure rule did not converge ({line_before} -> {line_after})"
        )
    if float(nav_after["opacity"]) >= float(nav_before["opacity"]) - .05:
        errors.append(
            f"part3@1440/js: pre-footer navigation did not settle ({nav_before} -> {nav_after})"
        )
    return errors


def reduced_motion_errors(browser, errors: list[str]) -> None:
    """Reduced-motion users keep the complete research image without semantic motion."""
    context = browser.new_context(
        viewport={"width": 1440, "height": 900},
        reduced_motion="reduce",
    )
    page = context.new_page()

    for name in ("part2", "part3"):
        page.goto(BASE + PAGES[name], wait_until="networkidle")
        page.evaluate("scrollTo(0,0)")
        page.wait_for_timeout(70)
        frame_before = _style_snapshot(page, '.paper-apparatus')
        trace_before = _style_snapshot(page, '.paper-apparatus i:first-of-type')

        page.evaluate("scrollTo(0, Math.round(innerHeight * 0.55))")
        page.wait_for_timeout(150)
        frame_after = _style_snapshot(page, '.paper-apparatus')
        trace_after = _style_snapshot(page, '.paper-apparatus i:first-of-type')

        if frame_after["transform"] != frame_before["transform"]:
            errors.append(
                f"{name}@1440/reduced-motion: apparatus moved "
                f"({frame_before} -> {frame_after})"
            )
        if trace_after["translate"] != trace_before["translate"]:
            errors.append(
                f"{name}@1440/reduced-motion: internal trace moved "
                f"({trace_before} -> {trace_after})"
            )

    page.goto(BASE + PAGES["part3"], wait_until="networkidle")
    page.evaluate("document.documentElement.style.scrollBehavior='auto'; scrollTo(0,0)")
    page.wait_for_timeout(50)
    line_before = _pseudo_snapshot(page, '.footer-wordmark')
    nav_before = _style_snapshot(page, '.series-nav')
    page.evaluate("scrollTo(0, document.documentElement.scrollHeight - innerHeight)")
    page.wait_for_timeout(100)
    line_after = _pseudo_snapshot(page, '.footer-wordmark')
    nav_after = _style_snapshot(page, '.series-nav')
    if abs(_px(line_after["width"]) - _px(line_before["width"])) > 1:
        errors.append(
            f"part3@1440/reduced-motion: closure rule moved ({line_before} -> {line_after})"
        )
    if abs(float(nav_after["opacity"]) - float(nav_before["opacity"])) > .01:
        errors.append(
            f"part3@1440/reduced-motion: terminal navigation faded ({nav_before} -> {nav_after})"
        )

    context.close()


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
        context = browser.new_context(
            viewport={"width": width, "height": height},
            java_script_enabled=js,
        )
        page = context.new_page()

        for name, path in pages.items():
            page.goto(BASE + path, wait_until="networkidle" if js else "domcontentloaded")
            page.locator("main").wait_for(state="visible")

            # Measure the actual runtime before manipulating reveal state.
            errors.extend(layout_errors(page, name, width, suffix))

            if js:
                errors.extend(semantic_motion_errors(page, name, width))
                errors.extend(transition_identity_errors(page, name, width))
                errors.extend(anchor_offset_errors(page, name, width))
                errors.extend(terminal_settle_errors(page, name, width))

                # Full-page screenshots do not scroll each section through its
                # IntersectionObserver. Reveal after measurement so artifacts remain
                # useful for editorial review without weakening the structural test.
                page.evaluate(
                    "document.querySelectorAll('[data-reveal]').forEach(x => x.classList.add('is-visible'))"
                )
                out = OUT / f"{name}-{vp_name}.png"
                out.parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(out), full_page=True)

        context.close()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        run_context(
            browser,
            js=True,
            suffix="js",
            viewports=VIEWPORTS,
            pages=PAGES,
            errors=errors,
        )

        # Progressive enhancement: representative mobile/desktop pages remain
        # structurally readable with JavaScript completely disabled.
        run_context(
            browser,
            js=False,
            suffix="nojs",
            viewports={"390": VIEWPORTS["390"], "1440": VIEWPORTS["1440"]},
            pages={
                "home": "/",
                "papers": "/papers/",
                "part1": "/papers/part1.html",
                "part3": "/papers/part3.html",
            },
            errors=errors,
        )
        reduced_motion_errors(browser, errors)
        browser.close()

    if errors:
        print(f"Visual smoke found {len(errors)} structural regression(s):")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print(
        f"Visual smoke passed: {len(PAGES) * len(VIEWPORTS)} JS views + "
        "representative no-JS views + semantic/reduced-motion/transition/anchor/terminal contracts"
    )


if __name__ == "__main__":
    main()
