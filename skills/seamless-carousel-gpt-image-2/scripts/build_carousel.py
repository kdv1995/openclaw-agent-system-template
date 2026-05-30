#!/usr/bin/env python3
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def load_font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        "<workspace>/assets/fonts/Unbounded-wght.ttf",
        "~/Library/Fonts/Unbounded-Black.ttf",
        "~/Library/Fonts/Unbounded-ExtraBold.ttf",
        "~/Library/Fonts/Unbounded-Bold.ttf",
        "/Library/Fonts/Unbounded-Black.ttf",
        "/Library/Fonts/Unbounded-ExtraBold.ttf",
        "/Library/Fonts/Unbounded-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description="Build seamless carousel slides from one wide base image.")
    parser.add_argument("--input", required=True, help="Wide base image path")
    parser.add_argument("--out-dir", required=True, help="Directory for cropped slides")
    parser.add_argument("--slides", type=int, default=3, help="Number of slides")
    parser.add_argument("--text", action="append", required=True, help="Slide text; pass once per slide")
    parser.add_argument("--prefix", default="carousel", help="Output filename prefix")
    args = parser.parse_args()

    if len(args.text) != args.slides:
        raise SystemExit(f"expected {args.slides} --text values, got {len(args.text)}")

    img = Image.open(args.input).convert("RGB")
    w, h = img.size
    panel_w = w // args.slides
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for i, text in enumerate(args.text):
        left = i * panel_w
        right = w if i == args.slides - 1 else (i + 1) * panel_w
        slide = img.crop((left, 0, right, h)).resize((1080, 1350), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(slide, "RGBA")

        margin = 78
        box_top = 92
        box_w = 1080 - margin * 2
        font_size = 92 if len(text) < 36 else 80
        font = load_font(font_size)
        lines = wrap_text(draw, text, font, box_w)
        line_h = int(font_size * 1.08)
        box_h = line_h * len(lines) + 54

        draw.rounded_rectangle(
            (margin - 26, box_top - 26, 1080 - margin + 26, box_top + box_h),
            radius=34,
            fill=(0, 0, 0, 172),
            outline=(226, 24, 44, 220),
            width=3,
        )

        y = box_top
        for line in lines:
            draw.text((margin, y), line, font=font, fill=(255, 255, 255, 255))
            y += line_h

        footer = f"{i + 1}/{args.slides}"
        footer_font = load_font(38)
        draw.text((margin, 1256), footer, font=footer_font, fill=(226, 24, 44, 255))
        slide.save(out_dir / f"{args.prefix}_{i + 1:02d}.png")


if __name__ == "__main__":
    main()
