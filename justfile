set positional-arguments

default:
    @just --list

setup:
    bash scripts/setup.sh

render:
    python3 scripts/build.py all

render-1053:
    python3 scripts/build.py 1053

render-2741:
    python3 scripts/build.py 2741

render-5471:
    python3 scripts/build.py 5471

render-gpu:
    python3 scripts/build.py all --device OPTIX

viewer:
    python3 scripts/make_preview.py

compare:
    python3 scripts/compare.py

view-compare:
    bash scripts/open_viewer.sh http://127.0.0.1:5803/compare.html

serve:
    python3 -m http.server 5803 --bind 0.0.0.0 --directory work/preview

view:
    bash scripts/open_viewer.sh

view-animate:
    bash scripts/open_viewer.sh http://127.0.0.1:5803/animate.html?model=2741

view-serve: viewer
    python3 -m http.server 5803 --bind 0.0.0.0 --directory work/preview
