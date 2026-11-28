# Takashi Sato — Research & Writings

A static personal research and writing archive. The current collection, **The Proper Ending Index**, covers AI governance, workflow failure, governing-capacity loss, Proper Ending, and Authority Return.

The interface should expose structure, not decorate content.

## Publication architecture

The website identity and the research collection identity are separate. `PUBLISHED_COLLECTIONS` in `src/archive/model.py` lists only released collections by stable entity ID. The home CollectionPage points to those IDs; `/research-index.json`, `/feed.xml`, the paper routes and DOI records remain the established trilogy-specific contracts. Do not repurpose or renumber them when adding a collection. Add independently versioned records and appropriate publication types (research article, working paper, essay or other work) only when an actual work is released. No empty public categories or unearned subject expertise.

The general publication catalogue is generated at `/publications/` and `/publications.json` from released records in `src/archive/publications.py`. The indexed HTML route registry in `src/archive/routes.py` supplies sitemap, release verification, IndexNow and archive QA. It does not require a series, DOI, or version for an essay or research note. The QA suite exercises bilingual, standalone and optional-metadata records with synthetic fixtures; these are not publication claims.

## Research record

The current *Workflow-Centric AI Governance Trilogy* is v6.3 (revision date: 28 November 2026). SSRN is the primary external research record. `/pdf/v6.3/` contains byte-identical copies of the verified SSRN downloads. `/reproduction/v6.3/trilogy_v6.3_publication_6953eeb9.zip` preserves the source archive. Earlier v6.2 PDFs and citations remain at their original versioned paths.

| Part | Research function | SSRN | DOI |
|---|---|---:|---|
| I | Route the case | 5911063 | 10.2139/ssrn.5911063 |
| II | Diagnose the institution | 5913703 | 10.2139/ssrn.5913703 |
| III | End and return authority | 6066430 | 10.2139/ssrn.6066430 |

## Architecture

Authoring source is separated from generated runtime output:

```text
src/archive/        canonical research model + page renderers
src/styles/         base, research instruments, performance, identity and research motion
src/scripts/        progressive-enhancement modules
tools/build_site.py build orchestration
tools/build_assets.py deterministic CSS/JS compilation
tools/generate_og.py deterministic social-card generation
tools/verify_v63.py current archive contract verification
tools/verify_v62.py historical v6.2 verifier (use on the v6.2 checkout)
assets/             generated production CSS/JS, fonts, and OG cards
papers/             generated HTML paper records
pdf/v6.3/           current immutable preserved papers
pdf/v6.2/           prior immutable preserved papers
```

Production remains intentionally small: pre-rendered HTML, one shared stylesheet,
one progressive-enhancement script, and no inline style blocks. No framework
runtime, remote font request, client-side router, account system, or UI package.

## Build

```bash
python tools/build_site.py
python tools/generate_og.py
python tools/verify_v63.py
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

Publication, correction, withdrawal and recovery procedures are documented in [`docs/publication-lifecycle.md`](docs/publication-lifecycle.md).
