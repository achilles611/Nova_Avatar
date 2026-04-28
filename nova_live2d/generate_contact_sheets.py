from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "contact_sheets"
MANIFEST_PATH = ROOT / "part_manifest.json"
TILE_W = 320
TILE_H = 320
PADDING = 24
LABEL_H = 40
BG = (20, 20, 24, 255)
PANEL = (34, 34, 40, 255)
TEXT = (245, 245, 245, 255)
ACCENT = (120, 175, 255, 255)


def load_manifest() -> list[dict]:
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return data.get("parts", [])


def fit_image(img: Image.Image, width: int, height: int) -> Image.Image:
    fitted = img.copy()
    fitted.thumbnail((width, height), Image.Resampling.LANCZOS)
    return fitted


def draw_tile(canvas: Image.Image, xy: tuple[int, int], title: str, source_path: Path, font: ImageFont.ImageFont) -> None:
    x, y = xy
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((x, y, x + TILE_W, y + TILE_H), radius=12, fill=PANEL, outline=ACCENT, width=2)

    with Image.open(source_path) as raw:
        img = raw.convert("RGBA")
    preview = fit_image(img, TILE_W - 32, TILE_H - LABEL_H - 32)
    px = x + (TILE_W - preview.width) // 2
    py = y + 16 + (TILE_H - LABEL_H - 32 - preview.height) // 2
    canvas.alpha_composite(preview, (px, py))
    draw.text((x + 12, y + TILE_H - LABEL_H + 8), title, fill=TEXT, font=font)


def build_contact_sheet(category: str, entries: list[dict]) -> Path:
    cols = min(4, max(1, len(entries)))
    rows = math.ceil(len(entries) / cols)
    width = PADDING + cols * (TILE_W + PADDING)
    height = 96 + rows * (TILE_H + PADDING)
    canvas = Image.new("RGBA", (width, height), BG)
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()

    draw.text((PADDING, 24), f"Nova contact sheet: {category}", fill=TEXT, font=font)

    for index, entry in enumerate(entries):
        row = index // cols
        col = index % cols
        x = PADDING + col * (TILE_W + PADDING)
        y = 64 + row * (TILE_H + PADDING)
        source_path = ROOT / entry["source_file"]
        draw_tile(canvas, (x, y), entry["display_name"], source_path, font)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{category}_contact_sheet.png"
    canvas.save(out_path)
    return out_path


def main() -> int:
    entries = load_manifest()
    by_category: dict[str, list[dict]] = {}
    for entry in entries:
        category = entry.get("category")
        if category not in {"body", "face", "hair", "accessory", "guide"}:
            continue
        source = entry.get("source_file")
        if not isinstance(source, str):
            continue
        if not source.lower().endswith(".png"):
            continue
        by_category.setdefault(category, []).append(entry)

    written = []
    for category in sorted(by_category):
        written.append(build_contact_sheet(category, by_category[category]))

    for path in written:
        print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
