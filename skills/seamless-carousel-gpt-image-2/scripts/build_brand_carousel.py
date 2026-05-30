#!/usr/bin/env python3
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter


W, H = 1080, 1350
RED = "#E40914"
INK = "#141414"
BLACK = "#0A0A0A"
PAPER = "#F7F5F2"
PAPER_2 = "#ECE9E3"
WHITE = "#FFFFFF"
RULE = (20, 20, 20, 36)


def font(size: int, role: str = "display") -> ImageFont.FreeTypeFont:
    candidates = [
        "<workspace>/assets/fonts/Unbounded-wght.ttf",
        "~/Library/Fonts/Unbounded-Black.ttf",
        "~/Library/Fonts/Unbounded-ExtraBold.ttf",
        "~/Library/Fonts/Unbounded-Bold.ttf",
        "/Library/Fonts/Unbounded-Black.ttf",
        "/Library/Fonts/Unbounded-ExtraBold.ttf",
        "/Library/Fonts/Unbounded-Bold.ttf",
    ]
    for item in candidates:
        if Path(item).exists():
            return ImageFont.truetype(item, size=size)
    return ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", size=size)


def shadow_layer(base: Image.Image, box: tuple[int, int, int, int], radius: int = 18) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(box, radius=radius, fill=(0, 0, 0, 34))
    layer = layer.filter(ImageFilter.GaussianBlur(18))
    base.alpha_composite(layer, (0, 8))


def card(draw: ImageDraw.ImageDraw, box, fill=PAPER_2, outline=RULE, radius=14, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def ui_row(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, red: bool = False):
    fill = RED if red else INK
    draw.rounded_rectangle((x, y, x + 38, y + 14), radius=7, fill=fill)
    draw.rounded_rectangle((x + 54, y, x + w, y + 14), radius=7, fill=(20, 20, 20, 76))


def rail(draw: ImageDraw.ImageDraw, points: list[tuple[int, int]], width: int = 8):
    draw.line(points, fill=RED, width=width, joint="curve")
    for x, y in points[1:-1]:
        draw.ellipse((x - 12, y - 12, x + 12, y + 12), fill=RED)


def eyebrow(draw, text, color=RED, y=74):
    f = font(22)
    draw.text((62, y), f"● {text.upper()}", font=f, fill=color)


def headline(draw, lines, y, colors=None, size=82, leading=0.95, fill=INK):
    colors = colors or {}
    f = font(size, "display")
    line_h = int(size * leading)
    for idx, line in enumerate(lines):
        draw.text((60, y + idx * line_h), line, font=f, fill=colors.get(idx, fill))


def footer(draw, idx, total, dark=False):
    f = font(34, "display")
    draw.text((60, 1242), f"{idx}/{total}", font=f, fill=RED if not dark else WHITE)
    draw.line((162, 1266, 1020, 1266), fill=(228, 9, 20, 210), width=4)


def slide_1(out: Path):
    img = Image.new("RGBA", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    eyebrow(draw, "MARKET SPEED // AI RESEARCH")
    headline(
        draw,
        ["КОНКУРЕНТИ", "НЕ СИЛЬНІШІ.", "ВОНИ ШВИДШЕ", "ТЕСТУЮТЬ."],
        132,
        colors={2: RED},
        size=82,
    )
    draw.line((60, 525, 1018, 525), fill=RULE, width=2)

    rail(draw, [(-40, 790), (210, 760), (430, 850), (660, 750), (1130, 800)])
    for i, (x, y, w, h) in enumerate(
        [(574, 604, 356, 108), (482, 746, 428, 118), (620, 904, 342, 108), (206, 840, 300, 102)]
    ):
        shadow_layer(img, (x, y, x + w, y + h))
        card(draw, (x, y, x + w, y + h), fill=WHITE if i % 2 else PAPER_2, radius=18)
        ui_row(draw, x + 28, y + 28, w - 62, red=i == 1)
        ui_row(draw, x + 28, y + 62, w - 104)
    draw.rectangle((62, 1120, 332, 1128), fill=RED)
    footer(draw, 1, 3)
    img.convert("RGB").save(out)


def slide_2(out: Path):
    img = Image.new("RGBA", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    eyebrow(draw, "OFFER MAP // SIGNALS")
    headline(
        draw,
        ["AI ЗБИРАЄ", "ОФЕРИ,", "РЕКЛАМУ", "І БОЛІ РИНКУ"],
        134,
        colors={0: RED},
        size=77,
    )
    draw.line((60, 518, 1018, 518), fill=RULE, width=2)

    rail(draw, [(-35, 730), (230, 725), (442, 646), (656, 782), (1124, 718)])
    for x in (584, 736, 888):
        shadow_layer(img, (x, 590, x + 96, 420 + 470), radius=24)
        card(draw, (x, 590, x + 96, 890), fill=WHITE, radius=24)
        draw.rounded_rectangle((x + 22, 622, x + 74, 674), radius=12, fill=RED if x == 736 else INK)
        for j in range(4):
            draw.rounded_rectangle((x + 20, 710 + j * 34, x + 76, 724 + j * 34), radius=7, fill=(20, 20, 20, 70))
    card(draw, (176, 762, 492, 1028), fill=INK, outline=(228, 9, 20, 220), radius=24, width=3)
    for j in range(4):
        ui_row(draw, 220, 818 + j * 48, 226, red=j == 0)
    draw.ellipse((874, 948, 1002, 1076), fill=RED)
    draw.ellipse((908, 982, 968, 1042), outline=WHITE, width=8)
    footer(draw, 2, 3)
    img.convert("RGB").save(out)


def slide_3(out: Path):
    img = Image.new("RGBA", (W, H), RED)
    draw = ImageDraw.Draw(img)
    eyebrow(draw, "CTA // NEXT STEP", color=WHITE)
    f_big = font(72, "display")
    draw.text((60, 134), "НАПИШИ", font=f_big, fill=WHITE)
    draw.rounded_rectangle((60, 222, 502, 308), radius=14, fill=WHITE)
    draw.text((86, 238), '"РИНОК"', font=font(48, "display"), fill=RED)
    draw.text((60, 334), "ПОКАЖУ, ДЕ", font=f_big, fill=WHITE)
    draw.text((60, 410), "ТОЧКА РОСТУ.", font=f_big, fill=WHITE)

    rail(draw, [(-45, 760), (260, 766), (472, 890), (706, 788), (982, 920)], width=9)
    card(draw, (510, 660, 968, 1018), fill=WHITE, outline=(255, 255, 255, 255), radius=28)
    d2 = ImageDraw.Draw(img)
    d2.rounded_rectangle((556, 718, 906, 760), radius=20, fill=INK)
    for j in range(4):
        d2.rounded_rectangle((556, 810 + j * 42, 866 - j * 28, 828 + j * 42), radius=9, fill=(20, 20, 20, 86))
    d2.ellipse((846, 888, 926, 968), fill=RED)
    d2.line((868, 930, 888, 950, 908, 906), fill=WHITE, width=7)
    footer(draw, 3, 3, dark=True)
    img.convert("RGB").save(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--prefix", default="brand_market_ai")
    args = parser.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    slide_1(out_dir / f"{args.prefix}_01.png")
    slide_2(out_dir / f"{args.prefix}_02.png")
    slide_3(out_dir / f"{args.prefix}_03.png")


if __name__ == "__main__":
    main()
