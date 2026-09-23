# The Proper Ending Index — v7.0 Design Direction

## Position

The Proper Ending Index is Takashi Sato's independent AI governance research archive and digital pavilion. It is not a portfolio, consultancy funnel, SaaS product, compliance service, or visual-effects demo.

The archive has three jobs: make the research claims legible, make their boundaries explicit, and make the external record citable. Design is successful only when the architecture strengthens those jobs.

v7.0 is a zero-base visual reset. It keeps the current research record, URLs, metadata, preservation policy, and semantic interaction model, but rethinks the exhibition surface from first principles.

## Core proposition

The site should feel less like a dark website with sections and more like a sequence of rooms cut from one institution.

The visual system is built from five primitives:

1. **Datum** — the stable reference against which a state is read.
2. **Threshold** — the point at which passage is allowed, delayed, blocked, or redirected.
3. **Trace** — evidence that procedure or capacity is moving, drifting, weakening, or closing.
4. **Containment** — the deliberate reduction of available space and energy.
5. **Record** — the fixed external or preserved research object.

No effect is allowed to exist only because it looks advanced.

## Spatial grammar

### Part I — Gate / Architecture / Measurement

Stable datum, orthogonal construction, old gold, bronze, structural thresholds, explicit passage conditions. Measurement geometry does not drift. Motion may clarify state, never destabilize the reference.

### Part II — Procedural Continuity / Capacity Loss / Entropy

A stable outer frame with weakening internal alignment. Lead gray, mercury, ice blue, interrupted traces, delay, slippage, and cold institutional fatigue. The point is not theatrical collapse; the point is that visible procedure can remain while governing capacity degrades.

### Part III — Proper Ending / Circuit Breaker / Authority Return

Black stopping space, oxide red, copper, residual heat, containment rings, breaker gaps, convergence, authority transfer, and decreasing interface energy. Motion closes, tightens, and settles. It never opens into a reward animation or generic visualizer.

Part identity must survive without a color legend. Geometry and behavior carry the meaning before palette does.

## Exhibition architecture

### Home

The first viewport is an entrance hall, not a summary dashboard. One proposition dominates the room. Secondary information is pushed to the edge and given documentary weight rather than product-UI prominence.

The trilogy is presented as three thresholds, not three cards.

### Papers

The catalogue is a plan drawing of three mechanisms. The research map is the primary spatial object. Paper records remain editorial and evidence-heavy; SSRN is visually recognized as the primary external research record.

### Paper rooms

The hero is the room threshold. The table of contents is a measured orientation rail, not a boxed navigation widget. Long-form reading becomes quieter than navigation. Part-specific apparatuses define the environment before motion is applied.

### Author

The author page is a dossier and public research record. Identity, research position, and external evidence are separate layers. ORCID, SSRN, and Google Scholar are records, not social links.

### Footer

The footer is a terminal field. It should feel like an ending, not a second navigation homepage. In Part III the site spends visual energy until the final archive threshold is visibly settled.

## Typography

Typography is treated as architecture.

- Newsreader carries editorial display and conceptual emphasis.
- Inter carries interface, data, metadata, and reading text.
- Mea Culpa remains deliberately scarce and must never become generic luxury decoration.
- Display lines are allowed to be very large when the surrounding space earns them.
- Numeric records use tabular figures.
- Long-form reading measure remains intentionally conservative.
- Wide screens receive more silence, not simply larger components.

## Material

Materiality comes from darkness, warm/cold light temperature, hairlines, measured fields, residual glow from state, and negative space.

Do not use glassmorphism, blurred product panels, generic gradients, ornamental particles, fake film grain, or decorative 3D scenes. Texture is generated only where it reinforces the archive as a physical record.

## Interaction

The archive is complete before JavaScript runs. Progressive enhancement may add orientation, pointer response, Typed Gate exploration, cross-document continuity, scroll-driven state change, and terminal settling.

Interaction grammar:

**route → state → contain → return → settle**

The strongest pointer response belongs at entrances and external research records. Reading rooms become quieter as attention moves from navigation to text.

Native platform features are preferred when they express the research more precisely: View Transitions, scroll-driven animation, typed custom properties, container queries, reduced-motion states, and semantic CSS selectors.

WebGL, WebGPU, Three.js, shaders, smooth-scroll libraries, and heavy animation frameworks remain excluded unless a future research mechanism genuinely requires them.

## Code as artifact

The repository is part of the pavilion.

- Research facts and identifiers have one canonical source of truth.
- Source modules own one semantic responsibility.
- Generated assets are deterministic.
- CSS comments explain meaning and invariants, not obvious syntax.
- New design work should consolidate historical patches rather than stack another visual layer on top.
- Reduced motion, forced colors, keyboard use, mobile, wide desktop, and no-JavaScript are first-class states.
- Performance budgets are constraints.
- A clever implementation that makes the source harder to understand is a regression.

## Permanent exclusions

Do not restore:

- 序 / 破 / 急 or Jo / Ha / Kyu staging;
- liquid or membrane effects;
- generic particle systems;
- decorative WebGL or full-screen shaders;
- a generic Part III visualizer without a new Proper Ending mechanism;
- Services, Samples, pricing, estimates, commissioned-work funnels, Sapporo Investment, or Operational Design routes;
- keyword-stacked visible Japanese SEO copy.

## Record hierarchy

SSRN remains the primary external research record. Local PDFs remain immutable preserved copies. Internal links are exhibition-room entrances. External research records may use `↗` where the change of context should be visible.

## Release standard

A visual release is complete only when the research record, visual hierarchy, browser behavior, accessibility, preservation, and code architecture all agree.

The final review question is not “does this look expensive?” It is:

**Does every detail make the research pavilion more exact, more memorable, and more inevitable?**
