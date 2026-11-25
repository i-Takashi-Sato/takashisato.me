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
    SITE_NAME,
    publication_collection_refs,
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
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "@id": f"{SITE}/#website",
                "url": f"{SITE}/",
                "name": SITE_NAME,
                "alternateName": "佐藤貴士",
                "description": "Independent research and writing by Takashi Sato. The current collection examines workflow-centric AI governance, governing-capacity loss, Proper Ending, and Authority Return.",
                "inLanguage": "en-US",
                "author": {"@id": AUTHOR_ID},
            },
            AUTHOR,
            series_schema(),
            {
                "@type": "CollectionPage",
                "@id": f"{SITE}/#index",
                "url": f"{SITE}/",
                "name": "Takashi Sato — Research & Writings",
                "hasPart": publication_collection_refs(),
                "isPartOf": {"@id": f"{SITE}/#website"},
                "mainEntity": {"@id": f"{SITE}/publications/#catalogue"},
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
            <div class="identity-masthead"><span>INDEPENDENT ARCHIVE</span><span>SAPPORO, JAPAN</span></div>
            <div class="identity-hero-grid">
              <div class="identity-copy">
                <p class="identity-overline">RESEARCH &amp; WRITINGS</p>
                <h1 id="hero-title">Takashi<br>Sato</h1>
                <p class="identity-thesis"><span lang="ja">佐藤貴士</span></p>
                <p class="identity-detail">An independent archive of research and writing. The current collection asks how institutions govern AI-assisted decisions, how that capacity erodes, and how failing workflows can be brought to an accountable end.</p>
                <div class="identity-actions">
                  <a class="button primary" href="/publications/">Explore publications <span aria-hidden="true">↗</span></a>
                  <a class="button" href="/papers/">Featured research</a>
                </div>
              </div>
              <figure class="identity-art">
                <div class="identity-art-head"><span>THE PROPER ENDING INDEX</span><span>I—III</span></div>
                <nav class="identity-instruments" aria-label="Three distinct research questions">{research_map_nodes()}</nav>
                <figcaption>Three working papers, each represented by a conceptual instrument rather than empirical data. Select an instrument to read the paper.</figcaption>
              </figure>
            </div>
          </section>

          <section class="section">
            <div class="shell">
              <div class="section-head" data-reveal>
                <p class="label">Featured research collection</p>
                <div>
                  <h2>From a case decision to an institutional exit.</h2>
                  <p class="section-intro">The papers address related problems without reducing them to a single score or prescribing a universal lifecycle. Each poses a distinct question and defines the limits of its claims.</p>
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
                <p>The v6.2 independent reimplementation reported in Part I covers 1,024 Stage-1 and 1,248 applicable Stage-2 configurations and nine isolated guard mutations. It is not an independent third-party replication. <a href="/papers/part1.html#verification">Truth-table abstraction and invariant checks.</a></p>
                <p class="label">Part II / Descriptive model</p>
                <p>Five rejectable propositions and a comparative retirement test. <a href="/papers/part2.html#propositions">Criteria for empirical rejection, not evidence of a validated classification.</a></p>
                <p class="label">Part III / Transition protocol</p>
                <p>Frozen v5.9 execution, carried forward in v6.2: 8,564 reachable states, 36,096 enabled transitions and 30 guard mutations within a selected finite abstraction. Synthetic benchmark results are also carried forward; no new execution is claimed in v6.2. <a href="/papers/part3.html#verification">Verification scope and disclosed execution provenance.</a></p>
                <p>These quantities describe different research objects. They are not comparable measures of validity, performance or practical effectiveness.</p>
              </div>
            </div>
          </section>

          <section class="section">
            <div class="shell">
              <div class="boundary" data-reveal>
                <h2>Limits of the featured research.</h2>
                <div>
                  <p>These are working papers and formalized research artifacts—not legal advice, a compliance certification, an operational decision engine, or evidence that the proposed architectures improve outcomes in the field.</p>
                  <p>Finite checks are exhaustive only over each declared abstraction. The shared public-record corpus supports traceability, not frequency, prediction, causal sufficiency, or independent validation.</p>
                <p>Independent critical review is invited. <a href="/papers/#critical-review">Read the review questions and submit a critique</a>.</p>
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
                  <p class="lead">Current research examines how institutions retain accountable judgment in AI-assisted decisions. When governance fails, the question is how to contain or retire the workflow and restore or reassign the capacity to decide.</p>
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
            title="Takashi Sato (佐藤貴士) — Research & Writings",
            description="Takashi Sato (佐藤貴士), independent researcher in Sapporo. An archive of research and writing, featuring the current AI governance collection, The Proper Ending Index.",
            path="/",
            image="/assets/og/archive.jpg",
            schema=schema,
            site_verification=True,
        ),
        body=body,
        active="index",
        page="home",
    )


def ja_phrases(*phrases: str) -> str:
    """Keep semantic Japanese phrases intact when the reading column wraps."""
    return "".join(f'<span class="ja-title-tail">{escape(phrase)}</span>' for phrase in phrases)


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
            <p class="page-deck" data-reveal>Accountability can fail when a case is routed, as an institution’s governing capacity erodes, or when a workflow ends. The trilogy treats these as related but distinct governance problems.</p>
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
                <p class="label">日本語の研究案内</p>
                <div>
                  <h2 id="japanese-title">{ja_phrases("AIガバナンス", "における", "権限と責任")}</h2>
                  <p class="section-intro">私の研究が問うのは、AIを用いる組織が、いかに判断の主体であり続けるかである。個別案件の処理、組織の統治能力、運用の終了という三つの水準から、この問題を検討する。三論文に共通する原則は、診断、暫定的な判定、検知指標のいずれにも、それ自体として制度上の決定権限を与えないことである。</p>
                  <p class="section-intro">三論文はワーキングペーパー（v6.2、2026年8月23日改訂）である。以下は英語原論文に基づく概要であり、正式な翻訳でも新たな研究結果でもない。</p>
                </div>
              </div>
              <div class="record-list">
                <article class="record-row">
                  <div><p class="label">第一部 ／ 意思決定の経路</p><h3>{ja_phrases("次に何が", "許されるのか")}</h3></div>
                  <div><p>人間が手続に関与していても、必要な証拠、時間、決定権限、審査の余力、実行可能な代替手段のいずれかを欠けば、監督は実質を失い得る。型付きゲート規約（<span lang="en">Typed Gate Contract</span>）は、案件の処理経路と権限者による決定を、二段階に分けて規定する。</p>
                    <p>第一段階では、三つの診断の結果、審査の権限と余力、代替手段の承認と準備状況に基づき、案件の処理経路を定める。三つの診断がすべて通過しても、実行の資格が認められるにすぎない。実行は別個の規約に従う。権限に基づく審査に進んだ案件については、第二段階で、実際に下された、その時点で有効かつ権限の範囲内にある署名付きの決定を記録する。</p>
                    <p>証拠の不足を暗黙の通過判定に、暫定的な遮断を最終的な否認に置き換えない。</p>
                    <p><a href="/papers/part1.html">論文・検証範囲{ja_phrases("（英語）")}</a></p></div>
                </article>
                <article class="record-row">
                  <div><p class="label">第二部 ／ 統治能力</p><h3>{ja_phrases("手続が維持されていても、", "統治できているか")}</h3></div>
                  <div><p>手続に覆われた統治能力の喪失（<span lang="en">Procedurally Masked Governing-Capacity Loss; PMGCL</span>）とは、外形上の手続遵守が維持または改善される一方で、独立した判断の寄与と実効的な統治能力がともに実質的かつ持続的に低下し、あらかじめ定めた保護対象機能も実質的に損なわれている状態をいう。四つの要件はいずれも不可欠であり、この定義は成因を特定するものではない。</p>
                    <p><span lang="en">Pre-Abuse Collapse</span>（<span lang="en">PAC</span>）は、PMGCLの成因に関する暫定的な下位類型である。悪意ある行為の経路について、介入条件または参照条件を事前に定める。その条件の下で、通常の組織的要因への曝露が保護対象機能に実質的な悪影響を及ぼすことを示す因果的対比が識別された場合に限り、この類型を用いる。「<span lang="en">Pre-Abuse</span>」は、崩壊が悪意ある行為に時間的に先行することを意味しない。また、この類型は、悪意ある行為が存在しないことも、十分構成原因（<span lang="en">sufficient component cause</span>）の意味で不要であったことも示さない。</p>
                    <p>いずれも妥当性の検証を経ていない。既存理論や構成要素を連続量で扱うモデルと比較し、拠点または期間を分けた検証において、判別力、早期把握のための先行時間、較正、介入判断への有用性のいずれにも再現可能な付加価値が認められなければ、当該概念の独立した使用を撤回する。PACにはさらに、再現可能な因果的識別と、記述的な状態分類を超える付加価値が求められる。</p>
                    <p><a href="/papers/part2.html">論文・状態モデルと反証条件{ja_phrases("（英語）")}</a></p></div>
                </article>
                <article class="record-row">
                  <div><p class="label">第三部 ／ 終了と権限返還</p><h3>{ja_phrases("責任を保ったまま、", "いかに終えるか")}</h3></div>
                  <div><p>AIの稼働を止めても、その判断規則は、案件の待ち行列、記録、人員配置、委託先との接続などに残り得る。拙速な停止は、必要なサービスを断ち、証拠を失わせ、未解決案件を宙に浮かせかねない。第三部は、兆候の調査、可逆的な封じ込め（<span lang="en">Circuit Breaker</span>）、適正終了（<span lang="en">Proper Ending</span>）、権限返還を区別する。指標は調査の端緒となり得るが、封じ込め、終了、再開、再配備を授権するものではない。</p>
                    <p>適正終了は、権限者の承認、封じ込め、証拠保全、通知、救済、引継ぎ、運用廃止、独立した確認を含む制度的な移行過程である。各手続の依存関係を規定するのであって、一律の逐次処理を求めるものではない。終結（<span lang="en">Closure</span>）には、証拠の保全、サービスの継続措置、通知と利用可能な救済経路、未解決の全案件と残存する義務を担う責任主体、独立した確認、権限者による終結の承認を要する。終結によって、記録保存、補償、不服申立てへの対応などの継続的な義務が消滅するわけではない。</p>
                    <p>権限返還（<span lang="en">Authority Return</span>）は、自動化以前の体制が当然に復元されることを意味しない。意思決定機能を存続させる場合には、引受けを承諾した後継主体に、判断、説明、是正、資源の確保を行う実質的な能力を再構成する。機能を廃止する場合には、残存する記録、未解決案件、救済義務を担う主体を定める。</p>
                    <p><a href="/papers/part3.html">論文・終了と権限返還の条件{ja_phrases("（英語）")}</a></p></div>
                </article>
              </div>
              <div class="ja-evidence">
                <h3>検証の範囲</h3>
                <div>
              <p class="section-intro">第一部と第三部の形式的検証が確認したのは、著者が定めた有限の抽象化の範囲内で、設定済みの不変条件との整合性が保たれることに限られる。第二部は記述モデルと反証可能な研究計画を提示したものであり、第三部の合成データによる試験は指標の実装と失敗の様態を調べるものである。現実の組織における有効性や検出性能を実証するものではない。</p>
              <p class="section-intro">三論文は、オーストラリアのRobodebt制度に関する王立委員会、オランダの保育手当問題に関する議会調査、米国ミシガン州の失業保険に関する公的監査から、同一の十五の記述箇所を用いている。目的に応じて選んだ失敗事例を著者一人が理論に沿って分類したものであり、統治上の対象が公的記録から追跡できることを例示するにとどまる。因果関係、発生頻度、予防効果を示すものではなく、記録の共用は三論文の独立した裏づけにはならない。</p>
              <p class="section-intro">三論文は、独立した査読や現場検証の完了、法的な十分性、新規性の確定を主張するものではない。<a href="#concepts">研究概念と根拠{ja_phrases("（英語）")}</a>、<a href="#critical-review">反証・批判の受付{ja_phrases("（英語）")}</a>も参照されたい。</p>
                </div>
              </div>
            </div>
          </section>
          <section class="section compact" id="concepts">
            <div class="shell">
              <div class="section-head">
                <p class="label">Research architecture / 01—07</p>
                <div>
                  <h2>Concepts and evidence.</h2>
                  <p class="section-intro">An index of the trilogy’s research concepts, not a set of new definitions or evidence of independent validation. Each entry links to the concept’s explanation, assessment, limits, citation, and the relevant pages of the preserved v6.2 paper.</p>
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
                <p><strong>Part II / Governing capacity.</strong> Do the proposed state distinctions capture anything that existing accounts of organizational failure do not? What observations would contradict the descriptive model?</p>
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
                "dateModified": "2026-11-26",
                "description": "Independent research in Sapporo, Japan. Current research: AI governance.",
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
                <p>I study authority, responsibility, and independent judgment. My current research asks how institutions retain the capacity to govern AI-assisted decisions, how that capacity is lost, and what an accountable exit requires.</p>
              </div>
            </div>
          </header>
          <section class="shell portrait-record" aria-labelledby="portrait-research">
            <div class="portrait-record-grid">
              <div>
                <p class="eyebrow">Research</p>
                <h2 id="portrait-research">The Proper Ending Index</h2>
                <p>Three working papers on accountable decision routing, governing capacity, and workflow exit. Each record sets out the paper’s claims, methods, and limits.</p>
                <a class="button primary" href="/papers/">Explore the research <span aria-hidden="true">↗</span></a>
                <p class="portrait-note"><a href="/papers/#critical-review">Invitation to independent review</a></p>
                <p class="portrait-note"><a href="/papers/#japanese" lang="ja">日本語の研究案内</a></p>
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
            title="Takashi Sato (佐藤貴士) — Independent Researcher",
            description="Author record for Takashi Sato (佐藤貴士), an independent researcher in Sapporo. Current research concerns AI governance, accountable decision routing, governing capacity, and institutional exit.",
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
          <p class="eyebrow">Takashi Sato</p>
          <h1>{title}</h1>
          <div class="content">{content}</div>
        </main>
        """
    ).strip()
    return shell_page(
        head_html=head(
            title=f"{title} · Takashi Sato",
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
            title=f"{title} · Takashi Sato",
            description=detail,
            path=canonical,
            image="/assets/og/papers.jpg",
            robots="noindex,follow,noarchive",
        ),
        body=body,
        page="legacy",
    )
