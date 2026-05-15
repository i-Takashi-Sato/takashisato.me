Takashi Sato — Museum Rebuild v1

Purpose:
- Rebuild the public site as a coherent museum-grade AI Governance Observatory.
- Unify homepage, paper index, paper abstract pages, demo index, about, and contact pages under one visual language.
- Replace inconsistent page headers with a single museum header system.
- Keep existing PDFs and visualizer URLs intact.

Files included:
- index.html
- papers/index.html
- papers/part1.html
- papers/part2.html
- papers/part3.html
- demo/index.html
- demo/_assets/demo-mobile-shell.css
- about.html
- contact.html
- assets/museum.css
- assets/museum.js

Upload strategy:
- Best: upload this entire folder contents to the repository root on a new branch, then create a PR.
- If GitHub upload is too painful, use GitHub Desktop or ask a developer to replace these files in one commit.

Notes:
- This package does not delete the existing visualizer JS/CSS files. It keeps the visualizers alive.
- The demo shell CSS hides accidental Skip-to-content exposure and preserves Back-to-Part links.
- The design intentionally follows a museum/catalogue system rather than the current mixed homepage/article look.
