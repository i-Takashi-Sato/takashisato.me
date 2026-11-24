# Architecture

The archive is a static publishing system, not a web application.

## Source and output

`src/` is the authoring source. Root HTML and `assets/site.css` and `assets/site.js`
are deterministic build output committed for GitHub Pages.

Research metadata has one canonical source: `src/archive/model.py`. Paper titles, DOI,
SSRN identifiers, publication dates, page counts, preserved-file sizes, and SHA-256
hashes must not be independently re-entered in renderers or QA.

Source styling is compiled in the declared order in `tools/build_assets.py`: `base.css`,
`instruments.css`, `performance.css`, `identity-2026.css`, and `research-motion-2026.css`.
Production ships one shared stylesheet without inline style blocks. The shared stylesheet participates
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
- no inline style blocks;
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

## Performance measurement

Lighthouse runs three times per URL. The least favorable measurement must satisfy the existing hard thresholds; LCP above 2500 ms remains a warning. The unsuccessful font-preload experiment was not adopted.

The Papers index contains a stable, semantic concept register. Citation-copy controls are created only when the browser exposes the Clipboard API, and errors preserve manual selection. No runtime dependency, remote request, new stylesheet, or storage is introduced.

## Content-addressed runtime delivery

Current HTML references the SHA-256-named CSS and JS bundles derived from the exact deterministic build bytes. The legacy `assets/site.css` and `assets/site.js` paths remain available for older links and are still byte-verified. Historical fingerprinted bundles are retained so cached documents cannot lose their referenced resources; the inventory validates their names, hashes and size limits. The current page still loads only one stylesheet and one script. No stylesheet or script content was changed in the initial migration.

The concept register's secondary preserved-PDF links now point to exact starting pages in the immutable v6.2 manuscripts. Each page range is checked for bounds and its source heading is located in the preserved PDF. This verifies locators, not external construct validity. The SSRN reading route remains primary.
