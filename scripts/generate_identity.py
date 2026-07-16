#!/usr/bin/env python3
"""Genera los assets de identidad de MEU en app/public/.

Piezas (decisión cerrada, sesión 2026-07-16):
  - Logo simplificado: M de Big Shoulders 900 en negativo
    (bloque tinta #111111, letra papel #F2EFE8, M al 84% de altura)
    -> favicon.svg, favicon.ico (16+32), apple-touch-icon.png (180)
  - Logo total: lockup "MAPA EUSKADI / UNDERGROUND" justificado a caja,
    negativo, centrado -> og.png (1200x630)

Reproducible: la fuente se descarga de google/fonts pineada a un commit.
Dependencias: fonttools, cairosvg, pillow, requests.
Uso: python scripts/generate_identity.py  (desde la raíz del repo)
"""

import io
import pathlib

import requests
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
import cairosvg
from PIL import Image, ImageDraw, ImageFont

# --- constantes del sistema visual (CERRADO) ---
PAPER = "#F2EFE8"
INK = "#111111"
PAPER_RGB = (242, 239, 232)
INK_RGB = (17, 17, 17)

GF_PIN = "26c5c976d82d50c24a8f0a7ac455e0a7c639c226"  # google/fonts main, 2026-07-16
FONT_URL = (
    "https://raw.githubusercontent.com/google/fonts/"
    f"{GF_PIN}/ofl/bigshoulders/BigShoulders%5Bopsz%2Cwght%5D.ttf"
)

OUT = pathlib.Path("app/public")


def get_font_instance() -> tuple[bytes, TTFont]:
    """Descarga Big Shoulders variable y la instancia a wght 900 / opsz 72."""
    raw = requests.get(FONT_URL, timeout=60)
    raw.raise_for_status()
    font = TTFont(io.BytesIO(raw.content))
    instantiateVariableFont(font, {"wght": 900, "opsz": 72}, inplace=True)
    buf = io.BytesIO()
    font.save(buf)
    return buf.getvalue(), font


def extract_m(font: TTFont):
    """Path SVG + bbox de la M."""
    glyphset = font.getGlyphSet()
    gname = font.getBestCmap()[ord("M")]
    glyph = glyphset[gname]
    pen = SVGPathPen(glyphset)
    glyph.draw(pen)
    bp = BoundsPen(glyphset)
    glyph.draw(bp)
    return pen.getCommands(), bp.bounds


def favicon_svg(path_d: str, bbox) -> str:
    """M negativa centrada al 84% de altura en viewBox 1000."""
    x0, y0, x1, y1 = bbox
    gw, gh = x1 - x0, y1 - y0
    s = 840 / gh
    tx = 500 - (x0 + gw / 2) * s
    ty = 500 + (y0 + gh / 2) * s
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">\n'
        f'<rect width="1000" height="1000" fill="{INK}"/>\n'
        f'<g transform="translate({tx:.1f},{ty:.1f}) scale({s:.5f},-{s:.5f})">'
        f'<path d="{path_d}" fill="{PAPER}"/></g>\n'
        "</svg>\n"
    )


def rasterize(svg: str, size: int) -> Image.Image:
    png = cairosvg.svg2png(
        bytestring=svg.encode(), output_width=size, output_height=size
    )
    return Image.open(io.BytesIO(png)).convert("RGBA")


def og_image(font_bytes: bytes) -> Image.Image:
    """Lockup MAPA EUSKADI / UNDERGROUND, negativo, centrado, 1200x630."""
    W, H, M, GAP = 1200, 630, 84, 40
    target = W - 2 * M

    def fitfont(text: str) -> ImageFont.FreeTypeFont:
        f = ImageFont.truetype(io.BytesIO(font_bytes), 100)
        bb = f.getbbox(text)
        return ImageFont.truetype(
            io.BytesIO(font_bytes), int(100 * target / (bb[2] - bb[0]))
        )

    im = Image.new("RGB", (W, H), INK_RGB)
    d = ImageDraw.Draw(im)
    lines = ["MAPA EUSKADI", "UNDERGROUND"]
    fonts = [fitfont(t) for t in lines]
    bbs = [f.getbbox(t) for f, t in zip(fonts, lines)]
    hs = [bb[3] - bb[1] for bb in bbs]
    y = (H - (sum(hs) + GAP)) // 2
    for t, f, bb, h in zip(lines, fonts, bbs, hs):
        d.text((M - bb[0], y - bb[1]), t, font=f, fill=PAPER_RGB)
        y += h + GAP
    return im


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    font_bytes, font = get_font_instance()
    path_d, bbox = extract_m(font)

    svg = favicon_svg(path_d, bbox)
    (OUT / "favicon.svg").write_text(svg)

    ico32 = rasterize(svg, 32)
    ico32.save(OUT / "favicon.ico", sizes=[(16, 16), (32, 32)])

    touch = rasterize(svg, 180).convert("RGB")  # iOS: sin transparencia
    touch.save(OUT / "apple-touch-icon.png")

    og_image(font_bytes).save(OUT / "og.png")

    for f in sorted(OUT.iterdir()):
        print(f"{f}  {f.stat().st_size} bytes")


if __name__ == "__main__":
    main()
