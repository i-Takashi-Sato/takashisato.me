#!/usr/bin/env python3
"""Compile human-readable source assets into the minimal runtime contract."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STYLE_SOURCES = (
    ROOT / "src/styles/base.css",
    ROOT / "src/styles/pavilion.css",
)
SCRIPT_SOURCES = (
    ROOT / "src/scripts/core.js",
    ROOT / "src/scripts/gate.js",
    ROOT / "src/scripts/analytics.js",
)

def join_sources(paths: tuple[Path, ...]) -> str:
    return "\n\n".join(path.read_text(encoding="utf-8").rstrip() for path in paths) + "\n"

def build_assets() -> None:
    (ROOT / "assets/site.css").write_text(join_sources(STYLE_SOURCES), encoding="utf-8")
    (ROOT / "assets/site.js").write_text(join_sources(SCRIPT_SOURCES), encoding="utf-8")
    critical = (ROOT / "src/styles/critical.css").read_text(encoding="utf-8").rstrip() + "\n"
    (ROOT / "assets/critical.css").write_text(critical, encoding="utf-8")

if __name__ == "__main__":
    build_assets()
