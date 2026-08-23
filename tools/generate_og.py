#!/usr/bin/env python3
"""Generate deterministic 1200×630 social cards for the research archive."""

from __future__ import annotations

import hashlib
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "og"
W, H = 1200, 630
PAPER = (5, 5, 5)
INK = (240, 240, 236)
SOFT = (164, 163, 156)
LINE = (55, 55, 55)
SIGNAL = (255, 91, 58)
SIGNAL_DARK = (166, 59, 40)

INSTRUMENT = ROOT / "tools" / "fonts" / "InstrumentSans-Variable.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

CARDS = {
    "home": {
        "label": "WORKFLOW-CENTRIC AI GOVERNANCE TRILOGY · v6.2",
        "title": "A role alone is not governance.",
        "subtitle": "Accountability lives in the sequence.",
        "mark": "INDEX",
        "accent": SIGNAL,
        "record": "DECISION ROUTING · GOVERNING CAPACITY · ACCOUNTABLE EXIT",
    },
    "papers": {
        "label": "THE PROPER ENDING INDEX · PAPER TRILOGY",
        "title": "Three papers.",
        "subtitle": "One institutional problem.",
        "mark": "I—III",
        "accent": SIGNAL,
        "record": "TAKASHI SATO · WORKING PAPERS · 23 AUGUST 2026",
    },
    "about": {
        "label": "AUTHOR RECORD · TAKASHI SATO",
        "title": "Takashi Sato",
        "subtitle": "Independent researcher · Sapporo, Japan",
        "mark": "TS",
        "accent": SIGNAL,
        "record": "AI GOVERNANCE · PROPER ENDING · AUTHORITY RETURN",
    },
    "part1": {
        "label": "WORKFLOW-CENTRIC AI GOVERNANCE TRILOGY · PART I",
        "title": "Workflow-Centric\nAI Governance",
        "subtitle": "A Typed Gate Contract for Accountable Human-AI Decisions",
        "mark": "I",
        "accent": SIGNAL,
        "record": "SSRN 5911063 · DOI 10.2139/SSRN.5911063 · v6.2",
    },
    "part2": {
        "label": "WORKFLOW-CENTRIC AI GOVERNANCE TRILOGY · PART II",
        "title": "Governing-\nCapacity Loss",
        "subtitle": "A Descriptive State Model with a Provisional Etiological Subtype",
        "mark": "II",
        "accent": SIGNAL,
        "record": "SSRN 5913703 · DOI 10.2139/SSRN.5913703 · v6.2",
    },
    "part3": {
        "label": "WORKFLOW-CENTRIC AI GOVERNANCE TRILOGY · PART III",
        "title": "From Governance Drift\nto Accountable Exit",
        "subtitle": "Proper Ending and Authority Return in AI-Assisted Institutions",
        "mark": "III",
        "accent": SIGNAL,
        "record": "SSRN 6066430 · DOI 10.2139/SSRN.6066430 · v6.2",
        "title_size": 56,
    },
}


def instrument(size: int, width: int = 100, weight: int = 400) -> ImageFont.FreeTypeFont:
    face = ImageFont.truetype(str(INSTRUMENT), size=size)
    face.set_variation_by_axes([width, weight])
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


def render(name: str, data: dict) -> Image.Image:
    image = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(image)
    rng = random.Random(int(hashlib.sha256(name.encode()).hexdigest()[:8], 16))
    accent = data["accent"]

    for _ in range(3400):
        x, y = rng.randrange(W), rng.randrange(H)
        value = rng.choice((0, 2, 3, 5))
        draw.point((x, y), fill=(value, value, value))

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    for radius, alpha in [(360, 7), (280, 9), (200, 11), (120, 14)]:
        glow_draw.ellipse((W - 110 - radius, -170 - radius, W - 110 + radius, -170 + radius), fill=(*accent, alpha))
    image = Image.alpha_composite(image.convert("RGBA"), glow).convert("RGB")
    draw = ImageDraw.Draw(image)

    draw.line((54, 78, 1146, 78), fill=LINE, width=1)
    draw.line((54, 548, 1146, 548), fill=LINE, width=1)
    draw.text((54, 41), data["label"], font=instrument(15, 88, 620), fill=accent)

    mark_face = instrument(162 if len(data["mark"]) < 4 else 86, 75, 620)
    mark_box = draw.textbbox((0, 0), data["mark"], font=mark_face)
    mark_width = mark_box[2] - mark_box[0]
    draw.text((1146 - mark_width, 105), data["mark"], font=mark_face, fill=SIGNAL_DARK)

    if name == "about":
        title_size = 108
    elif name.startswith("part"):
        title_size = data.get("title_size", 70)
    else:
        title_size = 88
    title_face = instrument(title_size, 76, 610)
    y = 126
    title_width = 840 if name == "home" else (900 if name.startswith("part") else 1010)
    line_step = round(title_size * .88)
    title = data["title"].upper() if name == "about" else data["title"]
    for line in wrap(draw, title, title_face, title_width):
        draw.text((54, y), line, font=title_face, fill=INK)
        y += line_step

    subtitle_face = instrument(22, 92, 430)
    subtitle_y = max(y + 26, 390)
    for line in wrap(draw, data["subtitle"], subtitle_face, 770)[:3]:
        draw.text((57, subtitle_y), line, font=subtitle_face, fill=SOFT)
        subtitle_y += 31

    draw.rectangle((54, 576, 66, 588), fill=accent)
    draw.text((83, 574), data["record"], font=mono(12), fill=SOFT)
    brand = "THE PROPER ENDING INDEX"
    brand_face = instrument(13, 86, 610)
    brand_box = draw.textbbox((0, 0), brand, font=brand_face)
    draw.text((1146 - (brand_box[2] - brand_box[0]), 574), brand, font=brand_face, fill=INK)
    return image


def render_icon(size: int, inverse: bool = False) -> Image.Image:
    scale = 4
    canvas = size * scale
    background = INK if inverse else PAPER
    foreground = PAPER if inverse else INK
    accent = SIGNAL
    image = Image.new("RGB", (canvas, canvas), background)
    draw = ImageDraw.Draw(image)
    inset_outer = round(canvas * .18)
    inset_inner = round(canvas * .30)
    width_outer = max(scale, round(canvas * .075))
    width_inner = max(scale, round(canvas * .055))
    draw.arc((inset_outer, inset_outer, canvas - inset_outer, canvas - inset_outer), 42, 318, fill=foreground, width=width_outer)
    draw.arc((inset_inner, inset_inner, canvas - inset_inner, canvas - inset_inner), 42, 318, fill=foreground, width=width_inner)
    cy = canvas // 2
    draw.line((round(canvas * .53), cy, round(canvas * .78), cy), fill=accent, width=max(scale, round(canvas * .045)))
    dot = round(canvas * .055)
    x = round(canvas * .79)
    draw.rectangle((x - dot, cy - dot, x + dot, cy + dot), fill=accent)
    return image.resize((size, size), Image.Resampling.LANCZOS)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in CARDS.items():
        image = render(name, data)
        image.save(OUT / f"{name}.jpg", "JPEG", quality=91, optimize=True, progressive=True, subsampling=0)
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
    render_icon(64).save(ROOT / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])


if __name__ == "__main__":
    main()
