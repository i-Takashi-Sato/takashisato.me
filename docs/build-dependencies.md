# Build dependency review — 25 November 2026

The archive has no third-party client runtime. The image generator and PDF verifier use pinned Python dependencies. Versions are reviewed separately from browser-tool dependencies because image encoding or PDF text extraction changes can alter verification results.

Candidate versions: pypdf 7.1.1 (18 November 2026) and Pillow 13.0.0 (16 October 2026), as listed by the maintainers on PyPI. The prior pins (6.6.2 and 12.3.0) predate subsequent security advisories. See the projects' advisory lists:
- https://github.com/py-pdf/pypdf/security/advisories
- https://github.com/python-pillow/Pillow/security/advisories
- https://pypi.org/project/pypdf/7.1.1/
- https://pypi.org/project/Pillow/13.0.0/

The dependencies operate on repository-controlled files, not visitor uploads. This reduces exposure but does not remove build supply-chain risk. No claim that the candidate versions are free of vulnerabilities.

Before adopting, require the normal deterministic build, immutable PDF verification, and all release gates. If generated OG images change, inspect the differences and explicitly review regenerated output; do not weaken the clean-diff check or silently change research files. Browser tooling and transitive packages are not certified by this direct dependency review.
