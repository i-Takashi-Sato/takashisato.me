#!/usr/bin/env python3
"""Report browser protection headers on the public archive; no configuration changes."""

import json
from urllib.request import Request, build_opener

from verify_live import SITE, NoRedirect

PAGES = ("/", "/publications/", "/papers/", "/papers/part1.html", "/about.html", "/.well-known/security.txt")
FIELDS = ("Strict-Transport-Security", "Content-Security-Policy",
          "Content-Security-Policy-Report-Only", "X-Content-Type-Options",
          "X-Frame-Options", "Referrer-Policy", "Permissions-Policy")
def observe(path):
    req = Request(SITE + path, headers={"User-Agent": "TakashiSatoArchive-HeaderAudit/1.0"})
    with build_opener(NoRedirect()).open(req, timeout=15) as res:
        if res.status != 200:
            raise RuntimeError(f"Unexpected response status: {res.status}")
        return {"path": path, "status": res.status,
                "headers": {name: res.headers.get_all(name, []) for name in FIELDS}}

def main():
    # Public first-party requests only. No cookies, credentials, or policy changes.
    report = {"scope": "One HTTPS observation per selected path; presence does not certify security.",
              "observations": [observe(path) for path in PAGES]}
    print(json.dumps(report, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
