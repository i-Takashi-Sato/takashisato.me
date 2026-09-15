#!/usr/bin/env python3
"""Generate deterministic 1200×630 social cards from the research identity."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.archive.model import PAPERS_BY_SLUG, VERSION

OUT = ROOT / "assets" / "og"
W, H = 1200, 630
SURFACE = (8, 8, 8)
INK = (242, 240, 233)
SOFT = (180, 177, 170)
RULE = (48, 48, 48)
SIGNAL = (89, 117, 255)
BRONZE = (215, 191, 140)
ICE = (168, 198, 210)
COPPER = (207, 129, 105)

INTER = ROOT / "assets/fonts/InterVariable.woff2"
NEWSREADER = ROOT / "assets/fonts/Newsreader-Variable.woff2"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

def paper_record(slug: str) -> str:
    paper = PAPERS_BY_SLUG[slug]
    return f"SSRN {paper['ssrn']} · DOI {paper['doi'].upper()} · v{VERSION}"

CARDS = {
    "home": {
        "label": "AI GOVERNANCE RESEARCH ARCHIVE · WORKFLOW-CENTRIC TRILOGY",
        "title": "A role alone is not governance.",
        "subtitle": "Accountability lives in the sequence.",
        "mark": "INDEX",
        "accent": SIGNAL,
        "record": "DECISION ROUTING · GOVERNING CAPACITY · ACCOUNTABLE EXIT",
    },
    "papers": {
        "label": "THE PROPER ENDING INDEX · WORKING PAPERS",
        "title": "Three papers.",
        "subtitle": "One institutional problem.",
        "mark": "I—III",
        "accent": SIGNAL,
        "record": "TAKASHI SATO · v6.2 · 23 AUGUST 2026",
    },
    "about": {
        "label": "AUTHOR RECORD · TAKASHI SATO",
        "title": "Takashi Sato",
        "subtitle": "Independent AI governance researcher · Sapporo, Japan",
        "mark": "TS",
        "accent": SIGNAL,
        "record": "AI GOVERNANCE · PROPER ENDING · AUTHORITY RETURN",
    },
    "part1": {
        "label": "WORKFLOW-CENTRIC AI GOVERNANCE TRILOGY · PART I",
        "title": "Workflow-Centric\nAI Governance",
        "subtitle": PAPERS_BY_SLUG["part1"]["subtitle"],
        "mark": "I",
        "accent": BRONZE,
        "record": paper_record("part1"),
    },
    "part2": {
        "label": "WORKFLOW-CENTRIC AI GOVERNANCE TRILOGY · PART II",
        "title": "Governing-\nCapacity Loss",
        "subtitle": PAPERS_BY_SLUG["part2"]["subtitle"],
        "mark": "II",
        "accent": ICE,
        "record": paper_record("part2"),
    },
    "part3": {
        "label": "WORKFLOW-CENTRIC AI GOVERNANCE TRILOGY · PART III",
        "title": "From Governance Drift\nto Accountable Exit",
        "subtitle": PAPERS_BY_SLUG["part3"]["subtitle"],
        "mark": "III",
        "accent": COPPER,
        "record": paper_record("part3"),
        "title_size": 56,
    },
}

def inter(size: int, weight: int = 400, optical: int = 24) -> ImageFont.FreeTypeFont:
    face = ImageFont.truetype(str(INTER), size=size)
    face.set_variation_by_axes([optical, weight])
    return face

def newsreader(size: int, weight: int = 350, optical: int = 72) -> ImageFont.FreeTypeFont:
    face = ImageFont.truetype(str(NEWSREADER), size=size)
    face.set_variation_by_axes([weight, optical])
    return face

def mono(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(MONO, size=size)

def wrap(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if draw.textbbox((0, 0), candidate, font=face)[2] <= width or not current:
                current = candidate
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines

def background(accent: tuple[int, int, int]) -> Image.Image:
    image = Image.new("RGB", (W, H), SURFACE)
    px = image.load()
    ax, ay = 1030, 65
    for y in range(H):
        for x in range(W):
            distance = ((x - ax) ** 2 + (y - ay) ** 2) ** 0.5
            glow = max(0.0, 1.0 - distance / 650.0) * 0.10
            line = 0.016 if (x % 96 == 0 or y % 96 == 0) else 0.0
            px[x, y] = tuple(min(255, round(SURFACE[i] + accent[i] * glow + 255 * line)) for i in range(3))
    return image

def render(name: str, data: dict) -> Image.Image:
    accent = data["accent"]
    image = background(accent)
    draw = ImageDraw.Draw(image)
    draw.line((54, 78, 1146, 78), fill=RULE, width=1)
    draw.line((54, 548, 1146, 548), fill=RULE, width=1)
    draw.text((54, 41), data["label"], font=inter(14, 640, 20), fill=accent)

    mark_face = newsreader(170 if len(data["mark"]) < 4 else 92, 300, 72)
    box = draw.textbbox((0, 0), data["mark"], font=mark_face)
    mark_width = box[2] - box[0]
    muted = tuple(round(channel * .28) for channel in accent)
    draw.text((1146 - mark_width, 105), data["mark"], font=mark_face, fill=muted)

    title_size = data.get("title_size", 70 if name.startswith("part") else 88)
    if name == "about":
        title_size = 104
    title_face = newsreader(title_size, 340, 72)
    y = 126
    width = 840 if name == "home" else (900 if name.startswith("part") else 1010)
    step = round(title_size * .86)
    for line in wrap(draw, data["title"], title_face, width):
        draw.text((54, y), line, font=title_face, fill=INK)
        y += step

    subtitle_face = inter(21, 430, 20)
    subtitle_y = max(y + 26, 390)
    for line in wrap(draw, data["subtitle"], subtitle_face, 790)[:3]:
        draw.text((57, subtitle_y), line, font=subtitle_face, fill=SOFT)
        subtitle_y += 31

    draw.rectangle((54, 576, 66, 588), fill=accent)
    draw.text((83, 574), data["record"], font=mono(12), fill=SOFT)
    brand = "THE PROPER ENDING INDEX"
    brand_face = inter(12, 630, 18)
    brand_box = draw.textbbox((0, 0), brand, font=brand_face)
    draw.text((1146 - (brand_box[2] - brand_box[0]), 574), brand, font=brand_face, fill=INK)
    return image

def render_icon(size: int, inverse: bool = False) -> Image.Image:
    scale = 4
    canvas = size * scale
    background_color = INK if inverse else SURFACE
    foreground = SURFACE if inverse else INK
    image = Image.new("RGB", (canvas, canvas), background_color)
    draw = ImageDraw.Draw(image)
    outer = round(canvas * .18)
    inner = round(canvas * .30)
    draw.arc((outer, outer, canvas - outer, canvas - outer), 42, 318, fill=foreground, width=max(scale, round(canvas * .075)))
    draw.arc((inner, inner, canvas - inner, canvas - inner), 42, 318, fill=foreground, width=max(scale, round(canvas * .055)))
    cy = canvas // 2
    draw.line((round(canvas * .53), cy, round(canvas * .78), cy), fill=SIGNAL, width=max(scale, round(canvas * .045)))
    dot = round(canvas * .055)
    x = round(canvas * .79)
    draw.rectangle((x - dot, cy - dot, x + dot, cy + dot), fill=SIGNAL)
    return image.resize((size, size), Image.Resampling.LANCZOS)

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in CARDS.items():
        render(name, data).save(OUT / f"{name}.jpg", "JPEG", quality=91, optimize=True, progressive=True, subsampling=0)
    icon_specs = {
        "android-chrome-192x192.png": (192, False),
        "android-chrome-512x512.png": (512, False),
        "apple-touch-icon.png": (180, False),
        "favicon-16x16.png": (16, False),
        "favicon-32x32.png": (32, False),
        "favicon-16x16-dark.png": (16, True),
        "favicon-32x32-dark.png": (32, True),
    }
    for filename, (size, inverse) in icon_specs.items():
        render_icon(size, inverse).save(ROOT / filename, "PNG", optimize=True)
    render_icon(64).save(ROOT / "favicon.ico", format="ICO", sizes=[(16,16),(32,32),(48,48),(64,64)])

if __name__ == "__main__":
    main()
