#!/usr/bin/env python3
"""Notify participating search engines of selected, verified public pages."""

import argparse
import json
import sys
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, build_opener
from verify_live import NoRedirect, ROOT, ROUTES, SITE, verify_one
from src.archive.routes import public_pages

KEY = "76a21f980fdabdd7e0452ee2206d1b18"
KEY_PATH = "/" + KEY + ".txt"
ENDPOINT = "https://api.indexnow.org/indexnow"
PUBLIC_PAGES = tuple(page.path for page in public_pages())


def payload(paths):
    """Allow only explicit, canonical page paths; never arbitrary URLs."""
    if not paths or any(path not in PUBLIC_PAGES for path in paths):
        raise ValueError("Select canonical public pages only")
    return {
        "host": urlsplit(SITE).hostname,
        "key": KEY,
        "keyLocation": SITE + KEY_PATH,
        "urlList": [SITE + path for path in dict.fromkeys(paths)],
    }


def submit(paths):
    data = payload(paths)
    # Check that the public content is this release, not an earlier cached version.
    for path in [KEY_PATH, *dict.fromkeys(paths)]:
        problem = verify_one(SITE, path, ROOT / ROUTES[path])
        if problem:
            raise RuntimeError(problem)
    request = Request(ENDPOINT, data=json.dumps(data).encode("utf-8"),
                      headers={"Content-Type": "application/json; charset=utf-8",
                               "User-Agent": "TakashiSatoArchive-SearchNotice/1.0"},
                      method="POST")
    # No redirects, no repeated submissions, no credentials.
    with build_opener(NoRedirect()).open(request, timeout=20) as response:
        if response.status not in (200, 202):
            raise RuntimeError(f"Unexpected HTTP {response.status}")
        print(f"IndexNow HTTP {response.status}: {len(data['urlList'])} URLs received "
              "(indexing and ranking are not guaranteed)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", choices=PUBLIC_PAGES)
    parser.add_argument("--send", action="store_true", help="Submit to IndexNow")
    args = parser.parse_args()
    if not args.send:
        print(json.dumps(payload(args.paths), indent=2))
        return 0
    try:
        submit(args.paths)
    except (HTTPError, OSError, RuntimeError) as error:
        print(f"IndexNow failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
