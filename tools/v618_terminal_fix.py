#!/usr/bin/env python3
"""Temporary v6.18 terminal-progress normalization; removed before merge."""
from pathlib import Path

path = Path("src/scripts/core.js")
text = path.read_text(encoding="utf-8")
old = """      if (footer) {
        const ending = clamp(1 - footer.getBoundingClientRect().top / innerHeight);
        root.style.setProperty('--ending', ending.toFixed(4));
        root.classList.toggle('is-ending', ending > 0.48);
      }
"""
new = """      if (footer) {
        const footerRect = footer.getBoundingClientRect();
        const terminalTravel = Math.max(1, Math.min(innerHeight, footerRect.height));
        const ending = clamp((innerHeight - footerRect.top) / terminalTravel);
        root.style.setProperty('--ending', ending.toFixed(4));
        root.classList.toggle('is-ending', ending > 0.48);
      }
"""
if old not in text:
    raise SystemExit("footer ending block not found")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
