"""Canonical concept summaries shared by the catalogue and machine index."""

from .model import AUTHOR_ID, SERIES_ID, SITE, VERSION

# Navigation records summarize existing archive sections; they do not extend the papers.
CONCEPTS = [
    [
        "typed-gate",
        "Typed Gate Contract",
        "part1",
        "I",
        "contract",
        "Decision routing, not execution.",
        "Stage 1 routes cases; all-PASS permits entry to separate execution control. Reviewed cases require a current, in-scope signed disposition.",
        "verification"
    ],
    [
        "evidence-hold",
        "Evidence hold",
        "part1",
        "I",
        "contract",
        "Missing evidence is not approval.",
        "UNKNOWN with review authority and capacity routes to evidence completion and rerun. Signed DEFER is a separate disposition.",
        "verification"
    ],
    [
        "pmgcl",
        "Procedurally Masked Governing-Capacity Loss (PMGCL)",
        "part2",
        "II",
        "state-model",
        "Descriptive state model.",
        "Stable or improving procedural fidelity, persistent material losses of judgment and governing capacity, and material impairment of a predeclared protected function.",
        "propositions"
    ],
    [
        "pac",
        "Pre-Abuse Collapse (PAC)",
        "part2",
        "II",
        "overview",
        "Provisional etiological subtype.",
        "Requires PMGCL plus an identified materially adverse ordinary-exposure contrast under a predeclared malicious-pathway intervention or reference condition.",
        "propositions"
    ],
    [
        "circuit-breaker",
        "Circuit Breaker",
        "part3",
        "III",
        "overview",
        "Reversible containment.",
        "An authorized, scoped and reversible containment action with a named owner. Indicators cannot authorize it.",
        "verification"
    ],
    [
        "proper-ending",
        "Proper Ending",
        "part3",
        "III",
        "proper-ending",
        "Accountable retirement.",
        "Retirement requires evidence preservation, service continuity, remedy, branch-specific responsibility, assurance and authorized closure.",
        "verification"
    ],
    [
        "authority-return",
        "Authority Return",
        "part3",
        "III",
        "authority-return",
        "Practical capacity, not title alone.",
        "Reconstitute practical decision capacity in an accepting successor, or assign residual custody or remedy authority if the function ends.",
        "verification"
    ]
]


# Printed page locators in the immutable v6.2 papers (cover is page 1).
# Each heading is checked against the preserved PDF by Archive QA.
CONCEPT_SOURCES = {
    "typed-gate": (9, 10, "total triage function"),
    "evidence-hold": (9, 10, "total triage function"),
    "pmgcl": (8, 9, "Core Constructs, Descriptive State"),
    "pac": (8, 9, "Core Constructs, Descriptive State"),
    "circuit-breaker": (13, 13, "5. Circuit Breaker"),
    "proper-ending": (14, 15, "7. Proper Ending"),
    "authority-return": (15, 16, "8. Authority Return"),
}


def concept_schema() -> dict[str, object]:
    """Describe the visible navigation summaries, not independent validation."""
    base = f"{SITE}/papers/"
    term_set = f"{base}#concepts"
    terms = []
    for slug, title, paper, roman, anchor, status, summary, assessment in CONCEPTS:
        url = f"{base}#concept-{slug}"
        terms.append({
            "@type": "DefinedTerm",
            "@id": url,
            "url": url,
            "name": title,
            "description": f"{status} {summary}",
            "inDefinedTermSet": {"@id": term_set},
            "subjectOf": {"@id": f"{base}{paper}.html#article"},
        })
    return {
        "@type": "DefinedTermSet",
        "@id": term_set,
        "url": term_set,
        "name": "Concepts and evidence",
        "description": "An index of the archive's research concepts, not new definitions or independent validation.",
        "version": VERSION,
        "inLanguage": "en",
        "creator": {"@id": AUTHOR_ID},
        "about": {"@id": SERIES_ID},
        "hasDefinedTerm": terms,
    }
