# Cubism rigging checklist

## Import PSD/assets

- [ ] Build a layered PSD from `../parts/` with one merged layer per part.
- [ ] Keep all layer names unique.
- [ ] Confirm the PSD is RGB / sRGB.
- [ ] Remove dust, stray alpha islands, and path data before import.
- [ ] In Cubism Editor, import the PSD by drag/drop or `File > Open`.
- [ ] Choose `Create new model from PSD file`.

## Verify layer order

- [ ] Confirm the Parts palette matches the intended body / face / hair hierarchy.
- [ ] Confirm back hair stays behind the head and front bangs stay in front.
- [ ] Confirm crown stays above the hair stack.
- [ ] Confirm eyes, brows, and mouth are above the head base where expected.

## Create/edit ArtMeshes

- [ ] Inspect all imported ArtMeshes after PSD import.
- [ ] Remember imported ArtMeshes start with a minimal mesh.
- [ ] Tighten face meshes around eyelids, irises, mouth, and bangs.
- [ ] Add denser mesh only where deformation needs it.
- [ ] Keep large flat regions light to avoid unnecessary point count.

## Build deformer hierarchy

- [ ] Create the base hierarchy from `deformer_tree.json`.
- [ ] Use warp deformers for broad bending and perspective-style shape shifts.
- [ ] Use rotation deformers where a clean pivot is more important than a squashy warp.
- [ ] Parent face and hair groups so head turn propagation is easy to test.

## Rig Angle X first

- [ ] Create `ParamAngleX` with `-30 / 0 / 30`.
- [ ] Block the head turn using head, face, and hair groups first.
- [ ] Keep the body mostly still during the first head pass.
- [ ] Test silhouette, eye spacing, bangs overlap, and crown placement at all three keys.

## Rig Angle Y/Z

- [ ] Add `ParamAngleY`.
- [ ] Add `ParamAngleZ`.
- [ ] Rebalance brow, eyelid, and jaw spacing at up/down angles.
- [ ] Add only mild body compensation until underlap cleanup is done.

## Rig eyes

- [ ] Create left and right eye groups.
- [ ] Rig open, blink, and smile eye states.
- [ ] Add iris movement under eye parent groups.
- [ ] Verify the blink holds shape at all Angle X keys.

## Rig mouth

- [ ] Create `ParamMouthOpenY`.
- [ ] Create `ParamMouthForm`.
- [ ] Place the neutral smile line and the A / I / U / E / O mouth shapes.
- [ ] Verify mouth shapes still read well after head-angle deformation.

## Add expressions

- [ ] Add brow variation keys.
- [ ] Add smile / neutral / tension variants.
- [ ] Save expressions only after the base blink and mouth setup are stable.

## Add physics

- [ ] Add light physics to side locks first.
- [ ] Add subtle secondary motion to front hair.
- [ ] Add crown motion only if it improves the model instead of making it floaty.
- [ ] Keep physics off torso/limb first-pass pieces until underlaps are cleaned.

## Export for VTube Studio

- [ ] Save the Cubism project before export.
- [ ] Export a real Cubism embedded-use model from Cubism when rigging is ready.
- [ ] Confirm the export includes the real `.moc3`, `.model3.json`, textures, and optional physics files.
- [ ] Copy the exported model folder into the VTube Studio model location.
- [ ] Test tracking, blink, mouth, draw order, and physics in VTube Studio.
