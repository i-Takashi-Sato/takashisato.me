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
PAPER = (242, 239, 232)
INK = (23, 23, 21)
SOFT = (91, 87, 80)
LINE = (204, 198, 187)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_ITALIC = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

CARDS = {
    "home": {
        "label": "WORKFLOW-CENTRIC AI GOVERNANCE TRILOGY · v6.2",
        "title": "A role alone is not governance.",
        "subtitle": "Accountability lives in the sequence.",
        "mark": "INDEX",
        "accent": (159, 67, 42),
        "record": "DECISION ROUTING · GOVERNING CAPACITY · ACCOUNTABLE EXIT",
    },
    "papers": {
        "label": "THE PROPER ENDING INDEX · PAPER TRILOGY",
        "title": "Three papers.",
        "subtitle": "One institutional problem.",
        "mark": "I—III",
        "accent": (159, 67, 42),
        "record": "TAKASHI SATO · WORKING PAPERS · 23 AUGUST 2026",
    },
    "about": {
        "label": "AUTHOR RECORD · TAKASHI SATO",
        "title": "Takashi Sato",
        "subtitle": "Independent researcher · Sapporo, Japan",
        "mark": "TS",
        "accent": (159, 67, 42),
        "record": "AI GOVERNANCE · PROPER ENDING · AUTHORITY RETURN",
    },
    "part1": {
        "label": "WORKFLOW-CENTRIC AI GOVERNANCE TRILOGY · PART I",
        "title": "Workflow-Centric\nAI Governance",
        "subtitle": "A Typed Gate Contract for Accountable Human-AI Decisions",
        "mark": "I",
        "accent": (154, 77, 40),
        "record": "SSRN 5911063 · DOI 10.2139/SSRN.5911063 · v6.2",
    },
    "part2": {
        "label": "WORKFLOW-CENTRIC AI GOVERNANCE TRILOGY · PART II",
        "title": "Governing-\nCapacity Loss",
        "subtitle": "A Descriptive State Model with a Provisional Etiological Subtype",
        "mark": "II",
        "accent": (54, 91, 105),
        "record": "SSRN 5913703 · DOI 10.2139/SSRN.5913703 · v6.2",
    },
    "part3": {
        "label": "WORKFLOW-CENTRIC AI GOVERNANCE TRILOGY · PART III",
        "title": "From Governance Drift\nto Accountable Exit",
        "subtitle": "Proper Ending and Authority Return in AI-Assisted Institutions",
        "mark": "III",
        "accent": (122, 65, 59),
        "record": "SSRN 6066430 · DOI 10.2139/SSRN.6066430 · v6.2",
        "title_size": 56,
    },
}


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)


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

    for _ in range(4600):
        x, y = rng.randrange(W), rng.randrange(H)
        value = rng.choice((-7, -5, 4, 6))
        base = PAPER[0] + value
        draw.point((x, y), fill=(base, base - 3, base - 8))

    draw.ellipse((815, -245, 1325, 265), fill=tuple(round(PAPER[i] * .89 + accent[i] * .11) for i in range(3)))
    draw.line((72, 74, 1128, 74), fill=LINE, width=1)
    draw.line((72, 548, 1128, 548), fill=LINE, width=1)
    draw.line((850, 74, 850, 548), fill=LINE, width=1)

    draw.text((72, 38), data["label"], font=font(SANS_BOLD, 15), fill=accent, spacing=4)
    draw.text((887, 105), data["mark"], font=font(SERIF_ITALIC, 126 if len(data["mark"]) < 4 else 74), fill=accent)
    draw.text((889, 330), "THE PROPER\nENDING INDEX", font=font(SANS_BOLD, 18), fill=INK, spacing=8)
    draw.text((889, 432), "TAKASHI SATO\nSAPPORO · JAPAN", font=font(MONO, 12), fill=SOFT, spacing=7)

    title_face = font(SERIF, data.get("title_size", 63 if name.startswith("part") else 70))
    y = 122
    for line in wrap(draw, data["title"], title_face, 710):
        draw.text((72, y), line, font=title_face, fill=INK)
        y += 76 if name.startswith("part") else 83

    subtitle_face = font(SANS, 22)
    y += 14
    for line in wrap(draw, data["subtitle"], subtitle_face, 700)[:3]:
        draw.text((75, y), line, font=subtitle_face, fill=SOFT)
        y += 32

    draw.rectangle((72, 573, 84, 585), fill=accent)
    draw.text((100, 570), data["record"], font=font(MONO, 13), fill=SOFT)
    return image


def render_icon(size: int, inverse: bool = False) -> Image.Image:
    scale = 4
    canvas = size * scale
    background = PAPER if inverse else INK
    foreground = INK if inverse else PAPER
    accent = (159, 67, 42)
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
