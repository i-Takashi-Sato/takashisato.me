#!/usr/bin/env python3
"""Temporary experiment v2: load the decorative cursor font only when its label becomes visible."""
from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise SystemExit(f"Expected one match in {path}: {old[:120]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    "src/styles/base.css",
    '''@font-face {
  font-family: "Mea Culpa";
  src: url("/assets/fonts/MeaCulpa.woff2") format("woff2");
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}

''',
    "",
)
replace_once(
    "src/styles/base.css",
    '  --script: "Mea Culpa", "Snell Roundhand", "Segoe Script", cursive;\n',
    "",
)
replace_once(
    "src/styles/base.css",
    'html.has-cursor-font .cursor-orbit span { font-family: var(--script); }',
    'html.has-cursor-font .cursor-orbit span { font-family: "Mea Culpa", "Snell Roundhand", "Segoe Script", cursive; }',
)

replace_once(
    "src/scripts/core.js",
    '''    const magneticControls = [...doc.querySelectorAll('.button')];
    const paperHero = doc.querySelector('.paper-hero');

    let pointerX = innerWidth / 2;
''',
    '''    const magneticControls = [...doc.querySelectorAll('.button')];
    const paperHero = doc.querySelector('.paper-hero');
    let cursorFontPromise = null;

    function ensureCursorFont() {
      if (root.classList.contains('has-cursor-font')) return Promise.resolve();
      if (cursorFontPromise) return cursorFontPromise;
      if (!window.FontFace || !doc.fonts) return Promise.resolve();

      const face = new FontFace(
        'Mea Culpa',
        'url("/assets/fonts/MeaCulpa.woff2") format("woff2")',
        { style: 'normal', weight: '400', display: 'swap' },
      );
      cursorFontPromise = face.load()
        .then((loaded) => {
          doc.fonts.add(loaded);
          root.classList.add('has-cursor-font');
        })
        .catch(() => undefined);
      return cursorFontPromise;
    }

    let pointerX = innerWidth / 2;
''',
)
replace_once(
    "src/scripts/core.js",
    '''    doc.addEventListener('pointermove', (event) => {
      if (event.pointerType === 'touch') return;
      if (!root.classList.contains('has-cursor-font')) root.classList.add('has-cursor-font');

      const samples = event.getCoalescedEvents?.() || [event];
''',
    '''    doc.addEventListener('pointermove', (event) => {
      if (event.pointerType === 'touch') return;

      const samples = event.getCoalescedEvents?.() || [event];
''',
)
replace_once(
    "src/scripts/core.js",
    '''      if (control) {
        const kind = cursorLabel(control);
        label.textContent = kind;
''',
    '''      if (control) {
        void ensureCursorFont();
        const kind = cursorLabel(control);
        label.textContent = kind;
''',
)
