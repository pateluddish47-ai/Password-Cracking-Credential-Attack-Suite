"""Crops each captured dashboard screenshot tightly to its real content
bounds (removing dead whitespace and the floating Streamlit badge), so the
images render larger/sharper when embedded in the report at a fixed width.
"""
from pathlib import Path

from PIL import Image, ImageChops

SRC_DIR = Path(__file__).resolve().parent.parent / "reports" / "screenshots"
MARGIN = 16


def crop(path: Path) -> None:
    im = Image.open(path).convert("RGB")
    w, h = im.size

    # Permanently white out the floating Streamlit "Manage app" badge
    # (fixed bottom-right corner of the viewport) before cropping.
    badge_box = (w - 140, h - 140, w, h)
    im.paste(Image.new("RGB", (140, 140), (255, 255, 255)), badge_box)

    bg = Image.new("RGB", im.size, (255, 255, 255))
    bbox = ImageChops.difference(im, bg).getbbox()
    if bbox is None:
        return

    left, top, right, bottom = bbox
    left = max(0, left - MARGIN)
    top = max(0, top - MARGIN)
    right = min(w, right + MARGIN)
    bottom = min(h, bottom + MARGIN)

    cropped = im.crop((left, top, right, bottom))
    cropped.save(path)
    print(f"{path.name}: {im.size} -> {cropped.size}")


def main():
    for f in sorted(SRC_DIR.glob("*.png")):
        crop(f)


if __name__ == "__main__":
    main()
