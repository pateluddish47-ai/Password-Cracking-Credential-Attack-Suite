"""Splits the two tallest dashboard screenshots into separate, legible
sub-images at natural section breaks, so each piece can be embedded larger
(and therefore more readable) in the Word report.
"""
from pathlib import Path

from PIL import Image

DIR = Path(__file__).resolve().parent.parent / "reports" / "screenshots"

SPLITS = {
    "04_Strength_Analyzer.png": [
        ("04a_Strength_Table.png", 0, 995),
        ("04b_Strength_Charts.png", 995, 1600),
        ("04c_Risk_Ranking.png", 1600, None),
    ],
    "07_Audit_Report.png": [
        ("07a_Report_Summary_Table.png", 0, 1190),
        ("07b_Report_Attacks_Compliance.png", 1190, None),
    ],
}


def main():
    for src_name, parts in SPLITS.items():
        src_path = DIR / src_name
        im = Image.open(src_path).convert("RGB")
        w, h = im.size
        for out_name, top, bottom in parts:
            bottom = bottom if bottom is not None else h
            crop = im.crop((0, top, w, min(bottom, h)))
            crop.save(DIR / out_name)
            print(f"{out_name}: {crop.size}")


if __name__ == "__main__":
    main()
