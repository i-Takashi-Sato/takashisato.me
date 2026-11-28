#!/usr/bin/env python3
"""Prepare a four-codepoint Medium author font from a pinned upstream OTF."""
from __future__ import annotations

import argparse
import base64
from hashlib import sha1, sha256
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen

from fontTools import subset
from fontTools.ttLib import TTFont

SOURCE_COMMIT = "9b0f1436e455d902de067a2501422e5dc71ad16b"
SOURCE_PATH = "Serif/SubsetOTF/JP/NotoSerifJP-Medium.otf"
SOURCE_BLOB = "686bd4acd04d5c8a7b7c024455d0a1bb5d03425e"
URL = f"https://raw.githubusercontent.com/notofonts/noto-cjk/{SOURCE_COMMIT}/{SOURCE_PATH}"
CODEPOINTS = set(map(ord, "佐藤貴士"))
FAMILY = "Takashi Name Serif"
PS_NAME = "TakashiNameSerif-Medium"


def verify_font(font: TTFont) -> None:
    if font["OS/2"].usWeightClass != 500:
        raise ValueError("Incorrect author font weight")
    if set(font.getBestCmap()) != CODEPOINTS:
        raise ValueError("Author font must cover exactly four codepoints")
    for table in font["cmap"].tables:
        if table.isUnicode() and set(table.cmap) - CODEPOINTS:
            raise ValueError("Unexpected Unicode cmap entry")


def prepare(data: bytes) -> tuple[bytes, str]:
    if sha1(f"blob {len(data)}".encode() + b"\x00" + data).hexdigest() != SOURCE_BLOB:
        raise ValueError("Upstream font does not match pinned Git blob")
    font = TTFont(BytesIO(data), recalcTimestamp=False)
    if font["OS/2"].usWeightClass != 500 or not CODEPOINTS <= set(font.getBestCmap()):
        raise ValueError("Upstream weight or codepoint coverage mismatch")
    copyrights = sorted({r.toUnicode() for r in font["name"].names if r.nameID == 0})
    if not copyrights:
        raise ValueError("Missing upstream copyright notice")
    options = subset.Options()
    options.name_IDs = ["*"]
    options.name_legacy = True
    options.name_languages = ["*"]
    options.recalc_timestamp = False
    sub = subset.Subsetter(options=options)
    sub.populate(unicodes=CODEPOINTS)
    sub.subset(font)
    # Rename the derivative instead of relying on an RFN exception. Preserve
    # original copyright, attribution and license metadata.
    replacements = {1: FAMILY, 2: "Medium", 3: PS_NAME + "-Serif2.003", 4: FAMILY + " Medium",
                    6: PS_NAME, 16: FAMILY, 17: "Medium", 18: FAMILY + " Medium",
                    20: PS_NAME, 21: FAMILY, 22: "Medium", 25: "TakashiNameSerif"}
    for record in font["name"].names:
        if record.nameID in replacements:
            record.string = replacements[record.nameID].encode(record.getEncoding(), errors="strict")
    if "CFF " in font:
        cff = font["CFF "].cff
        cff.fontNames = [PS_NAME]
        top = cff.topDictIndex[0]
        top.FamilyName = FAMILY
        top.FullName = FAMILY + " Medium"
        if hasattr(top, "FontName"):
            top.FontName = PS_NAME
    verify_font(font)
    font.flavor = None
    out = BytesIO()
    font.save(out, reorderTables=True)
    return out.getvalue(), "\n".join(copyrights)


def woff2(source: bytes) -> bytes:
    font = TTFont(BytesIO(source), recalcTimestamp=False)
    verify_font(font)
    font.flavor = "woff2"
    out = BytesIO()
    font.save(out, reorderTables=True)
    data = out.getvalue()
    with TTFont(BytesIO(data)) as check:
        verify_font(check)
    return data


ROOT = Path(__file__).resolve().parents[1]
SUBSET_SOURCE = ROOT / "src/fonts/TakashiNameSerif-Medium.otf"
SUBSET_SHA256 = "3a716316c099c1dd028e799146f72367fc5e9be4ab5f91279b66232d01c93c01"
WOFF2_SHA256 = "fcd03174884134e07fedbe5c8f361d37015b9b7c942a3c960e3c9687dee8b17f"
from src.archive.runtime_assets import NAME_FONT_PATH


def build_name_font() -> str:
    data = SUBSET_SOURCE.read_bytes()
    if sha256(data).hexdigest() != SUBSET_SHA256:
        raise ValueError("Committed author font source digest mismatch")
    payload = woff2(data)
    if sha256(payload).hexdigest() != WOFF2_SHA256:
        raise ValueError("Author font build is not byte-identical to the verified output")
    target = ROOT / NAME_FONT_PATH
    if target.exists() and target.read_bytes() != payload:
        raise ValueError("Immutable author font path contains different bytes")
    if not target.exists():
        target.write_bytes(payload)
    return NAME_FONT_PATH


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true", help="Reproduce the derivative from the pinned upstream file")
    parser.add_argument("--source", type=Path, help="Local pinned upstream OTF; otherwise fetch the exact commit")
    args = parser.parse_args()
    if not args.prepare:
        print(build_name_font())
        return
    if args.source:
        data = args.source.read_bytes()
    else:
        with urlopen(URL, timeout=60) as response:
            data = response.read(32 * 1024 * 1024 + 1)
        if len(data) > 32 * 1024 * 1024:
            raise ValueError("Upstream file exceeds acquisition bound")
    source, copyright_notice = prepare(data)
    payload = woff2(source)
    if payload != woff2(source):
        raise ValueError("Non-deterministic WOFF2")
    print("COPYRIGHT_B64=" + base64.b64encode(copyright_notice.encode()).decode())
    print("SOURCE_OTF_SHA256=" + sha256(source).hexdigest())
    print("SOURCE_OTF_B64=" + base64.b64encode(source).decode())
    print("NAME_WOFF2_SHA256=" + sha256(payload).hexdigest())
    print("NAME_WOFF2_B64=" + base64.b64encode(payload).decode())
    print(f"Medium (500), exactly 4 Unicode codepoints; OTF {len(source)}, WOFF2 {len(payload)} bytes")


if __name__ == "__main__":
    main()
