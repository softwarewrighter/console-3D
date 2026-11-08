# Refinement and acceptance

The models target original photos, user-supplied dense reconstructions, and IBM
illustrations. The current workflow is in [../less-worse.md](../less-worse.md).
Absolute enclosure scale remains inferred.

Use meters, Z-up, front −Y, right +X. The preview converts to glTF Y-up once:
`(x,y,z) → (x,z,−y)`. Shared input handling remains in Lucy.

For each change:

1. Name a feature, reference, and measurable acceptance criterion.
2. Match the reference camera before judging geometry. Keep camera, exposure,
   lighting, and render samples fixed between candidates.
3. Compare front, left, right, and top views. Check that related parts remain
   attached under rotation in the exported GLB.
4. Review the fresh report and Blender log. A normal process exit, complete
   artifacts, and successful GLB round-trip are required but do not prove fidelity.
5. Keep improvements without regressions; retain the previous passing output.

## Current limitations and next measurements

- Both enclosures: verify width, depth, height, bevels, and slopes from dimensioned
  drawings or measured hardware. Current values are model assumptions.
- 1053: refine the hollow hood profile, opening, carrier placement, scale, and
  handle against corresponding photo landmarks. The surrounding 1130 display
  and desk are outside this first assembly.
- 2741: the low shell, loaded paper, keyboard proportions, and carrier placement
  have been corrected. Refine paper curvature, APL glyph details, exact knob axes,
  rear fittings, and authentic keycap dishing next.
- 5471: controls follow IBM's manual rather than illegible generated texture.
  The known hanging underside is intentionally excluded; rear details, exact
  key spacing, paper-guide curvature, and physical dimensions remain provisional.
- TRS-80: first four-unit desktop reconstruction is accepted after six production
  views and five reference comparisons. Keyboard width and monitor width are
  museum constrained; expansion shelf profile, precise key spacing, disk latch,
  monitor rear details, and cable routing remain provisional. See [trs80.md](trs80.md).
- Mechanical motion: carrier travel, element tilt/spin, backspace, and return
  are implemented through separate pivots and checked in the browser. Exact
  character-code mapping, print impact and paper feed remain future work;
  see [animation.md](animation.md).

Build outputs are promoted only after complete renders and GLB bounds/identity
checks. Failed candidates and prior outputs remain under `work/ibm*/` for review.
The preview serves only the latest passing output of each model. Use
`--candidate-only`, matched comparisons, and `accept_candidate.py` for new
refinements so visual review happens before promotion.
