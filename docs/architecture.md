# Architecture

The archive is a static publishing system, not a web application.

## Source and output

`src/` is the authoring source. Root HTML and `assets/site.css`, `assets/site.js`, and
`assets/critical.css` are deterministic build output committed for GitHub Pages.

Research metadata has one canonical source: `src/archive/model.py`. Paper titles, DOI,
SSRN identifiers, publication dates, page counts, preserved-file sizes, and SHA-256
hashes must not be independently re-entered in renderers or QA.

Source styling is separated by responsibility: `base.css` holds the durable document
system, `pavilion.css` holds the archive-wide visual grammar, `instruments.css` turns the
research semantics into part-specific spatial and interaction mechanisms, `performance.css`
keeps first-viewport research content paintable without JavaScript reveal delay, and
`critical.css` supplies the minimal inline first-paint contract. Production still ships
one shared stylesheet plus the critical inline layer. The shared stylesheet participates
in the initial render directly; it is not held behind a JavaScript or `window.load`
style swap, so the archive does not trade a fast first paint for a delayed LCP restyle.

## Dependency direction

```text
model → layout → page renderers → build orchestration
  └──────→ feeds / schema / preservation metadata
source CSS/JS → build_assets.py → runtime CSS/JS
model + generated output → verify_v62.py
```

Renderers may depend on the model. The model must never depend on HTML output.
Verification imports the model but independently inspects generated artifacts.

## Runtime contract

- pre-rendered semantic HTML;
- one shared CSS file active during initial render;
- one progressive-enhancement JS file;
- inline critical first-viewport CSS;
- self-hosted fonts;
- no framework runtime or client-side router;
- no research action dependent on JavaScript.

## Naming

Code names should describe research semantics (`route`, `capacity`, `authority`,
`containment`, `ending`) rather than visual tricks (`magic`, `wow`, `liquid`).

## Generated-file discipline

Generated files are committed only when `python tools/build_site.py` and
`python tools/generate_og.py` have been run. CI rebuilds and rejects uncommitted drift.
Python bytecode, local screenshots, Lighthouse working directories, and package caches
are never repository content.
