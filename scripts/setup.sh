#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
ext="${XETAL_EXTENSIONS_ROOT:-$PWD/X_eTaL-extensions}"
if [ ! -d "$ext/.git" ]; then
    git clone --depth 1 https://github.com/softwarewrighter/X_eTaL-extensions.git "$ext"
fi
extensions_commit="$(tr -d '[:space:]' < EXTENSIONS_COMMIT)"
if ! git -C "$ext" cat-file -e "$extensions_commit^{commit}" 2>/dev/null; then
    git -C "$ext" fetch origin "$extensions_commit"
fi
git -C "$ext" checkout --detach "$extensions_commit"
if [ ! -d "$ext/work/xetal/.git" ]; then
    git clone https://github.com/softwarewrighter/X_eTaL.git "$ext/work/xetal"
fi
commit="$(tr -d '[:space:]' < "$ext/XETAL_COMMIT")"
if ! git -C "$ext/work/xetal" cat-file -e "$commit^{commit}" 2>/dev/null; then
    git -C "$ext/work/xetal" fetch origin "$commit"
fi
git -C "$ext/work/xetal" checkout --detach "$commit"
cargo build --manifest-path "$ext/Cargo.toml" --release -p xetal-x -p xetal-ext-blender
