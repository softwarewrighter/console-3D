# Reference evidence

Original source photographs are stored without modification. They are evidence,
not rendered project output, and are not covered by the project's MIT license.

| Local file | Source | Credit / rights | What it establishes |
|---|---|---|---|
| `ibm1130-console.jpg` | [Supplied photograph](https://apaacini.com/IBM-1130_Consola.jpg) | Photographer/license not established; supplied as a modeling reference | Front appearance of the 1053 installation within the IBM 1131 console; transparent hood, turquoise controls, data switches |
| `ibm2741-terminal.jpg` | [Commons original record](https://commons.wikimedia.org/wiki/File:IBM_2741_Communications_Terminal.jpg) | Oscar.nierstrasz, June 13, 2015; [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); unmodified | Desktop APL terminal, top/front enclosure shape, exposed mechanism, keyboard and controls |
| `ibm1130-superset-reference.glb` | `/home/mike/Downloads/sample_2026-11-02T010421.233.glb` | User supplied; reconstruction provenance beyond file metadata unknown | Dense full console; one textured mesh, 286,733 encoded triangles; display and keyboard are comparison context only |
| `ibm2741-reference.glb` | `/home/mike/trellis_output_2026-11-02T021414.glb` | User supplied; dense reconstruction | Complete desktop 2741 with loaded paper; 144,046 encoded triangles |
| `ibm5471-reference.glb` | `/home/mike/trellis_output_2026-11-02T023349.glb` | User supplied; dense reconstruction | System/3 console; 146,282 encoded triangles; known hanging underside artifacts must not be modeled as hardware |
| `ibm5471-manual-page-8-1.png` | [IBM GA21-9103-1, November 1970](https://bitsavers.trailing-edge.com/pdf/ibm/system3/GA21-9103-1_System3_ComponentsRef_Nov70.pdf), PDF page 101, printed page 8-1 | IBM manual scan; unchanged rasterization at 1600px page height | Figure 8-1: clean rounded base, paper guide, printer opening, keyboard, side knob, right control column |
| `ibm5471-manual-figure.jpg` | Crop of the preceding page, pixel rectangle `(130,550,1100,1300)` | Derived crop for preview only; original raster retained | Enlarged manual illustration for the viewer's reference-image mode |

The same IBM manual's printed page 8-2 (PDF page 102), Figure 8-2, establishes
the 5471's 44 graphic keys and separate LOCK, SHIFT, RETURN, END, REQ, CANCEL,
PROCEED, and REQUEST PENDING positions. Control spacing and case dimensions
remain inferred. The reference GLBs are not measurement authorities.

## Measurements

- **1053 installation:** current body width 560 mm and depth 220 mm are provisional
  modeling assumptions. Knobs and the acrylic paper deflector extend beyond the
  body. No printer-only IBM dimension drawing has been verified.
- **2741 desktop shell:** current body width 540 mm and depth 400 mm
  are provisional assumptions. The photographed unit has APL legends. Rear
  enclosure details are not visible and remain inferred.
- **5471 desktop shell:** body width 540 mm and depth 460 mm are provisional.
  The comparison maps the dense reference uniformly to a 560 mm overall envelope
  and places the intended base at source Z=-0.130. The diagnostic region excludes
  vertices below that plane; the original GLB retains all underside artifacts.
- **2740/2741 desk terminal:** IBM OEM Information A27-3002-0, printed page 15,
  Figure 14, specifies 28¾ in width, 25¼ in depth, 36½ in overall height, and
  29 in desktop height. Those dimensions describe the complete desk configuration;
  do not rescale the desktop shell to that envelope.

Manual links and candidate maintenance sources are in the main README. Manual
scans downloaded during research were inspected separately and are not included
in this repository. Preserve publication/page/figure provenance for future
verified measurements.

## 1053 sticker correction

The user identified the orange rectangle across the position scale in the first
photo as an incidental sticker, not console hardware. The additional
[technikum29 console reference](https://www.technikum29.de/en/computer/ibm1130/)
([close-up photo](https://www.technikum29.de/shared/photos/rechnertechnik/ibm-1130-konsole.jpg))
shows the console without it. Removed the modeled orange marker and its material;
the original reference photograph remains unmodified. Acceptance: no orange
marker mesh/material in the exported model, and an unobstructed position scale
in the front and both oblique renders. Switch positions vary between reference
photos and represent operating state rather than fixed enclosure geometry.

## 1053 installation variants

User clarification: the 1053 was used on IBM 1130/1800 systems. The 1130 placed
its toggle switches on the printer front cover; the 1800 placed them on its large
system panel. The current model represents the 1130 installation.

## TRS-80 Model I

`trs80-model-i.jpg` is the unmodified photograph from [Vintage Computer](https://vintagecomputer.com/tandy-trs-80-model-i.html), downloaded 2026-11-08. Photographer and license are not established; it is retained as user-requested modeling evidence. The depicted arrangement, museum measurements, uncertainties, and first-pass acceptance criteria are recorded in [../docs/trs80.md](../docs/trs80.md).

`trs80-reference.glb` is ignored by Git and remains local. It preserves the user-supplied `/home/mike/Downloads/sample_2026-11-08T211606.306.glb` unchanged (286,564 triangles, one mesh). Its reconstruction provenance beyond the supplied file is unknown. Lucy CPU import/render/export diagnostic passed in `work/trs80-reference-check/20261108-121441/1/`; normalization applies only to that diagnostic. See `models/comparison-trs80.json` for the separate physical-scale comparison transform.
