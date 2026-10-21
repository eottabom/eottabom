#!/usr/bin/env python3
"""eottabom 봇 코멘트용 배지 SVG를 만든다.

글자를 폰트 대신 경로(path)로 그려 어느 환경에서나 같은 모양으로 보이게 한다.
기존 배지(high, medium, low, engine-*)와 같은 높이 18px, 대문자 높이 8px, 좌우 여백 8px 비율을 쓴다.

사용법:
    pip install fonttools
    python3 scripts/generate_badges.py
"""

from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
OUT = Path(__file__).resolve().parent.parent / "img"
HEIGHT = 18
BASELINE = 13
CAP_HEIGHT = 8
PADDING = 8

# name: (label, aria, style, light colors, dark colors)
# solid: (배경, 글자), outline: (테두리·글자)
BADGES = {
    "engine-antigravity": ("antigravity", "antigravity", "solid", ("#1a73e8", "#ffffff"), ("#4285f4", "#ffffff")),
    "status-running": ("running", "Running", "solid", ("#9a6700", "#ffffff"), ("#bb8009", "#ffffff")),
    "status-done": ("done", "Done", "solid", ("#1a7f37", "#ffffff"), ("#238636", "#ffffff")),
    "status-failed": ("failed", "Failed", "solid", ("#cf222e", "#ffffff"), ("#da3633", "#ffffff")),
    "high-outline": ("High", "High severity", "outline", ("#cf222e",), ("#f85149",)),
    "medium-outline": ("Medium", "Medium severity", "outline", ("#9a6700",), ("#d29922",)),
    "low-outline": ("Low", "Low severity", "outline", ("#0969da",), ("#4493f8",)),
}


def text_path(font, text):
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    scale = CAP_HEIGHT / font["OS/2"].sCapHeight
    pen = SVGPathPen(glyph_set, ntos=lambda value: f"{value:.2f}".rstrip("0").rstrip("."))
    x = 0.0
    for char in text:
        name = cmap[ord(char)]
        glyph = glyph_set[name]
        glyph.draw(TransformPen(pen, (scale, 0, 0, -scale, PADDING + x, BASELINE)))
        x += glyph.width * scale
    return pen.getCommands(), x


def svg(font, label, aria, style, colors):
    path, text_width = text_path(font, label)
    width = round(text_width + PADDING * 2)
    if style == "solid":
        background, foreground = colors
        rect = f'<rect x="0.5" y="0.5" width="{width - 1}" height="{HEIGHT - 1}" rx="8.5" fill="{background}"/>'
    else:
        (foreground,) = colors
        rect = (f'<rect x="0.5" y="0.5" width="{width - 1}" height="{HEIGHT - 1}" rx="8.5" '
                f'fill="none" stroke="{foreground}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{HEIGHT}" '
            f'viewBox="0 0 {width} {HEIGHT}" role="img" aria-label="{aria}">\n'
            f'  <title>{aria}</title>\n  {rect}\n  <path fill="{foreground}" d="{path}"/>\n</svg>\n')


def main():
    font = TTFont(FONT)
    for name, (label, aria, style, light, dark) in BADGES.items():
        for theme, colors in (("light", light), ("dark", dark)):
            target = OUT / f"{name}-{theme}.svg"
            target.write_text(svg(font, label, aria, style, colors), encoding="utf-8")
            print(target.name)


if __name__ == "__main__":
    main()
