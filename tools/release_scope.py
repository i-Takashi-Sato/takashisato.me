#!/usr/bin/env python3
"""Choose full checks unless the checked-out tree proves an editorial-only delta.

Archive QA, HTML validation, axe and baseline visual smoke always run.
This classifier selects only the additional expensive checks; it never
authorizes deployment. Unknown events, files, structures and errors are full.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit

HTML = frozenset({
    "index.html", "about.html", "colophon.html", "privacy.html", "security.html",
    "404.html", "publications/index.html", "papers/index.html",
    "papers/part1.html", "papers/part2.html", "papers/part3.html",
    "demo/index.html", "demo/altrion-part1.html", "demo/altrion-part2.html",
})
EDITORIAL_SOURCE = frozenset({
    "src/archive/model.py", "src/archive/layout.py",
    "src/archive/pages.py", "src/archive/publications.py",
})
EDITORIAL_DATA = frozenset({
    "research-index.json", "publications.json", "sitemap.xml",
    "feed.xml", "llms.txt", "humans.txt",
})
META_TEXT = frozenset({
    "description", "author", "og:title", "og:description",
    "twitter:title", "twitter:description",
})
SENSITIVE = frozenset({
    "script", "style", "svg", "math", "pre", "code", "textarea",
    "template", "noscript", "iframe", "object", "embed", "xmp",
    "plaintext", "title",
})


def safe_external_origin(value: str) -> tuple[str, str]:
    """Only same-origin HTTPS link destination updates can be editorial."""
    if not value.startswith("https://") or any(
        ch.isspace() or ord(ch) < 32 or ord(ch) == 127 for ch in value
    ):
        return ("literal", value)
    try:
        url = urlsplit(value)
        if url.hostname and not url.username and not url.password and url.port in (None, 443):
            return ("https-origin", url.netloc)
    except ValueError:
        pass
    return ("literal", value)


class Structure(HTMLParser):
    """Retain markup, security/resource attributes and active/raw content.

    Only ordinary prose, selected descriptive metadata, valid inline JSON-LD
    and existing HTTPS destinations on the same origin are abstracted.
    """
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.events = []
        self.sensitive = []
        self.jsonld = None

    def attributes(self, tag, attrs):
        values = dict(attrs)
        if len(values) != len(attrs):
            raise ValueError("duplicate HTML attribute")
        result = []
        for name, value in attrs:
            if value is not None and name == "href" and (
                tag == "a" or (tag == "link" and values.get("rel") == "me")
            ):
                value = safe_external_origin(value)
            if (
                tag == "meta" and name == "content"
                and (values.get("name") or values.get("property")) in META_TEXT
                and value is not None
            ):
                value = "DESCRIPTIVE-METADATA"
            result.append((name, value))
        return tuple(result)

    def handle_starttag(self, tag, attrs):
        self.events.append(("start", tag, self.attributes(tag, attrs)))
        if tag in SENSITIVE:
            self.sensitive.append(tag)
        if tag == "script":
            values = dict(attrs)
            if values.get("type") == "application/ld+json" and "src" not in values:
                self.jsonld = []

    def handle_startendtag(self, tag, attrs):
        self.events.append(("empty", tag, self.attributes(tag, attrs)))

    def handle_endtag(self, tag):
        if tag in SENSITIVE:
            if not self.sensitive or self.sensitive[-1] != tag:
                raise ValueError("unbalanced protected HTML content")
            self.sensitive.pop()
        if tag == "script" and self.jsonld is not None:
            value = json.loads("".join(self.jsonld))
            if not isinstance(value, (dict, list)):
                raise ValueError("invalid JSON-LD root")
            self.events.append(("jsonld",))
            self.jsonld = None
        self.events.append(("end", tag))

    def handle_data(self, data):
        if self.jsonld is not None:
            self.jsonld.append(data)
        elif self.sensitive:
            self.events.append(("protected-data", data))
        # Ordinary text may alter wrapping, hence baseline visual and axe run.

    def handle_comment(self, data):
        self.events.append(("comment", data))

    def handle_decl(self, decl):
        self.events.append(("declaration", decl))

    def handle_pi(self, data):
        self.events.append(("processing-instruction", data))

    def unknown_decl(self, data):
        self.events.append(("unknown-declaration", data))


def signature(content: str):
    parser = Structure()
    parser.feed(content)
    parser.close()
    if parser.sensitive or parser.jsonld is not None:
        raise ValueError("unfinished protected HTML content")
    return parser.events


def editorial_only(paths, read_pair):
    if not paths:
        return False
    source_changed = False
    output_changed = False
    for path in paths:
        if re.fullmatch(r"docs/[A-Za-z0-9_.-]+\.md", path):
            continue
        if path in EDITORIAL_SOURCE:
            source_changed = True
        elif path in HTML:
            old, new = read_pair(path)
            if signature(old) != signature(new):
                return False
            output_changed = True
        elif path in EDITORIAL_DATA:
            output_changed = True
        else:
            return False
    return not source_changed or output_changed


def git(*args):
    return subprocess.check_output(["git", *args], stderr=subprocess.PIPE)


def classify(base: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{40}", base or ""):
        return "full"
    try:
        git("merge-base", "--is-ancestor", base, "HEAD")
        raw = git("diff", "--raw", "-z", "--no-renames", "--no-ext-diff", base, "HEAD", "--")
        entries = raw.split(b"\0")
        if entries.pop() != b"" or len(entries) % 2:
            return "full"
        paths = []
        for header, path in zip(entries[::2], entries[1::2]):
            fields = header.split()
            if (
                len(fields) != 5 or fields[:2] != [b":100644", b"100644"]
                or fields[-1] != b"M"
            ):
                return "full"
            paths.append(path.decode("utf-8"))

        def read_pair(path):
            return tuple(git("show", f"{rev}:{path}").decode("utf-8") for rev in (base, "HEAD"))

        return "light" if editorial_only(paths, read_pair) else "full"
    except (OSError, subprocess.SubprocessError, UnicodeError, ValueError) as exc:
        print(f"Scope uncertain; full checks: {type(exc).__name__}", file=sys.stderr)
        return "full"


def self_test():
    a = '<html><head><meta name="description" content="old"></head><body><p>Old</p><a href="https://example.com/one">Link</a></body></html>'
    b = a.replace("old", "new").replace("Old", "New").replace("/one", "/two")
    assert editorial_only(["about.html", "src/archive/pages.py"], lambda _: (a, b))
    assert editorial_only(["docs/governance.md"], lambda _: (a, b))
    assert editorial_only(["research-index.json"], lambda _: (a, b))
    assert not editorial_only([], lambda _: (a, b))
    assert not editorial_only(["src/archive/pages.py"], lambda _: (a, b))
    assert not editorial_only(["assets/site.css", "about.html"], lambda _: (a, b))
    assert not editorial_only([".github/workflows/quality-gate.yml"], lambda _: (a, b))
    for changed in (
        b.replace("<p>", "<section>").replace("</p>", "</section>"),
        b.replace("https://example.com", "https://other.example"),
        b.replace("https://example.com/two", "javascript:alert(1)"),
        b.replace("https://example.com/two", "HTTPS-EXTERNAL:example.com"),
        b.replace('<p>', '<p style="color:red">'),
        b.replace("</head>", '<script>active()</script></head>'),
        b.replace("</head>", '<link rel="stylesheet" href="/new.css"></head>'),
        b.replace("</head>", '<meta http-equiv="refresh" content="1"></head>'),
        b.replace("</body>", '<a href="/new">Added</a></body>'),
    ):
        assert not editorial_only(["about.html"], lambda _: (a, changed))
    assert signature('<script type="application/ld+json">{"name":"A"}</script>') == signature('<script type="application/ld+json">{"name":"B"}</script>')
    for tag in ("script", "style", "svg", "pre", "title"):
        assert signature(f"<{tag}>a</{tag}>") != signature(f"<{tag}>b</{tag}>")
    assert classify("") == "full"
    assert classify("not-a-commit") == "full"
    # Exercise the actual raw Git diff and ancestry comparison, not just fixtures.
    previous = os.getcwd()
    with tempfile.TemporaryDirectory() as temp:
        try:
            os.chdir(temp)
            git("init", "--quiet")
            git("config", "user.name", "Scope test")
            git("config", "user.email", "scope-test@example.invalid")
            git("config", "commit.gpgsign", "false")
            Path("about.html").write_text(a, encoding="utf-8")
            git("add", "--", "about.html")
            git("commit", "--quiet", "-m", "Base fixture")
            base = git("rev-parse", "HEAD").decode().strip()
            Path("about.html").write_text(b, encoding="utf-8")
            git("add", "--", "about.html")
            git("commit", "--quiet", "-m", "Editorial fixture")
            assert classify(base) == "light"
            Path("about.html").write_text(b.replace("</body>", "<section>Added</section></body>"), encoding="utf-8")
            git("add", "--", "about.html")
            git("commit", "--quiet", "-m", "Structural fixture")
            assert classify(base) == "full"
            last = git("rev-parse", "HEAD").decode().strip()
            Path("new.html").write_text(a, encoding="utf-8")
            git("add", "--", "new.html")
            git("commit", "--quiet", "-m", "New-file fixture")
            assert classify(last) == "full"
        finally:
            os.chdir(previous)
    print("Release scope self-tests passed.", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    else:
        scope = classify(args.base)
        print(f"Release scope: {scope}", file=sys.stderr)
        print(f"scope={scope}")


if __name__ == "__main__":
    main()
