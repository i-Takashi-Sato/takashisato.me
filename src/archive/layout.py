"""Shared document chrome and metadata rendering."""

from __future__ import annotations

import json
from html import escape
from textwrap import dedent

from .model import (
    ASSET_VERSION,
    GOOGLE_SITE_VERIFICATION,
    PAPER_REVISION_DATE,
    ROOT,
    SCHOLAR_URL,
    SITE,
    VERSION,
    Paper,
)


def breadcrumbs(items: list[tuple[str, str | None]]) -> str:
    rendered: list[str] = []
    for label, path in items:
        safe_label = escape(label)
        if path is None:
            rendered.append(f'<li><span aria-current="page">{safe_label}</span></li>')
        else:
            rendered.append(f'<li><a href="{path}">{safe_label}</a></li>')
    return '<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>' + "".join(rendered) + "</ol></nav>"


def head(
    *,
    title: str,
    description: str,
    path: str,
    image: str,
    schema: dict[str, object] | list[dict[str, object]] | None = None,
    robots: str = "index,follow,max-image-preview:large",
    og_type: str = "website",
    paper: Paper | None = None,
    site_verification: bool = False,
) -> str:
    canonical = f"{SITE}{path}"
    safe_title = escape(title, quote=True)
    safe_description = escape(description, quote=True)
    safe_canonical = escape(canonical, quote=True)
    critical_css = (ROOT / "assets/critical.css").read_text(encoding="utf-8").strip()

    schema_html = ""
    if schema:
        schema_html = (
            '<script type="application/ld+json">'
            + json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
            + "</script>"
        )

    verification_html = (
        f'<meta name="google-site-verification" content="{GOOGLE_SITE_VERIFICATION}">'
        if site_verification
        else ""
    )

    paper_meta = ""
    if paper:
        full_title = escape(f"{paper['title']}: {paper['subtitle']}", quote=True)
        paper_meta = dedent(
            f"""
            <meta name="citation_title" content="{full_title}">
            <meta name="citation_author" content="Takashi Sato">
            <meta name="citation_publication_date" content="{paper['posted'].replace('-', '/')}">
            <meta name="citation_doi" content="{paper['doi']}">
            <meta name="citation_language" content="en">
            <link rel="alternate" type="application/pdf" title="Preserved PDF · v{VERSION}" href="{SITE}/pdf/v{VERSION}/{paper['slug']}.pdf">
            <meta property="article:published_time" content="{paper['posted']}">
            <meta property="article:modified_time" content="{PAPER_REVISION_DATE}">
            <meta property="article:author" content="{SITE}/about.html">
            """
        ).strip()

    return dedent(
        f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
          <meta name="color-scheme" content="dark">
          <meta name="theme-color" content="#080808">
          <title>{safe_title}</title>
          <meta name="description" content="{safe_description}">
          <meta name="author" content="Takashi Sato">
          <meta name="robots" content="{robots}">
          {verification_html}
          <link rel="canonical" href="{safe_canonical}">
          <link rel="alternate" hreflang="en" href="{safe_canonical}">
          <link rel="alternate" hreflang="x-default" href="{safe_canonical}">
          <link rel="author" href="/about.html">
          <link rel="me" href="https://orcid.org/0009-0003-1584-6965">
          <link rel="me" href="https://papers.ssrn.com/Sol3/Cf_Dev/AbsByAuth.cfm?per_id=9540672">
          <link rel="me" href="{SCHOLAR_URL}">
          <link rel="manifest" href="/site.webmanifest">
          <link rel="icon" href="/favicon.svg" type="image/svg+xml" media="(prefers-color-scheme: light)">
          <link rel="icon" href="/favicon-dark.svg" type="image/svg+xml" media="(prefers-color-scheme: dark)">
          <link rel="alternate icon" href="/favicon.ico">
          <link rel="apple-touch-icon" href="/apple-touch-icon.png">
          <link rel="preload" href="/assets/fonts/Newsreader-Variable.woff2" as="font" type="font/woff2" crossorigin fetchpriority="high">
          <link rel="preload" href="/assets/fonts/InterVariable.woff2" as="font" type="font/woff2" crossorigin fetchpriority="low">
          <meta property="og:type" content="{og_type}">
          <meta property="og:locale" content="en_US">
          <meta property="og:site_name" content="The Proper Ending Index">
          <meta property="og:title" content="{safe_title}">
          <meta property="og:description" content="{safe_description}">
          <meta property="og:url" content="{safe_canonical}">
          <meta property="og:image" content="{SITE}{image}">
          <meta property="og:image:type" content="image/jpeg">
          <meta property="og:image:width" content="1200">
          <meta property="og:image:height" content="630">
          <meta property="og:image:alt" content="The Proper Ending Index — {safe_title}">
          <meta name="twitter:card" content="summary_large_image">
          <meta name="twitter:title" content="{safe_title}">
          <meta name="twitter:description" content="{safe_description}">
          <meta name="twitter:image" content="{SITE}{image}">
          <meta name="twitter:image:alt" content="The Proper Ending Index — {safe_title}">
          {paper_meta}
          {schema_html}
          <link rel="preload" href="/assets/site.css?v={ASSET_VERSION}" as="style">
          <link rel="stylesheet" href="/assets/site.css?v={ASSET_VERSION}">
          <style data-critical>{critical_css}</style>
          <script src="/assets/site.js?v={ASSET_VERSION}" defer></script>
        </head>
        """
    ).strip()


def header(active: str = "") -> str:
    def current(name: str) -> str:
        return ' aria-current="page"' if active == name else ""

    return dedent(
        f"""
        <a class="skip-link" href="#main">Skip to content</a>
        <header class="site-header">
          <div class="header-inner">
            <a class="brand" href="/" aria-label="The Proper Ending Index — home">
              <img class="brand-mark" src="/favicon.svg" width="29" height="29" alt="">
              <span>The Proper Ending Index</span>
            </a>
            <nav class="site-nav" aria-label="Primary navigation">
              <a href="/"{current('index')}>Index</a>
              <a href="/papers/"{current('papers')}>Papers</a>
              <a href="/about.html"{current('about')}>Author</a>
            </nav>
          </div>
          <div class="scroll-meter" aria-hidden="true"></div>
        </header>
        """
    ).strip()


def footer() -> str:
    return dedent(
        f"""
        <footer class="site-footer">
          <div class="shell">
            <a class="footer-wordmark" href="/" aria-label="The Proper Ending Index — home">Proper Ending</a>
            <div class="footer-grid">
              <div>
                <p class="eyebrow">The Proper Ending Index</p>
                <p class="footer-thesis">An independent research archive on decision routing, governing capacity, and accountable exit in AI-assisted institutions.</p>
              </div>
              <div class="footer-links">
                <div>
                  <p class="label">Research</p>
                  <a href="/papers/">Paper trilogy</a>
                  <a href="/research-index.json">Machine-readable index</a>
                  <a href="/llms.txt">LLM orientation</a>
                </div>
                <div>
                  <p class="label">Identity</p>
                  <a href="https://orcid.org/0009-0003-1584-6965" target="_blank" rel="me noopener noreferrer">ORCID ↗</a>
                  <a href="https://papers.ssrn.com/Sol3/Cf_Dev/AbsByAuth.cfm?per_id=9540672" target="_blank" rel="me noopener noreferrer">SSRN ↗</a>
                  <a href="{SCHOLAR_URL}" target="_blank" rel="me noopener noreferrer">Google Scholar ↗</a>
                </div>
                <div>
                  <p class="label">Site</p>
                  <a href="/about.html">Author record</a>
                  <a href="/colophon.html">Colophon</a>
                  <a href="/privacy.html">Privacy</a>
                  <a href="/security.html">Security</a>
                </div>
              </div>
            </div>
            <div class="footer-bottom">
              <span>© 2026 Takashi Sato</span>
              <span>Independent research · Sapporo, Japan</span>
            </div>
          </div>
        </footer>
        """
    ).strip()


def shell_page(
    *,
    head_html: str,
    body: str,
    active: str = "",
    tone: str = "neutral",
    page: str = "",
) -> str:
    return (
        f'{head_html}\n<body data-tone="{tone}" data-page="{page}">\n'
        f'{header(active)}\n{body}\n{footer()}\n</body>\n</html>\n'
    )
