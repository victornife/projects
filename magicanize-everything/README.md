# Magicanize Everything

A mini Python project that takes a source image and transforms it into a **Magic: The Gathering-style card**.

It prompts for:
- card color
- "style text" (rules/flavor style text)

Then it renders a complete card image with:
- the uploaded art integrated into a framed art box
- a card name bar
- type line
- style text box
- color-themed border treatment

## Quick start

```bash
cd magicanize-everything
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python create_card.py --input ./example.jpg --output ./card_output.png
```

Or run interactively (it will ask you for paths and text):

```bash
python create_card.py
```

## Notes

- The script is intentionally lightweight and offline.
- It uses Pillow for image composition.
- If a font isn't available, it falls back to Pillow defaults.
