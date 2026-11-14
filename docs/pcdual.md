# Dual-monitor IBM PC workstation

Appearance reference: `/disk1/block-dual-monitor-pc.jpg`, preserved unchanged as
`references/ibmpc-dual-photo.jpg`. Supplied detailed reconstruction:
`/disk1/sample_2026-11-09T181906.969.glb`, preserved locally as
`references/ibmpc-dual-reference.glb`, explicitly ignored by Git. Photographer,
license, and reconstruction provenance are not established. Neither the photo
nor the supplied GLB is covered by the repository's source-code license.

## Scope and evidence

Reconstruct the photo's desktop chassis with two black 5.25-inch drive faces,
detached IBM-style keyboard with function block on the left and keypad on the
right, elevated green APL CRT, and a second green graphics CRT to the right.
The original photo crops the right monitor; its complete exterior and hidden rear
fittings are therefore inferred. No internal electronics or adapter circuitry
is claimed. Screen art is redrawn schematic content, not captured software.

The nominal chassis envelope is 500 × 410 × 142 mm, consistent with the 5150
family envelope in IBM's *Personal Computer Family Service Information Manual*,
SA38-0037-00, July 1989 (5150 system-unit specifications):
https://bitsavers.org/pdf/ibm/pc/SA38-0037-00_Personal_Computer_Family_Service_Information_Manual_Jul89.pdf.
Exact chassis variant is not confirmed from the photograph. This envelope is a
modeling constraint, not a measurement of the pictured specimen. Monitors use
provisional 370 × 330 × 290 mm front envelopes, tapering behind the CRTs. Keyboard
width is a provisional 490 mm. Monitor offsets, angles, back contours, and
cabling remain photo/GLB estimates.

## Compact construction

`Pcdual.xtl` / `make-pcdual.xtl` compose the shared utilities with
`scripts/pcdual_scene.py`. Four physical assemblies plus interconnects retain
separate parent frames. Cases have rounded/tapered shells, real recessed bezel
surfaces, curved emissive screen grids, ventilation details, knobs, disk latches,
83 separately constructed caps with one shared legend atlas, and a coiled lead.
Small deterministic artwork is generated with `uv run scripts/make_pcdual_decals.py`.
The user's request to defer lettering is respected: exact glyphs, key outlines,
legends, and screen reproduction are explicitly later work.

Build: `python3 scripts/build.py pcdual --device OPTIX --candidate-only`.
Compare: `python3 scripts/compare.py --model pcdual --candidate <candidate>/pcdual.glb`.
The optional comparison requires the ignored supplied reference at its local path.
The production model builds without that GLB.

## Reviewed baseline and remaining work

Accepted candidate `20261109-092558-339205`: 25,024 triangles, 27 meshes/draws,
1,124,020 bytes. Supplied GLB: one mesh, 285,518 triangles, 304,838 vertices.
Lucy CPU diagnostic of the supplied reference passed in
`work/ibmpc-reference-check/20261109-092045/1/`; normalized diagnostic coordinates
are not used as production dimensions. Production OptiX build, fresh artifacts,
and independent semantic-name / bounds round trip passed. All six orthographic
renders and two perspective renders were reviewed, together with five matched
reference comparisons in `work/comparisons/20261109-092832-pcdual-first/`.

The model retains the arrangement and independent geometry rather than copying
melted keys or missing left-screen lettering from the dense reconstruction.
Remaining mismatches include the second monitor's angle/offset, exact keyboard
well and wide-key profiles, chassis/bezel edge details, screen proportions and
artwork, material wear, and the unseen rear layout. The dense model itself has
approximate dimensions; silhouette overlap is not a historical fidelity score.

## Three-panel preview

`uv run scripts/make_pcdual_comparison.py <comparison-folder>` creates the labeled
photo / supplied detailed GLB / compact Blender model sheet. The photo is kept
unmodified and letterboxed; both model renders use the same perspective camera,
lighting, and exposure from `models/comparison-pcdual.json`. The photograph's
original camera is not calibrated, so its framing does not exactly match those
renders. Files are preserved under the comparison folder, and the preview alias
is `pcdual-three-way.png`. The README uses `images/pcdual-three-way.jpg`.

The interactive fifth tab is `/?model=pcdual`; paired rotation is
`/compare.html?model=pcdual`. The local front render alias is `pcdual-front.png`.
