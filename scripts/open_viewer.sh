#!/usr/bin/env bash
# Match Lucy's verified interactive Chromium setup, in a dedicated profile.
set -euo pipefail
url="${1:-http://127.0.0.1:5803/}"
if command -v chromium >/dev/null 2>&1; then
    exec chromium \
        --user-data-dir=/tmp/console-3D-interactive-browser \
        --use-gl=angle \
        --use-angle=swiftshader \
        --enable-unsafe-swiftshader \
        --new-window "$url"
elif command -v open >/dev/null 2>&1; then
    exec open "$url"
else
    exec xdg-open "$url"
fi
