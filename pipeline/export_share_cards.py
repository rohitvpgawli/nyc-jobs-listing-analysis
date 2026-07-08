"""Export deterministic social share-card PNGs from atlas.json.

Outputs:
  site/public/og-card.png
  outputs/charts/og-card.png
  outputs/charts/reddit-role-family-card.png

The interactive site also includes a React share-card page, but this script is
the reproducible path used by the open-source package and CI.
"""

from __future__ import annotations

import json
import math
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from common import PROCESSED_DIR, ROOT

INK = "#0d0d11"
PAPER = "#f4f1ea"
PAPER_DIM = "#b9b5aa"
PAPER_FAINT = "#6d6a62"
YELLOW = "#fccc0a"
RED = "#ee352e"
BLUE = "#2864dc"

FAMILY_META = {
    "product_engineering": ("Product eng", "#2864DC", False),
    "gtm_sales_cs": ("GTM & sales", "#EE352E", False),
    "forward_deployed_solutions": ("Forward-deployed", "#FCCC0A", True),
    "ops_finance_people": ("Ops & finance", "#8A8D91", False),
    "design": ("Design", "#A7A9AC", False),
    "ai_ml_engineering": ("AI/ML eng", "#00A344", True),
    "product_management": ("Product mgmt", "#A96B2C", False),
    "data_science_research": ("DS & research", "#6CBE45", True),
    "founder_operator_generalist": ("Generalist", "#00ADD0", False),
    "data_engineering": ("Data eng", "#FF6319", True),
    "analytics_engineering_bi": ("Analytics & BI", "#C75FBB", True),
    "other": ("Other", "#58595B", False),
}


def _font(paths: list[str], size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default(size=size)


def display(size: int):
    return _font(
        [
            "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
            "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
            "/Library/Fonts/Georgia Bold.ttf",
        ],
        size,
    )


def display_italic(size: int):
    return _font(
        [
            "/System/Library/Fonts/Supplemental/Georgia Bold Italic.ttf",
            "/System/Library/Fonts/Supplemental/Times New Roman Bold Italic.ttf",
            "/Library/Fonts/Georgia Bold Italic.ttf",
        ],
        size,
    )


def body(size: int, bold: bool = False):
    return _font(
        [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ],
        size,
    )


def mono(size: int, bold: bool = False):
    return _font(
        [
            "/System/Library/Fonts/Supplemental/Andale Mono.ttf",
            "/System/Library/Fonts/Menlo.ttc",
        ],
        size,
    )


def draw_grid(draw: ImageDraw.ImageDraw, w: int, h: int):
    for x in range(0, w, 112):
        draw.line((x, 0, x, h), fill="#1f1f27", width=1)
    for y in range(0, h, 112):
        draw.line((0, y, w, y), fill="#1f1f27", width=1)


def draw_dots(draw: ImageDraw.ImageDraw, x: int, y: int, r: int = 12):
    for i, color in enumerate([YELLOW, RED, BLUE]):
        cx = x + i * (r * 2 + 10)
        draw.ellipse((cx, y, cx + r * 2, y + r * 2), fill=color)


def text_width(draw: ImageDraw.ImageDraw, text: str, font) -> int:
    return int(draw.textbbox((0, 0), text, font=font)[2])


def draw_rich_line(draw: ImageDraw.ImageDraw, xy: tuple[int, int], parts: list[tuple[str, ImageFont.ImageFont, str]]):
    x, y = xy
    for text, font, color in parts:
        draw.text((x, y), text, font=font, fill=color)
        x += text_width(draw, text, font)


def operator_share(atlas: dict) -> int:
    return round(sum(1 for j in atlas["jobs"] if j["operatorAdjacent"]) / len(atlas["jobs"]) * 100)


def export_og(atlas: dict):
    w, h = 1600, 900
    img = Image.new("RGB", (w, h), INK)
    draw = ImageDraw.Draw(img)
    draw_grid(draw, w, h)
    draw_dots(draw, 84, 72, 12)

    label = f"NYC AI STARTUP HIRING ATLAS · {atlas['meta']['collectedAt']}"
    draw.text((w - text_width(draw, label, mono(22)) - 84, 76), label, font=mono(22), fill=PAPER_FAINT)

    draw.text((84, 170), "The Hiring", font=display(150), fill=PAPER)
    draw.text((84, 310), "Signal", font=display_italic(150), fill=PAPER)
    draw.ellipse((502, 414, 542, 454), fill=YELLOW)

    draw.text((84, 520), "Every AI company says it's building the future.", font=body(34), fill=PAPER_DIM)
    draw.text((84, 566), "Their job boards say what they're building it with.", font=body(34, bold=True), fill=PAPER)

    stats = [
        (str(atlas["meta"]["jobCount"]), "open roles, classified"),
        (str(atlas["meta"]["companyCount"]), "YC-backed AI startups in NYC"),
        (f"{operator_share(atlas)}%", "core data/AI-operator roles"),
    ]
    x = 84
    for num, label in stats:
        draw.text((x, 720), num, font=display(90), fill=YELLOW)
        draw.text((x, 820), label, font=mono(19), fill=PAPER_FAINT)
        x += 410

    for dest in [ROOT / "site" / "public" / "og-card.png", ROOT / "outputs" / "charts" / "og-card.png"]:
        dest.parent.mkdir(parents=True, exist_ok=True)
        img.save(dest)
        print(f"Wrote {dest}")


def export_chart(atlas: dict):
    w, h = 1600, 1200
    img = Image.new("RGB", (w, h), INK)
    draw = ImageDraw.Draw(img)
    draw_grid(draw, w, h)
    draw_dots(draw, 90, 76, 12)

    label = f"COLLECTED {atlas['meta']['collectedAt']}"
    draw.text((w - text_width(draw, label, mono(21)) - 90, 80), label, font=mono(21), fill=PAPER_FAINT)

    draw.text((90, 140), f"What {atlas['meta']['companyCount']} NYC AI startups", font=display(58), fill=PAPER)
    draw.text((90, 206), "are hiring for right now", font=display(58), fill=PAPER)
    draw.text((90, 296), f"{atlas['meta']['jobCount']} open roles by role family. Dashed outline = data/AI operator work.", font=body(27), fill=PAPER_DIM)

    counts: dict[str, int] = {}
    for job in atlas["jobs"]:
        counts[job["family"]] = counts.get(job["family"], 0) + 1
    rows = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    max_count = rows[0][1]

    left, top = 430, 385
    bar_max = 870
    row_h = 62
    for i, (family, count) in enumerate(rows):
        label, color, adjacent = FAMILY_META[family]
        y = top + i * row_h
        draw.text((90, y + 4), label, font=mono(24), fill=PAPER_DIM)
        bw = math.ceil(bar_max * count / max_count)
        draw.rounded_rectangle((left, y, left + bw, y + 34), radius=17, fill=color)
        if adjacent:
            # Light dashed outline around operator-adjacent roles.
            for x in range(left - 4, left + bw + 4, 18):
                draw.line((x, y - 6, min(x + 9, left + bw + 4), y - 6), fill=(244, 241, 234), width=2)
                draw.line((x, y + 40, min(x + 9, left + bw + 4), y + 40), fill=(244, 241, 234), width=2)
            for yy in range(y - 6, y + 40, 18):
                draw.line((left - 6, yy, left - 6, min(yy + 9, y + 40)), fill=(244, 241, 234), width=2)
                draw.line((left + bw + 6, yy, left + bw + 6, min(yy + 9, y + 40)), fill=(244, 241, 234), width=2)
        draw.text((left + bar_max + 38, y - 2), str(count), font=mono(28), fill=PAPER)

    foot = (
        "Source: public YC directory (yc-oss API) + Work at a Startup postings. "
        "YC-backed, AI-tagged, NYC-located, actively hiring. "
        "Keyword + manual classification. Full method & data: github.com/rohitgawli/nyc-startups-hiring"
    )
    y = 1100
    for line in textwrap.wrap(foot, width=118):
        draw.text((90, y), line, font=mono(17), fill=PAPER_FAINT)
        y += 28

    dest = ROOT / "outputs" / "charts" / "reddit-role-family-card.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest)
    print(f"Wrote {dest}")


def main():
    atlas = json.loads((PROCESSED_DIR / "atlas.json").read_text())
    export_og(atlas)
    export_chart(atlas)


if __name__ == "__main__":
    main()
