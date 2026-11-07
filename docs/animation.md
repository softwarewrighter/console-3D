# Program-controlled Selectric mechanism

Open [the animation viewer](http://127.0.0.1:5803/animate.html?model=2741).
On Linux, run `just view-animate` to open that page in the configured
ANGLE/SwiftShader Chromium window. A tab in another browser window does not
inherit those launch settings.
Implementation order is 2741, 1053, then 5471. Each model uses the same queued
controller and independently exported carrier, tilt, and spin pivots.

The main preview's **Animate the type element** link opens the selected model.
Choose **Mechanism close-up** to follow the carrier; **Overview** and **Top**
show its movement across the machine. Pointer orbit disables following. Manual
controls and the editable JSON program use the same public API.

## JavaScript API

The loaded machine is available as `window.selectric`:

```js
await selectric.select({tilt: 12, rotate: 65, duration: 200});
await selectric.advance(5, {duration: 500});
await selectric.backspace(2, {duration: 250});
await selectric.carriageReturn({duration: 700});
```

Queue a complete program:

```js
await selectric.run([
  {op: 'select', tilt: -12, rotate: -65, duration: 250},
  {op: 'advance', columns: 1},
  {op: 'select', tilt: 4, rotate: 35},
  {op: 'advance', columns: 1},
  {op: 'backspace', columns: 1},
  {op: 'select', tilt: 12, rotate: 120},
  {op: 'advance', columns: 1},
  {op: 'wait', duration: 400},
  {op: 'return', duration: 700}
]);
```

Commands run in order, including separate API calls made while motion is active.
Angles are absolute degrees and selection takes the short angular path. Durations
are milliseconds; `0` applies a pose immediately. `columns` is a positive integer.
Backspace stops at the left margin; advance beyond the right margin rejects the
command. A return preserves the selected element orientation and moves only the
carrier. It does not move the whole printer or advance the paper.

`selectric.stop()` cancels active and queued motion, settling at the nearest
column. Its interrupted promise rejects with `name === 'AbortError'`.
`selectric.reset()` stops motion and sets column, tilt, and rotation to zero.
`selectric.state` returns `{column, tilt, rotate, busy}`; the column is fractional
during travel. Catch rejected promises when calling the API from your code.

Switch machines programmatically with
`await window.loadSelectricModel('1053')`. It disposes the previous controller,
cancels its work, and returns the new controller. The renderer-independent
`SelectricMachine` class can also be imported from `web/selectric-machine.mjs`
and connected to another renderer with an `applyPose` callback.

## Asset contract

The GLB contains this hierarchy:

```text
console root
├─ static enclosure, platen, rails, keyboard, controls
└─ selectric_carrier              translation along +X
   ├─ moving carrier assembly
   └─ selectric_tilt              rotation about local X
      └─ selectric_spin           rotation about local Y in glTF
         └─ type element assembly (ball, cap, raised type blocks)
```

`mechanism.json` beside each GLB provides the node names, column range, pitch,
left-margin X, rest X, and tilt limit. Blender uses Z-up; the exported glTF uses
Y-up. The spin axis therefore becomes local Y. World transforms are preserved
when parenting, and compaction merges geometry only within the same parent.
The shell and guide rails stay static while the carrier moves; the ball and its
cap tilt and spin together.

Default pitch is 0.00254 m (10 CPI), with travel coordinates matching the modeled
scales. The ±20° tilt range and motion timings are illustrative. Exact type-element
font coding, character-to-angle tables, print impact, ribbon movement, paper
printing, and line feed are not simulated in this first mechanism controller.

## Validation

`node scripts/test-selectric.mjs` checks queue ordering, margins, invalid programs,
interpolation, cancellation, reset, disposal, and short-path rotation with a
deterministic clock. `python3 scripts/check_animation.py` uses Chromium to check
the actual GLB hierarchy and transforms, correction/return sequences, stop,
the full demo, mobile layout, and browser errors for all three models.

The runtime uses pinned Three.js r170 modules stored locally under `web/vendor/`.
It uses Lucy's shared camera input handler once, through an adapter. There is no
dependency on model-viewer's private scene internals. See Three.js's official
[Object3D documentation](https://threejs.org/docs/pages/Object3D.html) and
[GLTFLoader documentation](https://threejs.org/docs/pages/GLTFLoader.html).

Validated on all three exported models: actual type-element geometry follows
the carrier, the console root stays fixed, tilt/spin transforms match commands,
backspace/return and stop work, the demo completes, and the mobile layout has
no overflow or severe browser errors. Reports and screenshots are in
`work/animation-browser-check/`. All three OptiX builds passed; a separate CPU
import/render/export diagnostic of the 2741 rig passed in
`work/animation-cpu-check/20261106-160706/`.

Playback controls sit directly above the model. **Run typing loop**, **Pause/Resume**,
**Stop**, and **Reset mechanism** remain beside the result; the JSON editor is
collapsed by default. Its **Run and view** button scrolls back to the model.
Click the model before using camera keyboard shortcuts.

The viewer renders on demand. When motion and camera rotation stop, it schedules
no recurring work. Playback defaults to 20 fps and a 100,000-pixel render budget;
Light uses 12 fps / 60,000 pixels and Detail uses 30 fps / 220,000 pixels.
The shared scheduler leaves at least 16 ms, or half the previous frame's work time,
between updates, so slow software rendering reduces its frame rate automatically.
Hidden tabs and offscreen stages suspend playback and rendering, preserving motion
time so returning to the model resumes where it paused. Camera rotation starts
only when explicitly requested with Space while the model has focus.

`python3 scripts/check_animation_idle.py` checks idle frame counts, pause/resume,
hidden-tab suspension, pixel budget, and simultaneous visibility of Run and the
model at 1280 × 800. `window.selectricRenderStats` exposes scheduler diagnostics.

Animation uses textured unlit shading to keep software rendering responsive.
Use the static viewer to inspect the full physical materials and reflections.


The primary **Run typing loop** button repeats a 13-character-per-second typing
cycle across one third of the available carrier travel, followed by a 350 ms
return and 120 ms linefeed. The paper strip displays sample text and scrolls it
upward during linefeed; this is a separate output visualization, not ink or paper
motion in the GLB. Character selection angles remain illustrative. The JSON
editor's **Run and view** runs its finite command sequence instead.

`selectric.typeContinuously({cps: 13, columns: 43, onPrint: sample => {}})` exposes
the loop under program control. `selectric.typing` reports the current line,
character count, phase, and feed position. Stop cancels it like any queued program.
The loop samples elapsed active time directly to avoid accumulating per-command
frame delays. GPU completion is included in frame cost to prevent queued renders
from hiding actual display delays.

`just serve` binds to `0.0.0.0:5803`; open `http://<server-LAN-IP>:5803/animate.html`
from another computer to render locally instead of through Remote Desktop.
