# Reference refinement record

All run paths below are under ignored `work/`; the source manifests and this
record are versioned. Each comparison uses front, left, right, top, and rear
views with the same alignment, lighting, exposure, and cameras. Scores measure
reference-mask agreement, not historical accuracy.

## Evidence

The four neighboring `*-3D` repositories were surveyed. Lucy supplied the shared
controls, checked Blender runner, and canonical `less-wrong-3d` skill. The 5100's
`docs/less-wrong.md` supplied the one-feature queue, camera matching, source-local
frames, and rollback procedure. The local skill was copied byte-for-byte at the
user's explicit request and is linked by `AGENTS.md`. No pre-existing
`less-worse.md` was located; the requested reusable procedure now lives at the
repository root under that name.

Dense reference originals remain unchanged. The source files are one textured
mesh each, rather than separately named equipment parts. Only diagnostic copies
are cut: the 1053 printer region excludes console context; the 5471 body region
excludes the user-identified hanging underside. The full originals remain in the
comparison viewers.

## IBM 1053

| Pass | Evidence and decision |
|---|---|
| Baseline `20261101-161257-baseline` | 412 meshes, 24,756 triangles, 1,347,176 bytes. Tall shoulder, overly deep case, overly high cover. |
| Shell `20261101-161749-pass1-shell` | Lowered shell, replaced tall shoulder with a thin ledge, tilted fascia and all attached controls in one frame. All five silhouette scores improved. Retained. |
| First printed legends | Geometry lettering was replaced by small print atlases. **Rejected**: UVs appeared rotated/stretched because normal recalculation reordered polygon loops. Anchoring UVs to vertex identity fixed it. |
| Detail `20261101-162250-pass2-detail` | Clear bit labels, wider recessed scale, outlined arrow legends, gray ledge/darker cabinet, and light acrylic tint. Visually checked against photos. |
| First batching `20261101-171843-pass3-compact` | Nodes dropped to 31 but evaluated micro-bevels increased geometry to 35,746 triangles and 1.54 MiB. **Rejected** against budget. |
| Batching correction | Removing tiny bevels initially had no effect because the dependency graph still held the previous evaluated mesh. Explicit dependency-graph update before baking resolved it. Bounds now use actual vertices, avoiding inflated bounds from rotated merged boxes. |
| Accepted `20261101-172933-final1053` | 31 meshes, 55 draw calls, 12,598 triangles, 609,044 bytes. Static groups retain logical-part metadata; sixteen switch actuators remain named nodes. |

| View | Baseline IoU | Accepted IoU |
|---|---:|---:|
| Front | 0.770 | 0.875 |
| Left | 0.669 | 0.844 |
| Right | 0.675 | 0.855 |
| Top | 0.668 | 0.870 |
| Rear | 0.541 | 0.724 |

Remaining mismatch: exact scale, knob placement, cover curvature and transparency,
rear fittings, and contextual remnants in the diagnostic cut. The photos resolve
switches that the dense reference texture does not; they remain modeled. The
orange sticker is excluded.

## IBM 2741

Baseline `20261101-171940-baseline2741`: the old case was too tall, its key field
too wide, and it lacked the loaded-paper configuration. The new reference is
`trellis_output_2026-11-02T021414.glb` (144,046 triangles, 6,549,760 bytes).

Pass `20261101-173227-pass1-2741` lowered and rounded the case, narrowed the key
field, added paper, and introduced an APL atlas. Inspection exposed the typeball
on the shoulder: it was still using the old mechanism's carrier offset. The
correction puts it inside the printer well using an explicit carrier frame.

Accepted `20261101-173758-final2741` also deepens key contrast, replaces a dense
text badge with a print texture, and limits key bevel tessellation. It contains
12 meshes, 14 draw calls, 12,666 triangles, and 607,644 bytes.

| View | Baseline IoU | Accepted IoU |
|---|---:|---:|
| Front | 0.855 | 0.937 |
| Left | 0.733 | 0.876 |
| Right | 0.759 | 0.895 |
| Top | 0.846 | 0.920 |
| Rear | 0.699 | 0.836 |

Remaining mismatch: paper curl, authentic keycap dishing and some APL glyphs,
exact knob axes, rear fittings, and the unverified absolute dimensions. The OEM
desk-terminal envelope is not applied to the desktop shell.

## IBM 5471

Reference: `trellis_output_2026-11-02T023349.glb`, 146,282 triangles and 5,956,332
bytes. The user explicitly identified the hanging underside as anomalous and
requested a clean case more like the 2741. IBM GA21-9103-1, printed pages 8-1 and
8-2 (PDF pages 101/102), confirms the rounded case, clear paper guide, side knob,
44 graphic-key positions, and separate request keys/status indicators.

The production case is rebuilt with shared Selectric helpers and its own keyboard
layout, right-side controls, carrier scale, and enclosure profile. It contains
no extracted dense geometry and no hanging skirt. Accepted comparison:
`20261101-174631-final5471`. Complexity: 12 meshes, 13 draw calls, 11,816 triangles,
566,448 bytes.

This model has no earlier compact baseline, so no before/after score improvement
is claimed. The diagnostic mask excludes the known underside but still contains
imperfect cut edges. Transparent guide differences are not treated as a defect
merely because the generated reference represents the guide as opaque.

Remaining mismatch: absolute scale, guide curvature, cap spacing, knob finish,
rear details, and some simplified case seams. The black front strip and control
identities are cross-checked against the IBM illustration, not copied from blurred
reference texture.

## Runtime review

The main preview loads and switches among all three GLBs. Camera presets,
zoom/reset, render/reference switching, one shared keyboard listener after repeated
switching, 390px layout, and browser console checks pass. The comparison viewer
links orbit in both directions; browser tests capture eight matched azimuths.
Reports and screenshots live in `work/browser-check/` and
`work/comparison-browser-check-MODEL/`.

All accepted builds exited normally, exported complete artifacts, and reimported
their GLBs with matching semantic node identities and vertex bounds. They were
rendered on OptiX. Separate CPU import/render/export and round-trip diagnostics
passed for all three accepted GLBs, using Lucy’s shared runner and four views
per model. Logs are under `work/cpu-check-MODEL/20261101-17532*/`.
