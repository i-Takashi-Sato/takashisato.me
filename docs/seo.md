# Search and Entity Contract

SEO follows the research record; it does not add visible keyword copy that a reader would
not otherwise need.

## Entity graph

```text
Takashi Sato / 佐藤貴士
  → The Proper Ending Index
  → Workflow-Centric AI Governance Trilogy
  → Part I / Part II / Part III
  → DOI / SSRN / immutable preserved PDF
```

Person identity is anchored by ORCID, SSRN Author ID, Google Scholar, and the author page.
`CreativeWorkSeries` is the canonical trilogy entity. Each `ScholarlyArticle` points back
to that series and carries its own DOI, SSRN identifier, publication date, revision date,
pagination, and preserved-file metadata.

## Visible field classification

Home identifies itself as an **AI Governance Research Archive**. The phrase is an honest
classification, not a search-keyword block.

## Canonical surfaces

The indexed primary routes are Home, Papers, About, Parts I–III, Colophon, Privacy, and
Security. SSRN remains primary for paper publication records; `/pdf/v6.2/` is preserved
local access and is not the primary reading route.

## Japanese identity

`佐藤貴士` appears once in the visible home author introduction and once in the author
record, alongside the English name, and in the home and author document titles. The
same canonical Person identity links both records to the established scholarly profiles.
The archive remains English-first. A bounded Japanese reading guide on the existing Papers page
provides meaningful local-language orientation, with links to the three English records and their
claim boundaries. It is neither a translated paper nor an equivalent locale-specific page; no
hreflang pairing, duplicate identity page, or keyword list is introduced. Search ranking and title display
are not guaranteed by these fields.

## Scholarly update syndication

`/feed.xml` is an Atom 1.0 feed with stable DOI entry identifiers, canonical paper links,
primary SSRN record links and canonical revision dates. It is generated from the paper
model and discoverable on every HTML page. Day-precision research dates are serialized
at 00:00 UTC for Atom compatibility; this is not a known publication time. Cosmetic
site releases do not change the scholarly update date. No new paper or revised claim
is implied by adding the feed.

## Scholarly interoperability

Each paper exposes CSL-JSON alongside BibTeX and RIS, and typed links for the preserved PDF, citation metadata, ORCID and related DOI. The DOI resolves through SSRN rather than this independent archive, so it is expressed as `related`, not `cite-as`. These links follow selected Signposting conventions; they do not claim full FAIR profile conformance. No license is asserted without authorization. Google Scholar's same-subdirectory requirement for `citation_pdf_url` is not met by the immutable `/pdf/v6.2/` structure; no misleading tag or duplicate PDF was added.

References: https://signposting.org/FAIR/ ; https://github.com/citation-style-language/schema ; https://scholar.google.com/intl/en/scholar/inclusion.html

## Search versus training

Google's generative Search guidance does not require llms.txt or special AI markup. The archive retains its existing machine-readable orientation as a convenience, not a ranking claim. Cloudflare's observed managed policy distinguishes search access from training; do not expand training permissions to pursue search exposure. Google Scholar's PDF association remains unresolved without duplicating or relocating preserved originals. Actual search visibility and crawl access must be assessed independently of Lighthouse.
