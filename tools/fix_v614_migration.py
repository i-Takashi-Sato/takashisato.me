#!/usr/bin/env python3
"""Repair one-shot v6.14 migration scopes before the final retry."""

from pathlib import Path

path = Path(__file__).with_name("migrate_v614_architecture.py")
text = path.read_text(encoding="utf-8")

map_needle = '''    )
    if marker not in papers:
        raise RuntimeError("papers body marker not found")
'''
map_replacement = '''    )
    map_code = "\\n".join(f"    {line}" if line else "" for line in map_code.strip().splitlines()) + "\\n"
    if marker not in papers:
        raise RuntimeError("papers body marker not found")
'''
if map_needle not in text:
    raise SystemExit("v6.14 map scope patch anchor not found")
text = text.replace(map_needle, map_replacement, 1)

qa_needle = '''    home_add = home_anchor + dedent(
        '''
'''
qa_replacement = '''    home_add = home_anchor + "\\n".join(
        f"    {line}" if line else ""
        for line in dedent(
        '''
'''
if qa_needle not in text:
    raise SystemExit("v6.14 QA scope patch anchor not found")
text = text.replace(qa_needle, qa_replacement, 1)

qa_close_needle = '''        '''
    )
    if home_anchor not in text:
'''
qa_close_replacement = '''        '''
        ).strip().splitlines()
    ) + "\\n"
    if home_anchor not in text:
'''
if qa_close_needle not in text:
    raise SystemExit("v6.14 QA scope close anchor not found")
text = text.replace(qa_close_needle, qa_close_replacement, 1)

path.write_text(text, encoding="utf-8")
print("v6.14 migration scopes repaired")
