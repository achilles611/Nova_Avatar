Nova rig starter plan

This folder is a rigging source pack, not a finished Live2D export.
It gives you clean transparent source art, a starter atlas, and a first-pass part breakdown for Cubism.

Core source files
- `textures/nova_base_fullbody.png`: transparent clean full-body reference.
- `textures/nova_face_sheet.png`: transparent facial parts sheet.
- `textures/nova_hair_sheet.png`: transparent hair and crown sheet.
- `textures/nova_texture_00.png`: packed starter atlas preview.
- `icon.jpg`: selector icon candidate.

Suggested Cubism hierarchy
- Root
- Body
- `torso_base`
- `left_arm_base`
- `right_arm_base`
- `left_hand_base`
- `right_hand_base`
- `left_leg_base`
- `right_leg_base`
- `left_shoe_base`
- `right_shoe_base`
- Head
- `head_base`
- Hair
- `hair_r01_c01` = back hair mass
- `hair_r01_c02` = front bangs
- `hair_r01_c03` = crown
- `hair_r02_c01` = left side lock
- `hair_r02_c02` = right side lock
- `hair_r03_c01` = lower neck/back hair
- Face
- `face_r02_c01` through `face_r02_c04` = open-eye set
- `face_r03_c01` and `face_r03_c02` = closed-eye set
- `face_r05_c01` and `face_r05_c02` = iris pieces
- `face_r07_c01` through `face_r07_c05` = mouth set
- Brows
- `face_r01_c01` through `face_r01_c04`
- `face_r04_c01` and `face_r04_c02`
- Misc
- `face_r06_c01` = small smile line

Suggested first rig pass
1. Build the body as a simple torso + arms + legs hierarchy.
2. Use `head_base` as the anchor for face and hair.
3. Place `hair_r01_c01` behind `head_base`.
4. Place `hair_r01_c02` in front of `head_base`.
5. Parent side locks and neck hair under the head angle deformers.
6. Use `face_r03_*` for blink swap/deform targets.
7. Use `face_r05_*` for eye-ball movement.
8. Use `face_r07_*` for mouth form/open toggles.
9. Add light physics to side locks and crown only after the base head turns look stable.

Important limitations
- The body parts are starter crops from generated art, not hand-painted hidden-underneath redraws.
- The face and hair sheets are much better suited to animation than the torso and limbs.
- Cubism should generate the final export atlas from the imported parts; the included starter atlas is mostly for organization and reference.
