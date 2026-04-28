# Angle X first pass

Goal: get Nova's head turn working on `ParamAngleX` before touching full body motion.

Target save name for this milestone: `nova_v01_head_angle_x.cmo3`

## 1. Open Cubism Editor

1. Launch `CubismEditor5.exe`.
2. Start a new modeling session.
3. If you already have a working project file, open it instead of starting over.

## 2. Import the layered source

1. Prepare a layered PSD built from `../parts/`.
2. In Cubism, drag the PSD into the Modeling workspace or use `File > Open`.
3. In the model settings dialog, choose `Create new model from PSD file`.
4. Wait for the PSD layers to become ArtMeshes.

## 3. Confirm the imported ArtMeshes

1. Open the Parts palette and Deformer palette.
2. Verify the head, face, hair, and crown layers all imported.
3. Click through the ArtMeshes and confirm draw order is sane.
4. Remember that imported ArtMeshes start with a minimal mesh.
5. Before heavy deformation, refine the mesh on:
   - head base
   - front bangs
   - side locks
   - eyes
   - mouth

## 4. Create the head parent deformer

1. Select the head-related ArtMeshes:
   - `head_base`
   - front hair
   - back hair
   - side locks
   - neck hair
   - crown if you want it to follow the head immediately
2. Create a warp deformer around the whole head group.
3. Name it `Head_ALL`.
4. Resize the warp so it fully contains the selected head content with a little margin.

## 5. Create head rotation / angle deformers

1. With `Head_ALL` selected, create a child rotation deformer.
2. Name it `Head_AngleX_Rot`.
3. Place the rotation origin near the base of the neck.
4. Create a child warp deformer for broad head-shape adjustments.
5. Name it `Head_XYZ_Warp`.
6. Put the face and hair feature groups under the head turn stack so they are easy to edit together.

Suggested grouping:

- `Head_ALL`
  - `Head_AngleX_Rot`
    - `Head_XYZ_Warp`
      - head base
      - face groups
      - hair groups

## 6. Add `ParamAngleX`

1. Open the Parameter palette.
2. Create a new parameter named `ParamAngleX` if it does not already exist.
3. Set:
   - minimum: `-30`
   - default: `0`
   - maximum: `30`
4. Add keyforms at:
   - `-30`
   - `0`
   - `30`

## 7. Block the left and right turns

At `0`:

1. Restore the neutral front view.
2. Confirm all head parts align before editing side keys.

At `-30`:

1. Rotate / warp the head slightly toward camera-left.
2. Shift the nearer eye, brow, and cheek mass slightly outward.
3. Compress the far eye spacing slightly.
4. Pull front bangs so they keep covering the forehead naturally.
5. Move the far side lock inward and the near side lock outward.
6. Keep the crown centered on the skull volume, not floating above the old front view.

At `30`:

1. Mirror the same logic toward camera-right.
2. Re-check overlap order between bangs, side locks, and crown.
3. Re-check iris placement if the eye whites feel too flat.

## 8. Move face and hair features manually

Adjust at all three keys as needed:

- brows
- open-eye shapes
- closed-eye shapes
- smiling-eye shapes
- irises
- mouth anchor
- front bangs
- side locks
- back hair silhouette
- crown

Do not worry about perfect mouth phonemes yet. This pass is only about head turn readability.

## 9. Test motion

1. Scrub `ParamAngleX` slowly from `-30` to `30`.
2. Check for:
   - collapsing face width
   - shrinking caused by overusing warp on rotation-heavy motion
   - bad eye spacing
   - side-lock clipping
   - crown drift
3. If the turn looks too squashy, lean more on the rotation deformer and less on extreme warp deformation.

## 10. Save milestone

1. Save the Cubism project as `nova_v01_head_angle_x.cmo3`.
2. Keep this version as the first stable head-turn checkpoint before adding eyes, mouth, or physics.
