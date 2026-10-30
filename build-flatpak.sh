#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
APP_ID="io.github.LionheartTim.UniversalLinuxTroubleshooter"
VERSION="v1.0.0-test-v138"
MANIFEST="$APP_ID.json"
BUILD_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/ults-flatpak/build"
REPO_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/ults-flatpak/repo"
OUTPUT="$PWD/Universal-Linux-Troubleshooter-$VERSION.flatpak"
for binary in flatpak flatpak-builder; do
  command -v "$binary" >/dev/null || { echo "Missing $binary. Install it first." >&2; exit 2; }
done
flatpak remotes --user --columns=name | grep -qx flathub || {
 echo "Missing user Flathub remote. Add it explicitly before building." >&2
 echo 'flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo' >&2
 exit 2
}
# Validate only the icon sizes that Flatpak will export. The high-resolution
# source image may remain in /app/opt/ults, but exported icons must be <=512px.
python3 - <<'PYICON'
import json
import re
import struct
from pathlib import Path
manifest = json.loads(Path("io.github.LionheartTim.UniversalLinuxTroubleshooter.json").read_text())
icons = []
for module in manifest["modules"]:
    for command in module.get("build-commands", []):
        match = re.fullmatch(
            r"install -Dm644 (\S+\.png) /app/share/icons/hicolor/(\d+)x(\d+)/apps/\S+\.png",
            command,
        )
        if not match:
            continue
        file_path, width, height = match.groups()
        width, height = int(width), int(height)
        data = Path(file_path).read_bytes()[:24]
        if not data.startswith(b"\x89PNG\r\n\x1a\n"):
            raise SystemExit(f"Invalid PNG: {file_path}")
        actual_width, actual_height = struct.unpack(">II", data[16:24])
        if width > 512 or height > 512 or (width, height) != (actual_width, actual_height):
            raise SystemExit(f"Invalid Flatpak icon size: {file_path}: {actual_width}x{actual_height}")
        icons.append(width)
if not icons or 512 not in icons:
    raise SystemExit("Flatpak manifest is missing the expected application icons")
print("Flatpak icon preflight passed:", sorted(icons))
PYICON
mkdir -p "$(dirname "$BUILD_DIR")" "$REPO_DIR"
flatpak-builder --user --install-deps-from=flathub --force-clean \
  --repo="$REPO_DIR" "$BUILD_DIR" "$MANIFEST"
flatpak build-bundle "$REPO_DIR" "$OUTPUT" "$APP_ID"
echo "BUNDLE_CREATED: $OUTPUT"
echo "To install locally: flatpak install --user --reinstall --bundle '$OUTPUT'"
echo "To run: flatpak run '$APP_ID'"
echo 'To uninstall (without deleting user data): flatpak uninstall --user io.github.LionheartTim.UniversalLinuxTroubleshooter'
