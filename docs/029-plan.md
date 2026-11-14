# IBM 029 keypunch — next equipment study

Status: initial procedural candidate and preview now built after the user expanded the request to three, then four model previews. The checklist below remains the refinement plan; this is not a production-fidelity acceptance. See `equipment-previews.md`.

## Preserved references

- Photo: `/home/mike/Downloads/ibm-029.jpg`, unchanged local copy
  `references/ibm029-photo.jpg`. It depicts the complete freestanding keypunch,
  including desktop, cabinet, legs, card-handling housing, and keyboard.
- Detailed reconstruction: `/home/mike/Downloads/sample_2026-11-10T195726.792.glb`,
  unchanged local copy `references/ibm029-reference.glb`, ignored by Git.
- Photographer, license, and reconstruction origin remain unverified. References
  are modeling evidence, not source-code assets under MIT.

## Separate assemblies

1. Rectangular worktop, thin edge band, overhang and depth.
2. Dark lower equipment cabinet, inset front service door, side sheet panels.
3. Four narrow legs, lower side rails, foot adjustment pads.
4. Tall rear card-handling housing with sloping face and top tray openings.
5. Left supply hopper, central transport/punch station, right output stacker,
   visible card guides and cards, treated as separate geometry.
6. Raised right-hand keyboard/control pod, recessed dark key bed and individual
   light keycaps; small legends deferred until silhouette is established.

## Build and evidence sequence

Inspect the complete GLB with Lucy's isolated CPU diagnostic, preserving logs,
four renders and round-trip result. Establish orientation and region landmarks
without treating the diagnostic normalization as physical dimensions. Seek IBM
029 drawings/manual dimensions before asserting physical scale; initially label
width, depth and desktop height as inferred. Keep the photographed 029 variant
separate from the IBM 026 or later keypunch arrangements.

Implement `Ibm029.xtl`, `make-ibm029.xtl`, and a dedicated `scripts/keypunch_scene.py`
using the existing X_eTaL/Blender export pipeline. Add an independent `029` viewer
entry with cameras centered on the taller freestanding machine; do not use the
Selectric animation controls for the keypunch. Keep original photo and supplied
GLB available beside the compact asset through clearly labeled reference views.

## Measurable acceptance targets

- Complete silhouette includes the tabletop, rear housing, lower cabinet,
  four legs, side rails and keyboard pod; no floor mesh in the equipment export.
- Table overhang, leg spacing, cabinet/top ratios, keyboard offset and tray
  positions match the selected photo landmarks, recorded before refinement.
- Front, both obliques, top and rear renders retain all structural attachments.
- Target 30,000 triangles, fewer than 70 mesh nodes, and under 1.5 MiB GLB;
  record actual cost and justify exceptions rather than decimating blindly.
- Independent GLB import retains semantic parts and bounds. Compare matched
  renders, then inspect eight synchronized orbit angles in the browser.
- Produce a labeled original photo / supplied detailed model / compact model
  comparison. Preserve source artifacts and previous passing revisions.

## Open questions for refinement

Exact dimensions, concealed rear service layout, authentic hopper and transport
geometry, leg cross sections, keyboard layout, and card stock/printing require
closer reference evidence. The black-and-white photo constrains relative tones,
not original paint colors. No card-feed or punch animation is implied by this
initial exterior modeling pass.


## Columbia-photo correction, November 2026

The original solid ramp and flat card-frame slabs were rejected by the user.
The replacement is in `scripts/keypunch_scene.py`: open horizontal card route,
left stacker and right hopper, split upper covers, pressure rollers and guides,
program drum visible through a raked inspection port, and 49 keycaps traced from
48 numbered positions plus the space bar in IBM manual Figure 8. The source's
64 characters are a repertoire, not a claim of 64 physical keys.

Follow-up corrections at user direction: switch-panel vertical span 120 → 85 mm,
backward rake 20.6 → 27.9 degrees, inspection face raked 12 degrees, and a shallow
full-width rear cabinet. Its modeled depth is 190 mm under a 760 mm tabletop,
leaving 570 mm nominal open depth (75%) for the operator. The keyboard and head
no longer overlap; the exported geometry has about 39.9 mm clear gap, and support
feet touch the tabletop. These are model design clearances, not manufacturer
measurements. No deep left cabinet remains beneath the operator's legs.

The old GLB and generated source remain in `work/029-refinement/baseline/`.
The current reviewed revision is `candidate-20261114-133721-023757`. Eight renders
and independent export/bounds checks pass. `scripts/check_029_clearance.py`
casts horizontal rays through the knee volume: baseline has 15 blocked samples,
revised has zero. It also verifies the keyboard/head gap and support-foot height.

Comparison: `/029-comparison/`, modeled after the sibling 5100 workflow.
`models/029-photo-cameras.json` is frozen across old and revised GLBs. Manual
photo camera uses the unchanged desktop/foot points only (14.6 px coordinate RMS).
The color close-up is approximate framing. Upper-head proportions and camera
residuals remain; the manual view clips the modeled upper head, shown explicitly
rather than hidden with independent model crops. The page includes overlay
controls, complete studio views, source links, complexity, hashes, and limitations.
