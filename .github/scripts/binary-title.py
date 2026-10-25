"""Combine two github-gravity renders into one two-row binary title.

The gravity action renders a single text line and uses its own glyph paths as collision obstacles.
This script keeps those exact glyph paths (so the falling blocks land on what is drawn), recolors
every digit (ones highlighted, zeros muted) and appends the glyphs of a second render below.

Usage: binary-title.py <gravity-svg> <second-row-svg> <light|dark>
"""
import re
import sys

ROWS = ("01001010 01100101 01100110", "01100110 01110010 01111001")
PALETTE = {
    "light": {"0": "#8c959f", "1": "#16a34a"},
    "dark": {"0": "#6e7681", "1": "#3fb950"},
}
ROW_GAP = 64
GLYPH_GROUP = re.compile(r'\n\s*<g transform="translate\(([\d.]+), ([\d.]+)\) scale\(3\)">(.*?)</g>', re.S)
GLYPH_PATH = re.compile(r'<path d="([^"]*)" fill="[^"]*" />')


def read_glyphs(svg, path):
    match = GLYPH_GROUP.search(svg)
    if match is None:
        sys.exit(f"{path}: glyph group not found; github-gravity output format changed")
    paths = GLYPH_PATH.findall(match.group(3))
    return match, [d for d in paths if d]


def recolor(glyphs, row, palette):
    digits = row.replace(" ", "")
    if len(glyphs) != len(digits):
        sys.exit(f"expected {len(digits)} glyphs for '{row}', found {len(glyphs)}")
    return "\n    ".join(f'<path d="{d}" fill="{palette[ch]}" />' for d, ch in zip(glyphs, digits))


def main(main_path, second_path, theme):
    palette = PALETTE[theme]
    svg = open(main_path, encoding="utf-8").read()
    match, first = read_glyphs(svg, main_path)
    _, second = read_glyphs(open(second_path, encoding="utf-8").read(), second_path)
    x, y = match.group(1), float(match.group(2))
    groups = (
        f'\n  <g transform="translate({x}, {y}) scale(3)">\n    {recolor(first, ROWS[0], palette)}\n  </g>'
        f'\n  <g transform="translate({x}, {y + ROW_GAP}) scale(3)">\n    {recolor(second, ROWS[1], palette)}\n  </g>'
    )
    svg = svg[: match.start()] + groups + svg[match.end():]
    open(main_path, "w", encoding="utf-8").write(svg)


if __name__ == "__main__":
    main(*sys.argv[1:4])
