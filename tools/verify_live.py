#!/usr/bin/env python3
"""Verify delivered public bytes against the checked-out release, not just its build."""
from __future__ import annotations

import argparse
import hashlib
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.archive.model import PAPERS, SITE, VERSION
from src.archive.runtime_assets import RUNTIME_NAMES, runtime_path
from src.archive.routes import public_pages

SLUGS = tuple(paper["slug"] for paper in PAPERS)
# Canonical public routes only; no mutable PDF aliases or third-party requests.
ROUTES = {
    **{page.path: page.file for page in public_pages()},
    **{f"/pdf/v{VERSION}/{slug}.pdf": f"pdf/v{VERSION}/{slug}.pdf" for slug in SLUGS},
    **{f"/citations/v{VERSION}/{slug}.{ext}": f"citations/v{VERSION}/{slug}.{ext}" for slug in SLUGS for ext in ("bib", "ris", "json")},
    **{f"/assets/og/{name}.jpg": f"assets/og/{name}.jpg" for name in ("home", "papers", "part1", "part2", "part3", "about", "archive")},
    # Check the exact URLs used by newly generated HTML as well as the legacy aliases.
    **{"/" + runtime_path(name): runtime_path(name) for name in RUNTIME_NAMES},
    **{f"/{name}": name for name in (
        "assets/site.css", "assets/site.js", "assets/brand-mark.svg",
        "assets/author-mark.svg", "assets/author-paper.webp", "assets/research-metal.webp",
        "assets/fonts/InterVariable.woff2", "assets/fonts/Newsreader-Variable.woff2",
        "favicon.svg", "favicon.ico", "favicon-96x96.png", "apple-touch-icon.png",
        "android-chrome-192x192.png", "android-chrome-512x512.png", "maskable-512x512.png",
        "site.webmanifest", "research-index.json", "publications.json", "sitemap.xml", "robots.txt", "llms.txt", "feed.xml",
        "humans.txt", ".well-known/security.txt",
        "76a21f980fdabdd7e0452ee2206d1b18.txt",
        "reproduction/v6.3/trilogy_v6.3_publication_6953eeb9.zip",
        "reproduction/v5.9/part3-historical-checker.zip",
        "reproduction/v5.9/part3-reexecution-2026-11-24.json",
    )},
}
TYPES = {
    ".html": {"text/html"},
    ".css": {"text/css"},
    ".js": {"text/javascript", "application/javascript"},
    ".pdf": {"application/pdf"},
    ".zip": {"application/zip", "application/x-zip-compressed", "application/octet-stream"},
    ".jpg": {"image/jpeg"},
    ".png": {"image/png"},
    ".webp": {"image/webp"},
    ".svg": {"image/svg+xml"},
    ".woff2": {"font/woff2", "application/font-woff2", "application/octet-stream"},
    ".ico": {"image/x-icon", "image/vnd.microsoft.icon", "application/octet-stream"},
    ".json": {"application/json"},
    ".xml": {"application/xml", "text/xml", "application/atom+xml"},
    ".webmanifest": {"application/manifest+json", "application/json", "application/octet-stream"},
    ".txt": {"text/plain"},
}
MAX_BYTES = 8 * 1024 * 1024
ROBOTS_PREFIX = ROOT / "tools/fixtures/cloudflare-managed-robots.txt"


class NoRedirect(HTTPRedirectHandler):
    """Canonical routes must serve directly; never fetch an unexpected destination."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def cache_details(headers) -> str:
    fields = ("Age", "Cache-Control", "CF-Cache-Status", "X-Cache", "ETag", "Last-Modified")
    values = [f"{name}={headers.get(name)[:180]!r}" for name in fields if headers.get(name)]
    return f" [cache: {'; '.join(values)}]" if values else ""


def verify_one(base: str, route: str, local: Path) -> str | None:
    expected = local.read_bytes()
    if len(expected) > MAX_BYTES:
        return f"{route}: release asset exceeds audit limit"
    url = urljoin(base.rstrip("/") + "/", route.lstrip("/"))
    opener = build_opener(NoRedirect())
    request = Request(url, headers={
        "User-Agent": "TakashiSatoArchive-ReleaseAudit/1.0",
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
            cache = cache_details(response.headers)
    except HTTPError as exc:
        return f"{route}: HTTPError: HTTP {exc.code}" + cache_details(exc.headers)
    except (URLError, TimeoutError, OSError) as exc:
        return f"{route}: {type(exc).__name__}: {exc}"
    if route == "/robots.txt" and actual != expected:
        prefix = ROBOTS_PREFIX.read_bytes()
        if actual == prefix + expected:
            print("/robots.txt: exact approved Cloudflare prefix and origin suffix match", flush=True)
            return None
    if actual != expected:
        return (f"{route}: SHA-256 mismatch; expected {digest(expected)}, "
                f"received {digest(actual)} ({len(actual)} bytes)" + cache)
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
        print(f"Attempt {attempt}/{attempts}: {len(routes) - len(pending)}/{len(routes)} verified responses", flush=True)
        if not pending:
            if attempt == 1:
                return 0
            # Partial successes from different attempts are not a coherent sweep.
            with ThreadPoolExecutor(max_workers=4) as pool:
                confirmation = list(pool.map(lambda item: (item[0], verify_one(base, item[0], root / item[1])), routes.items()))
            for route, problem in confirmation:
                if problem:
                    print(problem, flush=True)
                    pending[route] = routes[route]
            print(f"Full confirmation: {len(routes) - len(pending)}/{len(routes)} verified responses", flush=True)
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
