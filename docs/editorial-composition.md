# Editorial composition — candidate

A durable, discipline-neutral research publication, not a marketing landing page. Preserve the platinum paper reading field, black author chamber and authentic signature, three research instruments, stable publication and citation routes, and explicit evidentiary boundaries.

## Evidence and design decisions
- v6.3 release passed all 71 byte-delivery checks. Prior Lighthouse measurements: seven pages, three runs each; Author LCP about 3.00 s. LCP was the portrait chamber background, already preloaded and only about 2.6 KB. Do not assume image compression is the solution.
- The mobile audit showed missing Japanese glyphs on a machine without CJK fonts. The current stack cannot ensure legible Japanese.
- Move the existing Japanese guide link to the first reading decision on the index, without duplicate navigation. Preserve paper hierarchy and content.
- Use two pinned OFL Noto Japanese subsets, small UI and reading face, with no runtime third-party requests. Retain strict line breaking, phrase-preserving headings, and progressive enhancement for inter-script spacing.
- Clarify the Part II Japanese link terminology and the historically stranded retirement-authorized states. No manuscript or citation changes.

## Acceptance
Compare actual rendered screenshots, including 320/390/768/1440 widths, to previous main. Verify font cmap coverage, license, byte budgets, actual loaded faces, all full-scope CI and live byte delivery; maintain 100 KB CSS and 20 KB JS. Reject new layout or performance regressions. The Author LCP experiment is separate, not a justification for removing the signed material or relaxing limits. Content-addressed OG cards remain a separate future improvement. No claim of universal aesthetic superiority or real-device certification.

## References
- https://www.w3.org/TR/jlreq/
- https://www.w3.org/TR/WCAG22/
- https://developer.mozilla.org/en-US/docs/Web/CSS/text-autospace
- https://web.dev/articles/optimize-lcp
- https://mitpress.mit.edu/celebrating-muriel-coopers-legacy-on-world-design-day/
