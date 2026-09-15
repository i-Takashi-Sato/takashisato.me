#!/usr/bin/env python3
"""Repair one-shot v6.14 migration scopes before the final retry."""

from pathlib import Path

path = Path(__file__).with_name("migrate_v614_architecture.py")
text = path.read_text(encoding="utf-8")

map_needle = "    )\n    if marker not in papers:\n        raise RuntimeError(\"papers body marker not found\")\n"
map_replacement = "    )\n    map_code = \"\\\\n\".join(f\"    {line}\" if line else \"\" for line in map_code.strip().splitlines()) + \"\\\\n\"\n    if marker not in papers:\n        raise RuntimeError(\"papers body marker not found\")\n"
if map_needle not in text:
    raise SystemExit("v6.14 map scope patch anchor not found")
text = text.replace(map_needle, map_replacement, 1)

qa_needle = "    home_add = home_anchor + dedent(\n        '''\n"
qa_replacement = "    home_add = home_anchor + \"\\\\n\".join(\n        f\"    {line}\" if line else \"\"\n        for line in dedent(\n        '''\n"
if qa_needle not in text:
    raise SystemExit("v6.14 QA scope patch anchor not found")
text = text.replace(qa_needle, qa_replacement, 1)

qa_close_needle = "        '''\n    )\n    if home_anchor not in text:\n"
qa_close_replacement = "        '''\n        ).strip().splitlines()\n    ) + \"\\\\n\"\n    if home_anchor not in text:\n"
if qa_close_needle not in text:
    raise SystemExit("v6.14 QA scope close anchor not found")
text = text.replace(qa_close_needle, qa_close_replacement, 1)

path.write_text(text, encoding="utf-8")
print("v6.14 migration scopes repaired")
