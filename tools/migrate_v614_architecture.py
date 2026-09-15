#!/usr/bin/env python3
"""One-shot migration to the v6.14 source architecture.

This script changes authoring structure and the final editorial/SEO layer while
keeping production delivery static, deterministic, and framework-free.
"""

from __future__ import annotations

import ast
import re
import shutil
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "tools/build_site.py"
VERIFY = ROOT / "tools/verify_v62.py"
CSS = ROOT / "assets/site.css"
CRITICAL = ROOT / "assets/critical.css"
JS = ROOT / "assets/site.js"


def node_source(source: str, node: ast.AST) -> str:
    lines = source.splitlines(keepends=True)
    return "".join(lines[node.lineno - 1 : node.end_lineno]).rstrip() + "\n"


def top_level(source: str) -> tuple[dict[str, str], dict[str, str]]:
    tree = ast.parse(source)
    assignments: dict[str, str] = {}
    functions: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions[node.name] = node_source(source, node)
        elif isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            assignments[node.targets[0].id] = node_source(source, node)
    return assignments, functions


def write(path: str, content: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.rstrip() + "\n", encoding="utf-8")


def migrate_build() -> None:
    source = BUILD.read_text(encoding="utf-8")
    assignments, functions = top_level(source)

    required_assignments = [
        "SITE",
        "AUTHOR_ID",
        "SCHOLAR_URL",
        "UPDATED",
        "PAPER_REVISION_DATE",
        "VERSION",
        "ASSET_VERSION",
        "GOOGLE_SITE_VERIFICATION",
        "AUTHOR",
        "PAPERS",
    ]
    required_functions = {
        "paper_url",
        "ssrn_url",
        "article_schema",
        "breadcrumb_schema",
        "breadcrumbs",
        "head",
        "header",
        "footer",
        "shell_page",
        "home_page",
        "papers_index_page",
        "part1_content",
        "part2_content",
        "part3_content",
        "paper_page",
        "about_page",
        "utility_page",
        "legacy_notice",
        "research_index",
        "sitemap",
        "write",
        "main",
    }
    missing = [name for name in required_assignments if name not in assignments]
    missing += [name for name in required_functions if name not in functions]
    if missing:
        raise RuntimeError(f"build migration contract changed; missing {missing}")

    model_assignments: list[str] = []
    for name in required_assignments:
        block = assignments[name]
        if name == "UPDATED":
            block = 'UPDATED = "2026-09-16"\n'
        elif name == "ASSET_VERSION":
            block = 'ASSET_VERSION = "6.14.0"\n'
        elif name == "AUTHOR":
            block = block.replace("AUTHOR = {", "AUTHOR: dict[str, object] = {", 1)
            block = block.replace(
                '        "governing capacity",\n        "Proper Ending",',
                '        "governing capacity",\n        "Procedurally Masked Governing-Capacity Loss",\n        "accountable exit",\n        "Proper Ending",',
            )
        elif name == "PAPERS":
            block = block.replace("PAPERS = [", "PAPERS: list[Paper] = [", 1)
        model_assignments.append(block.rstrip())

    paper_type = '''class Paper(TypedDict):
    part: int
    roman: str
    tone: str
    slug: str
    title: str
    subtitle: str
    description: str
    ssrn: str
    doi: str
    posted: str
    pages: int
    bytes: int
    sha256: str
    function: str
    question: str
    state: str
'''

    model_helpers = "\n\n".join(
        functions[name].rstrip()
        for name in ("paper_url", "ssrn_url", "article_schema", "breadcrumb_schema")
    )
    model_helpers = model_helpers.replace(
        '"isPartOf": {"@id": f"{SITE}/papers/#trilogy"},',
        '"isPartOf": {"@id": SERIES_ID},',
    )
    series_schema = '''def series_schema() -> dict:
    """Return the canonical entity for the three-paper research programme."""
    return {
        "@type": "CreativeWorkSeries",
        "@id": SERIES_ID,
        "name": "Workflow-Centric AI Governance Trilogy",
        "alternateName": "The Proper Ending Index research trilogy",
        "url": f"{SITE}/papers/",
        "description": (
            "Takashi Sato's three-paper research programme on accountable decision "
            "routing, governing-capacity loss, Proper Ending, and Authority Return."
        ),
        "dateModified": UPDATED,
        "version": VERSION,
        "inLanguage": "en-US",
        "isAccessibleForFree": True,
        "creator": {"@id": AUTHOR_ID},
        "hasPart": [{"@id": f"{paper_url(paper)}#article"} for paper in PAPERS],
    }
'''
    model = dedent(
        '''
        """Canonical research metadata for The Proper Ending Index.

        This module is the single source of truth for author identity, paper records,
        identifiers, preservation hashes, publication dates, and the series entity.
        Renderers and QA import from here rather than maintaining parallel copies.
        """

        from __future__ import annotations

        from pathlib import Path
        from typing import TypedDict

        ROOT = Path(__file__).resolve().parents[2]
        '''
    ).strip()
    model += "\n\n" + paper_type.strip() + "\n\n"
    model += "\n\n".join(model_assignments) + "\n\n"
    model = model.replace(
        'AUTHOR_ID = f"{SITE}/about.html#takashi-sato"',
        'AUTHOR_ID = f"{SITE}/about.html#takashi-sato"\nSERIES_ID = f"{SITE}/papers/#trilogy"',
        1,
    )
    model += model_helpers + "\n\n" + series_schema
    model += '\nPAPERS_BY_SLUG: dict[str, Paper] = {paper["slug"]: paper for paper in PAPERS}\n'
    write("src/archive/model.py", model)

    layout = dedent(
        '''
        """Shared document chrome and metadata rendering."""

        from __future__ import annotations

        import json
        from html import escape
        from textwrap import dedent

        from .model import *
        '''
    ).strip()
    layout += "\n\n" + "\n\n".join(
        functions[name].rstrip()
        for name in ("breadcrumbs", "head", "header", "footer", "shell_page")
    )
    layout = layout.replace(
        '          <link rel="canonical" href="{safe_canonical}">',
        '          <link rel="canonical" href="{safe_canonical}">\n'
        '          <link rel="alternate" hreflang="en" href="{safe_canonical}">\n'
        '          <link rel="alternate" hreflang="x-default" href="{safe_canonical}">',
        1,
    )
    write("src/archive/layout.py", layout)

    paper_content = dedent(
        '''
        """Versioned human-readable research summaries for Parts I–III."""

        from __future__ import annotations

        from textwrap import dedent
        '''
    ).strip()
    paper_content += "\n\n" + "\n\n".join(
        functions[name].rstrip() for name in ("part1_content", "part2_content", "part3_content")
    )
    write("src/archive/paper_content.py", paper_content)

    excluded = {
        "paper_url",
        "ssrn_url",
        "article_schema",
        "breadcrumb_schema",
        "breadcrumbs",
        "head",
        "header",
        "footer",
        "shell_page",
        "part1_content",
        "part2_content",
        "part3_content",
        "research_index",
        "sitemap",
        "write",
        "main",
    }
    page_names = [name for name in functions if name not in excluded]
    pages_header = dedent(
        '''
        """Page renderers for the public research archive."""

        from __future__ import annotations

        from html import escape
        from textwrap import dedent

        from .layout import *
        from .model import *
        from .paper_content import part1_content, part2_content, part3_content
        '''
    ).strip()
    page_blocks = {name: functions[name] for name in page_names}

    home = page_blocks["home_page"]
    home = home.replace('"inLanguage": ["en-US", "ja-JP"],', '"inLanguage": "en-US",')
    home = home.replace("            AUTHOR,\n            {", "            AUTHOR,\n            series_schema(),\n            {", 1)
    home = home.replace(
        '<p class="eyebrow">Workflow-Centric AI Governance Trilogy · v6.2</p>',
        '<p class="eyebrow">AI Governance Research Archive · Workflow-Centric Trilogy · v6.2</p>',
    )
    home = home.replace(
        'title="The Proper Ending Index · Takashi Sato",',
        'title="The Proper Ending Index — AI Governance Research Archive · Takashi Sato",',
    )
    home = home.replace(
        'description="Independent research on decision routing, governing-capacity loss, Proper Ending, and Authority Return in AI-assisted institutions.",',
        'description="Takashi Sato’s independent AI governance research archive on accountable decision routing, governing-capacity loss, Proper Ending, and Authority Return.",',
    )
    page_blocks["home_page"] = home

    papers = page_blocks["papers_index_page"]
    papers = papers.replace(
        '            AUTHOR,\n            {\n                "@type": "CollectionPage",\n                "@id": f"{SITE}/papers/#trilogy",',
        '            AUTHOR,\n            series_schema(),\n            {\n                "@type": "CollectionPage",\n                "@id": f"{SITE}/papers/#catalogue",',
        1,
    )
    papers = papers.replace(
        '                "author": {"@id": AUTHOR_ID},\n                "hasPart": [{"@id": f"{paper_url(p)}#article"} for p in PAPERS],',
        '                "author": {"@id": AUTHOR_ID},\n                "mainEntity": {"@id": SERIES_ID},',
        1,
    )
    marker = '    body = dedent(\n'
    map_code = dedent(
        '''
            map_nodes = "\\n".join(
                f'<div class="research-map-node" data-part="{p["part"]}"><span>0{p["part"]}</span><b>{p["function"]}</b><small>{p["question"]}</small></div>'
                for p in PAPERS
            )
        '''
    )
    if marker not in papers:
        raise RuntimeError("papers body marker not found")
    papers = papers.replace(marker, map_code + marker, 1)
    papers = papers.replace(
        '          </header>\n          <section class="section">',
        '          </header>\n'
        '          <section class="research-map-section" aria-label="Trilogy research map">\n'
        '            <div class="shell"><div class="research-map" data-reveal>{map_nodes}</div></div>\n'
        '          </section>\n'
        '          <section class="section">',
        1,
    )
    papers = papers.replace(
        'title="Papers · Workflow-Centric AI Governance Trilogy",',
        'title="AI Governance Working Papers — The Proper Ending Index · Takashi Sato",',
    )
    papers = papers.replace(
        'description="The v6.2 working-paper trilogy by Takashi Sato: decision routing, governing-capacity loss, Proper Ending, and Authority Return.",',
        'description="Takashi Sato’s v6.2 AI governance working-paper trilogy on decision routing, governing-capacity loss, Proper Ending, and Authority Return.",',
    )
    page_blocks["papers_index_page"] = papers

    paper_page = page_blocks["paper_page"]
    paper_page = paper_page.replace(
        '                    AUTHOR,\n                    article_schema(paper),',
        '                    AUTHOR,\n                    series_schema(),\n                    article_schema(paper),',
        1,
    )
    paper_page = paper_page.replace(
        'title=f"{paper[\'title\']} · Part {paper[\'roman\']} · Takashi Sato",',
        'title=f"{paper[\'title\']}: {paper[\'subtitle\']} — Takashi Sato",',
    )
    page_blocks["paper_page"] = paper_page

    about = page_blocks["about_page"]
    about = about.replace(
        'title="Takashi Sato · Independent Researcher",',
        'title="Takashi Sato — AI Governance Researcher · The Proper Ending Index",',
    )
    about = about.replace(
        'description="Author record for Takashi Sato (佐藤貴士), an independent researcher in Sapporo studying accountable human-AI decisions, governing capacity, and institutional exit.",',
        'description="Author record for Takashi Sato (佐藤貴士), an independent AI governance researcher in Sapporo studying accountable decision routing, governing capacity, and institutional exit.",',
    )
    page_blocks["about_page"] = about

    pages = pages_header + "\n\n" + "\n\n".join(page_blocks[name].rstrip() for name in page_names)
    write("src/archive/pages.py", pages)

    feeds = dedent(
        '''
        """Machine-readable archive indexes and canonical URL inventory."""

        from __future__ import annotations

        from .model import *
        '''
    ).strip()
    feeds += "\n\n" + functions["research_index"].rstrip() + "\n\n" + functions["sitemap"].rstrip()
    write("src/archive/feeds.py", feeds)

    write("src/__init__.py", '"""Authoring source for The Proper Ending Index."""')
    write("src/archive/__init__.py", '"""Static publishing model for The Proper Ending Index."""')

    main_source = functions["main"]
    main_source = main_source.replace(
        '<section><h2>Architecture</h2><p>Every public page is pre-rendered static HTML. The first viewport uses a small inline critical style generated from the repository source, followed by one shared deferred stylesheet and one self-contained progressive-enhancement script, including the small local analytics adapter. There is no framework runtime, remote font request, client-side router, account system, or third-party UI package.</p></section>',
        '<section><h2>Architecture</h2><p>Every public page is pre-rendered static HTML from a small source model: canonical research metadata, document chrome, page renderers, source styles, and progressive-enhancement modules. Build output remains one shared stylesheet and one script, with first-viewport rules inlined for immediate paint. There is no framework runtime, remote font request, client-side router, account system, or third-party UI package.</p></section>',
    )
    main_source = main_source.replace(
        '<section><h2>Typography &amp; material</h2><p>The interface pairs Newsreader for editorial display, Inter for navigation and long-form screen text, and Mea Culpa for deliberately scarce calligraphic interaction labels. The author record uses supplied handwritten signature geometry. All three font families are self-hosted under the SIL Open Font License. Three supplied monochrome surfaces have distinct roles: grain as a quiet optical layer, paper around the research records, and brushed metal at institutional boundaries. Functional diagrams remain semantic HTML and CSS so their content is selectable, responsive, and printable.</p></section>',
        '<section><h2>Typography &amp; material</h2><p>The interface pairs Newsreader for editorial display, Inter for navigation and long-form screen text, and Mea Culpa only where a deliberately scarce calligraphic register remains useful. All three font families are self-hosted under the SIL Open Font License. Material depth is generated from light, hairlines, measurement fields, and part-specific color temperature rather than image textures. Functional diagrams remain semantic HTML and CSS so their content is selectable, responsive, and printable.</p></section>',
    )
    main_source = main_source.replace(
        '<section><h2>Interaction</h2><p>Fine-pointer devices receive a difference-blended cursor, magnetic controls, pointer-position lighting, scroll-linked material drift, and cross-document view transitions. Touch, keyboard, and reduced-motion users retain the complete archive without those effects; no research content or action depends on animation or pointer input.</p></section>',
        '<section><h2>Interaction</h2><p>Fine-pointer devices receive an authority-ring cursor, restrained magnetic response, section orientation, and a Proper Ending state that reduces motion as Part III approaches closure. Touch, keyboard, no-JavaScript, and reduced-motion users retain the complete archive; no research content or action depends on animation or pointer input.</p></section>',
    )
    main_source = main_source.replace(
        'Last rebuilt for the v6.2 papers on 24 August 2026.',
        'Source architecture and public records reconciled on 16 September 2026.',
    )
    main_source = main_source.replace("            Last update: 2026-08-24", "            Last update: 2026-09-16")

    orchestrator = dedent(
        '''
        #!/usr/bin/env python3
        """Build The Proper Ending Index from the canonical authoring source."""

        from __future__ import annotations

        import json
        import sys
        from pathlib import Path
        from textwrap import dedent

        ROOT = Path(__file__).resolve().parents[1]
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))

        from src.archive.feeds import research_index, sitemap
        from src.archive.model import PAPERS, SITE
        from src.archive.pages import (
            about_page,
            home_page,
            legacy_notice,
            paper_page,
            papers_index_page,
            utility_page,
        )
        from build_assets import build_assets
        '''
    ).strip()
    orchestrator += "\n\n" + functions["write"].rstrip() + "\n\n"
    orchestrator += main_source.replace("def main() -> None:\n", "def main() -> None:\n    build_assets()\n", 1)
    write("tools/build_site.py", orchestrator)


def migrate_assets() -> None:
    css = CSS.read_text(encoding="utf-8")
    split_marker = "/* v6.13 — State / Authority editorial grammar."
    if split_marker not in css:
        raise RuntimeError("CSS pavilion marker missing")
    base, pavilion_tail = css.split(split_marker, 1)
    pavilion = split_marker + pavilion_tail

    v614 = dedent(
        '''

        /* v6.14 — Research pavilion refinement. */
        /* Semantic aliases make the design system legible in code and in use. */
        :root {
          --surface-archive: var(--paper);
          --ink-primary: var(--ink);
          --ink-secondary: var(--ink-soft);
          --rule-structural: var(--archive-rule);
          --part-i-measure: var(--bronze-soft);
          --part-ii-capacity: var(--ice);
          --part-iii-return: var(--copper);
        }

        body[data-page="home"] .hero .eyebrow {
          display: flex;
          align-items: center;
          gap: .72rem;
          color: color-mix(in srgb, var(--signal-pale) 78%, var(--ink-soft));
        }
        body[data-page="home"] .hero .eyebrow::before {
          content: "";
          width: 2.6rem;
          height: 1px;
          background: var(--signal-soft);
          opacity: .72;
        }

        .research-map-section { padding: 0 0 clamp(2rem,5vw,4.5rem); }
        .research-map {
          position: relative;
          display: grid;
          grid-template-columns: repeat(3,minmax(0,1fr));
          border-top: 1px solid var(--archive-rule);
          border-bottom: 1px solid var(--archive-rule-soft);
        }
        .research-map::before {
          content: "";
          position: absolute;
          top: -1px;
          left: 0;
          width: 100%;
          height: 1px;
          background: linear-gradient(90deg,var(--route-case),var(--route-institution),var(--route-exit));
          opacity: .72;
        }
        .research-map-node {
          min-height: 9rem;
          padding: 1.2rem clamp(.8rem,2vw,1.6rem) 1.35rem 0;
          display: grid;
          align-content: space-between;
          gap: .7rem;
          border-right: 1px solid var(--archive-rule-soft);
        }
        .research-map-node:last-child { border-right: 0; }
        .research-map-node span {
          font-family: var(--mono);
          font-size: .57rem;
          letter-spacing: .08em;
          color: var(--ink-faint);
        }
        .research-map-node b {
          max-width: 15rem;
          font-family: var(--display);
          font-size: clamp(1.35rem,2vw,2rem);
          font-weight: 350;
          letter-spacing: -.03em;
          line-height: 1.05;
        }
        .research-map-node small { color: var(--ink-soft); line-height: 1.45; }
        .research-map-node[data-part="1"] b { color: var(--route-case); }
        .research-map-node[data-part="2"] b { color: var(--route-institution); }
        .research-map-node[data-part="3"] b { color: var(--route-exit); }

        /* Each paper has a distinct physical grammar while remaining one archive. */
        body[data-tone="part-1"] .paper-hero {
          background-image:
            linear-gradient(90deg, transparent 0 72%, rgba(215,191,140,.055) 72% calc(72% + 1px), transparent calc(72% + 1px)),
            linear-gradient(180deg, transparent 0 66%, rgba(215,191,140,.045) 66% calc(66% + 1px), transparent calc(66% + 1px));
        }
        body[data-tone="part-2"] .paper-hero {
          background-image:
            repeating-linear-gradient(180deg, rgba(168,198,210,.022) 0 1px, transparent 1px 3.8rem),
            linear-gradient(90deg, transparent 0 58%, rgba(168,198,210,.035) 58% 58.08%, transparent 58.08%);
        }
        body[data-tone="part-3"] .paper-hero {
          background-image:
            radial-gradient(circle at 82% 58%, transparent 0 8.7rem, rgba(207,129,105,.065) 8.76rem 8.82rem, transparent 8.9rem),
            radial-gradient(circle at 82% 58%, transparent 0 13.4rem, rgba(207,129,105,.035) 13.46rem 13.52rem, transparent 13.6rem);
        }
        body[data-tone="part-1"] .content > section { border-top-color: color-mix(in srgb,var(--part-i-measure) 28%,var(--line)); }
        body[data-tone="part-2"] .content > section { border-top-color: color-mix(in srgb,var(--part-ii-capacity) 24%,var(--line)); }
        body[data-tone="part-3"] .content > section { border-top-color: color-mix(in srgb,var(--part-iii-return) 26%,var(--line)); }

        /* Proper Ending progressively removes interface energy near the terminal state. */
        body[data-page="part3"] .site-footer .footer-links,
        body[data-page="part3"] .site-footer .footer-thesis {
          transition: opacity .8s var(--ease), transform .8s var(--ease);
        }
        html.is-ending body[data-page="part3"] .site-footer .footer-links,
        html.is-ending body[data-page="part3"] .site-footer .footer-thesis {
          opacity: .72;
          transform: translateY(.12rem);
        }
        html.is-ending body[data-page="part3"] .site-footer {
          --signal-glow: transparent;
        }

        @media (max-width:44rem) {
          .research-map { grid-template-columns: 1fr; }
          .research-map-node { min-height: 6.5rem; border-right: 0; border-bottom: 1px solid var(--archive-rule-soft); }
          .research-map-node:last-child { border-bottom: 0; }
          body[data-page="home"] .hero .eyebrow { align-items: flex-start; }
          body[data-page="home"] .hero .eyebrow::before { width: 1.4rem; margin-top: .45rem; flex: 0 0 auto; }
        }

        @media (prefers-reduced-motion:reduce) {
          body[data-page="part3"] .site-footer .footer-links,
          body[data-page="part3"] .site-footer .footer-thesis { transition: none; transform: none; }
        }
        '''
    ).rstrip()
    if "/* v6.14 — Research pavilion refinement. */" not in pavilion:
        pavilion = pavilion.rstrip() + "\n" + v614 + "\n"

    write("src/styles/base.css", base.rstrip())
    write("src/styles/pavilion.css", pavilion.rstrip())

    critical = CRITICAL.read_text(encoding="utf-8")
    critical_add = dedent(
        '''

        /* v6.14 critical identity. */
        body[data-page="home"] .hero .eyebrow {
          display:flex;align-items:center;gap:.72rem;
          color:color-mix(in srgb,var(--signal-pale) 78%,var(--ink-soft));
        }
        body[data-page="home"] .hero .eyebrow::before {
          content:"";width:2.6rem;height:1px;background:var(--signal-soft);opacity:.72;
        }
        body[data-tone="part-1"] .paper-hero {
          background-image:linear-gradient(90deg,transparent 0 72%,rgba(215,191,140,.055) 72% calc(72% + 1px),transparent calc(72% + 1px));
        }
        body[data-tone="part-2"] .paper-hero {
          background-image:repeating-linear-gradient(180deg,rgba(168,198,210,.022) 0 1px,transparent 1px 3.8rem);
        }
        body[data-tone="part-3"] .paper-hero {
          background-image:radial-gradient(circle at 82% 58%,transparent 0 8.7rem,rgba(207,129,105,.065) 8.76rem 8.82rem,transparent 8.9rem);
        }
        @media(max-width:44rem){body[data-page="home"] .hero .eyebrow::before{width:1.4rem;flex:0 0 auto}}
        '''
    ).rstrip()
    if "/* v6.14 critical identity. */" not in critical:
        critical = critical.rstrip() + "\n" + critical_add + "\n"
    write("src/styles/critical.css", critical.rstrip())

    source_js = JS.read_text(encoding="utf-8")
    second = '\n(()=>{"use strict";\nconst d=document;'
    third = "\n(function () {\n  'use strict';"
    if second not in source_js or third not in source_js:
        raise RuntimeError("site.js module boundaries changed")
    core, tail = source_js.split(second, 1)
    gate_body, analytics_body = (second + tail).split(third, 1)
    analytics = third + analytics_body
    write("src/scripts/core.js", core.rstrip())
    write("src/scripts/gate.js", gate_body.rstrip())
    write("src/scripts/analytics.js", analytics.rstrip())

    build_assets = dedent(
        '''
        #!/usr/bin/env python3
        """Compile human-readable source assets into the minimal runtime contract."""

        from __future__ import annotations

        from pathlib import Path

        ROOT = Path(__file__).resolve().parents[1]
        STYLE_SOURCES = (
            ROOT / "src/styles/base.css",
            ROOT / "src/styles/pavilion.css",
        )
        SCRIPT_SOURCES = (
            ROOT / "src/scripts/core.js",
            ROOT / "src/scripts/gate.js",
            ROOT / "src/scripts/analytics.js",
        )

        def join_sources(paths: tuple[Path, ...]) -> str:
            return "\\n\\n".join(path.read_text(encoding="utf-8").rstrip() for path in paths) + "\\n"

        def build_assets() -> None:
            (ROOT / "assets/site.css").write_text(join_sources(STYLE_SOURCES), encoding="utf-8")
            (ROOT / "assets/site.js").write_text(join_sources(SCRIPT_SOURCES), encoding="utf-8")
            critical = (ROOT / "src/styles/critical.css").read_text(encoding="utf-8").rstrip() + "\\n"
            (ROOT / "assets/critical.css").write_text(critical, encoding="utf-8")

        if __name__ == "__main__":
            build_assets()
        '''
    ).strip()
    write("tools/build_assets.py", build_assets)


def migrate_verifier() -> None:
    text = VERIFY.read_text(encoding="utf-8")
    start = text.index('ROOT = Path(__file__).resolve().parents[1]')
    class_at = text.index('\n\nclass AuditParser')
    replacement = dedent(
        '''
        ROOT = Path(__file__).resolve().parents[1]
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))

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
        '''
    ).strip()
    text = text[:start] + replacement + text[class_at:]
    for line in [
        '        "materials/grain.jpg",\n',
        '        "materials/paper.jpg",\n',
        '        "materials/black-metal.jpg",\n',
    ]:
        text = text.replace(line, "")
    material_start = text.find('    material_total = 0\n')
    material_end = text.find('    paper_match = re.search', material_start)
    if material_start < 0 or material_end < 0:
        raise RuntimeError("material verifier block missing")
    text = text[:material_start] + text[material_end:]
    text = text.replace('if index.get("@id") != f"{SITE}/papers/#trilogy":', 'if index.get("@id") != SERIES_ID:')
    home_anchor = '    if GOOGLE_SITE_VERIFICATION not in home:\n        fail(errors, "index.html: Search Console ownership verification is missing")\n'
    home_add = home_anchor + dedent(
        '''
            if "AI Governance Research Archive" not in home:
                fail(errors, "index.html: visible field classification is missing")
            if '"@type":"CreativeWorkSeries"' not in home or SERIES_ID not in home:
                fail(errors, "index.html: canonical research-series entity is missing")
        '''
    )
    if home_anchor not in text:
        raise RuntimeError("home verifier anchor missing")
    text = text.replace(home_anchor, home_add, 1)
    write("tools/verify_v62.py", text)


def migrate_visual_smoke() -> None:
    path = ROOT / "tools/visual_smoke.py"
    text = path.read_text(encoding="utf-8")
    old = dedent(
        '''
        VIEWPORTS = {
            "320": (320, 568),
            "390": (390, 844),
            "768": (768, 1024),
            "1440": (1440, 900),
            "1920": (1920, 1080),
        }
        '''
    ).strip()
    new = dedent(
        '''
        VIEWPORTS = {
            "320": (320, 568),
            "390": (390, 844),
            "430": (430, 932),
            "768": (768, 1024),
            "1024": (1024, 768),
            "1440": (1440, 900),
            "1920": (1920, 1080),
        }
        '''
    ).strip()
    if old not in text:
        raise RuntimeError("visual smoke viewport contract changed")
    text = text.replace(old, new, 1)
    write("tools/visual_smoke.py", text)


def migrate_og() -> None:
    code = dedent(
        '''
        #!/usr/bin/env python3
        """Generate deterministic 1200×630 social cards from the research identity."""

        from __future__ import annotations

        import sys
        from pathlib import Path

        from PIL import Image, ImageDraw, ImageFont

        ROOT = Path(__file__).resolve().parents[1]
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))

        from src.archive.model import PAPERS_BY_SLUG, VERSION

        OUT = ROOT / "assets" / "og"
        W, H = 1200, 630
        SURFACE = (8, 8, 8)
        INK = (242, 240, 233)
        SOFT = (180, 177, 170)
        RULE = (48, 48, 48)
        SIGNAL = (89, 117, 255)
        BRONZE = (215, 191, 140)
        ICE = (168, 198, 210)
        COPPER = (207, 129, 105)

        INTER = ROOT / "assets/fonts/InterVariable.woff2"
        NEWSREADER = ROOT / "assets/fonts/Newsreader-Variable.woff2"
        MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

        def paper_record(slug: str) -> str:
            paper = PAPERS_BY_SLUG[slug]
            return f"SSRN {paper['ssrn']} · DOI {paper['doi'].upper()} · v{VERSION}"

        CARDS = {
            "home": {
                "label": "AI GOVERNANCE RESEARCH ARCHIVE · WORKFLOW-CENTRIC TRILOGY",
                "title": "A role alone is not governance.",
                "subtitle": "Accountability lives in the sequence.",
                "mark": "INDEX",
                "accent": SIGNAL,
                "record": "DECISION ROUTING · GOVERNING CAPACITY · ACCOUNTABLE EXIT",
            },
            "papers": {
                "label": "THE PROPER ENDING INDEX · WORKING PAPERS",
                "title": "Three papers.",
                "subtitle": "One institutional problem.",
                "mark": "I—III",
                "accent": SIGNAL,
                "record": "TAKASHI SATO · v6.2 · 23 AUGUST 2026",
            },
            "about": {
                "label": "AUTHOR RECORD · TAKASHI SATO",
                "title": "Takashi Sato",
                "subtitle": "Independent AI governance researcher · Sapporo, Japan",
                "mark": "TS",
                "accent": SIGNAL,
                "record": "AI GOVERNANCE · PROPER ENDING · AUTHORITY RETURN",
            },
            "part1": {
                "label": "WORKFLOW-CENTRIC AI GOVERNANCE TRILOGY · PART I",
                "title": "Workflow-Centric\\nAI Governance",
                "subtitle": PAPERS_BY_SLUG["part1"]["subtitle"],
                "mark": "I",
                "accent": BRONZE,
                "record": paper_record("part1"),
            },
            "part2": {
                "label": "WORKFLOW-CENTRIC AI GOVERNANCE TRILOGY · PART II",
                "title": "Governing-\\nCapacity Loss",
                "subtitle": PAPERS_BY_SLUG["part2"]["subtitle"],
                "mark": "II",
                "accent": ICE,
                "record": paper_record("part2"),
            },
            "part3": {
                "label": "WORKFLOW-CENTRIC AI GOVERNANCE TRILOGY · PART III",
                "title": "From Governance Drift\\nto Accountable Exit",
                "subtitle": PAPERS_BY_SLUG["part3"]["subtitle"],
                "mark": "III",
                "accent": COPPER,
                "record": paper_record("part3"),
                "title_size": 56,
            },
        }

        def inter(size: int, weight: int = 400, optical: int = 24) -> ImageFont.FreeTypeFont:
            face = ImageFont.truetype(str(INTER), size=size)
            face.set_variation_by_axes([optical, weight])
            return face

        def newsreader(size: int, weight: int = 350, optical: int = 72) -> ImageFont.FreeTypeFont:
            face = ImageFont.truetype(str(NEWSREADER), size=size)
            face.set_variation_by_axes([weight, optical])
            return face

        def mono(size: int) -> ImageFont.FreeTypeFont:
            return ImageFont.truetype(MONO, size=size)

        def wrap(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont, width: int) -> list[str]:
            lines: list[str] = []
            for paragraph in text.split("\\n"):
                words = paragraph.split()
                current = ""
                for word in words:
                    candidate = f"{current} {word}".strip()
                    if draw.textbbox((0, 0), candidate, font=face)[2] <= width or not current:
                        current = candidate
                    else:
                        lines.append(current)
                        current = word
                if current:
                    lines.append(current)
            return lines

        def background(accent: tuple[int, int, int]) -> Image.Image:
            image = Image.new("RGB", (W, H), SURFACE)
            px = image.load()
            ax, ay = 1030, 65
            for y in range(H):
                for x in range(W):
                    distance = ((x - ax) ** 2 + (y - ay) ** 2) ** 0.5
                    glow = max(0.0, 1.0 - distance / 650.0) * 0.10
                    line = 0.016 if (x % 96 == 0 or y % 96 == 0) else 0.0
                    px[x, y] = tuple(min(255, round(SURFACE[i] + accent[i] * glow + 255 * line)) for i in range(3))
            return image

        def render(name: str, data: dict) -> Image.Image:
            accent = data["accent"]
            image = background(accent)
            draw = ImageDraw.Draw(image)
            draw.line((54, 78, 1146, 78), fill=RULE, width=1)
            draw.line((54, 548, 1146, 548), fill=RULE, width=1)
            draw.text((54, 41), data["label"], font=inter(14, 640, 20), fill=accent)

            mark_face = newsreader(170 if len(data["mark"]) < 4 else 92, 300, 72)
            box = draw.textbbox((0, 0), data["mark"], font=mark_face)
            mark_width = box[2] - box[0]
            muted = tuple(round(channel * .28) for channel in accent)
            draw.text((1146 - mark_width, 105), data["mark"], font=mark_face, fill=muted)

            title_size = data.get("title_size", 70 if name.startswith("part") else 88)
            if name == "about":
                title_size = 104
            title_face = newsreader(title_size, 340, 72)
            y = 126
            width = 840 if name == "home" else (900 if name.startswith("part") else 1010)
            step = round(title_size * .86)
            for line in wrap(draw, data["title"], title_face, width):
                draw.text((54, y), line, font=title_face, fill=INK)
                y += step

            subtitle_face = inter(21, 430, 20)
            subtitle_y = max(y + 26, 390)
            for line in wrap(draw, data["subtitle"], subtitle_face, 790)[:3]:
                draw.text((57, subtitle_y), line, font=subtitle_face, fill=SOFT)
                subtitle_y += 31

            draw.rectangle((54, 576, 66, 588), fill=accent)
            draw.text((83, 574), data["record"], font=mono(12), fill=SOFT)
            brand = "THE PROPER ENDING INDEX"
            brand_face = inter(12, 630, 18)
            brand_box = draw.textbbox((0, 0), brand, font=brand_face)
            draw.text((1146 - (brand_box[2] - brand_box[0]), 574), brand, font=brand_face, fill=INK)
            return image

        def render_icon(size: int, inverse: bool = False) -> Image.Image:
            scale = 4
            canvas = size * scale
            background_color = INK if inverse else SURFACE
            foreground = SURFACE if inverse else INK
            image = Image.new("RGB", (canvas, canvas), background_color)
            draw = ImageDraw.Draw(image)
            outer = round(canvas * .18)
            inner = round(canvas * .30)
            draw.arc((outer, outer, canvas - outer, canvas - outer), 42, 318, fill=foreground, width=max(scale, round(canvas * .075)))
            draw.arc((inner, inner, canvas - inner, canvas - inner), 42, 318, fill=foreground, width=max(scale, round(canvas * .055)))
            cy = canvas // 2
            draw.line((round(canvas * .53), cy, round(canvas * .78), cy), fill=SIGNAL, width=max(scale, round(canvas * .045)))
            dot = round(canvas * .055)
            x = round(canvas * .79)
            draw.rectangle((x - dot, cy - dot, x + dot, cy + dot), fill=SIGNAL)
            return image.resize((size, size), Image.Resampling.LANCZOS)

        def main() -> None:
            OUT.mkdir(parents=True, exist_ok=True)
            for name, data in CARDS.items():
                render(name, data).save(OUT / f"{name}.jpg", "JPEG", quality=91, optimize=True, progressive=True, subsampling=0)
            icon_specs = {
                "android-chrome-192x192.png": (192, False),
                "android-chrome-512x512.png": (512, False),
                "apple-touch-icon.png": (180, False),
                "favicon-16x16.png": (16, False),
                "favicon-32x32.png": (32, False),
                "favicon-16x16-dark.png": (16, True),
                "favicon-32x32-dark.png": (32, True),
            }
            for filename, (size, inverse) in icon_specs.items():
                render_icon(size, inverse).save(ROOT / filename, "PNG", optimize=True)
            render_icon(64).save(ROOT / "favicon.ico", format="ICO", sizes=[(16,16),(32,32),(48,48),(64,64)])

        if __name__ == "__main__":
            main()
        '''
    ).strip()
    write("tools/generate_og.py", code)


def migrate_docs() -> None:
    readme = dedent(
        '''
        # The Proper Ending Index

        A static research archive by **Takashi Sato** on AI governance, workflow failure,
        governing-capacity loss, Proper Ending, and Authority Return.

        The interface should expose structure, not decorate content.

        ## Research record

        The public archive preserves version 6.2 of the *Workflow-Centric AI Governance
        Trilogy* (revision date: 23 August 2026). SSRN is the primary external research
        record; `/pdf/v6.2/` contains immutable preserved copies with published byte counts
        and SHA-256 digests.

        | Part | Research function | SSRN | DOI |
        |---|---|---:|---|
        | I | Route the case | 5911063 | 10.2139/ssrn.5911063 |
        | II | Diagnose the institution | 5913703 | 10.2139/ssrn.5913703 |
        | III | End and return authority | 6066430 | 10.2139/ssrn.6066430 |

        ## Architecture

        Authoring source is separated from generated runtime output:

        ```text
        src/archive/        canonical research model + page renderers
        src/styles/         base, pavilion, and critical source styles
        src/scripts/        progressive-enhancement modules
        tools/build_site.py build orchestration
        tools/build_assets.py deterministic CSS/JS compilation
        tools/generate_og.py deterministic social-card generation
        tools/verify_v62.py archive contract verification
        assets/             generated production CSS/JS, fonts, and OG cards
        papers/             generated HTML paper records
        pdf/v6.2/           immutable preserved papers
        ```

        Production remains intentionally small: pre-rendered HTML, one shared stylesheet,
        one progressive-enhancement script, and inline first-viewport CSS. No framework
        runtime, remote font request, client-side router, account system, or UI package.

        ## Build

        ```bash
        python tools/build_site.py
        python tools/generate_og.py
        python tools/verify_v62.py
        ```

        `build_site.py` compiles source assets before rendering pages. CI then rebuilds the
        archive, requires a clean generated diff, validates HTML and accessibility, verifies
        identifiers and preserved PDFs, runs Lighthouse budgets, and captures multi-viewport
        visual smoke screenshots.

        ## Design grammar

        The visual system is derived from research structure:

        - **Part I — measurement / gate / architecture**
        - **Part II — governing-capacity loss / procedural continuity**
        - **Part III — containment / authority return / Proper Ending**

        Motion must express route, state, containment, return, or closure. Retired stage-mark
        notation, liquid/membrane experiments, generic WebGL spectacle, and commercial routes
        are forbidden by project policy.

        ## Claim discipline

        The archive does not present the papers as legal advice, compliance certification,
        operational decision software, or field validation. Exhaustive checks are bounded to
        declared abstractions; synthetic results are not open-world performance; the shared
        official-record corpus supports traceability rather than frequency, prediction, or
        causal sufficiency.

        See `docs/architecture.md`, `docs/visual-grammar.md`, `docs/seo.md`, and
        `docs/governance.md` for the maintained contracts behind the public archive.
        '''
    ).strip()
    write("README.md", readme)

    direction = dedent(
        '''
        # The Proper Ending Index — Design Direction

        ## Position

        The Proper Ending Index is Takashi Sato's independent AI governance research archive.
        It is not a portfolio, consultancy funnel, SaaS product, compliance service, or
        fictional control room.

        The interface exists to clarify four things: what each paper claims; what supports the
        claim; where the claim stops; and which versioned record should be cited.

        ## Spatial grammar

        One archive, three analytical states:

        - **Part I — Gate / Architecture / Measurement.** Old gold, bronze, structural lines,
          explicit passage conditions, and measured orthogonality.
        - **Part II — Capacity Loss / Entropy / Procedural Continuity.** Lead gray, mercury,
          ice blue, stable surfaces with weakening institutional signal, and no theatrical
          collapse.
        - **Part III — Circuit Breaker / Authority Return / Proper Ending.** Black, oxidized
          red, copper, residual heat, containment, convergence, and motion that settles.

        The three papers are connected but must not be represented as one degradation score or
        universal lifecycle.

        ## Typography and material

        Newsreader carries editorial display; Inter carries interface, data, and reading text;
        Mea Culpa is deliberately scarce. Materiality comes from light, hairlines, measurement
        fields, spacing, and color temperature—not wallpaper textures, glassmorphism, or glow.

        ## Interaction

        The archive is complete before JavaScript runs. Enhancement may add orientation,
        authority-ring pointer response, Typed Gate exploration, and terminal settling in Part
        III. The interaction grammar is **route → state → contain → return → settle**.

        Proper Ending is expressed by decreasing interface energy near the terminal state. It
        must never become a generic visualizer or spectacle.

        ## Permanent exclusions

        Do not restore:

        - `序 / 破 / 急` or Jo / Ha / Kyu stage notation;
        - liquid or membrane experiments;
        - gratuitous WebGL or full-screen shader work;
        - generic Part III visualizers without a research mechanism;
        - Services, Samples, pricing, estimates, commissioned-work funnels, Sapporo Investment,
          or Operational Design commercial routes;
        - keyword-stacked visible Japanese SEO copy.

        ## Record hierarchy

        SSRN is the primary external research record. Local PDFs are immutable preserved copies.
        Internal links are exhibition-room entrances; external research records may use `↗`.

        ## Review standard

        A change is ready only when a reader, reviewer, crawler, keyboard user, and future
        maintainer encounter the same current research record. Visual novelty never outranks
        research fidelity, accessibility, performance, preservation, or claim discipline.
        '''
    ).strip()
    write("DESIGN_DIRECTION.md", direction)

    architecture = dedent(
        '''
        # Architecture

        The archive is a static publishing system, not a web application.

        ## Source and output

        `src/` is the authoring source. Root HTML and `assets/site.css`, `assets/site.js`, and
        `assets/critical.css` are deterministic build output committed for GitHub Pages.

        Research metadata has one canonical source: `src/archive/model.py`. Paper titles, DOI,
        SSRN identifiers, publication dates, page counts, preserved-file sizes, and SHA-256
        hashes must not be independently re-entered in renderers or QA.

        ## Dependency direction

        ```text
        model → layout → page renderers → build orchestration
          └──────→ feeds / schema / preservation metadata
        source CSS/JS → build_assets.py → runtime CSS/JS
        model + generated output → verify_v62.py
        ```

        Renderers may depend on the model. The model must never depend on HTML output.
        Verification imports the model but independently inspects generated artifacts.

        ## Runtime contract

        - pre-rendered semantic HTML;
        - one deferred shared CSS file;
        - one progressive-enhancement JS file;
        - inline critical first-viewport CSS;
        - self-hosted fonts;
        - no framework runtime or client-side router;
        - no research action dependent on JavaScript.

        ## Naming

        Code names should describe research semantics (`route`, `capacity`, `authority`,
        `containment`, `ending`) rather than visual tricks (`magic`, `wow`, `liquid`).

        ## Generated-file discipline

        Generated files are committed only when `python tools/build_site.py` and
        `python tools/generate_og.py` have been run. CI rebuilds and rejects uncommitted drift.
        Python bytecode, local screenshots, Lighthouse working directories, and package caches
        are never repository content.
        '''
    ).strip()
    write("docs/architecture.md", architecture)

    visual = dedent(
        '''
        # Visual Grammar

        ## State vocabulary

        The public interface uses five semantic actions: **route, state, contain, return,
        settle**. Every motion or visual response must map to one of them.

        ## Part I

        Measurement, gates, passage conditions, orthogonal structure. Motion introduces and
        aligns; color temperature is bronze / old gold.

        ## Part II

        Procedural continuity with declining governing capacity. The page should remain composed
        while information confidence and institutional signal feel colder and thinner. Do not
        simulate failure with glitch effects.

        ## Part III

        Containment, circuit breaking, authority return, closure. Movement converges and reduces
        toward the footer. The terminal interaction is successful when the interface settles,
        not when it performs a final spectacle.

        ## Global boundaries

        No stage glyphs, liquid, glassmorphism, decorative dashboards, generic neon, cursor
        trails, particle fields, or arbitrary animation. Internal routes read as editorial
        entrances rather than product CTA buttons.
        '''
    ).strip()
    write("docs/visual-grammar.md", visual)

    seo = dedent(
        '''
        # Search and Entity Contract

        SEO follows the research record; it does not add visible keyword copy that a reader would
        not otherwise need.

        ## Entity graph

        ```text
        Takashi Sato / 佐藤貴士
          → The Proper Ending Index
          → Workflow-Centric AI Governance Trilogy
          → Part I / Part II / Part III
          → DOI / SSRN / immutable preserved PDF
        ```

        Person identity is anchored by ORCID, SSRN Author ID, Google Scholar, and the author page.
        `CreativeWorkSeries` is the canonical trilogy entity. Each `ScholarlyArticle` points back
        to that series and carries its own DOI, SSRN identifier, publication date, revision date,
        pagination, and preserved-file metadata.

        ## Visible field classification

        Home identifies itself as an **AI Governance Research Archive**. The phrase is an honest
        classification, not a search-keyword block.

        ## Canonical surfaces

        The indexed primary routes are Home, Papers, About, Parts I–III, Colophon, Privacy, and
        Security. SSRN remains primary for paper publication records; `/pdf/v6.2/` is preserved
        local access and is not the primary reading route.

        ## Japanese identity

        `佐藤貴士` remains in the factual author record and machine-readable Person identity.
        There is no parallel Japanese presentation layer unless a complete editorial Japanese
        edition is intentionally created in the future.
        '''
    ).strip()
    write("docs/seo.md", seo)

    governance = dedent(
        '''
        # Repository Governance

        ## May change

        Research revisions, new papers, verified identifiers, accessibility fixes, performance
        work, and interactions that directly express the research model may change the archive.

        ## Must not return

        Retired stage notation (`序 / 破 / 急`), liquid/membrane experiments, generic WebGL,
        commercial service routes, mutable PDF aliases, keyword-stacked Japanese presentation
        copy, or an ungrounded Part III visualizer.

        ## Release gate

        Visual changes require Archive QA, Web Quality Gate, and Visual Smoke. Generated output
        must be deterministic. A passing structural test is not evidence of visual quality; the
        screenshot artifact is part of release review.

        ## Proper Ending for the site itself

        The archive is not improved by perpetual redesign. Once a release passes its research,
        visual, accessibility, performance, and search contracts, it should be allowed to remain
        still until new evidence or a new research mechanism justifies change.
        '''
    ).strip()
    write("docs/governance.md", governance)

    gitignore = dedent(
        '''
        __pycache__/
        *.py[cod]
        .DS_Store
        node_modules/
        .lighthouseci/
        artifacts/
        playwright-report/
        test-results/
        *.log
        '''
    ).strip()
    write(".gitignore", gitignore)


def clean_repository() -> None:
    for target in [ROOT / "tools/__pycache__", ROOT / "assets/materials"]:
        if target.exists():
            shutil.rmtree(target)


def main() -> None:
    migrate_build()
    migrate_assets()
    migrate_verifier()
    migrate_visual_smoke()
    migrate_og()
    migrate_docs()
    clean_repository()
    print("v6.14 architecture migration prepared")


if __name__ == "__main__":
    main()
