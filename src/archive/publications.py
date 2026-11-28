"""Discipline-neutral catalogue of released works; no drafts or empty topics."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from html import escape
import re
from textwrap import dedent

from .layout import breadcrumbs, head, shell_page
from .model import (
    AUTHOR, AUTHOR_ID, PAPERS, PAPER_REVISION_DATE, SERIES_ID, SITE, VERSION,
    breadcrumb_schema, paper_url,
)

KINDS = {
    "working-paper": "Working paper",
    "research-article": "Research article",
    "research-note": "Research note",
    "essay": "Essay",
    "review": "Review",
    "other": "Writing",
}
REVIEW_STATES = {"not-established", "not-peer-reviewed", "peer-reviewed", "not-applicable"}


@dataclass(frozen=True)
class Publication:
    id: str
    path: str
    title: str
    summary: str
    language: str
    kind: str
    published: str
    revised: str | None = None
    version: str | None = None
    collection: str | None = None
    doi: str | None = None
    review: str | None = None
    subtitle: str | None = None

    @property
    def full_title(self) -> str:
        return f"{self.title}: {self.subtitle}" if self.subtitle else self.title


# Add only records with a real, released HTML destination. No placeholder topics.
STANDALONE_PUBLICATIONS: tuple[Publication, ...] = ()


def released_publications() -> tuple[Publication, ...]:
    """Adapt the established trilogy and include independently released works."""
    trilogy = tuple(
        Publication(
            id=f"{paper_url(paper)}#article",
            path=paper_url(paper).removeprefix(SITE),
            title=paper["title"],
            subtitle=paper["subtitle"],
            summary=paper["description"],
            language="en-US",
            kind="working-paper",
            published=paper["posted"],
            revised=PAPER_REVISION_DATE,
            version=VERSION,
            collection=SERIES_ID,
            doi=paper["doi"],
            review="not-established",
        )
        for paper in PAPERS
    )
    records = trilogy + STANDALONE_PUBLICATIONS
    validate_publications(records)
    return records


def validate_publications(records: tuple[Publication, ...]) -> None:
    ids, paths, dois = set(), set(), set()
    for work in records:
        if not re.fullmatch(r"/[a-z0-9][a-z0-9/-]*(?:\.html|/)", work.path) or "//" in work.path:
            raise ValueError("Invalid canonical publication path")
        if not re.fullmatch(re.escape(SITE + work.path) + r"#[a-z][a-z0-9-]*", work.id):
            raise ValueError("Invalid stable publication identifier")
        if work.id in ids or work.path in paths:
            raise ValueError("Duplicate publication identity")
        if not work.title.strip() or not work.summary.strip():
            raise ValueError("Missing title or summary")
        if work.subtitle is not None and not work.subtitle.strip():
            raise ValueError("Empty publication subtitle")
        if work.kind not in KINDS or not re.fullmatch(r"[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*", work.language):
            raise ValueError("Invalid publication type or language")
        if work.review is not None and work.review not in REVIEW_STATES:
            raise ValueError("Invalid review status")
        first = date.fromisoformat(work.published)
        if first.isoformat() != work.published:
            raise ValueError("Noncanonical publication date")
        if work.revised is not None:
            revised = date.fromisoformat(work.revised)
            if revised.isoformat() != work.revised or revised < first:
                raise ValueError("Invalid revision date")
        if work.collection is not None and not work.collection.startswith(SITE + "/"):
            raise ValueError("Invalid collection reference")
        if work.doi is not None:
            if not re.fullmatch(r"10\.\d{4,9}/\S+", work.doi) or work.doi.casefold() in dois:
                raise ValueError("Invalid or duplicate DOI")
            dois.add(work.doi.casefold())
        ids.add(work.id)
        paths.add(work.path)


def catalogue(records: tuple[Publication, ...] | None = None) -> dict[str, object]:
    records = released_publications() if records is None else records
    validate_publications(records)
    return {
        "schemaVersion": 1,
        "author": AUTHOR_ID,
        "url": f"{SITE}/publications/",
        "publications": [
            {**{key: value for key, value in asdict(work).items() if value is not None and key != "subtitle"}, "title": work.full_title}
            for work in records
        ],
    }


def publication_row(work: Publication) -> str:
    lang = escape(work.language, quote=True)
    title = escape(work.title)
    if work.subtitle:
        title += f'<span class="sr-only">: </span><span class="publication-subtitle">{escape(work.subtitle)}</span>'
    summary = escape(work.summary)
    path = escape(work.path, quote=True)
    meta = [work.published]
    if work.revised and work.revised != work.published:
        meta.append(f"Revised {work.revised}")
    if work.version:
        meta.append(f"v{work.version}")
    if work.doi:
        meta.append(f"DOI {work.doi}")
    if work.review == "not-established":
        meta.append("Independent review not established")
    elif work.review == "peer-reviewed":
        meta.append("Peer-reviewed")
    elif work.review == "not-peer-reviewed":
        meta.append("Not peer-reviewed")
    return dedent(f"""
        <article class="sequence-row">
          <p class="sequence-function">{KINDS[work.kind]}</p>
          <div>
            <h2 class="sequence-title" lang="{lang}"><a href="{path}">{title}</a></h2>
            <p class="sequence-copy" lang="{lang}">{summary}</p>
            <span class="sequence-state">{escape(" · ".join(meta))}</span>
          </div>
        </article>
        """).strip()


def publications_page(records: tuple[Publication, ...] | None = None) -> str:
    records = released_publications() if records is None else records
    validate_publications(records)
    title = "Publications · Takashi Sato"
    description = "Published research and writings by Takashi Sato (佐藤貴士), with publication dates, types, and links to individual records."
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            AUTHOR,
            {
                "@type": "CollectionPage",
                "@id": f"{SITE}/publications/#catalogue",
                "name": "Publications",
                "url": f"{SITE}/publications/",
                "author": {"@id": AUTHOR_ID},
                "isPartOf": {"@id": f"{SITE}/#website"},
                "mainEntity": {
                    "@type": "ItemList",
                    "itemListElement": [
                        {"@type": "ListItem", "position": i, "name": work.full_title, "url": SITE + work.path, "item": {"@id": work.id}}
                        for i, work in enumerate(records, 1)
                    ],
                },
            },
            breadcrumb_schema([("Index", "/"), ("Publications", "/publications/")]),
        ],
    }
    rows = " ".join(publication_row(work) for work in records)
    body = dedent(f"""
        <main id="main">
          <header class="page-hero shell">
            {breadcrumbs([("Index", "/"), ("Publications", None)])}
            <p class="eyebrow">Research &amp; writings</p>
            <h1>Publications.</h1>
            <p class="page-deck">A record of published work, with publication dates, revisions where applicable, and review status where known. Each entry leads to its individual record.</p>
            <div class="hero-actions"><a class="button primary" href="/papers/">The Proper Ending Index</a><a class="button" href="/publications.json">Machine-readable catalogue</a></div>
          </header>
          <section class="section compact">
            <div class="shell">
              <h2 class="sr-only">Publication records</h2>
              <div class="sequence">{rows}</div>
            </div>
          </section>
        </main>
        """).strip()
    return shell_page(head_html=head(title=title, description=description, path="/publications/", image="/assets/og/archive.jpg", schema=schema, robots="index,follow"), body=body, active="publications", page="publications")
