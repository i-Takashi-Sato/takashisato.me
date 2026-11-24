#!/usr/bin/env python3
"""Deterministic social cards and icon assets for the platinum research identity.

The generator uses canonical scholarly metadata; it never changes the papers.
Run after build_site.py to keep SVG, raster icons, and social cards aligned.
"""

from __future__ import annotations

import sys
import base64
import io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

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
        "label": "AI GOVERNANCE / TAKASHI SATO",
        "title": "A role alone is not governance.",
        "subtitle": "Accountability lives in the sequence.",
        "index": "00",
        "record": "THREE WORKING PAPERS · AI GOVERNANCE",
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


# Canonical paths; the open boundary and continuing line survive every medium.
BOUNDARY = "M11 59V12H55V30M55 52V59H11"
CONTINUITY = "M29 41H64"
GRAPHITE = (72, 72, 72)


def mark(draw: ImageDraw.ImageDraw, x: int, y: int, size: int, inverse: bool = False, optical: bool = False) -> None:
    """Square-capped strokes on one coordinate grid; strengthen the tiny raster variant."""
    k = size / 72
    ink = WHITE if inverse else INK
    trace = PLATINUM if inverse else GRAPHITE
    half = 4 if optical else 3.25
    def rect(a,b,c,d,fill):
        draw.rectangle((round(x+a*k),round(y+b*k),round(x+c*k),round(y+d*k)),fill=fill)
    for x0,y0,x1,y1 in ((11,12,11,59),(11,12,55,12),(55,12,55,30),(55,52,55,59),(11,59,55,59)):
        rect(x0-half,y0-half,x1+half,y1+half,ink)
    rect(29-half,41-half,64+half,41+half,trace)


def svg_mark(*, tile: bool, dark: bool = False, adaptive: bool = False) -> str:
    background = "#141414" if dark else "#F8F8F7"
    ink = "#F8F8F7" if dark else "#141414"
    trace = "#A6A8AB" if dark else "#484848"
    style = "<style>@media(prefers-color-scheme:dark){.paper{fill:#141414}.boundary{stroke:#F8F8F7}.continuity{stroke:#A6A8AB}}</style>" if adaptive else ""
    rect = f'<rect class="paper" width="72" height="72" fill="{background}"/>' if tile else ""
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 72 72" role="img" aria-labelledby="t">'
            '<title id="t">The Proper Ending Index — open boundary</title>' + style + rect
            + f'<path class="boundary" d="{BOUNDARY}" fill="none" stroke="{ink}" stroke-width="6.5" stroke-linecap="square" stroke-linejoin="miter"/>'
            + f'<path class="continuity" d="{CONTINUITY}" fill="none" stroke="{trace}" stroke-width="6.5" stroke-linecap="square"/></svg>\n')


def material(name: str, size: tuple[int, int], strength: float = .55) -> Image.Image:
    source = Image.open(ROOT / "assets" / name).convert("RGB")
    source = ImageOps.fit(source, size, method=Image.Resampling.LANCZOS)
    return Image.blend(Image.new("RGB", size, INK), source, strength)


def instrument(draw: ImageDraw.ImageDraw, part: int, box: tuple[int, int, int, int]) -> None:
    """The same three conceptual motifs used by Index, Papers and paper entrances.
    No axis, magnitude, empirical observation, or verified transition is implied.
    """
    x0, y0, x1, y1 = box
    w, h = x1-x0, y1-y0
    xy = lambda x,y: (round(x0+w*x), round(y0+h*y))
    def line(points, fill=PLATINUM, width=4):
        draw.line([xy(x,y) for x,y in points], fill=fill, width=width)
    def diamond(x,y,r):
        draw.line([xy(x,y-r),xy(x+r*h/w,y),xy(x,y+r),xy(x-r*h/w,y),xy(x,y-r)],fill=WHITE,width=4)
    if part == 1:
        line([(.26,.83),(.26,.18),(.74,.18),(.74,.83)])
        line([(.50,.11),(.50,.91)], DARK_RULE, 3)
        line([(.10,.62),(.90,.62)], WHITE, 4)
        diamond(.50,.18,.045)
    elif part == 2:
        line([(.08,.20),(.92,.20)])
        line([(.08,.80),(.92,.80)], DARK_RULE)
        for a,b in ((.08,.18),(.23,.31),(.36,.45),(.66,.71),(.76,.81),(.86,.92)):
            line([(a,.49),(b,.49)])
        line([(.44,.49),(.59,.38)], WHITE, 4)
        line([(.53,.52),(.65,.65)])
        line([(.49,.43),(.51,.68)], DARK_RULE)
    else:
        cx,cy=xy(.50,.50)
        radius=min(w,h)*.43
        for fraction,color in ((1,(127,127,127)),(.72,PLATINUM),(.45,WHITE)):
            r=radius*fraction
            draw.ellipse((round(cx-r),round(cy-r),round(cx+r),round(cy+r)),outline=color,width=4)
        line([(.08,.50),(.40,.50)],WHITE)
        line([(.60,.50),(.92,.50)],WHITE)
        diamond(.50,.50,.052)


def geometry(draw: ImageDraw.ImageDraw, selected: str) -> None:
    """Shared conceptual instruments, not a data visualization."""
    labels = ("I / CASE", "II / INSTITUTION", "III / EXIT")
    selected_part = {"I": 1, "II": 2, "III": 3}.get(selected)
    if selected_part:
        draw.text((824,96),labels[selected_part-1],font=face(26,640),fill=WHITE)
        draw.line((824,143,1152,143),fill=DARK_RULE,width=1)
        instrument(draw, selected_part,(824,175,1152,480))
        draw.text((824,525),"CONCEPTUAL INSTRUMENT",font=face(18,600),fill=WHITE)
    else:
        for i,y in enumerate((88,240,392),1):
            draw.text((824,y),labels[i-1],font=face(22,640),fill=WHITE)
            instrument(draw,i,(824,y+30,1152,y+130))
            draw.line((824,y+139,1152,y+139),fill=DARK_RULE,width=1)
    draw.text((824,568),"INTERPRETIVE · NOT EMPIRICAL",font=face(17,530),fill=PLATINUM)


def render_card(name: str, card: dict[str, str]) -> Image.Image:
    author = name == "about"
    image = material("author-paper.webp",(W,H),.62) if author else Image.new("RGB",(W,H),PAPER)
    if not author:
        image.paste(material("research-metal.webp",(W-784,H),.72),(784,0))
    draw = ImageDraw.Draw(image)
    ink, soft, rule = (WHITE,PLATINUM,DARK_RULE) if author else (INK,SOFT,RULE)
    mark(draw,65,26,48,author)
    draw.text((124,40),card["label"],font=face(21,650),fill=soft)
    draw.line((68,90,1132 if author else 744,90),fill=rule,width=1)
    draw.line((68,540,1132 if author else 744,540),fill=rule,width=1)

    max_width = 1040 if author else 676
    size = 100 if author else 76 if name in ("home","papers") else 65
    title = "Takashi Sato" if author else card["title"]
    # Editorial line breaks preserve phrases rather than leaving a single orphan word.
    preferred = {
        "papers": ("Three papers.", "One institutional problem."),
        "part1": ("Workflow-Centric", "AI Governance"),
        "part3": ("From Governance Drift", "to Accountable Exit"),
    }.get(name)
    if preferred and " ".join(preferred) != title:
        preferred = None  # Future title revisions still use the generic measured wrapper.
    while size >= 40:
        title_font = face(size,580)
        title_lines = list(preferred) if preferred else wrap(draw,title,title_font,max_width)
        if (len(title_lines) <= 3 and len(title_lines)*round(size*1.10) <= 262
                and all(draw.textbbox((0,0),line,font=title_font)[2] <= max_width for line in title_lines)):
            break
        size -= 2
    else:
        raise ValueError(f"{name}: title exceeds the card")
    y = 142
    for line in title_lines:
        if draw.textbbox((0,0),line,font=title_font)[2] > max_width:
            raise ValueError(f"{name}: title overflows")
        draw.text((68,y),line,font=title_font,fill=ink)
        y += round(size*1.10)

    subtitle_size = 25
    while subtitle_size >= 17:
        subtitle_font = face(subtitle_size,440)
        subtitle_lines = wrap(draw,card["subtitle"],subtitle_font,max_width)
        if len(subtitle_lines) <= 3 and max(y+32,330)+len(subtitle_lines)*round(subtitle_size*1.42) < 530:
            break
        subtitle_size -= 1
    else:
        raise ValueError(f"{name}: subtitle exceeds the card")
    y = max(y+32,330)
    for line in subtitle_lines:
        draw.text((70,y),line,font=subtitle_font,fill=soft)
        y += round(subtitle_size*1.42)

    draw.text((68,551),"THE PROPER ENDING INDEX",font=face(22,680),fill=ink)
    domain = "takashisato.me"
    right = 1132 if author else 744
    domain_font = face(19,570)
    draw.text((right-draw.textlength(domain,font=domain_font),554),domain,font=domain_font,fill=soft)
    draw.text((68,585),card["record"],font=face(17,480),fill=soft)
    if author:
        # Signature remains exclusive to the author page, not redistributed in cards.
        mark(draw,940,278,170,True)
    else:
        geometry(draw,card["index"])
    return image


def favicon_master() -> Image.Image:
    """Recovered January 2026 personal T mark; retain its original brush geometry."""
    with Image.open(ROOT / "assets/favicon-source-20260117.png") as original:
        mask = original.convert("L").point(lambda v: max(0, min(255, round((v-8)*255/247))))
    bounds = mask.point(lambda v: 255 if v > 18 else 0).getbbox()
    if bounds is None:
        raise ValueError("empty supplied favicon mark")
    return mask.crop(bounds)


def icon(size: int, inverse: bool = False, maskable: bool = False) -> Image.Image:
    """Restore the supplied mark; optical weight adjustment only at tiny raster sizes."""
    mask = favicon_master()
    if size <= 32:
        mask = mask.filter(ImageFilter.MaxFilter(15 if size <= 16 else 7))
    width = max(512, size*4)
    side = round(width * (.51 if maskable else .83 if size <= 32 else .70))
    factor = side / max(mask.size)
    mask = mask.resize(tuple(max(1,round(n*factor)) for n in mask.size),Image.Resampling.LANCZOS)
    bg = INK if inverse else PAPER
    ink = WHITE if inverse else INK
    image = Image.new("RGB",(width,width),bg)
    image.paste(ink,((width-mask.width)//2,(width-mask.height)//2),mask)
    return image.resize((size,size),Image.Resampling.LANCZOS)


def personal_favicon_svg(adaptive: bool = False, dark: bool = False) -> str:
    """Self-contained raster-based SVG wrapper, not a new vector drawing."""
    def encoded(inverse):
        buffer = io.BytesIO()
        icon(128,inverse).save(buffer,"PNG",optimize=True)
        return "data:image/png;base64,"+base64.b64encode(buffer.getvalue()).decode("ascii")
    style = '<style>.dark{display:none}@media(prefers-color-scheme:dark){.light{display:none}.dark{display:inline}}</style>' if adaptive else ""
    def layer(inverse, cls):
        return f'<image class="{cls}" width="128" height="128" href="{encoded(inverse)}"/>'
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" role="img" aria-labelledby="t">'
            '<title id="t">Takashi Sato — personal T mark</title>'+style
            +(layer(False,"light")+layer(True,"dark") if adaptive else layer(dark,"mark"))+'</svg>\n')


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, card in CARDS.items():
        render_card(name, card).save(OUT / f"{name}.jpg", "JPEG", quality=86, optimize=True, progressive=True, subsampling=0)

    (ROOT / "assets/brand-mark.svg").write_text(svg_mark(tile=False),encoding="utf-8")
    (ROOT / "favicon.svg").write_text(personal_favicon_svg(adaptive=True),encoding="utf-8")
    (ROOT / "favicon-dark.svg").write_text(personal_favicon_svg(dark=True),encoding="utf-8")
    icon(512,maskable=True).save(ROOT / "maskable-512x512.png","PNG",optimize=True)
    icon_specs = {
        "android-chrome-192x192.png": (192, False),
        "android-chrome-512x512.png": (512, False),
        "apple-touch-icon.png": (180, False),
        "favicon-16x16.png": (16, False),
        "favicon-32x32.png": (32, False),
        "favicon-96x96.png": (96, False),
        "favicon-16x16-dark.png": (16, True),
        "favicon-32x32-dark.png": (32, True),
    }
    for filename, (size, inverse) in icon_specs.items():
        icon(size, inverse).save(ROOT / filename, "PNG", optimize=True)
    icon(64).save(ROOT / "favicon.ico",format="ICO",sizes=[(16,16),(32,32),(48,48),(64,64)],append_images=[icon(n) for n in (16,32,48)])


if __name__ == "__main__":
    main()
