#!/usr/bin/env python3
"""Temporary experiment: keep decorative cursor font off the initial critical path."""
from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise SystemExit(f"Expected one match in {path}: {old[:100]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    "src/styles/base.css",
    '''.cursor-orbit span {
  color: #000;
  font-family: var(--script);
  font-size: 1.18rem;
''',
    '''.cursor-orbit span {
  color: #000;
  font-family: "Snell Roundhand", "Segoe Script", cursive;
  font-size: 1.18rem;
''',
)
replace_once(
    "src/styles/base.css",
    '''.cursor-orbit.is-active span { opacity: 1; transform: rotate(-7deg) scale(1); }

.skip-link {''',
    '''.cursor-orbit.is-active span { opacity: 1; transform: rotate(-7deg) scale(1); }
html.has-cursor-font .cursor-orbit span { font-family: var(--script); }

.skip-link {''',
)
replace_once(
    "src/scripts/core.js",
    '''    doc.addEventListener('pointermove', (event) => {
      if (event.pointerType === 'touch') return;

      const samples = event.getCoalescedEvents?.() || [event];
''',
    '''    doc.addEventListener('pointermove', (event) => {
      if (event.pointerType === 'touch') return;
      if (!root.classList.contains('has-cursor-font')) root.classList.add('has-cursor-font');

      const samples = event.getCoalescedEvents?.() || [event];
''',
)
