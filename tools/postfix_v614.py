#!/usr/bin/env python3
"""Finalize generated v6.14 authoring source before the release build."""

from pathlib import Path

root = Path(__file__).resolve().parents[1]

build = root / "tools/build_site.py"
build_text = build.read_text(encoding="utf-8")
entrypoint = '\n\nif __name__ == "__main__":\n    main()\n'
if 'if __name__ == "__main__"' not in build_text:
    build.write_text(build_text.rstrip() + entrypoint, encoding="utf-8")

pages = root / "src/archive/pages.py"
pages_text = pages.read_text(encoding="utf-8")
needle = '<section class="research-map-section" aria-label="Trilogy research map">\n            <div class="shell">'
replacement = '<section class="research-map-section" aria-label="Trilogy research map">\n            <h2 class="sr-only">Research map</h2>\n            <div class="shell">'
if needle not in pages_text:
    raise SystemExit("research-map semantic anchor not found")
pages.write_text(pages_text.replace(needle, replacement, 1), encoding="utf-8")

model = (root / "src/archive/model.py").read_text(encoding="utf-8")
for required in ('UPDATED = "2026-09-16"', 'ASSET_VERSION = "6.14.0"', 'SERIES_ID = f"{SITE}/papers/#trilogy"'):
    if required not in model:
        raise SystemExit(f"canonical v6.14 model contract missing: {required}")

print("v6.14 generated source finalized")
