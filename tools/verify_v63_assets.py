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
    # Verify the exact preserved citation bytes against the previous Git tree.
    historical_citations = {
        "part1.bib": "5885f81d463567fa8706fc9b038c0be8ceb85af7",
        "part1.json": "de51241102505359991e2185e9bed5726743211b",
        "part1.ris": "c82d64d2bcacec9ea5427984794e5e6faab8f767",
        "part2.bib": "a5820ac3ee4800116ce3a13301761443550721a6",
        "part2.json": "ce3072663264e7cd598ef048237277afc48d5015",
        "part2.ris": "2f5c33392947bfde956d9336d459a5634b496dbe",
        "part3.bib": "6507457e8af295c01d9f5b79c38f2a041a84d8b8",
        "part3.json": "523d4835cdf4f5a810d6566c5e61eedd33a39c63",
        "part3.ris": "241b2c102711d44465bc0c1f3a3ea372fc8429a8",
    }
    for name, expected in historical_citations.items():
        payload = (ROOT / "citations/v6.2" / name).read_bytes()
        actual = hashlib.sha1(f"blob {len(payload)}".encode() + bytes([0]) + payload).hexdigest()
        require(actual == expected, "Preserved citation changed: " + name)
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
    print("PASS: 3 current SSRN PDFs, 3 preserved PDFs, 9 preserved citations, and 153 archive member checksums.")

if __name__ == "__main__":
    main()
