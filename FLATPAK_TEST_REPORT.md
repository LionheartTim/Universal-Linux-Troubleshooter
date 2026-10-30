# ULTS v138 — Clean source and Flatpak test candidate

**Baseline:** user-confirmed working v137, Manual Diagnostics and Info only.

## Cleaned from distribution candidate

- Historical AI/Qwen agents, GUI and inference code; obsolete GGUF/llama.cpp integration.
- Historical experimental scripts, archived progress notes, older study datasets and development output.
- Cached Python bytecode, test result files, and original oversized icon master.

**Kept:** original 250 diagnosis cases, 500 solution routes, 143 symptom guides, SQLite offline reference, read-only diagnostic bridge, system profile, full scan, and nine official icon sizes. The original v137 archive has not been changed.

## Flatpak design

- App ID: `io.github.LionheartTim.UniversalLinuxTroubleshooter`
- Runtime/SDK: KDE 6.11; `io.qt.PySide.BaseApp` 6.11.
- User start-menu launcher and nine icons included.
- Fixed-argv read-only diagnostic commands are sent through `flatpak-spawn --host` when in a Flatpak, and only after the existing command allowlist checks.
- `/etc` and `/usr` read-only host views use Flatpak's `/run/host` mounts.
- Disk usage for `/`, `/var`, `/sysroot` uses bounded read-only `df` from the host; `/proc/meminfo` and mounts use bounded host reads.
- Network permissions are present because optional TLS/DNS tests require user consent; those checks remain disabled without approval.
- **Sandbox caveat:** Host-spawn is a powerful permission. The app's command whitelist is the application-level safety control, not a security guarantee about arbitrary compromised code.

## Local validation performed in this environment

- **2588 pytest tests passed; 28 subtests passed.** These include cleaned Manual Diagnostics, safety, Steam guide, package sources, complete scan and Flatpak-host adapter tests.
- All Python modules compile and import checks for catalog and offline knowledge passed.
- All nine official icons have the correct dimensions.
- Manifest parses as JSON; metainfo parses as XML; build/test scripts pass `bash -n`.
- **Actual Flatpak binary not built**: neither `flatpak-builder` nor `flatpak` is installed in this environment; PySide6 GUI runtime is also unavailable here.

## Build and Bazzite test

Extract the ZIP to a new directory and run:

```bash
./build-flatpak.sh
flatpak install --user --reinstall --bundle Universal-Linux-Troubleshooter-v1.0.0-test-v138.flatpak
./test-flatpak.sh
flatpak run io.github.LionheartTim.UniversalLinuxTroubleshooter
```

If the build script says your user Flathub remote is missing, it prints the explicit `flatpak remote-add` command to add it.

**Hardware acceptance still needed:** full scan, Stop/Rescan, packaged UIs, actual host package inventory, and host read-only checks on Bazzite, openSUSE, Arch and Ubuntu. Do not regard this as a distribution-ready Flatpak until those are verified. The application source license is still undecided; public distribution requires a license review.
