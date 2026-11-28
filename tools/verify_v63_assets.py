#!/usr/bin/env python3
"""Verify immutable v6.3 release inputs and preserved v6.2 PDFs.

Run after staging all four new binary inputs. Missing files fail closed.
This supplements the existing archive QA; it does not replace it.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs/releases/v6.3.json"

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)

def verify_file(record: dict) -> bytes:
    data = (ROOT / record["path"]).read_bytes()
    require(len(data) == record["bytes"], "Size mismatch: " + record["path"])
    require(digest(data) == record["sha256"], "SHA-256 mismatch: " + record["path"])
    return data

def main() -> None:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    require(record["version"] == "6.3", "Unexpected release version")
    require(len(record["pdfs"]) == 3, "Expected three current PDFs")
    require(len(record["preserved_pdfs"]) == 3, "Expected three preserved PDFs")
    for paper in record["pdfs"]:
        reader = PdfReader(io.BytesIO(verify_file(paper)))
        require(len(reader.pages) == paper["pages"], "Page count: " + paper["path"])
        first = reader.pages[0].extract_text() or ""
        require("Version 6.3" in first, "Version: " + paper["path"])
        require(paper["doi"] in first, "DOI: " + paper["path"])
    for old in record["preserved_pdfs"]:
        verify_file(old)
    archive = record["source_archive"]
    with ZipFile(io.BytesIO(verify_file(archive))) as z:
        entries = z.namelist()
        require(len(entries) == len(set(entries)) == archive["entries"], "Archive inventory")
        require(all(not PurePosixPath(n).is_absolute() and ".." not in PurePosixPath(n).parts for n in entries), "Unsafe archive path")
        checked = set()
        for line in z.read("SHA256SUMS").decode("utf-8").splitlines():
            checksum, path = line.split(maxsplit=1)
            path = path.lstrip("*").removeprefix("./")
            require(bool(re.fullmatch(r"[0-9a-f]{64}", checksum)), "Invalid checksum")
            require(path not in checked and path != "SHA256SUMS", "Duplicate checksum: " + path)
            require(digest(z.read(path)) == checksum, "Archive member mismatch: " + path)
            checked.add(path)
        require(len(checked) == archive["checksums"] and checked == set(entries) - {"SHA256SUMS"}, "Incomplete checksum manifest")
        for paper in record["pdfs"]:
            require(digest(z.read(paper["source_archive_path"])) == paper["source_archive_pdf_sha256"], "Archive PDF mismatch")
    print("PASS: 3 current SSRN PDFs, 3 preserved PDFs, and 153 archive member checksums.")

if __name__ == "__main__":
    main()
