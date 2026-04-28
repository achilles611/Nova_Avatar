from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent
RIG_NOTES = ROOT / "rig_notes"

REQUIRED_FILES = [
    ROOT.parent / "README.md",
    ROOT.parent / "TODO.md",
    ROOT.parent / "nova_vts_export_checklist.txt",
    ROOT / "build_nova_assets.py",
    ROOT / "generate_contact_sheets.py",
    ROOT / "part_manifest.json",
    ROOT / "icon.jpg",
    ROOT / "reference" / "nova_reference.png",
    ROOT / "generated" / "nova_base_chroma.png",
    ROOT / "generated" / "nova_face_sheet_chroma.png",
    ROOT / "generated" / "nova_hair_sheet_chroma.png",
    ROOT / "textures" / "nova_base_fullbody.png",
    ROOT / "textures" / "nova_face_sheet.png",
    ROOT / "textures" / "nova_hair_sheet.png",
    ROOT / "textures" / "nova_texture_00.png",
    RIG_NOTES / "atlas_manifest.json",
    RIG_NOTES / "parts_manifest.json",
    RIG_NOTES / "rig_plan.md",
    RIG_NOTES / "cubism_rigging_checklist.md",
    RIG_NOTES / "angle_x_first_pass.md",
    RIG_NOTES / "deformer_tree.json",
    RIG_NOTES / "parameters.json",
]

EXPECTED_DIMENSIONS = {
    "reference/nova_reference.png": (800, 1200),
    "generated/nova_base_chroma.png": (887, 1774),
    "generated/nova_face_sheet_chroma.png": (1536, 1024),
    "generated/nova_hair_sheet_chroma.png": (1536, 1024),
    "textures/nova_base_fullbody.png": (887, 1774),
    "textures/nova_face_sheet.png": (1536, 1024),
    "textures/nova_hair_sheet.png": (1536, 1024),
    "textures/nova_texture_00.png": (4096, 4096),
    "icon.jpg": (512, 512),
}

EXPECTED_ALPHA = [
    ROOT / "textures" / "nova_base_fullbody.png",
    ROOT / "textures" / "nova_face_sheet.png",
    ROOT / "textures" / "nova_hair_sheet.png",
    ROOT / "textures" / "nova_texture_00.png",
]

ALLOWED_CATEGORIES = {"body", "face", "hair", "accessory", "guide"}
ALLOWED_PRIORITIES = {"high", "medium", "low"}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        try:
            return str(path.relative_to(ROOT.parent))
        except ValueError:
            return str(path)


def report(ok: bool, message: str) -> bool:
    print(f"[{'PASS' if ok else 'FAIL'}] {message}")
    return ok


def check_exists(path: Path) -> bool:
    return report(path.exists(), f"Exists: {rel(path)}")


def check_dimensions(path: Path, expected: tuple[int, int]) -> bool:
    with Image.open(path) as img:
        actual = (img.width, img.height)
    return report(actual == expected, f"Dimensions {rel(path)} == {expected}, actual {actual}")


def has_transparency(path: Path) -> tuple[bool, str]:
    with Image.open(path) as img:
        if "A" in img.getbands():
            alpha = img.getchannel("A")
            extrema = alpha.getextrema()
            if extrema is None:
                return False, "missing alpha extrema"
            min_alpha, max_alpha = extrema
            return min_alpha < 255 and max_alpha > 0, f"alpha extrema {extrema}"
        if "transparency" in img.info:
            return True, "palette transparency info present"
    return False, "no alpha channel"


def check_alpha(path: Path) -> bool:
    ok, detail = has_transparency(path)
    return report(ok, f"Transparency {rel(path)} ({detail})")


def load_json(path: Path) -> tuple[bool, object | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        report(False, f"JSON parse failed for {rel(path)}: {exc}")
        return False, None
    report(True, f"JSON parses: {rel(path)}")
    return True, data


def check_part_counts() -> list[bool]:
    results = []
    expected_counts = {"body": 10, "face": 20, "hair": 6}
    for category, expected in expected_counts.items():
        count = len(list((ROOT / "parts" / category).glob("*.png")))
        results.append(report(count == expected, f"Part count {category} == {expected}, actual {count}"))
    return results


def check_manifest(manifest_path: Path) -> list[bool]:
    ok, data = load_json(manifest_path)
    if not ok or not isinstance(data, dict):
        return [False]

    parts = data.get("parts")
    results = [report(isinstance(parts, list), "part_manifest.json contains a parts list")]
    if not isinstance(parts, list):
        return results

    seen_ids: set[str] = set()
    for part in parts:
        if not isinstance(part, dict):
            results.append(report(False, "part_manifest entry is an object"))
            continue
        part_id = part.get("id")
        source = part.get("source_file")
        category = part.get("category")
        priority = part.get("rig_priority")
        needs_cleanup = part.get("needs_underlap_cleanup")
        results.append(report(isinstance(part_id, str) and bool(part_id), f"Manifest entry id present: {part_id}"))
        if isinstance(part_id, str) and part_id:
            results.append(report(part_id not in seen_ids, f"Manifest id unique: {part_id}"))
            seen_ids.add(part_id)
        results.append(report(category in ALLOWED_CATEGORIES, f"Manifest category valid for {part_id}: {category}"))
        results.append(report(priority in ALLOWED_PRIORITIES, f"Manifest priority valid for {part_id}: {priority}"))
        results.append(report(isinstance(needs_cleanup, bool), f"Manifest cleanup flag boolean for {part_id}"))
        if isinstance(source, str):
            source_path = ROOT / source
            results.append(report(source_path.exists(), f"Manifest source exists for {part_id}: {source}"))
        else:
            results.append(report(False, f"Manifest source_file string present for {part_id}"))
    return results


def main() -> int:
    checks: list[bool] = []

    print("Nova asset validation")
    print("=====================")

    for path in REQUIRED_FILES:
        checks.append(check_exists(path))

    for relative_path, expected in EXPECTED_DIMENSIONS.items():
        checks.append(check_dimensions(ROOT / relative_path, expected))

    for path in EXPECTED_ALPHA:
        checks.append(check_alpha(path))

    for path in sorted(ROOT.rglob("*.json")):
        ok, _ = load_json(path)
        checks.append(ok)

    checks.extend(check_part_counts())
    checks.extend(check_manifest(ROOT / "part_manifest.json"))

    all_ok = all(checks)
    print("=====================")
    print("OVERALL:", "PASS" if all_ok else "FAIL")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
