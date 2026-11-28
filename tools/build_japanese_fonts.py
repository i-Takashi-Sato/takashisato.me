#!/usr/bin/env python3
"""Build pinned OFL Japanese subsets explicitly; normal site builds are offline."""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parents[1]
FONTS = ROOT / "assets/fonts"
RECORD = ROOT / "docs/japanese-fonts.json"
UPSTREAM = "5026800714d07231937d92eb4cceabf06e05d74e"
UI_TEXT = "佐藤貴士日本語の研究案内第一部／意思決定経路第二部統治能力第三部終了と権限返還検証範囲論文記述モデル反証条件英語概念根拠批判受付（）、。"
SPECS = {
    "JPUI": ("notosansjp", "NotoSansJP[wght].ttf", "cdd8f083c1f5928ff3361f8cda4d3fc9462cbe89", "1c9f43281b8f216c5461fe9ac729afbade7724e4", 500, 40_000),
    "JPText": ("notoserifjp", "NotoSerifJP[wght].ttf", "bd98d809e02880e32f20f1f2a91ef97854f52f57", "94d1bf7b52481343e2983fb7751e8b7abe1ea07b", (400, 500), 400_000),
}

def japanese(text):
    return {ord(ch) for ch in text if 0x3000 <= ord(ch) <= 0x30ff or 0x3400 <= ord(ch) <= 0x9fff or 0xff00 <= ord(ch) <= 0xffef}

def needed(name):
    if name == "JPUI":
        return japanese(UI_TEXT)
    text = (ROOT / "src/archive/pages.py").read_text(encoding="utf-8")
    start = text.index('id="japanese" lang="ja"')
    return japanese(text[start:text.index("</section>", start)]) | japanese(UI_TEXT)

def git_sha(data):
    return hashlib.sha1(f"blob {len(data)}".encode() + bytes([0]) + data).hexdigest()

def fetch(folder, filename, expected):
    url = f"https://raw.githubusercontent.com/google/fonts/{UPSTREAM}/ofl/{folder}/{quote(filename)}"
    with urlopen(url, timeout=60) as response:
        data = response.read()
    if git_sha(data) != expected:
        raise ValueError("Upstream blob mismatch: " + filename)
    return data

def sha(data):
    return hashlib.sha256(data).hexdigest()

def build():
    records = {}
    for name, (folder, filename, source_sha, license_sha, weight, limit) in SPECS.items():
        source = fetch(folder, filename, source_sha)
        license_data = fetch(folder, "OFL.txt", license_sha)
        font = TTFont(io.BytesIO(source), recalcTimestamp=False)
        font = instantiateVariableFont(font, {"wght": weight}, inplace=True)
        chars = needed(name)
        if not chars <= set(font.getBestCmap()):
            raise ValueError("Missing upstream glyphs: " + name)
        sub = subset.Subsetter()
        sub.populate(unicodes=chars)
        sub.subset(font)
        font.flavor = "woff2"
        font.save(FONTS / f"{name}.woff2")
        (FONTS / f"{name}-OFL.txt").write_bytes(license_data)
        data = (FONTS / f"{name}.woff2").read_bytes()
        if len(data) > limit:
            raise ValueError(f"Japanese font budget exceeded: {name} {len(data)}")
        records[name] = {
            "source": f"google/fonts@{UPSTREAM}/ofl/{folder}/{filename}",
            "source_git_blob_sha1": source_sha,
            "source_sha256": sha(source),
            "license_sha256": sha(license_data),
            "subset_sha256": sha(data),
            "subset_bytes": len(data),
            "required_codepoints": sorted(chars),
            "weight": weight,
        }
    RECORD.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    verify()

def verify():
    records = json.loads(RECORD.read_text(encoding="utf-8"))
    if set(records) != set(SPECS):
        raise ValueError("Unexpected Japanese font inventory")
    for name, (_, _, source_sha, license_sha, _, limit) in SPECS.items():
        record = records[name]
        path = FONTS / f"{name}.woff2"
        data = path.read_bytes()
        license_data = (FONTS / f"{name}-OFL.txt").read_bytes()
        if (record["source_git_blob_sha1"] != source_sha or git_sha(license_data) != license_sha
                or record["subset_sha256"] != sha(data) or record["license_sha256"] != sha(license_data)
                or len(data) != record["subset_bytes"] or len(data) > limit):
            raise ValueError("Japanese font provenance or byte budget mismatch: " + name)
        chars = needed(name)
        with TTFont(path) as font:
            if not chars <= set(font.getBestCmap()) or not chars <= set(record["required_codepoints"]):
                raise ValueError("Japanese text exceeds committed subset: " + name)
        print(f"{name}: {len(chars)} required characters; {len(data)} bytes; OFL and SHA-256 verified")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true", help="Rebuild from pinned public upstream fonts")
    build() if parser.parse_args().fetch else verify()
