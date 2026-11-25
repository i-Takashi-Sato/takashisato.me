"""Shared document chrome and metadata rendering."""

from __future__ import annotations

import json
from html import escape
from textwrap import dedent

from .runtime_assets import runtime_url
from .model import (
    GOOGLE_SITE_VERIFICATION,
    PAPER_REVISION_DATE,
    SCHOLAR_URL,
    SITE,
    SITE_NAME,
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
            rendered.append(f'<li><a href="{escape(path, quote=True)}">{safe_label}</a></li>')
    return '<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>' + "".join(rendered) + "</ol></nav>"


def json_ld(schema: dict[str, object] | list[dict[str, object]]) -> str:
    """Serialize metadata without allowing a literal HTML script end tag."""
    payload = json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
    return '<script type="application/ld+json">' + payload.replace("<", "\\u003c") + "</script>"


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
    image_kind = image.rsplit("/",1)[-1]
    image_alt = {
        "home.jpg": "A role alone is not governance. Takashi Sato, AI governance, and three conceptual research instruments on black metal.",
        "papers.jpg": "Three papers. One institutional problem. Three distinct conceptual research instruments on black metal.",
        "about.jpg": "Takashi Sato, AI governance, Sapporo, Japan. Open-boundary mark on black paper.",
    }.get(image_kind, f"{paper['title']}: {paper['subtitle']}. Conceptual research instrument, not empirical data." if paper else title)
    safe_image_alt = escape(image_alt, quote=True)

    schema_html = json_ld(schema) if schema else ""

    verification_html = (
        f'<meta name="google-site-verification" content="{GOOGLE_SITE_VERIFICATION}">'
        if site_verification
        else ""
    )

    author_material_preload = (
        '\n          <link rel="preload" href="/assets/author-paper.webp" as="image" type="image/webp" fetchpriority="high">'
        '\n          <link rel="preload" href="/assets/fonts/Newsreader-Variable.woff2" as="font" type="font/woff2" crossorigin>'
        if path == "/about.html" else ""
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
            <link rel="related" href="https://doi.org/{paper['doi']}">
            <link rel="author" href="https://orcid.org/0009-0003-1584-6965">
            <link rel="item" type="application/pdf" href="{SITE}/pdf/v{VERSION}/{paper['slug']}.pdf">
            <link rel="describedby" type="application/json" href="{SITE}/citations/v{VERSION}/{paper['slug']}.json">
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
          <meta name="color-scheme" content="light">
          <meta name="theme-color" content="#F8F8F7">
          <title>{safe_title}</title>
          <meta name="description" content="{safe_description}">
          <meta name="author" content="Takashi Sato">
          <meta name="robots" content="{robots}">
          {verification_html}
          <link rel="canonical" href="{safe_canonical}">
          <link rel="alternate" type="application/atom+xml" title="Research updates" href="{SITE}/feed.xml">
          <link rel="alternate" hreflang="en" href="{safe_canonical}">
          <link rel="alternate" hreflang="x-default" href="{safe_canonical}">
          <link rel="author" href="/about.html">
          <link rel="me" href="https://orcid.org/0009-0003-1584-6965">
          <link rel="me" href="https://papers.ssrn.com/Sol3/Cf_Dev/AbsByAuth.cfm?per_id=9540672">
          <link rel="me" href="{SCHOLAR_URL}">
          <link rel="manifest" href="/site.webmanifest">
          <link rel="icon" href="/favicon-96x96.png" type="image/png" sizes="96x96">
          <link rel="icon" href="/favicon.svg" type="image/svg+xml" sizes="any">
          <link rel="alternate icon" href="/favicon.ico">
          <link rel="apple-touch-icon" href="/apple-touch-icon.png">
          <link rel="preload" href="/assets/fonts/InterVariable.woff2" as="font" type="font/woff2" crossorigin>{author_material_preload}
          <meta property="og:type" content="{og_type}">
          <meta property="og:locale" content="en_US">
          <meta property="og:site_name" content="{SITE_NAME}">
          <meta property="og:title" content="{safe_title}">
          <meta property="og:description" content="{safe_description}">
          <meta property="og:url" content="{safe_canonical}">
          <meta property="og:image" content="{SITE}{image}">
          <meta property="og:image:type" content="image/jpeg">
          <meta property="og:image:width" content="1200">
          <meta property="og:image:height" content="630">
          <meta property="og:image:alt" content="{safe_image_alt}">
          <meta name="twitter:card" content="summary_large_image">
          <meta name="twitter:title" content="{safe_title}">
          <meta name="twitter:description" content="{safe_description}">
          <meta name="twitter:image" content="{SITE}{image}">
          <meta name="twitter:image:alt" content="{safe_image_alt}">
          {paper_meta}
          {schema_html}
          <link rel="preload" href="{runtime_url("site.css")}" as="style">
          <link rel="stylesheet" href="{runtime_url("site.css")}">
          <script src="{runtime_url("site.js")}" defer></script>
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
            <a class="brand" href="/" aria-label="{SITE_NAME} — home">
              <img class="brand-mark" src="/assets/brand-mark.svg" width="32" height="32" alt="">
              <span>{SITE_NAME}</span>
            </a>
            <nav class="site-nav" aria-label="Primary navigation">
              <a href="/"{current('index')}>Index</a>
              <a href="/publications/"{current('publications')}>Works</a>
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
            <a class="footer-wordmark" href="/" aria-label="{SITE_NAME} — home">{SITE_NAME}</a>
            <div class="footer-grid">
              <div>
                <p class="eyebrow">Research &amp; writings</p>
                <p class="footer-thesis">An independent archive of research and writing. The current collection, The Proper Ending Index, examines decision routing, governing capacity, and accountable exit in AI-assisted institutions.</p>
              </div>
              <div class="footer-links">
                <div>
                  <p class="label">Research</p>
                  <a href="/publications/">All publications</a>
                  <a href="/papers/">Paper trilogy</a>
                  <a href="/research-index.json">Machine-readable index</a>
                  <a href="/feed.xml">Research feed · Atom</a>
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
