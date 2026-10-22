#!/usr/bin/env python3
"""eottabom 봇 코멘트용 배지 SVG를 만든다.

글자를 폰트 대신 경로(path)로 그려 어느 환경에서나 같은 모양으로 보이게 한다.
배지 높이 18px, 대문자 높이 8px, 좌우 여백 8px 비율을 쓴다.
GitHub에서 align="absmiddle"로 놓으면 배지가 글자보다 약 1.4px 아래에 보여서, 캔버스 아래에 투명 여백 3px을 둬
배지를 글자 세로 가운데로 올린다(본문·굵은 제목은 오차 0.1px 이내, 22px 제목은 0.4px). 그래서 SVG 높이는 21px이다.

사용법:
    pip install fonttools
    python3 scripts/generate_badges.py
"""

from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
# 아래 여백을 넣은 배지는 img/badge/에 둔다. 예전 18px 배지(img/*.svg)는 이미 달린 코멘트가 쓰고 있어서 그대로 둔다.
OUT = Path(__file__).resolve().parent.parent / "img" / "badge"
HEIGHT = 18
BASELINE = 13
CAP_HEIGHT = 8
PADDING = 8
BOTTOM_PAD = 3

# name: (label, aria, style, light colors, dark colors)
# solid: (배경, 글자), outline: (테두리·글자)
BADGES = {
    "engine-claude": ("claude", "claude", "solid", ("#c15f3c", "#ffffff"), ("#d97757", "#ffffff")),
    "engine-codex": ("codex", "codex", "solid", ("#0d8a6a", "#ffffff"), ("#10a37f", "#ffffff")),
    "engine-gemini": ("gemini", "gemini", "solid", ("#1a73e8", "#ffffff"), ("#4285f4", "#ffffff")),
    "mode-review": ("review", "review", "outline", ("#57606a",), ("#8b949e",)),
    "mode-fix": ("fix", "fix", "outline", ("#57606a",), ("#8b949e",)),
    "mode-dev": ("dev", "dev", "outline", ("#57606a",), ("#8b949e",)),
    "verdict-pass": ("pass", "Pass", "solid", ("#0969da", "#ffffff"), ("#1f6feb", "#ffffff")),
    "verdict-suggest": ("suggest", "Suggest changes", "solid", ("#ffd33d", "#1f2328"), ("#d29922", "#0d1117")),
    "verdict-must-fix": ("must fix", "Must fix", "solid", ("#cf222e", "#ffffff"), ("#da3633", "#ffffff")),
    # 종합 평가: 판정·심각도(채움형), 코멘트 목록(테두리형)과 구분되도록 옅은 바탕에 진한 글자
    "assess-good": ("good", "Good", "solid", ("#dafbe1", "#116329"), ("#12361f", "#56d364")),
    "assess-warn": ("warn", "Warning", "solid", ("#fff1e5", "#953800"), ("#3d2410", "#f0883e")),
    "assess-bad": ("bad", "Bad", "solid", ("#ffebe9", "#82071e"), ("#42161a", "#ff7b72")),
    "status-running": ("running", "Running", "solid", ("#9a6700", "#ffffff"), ("#bb8009", "#ffffff")),
    "status-done": ("done", "Done", "solid", ("#1a7f37", "#ffffff"), ("#238636", "#ffffff")),
    "status-failed": ("failed", "Failed", "solid", ("#cf222e", "#ffffff"), ("#da3633", "#ffffff")),
    "high": ("High", "High severity", "solid", ("#cf222e", "#ffffff"), ("#da3633", "#ffffff")),
    "medium": ("Medium", "Medium severity", "solid", ("#ffd33d", "#1f2328"), ("#d29922", "#0d1117")),
    "low": ("Low", "Low severity", "solid", ("#0969da", "#ffffff"), ("#1f6feb", "#ffffff")),
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
    canvas = HEIGHT + BOTTOM_PAD
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{canvas}" '
            f'viewBox="0 0 {width} {canvas}" role="img" aria-label="{aria}">\n'
            f'  <title>{aria}</title>\n  {rect}\n  <path fill="{foreground}" d="{path}"/>\n</svg>\n')


def main():
    font = TTFont(FONT)
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (label, aria, style, light, dark) in BADGES.items():
        for theme, colors in (("light", light), ("dark", dark)):
            target = OUT / f"{name}-{theme}.svg"
            target.write_text(svg(font, label, aria, style, colors), encoding="utf-8")
            print(target.name)


if __name__ == "__main__":
    main()
