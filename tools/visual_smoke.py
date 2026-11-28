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
    "publications": "/publications/",
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
        diagnostics = page.evaluate("""() => {
          const width = () => document.documentElement.scrollWidth;
          const baseline = width();
          const selectors = ['.site-header', 'main', '.site-footer',
            '.identity-hero', '.sequence', '.metric-grid', '.boundary',
            '.profile-grid', '.research-map', '.identity-questions',
            '.identity-art', '.identity-masthead'];
          const candidates = selectors.flatMap(selector =>
            [...document.querySelectorAll(selector)].map((el, i) => {
              const prior = el.style.getPropertyValue('display');
              const priority = el.style.getPropertyPriority('display');
              el.style.setProperty('display', 'none', 'important');
              const after = width();
              if (prior) el.style.setProperty('display', prior, priority);
              else el.style.removeProperty('display');
              return {selector, index:i, after, recovered:baseline-after};
            })
          ).filter(x => x.recovered > 1).sort((a,b) => b.recovered-a.recovered);
          const style = document.createElement('style');
          style.textContent='*::before,*::after{content:none!important;display:none!important}';
          document.head.append(style);
          const withoutPseudos = width();
          style.remove();
          return {baseline, withoutPseudos, candidates};
        }""")
        errors.append(f"{prefix}: horizontal overflow {metrics} diagnostic={diagnostics}")
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

    if name == "home":
        links = page.locator(".identity-instruments .research-map-node")
        if links.count() != 3 or [link.get_attribute("href") for link in links.all()] != ["/papers/part1.html", "/papers/part2.html", "/papers/part3.html"]:
            errors.append(f"{prefix}: research index destinations changed")
        for link in links.all():
            box = link.bounding_box()
            if not box or box["height"] < 44:
                errors.append(f"{prefix}: insufficient instrument touch target")

    if 368 <= width <= 704:
        wordmark = page.locator('.brand span:last-child')
        if not wordmark.is_visible():
            errors.append(f'{prefix}: mobile brand wordmark missing')
    if width <= 704 and name in {'part1', 'part2', 'part3'}:
        for target in page.locator('.toc a').all():
            rect = target.bounding_box()
            if not rect or rect['height'] < 44:
                errors.append(f'{prefix}: undersized reading navigation target')

    # Horizontal fit does not rule out internal overlap.
    overlaps = page.evaluate("""() => {
      const failures = [];
      const intersects = (a,b) => a.width>0 && a.height>0 && b.width>0 && b.height>0 &&
        Math.min(a.right,b.right)-Math.max(a.left,b.left)>2 &&
        Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>2;
      const hero = document.querySelector('.paper-hero');
      if (hero) {
        const plate = hero.querySelector('.paper-apparatus').getBoundingClientRect();
        for (const el of hero.querySelectorAll('.breadcrumbs,.eyebrow,h1,.paper-subtitle,.paper-meta,.paper-actions')) {
          if (intersects(plate,el.getBoundingClientRect())) failures.push('paper plate overlaps '+el.className+' '+el.tagName);
        }
      }
      for (const node of document.querySelectorAll('.research-map-node')) {
        const parts = [...node.querySelectorAll('.map-index,.map-glyph,b,small')];
        for (let i=0;i<parts.length;i++) for (let j=i+1;j<parts.length;j++) {
          if (intersects(parts[i].getBoundingClientRect(),parts[j].getBoundingClientRect()))
            failures.push('map '+node.dataset.part+' overlaps '+parts[i].tagName+' '+parts[j].tagName);
        }
      }
      return failures;
    }""")
    errors.extend(f"{prefix}: {message}" for message in overlaps)

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

    if name in {"home", "papers"}:
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
                    f"{name}@1440/js: {selector} transition identity {actual!r}; "
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


def material_interaction_errors(browser, errors: list[str]) -> None:
    """Check hover feedback, stable target geometry, and the local texture."""
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()
    page.goto(BASE + PAGES["home"], wait_until="networkidle")
    link = page.locator("a.sequence-row").first
    link.scroll_into_view_if_needed()
    page.evaluate("document.querySelectorAll('[data-reveal]').forEach(x => x.classList.add('is-visible'))")
    page.wait_for_timeout(400)
    before = link.bounding_box()
    link.hover()
    page.wait_for_timeout(400)
    after = link.bounding_box()
    if not before or not after or any(abs(before[k] - after[k]) > 1 for k in ("x", "y", "width", "height")):
        errors.append("material interaction: paper hover shifts the clickable target")
    sibling = page.locator("a.sequence-row").nth(1)
    if float(sibling.evaluate("el => getComputedStyle(el).opacity")) < .99:
        errors.append("material interaction: hover dims another paper")
    plate = page.locator(".identity-art")
    if "research-metal.webp" not in plate.evaluate("el => getComputedStyle(el).backgroundImage"):
        errors.append("material interaction: research metal missing on home plate")
    response = page.request.get(BASE + "/assets/research-metal.webp")
    if not response.ok or not response.body().startswith(b"RIFF"):
        errors.append("material interaction: research metal unavailable")
    for name, selector in (("home", ".identity-instruments .map-glyph"), ("papers", ".map-glyph"), ("part1", ".paper-apparatus"), ("part2", ".paper-apparatus"), ("part3", ".paper-apparatus")):
        page.goto(BASE + PAGES[name], wait_until="networkidle")
        for element in page.locator(selector).all():
            if "research-metal.webp" not in element.evaluate("el => getComputedStyle(el).backgroundImage"):
                errors.append(f"material interaction: {name} plate missing research metal")
    page.goto(BASE + PAGES["about"], wait_until="networkidle")
    paper = page.locator(".portrait-chamber")
    if "author-paper.webp" not in paper.evaluate("el => getComputedStyle(el).backgroundImage"):
        errors.append("material interaction: author texture missing")
    response = page.request.get(BASE + "/assets/author-paper.webp")
    if not response.ok or not response.body().startswith(b"RIFF"):
        errors.append("material interaction: author texture unavailable")
    link = page.locator(".portrait-identifiers dd a").first
    link.focus()
    if link.evaluate("el => getComputedStyle(el).outlineStyle") == "none":
        errors.append("material interaction: author identity keyboard focus invisible")
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


def reading_entry_errors(browser, errors: list[str]) -> None:
    for width in (320, 390, 1440):
        for js in (False, True):
            context = browser.new_context(viewport={"width": width, "height": 844}, java_script_enabled=js, reduced_motion="reduce")
            page = context.new_page()
            for name in ("part1", "part2", "part3"):
                page.goto(BASE + PAGES[name], wait_until="domcontentloaded")
                entry = page.locator('.paper-hero .paper-actions a[href="#abstract"]')
                if entry.count() != 1:
                    errors.append(f"{name}@{width}: missing unique reading entry")
                    continue
                box = entry.bounding_box()
                if not box or box["height"] < 44 or box["width"] < 44:
                    errors.append(f"{name}@{width}: reading entry target below 44px")
                entry.click(timeout=5000)
                if page.evaluate("location.hash") != "#abstract":
                    errors.append(f"{name}@{width}: reading entry failed")
                if not page.locator("#abstract").is_visible():
                    errors.append(f"{name}@{width}: abstract not visible")
                if page.locator('nav.toc[aria-label="On this page"]').count() != 1:
                    errors.append(f"{name}@{width}: missing named reading navigation")
            context.close()


def citation_copy_errors(browser, errors: list[str]) -> None:
    context = browser.new_context(viewport={"width": 390, "height": 844})
    # Deterministic clipboard stub exercises the click handler without OS permission.
    context.add_init_script("""
      Object.defineProperty(navigator, 'clipboard', {
        configurable: true,
        value: {writeText: async value => {window.__copiedCitation = value;}}
      });
    """)
    page = context.new_page()
    for name in ("part1", "part2", "part3"):
        page.goto(BASE + PAGES[name], wait_until="domcontentloaded")
        button = page.locator("[data-citation-copy]")
        try:
            button.click(timeout=5000)
            page.wait_for_function("window.__copiedCitation !== undefined")
            if page.evaluate("window.__copiedCitation") != page.locator("#citation .citation").inner_text().strip():
                errors.append(f"{name}: copied citation differs from displayed record")
            if button.inner_text() != "Citation copied":
                errors.append(f"{name}: copy action lacks success feedback")
        except Exception as exc:
            errors.append(f"{name}: citation copy failed: {exc}")
    context.close()



def concept_register_errors(browser, errors: list[str]) -> None:
    for width in (320, 390, 1440):
        context = browser.new_context(viewport={"width": width, "height": 844}, java_script_enabled=False)
        page = context.new_page()
        page.goto(BASE + PAGES["papers"] + "#concepts", wait_until="domcontentloaded")
        rows = page.locator(".concept-record")
        if rows.count() != 7:
            errors.append(f"concepts {width}: expected seven records")
        for row in rows.all():
            links = row.locator("a.button")
            if links.count() != 5:
                errors.append(f"concepts {width}: expected five source links")
            if row.locator('a.button[href*=".pdf#page="]').count() != 1:
                errors.append(f"concepts {width}: expected one preserved PDF page locator")
            for link in links.all():
                box = link.bounding_box()
                if not box or box["height"] < 44 or box["width"] < 44:
                    errors.append(f"concepts {width}: target below 44px")
        if page.evaluate("document.documentElement.scrollWidth > innerWidth"):
            errors.append(f"concepts {width}: horizontal overflow")
        context.close()



def japanese_guide_errors(browser, errors: list[str]) -> None:
    for width in (320, 360, 375, 390, 393, 430, 768, 820, 896, 897, 1024, 1280, 1440, 1920):
        for js in ((False, True) if width in (320, 390, 1440) else (True,)):
            context = browser.new_context(viewport={"width": width, "height": 844}, java_script_enabled=js, reduced_motion="reduce")
            page = context.new_page()
            page.goto(BASE + PAGES["home"], wait_until="domcontentloaded")
            page.locator('a[href="/papers/#japanese"]').click(timeout=5000)
            page.wait_for_url("**/papers/#japanese")
            heading = page.locator("#japanese-title")
            heading.wait_for(state="visible", timeout=5000)
            if page.locator('#japanese[lang="ja"] .record-row').count() != 3:
                errors.append(f"Japanese guide {width}/{js}: missing paper records")
            if page.evaluate("document.documentElement.scrollWidth > innerWidth"):
                errors.append(f"Japanese guide {width}/{js}: horizontal overflow")
            geometry = heading.bounding_box()
            if not geometry or geometry["y"] < 0 or geometry["y"] >= 844:
                errors.append(f"Japanese guide {width}/{js}: entry heading outside viewport")
            reading = page.locator("#japanese .section-head > div")
            rows = page.locator("#japanese .record-row > div:last-child")
            notes = page.locator("#japanese .ja-evidence > div")
            boxes = [reading.bounding_box(), *[rows.nth(j).bounding_box() for j in range(3)], notes.bounding_box()]
            if any(box is None for box in boxes):
                errors.append(f"Japanese guide {width}/{js}: missing reading column")
            elif max(box["x"] for box in boxes) - min(box["x"] for box in boxes) > 2:
                errors.append(f"Japanese guide {width}/{js}: inconsistent reading alignment {boxes}")
            paragraph = rows.first.locator("p").first
            metrics = paragraph.evaluate("""e => {
                const s = getComputedStyle(e);
                return {font:parseFloat(s.fontSize), line:parseFloat(s.lineHeight), family:s.fontFamily};
            }""")
            if metrics["font"] < 16 or metrics["line"] / metrics["font"] < 1.8 or "Hiragino Mincho" not in metrics["family"]:
                errors.append(f"Japanese guide {width}/{js}: inappropriate body typography {metrics}")
            if geometry and boxes[0] and geometry["width"] > boxes[0]["width"] + 2:
                errors.append(f"Japanese guide {width}/{js}: title wider than reading column")
            # The family assertion above tests the declaration, not installed glyphs.
            phrase_report = page.locator("#japanese").evaluate("""root => {
                const lines = el => {
                    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
                    const groups = [];
                    while (walker.nextNode()) {
                        const node = walker.currentNode;
                        for (let i = 0; i < node.length; i++) {
                            const range = document.createRange();
                            range.setStart(node, i); range.setEnd(node, i + 1);
                            const rect = range.getBoundingClientRect();
                            if (!rect.width) continue;
                            let line = groups.find(g => Math.abs(g.y - rect.top) < 2);
                            if (!line) { line = {y: rect.top, text: ""}; groups.push(line); }
                            line.text += node.data[i];
                        }
                    }
                    return groups.map(g => g.text);
                };
                return {
                    broken: [...root.querySelectorAll(".ja-title-tail")].filter(e =>
                        lines(e).length !== 1 || e.scrollWidth > e.clientWidth + 2
                    ).map(e => e.textContent),
                    headings: [...root.querySelectorAll("h2, .record-row h3")].map(lines),
                    tracking: [...root.querySelectorAll("a[href]")].filter(a =>
                        a.getAttribute("href").includes("utm_")
                    ).map(a => a.getAttribute("href")),
                    measure: root.querySelector(".record-row > div:last-child").getBoundingClientRect().width
                };
            }""")
            if phrase_report["broken"] or phrase_report["tracking"]:
                errors.append(f"Japanese guide {width}/{js}: broken phrases or tracking {phrase_report}")
            if width >= 1280 and phrase_report["headings"][2] != ["手続が維持されていても、", "統治できているか"]:
                errors.append(f"Japanese guide {width}/{js}: Part II heading rhythm {phrase_report}")
            if width >= 897 and phrase_report["measure"] < 500:
                errors.append(f"Japanese guide {width}/{js}: cramped reading column {phrase_report}")
            print(f"Japanese guide {width}/{js}: {phrase_report}")
            for anchor in ("concepts", "critical-review"):
                page.locator(f'#japanese a[href="#{anchor}"]').click(timeout=5000)
                page.wait_for_url(f"**/papers/#{anchor}")
                if page.locator(f"#{anchor}").count() != 1:
                    errors.append(f"Japanese guide {width}/{js}: missing target {anchor}")
            if width in (320, 390, 1440):
                page.goto(BASE + PAGES["about"], wait_until="domcontentloaded")
                author_entry = page.locator('.portrait-note a[href="/papers/#japanese"][lang="ja"]')
                if author_entry.count() != 1:
                    errors.append(f"Japanese guide {width}/{js}: missing author entry")
                else:
                    author_entry.click(timeout=5000)
                    page.wait_for_url("**/papers/#japanese")
                    if not page.locator("#japanese-title").is_visible():
                        errors.append(f"Japanese guide {width}/{js}: author entry failed")
            context.close()


def publication_expansion_errors(browser, errors: list[str]) -> None:
    import sys
    root = str(Path(__file__).resolve().parents[1])
    if root not in sys.path:
        sys.path.insert(0, root)
    from src.archive.publications import publications_page, released_publications
    from verify_publications import fixture_records
    records = released_publications() + fixture_records()
    html = publications_page(records)
    for width in (320, 390, 768, 1440):
        for js in (False, True):
            context = browser.new_context(viewport={"width": width, "height": 844}, java_script_enabled=js, reduced_motion="reduce")
            page = context.new_page()
            page.route(BASE + "/publications/", lambda route: route.fulfill(status=200, content_type="text/html; charset=utf-8", body=html))
            page.goto(BASE + "/publications/", wait_until="load")
            errors.extend(layout_errors(page, "publication-fixture", width, str(js)))
            if page.locator(".sequence-row").count() != len(records) or page.locator('.sequence-title a[href="/fixture/essay.html"]').count() != 1:
                errors.append(f"Publication expansion {width}/{js}: fixture coverage or language mismatch")
            if not page.locator('.sequence-title[lang="ja"] a[href="/fixture/essay.html"]').is_visible():
                errors.append(f"Publication expansion {width}/{js}: Japanese title not visible")
            context.close()


def author_archive_entry_errors(browser, errors: list[str]) -> None:
    """The author-wide archive is the primary route; the trilogy is a feature."""
    for width in (320, 390, 1440):
        for js in (False, True):
            context = browser.new_context(
                viewport={"width": width, "height": 844},
                java_script_enabled=js,
                reduced_motion="reduce",
            )
            page = context.new_page()
            page.goto(BASE + "/", wait_until="domcontentloaded")
            heading = " ".join(page.locator("main h1").inner_text().split())
            if heading != "Takashi Sato":
                errors.append(f"Author archive {width}/{js}: unexpected home heading {heading!r}")
            entries = page.locator('.identity-actions a[href="/publications/"]')
            if entries.count() != 1 or not entries.first.is_visible():
                errors.append(f"Author archive {width}/{js}: missing primary publication entry")
            else:
                entries.first.click(timeout=5000)
                page.wait_for_url("**/publications/")
                if page.locator('.site-nav a[href="/publications/"][aria-current="page"]').count() != 1:
                    errors.append(f"Author archive {width}/{js}: catalogue current-page state missing")
                if page.locator('main a[href="/papers/"]').count() < 1:
                    errors.append(f"Author archive {width}/{js}: featured collection route lost")
            context.close()


def legacy_notice_errors(browser, errors: list[str]) -> None:
    """Check computed colors even when axe cannot evaluate background images."""
    routes = {
        "legacy-index": "/demo/",
        "legacy-part1": "/demo/altrion-part1.html",
        "legacy-part2": "/demo/altrion-part2.html",
    }
    measure = """() => {
        const panel = document.querySelector('.utility-page .notice');
        if (!panel) return {error:'missing notice'};
        const channels = value => (value.match(/[0-9]+(?:\\.[0-9]+)?/g) || []).map(Number);
        const luminance = rgb => rgb.slice(0,3).map(c => c / 255)
            .map(c => c <= .04045 ? c / 12.92 : ((c + .055) / 1.055) ** 2.4)
            .reduce((sum,c,i) => sum + c * [.2126,.7152,.0722][i], 0);
        const ratio = (a,b) => {
            const x = luminance(a), y = luminance(b);
            return (Math.max(x,y)+.05)/(Math.min(x,y)+.05);
        };
        const s = getComputedStyle(panel), panelRgb = channels(s.backgroundColor);
        if (s.backgroundImage !== 'none' || panelRgb.length !== 3 || s.opacity !== '1')
            return {error:'notice must have an opaque solid background', background:s.backgroundColor, image:s.backgroundImage, opacity:s.opacity};
        return {background:s.backgroundColor, nodes:[...panel.querySelectorAll('h1,p,a.button')].map(el => {
            const style = getComputedStyle(el), color = channels(style.color), ownBg = channels(style.backgroundColor);
            const bg = ownBg.length === 3 ? ownBg : panelRgb;
            const visible = el.getBoundingClientRect().width > 0 && el.getBoundingClientRect().height > 0;
            const supported = (ownBg.length === 3 || (ownBg.length === 4 && ownBg[3] === 0)) &&
                color.length === 3 && style.backgroundImage === 'none' && style.opacity === '1';
            return {text:el.textContent.trim(), color:style.color, background:style.backgroundColor,
                contrast:supported ? ratio(color,bg) : 0, visible, threshold:4.5};
        })};
    }"""
    for width, height in ((390, 844), (1440, 900)):
        context = browser.new_context(viewport={"width": width, "height": height}, reduced_motion="reduce")
        page = context.new_page()
        for name, route in routes.items():
            page.goto(BASE + route, wait_until="networkidle")
            page.locator(".notice").wait_for(state="visible")
            if page.evaluate("document.documentElement.scrollWidth > innerWidth"):
                errors.append(f"{name}@{width}: horizontal overflow")
            buttons = page.locator(".notice a.button")
            if buttons.count() != 2:
                errors.append(f"{name}@{width}: missing navigation buttons")
            def check(state):
                report = page.evaluate(measure)
                print(f"{name}@{width}/{state}: {report}")
                if report.get("error") or len(report.get("nodes", [])) != 5:
                    errors.append(f"{name}@{width}/{state}: {report}")
                    return
                for node in report["nodes"]:
                    if not node["visible"] or node["contrast"] < node["threshold"]:
                        errors.append(f"{name}@{width}/{state}: insufficient contrast {node}")
            page.mouse.move(0, 0)
            check("normal")
            page.screenshot(path=str(OUT / f"{name}-{width}.png"), full_page=True)
            for i in range(buttons.count()):
                buttons.nth(i).hover()
                check(f"hover-{i}")
                page.mouse.move(0, 0)
                buttons.nth(i).focus()
                check(f"focus-{i}")
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
                "publications": "/publications/",
                "papers": "/papers/",
                "about": "/about.html",
                "part1": "/papers/part1.html",
                "part3": "/papers/part3.html",
            },
            errors=errors,
        )
        reduced_motion_errors(browser, errors)
        material_interaction_errors(browser, errors)
        citation_copy_errors(browser, errors)
        reading_entry_errors(browser, errors)
        concept_register_errors(browser, errors)
        japanese_guide_errors(browser, errors)
        publication_expansion_errors(browser, errors)
        author_archive_entry_errors(browser, errors)
        legacy_notice_errors(browser, errors)
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
