#!/usr/bin/env python3
"""Compile readable source assets into the deterministic runtime contract."""

from __future__ import annotations

from pathlib import Path
import re

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


def join_sources(paths: tuple[Path, ...]) -> str:
    """Join source modules in declared cascade order without hiding boundaries."""
    return "\n\n".join(path.read_text(encoding="utf-8").rstrip() for path in paths) + "\n"


def minify_css(css: str) -> str:
    """Compact generated CSS deterministically while keeping source files readable."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{}:;,])\s*", r"\1", css)
    css = css.replace(";} ", "} ").replace(";}", "}")
    return css.strip() + "\n"


def compact_js(js: str) -> str:
    """Drop source-only comments and blank lines without rewriting JavaScript syntax."""
    output: list[str] = []
    in_block_comment = False

    for line in js.splitlines():
        stripped = line.strip()
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
        output.append(line.rstrip())

    return "\n".join(output).rstrip() + "\n"


def build_assets() -> None:
    (ROOT / "assets/site.css").write_text(
        minify_css(join_sources(STYLE_SOURCES)),
        encoding="utf-8",
    )
    (ROOT / "assets/site.js").write_text(
        compact_js(join_sources(SCRIPT_SOURCES)),
        encoding="utf-8",
    )
    critical = (ROOT / "src/styles/critical.css").read_text(encoding="utf-8").rstrip() + "\n"
    (ROOT / "assets/critical.css").write_text(critical, encoding="utf-8")


if __name__ == "__main__":
    build_assets()
