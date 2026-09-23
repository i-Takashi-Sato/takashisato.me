"""Canonical research metadata for The Proper Ending Index.

This module is the single source of truth for author identity, paper records,
identifiers, preservation hashes, publication dates, and the series entity.
Renderers and QA import from here rather than maintaining parallel copies.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final, TypedDict

ROOT: Final = Path(__file__).resolve().parents[2]


class Paper(TypedDict):
    part: int
    roman: str
    tone: str
    slug: str
    title: str
    subtitle: str
    description: str
    ssrn: str
    doi: str
    posted: str
    pages: int
    bytes: int
    sha256: str
    function: str
    question: str
    state: str


SITE: Final = "https://takashisato.me"
AUTHOR_ID: Final = f"{SITE}/about.html#takashi-sato"
SERIES_ID: Final = f"{SITE}/papers/#trilogy"
SCHOLAR_URL: Final = "https://scholar.google.com/citations?user=tN4zV68AAAAJ"

UPDATED: Final = "2026-09-23"
PAPER_REVISION_DATE: Final = "2026-08-23"
VERSION: Final = "6.2"
ASSET_VERSION: Final = "6.18.0"

GOOGLE_SITE_VERIFICATION: Final = "ESXaqBbWmxcZWPt2W_eI3ROS20FTy-KOziE5jfw0OSM"

AUTHOR: dict[str, object] = {
    "@type": "Person",
    "@id": AUTHOR_ID,
    "name": "Takashi Sato",
    "givenName": "Takashi",
    "familyName": "Sato",
    "alternateName": ["佐藤貴士", "佐藤 貴士", "Sato Takashi"],
    "jobTitle": "Independent Researcher",
    "url": f"{SITE}/about.html",
    "workLocation": {
        "@type": "Place",
        "name": "Sapporo, Hokkaido, Japan",
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "Sapporo",
            "addressRegion": "Hokkaido",
            "addressCountry": "JP",
        },
    },
    "identifier": [
        {"@type": "PropertyValue", "propertyID": "ORCID", "value": "0009-0003-1584-6965"},
        {"@type": "PropertyValue", "propertyID": "SSRN Author ID", "value": "9540672"},
    ],
    "sameAs": [
        "https://orcid.org/0009-0003-1584-6965",
        "https://papers.ssrn.com/Sol3/Cf_Dev/AbsByAuth.cfm?per_id=9540672",
        SCHOLAR_URL,
    ],
    "knowsAbout": [
        "AI governance",
        "human oversight",
        "workflow governance",
        "governing capacity",
        "Procedurally Masked Governing-Capacity Loss",
        "accountable exit",
        "Proper Ending",
        "Authority Return",
    ],
}

PAPERS: list[Paper] = [
    {
        "part": 1,
        "roman": "I",
        "tone": "part-1",
        "slug": "part1",
        "title": "Workflow-Centric AI Governance",
        "subtitle": "A Typed Gate Contract for Accountable Human-AI Decisions",
        "description": "A falsifiable, two-stage state-and-authority grammar for routing consequential human-AI decisions without turning missing evidence, unavailable capacity, or preliminary machine states into silent approval or denial.",
        "ssrn": "5911063",
        "doi": "10.2139/ssrn.5911063",
        "posted": "2026-01-09",
        "pages": 18,
        "bytes": 514075,
        "sha256": "edf19f110f6b0302765e29d2dfa20ddb2cbea299ea93b9c30a6a98411f73c2e8",
        "function": "Route the case",
        "question": "What may happen next?",
        "state": "Typed case contract",
    },
    {
        "part": 2,
        "roman": "II",
        "tone": "part-2",
        "slug": "part2",
        "title": "Procedural Continuity and Governing-Capacity Loss in AI-Assisted Institutions",
        "subtitle": "A Descriptive State Model with Pre-Abuse Collapse as a Provisional Etiological Subtype",
        "description": "A descriptive state model for institutions whose visible procedure remains intact while independent judgment, practical governing capacity, and a predeclared protected function materially deteriorate.",
        "ssrn": "5913703",
        "doi": "10.2139/ssrn.5913703",
        "posted": "2026-01-12",
        "pages": 20,
        "bytes": 562947,
        "sha256": "6cb7a21940caa3c62a20820f8156d8d684317ad8db3a0be8c4ceb8b85d1d5e88",
        "function": "Diagnose the institution",
        "question": "Can it still govern?",
        "state": "Descriptive state model",
    },
    {
        "part": 3,
        "roman": "III",
        "tone": "part-3",
        "slug": "part3",
        "title": "From Governance Drift to Accountable Exit",
        "subtitle": "Proper Ending and Authority Return in AI-Assisted Institutions",
        "description": "A dependency-constrained protocol for containing and retiring AI-assisted workflows while preserving service, evidence, remedy, accountable ownership, and the practical capacity to decide.",
        "ssrn": "6066430",
        "doi": "10.2139/ssrn.6066430",
        "posted": "2026-02-10",
        "pages": 39,
        "bytes": 1032918,
        "sha256": "7cda8695056f7268d4ef9ffb794ac29022e478ff087b646c339f800b9fe1ef72",
        "function": "End and return authority",
        "question": "How does it end accountably?",
        "state": "Exit and authority protocol",
    },
]


def paper_url(paper: Paper) -> str:
    return f"{SITE}/papers/{paper['slug']}.html"


def ssrn_url(paper: Paper) -> str:
    return f"https://papers.ssrn.com/sol3/papers.cfm?abstract_id={paper['ssrn']}"


def article_schema(paper: Paper) -> dict[str, object]:
    return {
        "@type": "ScholarlyArticle",
        "@id": f"{paper_url(paper)}#article",
        "headline": f"{paper['title']}: {paper['subtitle']}",
        "name": f"{paper['title']}: {paper['subtitle']}",
        "description": paper["description"],
        "abstract": paper["description"],
        "author": {"@id": AUTHOR_ID},
        "datePublished": paper["posted"],
        "dateModified": PAPER_REVISION_DATE,
        "version": VERSION,
        "inLanguage": "en-US",
        "isAccessibleForFree": True,
        "pageStart": 1,
        "pageEnd": paper["pages"],
        "pagination": f"1-{paper['pages']}",
        "isPartOf": {"@id": SERIES_ID},
        "url": paper_url(paper),
        "mainEntityOfPage": paper_url(paper),
        "image": f"{SITE}/assets/og/{paper['slug']}.jpg",
        "sameAs": [ssrn_url(paper), f"https://doi.org/{paper['doi']}"],
        "identifier": [
            {"@type": "PropertyValue", "propertyID": "DOI", "value": paper["doi"]},
            {"@type": "PropertyValue", "propertyID": "SSRN", "value": paper["ssrn"]},
        ],
        "encoding": {
            "@type": "MediaObject",
            "contentUrl": f"{SITE}/pdf/v{VERSION}/{paper['slug']}.pdf",
            "encodingFormat": "application/pdf",
            "contentSize": f"{paper['bytes']} bytes",
            "sha256": paper["sha256"],
            "uploadDate": PAPER_REVISION_DATE,
        },
        "keywords": [
            "AI governance",
            "human oversight",
            "workflow governance",
            "governing capacity",
            "Proper Ending",
            "Authority Return",
        ],
    }


def breadcrumb_schema(items: list[tuple[str, str]]) -> dict[str, object]:
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": position,
                "name": label,
                "item": f"{SITE}{path}",
            }
            for position, (label, path) in enumerate(items, start=1)
        ],
    }


def series_schema() -> dict[str, object]:
    """Return the canonical entity for the three-paper research programme."""
    return {
        "@type": "CreativeWorkSeries",
        "@id": SERIES_ID,
        "name": "Workflow-Centric AI Governance Trilogy",
        "alternateName": "The Proper Ending Index research trilogy",
        "url": f"{SITE}/papers/",
        "description": (
            "Takashi Sato's three-paper research programme on accountable decision "
            "routing, governing-capacity loss, Proper Ending, and Authority Return."
        ),
        "dateModified": UPDATED,
        "version": VERSION,
        "inLanguage": "en-US",
        "isAccessibleForFree": True,
        "creator": {"@id": AUTHOR_ID},
        "hasPart": [{"@id": f"{paper_url(paper)}#article"} for paper in PAPERS],
    }


PAPERS_BY_SLUG: dict[str, Paper] = {paper["slug"]: paper for paper in PAPERS}
