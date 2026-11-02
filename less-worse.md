# A feedback loop for compact, faithful equipment models

This is the reusable project procedure requested for this reconstruction. Apply
the local [less-wrong-3d skill](skills/less-wrong-3d/SKILL.md). Lucy remains its
upstream source; the local copy was explicitly requested. This procedure builds
on the [5100's incremental method](../s5100-3D/docs/less-wrong.md) and
[Lucy's evidence and build survey](../lucy-3D/docs/survey.md).

## 1. Define the object, evidence, and budget

Name the exact equipment variant and what is excluded. A reference can contain
more equipment than the target. Here the dense model includes the display and
keyboard; the production asset is only the printer.

Preserve each reference unchanged and record its hash, provenance, view, and
confidence. A dense reconstructed mesh is a useful 3D guide, not a dimensional or
historical authority. Cross-check it against photographs and manuals. For this
printer the photos establish sixteen switches that the dense model barely
resolves. An incidental orange sticker is not console hardware.

Set separate limits for triangles, mesh nodes, draw calls, texture resolution,
file size, and interaction speed. One dense mesh can be cheaper in draw calls
than hundreds of primitive objects. Polygon count alone is not an agility budget.

## 2. Establish and freeze alignment

Record units, axis convention, object scope, reference region, uniform scale,
rotation, and translation. Keep normalization separate from real measurements.
Author in Blender meters, Z-up, front −Y. Viewer conversion is `(x,y,z)→(x,z,−y)`.

Identify at least three landmarks on the target equipment: enclosure corners,
control centers, a cover edge, a knob axis. Fit the camera and uniform reference
transform before judging geometry. Do not deform the reference to fit a candidate.
Freeze the camera, lighting, exposure, and render settings for every comparison.

For a connected superset mesh, either frame the target with cameras or make an
explicit diagnostic region. Do not pretend a coordinate cut is clean component
segmentation. Inspect topology and normals before extracting or repainting parts.
The original full model must remain available for rotation and context.

## 3. Measure the baseline in multiple views

Use front, left, right, top, and rear. Include a turntable or interactive orbit of
both models; defects that hide in front view often appear in depth. Use the same
camera and reference transform for old and new candidates.

Record normalized landmark errors and silhouette agreement per view, alongside
triangle count, mesh nodes, draw calls, bytes, and render/interaction behavior.
Silhouette IoU is `intersection / union` of corresponding masks. It is a geometry
diagnostic, not a fidelity score: contextual fragments, transparency, occlusion,
and the reference's own errors affect it. Do not optimize a cut boundary or a
single view merely to raise a number. Compare materials and readable labels
visually; baked lighting makes raw RGB differences misleading.

## 4. Make one testable change

Prioritize silhouette and proportions, then openings and depth, controls,
materials, legends, and wear. Before editing, state:

```text
Feature: printer cover shoulder
Evidence: reference side views plus original console photos
Expected change: replace tall sloping shoulder with a thin cover ledge
Measurement: height/width and depth/width move toward locked reference landmarks
Acceptance: improves front and both obliques, with no detached controls or rear regression
```

Use one panel frame for attached controls. Apply source transforms once. Avoid
independent guessed coordinates for each detail. Record rejected hypotheses;
after two or three failed attempts, inspect topology or change the construction
approach rather than adding more patches.

## 5. Build candidates without replacing the accepted model

```sh
python3 scripts/build.py 1053 --device OPTIX --candidate-only
python3 scripts/compare.py --candidate work/ibm1053/candidate-TIMESTAMP/ibm1053.glb --label feature
```

Use factory startup, timeout, saved logs, normal process exit, and fresh artifacts.
Candidates contain the generated scene, X_eTaL definition, exports, views, and
report. Comparisons contain the manifest, hashes, matched renders, mask differences,
and metrics. Failed candidates remain inspectable. Pipeline success is necessary
but does not establish visual quality.

## 6. Compare, rotate, and accept explicitly

Review all comparison sheets, the original photographs, and both GLBs under
rotation. Confirm the feature improved, attached parts stay attached, and other
views did not regress. Record remaining mismatches in the acceptance reason.

```sh
python3 scripts/accept_candidate.py work/comparisons/RUN/comparison.json \
  --reason 'Feature, evidence, measured improvement, reviewed views, remaining mismatch'
```

The acceptance tool checks that the compared asset and camera manifest have not
changed, artifacts exist, round-trip passed, and asset budgets hold. It preserves
the previous accepted output. Visual acceptance is the reviewer's judgment, not
something the script infers from an IoU threshold.

The same pipeline now handles the 2741 and 5471 using `--model 2741` or
`--model 5471` with `compare.py`. The 5471 is an example of explicit source-error
handling: retain the original for inspection, exclude the user-identified hanging
underside only in a diagnostic copy, and construct a clean base using the IBM
illustration. Do not optimize a model to reproduce known reference artifacts.

## 7. Compact after the shape is right

Rebuild simple, deliberate surfaces instead of indiscriminately decimating a
textured scan. Merge static surfaces by material or assembly. Keep moving controls
as semantic nodes, with provenance for merged components. Evaluate modifiers
before batching so one part's bevel does not affect another part.

Use small, deterministic printed textures for legends and scales rather than
thousands of tiny glyph triangles. Keep geometry for depth, silhouettes, recesses,
handles, and switch travel. Anchor UVs to vertex identity: recalculating normals
may reorder a polygon's loops. Recheck all views after batching and after export.

## 8. Carry the evidence forward

Save accepted measurements, source hashes, settings, rejected approaches, and
remaining defects with the project. Reuse the controls, process management,
comparison manifest, and acceptance structure on the next piece of equipment.
Reuse geometry only when the hardware part and variant actually match.
