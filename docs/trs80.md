# TRS-80 Model I desktop system

Requested configuration: the photograph on
https://vintagecomputer.com/tandy-trs-80-model-i.html, original image
https://vintagecomputer.com/wp-content/uploads/2011/12/tandy-trs-80-model-I.jpg.
The unmodified image is preserved as `references/trs80-model-i.jpg`.
Photographer and reproduction license are not established. It is modeling evidence,
not an asset covered by the repository's MIT license.

## Evidence and dimensions

The source shows the silver keyboard/CPU, a separate expansion interface under
the monitor, a blank curved CRT, and one upright Mini Disk drive on the right.
The user connected an IBM 5471 to their expansion interface. No 5471 cable adapter
or internal modification is visible in this photo, so none is invented here.

Museums Victoria HT 1839, https://collections.museumsvictoria.com.au/items/280670,
provides keyboard/CPU dimensions 424 × 205 × 85 mm and monitor dimensions
400 × 310 × 280 mm. Those constrain the component envelopes, with front trim and
feet separately modeled. It lists an expansion interface of 424 × 207 × 110 mm;
the model gives it a shallow 66 mm front and a raised 110 mm rear support to
reconcile the visible front with that overall envelope. That rear profile is an
inference, not a verified drawing. The monitor stands above the raised shelf on rubber feet; its shell clears the interface.

Museums Victoria HT 1879, https://collections.museumsvictoria.com.au/items/280994,
lists a 325 × 155 × 90 mm disk enclosure. Rotating this onto its narrow side gives
the pictured upright 90 mm width and 155 mm height. Fine drive latch details and
rear fittings remain provisional, as variants differed.

## Construction and review

`Trs80.xtl` and `make-trs80.xtl` compose the shared Blender utilities with
`scripts/trs80_scene.py`. Geometry stays procedural: separate component frames,
sloping CPU case, individually sculpted keys, shared legend atlas, deep CRT bezel,
convex glass, vents, control knobs, drive door, ribbon cable, and signal cables.
No photographic texture is projected over the machine.

Build candidates with `python3 scripts/build.py trs80 --device OPTIX --candidate-only`.
Run `uv run --with pillow --no-project python scripts/make_trs80_decals.py` if editing
printed artwork. Review front, left, right, top, overview, and keyboard detail
before promoting a candidate. Preserve candidates and record visual observations.
Do not interpret a successful GLB import as visual acceptance.

First-pass acceptance targets: four distinct equipment units; keyboard width
424 mm and monitor width 400 mm; one upright drive; black recessed keyboard with
silver surround and right badge; curved blank CRT with right controls and lower
grille; no solid fill obstructing the CRT; legible badges and consistent keys
in front and both obliques; independent GLB semantic identities and bounds check.


## Accepted first preview

Candidate `20261108-122117-736610` is the first accepted TRS-80 revision.
The failed sandbox GPU attempt is retained; the host OptiX build exited normally.
Production: 33 meshes / 33 draws, 15,298 triangles, 733,460-byte GLB. CPU import,
render, and independent export checks passed in `work/trs80-cpu-check/`.
The original dense reference passed the same CPU diagnostic separately.

Refinements after reviewing the first six renders and the supplied GLB: reduce
CPU front height from 49 to 28 mm, move the monitor/interface/drive group 40 mm
closer to the keyboard, replace CRT bezel corner gaps with a continuous ring,
use black keycaps and dark Enter lettering on ivory, and raise the monitor shell
above the interface shelf. All six final views and five comparison sheets were
reviewed before promotion. Artifacts and acceptance reason are preserved in
`work/comparisons/20261108-122153-trs80-final/` and `work/trs80/out/acceptance.json`.

Remaining mismatch: the procedural enclosures are cleaner and their rear detail
simpler than the dense model. The expansion shelf is an inferred compromise
between a front photograph and a museum envelope; it needs a measured side view.
Exact key legends/positions, CRT coating, and drive latch variant need close-ups.
The reference's trailing rear cables dominate its depth bounds and are not copied
as structural hardware. No numerical silhouette overlap is a fidelity score.


## Cabinet and camera correction

The first front PNG was our procedural model under an orthographic camera, not
the source photo or supplied GLB. The user correctly identified its excessive
rectangular roof band. At raw reference Y=-0.14, 1st–99th percentile roof Z reaches
0.261; at Y=0.20 it reaches 0.187, a 58 mm fall under the 0.79 alignment. Width
stays near 0.505 through the main body and narrows to 0.475 at the rear. These
samples constrain a reconstruction comparison, not original manufacturing data.

The new cabinet uses rounded cross sections, a 400 mm front, 376 mm rear width,
and a roof falling 66 mm to the rear. It replaces the earlier rectangular side
slabs and shallow 10 mm roof fall. Existing orthographic validation cameras and
studio lights are preserved. Additional 60 mm front and 58 mm oblique perspective
cameras serve the presentation images and viewer render modes. The supplied
reference remains local and is explicitly ignored by Git; fresh clones can build
the procedural system without it. Copy the reference to
`references/trs80-reference.glb` only to reproduce the optional comparison.

Accepted cabinet correction: candidate `20261108-123347-979252`; comparison
artifacts `work/comparisons/20261108-123436-trs80-roof/`. Current compact asset:
34 meshes, 14,862 triangles, 711,360 bytes. The prior passing output remains in
`work/trs80/out-before-accepted-*`. Presentation images are now clearly separate
from unchanged orthographic validation views.
