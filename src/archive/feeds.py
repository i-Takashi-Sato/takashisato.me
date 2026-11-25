"""Machine-readable archive indexes and canonical URL inventory."""

from __future__ import annotations

from .model import AUTHOR, PAPERS, PAPER_REVISION_DATE, SITE, UPDATED, VERSION, article_schema, paper_url, ssrn_url


from .concepts import concept_schema
from .routes import public_pages


RESEARCH_PROVENANCE = {
    1: "Reported from the v6.2 independent reimplementation (verify_part1_contract_v62.py), not an edit of the v5.9 checker. Independent third-party reproduction is not established here.",
    2: "Descriptive model and rejectable propositions; empirical validation is not established.",
    3: "Formal verification and synthetic benchmark results are carried forward from frozen v5.9 computational artifacts; v6.2 claims no new execution or empirical validation.",
}


def research_index() -> dict[str, object]:
    parts: list[dict[str, object]] = []
    for paper in PAPERS:
        record = article_schema(paper)
        record["position"] = paper["part"]
        record["additionalProperty"] = [
            {"@type": "PropertyValue", "name": "Research function", "value": paper["function"]},
            {"@type": "PropertyValue", "name": "Research question", "value": paper["question"]},
            {"@type": "PropertyValue", "name": "SSRN abstract ID", "value": paper["ssrn"]},
            {"@type": "PropertyValue", "name": "Research provenance", "value": RESEARCH_PROVENANCE[paper["part"]]},
        ]
        parts.append(record)

    return {
        "@context": "https://schema.org",
        "@type": "CreativeWorkSeries",
        "@id": f"{SITE}/papers/#trilogy",
        "name": "Workflow-Centric AI Governance Trilogy",
        "alternateName": "The Proper Ending Index research trilogy",
        "url": f"{SITE}/papers/",
        "mainEntityOfPage": f"{SITE}/research-index.json",
        "description": "Independent research archive on workflow-centric AI governance, governing-capacity loss, Proper Ending, and Authority Return.",
        "dateModified": UPDATED,
        "version": VERSION,
        "inLanguage": "en-US",
        "isAccessibleForFree": True,
        "creator": AUTHOR,
        "hasPart": parts,
        "subjectOf": concept_schema(),
        "about": [
            "AI governance",
            "human oversight",
            "workflow governance",
            "governing capacity",
            "Proper Ending",
            "Authority Return",
        ],
        "additionalProperty": [
            {"@type": "PropertyValue", "name": "Status", "value": "Working papers"},
            {"@type": "PropertyValue", "name": "Current version", "value": VERSION},
            {
                "@type": "PropertyValue",
                "name": "Claim discipline",
                "value": "Formal and synthetic results are bounded to their declared abstractions; public-record coding supports traceability rather than field validation.",
            },
            {
                "@type": "PropertyValue",
                "name": "Legacy prototype status",
                "value": "Superseded; excluded from current research routes because the prototypes do not implement version 6.2.",
            },
        ],
    }


def atom_feed() -> str:
    """Syndicate scholarly revisions, never routine cosmetic changes."""
    from xml.sax.saxutils import escape

    def timestamp(day: str) -> str:
        # Source metadata has day precision, not an asserted publication time.
        return f"{day}T00:00:00Z"

    rows = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="en">',
        f'  <id>{SITE}/feed.xml</id>',
        '  <title>The Proper Ending Index — Research updates</title>',
        '  <subtitle>AI governance working papers by Takashi Sato</subtitle>',
        f'  <updated>{timestamp(PAPER_REVISION_DATE)}</updated>',
        f'  <link rel="self" type="application/atom+xml" href="{SITE}/feed.xml"/>',
        f'  <link rel="alternate" type="text/html" href="{SITE}/papers/"/>',
        '  <author>',
        '    <name>Takashi Sato</name>',
        f'    <uri>{SITE}/about.html</uri>',
        '  </author>',
    ]
    for paper in sorted(PAPERS, key=lambda item: item["posted"], reverse=True):
        title = escape(f"{paper['title']}: {paper['subtitle']}")
        description = escape(f"Working paper · Version {VERSION}. {paper['description']}")
        rows.extend([
            '  <entry>',
            f'    <id>https://doi.org/{paper["doi"]}</id>',
            f'    <title>{title}</title>',
            f'    <published>{timestamp(paper["posted"])}</published>',
            f'    <updated>{timestamp(PAPER_REVISION_DATE)}</updated>',
            f'    <link rel="alternate" type="text/html" href="{paper_url(paper)}"/>',
            f'    <link rel="related" href="{ssrn_url(paper)}"/>',
            f'    <summary type="text">{description}</summary>',
            '  </entry>',
        ])
    rows.append('</feed>')
    return "\n".join(rows) + "\n"


def sitemap() -> str:
    urls = "\n".join(
        f"  <url><loc>{SITE}{page.path}</loc><lastmod>{page.lastmod}</lastmod></url>"
        for page in public_pages()
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n"
        "</urlset>\n"
    )
