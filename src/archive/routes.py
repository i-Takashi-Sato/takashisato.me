"""Canonical indexed page routes and editorial revision dates.

Publication dates describe works; route dates describe their public HTML records.
Non-indexed notices and binary assets have separate release contracts.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import re

from .model import PAPERS, SITE, UPDATED, paper_url
from .publications import Publication, released_publications, validate_publications


@dataclass(frozen=True)
class PublicPage:
    path: str
    lastmod: str

    def __post_init__(self) -> None:
        if not re.fullmatch(r"/(?:[a-z0-9][a-z0-9-]*/)*(?:[a-z0-9][a-z0-9-]*\.html)?", self.path):
            raise ValueError(f"Invalid public page path: {self.path}")
        if date.fromisoformat(self.lastmod).isoformat() != self.lastmod:
            raise ValueError(f"Invalid route revision date: {self.lastmod}")

    @property
    def file(self) -> str:
        return self.path.lstrip("/") + ("index.html" if self.path.endswith("/") else "")


# Editorial changes to preserved research records do not revise the manuscripts.
TRILOGY_PAGE_DATES = {
    paper_url(paper).removeprefix(SITE): "2026-11-25"
    for paper in PAPERS
}


def public_pages(records: tuple[Publication, ...] | None = None) -> tuple[PublicPage, ...]:
    records = released_publications() if records is None else records
    validate_publications(records)
    pages = (
        PublicPage("/", "2026-11-26"),
        PublicPage("/publications/", "2026-11-26"),
        PublicPage("/papers/", "2026-11-26"),
        *(PublicPage(work.path, TRILOGY_PAGE_DATES.get(work.path, work.revised or work.published)) for work in records),
        PublicPage("/about.html", "2026-11-26"),
        PublicPage("/colophon.html", "2026-11-24"),
        PublicPage("/privacy.html", UPDATED),
        PublicPage("/security.html", UPDATED),
    )
    if len({page.path for page in pages}) != len(pages):
        raise ValueError("Public page paths must be unique")
    if len({page.file for page in pages}) != len(pages):
        raise ValueError("Public page output files must be unique")
    return pages
