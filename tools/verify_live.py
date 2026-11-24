#!/usr/bin/env python3
"""Verify delivered public bytes against the checked-out release, not just its build."""
from __future__ import annotations

import argparse
import hashlib
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://takashisato.me"
# Canonical public routes only; no mutable PDF aliases or third-party requests.
ROUTES = {
    "/": "index.html",
    "/papers/": "papers/index.html",
    **{f"/papers/part{i}.html": f"papers/part{i}.html" for i in range(1, 4)},
    **{f"/{name}.html": f"{name}.html" for name in ("about", "colophon", "privacy", "security")},
    **{f"/pdf/v6.2/part{i}.pdf": f"pdf/v6.2/part{i}.pdf" for i in range(1, 4)},
    **{f"/citations/v6.2/part{i}.{ext}": f"citations/v6.2/part{i}.{ext}" for i in range(1, 4) for ext in ("bib", "ris")},
    **{f"/assets/og/{name}.jpg": f"assets/og/{name}.jpg" for name in ("home", "papers", "part1", "part2", "part3", "about")},
    **{f"/{name}": name for name in (
        "assets/site.css", "assets/site.js", "assets/brand-mark.svg",
        "assets/author-mark.svg", "assets/author-paper.webp", "assets/research-metal.webp",
        "assets/fonts/InterVariable.woff2", "assets/fonts/Newsreader-Variable.woff2",
        "favicon.svg", "favicon.ico", "favicon-96x96.png", "apple-touch-icon.png",
        "android-chrome-192x192.png", "android-chrome-512x512.png", "maskable-512x512.png",
        "site.webmanifest", "research-index.json", "sitemap.xml", "robots.txt", "llms.txt",
    )},
}
TYPES = {
    ".html": {"text/html"},
    ".css": {"text/css"},
    ".js": {"text/javascript", "application/javascript"},
    ".pdf": {"application/pdf"},
    ".jpg": {"image/jpeg"},
    ".png": {"image/png"},
    ".webp": {"image/webp"},
    ".svg": {"image/svg+xml"},
    ".woff2": {"font/woff2", "application/font-woff2", "application/octet-stream"},
    ".ico": {"image/x-icon", "image/vnd.microsoft.icon", "application/octet-stream"},
    ".json": {"application/json"},
    ".xml": {"application/xml", "text/xml"},
    ".webmanifest": {"application/manifest+json", "application/json", "application/octet-stream"},
    ".txt": {"text/plain"},
}
MAX_BYTES = 8 * 1024 * 1024


class NoRedirect(HTTPRedirectHandler):
    """Canonical routes must serve directly; never fetch an unexpected destination."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_one(base: str, route: str, local: Path) -> str | None:
    expected = local.read_bytes()
    if len(expected) > MAX_BYTES:
        return f"{route}: release asset exceeds audit limit"
    url = urljoin(base.rstrip("/") + "/", route.lstrip("/"))
    opener = build_opener(NoRedirect())
    request = Request(url, headers={
        "User-Agent": "ProperEndingIndex-ReleaseAudit/1.0",
        "Accept-Encoding": "identity",
        "Cache-Control": "no-cache",
    })
    try:
        with opener.open(request, timeout=12) as response:
            if response.status != 200:
                return f"{route}: HTTP {response.status}"
            encoding = response.headers.get("Content-Encoding", "identity").lower()
            if encoding != "identity":
                return f"{route}: unexpected Content-Encoding {encoding}"
            allowed = TYPES.get(local.suffix.lower())
            media = response.headers.get_content_type()
            if allowed and media not in allowed:
                return f"{route}: unexpected media type {media}"
            actual = response.read(MAX_BYTES + 1)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        return f"{route}: {type(exc).__name__}: {exc}"
    if actual != expected:
        return (f"{route}: SHA-256 mismatch; expected {digest(expected)}, "
                f"received {digest(actual)} ({len(actual)} bytes)")
    return None


def verify(base: str, root: Path, routes: dict[str, str], attempts: int, interval: int) -> int:
    pending = dict(routes)
    for attempt in range(1, attempts + 1):
        with ThreadPoolExecutor(max_workers=4) as pool:
            outcomes = list(pool.map(lambda item: (item[0], verify_one(base, item[0], root / item[1])), pending.items()))
        for route, problem in outcomes:
            if problem:
                print(problem, flush=True)
            else:
                pending.pop(route)
        print(f"Attempt {attempt}/{attempts}: {len(routes) - len(pending)}/{len(routes)} exact matches", flush=True)
        if not pending:
            return 0
        if attempt < attempts:
            time.sleep(interval)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempts", type=int, default=1)
    parser.add_argument("--interval", type=int, default=15)
    args = parser.parse_args()
    if not 1 <= args.attempts <= 20 or not 0 <= args.interval <= 60:
        parser.error("invalid retry budget")
    return verify(SITE, ROOT, ROUTES, args.attempts, args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
