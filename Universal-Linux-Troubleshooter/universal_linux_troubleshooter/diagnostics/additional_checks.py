"""Additional offline, read-only Linux checks.

Deliberately conservative: absence of visible messages is not proof of perfect
hardware. No remote network probes, privileged utilities, changes or shell.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Callable

from ..results import DiagnosticResult, ResultStatus
from .bridge import LocalHost, _result, _unknown, _safe_interface
from .desktop_guidance import network_settings_steps, desktop_settings_steps

JOURNAL = ("journalctl", "-b", "-p", "0..4", "-n", "160", "--no-pager", "--output=json")
GRAPHICS_JOURNAL_SHORT = ("journalctl", "-b", "-p", "0..4", "-n", "40", "--no-pager", "--output=json")
JOURNAL_TINY = ("journalctl", "-b", "-p", "0..4", "-n", "8", "--no-pager", "--output=json")


def _text(host: LocalHost, path: str) -> str | None:
    try:
        return host.read(path)
    except (OSError, ValueError, KeyError):
        return None


def _names(host: LocalHost, path: str) -> tuple[str, ...]:
    try:
        return tuple(host.list_names(path))
    except (OSError, ValueError, KeyError):
        return ()


def _journal(host: LocalHost):
    """Read a bounded sample; distinguish empty logs, denied access, and oversized JSON."""
    notes = ["Source: Linux system journal (current boot; warnings and errors)."]
    attempts = ((160, JOURNAL), (40, GRAPHICS_JOURNAL_SHORT), (8, JOURNAL_TINY))
    for index, (number, command) in enumerate(attempts):
        response = host.command(command)
        stderr = response.err.strip()[:240]
        restricted = any(word in stderr.casefold() for word in
                         ("permission denied", "access denied", "not seeing messages", "insufficient permissions", "no journal files were opened"))
        if restricted:
            notes.append(f"Reading {number} messages: Linux restricted access: {stderr}")
            return None, "Linux did not permit this account to read those messages.", notes
        if response.code == 127:
            notes.append("journalctl is not installed or not available in this environment.")
            return None, "The Linux journal reader is unavailable.", notes
        if response.code != 0:
            reason = "reading timed out" if response.code == 124 else f"reader failed (exit code {response.code})"
            notes.append(f"Reading {number} messages: {reason}. {stderr}".strip())
            if index < len(attempts) - 1 and response.code not in (125, 126):
                continue
            return None, f"The Linux journal reader failed: {reason}.", notes
        if response.truncated:
            notes.append(f"Reading {number} messages: output exceeded the safe limit.")
            if index < len(attempts) - 1:
                continue
            return None, "Even eight recent messages were too large to read safely.", notes
        raw = response.out.strip()
        if not raw or raw == "-- No entries --":
            notes.append(f"Reading {number} messages: no entries visible in this sample.")
            return [], "", notes
        try:
            entries = []
            for line in response.out.splitlines():
                if not line.strip():
                    continue
                obj = json.loads(line)
                if not isinstance(obj, dict) or not isinstance(obj.get("MESSAGE"), str):
                    raise ValueError("Not a readable message")
                entries.append(obj)
            if not entries:
                raise ValueError("No usable records")
        except (ValueError, TypeError):
            notes.append(f"Reading {number} messages: a record was incomplete or unreadable.")
            if index < len(attempts) - 1:
                continue
            return None, "Even a shorter journal sample contained unreadable messages.", notes
        notes.append(f"Read {len(entries)} accessible messages (requested up to {number}).")
        if index > 0:
            notes.append("The full sample was not readable, so only a smaller recent sample was checked.")
        return entries, "", notes
    return None, "The Linux journal could not be read.", notes


def _log_check(host: LocalHost, category: str, check: str, subject: str,
               pattern: str, advice: str) -> DiagnosticResult:
    entries, error, read_notes = _journal(host)
    if entries is None:
        return _result(category, check, ResultStatus.UNKNOWN,
                       f"Could not read recent messages about {subject}",
                       "The check could not finish reading recent Linux warnings: " + error +
                       " This is a problem reading information, not proof that something is broken.",
                       "1. Open Evidence / Logs to see why the messages could not be read.\n"
                       "2. If an app or device is giving you trouble, write down its name and when it happened.\n"
                       "3. You can inspect recent messages yourself with: journalctl -b -p 0..4 -n 40 --no-pager\n"
                       "4. If Linux hides the messages, do not disable security protections just for this test.",
                       read_notes, specific_guidance=True)
    if not entries:
        return _result(category, check, ResultStatus.INFO,
                       "No recent warning or error messages were visible",
                       "The system did not show any warnings or errors for this startup. "
                       "This is a limited view; older or protected messages may not be visible. "
                       "This check did not test the affected hardware or application directly.",
                       "No change is needed based on this result. If a problem still happens, note its time "
                       "and check the logs for that specific app or device.", read_notes, specific_guidance=True)
    regex = re.compile(pattern, re.I)
    matched = [entry for entry in entries if regex.search(
        str(entry.get("SYSLOG_IDENTIFIER", "")) + " " + entry["MESSAGE"])]
    proof = read_notes + [f"Messages read: {len(entries)}; messages about {subject}: {len(matched)}"]
    if matched:
        proof.append(f"Examples: {min(20, len(matched))} of {len(matched)} matching messages are shown below.")
        for item in matched[:20]:
            raw_stamp = item.get("__REALTIME_TIMESTAMP")
            try:
                stamp = datetime.fromtimestamp(int(raw_stamp) / 1_000_000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            except (ValueError, TypeError, OSError, OverflowError):
                stamp = "time not available"
            name = str(item.get("SYSLOG_IDENTIFIER") or item.get("_SYSTEMD_UNIT") or "Linux")[:120]
            proof.append(f"{stamp} | {name} | {item['MESSAGE'][:600]}")
        return _result(category, check, ResultStatus.WARNING,
                       f"Linux recorded {len(matched)} warning or error message(s) about {subject}",
                       "These messages may help explain a problem. Some can be harmless or unrelated, "
                       "and repeated messages may all describe one event. The cause has not been confirmed by this result.",
                       "1. Open 'Evidence / Logs' to read the messages and their times.\n"
                       "2. Check whether you noticed a problem around the same time. A log message alone does not mean something is broken.\n"
                       "3. If the message matches a problem you actually have, use this advice: " + advice + "\n"
                       "4. If you make any change yourself, run this check again to see whether the same message returns.",
                       proof, specific_guidance=True)
    return _result(category, check, ResultStatus.OK,
                   f"No recent warning about {subject} was found in the messages that could be read",
                   "Only a limited sample of recent important system messages was examined. "
                   "No matching message appeared there. Older, hidden or less urgent messages may still exist.",
                   "No changes are needed based on the messages examined. "
                   "Open 'Evidence / Logs' to see how many messages were checked.", proof,
                   specific_guidance=True)


def check_wifi(host: LocalHost) -> DiagnosticResult:
    # NetworkManager is not universal: lack of it is a limitation, not a fault.
    cmd = host.command(("nmcli", "-t", "-f", "DEVICE,TYPE,STATE,CONNECTION", "device", "status"))
    if cmd.code != 0:
        return _result("network", "wifi", ResultStatus.UNKNOWN,
                       "Wi-Fi connection could not be checked",
                       "The usual Wi-Fi information tool is not available on this computer. "
                       "That does not mean Wi-Fi is broken.",
                       "To check your Wi-Fi connection yourself, follow these steps:\n" + network_settings_steps() +
                       "\n\nYou can also open 'Evidence / Logs' to see what the check tried to read.",
                       ["Source: nmcli (local connection status only)", "Result: Wi-Fi status could not be read"],
                       specific_guidance=True)
    lines = [line.strip() for line in cmd.out.splitlines() if line.strip()]
    wifi = [line for line in lines if re.search(r"(^|:)wifi(:|$)", line, re.I)]
    if not wifi:
        return _result("network", "wifi", ResultStatus.INFO,
                       "No Wi-Fi device was shown by the local connection tool",
                       "Wi-Fi might be switched off, absent, or controlled by another program. "
                       "That does not prove anything is broken.",
                       "Follow these steps to check whether Wi-Fi is switched on:\n" + network_settings_steps() +
                       "\n\nThen run this check again. If your computer has no Wi-Fi device, do not change anything.",
                       ["Source: nmcli (local connection status only)", "No Wi-Fi device listed"],
                       specific_guidance=True)
    active = [line for line in wifi if "connected" in line.lower() and "disconnected" not in line.lower()]
    return _result("network", "wifi", ResultStatus.OK if active else ResultStatus.INFO,
                   "A Wi-Fi connection is shown as active" if active else "No active Wi-Fi connection was confirmed",
                   "This is the connection state right now. It does not measure signal strength or prove that Wi-Fi "
                   "stays connected. An unused Wi-Fi adapter may correctly be disconnected.",
                   ("No change is suggested by the Wi-Fi connection shown here. If Wi-Fi drops later, "
                    "note the time and run 'System errors' under 'System, Boot & Updates'. "
                    "This quick check cannot prove Wi-Fi will stay connected. "
                    "Open 'Evidence / Logs' for the connection details."
                    if active else
                    "This check could not confirm an active Wi-Fi connection. The settings can be found here:\n" +
                    network_settings_steps() +
                    "\n\nIf Wi-Fi disconnects later, note the time. Then run 'System errors' under "
                    "'System, Boot & Updates'. This check cannot prove Wi-Fi will stay connected."),
                   ["Source: nmcli (local status; no online test)"] + wifi[:15], specific_guidance=True)


def check_dns(host: LocalHost, *, allow_network: bool = False) -> DiagnosticResult:
    """Check real website-name resolution only after a visible consent dialog.

    getent uses the OS resolver; a cache may satisfy the request, or Linux
    might contact the configured DNS service. It does not fetch a web page.
    """
    if not allow_network:
        return _result(
            "network", "dns", ResultStatus.NOT_RUN,
            "The website name check was not started",
            "This optional test needs permission because looking up a website's name may contact a DNS server. You chose not to run it.",
            "To test website names, select 'Website name check' and click Run selected checks. "
            "Choose Yes in the permission window if you want to run it. No network request was made.",
            ["Website name check", "Your choice: No. No DNS lookup attempted.",
             "Website name: www.mozilla.org (not looked up)."],
            specific_guidance=True,
        )
    import ipaddress
    cmd = host.command(("getent", "ahostsv4", "www.mozilla.org"))
    addresses = []
    for line in cmd.out.splitlines():
        parts = line.split()
        if not parts:
            continue
        try:
            ip = ipaddress.IPv4Address(parts[0])
        except ipaddress.AddressValueError:
            continue
        if str(ip) not in addresses:
            addresses.append(str(ip))
    evidence = ["Website name check", "Your choice: Yes — one DNS lookup was permitted.",
                "Lookup: www.mozilla.org (using your computer's usual name resolver)",
                "Tool: getent ahostsv4; no web page opened or files uploaded.",
                f"Program return code: {cmd.code}"]
    if addresses and cmd.code == 0 and not cmd.truncated:
        evidence.extend(["Found website address(es): " + ", ".join(addresses[:8]),
                         "Scope: The website name resolved now; this does not test web browsing."])
        return _result("network", "dns", ResultStatus.OK,
                       "Website name lookup successful",
                       "Your computer was able to find the network address for www.mozilla.org.",
                       "No changes needed. Open Evidence / Logs to see the address found. "
                       "To check that an outside website can actually be reached, run External connectivity separately.",
                       evidence, specific_guidance=True)
    if cmd.code == 127:
        why = "The tool used to look up website names (getent) is not installed or accessible."
    elif cmd.code == 124:
        why = "The website name lookup did not finish within five seconds."
    elif cmd.truncated:
        why = "The website name lookup returned more data than this check can safely process."
    else:
        why = "Your computer could not find a usable address for the website during this test."
    evidence.append("Reason: " + why)
    if cmd.err.strip():
        evidence.append("Technical message: " + cmd.err.strip()[:240])
    return _result("network", "dns", ResultStatus.UNKNOWN,
                   "Could not confirm the website's address",
                   why + " This alone does not prove that the internet connection is broken.",
                   "1. Open Evidence / Logs to see why the lookup did not finish.\n"
                   "2. Open your computer's network settings:\n" + network_settings_steps() + "\n"
                   "3. Check the network you expect to use. If other websites also fail, run IP configuration and External connectivity.\n"
                   "4. Do not change DNS addresses or reset your router based on this result alone.",
                   evidence, specific_guidance=True)


def check_gateway(host: LocalHost) -> DiagnosticResult:
    cmd = host.command(("ip", "-j", "route", "show", "default"))
    if cmd.code != 0:
        return _unknown("network", "gateway", "Cannot read the local route toward your router.", "ip default route")
    try:
        routes = json.loads(cmd.out)
        if not isinstance(routes, list):
            raise ValueError("Bad routes")
    except (ValueError, TypeError):
        return _unknown("network", "gateway", "The computer's router settings were hard to understand.", "ip default route")
    found = [route for route in routes if isinstance(route, dict)]
    return _result("network", "gateway", ResultStatus.INFO,
                   "A router route is configured" if found else "No router route is currently configured",
                   "A default route tells Linux where to send traffic that leaves the local network. "
                   "This local check does not contact your router or confirm that it works. "
                   "Not every network needs an internet route.",
                   "To find your network connection settings, follow these steps:\n" + network_settings_steps() +
                   "\n\nOpen 'Evidence / Logs' to see the router address Linux knows about. "
                   "A listed address is not proof that your router answers. "
                   "This app has not contacted the router. Do not reset it based only on this result.",
                   ["Source: local routing table (no network packets sent)"] +
                   [f"Router: {route.get('gateway', 'on-link')}, device: {route.get('dev', '?')}" for route in found[:10]],
                   specific_guidance=True)


def check_sensors(host: LocalHost) -> DiagnosticResult:
    observations = []
    for device in _names(host, "/sys/class/thermal"):
        if not re.fullmatch(r"thermal_zone\d+", device):
            continue
        raw = _text(host, f"/sys/class/thermal/{device}/temp")
        if raw is None:
            continue
        try:
            temp = int(raw.strip()) / 1000
        except ValueError:
            continue
        if -40 <= temp <= 180:
            observations.append(f"{device}: {temp:.1f}°C")
    for name in _names(host, "/sys/class/hwmon"):
        if not re.fullmatch(r"hwmon\d+", name):
            continue
        for sensor in _names(host, f"/sys/class/hwmon/{name}"):
            if not re.fullmatch(r"temp\d+_input", sensor):
                continue
            raw = _text(host, f"/sys/class/hwmon/{name}/{sensor}")
            try:
                temp = int((raw or "").strip()) / 1000
            except ValueError:
                continue
            if -40 <= temp <= 180:
                observations.append(f"{name}/{sensor}: {temp:.1f}°C")
            if len(observations) >= 35:
                break
    if not observations:
        return _unknown("hardware", "sensors", "No readable temperature sensors were found. Missing sensors do not mean temperatures are safe.", "Linux /sys sensor readings")
    return _result("hardware", "sensors", ResultStatus.OK,
                   f"Linux provided {len(observations)} temperature reading(s)",
                   "Temperature readings were available from the computer. Different sensors measure different parts and "
                   "use different safe ranges. This simple list alone cannot confirm whether everything is cool enough.",
                   "Open the 'Evidence / Logs' tab below. It lists each temperature that Linux was able to read "
                   "(in °C), along with the name Linux gave that sensor. "
                   "If your computer shuts down or becomes very hot, compare the readings with the safe "
                   "temperature limits from your computer or component maker. "
                   "A temperature listed here is not proof that the hardware is safe. "
                   "Do not change fans or cooling settings based only on this list.",
                   ["Source: local /sys/class/thermal and /sys/class/hwmon sensors"] + observations,
                   specific_guidance=True)


def check_power(host: LocalHost) -> DiagnosticResult:
    return _log_check(host, "hardware", "power", "power or sleep", r"suspend|hibernate|power.?off|thermal.shutdown|acpi.*(fail|error)",
                      "If the computer unexpectedly switches off, write down when it happened. "
                      "A sudden loss of electricity may leave no message at all.")


def check_memory(host: LocalHost) -> DiagnosticResult:
    return _log_check(host, "hardware", "memory", "computer memory", r"out of memory|oom.kill|memory error|ecc.*error|edac.*error|machine.check", 
                      "If crashes continue, save your work and run the memory test recommended by your computer maker. "
                      "A log check cannot replace a proper RAM test.")


def check_hardware_logs(host: LocalHost) -> DiagnosticResult:
    return _log_check(host, "hardware", "hardware_logs", "hardware", r"pcie.*(error|aer)|mce:|hardware error|i/o error|usb.*(fail|error)|thermal.*(fail|error)",
                      "Look for a device name in Evidence / Logs. Check whether that device actually fails before changing drivers or parts.")


def check_fs_logs(host: LocalHost) -> DiagnosticResult:
    return _log_check(host, "storage", "fs_logs", "file storage", r"(ext4|btrfs|xfs|f2fs|ntfs|filesystem|i/o error).*(error|fail|corrupt|read.only)|buffer i/o error|no space left", 
                      "Make a backup of important files if you see repeated storage errors. "
                      "Do not run filesystem repairs automatically; they can require an unmounted drive.")


def check_app_crashes(host: LocalHost) -> DiagnosticResult:
    """Look for recent crash messages AND saved crash-report metadata.

    The coredump list is metadata only. No core memory is extracted, opened,
    debugged or uploaded. Earlier boots may also appear in this bounded list.
    """
    logs = _log_check(host, "applications", "app_crashes", "application crashes",
                      r"segfault|core.dump|coredump|application crash|signal 11|abrt",
                      "Look for the application's name and the time of the crash. First check whether that app is up to date.")
    cmd = host.command(("coredumpctl", "--no-legend", "--no-pager", "-n", "30", "list"))
    if cmd.code == 0 and cmd.out.strip() and not cmd.truncated:
        lines = [line.strip()[:220] for line in cmd.out.splitlines() if line.strip()]
        if lines and not all("no coredumps" in line.lower() for line in lines):
            evidence = list(logs.evidence) + [
                "Source: coredumpctl list (saved application crash records, up to 30; may include earlier restarts).",
                f"Crash records shown: {len(lines)}",
            ] + [f"Crash record {i}: {line}" for i, line in enumerate(lines[:30], 1)]
            # Extract only identifiable executable paths from the saved crash
            # listing; do not pretend an old record proves an active failure.
            # coredumpctl typically includes /usr/bin/program (or Flatpak app
            # paths) on each line. Names are displayed as data, never executed.
            from collections import Counter
            executables = []
            for record in lines:
                paths = re.findall(r"(?:^|\s)(/(?:usr|opt|app|var|home|run)/[^\s]{1,200})", record)
                if paths:
                    name = paths[-1].rstrip(',:')
                    executables.append(name)
            names = Counter(executables)
            affected = [name for name, _ in names.most_common(8)]
            if affected:
                program_list = "\n".join(
                    f"{i}. {name} ({names[name]} saved report{'s' if names[name] != 1 else ''})"
                    for i, name in enumerate(affected, 1))
                diagnosis = f"Saved crash records were found for {len(names)} named program(s)"
                explanation = (
                    "These programs stopped unexpectedly at the times listed in Evidence / Logs:\n"
                    + program_list + "\n\n"
                    "A saved report can come from an earlier session. It does not by itself "
                    "mean the program is failing now."
                )
                first = affected[0].split('/')[-1]
                solution = (
                    f"Troubleshooting {first}: choose the path that matches the current behaviour. "
                    "This crash was recorded previously; it does not prove the application still fails today.\n\n"
                    "OPTION 1 — Update and verify (best first step if the crash still occurs)\n"
                    f"1. Save your work. Open the same software manager that installed {first}.\n"
                    "2. If an update is available for that specific application, install it yourself.\n"
                    f"3. Open {first} again and repeat the same action once. Compare the time with NEW crash reports.\n\n"
                    "OPTION 2 — Isolate the application (if you suspect it affects other work)\n"
                    f"1. Close {first} and repeat the original workflow WITHOUT it running, where possible.\n"
                    "2. If the problem stops, the application may be involved. Back up any settings and files it owns first.\n"
                    "3. For an optional user-installed application only: if you choose to, remove that ONE app through "
                    "the original software manager. Keep application data/settings whenever offered. "
                    "Do not remove system components, shared packages, drivers, or select delete-data.\n"
                    "4. Try the same workflow again. If it works only without that app, its involvement is more likely. "
                    "Reinstall from the original source if needed; a clean uninstall by itself does not prove the cause.\n\n"
                    "OPTION 3 — Report a reproducible crash to the developer\n"
                    f"1. Name of affected application: {first}.\n"
                    "2. Record the installed app version, Linux distribution, desktop, and exactly what action triggers the crash.\n"
                    "3. Copy only the relevant error and crash time from Evidence / Logs. Remove private data before sending it online.\n"
                    "4. Use that app's official project issue tracker or support channel to report the issue. "
                    "The developer can investigate and publish a fix.\n\n"
                    "HOW TO VERIFY: Repeat the original failing action and check for a NEW report after the attempted fix. "
                    "An older saved crash entry may remain even when the app now works. "
                    "The troubleshooter never updates, removes, reinstalls or contacts the developer automatically."
                )
            else:
                diagnosis = f"Linux saved {len(lines)} application crash record(s)"
                explanation = (
                    "One or more programs stopped unexpectedly. Their names could not be "
                    "identified reliably from the available crash list. Previous sessions may "
                    "also be included."
                )
                solution = (
                    "1. Identify the affected program from the saved crash entry in Evidence / Logs.\n"
                    "2. Open that program normally. If it works now, no repair is necessary.\n"
                    "3. If it continues to close, check the software manager for an update to that "
                    "specific application.\n"
                    "4. Repeat the failing action and rerun Application crashes to see if a new "
                    "report was recorded. Do not modify unrelated system services."
                )
            return _result("applications", "app_crashes", ResultStatus.WARNING,
                           diagnosis, explanation, solution, evidence, specific_guidance=True)
    # Fall back to the journal result if the optional metadata tool is missing,
    # refuses access or sees no saved crashes. Do not mistake absence for proof.
    if logs.status == ResultStatus.UNKNOWN:
        evidence = list(logs.evidence)
        if cmd.code == 127:
            evidence.append("Extra crash check unavailable: coredumpctl is not installed.")
        elif cmd.code == 124:
            evidence.append("Extra crash check timed out.")
        elif cmd.code != 0:
            evidence.append("Extra crash check returned no accessible crash list or a tool error.")
        elif cmd.truncated:
            evidence.append("Extra crash list too large to read safely.")
        return _result("applications", "app_crashes", ResultStatus.UNKNOWN,
                       logs.diagnosis,
                       logs.explanation + " Stored application crash records were also checked.",
                       logs.solution, evidence, specific_guidance=True)
    return logs


def check_permissions(host: LocalHost) -> DiagnosticResult:
    return _log_check(host, "applications", "permissions", "access or permissions", r"permission denied|access denied|avc:.*denied|selinux.*(denied|prevent)|apparmor.*denied", 
                      "Check which program was blocked. Security restrictions sometimes work exactly as intended. "
                      "Do not disable SELinux, AppArmor or other protections just to remove a warning.")


def check_gpu(host: LocalHost) -> DiagnosticResult:
    cmd = host.command(("lspci", "-nn"))
    if cmd.code != 0:
        # DRM presence is only weak evidence, so no fake GPU identity.
        nodes = [n for n in _names(host, "/sys/class/drm") if re.fullmatch(r"card\d+", n)]
        if not nodes:
            return _unknown("graphics", "gpu", "Linux graphics hardware details are not available.", "lspci / local DRM devices")
        return _result("graphics", "gpu", ResultStatus.UNKNOWN,
                       f"Linux exposes {len(nodes)} graphics device node(s)",
                       "Linux lists a graphics device, but its name or driver details could not be read. "
                       "This does not say whether graphics work.", "Check your desktop system information for your graphics card name.",
                       ["Source: /sys/class/drm (lspci unavailable)"] + nodes, specific_guidance=True)
    graphics = [l.strip() for l in cmd.out.splitlines() if re.search(r"vga compatible controller|3d controller|display controller", l, re.I)]
    if not graphics:
        return _unknown("graphics", "gpu", "No display controller was visible in the local PCI inventory.", "lspci -nn")
    return _result("graphics", "gpu", ResultStatus.OK,
                   f"Linux listed {len(graphics)} graphics card(s) or controller(s)",
                   "This tells us which devices exist, not whether the current game or desktop is using the right one.",
                   "If a game or screen has problems, run Graphics errors next and compare its messages with this device list.",
                   ["Source: lspci -nn (read-only device list)"] + graphics[:15], specific_guidance=True)


def _graphics_log_entries(output):
    """Return (entries, why_unreadable). Treat truncated data as incomplete.

    A large journalctl JSON record can hit the host's 128 KiB output limit.
    Never treat a partial list as a clean bill of health.
    """
    if output.code != 0:
        if output.code == 127:
            return None, "The program used to read Linux system messages (journalctl) was not found."
        if output.code == 124:
            return None, "Reading the system messages took too long."
        detail = (output.err or "").lower()
        if any(word in detail for word in ("permission", "access denied", "not permitted")):
            return None, "Linux did not allow this account to read these system messages."
        return None, "Linux could not provide its system messages (reader returned an error)."
    if getattr(output, "truncated", False):
        return None, "The list of system messages was too long to read completely."
    data = output.out.strip()
    if not data or data == "-- No entries --":
        if any(word in output.err.casefold() for word in ("not seeing messages", "permission denied", "access denied", "insufficient permissions", "no journal files were opened")):
            return None, "Linux did not allow this user to read the system messages."
        return [], ""
    entries = []
    try:
        for line in output.out.splitlines():
            if not line.strip():
                continue
            item = json.loads(line)
            if not isinstance(item, dict) or not isinstance(item.get("MESSAGE"), str):
                raise ValueError("Not a readable journal message")
            entries.append(item)
    except (ValueError, TypeError):
        return None, "Linux returned an incomplete or unreadable list of system messages."
    if not entries:
        return [], ""
    return entries, ""


def check_render(host: LocalHost) -> DiagnosticResult:
    """Read graphics warnings without mistaking a broken journal read for a GPU fault."""
    primary, first_reason = _graphics_log_entries(host.command(JOURNAL))
    limited = False
    if primary is None:
        # The 160-message JSON output can exceed our fixed output limit.
        # Try a bounded smaller sample; it is always described as smaller.
        if "not found" in first_reason or "did not allow" in first_reason:
            entries, retry_reason = None, ""
        else:
            entries, retry_reason = _graphics_log_entries(host.command(GRAPHICS_JOURNAL_SHORT))
        limited = entries is not None
        if entries is None and "not found" not in first_reason and "did not allow" not in first_reason and "did not allow" not in retry_reason:
            tiny, tiny_reason = _graphics_log_entries(host.command(JOURNAL_TINY))
            if tiny is not None:
                entries, limited = tiny, True
            else:
                retry_reason += " A final eight-message reading also failed: " + tiny_reason
    else:
        entries, retry_reason = primary, ""

    if entries is None:
        detail = first_reason if not retry_reason else first_reason + " A second, smaller reading also failed: " + retry_reason
        return _result(
            "graphics", "render", ResultStatus.UNKNOWN,
            "Could not finish checking for graphics errors",
            "The app could not read enough system messages to check for recent graphics problems. "
            "This does not mean your graphics card is faulty. " + detail,
            "1. Open 'Evidence / Logs' to see why this check could not finish.\n"
            "2. If your screen freezes, flickers or a game closes unexpectedly, write down the time.\n"
            "3. Open 'System, Boot & Updates', run 'System errors' and look for messages around that time.\n"
            "4. Do not reinstall graphics drivers or change security settings just because this check says UNKNOWN.",
            ["Source: recent Linux system messages (journalctl, current startup)",
             "Check result: incomplete — no graphics problem has been proven",
             "Reason: " + detail,
             "No drivers, settings or permissions were changed."], specific_guidance=True,
        )

    if not entries:
        return _result("graphics", "render", ResultStatus.INFO,
                       "No graphics warning messages were visible",
                       "Linux did not show recent system warning messages in this reading. "
                       "That does not prove that the graphics card or driver is problem-free.",
                       "No change is needed based on this result. If your display has a problem, note when it happens "
                       "and check newer messages in System errors.",
                       ["Source: recent Linux system messages", "No visible journal entries were returned."], specific_guidance=True)
    pattern = re.compile(r"\b(amdgpu|i915|xe\.drm|nouveau|nvidia|drm|gpu|vulkan|mesa)\b", re.I)
    matching = [e for e in entries if pattern.search(
        str(e.get("SYSLOG_IDENTIFIER", "")) + " " + str(e.get("_SYSTEMD_UNIT", "")) + " " + e["MESSAGE"])]
    evidence = ["Source: recent Linux system messages (journalctl, current startup)",
                f"System messages read: {len(entries)}",
                f"Graphics-related messages found: {len(matching)}"]
    if limited:
        evidence.append("Note: The larger log list could not be read (" + first_reason + "). A smaller sample was used.")
    if matching:
        evidence.append(f"Examples: {min(len(matching), 20)} of {len(matching)} graphics-related messages are shown below.")
        for item in matching[:20]:
            stamp = "time not available"
            try:
                stamp = datetime.fromtimestamp(int(item.get("__REALTIME_TIMESTAMP")) / 1_000_000,
                                              tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            except (TypeError, ValueError, OSError, OverflowError):
                pass
            source = str(item.get("SYSLOG_IDENTIFIER") or item.get("_SYSTEMD_UNIT") or "Linux")[:100]
            evidence.append(f"{stamp} | {source} | {item['MESSAGE'][:600]}")
        return _result(
            "graphics", "render", ResultStatus.WARNING,
            f"Found {len(matching)} recent graphics-related warning or error message(s)",
            "Linux saved one or more messages mentioning the graphics system. "
            "They may relate to a screen or game problem, but a message alone does not prove a graphics fault. "
            "Repeated messages may describe the same event.",
            "1. Open 'Evidence / Logs' and look at the actual messages and times.\n"
            "2. Did your screen freeze, flicker or did a game close at the same time? If not, no repair is suggested yet.\n"
            "3. If the times match, run 'System errors' under 'System, Boot & Updates' for more context.\n"
            "4. Do not replace drivers or change display settings based on a warning alone. "
            "If you make a manual change for a confirmed issue, run this check again.",
            evidence, specific_guidance=True,
        )

    return _result(
        "graphics", "render", ResultStatus.OK,
        "No graphics-related warnings were found in the messages checked",
        f"No graphics-related warnings appeared among the {len(entries)} recent messages examined. "
        "No repair is suggested by this result.",
        "No changes are needed based on this check. Open 'Evidence / Logs' if you want to see how many messages were examined.",
        evidence, specific_guidance=True,
    )


def check_display(host: LocalHost) -> DiagnosticResult:
    nodes = []
    for name in _names(host, "/sys/class/drm"):
        if not re.fullmatch(r"card\d+-[A-Za-z0-9_.-]+", name):
            continue
        status = _text(host, f"/sys/class/drm/{name}/status")
        if status:
            nodes.append(f"{name}: {status.strip()}")
    if not nodes:
        return _result("graphics", "display", ResultStatus.UNKNOWN,
                       "Screen connections could not be checked",
                       "Linux did not show readable screen connection details. This can happen with virtual screens or different graphics drivers. It does not mean your screen is broken.",
                       "If a monitor is missing, find your screen settings:\n" + desktop_settings_steps("display") +
                       "\n\nOpen Evidence / Logs to see what Linux could read. If a cable is connected, "
                       "check it on both ends. Do not change graphics drivers based on this result.",
                       ["Source: /sys/class/drm/*/status", "No readable screen connection entries"], specific_guidance=True)
    return _result("graphics", "display", ResultStatus.OK,
                   f"Linux reported {len(nodes)} screen connection(s)",
                   "This describes which screen plugs Linux can see. It does not show your chosen resolution, "
                   "scaling or full KDE/GNOME/Xfce screen settings.",
                   "No changes needed based on this list. Open Evidence / Logs to see which monitor plugs Linux detected. "
                   "If a screen you want to use is missing, open its settings using these steps:\n" +
                   desktop_settings_steps("display") +
                   "\n\nA 'disconnected' entry can also be a plug you are not using.",
                   ["Source: /sys/class/drm/*/status (local connection data)"] + nodes[:30], specific_guidance=True)


def check_audio_devices(host: LocalHost) -> DiagnosticResult:
    content = _text(host, "/proc/asound/cards")
    if content is None:
        return _result("audio", "audio_devices", ResultStatus.UNKNOWN,
                       "Sound hardware could not be listed",
                       "The usual sound-card list was not readable. USB and Bluetooth sound might still work.",
                       "Find your sound settings with these steps:\n" + desktop_settings_steps("sound") +
                       "\n\nTry playing a sound yourself. A missing list does not mean your speakers are broken.",
                       ["Source: /proc/asound/cards", "Cannot read sound card list"], specific_guidance=True)
    if not content.strip() or "no soundcards" in content.lower():
        return _result("audio", "audio_devices", ResultStatus.INFO,
                       "No sound hardware was shown in this list",
                       "This list can be empty even when USB, Bluetooth or virtual audio is working.",
                       "Find your sound settings with these steps:\n" + desktop_settings_steps("sound") +
                       "\n\nIf sound works, no change is needed.",
                       ["Source: /proc/asound/cards", "No ALSA sound cards listed"], specific_guidance=True)
    return _result("audio", "audio_devices", ResultStatus.OK,
                   "Linux lists sound hardware on this computer",
                   "This confirms that local sound devices are listed, but not whether you can hear sound "
                   "or whether the correct speaker is selected.",
                   "No repair is needed just because Linux lists this sound hardware. "
                   "If you cannot hear anything, find your sound settings:\n" + desktop_settings_steps("sound") +
                   "\n\nChoose your speakers or headphones, check the volume, and play a test sound. "
                   "If that does not help, run 'Audio services' next.",
                   ["Source: /proc/asound/cards"] + content.splitlines()[:24], specific_guidance=True)


def check_audio_services(host: LocalHost) -> DiagnosticResult:
    info = []
    for unit in ("pipewire.service", "wireplumber.service", "pulseaudio.service"):
        cmd = host.command(("systemctl", "--user", "is-active", unit))
        if cmd.code == 127 or cmd.code == 124:
            continue
        info.append((unit, cmd.out.strip() or "unavailable"))
    if not info:
        return _unknown("audio", "audio_services", "Could not ask the session's sound services for their status.", "systemctl --user")
    active = [name for name, status in info if status == "active"]
    return _result("audio", "audio_services", ResultStatus.OK if active else ResultStatus.INFO,
                   "At least one sound service is running" if active else "No active sound service was confirmed",
                   "Different Linux desktops use different sound services. An inactive service may be unused. "
                   "Running sound services do not prove the speakers or microphone work.",
                   "If sound works, no change is needed. If you cannot hear anything, open your sound settings:\n" +
                   desktop_settings_steps("sound") +
                   "\n\nChoose the intended output and try playing a sound. "
                   "If it still fails, note when it happened and run 'System errors' in System, Boot & Updates.",
                   ["Source: systemctl --user is-active (local session)"] +
                   [f"{name}: {state}" for name, state in info], specific_guidance=True)


def check_bluetooth(host: LocalHost) -> DiagnosticResult:
    adapters = [n for n in _names(host, "/sys/class/bluetooth") if re.fullmatch(r"hci\d+", n)]
    service = host.command(("systemctl", "is-active", "bluetooth.service"))
    state = service.out.strip() or "not available"
    if not adapters:
        return _result("audio", "bluetooth", ResultStatus.INFO,
                       "No Bluetooth adapter was shown in the available device list",
                       "Some computers do not have Bluetooth. Others may have it turned off or controlled by another service. This does not mean anything is broken.",
                       "If you use Bluetooth, open its settings with these steps:\n" + desktop_settings_steps("bluetooth") +
                       "\n\nIf you do not use Bluetooth, you do not need to change anything.",
                       ["Source: /sys/class/bluetooth", "No Bluetooth adapter listed"], specific_guidance=True)
    return _result("audio", "bluetooth", ResultStatus.OK if state == "active" else ResultStatus.INFO,
                   "A Bluetooth adapter is visible" + (" and the service is running" if state == "active" else ""),
                   "This check examined the Bluetooth adapter and its background service. "
                   "This does not test pairing or whether headphones actually play sound.",
                   "If Bluetooth works, no changes are needed. If a device will not connect, open Bluetooth settings:\n" +
                   desktop_settings_steps("bluetooth") +
                   "\n\nSelect your device and check its connection. If it still fails, note the message shown "
                   "and run 'System errors' under System, Boot & Updates.",
                   ["Source: /sys/class/bluetooth and local service status", f"Bluetooth service: {state}"] + adapters,
                   specific_guidance=True)


def check_vm_backend(host: LocalHost) -> DiagnosticResult:
    nodes = [path for path in ("/dev/kvm", "/run/libvirt/libvirt-sock", "/var/run/libvirt/libvirt-sock") if host.exists(path)]
    units = []
    for unit in ("libvirtd.service", "virtqemud.service"):
        cmd = host.command(("systemctl", "is-active", unit))
        if cmd.code != 127:
            units.append(f"{unit}: {cmd.out.strip() or 'unknown'}")
    if not nodes and not any(line.endswith(": active") for line in units):
        return _result("virtualization", "vm_backend", ResultStatus.INFO,
                       "No active virtual-machine system was found",
                       "This is normal when you do not use virtual machines. It is not a computer fault.",
                       "Nothing needs to be changed if you do not use virtual machines. If a virtual machine fails to start, open its own app and read the error shown there.",
                       ["Source: /dev/kvm and local libvirt services", "No active KVM/libvirt item found"] + units, specific_guidance=True)
    return _result("virtualization", "vm_backend", ResultStatus.OK,
                   "Linux found signs of virtual machine support",
                   "The device or service is present. It does not prove any virtual machine is running correctly.",
                   "If a VM fails to start, check its own error message in your VM management application.",
                   ["Source: local KVM and libvirt presence"] + nodes + units, specific_guidance=True)


def check_vm_network(host: LocalHost) -> DiagnosticResult:
    cmd = host.command(("ip", "-j", "link", "show"))
    if cmd.code != 0:
        return _unknown("virtualization", "vm_network", "Could not read virtual network connections.", "ip -j link show")
    try:
        links = json.loads(cmd.out)
        if not isinstance(links, list):
            raise ValueError("Not a list")
    except (ValueError, TypeError):
        return _unknown("virtualization", "vm_network", "Virtual network connections could not be understood.", "ip -j link show")
    known = [f"{o.get('ifname')} ({o.get('operstate', 'unknown')})" for o in links if isinstance(o, dict) and
             re.match(r"^(virbr|vnet|veth|docker|podman|cni|br-)", str(o.get("ifname", "")))]
    if not known:
        return _result("virtualization", "vm_network", ResultStatus.INFO,
                       "No common virtual-network connections were found",
                       "This is normal when your computer is not running virtual machines or containers. Custom network names may not appear in this quick check.",
                       "No change is needed if you do not use virtual machines or containers.",
                       ["Source: ip -j link show", "No common virtual-network names found"], specific_guidance=True)
    return _result("virtualization", "vm_network", ResultStatus.OK,
                   f"Found {len(known)} possible virtual network connection(s)",
                   "These connections may belong to virtual machines or containers. "
                   "Their presence does not prove a guest can reach the network.",
                   "If a virtual machine cannot connect, check its virtual adapter and bridge settings in its own manager.",
                   ["Source: ip -j link show (local list)"] + known[:30], specific_guidance=True)


def check_containers(host: LocalHost) -> DiagnosticResult:
    paths = [p for p in ("/usr/bin/podman", "/usr/bin/docker", "/usr/bin/distrobox", "/usr/local/bin/podman",
                         "/usr/local/bin/docker", "/run/podman/podman.sock", "/var/run/docker.sock") if host.exists(p)]
    if not paths:
        return _result("virtualization", "containers", ResultStatus.INFO,
                       "No common container program was found",
                       "Not having Docker, Podman or similar software installed is normal if you do not use containers.",
                       "No change is needed. If you were looking for a specific container app, check whether that program is installed.",
                       ["Source: checked common local container program and socket paths", "No matching program or socket found"], specific_guidance=True)
    return _result("virtualization", "containers", ResultStatus.OK,
                   "Linux has one or more container tools installed",
                   "This is only a list of installed tools. It does not list running containers or prove they work.",
                   "If a container cannot start, open the container application and read its specific error message.",
                   ["Source: local program/socket presence"] + paths, specific_guidance=True)


def check_boot(host: LocalHost) -> DiagnosticResult:
    # Never claim to inspect prior boots when only current-boot logs are read.
    return _log_check(host, "system", "boot", "starting the computer", r"failed to start|dependency failed|timed out waiting|boot.*fail|emergency mode", 
                      "Check whether the message happened during this boot. "
                      "For previous start-ups, older journal records may not be available.")


def check_updates(host: LocalHost) -> DiagnosticResult:
    # No remote update search; an update check would otherwise contact servers.
    reboot = host.exists("/run/reboot-required") or host.exists("/var/run/reboot-required")
    ostree = host.exists("/run/ostree-booted")
    proof = ["Source: local reboot marker and atomic Linux presence (no update servers contacted)",
             f"Reboot reminder present: {'yes' if reboot else 'no'}",
             f"Atomic Linux (OSTree) detected: {'yes' if ostree else 'no'}"]
    if ostree:
        cmd = host.command(("rpm-ostree", "status", "--json"))
        if cmd.code == 0:
            try:
                state = json.loads(cmd.out)
                deployments = state.get("deployments", [])
                if isinstance(deployments, list):
                    proof.append(f"Available local system versions: {len(deployments)}")
                    pending = any(isinstance(d, dict) and not d.get("booted", False) and d.get("staged", False) for d in deployments)
                    if pending:
                        return _result("system", "updates", ResultStatus.WARNING,
                                       "A new Linux system version is ready to be used after restarting",
                                       "Linux shows a prepared system version that is not currently running. "
                                       "This check does not search update servers for new releases.",
                                       "Save your work and restart at a time you choose, following your distribution's guidance.", proof,
                                       specific_guidance=True)
            except (ValueError, TypeError):
                proof.append("Could not understand local rpm-ostree status")
        else:
            proof.append("Local rpm-ostree status unavailable")
    if reboot:
        return _result("system", "updates", ResultStatus.WARNING,
                       "Linux says a restart may be needed",
                       "A local marker asks for a restart after some change. "
                       "This does not tell us whether newer updates are available online.",
                       "Save your work and restart when convenient, following your Linux distribution's advice.",
                       proof, specific_guidance=True)
    return _result("system", "updates", ResultStatus.INFO,
                   "No restart reminder was found in local records",
                   "This check reads existing local restart reminders and, on supported atomic Linux systems, "
                   "locally stored update information. This application does not contact update servers "
                   "during this check. No local pending update was detected, but newer releases may still be available.",
                   "No repair is needed based on this result. To check for newly available updates, "
                   "open your distribution's usual Software Update application when you choose.",
                   proof, specific_guidance=True)


ADDITIONAL_READY_CHECKS: dict[tuple[str, str], Callable[[LocalHost], DiagnosticResult]] = {
    ("network", "wifi"): check_wifi,
    ("network", "dns"): check_dns,
    ("network", "gateway"): check_gateway,
    ("hardware", "sensors"): check_sensors,
    ("hardware", "power"): check_power,
    ("hardware", "memory"): check_memory,
    ("hardware", "hardware_logs"): check_hardware_logs,
    ("storage", "fs_logs"): check_fs_logs,
    ("applications", "app_crashes"): check_app_crashes,
    ("applications", "permissions"): check_permissions,
    ("graphics", "gpu"): check_gpu,
    ("graphics", "render"): check_render,
    ("graphics", "display"): check_display,
    ("audio", "audio_devices"): check_audio_devices,
    ("audio", "audio_services"): check_audio_services,
    ("audio", "bluetooth"): check_bluetooth,
    ("virtualization", "vm_backend"): check_vm_backend,
    ("virtualization", "vm_network"): check_vm_network,
    ("virtualization", "containers"): check_containers,
    ("system", "boot"): check_boot,
    ("system", "updates"): check_updates,
}
