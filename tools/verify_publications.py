"""Tests for the publication registry using synthetic, non-published records."""
from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path

from src.archive.model import SITE, SERIES_ID
from src.archive.layout import json_ld
from src.archive.publications import Publication, catalogue, publications_page, released_publications, validate_publications


def fixture_records() -> tuple[Publication, ...]:
    return (
        Publication(
            id=SITE + "/fixture/essay.html#work", path="/fixture/essay.html",
            title="検証専用：日本語の長い題名と、異なる研究領域に属する随筆の読みやすさについて",
            summary="これは公開用の成果ではなく、和文の題名、概要、任意の識別子がなくても組版できるかを調べるためのテストデータである。",
            language="ja", kind="essay", published="2026-01-01",
        ),
        Publication(
            id=SITE + "/fixture/research-note.html#work", path="/fixture/research-note.html",
            title="Fixture only: A research note with a long title about an independent subject and an explicitly separate revision history",
            summary="Synthetic test record & <not a publication>. No external identifier or academic review is implied.",
            language="en", kind="research-note", published="2026-01-02", revised="2026-02-01", version="1.1",
        ),
    )


def audit_publications(root: Path, errors: list[str]) -> None:
    records = released_publications()
    try:
        validate_publications(records)
        if sum(work.collection == SERIES_ID for work in records) != 3:
            errors.append("Publication catalogue: trilogy coverage differs")
        generated = json.loads((root / "publications.json").read_text(encoding="utf-8"))
        if generated != catalogue(records):
            errors.append("Publication catalogue: JSON differs from canonical registry")
        if (root / "publications/index.html").read_text(encoding="utf-8") != publications_page(records):
            errors.append("Publication catalogue: rendered page differs from registry")
        for work in records:
            target = root / work.path.lstrip("/")
            if work.path.endswith("/"):
                target /= "index.html"
            if not target.is_file():
                errors.append("Publication catalogue: missing released destination " + work.path)
        fixtures = fixture_records()
        expanded = records + fixtures
        validate_publications(expanded)
        trial = catalogue(expanded)["publications"]
        if len(trial) != len(records) + len(fixtures) or "doi" in trial[-2] or "collection" in trial[-2] or "version" in trial[-2]:
            errors.append("Publication catalogue: optional fields incorrectly required")
        html = publications_page(expanded)
        if 'lang="ja"' not in html or "&amp; &lt;not a publication&gt;" not in html:
            errors.append("Publication catalogue: language or HTML escaping contract failed")
        if "/fixture/" in (root / "publications/index.html").read_text(encoding="utf-8") or "/fixture/" in json.dumps(generated):
            errors.append("Publication catalogue: synthetic fixture leaked into generated output")
        hostile = {"headline": "</script><script>fixture</script>"}
        serialized = json_ld(hostile)
        if serialized.count("</script>") != 1 or json.loads(serialized.split(">", 1)[1].rsplit("</script>", 1)[0]) != hostile:
            errors.append("Publication catalogue: unsafe or lossy JSON-LD serialization")
        # Larger catalogues must remain deterministic, unique and independent of
        # the current trilogy's record count. These are in-memory fixtures only.
        for count in (10, 50, 100):
            synthetic = tuple(
                replace(
                    fixtures[i % len(fixtures)],
                    id=f"{SITE}/fixture/item-{i}.html#work",
                    path=f"/fixture/item-{i}.html",
                )
                for i in range(count)
            )
            sample = records + synthetic
            result = catalogue(sample)["publications"]
            rendered = publications_page(sample)
            if len(result) != len(sample) or rendered.count('<article class="sequence-row">') != len(sample):
                errors.append(f"Publication catalogue: expansion to {count} fixtures lost records")
            if rendered != publications_page(sample):
                errors.append(f"Publication catalogue: nondeterministic output for {count} fixtures")
        invalid = (
            records + (records[0],),
            (replace(fixtures[0], path="//external.example/"),),
            (replace(fixtures[0], revised="2025-01-01"),),
            (replace(fixtures[0], kind="draft"),),
            (replace(fixtures[0], language=""),),
            (replace(fixtures[0], doi="not-a-doi"),),
        )
        for candidate in invalid:
            try:
                validate_publications(candidate)
            except ValueError:
                continue
            errors.append("Publication catalogue: invalid record accepted")
    except (ValueError, OSError, KeyError) as exc:
        errors.append(f"Publication catalogue: {exc}")
