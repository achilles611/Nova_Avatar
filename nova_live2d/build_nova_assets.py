from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Iterable

from PIL import Image


BODY_CROPS = [
    ("head_base", (240, 95, 650, 500)),
    ("torso_base", (185, 360, 700, 975)),
    ("left_arm_base", (115, 410, 325, 980)),
    ("right_arm_base", (560, 410, 772, 980)),
    ("left_hand_base", (142, 862, 280, 1098)),
    ("right_hand_base", (610, 862, 744, 1098)),
    ("left_leg_base", (265, 905, 460, 1738)),
    ("right_leg_base", (430, 905, 625, 1738)),
    ("left_shoe_base", (225, 1496, 468, 1774)),
    ("right_shoe_base", (418, 1496, 686, 1774)),
]


def ensure_dirs(paths: Iterable[Path]) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def run_chroma_removal(script: Path, image_in: Path, image_out: Path) -> None:
    if image_out.exists():
        image_out.unlink()
    cmd = [
        "python",
        str(script),
        "--input",
        str(image_in),
        "--out",
        str(image_out),
        "--auto-key",
        "border",
        "--soft-matte",
        "--transparent-threshold",
        "12",
        "--opaque-threshold",
        "220",
        "--despill",
    ]
    subprocess.run(cmd, check=True)


def alpha_bbox(img: Image.Image) -> tuple[int, int, int, int] | None:
    alpha = img.getchannel("A")
    return alpha.getbbox()


def trim_crop(img: Image.Image, box: tuple[int, int, int, int], padding: int = 8) -> Image.Image:
    crop = img.crop(box)
    bbox = alpha_bbox(crop)
    if bbox is None:
        return crop
    left = max(bbox[0] - padding, 0)
    top = max(bbox[1] - padding, 0)
    right = min(bbox[2] + padding, crop.width)
    bottom = min(bbox[3] + padding, crop.height)
    return crop.crop((left, top, right, bottom))


def connected_components(img: Image.Image, alpha_threshold: int = 12, min_pixels: int = 120) -> list[tuple[int, int, int, int]]:
    alpha = img.getchannel("A")
    width, height = img.size
    data = alpha.load()
    visited = bytearray(width * height)
    boxes: list[tuple[int, int, int, int]] = []

    def idx(x: int, y: int) -> int:
        return y * width + x

    for y in range(height):
        for x in range(width):
            if visited[idx(x, y)] or data[x, y] <= alpha_threshold:
                continue
            stack = [(x, y)]
            visited[idx(x, y)] = 1
            min_x = max_x = x
            min_y = max_y = y
            pixels = 0
            while stack:
                cx, cy = stack.pop()
                pixels += 1
                if cx < min_x:
                    min_x = cx
                if cx > max_x:
                    max_x = cx
                if cy < min_y:
                    min_y = cy
                if cy > max_y:
                    max_y = cy
                for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
                    if 0 <= nx < width and 0 <= ny < height:
                        i = idx(nx, ny)
                        if not visited[i] and data[nx, ny] > alpha_threshold:
                            visited[i] = 1
                            stack.append((nx, ny))
            if pixels >= min_pixels:
                boxes.append((min_x, min_y, max_x + 1, max_y + 1))
    return boxes


def sort_boxes_row_major(boxes: list[tuple[int, int, int, int]], row_tolerance: int = 70) -> list[tuple[int, int, int, int]]:
    rows: list[list[tuple[int, int, int, int]]] = []
    for box in sorted(boxes, key=lambda b: (b[1], b[0])):
        cy = (box[1] + box[3]) / 2
        placed = False
        for row in rows:
            row_cy = sum((b[1] + b[3]) / 2 for b in row) / len(row)
            if abs(cy - row_cy) <= row_tolerance:
                row.append(box)
                placed = True
                break
        if not placed:
            rows.append([box])
    sorted_boxes: list[tuple[int, int, int, int]] = []
    for row in rows:
        sorted_boxes.extend(sorted(row, key=lambda b: b[0]))
    return sorted_boxes


def save_component_grid(img: Image.Image, boxes: list[tuple[int, int, int, int]], out_dir: Path, prefix: str) -> list[dict]:
    manifests: list[dict] = []
    rows: list[list[tuple[int, int, int, int]]] = []
    for box in boxes:
        cy = (box[1] + box[3]) / 2
        placed = False
        for row in rows:
            row_cy = sum((b[1] + b[3]) / 2 for b in row) / len(row)
            if abs(cy - row_cy) <= 70:
                row.append(box)
                placed = True
                break
        if not placed:
            rows.append([box])
    for r_index, row in enumerate(rows, start=1):
        for c_index, box in enumerate(sorted(row, key=lambda b: b[0]), start=1):
            piece = trim_crop(img, box, padding=8)
            name = f"{prefix}_r{r_index:02d}_c{c_index:02d}.png"
            out_path = out_dir / name
            piece.save(out_path)
            manifests.append(
                {
                    "name": out_path.stem,
                    "category": prefix,
                    "file": str(out_path),
                    "source_box": list(box),
                    "size": [piece.width, piece.height],
                }
            )
    return manifests


def build_body_parts(base_img: Image.Image, out_dir: Path) -> list[dict]:
    manifests: list[dict] = []
    for name, box in BODY_CROPS:
        piece = trim_crop(base_img, box, padding=10)
        out_path = out_dir / f"{name}.png"
        piece.save(out_path)
        manifests.append(
            {
                "name": out_path.stem,
                "category": "body",
                "file": str(out_path),
                "source_box": list(box),
                "size": [piece.width, piece.height],
            }
        )
    return manifests


def build_icon(base_img: Image.Image, icon_path: Path) -> None:
    crop = trim_crop(base_img, (220, 75, 670, 560), padding=20)
    side = max(crop.width, crop.height)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    x = (side - crop.width) // 2
    y = (side - crop.height) // 2
    canvas.alpha_composite(crop, (x, y))
    canvas = canvas.resize((512, 512), Image.Resampling.LANCZOS)
    canvas.convert("RGB").save(icon_path, quality=92)


def pack_atlas(parts: list[Path], atlas_path: Path, manifest_path: Path, size: int = 4096, padding: int = 16) -> None:
    images = []
    for part in parts:
        img = Image.open(part).convert("RGBA")
        images.append((part, img))
    images.sort(key=lambda item: max(item[1].width, item[1].height), reverse=True)

    atlas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    x = padding
    y = padding
    row_height = 0
    manifest = []

    for part, img in images:
        if x + img.width + padding > size:
            x = padding
            y += row_height + padding
            row_height = 0
        if y + img.height + padding > size:
            raise RuntimeError(f"Atlas overflow while packing {part.name}")
        atlas.alpha_composite(img, (x, y))
        manifest.append(
            {
                "file": str(part),
                "atlas_x": x,
                "atlas_y": y,
                "width": img.width,
                "height": img.height,
            }
        )
        x += img.width + padding
        row_height = max(row_height, img.height)

    atlas.save(atlas_path)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument("--cubism-root", required=True)
    parser.add_argument("--reference", required=True)
    parser.add_argument("--base-chroma", required=True)
    parser.add_argument("--face-chroma", required=True)
    parser.add_argument("--hair-chroma", required=True)
    parser.add_argument("--remove-script", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    workspace_root = Path(args.workspace_root)
    cubism_root = Path(args.cubism_root)
    reference = Path(args.reference)
    base_chroma = Path(args.base_chroma)
    face_chroma = Path(args.face_chroma)
    hair_chroma = Path(args.hair_chroma)
    remove_script = Path(args.remove_script)

    workspace_dirs = {
        "reference": workspace_root / "reference",
        "generated": workspace_root / "generated",
        "textures": workspace_root / "textures",
        "body_parts": workspace_root / "parts" / "body",
        "face_parts": workspace_root / "parts" / "face",
        "hair_parts": workspace_root / "parts" / "hair",
        "rig_notes": workspace_root / "rig_notes",
    }
    cubism_dirs = {
        "source": cubism_root / "source",
        "textures": cubism_root / "textures",
        "parts": cubism_root / "parts",
    }
    ensure_dirs([*workspace_dirs.values(), *cubism_dirs.values()])

    (workspace_dirs["reference"] / "nova_reference.png").write_bytes(reference.read_bytes())
    (cubism_dirs["source"] / "nova_reference.png").write_bytes(reference.read_bytes())

    raw_targets = {
        "base": workspace_dirs["generated"] / "nova_base_chroma.png",
        "face": workspace_dirs["generated"] / "nova_face_sheet_chroma.png",
        "hair": workspace_dirs["generated"] / "nova_hair_sheet_chroma.png",
    }
    raw_targets["base"].write_bytes(base_chroma.read_bytes())
    raw_targets["face"].write_bytes(face_chroma.read_bytes())
    raw_targets["hair"].write_bytes(hair_chroma.read_bytes())

    clean_targets = {
        "base": workspace_dirs["textures"] / "nova_base_fullbody.png",
        "face": workspace_dirs["textures"] / "nova_face_sheet.png",
        "hair": workspace_dirs["textures"] / "nova_hair_sheet.png",
    }
    run_chroma_removal(remove_script, raw_targets["base"], clean_targets["base"])
    run_chroma_removal(remove_script, raw_targets["face"], clean_targets["face"])
    run_chroma_removal(remove_script, raw_targets["hair"], clean_targets["hair"])

    base_img = Image.open(clean_targets["base"]).convert("RGBA")
    face_img = Image.open(clean_targets["face"]).convert("RGBA")
    hair_img = Image.open(clean_targets["hair"]).convert("RGBA")

    body_manifest = build_body_parts(base_img, workspace_dirs["body_parts"])
    face_boxes = sort_boxes_row_major(connected_components(face_img))
    hair_boxes = sort_boxes_row_major(connected_components(hair_img))
    face_manifest = save_component_grid(face_img, face_boxes, workspace_dirs["face_parts"], "face")
    hair_manifest = save_component_grid(hair_img, hair_boxes, workspace_dirs["hair_parts"], "hair")

    build_icon(base_img, workspace_root / "icon.jpg")

    part_paths = sorted((workspace_root / "parts").rglob("*.png"))
    atlas_path = workspace_dirs["textures"] / "nova_texture_00.png"
    atlas_manifest_path = workspace_dirs["rig_notes"] / "atlas_manifest.json"
    pack_atlas(part_paths, atlas_path, atlas_manifest_path)

    all_manifest = {
        "body": body_manifest,
        "face": face_manifest,
        "hair": hair_manifest,
        "atlas": str(atlas_path),
        "icon": str(workspace_root / "icon.jpg"),
    }
    (workspace_dirs["rig_notes"] / "parts_manifest.json").write_text(
        json.dumps(all_manifest, indent=2), encoding="utf-8"
    )

    for path in [
        clean_targets["base"],
        clean_targets["face"],
        clean_targets["hair"],
        atlas_path,
        workspace_root / "icon.jpg",
    ]:
        target_dir = cubism_dirs["textures"] if path.suffix == ".png" else cubism_root
        (target_dir / path.name).write_bytes(path.read_bytes())

    for part in part_paths:
        rel = part.relative_to(workspace_root / "parts")
        dest = cubism_dirs["parts"] / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(part.read_bytes())


if __name__ == "__main__":
    main()
