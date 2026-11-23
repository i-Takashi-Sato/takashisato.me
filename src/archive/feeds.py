"""Machine-readable archive indexes and canonical URL inventory."""

from __future__ import annotations

from .model import AUTHOR, PAPERS, SITE, UPDATED, VERSION, article_schema


def research_index() -> dict[str, object]:
    parts: list[dict[str, object]] = []
    for paper in PAPERS:
        record = article_schema(paper)
        record["position"] = paper["part"]
        record["additionalProperty"] = [
            {"@type": "PropertyValue", "name": "Research function", "value": paper["function"]},
            {"@type": "PropertyValue", "name": "Research question", "value": paper["question"]},
            {"@type": "PropertyValue", "name": "SSRN abstract ID", "value": paper["ssrn"]},
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


def sitemap() -> str:
    entries = [
        "/",
        "/papers/",
        "/papers/part1.html",
        "/papers/part2.html",
        "/papers/part3.html",
        "/about.html",
        "/colophon.html",
        "/privacy.html",
        "/security.html",
    ]
    # Only genuinely revised documents receive a newer sitemap lastmod.
    # Research version and PDF revision dates remain unchanged.
    changed_pages = {
        "/": "2026-11-24",
        "/papers/": "2026-11-24",
        "/papers/part1.html": "2026-11-24",
        "/papers/part2.html": "2026-11-24",
        "/papers/part3.html": "2026-11-24",
        "/about.html": "2026-11-24",
        "/colophon.html": "2026-11-23",
    }
    urls = "\n".join(
        f"  <url><loc>{SITE}{path}</loc><lastmod>{changed_pages.get(path, UPDATED)}</lastmod></url>"
        for path in entries
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n"
        "</urlset>\n"
    )
