# The Proper Ending Index

Static research archive for Takashi Sato's *Workflow-Centric AI Governance Trilogy*.

## Current research record

All three preserved papers are version 6.2, dated 23 August 2026.

| Part | Paper | SSRN | DOI |
|---|---|---:|---|
| I | *Workflow-Centric AI Governance: A Typed Gate Contract for Accountable Human-AI Decisions* | 5911063 | 10.2139/ssrn.5911063 |
| II | *Procedural Continuity and Governing-Capacity Loss in AI-Assisted Institutions: A Descriptive State Model with Pre-Abuse Collapse as a Provisional Etiological Subtype* | 5913703 | 10.2139/ssrn.5913703 |
| III | *From Governance Drift to Accountable Exit: Proper Ending and Authority Return in AI-Assisted Institutions* | 6066430 | 10.2139/ssrn.6066430 |

SSRN is the primary external research record. `pdf/` contains preserved v6.2 copies whose file sizes and SHA-256 digests are published in `research-index.json` and on each paper page.

## Architecture

- pre-rendered static HTML for GitHub Pages;
- one shared stylesheet and one progressive-enhancement script;
- self-hosted Newsreader, Inter, and Mea Culpa type families; no framework runtime, remote font request, client-side routing, account system, or third-party UI package;
- three optimized monochrome material surfaces supplied for the archive: grain, paper, and brushed metal;
- progressive fine-pointer interactions using Pointer Events, requestAnimationFrame, difference blending, magnetic controls, position-aware lighting, and View Transitions, with touch/keyboard/reduced-motion fallbacks;
- semantic HTML/CSS research diagrams that remain selectable, responsive, printable, and reduced-motion safe;
- stable author-entity JSON-LD, `CreativeWorkSeries`, `ScholarlyArticle`, and visible/structured breadcrumbs;
- Highwire citation metadata on each paper record while SSRN remains the primary external record;
- machine-readable orientation in `research-index.json` and `llms.txt`.

## Build and verify

```bash
python tools/build_site.py
python tools/generate_og.py
python tools/verify_v62.py
```

The build script has no dependencies. OG generation and PDF verification use the pinned packages in `tools/requirements.txt`. Repository QA regenerates the static pages, checks the committed output, validates identifiers and local links, verifies PDF byte counts and SHA-256 digests, and rejects legacy runtime assets.

## Claim discipline

This archive does not present the papers as legal advice, compliance certification, operational decision software, or field validation. Exhaustive checks are bounded to declared abstractions; synthetic results are not open-world performance; the shared official-record corpus supports traceability rather than frequency, prediction, or causal sufficiency.

Earlier ALTRION prototypes are superseded because they do not implement version 6.2. Their public URLs now return a clear retirement notice and are excluded from the sitemap.
