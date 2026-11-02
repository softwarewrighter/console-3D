---
name: less-wrong-3d
description: Reconstruct and incrementally refine Blender hardware models against photos, drawings, and measured dimensions, including Lucy racks and IBM 1130/5100 models. Use for reference matching, geometry or material refinement, and render/export validation.
---

Keep an evidence trail from reference to geometry to render. A successful export does not establish visual accuracy.

- Identify the exact hardware variant before borrowing dimensions or front-panel layouts. Lucy's server generation alone does not identify DL360/DL380, chassis height, drive cages, or rack position. Label inferred dimensions and unverified parts. Never represent an invented rack population as either observed Lucy version.
- Record reference provenance, view, dimensions, and confidence. Generated illustrations and Trellis meshes are reconstruction aids, not primary evidence. Keep source photos unmodified; create comparison artifacts separately.
- Use meters, Blender Z-up, front −Y, right +X. glTF/viewer maps `(x,y,z)` to `(x,z,-y)`. Vertical viewer pan changes only target Y. Match named cameras to references before editing geometry. Preserve camera transforms, lens, exposure, lighting, and render settings between candidates.
- Prioritize silhouette and scale, then panel openings and part depth, then materials, labels, and wear. State one measurable acceptance criterion per change. Anchor derived parts in the source object's local frame and apply its transform once. Inspect topology before classifying faces; broad coordinate masks can paint unrelated surfaces.
- Save the previous passing revision. Render front and both obliques; add top/rear views when depth or cabling matters. Compare corresponding landmarks and silhouettes, then inspect the GLB after export and rotation. Report the feature, measurement, evidence, and remaining mismatch. A front-only match is insufficient.
- Keep a candidate only when the intended feature improves without regression in other validation views. After repeated failed coordinate guesses, inspect the mesh or change the modeling approach.
- Use the shared `scripts/check_blender.py` from the Lucy checkout for isolated Blender import/render/export diagnostics. It normalizes a diagnostic copy: never treat those normalized bounds as physical dimensions. Keep production coordinates separate.
- Prefer factory-startup batch processes with `--python-exit-code 1`, `-noaudio`, bounded execution, fresh output directories, saved logs, and checked artifacts. Test CPU and intended GPU separately. Missing NVIDIA device nodes inside an agent sandbox do not establish a broken host driver; check outside the sandbox before recommending host changes.
- All three viewers use `shared/viewer-controls.js`: W/S zoom, A/D or left/right orbit, up/down elevation, I/K vertical pan, Space rotation, R reset. Use one keyboard listener; put model-specific cameras and mechanical actions in configuration.

The canonical source is `lucy-3D/skills/less-wrong-3d`; maintain one source rather than divergent per-project skills. See `lucy-3D/docs/survey.md` for the current evidence and build limitations.
