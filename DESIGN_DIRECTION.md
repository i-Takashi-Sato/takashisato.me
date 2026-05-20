# takashisato.me Design Direction

## Core Concept

takashisato.me is a **luxury forensic accident archive** for AI governance systems.

It is not a generic portfolio, a product landing page, or a decorative AI website. It is a research archive that treats governance failure as something to be examined, preserved, and ended correctly.

Primary thesis:

> A cinematic accident archive for governance systems that kept operating after judgment had left.

Operational principles:

- PDF as evidence.
- Research as exhibit.
- Failure as trace.
- Stopping as interface.

## Stable Baseline

The current black archive state is the baseline. Do not sacrifice rendering stability for spectacle.

The site should remain:

- black
- quiet
- typographic
- evidence-led
- source-aware
- mobile-stable
- full-page-capture stable on iPhone

## Non-Negotiables

- Do not change the Home Hero copy.
- Do not place epigraphs on the Home page.
- Do not treat quotations as decorative inspiration.
- Do not add white paper surfaces or large light gradients.
- Do not touch `assets/site.css` unless explicitly required.
- Do not add heavy cinematic motion until the archive surfaces are stable.

Current Home Hero copy:

> A research index for systems that look governed after judgment has left.

This is the face of the site and should remain primary.

## Epigraph Policy

Epigraphs are textual evidence / source specimens, not quote design.

Implementation rule:

```html
<figure class="pei-epigraph">
  <blockquote>...</blockquote>
  <figcaption>Source: ...</figcaption>
</figure>
```

Display rule:

- original text first
- English translation as support when needed
- source line small but readable
- no forced uppercase on source text
- no Japanese decorative paraphrase

## Aesthetic References

The site may learn from:

- Obys: specimen logic, numbering, large typography
- REJOUICE: space, quiet confidence, pacing
- Unseen: project-as-exhibit treatment
- Immersive Garden: immersive page atmosphere

But it must not imitate advertising aesthetics. The subject is research, evidence, institutional failure, and controlled stopping.

## Primary Disciplines

Use these as the conceptual atmosphere:

1. Accident investigation / aviation safety
2. Forensics / evidence preservation
3. Control engineering / cybernetics
4. Medical diagnosis / pathology reading
5. Signal detection theory
6. Structural failure / fatigue fracture
7. Audit / internal control
8. Organizational theory / bureaucracy
9. Quality control / SPC
10. Philology / archival text study

Mystical, religious, cosmic, DNA, and string-theory references may only appear as faint secondary texture, not as the main design language.

## Page-Level Direction

### Home

Quiet entry. Keep the existing hero. No epigraphs, no PDF fragments, no religious or mystical symbolism.

### Part I

Theme: Architecture / Control / Trace.

Use control engineering, audit, and quality management language. Show Four-Gate Architecture, ADR JSON, Governance Grammar, structured friction, and auditable decision records as evidence.

Part I should be the cleanest and most engineered page.

### Part II

Theme: Decay / Accident / Fatigue.

Use accident investigation, structural fatigue, organizational theory, and bureaucracy. Represent failure as timeline, compression, template drift, and silent standardization.

Do not use loud glitch.

### Part III

Theme: Silence / Diagnosis / Halt.

Use medical diagnosis, forensics, signal detection, and control engineering. Represent GDI, Semantic Entropy Decay, Temporal Compression, Exhaustion of Dissent, Circuit Breaker, and Proper Ending as diagnostic surfaces.

Stopping should be shown through interface behavior, not a red reject button.

### About

Theme: Operator Record.

Treat the page as practice log / governance practice / operational record, not a generic profile.

## PDF Handling

Do not iframe PDFs.

PDFs should be decomposed into:

- Evidence Plate
- Specimen
- Archive ID
- Source Page
- Extracted Fragment
- Governance Trace

Use black archive surfaces, code fragments, tables, labels, and source metadata. Do not paste white PDF pages into the interface.

## Avoid

Avoid:

- purple AI gradients
- neon
- holograms
- robots
- 3D neural networks
- generic space backgrounds
- loud glitch
- liquid metal
- religious symbols as literal icons
- red REJECT stamps
- red stop switches
- typing effects
- shutter sounds
- scroll jank
- stock photography
- quote-site layouts

Failure in this archive should often appear as silence, compression, missing context, and procedural smoothness.

## Near-Term Implementation Order

1. Preserve black stable baseline.
2. Refine typography, spacing, epigraphs, and button rhythm.
3. Add Part I ADR JSON as a black Evidence Plate.
4. Add Part I Four-Gate Architecture as a controlled diagram.
5. Add Part II failure timeline.
6. Add Part III diagnostic log / GDI surface.
7. Only then consider motion or instrument-level interactions.
