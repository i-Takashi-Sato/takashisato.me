from __future__ import annotations

import math
import random
import re
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "og"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1200, 630

PALETTE = {
    "home": {"bg": (7, 8, 8), "mid": (32, 35, 36), "hi": (224, 219, 205), "accent": (207, 174, 102)},
    "papers": {"bg": (10, 9, 7), "mid": (50, 44, 34), "hi": (230, 220, 196), "accent": (205, 160, 80)},
    "part1": {"bg": (10, 6, 4), "mid": (72, 43, 19), "hi": (235, 202, 139), "accent": (230, 165, 72)},
    "part2": {"bg": (4, 8, 10), "mid": (42, 58, 62), "hi": (210, 224, 222), "accent": (176, 202, 204)},
    "part3": {"bg": (4, 3, 3), "mid": (36, 18, 20), "hi": (218, 208, 194), "accent": (150, 96, 80)},
    "about": {"bg": (9, 8, 6), "mid": (66, 56, 42), "hi": (240, 233, 216), "accent": (205, 174, 112)},
}
IVORY = (238, 232, 218)
STONE = (176, 168, 148)
RED = (214, 43, 39)


def font(paths: list[str], size: int) -> ImageFont.FreeTypeFont:
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)

SERIF = font([
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf",
], 54)
SERIF_S = font([
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf",
], 47)
SANS = font([
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
], 17)
SANS_M = font([
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
], 10)
SANS_XS = font([
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
], 9)


def render_pdf(path: str, page: int = 0, zoom: float = 1.5) -> Image.Image:
    doc = fitz.open(str(ROOT / path))
    pg = doc.load_page(page)
    pix = pg.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    doc.close()
    return img

PDF = {
    "p1_1": render_pdf("pdf/part1.pdf", 0, 1.3),
    "p1_3": render_pdf("pdf/part1.pdf", 2, 1.3),
    "p1_6": render_pdf("pdf/part1.pdf", 5, 1.3),
    "p2_1": render_pdf("pdf/part2.pdf", 0, 1.3),
    "p2_3": render_pdf("pdf/part2.pdf", 2, 1.3),
    "p3_1": render_pdf("pdf/part3.pdf", 0, 1.3),
    "p3_4": render_pdf("pdf/part3.pdf", 3, 1.3),
    "p3_5": render_pdf("pdf/part3.pdf", 4, 1.3),
    "p3_6": render_pdf("pdf/part3.pdf", 5, 1.3),
}


def crop_pdf(key: str, rel: tuple[float, float, float, float]) -> Image.Image:
    im = PDF[key]
    w, h = im.size
    box = (int(rel[0]*w), int(rel[1]*h), int(rel[2]*w), int(rel[3]*h))
    return im.crop(box)


def pdf_etch(key: str, rel: tuple[float, float, float, float], size: tuple[int, int], color: tuple[int, int, int], alpha: int) -> Image.Image:
    im = crop_pdf(key, rel)
    im.thumbnail(size, Image.Resampling.LANCZOS)
    gray = ImageOps.grayscale(im)
    gray = ImageEnhance.Contrast(gray).enhance(1.16)
    mask = gray.point(lambda p: int(max(0, 214 - p) * 255 / 214))
    mask = mask.point(lambda p: int(p * alpha / 255))
    layer = Image.new("RGBA", im.size, color + (0,))
    layer.putalpha(mask)
    return layer


def gradient_base(page: str) -> Image.Image:
    pal = PALETTE[page]
    im = Image.new("RGB", (W, H), pal["bg"])
    px = im.load()
    cx, cy = 0.78*W, 0.32*H
    for y in range(H):
        for x in range(W):
            dx = (x-cx)/W
            dy = (y-cy)/H
            glow = max(0.0, 1.0 - math.sqrt(dx*dx*2.1 + dy*dy*4.0))
            left = max(0.0, 1.0 - x/720)
            r = int(pal["bg"][0]*(1-glow*0.45) + pal["mid"][0]*(glow*0.45))
            g = int(pal["bg"][1]*(1-glow*0.45) + pal["mid"][1]*(glow*0.45))
            b = int(pal["bg"][2]*(1-glow*0.45) + pal["mid"][2]*(glow*0.45))
            if left > 0:
                r = int(r*(1-left*0.45)); g = int(g*(1-left*0.45)); b = int(b*(1-left*0.45))
            px[x, y] = (r, g, b)
    noise = Image.effect_noise((W, H), 28).convert("L")
    grain = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    grain.putalpha(noise.point(lambda p: max(0, min(18, int((p-118)*0.06+8)))))
    return Image.alpha_composite(im.convert("RGBA"), grain)


def track(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fnt, fill, spacing: float = 2.4):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + spacing


def type_block(im: Image.Image, section: str, title: list[str], body: list[str], meta: str) -> None:
    d = ImageDraw.Draw(im)
    x, y = 80, 96
    track(d, (x, y), section.upper(), SANS_M, PALETTE["papers"]["accent"] + (222,), 2.7)
    y = 170
    for line in title:
        f = SERIF if len(line) <= 25 else SERIF_S
        d.text((x, y), line, font=f, fill=IVORY)
        y += 56 if f == SERIF else 49
    d.line((x+2, y+12, x+318, y+12), fill=PALETTE["papers"]["accent"] + (150,), width=1)
    y += 40
    for line in body:
        d.text((x+2, y), line, font=SANS, fill=STONE)
        y += 27
    track(d, (x, 536), meta.upper(), SANS_XS, (172, 135, 77, 190), 1.9)


def frame(im: Image.Image) -> None:
    d = ImageDraw.Draw(im)
    c = (207, 174, 102, 52)
    d.rectangle((42, 38, W-42, H-38), outline=c, width=1)
    d.line((80, 38, 146, 38), fill=(207, 174, 102, 86), width=1)
    d.line((80, H-38, 146, H-38), fill=(207, 174, 102, 56), width=1)


def paste_layer(im: Image.Image, layer: Image.Image, xy: tuple[int, int], angle: float = 0) -> None:
    if angle:
        layer = layer.rotate(angle, Image.Resampling.BICUBIC, expand=True, fillcolor=(0, 0, 0, 0))
    im.alpha_composite(layer, xy)


def save(im: Image.Image, name: str) -> None:
    frame(im)
    out = OUT / f"{name}.jpg"
    im.convert("RGB").save(out, "JPEG", quality=86, optimize=True, progressive=True, subsampling=1)


def home():
    im = gradient_base("home")
    paste_layer(im, pdf_etch("p1_1", (.05, .05, .60, .18), (410, 112), PALETTE["home"]["hi"], 18), (704, 120), -2)
    paste_layer(im, pdf_etch("p3_1", (.05, .05, .60, .18), (410, 112), PALETTE["home"]["hi"], 16), (680, 438), -1)
    d = ImageDraw.Draw(im, "RGBA")
    cx, cy, r = 900, 298, 204
    d.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(4, 5, 5, 205), outline=(207, 174, 102, 82), width=1)
    d.arc((cx-r+45, cy-r+60, cx+r-42, cy+r-30), 206, 322, fill=(220, 216, 200, 36), width=1)
    d.line((948, 78, 910, 510), fill=(242, 225, 174, 112), width=1)
    type_block(im, "Home / Black Cenotaph", ["AI Governance", "Research Archive"], ["The archive of judgment,", "record, and ending."], "Boullée / Pantheon light / PDF inscriptions")
    save(im, "home")


def papers():
    im = gradient_base("papers")
    d = ImageDraw.Draw(im, "RGBA")
    panels = [(648, 112, 786, 482, "p1_1", "I"), (822, 112, 960, 482, "p2_1", "II"), (996, 112, 1134, 482, "p3_1", "III")]
    for x1, y1, x2, y2, key, roman in panels:
        d.rounded_rectangle((x1, y1, x2, y2), radius=4, fill=(8, 7, 6, 190), outline=(207, 174, 102, 70), width=1)
        paste_layer(im, pdf_etch(key, (.04, .05, .72, .90), (x2-x1-34, y2-y1-82), PALETTE["papers"]["hi"], 50), (x1+17, y1+28))
        for j in range(4):
            yy = y1 + 98 + j*52
            d.line((x1+22, yy, x2-26, yy), fill=(230, 220, 196, 28), width=1)
        d.text((x1+18, y2-40), f"PART {roman}", font=SANS_XS, fill=(207, 174, 102, 190))
    d.line((786, 297, 822, 297), fill=(207, 174, 102, 42), width=1)
    d.line((960, 297, 996, 297), fill=(207, 174, 102, 42), width=1)
    type_block(im, "Papers / Material Atlas", ["Three papers.", "One index."], ["A Warburg-like atlas of", "architecture, decay, and ending."], "Warburg / Judd / PDF title-page etchings")
    save(im, "papers")


def part1():
    im = gradient_base("part1")
    paste_layer(im, pdf_etch("p1_3", (.06, .08, .60, .78), (300, 420), PALETTE["part1"]["hi"], 50), (740, 86))
    paste_layer(im, pdf_etch("p1_6", (.04, .12, .68, .42), (390, 210), PALETTE["part1"]["hi"], 16), (664, 366), -1.5)
    d = ImageDraw.Draw(im, "RGBA")
    cx, cy = 892, 306
    for rr, a in [(190, 86), (140, 62), (94, 42)]:
        d.ellipse((cx-rr, cy-rr, cx+rr, cy+rr), outline=(230, 165, 72, a), width=1)
    d.line((cx-208, cy-40, cx+208, cy-28), fill=(230, 165, 72, 165), width=2)
    d.line((cx, cy-82, cx, cy+150), fill=(230, 165, 72, 112), width=1)
    for sx, sy in [(cx-144, cy-36), (cx+144, cy-32)]:
        d.line((sx, sy, sx-42, cy+42), fill=(230, 165, 72, 68), width=1)
        d.line((sx, sy, sx+42, cy+42), fill=(230, 165, 72, 68), width=1)
        d.arc((sx-62, cy+25, sx+62, cy+70), 0, 180, fill=(230, 165, 72, 140), width=2)
    for i, x in enumerate([735, 808, 975, 1050]):
        d.rectangle((x, 92, x+7, 438), fill=(0, 0, 0, 125), outline=(230, 165, 72, 74), width=1)
        d.text((x-7, 452), f"G{i+1}", font=SANS_XS, fill=(230, 165, 72, 205))
    type_block(im, "Part I / Arbitration", ["Workflow-Centric", "AI Governance"], ["A four-gate apparatus for", "human arbitration and record."], "Weighing / Antikythera / Figure 1 as etched logic")
    save(im, "part1")


def part2():
    im = gradient_base("part2")
    paste_layer(im, pdf_etch("p2_3", (.04, .15, .66, .92), (430, 430), PALETTE["part2"]["hi"], 24), (704, 126))
    paste_layer(im, pdf_etch("p2_1", (.04, .05, .70, .34), (420, 210), PALETTE["part2"]["hi"], 18), (664, 84))
    d = ImageDraw.Draw(im, "RGBA")
    random.seed(202)
    for x in range(650, 1120, 28):
        drift = random.randint(-9, 9); ww = random.randint(3, 7)
        d.rectangle((x+drift, 82, x+drift+ww, 536), fill=(0, 0, 0, random.randint(15, 30)))
    layers = [(338, 350, 0, .36), (362, 377, -10, .42), (388, 405, 4, .48), (416, 435, -14, .54), (448, 468, 8, .60), (482, 502, -6, .66)]
    for y1, y2, dx, tone in layers:
        left = 670 + random.randint(-6, 8); right = 1110 - random.randint(0, 26)
        col = tuple(int(58*tone + v*(1-tone)) for v in (74, 88, 90))
        d.polygon([(left, y1), (right, y1+1), (right+dx, y2), (left+random.randint(-5,6), y2+1)], fill=col+(178,), outline=(220, 226, 220, 40))
    fracture = [(806, 218), (792, 270), (807, 324), (798, 382), (820, 444), (812, 506)]
    d.line(fracture, fill=(238, 242, 232, 76), width=1)
    for i in range(10):
        y = 205 + i*17 + random.randint(-2, 2)
        d.line((714+random.randint(-6,14), y, 1040-i*9-random.randint(0,42), y+random.randint(-1,1)), fill=(230, 236, 226, 42), width=1)
    type_block(im, "Part II / Forecasting Failure", ["Forecasting", "Failure"], ["A structurally sound system", "settling into low energy."], "Friedrich logic / entropy text / ribbed pressure")
    save(im, "part2")


def part3():
    im = gradient_base("part3")
    paste_layer(im, pdf_etch("p3_4", (.04, .05, .68, .52), (340, 330), PALETTE["part3"]["hi"], 12), (712, 104), -.5)
    paste_layer(im, pdf_etch("p3_5", (.48, .44, .98, .74), (300, 210), PALETTE["part3"]["hi"], 11), (820, 300), 1)
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle((648, 82, 1116, 538), radius=5, fill=(0,0,0,150), outline=(150,96,80,14), width=1)
    d.rectangle((704, 138, 1060, 294), fill=(38, 22, 22, 24))
    d.rectangle((706, 322, 1060, 482), fill=(8,8,8,66))
    d.rectangle((1006, 182, 1018, 194), fill=RED+(255,))
    d.line((690, 320, 1070, 320), fill=(230,224,206,16), width=1)
    type_block(im, "Part III / Silent Failure", ["Detecting Silent", "Governance Failure"], ["A near-black field where", "only one signal remains."], "Rothko / Maya Lin / GDI")
    save(im, "part3")


def about():
    im = gradient_base("about")
    paste_layer(im, pdf_etch("p3_6", (.04, .66, .70, .96), (430, 280), PALETTE["about"]["hi"], 20), (700, 270), -1)
    for key, y, a in [("p1_1", 104, 11), ("p2_1", 150, 10), ("p3_1", 198, 10)]:
        paste_layer(im, pdf_etch(key, (.04, .05, .70, .16), (390, 88), PALETTE["about"]["hi"], a), (680+(y-100)//2, y))
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle((680, 248, 1080, 452), radius=5, fill=(17,15,12,126), outline=(207,174,102,38), width=1)
    random.seed(43)
    for i in range(9):
        y = 286 + i*15
        d.line((720, y, 1038-random.randint(0,100), y+random.randint(-1,1)), fill=(207,174,102,31), width=1)
    # Draw a clean signature-like mark from vector strokes; avoids typed-name portrait logic.
    d.line((94,270,180,225,300,252,430,214,520,250), fill=IVORY+(225,), width=3)
    d.arc((84,198,250,310), 170, 345, fill=IVORY+(210,), width=3)
    d.line((268,252,346,252,455,306,536,278), fill=IVORY+(225,), width=3)
    d.arc((430,198,590,325), 108, 292, fill=IVORY+(210,), width=3)
    d.text((86, 323), "Takashi Sato", font=SANS_XS, fill=(218,208,188,92))
    track(d, (80, 96), "ABOUT / THE SCRIBE", SANS_M, (207,174,102,220), 2.7)
    d.line((82, 360, 418, 360), fill=(207,174,102,150), width=1)
    d.text((82, 388), "Not a portrait of authority,", font=SANS, fill=STONE)
    d.text((82, 416), "but the trace of judgment.", font=SANS, fill=STONE)
    track(d, (80, 536), "SIGNATURE / PDF TRACE / AUTHORIAL WITNESS", SANS_XS, (172,135,77,190), 1.9)
    save(im, "about")


def ensure_meta(path: str, image_name: str) -> None:
    p = ROOT / path
    html = p.read_text(encoding="utf-8")
    url = f"https://takashisato.me/assets/og/{image_name}.jpg"
    tags = f'''  <meta property="og:image" content="{url}" />\n  <meta property="og:image:width" content="1200" />\n  <meta property="og:image:height" content="630" />\n  <meta name="twitter:card" content="summary_large_image" />\n  <meta name="twitter:image" content="{url}" />'''
    html = re.sub(r'\n\s*<meta property="og:image"[^>]*>\s*', '\n', html)
    html = re.sub(r'\n\s*<meta property="og:image:width"[^>]*>\s*', '\n', html)
    html = re.sub(r'\n\s*<meta property="og:image:height"[^>]*>\s*', '\n', html)
    html = re.sub(r'\n\s*<meta name="twitter:image"[^>]*>\s*', '\n', html)
    html = re.sub(r'<meta name="twitter:card" content="[^"]*"\s*/>', '<meta name="twitter:card" content="summary_large_image" />', html)
    if 'property="og:site_name"' in html:
        html = re.sub(r'(\n\s*<meta property="og:site_name"[^>]*>\s*)', r'\1\n' + tags, html, count=1)
    elif 'property="og:url"' in html:
        html = re.sub(r'(\n\s*<meta property="og:url"[^>]*>\s*)', r'\1\n' + tags, html, count=1)
    else:
        html = html.replace('</head>', tags + '\n</head>')
    p.write_text(html, encoding="utf-8")


def main():
    home(); papers(); part1(); part2(); part3(); about()
    ensure_meta("index.html", "home")
    ensure_meta("papers/index.html", "papers")
    ensure_meta("papers/part1.html", "part1")
    ensure_meta("papers/part2.html", "part2")
    ensure_meta("papers/part3.html", "part3")
    ensure_meta("about.html", "about")

if __name__ == "__main__":
    main()
