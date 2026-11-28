"""Content-addressed production assets; public legacy aliases stay frozen."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNTIME_NAMES = ("site.css", "site.js")
FONT_NAMES = ("fonts/InterVariable.woff2", "fonts/Newsreader-Variable.woff2", "fonts/MeaCulpa.woff2")
OG_NAMES = tuple(f"og/{name}.jpg" for name in ("home", "papers", "part1", "part2", "part3", "about", "archive"))
ASSET_NAMES = RUNTIME_NAMES + FONT_NAMES + OG_NAMES
MANIFEST = ROOT / "src/archive/asset-manifest.json"

# Freeze the exact legacy bytes of the last public base, a311ddf. These
# are still served and byte-audited; a new release never overwrites them.
LEGACY_DIGESTS = {
    "fonts/InterVariable.woff2": "dd8a4575be9806105ac3decd02805cd2782fe7c05abb02c582316bc436ce03ae",
    "fonts/MeaCulpa.woff2": "b3907e33232e370842e8a07b773bcb6b5c3743eb19a7308bdccf08bd145b39d1",
    "fonts/Newsreader-Variable.woff2": "01817351be3edfc1714fe6d60ddea6a22a169a5ebd033b50c7f9495e5d9c386a",
    "og/about.jpg": "641941fb8f67bfae864c3f2263a941c8cca364fdd4bdd360992a213e99b79920",
    "og/archive.jpg": "0ce9ae8f00a9a606a6c56ed7cf20ba5e21df7ce9a89b0d94479b5538a41d1a2d",
    "og/home.jpg": "7f0efa913b496058cfad1138f6250332ab61fae5d610def5ddf9c28fd20e8a4f",
    "og/papers.jpg": "acac0cde4fe41d0b696ce85b2830d7a0321da0f0b75244f10c98b2338345ff8f",
    "og/part1.jpg": "da10a3aca24c53eb3cdde3d5cd78e6093a5e048cd17643adfdea57aec898174c",
    "og/part2.jpg": "51e707c2455f7ce724e626a58ae4699cc60aed2da649778f39650b666a7ed495",
    "og/part3.jpg": "4ec77a7d13953d480f59f27d79e993a8615ca26aa3cb8796fe7dea90d3e8cd19",
    "site.css": "081c6efc7928450d57de32431128f29db8bf828d0c658189918b7b1cd9c1e64e",
    "site.js": "3167074d934c075877dc01b5c874cc147f84eca53208185f8dc65c3151f8ed7c"
}


def fingerprint_path(name: str, data: bytes) -> str:
    if name not in ASSET_NAMES:
        raise ValueError(f"Unknown production asset: {name}")
    stem, suffix = name.rsplit(".", 1)
    return f"assets/{stem}.{sha256(data).hexdigest()}.{suffix}"


def read_manifest() -> dict[str, str]:
    value = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if set(value) != set(ASSET_NAMES):
        raise ValueError("Production asset manifest inventory mismatch")
    for name, path in value.items():
        if path != fingerprint_path(name, (ROOT / path).read_bytes()):
            raise ValueError(f"Production asset digest mismatch: {name}")
    return value


def asset_path(name: str) -> str:
    if name not in ASSET_NAMES:
        raise ValueError(f"Unknown production asset: {name}")
    return read_manifest()[name]


def asset_url(name: str) -> str:
    return "/" + asset_path(name)


def runtime_path(name: str) -> str:
    if name not in RUNTIME_NAMES:
        raise ValueError(f"Unknown runtime bundle: {name}")
    return asset_path(name)


def runtime_url(name: str) -> str:
    return "/" + runtime_path(name)


def publish_assets(payloads: dict[str, bytes]) -> None:
    manifest = read_manifest()
    for name, data in payloads.items():
        path = fingerprint_path(name, data)
        target = ROOT / path
        if target.exists() and target.read_bytes() != data:
            raise ValueError(f"Immutable asset mismatch: {target}")
        if not target.exists():
            target.write_bytes(data)
        manifest[name] = path
    MANIFEST.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
