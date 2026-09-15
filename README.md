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
