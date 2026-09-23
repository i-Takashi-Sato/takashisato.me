#!/usr/bin/env python3
"""Temporary v6.18 experiment: first-viewport content is not reveal-state content."""
from pathlib import Path

path = Path("src/archive/pages.py")
text = path.read_text(encoding="utf-8")
replacements = {
    '<div data-reveal>\n                <p class="eyebrow">AI Governance Research Archive': '<div>\n                <p class="eyebrow">AI Governance Research Archive',
    '<div class="hero-aside" data-reveal>': '<div class="hero-aside">',
    '<p class="eyebrow" data-reveal>Workflow-Centric AI Governance Trilogy</p>': '<p class="eyebrow">Workflow-Centric AI Governance Trilogy</p>',
    '<h1 data-reveal>Three papers. One institutional problem.</h1>': '<h1>Three papers. One institutional problem.</h1>',
    '<p class="page-deck" data-reveal>Accountability can fail': '<p class="page-deck">Accountability can fail',
    '<div class="paper-meta" data-reveal>\n              <span>Author · Takashi Sato</span>': '<div class="paper-meta">\n              <span>Author · Takashi Sato</span>',
    '<p class="eyebrow" data-reveal>Workflow-Centric AI Governance Trilogy · Part {paper[\'roman\']}</p>': '<p class="eyebrow">Workflow-Centric AI Governance Trilogy · Part {paper[\'roman\']}</p>',
    '<h1 data-reveal>{paper[\'title\']}</h1>': '<h1>{paper[\'title\']}</h1>',
    '<p class="paper-subtitle" data-reveal>{paper[\'subtitle\']}</p>': '<p class="paper-subtitle">{paper[\'subtitle\']}</p>',
    '<div class="paper-meta" data-reveal>\n              <span>Takashi Sato</span>': '<div class="paper-meta">\n              <span>Takashi Sato</span>',
    '<div class="paper-actions" data-reveal>': '<div class="paper-actions">',
    '<div class="author-name" data-reveal>': '<div class="author-name">',
    '<div class="author-thesis" data-reveal>': '<div class="author-thesis">',
}
for old, new in replacements.items():
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly one occurrence, got {count}: {old[:90]!r}")
    text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")
