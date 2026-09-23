#!/usr/bin/env python3
"""Compile readable source modules into the deterministic runtime contract."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STYLE_SOURCES = (
    ROOT / "src/styles/base.css",
    ROOT / "src/styles/pavilion.css",
    ROOT / "src/styles/instruments.css",
    ROOT / "src/styles/motion.css",
    ROOT / "src/styles/performance.css",
)

SCRIPT_SOURCES = (
    ROOT / "src/scripts/core.js",
    ROOT / "src/scripts/gate.js",
    ROOT / "src/scripts/analytics.js",
)

RUNTIME_STYLE_DIR = ROOT / "assets/styles"


def join_sources(paths: tuple[Path, ...]) -> str:
    """Join source modules in declared order without hiding boundaries."""
    return "\n\n".join(path.read_text(encoding="utf-8").rstrip() for path in paths) + "\n"


def _backtick_parity(line: str) -> int:
    """Return whether a line contains an odd number of unescaped template delimiters."""
    count = 0
    escaped = False
    for character in line:
        if escaped:
            escaped = False
            continue
        if character == "\\":
            escaped = True
            continue
        if character == "`":
            count += 1
    return count % 2


def compact_js(js: str) -> str:
    """Remove source-only space while preserving multiline template literal content."""
    output: list[str] = []
    in_block_comment = False
    in_template = False

    for line in js.splitlines():
        stripped = line.strip()

        if not in_template:
            if in_block_comment:
                if "*/" in stripped:
                    in_block_comment = False
                continue
            if stripped.startswith("/*"):
                if "*/" not in stripped:
                    in_block_comment = True
                continue
            if not stripped or stripped.startswith("//"):
                continue
            rendered = line.lstrip().rstrip()
        else:
            rendered = line.rstrip()

        output.append(rendered)
        if _backtick_parity(line):
            in_template = not in_template

    return "\n".join(output).rstrip() + "\n"


def build_styles() -> None:
    """Publish the cascade as inspectable modules behind one stable stylesheet URL."""
    RUNTIME_STYLE_DIR.mkdir(parents=True, exist_ok=True)
    imports: list[str] = []

    for source in STYLE_SOURCES:
        runtime = RUNTIME_STYLE_DIR / source.name
        runtime.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        imports.append(f'@import url("/assets/styles/{source.name}");')

    (ROOT / "assets/site.css").write_text("\n".join(imports) + "\n", encoding="utf-8")


def build_assets() -> None:
    build_styles()
    (ROOT / "assets/site.js").write_text(
        compact_js(join_sources(SCRIPT_SOURCES)),
        encoding="utf-8",
    )


if __name__ == "__main__":
    build_assets()
