#!/usr/bin/env python3
"""Create Magic-style trading cards from images and custom text."""
from __future__ import annotations

import argparse
from pathlib import Path
from textwrap import wrap
from PIL import Image, ImageDraw, ImageFont, ImageOps

CARD_W, CARD_H = 744, 1039
MARGIN = 28

COLOR_THEMES = {
    "white": {"frame": (228, 220, 200), "accent": (120, 105, 78), "textbox": (244, 239, 228)},
    "blue": {"frame": (163, 186, 209), "accent": (40, 73, 108), "textbox": (221, 232, 243)},
    "black": {"frame": (95, 95, 102), "accent": (30, 30, 34), "textbox": (210, 210, 216)},
    "red": {"frame": (209, 150, 139), "accent": (122, 46, 37), "textbox": (241, 220, 215)},
    "green": {"frame": (144, 183, 141), "accent": (52, 92, 54), "textbox": (219, 236, 216)},
    "colorless": {"frame": (180, 180, 180), "accent": (78, 78, 78), "textbox": (230, 230, 230)},
}


def load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    """Load a TrueType font from system paths or fallback to default.
    
    Args:
        size: Font size in pixels.
        bold: Whether to load bold variant.
        
    Returns:
        ImageFont object.
    """
    candidates = [
        (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            if bold
            else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        ),
        "/Library/Fonts/Arial.ttf",
        "arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def normalize_color(color: str) -> str:
    """Normalize and validate color name.
    
    Supports aliases: w=white, u=blue, b=black, r=red, g=green, c=colorless.
    
    Args:
        color: Color name or alias.
        
    Returns:
        Normalized color name.
        
    Raises:
        ValueError: If color is not supported.
    """
    c = color.strip().lower()
    aliases = {"w": "white", "u": "blue", "b": "black", "r": "red", "g": "green", "c": "colorless"}
    c = aliases.get(c, c)
    if c not in COLOR_THEMES:
        raise ValueError(f"Unsupported color '{color}'. Use one of: {', '.join(COLOR_THEMES)}")
    return c


def _draw_header(draw: ImageDraw.ImageDraw, card_name: str, accent_color: tuple) -> None:
    """Draw card header with name.
    
    Args:
        draw: ImageDraw object.
        card_name: Name to display in header.
        accent_color: Color for outline and text accents.
    """
    header_h = 84
    draw.rounded_rectangle(
        [(MARGIN + 10, MARGIN + 10), (CARD_W - MARGIN - 10, MARGIN + 10 + header_h)],
        radius=16,
        fill=(245, 245, 245),
        outline=accent_color,
        width=3,
    )
    name_font = load_font(40, bold=True)
    draw.text((MARGIN + 26, MARGIN + 30), card_name, fill=(20, 20, 20), font=name_font)


def _draw_art_box(card: Image.Image, draw: ImageDraw.ImageDraw, art_path: Path,
                  accent_color: tuple) -> int:
    """Draw art box and paste artwork.
    
    Args:
        card: PIL Image object for the card.
        draw: ImageDraw object.
        art_path: Path to artwork image.
        accent_color: Color for box outline.
        
    Returns:
        Y-coordinate after the art box.
    """
    art_top = MARGIN + 115
    art_h = 460
    art_box = (MARGIN + 18, art_top, CARD_W - MARGIN - 18, art_top + art_h)
    draw.rectangle(art_box, outline=accent_color, width=4)

    art = Image.open(art_path).convert("RGB")
    art = ImageOps.fit(
        art,
        (art_box[2] - art_box[0] - 6, art_box[3] - art_box[1] - 6),
        method=Image.Resampling.LANCZOS,
    )
    card.paste(art, (art_box[0] + 3, art_box[1] + 3))
    return art_box[3]


def _draw_type_line(draw: ImageDraw.ImageDraw, color: str, accent_color: tuple,
                    art_bottom: int) -> int:
    """Draw type line for the card.
    
    Args:
        draw: ImageDraw object.
        color: Card color name.
        accent_color: Color for outline.
        art_bottom: Y-coordinate of art box bottom.
        
    Returns:
        Y-coordinate after type line.
    """
    type_y = art_bottom + 18
    type_h = 60
    draw.rounded_rectangle(
        [(MARGIN + 12, type_y), (CARD_W - MARGIN - 12, type_y + type_h)],
        radius=12,
        fill=(245, 245, 245),
        outline=accent_color,
        width=3,
    )
    type_font = load_font(28, bold=True)
    draw.text(
        (MARGIN + 28, type_y + 15),
        f"Legendary Artifact — {color.title()}",
        fill=(18, 18, 18),
        font=type_font,
    )
    return type_y + type_h


def _draw_text_box(draw: ImageDraw.ImageDraw, style_text: str, accent_color: tuple,
                   textbox_color: tuple, text_top: int) -> None:
    """Draw text box with ability text.
    
    Args:
        draw: ImageDraw object.
        style_text: Text to display in box.
        accent_color: Color for outline.
        textbox_color: Fill color for text box.
        text_top: Y-coordinate for top of text box.
    """
    text_box = (MARGIN + 12, text_top, CARD_W - MARGIN - 12, CARD_H - MARGIN - 40)
    draw.rounded_rectangle(
        text_box, radius=14, fill=textbox_color, outline=accent_color, width=3
    )

    rules_font = load_font(28)
    x, y = text_box[0] + 18, text_box[1] + 16
    for line in wrap(style_text, width=44):
        draw.text((x, y), line, fill=(24, 24, 24), font=rules_font)
        y += 36


def _draw_signature(draw: ImageDraw.ImageDraw, accent_color: tuple) -> None:
    """Draw signature line at bottom of card.
    
    Args:
        draw: ImageDraw object.
        accent_color: Color for text.
    """
    sig_font = load_font(22)
    draw.text(
        (MARGIN + 24, CARD_H - MARGIN - 30),
        "Magicanize Everything",
        fill=accent_color,
        font=sig_font,
    )


def make_card(
    art_path: Path,
    output_path: Path,
    color: str,
    style_text: str,
    card_name: str = "Magicanized Relic",
) -> None:
    """Create a Magic-style card and save to file.
    
    Args:
        art_path: Path to source artwork image.
        output_path: Path where card image will be saved.
        color: Card color theme name.
        style_text: Card ability text to render.
        card_name: Card title (default: "Magicanized Relic").
    """
    theme = COLOR_THEMES[color]

    card = Image.new("RGB", (CARD_W, CARD_H), theme["frame"])
    draw = ImageDraw.Draw(card)

    outer_radius = 36
    mask = Image.new("L", (CARD_W, CARD_H), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [(0, 0), (CARD_W - 1, CARD_H - 1)], radius=outer_radius, fill=255
    )

    # Outer and inner frame
    draw.rounded_rectangle(
        [(0, 0), (CARD_W - 1, CARD_H - 1)],
        radius=outer_radius,
        fill=theme["frame"],
        outline=theme["accent"],
        width=8,
    )
    draw.rounded_rectangle(
        [(MARGIN, MARGIN), (CARD_W - MARGIN, CARD_H - MARGIN)],
        radius=22,
        outline=theme["accent"],
        width=4,
    )

    # Draw card sections
    _draw_header(draw, card_name, theme["accent"])
    art_bottom = _draw_art_box(card, draw, art_path, theme["accent"])
    type_bottom = _draw_type_line(draw, color, theme["accent"], art_bottom)
    text_top = type_bottom + 16
    _draw_text_box(draw, style_text, theme["accent"], theme["textbox"], text_top)
    _draw_signature(draw, theme["accent"])

    final = Image.new("RGBA", (CARD_W, CARD_H))
    final.paste(card, (0, 0))
    final.putalpha(mask)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    final.save(output_path)


def prompt_if_missing(value: str | None, prompt: str) -> str:
    """Prompt user for input if value is missing.
    
    Args:
        value: Existing value (if any).
        prompt: Prompt text to display.
        
    Returns:
        Provided or prompted value.
    """
    if value:
        return value
    return input(prompt).strip()


def main() -> None:
    """Main entry point for card creation."""
    parser = argparse.ArgumentParser(description="Create a Magic-style card from an image.")
    parser.add_argument("--input", type=str, help="Path to source art image")
    parser.add_argument(
        "--output", type=str, help="Output card image path", default="magicanized_card.png"
    )
    parser.add_argument(
        "--color", type=str, help="Card color (white/blue/black/red/green/colorless)"
    )
    parser.add_argument("--style-text", type=str, help='Card "style text" to render in text box')
    parser.add_argument("--name", type=str, help="Card name", default="Magicanized Relic")
    args = parser.parse_args()

    input_path = prompt_if_missing(args.input, "Image path: ")
    color_raw = prompt_if_missing(
        args.color, "Color (white/blue/black/red/green/colorless): "
    )
    style_text = prompt_if_missing(args.style_text, "Style text: ")

    color = normalize_color(color_raw)

    make_card(Path(input_path), Path(args.output), color, style_text, card_name=args.name)
    print(f"Saved card to {args.output}")


if __name__ == "__main__":
    main()
