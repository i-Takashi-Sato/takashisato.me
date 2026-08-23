#!/usr/bin/env python3
"""One-shot, idempotent production migration for The Proper Ending Index.

This migration folds the active visual/runtime layers into one production CSS/JS
pair, makes local v6.2 PDFs immutable, corrects scholarly metadata, and updates
the repository validator to enforce the resulting contract.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "6.2"
ASSET_VERSION = "6.12.0"
SITE_UPDATED = "2026-08-24"
PAPER_REVISION_DATE = "2026-08-23"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one migration anchor, found {count}")
    return text.replace(old, new, 1)


def filter_retired_stage_rules(text: str) -> str:
    tokens = [
        r"\.paper-hero::after",
        r"\.site-nav a\[href=\"/papers/\"\]::after",
        r"\.hero::before",
        r"\.sequence-row > div::after",
        r"\.page-hero::after",
    ]
    selector = "|".join(tokens)
    # Remove simple rules whose selector list belongs to the retired stage-mark
    # experiment. Nested @media/@supports containers may remain empty; that is
    # valid CSS and avoids risky broad deletion of unrelated rules.
    pattern = re.compile(rf"[^{{}}]*(?:{selector})[^{{}}]*\{{[^{{}}]*\}}", re.S)
    previous = None
    while previous != text:
        previous = text
        text = pattern.sub("", text)
    return text


def build_production_assets() -> None:
    base = read("assets/archive-v62.css")
    progressive = read("assets/archive-v66.css")
    author = read("styles/archive-v68.css")
    refinement = read("styles/archive-v611.css")

    # The retired brush-stage system was the only reason for these remote font
    # sources. Remove the remote face/import and all retired stage-mark rules.
    progressive = re.sub(
        r"@font-face\s*\{[^{}]*https?://[^{}]*\}\s*",
        "",
        progressive,
        count=1,
        flags=re.S,
    )
    author = re.sub(r"^@import\s+url\([^;]+;\s*", "", author, count=1, flags=re.M)
    progressive = filter_retired_stage_rules(progressive)
    author = filter_retired_stage_rules(author)
    refinement = filter_retired_stage_rules(refinement)

    css = (
        "/* The Proper Ending Index — production stylesheet. */\n"
        "/* Generated once from the audited v6.11 active cascade; legacy runtime layers retired. */\n\n"
        + base.strip()
        + "\n\n"
        + progressive.strip()
        + "\n\n"
        + author.strip()
        + "\n\n"
        + refinement.strip()
        + "\n"
    )
    if re.search(r"https?://", css):
        raise SystemExit("production CSS still contains a remote URL")
    write("assets/site.css", css)

    base_js = read("assets/archive-v62.js")
    base_js = re.sub(
        r'^if\(!d\.querySelector\("link\[data-v66\]"\)\)\{.*?\}\n',
        "",
        base_js,
        count=1,
        flags=re.M,
    )
    base_js = re.sub(
        r'^if\(!d\.querySelector\("link\[data-v68\]"\)\)\{.*?\}\n',
        "",
        base_js,
        count=1,
        flags=re.M,
    )
    site_js = (
        "/* The Proper Ending Index — production progressive enhancement. */\n"
        + base_js.strip()
        + "\n"
        + read("scripts/archive-v611.js").strip()
        + "\n"
        + read("assets/site-analytics.js").strip()
        + "\n"
    )
    for retired in ["archive-v66.css", "archive-v68.css", "research-fluid.js"]:
        if retired in site_js:
            raise SystemExit(f"production JS still references retired runtime: {retired}")
    write("assets/site.js", site_js)


def migrate_pdfs() -> None:
    target_dir = ROOT / "pdf" / f"v{VERSION}"
    target_dir.mkdir(parents=True, exist_ok=True)
    for slug in ("part1", "part2", "part3"):
        source = ROOT / "pdf" / f"{slug}.pdf"
        target = target_dir / f"{slug}.pdf"
        if target.exists():
            if source.exists() and source.read_bytes() != target.read_bytes():
                raise SystemExit(f"PDF migration conflict for {slug}")
        elif source.exists():
            target.write_bytes(source.read_bytes())
        else:
            raise SystemExit(f"missing source and immutable PDF for {slug}")
        if source.exists():
            source.unlink()


def migrate_builder() -> None:
    path = "tools/build_site.py"
    text = read(path)
    text = replace_once(
        text,
        'UPDATED = "2026-08-23"\nVERSION = "6.2"\nASSET_VERSION = "6.11.0"',
        f'UPDATED = "{SITE_UPDATED}"\nPAPER_REVISION_DATE = "{PAPER_REVISION_DATE}"\nVERSION = "6.2"\nASSET_VERSION = "{ASSET_VERSION}"',
        path,
    )
    text = replace_once(text, '"dateModified": UPDATED,', '"dateModified": PAPER_REVISION_DATE,', path)
    text = replace_once(text, '"uploadDate": UPDATED,', '"uploadDate": PAPER_REVISION_DATE,', path)
    text = replace_once(
        text,
        '<meta name="citation_publication_date" content="2026/08/23">',
        '<meta name="citation_publication_date" content="{paper[\'posted\'].replace(\'-\', \'/\')}">',
        path,
    )
    text = replace_once(
        text,
        '<meta property="article:modified_time" content="{UPDATED}">',
        '<meta property="article:modified_time" content="{PAPER_REVISION_DATE}">',
        path,
    )
    text = text.replace("/pdf/{paper['slug']}.pdf", "/pdf/v{VERSION}/{paper['slug']}.pdf")
    text = replace_once(
        text,
        '''          <link rel="stylesheet" href="/assets/archive-v62.css?v={ASSET_VERSION}">
          <link rel="stylesheet" href="/assets/archive-v66.css?v=6.7.0" data-v66>
          <link rel="stylesheet" href="/styles/archive-v68.css?v=6.8.0" data-v68>
          <link rel="stylesheet" href="/styles/archive-v611.css?v={ASSET_VERSION}" data-v611>
          <script src="/assets/archive-v62.js?v={ASSET_VERSION}"></script>
          <script src="/scripts/archive-v611.js?v={ASSET_VERSION}" defer></script>''',
        '''          <link rel="stylesheet" href="/assets/site.css?v={ASSET_VERSION}">
          <script src="/assets/site.js?v={ASSET_VERSION}"></script>''',
        path,
    )
    text = replace_once(
        text,
        '        <script src="/assets/site-analytics.js?v=entity-analytics-1" defer></script>\n',
        "",
        path,
    )
    text = replace_once(
        text,
        "The primary construct is <strong>PMGCL</strong>: Procedural Maintenance with Governing-Capacity Loss.",
        "The primary construct is <strong>PMGCL</strong>: Procedurally Masked Governing-Capacity Loss.",
        path,
    )
    text = replace_once(
        text,
        "The interface uses one shared stylesheet, one progressive-enhancement script, and a small analytics adapter. There is no framework runtime, remote font request, client-side router, account system, or third-party UI package.",
        "The interface uses one shared stylesheet and one self-contained progressive-enhancement script, including the small local analytics adapter. There is no framework runtime, remote font request, client-side router, account system, or third-party UI package.",
        path,
    )
    text = replace_once(
        text,
        "The interface pairs Newsreader for editorial display, Inter for navigation and long-form screen text, and Mea Culpa as a deliberately scarce calligraphic signature. All three families are self-hosted under the SIL Open Font License.",
        "The interface pairs Newsreader for editorial display, Inter for navigation and long-form screen text, and Mea Culpa for deliberately scarce calligraphic interaction labels. The author record uses supplied handwritten signature geometry. All three font families are self-hosted under the SIL Open Font License.",
        path,
    )
    text = replace_once(
        text,
        "Last rebuilt for the v6.2 papers on 23 August 2026.",
        "Last rebuilt for the v6.2 papers on 24 August 2026.",
        path,
    )
    text = replace_once(text, "Last update: 2026-08-23", "Last update: 2026-08-24", path)
    write(path, text)


def migrate_validator() -> None:
    path = "tools/verify_v62.py"
    text = read(path)
    text = replace_once(
        text,
        'UPDATED = "2026-08-23"\nVERSION = "6.2"\nASSET_VERSION = "6.11.0"',
        f'UPDATED = "{SITE_UPDATED}"\nVERSION = "6.2"\nASSET_VERSION = "{ASSET_VERSION}"',
        path,
    )
    posted = {
        "10.2139/ssrn.5911063": "2026-01-09",
        "10.2139/ssrn.5913703": "2026-01-12",
        "10.2139/ssrn.6066430": "2026-02-10",
    }
    for doi, date in posted.items():
        anchor = f'        "doi": "{doi}",\n'
        replacement = anchor + f'        "posted": "{date}",\n'
        text = replace_once(text, anchor, replacement, path)

    old_runtime = '''        expected_styles = [
            f"/assets/archive-v62.css?v={ASSET_VERSION}",
            "/assets/archive-v66.css?v=6.7.0",
            "/styles/archive-v68.css?v=6.8.0",
            f"/styles/archive-v611.css?v={ASSET_VERSION}",
        ]
        expected_enhancement = f"/assets/archive-v62.js?v={ASSET_VERSION}"
        expected_refinement = f"/scripts/archive-v611.js?v={ASSET_VERSION}"
        styles = [attrs.get("href", "") for tag, attrs in parser.tags if tag == "link" and attrs.get("rel") == "stylesheet"]
        if styles != expected_styles:
            fail(errors, f"{rel}: stylesheet contract mismatch: {styles}")
        enhancement_scripts = [
            attrs
            for tag, attrs in parser.tags
            if tag == "script" and attrs.get("src", "").startswith("/assets/archive-v62.js")
        ]
        if [attrs.get("src") for attrs in enhancement_scripts] != [expected_enhancement]:
            fail(errors, f"{rel}: enhancement script contract mismatch: {enhancement_scripts}")
        elif any("defer" in attrs or "async" in attrs for attrs in enhancement_scripts):
            fail(errors, f"{rel}: enhancement script must execute in head before body parsing")
        refinement_scripts = [
            attrs
            for tag, attrs in parser.tags
            if tag == "script" and attrs.get("src", "").startswith("/scripts/archive-v611.js")
        ]
        if [attrs.get("src") for attrs in refinement_scripts] != [expected_refinement]:
            fail(errors, f"{rel}: refinement script contract mismatch: {refinement_scripts}")
        elif any("defer" not in attrs for attrs in refinement_scripts):
            fail(errors, f"{rel}: refinement script must be deferred")
        head_text = text.partition("</head>")[0]
        if expected_enhancement not in head_text or expected_refinement not in head_text:
            fail(errors, f"{rel}: runtime scripts are not loaded from head")'''
    new_runtime = '''        expected_style = f"/assets/site.css?v={ASSET_VERSION}"
        expected_script = f"/assets/site.js?v={ASSET_VERSION}"
        styles = [attrs.get("href", "") for tag, attrs in parser.tags if tag == "link" and attrs.get("rel") == "stylesheet"]
        if styles != [expected_style]:
            fail(errors, f"{rel}: stylesheet contract mismatch: {styles}")
        scripts = [attrs for tag, attrs in parser.tags if tag == "script" and attrs.get("src")]
        production_scripts = [attrs for attrs in scripts if attrs.get("src", "").startswith("/assets/site.js")]
        if [attrs.get("src") for attrs in production_scripts] != [expected_script]:
            fail(errors, f"{rel}: production script contract mismatch: {production_scripts}")
        if len(scripts) != 1:
            fail(errors, f"{rel}: expected one production script, found {scripts}")
        head_text = text.partition("</head>")[0]
        if expected_style not in head_text or expected_script not in head_text:
            fail(errors, f"{rel}: production assets are not loaded from head")'''
    text = replace_once(text, old_runtime, new_runtime, path)
    text = replace_once(
        text,
        '                "citation_publication_date": "2026/08/23",',
        '                "citation_publication_date": paper["posted"].replace("-", "/"),',
        path,
    )
    text = replace_once(
        text,
        '            expected_pdf = f"{SITE}/pdf/{slug}.pdf"',
        '            expected_pdf = f"{SITE}/pdf/v{VERSION}/{slug}.pdf"',
        path,
    )

    new_assets = r'''def audit_assets(errors: list[str]) -> None:
    expected_assets = {
        "site.css",
        "site.js",
        "fonts/InterVariable.woff2",
        "fonts/Inter-OFL.txt",
        "fonts/Newsreader-Variable.woff2",
        "fonts/Newsreader-OFL.txt",
        "fonts/MeaCulpa.woff2",
        "fonts/MeaCulpa-OFL.txt",
        "materials/grain.jpg",
        "materials/paper.jpg",
        "materials/black-metal.jpg",
        "og/home.jpg",
        "og/papers.jpg",
        "og/about.jpg",
        "og/part1.jpg",
        "og/part2.jpg",
        "og/part3.jpg",
    }
    actual_assets = {
        str(path.relative_to(ROOT / "assets"))
        for path in (ROOT / "assets").rglob("*")
        if path.is_file()
    }
    if actual_assets != expected_assets:
        fail(
            errors,
            "runtime asset inventory mismatch; "
            f"missing={sorted(expected_assets - actual_assets)}, extra={sorted(actual_assets - expected_assets)}",
        )

    css = (ROOT / "assets/site.css").read_text(encoding="utf-8")
    js = (ROOT / "assets/site.js").read_text(encoding="utf-8")
    if css.count("{") != css.count("}"):
        fail(errors, "production stylesheet has unbalanced braces")
    if re.search(r"https?://|@import\s+url", css):
        fail(errors, "production stylesheet contains a remote dependency")
    for token in [":focus-visible", "::selection", "prefers-reduced-motion", "@media print", "cursor-orbit", "animation-timeline", "gate-probe"]:
        if token not in css:
            fail(errors, f"production stylesheet missing {token}")
    for token in ["pointermove", "requestAnimationFrame", "has-custom-cursor", "data-gate-probe", "site-analytics:event"]:
        if token not in js:
            fail(errors, f"production script missing {token}")
    for retired in ["archive-v62.css", "archive-v66.css", "archive-v68.css", "archive-v610.css", "research-fluid.js"]:
        if retired in js:
            fail(errors, f"production script references retired runtime: {retired}")
    if len(css.encode()) > 100_000:
        fail(errors, f"production stylesheet exceeds 100 KB: {len(css.encode())}")
    if len(js.encode()) > 20_000:
        fail(errors, f"production script exceeds 20 KB: {len(js.encode())}")

    fonts = {
        "Inter": (ROOT / "assets/fonts/InterVariable.woff2", 100_000),
        "Newsreader": (ROOT / "assets/fonts/Newsreader-Variable.woff2", 150_000),
        "MeaCulpa": (ROOT / "assets/fonts/MeaCulpa.woff2", 50_000),
    }
    for family, (font_path, size_limit) in fonts.items():
        if not font_path.read_bytes().startswith(b"wOF2"):
            fail(errors, f"{family} webfont is not a valid WOFF2 payload")
        if font_path.stat().st_size > size_limit:
            fail(errors, f"{family} webfont exceeds {size_limit // 1000} KB: {font_path.stat().st_size}")
        license_path = ROOT / f"assets/fonts/{family}-OFL.txt"
        if "SIL OPEN FONT LICENSE Version 1.1" not in license_path.read_text(encoding="utf-8"):
            fail(errors, f"{family} license record is missing or invalid")
        if font_path.name not in css:
            fail(errors, f"production stylesheet does not declare {family}")

    material_total = 0
    for name in ["grain", "paper", "black-metal"]:
        material_path = ROOT / f"assets/materials/{name}.jpg"
        material_total += material_path.stat().st_size
        with Image.open(material_path) as image:
            if image.format != "JPEG":
                fail(errors, f"{material_path.relative_to(ROOT)}: expected JPEG, found {image.format}")
            if image.width < 1500 or image.height < 850:
                fail(errors, f"{material_path.relative_to(ROOT)}: material resolution is too small: {image.size}")
        if f"materials/{name}.jpg" not in css:
            fail(errors, f"production stylesheet does not use {name}.jpg")
    if material_total > 350_000:
        fail(errors, f"material texture payload exceeds 350 KB: {material_total}")

    paper_match = re.search(r"--paper:\s*(#[0-9a-fA-F]{6})", css)
    if not paper_match:
        fail(errors, "production stylesheet is missing the paper color token")
    else:
        paper_color = paper_match.group(1)
        text_colors = set(re.findall(r"--(?:ink|ink-soft|ink-faint|signal-soft):\s*(#[0-9a-fA-F]{6})", css))
        for color in sorted(text_colors):
            ratio = contrast_ratio(color, paper_color)
            if ratio < 4.5:
                fail(errors, f"text color {color} has insufficient contrast on {paper_color}: {ratio:.2f}:1")

    for name in ["home", "papers", "about", *PAPERS]:
        image_path = ROOT / f"assets/og/{name}.jpg"
        if not image_path.exists():
            fail(errors, f"missing OG image: {image_path.relative_to(ROOT)}")
            continue
        with Image.open(image_path) as image:
            if image.size != (1200, 630):
                fail(errors, f"{image_path.relative_to(ROOT)}: expected 1200x630, found {image.size}")
            if image.format != "JPEG":
                fail(errors, f"{image_path.relative_to(ROOT)}: expected JPEG, found {image.format}")
    for name, size in {
        "android-chrome-192x192.png": (192, 192),
        "android-chrome-512x512.png": (512, 512),
        "apple-touch-icon.png": (180, 180),
        "favicon-16x16.png": (16, 16),
        "favicon-32x32.png": (32, 32),
    }.items():
        image_path = ROOT / name
        if not image_path.exists():
            fail(errors, f"missing icon: {name}")
            continue
        with Image.open(image_path) as image:
            if image.size != size:
                fail(errors, f"{name}: expected {size}, found {image.size}")
'''
    text, count = re.subn(
        r"def audit_assets\(errors: list\[str\]\) -> None:\n.*?\n\ndef audit_pdfs",
        new_assets + "\n\ndef audit_pdfs",
        text,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise SystemExit(f"{path}: could not replace audit_assets")

    text = replace_once(
        text,
        '        path = ROOT / f"pdf/{slug}.pdf"',
        '        path = ROOT / f"pdf/v{VERSION}/{slug}.pdf"',
        path,
    )
    pdf_digest_anchor = '''        if str(language) != "en-US":
            fail(errors, f"{path.relative_to(ROOT)}: PDF /Lang is {language!r}, expected en-US")'''
    pdf_digest_new = pdf_digest_anchor + '''
    for slug in PAPERS:
        legacy = ROOT / f"pdf/{slug}.pdf"
        if legacy.exists():
            fail(errors, f"mutable legacy PDF alias must not exist: {legacy.relative_to(ROOT)}")'''
    text = replace_once(text, pdf_digest_anchor, pdf_digest_new, path)
    text = replace_once(
        text,
        '        if encoding.get("contentUrl") != f"{SITE}/pdf/{slug}.pdf":',
        '        if encoding.get("contentUrl") != f"{SITE}/pdf/v{VERSION}/{slug}.pdf":',
        path,
    )
    write(path, text)


def migrate_ci() -> None:
    path = ".github/workflows/site-link-qa.yml"
    text = read(path)
    text = replace_once(
        text,
        '''          node --check assets/archive-v62.js
          node --check scripts/archive-v611.js
          node --check assets/site-analytics.js''',
        '''          node --check assets/site.js''',
        path,
    )
    write(path, text)


def remove_legacy_runtime() -> None:
    for rel in [
        "assets/archive-v62.css",
        "assets/archive-v62.js",
        "assets/archive-v66.css",
        "assets/site-analytics.js",
        "styles/archive-v610.css",
        "styles/archive-v68.css",
        "styles/archive-v69.css",
        "styles/archive-v611.css",
        "scripts/archive-v611.js",
        "scripts/research-fluid.js",
    ]:
        target = ROOT / rel
        if target.exists():
            target.unlink()


def main() -> None:
    build_production_assets()
    migrate_pdfs()
    migrate_builder()
    migrate_validator()
    migrate_ci()
    remove_legacy_runtime()
    print("Applied archive-integrity production migration.")


if __name__ == "__main__":
    main()
