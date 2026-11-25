# Release operations and maintenance baseline

## Established release

The social-profile release was merged into main on 2026-11-26 (JST), commit
`60977bf5cd6437195f92039e9ae1cb418a11e847`. Its PR #198 passed
Archive QA, Visual Smoke and Web Quality Gate. The main deployment
(run 45715432895) and Live Release Verification (run 45715433185) succeeded.
The main Archive QA (45715433249) and Visual Smoke (45715433306) also succeeded.
The immutable v6.2 manuscripts and public research identity are preserved.
This record describes observed checks, not aesthetic perfection or complete
WCAG conformance.

## Scope-aware quality policy

Every release retains Archive QA (deterministic rebuild, bibliography, PDF and
asset integrity, local links, syntax and verification tests), HTML validation,
axe and Chromium baseline visual smoke. On main, live release verification
continues comparing public HTTPS responses to checked-out release bytes.

Full checks additionally include the existing Chromium stress suite, WebKit
and Firefox checks and resilience suites, and all 21 Lighthouse collections
(seven URLs, three runs per URL) with unchanged budgets. Full checks are
mandatory for structural HTML changes, new/deleted/renamed files, runtime or
asset changes, build or QA changes, unknown scope, missing comparison commits,
and manual dispatch. Both browser and Lighthouse workflows run a full weekly
audit at Sunday 18:23 UTC (Monday 03:23 JST; actual start may vary).

Editorial-only changes may omit the additional full checks only when a Git
tree comparison proves that all changed paths are known, modified regular
files, and each changed HTML document retains the same protected markup,
attributes and active content. Ordinary prose, selected descriptive metadata,
valid JSON-LD and an existing same-origin HTTPS destination are the limited
exceptions. Changes to approved editorial source modules must also change a
known generated output. New sections and links are structural changes and
therefore full. The classifier is conservative, not a proof of semantic or
visual equivalence. The baseline visual and accessibility checks still run.
External destination ownership and link meaning need editorial confirmation.

The comparison uses the event's actual base and the checked-out tree. Missing
history or parsing uncertainty forces full checks. Classification is visible in
each workflow log. The release workflows keep their names; a failed or
unfinished workflow is not a release approval.

## Finalization and maintenance

Use the checked main commit as the versioned source of truth. The existing
verified repository recovery workflow is the reproducible backup mechanism;
its bundle must be exported and retained separately before the seven-day
artifact expiry. No account credentials or DNS/CDN configuration are in that
bundle. A particular fresh recovery artifact is not implied by this document.

No routine redesign is required. Reopen design or engineering work only for a
documented defect, security or compatibility change, a new research work, or
a demonstrable improvement. Keep author identity disclosure within the
approved public scope. Review search visibility and citations separately from
the site quality gates. New scholarly work must retain its own citation and
version history.

## Release acceptance

Confirm the exact PR head, required workflow results, the merge result and the
live verification of main. Record the commit and workflow links. Inspect
representative desktop/mobile screenshots for material visual changes.
Automated tests alone do not establish aesthetic quality, native-device
compatibility, screen-reader usability, or search rankings.
