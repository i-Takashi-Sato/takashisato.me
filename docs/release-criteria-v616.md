# v6.16 Release Criteria

v6.16 may merge only when all of the following are true:

- Archive QA passes without relaxing existing research-record checks.
- Visual Smoke passes at 320, 390, 430, 768, 1024, 1440, and 1920 px.
- Reduced-motion and no-JavaScript states remain complete and legible.
- Part I datum remains fixed; Part II frame remains fixed while internal traces drift; Part III contracts rather than expands.
- Cross-document transition identities are unique and deterministic.
- Lighthouse release budgets remain at or above the current v6.15 contract.
- Generated CSS stays under the existing CSS budget and generated JavaScript stays under 20 KB.
- No source or generated output introduces the retired commercial layer or superseded visualizer language.
- Human review finds no illegible title break, clipped instrument, low-contrast terminal state, or mobile overflow.
- Main is not changed until the reviewed branch tree is the tree intended for production.
