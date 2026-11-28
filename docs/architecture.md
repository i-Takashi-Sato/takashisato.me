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
model + generated output → verify_v63.py
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
`python tools/generate_og.py` have been run. CI rebuilds and rejects both modified tracked output and untracked generated files. The active CSS and JavaScript directories must match their declared build inventories; retired experiments remain recoverable in Git history, not in the active source.
Python bytecode, local screenshots, Lighthouse working directories, and package caches
are never repository content.

## Performance measurement

For full-scope changes, manual runs and the weekly audit, Lighthouse runs three times per URL. The least favorable measurement must satisfy the existing hard thresholds; LCP above 2500 ms remains a warning. The unsuccessful font-preload experiment was not adopted.

The Papers index contains a stable, semantic concept register. Citation-copy controls are created only when the browser exposes the Clipboard API, and errors preserve manual selection. No runtime dependency, remote request, new stylesheet, or storage is introduced.

## Content-addressed runtime delivery

Current HTML references the SHA-256-named CSS and JS bundles derived from the exact deterministic build bytes. The legacy `assets/site.css` and `assets/site.js` paths remain available for older links and are still byte-verified. Historical fingerprinted bundles are retained so cached documents cannot lose their referenced resources; the inventory validates their names, hashes and size limits. The current page still loads only one stylesheet and one script. No stylesheet or script content was changed in the initial migration.

The concept register's secondary preserved-PDF links now point to exact starting pages in the immutable current v6.3 manuscripts. Each page range is checked for bounds and its source heading is located in the preserved PDF. This verifies locators, not external construct validity. The SSRN reading route remains primary.

## Reading resilience

The separate Chromium stress suite checks landscape, 320px reflow, doubled root font size, forced colors, font/script failure and print media. It records diagnostic geometry and screenshots on failure. These are bounded laboratory probes, not native zoom, a screen-reader test, physical-device certification or full WCAG conformance.

Reading-resilience follow-up: preserve the 200% root-font stress probe and original viewport/reading-element limits. Allow narrow single-column grid tracks to shrink to zero intrinsic minimum, wrap long headings and series titles, and let masthead flex items wrap instead of overlapping when text expands. The header brand/navigation overlap and header target boundaries are additional checks; all seven large-text screenshots are retained for review even when passing. These are stress probes, not native browser zoom or complete WCAG conformance evidence.

### Cross-engine reading resilience

The Chromium seven-mode reading-resilience suite covers all seven core reading pages (49 page/mode combinations). Firefox and WebKit additionally run the same five comparable screen-reading modes — landscape, 320 px reflow, 200% root text stress, font request failure, and JavaScript disabled — across all seven core reading pages (70 additional combinations). Both engines produce their own JSON report and enlarged-text screenshots. Print and forced-colors probes remain in the Chromium suite. These are synthetic browser stress tests, not native zoom, assistive-technology, or physical-device certification.

### Editorial reading entry

Each paper cover retains the primary SSRN research record and adds a native in-page abstract link before the preserved PDF and DOI. The named table of contents is a navigation landmark. Wide paper layouts reduce the empty space between cover and reading field; mobile spacing remains unchanged. No claims, original documents, or citations are altered. The reading entry is tested at three widths with and without JavaScript.

## Discipline-neutral publication catalogue

The individual author archive has a separate catalogue at `/publications/` and `/publications.json`. The adapter in `src/archive/publications.py` derives the current three records from the immutable trilogy metadata. Future released works may have independent dates, languages, types, optional series, optional DOI, optional versions and explicitly known review status. No topic is reserved in advance. A record must point to a real published destination; new individual record renderers and preservation/citation rules must be added when the corresponding work exists. The trilogy-specific index and Atom feed remain unchanged. Synthetic bilingual expansion probes are executed only in tests, not in generated public records.

## Canonical route registry

The indexed HTML route inventory, editorial page dates and output paths are owned by `src/archive/routes.py`. The sitemap, deployed-byte audit, IndexNow allowlist and HTML archive QA consume the same registry. QA independently parses the generated sitemap and each document's canonical link. Standalone published works enter via `STANDALONE_PUBLICATIONS` in the catalogue model and must have real rendered destinations; the fixtures prove route propagation and reject collisions with existing pages. No new public route is fabricated. Binary preservation and retired notices remain separate contracts.

## Publication title hierarchy

The catalogue model stores main title and optional subtitle independently and derives the complete citation title through `full_title`. HTML distinguishes the subtitle visually without changing the accessible full title. The existing JSON title and scholarly entity names retain the complete title; no title parsing or new claims. Optional subtitles are not required for standalone works.
