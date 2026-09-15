#!/usr/bin/env python3
"""Repair the one-shot v6.14 migration before its final retry."""

from pathlib import Path

path = Path(__file__).with_name("migrate_v614_architecture.py")
text = path.read_text(encoding="utf-8")
needle = '''    )
    if marker not in papers:
        raise RuntimeError("papers body marker not found")
'''
replacement = '''    )
    map_code = "\\n".join(f"    {line}" if line else "" for line in map_code.strip().splitlines()) + "\\n"
    if marker not in papers:
        raise RuntimeError("papers body marker not found")
'''
if needle not in text:
    raise SystemExit("v6.14 migration patch anchor not found")
path.write_text(text.replace(needle, replacement, 1), encoding="utf-8")
print("v6.14 migration scope repaired")
