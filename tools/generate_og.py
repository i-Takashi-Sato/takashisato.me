#!/usr/bin/env python3
"""Deterministic social cards and icon assets for the platinum research identity.

The generator uses canonical scholarly metadata; it never changes the papers.
Run after build_site.py to keep SVG, raster icons, and social cards aligned.
"""

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
PAPER = (248, 248, 247)         # #F8F8F7
INK = (20, 20, 20)              # #141414
SOFT = (72, 72, 72)             # readable neutral auxiliary copy
PLATINUM = (166, 168, 171)      # #A6A8AB
RULE = (212, 212, 211)
DARK_RULE = (94, 94, 94)
WHITE = (246, 246, 245)
FONT = ROOT / "assets/fonts/InterVariable.woff2"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

CARDS = {
    "home": {
        "label": "INDEPENDENT RESEARCH / TAKASHI SATO",
        "title": "A role alone is not governance.",
        "subtitle": "Accountability lives in the sequence.",
        "index": "00",
        "record": "DECISION ROUTING · CAPACITY · ACCOUNTABLE EXIT",
    },
    "papers": {
        "label": "THE PROPER ENDING INDEX / RESEARCH SERIES",
        "title": "Three papers. One institutional problem.",
        "subtitle": "Three distinct inquiries; no universal decision score.",
        "index": "I–III",
        "record": "WORKFLOW-CENTRIC AI GOVERNANCE TRILOGY",
    },
    "about": {
        "label": "AUTHOR RECORD / INDEPENDENT RESEARCH",
        "title": "Takashi Sato",
        "subtitle": "AI governance · Sapporo, Japan",
        "index": "TS",
        "record": "ORCID · SSRN · GOOGLE SCHOLAR",
    },
    "part1": {
        "label": "WORKFLOW-CENTRIC AI GOVERNANCE / PART I",
        "title": PAPERS_BY_SLUG["part1"]["title"],
        "subtitle": PAPERS_BY_SLUG["part1"]["subtitle"],
        "index": "I",
        "record": f"SSRN {PAPERS_BY_SLUG['part1']['ssrn']} · DOI {PAPERS_BY_SLUG['part1']['doi']} · v{VERSION}",
    },
    "part2": {
        "label": "WORKFLOW-CENTRIC AI GOVERNANCE / PART II",
        "title": PAPERS_BY_SLUG["part2"]["title"],
        "subtitle": PAPERS_BY_SLUG["part2"]["subtitle"],
        "index": "II",
        "record": f"SSRN {PAPERS_BY_SLUG['part2']['ssrn']} · DOI {PAPERS_BY_SLUG['part2']['doi']} · v{VERSION}",
    },
    "part3": {
        "label": "WORKFLOW-CENTRIC AI GOVERNANCE / PART III",
        "title": PAPERS_BY_SLUG["part3"]["title"],
        "subtitle": PAPERS_BY_SLUG["part3"]["subtitle"],
        "index": "III",
        "record": f"SSRN {PAPERS_BY_SLUG['part3']['ssrn']} · DOI {PAPERS_BY_SLUG['part3']['doi']} · v{VERSION}",
    },
}


def face(size: int, weight: int = 450) -> ImageFont.FreeTypeFont:
    try:
        font = ImageFont.truetype(str(FONT), size=size)
        font.set_variation_by_axes([24, weight])
        return font
    except (OSError, ValueError):
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size=size)


def mono(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(MONO, size=size)


def wrap(draw: ImageDraw.ImageDraw, txt: str, font: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in txt.split("\n"):
        line = ""
        for word in paragraph.split():
            trial = (line + " " + word).strip()
            if not line or draw.textbbox((0, 0), trial, font=font)[2] <= width:
                line = trial
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
    return lines


def geometry(draw: ImageDraw.ImageDraw, selected: str) -> None:
    """Three abstract, non-empirical diagrams, grounded in the public series questions."""
    draw.line((784, 82, 784, 555), fill=DARK_RULE, width=1)
    top = (150, 291, 432)
    for i, y in enumerate(top, 1):
        number = ["I / CASE", "II / INSTITUTION", "III / EXIT"][i - 1]
        draw.text((823, y - 45), number, font=face(16, 640), fill=PLATINUM)
        line = WHITE if selected in ("00", "I–III", "TS", ("I", "II", "III")[i-1]) else DARK_RULE
        if i == 1:
            draw.line((831, y, 938, y), fill=line, width=2)
            draw.line((938, y, 967, y-24), fill=line, width=2)
            draw.line((967, y-24, 1050, y-24, 1050, y, 1130, y), fill=line, width=2)
        elif i == 2:
            for x0, x1 in ((831, 893), (922, 972), (1001, 1130)):
                draw.line((x0, y, x1, y), fill=line, width=2)
            draw.ellipse((967, y-5, 977, y+5), outline=PLATINUM, width=2)
        else:
            draw.line((831, y+25, 831, y-20, 973, y-20, 973, y+12), fill=line, width=2)
            draw.line((940, y+12, 1130, y+12), fill=PLATINUM, width=4)
            draw.ellipse((966, y+5, 980, y+19), outline=PLATINUM, width=3)


def render_card(name: str, card: dict[str, str]) -> Image.Image:
    image = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(image)
    draw.rectangle((784, 0, W, H), fill=INK)
    draw.line((68, 82, 744, 82), fill=RULE, width=1)
    draw.line((68, 546, 744, 546), fill=RULE, width=1)
    draw.text((68, 45), card["label"], font=face(16, 650), fill=SOFT)

    title = card["title"]
    max_width = 650
    size = 76 if name in ("home", "papers", "about") else 61
    title_lines: list[str] = []
    while size >= 43:
        title_lines = wrap(draw, title, face(size, 580), max_width)
        if len(title_lines) <= 3 and (len(title_lines) * round(size * 1.05)) <= 260:
            break
        size -= 3
    y = 143
    for line in title_lines[:3]:
        draw.text((68, y), line, font=face(size, 580), fill=INK)
        y += round(size * 1.06)

    subtitle = card["subtitle"]
    subtitle_size = 22
    while subtitle_size >= 17:
        subtitle_lines = wrap(draw, subtitle, face(subtitle_size, 440), 640)
        if len(subtitle_lines) <= 2:
            break
        subtitle_size -= 1
    y = max(y + 35, 398)
    for line in subtitle_lines[:2]:
        draw.text((70, y), line, font=face(subtitle_size, 440), fill=SOFT)
        y += 34

    draw.line((68, 562, 115, 562), fill=PLATINUM, width=3)
    draw.text((68, 578), "THE PROPER ENDING INDEX", font=face(13, 680), fill=INK)
    draw.text((68, 599), card["record"], font=face(11, 480), fill=SOFT)

    geometry(draw, card["index"])
    draw.text((824, 563), "THREE DISTINCT RESEARCH QUESTIONS", font=face(13, 570), fill=WHITE)
    draw.text((824, 591), "INTERPRETIVE GEOMETRY · NOT EMPIRICAL", font=face(11, 500), fill=PLATINUM)
    return image


def icon(size: int, inverse: bool = False) -> Image.Image:
    """Rasterize the exact 'open boundary / continuing line' identity from brand-mark.svg."""
    scale = max(4, 320 // size)
    width = size * scale
    image = Image.new("RGB", (width, width), INK if inverse else PAPER)
    draw = ImageDraw.Draw(image)
    ink = PAPER if inverse else INK
    factor = width / 72.0
    xy = lambda x, y: (round(x*factor), round(y*factor))
    points = [xy(11, 59), xy(11, 12), xy(55, 12), xy(55, 30)]
    draw.line(points, fill=ink, width=max(2, round(5*factor)), joint="curve")
    draw.line([xy(55, 52), xy(55, 59), xy(11, 59)], fill=ink, width=max(2, round(5*factor)))
    draw.line([xy(29, 41), xy(67, 41)], fill=PLATINUM, width=max(2, round(5*factor)))
    return image.resize((size, size), Image.Resampling.LANCZOS)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, card in CARDS.items():
        render_card(name, card).save(OUT / f"{name}.jpg", "JPEG", quality=86, optimize=True, progressive=True, subsampling=0)

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
        icon(size, inverse).save(ROOT / filename, "PNG", optimize=True)
    icon(64).save(ROOT / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])


if __name__ == "__main__":
    main()
