#!/usr/bin/env python3
"""Apply semantic HTML corrections discovered by the production validator."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools" / "build_site.py"


def replace_once(text: str, old: str, new: str) -> str:
    if new in text:
        return text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected one anchor, found {count}: {old[:80]!r}")
    return text.replace(old, new, 1)


def main() -> None:
    text = PATH.read_text(encoding="utf-8")
    text = replace_once(text, "<!doctype html>", "<!DOCTYPE html>")
    text = replace_once(
        text,
        '<h1 aria-label="Takashi Sato"><span>Takashi Sato</span></h1>',
        '<h1><span>Takashi Sato</span></h1>',
    )
    text = replace_once(
        text,
        '<thead><tr><th>Proposition</th><th>Target contrast</th><th>Evidence against</th></tr></thead>',
        '<thead><tr><th scope="col">Proposition</th><th scope="col">Target contrast</th><th scope="col">Evidence against</th></tr></thead>',
    )
    for label in [
        "P1 · Capacity-strain decoupling",
        "P2 · Target conversion",
        "P3 · Voice-efficacy feedback",
        "P4 · Coupled-trace discrimination",
        "P5 · Comparative state validity",
    ]:
        text = replace_once(text, f'<tr><th>{label}</th>', f'<tr><th scope="row">{label}</th>')
    PATH.write_text(text, encoding="utf-8")
    print("Applied semantic HTML corrections to build_site.py")


if __name__ == "__main__":
    main()
