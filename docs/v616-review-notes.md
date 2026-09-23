# v6.16 Review Notes — Advanced Pavilion

## Intent

v6.16 is a refinement release for The Proper Ending Index. It does not change the v6.2 research record, SSRN primacy, preserved PDF hashes, or the archive's commercial exclusions.

The design goal is to make the site behave less like a styled research website and more like a research pavilion whose visual physics are derived from the papers themselves.

## Visual invariants

- Part I: measurement geometry remains fixed. Interaction may emphasize a gate state, but the datum does not drift.
- Part II: the procedural frame remains fixed while internal capacity traces separate and weaken.
- Part III: containment contracts, interface energy decreases, and the terminal state settles instead of expanding.
- Part identity must remain recognizable without relying on color alone.
- SSRN remains the primary external research record; preserved local PDFs remain secondary archival copies.

## Advanced browser features

All advanced behavior is progressive enhancement:

- cross-document View Transitions carry the archive brand, paper title, and research instrument between Papers and each paper room;
- typed CSS custom properties encode capacity drift and accountable closure;
- native scroll-driven animations replace main-thread motion where supported;
- container queries size the research-map instruments from their own available space;
- `:has()` reflects the Typed Gate probe's declared pressed state without duplicating presentation state in JavaScript;
- coalesced pointer events and requestAnimationFrame provide restrained authority-ring response on fine pointers.

No essential research text, citation, link, state, or action depends on these features.

## Code review standard

Review the repository as part of the artifact:

- source modules must remain readable and semantically owned;
- generated assets remain deterministic;
- public metadata remains single-source;
- accessibility, no-JavaScript, reduced-motion, forced-colors, print, and narrow-screen states are preserved;
- performance budgets are not relaxed to accommodate visual effects.

## Human visual review

Review at minimum:

- 320 / 390 / 430 px mobile;
- 768 / 1024 px intermediate;
- 1440 px ordinary desktop;
- 1920 px wide desktop.

Inspect Home, Papers, About, and Part I–III. Particular attention should be paid to title line breaks, paper apparatus alignment, research-map legibility, terminal Part III settling, footer contrast, and cross-document continuity.

The final question is not whether an effect works. It is whether the detail makes the research pavilion more exact.
