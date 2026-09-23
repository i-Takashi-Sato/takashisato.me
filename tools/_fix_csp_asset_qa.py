#!/usr/bin/env python3
from pathlib import Path

qa = Path('tools/verify_v62.py')
text = qa.read_text(encoding='utf-8')

old = '''    expected_assets = {
        "critical.css",
        "site.css",
'''
new = '''    expected_assets = {
        "site.css",
'''
if old not in text:
    raise SystemExit('critical.css expected asset entry not found')
text = text.replace(old, new)

old = '''    css = (ROOT / "assets/site.css").read_text(encoding="utf-8")
    critical_css = (ROOT / "assets/critical.css").read_text(encoding="utf-8")
    js = (ROOT / "assets/site.js").read_text(encoding="utf-8")
'''
new = '''    css = (ROOT / "assets/site.css").read_text(encoding="utf-8")
    js = (ROOT / "assets/site.js").read_text(encoding="utf-8")
'''
if old not in text:
    raise SystemExit('critical_css read block not found')
text = text.replace(old, new)

old = '''    if len(critical_css.encode()) > 25_000:
        fail(errors, f"critical stylesheet exceeds 25 KB: {len(critical_css.encode())}")
    if re.search(r"https?://|@import\\s+url", critical_css):
        fail(errors, "critical stylesheet contains a remote dependency")
    for token in ["site-header", "page-hero", "paper-hero", "author-hero", "hero-transition"]:
        if token not in critical_css:
            fail(errors, f"critical stylesheet missing {token}")
'''
if old not in text:
    raise SystemExit('critical stylesheet QA block not found')
text = text.replace(old, '')

qa.write_text(text, encoding='utf-8')
