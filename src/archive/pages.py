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
from .abstracts import ABSTRACTS
from .concepts import CONCEPTS, CONCEPT_SOURCES, concept_schema
from html import escape


def concept_register() -> str:
    rows: list[str] = []
    for slug, title, paper, roman, anchor, status, summary, assessment in CONCEPTS:
        links = "".join(
            f'<a class="button" href="/papers/{paper}.html#{section}" aria-label="{label}: {escape(title)}">{label}</a>'
            for label, section in (("Explanation", anchor), ("Assessment", assessment), ("Limits", "boundary"), ("Citation", "citation"))
        )
        start, end, _ = CONCEPT_SOURCES[slug]
        pages = f"p. {start}" if start == end else f"pp. {start}–{end}"
        links += (
            f'<a class="button" href="/pdf/v{VERSION}/{paper}.pdf#page={start}" '
            f'aria-label="Preserved v{VERSION} PDF, {pages}: {escape(title)}">PDF {pages}</a>'
        )
        rows.append(
            f'<article class="record-row concept-record" id="concept-{slug}"><div><p class="label">Part {roman}</p>'
            f'<h3>{escape(title)}</h3></div><div><p><strong>{escape(status)}</strong> {escape(summary)}</p>'
            f'<div class="paper-actions">{links}</div></div></article>'
        )
    return "".join(rows)


def research_map_nodes() -> str:
    return "\n".join(
        f'<a class="research-map-node" href="/papers/{paper["slug"]}.html" data-part="{paper["part"]}"><span class="map-index">0{paper["part"]}</span><span class="map-glyph" aria-hidden="true"><i></i><i></i><i></i></span><b>{paper["function"]}</b><small>{paper["question"]}</small></a>'
        for paper in PAPERS
    )


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
          <section class="hero shell identity-hero" aria-labelledby="hero-title">
            <div class="identity-masthead"><span>TAKASHI SATO <span class="identity-masthead-sep">/</span> INDEPENDENT RESEARCH</span><span>AI GOVERNANCE · 2026</span></div>
            <div class="identity-hero-grid">
              <div class="identity-copy">
                <p class="identity-overline">THE PROPER ENDING INDEX <span aria-hidden="true">/</span> 01–03</p>
                <h1 id="hero-title">A role alone<br>is not <strong>governance.</strong></h1>
                <p class="identity-thesis">Accountability lives in the sequence.</p>
                <p class="identity-detail">Three working papers examine decision routing in human–AI cases, the loss of governing capacity beneath intact procedures, and how workflows can end without abandoning unresolved obligations. Analytical models and bounded verification—not demonstrated operational effectiveness.</p>
                <div class="identity-actions">
                  <a class="button primary" href="/papers/">Explore the research <span aria-hidden="true">↗</span></a>
                  <a class="button" href="/about.html">Author record</a>
                </div>
              </div>
              <figure class="identity-art">
                <div class="identity-art-head"><span>THE INSTRUMENTS / I—III</span><span>CONCEPTUAL STUDY</span></div>
                <nav class="identity-instruments" aria-label="Three distinct research questions">{research_map_nodes()}</nav>
                <figcaption>Conceptual instruments, not empirical results. Each is a distinct analytical question and opens its corresponding paper.</figcaption>
              </figure>
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

          <section class="section compact" aria-labelledby="verification-register">
            <div class="shell boundary" data-reveal>
              <h2 id="verification-register">Verification register.</h2>
              <div>
                <p class="label">Part I / Finite contract</p>
                <p>v6.2 independent reimplementation: 1,024 Stage-1 and 1,248 applicable Stage-2 configurations; nine isolated guard mutations. <a href="/papers/part1.html#verification">Truth-table abstraction and invariant checks.</a></p>
                <p class="label">Part II / Descriptive model</p>
                <p>Five rejectable propositions and a comparative retirement test. <a href="/papers/part2.html#propositions">Empirical rejection criteria, not a validated classification.</a></p>
                <p class="label">Part III / Transition protocol</p>
                <p>Frozen v5.9 execution, carried forward in v6.2: 8,564 reachable states, 36,096 enabled transitions and 30 guard mutations within a selected finite abstraction. Synthetic benchmark results are also carried forward; no new execution is claimed in v6.2. <a href="/papers/part3.html#verification">Verification scope and disclosed execution provenance.</a></p>
                <p>These quantities describe different research objects. They are not comparable measures of validity, performance or practical effectiveness.</p>
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
                <p>Independent critical review is invited. <a href="/papers/#critical-review">Examine the review questions and submission route</a>.</p>
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
                  <p class="lead">Takashi Sato (<span lang="ja">佐藤貴士</span>) studies how AI-assisted institutions preserve accountable judgment—and how they should contain, retire, and transfer decision capacity when governance fails.</p>
                  <div class="hero-actions">
                    <a class="button" href="/about.html">About the author</a>
                    <a class="button" href="/papers/#japanese" lang="ja">日本語の研究案内</a>
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
            title="Takashi Sato (佐藤貴士) — AI Governance Research Archive",
            description="Takashi Sato (佐藤貴士), independent researcher in Sapporo. Working papers on AI governance, accountable decisions, governing-capacity loss, Proper Ending, and Authority Return.",
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
            concept_schema(),
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
                      <a class="button" href="/pdf/v{VERSION}/{paper['slug']}.pdf" aria-label="Read PDF ({paper['pages']} pages) — Part {paper['roman']}, version {VERSION}">Read PDF ({paper['pages']} pages)</a>
                      <a class="button" href="{ssrn_url(paper)}" target="_blank" rel="noopener noreferrer">SSRN <span class="arrow" aria-hidden="true">↗</span></a>
                    </div>
                  </div>
                </article>
                """
            ).strip()
        )
    map_nodes = research_map_nodes()
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
                <p>For citation and version history, use the SSRN record as the primary external research record. Local PDFs are preserved copies of version 6.2. <a href="#concepts">Browse concepts and evidence.</a> <a href="#japanese" lang="ja">日本語の研究案内</a></p>
              </div>
            </div>
          </section>
          <section class="section compact" id="japanese" lang="ja" aria-labelledby="japanese-title">
            <div class="shell">
              <div class="section-head">
                <p class="label">研究概要</p>
                <div>
                  <h2 id="japanese-title">AIガバナンスにおける権限と責任</h2>
                  <p class="section-intro">私の研究の主題は、AIを組み込んだ意思決定において、組織が判断の主体であり続けるための制度的条件である。権限を付与することと、それを実効的に行使できることとは別の問題である。この三部作では、個別案件の処理、組織の統治能力、運用の終結を、それぞれ独立した分析課題として扱う。</p>
                </div>
              </div>
              <div class="record-list">
                <article class="record-row"><div><p class="label">第一部 ／ 案件の処理経路</p><h3>案件の処理と判断・執行の分離</h3></div><div><p>型付きゲート契約（<span lang="en">Typed Gate Contract</span>）は、案件の処理経路を定める二段階の形式仕様である。第一段階では、診断状態、審査の権限と能力、代替手段の承認と実行準備の状況に応じて処理経路を定める。権限に基づく審査へ進んだ案件については、第二段階で、権限の範囲内で実際に下された、その時点で有効な署名付き判断を記録する。</p><p>すべての診断が通過判定となっても、それは執行適格性を示すにとどまる。執行は別個の仕様に従う。証拠の欠落を暗黙の通過判定で補わず、暫定的な遮断を最終的な否認とみなさない。</p><p><a href="/papers/part1.html">論文・検証範囲（英語）</a></p></div></article>
                <article class="record-row"><div><p class="label">第二部 ／ 統治能力</p><h3>手続の維持と統治能力の喪失</h3></div><div><p>手続に覆い隠された統治能力の喪失（<span lang="en">Procedurally Masked Governing-Capacity Loss; PMGCL</span>）とは、外形上の手続遵守度が維持または改善されているにもかかわらず、独立した判断能力と実効的な統治能力が実質的かつ持続的に低下し、あらかじめ保護の対象と定めた機能にも実質的な毀損が生じている状態をいう。</p><p>濫用前崩壊（<span lang="en">Pre-Abuse Collapse; PAC</span>）は、PMGCLのうち特定の因果的条件を満たす状態を指す暫定的な成因類型である。悪意ある行為に至る経路についてあらかじめ定めた介入条件または参照条件の下で、通常のAI利用に伴う実質的な悪化を示す因果的対比が識別されていることを要する。濫用が存在しないことや、崩壊が濫用に先行したことを立証する分類ではない。</p><p>状態の記述とその成因の説明を区別し、経験的な反証が可能なモデルとして提示する。現実の組織における妥当性は未検証である。</p><p><a href="/papers/part2.html">論文・状態モデルと反証条件（英語）</a></p></div></article>
                <article class="record-row"><div><p class="label">第三部 ／ 責任ある終結</p><h3>責任ある終結と実効的な判断能力の再構成</h3></div><div><p>適正な終結（<span lang="en">Proper Ending</span>）と権限返還（<span lang="en">Authority Return</span>）は、AIを用いた業務を可逆的な封じ込め、運用廃止、終結へと移行させる際の条件を規定する。異常を示す指標は調査の端緒となり得るが、それ自体は介入の権限を付与しない。終結に先立ち、証拠の保全、サービス継続措置、通知と救済、未処理案件ごとの責任主体を確保し、必要な確認を経て権限者の承認を得る。</p><p>意思決定機能を存続させる場合は、引受けに同意した後継主体が実際に判断できるよう、その能力を再構成する。機能を廃止する場合にも、残存する記録管理や救済の責任を負う主体を定める。運用を停止することと、制度的責任を全うすることとは異なる。</p><p><a href="/papers/part3.html">論文・終了と権限移転の条件（英語）</a></p></div></article>
              </div>
              <p class="section-intro">以上は英語論文（v6.2、2026年8月23日改訂）に基づく概要であり、正式な翻訳でも新たな研究結果でもない。専門概念の定義は英語原文に従う。三論文はいずれもワーキングペーパーである。形式的検証と合成データによる結果は、各論文で設定した抽象化と実験条件の範囲に限られ、現実の組織における有効性を実証するものではない。<a href="#concepts">研究概念と根拠（英語）</a>、<a href="#critical-review">批判的検討・反証（英語）</a>に、各概念の出典と検討課題を示した。</p>
            </div>
          </section>
          <section class="section compact" id="concepts">
            <div class="shell">
              <div class="section-head">
                <p class="label">Research architecture / 01—07</p>
                <div>
                  <h2>Concepts and evidence.</h2>
                  <p class="section-intro">An index of the archive's research concepts, not new definitions or independent validation. Each entry links to its explanation, assessment, stated limits, citation and the relevant pages of the preserved v6.2 paper.</p>
                </div>
              </div>
              <div class="record-list">{concept_register()}</div>
            </div>
          </section>
          <section class="section compact" id="critical-review">
            <div class="shell boundary" data-reveal>
              <h2>How to challenge these papers.</h2>
              <div>
                <p>The most useful review identifies a claim that is unclear, already established elsewhere, unsupported, or contradicted by a counterexample. Criticism is welcome across all three working papers.</p>
                <p><strong>Part I / Decision routing.</strong> Are important states or precedence rules missing? Can a counterexample breach the separation between typed routing, authorized disposition, and actual execution?</p>
                <p><strong>Part II / Governing capacity.</strong> Can the proposed state distinctions be separated from existing accounts of organizational failure? What observations would contradict the descriptive model?</p>
                <p><strong>Part III / Accountable exit.</strong> Do the proposed dependencies preserve evidence, remedy, service continuity, and accountable authority? Which transitions are infeasible or omit a failure path?</p>
                <h3>Selected prior work for comparison</h3>
                                <p>The following are comparison anchors, not endorsements or a systematic literature review. The existence of an oversight or decommissioning concern is not, by itself, a novel contribution.</p>
                                <p><a href="https://doi.org/10.1177/1023263X20978649" target="_blank" rel="noopener noreferrer">Koulu (2020), Proceduralizing control and discretion</a>, examines how human oversight can become an empty procedural safeguard. The open question is what the present models define beyond that critique.</p>
                                <p><a href="https://doi.org/10.1016/j.clsr.2022.105681" target="_blank" rel="noopener noreferrer">Green (2022), The flaws of policies requiring human oversight of government algorithms</a>, argues for institutional oversight. Part II should be assessed for a distinct, refutable state model rather than the general proposition that institutions matter.</p>
                                <p><a href="https://airc.nist.gov/airmf-resources/airmf/5-sec-core/" target="_blank" rel="noopener noreferrer">NIST AI RMF 1.0 (2023), GOVERN 1.7 and MANAGE 4.1</a>, already addresses safe decommissioning, appeal, recovery, and ongoing monitoring. Part III's claimed contribution must rest on what its proposed transition constraints add to that baseline.</p>
                                <p><a href="https://doi.org/10.1007/s43681-026-01147-7" target="_blank" rel="noopener noreferrer">Zhu et al. (2026), Designing meaningful human oversight in AI</a>, distinguishes human evaluative agency from AI operative agency and describes concrete oversight patterns. Parts I and II should be compared on the level of explicit states, authority rules, and testability.</p>
                                <p>These are questions for comparison, not determinations of originality, priority, reproducibility, or practical effectiveness. The three papers remain version 6.2; this site note does not revise their references or claims.</p>
                <p>Send critiques, relevant prior work, or reproducible counterexamples to <a href="mailto:i@takashisato.me?subject=Critical%20review%20of%20AI%20governance%20working%20papers">i@takashisato.me</a>. Please identify the paper, version 6.2, section or page, and supporting reasoning. This invitation is not a claim of completed independent peer review or field validation.</p>
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

    toc = [("abstract", "Abstract"), *toc, ("citation", "Citation")]
    toc_items = "".join(f'<li><a href="#{anchor}">{label}</a></li>' for anchor, label in toc)
    abstract_html = "".join(f"<p>{escape(paragraph)}</p>" for paragraph in ABSTRACTS[paper["slug"]])
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
            <div class="paper-intro">
              <p class="eyebrow" data-reveal>Workflow-Centric AI Governance Trilogy · Part {paper['roman']}</p>
              <h1 data-reveal>{paper['title']}</h1>
              <p class="paper-subtitle" data-reveal>{paper['subtitle']}</p>
            </div>
            <div class="paper-meta" data-reveal>
              <span>Takashi Sato</span>
              <span>Working paper · v6.2</span>
              <span>23 August 2026</span>
              <span>{paper['pages']} pages</span>
              <span>SSRN {paper['ssrn']}</span>
            </div>
            <div class="paper-actions" data-reveal>
              <a class="button primary" href="{ssrn_url(paper)}" target="_blank" rel="noopener noreferrer">SSRN research record <span class="arrow" aria-hidden="true">↗</span></a>
              <a class="button" href="#abstract" aria-label="Read abstract">Abstract <span aria-hidden="true">↓</span></a>
              <a class="button" href="/pdf/v{VERSION}/{paper['slug']}.pdf" aria-label="Preserved PDF · v6.2">PDF · v6.2</a>
              <a class="button" href="https://doi.org/{paper['doi']}" target="_blank" rel="noopener noreferrer">DOI <span class="arrow" aria-hidden="true">↗</span></a>
            </div>
          </header>

          <div class="section">
            <div class="shell paper-layout">
              <nav class="toc" aria-label="On this page">
                <p class="label">On this page</p>
                <ol>{toc_items}</ol>
              </nav>
              <article class="content" data-reveal>
                <h2 class="sr-only">Part {paper['roman']} analysis</h2>
                <section id="abstract"><p class="eyebrow">Author abstract · v{VERSION}</p><h2>Abstract</h2>{abstract_html}<p class="caveat">Transcribed from <a href="/pdf/v{VERSION}/{paper['slug']}.pdf#page=2">the preserved paper, page 2</a>. The original includes the generative-AI disclosure.</p></section>
                {content}
                <section id="citation">
                  <p class="eyebrow">Citation &amp; preservation</p>
                  <h2>Cite the versioned record.</h2>
                  <p>The SSRN page is the primary external research record. The local file is a preserved copy of version 6.2 for stable access.</p>
                  <p>To challenge an assumption, identify relevant prior work, or report a counterexample, see the <a href="/papers/#critical-review">critical-review questions and contact route</a>.</p>
                  <div class="citation">{citation}</div>
                  <div class="paper-actions"><a class="button" href="/citations/v{VERSION}/{paper['slug']}.bib" download>Export BibTeX</a><a class="button" href="/citations/v{VERSION}/{paper['slug']}.ris" download>Export RIS</a><a class="button" href="/citations/v{VERSION}/{paper['slug']}.json" download>Export CSL-JSON</a></div>
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
                "name": "Takashi Sato (佐藤貴士) · Author Record",
                "dateModified": "2026-11-24",
                "description": "Independent AI governance research in Sapporo, Japan.",
                "mainEntity": {"@id": AUTHOR_ID},
            },
            breadcrumb_schema([("Index", "/"), ("Author", "/about.html")]),
        ],
    }
    body = dedent(
        f"""
        <main id="main" class="portrait">
          <header class="portrait-chamber">
            <div class="shell portrait-inner">
              {breadcrumbs([("Index", "/"), ("Author", None)])}
              <div class="portrait-mast">
                <p>Independent research</p>
                <p>Sapporo, Japan</p>
              </div>
              <div class="portrait-grid">
                <div class="portrait-name">
                  <h1>Takashi<br>Sato</h1>
                  <p lang="ja">佐藤貴士</p>
                </div>
                <div class="portrait-signature" aria-hidden="true"></div>
              </div>
              <div class="portrait-position">
                <p class="portrait-question">What remains when form and function diverge?</p>
                <p>I study authority, responsibility, and independent judgment, with particular attention to the conditions under which institutions retain or lose the capacity to govern. My current work examines these questions in AI-assisted systems.</p>
              </div>
            </div>
          </header>
          <section class="shell portrait-record" aria-labelledby="portrait-research">
            <div class="portrait-record-grid">
              <div>
                <p class="eyebrow">Research</p>
                <h2 id="portrait-research">The Proper Ending Index</h2>
                <p>Three working papers on accountable decision routing, governing capacity, and responsible workflow exit. Their claims, methods, and limits are documented in the archive.</p>
                <a class="button primary" href="/papers/">Explore the research <span aria-hidden="true">↗</span></a>
                <p class="portrait-note"><a href="/papers/#critical-review">Invitation to independent review</a></p>
              </div>
              <div class="portrait-identifiers">
                <h2 class="eyebrow">Scholarly record</h2>
                <dl>
                  <div><dt>ORCID</dt><dd><a href="https://orcid.org/0009-0003-1584-6965" target="_blank" rel="me noopener noreferrer">0009-0003-1584-6965 <span aria-hidden="true">↗</span></a></dd></div>
                  <div><dt>SSRN</dt><dd><a href="https://papers.ssrn.com/Sol3/Cf_Dev/AbsByAuth.cfm?per_id=9540672" target="_blank" rel="me noopener noreferrer">Author 9540672 <span aria-hidden="true">↗</span></a></dd></div>
                  <div><dt>Google Scholar</dt><dd><a href="{SCHOLAR_URL}" target="_blank" rel="me noopener noreferrer">Author profile <span aria-hidden="true">↗</span></a></dd></div>
                </dl>
                <h2 class="eyebrow portrait-contact">Correspondence</h2>
                <a class="portrait-mail" href="mailto:i@takashisato.me">i@takashisato.me</a>
              </div>
            </div>
          </section>
        </main>
        """
    ).strip()
    return shell_page(
        head_html=head(
            title="Takashi Sato (佐藤貴士) — AI Governance Researcher",
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
                        "dateModified": "2026-11-24" if slug == "colophon.html" else UPDATED,
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
