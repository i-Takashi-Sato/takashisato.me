#!/usr/bin/env python3
"""Compare the served archive with the generated files of a release checkout."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.error import URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://takashisato.me"
FINGERPRINT = re.compile(r"/assets/site\.([0-9a-f]{64})\.(?:css|js)")


@dataclass(frozen=True)
class Resource:
    route: str
    content: bytes

    @property
    def digest(self) -> str:
        return sha256(self.content).hexdigest()


@dataclass(frozen=True)
class Finding:
    route: str
    state: str
    detail: str = ""


class RuntimeReferences(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.paths: set[str] = set()

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        path = attributes.get("href") if tag == "link" else attributes.get("src") if tag == "script" else None
        if path and FINGERPRINT.fullmatch(path):
            self.paths.add(path)


def local_file(root: Path, route: str) -> Path:
    """Only canonical archive paths; no query, traversal or external URL."""
    if not route.startswith("/") or "//" in route or any(
        part in {".", ".."} for part in route.split("/")
    ) or not re.fullmatch(r"/[a-zA-Z0-9/_.-]*", route):
        raise ValueError(f"Invalid local route: {route!r}")
    path = root / route.lstrip("/")
    return path / "index.html" if route.endswith("/") else path


def inventory(root: Path, *, include_pdfs: bool = False) -> tuple[Resource, ...]:
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap = ElementTree.parse(root / "sitemap.xml")
    routes = set()
    for loc in sitemap.findall("s:url/s:loc", namespace):
        url = loc.text or ""
        if not url.startswith(ORIGIN + "/"):
            raise ValueError(f"Noncanonical sitemap URL: {url!r}")
        routes.add(url.removeprefix(ORIGIN))
    if "/" not in routes:
        raise ValueError("Home page missing from sitemap")

    assets = set()
    for route in routes:
        parser = RuntimeReferences()
        parser.feed(local_file(root, route).read_text(encoding="utf-8"))
        if len(parser.paths) != 2 or {path.rsplit(".", 1)[-1] for path in parser.paths} != {"css", "js"}:
            raise ValueError(f"Runtime asset contract differs: {route}")
        assets.update(parser.paths)

    routes.update(assets)
    routes.update(("/sitemap.xml", "/site.webmanifest", "/feed.xml", "/research-index.json", "/llms.txt"))
    if (root / "publications.json").is_file():
        routes.add("/publications.json")
    if include_pdfs:
        index = json.loads((root / "research-index.json").read_text(encoding="utf-8"))
        for work in index["hasPart"]:
            url = work["encoding"]["contentUrl"]
            if not url.startswith(ORIGIN + "/pdf/"):
                raise ValueError(f"Noncanonical PDF URL: {url!r}")
            routes.add(url.removeprefix(ORIGIN))

    resources = tuple(Resource(route, local_file(root, route).read_bytes()) for route in sorted(routes))
    for item in resources:
        match = FINGERPRINT.fullmatch(item.route)
        if match and item.digest != match.group(1):
            raise ValueError(f"Local fingerprint mismatch: {item.route}")
    return resources


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch(resource: Resource) -> bytes:
    # A release-specific query key reduces stale cache reuse. It does not prove
    # that an intermediary honored the cache directives.
    url = f"{ORIGIN}{resource.route}?archive-check={resource.digest[:16]}"
    request = Request(url, headers={
        "Accept-Encoding": "identity",
        "Cache-Control": "no-cache",
        "User-Agent": "TakashiSatoArchiveReleaseCheck/1.0",
    })
    with build_opener(NoRedirect()).open(request, timeout=15) as response:
        if response.status != 200 or response.headers.get("Content-Encoding", "identity").lower() != "identity":
            raise ValueError("Unexpected HTTP response status or encoding")
        return response.read(len(resource.content) + 1)


def compare(resource: Resource, loader=fetch) -> Finding:
    try:
        served = loader(resource)
    except (OSError, URLError, ValueError) as exc:
        return Finding(resource.route, "unavailable", str(exc))
    if served != resource.content:
        return Finding(resource.route, "different", "Served bytes do not match checkout")
    return Finding(resource.route, "match")


def exit_status(findings: list[Finding]) -> int:
    states = {finding.state for finding in findings}
    # 0 = exact match; 1 = observed difference; 2 = incomplete verification.
    return 2 if "unavailable" in states else 1 if "different" in states else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdfs", action="store_true", help="Also compare preserved trilogy PDFs.")
    args = parser.parse_args()
    try:
        resources = inventory(ROOT, include_pdfs=args.pdfs)
    except (OSError, ValueError, KeyError, ElementTree.ParseError) as exc:
        print(f"Invalid local release checkout: {exc}", file=sys.stderr)
        return 2
    findings = [compare(resource) for resource in resources]
    for finding in findings:
        print(f"{finding.state:11} {finding.route} {finding.detail}".rstrip())
    result = exit_status(findings)
    print(f"Matched {sum(item.state == 'match' for item in findings)}/{len(findings)} resources.")
    return result


if __name__ == "__main__":
    raise SystemExit(main())
