"""Bibliographic exports derived from the canonical paper records."""
from .model import Paper, VERSION, PAPER_REVISION_DATE

def citation_export(paper: Paper, kind: str) -> str:
    title = f"{paper['title']}: {paper['subtitle']}"
    doi = paper["doi"]
    note = f"Working paper, version {VERSION}, revised {PAPER_REVISION_DATE}"
    year = paper["posted"][:4]
    if kind == "bib":
        return (
            "@unpublished{Sato" + year + paper["roman"] + ",\n"
            + "  author = {Sato, Takashi},\n"
            + "  title = {{" + title + "}},\n"
            + "  year = {" + year + "},\n"
            + "  note = {" + note + "},\n"
            + "  doi = {" + doi + "},\n"
            + "  url = {https://doi.org/" + doi + "}\n}\n"
        )
    if kind == "ris":
        return (
            "TY  - RPRT\nAU  - Sato, Takashi\nTI  - " + title
            + "\nPY  - " + year + "\nDO  - " + doi
            + "\nUR  - https://doi.org/" + doi
            + "\nN1  - " + note + "\nER  -\n"
        )
    raise ValueError(f"Unsupported citation format: {kind}")
