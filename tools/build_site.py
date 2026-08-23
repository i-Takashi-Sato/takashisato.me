#!/usr/bin/env python3
"""Build the static v6.2 research archive with no runtime dependencies."""

from __future__ import annotations

import json
from html import escape
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://takashisato.me"
AUTHOR_ID = f"{SITE}/about.html#takashi-sato"
SCHOLAR_URL = "https://scholar.google.com/citations?user=tN4zV68AAAAJ"
UPDATED = "2026-08-23"
VERSION = "6.2"
ASSET_VERSION = "6.2.1"
GOOGLE_SITE_VERIFICATION = "ESXaqBbWmxcZWPt2W_eI3ROS20FTy-KOziE5jfw0OSM"
AUTHOR = {
    "@type": "Person",
    "@id": AUTHOR_ID,
    "name": "Takashi Sato",
    "givenName": "Takashi",
    "familyName": "Sato",
    "alternateName": ["佐藤貴士", "佐藤 貴士", "Sato Takashi"],
    "jobTitle": "Independent Researcher",
    "url": f"{SITE}/about.html",
    "workLocation": {
        "@type": "Place",
        "name": "Sapporo, Hokkaido, Japan",
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "Sapporo",
            "addressRegion": "Hokkaido",
            "addressCountry": "JP",
        },
    },
    "identifier": [
        {"@type": "PropertyValue", "propertyID": "ORCID", "value": "0009-0003-1584-6965"},
        {"@type": "PropertyValue", "propertyID": "SSRN Author ID", "value": "9540672"},
    ],
    "sameAs": [
        "https://orcid.org/0009-0003-1584-6965",
        "https://papers.ssrn.com/Sol3/Cf_Dev/AbsByAuth.cfm?per_id=9540672",
        SCHOLAR_URL,
    ],
    "knowsAbout": [
        "AI governance",
        "human oversight",
        "workflow governance",
        "governing capacity",
        "Proper Ending",
        "Authority Return",
    ],
}

PAPERS = [
    {
        "part": 1,
        "roman": "I",
        "tone": "part-1",
        "slug": "part1",
        "title": "Workflow-Centric AI Governance",
        "subtitle": "A Typed Gate Contract for Accountable Human-AI Decisions",
        "description": "A falsifiable, two-stage state-and-authority grammar for routing consequential human-AI decisions without turning missing evidence, unavailable capacity, or preliminary machine states into silent approval or denial.",
        "ssrn": "5911063",
        "doi": "10.2139/ssrn.5911063",
        "posted": "2026-01-09",
        "pages": 18,
        "bytes": 514075,
        "sha256": "edf19f110f6b0302765e29d2dfa20ddb2cbea299ea93b9c30a6a98411f73c2e8",
        "function": "Route the case",
        "question": "What may happen next?",
        "state": "Typed case contract",
    },
    {
        "part": 2,
        "roman": "II",
        "tone": "part-2",
        "slug": "part2",
        "title": "Procedural Continuity and Governing-Capacity Loss in AI-Assisted Institutions",
        "subtitle": "A Descriptive State Model with Pre-Abuse Collapse as a Provisional Etiological Subtype",
        "description": "A descriptive state model for institutions whose visible procedure remains intact while independent judgment, practical governing capacity, and a predeclared protected function materially deteriorate.",
        "ssrn": "5913703",
        "doi": "10.2139/ssrn.5913703",
        "posted": "2026-01-12",
        "pages": 20,
        "bytes": 562947,
        "sha256": "6cb7a21940caa3c62a20820f8156d8d684317ad8db3a0be8c4ceb8b85d1d5e88",
        "function": "Diagnose the institution",
        "question": "Can it still govern?",
        "state": "Descriptive state model",
    },
    {
        "part": 3,
        "roman": "III",
        "tone": "part-3",
        "slug": "part3",
        "title": "From Governance Drift to Accountable Exit",
        "subtitle": "Proper Ending and Authority Return in AI-Assisted Institutions",
        "description": "A dependency-constrained protocol for containing and retiring AI-assisted workflows while preserving service, evidence, remedy, accountable ownership, and the practical capacity to decide.",
        "ssrn": "6066430",
        "doi": "10.2139/ssrn.6066430",
        "posted": "2026-02-10",
        "pages": 39,
        "bytes": 1032918,
        "sha256": "7cda8695056f7268d4ef9ffb794ac29022e478ff087b646c339f800b9fe1ef72",
        "function": "End and return authority",
        "question": "How does it end accountably?",
        "state": "Exit and authority protocol",
    },
]


def paper_url(paper: dict) -> str:
    return f"{SITE}/papers/{paper['slug']}.html"


def ssrn_url(paper: dict) -> str:
    return f"https://papers.ssrn.com/sol3/papers.cfm?abstract_id={paper['ssrn']}"


def article_schema(paper: dict) -> dict:
    return {
        "@type": "ScholarlyArticle",
        "@id": f"{paper_url(paper)}#article",
        "headline": f"{paper['title']}: {paper['subtitle']}",
        "name": f"{paper['title']}: {paper['subtitle']}",
        "description": paper["description"],
        "abstract": paper["description"],
        "author": {"@id": AUTHOR_ID},
        "datePublished": paper["posted"],
        "dateModified": UPDATED,
        "version": VERSION,
        "inLanguage": "en-US",
        "isAccessibleForFree": True,
        "pageStart": 1,
        "pageEnd": paper["pages"],
        "pagination": f"1-{paper['pages']}",
        "isPartOf": {"@id": f"{SITE}/papers/#trilogy"},
        "url": paper_url(paper),
        "mainEntityOfPage": paper_url(paper),
        "image": f"{SITE}/assets/og/{paper['slug']}.jpg",
        "sameAs": [ssrn_url(paper), f"https://doi.org/{paper['doi']}"],
        "identifier": [
            {"@type": "PropertyValue", "propertyID": "DOI", "value": paper["doi"]},
            {"@type": "PropertyValue", "propertyID": "SSRN", "value": paper["ssrn"]},
        ],
        "encoding": {
            "@type": "MediaObject",
            "contentUrl": f"{SITE}/pdf/{paper['slug']}.pdf",
            "encodingFormat": "application/pdf",
            "contentSize": f"{paper['bytes']} bytes",
            "sha256": paper["sha256"],
            "uploadDate": UPDATED,
        },
        "keywords": [
            "AI governance",
            "human oversight",
            "workflow governance",
            "governing capacity",
            "Proper Ending",
            "Authority Return",
        ],
    }


def breadcrumb_schema(items: list[tuple[str, str]]) -> dict:
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": position,
                "name": label,
                "item": f"{SITE}{path}",
            }
            for position, (label, path) in enumerate(items, start=1)
        ],
    }


def breadcrumbs(items: list[tuple[str, str | None]]) -> str:
    rendered = []
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
    schema: dict | list[dict] | None = None,
    robots: str = "index,follow,max-image-preview:large",
    og_type: str = "website",
    paper: dict | None = None,
    site_verification: bool = False,
) -> str:
    canonical = f"{SITE}{path}"
    safe_title = escape(title, quote=True)
    safe_description = escape(description, quote=True)
    safe_canonical = escape(canonical, quote=True)
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
            <meta name="citation_publication_date" content="2026/08/23">
            <meta name="citation_doi" content="{paper['doi']}">
            <meta name="citation_language" content="en">
            <link rel="alternate" type="application/pdf" title="Preserved PDF · v{VERSION}" href="{SITE}/pdf/{paper['slug']}.pdf">
            <meta property="article:published_time" content="{paper['posted']}">
            <meta property="article:modified_time" content="{UPDATED}">
            <meta property="article:author" content="{SITE}/about.html">
            """
        ).strip()
    return dedent(
        f"""
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
          <meta name="color-scheme" content="light">
          <meta name="theme-color" content="#f2efe8">
          <title>{safe_title}</title>
          <meta name="description" content="{safe_description}">
          <meta name="author" content="Takashi Sato">
          <meta name="robots" content="{robots}">
          {verification_html}
          <link rel="canonical" href="{safe_canonical}">
          <link rel="author" href="/about.html">
          <link rel="me" href="https://orcid.org/0009-0003-1584-6965">
          <link rel="me" href="https://papers.ssrn.com/Sol3/Cf_Dev/AbsByAuth.cfm?per_id=9540672">
          <link rel="me" href="{SCHOLAR_URL}">
          <link rel="manifest" href="/site.webmanifest">
          <link rel="icon" href="/favicon.svg" type="image/svg+xml" media="(prefers-color-scheme: light)">
          <link rel="icon" href="/favicon-dark.svg" type="image/svg+xml" media="(prefers-color-scheme: dark)">
          <link rel="alternate icon" href="/favicon.ico">
          <link rel="apple-touch-icon" href="/apple-touch-icon.png">
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
          <link rel="stylesheet" href="/assets/archive-v62.css?v={ASSET_VERSION}">
          <script src="/assets/archive-v62.js?v={ASSET_VERSION}"></script>
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
        <script src="/assets/site-analytics.js?v=entity-analytics-1" defer></script>
        """
    ).strip()


def shell_page(*, head_html: str, body: str, active: str = "", tone: str = "neutral", page: str = "") -> str:
    return f"{head_html}\n<body data-tone=\"{tone}\" data-page=\"{page}\">\n{header(active)}\n{body}\n{footer()}\n</body>\n</html>\n"


def write(path: str, content: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def home_page() -> str:
    item_list = [
        {"@type": "ListItem", "position": p["part"], "url": paper_url(p), "name": f"{p['title']}: {p['subtitle']}"}
        for p in PAPERS
    ]
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "@id": f"{SITE}/#website",
                "url": f"{SITE}/",
                "name": "The Proper Ending Index",
                "description": "Takashi Sato's independent research archive on workflow-centric AI governance, governing-capacity loss, Proper Ending, and Authority Return.",
                "inLanguage": ["en-US", "ja-JP"],
                "author": {"@id": AUTHOR_ID},
            },
            AUTHOR,
            {
                "@type": "CollectionPage",
                "@id": f"{SITE}/#index",
                "url": f"{SITE}/",
                "name": "The Proper Ending Index",
                "isPartOf": {"@id": f"{SITE}/#website"},
                "mainEntity": {"@type": "ItemList", "itemListElement": item_list},
            },
        ],
    }
    rows = "\n".join(
        dedent(
            f"""
            <a class="sequence-row" href="/papers/{p['slug']}.html" data-reveal>
              <p class="sequence-function">{p['function']}</p>
              <div>
                <h3 class="sequence-title">{p['title']}</h3>
                <p class="sequence-copy">{p['question']} {p['description']}</p>
                <span class="sequence-state">{p['state']} · v6.2 · {p['pages']} pages</span>
              </div>
            </a>
            """
        ).strip()
        for p in PAPERS
    )
    body = dedent(
        f"""
        <main id="main">
          <section class="hero shell" aria-labelledby="hero-title">
            <div class="hero-grid">
              <div data-reveal>
                <p class="eyebrow">Workflow-Centric AI Governance Trilogy · v6.2</p>
                <h1 id="hero-title">A role alone is not governance. Accountability lives in the sequence.</h1>
              </div>
              <div class="hero-aside" data-reveal>
                <p>Three working papers trace one institutional problem across three scales: route the decision, diagnose governing-capacity loss, and end a failing workflow without abandoning authority or remedy.</p>
                <div class="hero-actions">
                  <a class="button primary" href="/papers/">Read the trilogy <span class="arrow" aria-hidden="true">↗</span></a>
                  <a class="button" href="/about.html">Author record</a>
                </div>
              </div>
            </div>
          </section>

          <section class="section">
            <div class="shell">
              <div class="section-head" data-reveal>
                <p class="label">The research sequence</p>
                <div>
                  <h2>From a case decision to an institutional exit.</h2>
                  <p class="section-intro">The papers are connected, but they do not collapse into a single score or universal lifecycle. Each asks a distinct question and states its own claim boundary.</p>
                </div>
              </div>
              <div class="sequence">{rows}</div>
            </div>
          </section>

          <section class="section compact">
            <div class="shell">
              <h2 class="sr-only">Series at a glance</h2>
              <div class="metric-grid" data-reveal role="list" aria-label="Series at a glance">
                <div class="metric" role="listitem"><strong>1,024</strong><span>Stage-1 configurations enumerated in Part I</span></div>
                <div class="metric" role="listitem"><strong>1,248</strong><span>applicable Stage-2 configurations in Part I</span></div>
                <div class="metric" role="listitem"><strong>5</strong><span>rejectable propositions in Part II</span></div>
                <div class="metric" role="listitem"><strong>8,564</strong><span>reachable states explored in Part III</span></div>
              </div>
            </div>
          </section>

          <section class="section">
            <div class="shell">
              <div class="boundary" data-reveal>
                <h2>What this archive does not claim.</h2>
                <div>
                  <p>These are working papers and formalized research artifacts—not legal advice, a compliance certification, an operational decision engine, or evidence that the proposed architectures improve outcomes in the field.</p>
                  <p>Finite checks are exhaustive only over each declared abstraction. The shared public-record corpus supports traceability, not frequency, prediction, causal sufficiency, or independent validation.</p>
                </div>
              </div>
            </div>
          </section>

          <section class="section compact">
            <div class="shell">
              <h2 class="sr-only">About the author</h2>
              <div class="profile-grid" data-reveal>
                <div class="profile-aside">
                  <p class="label">Author</p>
                  <p>Independent research<br>Sapporo, Japan</p>
                </div>
                <div class="profile-copy">
                  <p class="lead">Takashi Sato studies how AI-assisted institutions preserve accountable judgment—and how they should contain, retire, and transfer decision capacity when governance fails.</p>
                  <div class="hero-actions">
                    <a class="button" href="/about.html">About the author</a>
                    <a class="button" href="https://orcid.org/0009-0003-1584-6965" target="_blank" rel="me noopener noreferrer">ORCID <span class="arrow" aria-hidden="true">↗</span></a>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </main>
        """
    ).strip()
    return shell_page(
        head_html=head(
            title="The Proper Ending Index · Takashi Sato",
            description="Independent research on decision routing, governing-capacity loss, Proper Ending, and Authority Return in AI-assisted institutions.",
            path="/",
            image="/assets/og/home.jpg",
            schema=schema,
            site_verification=True,
        ),
        body=body,
        active="index",
        page="home",
    )


def papers_index_page() -> str:
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            AUTHOR,
            {
                "@type": "CollectionPage",
                "@id": f"{SITE}/papers/#trilogy",
                "name": "Workflow-Centric AI Governance Trilogy",
                "url": f"{SITE}/papers/",
                "dateModified": UPDATED,
                "author": {"@id": AUTHOR_ID},
                "hasPart": [{"@id": f"{paper_url(p)}#article"} for p in PAPERS],
            },
            breadcrumb_schema([("Index", "/"), ("Papers", "/papers/")]),
        ],
    }
    records = []
    for p in PAPERS:
        records.append(
            dedent(
                f"""
                <article class="sequence-row" data-reveal>
                  <p class="sequence-function">Part {p['roman']} · {p['function']}</p>
                  <div>
                    <h2 class="sequence-title"><a href="/papers/{p['slug']}.html">{p['title']}</a></h2>
                    <p class="paper-subtitle">{p['subtitle']}</p>
                    <p class="sequence-copy">{p['description']}</p>
                    <span class="sequence-state">SSRN {p['ssrn']} · DOI {p['doi']} · v6.2 · {p['pages']} pages</span>
                    <div class="hero-actions">
                      <a class="button primary" href="/papers/{p['slug']}.html">Paper record</a>
                      <a class="button" href="{ssrn_url(p)}" target="_blank" rel="noopener noreferrer">SSRN <span class="arrow" aria-hidden="true">↗</span></a>
                    </div>
                  </div>
                </article>
                """
            ).strip()
        )
    body = dedent(
        f"""
        <main id="main">
          <header class="page-hero shell">
            {breadcrumbs([("Index", "/"), ("Papers", None)])}
            <p class="eyebrow" data-reveal>Workflow-Centric AI Governance Trilogy</p>
            <h1 data-reveal>Three papers. One institutional problem.</h1>
            <p class="page-deck" data-reveal>Accountability can fail at the moment of routing, across the life of an institution, and at the point of exit. The trilogy treats those as related but analytically separate governance problems.</p>
            <div class="paper-meta" data-reveal>
              <span>Author · Takashi Sato</span>
              <span>Status · Working papers</span>
              <span>Current version · 6.2</span>
              <span>Updated · 23 August 2026</span>
            </div>
          </header>
          <section class="section">
            <div class="shell">
              <h2 class="sr-only">Paper records</h2>
              <div class="sequence">{' '.join(records)}</div>
            </div>
          </section>
          <section class="section compact">
            <div class="shell boundary" data-reveal>
              <h2>Reading order is useful, not mandatory.</h2>
              <div>
                <p>Part I specifies a case-level routing contract. Part II models institutional loss over time. Part III specifies containment, accountable retirement, and authority transfer. Each paper contains its own definitions, limitations, and verification boundary.</p>
                <p>For citation and version history, use the SSRN record as the primary external research record. Local PDFs are preserved copies of version 6.2.</p>
              </div>
            </div>
          </section>
        </main>
        """
    ).strip()
    return shell_page(
        head_html=head(
            title="Papers · Workflow-Centric AI Governance Trilogy",
            description="The v6.2 working-paper trilogy by Takashi Sato: decision routing, governing-capacity loss, Proper Ending, and Authority Return.",
            path="/papers/",
            image="/assets/og/papers.jpg",
            schema=schema,
        ),
        body=body,
        active="papers",
        page="papers",
    )


def part1_content() -> str:
    return dedent(
        """
        <section id="overview">
          <p class="eyebrow">Research question</p>
          <h2>Can oversight be specified as a case contract?</h2>
          <p class="lead">A person may be formally “in the loop” while lacking admissible evidence, time, authority, review capacity, or a usable fallback. Part I makes those conditions explicit and typed.</p>
          <p>The paper shifts the unit of governance from the model alone to the institutional workflow that defines evidence, routes exceptions, allocates authority, and turns a recommendation into action. Its contribution is deliberately narrow: a falsifiable state-and-authority grammar for case routing.</p>
          <div class="fact-grid">
            <article class="fact"><code>DOMAIN CONTRACT</code><h3>Define before deployment</h3><p>Decision scope, evidence, authority, execution, capacity, fallback, record, and remedy are versioned objects—not assumptions left to an interface.</p></article>
            <article class="fact"><code>TYPE DISCIPLINE</code><h3>Keep unlike conditions unlike</h3><p>Missing evidence, unavailable capacity, nominal authority, and fallback readiness do not silently collapse into approval or denial.</p></article>
          </div>
        </section>

        <section id="contract">
          <p class="eyebrow">The contract</p>
          <h2>Three diagnostics. Two stages. No silent action.</h2>
          <div class="model">
            <div class="model-head"><h3>Stage 1 · total routing semantics</h3><span>routing status ≠ execution event</span></div>
            <div class="gate-flow">
              <div class="gate"><span class="meta-label">Gate 1</span><b>Hard constraints &amp; admissibility</b><small>Scope, prohibitions, and minimum evidentiary preconditions.</small><div class="state-line"><i>PASS</i><i>REVIEW</i><i>BLOCK</i><i>UNKNOWN</i></div></div>
              <div class="gate"><span class="meta-label">Gate 2</span><b>Value, impact &amp; conflict</b><small>Proportionality, material tension, and rights-sensitive tradeoffs.</small><div class="state-line"><i>PASS</i><i>REVIEW</i><i>BLOCK</i><i>UNKNOWN</i></div></div>
              <div class="gate"><span class="meta-label">Gate 3</span><b>Temporal validity &amp; reliability</b><small>Evidence, policy, system version, and assumptions remain current.</small><div class="state-line"><i>PASS</i><i>REVIEW</i><i>BLOCK</i><i>UNKNOWN</i></div></div>
              <div class="route-box"><span class="meta-label">Route</span><b>Typed status only</b><small>Execution eligible · Evidence hold · Authorized review · Fallback · Unresolved</small></div>
            </div>
            <div class="model-head model-head-spaced"><h3>Stage 2 · signed institutional disposition</h3><span>authorized review only</span></div>
            <div class="disposition-grid" role="list" aria-label="Signed dispositions"><span role="listitem">RELEASE</span><span role="listitem">MODIFIED ACTION</span><span role="listitem">FINAL STOP</span><span role="listitem">AUTHORIZED DEFER</span><span role="listitem">FALLBACK</span></div>
          </div>
          <p>All-PASS yields <strong>EXECUTION ELIGIBLE</strong> only. The actual act remains governed by a separate, versioned execution contract. A preliminary BLOCK is not a final denial, authority availability is not a decision event, and UNKNOWN cannot silently become PASS.</p>
          <p>Review authority and review capacity are distinct inputs. Fallback authorization and operational readiness are distinct inputs. If either member of a pair is absent, that route is unavailable.</p>
        </section>

        <section id="verification">
          <p class="eyebrow">Finite-domain verification</p>
          <h2>Complete over the declared truth tables.</h2>
          <div class="verification" role="list" aria-label="Verification results">
            <div role="listitem"><strong>1,024</strong><span>Stage-1 configurations enumerated</span></div>
            <div role="listitem"><strong>1,248</strong><span>applicable Stage-2 configurations enumerated</span></div>
            <div role="listitem"><strong>9 / 9</strong><span>isolated guard mutations produced a counterexample</span></div>
          </div>
          <p class="caveat"><strong>Result:</strong> the authored functions produced zero invariant violations. “Exhaustive” means complete over the declared finite abstraction; it is not proof that the invariants are complete, comparison with external ground truth, or evidence of legal or field effectiveness.</p>
          <div class="fact-grid">
            <article class="fact"><code>CROSS-STAGE TEST</code><h3>Defer is not evidence hold</h3><p>A dedicated mutation catches any collapse of signed DEFER back into the Stage-1 EVIDENCE HOLD label.</p></article>
            <article class="fact"><code>PUBLIC RECORDS</code><h3>Traceability, not validation</h3><p>Fifteen author-coded units from three official investigations trace evidence, reasons, review access, authority, proportionality, feedback, and remedy.</p></article>
          </div>
        </section>

        <section id="boundary">
          <p class="eyebrow">Claim boundary</p>
          <h2>What Part I does not establish.</h2>
          <ul>
            <li>That three gates are optimal or the risk decomposition is exhaustive.</li>
            <li>That the routing priority is legally sufficient in any jurisdiction.</li>
            <li>That signatures, identity proofing, cryptography, coercion, or legal authority are solved by a Boolean input.</li>
            <li>That the architecture improves outcomes, can be resourced in practice, or is suitable where lawful fallback and effective authority cannot be established.</li>
          </ul>
        </section>
        """
    ).strip()


def part2_content() -> str:
    return dedent(
        """
        <section id="overview">
          <p class="eyebrow">Research question</p>
          <h2>Can procedure remain visible after governing capacity has declined?</h2>
          <p class="lead">Part II models a joint institutional state in which observable process remains stable or improves while independent judgment, practical actionability, and a predeclared protected function materially deteriorate.</p>
          <p>The primary construct is <strong>PMGCL</strong>: Procedural Maintenance with Governing-Capacity Loss. It is descriptive and does not assign an ordinary or malicious cause. <strong>PAC</strong>—Pre-Abuse Collapse—is only a provisional etiological subtype and requires an additional identified causal boundary.</p>
        </section>

        <section id="state-model">
          <p class="eyebrow">Descriptive state model</p>
          <h2>Four objects must remain separate.</h2>
          <div class="model">
            <div class="model-head"><h3>Declared workflow · protected function · population · interval I</h3><span>formative, non-interchangeable elements</span></div>
            <div class="construct-grid">
              <div class="construct"><strong>P</strong><b>Procedural fidelity</b><span>Visible steps, approvals, documentation, and service-level completion.</span></div>
              <div class="construct"><strong>J</strong><b>Judgment contribution</b><span>Case-level evidence or reasoning beyond the AI output and template.</span></div>
              <div class="construct"><strong>G</strong><b>Governing capacity</b><span>Practical ability to alter, resource, escalate, remedy, or stop.</span></div>
              <div class="construct"><strong>N</strong><b>Protected function</b><span>An independently measured, predeclared outcome—not model accuracy by default.</span></div>
            </div>
            <div class="formula">PMGCL(I) = 1 iff F<sub>P</sub>(I) ∧ D<sub>J</sub>(I) ∧ D<sub>G</sub>(I) ∧ I<sub>N</sub>(I)<br>PAC(I) = 1 iff PMGCL(I) = 1 ∧ S<sub>NA</sub>(I) = IDENTIFIED</div>
          </div>
          <p>If judgment and capacity are credibly declining but protected-function impairment is not yet demonstrated, the correct state is <strong>incipient governing-capacity-loss risk</strong>. If all four descriptive conjuncts are established but the causal condition is unidentified, the correct state is <strong>realized PMGCL with etiology unresolved</strong>—not PAC.</p>
        </section>

        <section id="mechanisms">
          <p class="eyebrow">Four candidate mechanisms</p>
          <h2>Pathways to loss, not a closed taxonomy.</h2>
          <div class="fact-grid">
            <article class="fact"><code>01</code><h3>Cognitive externalization</h3><p>Reviewers increasingly treat the model output as both the starting and ending representation of the case, displacing complementary scrutiny.</p></article>
            <article class="fact"><code>02</code><h3>Legibility capture</h3><p>Actors optimize countable completion, agreement, or documentation artifacts while the protected function deteriorates.</p></article>
            <article class="fact"><code>03</code><h3>Responsibility inversion</h3><p>Formal accountability concentrates on the reviewer who bears the cost of deviation but lacks power over the system.</p></article>
            <article class="fact"><code>04</code><h3>Voice attenuation</h3><p>Unremedied or punished concerns reduce the future supply of dissent and deprive the institution of corrective information.</p></article>
          </div>
          <p class="caveat">The set is provisional and theory-directed. Deskilling, vendor lock-in, update opacity, dependency, resource withdrawal, or other mechanisms should be added or preferred when they improve identification.</p>
        </section>

        <section id="propositions">
          <p class="eyebrow">Falsifiability</p>
          <h2>Five derived propositions—and what would count against them.</h2>
          <div class="table-wrap">
            <table class="research-table">
              <caption class="sr-only">Five Part II propositions, target contrasts, and evidence against</caption>
              <thead><tr><th>Proposition</th><th>Target contrast</th><th>Evidence against</th></tr></thead>
              <tbody>
                <tr><th>P1 · Capacity-strain decoupling</th><td>Change in independent judgment relative to procedural completion after exogenous throughput pressure.</td><td>Judgment remains stable or the decline is explained by case mix, model improvement, or learning.</td></tr>
                <tr><th>P2 · Target conversion</th><td>Visible artifact and its conditional relation to evidence or the protected outcome after a completion target.</td><td>Both procedure and protected function improve without hidden burden displacement.</td></tr>
                <tr><th>P3 · Voice-efficacy feedback</th><td>Effect of prior remedy efficacy on later risk-adjusted dissent.</td><td>No temporal association, or the relation is explained by fewer opportunities to dissent.</td></tr>
                <tr><th>P4 · Coupled-trace discrimination</th><td>Held-out gain from joint rationale, time, and voice traces.</td><td>Single raw metrics perform equally well, or the coupled signal fails under benign efficiency.</td></tr>
                <tr><th>P5 · Comparative state validity</th><td>Calibrated, decision-relevant gain over continuous components and established baselines.</td><td>The gain vanishes under leakage controls or a simpler model chooses the same intervention.</td></tr>
              </tbody>
            </table>
          </div>
        </section>

        <section id="boundary">
          <p class="eyebrow">Claim boundary</p>
          <h2>Classification is not a detector or an accusation.</h2>
          <ul>
            <li>The framework does not establish that any real institution satisfies PMGCL or PAC.</li>
            <li>A verbal absence of malice, a directed acyclic graph alone, or retrospective conditioning on “no documented malice” cannot establish the PAC subtype.</li>
            <li>The shared fifteen-unit official-record corpus supports theory-directed traceability, not frequency, necessity, sufficiency, prediction, or independent triangulation.</li>
            <li>Thresholds, measurement validity, site transportability, causal identification, and intervention utility remain empirical questions.</li>
          </ul>
        </section>
        """
    ).strip()


def part3_content() -> str:
    return dedent(
        """
        <section id="overview">
          <p class="eyebrow">Research question</p>
          <h2>How should a failing workflow end?</h2>
          <p class="lead">Detection is not governance. An accountable exit is incomplete if service collapses, evidence disappears, affected people lose remedy, or unresolved decisions have no accountable owner.</p>
          <p>Part III connects investigation, a reversible Circuit Breaker, Resolution Collapse, Proper Ending, and Authority Return. Its stronger contribution is institutional structure: containment and retirement are authorized acts, indicators do not make those decisions, and closure cannot erase unresolved obligations.</p>
          <div class="fact-grid">
            <article class="fact"><code>CIRCUIT BREAKER</code><h3>Reversible containment</h3><p>A bounded response for a workflow that may be corrected, narrowed, replaced, or otherwise recovered under an independent authorization record.</p></article>
            <article class="fact"><code>PROPER ENDING</code><h3>Accountable retirement</h3><p>A dependency-constrained transition that preserves continuity, evidence, notice, remedy, post-exit responsibility, assurance, and closure.</p></article>
          </div>
        </section>

        <section id="proper-ending">
          <p class="eyebrow">Proper Ending</p>
          <h2>Nine evidence-producing functions—not a shutdown button.</h2>
          <div class="model">
            <div class="model-head"><h3>Dependency-constrained institutional transition</h3><span>parallel work where prerequisites permit</span></div>
            <ol class="protocol">
              <li><b>Authorize</b><span>Record the lawful decision maker, scope, effective time, and review path.</span></li>
              <li><b>Contain</b><span>Use tested fallback or a separately authorized emergency safe-stop.</span></li>
              <li><b>Preserve</b><span>Freeze versions, logs, decisions, notices, and investigative evidence lawfully.</span></li>
              <li><b>Notify</b><span>Give accurate, accessible notice appropriate to rights and risks.</span></li>
              <li><b>Remedy</b><span>Identify affected decisions, open review and relief, correct records, and prioritize severe cases.</span></li>
              <li><b>Transfer</b><span>Assign the continuing function to an accepting successor—or residual duties to a named custodian.</span></li>
              <li><b>Decommission</b><span>Revoke integrations and credentials, dispose safely, and verify shadow use has ceased.</span></li>
              <li><b>Assure</b><span>Independently confirm continuity, remedy progress, security, and absence of unauthorized restart.</span></li>
              <li><b>Learn &amp; close</b><span>Publish a proportionate account, assign follow-up owners, and record closure after the assurance cutoff.</span></li>
            </ol>
            <p class="protocol-note">Containment history enables preservation, notice, and remedy in parallel. Preservation and branch-specific responsibility must converge before decommissioning; assurance precedes final closure. No affected case or remedy obligation may be left without an accountable owner.</p>
          </div>
          <p>Urgent protective remedy may begin before individual notice where lawful and necessary, but the exception and later notice must be recorded. Transfer may accept incomplete remedy obligations; it must not falsely certify that every remedy is complete.</p>
        </section>

        <section id="authority-return">
          <p class="eyebrow">Authority Return</p>
          <h2>Ending software does not restore the capacity it displaced.</h2>
          <p class="lead">Authority Return identifies power embedded in data definitions, rankings, defaults, access controls, and queue architecture, then reconstitutes or reassigns the practical capacity to decide, explain, correct, and resource the function.</p>
          <div class="fact-grid">
            <article class="fact"><code>CONTINUING FUNCTION</code><h3>Accepting successor</h3><p>The successor must be able to exercise judgment, operate without a defeating undisclosed dependency, and accept records, resources, queues, cases, and remedy obligations.</p></article>
            <article class="fact"><code>ABOLISHED FUNCTION</code><h3>Residual custodian</h3><p>A named custodian or remedy authority accepts records, unresolved cases, appeals, compensation pathways, incomplete remedies, and residual liabilities.</p></article>
            <article class="fact"><code>CAPACITY</code><h3>People, budget, tools</h3><p>Formal title is insufficient. Competence, protected time, staffing, budget, interpretive knowledge, and operational access must move.</p></article>
            <article class="fact"><code>STANDING</code><h3>Affected-party challenge</h3><p>The destination and terms of return remain normative and legal questions subject to appropriate participation, review, and appeal.</p></article>
          </div>
        </section>

        <section id="verification">
          <p class="eyebrow">Finite-state safety verification</p>
          <h2>The guard model is executable—and bounded.</h2>
          <div class="verification" role="list" aria-label="Finite-state verification results">
            <div role="listitem"><strong>8,564</strong><span>reachable states under exhaustive breadth-first exploration</span></div>
            <div role="listitem"><strong>36,096</strong><span>enabled transitions explored</span></div>
            <div role="listitem"><strong>30</strong><span>mutation-adequate guards with a minimal counterexample when weakened</span></div>
          </div>
          <p class="caveat"><strong>Result:</strong> no authored-invariant violation in the unmutated model. This is executable consistency testing of a selected abstraction—not certification, semantic validation, or proof that a real institution records facts honestly or performs remedy effectively.</p>
        </section>

        <section id="measurement">
          <p class="eyebrow">Measurement boundary</p>
          <h2>Indicators route investigation. They do not authorize action.</h2>
          <p>The Governance Drift Indicator layer asks whether rationales add held-out information, review time remains responsive to legitimate complexity, and corrective voice is supplied and acted upon. It is subordinate to the authorization protocol and is not a prerequisite for Proper Ending.</p>
          <p>Aggregate monitoring misses 92 of 100 constructed localized-collapse streams in the frozen benchmark. The added fixed subgroup rule recovers 97 of 100, and the union 98 of 100—but the subgroup definition matches the synthetic generator’s declared failure boundary. Those are internal implementation results, not field sensitivity, specificity, discovery, or a validated real-world threshold.</p>
        </section>

        <section id="boundary">
          <p class="eyebrow">Claim boundary</p>
          <h2>What Part III does not verify.</h2>
          <ul>
            <li>That the synthetic indicators have prospective lead time, open-world validity, or an operationally justified threshold.</li>
            <li>That retirement bases are lawful, notice intelligible, remedy accessible, staffing sufficient, or successor and custodian roles legitimate in substance.</li>
            <li>Repeated incidents, contested facts, parallel authorities, partial-population rollback, real calendar time, and jurisdictional conflict.</li>
            <li>That “independence” is more than a label unless organizational separation, conflicts, evidence access, competence, power, reasons, and review routes are actually established.</li>
          </ul>
        </section>
        """
    ).strip()


def series_navigation(current: int) -> str:
    links = []
    for p in PAPERS:
        attrs = ' aria-current="page"' if p["part"] == current else ""
        links.append(
            f'<a href="/papers/{p["slug"]}.html"{attrs}><small>PART {p["roman"]} · {p["function"].upper()}</small><strong>{p["title"]}</strong></a>'
        )
    return '<nav class="series-nav" aria-label="Paper trilogy">' + "".join(links) + "</nav>"


def paper_page(paper: dict) -> str:
    if paper["part"] == 1:
        content = part1_content()
        toc = [("overview", "Question"), ("contract", "Contract"), ("verification", "Verification"), ("boundary", "Boundary")]
    elif paper["part"] == 2:
        content = part2_content()
        toc = [("overview", "Question"), ("state-model", "State model"), ("mechanisms", "Mechanisms"), ("propositions", "Propositions"), ("boundary", "Boundary")]
    else:
        content = part3_content()
        toc = [("overview", "Question"), ("proper-ending", "Proper Ending"), ("authority-return", "Authority Return"), ("verification", "Verification"), ("measurement", "Measurement"), ("boundary", "Boundary")]
    toc_items = "".join(f'<li><a href="#{anchor}">{label}</a></li>' for anchor, label in toc)
    citation = f"Sato, Takashi. “{paper['title']}: {paper['subtitle']}.” Working Paper, version 6.2, 23 August 2026. https://doi.org/{paper['doi']}."
    body = dedent(
        f"""
        <main id="main">
          <header class="paper-hero shell" data-roman="{paper['roman']}">
            {breadcrumbs([("Index", "/"), ("Papers", "/papers/"), (f"Part {paper['roman']}", None)])}
            <p class="eyebrow" data-reveal>Workflow-Centric AI Governance Trilogy · Part {paper['roman']}</p>
            <h1 data-reveal>{paper['title']}</h1>
            <p class="paper-subtitle" data-reveal>{paper['subtitle']}</p>
            <div class="paper-meta" data-reveal>
              <span>Takashi Sato</span>
              <span>Working paper · v6.2</span>
              <span>23 August 2026</span>
              <span>{paper['pages']} pages</span>
              <span>SSRN {paper['ssrn']}</span>
            </div>
            <div class="paper-actions" data-reveal>
              <a class="button primary" href="{ssrn_url(paper)}" target="_blank" rel="noopener noreferrer">SSRN research record <span class="arrow" aria-hidden="true">↗</span></a>
              <a class="button" href="/pdf/{paper['slug']}.pdf">Preserved PDF · v6.2</a>
              <a class="button" href="https://doi.org/{paper['doi']}" target="_blank" rel="noopener noreferrer">DOI <span class="arrow" aria-hidden="true">↗</span></a>
            </div>
          </header>

          <div class="section">
            <div class="shell paper-layout">
              <aside class="toc" aria-label="On this page">
                <p class="label">On this page</p>
                <ol>{toc_items}</ol>
              </aside>
              <article class="content" data-reveal>
                <h2 class="sr-only">Part {paper['roman']} analysis</h2>
                {content}
                <section id="citation">
                  <p class="eyebrow">Citation &amp; preservation</p>
                  <h2>Cite the versioned record.</h2>
                  <p>The SSRN page is the primary external research record. The local file is a preserved copy of version 6.2 for stable access.</p>
                  <div class="citation">{citation}</div>
                  <dl class="record-list">
                    <div class="record-row"><dt>DOI</dt><dd><a href="https://doi.org/{paper['doi']}" target="_blank" rel="noopener noreferrer">{paper['doi']}</a></dd></div>
                    <div class="record-row"><dt>SSRN</dt><dd><a href="{ssrn_url(paper)}" target="_blank" rel="noopener noreferrer">Abstract ID {paper['ssrn']}</a></dd></div>
                    <div class="record-row"><dt>Preserved file</dt><dd><a href="/pdf/{paper['slug']}.pdf">/pdf/{paper['slug']}.pdf</a> · {paper['bytes']:,} bytes</dd></div>
                    <div class="record-row"><dt>SHA-256</dt><dd><code>{paper['sha256']}</code></dd></div>
                  </dl>
                </section>
              </article>
            </div>
          </div>
          <div class="section compact"><div class="shell">{series_navigation(paper['part'])}</div></div>
        </main>
        """
    ).strip()
    return shell_page(
        head_html=head(
            title=f"{paper['title']} · Part {paper['roman']} · Takashi Sato",
            description=paper["description"],
            path=f"/papers/{paper['slug']}.html",
            image=f"/assets/og/{paper['slug']}.jpg",
            schema={
                "@context": "https://schema.org",
                "@graph": [
                    AUTHOR,
                    article_schema(paper),
                    breadcrumb_schema(
                        [("Index", "/"), ("Papers", "/papers/"), (f"Part {paper['roman']}", f"/papers/{paper['slug']}.html")]
                    ),
                ],
            },
            og_type="article",
            paper=paper,
        ),
        body=body,
        active="papers",
        tone=paper["tone"],
        page=paper["slug"],
    )


def about_page() -> str:
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            AUTHOR,
            {
                "@type": "ProfilePage",
                "@id": f"{SITE}/about.html#profile",
                "url": f"{SITE}/about.html",
                "name": "Takashi Sato · Author Record",
                "dateModified": UPDATED,
                "mainEntity": {"@id": AUTHOR_ID},
            },
            breadcrumb_schema([("Index", "/"), ("Author", "/about.html")]),
        ],
    }
    body = dedent(
        f"""
        <main id="main">
          <header class="page-hero shell">
            {breadcrumbs([("Index", "/"), ("Author", None)])}
            <p class="eyebrow" data-reveal>Author record · 佐藤貴士</p>
            <h1 data-reveal>Researching the point where oversight becomes governable—and where it must end.</h1>
          </header>
          <div class="section">
            <div class="shell profile-grid">
              <aside class="profile-aside" data-reveal>
                <p class="label">Takashi Sato</p>
                <p>Independent Researcher<br>Sapporo, Hokkaido, Japan</p>
                <div class="hero-actions">
                  <a class="button" href="https://orcid.org/0009-0003-1584-6965" target="_blank" rel="me noopener noreferrer">ORCID ↗</a>
                  <a class="button" href="https://papers.ssrn.com/Sol3/Cf_Dev/AbsByAuth.cfm?per_id=9540672" target="_blank" rel="me noopener noreferrer">SSRN ↗</a>
                </div>
              </aside>
              <div class="content profile-copy" data-reveal>
                <section>
                  <h2 class="sr-only">Research focus</h2>
                  <p class="lead">Takashi Sato is an independent researcher focused on AI governance, human oversight, workflow governance, governing capacity, Proper Ending, and Authority Return.</p>
                  <p>The current working-paper trilogy asks how consequential human-AI decisions should be routed, how an institution can remain procedurally intact while losing its practical capacity to govern, and how a failing workflow can be contained and retired without abandoning service, evidence, remedy, or decision responsibility.</p>
                </section>
                <section>
                  <p class="eyebrow">日本語</p>
                  <h2 class="jp" lang="ja">佐藤貴士について</h2>
                  <p class="jp" lang="ja">佐藤貴士（Takashi Sato）は、札幌を拠点とする独立研究者です。AIガバナンス、人間による監督、ワークフロー・ガバナンス、統治能力、Proper Ending、Authority Returnを研究しています。</p>
                  <p class="jp" lang="ja">現在の研究では、人間が形式上「ループ内」にいることと、証拠・時間・権限・審査能力・代替手段を備えた実効的な監督とを区別しています。また、制度が手続を維持しながら判断能力を失う過程と、問題のあるAI支援ワークフローを説明責任ある形で終結させる条件を検討しています。</p>
                </section>
                <section>
                  <p class="eyebrow">Research practice</p>
                  <h2>Formalize the claim. Publish the boundary.</h2>
                  <p>The papers combine typed protocols, finite-state exploration, mutation testing, synthetic stress tests, and theory-directed public-record traceability. Each method is reported with an explicit limit: executable consistency is not legal sufficiency, synthetic performance is not field validity, and a purposive official-record corpus is not representative evidence.</p>
                </section>
                <section>
                  <p class="eyebrow">Public identifiers</p>
                  <h2>One author record across research systems.</h2>
                  <dl class="record-list">
                    <div class="record-row"><dt>ORCID</dt><dd><a href="https://orcid.org/0009-0003-1584-6965" target="_blank" rel="me noopener noreferrer">0009-0003-1584-6965</a></dd></div>
                    <div class="record-row"><dt>SSRN Author ID</dt><dd><a href="https://papers.ssrn.com/Sol3/Cf_Dev/AbsByAuth.cfm?per_id=9540672" target="_blank" rel="me noopener noreferrer">9540672</a></dd></div>
                    <div class="record-row"><dt>Google Scholar</dt><dd><a href="{SCHOLAR_URL}" target="_blank" rel="me noopener noreferrer">Author profile</a></dd></div>
                    <div class="record-row"><dt>Location</dt><dd>Sapporo, Hokkaido, Japan</dd></div>
                  </dl>
                </section>
              </div>
            </div>
          </div>
        </main>
        """
    ).strip()
    return shell_page(
        head_html=head(
            title="Takashi Sato · Independent Researcher",
            description="Author record for Takashi Sato (佐藤貴士), an independent researcher in Sapporo working on AI governance, governing capacity, Proper Ending, and Authority Return.",
            path="/about.html",
            image="/assets/og/about.jpg",
            schema=schema,
            og_type="profile",
        ),
        body=body,
        active="about",
        page="about",
    )


def utility_page(*, slug: str, title: str, description: str, content: str, robots: str = "index,follow") -> str:
    body = dedent(
        f"""
        <main id="main" class="utility-page shell">
          {breadcrumbs([("Index", "/"), (title, None)])}
          <p class="eyebrow">The Proper Ending Index</p>
          <h1>{title}</h1>
          <div class="content">{content}</div>
        </main>
        """
    ).strip()
    return shell_page(
        head_html=head(
            title=f"{title} · The Proper Ending Index",
            description=description,
            path=f"/{slug}",
            image="/assets/og/home.jpg",
            robots=robots,
            schema={
                "@context": "https://schema.org",
                "@graph": [
                    {
                        "@type": "WebPage",
                        "@id": f"{SITE}/{slug}#page",
                        "url": f"{SITE}/{slug}",
                        "name": title,
                        "description": description,
                        "dateModified": UPDATED,
                        "author": {"@id": AUTHOR_ID},
                    },
                    AUTHOR,
                    breadcrumb_schema([("Index", "/"), (title, f"/{slug}")]),
                ],
            },
        ),
        body=body,
        page=slug.replace(".html", ""),
    )


def legacy_notice(*, path: str, part: int | None = None) -> str:
    if part:
        paper = PAPERS[part - 1]
        title = f"Part {paper['roman']} prototype superseded"
        destination = f"/papers/{paper['slug']}.html"
        detail = "This prototype encoded an earlier research architecture and does not represent the current v6.2 paper. It has been retired to prevent a legacy visualization from being mistaken for the present specification."
    else:
        title = "Research prototypes retired"
        destination = "/papers/"
        detail = "The earlier interactive prototypes do not implement the current v6.2 papers. The paper records now provide the authoritative definitions, verification results, and claim boundaries."
    body = dedent(
        f"""
        <main id="main" class="utility-page shell">
          <div class="notice">
            <p class="eyebrow">Superseded research artifact</p>
            <h1>{title}</h1>
            <p>{detail}</p>
            <div class="hero-actions"><a class="button primary" href="{destination}">Open the current record</a><a class="button" href="/">Return to the index</a></div>
          </div>
        </main>
        """
    ).strip()
    canonical = destination if destination.endswith(".html") else "/papers/"
    return shell_page(
        head_html=head(
            title=f"{title} · The Proper Ending Index",
            description=detail,
            path=canonical,
            image="/assets/og/papers.jpg",
            robots="noindex,follow,noarchive",
        ),
        body=body,
        page="superseded",
    )


def research_index() -> dict:
    parts = []
    for paper in PAPERS:
        record = article_schema(paper)
        record["position"] = paper["part"]
        record["additionalProperty"] = [
            {"@type": "PropertyValue", "name": "Research function", "value": paper["function"]},
            {"@type": "PropertyValue", "name": "Research question", "value": paper["question"]},
            {"@type": "PropertyValue", "name": "SSRN abstract ID", "value": paper["ssrn"]},
        ]
        parts.append(record)
    return {
        "@context": "https://schema.org",
        "@type": "CreativeWorkSeries",
        "@id": f"{SITE}/papers/#trilogy",
        "name": "Workflow-Centric AI Governance Trilogy",
        "alternateName": "The Proper Ending Index research trilogy",
        "url": f"{SITE}/papers/",
        "mainEntityOfPage": f"{SITE}/research-index.json",
        "description": "Independent research archive on workflow-centric AI governance, governing-capacity loss, Proper Ending, and Authority Return.",
        "dateModified": UPDATED,
        "version": VERSION,
        "inLanguage": "en-US",
        "isAccessibleForFree": True,
        "creator": AUTHOR,
        "hasPart": parts,
        "about": [
            "AI governance",
            "human oversight",
            "workflow governance",
            "governing capacity",
            "Proper Ending",
            "Authority Return",
        ],
        "additionalProperty": [
            {"@type": "PropertyValue", "name": "Status", "value": "Working papers"},
            {"@type": "PropertyValue", "name": "Current version", "value": VERSION},
            {
                "@type": "PropertyValue",
                "name": "Claim discipline",
                "value": "Formal and synthetic results are bounded to their declared abstractions; public-record coding supports traceability rather than field validation.",
            },
            {
                "@type": "PropertyValue",
                "name": "Legacy prototype status",
                "value": "Superseded; excluded from current research routes because the prototypes do not implement version 6.2.",
            },
        ],
    }


def sitemap() -> str:
    entries = [
        "/",
        "/papers/",
        "/papers/part1.html",
        "/papers/part2.html",
        "/papers/part3.html",
        "/about.html",
        "/colophon.html",
        "/privacy.html",
        "/security.html",
    ]
    urls = "\n".join(
        f"  <url><loc>{SITE}{path}</loc><lastmod>{UPDATED}</lastmod></url>"
        for path in entries
    )
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n'


def main() -> None:
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
                <section><h2>Architecture</h2><p>Every public page is pre-rendered static HTML. The interface uses one shared stylesheet, one progressive-enhancement script, and a small analytics adapter. There is no framework runtime, external font request, client-side router, account system, or third-party UI package.</p></section>
                <section><h2>Typography &amp; material</h2><p>The system uses native serif, sans-serif, and monospace stacks. Color and geometry distinguish the trilogy without creating three incompatible microsites. Functional diagrams are built from semantic HTML and CSS so their content remains selectable, responsive, and printable.</p></section>
                <section><h2>Accessibility</h2><p>Landmarks, heading order, skip links, keyboard-visible focus, 44-pixel navigation targets, reduced-motion behavior, high-contrast text, and print styles are part of the base system. No research content depends on animation or pointer input.</p></section>
                <section><h2>Preservation</h2><p>SSRN remains the primary external research record. Versioned local PDFs are preserved with file size and SHA-256 recorded on each paper page and in <a href="/research-index.json">research-index.json</a>.</p></section>
                <section><h2>Build</h2><p>The site is generated by a dependency-free Python script and checked by a repository validator in continuous integration. Last rebuilt for the v6.2 papers on 23 August 2026.</p></section>
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
            No external font or framework runtime
            Current research version: 6.2
            Last update: 2026-08-23

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
                "background_color": "#f2efe8",
                "theme_color": "#f2efe8",
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
