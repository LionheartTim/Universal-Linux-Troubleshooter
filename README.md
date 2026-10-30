# Universal Linux Troubleshooter (ULTS)

![Universal Linux Troubleshooter application icon](universal_linux_troubleshooter/assets/icons/ults-256.png)

**Investigate Linux hardware and software problems with clear, evidence-based guidance.**

Universal Linux Troubleshooter is a desktop diagnostic application built with Python, Qt 6 and PySide6. It brings system checks, documented symptoms and practical troubleshooting steps together in one interface. It is designed to be approachable for beginners while keeping detailed evidence available for more experienced users.

> **The same application. The same capabilities. No compromises in functionality.**  
> Beginner — Simple, clear, intuitive. · Advanced — Extensive, powerful, flexible.

## Features

- **Complete system scan:** Run up to **72 distinct local read-only measurements** in the current scan plan, without choosing checks individually. Two additional external checks are available only after explicit permission. These are measurements, **not 72 confirmed defects**.
- **Manual Diagnostics:** Search and select hardware or software checks and investigate specific symptoms.
- **Offline troubleshooting library:** **250 documented problem cases**, **500 conditional solution routes**, and **143 supplemental problem guides**, including **69 Steam-related guides**. Guides are not independent diagnostic tests.
- **Finding-specific guidance:** The complete scan links supported findings to existing relevant troubleshooting topics. Each topic has its own observations, possible causes, conditions and next steps.
- **Detailed evidence:** Read the check description, diagnosis, suggested solution and **Evidence / Logs** separately. Unknown or unavailable measurements are not presented as healthy results.
- **Rescan and stop:** Stop an active investigation or rescan after taking your own action.
- **Distribution-aware inventory:** Read available Flatpak, RPM, DEB, pacman, Snap and other supported package-source information without treating an unavailable inventory source as proof an application is missing.
- **Info tab:** Built-in guidance for using the application.

ULTS does **not** include an AI assistant, download an AI model or perform automatic repairs. Recommendations are instructions for the user to assess and choose; running a scan does not install, remove or repair packages.

## Installation

### Install a downloadable Flatpak bundle

Install [Flatpak](https://flatpak.org/setup/) on your distribution first. The bundle is a local file; you do **not** need to double-click it or have a graphical software center installed.

For the existing **v138 test bundle**:

```bash
flatpak install --user --bundle ~/Downloads/Universal-Linux-Troubleshooter-v1.0.0-test-v138.flatpak
flatpak run io.github.LionheartTim.UniversalLinuxTroubleshooter
```

If the bundle is stored in another folder, use its actual path. Confirm the requested runtime installation if prompted. After installation, the application is also available from the desktop's application menu as **Universal Linux Troubleshooter**.

For a future final release bundle, substitute its published filename in the first command. **ULTS has not been claimed as published on Flathub.**

### Uninstall

```bash
flatpak uninstall --user io.github.LionheartTim.UniversalLinuxTroubleshooter
```

This command does not request deletion of user application data.

## Getting started

1. Launch **Universal Linux Troubleshooter** from the application menu.
2. Choose **Complete system scan** for an overview, or find a specific issue in **Manual Diagnostics**.
3. If optional network checks are offered, decide whether to approve them for that run. Local checks remain available without consent.
4. Review **Diagnosis** to see what was actually detected and **Solution** for the relevant documented topic and its conditions.
5. Open **Evidence / Logs** when detailed technical information is needed.
6. After carrying out a chosen action yourself, select **Rescan** to check the result.

A saved crash report or historical system-log warning does not necessarily mean the computer currently has a problem. ULTS distinguishes confirmed observations, possible explanations and information that cannot yet be determined.

## Supported systems and testing

ULTS is intended for multiple Linux distributions and desktop environments, including atomic systems. Actual diagnostic coverage depends on the machine, its installed utilities and the permissions available to the app.

**Flatpak practical testing reported by the developer:**

| Distribution | Desktop environment | Result |
| --- | --- | --- |
| openSUSE | GNOME | Installation and application operation confirmed |
| Xubuntu | Xfce | Installation and application operation confirmed |

The app has also been developed and the Flatpak bundle built on **Bazzite with KDE Plasma**. These results are not a claim that every diagnostic probe, hardware combination or Linux distribution has been verified. In particular, Arch Linux Flatpak acceptance was not established by these tests.

## Privacy, permissions and safety

- **Read-only diagnostics:** The application uses reviewed, bounded read-only inspection paths and does not perform unattended repairs.
- **Network checks:** External connectivity checks require separate approval. General network permission in a Flatpak does **not** mean every scan accesses the internet.
- **Host diagnostics:** To inspect the real system rather than the Flatpak runtime, the bundle uses `flatpak-spawn --host` for allowlisted commands and requests broad read-only host filesystem access.
- **Security limitation:** `flatpak-spawn --host` is a powerful interface. The application's command allowlist is a software safeguard, **not** a strict sandbox guarantee against compromised code.
- **Uncertainty:** If a command is missing, inaccessible or unsupported, ULTS should report the measurement as unknown or unavailable, rather than silently marking it healthy.
- **No automatic modifications:** Users remain in control of whether to follow any suggested repair steps.

Inspect the [Flatpak manifest](io.github.LionheartTim.UniversalLinuxTroubleshooter.json) before installing if you want to review the full permission set.

## Build from source

The included Flatpak test builder targets **KDE Platform/SDK 6.11** with **`io.qt.PySide.BaseApp` 6.11**. Install `flatpak` and `flatpak-builder`, configure a user Flathub remote and run:

```bash
./build-flatpak.sh
flatpak install --user --reinstall --bundle ./Universal-Linux-Troubleshooter-v1.0.0-test-v138.flatpak
./test-flatpak.sh
```

`test-flatpak.sh` checks packaged resources, the offline knowledge base, icon assets, host identification and selected read-only host commands. A successful automated smoke test does not replace manual GUI and distribution testing.

For direct Python development from this project directory, with the required Python and Qt dependencies installed in a local virtual environment:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m universal_linux_troubleshooter
```

## Project documentation

- [Complete diagnostic handbook](docs/complete-handbook.md)
- [Diagnosis-tree reference](docs/diagnosis-trees.md)
- [Steam troubleshooting guide documentation](docs/steam-troubleshooting-v128.md)
- [Flatpak validation notes](FLATPAK_TEST_REPORT.md)
- [Universal Linux Software Manager](https://github.com/LionheartTim/Universal-Linux-Software-Manager) — an optional GUI route where a documented solution involves software management
- [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal) — a separate companion terminal application

**Developer:** [LionheartTim](https://github.com/LionheartTim)

## Release and licensing status

This documentation describes the **v1.0.0 release candidate based on the v138 Flatpak test source**. Do not treat a test-bundle filename as evidence that a final GitHub release or Flathub listing already exists.

**A software source-code license has not yet been specified.** The `CC0-1.0` license on the AppStream metadata applies **only to that metadata file**, not to the application. Before a public source release or Flathub submission, select and verify the application's license and any third-party license obligations, then add the actual project license to the AppStream metadata.

Before a **Flathub** submission, also publish the project homepage/repository and stable, real screenshots; update the final release date and run the official AppStream and Flatpak linter checks. The current metadata uses the developer's existing GitHub profile as a temporary homepage. No unreleased repository or screenshot URL has been invented.
