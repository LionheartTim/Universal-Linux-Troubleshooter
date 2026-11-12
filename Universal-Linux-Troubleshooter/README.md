# Universal Linux Troubleshooter (ULTS)

Restored, GitHub-ready source package for the **v139 Qt/PySide compatibility repair**.
It is reconstructed from the working v138 Flatpak installation. It contains
application Python source, diagnostic modules, knowledge data, icons, desktop
integration, and the Flatpak manifest. It does **not** recreate missing Git
history or files that were not in the installed application.

## Qt/PySide repair

The prior installed package included PySide6 6.11.2 and crashed against
`org.kde.Platform` Qt 6.11.3 with an undefined Qt private API symbol.
The v139 rebuild uses the current `io.qt.PySide.BaseApp//6.11` (Qt/PySide
6.11.3 at the time of the repair) instead of redistributing the older copied
PySide binaries. The latest patch version for this BaseApp branch can change;
rebuild/test the app whenever the KDE runtime updates.

## Building on Linux

Install `flatpak-builder`, configure Flathub, and run:

```bash
flatpak install --user flathub org.kde.Sdk//6.11 io.qt.PySide.BaseApp//6.11
flatpak-builder --user --force-clean --install-deps-from=flathub build-v139 manifest.json
flatpak build-export repo-v139 build-v139 master
flatpak build-bundle repo-v139 Universal-Linux-Troubleshooter-v139.flatpak \
  io.github.LionheartTim.UniversalLinuxTroubleshooter master \
  --runtime-repo=https://dl.flathub.org/repo/flathub.flatpakrepo
```

## Test the rebuilt UI

From an active Wayland desktop session, where appropriate:

```bash
flatpak build --runtime --readonly --socket=wayland --share=ipc --device=dri \
  --env=WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-0}" \
  --env=QT_QPA_PLATFORM=wayland build-v139 /app/bin/ults-run
```

The application ID remains `io.github.LionheartTim.UniversalLinuxTroubleshooter`.
The embedded version metadata is inherited from the recovered v138 installation;
check/update release metadata separately if publishing an official v139 release.

## Source provenance and licensing

This source tree was reconstructed from a previously installed build. Review
its contents and add the **original project's actual license** if it is not
present. No license has been guessed or generated.
