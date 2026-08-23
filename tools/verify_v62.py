#!/usr/bin/env python3
"""Repository-level QA for The Proper Ending Index v6.2."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

from PIL import Image
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://takashisato.me"
AUTHOR_ID = f"{SITE}/about.html#takashi-sato"
UPDATED = "2026-08-23"
VERSION = "6.2"
ASSET_VERSION = "6.10.3"
GOOGLE_SITE_VERIFICATION = "ESXaqBbWmxcZWPt2W_eI3ROS20FTy-KOziE5jfw0OSM"
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
PAPERS = {
    "part1": {
        "title": "Workflow-Centric AI Governance",
        "subtitle": "A Typed Gate Contract for Accountable Human-AI Decisions",
        "ssrn": "5911063",
        "doi": "10.2139/ssrn.5911063",
        "pages": 18,
        "bytes": 514075,
        "sha256": "edf19f110f6b0302765e29d2dfa20ddb2cbea299ea93b9c30a6a98411f73c2e8",
    },
    "part2": {
        "title": "Procedural Continuity and Governing-Capacity Loss in AI-Assisted Institutions",
        "subtitle": "A Descriptive State Model with Pre-Abuse Collapse as a Provisional Etiological Subtype",
        "ssrn": "5913703",
        "doi": "10.2139/ssrn.5913703",
        "pages": 20,
        "bytes": 562947,
        "sha256": "6cb7a21940caa3c62a20820f8156d8d684317ad8db3a0be8c4ceb8b85d1d5e88",
    },
    "part3": {
        "title": "From Governance Drift to Accountable Exit",
        "subtitle": "Proper Ending and Authority Return in AI-Assisted Institutions",
        "ssrn": "6066430",
        "doi": "10.2139/ssrn.6066430",
        "pages": 39,
        "bytes": 1032918,
        "sha256": "7cda8695056f7268d4ef9ffb794ac29022e478ff087b646c339f800b9fe1ef72",
    },
}


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
        if parser.inline_executable_scripts:
            fail(errors, f"{rel}: executable inline script conflicts with production CSP at lines {parser.inline_executable_scripts}")
        if parser.section_without_heading:
            fail(errors, f"{rel}: section elements lack headings at lines {parser.section_without_heading}")
        if parser.article_without_heading:
            fail(errors, f"{rel}: article elements lack headings at lines {parser.article_without_heading}")
        for tag, attrs in parser.tags:
            if tag == "div" and attrs.get("aria-label") and not attrs.get("role"):
                fail(errors, f"{rel}: generic div with aria-label requires an explicit role")

        expected_stylesheet = f"/assets/archive-v62.css?v={ASSET_VERSION}"
        expected_enhancement = f"/assets/archive-v62.js?v={ASSET_VERSION}"
        styles = [attrs.get("href", "") for tag, attrs in parser.tags if tag == "link" and attrs.get("rel") == "stylesheet"]
        if styles != [expected_stylesheet]:
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
        if expected_enhancement not in text.partition("</head>")[0]:
            fail(errors, f"{rel}: enhancement script is not loaded from head")

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
                "citation_publication_date": "2026/08/23",
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
            expected_pdf = f"{SITE}/pdf/{slug}.pdf"
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
    for identity in ["佐藤貴士　札幌", "Sapporo", "0009-0003-1584-6965", "tN4zV68AAAAJ", "9540672"]:
        if identity not in about:
            fail(errors, f"about.html: identity element missing: {identity}")
    for stale_copy in ["佐藤貴士について", "現在の研究では、人間が形式上", "AIガバナンス、人間による監督、ワークフロー・ガバナンス"]:
        if stale_copy in about:
            fail(errors, f"about.html: verbose Japanese profile copy returned: {stale_copy}")
    if "mailto:" in about or ">Contact<" in about:
        fail(errors, "about.html: direct contact route must remain outside the author record")
    if about.count('lang="ja"') != 1 or about.count("佐藤貴士　札幌") != 1:
        fail(errors, "about.html: visible Japanese identity must be exactly one instance of 佐藤貴士　札幌")

    home = (ROOT / "index.html").read_text(encoding="utf-8")
    if GOOGLE_SITE_VERIFICATION not in home:
        fail(errors, "index.html: Search Console ownership verification is missing")

    for slug, paper in PAPERS.items():
        text = (ROOT / f"papers/{slug}.html").read_text(encoding="utf-8")
        for value in [paper["title"], paper["subtitle"], paper["ssrn"], paper["doi"], "v6.2", paper["sha256"]]:
            if str(value) not in text:
                fail(errors, f"papers/{slug}.html: missing {value}")


def audit_assets(errors: list[str]) -> None:
    expected_assets = {
        "archive-v62.css",
        "archive-v62.js",
        "archive-v66.css",
        "site-analytics.js",
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

    css = (ROOT / "assets/archive-v62.css").read_text(encoding="utf-8")
    progressive_css = (ROOT / "assets/archive-v66.css").read_text(encoding="utf-8")
    js = (ROOT / "assets/archive-v62.js").read_text(encoding="utf-8")
    if "!important" in css:
        fail(errors, "archive stylesheet must not use !important")
    if css.count("{") != css.count("}"):
        fail(errors, "archive stylesheet has unbalanced braces")
    if progressive_css.count("{") != progressive_css.count("}"):
        fail(errors, "progressive stylesheet has unbalanced braces")
    for token in [":focus-visible", "::selection", "prefers-reduced-motion", "@media print", "cursor-orbit", "animation-timeline"]:
        if token not in css:
            fail(errors, f"archive stylesheet missing {token}")
    for token in ["序", "破", "急", "Aoyagi Kouzan T", "prefers-reduced-motion", "forced-colors", "@media print"]:
        if token not in progressive_css:
            fail(errors, f"progressive stylesheet missing {token}")
    for token in ["pointermove", "requestAnimationFrame", "has-custom-cursor", "archive-v66.css"]:
        if token not in js:
            fail(errors, f"enhancement script missing {token}")
    if len(css.encode()) > 50_000:
        fail(errors, f"archive stylesheet exceeds 50 KB: {len(css.encode())}")
    if len(progressive_css.encode()) > 25_000:
        fail(errors, f"progressive stylesheet exceeds 25 KB: {len(progressive_css.encode())}")
    if len(js.encode()) > 7_000:
        fail(errors, f"enhancement script exceeds 7 KB: {len(js.encode())}")
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
        license_text = license_path.read_text(encoding="utf-8")
        if "SIL OPEN FONT LICENSE Version 1.1" not in license_text:
            fail(errors, f"{family} license record is missing or invalid")
        if font_path.name not in css:
            fail(errors, f"archive stylesheet does not declare {family}")
    if "InstrumentSans" in css or "font-stretch" in css or '"wdth"' in css:
        fail(errors, "superseded compressed Instrument Sans typography returned")
    for stale_color in ["#ac402d", "#e6755c", "rgba(172, 64, 45", "rgba(230, 117, 92"]:
        if stale_color in css or stale_color in progressive_css:
            fail(errors, f"superseded vermilion signal returned: {stale_color}")

    material_total = 0
    for name in ["grain", "paper", "black-metal"]:
        path = ROOT / f"assets/materials/{name}.jpg"
        material_total += path.stat().st_size
        with Image.open(path) as image:
            if image.format != "JPEG":
                fail(errors, f"{path.relative_to(ROOT)}: expected JPEG, found {image.format}")
            if image.width < 1500 or image.height < 850:
                fail(errors, f"{path.relative_to(ROOT)}: material resolution is too small: {image.size}")
        if f"materials/{name}.jpg" not in css:
            fail(errors, f"archive stylesheet does not use {name}.jpg")
    if material_total > 350_000:
        fail(errors, f"material texture payload exceeds 350 KB: {material_total}")

    paper_match = re.search(r"--paper:\s*(#[0-9a-fA-F]{6})", css)
    if not paper_match:
        fail(errors, "archive stylesheet is missing the paper color token")
    else:
        paper = paper_match.group(1)
        text_colors = set(re.findall(r"--(?:ink|ink-soft|ink-faint|signal-soft):\s*(#[0-9a-fA-F]{6})", css))
        for color in sorted(text_colors):
            ratio = contrast_ratio(color, paper)
            if ratio < 4.5:
                fail(errors, f"text color {color} has insufficient contrast on {paper}: {ratio:.2f}:1")
        accent_colors = set(re.findall(r"--signal:\s*(#[0-9a-fA-F]{6})", css))
        for color in sorted(accent_colors):
            ratio = contrast_ratio(color, "#ffffff")
            if ratio < 4.5:
                fail(errors, f"white text has insufficient contrast on accent {color}: {ratio:.2f}:1")

    for name in ["home", "papers", "about", *PAPERS]:
        path = ROOT / f"assets/og/{name}.jpg"
        if not path.exists():
            fail(errors, f"missing OG image: {path.relative_to(ROOT)}")
            continue
        with Image.open(path) as image:
            if image.size != (1200, 630):
                fail(errors, f"{path.relative_to(ROOT)}: expected 1200x630, found {image.size}")
            if image.format != "JPEG":
                fail(errors, f"{path.relative_to(ROOT)}: expected JPEG, found {image.format}")
    for name, size in {
        "android-chrome-192x192.png": (192, 192),
        "android-chrome-512x512.png": (512, 512),
        "apple-touch-icon.png": (180, 180),
        "favicon-16x16.png": (16, 16),
        "favicon-32x32.png": (32, 32),
    }.items():
        path = ROOT / name
        if not path.exists():
            fail(errors, f"missing icon: {name}")
            continue
        with Image.open(path) as image:
            if image.size != size:
                fail(errors, f"{name}: expected {size}, found {image.size}")


def audit_pdfs(errors: list[str]) -> None:
    for slug, expected in PAPERS.items():
        path = ROOT / f"pdf/{slug}.pdf"
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


def audit_indexes(errors: list[str]) -> None:
    index = json.loads((ROOT / "research-index.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "site.webmanifest").read_text(encoding="utf-8"))
    if index.get("@context") != "https://schema.org" or index.get("@type") != "CreativeWorkSeries":
        fail(errors, "research-index.json: expected a Schema.org CreativeWorkSeries")
    if index.get("@id") != f"{SITE}/papers/#trilogy":
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
        if encoding.get("contentUrl") != f"{SITE}/pdf/{slug}.pdf":
            fail(errors, f"research-index.json: {slug} PDF URL mismatch")
        if encoding.get("contentSize") != f"{expected['bytes']} bytes" or encoding.get("sha256") != expected["sha256"]:
            fail(errors, f"research-index.json: {slug} PDF preservation metadata mismatch")

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
    if sitemap.count(f"<lastmod>{UPDATED}</lastmod>") != len(expected_urls):
        fail(errors, "sitemap.xml: lastmod contract mismatch")

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
