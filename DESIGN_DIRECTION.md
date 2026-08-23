# The Proper Ending Index — Design Direction

## Position

The Proper Ending Index is Takashi Sato's independent research archive for the
*Workflow-Centric AI Governance Trilogy*. It is not a portfolio, consultancy
funnel, product landing page, compliance service, or fictional control room.

The interface exists to make four things unusually clear:

1. what each paper claims;
2. what evidence or executable check supports that claim;
3. where the claim stops; and
4. which versioned record should be cited.

Research fidelity outranks any inherited visual motif. Aesthetic references may
inform craft, but they must never determine the theory, terminology, hierarchy,
or apparent strength of the evidence.

## Canonical Research Structure

The current public record is version 6.2, dated 23 August 2026.

- **Part I — Route the case.** A typed, two-stage state-and-authority contract
  for consequential human–AI decisions.
- **Part II — Diagnose the institution.** A descriptive model of procedural
  continuity and governing-capacity loss; PMGCL is the primary construct and
  PAC is a provisional etiological subtype.
- **Part III — End and return authority.** A dependency-constrained Proper
  Ending and Authority Return protocol; indicators route investigation but do
  not authorize containment or retirement.

The trilogy is a connected sequence across different analytical scales, not a
single degradation score, universal lifecycle, or commercial methodology.

## Visual System

The site is one archive with one twelve-column grid, an editorial serif paired
with a neutral screen grotesk, a scarce formal script, and one signal color. It should combine the
scale confidence of a cultural studio with the restraint and precision of a
serious research record.

- Use a near-black field, gray-white type, full-width hairlines, and one
  electric-ultramarine signal. Black must have enough tonal depth to separate structure
  without card shadows or gloss.
- Self-host Newsreader for editorial display, Inter for interface, data, and
  reading text, and Mea Culpa only for the author signature, one thesis accent,
  the footer wordmark, and pointer labels. Keep all at their natural proportions; hierarchy comes from optical
  size, weight, space, and composition rather than artificial compression.
- Use the public-domain Aoyagi Kouzan brush form only for the three stage marks
  `序 / 破 / 急`. It is a symbolic background layer, never reading text, evidence,
  navigation copy, or an accessibility dependency.
- Use the supplied grain, paper, and brushed-metal images as distinct material
  roles. Grain is an optical film, paper belongs to research surfaces, and
  metal marks records and boundaries. Never stack them as decoration.
- Let editorial display type establish the spatial rhythm, then return quickly
  to measured reading widths and explicit evidence boundaries.
- Distinguish the three papers through hierarchy, formal structure, and the
  `序 / 破 / 急` stage notation—not three decorative palettes or unrelated art references.
- Build diagrams from semantic HTML and CSS so their text remains selectable,
  responsive, printable, and available without JavaScript.

### Jo / Ha / Kyu stage notation

The former decorative Roman numerals are replaced by Japanese stage marks:

- **Part I — 序.** Upright, spacious, quiet, and measured. Motion introduces and
  aligns; it should feel architectural rather than theatrical.
- **Part II — 破.** Slightly displaced and optically less stable. Motion may split,
  lag, or decouple, but must remain legible and controlled.
- **Part III — 急.** Tighter and more convergent. Motion moves toward closure,
  authority return, and rest rather than toward spectacle.

The marks sit behind the hero as low-opacity ultramarine ink. They may react to
fine-pointer proximity and scroll by only a few pixels. They never compete with
the paper title, never become a button, and disappear from print, forced-colors,
and reduced-motion compositions where needed.

Part III may carry the greatest visual gravity, but it must not become a dark
microsite detached from the archive. Its motion language is convergence:
routes settle, obligations acquire owners, and the interface comes to rest.

## Content Hierarchy

Every paper record should make the following sequence easy to scan:

1. full title, author, version, date, pages, and SSRN identifier;
2. research question and plain-language contribution;
3. formal structure or diagnostic model;
4. reported verification or traceability result;
5. explicit measurement and claim boundary; and
6. SSRN, DOI, preserved PDF, file size, and SHA-256.

SSRN is the primary external research record. Local PDFs are preserved copies,
not a competing publication source. Earlier ALTRION visualizers remain at their
old URLs only as `noindex` retirement notices and must not be linked as current
research instruments.

The author record is English-primary. Its complete visible Japanese identity is
exactly `佐藤貴士　札幌`; structured data and metadata carry the wider entity
graph. Do not restore a second, keyword-stacked Japanese biography.

Do not introduce decorative quotations, invented case files, fictional JSON,
award claims, unverified performance claims, or language that makes a bounded
finite check sound like field validation. Do not add services, samples,
investment, lead-generation, or contact-conversion flows.

## Interaction

The archive is complete before JavaScript runs. Enhancement may add orientation,
physical response, and pacing:

- restrained opacity-and-translation reveal transitions;
- a reading-progress line and section-aware table of contents;
- current-page and keyboard focus states;
- a fine-pointer-only difference cursor with short calligraphic labels;
- velocity-aware cursor response without cursor trails;
- proximity-aware magnetic controls and position-aware surface light;
- relational hover in which associated metadata, stage marks, and neighboring
  controls respond as one system;
- progressive scroll-linked material drift and cross-document view transitions;
- a footer settling state in which motion and visual energy reduce as the page
  reaches `Proper Ending`; and
- optional first-party analytics that fails closed.

The interaction grammar is **enter → approach → engage → release → settle**.
Effects should share easing and timing families rather than behaving like an
assortment of unrelated demos.

No research content may depend on these enhancements, canvas, WebGL, pointer
input, audio, autoplay, or a client-side router. Touch and keyboard retain every
action. Respect reduced-motion and forced-colors preferences. Motion should
confirm structure, never simulate scientific authority.

### Overuse boundary

Do not add an effect merely because the platform supports it. Specifically:

- no scroll-jacking, smooth-scroll replacement, cursor trails, particle fields,
  autoplay media, gratuitous WebGL, or continuous full-screen shader work;
- no hover transformation that moves a target far enough to impede acquisition;
- no more than one dominant response per interaction plus one subtle related
  response in the surrounding context;
- no effect that hides SSRN, DOI, preserved PDF, navigation, focus, or claim
  boundaries;
- no motion that survives `prefers-reduced-motion`; and
- no decorative dependency that blocks first paint or reading.

The desired impression is not “many effects.” It is that the archive behaves as
one governed physical system.

## Technical Baseline

- Pre-rendered static HTML suitable for GitHub Pages.
- One shared stylesheet and small dependency-free enhancement scripts.
- Newsreader, Inter, and Mea Culpa remain self-hosted. The public-domain Aoyagi
  webfont is restricted to three decorative stage glyphs and is optional at
  runtime; if it is unavailable, a local Japanese Mincho fallback preserves the
  layout without changing research content.
- No framework runtime, third-party UI kit, tracking pixel, or build-time
  network dependency.
- Stable URLs, canonical links, semantic landmarks, visible breadcrumbs,
  keyboard focus, skip links, adequate targets, and print styles.
- Stable Person, CreativeWorkSeries, ScholarlyArticle, BreadcrumbList, and
  Highwire citation metadata.
- Deterministic generation of HTML and social cards.
- CI verification of generated output, local links, identifiers, PDF byte
  counts, page counts, language metadata, and SHA-256 digests.
- Fine-pointer effects should stay transform/opacity-first, avoid forced layout
  loops, and preserve responsive input performance; touch receives a composed
  static state rather than an imitation of desktop hover.

## Review Standard

A change is ready only when it improves the archive without weakening claim
discipline, identity consistency, accessibility, mobile reading, print output,
or long-term preservation. The final test is not whether the page looks
spectacular in one screenshot; it is whether a reader, reviewer, crawler, and
future maintainer all encounter the same current research record.