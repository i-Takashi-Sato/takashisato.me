# Publication lifecycle

The author archive preserves released works and their provenance. A new site release is
not automatically a new manuscript version.

## Add a work

- Establish its title, language, publication date, type, canonical path and stable entity ID.
  Record a subtitle, series, DOI, revision, version and review status only where supported.
- Retain the original manuscript or source text and verify any external identifier before
  declaring it. Do not reuse a trilogy DOI or version for an independent work.
- Add an actual individual record and, where necessary, a renderer in the build process.
  Register the released work in `STANDALONE_PUBLICATIONS` in
  `src/archive/publications.py`. Register a collection in `PUBLISHED_COLLECTIONS`
  only when it exists. No empty topic pages, fixture records or unpublished claims.
- Give a Japanese-language work its own correct document language and metadata; the
  present mixed-language research guide does not constitute a complete translated site.
  Establish its citation and preservation contract before release.

The catalogue and public route registry already support independent records. A
standalone renderer and any new citation/export or version-preservation contract
must be implemented when a real work requires them. The trilogy feed and index
retain their established scope.

## Revise or correct

Distinguish editorial correction of an HTML record from a revision of the work itself.
For an editorial correction, update the affected public page date in the route registry;
preserve the original work version and bibliographic facts. For a manuscript revision,
preserve the superseded bytes and citation, add a versioned destination and explicit
revision record, then update only the current-record references that are intended to move.
Record substantive corrections with date, scope, rationale and affected version.
Do not overwrite preserved files, invent review status, or silently change evidential claims.

## Withdraw

If a work is withdrawn, preserve its stable record route with an accurate dated notice
and the reason that can appropriately be disclosed. Indicate the affected version and
any replacement. Retain preserved bytes where lawful and appropriate; if removal is
required, retain a non-sensitive tombstone and record the reason rather than creating
a broken URL. Implement explicit withdrawal status and its rendering before applying
this procedure to any real work; no existing work is marked withdrawn by this policy.

## Release verification

Build from the intended source, verify the archive and generated outputs, and require
Archive QA, Visual Smoke and Web Quality Gate on the exact merge head. Review screenshots
for visual changes. After the Pages deployment succeeds, require Live Release Verification
against the same release. A cache mismatch, incomplete check or successful build alone
does not establish live byte identity. Search-engine indexing is a separate observation.
Do not send search notifications until the canonical public routes serve the intended
release. Preserve the release commit and validation records.

## Recovery and preservation

Maintain an independent copy of the repository history and the original research
materials outside the hosting account. A Git mirror alone does not preserve external
SSRN records, DNS, registrar access or CDN settings. Preserve the public configuration
and documented recovery procedure separately from credentials and recovery secrets.
For an actual backup, verify the Git object inventory and manuscript digests, then test
a restore into an isolated checkout. Rebuild with the pinned dependencies and compare
the restored outputs before changing DNS or promoting a recovered release.

To reverse a defective site release, prefer a reviewed revert on main, not a force push
or deletion of published immutable assets. Preserve versioned citation routes and
content-addressed assets for older documents. Re-run the full release gates and
post-deployment checks on the recovery release. Domain renewal, account recovery,
off-host backup location and actual restore verification remain operator-controlled
tasks; this document does not claim that an independent backup has been created.
