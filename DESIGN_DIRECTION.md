# The Proper Ending Index — Design Direction

## Position

The Proper Ending Index is Takashi Sato's independent AI governance research archive.
It is not a portfolio, consultancy funnel, SaaS product, compliance service, or
fictional control room.

The interface exists to clarify four things: what each paper claims; what supports the
claim; where the claim stops; and which versioned record should be cited.

The public site should feel less like a website with effects and more like a research
pavilion whose architecture has been derived from the research itself.

## Spatial grammar

One archive, three analytical states:

- **Part I — Gate / Architecture / Measurement.** Old gold, bronze, structural lines,
  explicit passage conditions, measured orthogonality, and a stable datum.
- **Part II — Capacity Loss / Entropy / Procedural Continuity.** Lead gray, mercury,
  ice blue, a stable procedural frame with weakening or displaced internal capacity,
  and no theatrical collapse.
- **Part III — Circuit Breaker / Authority Return / Proper Ending.** Black, oxidized
  red, copper, residual heat, containment, convergence, and motion that spends energy
  until it settles.

The three papers are connected but must not be represented as one degradation score or
universal lifecycle.

## Research-instrument rule

Part identity must survive without a color legend. A reader should be able to infer the
analytical state from geometry and behavior alone:

- Part I uses thresholds, datums, rulers, gates, orthogonal construction, and explicit
  passage points. Measurement geometry does not drift.
- Part II preserves the outer procedural frame while traces inside it separate, weaken,
  drift, or become discontinuous. The frame is the point: visible procedure survives.
- Part III uses containment rings, breaker gaps, dependency spines, convergence, and
  decreasing spatial and kinetic energy as authority is returned.

A visual element is justified only when it communicates route, state, evidence,
capacity, containment, authority, return, or closure. If removing an effect leaves the
research meaning unchanged, the effect is decoration and should usually be removed.

## Typography and material

Newsreader carries editorial display; Inter carries interface, data, and reading text;
Mea Culpa is deliberately scarce. Materiality comes from light, hairlines, measurement
fields, spacing, and color temperature—not wallpaper textures, glassmorphism, or glow.

Typography is architecture. Line length, line break, optical size, letter spacing,
vertical rhythm, numeric alignment, and the relationship between display and evidence
text are treated as structural decisions rather than cosmetic tuning.

## Interaction

The archive is complete before JavaScript runs. Enhancement may add orientation,
authority-ring pointer response, Typed Gate exploration, cross-document continuity,
and terminal settling in Part III. The interaction grammar is:

**route → state → contain → return → settle**

Interaction must preserve the semantics of each paper:

- Part I may respond through emphasis, but its measurement datum remains stable.
- Part II may move internal capacity traces while the procedural frame remains fixed.
- Part III contracts and quiets. It never expands into a reward animation or generic
  visualizer.

Proper Ending is expressed by decreasing interface energy near the terminal state.

## Advanced-technology covenant

Advanced browser features are welcome only when they improve research meaning,
continuity, legibility, or performance. Technical novelty is never a design argument by
itself.

- Cross-document View Transitions may carry a research instrument from the Papers map
  into its paper record. They must not turn navigation into a cinematic interstitial.
- Scroll-driven animation should be native-first where available, with a complete
  JavaScript or static fallback where it is not.
- Typed CSS custom properties may encode visual state so one declared state controls a
  coherent family of lines, traces, gaps, opacity, and contraction.
- Container queries should let an exhibit respond to the space it actually occupies,
  rather than accumulating viewport-specific exceptions.
- Pointer response belongs primarily to entrances and external research records. The
  reading room itself should become quieter as attention moves from navigation to text.
- No essential research content, link, citation, or state may depend on animation,
  pointer precision, JavaScript, a particular browser engine, or a high refresh rate.

WebGL, WebGPU, shaders, 3D scenes, smooth-scroll libraries, and other heavy techniques
remain excluded unless a future research mechanism cannot be expressed more precisely
with semantic HTML, CSS, SVG, and restrained progressive JavaScript.

## Code as artifact

The repository is part of the work. A reviewer who opens the source should encounter the
same discipline as a reader who opens the site.

- Canonical research metadata has one source of truth.
- Imports are explicit where practical; public types are named; preservation hashes and
  identifiers are not duplicated casually.
- Human-readable source files remain readable. Generated assets may be compact, but
  source code is not written as generated code.
- Comments explain **why a mechanism exists or what invariant it protects**, not what an
  obvious line of syntax does.
- New behavior belongs in the narrowest semantic module that owns it. Historical patch
  stacks should be consolidated rather than extended indefinitely.
- Generated HTML, CSS, JavaScript, metadata, PDFs, and OG records are deterministic and
  reconciled in CI.
- Performance budgets are constraints, not numbers to relax when a new effect is added.
- Reduced motion, forced colors, keyboard navigation, print, no-JavaScript, and narrow
  screens are first-class states of the artifact.

A clever implementation that makes the source harder to understand is a regression.

## Permanent exclusions

Do not restore:

- `序 / 破 / 急` or Jo / Ha / Kyu stage notation;
- liquid or membrane experiments;
- gratuitous WebGL or full-screen shader work;
- generic Part III visualizers without a research mechanism;
- Services, Samples, pricing, estimates, commissioned-work funnels, Sapporo Investment,
  or Operational Design commercial routes;
- keyword-stacked visible Japanese SEO copy.

## Record hierarchy

SSRN is the primary external research record. Local PDFs are immutable preserved copies.
Internal links are exhibition-room entrances; external research records may use `↗`.

## Review standard

A change is ready only when a reader, reviewer, crawler, keyboard user, and future
maintainer encounter the same current research record. Visual novelty never outranks
research fidelity, accessibility, performance, preservation, or claim discipline.

A release is not complete merely because CI passes. Major visual changes require human
review at narrow mobile, ordinary desktop, and wide desktop widths. The final question is
not “does the effect work?” but “does every detail make the research pavilion more exact?”
