"""Page renderers for the public research archive."""

from __future__ import annotations

from textwrap import dedent

from .layout import breadcrumbs, head, shell_page
from .model import (
    AUTHOR,
    AUTHOR_ID,
    PAPERS,
    SERIES_ID,
    SCHOLAR_URL,
    SITE,
    UPDATED,
    VERSION,
    Paper,
    article_schema,
    breadcrumb_schema,
    paper_url,
    series_schema,
    ssrn_url,
)
from .paper_content import part1_content, part2_content, part3_content


def home_page() -> str:
    item_list = [
        {
            "@type": "ListItem",
            "position": paper["part"],
            "url": paper_url(paper),
            "name": f"{paper['title']}: {paper['subtitle']}",
        }
        for paper in PAPERS
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
                "inLanguage": "en-US",
                "author": {"@id": AUTHOR_ID},
            },
            AUTHOR,
            series_schema(),
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
            <a class="sequence-row" href="/papers/{paper['slug']}.html" data-reveal>
              <p class="sequence-function">Part {paper['roman']} · {paper['function']}</p>
              <div>
                <h3 class="sequence-title">{paper['title']}</h3>
                <p class="sequence-copy">{paper['question']} {paper['description']}</p>
                <span class="sequence-state">{paper['state']} · v6.2 · {paper['pages']} pages</span>
              </div>
            </a>
            """
        ).strip()
        for paper in PAPERS
    )
    body = dedent(
        f"""
        <main id="main">
          <section class="hero shell" aria-labelledby="hero-title">
            <div class="hero-grid">
              <div data-reveal>
                <p class="eyebrow">AI Governance Research Archive · Workflow-Centric Trilogy · v6.2</p>
                <h1 id="hero-title"><span>A role alone</span><span class="hero-turn">is <em>not</em></span><span class="hero-governance">governance.</span></h1>
              </div>
              <div class="hero-aside" data-reveal>
                <p class="hero-statement">Accountability lives in the sequence.</p>
                <ol class="hero-transition" aria-label="Research sequence">
                  <li><b>01</b><span>Case</span></li>
                  <li><b>02</b><span>Institution</span></li>
                  <li><b>03</b><span>Exit</span></li>
                </ol>
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
            title="The Proper Ending Index — AI Governance Research Archive · Takashi Sato",
            description="Takashi Sato’s independent AI governance research archive on accountable decision routing, governing-capacity loss, Proper Ending, and Authority Return.",
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
            series_schema(),
            {
                "@type": "CollectionPage",
                "@id": f"{SITE}/papers/#catalogue",
                "name": "Workflow-Centric AI Governance Trilogy",
                "url": f"{SITE}/papers/",
                "dateModified": UPDATED,
                "author": {"@id": AUTHOR_ID},
                "mainEntity": {"@id": SERIES_ID},
            },
            breadcrumb_schema([("Index", "/"), ("Papers", "/papers/")]),
        ],
    }
    records: list[str] = []
    for paper in PAPERS:
        records.append(
            dedent(
                f"""
                <article class="sequence-row" data-reveal>
                  <p class="sequence-function">Part {paper['roman']} · {paper['function']}</p>
                  <div>
                    <h2 class="sequence-title"><a href="/papers/{paper['slug']}.html">{paper['title']}</a></h2>
                    <p class="paper-subtitle">{paper['subtitle']}</p>
                    <p class="sequence-copy">{paper['description']}</p>
                    <span class="sequence-state">SSRN {paper['ssrn']} · DOI {paper['doi']} · v6.2 · {paper['pages']} pages</span>
                    <div class="hero-actions">
                      <a class="button primary" href="/papers/{paper['slug']}.html">Paper record</a>
                      <a class="button" href="{ssrn_url(paper)}" target="_blank" rel="noopener noreferrer">SSRN <span class="arrow" aria-hidden="true">↗</span></a>
                    </div>
                  </div>
                </article>
                """
            ).strip()
        )
    map_nodes = "\n".join(
        f'<a class="research-map-node" href="/papers/{paper["slug"]}.html" data-part="{paper["part"]}"><span class="map-index">0{paper["part"]}</span><span class="map-glyph" aria-hidden="true"><i></i><i></i><i></i></span><b>{paper["function"]}</b><small>{paper["question"]}</small></a>'
        for paper in PAPERS
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
          <section class="research-map-section" aria-label="Trilogy research map">
            <h2 class="sr-only">Research map</h2>
            <div class="shell"><div class="research-map" data-reveal>{map_nodes}</div></div>
          </section>
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
            title="AI Governance Working Papers — The Proper Ending Index · Takashi Sato",
            description="Takashi Sato’s v6.2 AI governance working-paper trilogy on decision routing, governing-capacity loss, Proper Ending, and Authority Return.",
            path="/papers/",
            image="/assets/og/papers.jpg",
            schema=schema,
        ),
        body=body,
        active="papers",
        page="papers",
    )


def series_navigation(current: int) -> str:
    links: list[str] = []
    for paper in PAPERS:
        attrs = ' aria-current="page"' if paper["part"] == current else ""
        links.append(
            f'<a href="/papers/{paper["slug"]}.html"{attrs}><small>PART {paper["roman"]} · {paper["function"].upper()}</small><strong>{paper["title"]}</strong></a>'
        )
    return '<nav class="series-nav" aria-label="Paper trilogy">' + "".join(links) + "</nav>"


def paper_page(paper: Paper) -> str:
    if paper["part"] == 1:
        content = part1_content()
        toc = [
            ("overview", "Question"),
            ("contract", "Contract"),
            ("verification", "Verification"),
            ("boundary", "Boundary"),
        ]
    elif paper["part"] == 2:
        content = part2_content()
        toc = [
            ("overview", "Question"),
            ("state-model", "State model"),
            ("mechanisms", "Mechanisms"),
            ("propositions", "Propositions"),
            ("boundary", "Boundary"),
        ]
    else:
        content = part3_content()
        toc = [
            ("overview", "Question"),
            ("proper-ending", "Proper Ending"),
            ("authority-return", "Authority Return"),
            ("verification", "Verification"),
            ("measurement", "Measurement"),
            ("boundary", "Boundary"),
        ]

    toc_items = "".join(f'<li><a href="#{anchor}">{label}</a></li>' for anchor, label in toc)
    citation = (
        f"Sato, Takashi. “{paper['title']}: {paper['subtitle']}.” Working Paper, "
        f"version 6.2, 23 August 2026. https://doi.org/{paper['doi']}."
    )
    body = dedent(
        f"""
        <main id="main">
          <header class="paper-hero shell" data-roman="{paper['roman']}">
            <div class="paper-apparatus" aria-hidden="true"><span class="apparatus-label">{paper['function']}</span><i></i><i></i><i></i><i></i></div>
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
              <a class="button" href="/pdf/v{VERSION}/{paper['slug']}.pdf">Preserved PDF · v6.2</a>
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
                    <div class="record-row"><dt>Preserved file</dt><dd><a href="/pdf/v{VERSION}/{paper['slug']}.pdf">/pdf/v{VERSION}/{paper['slug']}.pdf</a> · {paper['bytes']:,} bytes</dd></div>
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
            title=f"{paper['title']}: {paper['subtitle']} — Takashi Sato",
            description=paper["description"],
            path=f"/papers/{paper['slug']}.html",
            image=f"/assets/og/{paper['slug']}.jpg",
            schema={
                "@context": "https://schema.org",
                "@graph": [
                    AUTHOR,
                    series_schema(),
                    article_schema(paper),
                    breadcrumb_schema(
                        [
                            ("Index", "/"),
                            ("Papers", "/papers/"),
                            (f"Part {paper['roman']}", f"/papers/{paper['slug']}.html"),
                        ]
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
                "mainEntity": {"@id": AUTHOR_ID},
            },
            breadcrumb_schema([("Index", "/"), ("Author", "/about.html")]),
        ],
    }
    body = dedent(
        f"""
        <main id="main">
          <header class="author-hero shell">
            {breadcrumbs([("Index", "/"), ("Author", None)])}
            <div class="author-hero-grid">
              <div class="author-name" data-reveal>
                <p class="eyebrow">Author record · 001</p>
                <h1><span>Takashi Sato</span></h1>
              </div>
              <div class="author-thesis" data-reveal>
                <p>I study the conditions under which human oversight remains real—and the terms on which an AI-assisted institution should stop, transfer authority, and close.</p>
              </div>
            </div>
          </header>
          <div class="section author-section">
            <div class="shell author-layout">
              <aside class="author-rail" data-reveal>
                <h2 class="label">At a glance</h2>
                <dl class="author-facts">
                  <div><dt>Role</dt><dd>Independent researcher</dd></div>
                  <div><dt>Native name</dt><dd lang="ja">佐藤貴士</dd></div>
                  <div><dt>Base</dt><dd>Sapporo, Japan</dd></div>
                  <div><dt>Series</dt><dd>The Proper Ending Index</dd></div>
                </dl>
                <nav class="author-links" aria-label="External author records">
                  <a href="https://orcid.org/0009-0003-1584-6965" target="_blank" rel="me noopener noreferrer"><span>ORCID</span><span aria-hidden="true">↗</span></a>
                  <a href="https://papers.ssrn.com/Sol3/Cf_Dev/AbsByAuth.cfm?per_id=9540672" target="_blank" rel="me noopener noreferrer"><span>SSRN</span><span aria-hidden="true">↗</span></a>
                  <a href="{SCHOLAR_URL}" target="_blank" rel="me noopener noreferrer"><span>Google Scholar</span><span aria-hidden="true">↗</span></a>
                </nav>
              </aside>
              <div class="author-copy">
                <section data-reveal>
                  <p class="eyebrow">01 · Research position</p>
                  <h2>Oversight is a capacity, not a presence.</h2>
                  <p class="lead">A person can be present in a workflow and still be unable to govern it.</p>
                  <p>My work treats evidence, time, authority, review capacity, fallback readiness, and remedy as institutional conditions—not interface labels.</p>
                  <p>The current trilogy follows that problem at three levels: the decision contract, the institution’s governing capacity, and the exit through which authority is returned.</p>
                </section>
                <section data-reveal>
                  <p class="eyebrow">02 · Research practice</p>
                  <h2>Formalize the claim. Publish the boundary.</h2>
                  <p>The papers combine typed protocols, finite-state exploration, mutation testing, synthetic stress tests, and theory-directed public-record traceability.</p>
                  <p>Each method carries an explicit limit: executable consistency is not legal sufficiency, synthetic performance is not field validity, and a purposive official-record corpus is not representative evidence.</p>
                </section>
                <section data-reveal>
                  <p class="eyebrow">03 · Public record</p>
                  <h2>One author. One verifiable record.</h2>
                  <p>SSRN carries the primary paper records. This archive preserves versioned copies and connects them to a single public author identity.</p>
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
            title="Takashi Sato — AI Governance Researcher · The Proper Ending Index",
            description="Author record for Takashi Sato (佐藤貴士), an independent AI governance researcher in Sapporo studying accountable decision routing, governing capacity, and institutional exit.",
            path="/about.html",
            image="/assets/og/about.jpg",
            schema=schema,
            og_type="profile",
        ),
        body=body,
        active="about",
        page="about",
    )


def utility_page(
    *,
    slug: str,
    title: str,
    description: str,
    content: str,
    robots: str = "index,follow",
) -> str:
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
        page="legacy",
    )
