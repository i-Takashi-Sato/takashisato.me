#!/usr/bin/env python3
"""Repository-level QA for The Proper Ending Index v6.2."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
import zipfile
import unicodedata
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

from PIL import Image
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.archive.abstracts import ABSTRACTS
from src.archive.citations import citation_export
from src.archive.model import (
    ASSET_VERSION,
    AUTHOR_ID,
    GOOGLE_SITE_VERIFICATION,
    PAPERS_BY_SLUG as PAPERS,
    SERIES_ID,
    SITE,
    UPDATED,
    VERSION,
)

CORE_HTML = [
    "index.html",
    "papers/index.html",
    "papers/part1.html",
    "papers/part2.html",
    "papers/part3.html",
    "about.html",
    "privacy.html",
    "security.html",
    "colophon.html",
]
ALL_HTML = CORE_HTML + ["404.html", "demo/index.html", "demo/altrion-part1.html", "demo/altrion-part2.html"]

class AuditParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[tuple[str, dict[str, str]]] = []
        self.ids: set[str] = set()
        self.id_list: list[str] = []
        self.hrefs: list[tuple[str, dict[str, str]]] = []
        self.json_ld: list[str] = []
        self.inline_executable_scripts: list[int] = []
        self.section_without_heading: list[int] = []
        self.article_without_heading: list[int] = []
        self._script_type = ""
        self._script_src = ""
        self._script_line = 0
        self._in_script = False
        self._script_text: list[str] = []
        self._sectioning_stack: list[list[str | int | bool]] = []
        self.h1_count = 0
        self.title_text: list[str] = []
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        self.tags.append((tag, data))
        if data.get("id"):
            self.ids.add(data["id"])
            self.id_list.append(data["id"])
        if tag == "a" and data.get("href"):
            self.hrefs.append((data["href"], data))
        if tag == "h1":
            self.h1_count += 1
        if tag in {"section", "article"}:
            self._sectioning_stack.append([tag, self.getpos()[0], False])
        elif re.fullmatch(r"h[1-6]", tag) and self._sectioning_stack:
            self._sectioning_stack[-1][2] = True
        if tag == "title":
            self._in_title = True
        if tag == "script":
            self._script_type = data.get("type", "")
            self._script_src = data.get("src", "")
            self._script_line = self.getpos()[0]
            self._in_script = True
            self._script_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag == "script":
            script_text = "".join(self._script_text)
            if self._script_type.casefold() == "application/ld+json":
                self.json_ld.append(script_text)
            elif not self._script_src and script_text.strip():
                self.inline_executable_scripts.append(self._script_line)
            self._script_type = ""
            self._script_src = ""
            self._script_line = 0
            self._in_script = False
            self._script_text = []
        if tag in {"section", "article"} and self._sectioning_stack:
            sectioning_tag, line, has_heading = self._sectioning_stack.pop()
            if sectioning_tag == tag and not has_heading:
                target = self.section_without_heading if tag == "section" else self.article_without_heading
                target.append(int(line))

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_text.append(data)
        if self._in_script:
            self._script_text.append(data)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def relative_luminance(color: str) -> float:
    channels = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(first: str, second: str) -> float:
    lighter, darker = sorted((relative_luminance(first), relative_luminance(second)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def local_target(href: str, source: Path) -> tuple[Path | None, str]:
    parsed = urlparse(href)
    if parsed.scheme or parsed.netloc or href.startswith("mailto:"):
        return None, parsed.fragment
    path = unquote(parsed.path)
    if not path:
        return source, parsed.fragment
    if path.startswith("/"):
        target = ROOT / path.lstrip("/")
    else:
        target = source.parent / path
    if path.endswith("/"):
        target = target / "index.html"
    elif target.is_dir():
        target = target / "index.html"
    return target, parsed.fragment


def audit_html(errors: list[str]) -> None:
    for rel in ALL_HTML:
        path = ROOT / rel
        if not path.exists():
            fail(errors, f"missing HTML: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        parser = AuditParser()
        parser.feed(text)

        if not re.search(r'<html\s+lang="[^"]+"', text):
            fail(errors, f"{rel}: missing html lang")
        if parser.h1_count != 1:
            fail(errors, f"{rel}: expected one h1, found {parser.h1_count}")
        if len(parser.id_list) != len(parser.ids):
            duplicates = sorted({value for value in parser.id_list if parser.id_list.count(value) > 1})
            fail(errors, f"{rel}: duplicate id values: {duplicates}")
        if not any(tag == "main" for tag, _ in parser.tags):
            fail(errors, f"{rel}: missing main landmark")
        if not "".join(parser.title_text).strip():
            fail(errors, f"{rel}: empty title")
        if not any(tag == "meta" and attrs.get("name") == "description" and attrs.get("content") for tag, attrs in parser.tags):
            fail(errors, f"{rel}: missing meta description")
        canonicals = [attrs.get("href", "") for tag, attrs in parser.tags if tag == "link" and attrs.get("rel") == "canonical"]
        if len(canonicals) != 1:
            fail(errors, f"{rel}: expected one canonical, found {canonicals}")
        inline_styles = [attrs.get("style", "") for _, attrs in parser.tags if attrs.get("style")]
        if inline_styles:
            fail(errors, f"{rel}: inline style attributes are not allowed")
        style_blocks = [attrs for tag, attrs in parser.tags if tag == "style"]
        if style_blocks:
            fail(errors, f"{rel}: inline style blocks conflict with production style-src-elem CSP")
        if parser.inline_executable_scripts:
            fail(errors, f"{rel}: executable inline script conflicts with production CSP at lines {parser.inline_executable_scripts}")
        if parser.section_without_heading:
            fail(errors, f"{rel}: section elements lack headings at lines {parser.section_without_heading}")
        if parser.article_without_heading:
            fail(errors, f"{rel}: article elements lack headings at lines {parser.article_without_heading}")
        for tag, attrs in parser.tags:
            if tag == "div" and attrs.get("aria-label") and not attrs.get("role"):
                fail(errors, f"{rel}: generic div with aria-label requires an explicit role")

        expected_style = f"/assets/site.css?v={ASSET_VERSION}"
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
            fail(errors, f"{rel}: production assets are not loaded from head")

        identity_links = {
            attrs.get("href", "")
            for tag, attrs in parser.tags
            if tag == "link" and "me" in attrs.get("rel", "").split()
        }
        expected_identity_links = {
            "https://orcid.org/0009-0003-1584-6965",
            "https://papers.ssrn.com/Sol3/Cf_Dev/AbsByAuth.cfm?per_id=9540672",
            "https://scholar.google.com/citations?user=tN4zV68AAAAJ",
        }
        if identity_links != expected_identity_links:
            fail(errors, f"{rel}: rel=me identity links mismatch: {sorted(identity_links)}")

        for raw in parser.json_ld:
            try:
                json.loads(raw)
            except json.JSONDecodeError as exc:
                fail(errors, f"{rel}: invalid JSON-LD: {exc}")

        if rel in CORE_HTML:
            if len(parser.json_ld) != 1:
                fail(errors, f"{rel}: expected one JSON-LD block, found {len(parser.json_ld)}")
            elif parser.json_ld:
                data = json.loads(parser.json_ld[0])
                if data.get("@context") != "https://schema.org":
                    fail(errors, f"{rel}: JSON-LD context mismatch")
                nodes = data.get("@graph", [data])
                if rel != "index.html" and not any(node.get("@type") == "BreadcrumbList" for node in nodes):
                    fail(errors, f"{rel}: missing BreadcrumbList structured data")
            if rel != "index.html" and not any(
                tag == "nav" and "breadcrumbs" in attrs.get("class", "").split()
                for tag, attrs in parser.tags
            ):
                fail(errors, f"{rel}: missing visible breadcrumb navigation")

        if rel.startswith("papers/part"):
            slug = Path(rel).stem
            paper = PAPERS[slug]
            meta_by_name: dict[str, list[str]] = {}
            for tag, attrs in parser.tags:
                if tag == "meta" and attrs.get("name"):
                    meta_by_name.setdefault(attrs["name"], []).append(attrs.get("content", ""))
            expected_citations = {
                "citation_title": f"{paper['title']}: {paper['subtitle']}",
                "citation_author": "Takashi Sato",
                "citation_publication_date": paper["posted"].replace("-", "/"),
                "citation_doi": paper["doi"],
                "citation_language": "en",
            }
            for name, expected in expected_citations.items():
                if meta_by_name.get(name) != [expected]:
                    fail(errors, f"{rel}: {name} mismatch: {meta_by_name.get(name)}")
            pdf_alternates = [
                attrs.get("href", "")
                for tag, attrs in parser.tags
                if tag == "link" and attrs.get("rel") == "alternate" and attrs.get("type") == "application/pdf"
            ]
            expected_pdf = f"{SITE}/pdf/v{VERSION}/{slug}.pdf"
            if pdf_alternates != [expected_pdf]:
                fail(errors, f"{rel}: PDF alternate mismatch: {pdf_alternates}")

        for href, attrs in parser.hrefs:
            if attrs.get("target") == "_blank":
                rel_tokens = set(attrs.get("rel", "").split())
                if not {"noopener", "noreferrer"}.issubset(rel_tokens):
                    fail(errors, f"{rel}: target=_blank lacks noopener noreferrer: {href}")
            target, fragment = local_target(href, path)
            if target is None:
                continue
            if not target.exists():
                fail(errors, f"{rel}: broken local link {href} -> {target.relative_to(ROOT) if target.is_relative_to(ROOT) else target}")
                continue
            if fragment and target.suffix == ".html":
                target_parser = AuditParser()
                target_parser.feed(target.read_text(encoding="utf-8"))
                if fragment not in target_parser.ids:
                    fail(errors, f"{rel}: missing fragment #{fragment} in {target.relative_to(ROOT)}")


def audit_content(errors: list[str]) -> None:
    core = "\n".join((ROOT / rel).read_text(encoding="utf-8") for rel in CORE_HTML)
    production_css = (ROOT / "assets/site.css").read_text(encoding="utf-8")
    for retired_mark in ("序", "破", "急", "Jo / Ha / Kyu"):
        if retired_mark in production_css:
            fail(errors, f"retired stage mark present in production CSS: {retired_mark}")
    stale = ["Four-Gate", "Forecasting Failure", "Detecting Silent Governance Failure", "A Sociotechnical Architecture"]
    for term in stale:
        if term.casefold() in core.casefold():
            fail(errors, f"stale current-research term present: {term}")
    required = [
        "EXECUTION ELIGIBLE",
        "AUTHORIZED DEFER",
        "PMGCL",
        "PAC",
        "Authority Return",
        "8,564",
        "36,096",
        "23 August 2026",
    ]
    for term in required:
        if term not in core:
            fail(errors, f"required v6.2 term missing: {term}")

    commercial_traces = [
        "/services/",
        "/samples/",
        "contact.html",
        "Sapporo Investment",
        "サッポロインベストメント",
        "業務設計室",
        "Operational Design",
    ]
    for term in commercial_traces:
        if term.casefold() in core.casefold():
            fail(errors, f"commercial or services trace present in current archive: {term}")

    about = (ROOT / "about.html").read_text(encoding="utf-8")
    for identity in ["佐藤貴士", "Sapporo", "0009-0003-1584-6965", "tN4zV68AAAAJ", "9540672"]:
        if identity not in about:
            fail(errors, f"about.html: identity element missing: {identity}")
    for stale_copy in ["佐藤貴士について", "現在の研究では、人間が形式上", "AIガバナンス、人間による監督、ワークフロー・ガバナンス"]:
        if stale_copy in about:
            fail(errors, f"about.html: verbose Japanese profile copy returned: {stale_copy}")
    if about.count('href="mailto:i@takashisato.me"') != 1:
        fail(errors, "about.html: approved correspondence link must appear once")
    if any(term in about for term in ["business operations", "organizational management", "competitive golf"]):
        fail(errors, "about.html: private biography must remain outside the public author record")
    if about.count('<p lang="ja">佐藤貴士</p>') != 1:
        fail(errors, "about.html: native-name identity fact must be exactly one instance")
    if "佐藤貴士　札幌" in about:
        fail(errors, "about.html: awkward Japanese SEO phrase returned to the visible author record")

    home = (ROOT / "index.html").read_text(encoding="utf-8")
    if home.count('<span lang="ja">佐藤貴士</span>') != 1:
        fail(errors, "index.html: native author name must appear once in visible copy")
    for rel, html in [("index.html", home), ("about.html", about)]:
        if "<title>Takashi Sato (佐藤貴士) — " not in html:
            fail(errors, f"{rel}: bilingual identity title missing")
    if '<link rel="preload" href="/assets/author-paper.webp" as="image" type="image/webp" fetchpriority="high">' not in about or "/assets/author-paper.webp" in home:
        fail(errors, "author-only material preload contract violated")
    if '<link rel="preload" href="/assets/fonts/Newsreader-Variable.woff2" as="font" type="font/woff2" crossorigin media="(min-width:48.01rem)">' not in about or '<link rel="preload" href="/assets/fonts/Newsreader-Variable.woff2" as="font" type="font/woff2" crossorigin media="(min-width:48.01rem)">' in home:
        fail(errors, "author-only editorial font preload contract violated")
    record_path = ROOT / "reproduction/v5.9/part3-reexecution-2026-11-24.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    if record["artifactVersion"] != "5.9" or record["manuscriptVersion"] != "6.2" or record["independentReplication"] or record["fullPackagePublished"]:
        fail(errors, "Part III re-execution scope mismatch")
    if record["partIII"] != {"reachableStates": 8564, "enabledTransitions": 36096, "authoredInvariantViolations": 0, "mutationsWithCounterexamples": 30}:
        fail(errors, "Part III re-execution results mismatch")
    # Verify the downloadable historical source before executing it in an isolated directory.
    bundle = ROOT / "reproduction/v5.9/part3-historical-checker.zip"
    expected_bundle_sha = "f2daa94a5c9c88358d2d1579be2ada55afe20fe5ba8bd5ddbaff92e9f5b16086"
    expected_members = {"LICENSE", "formal_protocol_checks.py", "README.txt"}
    expected_hashes = {
        "LICENSE": "7735ca7d95593d86cfeb31a7165dc3e8c8d6eec76a1c154954e71d98d610ac80",
        "formal_protocol_checks.py": "ca82fc325fce1ddac2dcbcc407fe3eaa96892914855decc961ab220caebc0c7d",
        "formal_protocol_results.json": "30608277c7c8f1ede88e86699674ac4679ad7a2cf0a36ebd3c2d5507928ef952",
        "formal_protocol_results.md": "51e21af27021d1b94e20ff1b0f4f699c807f9a31303713217ba77d7a40fb6e5e",
    }
    subset = record.get("executableSubset", {})
    if subset.get("sha256") != expected_bundle_sha or subset.get("bytes") != 8908 or subset.get("url") != f"{SITE}/reproduction/v5.9/part3-historical-checker.zip":
        fail(errors, "historical checker metadata mismatch")
    if not bundle.is_file() or bundle.stat().st_size != 8908 or hashlib.sha256(bundle.read_bytes()).hexdigest() != expected_bundle_sha:
        fail(errors, "historical checker bundle integrity mismatch")
    else:
        with zipfile.ZipFile(bundle) as z:
            if set(z.namelist()) != expected_members or len(z.namelist()) != 3 or z.testzip() is not None:
                fail(errors, "historical checker bundle members mismatch")
            elif any(hashlib.sha256(z.read(n)).hexdigest() != expected_hashes[n] for n in ("LICENSE", "formal_protocol_checks.py")):
                fail(errors, "historical checker source or license mismatch")
            else:
                with tempfile.TemporaryDirectory(prefix="historical-checker-") as tmp:
                    work = Path(tmp)
                    (work / "formal_protocol_checks.py").write_bytes(z.read("formal_protocol_checks.py"))
                    run = subprocess.run([sys.executable, "-I", "formal_protocol_checks.py", "--out", "rerun"], cwd=work, capture_output=True, timeout=120)
                    if run.returncode:
                        fail(errors, "historical checker re-execution failed")
                    else:
                        for n in ("formal_protocol_results.json", "formal_protocol_results.md"):
                            output = work / "rerun" / n
                            if not output.is_file() or hashlib.sha256(output.read_bytes()).hexdigest() != expected_hashes[n]:
                                fail(errors, f"historical checker output mismatch: {n}")
    if f'href="/reproduction/v5.9/part3-historical-checker.zip" download' not in (ROOT / "papers/part3.html").read_text(encoding="utf-8"):
        fail(errors, "historical checker download link missing")
    if '"dateModified":"2026-11-24"' not in (ROOT / "colophon.html").read_text(encoding="utf-8"):
        fail(errors, "colophon.html: structured revision date mismatch")
    if GOOGLE_SITE_VERIFICATION not in home:
        fail(errors, "index.html: Search Console ownership verification is missing")
    if "AI Governance Research Archive" not in home:
        fail(errors, "index.html: visible field classification is missing")
    if '"@type":"CreativeWorkSeries"' not in home or SERIES_ID not in home:
        fail(errors, "index.html: canonical research-series entity is missing")

    for slug, paper in PAPERS.items():
        text = (ROOT / f"papers/{slug}.html").read_text(encoding="utf-8")
        for value in [paper["title"], paper["subtitle"], paper["ssrn"], paper["doi"], "v6.2", paper["sha256"]]:
            if str(value) not in text:
                fail(errors, f"papers/{slug}.html: missing {value}")


def audit_assets(errors: list[str]) -> None:
    expected_assets = {
        "site.css",
        "site.js",
        "brand-mark.svg",
        "fonts/InterVariable.woff2",
        "fonts/Inter-OFL.txt",
        "fonts/Newsreader-Variable.woff2",
        "fonts/Newsreader-OFL.txt",
        "fonts/MeaCulpa.woff2",
        "fonts/MeaCulpa-OFL.txt",
        "og/home.jpg",
        "og/papers.jpg",
        "og/about.jpg",
        "author-mark.svg",
        "author-paper.webp",
        "research-metal.webp",
        "favicon-source-20260117.png",
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

    texture = ROOT / "assets/author-paper.webp"
    with Image.open(texture) as image:
        if image.format != "WEBP" or image.size != (900, 599) or texture.stat().st_size > 12_000:
            fail(errors, "author paper texture violates the local asset budget")
    metal = ROOT / "assets/research-metal.webp"
    with Image.open(metal) as image:
        if image.format != "WEBP" or image.size != (480, 280) or metal.stat().st_size > 4_000 or image.getexif():
            fail(errors, "research metal texture violates the local asset budget")
    if hashlib.sha256(metal.read_bytes()).hexdigest() != "991c61263406b977f10b94dad4481afdde30f929028f33245e1c4349aed9c22c":
        fail(errors, "research metal texture digest mismatch")
    css = (ROOT / "assets/site.css").read_text(encoding="utf-8")
    js = (ROOT / "assets/site.js").read_text(encoding="utf-8")
    if css.count("{") != css.count("}"):
        fail(errors, "production stylesheet has unbalanced braces")
    if re.search(r"https?://|@import\s+url", css):
        fail(errors, "production stylesheet contains a remote dependency")
    for token in [":focus-visible", "::selection", "prefers-reduced-motion", "@media print", "identity-hero-grid", "gate-probe"]:
        if token not in css:
            fail(errors, f"production stylesheet missing {token}")
    for token in ["requestAnimationFrame", "data-gate-probe", "site-analytics:event"]:
        if token not in js:
            fail(errors, f"production script missing {token}")
    for retired_pointer in ["has-custom-cursor", "cursorLabel", "initAuthorityCursor"]:
        if retired_pointer in js:
            fail(errors, f"retired custom pointer code remains: {retired_pointer}")
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

    # Only :root color tokens belong to the global paper/ink contrast test.
    # Scoped dark research exhibits are audited against their actual backgrounds by axe.
    required_palette = ("paper", "ink", "ink-soft", "ink-faint", "signal-soft")
    root_bodies = re.findall(r":root\s*\{([^{}]*)\}", css)
    # Print-only roots may override paper and ink without being the screen palette.
    # Require one coherent root declaration containing the full semantic palette.
    main_roots = [
        root_body for root_body in root_bodies
        if all(re.search(rf"--{token}\s*:", root_body) for token in required_palette)
    ]
    global_palette = (
        dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})", main_roots[-1]))
        if main_roots else {}
    )
    paper_color = global_palette.get("paper")
    if not paper_color:
        fail(errors, "production stylesheet is missing the root paper color token")
    else:
        for token in ("ink", "ink-soft", "ink-faint", "signal-soft"):
            color = global_palette.get(token)
            if not color:
                fail(errors, f"production stylesheet missing global --{token} palette token")
                continue
            ratio = contrast_ratio(color, paper_color)
            if ratio < 4.5:
                fail(errors, f"global text color {color} has insufficient contrast on {paper_color}: {ratio:.2f}:1")

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
    brand_svg = (ROOT / "assets/brand-mark.svg").read_text(encoding="utf-8")
    if 'M11 59V12H55V30M55 52V59H11' not in brand_svg or 'M29 41H64' not in brand_svg:
        fail(errors, "archive brand geometry mismatch")
    source_bytes = (ROOT / "assets/favicon-source-20260117.png").read_bytes()
    git_header = f"blob {len(source_bytes)}".encode()+b"\x00"
    if hashlib.sha1(git_header+source_bytes).hexdigest() != "77b0d7361039b623cc383ee053b88211d00c5735":
        fail(errors, "recovered January favicon source mismatch")
    for name in ("favicon.svg","favicon-dark.svg"):
        svg = (ROOT / name).read_text(encoding="utf-8")
        if 'Takashi Sato — personal T mark' not in svg or 'data:image/png;base64,' not in svg:
            fail(errors, f"{name}: supplied personal mark missing")
    for name, size in {
        "android-chrome-192x192.png": (192, 192),
        "android-chrome-512x512.png": (512, 512),
        "apple-touch-icon.png": (180, 180),
        "favicon-16x16.png": (16, 16),
        "favicon-32x32.png": (32, 32),
        "favicon-96x96.png": (96, 96),
        "favicon-16x16-dark.png": (16, 16),
        "favicon-32x32-dark.png": (32, 32),
        "maskable-512x512.png": (512, 512),
    }.items():
        image_path = ROOT / name
        if not image_path.exists():
            fail(errors, f"missing icon: {name}")
            continue
        with Image.open(image_path) as image:
            if image.size != size:
                fail(errors, f"{name}: expected {size}, found {image.size}")
    if "prefers-color-scheme:dark" not in (ROOT / "favicon.svg").read_text(encoding="utf-8"):
        fail(errors, "favicon: missing adaptive theme")
    with Image.open(ROOT / "favicon.ico") as image:
        if image.ico.sizes() != {(16,16),(32,32),(48,48),(64,64)}:
            fail(errors, "favicon.ico: incomplete multi-size master")
        for n in (16,32):
            with Image.open(ROOT / f"favicon-{n}x{n}.png") as png:
                if image.ico.getimage((n,n)).convert("RGB").tobytes() != png.convert("RGB").tobytes():
                    fail(errors, f"favicon.ico: optical {n}px variant mismatch")
    with Image.open(ROOT / "maskable-512x512.png") as image:
        pixels = image.convert("RGB").load()
        bg = pixels[0,0]
        if any(pixels[x,y] != bg for y in range(512) for x in range(512) if (x-255.5)**2+(y-255.5)**2 > (512*.40)**2):
            fail(errors, "maskable icon: artwork exceeds circular safe zone")


def normalize_abstract(value: str) -> str:
    """Ignore layout-only whitespace, discretionary hyphens, and extraction controls."""
    value = unicodedata.normalize("NFKC", value)
    return "".join(
        char for char in value
        if not char.isspace() and unicodedata.category(char) not in {"Cc", "Cf", "Pd"}
    )


def audit_scholarly_apparatus(errors: list[str]) -> None:
    index = json.loads((ROOT / "research-index.json").read_text(encoding="utf-8"))
    for position, (slug, paper) in enumerate(PAPERS.items()):
        abstract = "\n\n".join(ABSTRACTS[slug])
        html = (ROOT / f"papers/{slug}.html").read_text(encoding="utf-8")
        section = re.search(r'<section id="abstract">(.*?)</section>', html, re.S)
        if not section:
            fail(errors, f"{slug}: visible abstract missing")
        else:
            paragraphs = re.findall(r"<p>(.*?)</p>", section.group(1), re.S)
            if [unescape(p) for p in paragraphs] != ABSTRACTS[slug]:
                fail(errors, f"{slug}: visible abstract differs from source")
        parser = AuditParser()
        parser.feed(html)
        articles = [
            item for raw in parser.json_ld for item in json.loads(raw).get("@graph", [])
            if item.get("@type") == "ScholarlyArticle"
        ]
        if len(articles) != 1 or articles[0].get("abstract") != abstract:
            fail(errors, f"{slug}: article metadata abstract mismatch")
        if position >= len(index.get("hasPart", [])) or index["hasPart"][position].get("abstract") != abstract:
            fail(errors, f"{slug}: research-index abstract mismatch")
        for kind in ("bib", "ris"):
            path = ROOT / f"citations/v{VERSION}/{slug}.{kind}"
            if not path.exists() or path.read_text(encoding="utf-8") != citation_export(paper, kind):
                fail(errors, f"{slug}: {kind} citation export mismatch")
            if not any(href == f"/citations/v{VERSION}/{slug}.{kind}" for href, _ in parser.hrefs):
                fail(errors, f"{slug}: {kind} citation link missing")


def audit_pdfs(errors: list[str]) -> None:
    for slug, expected in PAPERS.items():
        path = ROOT / f"pdf/v{VERSION}/{slug}.pdf"
        if not path.exists():
            fail(errors, f"missing PDF: {path.relative_to(ROOT)}")
            continue
        payload = path.read_bytes()
        if len(payload) != expected["bytes"]:
            fail(errors, f"{path.relative_to(ROOT)}: byte size {len(payload)} != {expected['bytes']}")
        digest = hashlib.sha256(payload).hexdigest()
        if digest != expected["sha256"]:
            fail(errors, f"{path.relative_to(ROOT)}: SHA-256 mismatch")
        reader = PdfReader(path)
        if len(reader.pages) > 1:
            raw = reader.pages[1].extract_text() or ""
            match = re.search(r"\bAbstract\s+(.*?)\bKeywords\s*:", raw, re.S | re.I)
            if not match or normalize_abstract(match.group(1)) != normalize_abstract(" ".join(ABSTRACTS[slug])):
                fail(errors, f"{slug}: transcribed abstract differs from preserved PDF page 2")
        if len(reader.pages) != expected["pages"]:
            fail(errors, f"{path.relative_to(ROOT)}: page count {len(reader.pages)} != {expected['pages']}")
        metadata_title = (reader.metadata.title or "") if reader.metadata else ""
        if expected["title"] not in metadata_title:
            fail(errors, f"{path.relative_to(ROOT)}: PDF title metadata mismatch: {metadata_title!r}")
        if not reader.metadata or reader.metadata.author != "Takashi Sato":
            fail(errors, f"{path.relative_to(ROOT)}: PDF author metadata mismatch")
        language = reader.trailer["/Root"].get("/Lang")
        if str(language) != "en-US":
            fail(errors, f"{path.relative_to(ROOT)}: PDF /Lang is {language!r}, expected en-US")
    for slug in PAPERS:
        legacy = ROOT / f"pdf/{slug}.pdf"
        if legacy.exists():
            fail(errors, f"mutable legacy PDF alias must not exist: {legacy.relative_to(ROOT)}")


def audit_indexes(errors: list[str]) -> None:
    index = json.loads((ROOT / "research-index.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "site.webmanifest").read_text(encoding="utf-8"))
    if index.get("@context") != "https://schema.org" or index.get("@type") != "CreativeWorkSeries":
        fail(errors, "research-index.json: expected a Schema.org CreativeWorkSeries")
    if index.get("@id") != SERIES_ID:
        fail(errors, "research-index.json: series identifier mismatch")
    if index.get("dateModified") != UPDATED or index.get("version") != VERSION:
        fail(errors, "research-index.json: stale version or update date")
    creator = index.get("creator", {})
    if creator.get("@id") != AUTHOR_ID:
        fail(errors, "research-index.json: author entity identifier mismatch")
    expected_same_as = {
        "https://orcid.org/0009-0003-1584-6965",
        "https://papers.ssrn.com/Sol3/Cf_Dev/AbsByAuth.cfm?per_id=9540672",
        "https://scholar.google.com/citations?user=tN4zV68AAAAJ",
    }
    if set(creator.get("sameAs", [])) != expected_same_as:
        fail(errors, "research-index.json: author sameAs mismatch")

    parts = index.get("hasPart", [])
    if len(parts) != 3:
        fail(errors, "research-index.json: expected three papers")
    for position, (slug, expected) in enumerate(PAPERS.items(), start=1):
        if position > len(parts):
            break
        item = parts[position - 1]
        if item.get("position") != position:
            fail(errors, f"research-index.json: {slug} position mismatch")
        if item.get("name") != f"{expected['title']}: {expected['subtitle']}":
            fail(errors, f"research-index.json: {slug} title mismatch")
        if item.get("version") != VERSION or item.get("pagination") != f"1-{expected['pages']}":
            fail(errors, f"research-index.json: {slug} version or pagination mismatch")
        identifiers = {entry.get("propertyID"): entry.get("value") for entry in item.get("identifier", [])}
        if identifiers != {"DOI": expected["doi"], "SSRN": expected["ssrn"]}:
            fail(errors, f"research-index.json: {slug} identifiers mismatch")
        encoding = item.get("encoding", {})
        if encoding.get("contentUrl") != f"{SITE}/pdf/v{VERSION}/{slug}.pdf":
            fail(errors, f"research-index.json: {slug} PDF URL mismatch")
        if encoding.get("contentSize") != f"{expected['bytes']} bytes" or encoding.get("sha256") != expected["sha256"]:
            fail(errors, f"research-index.json: {slug} PDF preservation metadata mismatch")

    # Preserve the disclosed distinction between manuscript and computational versions.
    provenance_checks = {
        "index.html": ("v6.2 independent reimplementation", "Frozen v5.9 execution"),
        "papers/part1.html": ("verify_part1_contract_v62.py", "not a claim of third-party reproduction"),
        "papers/part3.html": ("frozen v5.9 computational artifacts", "frozen v5.9 computational artifact (p. 35"),
        "llms.txt": ("## Research provenance", "v6.2 independent reimplementation", "frozen v5.9 computational artifacts"),
    }
    for rel, phrases in provenance_checks.items():
        content = (ROOT / rel).read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in content:
                fail(errors, f"{rel}: research provenance disclosure missing: {phrase}")
    for position, markers in enumerate((
        ("v6.2", "verify_part1_contract_v62.py"),
        ("empirical validation is not established",),
        ("v5.9", "synthetic benchmark", "no new execution"),
    )):
        if position >= len(parts):
            break
        provenance = [
            str(entry.get("value", "")) for entry in parts[position].get("additionalProperty", [])
            if entry.get("name") == "Research provenance"
        ]
        if len(provenance) != 1 or not all(marker in provenance[0] for marker in markers):
            fail(errors, f"research-index.json: Part {position + 1} provenance mismatch")

    manifest_expectations = {
        "name": "The Proper Ending Index",
        "id": "/",
        "start_url": "/",
        "scope": "/",
        "lang": "en",
    }
    for key, value in manifest_expectations.items():
        if manifest.get(key) != value:
            fail(errors, f"site.webmanifest: {key} mismatch")

    if not any(x.get("src")=="/maskable-512x512.png" and x.get("purpose")=="maskable" for x in manifest.get("icons", [])):
        fail(errors, "site.webmanifest: missing dedicated maskable icon")

    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    expected_urls = [
        f"{SITE}/",
        f"{SITE}/papers/",
        f"{SITE}/papers/part1.html",
        f"{SITE}/papers/part2.html",
        f"{SITE}/papers/part3.html",
        f"{SITE}/about.html",
        f"{SITE}/colophon.html",
        f"{SITE}/privacy.html",
        f"{SITE}/security.html",
    ]
    actual_urls = re.findall(r"<loc>(.*?)</loc>", sitemap)
    if actual_urls != expected_urls:
        fail(errors, f"sitemap.xml: canonical URL inventory mismatch: {actual_urls}")
    if "<priority>" in sitemap or "<changefreq>" in sitemap or "/demo/" in sitemap or "/pdf/" in sitemap:
        fail(errors, "sitemap.xml contains ignored metadata or non-primary records")
    # Page freshness is not the same as the immutable v6.2 paper revision.
    expected_lastmods = ["2026-11-24"] * 7 + [UPDATED, UPDATED]
    actual_lastmods = re.findall(r"<lastmod>(.*?)</lastmod>", sitemap)
    if actual_lastmods != expected_lastmods:
        fail(errors, f"sitemap.xml: per-page lastmod mismatch: {actual_lastmods}")

    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if f"Sitemap: {SITE}/sitemap.xml" not in robots or f"{SITE}/llms.txt" not in robots:
        fail(errors, "robots.txt: sitemap or LLM orientation missing")
    if "add your A+" in (ROOT / "colophon.html").read_text(encoding="utf-8"):
        fail(errors, "colophon contains placeholder text")
    if (ROOT / "demo/altrion-part3.html").exists():
        fail(errors, "retired Part III prototype must not exist")
    for rel in ALL_HTML[-3:]:
        if "noindex,follow,noarchive" not in (ROOT / rel).read_text(encoding="utf-8"):
            fail(errors, f"{rel}: superseded route is not noindexed")


def main() -> int:
    errors: list[str] = []
    audit_html(errors)
    audit_content(errors)
    audit_assets(errors)
    audit_pdfs(errors)
    audit_scholarly_apparatus(errors)
    audit_indexes(errors)
    if errors:
        print("v6.2 archive verification failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print(f"Verified {len(ALL_HTML)} HTML pages, 3 preserved PDFs, 6 OG images, and the v6.2 metadata contract.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
