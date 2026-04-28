# Nova Avatar

Nova Live2D starter pack for Live2D Cubism and VTube Studio.

## Current status

This repository contains a starter art pack and rigging prep assets for Nova. It is not a finished Cubism rig, not a `.moc3`, and not a VTube Studio-ready export yet.

The repo is meant to remove as much prep work as possible before manual Cubism rigging:

- cleaned transparent source textures
- split body / face / hair parts
- starter texture atlas
- rig notes
- deformer and parameter specs
- validation and contact-sheet scripts

Important warning: the torso and limb crops are first-pass slices from generated art. They are good enough to block in hierarchy and early motion tests, but they still need hidden-underlap cleanup or redraw before strong torso turns, arm bends, and polished body motion.

## Repo map

```text
Nova_Avatar/
  README.md
  TODO.md
  nova_vts_export_checklist.txt
  nova_live2d/
    build_nova_assets.py
    validate_assets.py
    generate_contact_sheets.py
    part_manifest.json
    icon.jpg
    generated/
      nova_base_chroma.png
      nova_face_sheet_chroma.png
      nova_hair_sheet_chroma.png
    reference/
      nova_reference.png
    textures/
      nova_base_fullbody.png
      nova_face_sheet.png
      nova_hair_sheet.png
      nova_texture_00.png
    parts/
      body/ (10 PNGs)
      face/ (20 PNGs)
      hair/ (6 PNGs, including crown accessory)
    rig_notes/
      rig_plan.md
      cubism_rigging_checklist.md
      angle_x_first_pass.md
      deformer_tree.json
      parameters.json
      atlas_manifest.json
      parts_manifest.json
```

## Asset inventory

- Reference art
  - `nova_live2d/reference/nova_reference.png`
- Raw generated chroma-key sheets
  - `nova_live2d/generated/nova_base_chroma.png`
  - `nova_live2d/generated/nova_face_sheet_chroma.png`
  - `nova_live2d/generated/nova_hair_sheet_chroma.png`
- Cleaned transparent working textures
  - `nova_live2d/textures/nova_base_fullbody.png`
  - `nova_live2d/textures/nova_face_sheet.png`
  - `nova_live2d/textures/nova_hair_sheet.png`
  - `nova_live2d/textures/nova_texture_00.png`
- Split rigging parts
  - `nova_live2d/parts/body/` - 10 parts
  - `nova_live2d/parts/face/` - 20 parts
  - `nova_live2d/parts/hair/` - 6 parts
- Metadata / planning
  - `nova_live2d/part_manifest.json`
  - `nova_live2d/rig_notes/atlas_manifest.json`
  - `nova_live2d/rig_notes/parts_manifest.json`
  - `nova_live2d/rig_notes/deformer_tree.json`
  - `nova_live2d/rig_notes/parameters.json`
  - `nova_live2d/rig_notes/rig_plan.md`
  - `nova_live2d/rig_notes/cubism_rigging_checklist.md`
  - `nova_live2d/rig_notes/angle_x_first_pass.md`
- Utility scripts
  - `nova_live2d/build_nova_assets.py`
  - `nova_live2d/validate_assets.py`
  - `nova_live2d/generate_contact_sheets.py`

## Fastest next path into Cubism

Live2D Cubism imports PSDs by drag/drop or `File > Open`, and imported PSD layers become ArtMeshes. Imported ArtMeshes start with a minimal mesh, so mesh cleanup still needs to happen inside Cubism.

Because this repo currently stores split PNG parts rather than a layered PSD, the fastest manual path is:

1. Build a layered import PSD from `nova_live2d/parts/`.
2. Use one unique layer name per part.
3. Keep each part merged as a single layer in the PSD.
4. Keep the PSD in RGB / sRGB.
5. Remove dust, stray transparency islands, and path data before import.
6. Import the PSD into Cubism with drag/drop or `File > Open`.
7. Choose `Create new model from PSD file`.
8. Verify layer order in the Parts palette and draw order on canvas.
9. Edit ArtMeshes before heavy deformation work.
10. Build the deformer hierarchy from `nova_live2d/rig_notes/deformer_tree.json`.
11. Create parameters from `nova_live2d/rig_notes/parameters.json`.
12. Rig `ParamAngleX` first using `nova_live2d/rig_notes/angle_x_first_pass.md`.
13. Clean torso / limb underlaps before committing to body turns and arm motion.
14. Add blink, mouth, expressions, then physics.
15. Export a real Cubism model for VTube Studio only after manual rigging is complete.

## Manual Cubism steps

### PSD prep

- Use the split PNGs under `nova_live2d/parts/` as PSD layers.
- Keep every layer name unique.
- Merge line / fill / clipping information down so each imported part is one layer.
- Do not flatten the whole character into one image.
- Do not use the starter atlas as the import PSD.

### First rigging focus

- Head turn on `ParamAngleX`
- Eye open / blink states
- Iris placement
- Mouth open / form
- Hair grouping and light physics

### Body caution

The face and hair pack are closest to rig-ready. The torso and limb pieces are useful for hierarchy layout and early motion blocking, but they still need redraw-underlap cleanup at:

- jacket front overlap
- sleeve to torso joins
- wrist to cuff joins
- pant overlap near hips
- upper leg coverage under jacket hem

## Validation and derived outputs

- Run `python nova_live2d/validate_assets.py` before rigging or committing structural changes.
- Run `python nova_live2d/generate_contact_sheets.py` to generate visual review sheets in `nova_live2d/contact_sheets/`.
- `build_nova_assets.py` rebuilds the split parts, icon, and starter atlas from the generated source sheets.

## VTube Studio note

This repo prepares Cubism input assets. It does not claim to produce a finished `.moc3`, completed Cubism rig, or final VTube Studio export by itself.
