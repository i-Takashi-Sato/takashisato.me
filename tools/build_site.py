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

def write(path: str, content: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")

def main() -> None:
    build_assets()
    write("index.html", home_page())
    write("papers/index.html", papers_index_page())
    for paper in PAPERS:
        write(f"papers/{paper['slug']}.html", paper_page(paper))
    write("about.html", about_page())

    write(
        "privacy.html",
        utility_page(
            slug="privacy.html",
            title="Privacy",
            description="Privacy information for The Proper Ending Index.",
            content=dedent(
                """
                <section><h2 class="sr-only">Overview</h2><p class="lead">This is a static research archive. It provides no user accounts, advertising, profiling, or first-party cookies.</p></section>
                <section><h2>Measurement</h2><p>A small local adapter emits aggregate page and link events inside the browser. It does not transmit data by itself. If a compatible external analytics property is configured, it is intended for aggregate archive measurement rather than identifying visitors or building advertising profiles.</p></section>
                <section><h2>Hosting logs</h2><p>The hosting and network providers may process standard operational logs such as IP address, user agent, requested path, and timestamp for delivery, abuse prevention, and security.</p></section>
                <section><h2>External records</h2><p>Links to SSRN, DOI, ORCID, and Google Scholar lead to services governed by their own privacy policies.</p></section>
                <section><h2>Contact</h2><p>Privacy questions may be sent to <a href="mailto:i@takashisato.me">i@takashisato.me</a>.</p><p>Last updated: 23 August 2026.</p></section>
                """
            ).strip(),
        ),
    )
    write(
        "security.html",
        utility_page(
            slug="security.html",
            title="Security",
            description="Security contact and disclosure information for The Proper Ending Index.",
            content=dedent(
                """
                <section><h2 class="sr-only">Overview</h2><p class="lead">If you believe you have found a security issue affecting this archive, please report it privately.</p><div class="hero-actions"><a class="button primary" href="mailto:i@takashisato.me">i@takashisato.me</a><a class="button" href="/.well-known/security.txt">security.txt</a></div></section>
                <section><h2>Scope</h2><p>The site is a static GitHub Pages archive with no login, application database, server-side form, or payment surface. Reports should include the affected URL, reproducible steps, impact, and any safe proof of concept.</p></section>
                """
            ).strip(),
        ),
    )
    write(
        "colophon.html",
        utility_page(
            slug="colophon.html",
            title="Colophon",
            description="Design, technology, and preservation notes for The Proper Ending Index.",
            content=dedent(
                """
                <section><h2 class="sr-only">Overview</h2><p class="lead">The archive is designed for legibility, evidence traceability, and long-term survival—not for product conversion or decorative spectacle.</p></section>
                <section><h2>Architecture</h2><p>Every public page is pre-rendered static HTML from a small source model: canonical research metadata, document chrome, page renderers, source styles, and progressive-enhancement modules. Build output remains one shared stylesheet and one script, with first-viewport rules inlined for immediate paint. There is no framework runtime, remote font request, client-side router, account system, or third-party UI package.</p></section>
                <section><h2>Typography &amp; material</h2><p>The interface pairs Newsreader for editorial display, Inter for navigation and long-form screen text, and Mea Culpa only where a deliberately scarce calligraphic register remains useful. All three font families are self-hosted under the SIL Open Font License. Material depth is generated from light, hairlines, measurement fields, and part-specific color temperature rather than image textures. Functional diagrams remain semantic HTML and CSS so their content is selectable, responsive, and printable.</p></section>
                <section><h2>Interaction</h2><p>Fine-pointer devices receive an authority-ring cursor, restrained magnetic response, section orientation, and a Proper Ending state that reduces motion as Part III approaches closure. Touch, keyboard, no-JavaScript, and reduced-motion users retain the complete archive; no research content or action depends on animation or pointer input.</p></section>
                <section><h2>Accessibility</h2><p>Landmarks, heading order, skip links, keyboard-visible focus, 44-pixel navigation targets, reduced-motion behavior, high-contrast text, and print styles are part of the base system.</p></section>
                <section><h2>Preservation</h2><p>SSRN remains the primary external research record. Versioned local PDFs are preserved with file size and SHA-256 recorded on each paper page and in <a href="/research-index.json">research-index.json</a>.</p></section>
                <section><h2>Build</h2><p>The site is generated by a dependency-free Python script and checked by a repository validator in continuous integration. Source architecture and public records reconciled on 16 September 2026.</p></section>
                """
            ).strip(),
        ),
    )
    write(
        "404.html",
        utility_page(
            slug="404.html",
            title="Record not found",
            description="The requested record is not part of The Proper Ending Index.",
            robots="noindex,follow",
            content='<section><h2 class="sr-only">Overview</h2><p class="lead">This path does not resolve to a current archive record.</p><div class="hero-actions"><a class="button primary" href="/">Open the index</a><a class="button" href="/papers/">Browse papers</a></div></section>',
        ),
    )

    write("demo/index.html", legacy_notice(path="/demo/"))
    write("demo/altrion-part1.html", legacy_notice(path="/demo/altrion-part1.html", part=1))
    write("demo/altrion-part2.html", legacy_notice(path="/demo/altrion-part2.html", part=2))

    write("research-index.json", json.dumps(research_index(), ensure_ascii=False, indent=2) + "\n")
    write("sitemap.xml", sitemap())
    write(
        "robots.txt",
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n# Archive orientation: {SITE}/llms.txt\n",
    )
    write(
        "llms.txt",
        dedent(
            f"""
            # The Proper Ending Index

            > Independent research archive by Takashi Sato on workflow-centric AI governance, governing-capacity loss, Proper Ending, and Authority Return.

            Canonical site: {SITE}/
            Author: Takashi Sato (佐藤貴士), Independent Researcher, Sapporo, Japan
            ORCID: https://orcid.org/0009-0003-1584-6965
            SSRN author record: https://papers.ssrn.com/Sol3/Cf_Dev/AbsByAuth.cfm?per_id=9540672
            Machine-readable index: {SITE}/research-index.json
            Current paper version: 6.2 (23 August 2026)

            ## Papers

            - Part I — Workflow-Centric AI Governance: A Typed Gate Contract for Accountable Human-AI Decisions
              {SITE}/papers/part1.html
              DOI: 10.2139/ssrn.5911063
            - Part II — Procedural Continuity and Governing-Capacity Loss in AI-Assisted Institutions: A Descriptive State Model with Pre-Abuse Collapse as a Provisional Etiological Subtype
              {SITE}/papers/part2.html
              DOI: 10.2139/ssrn.5913703
            - Part III — From Governance Drift to Accountable Exit: Proper Ending and Authority Return in AI-Assisted Institutions
              {SITE}/papers/part3.html
              DOI: 10.2139/ssrn.6066430

            ## Interpretation boundary

            - These are working papers, not legal advice, compliance certification, or an operational decision service.
            - Exhaustive finite checks are exhaustive only over each declared abstraction.
            - Synthetic results are implementation and stress-test results, not field sensitivity, specificity, or effectiveness.
            - The shared official-record corpus supports traceability, not frequency, prediction, causal sufficiency, or independent validation.
            - Earlier ALTRION visualizers are superseded and do not represent v6.2.
            """
        ).strip()
        + "\n",
    )
    write(
        "humans.txt",
        dedent(
            """
            /* AUTHOR */
            Takashi Sato / 佐藤貴士
            Independent Researcher
            Sapporo, Hokkaido, Japan
            ORCID: 0009-0003-1584-6965

            /* SITE */
            The Proper Ending Index
            Static HTML, CSS, and progressive JavaScript
            Three self-hosted type families; no framework runtime
            Current research version: 6.2
            Last update: 2026-09-16

            /* ORIENTATION */
            https://takashisato.me/llms.txt
            https://takashisato.me/research-index.json
            """
        ).strip()
        + "\n",
    )
    write(
        "site.webmanifest",
        json.dumps(
            {
                "name": "The Proper Ending Index",
                "short_name": "Proper Ending",
                "description": "Takashi Sato's independent AI governance research archive.",
                "id": "/",
                "start_url": "/",
                "scope": "/",
                "display": "standalone",
                "lang": "en",
                "background_color": "#080808",
                "theme_color": "#080808",
                "icons": [
                    {"src": "/android-chrome-192x192.png", "sizes": "192x192", "type": "image/png"},
                    {"src": "/android-chrome-512x512.png", "sizes": "512x512", "type": "image/png"},
                ],
            },
            indent=2,
        )
        + "\n",
    )
    write(
        ".well-known/security.txt",
        "Contact: mailto:i@takashisato.me\nExpires: 2027-08-23T00:00:00.000Z\nPreferred-Languages: en, ja\nCanonical: https://takashisato.me/.well-known/security.txt\nPolicy: https://takashisato.me/security.html\n",
    )

if __name__ == "__main__":
    main()
