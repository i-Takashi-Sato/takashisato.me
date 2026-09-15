# Repository Governance

## May change

Research revisions, new papers, verified identifiers, accessibility fixes, performance
work, and interactions that directly express the research model may change the archive.

## Must not return

Retired stage notation (`序 / 破 / 急`), liquid/membrane experiments, generic WebGL,
commercial service routes, mutable PDF aliases, keyword-stacked Japanese presentation
copy, or an ungrounded Part III visualizer.

## Release gate

Visual changes require Archive QA, Web Quality Gate, and Visual Smoke. Generated output
must be deterministic. A passing structural test is not evidence of visual quality; the
screenshot artifact is part of release review.

A build commit produced by GitHub Actions may synchronize generated assets, but it does
not substitute for release checks. After any bot-authored synchronization commit, a
user-authored repository commit must retrigger the three release gates so that the final
head being merged is the head that was actually tested.

## Proper Ending for the site itself

The archive is not improved by perpetual redesign. Once a release passes its research,
visual, accessibility, performance, and search contracts, it should be allowed to remain
still until new evidence or a new research mechanism justifies change.
