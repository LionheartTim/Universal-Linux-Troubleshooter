# Universal Linux Troubleshooter — Master Diagnostic Handbook 34

**Hardware documentation pass only.** This consolidated book keeps the earlier 96 case families and appends 70 specialized hardware cases. Overlapping variants may describe related symptoms from different hardware angles; the total is a *reference count*, not proof of coverage of every possible Linux failure.

- Part I: Previously documented 96 families (including OS and applications), **unchanged** from Handbook 33.
- Part II: 70 new hardware/device investigations, with specific supporting/counter evidence, user-performed solutions, read-only diagnostic commands and retests.
- **Future development order:** hardware documentation first, OS expansion next only when requested, then diagnosis trees, AI training and GUI packaging.
- No command in this handout authorizes automatic repairs, auto-elevation, unapproved network requests or arbitrary AI shell access.

---


## PART I — Prior 96 dossier families

# Universal Linux Troubleshooter — Master Diagnostic Handbook, Edition 33

**96 documented case families**: 57 from the original Diagnostic Bridge knowledge base plus 39 newly expanded troubleshooting references. All material is written as user-executed troubleshooting guidance, not as executable scripts or permissions for AI-controlled repairs.

**Read-only boundaries:** Some queries need explicit administrator access or network permission; never infer these permissions from a general scan request. Firmware-update metadata checks can require network access.

**Reading order:** The original 57 cases come first. The 39 reference cases follow in the second section. When symptoms overlap, compare exact device, package manager and evidence before selecting a case.

**Operator rule:** the Troubleshooter may only run allowlisted read-only checks. The user performs each chosen remedy, including changes in Universal Linux Terminal or Universal Linux Software Manager. The latter only handles supported software package-management actions. Bazzite base image maintenance must use Bazzite's supported procedures.

---

# Part I — Established original problem families (57)

# Universal Linux Troubleshooter — Diagnostic Command Handbook 31

**Status:** 57 existing case families / 57 command-guides drafted; **0 cases field-validated**. Documentation only. 2026-10-28.

This guide is not a script and does not execute commands. Every Linux failure should be followed toward a concrete **repair, isolation, workaround, hardware replacement, or evidence-supported developer fix**. These are not guaranteed outcomes until a controlled user retest.

**Hard boundary:** Universal Linux Troubleshooter may run only its pre-approved, read-only diagnostics. **All updates, removals, restarts, changes of settings, network-dependent probes and recovery actions are user-controlled.** This handbook does **not** register new actions for the AI. No automatic repairs, no automatic privilege elevation.

**Before using ANY command:** verify distro (`cat /etc/os-release`), installation source (`flatpak list --app`, `rpm-ostree status`, appropriate native tool), relevant device/app identifier and installed tools. `<...>` placeholders are NOT literal runnable values. `journalctl -b -1` requires a previous boot log (not always present). A missing log is not evidence of good health. `sudo` read-only commands still require explicit user authorization. Screen/desktop commands are desktop-specific. Do not copy secrets from logs or network settings into bug reports.

**Bazzite:** Immutable system image/composefs `/` being 100% full is expected. Inspect writable `/var` or `/sysroot` for low space. Do not use `dnf`, `apt`, `pacman` or `zypper` as if they manage Bazzite's base image. The documented Bazzite tool is `ujust update`, or Bazzite Updater; image rollback uses the official recovery flow. Package layering is a last resort.

**Installation-source principle:** A Flatpak is updated/removed as Flatpak, a distro package by that distro's native manager, and an AppImage from its actual installation source. Never silently switch Flathub ↔ GitHub or change a system-installed package just to test.

## Choose ONE way to follow the instructions

In the future Troubleshooter UI, the user chooses **one** presentation for each applicable solution, not three stacked instruction blocks:

1. **Terminal (advanced):** exact conditional commands and retest, run manually.
2. **[Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal) (guided terminal):** the **same** commands, with host-command discovery, command descriptions and optional *Insert into terminal* (insertion does NOT execute). The user reviews and presses Enter. A command explanation is not a guarantee that it is safe or appropriate; always verify real IDs, distro, privileges and flags. Some solutions are hardware or desktop procedures, not executable commands; Universal Linux Terminal then helps with the diagnostic commands only.
3. **Graphical method:** for supported software package operations use [Universal Linux Software Manager](https://github.com/LionheartTim/Universal-Linux-Software-Manager) in its actual package tab; otherwise use the supported system, desktop or vendor GUI. ULSM is not a generic repair backend.

The human-readable handbook lists all routes for editorial review; the eventual app must show **only the user-selected route**. There is **no direct app-to-app command execution or transfer** in this edition. The Troubleshooter runs only its allowlisted read-only controls; **all changing actions remain user-executed**. For base Bazzite image updates recommend Bazzite Updater GUI, not ULSM.

### Package source–specific user commands (conditional, NOT universal)

- Identify OS: `cat /etc/os-release`.
- Flatpak: inspect `flatpak list --app` and `flatpak info <APP_ID>`; selected user update `flatpak update <APP_ID>`; selected removal `flatpak uninstall <APP_ID>` after confirmation. Do not confuse `--user` and `--system` installations.
- Bazzite image: inspect `rpm-ostree status`; user update `ujust update` or **Bazzite Updater**. Remove a verified extra **layered** package only if necessary with `rpm-ostree uninstall <LAYERED_PACKAGE>`, followed by reboot; never remove base image packages.
- Fedora Workstation (not Bazzite): `sudo dnf upgrade <PACKAGE>` for an identified native package, or `sudo dnf upgrade` to update all. Verify transaction first.
- Debian/Ubuntu: `sudo apt update` then `sudo apt install --only-upgrade <PACKAGE>` for an already installed native package (review apt's proposed operations).
- openSUSE: `sudo zypper refresh` then `sudo zypper update <PACKAGE>` for a verified installed native package (review transaction).
- Arch: `sudo pacman -Syu` for coherent full-system upgrade; avoid unsupported partial upgrade workflow (`pacman -Sy` followed by single-package updates).
- Snap (where actually installed): `snap list`; `sudo snap refresh <SNAP_NAME>` for an intended snap; review the active snap and permissions.
- AppImage: identify actual file and trusted release; manage through supported AppImage workflow. **No universal `apt`/`rpm` command** applies to arbitrary standalone AppImages.

Do not execute the above commands in the Troubleshooter. They are **user-selected instructions** and require per-platform review and confirmation.

---


## 01. Application closes unexpectedly (`applications.app-crash`)

**Possible cause:** The program may have failed; logs and crash records might identify the process and event.

**Read-only check IDs:** `applications/app_crashes`, `applications/resources`, `system/system_logs`

**Discriminating evidence:** A new coredump names the affected executable at the failure time; distinguish crashes of other processes.

**Counterevidence:** Old crash data or a crash from an unrelated program is not current proof.


**Diagnostic terminal commands (read-only unless noted):**


```bash
coredumpctl --no-pager list
journalctl --user -b --no-pager -p warning -n 100
flatpak list --app
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Only one optional application crashes


**Option A — Terminal / user-directed procedure:**

1. For a CONFIRMED Flatpak: flatpak info <APP_ID>

2. For a CONFIRMED Flatpak: flatpak update <APP_ID>


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Flatpak tab → find the verified app ID → Update if available, or Uninstall only if the user chooses to isolate the issue.


**If that does not help:**

Close optional app integrations and repeat once in ordinary use; if only this application crashes, retain the time-stamped traceback and report it to its developer.


**Conditional second route:** Crash persists after update

1. Close the app, reproduce without optional integrations if practical, then send its developer a concise redacted report including version, time, steps and relevant error.


**Retest:** Repeat the previously failing action and confirm there is no NEW report.

```bash
coredumpctl --no-pager list
```

**Second-route verification:** Developer fix or corrected optional integration survives the same test.

**Safety:** Avoid removing system packages or deleting application data without a backup and explicit consent.


**Primary command/reference manuals:** [systemd coredumpctl](https://www.freedesktop.org/software/systemd/man/latest/coredumpctl.html) · [Flatpak user guide](https://docs.flatpak.org/en/latest/using-flatpak.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 02. Application will not start (`applications.app-wont-open`)

**Possible cause:** The application, its service or its runtime may be failing.

**Read-only check IDs:** `applications/app_crashes`, `applications/permissions`, `applications/services`

**Discriminating evidence:** Distinguish missing runtime, permission denial, and a crash of the exact program.

**Counterevidence:** The app opens under another user or install scope; source/permissions may differ.


**Diagnostic terminal commands (read-only unless noted):**


```bash
flatpak list --app
flatpak info <APP_ID>
journalctl --user -b --no-pager -p warning -n 100
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** App was installed as Flatpak and lacks a required permission


**Option A — Terminal / user-directed procedure:**

1. If it is a Flatpak: flatpak run <APP_ID>

2. If a newer version is available from the SAME source: flatpak update <APP_ID>


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Flatpak tab or the package-type tab matching the actual installation source → inspect the installed app and available updates.


**If that does not help:**

For non-Flatpak apps inspect the application’s actual install source and fix it there; avoid switching sources without removing the original.


**Conditional second route:** App package/runtime is missing or incompatible

1. Use the same software source that originally installed it for a supported repair or update

2. avoid switching sources blindly.


**Retest:** App starts and affected feature works after the exact permission change.

```bash
flatpak info <APP_ID>
```

**Second-route verification:** App launches normally without new errors.

**Safety:** Do not grant full filesystem/network access blindly to sandboxed applications.


**Primary command/reference manuals:** [systemd coredumpctl](https://www.freedesktop.org/software/systemd/man/latest/coredumpctl.html) · [Flatpak user guide](https://docs.flatpak.org/en/latest/using-flatpak.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 03. CPU usage is very high (`applications.cpu-high`)

**Possible cause:** An application or short workload peak may be using CPU heavily.

**Read-only check IDs:** `applications/resources`, `applications/services`, `hardware/sensors`

**Discriminating evidence:** The same unexpected process remains busy when the user is otherwise idle.

**Counterevidence:** High CPU during an intentionally demanding task is not a software fault.


**Diagnostic terminal commands (read-only unless noted):**


```bash
ps -eo pid,comm,%cpu,%mem --sort=-%cpu | head -n 20
uptime
free -h
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** One background optional app consumes CPU continuously


**Option A — Terminal / user-directed procedure:**

1. Identify the PID and program with: ps -p <PID> -o pid,comm,etime,%cpu,%mem

2. For a separately installed app, compare its current version with the version offered by its original source.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Updates tab → inspect the identified non-system application. Update only through its original package source.


**If that does not help:**

Close the optional application via its own user interface and compare load. If intentional workload, tune its own options rather than killing a system process.


**Conditional second route:** Usage is normal for intended workload

1. Explain expected load and thermal limits

2. consider the app’s own quality/performance settings rather than deleting it.


**Retest:** CPU usage falls at idle after the same app is closed/updated.

```bash
ps -eo pid,comm,%cpu,%mem --sort=-%cpu | head -n 20
```

**Second-route verification:** Workload remains stable at expected resource levels.

**Safety:** Never kill core services based solely on a percentage.


**Primary command/reference manuals:** [systemd coredumpctl](https://www.freedesktop.org/software/systemd/man/latest/coredumpctl.html) · [Flatpak user guide](https://docs.flatpak.org/en/latest/using-flatpak.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 04. Application cannot open a file (`applications.permission-denied`)

**Possible cause:** The process may lack permission for the requested file or resource.

**Read-only check IDs:** `applications/permissions`, `system/system_logs`

**Discriminating evidence:** Inspect ownership AND every parent-directory execute permission; Flatpak sandbox denials are different from Unix file rights.

**Counterevidence:** Missing file/path can look similar but is not a permissions issue.


**Diagnostic terminal commands (read-only unless noted):**


```bash
id
stat -c "%A %U:%G %n" <FILE>
namei -l <FILE>
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** App is Flatpak and a document/folder is not permitted


**Option A — Terminal / user-directed procedure:**

1. For Flatpak apps: flatpak info --show-permissions <APP_ID>

2. Only after confirming the exact app and needed access: adjust a narrow app permission in a trusted GUI; do not use chmod 777.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

Use the native file manager to grant the intended user access, or choose a file inside the app’s already permitted directories.


**Conditional second route:** A normal user-owned file has restrictive permissions

1. Verify ownership and location before changing one specific file permission through normal file manager controls.


**Retest:** Opening that same document succeeds.

```bash
stat -c "%A %U:%G %n" <FILE>
```

**Second-route verification:** The intended user and app can open the selected file.

**Safety:** Never run chmod -R 777, disable MAC security, or grant unrestricted home access.


**Primary command/reference manuals:** [systemd coredumpctl](https://www.freedesktop.org/software/systemd/man/latest/coredumpctl.html) · [Flatpak user guide](https://docs.flatpak.org/en/latest/using-flatpak.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 05. Computer runs out of memory (`applications.ram-low`)

**Possible cause:** The operating system may be short on available memory.

**Read-only check IDs:** `applications/resources`, `hardware/memory`, `system/system_logs`

**Discriminating evidence:** Memory pressure, OOM kills and the exact process coincide; page-cache use alone is not an error.

**Counterevidence:** An application using lots of cache is not necessarily out of memory.


**Diagnostic terminal commands (read-only unless noted):**


```bash
free -h
swapon --show
ps -eo pid,comm,rss --sort=-rss | head -n 20
journalctl -b -k --no-pager -g "Out of memory|oom-killer" -n 40
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** One optional program uses most RAM


**Option A — Terminal / user-directed procedure:**

1. Close a confirmed memory-heavy OPTIONAL app after saving work.

2. Check for its supported update in the original package manager; add RAM only if workloads legitimately exceed capacity.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Updates tab → identify whether a newer release of the affected app exists from its installed source.


**If that does not help:**

For a repeatable leak collect a before/after memory snapshot and report version, steps and measurements to the developer.


**Conditional second route:** Multiple normal apps exceed physical memory

1. Reduce concurrent workload or consider a supported memory expansion after checking hardware compatibility.


**Retest:** Memory pressure subsides and no new OOM event appears.

```bash
free -h
journalctl -b -k --no-pager -g "Out of memory|oom-killer" -n 40
```

**Second-route verification:** Same workload completes without OOM events.

**Safety:** Do not delete swap or disable OOM protection as a generic fix.


**Primary command/reference manuals:** [systemd coredumpctl](https://www.freedesktop.org/software/systemd/man/latest/coredumpctl.html) · [Flatpak user guide](https://docs.flatpak.org/en/latest/using-flatpak.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 06. Security policy blocks an action (`applications.selinux-denial`)

**Possible cause:** SELinux might be denying a specific requested action.

**Read-only check IDs:** `applications/permissions`, `system/system_logs`

**Discriminating evidence:** A matching AVC denial identifies the target process and resource; nonmatching denials are not causation.

**Counterevidence:** A generic denial unrelated in time or target is insufficient.


**Diagnostic terminal commands (read-only unless noted):**


```bash
getenforce
journalctl -b --no-pager -g "avc:.*denied|SELinux" -n 80
ls -Zd <FILE>
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** App is Flatpak and request is actually sandbox access


**Option A — Terminal / user-directed procedure:**

1. Match the AVC to the affected application, action and security context.

2. Apply a narrowly documented vendor- or distro-approved policy/label correction ONLY after identifying the underlying cause.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

Temporarily stop the optional app and update it from its trusted source; if a policy defect remains, prepare an AVC report for the distro maintainer.


**Conditional second route:** Genuine SELinux policy denial is reproducible

1. Preserve the AVC type, source/target and time and use distribution-supported SELinux troubleshooting or vendor fix.


**Retest:** Affected operation works with the minimum correctly scoped access.

```bash
getenforce
journalctl -b --no-pager -g "avc:.*denied|SELinux" -n 80
```

**Second-route verification:** New identical denial no longer happens after an approved policy/application fix.

**Safety:** Never suggest disabling SELinux or globally permissive mode as a fix.


**Primary command/reference manuals:** [systemd coredumpctl](https://www.freedesktop.org/software/systemd/man/latest/coredumpctl.html) · [Flatpak user guide](https://docs.flatpak.org/en/latest/using-flatpak.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 07. Background service fails to start (`applications.service-failed`)

**Possible cause:** A named background service may have stopped or failed to start.

**Read-only check IDs:** `applications/services`, `system/system_logs`

**Discriminating evidence:** The unit is failed AND its journal names a specific unmet dependency, config error or denied resource.

**Counterevidence:** An inactive service that is intentionally disabled is not failed.


**Diagnostic terminal commands (read-only unless noted):**


```bash
systemctl --failed --no-pager
systemctl status <SERVICE>.service --no-pager
journalctl -b -u <SERVICE>.service --no-pager -n 100
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Failed service belongs to an optional application


**Option A — Terminal / user-directed procedure:**

1. For a USER-OWNED optional service, fix the specific configuration/dependency indicated by its log.

2. After correction, user may run: systemctl --user restart <SERVICE>.service


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

For essential system services avoid a blind restart; use vendor recovery instructions with backup before changing the unit.


**Conditional second route:** Service failure is due to a missing configuration/dependency

1. Preserve the exact error, restore only the documented missing dependency or config using the distro’s supported process.


**Retest:** Named unit becomes active and stays active.

```bash
systemctl --user status <SERVICE>.service --no-pager
```

**Second-route verification:** Fresh systemctl status and journal no longer report that failure.

**Safety:** Never delete or disable a core unit merely to hide its log message.


**Primary command/reference manuals:** [systemd coredumpctl](https://www.freedesktop.org/software/systemd/man/latest/coredumpctl.html) · [Flatpak user guide](https://docs.flatpak.org/en/latest/using-flatpak.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 08. Sound gone after suspend (`audio.audio-after-sleep`)

**Possible cause:** Audio services or devices might not have resumed cleanly.

**Read-only check IDs:** `audio/audio_services`, `hardware/power`, `system/system_logs`

**Discriminating evidence:** After resume, audio nodes vanish or the session manager reports a fresh failure.

**Counterevidence:** No sound before sleep suggests a different baseline audio problem.


**Diagnostic terminal commands (read-only unless noted):**


```bash
wpctl status
systemctl --user status pipewire wireplumber --no-pager
journalctl --user -b --no-pager -g "pipewire|wireplumber" -n 80
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Output switched after resume


**Option A — Terminal / user-directed procedure:**

1. Confirm the intended device is selected in desktop Sound settings.

2. If the user chooses to recover the USER audio services: systemctl --user restart wireplumber pipewire


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

On Bazzite inspect the built-in user command with: ujust --show restart-pipewire; use that supported option if appropriate.


**Conditional second route:** Sound services have a fresh error

1. Use the desktop’s supported session restart/logoff and supported updates

2. avoid overwriting service unit files.


**Retest:** Sound returns after waking with the same device selected.

```bash
wpctl status
```

**Second-route verification:** Device and PipeWire user services are healthy after waking.

**Safety:** Do not delete PipeWire configuration or reset every audio device to fix one symptom.


**Primary command/reference manuals:** [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html) · [Bazzite maintenance commands](https://docs.bazzite.gg/Installing_and_Managing_Software/ujust/index.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 09. Bluetooth sound cuts out (`audio.bluetooth-audio`)

**Possible cause:** Bluetooth connection quality or audio routing may be unstable.

**Read-only check IDs:** `audio/bluetooth`, `audio/audio_services`, `system/system_logs`

**Discriminating evidence:** The paired audio device disconnects or switches audio profile when sound stops.

**Counterevidence:** A disconnect or low battery can create similar silence; check link state first.


**Diagnostic terminal commands (read-only unless noted):**


```bash
bluetoothctl show
bluetoothctl devices Connected
wpctl status
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Connected but not default output


**Option A — Terminal / user-directed procedure:**

1. Use desktop Bluetooth settings to reconnect the known device and select the intended audio profile.

2. Move away from radio interference and test with a separate Bluetooth device.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

Update the headset firmware through its documented process, or test a wired audio route to separate audio stack and radio causes.


**Conditional second route:** Audio drops while Bluetooth connection itself disconnects

1. Check distance, power and battery and reconnect in Bluetooth settings

2. compare with another location.


**Retest:** Audio routes to the intended headset.

```bash
bluetoothctl devices Connected
wpctl status
```

**Second-route verification:** No fresh disconnect and stable playback.

**Safety:** Avoid permanent codec/suspension tweaks without device-specific evidence.


**Primary command/reference manuals:** [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html) · [Bazzite maintenance commands](https://docs.bazzite.gg/Installing_and_Managing_Software/ujust/index.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 10. Bluetooth adapter cannot be found (`audio.bluetooth-not-found`)

**Possible cause:** The adapter or its background service may not be available.

**Read-only check IDs:** `audio/bluetooth`, `applications/services`, `hardware/hardware_logs`

**Discriminating evidence:** Bluetooth controller absent vs soft-blocked vs service failed require different actions.

**Counterevidence:** Some desktops have no Bluetooth hardware; absence is informational there.


**Diagnostic terminal commands (read-only unless noted):**


```bash
rfkill list
bluetoothctl list
systemctl status bluetooth --no-pager
lsusb
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Adapter radio is switched off or blocked


**Option A — Terminal / user-directed procedure:**

1. If rfkill reports Soft blocked: use the desktop Airplane mode / Bluetooth toggle to enable it.

2. If USB/PCI controller is not enumerated, check firmware/BIOS switch or hardware connection; do not install random drivers.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

If controller is listed and only the optional service is inactive, user can enable it via distro service controls after checking boot policy.


**Conditional second route:** Adapter physically missing from USB/PCI inventory

1. Check removable dongle seating and power, then follow device maker diagnostics.


**Retest:** Controller appears and is enabled.

```bash
rfkill list
bluetoothctl list
```

**Second-route verification:** Controller appears reliably after replacement/reconnect.

**Safety:** Do not repeatedly restart system services if Bluetooth hardware is not present.


**Primary command/reference manuals:** [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html) · [Bazzite maintenance commands](https://docs.bazzite.gg/Installing_and_Managing_Software/ujust/index.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 11. Bluetooth device refuses to pair (`audio.bluetooth-pair`)

**Possible cause:** The device could be out of pairing mode, already connected elsewhere, or rejected by Bluetooth.

**Read-only check IDs:** `audio/bluetooth`, `system/system_logs`

**Discriminating evidence:** Identify pairing authentication rejection vs radio/service discovery errors.

**Counterevidence:** A device paired to a different host may need owner intervention.


**Diagnostic terminal commands (read-only unless noted):**


```bash
bluetoothctl show
bluetoothctl devices
journalctl -b -u bluetooth --no-pager -n 80
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Device is not in pairing mode


**Option A — Terminal / user-directed procedure:**

1. Set only the target device into its documented pairing mode and use desktop Bluetooth settings to pair again.

2. If the device is still bound to another computer, disconnect there and retry.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

Update the device firmware via manufacturer documentation, then repeat pairing without altering the Linux radio stack.


**Conditional second route:** Stored bond is stale after a device firmware change

1. Remove only that saved pairing from both sides with user consent, then pair again.


**Retest:** Device becomes paired and connects.

```bash
bluetoothctl devices Paired
bluetoothctl devices Connected
```

**Second-route verification:** Fresh pairing survives a reconnect.

**Safety:** Re-pairing may disrupt other paired devices; avoid deleting all pairings.


**Primary command/reference manuals:** [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html) · [Bazzite maintenance commands](https://docs.bazzite.gg/Installing_and_Managing_Software/ujust/index.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 12. Microphone not working (`audio.mic-not-working`)

**Possible cause:** The wrong input device or muted microphone may prevent recordings.

**Read-only check IDs:** `audio/audio_devices`, `audio/audio_services`, `applications/permissions`

**Discriminating evidence:** Separate wrong input selection, mute, missing node, and sandbox/portal restrictions.

**Counterevidence:** Mic hardware is missing entirely or source cannot be opened: different path.


**Diagnostic terminal commands (read-only unless noted):**


```bash
wpctl status
systemctl --user status wireplumber --no-pager
flatpak info --show-permissions <APP_ID>
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Wrong input or mute


**Option A — Terminal / user-directed procedure:**

1. Choose the intended input in desktop Sound settings, unmute it and test input level.

2. For a confirmed Flatpak, grant only the needed microphone portal permission in the desktop permission manager.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

Test another microphone and input port; if hardware works outside one app, focus on its own settings/permissions.


**Conditional second route:** Only one sandboxed app cannot record

1. Inspect app-specific microphone permission and enable only that access when appropriate.


**Retest:** Input level changes with speech.

```bash
wpctl status
```

**Second-route verification:** The app records a short test clip.

**Safety:** Ask permission before enabling microphone access in any application.


**Primary command/reference manuals:** [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html) · [Bazzite maintenance commands](https://docs.bazzite.gg/Installing_and_Managing_Software/ujust/index.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 13. Sound crackles or distorts (`audio.sound-crackles`)

**Possible cause:** CPU load, device buffering or wireless interference may be involved.

**Read-only check IDs:** `audio/audio_services`, `audio/audio_devices`, `applications/resources`

**Discriminating evidence:** Check whether crackles correlate with xruns, an overloaded system or one audio device.

**Counterevidence:** No xrun evidence and only one damaged media file may be a content issue.


**Diagnostic terminal commands (read-only unless noted):**


```bash
wpctl status
journalctl --user -b --no-pager -g "pipewire|wireplumber|alsa" -n 80
uptime
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** One USB headset/sound device crackles


**Option A — Terminal / user-directed procedure:**

1. Use the desktop audio panel to select the correct device/profile and compare wired vs Bluetooth audio.

2. On Bazzite, inspect: ujust --show restart-pipewire; use the documented audio restart if selected by the user.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

Update the audio application from its own source if the problem is app-specific; avoid arbitrary kernel audio parameter changes.


**Conditional second route:** Audio service reports scheduling/xrun issues

1. Check for supported PipeWire/WirePlumber updates and close excessive concurrent loads before retest.


**Retest:** Crackle disappears on the tested connection.

```bash
wpctl status
```

**Second-route verification:** Same audio stream plays cleanly with no new underrun.

**Safety:** Avoid replacing audio backend or changing real-time kernel scheduling blindly.


**Primary command/reference manuals:** [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html) · [Bazzite maintenance commands](https://docs.bazzite.gg/Installing_and_Managing_Software/ujust/index.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 14. No sound from speakers (`audio.sound-missing`)

**Possible cause:** The wrong output device or a stopped audio service may explain missing sound.

**Read-only check IDs:** `audio/audio_devices`, `audio/audio_services`, `applications/services`

**Discriminating evidence:** Observe sink availability, mute/route selection and audio-session health.

**Counterevidence:** No sound card recognized: hardware/driver investigation is needed.


**Diagnostic terminal commands (read-only unless noted):**


```bash
wpctl status
systemctl --user status pipewire wireplumber --no-pager
aplay -l
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Wrong output or muted


**Option A — Terminal / user-directed procedure:**

1. Select the right output, raise volume, and verify the headset or monitor is not muted.

2. If the user audio session itself failed: systemctl --user restart wireplumber pipewire


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

Test sound in another program and device before modifying drivers.


**Conditional second route:** Only one application has no sound

1. Check that app’s own mute/output settings

2. compare with system test sound, then update the affected optional app if needed.


**Retest:** Test sound plays from intended speakers.

```bash
wpctl status
```

**Second-route verification:** Same app plays audio while other apps remain working.

**Safety:** Do not reset every audio preference before isolating output and app.


**Primary command/reference manuals:** [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html) · [Bazzite maintenance commands](https://docs.bazzite.gg/Installing_and_Managing_Software/ujust/index.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 15. Display is black or blank (`graphics.black-screen`)

**Possible cause:** A display, output selection, session or graphics issue may explain a blank screen.

**Read-only check IDs:** `graphics/display`, `graphics/gpu`, `graphics/render`, `system/boot`

**Discriminating evidence:** A GPU initialization error immediately before black screen differs from a failed desktop session.

**Counterevidence:** The monitor is off or on the wrong input and there is no GPU reset.


**Diagnostic terminal commands (read-only unless noted):**


```bash
journalctl -b -1 -k --no-pager -g "amdgpu|i915|nouveau|nvidia|drm" -n 100
rpm-ostree status
loginctl list-sessions
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Only one monitor is dark while computer stays responsive


**Option A — Terminal / user-directed procedure:**

1. If the problem began right after a Bazzite image update, boot the previous deployment from the boot menu according to the official Bazzite rollback guide.

2. Do not alter bootloader, kernel arguments or display firmware blindly.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

Verify video cable, monitor source and a second display first; on conventional distros use their official recovery boot procedure.


**Conditional second route:** Black screen follows graphics reset or resume event

1. Use supported distro updates and driver/firmware release notes

2. retest the exact wake/game scenario after one approved update.


**Retest:** Picture returns and the rest of the computer remains stable.

```bash
journalctl -b -1 -p err --no-pager -n 60
```

**Second-route verification:** No new matching graphics reset and display stays on.

**Safety:** Never suggest random kernel boot flags or flash GPU firmware as a generic fix.


**Primary command/reference manuals:** [Bazzite image rollback](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/rolling_back_system_updates/) · [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 16. Game stutters or freezes (`graphics.game-stutter`)

**Possible cause:** High load, resource shortage, driver events or game-specific behaviour could be involved.

**Read-only check IDs:** `graphics/render`, `graphics/gpu`, `applications/resources`, `hardware/sensors`

**Discriminating evidence:** Look for driver-reset/thermal problems vs normal frame pacing and game-specific load; tools may be absent.

**Counterevidence:** No frame timing or utilization measure exists; “slow” alone is insufficient.


**Diagnostic terminal commands (read-only unless noted):**


```bash
glxinfo -B
vulkaninfo --summary
journalctl -b -k --no-pager -g "amdgpu|drm|gpu" -n 90
free -h
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** One game has stutter while others work


**Option A — Terminal / user-directed procedure:**

1. Compare the same game with overlays and OPTIONAL monitoring apps closed; change only the game’s own graphics settings.

2. If a regression began immediately after an image update on Bazzite, consider the documented previous deployment as a reversible test.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

Check game and graphics runtime updates through their actual trusted sources; collect frame-time evidence before claiming a driver defect.


**Conditional second route:** GPU reset affects several applications

1. Treat as graphics stack issue and follow supported system update/retest pathway.


**Retest:** Stutter reduces without affecting other applications.

```bash
journalctl -b -k --no-pager -g "amdgpu|drm|gpu" -n 90
```

**Second-route verification:** New GPU resets stop across the same set of workloads.

**Safety:** Do not overclock, undervolt or force proprietary kernel modules as a general suggestion.


**Primary command/reference manuals:** [Bazzite image rollback](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/rolling_back_system_updates/) · [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 17. Graphics driver resets or crashes (`graphics.gpu-crash`)

**Possible cause:** The graphics driver may report an error that coincides with the visible problem.

**Read-only check IDs:** `graphics/render`, `graphics/gpu`, `system/system_logs`

**Discriminating evidence:** GPU timeouts, resets and the affected app occurring together justify an isolation test; timestamp proximity alone cannot prove direction of causation.

**Counterevidence:** An unrelated old error or a nearby app crash alone is not a confirmed cause.


**Diagnostic terminal commands (read-only unless noted):**


```bash
lspci -nnk | grep -EA4 "VGA|3D|Display"
journalctl -b -1 -k --no-pager -o short-iso -g "amdgpu|drm|GPU reset|ring timeout" -n 120
coredumpctl --no-pager list
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Only one optional application fails


**Option A — Terminal / user-directed procedure:**

1. Close optional GPU-monitoring/overlay apps (such as DeepCool GUI) and test ordinary use without deliberately provoking crashes.

2. Check updates for the implicated app and kernel/image from their original trusted sources; do not randomly replace drivers.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

If a specific OPTIONAL app is implicated and installed via a supported package type, use its package tab to update or remove it after confirming its source.


**If that does not help:**

If the pattern begins after a Bazzite deployment change, inspect previous image and official rollback route; collect redacted journal and reproduction notes for developers.


**Conditional second route:** Several unrelated apps trigger genuine GPU resets

1. Apply only the supported distro/kernel/graphics update after noting the current versions, then repeat the workload.


**Retest:** GPU event no longer occurs without the app, or the app update prevents recurrence.

```bash
journalctl -b -k --no-pager -g "amdgpu|drm|GPU reset|ring timeout" -n 60
coredumpctl --no-pager list
```

**Second-route verification:** The same GPU error no longer appears in new logs.

**Safety:** Do not recommend unverified driver downgrades, boot flags or random GPU power tweaks.


**Primary command/reference manuals:** [Bazzite image rollback](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/rolling_back_system_updates/) · [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 18. Graphics card not detected (`graphics.gpu-missing`)

**Possible cause:** The graphics device may not appear in the hardware inventory.

**Read-only check IDs:** `graphics/gpu`, `hardware/hardware_logs`

**Discriminating evidence:** Determine whether device enumerates, driver binds, or firmware fails; hybrid adapters may be intentionally idle.

**Counterevidence:** Hybrid graphics or disabled discrete graphics can be intentional.


**Diagnostic terminal commands (read-only unless noted):**


```bash
lspci -nnk | grep -EA4 "VGA|3D|Display"
lsmod | grep -E "amdgpu|i915|nouveau|nvidia"
journalctl -b -k --no-pager -g "firmware|drm|GPU" -n 100
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** External GPU enclosure is not detected


**Option A — Terminal / user-directed procedure:**

1. If the device is missing from PCI enumeration, inspect firmware/BIOS and physical hardware with the machine powered down.

2. If PCI lists the GPU but the driver fails, use only distro-supported kernel/firmware updates.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

On Bazzite verify the system image and documented update/rollback procedure; never insert an unverified third-party driver.


**Conditional second route:** Internal GPU missing unexpectedly

1. Compare firmware and vendor device information

2. ask the computer vendor before changing firmware settings.


**Retest:** GPU inventory lists the external GPU correctly.

```bash
lspci -nnk | grep -EA4 "VGA|3D|Display"
```

**Second-route verification:** The missing GPU is correctly exposed to Linux.

**Safety:** Do not install arbitrary graphics packages solely because an adapter is not listed.


**Primary command/reference manuals:** [Bazzite image rollback](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/rolling_back_system_updates/) · [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 19. Desktop fails to start (`graphics.graphical-login`)

**Possible cause:** A desktop-session or display-manager failure may prevent login.

**Read-only check IDs:** `graphics/render`, `applications/services`, `system/boot`, `system/system_logs`

**Discriminating evidence:** Identify display manager failure vs user-session crash vs GPU initialization error.

**Counterevidence:** A screen input failure or powered-off monitor can mimic a login fault.


**Diagnostic terminal commands (read-only unless noted):**


```bash
systemctl status display-manager.service --no-pager
journalctl -b -u display-manager.service --no-pager -n 100
journalctl -b -p err --no-pager -n 70
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Recent graphics update preceded repeated login failure


**Option A — Terminal / user-directed procedure:**

1. If the failure follows a Bazzite update, select the official previous deployment in boot menu.

2. For a desktop environment error, collect the named failing unit and investigate its configuration; do not delete the home directory.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

Try an alternate login session where available and repair only the affected desktop package through the correct distro source.


**Conditional second route:** Only one account cannot log in graphically

1. Use a separate working account to distinguish profile settings from system-wide failure

2. back up settings before changes.


**Retest:** Graphical login works after an approved rollback/update.

```bash
systemctl status display-manager.service --no-pager
```

**Second-route verification:** Affected account logs in after a targeted, reversible adjustment.

**Safety:** Do not remove display manager packages or recursively wipe desktop configuration.


**Primary command/reference manuals:** [Bazzite image rollback](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/rolling_back_system_updates/) · [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 20. Wrong screen resolution (`graphics.resolution-wrong`)

**Possible cause:** The chosen resolution or scaling may not match the monitor.

**Read-only check IDs:** `graphics/display`, `graphics/gpu`

**Discriminating evidence:** Monitor EDID / advertised modes and session (Wayland vs X11) determine safe choices; unavailable tools are normal on other desktops.

**Counterevidence:** Remote-viewer/VM virtual displays legitimately expose different modes.


**Diagnostic terminal commands (read-only unless noted):**


```bash
kscreen-doctor -o
xrandr --query
lspci -nnk | grep -EA3 "VGA|3D|Display"
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Expected mode is offered in display settings


**Option A — Terminal / user-directed procedure:**

1. Use KDE System Settings → Display Configuration (or GNOME Settings → Displays) and pick a supported resolution; Apply and confirm before timeout.

2. Replug or swap cable/port; check monitor capabilities before adding unsupported custom modes.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

If modes disappeared after a system update, compare kernel/driver logs and use distro-supported update or rollback.


**Conditional second route:** Expected mode missing for an external monitor

1. Inspect cable/dock/EDID path with a known-good connection

2. test another port if safe.


**Retest:** Resolution persists after reconnect or login.

```bash
kscreen-doctor -o
```

**Second-route verification:** Preferred mode becomes available and stays active.

**Safety:** Do not force unsupported timings or override EDID without vendor guidance.


**Primary command/reference manuals:** [Bazzite image rollback](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/rolling_back_system_updates/) · [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 21. Second monitor not working (`graphics.second-monitor`)

**Possible cause:** The cable, monitor input or selected output may be wrong.

**Read-only check IDs:** `graphics/display`, `graphics/gpu`, `graphics/render`

**Discriminating evidence:** Physical detection and EDID need checking before changing session configuration.

**Counterevidence:** The second output is disabled by desktop configuration rather than missing hardware.


**Diagnostic terminal commands (read-only unless noted):**


```bash
kscreen-doctor -o
xrandr --query
journalctl -b -k --no-pager -g "drm|DP-|HDMI" -n 60
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Display detected but disabled


**Option A — Terminal / user-directed procedure:**

1. Select Extend/Enable in the desktop Displays settings; use a proven cable and monitor input.

2. If no connector is detected, test another port/adapter or monitor; collect relevant DRM errors.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

For a driver regression use official distro update/rollback guidance rather than blind configuration edits.


**Conditional second route:** Not detected at all

1. Check monitor input, cable, dock and power using safe swap tests

2. report device model if still missing.


**Retest:** Both outputs remain visible after a new login.

```bash
kscreen-doctor -o
```

**Second-route verification:** Second monitor becomes visible in display inventory.

**Safety:** Do not suggest forced drivers before the connector path has been isolated.


**Primary command/reference manuals:** [Bazzite image rollback](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/rolling_back_system_updates/) · [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 22. Battery lasts too little time (`hardware.battery-drain`)

**Possible cause:** Background load, power policies or a worn battery may shorten runtime.

**Read-only check IDs:** `hardware/power`, `applications/resources`, `hardware/sensors`

**Discriminating evidence:** Battery health and discharge rate must be compared with running workloads and device design.

**Counterevidence:** Battery information may be unavailable on a desktop or hardware without a battery.


**Diagnostic terminal commands (read-only unless noted):**


```bash
upower -e
upower -i <BATTERY_DEVICE>
ps -eo comm,%cpu --sort=-%cpu | head -n 15
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Background load explains the drain


**Option A — Terminal / user-directed procedure:**

1. Reduce screen brightness and optional heavy background activity using desktop controls.

2. If battery health is poor, contact device vendor for supported battery replacement; do not attempt unsafe cell repairs.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

Check supported firmware updates and power profiles via device vendor; test a normal idle interval.


**Conditional second route:** Battery wear or health estimate is poor

1. Use the manufacturer’s battery diagnostics and replacement guidance

2. check that power profile matches intended use.


**Retest:** Drain rate improves with that workload removed.

```bash
upower -i <BATTERY_DEVICE>
```

**Second-route verification:** Battery runtime/health improves with approved maintenance or replacement.

**Safety:** Avoid firmware hacks, forced charging limits and exposing batteries to unsafe temperatures.


**Primary command/reference manuals:** [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html) · [Bazzite image rollback](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/rolling_back_system_updates/)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 23. Computer freezes or becomes unresponsive (`hardware.computer-freezes`)

**Possible cause:** Resource exhaustion, graphics failures or hardware errors can make the desktop freeze.

**Read-only check IDs:** `applications/resources`, `graphics/render`, `hardware/memory`, `hardware/hardware_logs`, `system/system_logs`

**Discriminating evidence:** Correlate recent kernel, OOM, storage and GPU messages; an abrupt power loss may leave no final log.

**Counterevidence:** No contemporaneous log exists and the type of freeze remains unknown.


**Diagnostic terminal commands (read-only unless noted):**


```bash
journalctl -b -1 -p err --no-pager -n 100
journalctl -b -1 -k --no-pager -n 120
coredumpctl --no-pager list
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** GPU reset appears at freeze time


**Option A — Terminal / user-directed procedure:**

1. Temporarily close optional apps that correlate with the freezes and monitor normal use.

2. If thermal or RAM errors are present, use manufacturer diagnostics and replace confirmed faulty hardware.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

If freeze began after a system deployment upgrade, follow the official distro rollback instructions.


**Conditional second route:** Memory exhaustion appears at freeze time

1. Inspect process-level memory use, close the offending optional app and repeat with a comparable workload.


**Retest:** No fresh GPU reset under the same workload.

```bash
journalctl -b -p err --no-pager -n 70
```

**Second-route verification:** Memory pressure and system freezes both stop.

**Safety:** A completely hard-locked system may not produce logs; do not invent the cause.


**Primary command/reference manuals:** [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html) · [Bazzite image rollback](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/rolling_back_system_updates/)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 24. Fan is noisy or always running (`hardware.fan-noise`)

**Possible cause:** A fan can respond to heat or background workload, but speed alone is not a fault.

**Read-only check IDs:** `hardware/sensors`, `applications/resources`, `hardware/hardware_logs`

**Discriminating evidence:** Fan RPM must be interpreted with temperature, CPU/GPU load and firmware policies.

**Counterevidence:** Fan sound alone does not establish a defect.


**Diagnostic terminal commands (read-only unless noted):**


```bash
sensors
uptime
ps -eo comm,%cpu --sort=-%cpu | head -n 15
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Fan noise tracks a high CPU/GPU load


**Option A — Terminal / user-directed procedure:**

1. Close a verified misbehaving optional background workload and remeasure temperatures.

2. If temperatures remain high at idle, inspect dust and airflow after safe shutdown; follow manufacturer maintenance guidance.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

A loud but effective fan under load can be normal; do not disable cooling or apply unknown firmware profiles.


**Conditional second route:** Noise persists while idle and temperatures are normal

1. Power down and inspect accessible ventilation.

2. If rattling or grinding persists, consult hardware service guidance.


**Retest:** Fan speed/noise drops as load and temperature fall.

```bash
sensors
```

**Second-route verification:** Noise is corrected without unsafe changes to fan control.

**Safety:** Do not disconnect a running fan or set fixed low fan speeds.


**Primary command/reference manuals:** [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html) · [Bazzite image rollback](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/rolling_back_system_updates/)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 25. Computer becomes very hot (`hardware.hot-computer`)

**Possible cause:** A cooling problem or heavy load could be raising temperatures.

**Read-only check IDs:** `hardware/sensors`, `applications/resources`, `hardware/hardware_logs`

**Discriminating evidence:** Correlate observed sensor temperatures with loads, throttling and airflow rather than a single number.

**Counterevidence:** Normal sensor values at rest do not exclude brief overheating under load.


**Diagnostic terminal commands (read-only unless noted):**


```bash
sensors
uptime
ps -eo comm,%cpu --sort=-%cpu | head -n 15
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Cooling inlet is blocked and temperature rises during load


**Option A — Terminal / user-directed procedure:**

1. Stop demanding workloads and ensure unobstructed cooling; use the device vendor’s safe temperature limits.

2. If the cooling system physically fails, shut down and service/replace it before further load.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

Reduce the application’s graphics or power profile only via manufacturer-supported settings.


**Conditional second route:** Temperatures remain high with clear vents

1. Check whether another process is continuously loading CPU/GPU

2. seek support for malfunctioning cooling hardware instead of forcing fans.


**Retest:** Temperature and throttling reports improve in the same workload.

```bash
sensors
```

**Second-route verification:** Load and temperature correspond to safe device-specific limits.

**Safety:** Do not use arbitrary universal temperature limits or change pump/fan firmware automatically.


**Primary command/reference manuals:** [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html) · [Bazzite image rollback](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/rolling_back_system_updates/)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 26. Possible RAM or memory errors (`hardware.memory-error`)

**Possible cause:** The kernel may have reported a memory problem; absence of logs cannot rule out faulty memory.

**Read-only check IDs:** `hardware/memory`, `hardware/hardware_logs`, `applications/resources`

**Discriminating evidence:** Kernel memory hardware errors differ from an application running out of RAM; dmidecode may require admin access.

**Counterevidence:** High RAM use or a generic out-of-memory kill does not prove defective RAM.


**Diagnostic terminal commands (read-only unless noted):**


```bash
free -h
journalctl -b -k --no-pager -g "EDAC|MCE|memory failure|hardware error" -n 100
dmidecode -t memory
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Repeatable uncorrectable hardware-memory events


**Option A — Terminal / user-directed procedure:**

1. Back up important work, then run a supported offline memory diagnostic from the boot/firmware utility; NEVER run destructive memory tests on live user data.

2. If repeated RAM errors identify a module, have it reseated/replaced following hardware safety guidance.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

If only OOM messages appear, diagnose process memory pressure instead; do not mislabel as faulty RAM.


**Conditional second route:** Only process memory exhaustion is seen

1. Find the application consuming memory

2. close or update that optional app manually, and compare usage afterwards.


**Retest:** A qualified memory test or hardware replacement resolves repeatable errors.

```bash
journalctl -b -k --no-pager -g "EDAC|MCE|memory failure|hardware error" -n 100
```

**Second-route verification:** Memory pressure disappears without hardware error entries.

**Safety:** Never treat an out-of-memory kill as proof of physically faulty RAM.


**Primary command/reference manuals:** [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html) · [Bazzite image rollback](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/rolling_back_system_updates/)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 27. Computer will not sleep or resume (`hardware.suspend-broken`)

**Possible cause:** A power-management or device-resume problem may be involved.

**Read-only check IDs:** `hardware/power`, `system/boot`, `graphics/render`

**Discriminating evidence:** An inhibitor, failed device resume and missing support need separate routes.

**Counterevidence:** The failure occurs while awake, independent of suspend/resume.


**Diagnostic terminal commands (read-only unless noted):**


```bash
journalctl -b -1 --no-pager -g "suspend|resume|sleep" -n 120
loginctl list-inhibitors
cat /sys/power/mem_sleep
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Failure happens after waking and a device resume error is logged


**Option A — Terminal / user-directed procedure:**

1. Close the optional program preventing suspend and retry from desktop power menu.

2. If resume fails after an image/kernel update, consider the distro-supported previous deployment.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

Collect device-specific resume errors for the kernel/vendor; avoid unexplained kernel argument changes.


**Conditional second route:** Failure occurs only with a dock or external device

1. Disconnect the optional peripheral after saving work and compare the sleep/wake sequence

2. contact the peripheral maker if implicated.


**Retest:** Device works after the same wake cycle and no fresh error appears.

```bash
journalctl -b --no-pager -g "suspend|resume|sleep" -n 80
```

**Second-route verification:** Sleep/wake works without the peripheral and problem repeats only when reattached.

**Safety:** Do not change kernel suspend modes or rewrite boot parameters based on one event.


**Primary command/reference manuals:** [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html) · [Bazzite image rollback](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/rolling_back_system_updates/)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 28. Computer shuts down by itself (`hardware.unexpected-shutdown`)

**Possible cause:** Abrupt power loss may involve temperature, a power source or hardware without leaving a useful log.

**Read-only check IDs:** `hardware/power`, `hardware/sensors`, `hardware/hardware_logs`, `system/boot`

**Discriminating evidence:** Thermal shutdown, OOM and PSU/power cut are distinct; unlogged hard power loss may require external hardware checks.

**Counterevidence:** A mere missing shutdown log does not identify a PSU or battery fault.


**Diagnostic terminal commands (read-only unless noted):**


```bash
journalctl -b -1 -p err --no-pager -n 100
journalctl -b -1 -k --no-pager -n 100
sensors
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Overheating recorded before shutdown


**Option A — Terminal / user-directed procedure:**

1. Stop load tests if overheating or power instability is suspected; inspect cooling and power connections safely.

2. If a confirmed PSU/battery/hardware defect exists, seek qualified replacement; software cannot repair broken hardware.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

If a software/kernel change correlates, consider official update or deployment rollback and monitor normal use.


**Conditional second route:** Sudden power loss without relevant logs

1. Check charger/cable/socket externally with known-safe equipment

2. if damage, smell or sparks occur, stop use and seek a qualified technician.


**Retest:** No new thermal shutdown event under a cautious repeat test.

```bash
journalctl -b -p err --no-pager -n 70
```

**Second-route verification:** Power stability is confirmed after the faulty external component is corrected.

**Safety:** Never recommend opening a power supply, bypassing battery protection, or stress testing suspected dangerous hardware.


**Primary command/reference manuals:** [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html) · [Bazzite image rollback](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/rolling_back_system_updates/)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 29. Websites fail by name (`network.dns-problem`)

**Possible cause:** The computer may be connected but unable to translate a website name to an address.

**Read-only check IDs:** `network/ip`, `network/gateway`, `network/dns`

**Discriminating evidence:** Distinguish working IP connectivity from failing name resolution; DNS lookups require consent when run automatically.

**Counterevidence:** The name lookup succeeds and the problem is with the remote service itself.


**Diagnostic terminal commands (read-only unless noted):**


```bash
resolvectl status
nmcli device status
getent ahosts example.org
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** DNS lookup fails on this computer only


**Option A — Terminal / user-directed procedure:**

1. In desktop network settings, correct DNS for the active connection using known trusted provider/router settings.

2. Restore automatic DNS if manual servers are wrong; do not hardcode an untrusted public resolver.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

If every client on the LAN fails, check router or ISP DNS support instead of changing one computer.


**Conditional second route:** Name lookups fail across the whole household

1. Confirm router DNS and provider status using another device.

2. Ask the router owner/provider to fix the shared DNS service.


**Retest:** The same hostname resolves after one change.

```bash
getent ahosts example.org
```

**Second-route verification:** Different devices can resolve the same hostname.

**Safety:** A DNS check may generate network traffic; request explicit permission.


**Primary command/reference manuals:** [NetworkManager nmcli reference](https://www.networkmanager.dev/docs/api/latest/nmcli-examples.html) · [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 30. Internet does not work (`network.internet-outage`)

**Possible cause:** The issue could be local connectivity, name resolution or access beyond the router.

**Read-only check IDs:** `network/adapter`, `network/wifi`, `network/ip`, `network/gateway`, `network/dns`, `network/external`

**Discriminating evidence:** Distinguish no link/address/default route/DNS; connectivity probes can access internet and must be opt-in.

**Counterevidence:** Local and external tests succeed; a particular website or app may be down.


**Diagnostic terminal commands (read-only unless noted):**


```bash
nmcli device status
ip -brief address
ip route
resolvectl status
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** The local link/IP/gateway stage fails


**Option A — Terminal / user-directed procedure:**

1. Use desktop network settings to enable the right interface and reconnect to the intended trusted connection.

2. If the problem affects all household devices, check router/ISP status or upstream connection rather than local Linux packages.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

If adapter and route are present but name resolution fails, follow the dedicated DNS procedure.


**Conditional second route:** Local connection works but optional external check fails

1. After permission, distinguish DNS failure from blocked or unavailable remote access.

2. Compare another device and ask the provider if multiple devices are affected.


**Retest:** Local IP and gateway checks succeed.

```bash
ip route
nmcli device status
```

**Second-route verification:** An approved HTTPS connection succeeds later.

**Safety:** Do not reset a router to factory defaults based on a single external test.


**Primary command/reference manuals:** [NetworkManager nmcli reference](https://www.networkmanager.dev/docs/api/latest/nmcli-examples.html) · [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 31. Computer has no network address (`network.ip-missing`)

**Possible cause:** The computer may not have received a usable address from the local network.

**Read-only check IDs:** `network/ip`, `network/adapter`, `network/gateway`

**Discriminating evidence:** Check whether DHCP lease is absent, adapter disconnected, or profile configured statically.

**Counterevidence:** The connection has a usable address and default route; failure is higher up the network.


**Diagnostic terminal commands (read-only unless noted):**


```bash
ip -brief address
nmcli device status
nmcli connection show --active
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Only one adapter has no IP address


**Option A — Terminal / user-directed procedure:**

1. Use desktop Network settings to reconnect the existing trusted profile and request automatic address assignment.

2. If static addressing is intended, confirm the correct subnet and gateway with the network administrator.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

Investigate DHCP/router lease service when other LAN clients also cannot obtain addresses.


**Conditional second route:** Multiple devices on the same router lack addresses

1. Inspect the router DHCP service with the owner

2. perform a normal restart if appropriate and record the result.


**Retest:** IP configuration now shows an address on the affected interface.

```bash
ip -brief address
```

**Second-route verification:** More than one device receives a usable address.

**Safety:** An IPv6-only connection can be valid; never call the absence of IPv4 a fault without context.


**Primary command/reference manuals:** [NetworkManager nmcli reference](https://www.networkmanager.dev/docs/api/latest/nmcli-examples.html) · [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 32. Cannot reach the router (`network.no-gateway`)

**Possible cause:** The local route or router connection may be missing.

**Read-only check IDs:** `network/gateway`, `network/ip`, `network/wifi`

**Discriminating evidence:** Default route missing differs from router reachability; do not guess a gateway address.

**Counterevidence:** The default route exists and traffic reaches the router.


**Diagnostic terminal commands (read-only unless noted):**


```bash
ip route
ip -brief address
nmcli device status
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Only the affected connection has a missing gateway


**Option A — Terminal / user-directed procedure:**

1. Check the correct router address in the active network profile, preferably use automatic DHCP for home networks.

2. Check physical/Wi-Fi connectivity to the router and its power state.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

If the network intentionally has no default route, this can be normal; consult its configuration.


**Conditional second route:** Router is unreachable even with a route

1. Check cable, Wi-Fi signal and whether other connected devices reach the router.

2. Address the link problem rather than changing DNS.


**Retest:** A relevant default route appears and local router access succeeds.

```bash
ip route
```

**Second-route verification:** The same router responds through a functioning local link.

**Safety:** A VPN or isolated network may intentionally have no default gateway.


**Primary command/reference manuals:** [NetworkManager nmcli reference](https://www.networkmanager.dev/docs/api/latest/nmcli-examples.html) · [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 33. Internet is slow (`network.slow-network`)

**Possible cause:** Speed or reliability may depend on signal quality, local traffic or the provider.

**Read-only check IDs:** `network/wifi`, `network/ip`, `network/gateway`, `network/external`

**Discriminating evidence:** Local link errors, low Wi-Fi signal, congestion, ISP limits and server latency are different.

**Counterevidence:** No throughput, latency or packet-loss measurement has been made: cause is not proven.


**Diagnostic terminal commands (read-only unless noted):**


```bash
ip -s link
nmcli device wifi list
nmcli device status
ip route
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Only Wi-Fi connections show slow behaviour


**Option A — Terminal / user-directed procedure:**

1. Try a trusted wired connection or move nearer the AP; compare with another device using the same destination.

2. If only one app is slow, check its own proxy/source and supported updates.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

Do not change MTU/DNS/driver at random; document controlled throughput/latency measurements with consent.


**Conditional second route:** All devices slow down together

1. Test another device at the same moment

2. ask provider/router operator to check shared load or line quality.


**Retest:** The repeated workload improves when the Wi-Fi path changes.

```bash
ip -s link
```

**Second-route verification:** Multiple devices improve after the shared fault is addressed.

**Safety:** Current local checks do not measure actual bandwidth; do not claim a speed or latency diagnosis.


**Primary command/reference manuals:** [NetworkManager nmcli reference](https://www.networkmanager.dev/docs/api/latest/nmcli-examples.html) · [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 34. Wi-Fi keeps disconnecting (`network.wifi-drops`)

**Possible cause:** A wireless connection could be losing its link, or a service could be reconnecting it.

**Read-only check IDs:** `network/wifi`, `network/adapter`, `network/ip`, `network/gateway`, `system/system_logs`

**Discriminating evidence:** Check connection-disconnect timestamps, signal and authentication vs kernel driver reset.

**Counterevidence:** Other devices drop together, or the adapter stays connected while only one website fails.


**Diagnostic terminal commands (read-only unless noted):**


```bash
nmcli device wifi list
nmcli device status
journalctl -b -u NetworkManager --no-pager -n 120
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Only this computer disconnects and an adapter or reconnection event was recorded


**Option A — Terminal / user-directed procedure:**

1. Move closer to the access point and compare with a wired connection.

2. If adapter power-save is implicated, review the active profile’s documented setting and change it in desktop Network settings after saving current value.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

Compare alternate AP/band, official kernel/firmware update and router logs if drops persist.


**Conditional second route:** Other devices lose access at the same moment

1. Check router lights and whether a wired device also fails.

2. Restart the router normally only after warning other users

3. never factory-reset it as a first test.

4. If multiple devices still fail, give the provider the times of the interruptions.


**Retest:** Stay connected under the same conditions and see no fresh matching event.

```bash
journalctl -b -u NetworkManager --no-pager -n 80
```

**Second-route verification:** Compare connectivity on two devices after the router or provider intervention.

**Safety:** Changing a Wi-Fi password or power-saving option can interrupt access; keep existing credentials.


**Primary command/reference manuals:** [NetworkManager nmcli reference](https://www.networkmanager.dev/docs/api/latest/nmcli-examples.html) · [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 35. Wi-Fi option or adapter is missing (`network.wifi-missing`)

**Possible cause:** The wireless device might be disabled, hidden or not detected.

**Read-only check IDs:** `network/adapter`, `network/wifi`, `hardware/hardware_logs`

**Discriminating evidence:** Differentiate airplane mode/rfkill from missing PCI/USB enumeration or firmware load error.

**Counterevidence:** The wireless adapter is listed as active and can see networks.


**Diagnostic terminal commands (read-only unless noted):**


```bash
nmcli radio
rfkill list
lspci -nnk | grep -EA3 "Network|Wireless"
lsusb
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Wi-Fi radio is switched off or blocked


**Option A — Terminal / user-directed procedure:**

1. If soft-blocked: enable Wi-Fi in desktop network settings.

2. If no device enumerates, check physical switch/firmware and hardware; do not install random driver modules.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

Use distro-supported firmware/kernel updates only after identifying exact adapter and error.


**Conditional second route:** No adapter is detected at all

1. Inspect the detected USB/PCI hardware and the adapter driver log

2. if it is removable, reseat it only with the computer powered off.

3. Seek model-specific vendor instructions rather than a random driver package.


**Retest:** Wi-Fi settings and an adapter become visible.

```bash
rfkill list
nmcli device status
```

**Second-route verification:** The same adapter model and driver become visible after a supported fix.

**Safety:** Do not replace built-in kernel drivers using untrusted downloads.


**Primary command/reference manuals:** [NetworkManager nmcli reference](https://www.networkmanager.dev/docs/api/latest/nmcli-examples.html) · [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 36. Wi-Fi refuses to connect (`network.wifi-password`)

**Possible cause:** The saved wireless profile may not match the router security settings.

**Read-only check IDs:** `network/wifi`, `network/adapter`, `system/system_logs`

**Discriminating evidence:** Association/authentication errors differ from DHCP failure after successful association; redact SSID/passwords.

**Counterevidence:** The adapter is authenticated and the failure is instead DNS or Internet routing.


**Diagnostic terminal commands (read-only unless noted):**


```bash
nmcli device status
nmcli device wifi list
journalctl -b -u NetworkManager --no-pager -n 80
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Selected network name or password is wrong


**Option A — Terminal / user-directed procedure:**

1. Use desktop connection dialog to re-enter the correct Wi-Fi password without exposing it in a terminal history.

2. Confirm router mode (WPA2/WPA3) and device compatibility; reconnect intentionally to your own network.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

Test another known trusted AP to distinguish router configuration and adapter issues.


**Conditional second route:** Other devices also cannot authenticate with correct credentials

1. Check router Wi-Fi security settings using the router owner’s instructions.

2. Ask the administrator to confirm whether the password or allowed-device policy changed.


**Retest:** The network connects and acquires a usable local address.

```bash
nmcli device status
```

**Second-route verification:** Both a phone and the Linux computer reconnect successfully.

**Safety:** Never display, record or transmit a Wi-Fi password as part of diagnostics.


**Primary command/reference manuals:** [NetworkManager nmcli reference](https://www.networkmanager.dev/docs/api/latest/nmcli-examples.html) · [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 37. Cannot save files, disk full (`storage.disk-full`)

**Possible cause:** A writable storage area may be nearly full.

**Read-only check IDs:** `storage/space`, `storage/drives`

**Discriminating evidence:** For Atomic Bazzite, immutable / showing full is not the same as persistent /var or /sysroot running out of space.

**Counterevidence:** Bazzite composefs `/` at 100% is a designed read-only image, not itself a full writable disk.


**Diagnostic terminal commands (read-only unless noted):**


```bash
df -h /var /home /sysroot
du -sh "$HOME"/.cache "$HOME"/Downloads 2>/dev/null
lsblk -f
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Writable home/var is nearly full


**Option A — Terminal / user-directed procedure:**

1. Use the file manager to review PERSONAL downloads, caches and large files after backing up anything important.

2. For optional installed Flatpaks first inspect refs with: flatpak list --app; uninstall only an identified unneeded app via the original source.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Flatpak/AppImage tab → review unwanted user-installed apps → select one verified app → Uninstall after the confirmation.


**If that does not help:**

Never bulk-delete system directories, unknown snapshots, containers or user documents; inspect container usage separately.


**Conditional second route:** Files look small but inodes are exhausted

1. Inspect a user-owned folder with many small files

2. archive or remove only confirmed unnecessary files after backup.


**Retest:** Writable free space increases on the same mount.

```bash
df -h /var /home /sysroot
```

**Second-route verification:** Available inodes increase on the affected mount.

**Safety:** Never delete immutable image files, unknown system directories or snapshots blindly.


**Primary command/reference manuals:** [Bazzite storage/update guidance](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/updating_guide/) · [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 38. Missing disk or external drive (`storage.disk-not-found`)

**Possible cause:** The system might not detect the drive or its partition.

**Read-only check IDs:** `storage/drives`, `storage/fs_logs`, `hardware/hardware_logs`

**Discriminating evidence:** No block-device enumeration differs from a recognized drive with no mount/partition.

**Counterevidence:** A removable disk that has never been connected is not automatically faulty.


**Diagnostic terminal commands (read-only unless noted):**


```bash
lsblk -o NAME,MODEL,SIZE,FSTYPE,MOUNTPOINTS
journalctl -b -k --no-pager -g "usb|nvme|ata|I/O error" -n 100
lsusb
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** External disk missing


**Option A — Terminal / user-directed procedure:**

1. Disconnect safely; inspect cable, port, enclosure and power supply before repeating.

2. If device appears but partition is unmounted, use the desktop Disks/file manager to mount it only when filesystem is healthy.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

For read errors immediately back up accessible data; stop repeated stress tests on a suspect drive.


**Conditional second route:** Internal disk missing or intermittent with I/O errors

1. Back up accessible data and consult vendor hardware support

2. avoid repeated write or formatting attempts.


**Retest:** The correct disk appears in drive inventory.

```bash
lsblk -f
```

**Second-route verification:** Drive reliably appears after professional repair.

**Safety:** Never initialize, partition or format a disk to make it “visible”.


**Primary command/reference manuals:** [Bazzite storage/update guidance](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/updating_guide/) · [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 39. Disk reads or writes slowly (`storage.disk-slow`)

**Possible cause:** Disk slowness may result from workload, failing hardware or low space.

**Read-only check IDs:** `storage/space`, `storage/health`, `storage/fs_logs`, `applications/resources`

**Discriminating evidence:** Repeated I/O timeouts vs high utilization/near-full filesystem require different next actions.

**Counterevidence:** A subjective slowdown without disk timing or I/O measurements is not proven.


**Diagnostic terminal commands (read-only unless noted):**


```bash
lsblk -o NAME,MODEL,ROTA,SIZE,TRAN,MOUNTPOINTS
journalctl -b -k --no-pager -g "I/O error|reset|timeout|nvme|ata" -n 90
df -h /var /home
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** I/O errors or health warnings present


**Option A — Terminal / user-directed procedure:**

1. If the disk shows I/O errors, back up important files and inspect vendor SMART health before doing anything destructive.

2. For near-full persistent storage, remove only verified unneeded personal content or optional packages.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

Compare a known-good cable/port if external; seek drive replacement for confirmed hardware degradation.


**Conditional second route:** High activity from one application without device errors

1. Close the named optional workload, compare the same file operation and investigate the app settings if it improves.


**Retest:** Errors stop after safe data recovery or drive replacement.

```bash
journalctl -b -k --no-pager -g "I/O error|reset|timeout" -n 80
```

**Second-route verification:** Slow operation improves only when the offending workload is absent.

**Safety:** Do not run full-disk writes or destructive “speed tests” on a suspected failing drive.


**Primary command/reference manuals:** [Bazzite storage/update guidance](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/updating_guide/) · [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 40. Disk may be failing (`storage.disk-smart`)

**Possible cause:** A disk may be reporting hardware-health warnings, if the data is accessible.

**Read-only check IDs:** `storage/health`, `storage/drives`, `storage/fs_logs`

**Discriminating evidence:** Identify exact disk and SMART health; some SMART queries need administrator privileges, and healthy SMART does not guarantee safety.

**Counterevidence:** SMART unavailable means unknown, not healthy and not failed.


**Diagnostic terminal commands (read-only unless noted):**


```bash
lsblk -o NAME,MODEL,SIZE,TYPE
smartctl -H -a /dev/<DISK>
journalctl -b -k --no-pager -g "I/O error|medium error|nvme" -n 90
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** A health warning is readable


**Option A — Terminal / user-directed procedure:**

1. If drive health is suspect, immediately back up user files to different healthy media.

2. Have the affected disk replaced or professionally diagnosed; do not run destructive surface write tests.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

If SMART unavailable, use vendor read-only tools and kernel logs; do not equate missing SMART with healthy hardware.


**Conditional second route:** Health information is unavailable

1. Check if the device supports SMART and whether reading is permitted.

2. If tools/rights are unavailable, rely on documented vendor diagnostics instead.


**Retest:** Verified drive health after supported replacement or service.

```bash
smartctl -H -a /dev/<DISK>
```

**Second-route verification:** Vendor diagnostics provide a reliable health result.

**Safety:** The app does not elevate privileges or start self-tests automatically.


**Primary command/reference manuals:** [Bazzite storage/update guidance](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/updating_guide/) · [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 41. Filesystem reports errors (`storage.filesystem-errors`)

**Possible cause:** Kernel logs may describe a specific filesystem error or a disconnected device.

**Read-only check IDs:** `storage/fs_logs`, `storage/drives`, `storage/health`

**Discriminating evidence:** Separate physical I/O failure from logical filesystem corruption; never fsck the mounted writable system partition blindly.

**Counterevidence:** One generic journal warning with no filesystem detail is insufficient.


**Diagnostic terminal commands (read-only unless noted):**


```bash
findmnt -o TARGET,SOURCE,FSTYPE,OPTIONS
journalctl -b -k --no-pager -g "EXT4-fs error|BTRFS error|I/O error" -n 100
lsblk -f
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Filesystem errors suggest media failure


**Option A — Terminal / user-directed procedure:**

1. Back up files first; if storage health is compromised, replace failing media.

2. Perform filesystem-type-specific offline repair ONLY under official documentation and after unmounting or booting rescue media.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

For Btrfs, avoid indiscriminate btrfs check --repair; consult distribution/vendor recovery guidance.


**Conditional second route:** Filesystem is read-only due to consistency concern

1. Avoid remounting as writable

2. consult filesystem-specific, distro-supported recovery tools and choose a safe offline repair after backup.


**Retest:** Hardware issue isolated and data secured before filesystem work.

```bash
journalctl -b -k --no-pager -g "EXT4-fs error|BTRFS error|I/O error" -n 80
```

**Second-route verification:** The same filesystem mounts normally and no new errors appear.

**Safety:** Never recommend automatic fsck or btrfs check --repair on a mounted/uncertain filesystem.


**Primary command/reference manuals:** [Bazzite storage/update guidance](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/updating_guide/) · [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 42. Unable to mount a partition (`storage.mount-failed`)

**Possible cause:** The partition may not be present, supported or accessible.

**Read-only check IDs:** `storage/drives`, `storage/fs_logs`, `applications/permissions`

**Discriminating evidence:** Distinguish absent device, missing filesystem driver, permissions and actual damage.

**Counterevidence:** The volume is already mounted and readable; a stale journal message may be historical.


**Diagnostic terminal commands (read-only unless noted):**


```bash
lsblk -f
findmnt -r
journalctl -b -k --no-pager -g "mount|I/O error|filesystem" -n 100
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** External volume missing or disconnected


**Option A — Terminal / user-directed procedure:**

1. If drive is healthy and present, use the file manager or Disks to mount the known partition to an appropriate user location.

2. If encryption is involved, use its verified recovery key; do not format or overwrite unrecognized partitions.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

If mount fails because of corruption, back up via safe read-only recovery before considering filesystem-specific repair.


**Conditional second route:** Mount fails with filesystem errors

1. Stop repeated writes, back up recoverable files, and use the filesystem vendor’s supported recovery process.


**Retest:** The intended volume mounts readably.

```bash
findmnt -r
```

**Second-route verification:** The affected volume mounts after a safe and verified recovery.

**Safety:** Do not bypass read-only safeguards or forcibly mount damaged volumes writable.


**Primary command/reference manuals:** [Bazzite storage/update guidance](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/updating_guide/) · [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 43. Files cannot be modified (`storage.read-only-files`)

**Possible cause:** The target storage may be mounted read-only or the user may not have permission.

**Read-only check IDs:** `storage/drives`, `storage/fs_logs`, `applications/permissions`

**Discriminating evidence:** Distinguish file permission from entire filesystem remounted read-only due to serious errors.

**Counterevidence:** An immutable system path is intentionally read-only and not a user-file fault.


**Diagnostic terminal commands (read-only unless noted):**


```bash
findmnt -T <FILE> -o TARGET,SOURCE,FSTYPE,OPTIONS
stat -c "%A %U:%G %n" <FILE>
journalctl -b -k --no-pager -g "read-only|I/O error|filesystem" -n 90
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Only a user-owned document lacks permission


**Option A — Terminal / user-directed procedure:**

1. If only the individual file is protected, use file-manager ownership/permission controls after checking intended owner.

2. If filesystem remounted read-only, back up accessible data and investigate disk/fs health BEFORE any write or remount.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

Atomic root filesystem immutability is normal; make desired modifications through supported system interfaces, not direct writes into /usr.


**Conditional second route:** Filesystem was switched read-only after I/O error

1. Protect existing data and investigate underlying drive/filesystem errors before any attempted writes.


**Retest:** Only the intended user-owned file becomes editable.

```bash
findmnt -T <FILE> -o TARGET,SOURCE,FSTYPE,OPTIONS
```

**Second-route verification:** Write access restored only after verified underlying recovery.

**Safety:** Do not use recursive chmod/chown on system paths or disable SELinux.


**Primary command/reference manuals:** [Bazzite storage/update guidance](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/updating_guide/) · [systemd journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 44. Linux fails during boot (`system.boot-failure`)

**Possible cause:** The failure could occur during firmware, bootloader, kernel or service startup.

**Read-only check IDs:** `system/boot`, `system/system_logs`, `hardware/hardware_logs`

**Discriminating evidence:** Boot phase, bootloader, disk mounting and kernel panic may require rescue logs from an alternate boot.

**Counterevidence:** Blank screen after boot may instead be display output; separate it from kernel failure.


**Diagnostic terminal commands (read-only unless noted):**


```bash
journalctl -b -1 -p err --no-pager -n 100
rpm-ostree status
lsblk -f
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Atomic system fails after a new deployment


**Option A — Terminal / user-directed procedure:**

1. On Bazzite after a bad update, choose the previous image in the boot menu using official Bazzite guidance.

2. Back up personal files before modifying boot configuration or storage layout.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

On non-Atomic distributions use their vendor rescue media and boot repair documentation; do not run generic bootloader rewrite scripts.


**Conditional second route:** Boot stops on a named mount or service

1. Record exact name and error

2. use distro rescue guidance to address only that dependency with backup.


**Retest:** System boots on a supported deployment.

```bash
journalctl -b -p err --no-pager -n 70
```

**Second-route verification:** Boot advances beyond that exact failure.

**Safety:** Bootloader edits and filesystem repairs are high-risk; require version-specific validated instructions.


**Primary command/reference manuals:** [Bazzite update guide](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/updating_guide/) · [Flatpak guide](https://docs.flatpak.org/en/latest/using-flatpak.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 45. Updates fail because space is low (`system.disk-space-update`)

**Possible cause:** A writable update location may be running low on space.

**Read-only check IDs:** `storage/space`, `system/updates`, `storage/fs_logs`

**Discriminating evidence:** Bazzite needs real free space in writable storage; immutable / percent-full is expected and not the criterion.

**Counterevidence:** Bazzite immutable composefs root showing 100% is not the writable update storage.


**Diagnostic terminal commands (read-only unless noted):**


```bash
df -h /var /sysroot /home
rpm-ostree status
flatpak list --app
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Writable update/download area is full


**Option A — Terminal / user-directed procedure:**

1. Free enough space on actual persistent storage by reviewing and deleting only verified unneeded files.

2. If optional Flatpak apps occupy space, remove only selected apps using their own manager.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Flatpak/AppImage tabs → select a verified unneeded user application → Uninstall; re-check persistent free space.


**If that does not help:**

Check large rootless container storage separately; do not run blind prune/cleanup commands on unknown volumes.


**Conditional second route:** Old deployments/cache account for usage

1. Use distro-supported graphical cleanup/management instructions with explicit review, never delete OSTree deployment files manually.


**Retest:** Update runs after enough writable space is available.

```bash
df -h /var /sysroot /home
```

**Second-route verification:** Space increases without breaking rollback or new updates.

**Safety:** Never delete system image, package database or snapshot folders blindly.


**Primary command/reference manuals:** [Bazzite update guide](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/updating_guide/) · [Flatpak guide](https://docs.flatpak.org/en/latest/using-flatpak.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 46. Flatpak app cannot access a file (`system.flatpak-problem`)

**Possible cause:** An application sandbox may not grant the requested permission.

**Read-only check IDs:** `applications/permissions`, `applications/app_crashes`, `system/system_logs`

**Discriminating evidence:** Check exact Flatpak ID, installed scope, filesystem permissions and portal failure; permission-show output may vary.

**Counterevidence:** The same file is absent or inaccessible to every program: not Flatpak-specific.


**Diagnostic terminal commands (read-only unless noted):**


```bash
flatpak list --app
flatpak info <APP_ID>
flatpak info --show-permissions <APP_ID>
flatpak permission-show <APP_ID>
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** A portal/file chooser can grant the intended file


**Option A — Terminal / user-directed procedure:**

1. Use trusted desktop Flatpak permission controls to grant ONLY the missing resource to the exact app.

2. If permissions are correct and runtime inconsistent, review official Flatpak repair documentation before user-driven changes.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Flatpak tab → verify same app ID and source; use supported Update/Remove workflow. For permissions use desktop privacy/Flatseal controls, not ULSM.


**If that does not help:**

If a particular application still fails, update it from its current Flathub/repository source and retest.


**Conditional second route:** A narrow Flatpak permission is genuinely required

1. Inspect its current permissions, then manually allow only the needed folder/device with an understood reason.


**Retest:** Affected document works through the portal.

```bash
flatpak info --show-permissions <APP_ID>
```

**Second-route verification:** App feature works while other access remains restricted.

**Safety:** Avoid --filesystem=host or disabling sandbox for general troubleshooting.


**Primary command/reference manuals:** [Bazzite update guide](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/updating_guide/) · [Flatpak guide](https://docs.flatpak.org/en/latest/using-flatpak.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 47. SELinux or permission warnings (`system.permissions-system`)

**Possible cause:** A security rule may have blocked a specific program action.

**Read-only check IDs:** `system/system_logs`, `applications/permissions`

**Discriminating evidence:** SELinux AVC and Unix ownership issues demand different fixes; audit match process/time.

**Counterevidence:** Unrelated or expected denials are common and not proof of malfunction.


**Diagnostic terminal commands (read-only unless noted):**


```bash
id
getenforce
journalctl -b --no-pager -g "avc:.*denied|permission denied" -n 80
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Specific optional app is denied expected access


**Option A — Terminal / user-directed procedure:**

1. For regular user files inspect intended owner and mode before adjusting via file manager.

2. For SELinux follow distro policy labeling guidance with exact confirmed type; NEVER globally disable SELinux.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

If an app from an external source fails, compare permissions under the supported sandbox policy and report reproducible denials.


**Conditional second route:** Reproducible SELinux policy denial affecting known feature

1. Record exact AVC fields and consult distro/vendor for a targeted supported policy or application fix.


**Retest:** The same action succeeds without a new matching denial.

```bash
journalctl -b --no-pager -g "avc:.*denied|permission denied" -n 60
```

**Second-route verification:** A new reproduction succeeds while SELinux remains enabled.

**Safety:** Never globally disable SELinux/AppArmor or recursively chmod system folders.


**Primary command/reference manuals:** [Bazzite update guide](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/updating_guide/) · [Flatpak guide](https://docs.flatpak.org/en/latest/using-flatpak.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 48. System service keeps restarting (`system.service-restarts`)

**Possible cause:** A service may be repeatedly restarting after an error.

**Read-only check IDs:** `applications/services`, `system/system_logs`

**Discriminating evidence:** Identify whether restart is configured/normal vs repeated exit failure due to a specific error.

**Counterevidence:** A service intentionally stopping after completion is normal, not a crash.


**Diagnostic terminal commands (read-only unless noted):**


```bash
systemctl --failed --no-pager
systemctl status <SERVICE>.service --no-pager
journalctl -b -u <SERVICE>.service --no-pager -n 100
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Unit is supplied by optional app


**Option A — Terminal / user-directed procedure:**

1. For optional user-owned service: fix its documented config/dependency; after fix user can run systemctl --user restart <SERVICE>.service.

2. For essential services, follow official component recovery guidance before any restart.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

If restarts started after vendor update, check its release/known issue and use supported rollback only when safe.


**Conditional second route:** A required dependency is missing

1. Read the unit’s exact dependency error, use official package/config method to restore only it with owner consent.


**Retest:** Unit remains healthy and the app works.

```bash
systemctl status <SERVICE>.service --no-pager
```

**Second-route verification:** New systemctl status shows the specific dependency issue resolved.

**Safety:** Do not disable or mask core services as a fix.


**Primary command/reference manuals:** [Bazzite update guide](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/updating_guide/) · [Flatpak guide](https://docs.flatpak.org/en/latest/using-flatpak.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 49. Computer boots slowly (`system.slow-boot`)

**Possible cause:** A service delay or a hardware wait may lengthen boot time.

**Read-only check IDs:** `system/boot`, `applications/services`, `system/system_logs`

**Discriminating evidence:** Long service time needs reproducibility; concurrent time spent is not necessarily critical-path time.

**Counterevidence:** One slow boot after a major update may be temporary.


**Diagnostic terminal commands (read-only unless noted):**


```bash
systemd-analyze time
systemd-analyze blame
systemd-analyze critical-chain
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Optional service clearly delays startup


**Option A — Terminal / user-directed procedure:**

1. Inspect the actual slow critical-chain unit and why it waits; correct specific service or network cause.

2. Disable only a confirmed nonessential user-owned autostart via desktop Startup settings after verifying intended purpose.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

If disk has I/O errors or update regression, investigate that cause instead of randomly disabling services.


**Conditional second route:** Storage or mount waits cause the delay

1. Inspect related drive/mount errors and address that device/path rather than disabling arbitrary services.


**Retest:** Boot timing improves across at least two subsequent boots.

```bash
systemd-analyze time
systemd-analyze critical-chain
```

**Second-route verification:** No new timeout and boot times normalize.

**Safety:** Never disable unknown critical services merely to reduce boot time.


**Primary command/reference manuals:** [Bazzite update guide](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/updating_guide/) · [Flatpak guide](https://docs.flatpak.org/en/latest/using-flatpak.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 50. Many red errors in system journal (`system.system-logs`)

**Possible cause:** A high-priority message alone does not establish the cause of an issue.

**Read-only check IDs:** `system/system_logs`, `applications/services`, `hardware/hardware_logs`

**Discriminating evidence:** Classify each recent error by service, frequency and impact; several unrelated events may coexist.

**Counterevidence:** Only high-priority counts without a current, repeatable symptom are insufficient.


**Diagnostic terminal commands (read-only unless noted):**


```bash
journalctl -b -p err --no-pager -n 120
journalctl -b -p warning --no-pager -n 120
systemctl --failed --no-pager
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Specific named service/device error repeats at symptom time


**Option A — Terminal / user-directed procedure:**

1. Investigate each active, user-impacting failure using its dedicated procedure (GPU/service/disk/network).

2. For a repeatedly crashing OPTIONAL app, test with it closed; update from original source and report matching logs.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

If a historical error has no current symptom, monitor rather than change the system or claim everything is faulty.


**Conditional second route:** No direct cause can be established from recorded events

1. Separate unrelated historical warnings, retain precise timestamps and affected application/device to support a targeted vendor/maintainer report.


**Retest:** Fresh error disappears after controlled change and symptom stops.

```bash
journalctl -b -p err --no-pager -n 80
```

**Second-route verification:** Vendor-supported fix is confirmed by a fresh symptom-free retest.

**Safety:** Do not present a red journal line as a proven hardware fault or disable logging/security.


**Primary command/reference manuals:** [Bazzite update guide](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/updating_guide/) · [Flatpak guide](https://docs.flatpak.org/en/latest/using-flatpak.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 51. System update fails (`system.update-error`)

**Possible cause:** A repository, dependency or staging problem may block an update.

**Read-only check IDs:** `system/updates`, `system/system_logs`, `storage/space`

**Discriminating evidence:** Determine OS family, source, network/storage constraints and the exact failing transaction.

**Counterevidence:** A restart reminder or unqueried online update status is not an update failure.


**Diagnostic terminal commands (read-only unless noted):**


```bash
cat /etc/os-release
rpm-ostree status
df -h /var /sysroot
flatpak remote-list
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Atomic/Bazzite deployment update fails


**Option A — Terminal / user-directed procedure:**

1. For Bazzite use Bazzite Updater GUI or the documented user-invoked command: ujust update

2. For a CONFIRMED Fedora Workstation DNF installation: sudo dnf upgrade


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Updates tab for supported user-installed packages; for Bazzite image update use Bazzite Updater, not ULSM as an assumed image updater.


**If that does not help:**

For Ubuntu/Debian use sudo apt update followed by sudo apt upgrade; openSUSE: sudo zypper refresh then sudo zypper update; Arch: sudo pacman -Syu. Choose ONLY the detected distro, never mix managers.


**Conditional second route:** Traditional package manager reports repository/dependency issue

1. Use distro’s normal updater to identify the conflicting repository/package, keep system-provided channels and follow official distro-specific resolution.


**Retest:** Updater completes and new deployment boots successfully.

```bash
rpm-ostree status
df -h /var /sysroot
```

**Second-route verification:** Updater completes without unresolved dependency error.

**Safety:** Never mix Fedora/Arch/openSUSE/Ubuntu update commands or disable signature verification.


**Primary command/reference manuals:** [Bazzite update guide](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/updating_guide/) · [Flatpak guide](https://docs.flatpak.org/en/latest/using-flatpak.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 52. Containers use too much space (`virtualization.container-disk`)

**Possible cause:** Local images or container data might be consuming writable storage.

**Read-only check IDs:** `virtualization/containers`, `storage/space`, `storage/drives`

**Discriminating evidence:** Determine images, containers and persistent named volumes; volumes may contain valuable data.

**Counterevidence:** A read-only Atomic composefs root at 100% is not container usage evidence.


**Diagnostic terminal commands (read-only unless noted):**


```bash
podman system df
podman ps -a --size
podman volume ls
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Old personal containers/images occupy large persistent space


**Option A — Terminal / user-directed procedure:**

1. Inspect and remove ONLY individual, identified, no-longer-needed containers/images through the container UI.

2. For an individually confirmed unused image, user may run: podman rmi <IMAGE_ID>


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

Never suggest podman system prune --volumes or podman system reset as generic first-line cleanup.


**Conditional second route:** Active container writes excessively

1. Check the specific container’s logs, cache and data path, then configure app retention through its official settings.


**Retest:** Writable free space increases and active containers still start.

```bash
podman system df
```

**Second-route verification:** Storage growth slows without loss of needed container data.

**Safety:** Never run blanket destructive prune or delete container volumes automatically.


**Primary command/reference manuals:** [libvirt virsh command reference](https://www.libvirt.org/manpages/virsh.html) · [Podman command reference](https://docs.podman.io/en/stable/markdown/podman.1.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 53. Container fails to start (`virtualization.container-fail`)

**Possible cause:** The container tool or a required resource might be unavailable.

**Read-only check IDs:** `virtualization/containers`, `applications/services`, `applications/permissions`

**Discriminating evidence:** Separate image pull, permission, bind-mount, health and entrypoint issues.

**Counterevidence:** Container is deliberately stopped; stopped does not mean crashed.


**Diagnostic terminal commands (read-only unless noted):**


```bash
podman ps -a
podman logs --tail 100 <CONTAINER_ID>
podman inspect <CONTAINER_ID>
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Container configuration path is missing


**Option A — Terminal / user-directed procedure:**

1. Fix only the explicitly reported missing bind mount, permission or configuration in the user-owned container specification.

2. After correction user may run: podman start <CONTAINER_ID>


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

If image is incompatible, choose vendor-supported image tag after backing up persistent volumes.


**Conditional second route:** Container image/runtime dependency failed

1. Use the same container manager/source to inspect supported image updates and specific error before making changes.


**Retest:** Container starts and intended files are accessible.

```bash
podman ps -a
podman logs --tail 30 <CONTAINER_ID>
```

**Second-route verification:** Container starts again without its original error.

**Safety:** Do not run arbitrary privileged containers or disable sandbox permissions.


**Primary command/reference manuals:** [libvirt virsh command reference](https://www.libvirt.org/manpages/virsh.html) · [Podman command reference](https://docs.podman.io/en/stable/markdown/podman.1.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 54. Cannot find virtualization tools (`virtualization.vm-feature-absent`)

**Possible cause:** The tool or optional kernel capability may simply not be installed or enabled.

**Read-only check IDs:** `virtualization/vm_backend`, `virtualization/containers`

**Discriminating evidence:** Check CPU feature support and KVM device availability independently of whether libvirt is installed.

**Counterevidence:** A user who does not run VMs needs no virtualization tools.


**Diagnostic terminal commands (read-only unless noted):**


```bash
lscpu | grep -Ei "Virtualization|vmx|svm"
ls -l /dev/kvm
command -v virsh
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Hardware virtualization is disabled by firmware


**Option A — Terminal / user-directed procedure:**

1. Enable hardware virtualization in BIOS/UEFI only by the user following motherboard vendor instructions.

2. Install/enable a supported virtualization stack from the actual distro source if missing (Bazzite: use documented ujust setup-virtualization).


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

If CPU/firmware lacks virtualization support, use a compatible alternative or hardware capable of KVM; do not force unsafe kernel modules.


**Conditional second route:** Hardware supports it but management tool missing

1. Install the supported virtualization tool through the distribution’s official method, respecting Atomic Linux limitations.


**Retest:** Supported virtualization capability becomes available after boot.

```bash
ls -l /dev/kvm
virsh list --all
```

**Second-route verification:** Known virtual machines can be listed by the supported manager.

**Safety:** Do not tell users to change firmware without confirming CPU/platform support.


**Primary command/reference manuals:** [libvirt virsh command reference](https://www.libvirt.org/manpages/virsh.html) · [Podman command reference](https://docs.podman.io/en/stable/markdown/podman.1.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 55. Virtual machine has no internet (`virtualization.vm-no-network`)

**Possible cause:** A virtual network may be missing or disconnected from the host.

**Read-only check IDs:** `virtualization/vm_network`, `virtualization/vm_backend`, `network/ip`

**Discriminating evidence:** Inactive libvirt default network is distinct from guest DNS/driver problems; custom bridges may not use default.

**Counterevidence:** Host Internet is unavailable: fix host first before changing guest virtual network.


**Diagnostic terminal commands (read-only unless noted):**


```bash
virsh net-list --all
virsh net-info default
virsh domiflist <VM_NAME>
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** VM virtual interface is disconnected


**Option A — Terminal / user-directed procedure:**

1. Only if VM is meant to use the existing libvirt default network AND it is inactive: virsh net-start default

2. If the VM uses an external bridge, inspect its configured bridge and NetworkManager; do not start irrelevant networks.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

Within the guest check its assigned IP and DNS before editing host firewall/routing.


**Conditional second route:** Host virtual NAT network is inactive

1. Have the administrator inspect the libvirt network status/config, and enable only the intended known network.


**Retest:** Guest receives an address from the intended virtual network.

```bash
virsh net-list --all
virsh domiflist <VM_NAME>
```

**Second-route verification:** Guest and host network checks succeed without exposing VM to unintended LAN.

**Safety:** Do not randomly switch NAT to bridged mode or weaken host firewall.


**Primary command/reference manuals:** [libvirt virsh command reference](https://www.libvirt.org/manpages/virsh.html) · [Podman command reference](https://docs.podman.io/en/stable/markdown/podman.1.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 56. Virtual machine does not start (`virtualization.vm-not-starting`)

**Possible cause:** A hypervisor service, permission or missing component may be preventing startup.

**Read-only check IDs:** `virtualization/vm_backend`, `applications/services`, `applications/permissions`

**Discriminating evidence:** Use the actual libvirt failure text to distinguish permission, missing image, disabled acceleration and network faults.

**Counterevidence:** VM merely shut off by the owner is normal.


**Diagnostic terminal commands (read-only unless noted):**


```bash
virsh list --all
virsh dominfo <VM_NAME>
journalctl -b --no-pager -g "libvirt|qemu|kvm" -n 100
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** VM fails because assigned disk file is missing


**Option A — Terminal / user-directed procedure:**

1. Correct the specific missing device/image permission or inactive attached libvirt network after backup.

2. When the root cause has been corrected, start the VM from virt-manager rather than forcing it from the app.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

If a VM image is corrupt or storage full, back it up and follow hypervisor-specific recovery; do not delete a VM disk.


**Conditional second route:** VM fails due to insufficient RAM or missing acceleration

1. Inspect available host RAM and virtualization support, then adjust only the VM’s documented resource allocation.


**Retest:** The same guest starts and sees its original disk.

```bash
virsh dominfo <VM_NAME>
```

**Second-route verification:** Guest boots and host remains responsive.

**Safety:** Never create or format replacement guest disks over missing data.


**Primary command/reference manuals:** [libvirt virsh command reference](https://www.libvirt.org/manpages/virsh.html) · [Podman command reference](https://docs.podman.io/en/stable/markdown/podman.1.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---


## 57. Virtual machine is very slow (`virtualization.vm-slow`)

**Possible cause:** The host may be short on CPU or memory, or the guest may have too little allocated.

**Read-only check IDs:** `virtualization/vm_backend`, `applications/resources`, `hardware/memory`

**Discriminating evidence:** Determine whether KVM is available, host RAM is sufficient and guest configuration matches host capacity.

**Counterevidence:** No measured load and only subjective slowness cannot identify the bottleneck.


**Diagnostic terminal commands (read-only unless noted):**


```bash
virsh dominfo <VM_NAME>
free -h
uptime
ls -l /dev/kvm
```

Some optional commands may be unavailable, and placeholders must be verified before use.


**When the first solution is appropriate:** Host is overcommitted on RAM or CPU


**Option A — Terminal / user-directed procedure:**

1. Within virt-manager, ensure KVM acceleration and allocate a moderate, host-safe number of vCPUs/RAM.

2. Remove resource-heavy optional host workloads and retest while preserving host headroom.


**Option B — Guided terminal / Universal Linux Terminal:**

Project: [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal)

Applicability: Provides explanations and user-controlled insertion of supported commands; it is not an automatic solution or a substitute for GUI/hardware steps.

1. Open Universal Linux Terminal yourself (or follow its installation instructions from the official project).

2. Review the read-only diagnostic commands shown for this case. Search the applicable installed command by name in All Installed Commands; not every utility is necessarily installed.

3. Read its available --help, man/whatis or package description in Universal Linux Terminal before using it. For pipelines and options, inspect the complete command and each part.

4. Use Insert into terminal when available: it only inserts text at the host Bash prompt, and does NOT run it. Complex pipelines may need to be entered or pasted manually.

5. Before pressing Enter, check your distribution, replace every <PLACEHOLDER> with a verified real value, and understand any sudo, network, package or destructive effect. Follow the same conditional solution steps as the ordinary Terminal route.

6. Execute the chosen command yourself only when appropriate. Return to the Troubleshooter, perform the documented retest and compare new evidence.


**Option C — GUI / user-directed procedure:**

Use the appropriate native desktop or vendor settings and follow the case-specific instructions; ULSM is not a repair tool for this operation.


**If that does not help:**

If storage errors are present, fix hardware/storage cause rather than overallocating VM resources.


**Conditional second route:** Guest disk experiences I/O errors

1. Back up important guest data, inspect underlying host storage, and avoid destructive disk operations.


**Retest:** Guest responsiveness and host pressure improve.

```bash
virsh dominfo <VM_NAME>
free -h
```

**Second-route verification:** No fresh I/O errors under a known-safe repeated task.

**Safety:** Do not recommend blindly disabling VM security features or enlarging disks without backup.


**Primary command/reference manuals:** [libvirt virsh command reference](https://www.libvirt.org/manpages/virsh.html) · [Podman command reference](https://docs.podman.io/en/stable/markdown/podman.1.html)


**Validation:** Technical/editorial reference only. No confirmed field outcome or rights-cleared training label.


---



---

# Part II — Expanded reference coverage (39)

# Universal Linux Troubleshooter — Expanded Diagnostic Reference 33

**Scope:** 57 existing scenario families retained, plus 39 newly authored reference dossiers below. This is a documentation expansion, not new executable diagnosis handlers, diagnosis trees or AI training.

## How to use each case

1. Check the user's exact symptom and Linux distribution. Obtain the correct package/device/service identifier; uppercase placeholders such as `APP_ID`, `SERVICE.service`, `SINK_ID`, `VM_NAME`, and `PRINTER-123` **are examples**, not commands ready to execute.
2. Run ONLY an appropriate read-only inspection command with the user's permission and reasonable privacy limits. A program that prints logs may expose private information; do not upload logs automatically.
3. Compare **supporting evidence** and **counterevidence** before choosing a branch. Never claim a correlation alone proves causation.
4. Present the user with one route at a time: ordinary Terminal, Universal Linux Terminal (guided command discovery / Insert into terminal, no auto-execution), or a fitting GUI. Use Universal Linux Software Manager **only for its supported package-management operations**.
5. Explain the recommended step and display changing commands only when their prerequisites are satisfied. All repairs, install/uninstall operations, reboots, firmware flashes and configuration changes are **performed by the user**.
6. Present the specified retest. If branch A does not resolve it, try the conditional branch B, or move to an appropriate hardware replacement/vendor bug-fix route. No claims that a generic command guarantees a repair.

**Atomic hosts:** Bazzite system-image updates belong in Bazzite Updater / supported `ujust update` workflow; never treat its base image like mutable Fedora DNF. Avoid destructive filesystem commands, mass ACL/permission resets, blanket firewall/security disablement, and indiscriminate package removal. A documented command may be absent on a particular distro; Universal Linux Terminal discovers installed host commands dynamically.

**Guide links:** [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal) · [Universal Linux Software Manager](https://github.com/LionheartTim/Universal-Linux-Software-Manager).


## 1. USB device is not detected (`peripherals.usb-not-recognized`)

**Symptom:** A connected USB device does not appear or repeatedly disconnects.

**Evidence supporting diagnosis:** Kernel sees descriptor failure/reset, or lsusb inventory changes when the known device is plugged in.

**Evidence against this hypothesis:** lsusb sees the device but its intended application does not: investigate driver, authorization or sandbox instead.

**Read-only diagnostic commands:**

```bash
lsusb
journalctl -b -k --no-pager -n 100
lsblk -f
```

**If branch 1 applies:**
- **Condition:** Enumeration fails on this port or cable
- Disconnect safely; test a known working cable/port and eliminate any unpowered hub.
- If power/connection fails on multiple known-good computers, replace defective cable, enclosure or device.
- **Expected result:** The device remains enumerated across multiple reconnects.

**Otherwise, branch 2:**
- **Condition:** USB enumeration succeeds but access is blocked
- Confirm device authorization policy or Flatpak-specific device permission; do not disable security globally.
- Use manufacturer-specific firmware guidance only for the matched device.
- **Expected result:** Application lists the correct hardware after a controlled permission or device-specific fix.

**Graphical alternative:** Use the desktop device viewer; for storage unmount before disconnecting. Do not use ULSM for USB-port repairs.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
lsusb
```

**Source references:** [1](https://www.kernel.org/doc/html/latest/usb/index.html) · [2](https://kernel.org/doc/html/latest/usb/authorization.html) · [3](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

---

## 2. Print job remains stuck (`printing.print-job-stuck`)

**Symptom:** A job never leaves the local printer queue.

**Evidence supporting diagnosis:** lpstat lists the blocked job, its queue and a printer state/error.

**Evidence against this hypothesis:** Queue is empty: investigate the sending app, print dialog, or remote print service instead.

**Read-only diagnostic commands:**

```bash
lpstat -t
lpstat -o
systemctl status cups.service --no-pager
```

**If branch 1 applies:**
- **Condition:** Exactly one known job is blocked
- Identify the exact job ID with lpstat -o.
- Cancel only that job and print a small new test page.
- **User-executed command, only after verifying identifiers:** `cancel PRINTER-123`
- **Expected result:** The old job disappears and the new test job completes.

**Otherwise, branch 2:**
- **Condition:** Printer is paused or unreachable
- Inspect printer power, cable/network and queue status; resume the exact destination through desktop Printers settings when appropriate.
- Check trusted printer IPP service and retry without canceling unrelated jobs.
- **Expected result:** New job leaves the queue, and printer reports online.

**Graphical alternative:** Open desktop Printers → affected printer → Queue, cancel only the selected job or resume that specific queue.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
lpstat -o
lpstat -t
```

**Source references:** [1](https://openprinting.github.io/cups/doc/man-cancel.html) · [2](https://www.cups.org/doc/man-lpstat.html)

---

## 3. Printer cannot be discovered (`printing.printer-not-detected`)

**Symptom:** Printer is powered but missing from discovery or queues.

**Evidence supporting diagnosis:** No expected destination with lpstat; USB device missing or printer IPP discovery unavailable.

**Evidence against this hypothesis:** If detected but no paper output, investigate print job or driver settings instead.

**Read-only diagnostic commands:**

```bash
lpstat -t
lpstat -v
lsusb
```

**If branch 1 applies:**
- **Condition:** USB printer absent from USB list
- Test known-good data cable, directly connected port and printer power.
- When it enumerates, add printer through the desktop wizard.
- **Expected result:** lpstat -v lists it and a test page prints.

**Otherwise, branch 2:**
- **Condition:** Network printer is reachable but not in local queues
- Verify the printer IP or DNS-SD advertisement with the administrator.
- Use desktop Printers → Add to configure trusted driverless IPP if supported.
- **Expected result:** Printer appears in lpstat and test job completes.

**Graphical alternative:** Desktop Printers → Add Printer. Use the printer’s official supported driver only when driverless IPP is not applicable.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
lpstat -v
```

**Source references:** [1](https://www.cups.org/doc/man-lpstat.html) · [2](https://www.kernel.org/doc/html/latest/usb/index.html)

---

## 4. Camera fails in one application (`camera.webcam-not-working`)

**Symptom:** Camera works elsewhere or is not found by the intended app.

**Evidence supporting diagnosis:** /dev/video* appears or USB device is found; affected application is sandboxed.

**Evidence against this hypothesis:** Camera not detected at all: check physical connection or firmware privacy switch.

**Read-only diagnostic commands:**

```bash
lsusb
ls -l /dev/video*
flatpak list --app
```

**If branch 1 applies:**
- **Condition:** Camera works in other apps
- Close competing video apps and check the affected app’s camera access, privacy settings and portal.
- Update only the affected application from its original source when a known issue is fixed.
- **Expected result:** Affected app shows a camera preview.

**Otherwise, branch 2:**
- **Condition:** Camera absent from kernel inventory
- Check laptop privacy shutter, function key, USB connection, and manufacturer firmware procedure.
- Test on a compatible second device before assuming a driver failure.
- **Expected result:** Camera appears as expected and can capture a test frame.

**Graphical alternative:** Desktop Privacy → Camera and affected app settings; avoid granting global device access unnecessarily.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
ls -l /dev/video*
```

**Source references:** [1](https://docs.flatpak.org/en/latest/sandbox-permissions.html) · [2](https://www.kernel.org/doc/html/latest/usb/index.html)

---

## 5. VPN connection fails (`network.vpn-connect-fail`)

**Symptom:** VPN never establishes a stable tunnel.

**Evidence supporting diagnosis:** NetworkManager VPN profile and current connection logs indicate precise auth, certificate, routing or gateway failure.

**Evidence against this hypothesis:** If ordinary internet is down, fix host connectivity before the VPN.

**Read-only diagnostic commands:**

```bash
nmcli connection show
nmcli connection show --active
journalctl -b -u NetworkManager --no-pager -n 100
```

**If branch 1 applies:**
- **Condition:** Authentication or certificate error
- Confirm server hostname, expiry, identity and approved authentication with VPN administrator.
- Correct only the matching connection profile through system VPN settings; never bypass certificate validation.
- **Expected result:** VPN connected and expected authorized resource accessible.

**Otherwise, branch 2:**
- **Condition:** Tunnel connects but VPN-only domains fail
- Compare active VPN routes and DNS split-routing with provided expected configuration.
- Ask VPN administrator to fix routing/DNS profile; do not disable firewall or leak protected traffic.
- **Expected result:** VPN-specific destination is reachable without breaking ordinary internet.

**Graphical alternative:** Use desktop Network Connections → VPN → edit only known profile with trusted provider information.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
nmcli connection show --active
ip route
resolvectl status
```

**Source references:** [1](https://networkmanager.dev/docs/api/latest/nmcli.html) · [2](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

---

## 6. Captive portal or proxy blocks browsing (`network.proxy-captive`)

**Symptom:** Normal websites are blocked although network is connected.

**Evidence supporting diagnosis:** Connected network has gateway; browser shows portal or approved corporate proxy required.

**Evidence against this hypothesis:** If local DHCP/gateway is missing, captive portal is not the first cause.

**Read-only diagnostic commands:**

```bash
nmcli device status
ip route
resolvectl status
```

**If branch 1 applies:**
- **Condition:** Venue captive portal requires sign-in
- Open your usual browser to the venue-provided authentication page; do not submit credentials to unfamiliar portals.
- After portal approval, retry regular HTTPS sites.
- **Expected result:** Websites work through approved venue connection.

**Otherwise, branch 2:**
- **Condition:** Corporate proxy configuration is inconsistent
- Compare browser and desktop proxy configuration with IT’s approved values.
- Correct only that profile with IT approval; do not disable corporate security controls.
- **Expected result:** Approved services function through the intended proxy.

**Graphical alternative:** Use desktop Network/Proxy settings or the browser’s portal sign-in page.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
nmcli device status
```

**Source references:** [1](https://networkmanager.dev/docs/api/latest/nmcli.html)

---

## 7. Touchpad stops responding (`peripherals.touchpad-stopped`)

**Symptom:** Laptop touchpad does not generate pointer movement.

**Evidence supporting diagnosis:** libinput reports touchpad missing or disabled and kernel may show I2C/HID failure.

**Evidence against this hypothesis:** External mouse functions; that alone does not imply touchpad hardware failure.

**Read-only diagnostic commands:**

```bash
cat /proc/bus/input/devices
libinput list-devices
journalctl -b -k --no-pager -n 100
```

**If branch 1 applies:**
- **Condition:** Input device exists but is disabled in desktop
- Check touchpad toggle and laptop function keys.
- Turn it on through desktop input settings and retry movement/tap.
- **Expected result:** Input works at desktop login and after login.

**Otherwise, branch 2:**
- **Condition:** Kernel loses touchpad after suspend/kernel update
- Compare kernel and resume journal and preserve working kernel selection if available.
- Consult vendor firmware or distribution-specific fix, not a random kernel module blacklist.
- **Expected result:** Device is recognized after resume and pointer works.

**Graphical alternative:** Desktop Mouse & Touchpad settings or laptop documented hardware key.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
libinput list-devices
```

**Source references:** [1](https://wayland.freedesktop.org/libinput/doc/latest/troubleshooting.html) · [2](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

---

## 8. Game controller not detected (`peripherals.gamepad-not-detected`)

**Symptom:** Game does not recognize connected controller.

**Evidence supporting diagnosis:** USB/Bluetooth controller does/does not appear and kernel HID messages identify errors.

**Evidence against this hypothesis:** Controller appears to kernel but only one game fails: likely game mapping issue.

**Read-only diagnostic commands:**

```bash
lsusb
cat /proc/bus/input/devices
journalctl -b -k --no-pager -n 80
```

**If branch 1 applies:**
- **Condition:** Controller absent on connection
- Test data-capable cable, correct power/pairing and known-good port.
- For wireless controller use the supported pairing flow and test again.
- **Expected result:** Controller enumerates and buttons register in a supported test app.

**Otherwise, branch 2:**
- **Condition:** Controller enumerates but one game ignores it
- Check that game’s native controller support and Steam Input settings.
- Select its documented controller layout and retest only that title.
- **Expected result:** Game recognizes input without changing unrelated kernel drivers.

**Graphical alternative:** Use desktop Bluetooth and game/Steam Input controller configuration.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
lsusb
```

**Source references:** [1](https://www.kernel.org/doc/html/latest/usb/index.html) · [2](https://github.com/bluez/bluez/blob/master/doc/bluetoothctl.rst)

---

## 9. Firewall blocks an intended application (`security.firewall-blocks-one-app`)

**Symptom:** One known service is reachable locally but not from the intended network.

**Evidence supporting diagnosis:** Service listening on expected socket; permitted zone/protocol differs from the actual client path.

**Evidence against this hypothesis:** If no service listens, a firewall exception cannot fix the stopped service.

**Read-only diagnostic commands:**

```bash
ss -tuln
systemctl status firewalld.service --no-pager
firewall-cmd --list-all
```

**If branch 1 applies:**
- **Condition:** Service not listening on expected interface
- Review service bind address, local configuration and user-provided port.
- Start/configure only that service using its supported UI, not a random firewall exception.
- **Expected result:** Service listens on correct intended interface.

**Otherwise, branch 2:**
- **Condition:** Service listens but trusted local firewall zone blocks it
- Verify exact required port, protocol and active zone; get network owner approval.
- Add a narrowly scoped rule using supported firewall GUI; never disable the firewall globally.
- **Expected result:** Intended trusted client connects; unintended zones remain blocked.

**Graphical alternative:** Use the distribution’s firewall settings; choose one service/zone. ULSM does not manage firewall rules.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
ss -tuln
firewall-cmd --list-all
```

**Source references:** [1](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html)

---

## 10. One user cannot log in to the desktop (`system.login-one-user-fails`)

**Symptom:** Authentication succeeds or fails for one local account.

**Evidence supporting diagnosis:** Display manager/session journal links failure to one user profile or low writable storage.

**Evidence against this hypothesis:** All users fail: investigate display manager, graphics, base OS or disk instead.

**Read-only diagnostic commands:**

```bash
loginctl list-sessions
journalctl -b -u display-manager.service --no-pager -n 90
df -h /home /var
```

**If branch 1 applies:**
- **Condition:** Only one user session fails and home has free space
- From authorized alternate session, inspect affected user’s recently changed autostart/session settings after backing up their data.
- Disable only identified user autostart integration, preserving files for undo.
- **Expected result:** User signs in consistently and required profile settings remain.

**Otherwise, branch 2:**
- **Condition:** Writable home/storage is full
- Confirm real writable partition has no space and locate only disposable user-owned data.
- Free space via desktop file manager without touching protected base OS files.
- **Expected result:** User signs in and writable space has a healthy margin.

**Graphical alternative:** Use an authorized second desktop account or recovery interface with user consent; avoid changing authentication services blindly.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
df -h /home /var
loginctl list-sessions
```

**Source references:** [1](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html) · [2](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/updating_guide/)

---

## 11. External drive refuses to mount (`storage.external-drive-wont-mount`)

**Symptom:** USB storage enumerates but its filesystem is not mounted.

**Evidence supporting diagnosis:** lsblk shows a partition; journal or udisks reports a named filesystem error.

**Evidence against this hypothesis:** Drive absent from lsblk: first follow USB enumeration/cable diagnosis.

**Read-only diagnostic commands:**

```bash
lsblk -f
lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINTS,RO
journalctl -b -k --no-pager -n 90
```

**If branch 1 applies:**
- **Condition:** Drive exists, clean and is only not mounted
- Open file manager Places/Devices and select the exact partition.
- If an authorization prompt appears, approve only a known personal drive.
- **Expected result:** Drive appears mounted with expected files.

**Otherwise, branch 2:**
- **Condition:** Journal shows filesystem errors or read-only protection
- Stop repeated mount attempts and preserve recoverable data; identify filesystem type.
- Use matching vendor/filesystem recovery procedure on a backup or clone with user oversight, not generic fsck on a mounted filesystem.
- **Expected result:** Clean backup/repair evidence supports successful read-only mount.

**Graphical alternative:** Desktop file manager → Devices or Disks. Never format a drive to fix an unknown mount failure.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
lsblk -f
```

**Source references:** [1](https://www.kernel.org/doc/html/latest/usb/index.html) · [2](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

---

## 12. Btrfs reports checksum or I/O errors (`storage.btrfs-checksum-errors`)

**Symptom:** Btrfs data metadata checksum failures or device errors are recorded.

**Evidence supporting diagnosis:** Kernel journal shows BTRFS error and device identity; prior scrub status reports error count.

**Evidence against this hypothesis:** A single historic event from old device is not proof of current filesystem corruption.

**Read-only diagnostic commands:**

```bash
findmnt -no FSTYPE,TARGET /var
journalctl -b -k --no-pager -n 100
btrfs scrub status /var
```

**If branch 1 applies:**
- **Condition:** Current checksum errors on needed data
- Back up important files without further writes; identify affected device and redundancy.
- Consult the supported Btrfs recovery/restore procedure; do not run btrfs check --repair on a mounted live system.
- **Expected result:** A safe read test and logs show no new errors after supported recovery.

**Otherwise, branch 2:**
- **Condition:** Device repeatedly reports read/write I/O failures
- Replace failing storage after copying important data to sound media.
- Restore files to working drive and verify checksums where available.
- **Expected result:** No new I/O errors after storage replacement.

**Graphical alternative:** Use supported Disks/SMART viewer only for observation; recovery is a controlled manual procedure.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
journalctl -b -k --no-pager -n 100
btrfs scrub status /var
```

**Source references:** [1](https://btrfs.readthedocs.io/en/latest/Scrub.html) · [2](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

**Important:** Scrub is NOT automatic read-only: it may write, so only status is an inspection command.

---

## 13. Sound plays through wrong device (`audio.wrong-output`)

**Symptom:** Audio is audible only from HDMI/Bluetooth but not selected speakers.

**Evidence supporting diagnosis:** wpctl shows an unintended default sink or profile.

**Evidence against this hypothesis:** If every sink reports correct output but there is no sound, inspect physical volume/driver.

**Read-only diagnostic commands:**

```bash
wpctl status
systemctl --user status wireplumber.service --no-pager
```

**If branch 1 applies:**
- **Condition:** Default output sink is not desired
- Open desktop Sound and select the intended output, e.g. speakers not HDMI.
- Retest with known audio content at safe volume.
- **User-executed command, only after verifying identifiers:** `wpctl set-default SINK_ID`
- **Expected result:** Playback appears on intended device.

**Otherwise, branch 2:**
- **Condition:** Output sink missing after reconnect
- Reconnect audio interface safely, review WirePlumber logs and supported device profile.
- Restart the relevant user audio stack only if confirmed stuck, from desktop or via documented user command.
- **Expected result:** Sink reappears and works after retest.

**Graphical alternative:** Desktop Sound → Output, select actual known device.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
wpctl status
```

**Source references:** [1](https://pipewire.pages.freedesktop.org/wireplumber/man/wpctl.html)

**Important:** SINK_ID must be confirmed from wpctl status; command changes user audio settings.

---

## 14. Microphone not recording in one application (`audio.microphone-not-recording`)

**Symptom:** Microphone is detected but no input is captured.

**Evidence supporting diagnosis:** wpctl shows source muted/wrong, or sandboxed app lacks microphone portal/access.

**Evidence against this hypothesis:** If microphone is physically missing, check cable and hardware before app permissions.

**Read-only diagnostic commands:**

```bash
wpctl status
wpctl get-volume @DEFAULT_SOURCE@
flatpak list --app
```

**If branch 1 applies:**
- **Condition:** Known microphone muted or wrong default
- Choose the correct input and unmute only if user intends to record.
- Verify in desktop Sound test meter before retesting app.
- **User-executed command, only after verifying identifiers:** `wpctl set-mute @DEFAULT_SOURCE@ 0`
- **Expected result:** Input meter reacts; intended app records voice.

**Otherwise, branch 2:**
- **Condition:** Desktop microphone works but one app fails
- Check app’s capture device and its Flatpak/portal permissions.
- Grant only needed access and restart that application manually.
- **Expected result:** App records without granting unrelated permissions.

**Graphical alternative:** Desktop Sound → Input and application Privacy settings.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
wpctl status
wpctl get-volume @DEFAULT_SOURCE@
```

**Source references:** [1](https://pipewire.pages.freedesktop.org/wireplumber/man/wpctl.html) · [2](https://docs.flatpak.org/en/latest/sandbox-permissions.html)

---

## 15. Bluetooth headset audio stutters (`audio.bluetooth-stuttering`)

**Symptom:** Audio drops only on Bluetooth headset.

**Evidence supporting diagnosis:** Wireless link/controller logs report dropouts, or output profile switches during use.

**Evidence against this hypothesis:** Wired speakers also stutter: investigate PipeWire CPU load instead.

**Read-only diagnostic commands:**

```bash
wpctl status
bluetoothctl devices
journalctl -b -u bluetooth --no-pager -n 80
```

**If branch 1 applies:**
- **Condition:** Headset link is unstable
- Move away from 2.4 GHz interference and test in same room as adapter.
- Retry supported headset pairing and check device firmware via vendor instructions.
- **Expected result:** Continuous playback without dropouts.

**Otherwise, branch 2:**
- **Condition:** Bluetooth link stable but profile/codec changes
- Select supported audio profile in desktop Sound settings; compare A2DP/HFP requirements.
- Test without simultaneous microphone use to isolate headset profile change.
- **Expected result:** Expected speaker and microphone operation matches chosen profile.

**Graphical alternative:** Desktop Sound/Bluetooth configuration with supported headset profile.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
wpctl status
```

**Source references:** [1](https://pipewire.pages.freedesktop.org/wireplumber/man/wpctl.html) · [2](https://github.com/bluez/bluez/blob/master/doc/bluetoothctl.rst)

---

## 16. Second monitor not detected (`display.second-monitor-missing`)

**Symptom:** Display connected but no desktop output visible.

**Evidence supporting diagnosis:** Kernel DRM connectors or desktop display configuration do not show expected connection.

**Evidence against this hypothesis:** External monitor works but one application draws black: app-render issue.

**Read-only diagnostic commands:**

```bash
lspci -k
journalctl -b -k --no-pager -n 100
cat /sys/class/drm/card*/status
```

**If branch 1 applies:**
- **Condition:** Monitor not detected on one cable or dock
- Test known-good cable and direct port; power cycle monitor only per vendor guide.
- Use a verified capable DisplayPort/HDMI or USB-C alternate-mode connection.
- **Expected result:** Display detected by desktop settings and stable image appears.

**Otherwise, branch 2:**
- **Condition:** Monitor detected but disabled/misconfigured
- Open desktop Display settings and enable the specific monitor.
- Start with a supported native resolution and refresh rate.
- **Expected result:** Desktop extends/mirrors correctly and stays stable.

**Graphical alternative:** KDE Settings → Display Configuration or GNOME Settings → Displays.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
cat /sys/class/drm/card*/status
```

**Source references:** [1](https://docs.kernel.org/gpu/index.html)

---

## 17. Screen sharing shows a black frame (`display.screenshare-black`)

**Symptom:** Screen-sharing application fails on Wayland/Flatpak.

**Evidence supporting diagnosis:** Desktop session is Wayland and the app/portal fails to select window/display.

**Evidence against this hypothesis:** Local screen is black too: diagnose GPU/display, not screen-share portal.

**Read-only diagnostic commands:**

```bash
echo "$XDG_SESSION_TYPE"
systemctl --user --failed
flatpak list --app
```

**If branch 1 applies:**
- **Condition:** Screen share dialog or portal is missing
- Use the desktop-supported screen sharing dialog, update the affected app and portal from proper sources.
- Check the window-sharing option and consent prompt; do not grant blanket host display access.
- **Expected result:** Share shows only selected authorized area.

**Otherwise, branch 2:**
- **Condition:** Portal works in one app, not another
- Collect the affected app version and portal journal entries.
- Use the application’s supported Wayland screen-share method or report regression with redacted data.
- **Expected result:** App streams selected content on the same desktop session.

**Graphical alternative:** Use desktop sharing permission dialog and app screen-share UI.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
systemctl --user --failed
```

**Source references:** [1](https://flatpak.github.io/xdg-desktop-portal/docs/) · [2](https://docs.flatpak.org/en/latest/sandbox-permissions.html)

---

## 18. Black screen after suspend (`display.black-after-resume`)

**Symptom:** Display stays black after a resume attempt.

**Evidence supporting diagnosis:** Previous boot journal shows suspend/resume errors or DRM GPU-reset around wakeup.

**Evidence against this hypothesis:** Full power loss without resume logs suggests battery/power hardware.

**Read-only diagnostic commands:**

```bash
journalctl -b -1 -k --no-pager -n 150
cat /sys/power/state
lspci -k
```

**If branch 1 applies:**
- **Condition:** Regression began with a known new kernel
- Record working vs failing kernel and image version.
- Use distribution-supported previous deployment/kernel selection, without replacing base packages arbitrarily.
- **Expected result:** Computer resumes normally using the confirmed working system.

**Otherwise, branch 2:**
- **Condition:** External monitor or dock fails on wake
- Reconnect video path without force reboot when safe; compare direct connection and dock.
- Use vendor-supported dock firmware only if exact device/regression matches.
- **Expected result:** External display returns after ordinary suspend/wake.

**Graphical alternative:** Desktop power/display options; Bazzite use official boot deployment recovery.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
journalctl -b -1 -k --no-pager -n 150
```

**Source references:** [1](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html) · [2](https://docs.kernel.org/admin-guide/pm/sleep-states.html) · [3](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/updating_guide/)

---

## 19. System clock or time zone is wrong (`system.clock-offset`)

**Symptom:** Clock offset causes bad timestamps or TLS certificate warnings.

**Evidence supporting diagnosis:** timedatectl reports incorrect timezone or NTP unsynchronized.

**Evidence against this hypothesis:** Clock is correct but only one app times out: investigate app/TLS separately.

**Read-only diagnostic commands:**

```bash
timedatectl status
date -Is
systemctl status systemd-timesyncd.service --no-pager
```

**If branch 1 applies:**
- **Condition:** Time zone does not match user location
- Choose correct local time zone in desktop Date & Time.
- Review displayed date before accessing signed/time-dependent services.
- **User-executed command, only after verifying identifiers:** `timedatectl set-timezone REGION/CITY`
- **Expected result:** Local time and UTC offset are correct.

**Otherwise, branch 2:**
- **Condition:** Time sync disabled or NTP unreachable
- Check connected network and approved time-source policy.
- Enable supported system time synchronization through desktop Date & Time with authorization.
- **User-executed command, only after verifying identifiers:** `timedatectl set-ntp true`
- **Expected result:** timedatectl reports synchronized and clock stays correct.

**Graphical alternative:** Desktop Date & Time settings (system administrator authorization may be required).

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
timedatectl status
```

**Source references:** [1](https://www.freedesktop.org/software/systemd/man/latest/timedatectl.html)

---

## 20. An expected service is failing (`system.failed-service`)

**Symptom:** Named service does not start or repeatedly fails.

**Evidence supporting diagnosis:** systemctl --failed names the relevant service and journal contains a cause.

**Evidence against this hypothesis:** Optional service intentionally disabled is not a defect.

**Read-only diagnostic commands:**

```bash
systemctl --failed
systemctl status SERVICE.service --no-pager
journalctl -b -u SERVICE.service --no-pager -n 80
```

**If branch 1 applies:**
- **Condition:** Configuration or dependency reported missing
- Check only the exact unit’s dependencies and original package source.
- Restore supported setting or dependency through the distribution’s documented user/administrator procedure.
- **Expected result:** Unit becomes active or an intended on-demand state; dependent feature works.

**Otherwise, branch 2:**
- **Condition:** Service fails after package/image update
- Compare old and new release, identify known upstream bug and affected dependency.
- Apply documented supported update/rollback yourself, with work saved and recovery plan.
- **Expected result:** Service runs after same test and journal no longer records fresh failure.

**Graphical alternative:** Use service-specific desktop GUI or distro admin panel, if available. ULSM only if correcting an identified user-manageable app package.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
systemctl --failed
```

**Source references:** [1](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html) · [2](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

---

## 21. Hardware firmware is outdated or bugged (`system.firmware-update`)

**Symptom:** Device regression is known to require a verified vendor firmware fix.

**Evidence supporting diagnosis:** Exact device appears in fwupd inventory and manufacturer publishes matching fix.

**Evidence against this hypothesis:** fwupdmgr shows no supported update: do not force unrelated firmware.

**Read-only diagnostic commands:**

```bash
fwupdmgr get-devices
fwupdmgr get-updates
```

**If branch 1 applies:**
- **Condition:** Verified matching firmware release is published
- Connect stable power, back up important work and read vendor release notes.
- Initiate firmware update using trusted GUI after reviewing firmware compatibility and any reboot.
- **User-executed command, only after verifying identifiers:** `fwupdmgr update`
- **Expected result:** Device reports intended new firmware and original defect no longer occurs.

**Otherwise, branch 2:**
- **Condition:** Device not handled by fwupd
- Check manufacturer’s exact model/version support site.
- Use only vendor-approved platform update procedure or hardware support, not generic firmware flashes.
- **Expected result:** Vendor utility shows exact model firmware and issue resolved.

**Graphical alternative:** GNOME Firmware or supported vendor firmware UI; no ULSM firmware-update claim.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
fwupdmgr get-devices
```

**Source references:** [1](https://github.com/fwupd/fwupd/blob/main/src/fwupdmgr.md)

**Important:** get-updates may use cached or downloaded metadata; any update/network operation is user-initiated.

---

## 22. Application terminated by out-of-memory policy (`system.oom-killed`)

**Symptom:** Program disappears when memory pressure rises.

**Evidence supporting diagnosis:** Journal OOM lines mention the same service/process during reported event.

**Evidence against this hypothesis:** Coredump from another process is not proof of an OOM kill.

**Read-only diagnostic commands:**

```bash
free -h
journalctl -b -k --no-pager -n 120
systemctl --user --failed
```

**If branch 1 applies:**
- **Condition:** One app uses excessive memory
- Reduce that app’s workload (tabs/assets) and close duplicate instances.
- Use app-specific settings or supported update if regression confirmed; preserve files before restarting.
- **Expected result:** Same task completes without new OOM log and memory recovers.

**Otherwise, branch 2:**
- **Condition:** Host consistently exceeds installed memory
- Close unnecessary workloads or increase physical RAM/swap through a planned supported user-managed procedure.
- Do not delete kernel swap files or change system memory configuration blindly.
- **Expected result:** Representative workload runs without OOM events.

**Graphical alternative:** Desktop System Monitor and workload-specific settings.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
free -h
journalctl -b -k --no-pager -n 120
```

**Source references:** [1](https://www.freedesktop.org/software/systemd/man/latest/systemd-oomd.service.html) · [2](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

---

## 23. Flatpak application cannot open selected files (`apps.flatpak-file-access`)

**Symptom:** App cannot see file or directory available in normal file manager.

**Evidence supporting diagnosis:** App ID and current permissions show sandbox; file chooser/portal or export path may be missing.

**Evidence against this hypothesis:** Native install of same app also fails: not necessarily sandbox-related.

**Read-only diagnostic commands:**

```bash
flatpak list --app
flatpak info --show-permissions APP_ID
flatpak ps
```

**If branch 1 applies:**
- **Condition:** App uses a portal file picker and needs one file
- Open file with the app’s file picker; select only intended document via portal.
- Avoid granting home or host filesystem broadly.
- **Expected result:** Selected file opens without exposing unrelated folders.

**Otherwise, branch 2:**
- **Condition:** App needs persistent, documented folder access
- Identify exact directory and affected Flatpak ID first.
- Grant narrowly scoped access using desktop Flatpak permission GUI, not global --filesystem=host.
- **Expected result:** App can work on intended folder; other folders remain inaccessible.

**Graphical alternative:** Desktop Flatpak permission controls; ULSM is for package operations, not changing sandbox overrides.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
flatpak info --show-permissions APP_ID
```

**Source references:** [1](https://docs.flatpak.org/en/latest/sandbox-permissions.html) · [2](https://flatpak.github.io/xdg-desktop-portal/docs/)

---

## 24. Application crashes after update (`apps.update-caused-crash`)

**Symptom:** One previously working application fails immediately after its latest update.

**Evidence supporting diagnosis:** Installed application version and crash journal time correlate with update history.

**Evidence against this hypothesis:** Kernel errors at same time might indicate GPU driver problem instead of app regression.

**Read-only diagnostic commands:**

```bash
flatpak history
flatpak list --app
coredumpctl --no-pager list
```

**If branch 1 applies:**
- **Condition:** A newer fixed release is available from same source
- Check official app release notes and installed package source.
- Update only that app through ULSM corresponding tab or exact native manager, not an unrelated source.
- **Expected result:** Previously failing workflow works with fixed version.

**Otherwise, branch 2:**
- **Condition:** Current release still fails, prior release was known stable
- Use official release-specific downgrade/rollback instructions supported by the installed source.
- Report crash trace and versions to developer; avoid mixing Github/Flathub installs or forcing third-party packages.
- **Expected result:** Workflow works on supported release and no new crash appears.

**Graphical alternative:** Universal Linux Software Manager → matching source tab / Updates for supported application packages.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
flatpak history
coredumpctl --no-pager list
```

**Source references:** [1](https://docs.flatpak.org/en/latest/sandbox-permissions.html) · [2](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

---

## 25. Service cannot bind to its port (`apps.port-in-use`)

**Symptom:** Application reports address already in use when starting local server.

**Evidence supporting diagnosis:** ss -tuln shows port already used by known service.

**Evidence against this hypothesis:** No listener means check firewall, permissions or application configuration.

**Read-only diagnostic commands:**

```bash
ss -tuln
systemctl --failed
```

**If branch 1 applies:**
- **Condition:** Unexpected duplicate instance owns the same socket
- Identify process using system service manager or authorized app process view.
- Close only the duplicate service after saving work; start intended instance.
- **Expected result:** Desired service listens and duplicate no longer conflicts.

**Otherwise, branch 2:**
- **Condition:** Both services require distinct network sockets
- Assign an approved free port to exactly one service in its supported config.
- Update clients to intended port; do not disable firewall by default.
- **Expected result:** Both services start and expected local clients connect.

**Graphical alternative:** Desktop system monitor/service app. Avoid blanket kill -9.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
ss -tuln
```

**Source references:** [1](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html)

---

## 26. VPN connected but internal names fail (`network.vpn-split-dns`)

**Symptom:** Tunnel active but protected company hostnames do not resolve.

**Evidence supporting diagnosis:** Active VPN route present; resolvectl shows wrong DNS domain routing.

**Evidence against this hypothesis:** VPN endpoint unreachable: this is connection failure, not split-DNS.

**Read-only diagnostic commands:**

```bash
nmcli connection show --active
resolvectl status
ip route
```

**If branch 1 applies:**
- **Condition:** Incorrect search domains for VPN
- Compare protected DNS domain routing with VPN admin configuration.
- Correct only the approved connection DNS routing in desktop network profile.
- **Expected result:** Authorized internal name resolves through intended VPN DNS.

**Otherwise, branch 2:**
- **Condition:** Protected hostname resolves but wrong route used
- Compare VPN split routes with organization policy.
- Request corrected VPN profile from administrator; never bypass tunnel for protected internal addresses.
- **Expected result:** Authorized resource connects through intended protected path.

**Graphical alternative:** Desktop VPN settings using administrator-provided values.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
resolvectl status
ip route
```

**Source references:** [1](https://networkmanager.dev/docs/api/latest/nmcli.html)

---

## 27. Wi-Fi chipset firmware fails to load (`network.wifi-no-firmware`)

**Symptom:** Wi-Fi adapter visible but driver requests missing firmware.

**Evidence supporting diagnosis:** lspci/lsusb identifies chip and kernel logs name an absent firmware blob.

**Evidence against this hypothesis:** Wi-Fi radio soft-blocked or wrong password is not missing firmware.

**Read-only diagnostic commands:**

```bash
lspci -k
lsusb
journalctl -b -k --no-pager -n 150
```

**If branch 1 applies:**
- **Condition:** Official distro firmware package exists for this chipset
- Identify exact device and distribution firmware package name from official source.
- Have user update/install only matching firmware using distro-supported tool; reboot if documented.
- **Expected result:** Driver loads firmware and network interfaces show adapter.

**Otherwise, branch 2:**
- **Condition:** Device unsupported on current kernel/image
- Use manufacturer/distro supported kernel or firmware release from an official stable channel.
- For Bazzite use image update/rollback guide rather than random host DNF package install.
- **Expected result:** Adapter appears without firmware-load error.

**Graphical alternative:** Use supported Bazzite Updater or distro Software Center for matching firmware; ULSM only if native package is safely supported.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
lspci -k
nmcli device status
```

**Source references:** [1](https://docs.kernel.org/gpu/index.html) · [2](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/updating_guide/) · [3](https://docs.bazzite.gg/Installing_and_Managing_Software/rpm-ostree/)

---

## 28. Libvirt default network is inactive (`virtualization.libvirt-default-off`)

**Symptom:** Virtual machine receives no address from its configured default NAT network.

**Evidence supporting diagnosis:** virsh net-list --all shows default network inactive AND affected guest attached to default.

**Evidence against this hypothesis:** Custom bridge/other backend does not use the default network.

**Read-only diagnostic commands:**

```bash
virsh net-list --all
virsh net-info default
virsh domiflist VM_NAME
```

**If branch 1 applies:**
- **Condition:** VM explicitly configured for default NAT network and it is inactive
- Start only the named virtual network after confirming it belongs to this VM.
- Retry DHCP from within guest using its network controls.
- **User-executed command, only after verifying identifiers:** `virsh net-start default`
- **Expected result:** Guest receives address and reaches intended destination.

**Otherwise, branch 2:**
- **Condition:** VM uses different virtual bridge
- Inspect guest definition to identify intended interface and bridge.
- Repair that network’s physical bridge or connection with administrator approval.
- **Expected result:** Guest reaches intended network while host firewall remains intact.

**Graphical alternative:** virt-manager → Connection Details → Virtual Networks; start only verified network.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
virsh net-list --all
virsh domiflist VM_NAME
```

**Source references:** [1](https://www.libvirt.org/manpages/virsh.html)

---

## 29. Rootless container fails to run (`virtualization.podman-rootless-error`)

**Symptom:** Podman fails for one user but rootful containers may work.

**Evidence supporting diagnosis:** podman info reports rootless environment limitations or relevant user namespace/storage error.

**Evidence against this hypothesis:** Image missing from registry is not a rootless namespace issue.

**Read-only diagnostic commands:**

```bash
podman info
podman ps -a
journalctl --user -b --no-pager -n 90
```

**If branch 1 applies:**
- **Condition:** User namespaces unavailable or restricted
- Confirm host distro supports rootless user namespaces and user mapping.
- Use documented distro-supported rootless setup rather than privileged/rootful workaround.
- **Expected result:** Rootless container starts with original user and isolation retained.

**Otherwise, branch 2:**
- **Condition:** Container storage is full or corrupted
- Back up needed container volumes and confirm storage location.
- Free only user-approved unused images/volumes using Podman supported UI/commands after inventory review.
- **Expected result:** Container starts; persistent volume data remains intact.

**Graphical alternative:** Use supported Podman Desktop/container manager where available; ULSM does not manage Podman volumes.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
podman ps -a
```

**Source references:** [1](https://docs.podman.io/en/stable/markdown/podman.1.html)

---

## 30. Proton game refuses to launch (`gaming.proton-game-no-start`)

**Symptom:** One Windows game starts then exits without a visible window.

**Evidence supporting diagnosis:** Game launch logs show runtime error, Proton incompatibility or GPU driver failure.

**Evidence against this hypothesis:** Native games fail similarly: investigate GPU/hardware before Proton tuning.

**Read-only diagnostic commands:**

```bash
lspci -k
journalctl -b -p warning --no-pager -n 150
flatpak ps
```

**If branch 1 applies:**
- **Condition:** Game regression after Proton selection
- Use Steam → Game Properties → Compatibility to choose a supported current Proton version.
- Retry game while preserving saves; avoid arbitrary launch flags.
- **Expected result:** Game launches and can load existing save.

**Otherwise, branch 2:**
- **Condition:** GPU reset/driver failure present
- Compare GPU resets with game start in previous boot journal.
- Use distribution-supported graphics/kernel update or earlier known stable deployment after saving work.
- **Expected result:** Game runs normally and no new GPU reset occurs.

**Graphical alternative:** Steam → Properties → Compatibility, game-specific supported troubleshoot notes.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
journalctl -b -k --no-pager -n 120
```

**Source references:** [1](https://docs.kernel.org/gpu/index.html) · [2](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/updating_guide/)

---

## 31. Kernel module fails under Secure Boot (`system.secureboot-module`)

**Symptom:** Device driver cannot load when signature enforcement active.

**Evidence supporting diagnosis:** Kernel journal reports module verification or key rejection and secure boot is enabled.

**Evidence against this hypothesis:** Device missing entirely from hardware bus is not signature failure.

**Read-only diagnostic commands:**

```bash
mokutil --sb-state
lspci -k
journalctl -b -k --no-pager -n 120
```

**If branch 1 applies:**
- **Condition:** Vendor-supported signed driver available
- Install/update only trusted signed module from verified distro support channel.
- Follow supported firmware/module key enrollment with explicit user presence; no global Secure Boot disabling.
- **Expected result:** Expected signed module loads and device functions.

**Otherwise, branch 2:**
- **Condition:** Device requires unsupported third-party module
- Choose a properly signed supported driver/kernel or compatible hardware.
- Report device ID to vendor; do not bypass security protections to make a doubtful driver load.
- **Expected result:** Supported signed module operates without key rejection.

**Graphical alternative:** UEFI firmware settings and official vendor documented signing enrollment; no blanket disable-Secure-Boot advice.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
mokutil --sb-state
lspci -k
```

**Source references:** [1](https://docs.kernel.org/gpu/index.html) · [2](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/updating_guide/)

---

## 32. Shutdown takes too long (`system.shutdown-hangs`)

**Symptom:** Computer waits on one service or mounted resource when powering down.

**Evidence supporting diagnosis:** Previous boot logs identify timeout or stop-job for named unit.

**Evidence against this hypothesis:** Hard power loss is not a graceful shutdown timeout.

**Read-only diagnostic commands:**

```bash
journalctl -b -1 -p warning --no-pager -n 150
systemctl --failed
systemd-analyze blame
```

**If branch 1 applies:**
- **Condition:** Specific optional service repeatedly times out
- Inspect its unit journal and upstream supported stop behavior.
- Update/configure only that identified optional app; do not globally slash systemd timeouts.
- **Expected result:** Clean shutdown completes within expected time.

**Otherwise, branch 2:**
- **Condition:** Remote mount or removable drive holds shutdown
- Identify mounted remote filesystem and active processes.
- Safely close relevant apps/disconnect mount using desktop GUI before shutdown; correct mount policy with admin if needed.
- **Expected result:** Shutdown completes without affected mount timeout.

**Graphical alternative:** Desktop session logout, mounted drive options or service-specific UI.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
journalctl -b -1 -p warning --no-pager -n 150
```

**Source references:** [1](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html) · [2](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

---

## 33. External dock overheats and disconnects (`hardware.peripheral-thermal`)

**Symptom:** Dock/hub loses devices under high load.

**Evidence supporting diagnosis:** USB reset messages coincide with multiple devices dropping and hub power state changes.

**Evidence against this hypothesis:** Only one individual device fails on every port: investigate that device alone.

**Read-only diagnostic commands:**

```bash
lsusb
journalctl -b -k --no-pager -n 120
```

**If branch 1 applies:**
- **Condition:** Bus-powered hub overloaded
- Disconnect nonessential devices safely and test powered hub rated for load.
- Follow manufacturer dock power/thermal limits.
- **Expected result:** Devices remain detected through representative load.

**Otherwise, branch 2:**
- **Condition:** Dock works at idle, disconnects only at heat
- Allow device to cool and place according to vendor air flow requirements.
- Use manufacturer-supported replacement/firmware remedy only when known for exact dock.
- **Expected result:** Dock stable during safe normal use.

**Graphical alternative:** Desktop Disks/Device manager to identify devices; vendor dock utility as appropriate.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
lsusb
```

**Source references:** [1](https://www.kernel.org/doc/html/latest/usb/index.html)

---

## 34. Laptop suspends unexpectedly on lid or dock (`system.laptop-lid-suspend`)

**Symptom:** System suspends when external monitor/dock is in use.

**Evidence supporting diagnosis:** logind messages coincide with lid close or sleep target; desktop power policy identifies selected action.

**Evidence against this hypothesis:** Kernel crash unrelated to lid-close input is separate.

**Read-only diagnostic commands:**

```bash
loginctl show-session "$XDG_SESSION_ID"
journalctl -b -u systemd-logind --no-pager -n 80
systemctl status sleep.target --no-pager
```

**If branch 1 applies:**
- **Condition:** Desktop lid-close power policy undesired
- Open desktop Power Management and set lid action to intended supported choice.
- Retest with external monitor and safe ventilation.
- **Expected result:** Lid events follow chosen policy.

**Otherwise, branch 2:**
- **Condition:** Dock falsely triggers suspend when unplugging
- Compare dock cable attach/detach and logind events.
- Test direct display and vendor firmware/config after validating exact dock issue.
- **Expected result:** No unintended suspends after dock event.

**Graphical alternative:** KDE Power Management or GNOME power settings where provided; do not globally disable all suspend safety.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
journalctl -b -u systemd-logind --no-pager -n 80
```

**Source references:** [1](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html) · [2](https://docs.kernel.org/admin-guide/pm/sleep-states.html)

---

## 35. SELinux blocks an application action (`security.selinux-denial`)

**Symptom:** Application access fails and AVC denial occurs at same time.

**Evidence supporting diagnosis:** journal or audit report links AVC to exact domain/path/operation.

**Evidence against this hypothesis:** No AVC evidence means do not blame SELinux by default.

**Read-only diagnostic commands:**

```bash
getenforce
journalctl -b --no-pager -n 150
```

**If branch 1 applies:**
- **Condition:** App is trying to use a path not intended by its documented sandbox
- Correct app’s configuration/location to supported path and context through upstream documentation.
- Keep SELinux enforcing; do not use permissive mode as universal fix.
- **Expected result:** App feature works with SELinux still enforcing.

**Otherwise, branch 2:**
- **Condition:** Legitimate behavior denied due to policy bug
- Record minimal anonymized AVC evidence and version.
- Install trusted updated policy/package when official fix exists or report minimal reproducer to maintainer.
- **Expected result:** Requested action works under the intended security policy.

**Graphical alternative:** Use vendor/distro SELinux troubleshooting GUI when installed; not ULSM generic permission removal.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
getenforce
```

**Source references:** [1](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

---

## 36. Laptop battery is not charging (`hardware.battery-not-charging`)

**Symptom:** Battery remains at low state while external power is attached.

**Evidence supporting diagnosis:** UPower shows battery state and AC/charger detection.

**Evidence against this hypothesis:** Charging limit near maximum can be intended firmware battery care.

**Read-only diagnostic commands:**

```bash
upower -e
upower -d
journalctl -b -k --no-pager -n 80
```

**If branch 1 applies:**
- **Condition:** Charge threshold set intentionally
- Inspect firmware/desktop battery care limit and adapter identification.
- Adjust documented charge limit only if user needs a different threshold.
- **Expected result:** Battery charges according to new user-selected threshold.

**Otherwise, branch 2:**
- **Condition:** AC not recognized or battery reports hardware fault
- Test supported manufacturer charger and connector safely; stop if heat/damage.
- Replace defective charger/battery via qualified vendor route; do not bypass battery safety.
- **Expected result:** Battery charges safely on supported hardware.

**Graphical alternative:** Desktop Power settings or official vendor power/battery settings.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
upower -d
```

**Source references:** [1](https://docs.kernel.org/admin-guide/pm/sleep-states.html)

---

## 37. Ethernet cable connected but no network (`network.wired-link-no-carrier`)

**Symptom:** Wired connection lacks link/carrier.

**Evidence supporting diagnosis:** NetworkManager reports disconnected and link is down after cable is inserted.

**Evidence against this hypothesis:** Carrier up but no IP: inspect DHCP/route rather than cable.

**Read-only diagnostic commands:**

```bash
nmcli device status
ip -brief address
journalctl -b -u NetworkManager --no-pager -n 90
```

**If branch 1 applies:**
- **Condition:** Link physically down
- Test known-good Ethernet cable and another switch/router port.
- Verify supported dock or NIC interface and speed negotiation in official driver guide.
- **Expected result:** Link carrier appears; intended IP acquired.

**Otherwise, branch 2:**
- **Condition:** Link up, but DHCP fails
- Check router DHCP service or intended static IP profile with network admin.
- Correct only the matching connection profile using NetworkManager GUI.
- **Expected result:** Valid IP, gateway and authorized destination work.

**Graphical alternative:** Desktop Network → Wired connections, matching adapter only.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
nmcli device status
ip route
```

**Source references:** [1](https://networkmanager.dev/docs/api/latest/nmcli.html)

---

## 38. Cannot open or save a file because of permissions (`storage.file-permission-denied`)

**Symptom:** User cannot write file in intended home/application folder.

**Evidence supporting diagnosis:** namei and stat report owner/rights/ACL mismatch or FS read-only flag.

**Evidence against this hypothesis:** Full filesystem is separate problem; do not chmod everything.

**Read-only diagnostic commands:**

```bash
ls -ld "$HOME"
findmnt -no TARGET,OPTIONS "$HOME"
id
```

**If branch 1 applies:**
- **Condition:** File belongs to another user or root
- Inspect exact file/folder owner and understand why it was created.
- Use file manager approved ownership correction for only the affected user-owned file, or application-specific recovery; avoid recursive chown.
- **Expected result:** Affected user can create/save file without new errors.

**Otherwise, branch 2:**
- **Condition:** Filesystem mounted read-only because of I/O failures
- Stop writes, back up readable data and investigate disk/filesystem state first.
- Use supported filesystem/device repair or replacement under user supervision.
- **Expected result:** File operations work on healthy writable filesystem.

**Graphical alternative:** Desktop file manager → file Properties/Permissions for precisely selected non-system item.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
id
findmnt -no TARGET,OPTIONS "$HOME"
```

**Source references:** [1](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

---

## 39. Package update fails signature verification (`system.upgrade-signature-error`)

**Symptom:** Software update reports invalid signing key or metadata checksum.

**Evidence supporting diagnosis:** Original distro manager identifies exact repository/signature error.

**Evidence against this hypothesis:** General download timeout is a connectivity issue instead.

**Read-only diagnostic commands:**

```bash
cat /etc/os-release
rpm-ostree status
flatpak remotes --show-details
```

**If branch 1 applies:**
- **Condition:** Trusted official remote metadata out of date
- Identify the original trusted repository and verify official updated signing details.
- Use distribution-supported refresh/updater rather than disable GPG verification.
- **Expected result:** Updater verifies signatures and selected update completes.

**Otherwise, branch 2:**
- **Condition:** Third-party repository has revoked or mismatched keys
- Stop using the affected repository until its owner publishes a verifiable correction.
- Remove/disable only that optional broken repository through its supported GUI, preserving installed packages until reviewed.
- **Expected result:** Official trusted repositories update normally without relaxed signature checks.

**Graphical alternative:** Bazzite Updater or ULSM matching source tab; avoid mixing source/channel.

**Guided terminal alternative:** Use ULT’s installed-command discovery, inspect available `--help`/manual metadata, prepare the same command, and choose **Insert into terminal**. This does not run it; the user reviews every flag and presses Enter. Not every command is in ULT’s fixed catalog; some depend on host tools.

**Retest commands:**

```bash
flatpak remotes --show-details
rpm-ostree status
```

**Source references:** [1](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/updating_guide/) · [2](https://docs.bazzite.gg/Installing_and_Managing_Software/rpm-ostree/) · [3](https://docs.flatpak.org/en/latest/sandbox-permissions.html)

---


---

## PART II — Expanded hardware-only diagnoses

# Universal Linux Troubleshooter — Hardware Diagnostic Handbook 34

**Documentation scope:** hardware and hardware-facing peripherals ONLY. Previous 96 documented scenario families remain; this file adds narrowly discriminated hardware cases rather than claiming the entire Linux universe is solved. OS/application diagnosis expansion is intentionally deferred.

## Critical operating rules

- Troubleshooter may observe only specifically approved, local, read-only diagnostics. Listing a command here **does not** authorize the application or AI to run it; new runtime handlers must be reviewed later.
- **All repair steps are performed by the user** (including firmware updates, physical changes, part replacement, package changes, settings changes and service restarts). The three user-selected presentation routes are ordinary terminal, Universal Linux Terminal, or an appropriate vendor/desktop GUI. ULSM is applicable only to software/package administration, never firmware flashing or physical repairs.
- Inspect the actual device, driver, distro, model and version before using commands. `/dev/sdX`, `/dev/nvme0`, `ENP_INTERFACE` are **placeholders** requiring confirmation. `sudo` for health queries still asks permission. Missing sensors/logs/optional tools are **unknown**, not a healthy result. Previous boot journal may be absent.
- Read-only hardware health commands may require device privileges and carry privacy implications. No internet or automatic uploads. External firmware metadata requests require separate user consent.
- Hardware failures cannot always be fixed in software. A specific confirmed replacement, supported workaround or vendor fix is a concrete resolution route; do not invent a guaranteed software command.
- During possible storage failure, **back up before invasive testing**. During suspected overheating, stop unsafe workloads rather than forcing reproduction. No unsupervised firmware flashing, stress-testing, destructive filesystems checks, data erasure or controller resets.

## Cross-application options

- [Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal): teaches discovered host commands and puts selected text at the prompt, **not automatically executed**.
- [Universal Linux Software Manager](https://github.com/LionheartTim/Universal-Linux-Software-Manager): use ONLY if the required action is a supported package operation. It cannot repair hardware directly.
- Vendor or desktop settings are used for firmware, monitor, keyboard, battery and physical hardware cases.

## Contents

- **Audio**: 2 cases
- **Board**: 8 cases
- **Cooling**: 4 cases
- **Cpu**: 5 cases
- **Display**: 4 cases
- **Gpu**: 6 cases
- **Memory**: 5 cases
- **Other**: 5 cases
- **Peripherals**: 15 cases
- **Power**: 6 cases
- **Storage**: 10 cases


# Audio

## Headset microphone jack is not detected (`hardware34.audio.mic-jack-detection`)

**Area:** audio  

**Symptom:** Analog headset playback works but microphone is missing.

**Supporting evidence:** ALSA codec/card exposes differing input jacks or headset standard mismatch.

**Counterevidence:** Microphone privacy permission can independently hide a working mic from one app.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

arecord -l

aplay -l

wpctl status

```

**Resolution route 1 — use only when:** Wrong physical headset wiring or jack

1. Confirm TRRS standard and combined headset jack support

2. Use compatible splitter/USB sound interface if hardware cannot accept microphone

**Resolution route 2 — use only when:** Codec input available but default source wrong

1. Choose physical headset microphone in desktop Sound settings

2. Compare ordinary mic meter without recording private content

**GUI option:** Desktop Input Settings and hardware jack/splitter diagram.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

arecord -l

wpctl status

```

**Safety:** Do not automatically capture audio or upload recordings.

**Sources:** [alsa](https://www.alsa-project.org/alsa-doc/alsa-lib/)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Speakers distort only at certain levels (`hardware34.audio.speaker-distortion`)

**Area:** audio  

**Symptom:** Crackling occurs with a specific output device or cable.

**Supporting evidence:** Distortion tracks analog cable/speaker volume and not digital playback elsewhere.

**Counterevidence:** Same artifact on every device may reflect PipeWire or application underruns.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

aplay -l

wpctl status

journalctl -b --no-pager -n 110

```

**Resolution route 1 — use only when:** Analog speaker/cable issue

1. Lower playback volume to safe level and inspect damaged cable/cone

2. Replace defective speakers/cable or use supported audio port

**Resolution route 2 — use only when:** Issue affects only one audio routing mode

1. Set supported output/profile through desktop GUI

2. Use official device/codec update or bug route if reproduced only in software

**GUI option:** Desktop Sound output profile and physical speaker diagnostics.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

wpctl status

```

**Safety:** Avoid loud sound tests that could damage hearing/speakers.

**Sources:** [alsa](https://www.alsa-project.org/alsa-doc/alsa-lib/)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---


# Board

## PCIe corrected error messages (`hardware34.board.pcie-correctable`)

**Area:** board  

**Symptom:** Kernel reports repeated PCIe AER correctable messages.

**Supporting evidence:** New AER corrected events identify device or upstream port and correlate with device malfunction.

**Counterevidence:** A corrected error with no symptom does not establish failing motherboard.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

journalctl -b -k --no-pager -n 240

lspci -nnk

lspci -tv

```

**Resolution route 1 — use only when:** One peripheral and cable/slot implicated

1. Record exact device and event times

2. Shut down, check approved seating/riser/power cabling, and compare without that optional device if safe

**Resolution route 2 — use only when:** AER persists across known-good device

1. Use vendor-specific board/BIOS diagnostic and service path

2. Escalate board or controller replacement if repeated faults are corroborated

**GUI option:** UEFI diagnostics and vendor service instructions.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

journalctl -b -k --no-pager -n 240

```

**Safety:** Never disable PCIe AER globally just to hide a fault.

**Sources:** [pci](https://docs.kernel.org/PCI/pcieaer-howto.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## PCIe uncorrectable/fatal event (`hardware34.board.pcie-fatal`)

**Area:** board  

**Symptom:** A PCIe device disappears following fatal bus error.

**Supporting evidence:** AER severity uncorrectable or DPC event precedes loss of the exact device.

**Counterevidence:** Other buses or unrelated logs cannot identify this device failure.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

journalctl -b -k --no-pager -n 250

lspci -nnk

lspci -tv

```

**Resolution route 1 — use only when:** Device or riser physically suspect

1. Save important data; power down before touching hardware

2. Inspect vendor-approved riser/connector and PCIe auxiliary power, seek professional replacement if needed

**Resolution route 2 — use only when:** Fault tied to board firmware/compatibility

1. Confirm device+board model and firmware versions

2. Apply a specific vendor-reviewed fix manually or use tested compatible component

**GUI option:** Board vendor diagnostics; prioritize data protection if storage adapter is involved.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

journalctl -b -k --no-pager -n 200

lspci -nnk

```

**Safety:** Do not force PCIe link speed, kernel AER off switches, or GPU overclock.

**Sources:** [pci](https://docs.kernel.org/PCI/pcieaer-howto.html) · [fwupd](https://github.com/fwupd/fwupd/blob/main/src/fwupdmgr.md)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Firmware time or settings reset (`hardware34.board.bios-cmos-clock`)

**Area:** board  

**Symptom:** BIOS clock resets or settings disappear after power loss.

**Supporting evidence:** Settings repeatedly reset after total power disconnect; RTC battery or firmware issue is plausible.

**Counterevidence:** An OS timezone mismatch alone does not imply bad CMOS battery.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

sudo dmidecode -t bios

timedatectl

date

```

**Resolution route 1 — use only when:** RTC resets with complete power removal

1. Check mainboard model and CMOS service instructions

2. Replace RTC battery only per manufacturer safety procedure and retest power-off retention

**Resolution route 2 — use only when:** Clock issue exists only inside OS

1. Check time zone and NTP status with supported desktop settings

2. Leave motherboard hardware untouched unless RTC also loses state

**GUI option:** Firmware clock page and vendor RTC battery replacement instructions.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

date

timedatectl

```

**Safety:** Laptop RTC batteries may be internal and service-only; never suggest shorting CMOS contacts.

**Sources:** [fwupd](https://github.com/fwupd/fwupd/blob/main/src/fwupdmgr.md)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Device lacks working hardware firmware (`hardware34.board.firmware-device-missing`)

**Area:** board  

**Symptom:** Device enumerates but reports firmware load failures.

**Supporting evidence:** Kernel reports specific missing firmware filename for a confirmed device ID.

**Counterevidence:** Device absence on bus indicates physical enumeration issue, not missing firmware.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

lspci -nnk

lsusb

journalctl -b -k --no-pager -n 220

```

**Resolution route 1 — use only when:** Exact compatible firmware missing

1. Record device PCI/USB ID and exact firmware name

2. Have the user follow distro/vendor-supported firmware package instructions, without downloading random blobs

**Resolution route 2 — use only when:** Firmware is present but device still fails

1. Check driver, hardware fault and matching vendor bug report

2. Use official supported firmware update or vendor device replacement if defect confirmed

**GUI option:** Use vendor firmware manager or supported distro package UI as appropriate.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

journalctl -b -k --no-pager -n 220

lspci -nnk

```

**Safety:** A driver firmware blob is distinct from UEFI flashing. Never download untrusted firmware.

**Sources:** [fwupd](https://github.com/fwupd/fwupd/blob/main/src/fwupdmgr.md) · [journal](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Firmware update fails or device update unavailable (`hardware34.board.bios-update-failed`)

**Area:** board  

**Symptom:** fwupd or vendor firmware tool cannot apply a device update.

**Supporting evidence:** Exact model/GUID and update error are captured from fwupd; device may not be supported.

**Counterevidence:** No updates offered may mean current version or lack of LVFS coverage, not a fault.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

fwupdmgr get-devices

fwupdmgr get-history

sudo dmidecode -t bios

```

**Resolution route 1 — use only when:** Firmware update not supported by LVFS

1. Use the verified manufacturer firmware download and documented platform flashing procedure

2. Do not attempt unsupported cross-model image or assume every device is LVFS managed

**Resolution route 2 — use only when:** Update failed for a matching supported device

1. Review power/battery preconditions and device-specific failure reason

2. Ask manufacturer for supported recovery process before any retry

**GUI option:** Firmware GUI only after user explicitly opts for a firmware update; never auto-flash.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

fwupdmgr get-devices

fwupdmgr get-history

```

**Safety:** Do not run fwupdmgr refresh/update automatically; refresh may network and update changes firmware.

**Sources:** [fwupd](https://github.com/fwupd/fwupd/blob/main/src/fwupdmgr.md)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## TPM device missing or unresponsive (`hardware34.board.tpm-unavailable`)

**Area:** board  

**Symptom:** Firmware-backed TPM not visible to software.

**Supporting evidence:** Exact platform TPM device absent or fails kernel initialization.

**Counterevidence:** Not every motherboard contains a TPM or exposes it under Linux.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

ls /sys/class/tpm

journalctl -b -k --no-pager -n 160

sudo dmidecode -t baseboard

```

**Resolution route 1 — use only when:** TPM feature is disabled in firmware

1. Verify the board supports TPM/fTPM

2. Let the user enable only the vendor-documented feature if genuinely needed, noting disk-encryption implications

**Resolution route 2 — use only when:** TPM fails to initialize with firmware enabled

1. Check firmware release notes and hardware compatibility

2. Use vendor maintenance/support, preserving encryption recovery keys beforehand

**GUI option:** UEFI security settings and platform vendor documentation.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

ls /sys/class/tpm

```

**Safety:** Never tell users to clear TPM or security keys automatically; data loss risk.

**Sources:** [fwupd](https://github.com/fwupd/fwupd/blob/main/src/fwupdmgr.md) · [journal](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Hardware timer or RTC errors (`hardware34.board.clock-source-reset`)

**Area:** board  

**Symptom:** Kernel reports clocksource/RTC faults or unstable hardware timekeeping.

**Supporting evidence:** Repeatable RTC/clocksource warnings with matching resets or time drift.

**Counterevidence:** Ordinary NTP adjustment is not proof of clock hardware failure.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

journalctl -b -k --no-pager -n 200

timedatectl

cat /sys/devices/system/clocksource/clocksource0/current_clocksource

```

**Resolution route 1 — use only when:** RTC loses time when powered down

1. Inspect supported RTC battery and motherboard hardware condition

2. Follow platform approved service for battery or board replacement

**Resolution route 2 — use only when:** Clock warnings follow firmware regression

1. Identify exact model and version

2. Use only manufacturer-approved firmware rollback/update instructions if supported

**GUI option:** Vendor firmware diagnostic page and approved time configuration controls.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

journalctl -b -k --no-pager -n 160

timedatectl

```

**Safety:** Do not change clocksource kernel parameters speculatively.

**Sources:** [fwupd](https://github.com/fwupd/fwupd/blob/main/src/fwupdmgr.md) · [journal](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Motherboard hardware-monitor chip absent (`hardware34.board.sensor-controller`)

**Area:** board  

**Symptom:** Expected fan/temperature channels disappear from Linux readings.

**Supporting evidence:** Previously supported hwmon controller is no longer enumerated or driver logs indicate sensor failure.

**Counterevidence:** Motherboard may not expose every sensor to Linux, especially with vendor-only interfaces.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

sensors

ls /sys/class/hwmon

sudo dmidecode -t baseboard

```

**Resolution route 1 — use only when:** Linux cannot map a proprietary sensor

1. Cross-check vendor UEFI hardware monitor and documented interface

2. Use supported monitoring path or record unsupported telemetry, not a made-up zero RPM

**Resolution route 2 — use only when:** UEFI also fails to read required sensor

1. Use board vendor diagnostics and approved firmware path

2. Arrange motherboard sensor/controller service or replacement if confirmed

**GUI option:** UEFI Board Monitor and motherboard service information.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

sensors

```

**Safety:** Never probe undocumented I/O registers or write to hwmon outputs.

**Sources:** [sensors](https://docs.kernel.org/hwmon/sysfs-interface.html) · [fwupd](https://github.com/fwupd/fwupd/blob/main/src/fwupdmgr.md)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---


# Cooling

## AIO water pump may be stopped (`hardware34.cooling.pump-rpm`)

**Area:** cooling  

**Symptom:** AIO pump reads zero RPM or CPU temperature rises suddenly.

**Supporting evidence:** Confirmed pump tachometer remains zero when it should be active and CPU temperature rises.

**Counterevidence:** Pump RPM telemetry may not be exposed via motherboard, and a missing sensor is not proof of failure.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

sensors

ls /sys/class/hwmon

journalctl -b -k --no-pager -n 120

```

**Resolution route 1 — use only when:** Cooling loop not functioning

1. Stop heavy workloads and power down if thermal shutdown occurs

2. Check approved SATA/USB/pump header connections and pump controller

3. Seek vendor warranty replacement for failed pump

**Resolution route 2 — use only when:** Only monitoring data is missing

1. Identify which tachometer input actually represents pump

2. Use firmware hardware-monitor page and vendor utility for supported telemetry before judging failure

**GUI option:** UEFI pump header monitoring and AIO manufacturer installation guide.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

sensors

```

**Safety:** Do not ask users to disconnect a powered liquid cooler or run stress tests without cooling.

**Sources:** [sensors](https://docs.kernel.org/hwmon/sysfs-interface.html) · [power](https://docs.kernel.org/power/power_supply_class.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Case or CPU fan not spinning (`hardware34.cooling.fan-rpm-zero`)

**Area:** cooling  

**Symptom:** Fan speed reports zero or airflow is absent.

**Supporting evidence:** Tachometer for mapped CPU/case header shows zero under real demand with rising temperature.

**Counterevidence:** Fan-stop control and mislabeled headers can report zero harmlessly.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

sensors

ls /sys/class/hwmon

journalctl -b -k --no-pager -n 100

```

**Resolution route 1 — use only when:** Cable or fan motor problem

1. Power off and check fan header and mechanical obstruction

2. Replace fan or arrange qualified repair if not spinning under expected demand

**Resolution route 2 — use only when:** Fan-stop policy or wrong sensor channel

1. Map motherboard header to real fan

2. Review vendor-supported fan curve through firmware and retest normal load

**GUI option:** UEFI hardware monitor and chassis vendor wiring guide.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

sensors

```

**Safety:** Avoid arbitrary pwm sysfs writes or overriding CPU fan warnings.

**Sources:** [sensors](https://docs.kernel.org/hwmon/sysfs-interface.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Thermal sensor reports implausible values (`hardware34.cooling.sensor-disconnect`)

**Area:** cooling  

**Symptom:** Monitoring tools show frozen, missing, or impossible temperatures.

**Supporting evidence:** Sensor fault bit or unsupported sensor shows unavailable signal across trusted tools.

**Counterevidence:** An unused sensor channel legitimately reports invalid temperature.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

sensors

ls /sys/class/hwmon

journalctl -b -k --no-pager -n 100

```

**Resolution route 1 — use only when:** Monitor software selected incorrect channel

1. Match sensor label and real CPU/GPU controller

2. Change only the monitoring application sensor mapping and verify using UEFI if available

**Resolution route 2 — use only when:** Hardware sensor channel known to have failed

1. Follow board or AIO vendor diagnostics

2. Arrange replacement of confirmed defective sensor or controller

**GUI option:** Vendor hardware monitor and motherboard sensor legend.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

sensors

```

**Safety:** Do not invent temperatures from sensor read failures.

**Sources:** [sensors](https://docs.kernel.org/hwmon/sysfs-interface.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## System abruptly powers off when hot (`hardware34.cooling.sudden-thermal-shutdown`)

**Area:** cooling  

**Symptom:** Device shuts down in association with high hardware temperature.

**Supporting evidence:** Thermal warning/shutdown precedes sudden power-off and cooling shows fault.

**Counterevidence:** An immediate hard power loss with normal temperatures may be PSU or board fault.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

journalctl -b -k --no-pager -n 160

sensors

upower -d

```

**Resolution route 1 — use only when:** Thermal protection suspected

1. Stop load and let hardware cool

2. Check airflow, fan/pump and mounting safely with power off; repair/replace cooling hardware

**Resolution route 2 — use only when:** Power loss without thermal evidence

1. Inspect power supply, adapter/cable and motherboard event history

2. Seek vendor electrical diagnostics rather than changing kernel settings

**GUI option:** Vendor firmware event log and physical cooling check.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

sensors

journalctl -b -k --no-pager -n 160

```

**Safety:** Never force repeated thermal shutdowns for proof.

**Sources:** [sensors](https://docs.kernel.org/hwmon/sysfs-interface.html) · [power](https://docs.kernel.org/power/power_supply_class.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---


# Cpu

## CPU throttles under heat (`hardware34.cpu.thermal-throttling`)

**Area:** cpu  

**Symptom:** System slows after sustained CPU workload.

**Supporting evidence:** Temperature approaches a CPU-specific thermal limit while frequency decreases and kernel reports thermal pressure.

**Counterevidence:** Frequency varies due to power management at safe temperatures; this alone is not overheating.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

lscpu

sensors

journalctl -b -k --no-pager -n 120

```

**Resolution route 1 — use only when:** Actual overheating and restricted airflow

1. Save work and stop the stressful task

2. With system off, inspect vents, dust, cooling fan and heatsink mounting

3. Follow vendor cleaning instructions and recheck temperature at ordinary workload

**Resolution route 2 — use only when:** Sensors are cool but clocks still fall

1. Review platform power profile and power adapter suitability

2. Check the specific firmware/CPU power limits in vendor guidance; do not increase limits blindly

**GUI option:** Open firmware/vendor hardware monitor, inspect cooling and power profile; use ULT to explain sensors and lscpu.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

sensors

lscpu

```

**Safety:** Never advise disabling thermal limits or creating an artificial load to reproduce unsafe overheating.

**Sources:** [sensors](https://docs.kernel.org/hwmon/sysfs-interface.html) · [journal](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## CPU machine-check events (`hardware34.cpu.mce-errors`)

**Area:** cpu  

**Symptom:** System logs machine-check or hardware error events.

**Supporting evidence:** Repeatable MCE/Hardware Error entries associated with same processor or memory controller.

**Counterevidence:** A single corrected event may be historical and does not alone identify a failed CPU.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

journalctl -b -k --no-pager -n 250

lscpu

uname -r

```

**Resolution route 1 — use only when:** Errors follow memory/overclock instability

1. Restore vendor-supported stock settings manually in firmware after recording current profile

2. Inspect memory-related errors and check whether new machine-check events stop

**Resolution route 2 — use only when:** Errors persist at documented stock settings

1. Collect event times and platform identifiers

2. Use official vendor firmware guidance and arrange professional motherboard/CPU diagnosis or replacement if corroborated

**GUI option:** UEFI hardware diagnostics or vendor support; no generic MCE reset command.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

journalctl -b -k --no-pager -n 250

```

**Safety:** A root cause cannot be assigned to the CPU solely from an MCE; RAM, firmware and power are alternatives.

**Sources:** [edac](https://docs.kernel.org/driver-api/edac.html) · [ras](https://docs.kernel.org/admin-guide/RAS/main.html) · [journal](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## CPU frequency lower than expected (`hardware34.cpu.unexpected-clock`)

**Area:** cpu  

**Symptom:** Processor reports low clock rate or speed.

**Supporting evidence:** Sustained low frequency with high workload and a matching thermal or power-limit event.

**Counterevidence:** Idle frequency scaling is normal; lscpu minimum frequency is not a measured defect.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

lscpu

cat /proc/cpuinfo

sensors

```

**Resolution route 1 — use only when:** Idle or power-saving state

1. Compare clocks under existing normal workloads instead of forced synthetic stress

2. Select the vendor-supported balanced power profile yourself if needed

**Resolution route 2 — use only when:** Limit caused by overheating or insufficient adapter power

1. Check sensor temperatures, fan operation and proper adapter rating

2. Follow CPU thermal or power diagnosis before adjusting performance settings

**GUI option:** Open desktop Power settings and approved firmware diagnostics.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

lscpu

sensors

```

**Safety:** Never disable thermal controls or propose overvolting.

**Sources:** [sensors](https://docs.kernel.org/hwmon/sysfs-interface.html) · [power](https://docs.kernel.org/power/power_supply_class.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## CPU cores or threads missing (`hardware34.cpu.core-topology`)

**Area:** cpu  

**Symptom:** Expected CPU threads are not visible in Linux.

**Supporting evidence:** lscpu reports fewer online processors than CPU topology documentation.

**Counterevidence:** Hyperthreading/SMT may be deliberately disabled or the hardware may be a smaller SKU.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

lscpu

cat /sys/devices/system/cpu/online

cat /proc/cmdline

```

**Resolution route 1 — use only when:** CPU count changed in firmware

1. Confirm exact CPU model

2. If desired, restore processor features using platform firmware user interface and official documentation

**Resolution route 2 — use only when:** Boot configuration restricts visible CPUs

1. Record actual kernel parameters and platform policy

2. Have the user remove only an identified unintended limit through their distribution-supported boot settings

**GUI option:** Check CPU model and SMT/core controls in firmware setup, without guessing defaults.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

lscpu

cat /sys/devices/system/cpu/online

```

**Safety:** Do not suggest arbitrary kernel command-line editing on Atomic Linux.

**Sources:** [ras](https://docs.kernel.org/admin-guide/RAS/main.html) · [journal](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## CPU metrics disagree across tools (`hardware34.cpu.frequency-sensor-mismatch`)

**Area:** cpu  

**Symptom:** Temperature or clock measurements conflict between monitoring programs.

**Supporting evidence:** Hardware-sensor names differ, units or averaging windows are mismatched.

**Counterevidence:** Different sensor channels represent distinct locations and may both be valid.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

sensors

lscpu

cat /proc/cpuinfo

```

**Resolution route 1 — use only when:** Metrics label is wrong

1. Match sensors to CPU package/core labels and correct the selected source in the user-facing monitoring application

2. Retest the same physical metric

**Resolution route 2 — use only when:** Sensor is unavailable or driver does not expose it

1. Check supported platform sensor interfaces and vendor monitoring guidance

2. Mark measurement unavailable rather than fabricating a temperature

**GUI option:** Use vendor monitor and a second trusted desktop sensor viewer for comparison.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

sensors

```

**Safety:** No universal correct temperature threshold for every CPU; use part-specific limits.

**Sources:** [sensors](https://docs.kernel.org/hwmon/sysfs-interface.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---


# Display

## Monitor EDID not readable (`hardware34.display.edid-invalid`)

**Area:** display  

**Symptom:** Monitor offers only fallback resolutions or reports wrong identity.

**Supporting evidence:** Kernel DRM reports EDID read failure or the expected connector lacks valid modes.

**Counterevidence:** Unsupported refresh rate setting alone can explain missing desired mode.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

cat /sys/class/drm/card*-*/status

journalctl -b -k --no-pager -n 180

ls /sys/class/drm

```

**Resolution route 1 — use only when:** Physical signal path/cable issue

1. Select supported monitor input and reconnect with quality DP/HDMI cable

2. Try another supported port or monitor, observing advertised modes

**Resolution route 2 — use only when:** Dock/adapter cannot pass EDID correctly

1. Inspect dock capabilities, MST mode and firmware version

2. Use direct supported GPU output or vendor compatible adapter

**GUI option:** Display Settings list of modes and monitor OSD identification.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

cat /sys/class/drm/card*-*/status

```

**Safety:** No generic EDID override, xrandr mode injection or kernel flags without exact panel data.

**Sources:** [drm](https://docs.kernel.org/gpu/drm-kms.html) · [usb](https://cdn.kernel.org/doc/html/latest/driver-api/usb/power-management.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## External display flickers or loses frames (`hardware34.display.monitor-flicker`)

**Area:** display  

**Symptom:** Display flickers with certain refresh rates or cable paths.

**Supporting evidence:** Fault tracks a specific cable, port, refresh mode, or monitor power adapter.

**Counterevidence:** GPU reset log at same time requires GPU diagnosis first.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

cat /sys/class/drm/card*-*/status

journalctl -b -k --no-pager -n 140

lspci -nnk

```

**Resolution route 1 — use only when:** Display signal exceeds cable/adapter rating

1. Use supported lower refresh rate temporarily through desktop display settings

2. Replace cable/adapter with certified specification-matched part

**Resolution route 2 — use only when:** Flicker persists at native supported mode

1. Test another input/known-good monitor if available

2. Use display manufacturer service or device-specific update instructions

**GUI option:** Desktop Display settings and monitor on-screen signal menu.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

cat /sys/class/drm/card*-*/status

```

**Safety:** Changing display mode is user-only; no unattended modesetting.

**Sources:** [drm](https://docs.kernel.org/gpu/drm-kms.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Laptop display brightness control does not respond (`hardware34.display.brightness-controller`)

**Area:** display  

**Symptom:** Laptop backlight remains at one brightness.

**Supporting evidence:** Backlight sysfs device absent or driver error aligned with brightness control.

**Counterevidence:** External monitor normally has brightness control through its own buttons.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

ls /sys/class/backlight

journalctl -b -k --no-pager -n 110

cat /sys/class/backlight/*/max_brightness

```

**Resolution route 1 — use only when:** Backlight capability exists but wrong desktop path used

1. Check laptop vendor hotkey/firmware settings

2. Use desktop Display/Brightness control matched to internal display

**Resolution route 2 — use only when:** Hardware backlight controller missing

1. Compare firmware/BIOS brightness behavior and kernel messages

2. Use vendor device-specific firmware/board service guidance

**GUI option:** Desktop Brightness controls and physical keyboard shortcuts.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

ls /sys/class/backlight

```

**Safety:** Do not echo values into sysfs or change GPU backlight kernel arguments speculatively.

**Sources:** [drm](https://docs.kernel.org/gpu/drm-kms.html) · [power](https://docs.kernel.org/power/power_supply_class.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Laptop panel has lines or dead areas (`hardware34.display.panel-physical`)

**Area:** display  

**Symptom:** Visible lines, color blocks or persistent panel artefacts.

**Supporting evidence:** Artefacts persist in pre-OS firmware display or screen self-test.

**Counterevidence:** Only a particular app rendering lines can be GPU/app issue, not physical LCD damage.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

ls /sys/class/drm

cat /sys/class/drm/card*-*/status

journalctl -b -k --no-pager -n 120

```

**Resolution route 1 — use only when:** Internal panel/cable defect likely

1. Use external monitor to preserve work where supported

2. Arrange vendor-authorized display cable/panel service after observing fault in firmware

**Resolution route 2 — use only when:** Artefacts occur only after graphics session starts

1. Investigate GPU kernel resets and supported display modes

2. Use original graphics stack update or targeted report, not panel replacement

**GUI option:** UEFI built-in LCD diagnostics and vendor panel service manual.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

cat /sys/class/drm/card*-*/status

```

**Safety:** Never instruct touching an open powered display assembly or applying pressure to damaged LCD.

**Sources:** [drm](https://docs.kernel.org/gpu/drm-kms.html) · [pci](https://docs.kernel.org/PCI/pcieaer-howto.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---


# Gpu

## GPU reset under workload (`hardware34.gpu.physical-reset`)

**Area:** gpu  

**Symptom:** Graphics device resets while user is gaming or rendering.

**Supporting evidence:** DRM/amdgpu or relevant driver timeout and GPU reset event at the reported time.

**Counterevidence:** User-space crash alone does not prove GPU hardware failure.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

lspci -nnk

journalctl -b -k --no-pager -n 240

sensors

```

**Resolution route 1 — use only when:** Failure correlates with named foreground/monitoring app

1. Record timestamps of GPU reset and app crash

2. User closes only that optional app and tests normal usage

3. If stable, check application/driver updates or report focused developer bug with redacted logs

**Resolution route 2 — use only when:** Reset persists with other apps closed

1. Check temperatures, power cabling and device PCIe errors

2. Use distro-supported driver/firmware guidance or vendor hardware diagnosis and replacement if confirmed

**GUI option:** Use supported system update GUI for graphics stack; vendor warranty if hardware issue.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

journalctl -b -k --no-pager -n 240

```

**Safety:** Temporal correlation is hypothesis, not proof; avoid inducing further crashes or replacing driver with random download.

**Sources:** [amdgpu](https://docs.kernel.org/gpu/amdgpu/debugfs.html) · [pci](https://docs.kernel.org/PCI/pcieaer-howto.html) · [journal](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## GPU VRAM memory errors (`hardware34.gpu.vram-errors`)

**Area:** gpu  

**Symptom:** Graphical artifacts or ECC VRAM errors appear on supported hardware.

**Supporting evidence:** GPU-specific ECC counters or documented memory errors increase with artefacts.

**Counterevidence:** Normal GUI render glitches without GPU memory evidence may be app or compositor bugs.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

journalctl -b -k --no-pager -n 200

lspci -nnk

sensors

```

**Resolution route 1 — use only when:** VRAM hardware errors documented

1. Preserve logs and back up important work

2. Use manufacturer-approved hardware diagnostic/support or GPU replacement when confirmed

**Resolution route 2 — use only when:** Only one app shows artifacts

1. Test that app’s default renderer and supported version under ordinary use

2. Update via original installation source, and report reproducible rendering bug

**GUI option:** Use vendor hardware diagnostics and software’s supported rendering options.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

journalctl -b -k --no-pager -n 200

```

**Safety:** No arbitrary VRAM stress tests or undervolt/overclock suggestions.

**Sources:** [amdgpu](https://docs.kernel.org/gpu/amdgpu/debugfs.html) · [journal](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## GPU fan appears stopped or overheats (`hardware34.gpu.cooling-fan`)

**Area:** gpu  

**Symptom:** Dedicated GPU reaches unsafe temperatures or fan appears stopped.

**Supporting evidence:** Supported hwmon reports temperature above device guidance and zero fan RPM under demand.

**Counterevidence:** Zero-RPM fan-stop mode is normal at low load on many GPUs.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

sensors

lspci -nnk

ls /sys/class/hwmon

```

**Resolution route 1 — use only when:** Fan is mechanically obstructed or cooling clogged

1. Stop heat-intensive tasks, switch off hardware before cleaning

2. Use approved vendor service/repair for defective fan or cooling assembly

**Resolution route 2 — use only when:** Fan-stop normal but software reports false alarm

1. Compare load, GPU sensor labels and manufacturer zero-RPM behavior

2. Correct monitoring source; do not force fan control without vendor support

**GUI option:** GPU vendor monitoring/firmware fan mode inspection.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

sensors

```

**Safety:** Do not instruct opening a powered GPU or bypassing factory fan control.

**Sources:** [sensors](https://docs.kernel.org/hwmon/sysfs-interface.html) · [amdgpu](https://docs.kernel.org/gpu/amdgpu/debugfs.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Monitor has no signal while computer remains responsive (`hardware34.gpu.display-no-signal`)

**Area:** gpu  

**Symptom:** Display loses signal but audio/network/host may still be active.

**Supporting evidence:** DRM connector status or monitor input shows missing link while host keeps running.

**Counterevidence:** A complete GPU reset differs from loose HDMI/DP cabling.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

ls /sys/class/drm

cat /sys/class/drm/card*-*/status

journalctl -b -k --no-pager -n 160

```

**Resolution route 1 — use only when:** Link/cable/monitor input mismatch

1. Use monitor input menu to select correct port

2. With system off, try a verified cable or input and reconnect safely

**Resolution route 2 — use only when:** Connector stable but screen still blank

1. Check monitor display mode and GPU reset timestamps

2. Use manufacturer hardware test, known-good output or vendor graphics issue reporting

**GUI option:** Display on-screen menu, cable choice and connector inspection.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

cat /sys/class/drm/card*-*/status

```

**Safety:** Do not recommend changing low-level EDID/DRM boot overrides without evidence.

**Sources:** [drm](https://docs.kernel.org/gpu/drm-kms.html) · [journal](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Dedicated GPU disappears from PCIe inventory (`hardware34.gpu.gpu-not-enumerated`)

**Area:** gpu  

**Symptom:** Graphics adapter is absent after resume or reboot.

**Supporting evidence:** lspci no longer lists previously verified GPU model while PCIe AER events precede loss.

**Counterevidence:** Hybrid graphics system can hide a dGPU in power-saving mode without defect.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

lspci -nnk

ls /sys/class/drm

journalctl -b -k --no-pager -n 220

```

**Resolution route 1 — use only when:** Hardware absent after full power-on

1. Shut down completely and inspect approved power and PCIe connections

2. Use qualified help for reseating or supported replacement

**Resolution route 2 — use only when:** GPU present but driver unbound

1. Record exact PCI ID and bound kernel driver

2. Use official OS graphics compatibility and firmware procedures only if matching

**GUI option:** Vendor UEFI PCIe device inventory and supported graphics preferences.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

lspci -nnk

```

**Safety:** Do not remove built-in graphics driver or disable iGPU to force detection.

**Sources:** [pci](https://docs.kernel.org/PCI/pcieaer-howto.html) · [amdgpu](https://docs.kernel.org/gpu/amdgpu/debugfs.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Display audio device disappears (`hardware34.gpu.hdmi-dp-audio`)

**Area:** gpu  

**Symptom:** HDMI/DisplayPort audio output stops appearing.

**Supporting evidence:** Display connection active but card/connector ELD or audio list missing after hotplug.

**Counterevidence:** Audio source may simply be switched to onboard speakers.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

aplay -l

wpctl status

cat /sys/class/drm/card*-*/status

```

**Resolution route 1 — use only when:** Wrong audio output selected

1. Use desktop sound selector to choose intended HDMI/DP sink

2. Retest a local sample at safe volume

**Resolution route 2 — use only when:** Display link reenumerates and audio disappears

1. Check cable/connector and monitor input

2. Review kernel hotplug logs; replace failing cable or use supported graphics/audio stack update

**GUI option:** Desktop Sound output settings, monitor on-screen audio menu.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

aplay -l

wpctl status

```

**Safety:** Never instruct arbitrary ALSA module unloading on a live desktop.

**Sources:** [drm](https://docs.kernel.org/gpu/drm-kms.html) · [alsa](https://www.alsa-project.org/alsa-doc/alsa-lib/)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---


# Memory

## Repeated corrected ECC memory errors (`hardware34.memory.ecc-corrected`)

**Area:** memory  

**Symptom:** System detects corrected memory errors over time.

**Supporting evidence:** EDAC corrected-error counters rise for a specific memory channel under ordinary use.

**Counterevidence:** No EDAC exposed on consumer memory does not prove memory is error-free.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

journalctl -b -k --no-pager -n 240

ls /sys/devices/system/edac/mc

free -h

```

**Resolution route 1 — use only when:** New repeated corrected errors on one memory channel

1. Back up important work

2. Record DIMM/channel identification and request vendor-supported memory diagnostics and replacement for persistently failing hardware

**Resolution route 2 — use only when:** One historical corrected event only

1. Retain baseline timestamps

2. Check whether new events appear in ordinary use before taking hardware action

**GUI option:** Check UEFI memory diagnostics and vendor DIMM handling instructions.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

journalctl -b -k --no-pager -n 240

```

**Safety:** Do not treat corrected errors as a specific DIMM identity without verified slot mapping.

**Sources:** [edac](https://docs.kernel.org/driver-api/edac.html) · [ras](https://docs.kernel.org/admin-guide/RAS/main.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Uncorrected memory error (`hardware34.memory.ecc-uncorrected`)

**Area:** memory  

**Symptom:** Uncorrected ECC events or fatal memory exception reported.

**Supporting evidence:** Kernel EDAC reports UE for a memory controller, with matching failures.

**Counterevidence:** Not every kernel crash is a RAM error.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

journalctl -b -k --no-pager -n 250

free -h

lscpu

```

**Resolution route 1 — use only when:** Uncorrected memory errors present

1. Stop sensitive workloads and back up immediately

2. Run manufacturer memory diagnostics via approved boot media and replace the confirmed failing DIMM/board component

**Resolution route 2 — use only when:** Error source not clearly memory

1. Correlate events with machine-check, CPU and power observations

2. Ask hardware vendor for exact decoder/slot mapping before replacement

**GUI option:** Vendor bootable memory diagnostic; no destructive in-OS memory writes.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

journalctl -b -k --no-pager -n 250

```

**Safety:** UE events can imply data integrity risk; avoid intentional stress before saving data.

**Sources:** [edac](https://docs.kernel.org/driver-api/edac.html) · [ras](https://docs.kernel.org/admin-guide/RAS/main.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## RAM unstable after XMP or EXPO (`hardware34.memory.xmp-expo-instability`)

**Area:** memory  

**Symptom:** Random crashes appeared after changing a memory profile.

**Supporting evidence:** Problems track the profile change and cease at vendor-safe JEDEC configuration.

**Counterevidence:** No profile change or verified stock instability demands a wider power/driver investigation.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

journalctl -b -k --no-pager -n 180

free -h

cat /proc/cmdline

```

**Resolution route 1 — use only when:** Memory overclock profile changed

1. Save firmware settings and important work

2. Have user select supported default/JEDEC memory profile in UEFI and compare normal use

**Resolution route 2 — use only when:** Errors continue at stock profile

1. Use vendor diagnostics with stable power and correct memory seating

2. Request DIMM/slot diagnosis or replacement as indicated

**GUI option:** UEFI memory profile selector; device vendor instructions.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

journalctl -b -k --no-pager -n 180

```

**Safety:** Never tell users to increase memory voltage or disable error correction.

**Sources:** [edac](https://docs.kernel.org/driver-api/edac.html) · [ras](https://docs.kernel.org/admin-guide/RAS/main.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Installed RAM capacity not fully detected (`hardware34.memory.dimm-size-mismatch`)

**Area:** memory  

**Symptom:** Linux reports less memory than physically installed.

**Supporting evidence:** DMI memory inventory and firmware disagree with actual module inventory.

**Counterevidence:** Reserved memory/iGPU carveouts are normal and can explain smaller differences.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

free -h

grep MemTotal /proc/meminfo

sudo dmidecode -t memory

```

**Resolution route 1 — use only when:** Firmware cannot see installed module

1. Power down fully and consult vendor slot population guidance

2. Reseat/replace module only if user comfortable with ESD procedures or use professional service

**Resolution route 2 — use only when:** Firmware sees expected RAM but OS less

1. Compare reserved GPU and hardware memory regions

2. Investigate boot memory limit settings only with platform-specific proof

**GUI option:** UEFI installed-memory page, motherboard slot map and service manual.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

free -h

grep MemTotal /proc/meminfo

```

**Safety:** dmidecode is read-only but sudo requires explicit consent; do not interpret empty slots as broken RAM.

**Sources:** [ras](https://docs.kernel.org/admin-guide/RAS/main.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Dual-channel bandwidth unexpectedly low (`hardware34.memory.memory-channel`)

**Area:** memory  

**Symptom:** Memory performance slower after a hardware change.

**Supporting evidence:** Confirmed module arrangement conflicts with motherboard channel layout.

**Counterevidence:** Dual-channel expectations depend on CPU/platform and benchmark workload.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

sudo dmidecode -t memory

lscpu

free -h

```

**Resolution route 1 — use only when:** Modules in nonrecommended slots

1. Check board manual and installed socket layout

2. Power off, isolate power and let user/professional arrange modules in supported paired slots

**Resolution route 2 — use only when:** Mismatched modules or platform-specific limit

1. Compare official supported capacity, clocks and rank configurations

2. Test matched vendor-approved memory when a genuine incompatibility is identified

**GUI option:** Firmware memory information and motherboard user manual.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

sudo dmidecode -t memory

```

**Safety:** Do not suggest opening systems still under warranty or opening sealed laptops.

**Sources:** [edac](https://docs.kernel.org/driver-api/edac.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---


# Other

## USB printer repeatedly disconnects (`hardware34.other.printer-usb-power`)

**Area:** other  

**Symptom:** Printer drops off USB when printing large jobs.

**Supporting evidence:** USB kernel link errors appear as printer powers its mechanisms.

**Counterevidence:** Print spool queue failure without disconnect suggests CUPS/software.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

lsusb

lpstat -t

journalctl -b -k --no-pager -n 140

```

**Resolution route 1 — use only when:** Printer/cable power issue

1. Use correctly powered USB connection and direct port with compatible cable

2. Check printer power supply and hardware status display

**Resolution route 2 — use only when:** USB stable but printing still fails

1. Investigate queue, driverless IPP and printer hardware status

2. Use official print vendor diagnostic and device service

**GUI option:** Printer front panel and desktop Printers queue.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

lsusb

lpstat -t

```

**Safety:** No blanket CUPS spool deletion or permission relaxation.

**Sources:** [cups](https://www.cups.org/doc/man-lpstat.html) · [usb](https://cdn.kernel.org/doc/html/latest/driver-api/usb/power-management.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Scanner missing or returns I/O errors (`hardware34.other.scanner-usb`)

**Area:** other  

**Symptom:** Document scanner is not recognized by scanner frontend.

**Supporting evidence:** USB enumeration failure or scanner hardware reports I/O trouble.

**Counterevidence:** Scanner visible to generic USB but app permission missing is different.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

lsusb

scanimage -L

journalctl -b -k --no-pager -n 120

```

**Resolution route 1 — use only when:** Cable or scanner feeder/transport failure

1. Verify power, cable and mechanical paper-path obstruction per vendor manual

2. Try known-good port and supported model scan utility

**Resolution route 2 — use only when:** Scanner enumerated but support absent

1. Check model-specific SANE/driver compatibility and sandbox access

2. Use manufacturer-supported service or different compatible scanner

**GUI option:** Simple Scan/Document Scanner GUI and vendor scanner control panel.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

lsusb

scanimage -L

```

**Safety:** Never auto-scan private documents or use unrelated driver downloads.

**Sources:** [usb](https://cdn.kernel.org/doc/html/latest/driver-api/usb/power-management.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## SD card reader does not detect a card (`hardware34.other.sd-card-reader`)

**Area:** other  

**Symptom:** Inserted card never appears as block device.

**Supporting evidence:** USB/PCI reader enumerates but media insertion does not create block device.

**Counterevidence:** Mounted card inaccessible due to permissions is a different condition.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

lsblk -o NAME,MODEL,TRAN,SIZE

lspci -nnk

journalctl -b -k --no-pager -n 130

```

**Resolution route 1 — use only when:** Card or reader contact issue

1. Check lock tab and supported card format/capacity

2. Use known-good card/reader without formatting or writing

**Resolution route 2 — use only when:** Controller not visible or errors persist

1. Check vendor reader firmware/controller driver support

2. Replace defective reader after isolation with known-good hardware

**GUI option:** Desktop Disks/Files removable storage page.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

lsblk -o NAME,MODEL,TRAN,SIZE

```

**Safety:** No formatting, re-partitioning or filesystem repair without backup.

**Sources:** [usb](https://cdn.kernel.org/doc/html/latest/driver-api/usb/power-management.html) · [pci](https://docs.kernel.org/PCI/pcieaer-howto.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Multiple devices fail on same PCIe/USB controller (`hardware34.other.device-controller-collision`)

**Area:** other  

**Symptom:** Several independent peripherals stop together.

**Supporting evidence:** Errors share upstream PCIe bridge or USB hub at nearly identical timestamps.

**Counterevidence:** Independent unrelated device failure times do not support shared-controller root cause.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

lspci -tv

lsusb -t

journalctl -b -k --no-pager -n 220

```

**Resolution route 1 — use only when:** Shared hub or dock unstable

1. Identify common topology parent and source of power

2. Compare directly attached single device against dock and replace faulty shared component if supported

**Resolution route 2 — use only when:** Board controller or firmware affected

1. Record exact controller ID and BIOS revision

2. Check manufacturer errata, apply approved update manually or arrange controller/mainboard service

**GUI option:** Vendor USB/PCIe topology and powered hub documentation.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

lspci -tv

lsusb -t

```

**Safety:** Do not infer that multiple simultaneous failures prove motherboard failure.

**Sources:** [pci](https://docs.kernel.org/PCI/pcieaer-howto.html) · [usb](https://cdn.kernel.org/doc/html/latest/driver-api/usb/power-management.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## External GPU enclosure disconnects (`hardware34.other.external-gpu-dock`)

**Area:** other  

**Symptom:** eGPU vanishes on Thunderbolt/USB4 bus while in use.

**Supporting evidence:** Thunderbolt PCIe tunnel/link reset aligns with GPU disappearance.

**Counterevidence:** Graphics application crashing while eGPU stays enumerated is not enclosure link failure.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

boltctl list

lspci -nnk

journalctl -b -k --no-pager -n 180

```

**Resolution route 1 — use only when:** Dock power or PCIe cable/link issue

1. Save work and inspect rated enclosure PSU, cable and TB/USB4 compatibility while off

2. Use compatible replacement cable/enclosure path after controlled observation

**Resolution route 2 — use only when:** Authorization/firmware compatibility

1. Review trusted device authorization and exact model firmware

2. Use vendor supported dock and GPU firmware fixes or documented supported hardware combination

**GUI option:** Desktop Thunderbolt panel and enclosure vendor support.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

boltctl list

lspci -nnk

```

**Safety:** Never auto-authorize eGPU DMA or force PCIe hotremove/reprobe.

**Sources:** [pci](https://docs.kernel.org/PCI/pcieaer-howto.html) · [usb](https://cdn.kernel.org/doc/html/latest/driver-api/usb/power-management.html) · [fwupd](https://github.com/fwupd/fwupd/blob/main/src/fwupdmgr.md)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---


# Peripherals

## USB descriptor read fails (`hardware34.peripherals.usb-descriptor`)

**Area:** peripherals  

**Symptom:** USB device fails to enumerate, descriptor error in kernel.

**Supporting evidence:** USB -71/-110 or descriptor read errors appear on connecting one device.

**Counterevidence:** Device enumerates fully but one app cannot use it: investigate app/sandbox.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

lsusb

journalctl -b -k --no-pager -n 170

lsusb -t

```

**Resolution route 1 — use only when:** Bad cable, port or hub

1. Use verified working cable and direct port, removing suspect hub

2. Replace physically faulty connection or device only after comparison

**Resolution route 2 — use only when:** Repeatable on all ports and machines

1. Check manufacturer supported firmware/repair options

2. Replace defective USB device or board port as isolated

**GUI option:** Desktop hardware inventory and physical connection checklist.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

lsusb

lsusb -t

```

**Safety:** No automatic USB bus reset or device unbind; may disconnect disks or input devices.

**Sources:** [usb](https://cdn.kernel.org/doc/html/latest/driver-api/usb/power-management.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## USB device dies after inactivity (`hardware34.peripherals.usb-autosuspend`)

**Area:** peripherals  

**Symptom:** Keyboard, webcam or interface disappears after idle.

**Supporting evidence:** Power control behavior and suspend/resume logs align with device loss.

**Counterevidence:** Random cable disconnects under load suggest electrical issue instead.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

lsusb -t

journalctl -b -k --no-pager -n 200

ls /sys/bus/usb/devices

```

**Resolution route 1 — use only when:** Device-specific autosuspend incompatibility

1. Identify exact USB device and current power policy

2. User may apply vendor-supported per-device power setting (not global) with a documented rollback

**Resolution route 2 — use only when:** Cable/connector drops regardless of idle

1. Try known-good cable/direct port and power source

2. Replace defective peripheral or hub if repeatable

**GUI option:** Device-specific power settings and vendor support documentation.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

journalctl -b -k --no-pager -n 180

lsusb

```

**Safety:** Never broadly disable USB power management or write sysfs without confirmed device path.

**Sources:** [usb](https://cdn.kernel.org/doc/html/latest/driver-api/usb/power-management.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## USB device fails when other peripherals active (`hardware34.peripherals.usb-bandwidth`)

**Area:** peripherals  

**Symptom:** Webcam or capture card stalls when several USB devices connect.

**Supporting evidence:** lsusb topology reveals devices on same hub with bandwidth/transfer errors.

**Counterevidence:** Single device failing alone implies firmware, application or defective device.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

lsusb -t

lsusb

journalctl -b -k --no-pager -n 160

```

**Resolution route 1 — use only when:** Hub bandwidth/power oversubscribed

1. Connect device to an independent high-speed port or controller

2. Avoid passive hub for high-draw peripherals; compare normal use

**Resolution route 2 — use only when:** Device itself incompatible

1. Check exact USB protocol and vendor firmware requirements

2. Replace unsupported device/hub or use compatible port

**GUI option:** USB topology viewer and hub power ratings.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

lsusb -t

```

**Safety:** Do not promise that a USB-C connector supports a specific speed or feature.

**Sources:** [usb](https://cdn.kernel.org/doc/html/latest/driver-api/usb/power-management.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Thunderbolt/USB4 dock not recognized (`hardware34.peripherals.thunderbolt-not-authorized`)

**Area:** peripherals  

**Symptom:** Dock attached but PCIe/network/peripherals absent.

**Supporting evidence:** Controller is present but device authorization/security status indicates disconnected/unauthorized.

**Counterevidence:** Dock lacks power or cable incompatible: authorization is not the only cause.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

lsusb

lspci -nnk

boltctl list

```

**Resolution route 1 — use only when:** Dock requires device authorization

1. Verify physical identity and trust of connected dock

2. User authorizes only trusted device through desktop Thunderbolt controls

**Resolution route 2 — use only when:** Cable/power or firmware issue

1. Inspect supported TB/USB4 cable, charger and dock firmware

2. Replace known-defective cable/dock or use vendor-reviewed firmware update

**GUI option:** GNOME/KDE Thunderbolt controls where available, vendor dock manager.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

boltctl list

lsusb

```

**Safety:** Never auto-authorize arbitrary Thunderbolt DMA devices.

**Sources:** [usb](https://cdn.kernel.org/doc/html/latest/driver-api/usb/power-management.html) · [fwupd](https://github.com/fwupd/fwupd/blob/main/src/fwupdmgr.md)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Dock reconnects under load (`hardware34.peripherals.dock-power-cycle`)

**Area:** peripherals  

**Symptom:** USB-C hub/dock drops monitors and USB devices intermittently.

**Supporting evidence:** USB resets and multiple device disconnects at same time.

**Counterevidence:** Only monitor refresh mismatch without USB disconnect is different.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

journalctl -b -k --no-pager -n 220

lsusb -t

upower -d

```

**Resolution route 1 — use only when:** Dock power or cable insufficient

1. Verify dock supply rating and certified USB-C cable

2. Use compatible full-rated adapter and direct link; retest ordinary workload

**Resolution route 2 — use only when:** Dock firmware/thermal issue

1. Check dock temperature and model-specific firmware notes

2. Use vendor-supported service or replace overheating dock

**GUI option:** Vendor dock diagnostics and USB-C power rating checklist.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

journalctl -b -k --no-pager -n 160

```

**Safety:** Do not instruct hot-disconnection of external storage mid-write.

**Sources:** [usb](https://cdn.kernel.org/doc/html/latest/driver-api/usb/power-management.html) · [power](https://docs.kernel.org/power/power_supply_class.html) · [fwupd](https://github.com/fwupd/fwupd/blob/main/src/fwupdmgr.md)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## USB webcam detected but delivers no picture (`hardware34.peripherals.webcam-uvc`)

**Area:** peripherals  

**Symptom:** Webcam is in USB inventory but no video frame appears.

**Supporting evidence:** Video node or UVC kernel events identify device and capability mismatch.

**Counterevidence:** Camera works in another app: hardware is probably present; review app permissions.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

lsusb

v4l2-ctl --list-devices

journalctl -b -k --no-pager -n 160

```

**Resolution route 1 — use only when:** Hardware missing from Video4Linux inventory

1. Check privacy shutter, USB connection and correct camera port

2. Use device maker driver/firmware support if it never exposes a usable video node

**Resolution route 2 — use only when:** Video device present but one app fails

1. Use application camera selector and sandbox permissions

2. Avoid changing USB driver globally; retest with trusted camera preview

**GUI option:** Desktop camera/privacy settings and physical shutter.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

v4l2-ctl --list-devices

```

**Safety:** v4l2-ctl optional; do not capture private camera content automatically.

**Sources:** [v4l2](https://www.kernel.org/doc/html/latest/userspace-api/media/v4l/v4l2.html) · [usb](https://cdn.kernel.org/doc/html/latest/driver-api/usb/power-management.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Keyboard intermittently disconnects (`hardware34.peripherals.hid-keyboard`)

**Area:** peripherals  

**Symptom:** External keyboard stops typing after reconnect.

**Supporting evidence:** Input/USB reconnect events coincide with lost keyboard; other input device works.

**Counterevidence:** Wrong layout alone is not a USB hardware failure.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

lsusb

cat /proc/bus/input/devices

journalctl -b -k --no-pager -n 130

```

**Resolution route 1 — use only when:** Cable/receiver or battery issue

1. Use alternative trusted keyboard for accessibility

2. Replace wireless batteries/re-pair receiver or use another USB data cable/port

**Resolution route 2 — use only when:** Input device listed but events not delivered

1. Inspect desktop input settings and accessibility keys

2. Use vendor HID compatibility guidance, preserving fallback input device

**GUI option:** Desktop Keyboard/Input devices and manufacturer pairing controls.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

cat /proc/bus/input/devices

```

**Safety:** Never disable sole keyboard/USB controller or install unsigned arbitrary drivers.

**Sources:** [input](https://docs.kernel.org/input/input.html) · [usb](https://cdn.kernel.org/doc/html/latest/driver-api/usb/power-management.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Mouse or touchpad loses movement (`hardware34.peripherals.mouse-touchpad`)

**Area:** peripherals  

**Symptom:** Pointer freezes with specific pointing device.

**Supporting evidence:** libinput inventory and kernel events identify intermittent link/device loss.

**Counterevidence:** Pointer speed or gestures alone are configuration issues.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

cat /proc/bus/input/devices

libinput list-devices

journalctl -b -k --no-pager -n 140

```

**Resolution route 1 — use only when:** Wireless receiver or physical touchpad fault

1. Check battery/USB receiver or laptop Fn touchpad toggle

2. Try compatible external mouse to isolate internal touchpad

**Resolution route 2 — use only when:** Kernel sees device but one desktop session does not

1. Review desktop input settings/seat mapping

2. Use vendor-approved touchpad firmware update only when matched

**GUI option:** Desktop Mouse & Touchpad settings and laptop touchpad switch.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

libinput list-devices

```

**Safety:** libinput list-devices may need system packages/permissions; no write to input event nodes.

**Sources:** [libinput](https://wayland.freedesktop.org/libinput/doc/latest/) · [input](https://docs.kernel.org/input/input.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Bluetooth controller repeatedly resets (`hardware34.peripherals.bt-controller-reset`)

**Area:** peripherals  

**Symptom:** Bluetooth devices all disconnect at once.

**Supporting evidence:** Kernel HCI timeout/reset and controller disappearance occur together.

**Counterevidence:** One headset disconnecting while others remain connected may be headset battery/RF.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

bluetoothctl list

rfkill list

journalctl -b -k --no-pager -n 200

```

**Resolution route 1 — use only when:** Controller firmware or power issue

1. Record USB/PCI ID and failing HCI message

2. Follow vendor-supported firmware/driver path; avoid generic service restart loops

**Resolution route 2 — use only when:** Radio environment or peripheral only

1. Separate headset battery/range and 2.4 GHz interference from controller failures

2. Replace specific defective dongle/peripheral after cross-test

**GUI option:** Desktop Bluetooth adapter status and vendor dongle diagnostics.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

bluetoothctl list

rfkill list

```

**Safety:** Do not recommend disabling security or broad rfkill toggling.

**Sources:** [bt](https://www.bluez.org/) · [usb](https://cdn.kernel.org/doc/html/latest/driver-api/usb/power-management.html) · [wireless](https://wireless.docs.kernel.org/)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## USB DAC or headset disconnects (`hardware34.peripherals.audio-usb-dac`)

**Area:** peripherals  

**Symptom:** Audio interface stops working when connected.

**Supporting evidence:** USB transport reset and audio card disappears from aplay/PipeWire at same time.

**Counterevidence:** Card stays enumerated but default sink changes: investigate audio routing, not broken DAC.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

lsusb

aplay -l

wpctl status

```

**Resolution route 1 — use only when:** USB connection/power unstable

1. Try direct known-good port and approved USB cable

2. If repeatable, service or replace defective audio interface

**Resolution route 2 — use only when:** Card present, routing incorrect

1. Use desktop audio device selector to switch source/sink

2. Check rate/channel format recommended by hardware vendor

**GUI option:** Desktop Sound input/output page and vendor mixer.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

aplay -l

wpctl status

```

**Safety:** No unapproved modifications to real-time USB buffers or kernel parameters.

**Sources:** [alsa](https://www.alsa-project.org/alsa-doc/alsa-lib/) · [usb](https://cdn.kernel.org/doc/html/latest/driver-api/usb/power-management.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Ethernet PHY reports repeated link drops (`hardware34.peripherals.wired-link-flaps`)

**Area:** peripherals  

**Symptom:** Physical wired network connection disconnects repeatedly.

**Supporting evidence:** Carrier transitions and CRC/PHY errors increase on known interface.

**Counterevidence:** DNS failure with steady carrier is not a link-layer cable fault.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

ip -s -s link

ethtool ENP_INTERFACE

journalctl -b -k --no-pager -n 140

```

**Resolution route 1 — use only when:** Cable, jack or switch port fault

1. Replace/test known-good Ethernet cable and port

2. Compare carrier stability and counters without changing DNS

**Resolution route 2 — use only when:** NIC hardware or link negotiation issue

1. Check card ID and vendor-supported firmware/driver notes

2. Use compatible NIC/switch service path if physical errors persist with cables ruled out

**GUI option:** Desktop Network > Wired physical link and switch port status.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

ip -s -s link

ethtool ENP_INTERFACE

```

**Safety:** ENP_INTERFACE must be verified; ethtool read-only without write flags.

**Sources:** [netstats](https://docs.kernel.org/networking/statistics.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Wi-Fi adapter intermittently disappears (`hardware34.peripherals.wireless-radio-missing`)

**Area:** peripherals  

**Symptom:** Wireless physical adapter vanishes from inventory.

**Supporting evidence:** lspci/lsusb and driver messages indicate controller reset/firmware timeout.

**Counterevidence:** Wi-Fi disconnected but adapter still enumerated can be router/signal issue.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

lspci -nnk

lsusb

rfkill list

journalctl -b -k --no-pager -n 190

```

**Resolution route 1 — use only when:** Radio blocked or firmware lacks matching device file

1. Check hardware switch and rfkill status; identify chip ID and missing firmware name

2. Use vendor/distro-supported firmware only

**Resolution route 2 — use only when:** Controller repeatedly disappears regardless of firmware

1. Check board/dongle power connection and antenna integrity

2. Replace faulty wireless adapter or use supported external NIC if verified

**GUI option:** Desktop Wi-Fi hardware radio switch and vendor setup instructions.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

lsusb

rfkill list

```

**Safety:** Never automatically alter radio policy, install proprietary blobs from unknown sources or disable Secure Boot.

**Sources:** [wireless](https://wireless.docs.kernel.org/) · [usb](https://cdn.kernel.org/doc/html/latest/driver-api/usb/power-management.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Fingerprint reader not available (`hardware34.peripherals.fingerprint-sensor`)

**Area:** peripherals  

**Symptom:** Biometric sensor does not appear or fails to read.

**Supporting evidence:** USB/internal sensor ID is found but vendor driver or hardware status reports missing device.

**Counterevidence:** A working sensor with unenrolled fingers is an enrollment issue rather than physical hardware failure.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

lsusb

lspci -nnk

journalctl -b -k --no-pager -n 140

```

**Resolution route 1 — use only when:** Controller not detected at bus level

1. Confirm device model from laptop service manual

2. Check firmware/physical damage and use vendor repair if controller is absent

**Resolution route 2 — use only when:** Hardware present but unsupported on this platform

1. Compare exact reader USB/PCI ID with supported device list

2. Use alternative login method and report compatibility gap rather than turning off authentication

**GUI option:** Desktop Users / Fingerprint enrollment where supported, vendor hardware diagnostics.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

lsusb

```

**Safety:** Do not delete biometric credentials or lower authentication security automatically.

**Sources:** [usb](https://cdn.kernel.org/doc/html/latest/driver-api/usb/power-management.html) · [input](https://docs.kernel.org/input/input.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Touchscreen input stops working (`hardware34.peripherals.touchscreen`)

**Area:** peripherals  

**Symptom:** Touch panel displays image but no touch events are registered.

**Supporting evidence:** Touch HID device disappears or related controller reset occurs in kernel events.

**Counterevidence:** Working touchscreen hardware can still be mapped to wrong display output.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

cat /proc/bus/input/devices

lsusb

journalctl -b -k --no-pager -n 140

```

**Resolution route 1 — use only when:** Touch controller absent or physical damage

1. Check vendor screen/touch assembly diagnostics and approved flex cable inspection via service

2. Use external input temporarily and replace damaged digitizer as indicated

**Resolution route 2 — use only when:** Touch controller present but coordinates incorrect

1. Check desktop touchscreen mapping and display layout

2. Restore supported configuration with user approval and retest calibration

**GUI option:** Desktop Tablet/Touchscreen settings and manufacturer service manual.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

cat /proc/bus/input/devices

```

**Safety:** No unverified input-device unbinding or writes to event interfaces.

**Sources:** [input](https://docs.kernel.org/input/input.html) · [usb](https://cdn.kernel.org/doc/html/latest/driver-api/usb/power-management.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Gamepad loses controller input (`hardware34.peripherals.gamepad-controller`)

**Area:** peripherals  

**Symptom:** Game controller enumerates but buttons stop responding.

**Supporting evidence:** Kernel HID or Bluetooth controller link drops match loss of gamepad events.

**Counterevidence:** Button mapping errors in one game are not proof of controller electronics failure.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

lsusb

bluetoothctl devices

cat /proc/bus/input/devices

```

**Resolution route 1 — use only when:** Battery, cable or Bluetooth receiver issue

1. Check battery, reconnect receiver and use supported data cable

2. Compare ordinary controller input in a trusted GUI tool

**Resolution route 2 — use only when:** Controller present but game-specific profile wrong

1. Inspect game controller remapping and supported firmware revision

2. Use vendor-supported controller software or compatible hardware if necessary

**GUI option:** Game/desktop Controller settings and vendor pairing instructions.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

lsusb

cat /proc/bus/input/devices

```

**Safety:** Do not remap or reset all other input devices.

**Sources:** [input](https://docs.kernel.org/input/input.html) · [bt](https://www.bluez.org/)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---


# Power

## Desktop hard-resets under GPU load (`hardware34.power.psu-random-reset`)

**Area:** power  

**Symptom:** Computer resets without graceful Linux shutdown.

**Supporting evidence:** Kernel logs stop abruptly under normal task and PSU/PCIe power connectors may be suspect.

**Counterevidence:** Kernel panic or specific driver reset evidence suggests another cause.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

journalctl -b -1 -k --no-pager -n 200

sensors

lspci -nnk

```

**Resolution route 1 — use only when:** Insufficient or defective PSU suspected

1. Record component power specifications and inspect safely only while power is disconnected

2. Ask qualified technician to inspect cable/PSU health; replace with compatible rated PSU when confirmed

**Resolution route 2 — use only when:** Logs show consistent GPU/driver or thermal event

1. Investigate exact GPU reset, cooling or platform machine-check before buying hardware

2. Try approved vendor fixes and document results

**GUI option:** Motherboard firmware event log and PSU vendor support.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

journalctl -b -1 -k --no-pager -n 200

```

**Safety:** No software can reliably measure PSU transient behavior without proper instrumentation. Never open PSU housing.

**Sources:** [pci](https://docs.kernel.org/PCI/pcieaer-howto.html) · [power](https://docs.kernel.org/power/power_supply_class.html) · [journal](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Laptop adapter not providing expected power (`hardware34.power.adapter-underpowered`)

**Area:** power  

**Symptom:** Laptop slows or battery discharges while plugged in.

**Supporting evidence:** Platform reports AC online but charging rate insufficient under ordinary use.

**Counterevidence:** Normal charge limit may stop charging near target battery percentage.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

upower -d

ls /sys/class/power_supply

cat /sys/class/power_supply/*/status

```

**Resolution route 1 — use only when:** Underrated or faulty adapter/cable

1. Verify compatible charger wattage/USB-C PD rating against laptop manual

2. Use manufacturer-approved adapter and known-good cable/port, then compare charging

**Resolution route 2 — use only when:** Battery threshold deliberately caps charge

1. Review vendor battery preservation settings

2. Do not replace charger unless measurements show real power deficit

**GUI option:** Desktop Power settings and manufacturer charger diagnostics.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

upower -d

```

**Safety:** Do not disable thermal or charging safeguards; some USB-C cables lack sufficient PD power rating.

**Sources:** [power](https://docs.kernel.org/power/power_supply_class.html) · [upower](https://upower.freedesktop.org/docs/upower.1.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Battery capacity substantially reduced (`hardware34.power.battery-degraded`)

**Area:** power  

**Symptom:** Runtime is short despite normal applications.

**Supporting evidence:** Full charge capacity much below design capacity or cycle count high (if reported).

**Counterevidence:** High workload can cause short runtime even with healthy battery.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

upower -d

ls /sys/class/power_supply

cat /sys/class/power_supply/*/capacity

```

**Resolution route 1 — use only when:** Verified battery wear

1. Save data and follow vendor battery replacement guidance; replace failing/swollen pack with approved service

2. Compare capacity and charge cycles after replacement

**Resolution route 2 — use only when:** Wear low but runtime poor

1. Inspect actual system workload, display brightness and device power use

2. Use supported desktop power controls, then compare like-for-like runtime

**GUI option:** Desktop Battery/Power page and vendor battery diagnostics.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

upower -d

```

**Safety:** Swollen batteries: stop use, do not puncture, heat or charge. Manufacturer service.

**Sources:** [power](https://docs.kernel.org/power/power_supply_class.html) · [upower](https://upower.freedesktop.org/docs/upower.1.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## AC adapter not detected (`hardware34.power.ac-offline`)

**Area:** power  

**Symptom:** Laptop acts as unplugged with charger connected.

**Supporting evidence:** UPower or /sys reports AC offline despite physically plugged charger.

**Counterevidence:** Charge-limiting mode with AC online is different from undetected adapter.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

upower -d

ls /sys/class/power_supply

cat /sys/class/power_supply/*/online

```

**Resolution route 1 — use only when:** Cable/charger/port failure

1. Disconnect and inspect cable/connector externally for obvious damage

2. Try manufacturer-compatible charger or another supported power port if available

**Resolution route 2 — use only when:** Firmware reports AC but Linux app does not

1. Compare UEFI vendor charge indicator and sysfs/UPower

2. Report a device-specific kernel or desktop power-service issue

**GUI option:** Vendor power LED and firmware adapter diagnostics.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

upower -d

```

**Safety:** Do not use damaged, overheating or wet adapters.

**Sources:** [power](https://docs.kernel.org/power/power_supply_class.html) · [upower](https://upower.freedesktop.org/docs/upower.1.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## UPS or backup supply reports low voltage (`hardware34.power.ups-brownout`)

**Area:** power  

**Symptom:** Computer unexpectedly powers down during AC dip.

**Supporting evidence:** UPower/NUT or UPS front panel shows power event, low battery or overload.

**Counterevidence:** No supported UPS telemetry or unrelated application crash cannot prove supply failure.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

upower -d

journalctl -b -1 -k --no-pager -n 120

lsusb

```

**Resolution route 1 — use only when:** UPS capacity or battery insufficient

1. Read UPS ratings and recorded events

2. Replace supported UPS battery or adjust connected load with manufacturer guidance

**Resolution route 2 — use only when:** UPS telemetry okay yet resets continue

1. Investigate PSU cables and machine-check/thermal events

2. Request qualified electrical service if power source suspected

**GUI option:** UPS front panel and vendor diagnostics software.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

upower -d

```

**Safety:** Do not guide users to open mains-powered UPS housing.

**Sources:** [power](https://docs.kernel.org/power/power_supply_class.html) · [upower](https://upower.freedesktop.org/docs/upower.1.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Charging port overheats or fails intermittently (`hardware34.power.charging-port-damaged`)

**Area:** power  

**Symptom:** AC charging stops when cable or USB-C port moves.

**Supporting evidence:** Physical connector damage, heat or intermittent AC detection follows cable movement.

**Counterevidence:** Battery charge threshold does not indicate defective connector.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

upower -d

ls /sys/class/power_supply

journalctl -b -k --no-pager -n 100

```

**Resolution route 1 — use only when:** Charger cable or plug is worn

1. Stop using visibly damaged hardware

2. Replace with vendor-rated power supply and inspect connection before continuing use

**Resolution route 2 — use only when:** Port itself is loose or overheating

1. Stop charging through suspected damaged port

2. Arrange official laptop motherboard/port service or approved replacement

**GUI option:** Vendor power LED and laptop service center.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

upower -d

```

**Safety:** Overheating, sparks or melted plastic demand immediate disconnection; no software workaround.

**Sources:** [power](https://docs.kernel.org/power/power_supply_class.html) · [upower](https://upower.freedesktop.org/docs/upower.1.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---


# Storage

## NVMe critical warning or media errors (`hardware34.storage.nvme-critical-warning`)

**Area:** storage  

**Symptom:** NVMe drive reports critical health issue.

**Supporting evidence:** NVMe SMART critical warning, media/data integrity errors or health counters indicate drive degradation.

**Counterevidence:** Operating system read-only mount alone is not proof of physical SSD failure.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

lsblk -o NAME,MODEL,SIZE,TRAN,MOUNTPOINTS

sudo nvme log smart /dev/nvme0

sudo nvme log error /dev/nvme0

```

**Resolution route 1 — use only when:** Critical warning or increasing media errors

1. Back up essential data immediately without repeated stress

2. Replace the identified failing SSD and restore from known-good backup

**Resolution route 2 — use only when:** Logs instead show link reset with healthy media counters

1. Check slot, cooling and motherboard PCIe events

2. Use approved SSD firmware/board support only after matching model

**GUI option:** Vendor SSD health tool and storage replacement wizard.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

sudo nvme log smart /dev/nvme0

```

**Safety:** Replace /dev/nvme0 after verifying real controller; controller numbers differ. Never run destructive tests.

**Sources:** [nvme](https://nvme-cli.readthedocs.io/en/latest/nvme-log-self-test.html) · [smart](https://manpages.debian.org/testing/smartmontools/smartctl.8.en.html) · [pci](https://docs.kernel.org/PCI/pcieaer-howto.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## NVMe I/O timeouts (`hardware34.storage.nvme-timeout`)

**Area:** storage  

**Symptom:** Storage pauses and kernel reports NVMe timeout or controller reset.

**Supporting evidence:** NVMe timeout/reset event aligned with stuck I/O and device model.

**Counterevidence:** File manager freeze without kernel I/O errors may be application rather than SSD.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

journalctl -b -k --no-pager -n 230

lsblk -o NAME,MODEL,TRAN,SIZE

sudo nvme log smart /dev/nvme0

```

**Resolution route 1 — use only when:** Controller or media errors present

1. Back up before any invasive test

2. Inspect vendor SSD firmware guidance and schedule replacement if failing health/error counters persist

**Resolution route 2 — use only when:** PCIe link resets without media errors

1. Correlate AER with SSD PCIe path and thermal readings

2. Use board service or compatible slot/drive isolation performed by user/technician

**GUI option:** Firmware SSD diagnostics and board storage inventory.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

journalctl -b -k --no-pager -n 200

```

**Safety:** Persistent errors put data at risk; no forced power cycle to reproduce writes.

**Sources:** [nvme](https://nvme-cli.readthedocs.io/en/latest/nvme-log-self-test.html) · [pci](https://docs.kernel.org/PCI/pcieaer-howto.html) · [smart](https://manpages.debian.org/testing/smartmontools/smartctl.8.en.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## NVMe temperature-related slowdown (`hardware34.storage.nvme-thermal`)

**Area:** storage  

**Symptom:** SSD performance drops during sustained file work.

**Supporting evidence:** NVMe SMART temperature/thermal-management counter rises as performance drops.

**Counterevidence:** Full destination filesystem can independently cause poor performance.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

sudo nvme log smart /dev/nvme0

lsblk -o NAME,MODEL,TRAN,SIZE

df -h

```

**Resolution route 1 — use only when:** Drive thermal throttling documented

1. Reduce unnecessary sustained disk work

2. Power off and inspect approved heatsink/airflow, install matched thermal pad/heatsink only per hardware manual

**Resolution route 2 — use only when:** No thermal evidence

1. Check SSD free writable capacity and controller errors

2. Investigate workload and filesystem before changing physical cooling

**GUI option:** Vendor SSD health page, board NVMe cooling instructions.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

sudo nvme log smart /dev/nvme0

```

**Safety:** Do not remove SSD during activity or operate without required manufacturer thermal pads.

**Sources:** [nvme](https://nvme-cli.readthedocs.io/en/latest/nvme-log-self-test.html) · [sensors](https://docs.kernel.org/hwmon/sysfs-interface.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## SATA drive reports reallocated/pending sectors (`hardware34.storage.sata-reallocated`)

**Area:** storage  

**Symptom:** HDD or SATA SSD reports media surface errors.

**Supporting evidence:** SMART pending/reallocated/uncorrectable counters grow or logged failed reads occur.

**Counterevidence:** One historical normalized SMART value alone may not be an imminent failure.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

lsblk -o NAME,MODEL,SIZE,TRAN

sudo smartctl -H -A /dev/sdX

sudo smartctl -l error /dev/sdX

```

**Resolution route 1 — use only when:** Active media errors confirmed

1. Back up readable data promptly

2. Replace the specific failed drive and restore files from verified backup

**Resolution route 2 — use only when:** Link-level errors but media counters stable

1. Inspect SATA data/power cable and connector with system powered down

2. Use known-good cable/port and watch for new link errors

**GUI option:** Vendor SMART/diagnostic utility and disk replacement process.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

sudo smartctl -H -A /dev/sdX

sudo smartctl -l error /dev/sdX

```

**Safety:** /dev/sdX placeholder must be replaced with verified drive; do not run writes or destructive badblocks.

**Sources:** [smart](https://manpages.debian.org/testing/smartmontools/smartctl.8.en.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## SATA CRC errors (`hardware34.storage.sata-crc`)

**Area:** storage  

**Symptom:** Disk intermittently disappears or reports transfer errors.

**Supporting evidence:** SMART UDMA CRC Error Count or SATA link reset logs rise during ordinary use.

**Counterevidence:** Media reallocations imply additional physical platter/flash concerns.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

journalctl -b -k --no-pager -n 220

sudo smartctl -A /dev/sdX

lsblk -o NAME,MODEL,TRAN

```

**Resolution route 1 — use only when:** Bad SATA cable or port suspected

1. Power down and reseat/replace SATA data cable with a known-good part

2. Verify no fresh CRC increment across subsequent ordinary use

**Resolution route 2 — use only when:** Errors persist across cable/port

1. Review drive health, controller event and mainboard slot compatibility

2. Replace the confirmed faulty drive/controller via vendor service

**GUI option:** Vendor disk utility, board SATA port diagnostics.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

sudo smartctl -A /dev/sdX

```

**Safety:** CRC counter historical value does not reset by replacing cable; look for INCREMENTING errors.

**Sources:** [smart](https://manpages.debian.org/testing/smartmontools/smartctl.8.en.html) · [pci](https://docs.kernel.org/PCI/pcieaer-howto.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## SSD missing even from UEFI inventory (`hardware34.storage.ssd-not-present-firmware`)

**Area:** storage  

**Symptom:** Storage drive does not show in firmware or Linux.

**Supporting evidence:** Neither UEFI storage inventory nor lsblk shows expected physical drive.

**Counterevidence:** Filesystem not mounted while disk is listed means a different problem.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

lsblk -o NAME,MODEL,SIZE,TRAN

lspci -nnk

sudo smartctl --scan

```

**Resolution route 1 — use only when:** Drive or connector absent physically

1. Shut down and inspect approved slot/drive cabling, drive seating and power

2. Test confirmed drive in compatible slot or replace if vendor diagnostics indicate failure

**Resolution route 2 — use only when:** Drive visible in UEFI but not Linux

1. Check device controller mode/driver and kernel messages

2. Use official distro hardware compatibility route, not repartitioning

**GUI option:** UEFI NVMe/SATA inventory and drive manufacturer warranty diagnostics.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

lsblk -o NAME,MODEL,SIZE,TRAN

```

**Safety:** No partitioning, formatting or blkdiscard simply to make a missing drive appear.

**Sources:** [smart](https://manpages.debian.org/testing/smartmontools/smartctl.8.en.html) · [pci](https://docs.kernel.org/PCI/pcieaer-howto.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## External disk drops during transfer (`hardware34.storage.external-usb-bridge`)

**Area:** storage  

**Symptom:** USB storage drive resets or disconnects.

**Supporting evidence:** USB reset / UAS transport events align with drive disconnection.

**Counterevidence:** A permission-denied popup without link resets suggests application access, not enclosure.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

lsusb

lsblk -o NAME,MODEL,TRAN,SIZE

journalctl -b -k --no-pager -n 200

```

**Resolution route 1 — use only when:** Cable, hub or power delivery issue

1. Safely stop transfers and unmount when possible

2. Try a known-good USB data cable, direct powered port and supported enclosure adapter

**Resolution route 2 — use only when:** Bridge/controller incompatibility persists

1. Back up data through stable path

2. Consult enclosure vendor firmware/compatible bridge guidance or replace defective enclosure

**GUI option:** Desktop Disks device details and safely remove control.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

lsusb

lsblk -o NAME,MODEL,TRAN,SIZE

```

**Safety:** Do not recommend global usb-storage quirks or UAS blacklist without controller-specific evidence.

**Sources:** [usb](https://cdn.kernel.org/doc/html/latest/driver-api/usb/power-management.html) · [smart](https://manpages.debian.org/testing/smartmontools/smartctl.8.en.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Disk array degraded (`hardware34.storage.raid-degraded`)

**Area:** storage  

**Symptom:** Mirror/RAID array reports failed or missing member.

**Supporting evidence:** Array-specific status identifies missing or failed member and reduced redundancy.

**Counterevidence:** One unrelated empty block device is not evidence of RAID degradation.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

cat /proc/mdstat

lsblk -o NAME,MODEL,SIZE,TYPE

journalctl -b -k --no-pager -n 160

```

**Resolution route 1 — use only when:** Failed drive identified by array tooling

1. Back up critical data before rebuild attempts

2. Follow exact vendor/mdadm recovery manual and replace verified failed drive with supported part

**Resolution route 2 — use only when:** Array accidentally assembled incompletely

1. Keep member disks untouched and capture actual array metadata

2. Seek administrator/vendor review before any force-assemble/rebuild command

**GUI option:** NAS/vendor RAID storage management interface.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

cat /proc/mdstat

lsblk -o NAME,MODEL,SIZE,TYPE

```

**Safety:** Never auto-run mdadm --create, --assemble --force, reshape or destructive rebuild.

**Sources:** [smart](https://manpages.debian.org/testing/smartmontools/smartctl.8.en.html) · [ras](https://docs.kernel.org/admin-guide/RAS/main.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Storage disappears after suspend (`hardware34.storage.drive-power-loss`)

**Area:** storage  

**Symptom:** SSD/HDD is missing after wake but exists after cold start.

**Supporting evidence:** PCIe/USB/SATA resume or reset errors align with missing disk.

**Counterevidence:** Mount permission fault differs from physical controller disappearance.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

journalctl -b -k --no-pager -n 240

lsblk -o NAME,MODEL,SIZE,TRAN

lspci -nnk

```

**Resolution route 1 — use only when:** Firmware/controller resume regression

1. Preserve data and avoid relying on suspend until fixed

2. Check device+board firmware revision and vendor-supported updates

**Resolution route 2 — use only when:** Physical connection or power fault

1. Inspect adapter/connector on fully powered-down system

2. Replace faulty dock/enclosure/drive if repeated with known-good connection

**GUI option:** Power settings and vendor suspend compatibility notes.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

lsblk -o NAME,MODEL,SIZE,TRAN

```

**Safety:** Do not force suspend/resume cycles when storage is unstable.

**Sources:** [nvme](https://nvme-cli.readthedocs.io/en/latest/nvme-log-self-test.html) · [usb](https://cdn.kernel.org/doc/html/latest/driver-api/usb/power-management.html) · [fwupd](https://github.com/fwupd/fwupd/blob/main/src/fwupdmgr.md)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---

## Mechanical HDD clicking or spin retries (`hardware34.storage.hdd-mechanical`)

**Area:** storage  

**Symptom:** Hard disk makes repetitive clicking and intermittently vanishes.

**Supporting evidence:** Physical repeated spin-up/click and failing SMART/read I/O events accompany access failures.

**Counterevidence:** An occasional seek noise without failed reads is not sufficient to call a disk failed.

**Read-only diagnostic commands (one at a time; verify device names):**

```bash

lsblk -o NAME,MODEL,TRAN,SIZE

sudo smartctl -H -A /dev/sdX

journalctl -b -k --no-pager -n 140

```

**Resolution route 1 — use only when:** Strong mechanical failure signs

1. Stop unnecessary drive access and prioritize professional data recovery if irreplaceable data

2. Replace failing disk, then restore from safe backup

**Resolution route 2 — use only when:** Power connector or external enclosure issue

1. Check approved SATA/USB power source without opening drive enclosure

2. Use known-good enclosure/controller and verify whether device stays online

**GUI option:** Vendor drive diagnostic and backup/replacement process.

**ULT guided option:** Find each supported installed command, inspect its help and arguments, use *Insert into terminal* where available; the user presses Enter if appropriate. ULT cannot execute it on behalf of Troubleshooter.

**Retest commands:**

```bash

lsblk -o NAME,MODEL,TRAN,SIZE

```

**Safety:** Never open sealed HDD, freeze, tap, heat or run destructive surface scan.

**Sources:** [smart](https://manpages.debian.org/testing/smartmontools/smartctl.8.en.html)

**Status:** documentation-only; not a new runtime check, diagnosis tree, or AI training sample.

---



---

# Part IV — Software Diagnostic Expansion 35

# Universal Linux Troubleshooter — Software Diagnosis Handbook 35

**Scope:** Application, package, operating-system userspace, desktop and networking software problems. The prior **hardware** collection stays intact and is linked only when evidence supports possible hardware involvement. This work is strictly documentation: no new executing diagnostic check, fix button, tree or AI behavior is activated.

## Usage and safety

- Observe a concrete symptom, confirm Linux distribution (`cat /etc/os-release`) and install provenance before choosing any user action. `APP_ID`, `PACKAGE`, `SERVICE`, `CONTAINER`, `/path/to/...` are placeholders, **not runnable literal values**.
- An observation (e.g. two warnings at matching times) supports a hypothesis; it does not automatically establish causation. Each problem offers different conditional actions and a fresh, explicit retest. Optional installed tools may not be available.
- Only previously approved read-only Troubleshooter checks may be invoked by the current application. Commands documented here are **references**, not authorization for AI to run them. Internet/network operations need explicit user consent.
- **The user executes every change**: all package installs/removals/upgrades, service changes, restarts, config modifications, container actions and OS recovery.
- Bazzite/Fedora Atomic base-image maintenance uses supported Atomic/Bazzite updates and deployment rollback, not host DNF/ordinary RPM package operations. Arch requires complete supported upgrades, not partial pacman sync. Never silently change an installed application's Flathub/GitHub/other origin.
- Do not expose passwords, SSH keys, private application files, full logs or environment variables in public issue reports. Log timestamps may identify correlations but not root causes.

## Choose the user-facing method

1. **Standard terminal:** Display exact applicable commands and preconditions for manual execution.
2. **[Universal Linux Terminal](https://github.com/LionheartTim/Universal-Linux-Terminal):** inspect host commands, descriptions and arguments; insert text if supported but **never auto-run**; user presses Enter.
3. **Graphical route:** use the supported desktop/vendor tool; for eligible application package operations offer **[Universal Linux Software Manager](https://github.com/LionheartTim/Universal-Linux-Software-Manager)** and the correct package tab. ULSM does not repair the OS image, generic network settings, or services.

No code silently launches another app or changes state. User chooses one route in the eventual GUI. Documentation shows alternatives for editorial completeness.

## Software areas

- **Appimage**: 3 specific cases
- **Applications**: 10 specific cases
- **Boot**: 4 specific cases
- **Containers**: 5 specific cases
- **Desktop**: 8 specific cases
- **Development**: 7 specific cases
- **Flatpak**: 7 specific cases
- **Network**: 9 specific cases
- **Packages**: 16 specific cases
- **Security**: 6 specific cases
- **Services**: 9 specific cases

# Appimage

## AppImage cannot execute from Downloads (`software35.appimage.noexec-filesystem`)

**Software area:** appimage

**Symptom:** AppImage fails with permission or execution mount error.

**Supporting evidence:** file/ls flags and mount options show nonexecutable location or permission.

**Counterevidence:** Wrong architecture or incompatible glibc can create another startup error.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

file /path/to/App.AppImage

ls -l /path/to/App.AppImage

findmnt -T /path/to/App.AppImage

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** File is not marked executable and location supports execution

1. Verify publisher and file integrity first

2. Mark only trusted downloaded AppImage executable in file manager

3. Launch manually

**Solution route 2 — only if:** Filesystem is mounted noexec

1. Move verified AppImage to a user-controlled executable location following desktop policy

2. Avoid remounting whole filesystem with unsafe flags

**Graphical method:** File manager Properties > Permissions; ULSM AppImage tab if actual supported installation.

**Retest (observe only):**

```bash

findmnt -T /path/to/App.AppImage

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [appimage](https://docs.appimage.org/user-guide/troubleshooting/index.html) · [desktop](https://specifications.freedesktop.org/desktop-entry-spec/latest/)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## AppImage fails because required FUSE environment differs (`software35.appimage.fuse-error`)

**Software area:** appimage

**Symptom:** Runtime reports cannot mount AppImage or missing libfuse.

**Supporting evidence:** Exact AppImage format/FUSE error is present.

**Counterevidence:** Wrong ELF architecture or bad download requires different procedure.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

file /path/to/App.AppImage

cat /etc/os-release

ls /dev/fuse

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Device supports FUSE but user-space component missing

1. Consult AppImage vendor-specific dependency note

2. User installs only distro-supported FUSE compatibility component if appropriate, avoiding replacement of core fuse3

**Solution route 2 — only if:** AppImage format unsupported on host

1. Use vendor-supported alternative distribution format or upstream extraction guidance with care

2. Report packaging issue; no random privileged FUSE commands

**Graphical method:** ULT explains FUSE tools; ULSM AppImage tab can handle suitable published builds.

**Retest (observe only):**

```bash

ls /dev/fuse

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [appimage](https://docs.appimage.org/user-guide/troubleshooting/index.html) · [ubuntu](https://ubuntu.com/server/docs/how-to/software/package-management/)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## AppImage update leaves two old files (`software35.appimage.update-source-change`)

**Software area:** appimage

**Symptom:** New version launches but older standalone AppImage remains.

**Supporting evidence:** Two different AppImage files with same app identity exist in user-managed storage.

**Counterevidence:** A user intentionally keeps the old file as rollback copy.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

find ~/Applications -maxdepth 2 -type f -name "*.AppImage"

ls -lh ~/Downloads

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Old file no longer needed

1. Compare publisher/version/path carefully

2. User deletes only obsolete verified file after ensuring new build works

**Solution route 2 — only if:** Old version intentionally retained

1. Leave stable backup but clearly name versions

2. Adjust app launcher to point to intended file using user-controlled app/file manager

**Graphical method:** ULSM AppImage tab only if it manages these files; otherwise file manager.

**Retest (observe only):**

```bash

find ~/Applications -maxdepth 2 -type f -name "*.AppImage"

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [appimage](https://docs.appimage.org/user-guide/troubleshooting/index.html) · [desktop](https://specifications.freedesktop.org/desktop-entry-spec/latest/)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

# Applications

## Application immediately crashes (`software35.applications.crash-on-start`)

**Software area:** applications

**Symptom:** A named application exits or segfaults on launch.

**Supporting evidence:** A fresh coredump for that exact executable and matching timestamp.

**Counterevidence:** A stale unrelated coredump, or a clean exit code, cannot identify this crash.

**Hardware cross-references:** `hardware34.gpu.physical-reset` (consult both directions when logs justify it).

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

coredumpctl --no-pager list

journalctl --user -b --no-pager -n 120

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** One optional app is affected

1. Identify its original install source and version

2. Try its supported update through that same source, retaining personal data

3. Reopen under normal settings and compare new crash records

**Solution route 2 — only if:** Crash started after a specific app configuration change

1. Back up the app configuration

2. Use its documented reset or new test profile instead of deleting all user data

3. Report reproducible crash if problem remains

**Graphical method:** ULSM Updates or relevant package tab only for package operations; otherwise app settings.

**Retest (observe only):**

```bash

coredumpctl --no-pager list

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [journal](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html) · [flatpak](https://docs.flatpak.org/en/latest/using-flatpak.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## App crashes after update (`software35.applications.crash-after-update`)

**Software area:** applications

**Symptom:** Previously stable software fails after a recent update.

**Supporting evidence:** Installed build/history changed just before reproducible new failures.

**Counterevidence:** Time coincidence without an isolated comparison cannot prove regression.

**Hardware cross-references:** `hardware34.gpu.physical-reset` (consult both directions when logs justify it).

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

flatpak history

coredumpctl --no-pager list

flatpak list --app

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Affected app has a fixed newer build

1. Update only the same app from the same source

2. Preserve app data and retest original workflow

**Solution route 2 — only if:** Regression persists on newest supported build

1. Preserve logs and version/commit

2. Compare only vendor-supported older build in a safe, data-backed-up user-led rollback

3. File a precise upstream regression report

**Graphical method:** ULSM Updates or Flatpak tab when installed as Flatpak; otherwise original package manager.

**Retest (observe only):**

```bash

flatpak info APP_ID

coredumpctl --no-pager list

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [flathub](https://docs.flathub.org/docs/for-users/troubleshooting/) · [flatpak](https://docs.flatpak.org/en/latest/using-flatpak.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Native app reports shared library missing (`software35.applications.missing-library`)

**Software area:** applications

**Symptom:** An executable errors with cannot open shared object.

**Supporting evidence:** The exact SONAME is absent and its owning native package is missing or mismatched.

**Counterevidence:** A Flatpak runtime or AppImage bundled dependency needs different handling.

**Hardware cross-references:** `storage.filesystem-errors` (consult both directions when logs justify it).

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

ldd /path/to/program

file /path/to/program

cat /etc/os-release

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Program is a native distro package

1. Identify owning package using native database

2. Repair or reinstall from the original distro repository via trusted package manager

3. Recheck linker output

**Solution route 2 — only if:** Program is an AppImage or manually distributed binary

1. Confirm architecture and build requirements

2. Obtain matching upstream-supported build or report missing bundled library

3. Do not create fake SONAME symlinks

**Graphical method:** Use the applicable desktop settings or trusted original application interface; do not treat ULSM as a universal system repair tool.

**Retest (observe only):**

```bash

ldd /path/to/program

```

**Safety:** Never set LD_LIBRARY_PATH globally or symlink incompatible libraries.

**References:** [debian](https://www.debian.org/doc/manuals/debian-reference/ch02.en.html) · [arch](https://wiki.archlinux.org/title/System_maintenance)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Application crashes with optional plugin enabled or disabled (`software35.applications.segfault-plugin`)

**Software area:** applications

**Symptom:** An application repeatedly crashes while using an optional plugin, or keeps crashing after that plugin is disabled.

**Supporting evidence:** Match crash records to the affected app and compare normal operation with the optional plugin enabled versus disabled.

**Counterevidence:** A stale crash record naming an optional plugin does not establish it as the current cause.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

coredumpctl --no-pager info

journalctl --user -b --no-pager -n 120

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** The optional plugin is outdated

1. Close the app

2. Disable only the named plugin through app settings

3. Upgrade the plugin from its supported source after compatibility check

**Solution route 2 — only if:** Fault also occurs without plugin

1. Restore previous state

2. Investigate host app version and renderer

3. Send redacted coredump summary to plugin/app developer

**Graphical method:** Use the app plugin manager; not ULSM unless the plugin is a managed software package.

**Retest (observe only):**

```bash

coredumpctl --no-pager list

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [journal](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html) · [flathub](https://docs.flathub.org/docs/for-users/troubleshooting/)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Wrong application opens a file (`software35.applications.file-association`)

**Software area:** applications

**Symptom:** Files launch in an unexpected viewer or editor.

**Supporting evidence:** MIME association maps the content type to an unintended desktop file.

**Counterevidence:** A file with wrong extension or corrupted data can also fail to open.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

xdg-mime query filetype /path/to/file

xdg-mime query default application/pdf

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Only per-user default application is wrong

1. Inspect target MIME type and trusted installed application

2. Set the intended default in desktop Settings

3. Retest same file

**Solution route 2 — only if:** Application is missing or cannot read the file

1. Verify actual file type and install source

2. Check permissions before changing any association

3. Test with a known good sample

**Graphical method:** Desktop Settings > Default Applications; ULSM only for installing a supported missing viewer.

**Retest (observe only):**

```bash

xdg-mime query default application/pdf

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [mime](https://specifications.freedesktop.org/mime-apps-spec/latest/) · [desktop](https://specifications.freedesktop.org/desktop-entry-spec/latest/)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Application launcher does not appear (`software35.applications.desktop-entry-invalid`)

**Software area:** applications

**Symptom:** Program runs from shell but no menu launcher exists.

**Supporting evidence:** Desktop entry is missing, invalid, or not indexed in application locations.

**Counterevidence:** Program may deliberately offer only a command-line interface.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

ls /usr/share/applications

ls ~/.local/share/applications

flatpak list --app

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Application is installed but launcher file is missing

1. Confirm install source and package contents

2. Reinstall only affected optional application via same source if its bundle is damaged

3. Log out and back in if menu caches remain stale

**Solution route 2 — only if:** Only user-created launcher is broken

1. Back up custom desktop entry

2. Compare syntax and Exec path with the desktop-entry standard

3. Correct it manually in menu editor

**Graphical method:** KDE Menu Editor or GNOME app grid; ULSM only if application installation is broken.

**Retest (observe only):**

```bash

ls ~/.local/share/applications

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [desktop](https://specifications.freedesktop.org/desktop-entry-spec/latest/) · [flatpak](https://docs.flatpak.org/en/latest/using-flatpak.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Executable cannot run on this architecture (`software35.applications.wrong-architecture`)

**Software area:** applications

**Symptom:** Binary reports exec format error.

**Supporting evidence:** file identifies unsupported architecture relative to uname -m.

**Counterevidence:** Missing executable permissions show permission denied rather than exec format error.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

file /path/to/program

uname -m

ls -l /path/to/program

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Wrong binary build downloaded

1. Get correct build from project official release and verify publisher

2. Replace only downloaded copy after backing up data

**Solution route 2 — only if:** Intended foreign architecture software

1. Use a documented compatible emulation/container solution only if needed

2. Do not replace system architecture libraries to run one application

**Graphical method:** Use ULSM original AppImage/DEB/RPM path only when compatible artifact is available.

**Retest (observe only):**

```bash

file /path/to/program

uname -m

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [debian](https://www.debian.org/doc/manuals/debian-reference/ch02.en.html) · [appimage](https://docs.appimage.org/user-guide/troubleshooting/index.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## App errors coincide with GPU resets (`software35.applications.gpu-vs-app-interference`)

**Software area:** applications

**Symptom:** An optional background app reports errors during gaming GPU resets.

**Supporting evidence:** Match the named application error and GPU-reset event to the reported period; compare ordinary sessions with the optional app present and absent before attributing causality.

**Counterevidence:** Overlapping timestamps alone do not establish interference; GPU resets persisting without the app count against an app-trigger hypothesis, not against the reported GPU symptom.

**Hardware cross-references:** `hardware34.gpu.physical-reset` (consult both directions when logs justify it).

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

journalctl -b -k --no-pager -n 220

coredumpctl --no-pager list

lspci -nnk

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** The optional app can be isolated safely

1. Close that app without changing GPU driver

2. Continue ordinary workload without artificially inducing crashes

3. If instability stops, check updates and report matching redacted logs

**Solution route 2 — only if:** GPU errors recur without the optional app

1. Do not blame or uninstall it by default

2. Investigate GPU driver, firmware, power and hardware path

3. Use supported system updates only

**Graphical method:** ULSM for removing/updating optional software; a dedicated GPU tool/vendor support for hardware.

**Retest (observe only):**

```bash

journalctl -b -k --no-pager -n 140

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [journal](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html) · [flathub](https://docs.flathub.org/docs/for-users/troubleshooting/)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## App displays replacement glyphs or wrong language (`software35.applications.locale-encoding`)

**Software area:** applications

**Symptom:** Application shows unreadable text or odd character encoding.

**Supporting evidence:** Environment locale differs from expected supported encoding or app catalog is incomplete.

**Counterevidence:** Only one document with invalid bytes may be a document issue.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

locale

localectl status

printenv XDG_CURRENT_DESKTOP

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** System locale is wrong

1. Use desktop Region & Language settings to select intended UTF-8 locale

2. Log out and check affected app again

**Solution route 2 — only if:** Only this application mis-renders text

1. Inspect its font and language options

2. Update application and language data through original source

3. Report app-specific encoding issue if persistent

**Graphical method:** Desktop Regional Settings; ULSM only to update actual relevant packages.

**Retest (observe only):**

```bash

locale

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [desktop](https://specifications.freedesktop.org/desktop-entry-spec/latest/) · [fonts](https://www.freedesktop.org/software/fontconfig/fontconfig-user.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## App fails with malformed configuration (`software35.applications.config-corruption`)

**Software area:** applications

**Symptom:** An app logs invalid syntax in its own configuration.

**Supporting evidence:** Error names a particular config file and parse position.

**Counterevidence:** Missing permissions or unsupported version can yield similar errors.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

journalctl --user -b --no-pager -n 120

ls -la ~/.config

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** A user-edited config has invalid syntax

1. Back up named config and compare format with app documentation

2. Correct only the identified line in app GUI/editor

3. Restart app and retest

**Solution route 2 — only if:** Config format changed across versions

1. Check app release notes

2. Prefer vendor migration or official reset of only this app

3. Restore from known-good backup if needed

**Graphical method:** App settings/editor; do not wipe ~/.config globally.

**Retest (observe only):**

```bash

journalctl --user -b --no-pager -n 80

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [journal](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html) · [desktop](https://specifications.freedesktop.org/desktop-entry-spec/latest/)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

# Boot

## Desktop login returns to greeter (`software35.boot.login-loop`)

**Software area:** boot

**Symptom:** Login accepted but graphical session immediately exits.

**Supporting evidence:** Per-session journal indicates named compositor or session process failure.

**Counterevidence:** Incorrect password or locked account differs from session failure.

**Hardware cross-references:** `hardware34.gpu.physical-reset` (consult both directions when logs justify it).

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

loginctl list-sessions

journalctl -b -p err --no-pager -n 120

systemctl status display-manager --no-pager

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Only the selected desktop session fails

1. From supported greeter choose alternative installed session

2. Back up only affected user session config and follow KDE/GNOME repair guidance

3. Retest normal login

**Solution route 2 — only if:** Display manager itself fails

1. Record unit and package version

2. Use distro supported update/rollback or recovery terminal

3. Avoid deleting user home/session data

**Graphical method:** Greeter session selector / KDE Plasma or GNOME Settings after login.

**Retest (observe only):**

```bash

systemctl status display-manager --no-pager

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [logind](https://www.freedesktop.org/software/systemd/man/latest/loginctl.html) · [systemd](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## System boots to emergency shell (`software35.boot.emergency-mode`)

**Software area:** boot

**Symptom:** systemd enters emergency.target instead of desktop.

**Supporting evidence:** Boot log shows failed required mount or unit prompting emergency mode.

**Counterevidence:** An encrypted volume requiring passphrase can be intentional.

**Hardware cross-references:** `hardware34.storage.nvme-timeout` (consult both directions when logs justify it).

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

journalctl -b -p err --no-pager -n 160

systemctl --failed --no-pager

findmnt

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** A removable secondary mount is missing

1. Verify failing path/device and last known configuration

2. User corrects only that mount entry through supported recovery method

3. Preserve data and retest boot

**Solution route 2 — only if:** Root filesystem or storage errors

1. Stop modifying drive

2. Follow distro documented rescue/recovery and back up data

3. Escalate to storage hardware procedure on matching I/O errors

**Graphical method:** Use the applicable desktop settings or trusted original application interface; do not treat ULSM as a universal system repair tool.

**Retest (observe only):**

```bash

systemctl --failed --no-pager

```

**Safety:** Do not run fsck against mounted writable system filesystems or blindly edit /etc/fstab.

**References:** [systemd](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html) · [journal](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Kernel version differs from expected image (`software35.boot.wrong-kernel-after-update`)

**Software area:** boot

**Symptom:** Booted kernel remains older/newer than proposed update.

**Supporting evidence:** rpm-ostree deployment or distro package inventory differs from uname -r.

**Counterevidence:** Having multiple installed kernels is normal.

**Hardware cross-references:** `hardware34.gpu.physical-reset` (consult both directions when logs justify it).

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

uname -r

rpm-ostree status

cat /etc/os-release

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Bazzite pending deployment not yet booted

1. Read booted/staged status

2. User reboots normally after saving data

3. Confirm active deployment

**Solution route 2 — only if:** New kernel produces regression

1. Compare a known-good supported deployment

2. Follow distro rollback/recovery instructions

3. Do not manually overwrite kernel or GRUB files

**Graphical method:** Bazzite Updater or bootloader supported recovery.

**Retest (observe only):**

```bash

uname -r

rpm-ostree status

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [bazzite](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/) · [kernel](https://docs.kernel.org/admin-guide/kernel-parameters.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## System clock remains incorrect (`software35.boot.time-sync-service`)

**Software area:** boot

**Symptom:** Applications reject TLS due to erroneous system time.

**Supporting evidence:** timedatectl shows unsynchronized time and relevant service warnings.

**Counterevidence:** Certificate expiration and real time offset are different failures.

**Hardware cross-references:** `hardware34.board.clock-source-reset` (consult both directions when logs justify it).

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

timedatectl status

systemctl status systemd-timesyncd --no-pager

journalctl -b -u systemd-timesyncd --no-pager -n 70

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Configured time source unavailable

1. Verify connectivity and trusted NTP service on this distro

2. User configures a documented time source with desktop tool

3. Check sync again

**Solution route 2 — only if:** Hardware RTC repeatedly loses time

1. Inspect firmware/RTC and hardware battery

2. Avoid treating recurring power-off RTC reset as solely NTP misconfiguration

**Graphical method:** Desktop Date & Time configuration; not ULSM.

**Retest (observe only):**

```bash

timedatectl status

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [systemd](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html) · [journal](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

# Containers

## Podman container image not found (`software35.containers.podman-image-missing`)

**Software area:** containers

**Symptom:** Start fails referencing absent or unauthorized image.

**Supporting evidence:** podman inspect and images list show required tag/digest unavailable.

**Counterevidence:** Container may exist under a different rootless user, not absent.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

podman images

podman ps -a

podman info

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Correct image exists in trusted registry

1. Check exact publisher and digest

2. User performs authorized image pull after explicit network choice

3. Recreate only optional target from saved configuration

**Solution route 2 — only if:** Image tag or registry no longer supported

1. Consult project image migration docs

2. Update compose/container definition only with documented compatible tag

3. Retest service

**Graphical method:** Container manager UI if available; ULSM is not container orchestrator.

**Retest (observe only):**

```bash

podman images

podman ps -a

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [podman](https://docs.podman.io/en/latest/Commands.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Rootless container cannot bind privileged host port (`software35.containers.podman-rootless-port`)

**Software area:** containers

**Symptom:** Container errors binding port below privileged threshold.

**Supporting evidence:** podman inspect exposes mapped host port requiring privileges.

**Counterevidence:** Port already used by other process has separate resolution.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

podman ps -a

podman inspect CONTAINER

ss -ltnp

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Service can use unprivileged port

1. Choose supported unprivileged host port in user container configuration

2. Update client/proxy route correspondingly and retest

**Solution route 2 — only if:** Service requires standard publicly exposed port

1. Use documented rootless proxy or administrator-managed front-end only after security review

2. Avoid broad kernel sysctl or running entire app privileged

**Graphical method:** Container management app or configuration editor.

**Retest (observe only):**

```bash

podman ps -a

ss -ltnp

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [podman-rootless](https://docs.podman.io/en/latest/markdown/podman.1.html) · [systemd](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Container cannot write bound volume (`software35.containers.volume-permission`)

**Software area:** containers

**Symptom:** Rootless container gets permission denied to mounted host directory.

**Supporting evidence:** Volume mount path/UID map and SELinux label mismatch seen in logs.

**Counterevidence:** Application may lack internal write permission even without mount.

**Hardware cross-references:** `storage.filesystem-errors` (consult both directions when logs justify it).

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

podman inspect CONTAINER

id

ls -ld /path/to/volume

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** UID mapping or label mismatch for this volume

1. Identify expected container UID and exact host directory

2. Apply only documented rootless ownership or label option to intended volume after backup

3. Retest

**Solution route 2 — only if:** Path is read-only by design or wrong mount

1. Confirm intended volume purpose

2. Correct application volume declaration rather than blanket chmod of host filesystem

**Graphical method:** Use the applicable desktop settings or trusted original application interface; do not treat ULSM as a universal system repair tool.

**Retest (observe only):**

```bash

podman inspect CONTAINER

```

**Safety:** Avoid chmod 777, blanket chcon or disabling SELinux.

**References:** [podman](https://docs.podman.io/en/latest/Commands.html) · [podman-rootless](https://docs.podman.io/en/latest/markdown/podman.1.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## DNS lookup fails in container or host (`software35.containers.container-network`)

**Software area:** containers

**Symptom:** A container cannot resolve expected names; host resolution may work or also be broken and must be compared.

**Supporting evidence:** Compare a specific name lookup inside the container with the host resolver and inspect isolated network configuration if available.

**Counterevidence:** Hostwide DNS failure cannot be assigned to a container-only resolver without separate evidence.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

podman network ls

podman ps -a

resolvectl status

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Container uses stale or isolated network

1. Check network attachment in saved deployment config

2. User reconnects or recreates only affected optional container through supported tool

3. Retest after user-authorized request

**Solution route 2 — only if:** Host DNS is broken

1. Correct host networking first

2. Do not inject public DNS into every container blindly

**Graphical method:** Container manager network settings; no automatic external probe.

**Retest (observe only):**

```bash

podman network ls

resolvectl status

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [podman](https://docs.podman.io/en/latest/Commands.html) · [resolved](https://www.freedesktop.org/software/systemd/man/latest/resolvectl.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Container image storage fills user home (`software35.containers.disk-space`)

**Software area:** containers

**Symptom:** Writable storage filled by images/layers.

**Supporting evidence:** podman system df identifies significant reclaimable images while actual filesystem is full.

**Counterevidence:** On Atomic Linux composefs root fullness is not writable storage exhaustion.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

podman system df

df -h /var

podman ps -a

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Only unused noncritical images consume space

1. Record important container names and volumes

2. User prunes only verified unneeded images after review and backups

3. Recheck storage

**Solution route 2 — only if:** Persistent container volumes hold real data

1. Inspect named volume ownership and retention

2. Move/archive data with supported app tooling; never blind prune persistent volumes

**Graphical method:** Container management UI; never one-click automatic prune.

**Retest (observe only):**

```bash

podman system df

df -h /var

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [podman](https://docs.podman.io/en/latest/Commands.html) · [bazzite](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

# Desktop

## Screen sharing produces a blank frame (`software35.desktop.wayland-screencast`)

**Software area:** desktop

**Symptom:** App can open screen share selection but stream is black.

**Supporting evidence:** Portal/WirePlumber session errors align with a Wayland capture failure.

**Counterevidence:** Display hardware no signal is different; some DRM-protected content intentionally stays black.

**Hardware cross-references:** `hardware34.gpu.physical-reset` (consult both directions when logs justify it).

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

echo $XDG_SESSION_TYPE

systemctl --user status xdg-desktop-portal --no-pager

wpctl status

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Portal backend misaligned with desktop

1. Identify actual session and portal backend

2. Update appropriate distro portal packages, no mixed GUI backends

3. Log out/in and retest benign window

**Solution route 2 — only if:** Only one app lacks compatible screencast support

1. Check that app supports intended Wayland portal API

2. Update app from original source

3. Report program-specific screen sharing bug

**Graphical method:** KDE/GNOME screen share picker; ULSM only for updating optional app.

**Retest (observe only):**

```bash

systemctl --user status xdg-desktop-portal --no-pager

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [portal](https://flatpak.github.io/xdg-desktop-portal/docs/) · [wire](https://pipewire.pages.freedesktop.org/wireplumber/man/wpctl.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Clipboard is empty between apps (`software35.desktop.wayland-clipboard`)

**Software area:** desktop

**Symptom:** Copy/paste fails between XWayland and native Wayland programs.

**Supporting evidence:** Reproducible failure occurs across certain app protocols or sandbox scopes.

**Counterevidence:** Clipboard content that disappears when owning app exits can be normal.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

echo $XDG_SESSION_TYPE

systemctl --user status xdg-desktop-portal --no-pager

flatpak list --app

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Failure isolated to one app

1. Check app clipboard support and sandbox permissions

2. Update app/portal through original supported sources

3. Retest plain text transfer

**Solution route 2 — only if:** Desktop session interoperability regression

1. Compare standard session behavior without changing compositor policy blindly

2. Follow desktop bug tracker and supported update/rollback

3. Supply redacted reproduction details

**Graphical method:** KDE Clipboard settings; GNOME desktop clipboard options where supported.

**Retest (observe only):**

```bash

echo $XDG_SESSION_TYPE

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [portal](https://flatpak.github.io/xdg-desktop-portal/docs/) · [desktop](https://specifications.freedesktop.org/desktop-entry-spec/latest/)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Applications blurry after display scaling (`software35.desktop.scaling-blur`)

**Software area:** desktop

**Symptom:** Only some apps render blurry text on high DPI screen.

**Supporting evidence:** Blur limited to XWayland scaled windows, while native Wayland windows are sharp.

**Counterevidence:** Low-resolution image assets can be blurry even with correct scaling.

**Hardware cross-references:** `hardware34.display.panel-physical` (consult both directions when logs justify it).

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

echo $XDG_SESSION_TYPE

loginctl list-sessions

flatpak list --app

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** App supports native Wayland backend

1. Select supported native rendering mode via app settings

2. Restart just affected app and compare text

**Solution route 2 — only if:** App does not support native protocol

1. Use desktop-supported scale settings or per-app compromise

2. Report upstream toolkit limitation rather than changing driver

**Graphical method:** KDE Display Configuration / GNOME Displays; avoid custom undocumented environment vars.

**Retest (observe only):**

```bash

echo $XDG_SESSION_TYPE

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [desktop](https://specifications.freedesktop.org/desktop-entry-spec/latest/) · [portal](https://flatpak.github.io/xdg-desktop-portal/docs/)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Global keyboard shortcut stopped working (`software35.desktop.shortcut-conflict`)

**Software area:** desktop

**Symptom:** A shortcut executes wrong app or does nothing.

**Supporting evidence:** Two bindings target same sequence or desktop logs record capture conflict.

**Counterevidence:** A physically faulty keyboard requires hardware diagnosis.

**Hardware cross-references:** `hardware34.peripherals.hid-keyboard` (consult both directions when logs justify it).

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

echo $XDG_CURRENT_DESKTOP

loginctl list-sessions

journalctl --user -b --no-pager -n 90

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Conflict between two desktop bindings

1. Inspect KDE/GNOME keyboard shortcuts

2. Remove only duplicate user binding

3. Test shortcut in normal session

**Solution route 2 — only if:** Only specific app intercepts shortcut

1. Inspect app keybindings or permissions

2. Update affected app and report issue

3. Leave global desktop shortcuts intact

**Graphical method:** Desktop Keyboard Shortcuts UI.

**Retest (observe only):**

```bash

echo $XDG_CURRENT_DESKTOP

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [desktop](https://specifications.freedesktop.org/desktop-entry-spec/latest/) · [logind](https://www.freedesktop.org/software/systemd/man/latest/loginctl.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## App fails to open on desktop login (`software35.desktop.broken-autostart`)

**Software area:** desktop

**Symptom:** An app starts manually but not from autostart.

**Supporting evidence:** User autostart desktop entry or systemd --user unit references stale Exec path.

**Counterevidence:** Desktop may purposely postpone app launch until online.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

ls ~/.config/autostart

systemctl --user --failed --no-pager

journalctl --user -b --no-pager -n 100

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Autostart path outdated after app update

1. Identify exact launcher executable or Flatpak ID

2. User corrects only affected autostart entry in desktop UI

3. Log out/in and verify

**Solution route 2 — only if:** A user service fails independently

1. Use systemctl --user status and journal for named unit

2. Fix actual dependency/config before enabling autostart

**Graphical method:** KDE Autostart / GNOME Startup Apps.

**Retest (observe only):**

```bash

ls ~/.config/autostart

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [desktop](https://specifications.freedesktop.org/desktop-entry-spec/latest/) · [systemd](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Fonts or icons missing in applications (`software35.desktop.font-missing`)

**Software area:** desktop

**Symptom:** Text uses unexpected substitute font or glyphs are boxes.

**Supporting evidence:** fc-match reports wrong family; app cannot find installed font in its environment.

**Counterevidence:** Malformed document with unsupported glyph is unrelated to system font packages.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

fc-match sans

fc-list : family

echo $XDG_CURRENT_DESKTOP

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Font not installed in actual scope

1. Identify required font licence/source

2. Use distro or trusted font installer under user control

3. Rebuild cache only with user consent if docs require

**Solution route 2 — only if:** Only sandbox app cannot see installed font

1. Inspect Flatpak runtime/font integration

2. Update affected app/runtime via installed source and report app-specific issue

**Graphical method:** Desktop Fonts settings; ULSM only for actual native package install.

**Retest (observe only):**

```bash

fc-match sans

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [fonts](https://www.freedesktop.org/software/fontconfig/fontconfig-user.html) · [flatpak](https://docs.flatpak.org/en/latest/using-flatpak.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Links open wrong browser (`software35.desktop.xdg-default-browser`)

**Software area:** desktop

**Symptom:** Clicking URLs launches unexpected application.

**Supporting evidence:** xdg-settings or MIME default points to undesired .desktop app.

**Counterevidence:** An app may use its own internal browser independently of system defaults.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

xdg-settings get default-web-browser

xdg-mime query default x-scheme-handler/https

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** System default changed

1. Choose preferred installed browser via desktop Default Applications

2. Retest HTTPS link without altering protocol handlers for all users

**Solution route 2 — only if:** Only one application uses wrong browser

1. Inspect that app preference or sandbox portal behavior

2. Update app if integration bug, report reproduction

**Graphical method:** KDE Default Applications or GNOME Settings.

**Retest (observe only):**

```bash

xdg-settings get default-web-browser

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [mime](https://specifications.freedesktop.org/mime-apps-spec/latest/) · [desktop](https://specifications.freedesktop.org/desktop-entry-spec/latest/)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Desktop unlock returns black screen (`software35.desktop.lockscreen-after-suspend`)

**Software area:** desktop

**Symptom:** After resume the user session stays black while host seems active.

**Supporting evidence:** Compositor/user journal records render or session errors around suspend/resume.

**Counterevidence:** Machine losing power without logs can indicate hardware instead.

**Hardware cross-references:** `hardware34.gpu.physical-reset` (consult both directions when logs justify it).

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

journalctl --user -b --no-pager -n 140

loginctl list-sessions

journalctl -b -k --no-pager -n 120

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Only desktop session is affected

1. Preserve work if accessible through supported means

2. Install desktop supported updates

3. Test normal suspend/resume without custom GPU tweaks

**Solution route 2 — only if:** Kernel reports GPU timeout or failed device resume

1. Follow GPU hardware/driver crosslink and distribution recovery

2. Avoid treating it only as display-manager issue

**Graphical method:** Desktop Power management and session settings.

**Retest (observe only):**

```bash

journalctl -b -k --no-pager -n 110

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [logind](https://www.freedesktop.org/software/systemd/man/latest/loginctl.html) · [journal](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

# Development

## pip refuses installation in externally managed Python (`software35.development.python-externally-managed`)

**Software area:** development

**Symptom:** pip reports externally-managed-environment.

**Supporting evidence:** Python install is managed by distro according to PEP 668 marker.

**Counterevidence:** User may already have a virtualenv and be using wrong interpreter.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

python3 -m pip --version

python3 -c "import sys; print(sys.prefix, sys.base_prefix)"

cat /etc/os-release

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Project needs Python-only dependency

1. Create project virtual environment per Python docs

2. Activate venv and install only project dependencies inside it

3. Confirm package imported from venv

**OPTIONAL user-entered command after checking distro, prerequisites, version and exact target:**

```bash

python3 -m venv .venv

```

**Solution route 2 — only if:** System dependency is required by distro service

1. Use distro package tool for packaged module, not system pip override

2. Check supported package versions and service requirements

**Graphical method:** ULT can explain python -m venv; ULSM only manages distro packages, not venv internals.

**Retest (observe only):**

```bash

python3 -m pip --version

```

**Safety:** Never suggest pip --break-system-packages as first repair.

**References:** [python](https://docs.python.org/3/library/venv.html) · [packaging](https://packaging.python.org/en/latest/specifications/externally-managed-environments/)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Virtual environment uses wrong interpreter (`software35.development.venv-wrong-python`)

**Software area:** development

**Symptom:** App imports fail despite pip showing installed package.

**Supporting evidence:** python and pip paths point to different virtualenv/system interpreters.

**Counterevidence:** A package may genuinely have incompatible version rather than path mismatch.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

python3 -m pip --version

python3 -c "import sys; print(sys.executable)"

printenv XDG_CURRENT_DESKTOP

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** User installed into other interpreter

1. Activate intended venv

2. Install with that interpreter python -m pip, not bare pip

3. Recheck exact module import

**Solution route 2 — only if:** Virtualenv built for outdated Python

1. Create new project venv from supported Python

2. Restore requirements from reviewed lockfile

3. Keep system Python intact

**Graphical method:** ULT command builder can show interpreter path; no system python modification.

**Retest (observe only):**

```bash

python3 -c "import sys; print(sys.executable)"

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [python](https://docs.python.org/3/library/venv.html) · [packaging](https://packaging.python.org/en/latest/specifications/externally-managed-environments/)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Git refuses branch switch due to local modifications (`software35.development.git-worktree-dirty`)

**Software area:** development

**Symptom:** Checkout would overwrite tracked user changes.

**Supporting evidence:** git status shows modified tracked files conflicting with target.

**Counterevidence:** Permission denied accessing .git is separate issue.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

git status --short

git branch --show-current

git log -1 --oneline

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Local work must be preserved

1. Review changed files

2. Commit changes or use supported stash only if developer understands consequences

3. Retry branch change

**Solution route 2 — only if:** Changes are generated build outputs

1. Confirm files are safe to discard using repository guidance

2. Remove only recognized generated artifacts under user control

**Graphical method:** Git GUI staging/commit; avoid forced git clean/reset.

**Retest (observe only):**

```bash

git status --short

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [git](https://git-scm.com/docs/git-status)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Git fetch fails authentication (`software35.development.git-auth`)

**Software area:** development

**Symptom:** Git reports access denied to remote.

**Supporting evidence:** git remote -v and error show authenticated endpoint failure.

**Counterevidence:** DNS/TLS outage might fail before authentication.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

git remote -v

git status --short

printenv XDG_CURRENT_DESKTOP

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Stored credentials/token expired

1. Use host project approved credential manager

2. Reauthorize minimum-scope access without sharing token

3. Retry user-run fetch

**Solution route 2 — only if:** Remote URL points to wrong repository

1. Verify upstream URL and account privileges

2. Correct only project-specific remote using trusted project information

**Graphical method:** Git credential GUI or official provider login.

**Retest (observe only):**

```bash

git remote -v

```

**Safety:** Environment output may include secrets; redact and never paste tokens in troubleshooting report.

**References:** [git](https://git-scm.com/docs/git-status)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Build script reports command not found (`software35.development.build-tool-missing`)

**Software area:** development

**Symptom:** Toolchain executable absent from PATH or sandbox.

**Supporting evidence:** command -v returns missing for exact named build tool.

**Counterevidence:** Tool may be packaged under a different name or provided inside dev container.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

command -v cmake

command -v gcc

cat /etc/os-release

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Build requires supported local toolchain

1. Read project build prerequisites

2. User installs only required developer tools via original distro source or uses supported Toolbox/Distrobox

3. Retest tool version

**Solution route 2 — only if:** Developer project expects container environment

1. Use documented container/toolchain image

2. Do not layer random compilers onto Atomic host just to satisfy one script

**Graphical method:** ULSM package tabs where suitable; Toolbox on Atomic systems.

**Retest (observe only):**

```bash

command -v cmake

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [bazzite](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/) · [ubuntu](https://ubuntu.com/server/docs/how-to/software/package-management/)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Unexpected command selected from PATH (`software35.development.path-command-shadowed`)

**Software area:** development

**Symptom:** Running a command selects a version or executable different from what the system or project expects.

**Supporting evidence:** Compare the resolved executable and actual shell PATH with the version required for the intended project or distro.

**Counterevidence:** A custom tool earlier in PATH is not an error if it is explicitly the intended project tool.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

type -a python3

command -v python3

printenv XDG_CURRENT_DESKTOP

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** User shell PATH prepends stale binary

1. Locate shell/profile config that altered PATH

2. Back up and correct only offending line

3. Start new shell and verify

**Solution route 2 — only if:** Project expects custom tool version

1. Use project venv/container or explicit interpreter

2. Keep system PATH unchanged and document project invocation

**Graphical method:** Shell profile editor; guided ULT explains PATH.

**Retest (observe only):**

```bash

type -a python3

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [python](https://docs.python.org/3/library/venv.html) · [desktop](https://specifications.freedesktop.org/desktop-entry-spec/latest/)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Desktop application fails to contact D-Bus service (`software35.development.dbus-service`)

**Software area:** development

**Symptom:** App reports service unknown or timeout from session bus.

**Supporting evidence:** Session bus available but specific service name is absent or repeatedly fails activation.

**Counterevidence:** User launched app outside graphical session can lack bus environment.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

systemctl --user --failed --no-pager

loginctl list-sessions

journalctl --user -b --no-pager -n 100

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Optional service package missing/outdated

1. Identify D-Bus service vendor and owning original package

2. User reinstalls/updates only it through trusted package manager

3. Retest client

**Solution route 2 — only if:** Session environment exported incorrectly

1. Launch app within supported desktop session

2. Correct only affected launch script/session integration

3. Do not export arbitrary D-Bus sockets globally

**Graphical method:** Desktop session settings or trusted app package management.

**Retest (observe only):**

```bash

systemctl --user --failed --no-pager

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [dbus](https://dbus.freedesktop.org/doc/dbus-send.1.html) · [systemd](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

# Flatpak

## Flatpak cannot open host file (`software35.flatpak.file-access-denied`)

**Software area:** flatpak

**Symptom:** Sandboxed app sees permission denied for a selected file.

**Supporting evidence:** Flatpak app ID and exact denied path/portal grant are confirmed.

**Counterevidence:** Unreadable host file may be owned by another user, not a sandbox issue.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

flatpak info --show-permissions APP_ID

flatpak override --user --show APP_ID

flatpak list --app

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Application needs one specific file/folder

1. First use desktop file chooser portal

2. If supported, authorize only that file/folder through Flatseal or app settings

3. Retest with same file

**Solution route 2 — only if:** App lacks expected portal integration

1. Inspect portal status and app version

2. Update affected app and portal through distro-supported channels

3. File app integration issue instead of granting host-wide access

**Graphical method:** Flatseal for a narrow approved permission; ULSM for update only.

**Retest (observe only):**

```bash

flatpak info --show-permissions APP_ID

```

**Safety:** Never grant --filesystem=host or --device=all as a generic fix.

**References:** [sandbox](https://docs.flatpak.org/en/latest/sandbox-permissions.html) · [flathub](https://docs.flathub.org/docs/for-users/troubleshooting/) · [portal](https://flatpak.github.io/xdg-desktop-portal/docs/)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Flatpak cannot use camera or microphone (`software35.flatpak.camera-microphone-portal`)

**Software area:** flatpak

**Symptom:** Permission dialog does not appear or device is invisible to a Flatpak.

**Supporting evidence:** Portal backend reports failures while host device is available to native apps.

**Counterevidence:** Device not enumerated at host level is a hardware issue.

**Hardware cross-references:** `hardware34.peripherals.webcam-uvc` (consult both directions when logs justify it).

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

flatpak info --show-permissions APP_ID

systemctl --user status xdg-desktop-portal --no-pager

journalctl --user -b --no-pager -n 100

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Desktop privacy toggle blocks this app

1. Open desktop privacy settings and grant only intended camera/mic access

2. Restart affected app and retest

**Solution route 2 — only if:** Portal backend itself is failing

1. Inspect user journal for the named portal implementation

2. Use distro-supported portal package update or session restart, user-directed

3. Report desktop/portal mismatch with versions

**Graphical method:** Desktop Privacy settings; ULSM only for installed-app updates.

**Retest (observe only):**

```bash

systemctl --user status xdg-desktop-portal --no-pager

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [portal](https://flatpak.github.io/xdg-desktop-portal/docs/) · [sandbox](https://docs.flatpak.org/en/latest/sandbox-permissions.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Flatpak reports required runtime not installed (`software35.flatpak.missing-runtime`)

**Software area:** flatpak

**Symptom:** A Flatpak app cannot start due to missing required runtime.

**Supporting evidence:** flatpak info/launch identifies an exact unavailable runtime reference.

**Counterevidence:** Application may be broken for unrelated missing file/data.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

flatpak info APP_ID

flatpak list --runtime

flatpak remotes

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Required runtime comes from configured trusted remote

1. Confirm original application remote and runtime ref

2. Let Flatpak resolve matching runtime via its normal update/install interface

3. Retest app

**Solution route 2 — only if:** Original runtime no longer exists upstream

1. Identify supported newer app build using same original remote

2. Report orphaned runtime dependency to packager; do not switch source silently

**Graphical method:** ULSM Flatpak/Updates, if app update supported, or Flatpak original frontend.

**Retest (observe only):**

```bash

flatpak list --runtime

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [flatpak](https://docs.flatpak.org/en/latest/using-flatpak.html) · [flathub](https://docs.flathub.org/docs/for-users/troubleshooting/)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## User and system Flatpak installations conflict (`software35.flatpak.duplicate-scope`)

**Software area:** flatpak

**Symptom:** Duplicate app IDs have unexpected launch/version.

**Supporting evidence:** flatpak list indicates same app ID in USER and SYSTEM scopes.

**Counterevidence:** Two different app IDs with similar names are not duplicates.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

flatpak list --app --columns=application,installation,origin

flatpak info --user APP_ID

flatpak info --system APP_ID

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Unintended duplicate installation exists

1. Identify which scope is intended and back up app data

2. User removes only the verified unwanted duplicate from its original scope

3. Launch remaining app

**Solution route 2 — only if:** Different versions/sources are intentional

1. Preserve both while understanding launch selection

2. Use explicit scope when diagnosing, avoid automatic source switch

**Graphical method:** ULSM Flatpak tab with installation-scope verification.

**Retest (observe only):**

```bash

flatpak list --app --columns=application,installation,origin

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [flatpak](https://docs.flatpak.org/en/latest/using-flatpak.html) · [flathub](https://docs.flathub.org/docs/for-users/troubleshooting/)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Flatpak file chooser never opens (`software35.flatpak.portal-dialog-missing`)

**Software area:** flatpak

**Symptom:** File picker/share dialog fails only in sandboxed apps.

**Supporting evidence:** xdg-desktop-portal user service errors or desktop backend mismatch align with symptom.

**Counterevidence:** Only a single app failing to call portal is app-specific.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

systemctl --user status xdg-desktop-portal --no-pager

journalctl --user -b --no-pager -n 120

flatpak list --app

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Correct desktop portal backend is missing/stale

1. Confirm KDE/GNOME/other session and available backend through distro packages

2. User updates matching portal packages via native distro-supported route

3. Sign out/in when requested

**Solution route 2 — only if:** Portal operational but app still fails

1. Update app through same Flatpak source

2. Capture exact repro and submit upstream app issue; avoid blanket sandbox override

**Graphical method:** KDE/GNOME desktop session settings; ULSM only for supported app updates.

**Retest (observe only):**

```bash

systemctl --user status xdg-desktop-portal --no-pager

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [portal](https://flatpak.github.io/xdg-desktop-portal/docs/) · [flathub](https://docs.flathub.org/docs/for-users/troubleshooting/)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Flatpak exits immediately (`software35.flatpak.app-not-launching`)

**Software area:** flatpak

**Symptom:** A Flatpak fails to open despite being installed.

**Supporting evidence:** flatpak run reports a specific runtime, permission or app stack error.

**Counterevidence:** User was invoking an incorrect app ID, or running a native app instead.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

flatpak info APP_ID

flatpak list --app

flatpak history

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** App package or runtime update is available

1. Verify origin and scope

2. Install supported update using original source

3. Test launch with correct ID

**Solution route 2 — only if:** No update and reproducible error remains

1. Record flatpak run stderr and application commit

2. Review narrow overrides, file portal or package issue

3. Submit redacted reproducible report

**Graphical method:** ULSM Flatpak/Updates; developer packaging page for issue.

**Retest (observe only):**

```bash

flatpak info APP_ID

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [flatpak](https://docs.flatpak.org/en/latest/using-flatpak.html) · [flathub](https://docs.flathub.org/docs/for-users/troubleshooting/)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Flatpak fails after user-data migration (`software35.flatpak.corrupt-user-data`)

**Software area:** flatpak

**Symptom:** A Flatpak works with new profile but not old one.

**Supporting evidence:** Named app state/config parse error matches failure; data path verified.

**Counterevidence:** Repeated GPU resets or host filesystem I/O errors suggest external issue.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

flatpak info APP_ID

journalctl --user -b --no-pager -n 130

ls ~/.var/app

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Only optional cache is corrupted

1. Back up affected app data in ~/.var/app/APP_ID

2. Use in-app reset or documented cache clearing manually without deleting unrelated folders

3. Test app on copied data

**Solution route 2 — only if:** Persistent application data incompatible

1. Locate upstream migration instructions and preserve backup

2. Use supported older/newer app migration path

3. Report incompatibility if no safe conversion

**Graphical method:** Use app Settings for reset and ULSM only for version updates.

**Retest (observe only):**

```bash

flatpak info APP_ID

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [flathub](https://docs.flathub.org/docs/for-users/troubleshooting/) · [flatpak](https://docs.flatpak.org/en/latest/using-flatpak.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

# Network

## DNS lookups fail in one application or across host (`software35.network.dns-per-app`)

**Software area:** network

**Symptom:** DNS lookups fail in one program or across applications; identify whether the failure is app-specific or host-wide.

**Supporting evidence:** Compare the exact failing hostname from the affected app against a local host resolver result, inspecting sandbox/container differences and system resolver status if available.

**Counterevidence:** A misspelled hostname, an HTTP application error, or general network loss is not by itself a DNS resolver failure.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

resolvectl status

nmcli device status

flatpak info APP_ID

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Sandbox app has stale network/portal setup

1. Verify app installation source and network permissions

2. Update only affected app/runtime through original manager

3. Test same URL under normal conditions

**Solution route 2 — only if:** Host DNS is inconsistent too

1. Inspect NetworkManager/resolved service and actual DNS servers

2. Correct only the named connection via desktop settings and retry

**Graphical method:** Network Settings or ULSM Updates for affected optional app.

**Retest (observe only):**

```bash

resolvectl status

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [nm](https://networkmanager.dev/docs/api/latest/nmcli.html) · [resolved](https://www.freedesktop.org/software/systemd/man/latest/resolvectl.html) · [sandbox](https://docs.flatpak.org/en/latest/sandbox-permissions.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## NetworkManager says device unmanaged (`software35.network.nm-unmanaged`)

**Software area:** network

**Symptom:** Network adapter present but GUI will not manage it.

**Supporting evidence:** nmcli reports unmanaged and other network manager/config claims same interface.

**Counterevidence:** Physically absent adapter is not a NetworkManager ownership issue.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

nmcli device status

nmcli general status

ip link

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Another legitimate manager owns interface

1. Identify owner and distro network configuration

2. Keep one intended manager, user adjusts appropriate supported interface settings

3. Verify connection

**Solution route 2 — only if:** NetworkManager policy unintentionally excludes interface

1. Back up matching config and inspect rules

2. Have administrator remove only incorrect exclusion, then apply via approved UI/service workflow

**Graphical method:** KDE/GNOME Network Settings; avoid simultaneous network daemons.

**Retest (observe only):**

```bash

nmcli device status

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [nm](https://networkmanager.dev/docs/api/latest/nmcli.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Wi-Fi association fails due to authentication (`software35.network.wifi-secret`)

**Software area:** network

**Symptom:** Access point rejects credentials and connection cycles.

**Supporting evidence:** NetworkManager logs show authentication/secret exchange issue for exact SSID.

**Counterevidence:** Radio disconnected by rfkill or DHCP failure is a different stage.

**Hardware cross-references:** `hardware34.peripherals.wireless-radio-missing` (consult both directions when logs justify it).

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

nmcli device status

nmcli connection show

journalctl -b -u NetworkManager --no-pager -n 90

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Saved key no longer matches router configuration

1. Confirm SSID/security with network owner

2. Enter corrected passphrase via desktop Wi-Fi settings; never paste to bug report

3. Reconnect and verify state

**Solution route 2 — only if:** Enterprise authentication requires certificates

1. Check EAP method and expiration against administrator policy

2. Renew only official certificate/profile

3. Avoid weakening TLS verification

**Graphical method:** Desktop Network Settings; no automated password extraction.

**Retest (observe only):**

```bash

nmcli device status

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [nm](https://networkmanager.dev/docs/api/latest/nmcli.html) · [journal](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Connection active but no DHCP address (`software35.network.dhcp-no-address`)

**Software area:** network

**Symptom:** Link active yet no usable IPv4 address or route.

**Supporting evidence:** nmcli/ip shows carrier and no acquired address with DHCP timeout logs.

**Counterevidence:** Static IPv4 or IPv6-only connection may intentionally omit DHCPv4.

**Hardware cross-references:** `hardware34.peripherals.wired-link-flaps` (consult both directions when logs justify it).

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

nmcli device status

ip address show

ip route

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** DHCP service/router does not answer

1. Compare another client on same LAN with approval

2. Ask network owner to check router DHCP

3. Reconnect using desktop settings rather than random static IP

**Solution route 2 — only if:** Incorrect client connection profile

1. Inspect configured IPv4 method and interface ownership

2. Correct only affected profile to intended DHCP/static mode under user control

**Graphical method:** Network Settings; router administration by owner.

**Retest (observe only):**

```bash

ip address show

ip route

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [nm](https://networkmanager.dev/docs/api/latest/nmcli.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## VPN connects but traffic uses wrong route (`software35.network.vpn-route`)

**Software area:** network

**Symptom:** Internet works outside VPN, remote resources fail after connection.

**Supporting evidence:** ip route and nmcli show tunnel attached but default/split routing differs from intended policy.

**Counterevidence:** DNS-only failure should be investigated separately.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

nmcli connection show --active

ip route

resolvectl status

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** VPN profile uses wrong split tunnel routes

1. Ask network administrator for intended routes

2. User corrects only VPN profile using approved GUI

3. Reconnect and compare route

**Solution route 2 — only if:** Remote service or VPN gateway unavailable

1. Verify reachability with approved opt-in test and server owner

2. Report gateway outage without changing host firewall broadly

**Graphical method:** Desktop VPN settings; no auto-probing external networks.

**Retest (observe only):**

```bash

ip route

nmcli connection show --active

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [nm](https://networkmanager.dev/docs/api/latest/nmcli.html) · [resolved](https://www.freedesktop.org/software/systemd/man/latest/resolvectl.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Network works in terminal but browser/app cannot connect (`software35.network.proxy-wrong`)

**Software area:** network

**Symptom:** Some apps use stale proxy while others connect normally.

**Supporting evidence:** Environment/app proxy settings differ from desktop managed proxy.

**Counterevidence:** Company-mandated proxy might be correct and externally required.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

printenv XDG_CURRENT_DESKTOP

nmcli connection show --active

resolvectl status

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Old user proxy setting no longer valid

1. Identify which app/profile exports proxy, redact credentials

2. User updates app/desktop proxy to valid known value

3. Retest connection

**Solution route 2 — only if:** Network requires organization proxy

1. Preserve mandated proxy

2. Consult network administrator and set matching supported app configuration

3. Do not bypass organizational access rules

**Graphical method:** Desktop Proxy settings or application Network settings.

**Retest (observe only):**

```bash

nmcli connection show --active

```

**Safety:** Environment listing can expose credentials; redact before sharing.

**References:** [nm](https://networkmanager.dev/docs/api/latest/nmcli.html) · [desktop](https://specifications.freedesktop.org/desktop-entry-spec/latest/)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Local service listens but client cannot connect (`software35.network.firewall-blocks`)

**Software area:** network

**Symptom:** App port is listening locally but inbound connections fail.

**Supporting evidence:** Listener exists, firewall rules cover port/interface and expected external client is blocked.

**Counterevidence:** Service not listening or upstream router issue cannot be fixed by firewall opening.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

ss -ltnp

sudo nft list ruleset

ip address show

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Firewall rule is too strict for an intended trusted local service

1. Confirm service identity, exposure and network scope

2. Administrator adds only narrowly scoped approved rule via firewall UI

3. Verify from permitted local client

**Solution route 2 — only if:** Service bound only to loopback or wrong interface

1. Inspect service binding and access policy

2. Adjust only app listener config if user actually intends remote access

3. Retest without weakening default firewall

**Graphical method:** Firewall settings per distro; never open ports globally as a diagnostic shortcut.

**Retest (observe only):**

```bash

ss -ltnp

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [nft](https://wiki.nftables.org/wiki-nftables/index.php/Main_Page) · [systemd](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## HTTPS certificate validation or clock error (`software35.network.time-tls`)

**Software area:** network

**Symptom:** HTTPS clients reject a TLS certificate or report a certificate validity/time error; the clock and the server certificate require independent checking.

**Supporting evidence:** Confirm the exact TLS validation error, trusted local time and certificate validity information. Distinguish incorrect local time from an invalid or untrusted server certificate without bypassing validation.

**Counterevidence:** Correct local time does not prove the server certificate is trustworthy, and a server certificate error is not proof of a local clock fault.

**Hardware cross-references:** `hardware34.board.clock-source-reset` (consult both directions when logs justify it).

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

timedatectl status

resolvectl status

journalctl -b -p warning --no-pager -n 90

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Machine clock is inaccurate

1. Use approved Date/Time settings and trusted NTP

2. Restore sync before retrying TLS connection

**Solution route 2 — only if:** Server cert is invalid despite correct local time

1. Do not bypass verification

2. Contact server operator or use correctly signed official service

3. Report exact hostname and error without revealing tokens

**Graphical method:** Desktop Date & Time settings.

**Retest (observe only):**

```bash

timedatectl status

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [systemd](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html) · [resolved](https://www.freedesktop.org/software/systemd/man/latest/resolvectl.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Host name resolves to unexpected address (`software35.network.hostname-resolution`)

**Software area:** network

**Symptom:** Local network services use wrong hostname/IP.

**Supporting evidence:** getent/hostnamectl output differs from intended local DNS or hosts mapping.

**Counterevidence:** VPN DNS split horizon may legitimately yield different answers.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

hostnamectl status

getent hosts localhost

resolvectl status

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Local hostname override is stale

1. Identify name and associated intended address

2. User updates only stale hosts/local DNS entry according to network policy

3. Retest

**Solution route 2 — only if:** Remote DNS is source of wrong address

1. Collect redacted lookup result

2. Network owner corrects authoritative DNS rather than altering every client

**Graphical method:** Network/DNS settings; administrator-controlled when shared network.

**Retest (observe only):**

```bash

hostnamectl status

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [resolved](https://www.freedesktop.org/software/systemd/man/latest/resolvectl.html) · [nm](https://networkmanager.dev/docs/api/latest/nmcli.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

# Packages

## APT/dpkg interrupted transaction (`software35.packages.apt-interrupted`)

**Software area:** packages

**Symptom:** APT says dpkg was interrupted or a package is half-configured.

**Supporting evidence:** dpkg database reports half-configured package with matching recent update error.

**Counterevidence:** A network mirror failure can occur without interrupted dpkg state.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

dpkg --audit

apt-cache policy PACKAGE

cat /etc/os-release

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** dpkg audit identifies pending configuration

1. Back up important data and confirm no package manager is running

2. User follows Debian-supported dpkg configuration completion only after reviewing package prompts

3. Retry intended APT action

**OPTIONAL user-entered command after checking distro, prerequisites, version and exact target:**

```bash

sudo dpkg --configure -a

```

**Solution route 2 — only if:** Dependency mismatch remains after configuration

1. Read exact affected packages and held state

2. Use distro-supported package repair interface and review all proposed changes

3. Do not force-remove essential packages

**Graphical method:** Native APT frontend or ULSM DEB where supported; proposed transaction must be reviewed.

**Retest (observe only):**

```bash

dpkg --audit

```

**Safety:** Never run dpkg recovery while another package manager owns the lock.

**References:** [debian](https://www.debian.org/doc/manuals/debian-reference/ch02.en.html) · [ubuntu](https://ubuntu.com/server/docs/how-to/software/package-management/)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## APT package upgrade withheld (`software35.packages.apt-held`)

**Software area:** packages

**Symptom:** A package remains on an old version during updates.

**Supporting evidence:** apt-mark shows package held, or APT reports phased/dependency-based deferral.

**Counterevidence:** A normal upstream version rollout is not necessarily a broken package.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

apt-mark showhold

apt-cache policy PACKAGE

cat /etc/os-release

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Package was explicitly pinned/held by administrator

1. Identify purpose and origin of hold

2. Only user/administrator may remove an unintended hold after verifying dependent packages

3. Recheck package candidate

**Solution route 2 — only if:** Deferral is from distro release policy

1. Read distro update policy, phased rollout or dependency note

2. Leave deferred package until supported update becomes available; do not force risky mix

**Graphical method:** Distribution package updater, ULSM DEB if it accurately supports update/hold scenario.

**Retest (observe only):**

```bash

apt-cache policy PACKAGE

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [ubuntu](https://ubuntu.com/server/docs/how-to/software/package-management/) · [debian](https://www.debian.org/doc/manuals/debian-reference/ch02.en.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Third-party APT repository breaks upgrades (`software35.packages.apt-foreign-repository`)

**Software area:** packages

**Symptom:** APT reports signed key, Release file or package provenance error.

**Supporting evidence:** Error names a specific extra repository, URL or key.

**Counterevidence:** Official repository outage is different from obsolete third-party source.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

apt-cache policy PACKAGE

ls /etc/apt/sources.list.d

cat /etc/os-release

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** One outdated external repository causes errors

1. Identify and back up its source file

2. Use graphical Software Sources to disable only the broken optional source

3. Obtain corrected upstream signing/instructions before re-enabling

**Solution route 2 — only if:** Error originates from official distro repository

1. Check official status and clock/release version

2. Wait for trusted repair or adjust official mirror through supported UI

3. Do not turn off signature verification

**Graphical method:** Software Sources; never permit unsigned packages as workaround.

**Retest (observe only):**

```bash

ls /etc/apt/sources.list.d

```

**Safety:** Never bypass apt signature checks or run curl-pipe-shell fixes.

**References:** [debian](https://www.debian.org/doc/manuals/debian-reference/ch02.en.html) · [ubuntu](https://ubuntu.com/server/docs/how-to/software/package-management/)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Arch library ABI mismatch after partial update (`software35.packages.pacman-partial-upgrade`)

**Software area:** packages

**Symptom:** Arch binary reports missing lib version after pacman operations.

**Supporting evidence:** Log/version mismatch supports unsupported partial system upgrade.

**Counterevidence:** Manually downloaded app bundle could be the only incompatible component.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

pacman -Q

pacman -Qm

cat /etc/os-release

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** System uses Arch and partial update happened

1. Back up important work

2. Review pacman log and official Arch News

3. Perform an official complete system upgrade under user control

**OPTIONAL user-entered command after checking distro, prerequisites, version and exact target:**

```bash

sudo pacman -Syu

```

**Solution route 2 — only if:** Local AUR/rebuilt package is incompatible after update

1. Identify foreign packages and dependency SONAME change

2. Rebuild only affected package from trusted source after full official update

3. Check program again

**Graphical method:** ULSM Arch updates only if its implementation preserves full-upgrade rules.

**Retest (observe only):**

```bash

pacman -Q

```

**Safety:** Never suggest pacman -Sy PACKAGE or --nodeps as a quick fix.

**References:** [arch](https://wiki.archlinux.org/title/System_maintenance) · [pacman](https://wiki.archlinux.org/title/Pacman)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Pacman reports existing file conflict (`software35.packages.pacman-file-conflict`)

**Software area:** packages

**Symptom:** Transaction cannot overwrite a filesystem path.

**Supporting evidence:** Pacman identifies an exact conflicting path and owning package or unowned file.

**Counterevidence:** A signature failure or missing disk space is a different problem.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

pacman -Qo /path/to/file

pacman -Qk PACKAGE

cat /etc/os-release

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Conflicting file owned by trusted package

1. Record owners and path

2. Resolve the precise packaging conflict through Arch official guidance

3. Reattempt full supported transaction

**Solution route 2 — only if:** Unowned local file conflicts

1. Back up the affected local file first

2. Determine source and need before manually relocating only that file

3. Avoid broad overwrite globs

**Graphical method:** Package transaction view in ULSM Arch if exposed, or terminal with reviewed exact path.

**Retest (observe only):**

```bash

pacman -Qk PACKAGE

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [pacman](https://wiki.archlinux.org/title/Pacman) · [arch](https://wiki.archlinux.org/title/System_maintenance)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Unused Arch dependencies consume space (`software35.packages.pacman-orphans`)

**Software area:** packages

**Symptom:** Package database reports orphaned packages.

**Supporting evidence:** pacman -Qdt shows package set not explicitly installed or currently required.

**Counterevidence:** Some intentionally useful standalone tools may be marked as dependencies.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

pacman -Qdt

pacman -Qe

df -h /var

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Selected orphan truly unused

1. Review each orphan and package ownership

2. Remove only chosen unneeded optional packages through pacman/ULSM with dependency preview

3. Recheck free space

**Solution route 2 — only if:** Packages intentionally required by user workflows

1. Retain/mark desired packages explicitly using supported interface

2. Do not auto-delete every entry just to free disk

**Graphical method:** ULSM Arch tab if installed package removal is supported and reviewed.

**Retest (observe only):**

```bash

pacman -Qdt

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [pacman](https://wiki.archlinux.org/title/Pacman) · [arch](https://wiki.archlinux.org/title/System_maintenance)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Zypper reports repository conflicts (`software35.packages.zypper-repo-mismatch`)

**Software area:** packages

**Symptom:** openSUSE package resolver presents vendor or version conflict.

**Supporting evidence:** zypper repository list shows source and package version/provider differences.

**Counterevidence:** Insufficient space or network outage is unrelated to provider mixing.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

zypper lr -u

zypper se -si PACKAGE

cat /etc/os-release

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Conflicting optional third-party repository

1. Read proposed vendor switch and repo priorities

2. Use YaST repositories to disable only unintended repository

3. Retry official resolution without forced vendor switches

**Solution route 2 — only if:** Distro upgrade is underway and resolver needs planned migration

1. Use openSUSE release-specific upgrade instructions

2. Ensure backup and correct repositories before user-authorized upgrade

3. Inspect dry-run proposals carefully

**Graphical method:** YaST Software Repositories or ULSM RPM/Zypper if actual support covers operation.

**Retest (observe only):**

```bash

zypper lr -u

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [suse](https://doc.opensuse.org/knowledge_sources/leap/reference/html/book-reference/cha-sw-cl.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Zypper package lock blocks dependency (`software35.packages.zypper-lock`)

**Software area:** packages

**Symptom:** Package is locked and required dependency cannot update.

**Supporting evidence:** zypper locks list shows relevant exact pattern/package.

**Counterevidence:** Dependency conflict may be due to vendor differences without a lock.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

zypper locks

zypper se -si PACKAGE

zypper lr -u

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Lock is stale and no longer intentional

1. Identify who created the lock and why

2. User removes only that exact unnecessary lock via YaST/Zypper with review

3. Recheck resolver proposal

**Solution route 2 — only if:** Lock protects needed compatibility

1. Keep lock

2. Select supported package versions or consult repo maintainer

3. Avoid force-removing dependency chain

**Graphical method:** YaST package manager.

**Retest (observe only):**

```bash

zypper locks

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [suse](https://doc.opensuse.org/knowledge_sources/leap/reference/html/book-reference/cha-sw-cl.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## DNF transaction dependency conflict (`software35.packages.dnf-dependency-conflict`)

**Software area:** packages

**Symptom:** DNF cannot solve package dependencies.

**Supporting evidence:** Native DNF resolver error lists exact incompatible package and repository.

**Counterevidence:** Bazzite Atomic base must not be repaired using ordinary dnf.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

cat /etc/os-release

rpm -q PACKAGE

dnf history list

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Conventional mutable Fedora/RHEL based system

1. Identify repo and conflicting packages

2. Review proposed DNF resolution without --allowerasing by default

3. Update or remove only optional verified conflicting application as appropriate

**Solution route 2 — only if:** System is Bazzite/Fedora Atomic

1. Stop using host DNF for OS image

2. Inspect rpm-ostree status and layered packages

3. Use supported Bazzite update or rollback guide

**Graphical method:** Fedora DNF package manager or Bazzite Updater; ULSM only for supported package work.

**Retest (observe only):**

```bash

cat /etc/os-release

rpm -q PACKAGE

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [bazzite](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/) · [layer](https://docs.bazzite.gg/Installing_and_Managing_Software/rpm-ostree/)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Layered package blocks Atomic upgrade (`software35.packages.rpm-ostree-layered`)

**Software area:** packages

**Symptom:** rpm-ostree error names a layered RPM conflict.

**Supporting evidence:** rpm-ostree status lists layered package with conflict in pending deployment.

**Counterevidence:** Failure may instead be download or signature issue.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

rpm-ostree status

journalctl -b --no-pager -n 160

cat /etc/os-release

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Optional layered package is conflicting

1. Identify exact layered name and its function

2. User removes only dispensable confirmed layer following Bazzite guide

3. Reboot into new deployment and retest

**Solution route 2 — only if:** Layer is necessary to core workflow

1. Keep layer and use vendor/Bazzite supported alternative or await fixed repo

2. Collect exact rpm-ostree deployment error for maintainers

**Graphical method:** Bazzite Updater or rpm-ostree terminal; ULSM must not manage base image as a normal RPM.

**Retest (observe only):**

```bash

rpm-ostree status

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [bazzite](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/) · [layer](https://docs.bazzite.gg/Installing_and_Managing_Software/rpm-ostree/)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Atomic image update seems not applied (`software35.packages.atomic-pending-reboot`)

**Software area:** packages

**Symptom:** Bazzite shows pending deployment but current kernel/image remains old.

**Supporting evidence:** rpm-ostree status indicates new staged deployment not currently booted.

**Counterevidence:** An app Flatpak update need not reboot OS image.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

rpm-ostree status

uname -r

cat /etc/os-release

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Pending deployment has been staged successfully

1. Save work and use normal user-initiated reboot at convenient time

2. Confirm booted deployment afterwards

**Solution route 2 — only if:** New deployment fails to boot

1. Use documented GRUB or Bazzite Updater rollback without manually editing boot partitions

2. Record failed deployment and report to Bazzite maintainers

**Graphical method:** Bazzite Updater; not ULSM update tab for OS image.

**Retest (observe only):**

```bash

rpm-ostree status

uname -r

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [bazzite](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Updated Atomic image causes regression (`software35.packages.atomic-rollback`)

**Software area:** packages

**Symptom:** System stopped working after a Bazzite deployment update.

**Supporting evidence:** Last working deployment and new booted deployment are visible in rpm-ostree status.

**Counterevidence:** App-specific update around same time can also be culprit.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

rpm-ostree status

journalctl -b -1 --no-pager -n 120

cat /etc/os-release

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Specific image regression affects multiple system components

1. Record old/new deployment IDs

2. User rolls back via Bazzite supported GUI/GRUB/terminal to previous deployment

3. Recheck symptoms before considering new rebase

**Solution route 2 — only if:** Only one optional app regressed

1. Keep OS deployment

2. Use original app update/history path and report app-specific issue

**Graphical method:** Bazzite Updater or GRUB recovery.

**Retest (observe only):**

```bash

rpm-ostree status

```

**Safety:** Never overwrite OSTree internals or force an unsupported rebase.

**References:** [bazzite](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Flatpak remote has errors (`software35.packages.flatpak-remote`)

**Software area:** packages

**Symptom:** Flatpak cannot find app updates or repository.

**Supporting evidence:** flatpak remotes shows absent or incorrect origin and history names exact remote.

**Counterevidence:** DNS, TLS trust or site outage may be cause; do not blindly add remote.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

flatpak remotes --show-details

flatpak list --app --columns=application,origin,installation

flatpak history

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** The original trusted remote is missing from correct scope

1. Verify official remote URL and installation scope

2. User restores that exact remote from trusted documentation

3. Retry update only after confirming signature source

**Solution route 2 — only if:** Remote exists but endpoint is unavailable

1. Check offline/local proxy/DNS and vendor status

2. Wait or report outage rather than switching app provenance

**Graphical method:** ULSM Flatpak tab or original GUI if remote controls supported.

**Retest (observe only):**

```bash

flatpak remotes --show-details

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [flatpak](https://docs.flatpak.org/en/latest/using-flatpak.html) · [flathub](https://docs.flathub.org/docs/for-users/troubleshooting/)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Snap operation fails because daemon unavailable (`software35.packages.snap-daemon`)

**Software area:** packages

**Symptom:** snap reports cannot communicate with snapd.

**Supporting evidence:** systemctl status snapd shows inactive/failed and snap CLI cannot connect.

**Counterevidence:** Snap may not be installed or supported on selected distro.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

systemctl status snapd --no-pager

snap list

cat /etc/os-release

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Snap installed but optional daemon failed

1. Inspect snapd journal for exact error

2. User restores only the intended snapd unit using distro-supported service procedures

3. Retest snap listing

**Solution route 2 — only if:** Distro uses Flatpak/AppImage instead

1. Do not add snap infrastructure unnecessarily

2. Choose original app installer when reinstalling or updating

**Graphical method:** System services or ULSM Snap tab if actually supported.

**Retest (observe only):**

```bash

systemctl status snapd --no-pager

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [snap](https://snapcraft.io/docs/keeping-snaps-up-to-date) · [systemd](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Snap update held or refresh fails (`software35.packages.snap-refresh`)

**Software area:** packages

**Symptom:** snap shows held, pending or failed refresh.

**Supporting evidence:** snap tasks/changes show failing named application refresh operation.

**Counterevidence:** Unrelated native package update cannot be repaired by snap commands.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

snap refresh --time

snap changes

snap list

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Refresh failure transient or store unavailable

1. Check connectivity and snapd status

2. Retry using Snap supported refresh controls only with user consent after outage ends

**Solution route 2 — only if:** Held version intentional or app regression

1. Read snap hold/refresh policy and publisher revision

2. Preserve app data and report reproducible regression rather than forcing unrestricted refresh

**Graphical method:** ULSM Snap tab where supported or snap desktop tool.

**Retest (observe only):**

```bash

snap changes

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [snap](https://snapcraft.io/docs/keeping-snaps-up-to-date)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Application exists from multiple different sources (`software35.packages.app-source-mismatch`)

**Software area:** packages

**Symptom:** User expects updates from a different provider.

**Supporting evidence:** Package inventory shows Flathub build while GitHub/AppImage releases have different provenance.

**Counterevidence:** Similar app names may be unrelated forks.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

flatpak list --app

rpm -qa

cat /etc/os-release

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Existing install working and trustworthy

1. Keep existing provenance

2. Follow updates only for installed source

3. Explain that upstream GitHub version does not automatically replace Flathub

**Solution route 2 — only if:** User explicitly elects to switch source

1. Back up personal app data

2. Remove old installation via original manager only after clear informed choice

3. Install new trusted source and verify compatibility; never overwrite silently

**Graphical method:** ULSM Discover is read-only; actions belong to package tabs.

**Retest (observe only):**

```bash

flatpak list --app

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [flatpak](https://docs.flatpak.org/en/latest/using-flatpak.html) · [appimage](https://docs.appimage.org/user-guide/troubleshooting/index.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

# Security

## SELinux denies application action (`software35.security.selinux-avc`)

**Software area:** security

**Symptom:** Access operation fails with AVC in logs.

**Supporting evidence:** Audit event precisely names process, object and denied action.

**Counterevidence:** A generic denied file permission may not involve SELinux.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

getenforce

sudo ausearch -m AVC -ts recent

journalctl -b -p warning --no-pager -n 100

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** File label is wrong for that known trusted app

1. Identify intended SELinux domain/path and supported label policy

2. Administrator restores only correct label via official tooling with verified paths

3. Recheck denial

**Solution route 2 — only if:** Policy genuinely lacks permitted optional action

1. Preserve denial and identify publisher/policy

2. Use distribution SELinux troubleshooting and least-privilege policy fix

3. Report upstream; never disable SELinux

**Graphical method:** SELinux troubleshooter app where distro provides it.

**Retest (observe only):**

```bash

getenforce

```

**Safety:** Never recommend setenforce 0 or disabling SELinux to silence a warning.

**References:** [selinux](https://docs.fedoraproject.org/en-US/quick-docs/selinux-troubleshooting/) · [journal](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Privileged GUI action never asks for authentication (`software35.security.polkit-auth`)

**Software area:** security

**Symptom:** Desktop admin action fails authorization.

**Supporting evidence:** polkit helper/agent logs show no active session agent or explicit rejection.

**Counterevidence:** User account may simply lack admin privileges intentionally.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

loginctl list-sessions

journalctl -b --no-pager -n 130

id

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Desktop authentication agent missing

1. Identify current session and packaged agent

2. Restore only supported agent through distro desktop packages

3. Retry approved action under user control

**Solution route 2 — only if:** Policy denies requested operation

1. Confirm whether current account is intended administrator

2. Request appropriate administrator authorization

3. Do not grant blanket passwordless admin permissions

**Graphical method:** Desktop privilege dialog; ULSM only if admin authorizes package transaction.

**Retest (observe only):**

```bash

loginctl list-sessions

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [polkit](https://polkit.pages.freedesktop.org/polkit/polkit.8.html) · [logind](https://www.freedesktop.org/software/systemd/man/latest/loginctl.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## App cannot read its own user settings (`software35.security.permission-home`)

**Software area:** security

**Symptom:** User-owned config file reports permission denied.

**Supporting evidence:** File ownership/mode of exact path conflicts with executing UID.

**Counterevidence:** Flatpak sandbox restrictions can differ from filesystem permission issue.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

id

ls -ld ~/.config

ls -la ~/.config

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Only one application folder has wrong ownership

1. Identify exact folder and owner

2. Back up it and correct ownership/permissions ONLY for that app through reviewed user action

3. Test again

**Solution route 2 — only if:** Data belongs to a different user by design

1. Do not recursively chmod/chown home

2. Ask administrator for appropriate group/access or use supported document portal

**Graphical method:** File manager Properties > Permissions if supported.

**Retest (observe only):**

```bash

ls -ld ~/.config

```

**Safety:** Never issue blanket chmod -R 777 or chown of whole home.

**References:** [polkit](https://polkit.pages.freedesktop.org/polkit/polkit.8.html) · [sandbox](https://docs.flatpak.org/en/latest/sandbox-permissions.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## SSH login rejected (`software35.security.ssh-auth`)

**Software area:** security

**Symptom:** SSH server rejects credentials or keys.

**Supporting evidence:** sshd journal indicates exact authentication refusal or authorized_keys ownership issue.

**Counterevidence:** Port reachability or DNS failure precedes authentication entirely.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

systemctl status sshd --no-pager

journalctl -b -u sshd --no-pager -n 120

ss -ltnp

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** User public key not installed or improperly protected

1. Confirm host identity and targeted account

2. Administrator updates only this account authorized_keys and supported permissions

3. Retest without disabling key checks

**Solution route 2 — only if:** Account/policy disallows remote login

1. Review sshd configuration and organizational policy

2. Request approved account access or use local console; do not enable root/password login broadly

**Graphical method:** Administrator-managed SSH settings only.

**Retest (observe only):**

```bash

systemctl status sshd --no-pager

```

**Safety:** Never copy private SSH keys into tickets or logs.

**References:** [sshd](https://man.openbsd.org/sshd_config) · [systemd](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## App repeatedly asks for password after login (`software35.security.secret-store`)

**Software area:** security

**Symptom:** Credential store/secret service cannot unlock.

**Supporting evidence:** Named secret-service or KDE Wallet startup warning matches login/keyring state.

**Counterevidence:** A legitimate app reauthentication/token expiry differs from broken keyring.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

systemctl --user --failed --no-pager

journalctl --user -b --no-pager -n 120

loginctl list-sessions

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Keyring password does not match user login method

1. Use trusted desktop wallet/keyring settings to synchronize intended unlock method

2. Preserve credentials before any reset

3. Test at next normal login

**Solution route 2 — only if:** Only one app token expired

1. Reauthenticate within the original service/app

2. Check app keyring integration and supported updates without resetting whole wallet

**Graphical method:** KDE Wallet Manager or GNOME Passwords and Keys; do not log secrets.

**Retest (observe only):**

```bash

systemctl --user --failed --no-pager

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [logind](https://www.freedesktop.org/software/systemd/man/latest/loginctl.html) · [desktop](https://specifications.freedesktop.org/desktop-entry-spec/latest/)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Kernel module refused due to Secure Boot signature (`software35.security.secureboot-module`)

**Software area:** security

**Symptom:** Third-party module is denied at insertion.

**Supporting evidence:** Kernel logs contain signature/key rejection for exact module and Secure Boot enabled.

**Counterevidence:** Absent device firmware or kernel ABI mismatch can cause different load failure.

**Hardware cross-references:** `hardware34.board.firmware-device-missing` (consult both directions when logs justify it).

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

mokutil --sb-state

journalctl -b -k --no-pager -n 120

uname -r

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Vendor offers correctly signed supported driver

1. Use distro/vendor official signed package and documented enrollment procedure

2. User reviews any new trust enrollment carefully

**Solution route 2 — only if:** No supported signed module

1. Avoid disabling security simply to load untrusted module

2. Use built-in supported driver or hardware alternative and report vendor issue

**Graphical method:** Firmware Secure Boot UI only when user consciously accepts security implications.

**Retest (observe only):**

```bash

mokutil --sb-state

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [kernel](https://docs.kernel.org/admin-guide/kernel-parameters.html) · [selinux](https://docs.fedoraproject.org/en-US/quick-docs/selinux-troubleshooting/)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

# Services

## System service keeps restarting (`software35.services.service-restart-loop`)

**Software area:** services

**Symptom:** systemd reports start-limit-hit for a specific unit.

**Supporting evidence:** Exact named unit repeatedly fails with same root error; status and logs match.

**Counterevidence:** A disabled optional unit alone does not prove failure.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

systemctl --failed --no-pager

systemctl status SERVICE --no-pager

journalctl -b -u SERVICE --no-pager -n 100

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Optional service configuration is invalid

1. Identify precise ExecStart and error

2. Correct only named app config through vendor-supported editor after backup

3. Ask user to restart only affected optional service

**Solution route 2 — only if:** Binary or dependency is missing

1. Find owning package and dependency

2. Use original package manager for supported reinstall/update

3. Avoid disabling unrelated services

**Graphical method:** System Services UI only when installed; package manager only for affected optional package.

**Retest (observe only):**

```bash

systemctl status SERVICE --no-pager

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [systemd](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html) · [journal](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## User session service fails but system service is healthy (`software35.services.user-service-failed`)

**Software area:** services

**Symptom:** Per-user service cannot start.

**Supporting evidence:** systemctl --user shows named failure tied to per-user config/permissions.

**Counterevidence:** The system-level service might be a separate working instance.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

systemctl --user --failed --no-pager

systemctl --user status SERVICE --no-pager

journalctl --user -b --no-pager -n 100

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** User unit override is invalid

1. Record systemctl --user cat output

2. Back up only named user drop-in

3. Correct according to unit docs, then user restarts that service

**Solution route 2 — only if:** Service is managed by an optional app

1. Update/reinstall through app original source if verified

2. Check profile and session environment

3. Report repeatable failure

**Graphical method:** Desktop Autostart / User Services GUI where available.

**Retest (observe only):**

```bash

systemctl --user status SERVICE --no-pager

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [systemd](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html) · [journal](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Socket exists but service never activates (`software35.services.socket-activation`)

**Software area:** services

**Symptom:** A socket/listener is active yet dependent daemon fails on demand.

**Supporting evidence:** Specific systemd socket triggers named service with failed logs.

**Counterevidence:** A healthy idle on-demand service might show inactive until requested.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

systemctl list-sockets --no-pager

systemctl status SERVICE.socket --no-pager

journalctl -b -u SERVICE.service --no-pager -n 80

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Socket unit references missing service

1. Verify actual named unit and package installation

2. Restore only the correct owning optional package using original source

3. Retest intended connection

**Solution route 2 — only if:** Application itself has invalid startup config

1. Use journal failure code to correct supported app config

2. User invokes app-defined reload/restart after reviewing effect

**Graphical method:** System Services viewer.

**Retest (observe only):**

```bash

systemctl status SERVICE.socket --no-pager

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [systemd](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html) · [journal](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Scheduled systemd timer did not fire (`software35.services.timer-not-running`)

**Software area:** services

**Symptom:** Expected scheduled task has no recent execution.

**Supporting evidence:** systemctl list-timers and unit metadata show a missed occurrence.

**Counterevidence:** Persistent=false timers are not intended to replay missed runs by default.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

systemctl list-timers --all --no-pager

systemctl status TIMER.timer --no-pager

journalctl -b -u TIMER.service --no-pager -n 80

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Timer disabled or calendar syntax unexpected

1. Confirm expected schedule and service target

2. User corrects timer config only after backup

3. Enable only optional intended timer

**Solution route 2 — only if:** Timer fired but target service fails

1. Investigate service unit error rather than timer schedule

2. Fix service-specific dependency or access failure

3. Monitor next scheduled run

**Graphical method:** System services/timer settings where provided.

**Retest (observe only):**

```bash

systemctl list-timers --all --no-pager

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [systemd](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html) · [journal](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Unit fails because prerequisite is unavailable (`software35.services.systemd-ordering`)

**Software area:** services

**Symptom:** A service fails with dependency or ordering error.

**Supporting evidence:** systemctl list-dependencies indicates named failed required unit.

**Counterevidence:** Ordering information alone does not prove start deadlock.

**Hardware cross-references:** `hardware34.storage.drive-power-loss` (consult both directions when logs justify it).

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

systemctl list-dependencies SERVICE

systemctl status SERVICE --no-pager

systemctl --failed --no-pager

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Required service truly absent or failed

1. Diagnose prerequisite first

2. Correct just that prerequisite using distro-supported package/service method

3. Retest dependent unit

**Solution route 2 — only if:** Service expects hardware/mount not present

1. Verify dependency requirement and optional nature

2. Have administrator correct documented unit dependencies instead of forcing startup

**Graphical method:** Use the applicable desktop settings or trusted original application interface; do not treat ULSM as a universal system repair tool.

**Retest (observe only):**

```bash

systemctl status SERVICE --no-pager

```

**Safety:** Do not mask dependencies or force target isolation.

**References:** [systemd](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html) · [journal](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Service cannot bind TCP port (`software35.services.port-already-bound`)

**Software area:** services

**Symptom:** Service log reports address already in use.

**Supporting evidence:** ss shows an owning listener occupying exactly configured port.

**Counterevidence:** Firewall blocking is a distinct issue from EADDRINUSE.

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

ss -ltnp

systemctl status SERVICE --no-pager

journalctl -b -u SERVICE --no-pager -n 70

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Another optional app intentionally owns port

1. Identify listener owner and users

2. Configure only optional target service on supported alternative port in its GUI

3. Retest bound address

**Solution route 2 — only if:** Unexpected stale service occupies port

1. Verify owning process/package

2. User stops only confirmed optional conflicting instance gracefully

3. Avoid killing core system processes

**Graphical method:** Service app configuration; users choose ports and acknowledge exposure.

**Retest (observe only):**

```bash

ss -ltnp

```

**Safety:** Do not change unrelated settings, remove core packages, or grant broad privileges as a shortcut.

**References:** [systemd](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html) · [sshd](https://man.openbsd.org/sshd_config)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## Application terminated by out-of-memory killer (`software35.services.oom-killed`)

**Software area:** services

**Symptom:** App closes under memory pressure.

**Supporting evidence:** Kernel journal/cgroup log names killed process and out-of-memory event.

**Counterevidence:** A generic segmentation fault is not necessarily OOM.

**Hardware cross-references:** `hardware34.memory.ecc-uncorrected` (consult both directions when logs justify it).

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

journalctl -b -k --no-pager -n 240

free -h

systemctl --user --failed --no-pager

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Workload exceeds available RAM and swap

1. Close unnecessary heavy workloads normally

2. Lower app workload limits using app settings

3. Check memory availability under normal tasks

**Solution route 2 — only if:** Only one app leaks memory

1. Identify app version, workload and process

2. Update same app source or report leak

3. Avoid changing global OOM policy as first fix

**Graphical method:** Use the applicable desktop settings or trusted original application interface; do not treat ULSM as a universal system repair tool.

**Retest (observe only):**

```bash

free -h

journalctl -b -k --no-pager -n 90

```

**Safety:** Do not disable system OOM protection or force unsafe memory stress.

**References:** [systemd](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html) · [journal](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## System or desktop startup is unusually slow (`software35.services.high-boot-time`)

**Software area:** services

**Symptom:** The desktop or system becomes usable unusually late after a boot, with potential delay before or after userspace services.

**Supporting evidence:** Separate firmware/bootloader/kernel timings from userspace service timings using available, matching boot records.

**Counterevidence:** A slow firmware or kernel stage is not caused by a userspace service merely appearing in the boot report.

**Hardware cross-references:** `hardware34.storage.nvme-timeout` (consult both directions when logs justify it).

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

systemd-analyze time

systemd-analyze critical-chain

systemctl --failed --no-pager

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Optional unit waits for unavailable resource

1. Identify specific dependency and whether it is truly optional

2. User corrects its configuration or service startup mode in supported settings

3. Measure another ordinary boot

**Solution route 2 — only if:** Slow stage predates userspace services

1. Check firmware, disk and kernel errors rather than disabling units blindly

2. Apply official firmware/OS solution only for observed issue

**Graphical method:** Use the applicable desktop settings or trusted original application interface; do not treat ULSM as a universal system repair tool.

**Retest (observe only):**

```bash

systemd-analyze time

```

**Safety:** Do not disable unknown system targets based solely on blame output.

**References:** [analyze](https://www.freedesktop.org/software/systemd/man/latest/systemd-analyze.html) · [systemd](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

## System journal consumes writable disk space (`software35.services.journal-growth`)

**Software area:** services

**Symptom:** Journal storage grows quickly and app/log spam is suspected.

**Supporting evidence:** journalctl --disk-usage large and named unit repeatedly emits identical errors.

**Counterevidence:** Bazzite composefs root apparent fullness must not be mistaken for writable disk pressure.

**Hardware cross-references:** `storage.disk-full` (consult both directions when logs justify it).

**Read-only diagnosis, run only with confirmed context (not automatically authorized for the Troubleshooter):**

```bash

journalctl --disk-usage

df -h /var

journalctl -b -p warning --no-pager -n 120

```

**Routing options:** Terminal (manual) / Universal Linux Terminal (describe → insert only → user Enter) / suitable GUI. ULSM is only offered for supported package tasks.

**Solution route 1 — only if:** Named optional service floods logs

1. Identify actual emitting unit and cause

2. Correct its configuration or update owning app rather than purging evidence

3. Review journal usage after normal operation

**Solution route 2 — only if:** Retention policy is too large for actual writable volume

1. Back up relevant diagnostics

2. User adjusts supported journald quota setting following distro policy

3. Do not vacuum logs before capturing evidence

**Graphical method:** Use the applicable desktop settings or trusted original application interface; do not treat ULSM as a universal system repair tool.

**Retest (observe only):**

```bash

journalctl --disk-usage

df -h /var

```

**Safety:** Do not delete /var/log/journal contents blindly.

**References:** [journal](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html) · [systemd](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html)

**Status:** Documentation draft, not a runtime tool, diagnosis tree, automated repair, or LoRA training sample.

---

