#!/usr/bin/env bash
set -euo pipefail
APP_ID='io.github.LionheartTim.UniversalLinuxTroubleshooter'
command -v flatpak >/dev/null || { echo 'Flatpak not available'; exit 2; }
echo '=== 1. Installed Flatpak identity ==='
flatpak info --user "$APP_ID" | head -25
echo '=== 2. Real app imports / selected official icon / offline catalogs ==='
flatpak run --user --command=/usr/bin/python3 "$APP_ID" -c '
import sys
sys.path.insert(0, "/app/opt/ults")
from universal_linux_troubleshooter.app_identity import DESKTOP_ID, ICON_SIZES, icon_file
from universal_linux_troubleshooter.diagnostics.topic_catalog127 import all_topics
from universal_linux_troubleshooter.knowledge.diagnosis_trees import load_trees
from universal_linux_troubleshooter.knowledge.engine import KnowledgeBase
import PySide6
assert len(all_topics()) == 143
assert len(ICON_SIZES) == 9 and all(icon_file(x).exists() for x in ICON_SIZES)
assert KnowledgeBase().path.exists()
assert load_trees()
print("PASS: PySide6, icons, offline catalog and SQLite database")'
echo '=== 3. Real host diagnostics (no changes) ==='
flatpak run --user --command=/usr/bin/python3 "$APP_ID" -c '
import os
import sys
sys.path.insert(0, "/app/opt/ults")
from universal_linux_troubleshooter.diagnostics.bridge import LocalHost
from universal_linux_troubleshooter.system_profile119 import os_facts
assert os.environ.get("FLATPAK_ID")
facts=os_facts()
print("Detected host distro:",facts.get("distro_name","UNKNOWN"))
assert facts.get("distro_id"),"Host OS metadata unavailable: Flatpak must not misidentify KDE runtime"
result=LocalHost().command(("ip","-j","route","show","default"))
print("Host network route probe code:",result.code)
assert result.code == 0, "Host-spawn failed or ip is missing; investigate before relying on network checks"
try:
    LocalHost().command(("sh","-c","echo unsupported"))
    raise AssertionError("Unsafe command was accepted")
except ValueError:
    pass
print("PASS: host OS profile, read-only host command and command allowlist")'
echo '=== All automated smoke checks passed ==='
echo 'Run the visible GUI: flatpak run io.github.LionheartTim.UniversalLinuxTroubleshooter'
echo 'Then test the complete 72-check system scan, selected problem/Steam guides, Stop/Rescan, icons and package-source inventory.'
