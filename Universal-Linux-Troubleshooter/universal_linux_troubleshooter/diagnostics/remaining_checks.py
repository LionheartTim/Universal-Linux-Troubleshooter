"""Two optional diagnostic checks, never repairs.

An external connection is NEVER made unless the caller explicitly sets
allow_network=True following an informed, user-initiated choice. SMART uses a
bounded, non-privileged, read-only command; no drive tests are started.
"""
from __future__ import annotations

import json
import re
from ..results import DiagnosticResult, ResultStatus
from .bridge import LocalHost, _result, _unknown

DISKS = ("lsblk", "-J", "-b", "-o", "NAME,TYPE,SIZE,MOUNTPOINT,MODEL,RO")
# Block devices only; never partitions, root mount paths, loop, zram, or arbitrary strings.
DRIVE_NAME = re.compile(r"(?:sd[a-z]{1,3}|hd[a-z]{1,3}|vd[a-z]{1,3}|xvd[a-z]{1,3}|nvme\d{1,3}n\d{1,3}|mmcblk\d{1,3})\Z")
MAX_DISKS = 8


def check_drive_health(host: LocalHost) -> DiagnosticResult:
    """Try reading the SMART health summary without invoking a drive self-test."""
    response = host.command(DISKS)
    if response.code != 0 or response.truncated:
        return _unknown("storage", "health", "The computer's disk list could not be read completely.", "lsblk")
    try:
        devices = json.loads(response.out)["blockdevices"]
        if not isinstance(devices, list):
            raise ValueError("Invalid disk list")
    except (ValueError, KeyError, TypeError):
        return _unknown("storage", "health", "The disk information returned by Linux could not be interpreted safely.", "lsblk")

    selected = list(dict.fromkeys(str(d.get("name", "")) for d in devices if isinstance(d, dict)
                and d.get("type") == "disk" and DRIVE_NAME.fullmatch(str(d.get("name", "")))))
    # Do not silently drop disks if we would exceed the bounded scan size.
    if len(selected) > MAX_DISKS:
        return _unknown("storage", "health", "There are more disks than this quick check can safely inspect. Review each disk manually.", "lsblk")
    if not selected:
        return _unknown("storage", "health", "No supported physical disk was found in the disk list. USB drives, virtual disks and some controllers may need another tool.", "lsblk")

    evidence = ["Source: lsblk device list and smartctl SMART information, read-only; no disk self-tests started.",
                f"Drives found for this test: {len(selected)}."]
    passed, failed, unclear, history = [], [], [], []
    causes = []
    by_name = {str(d.get("name", "")): d for d in devices if isinstance(d, dict)}
    for name in selected:
        model = str(by_name.get(name, {}).get("model") or "model not reported").strip()[:90]
        evidence.append(f"Disk /dev/{name}: {model}")
        cmd = host.command(("smartctl", "-j", "-H", "-A", "-n", "standby", "/dev/" + name))
        if cmd.truncated or not cmd.out.strip():
            unclear.append(name)
            if cmd.code == 127:
                reason = "the smartctl tool is not installed"
            elif cmd.code == 124:
                reason = "the disk did not answer within the time limit"
            elif cmd.code in (125, 126):
                reason = "the disk information could not be accessed"
            else:
                reason = "SMART information was not available (for example permission denied, sleeping or unsupported hardware)"
            causes.append(reason)
            evidence.append(f"{name}: Could not read drive health: {reason}.")
            if cmd.err.strip():
                evidence.append(f"{name}: System message: {cmd.err.strip()[:250]}")
            continue
        try:
            report = json.loads(cmd.out)
            if not isinstance(report, dict):
                raise ValueError("Bad health record")
        except (TypeError, ValueError):
            unclear.append(name)
            causes.append("the disk returned data that could not be understood")
            evidence.append(f"{name}: Drive returned health data that could not be understood.")
            continue
        status = report.get("smart_status")
        passed_flag = status.get("passed") if isinstance(status, dict) else None
        bits = cmd.code
        # smartctl's exit codes are a bitmask; 0x18 indicates an impending failure.
        # Command/device/read failures take precedence over all SMART
        # health bits or JSON fields, even when a wrapper returned some data.
        # Otherwise a timed-out smartctl command (124 = 0x7c) may be
        # mistakenly classified as a disk failure by its 0x18 bits.
        if type(bits) is not int or not 0 <= bits <= 255 or bits & 0x07:
            unclear.append(name)
            label = "SMART reading failed or was incomplete"
        elif passed_flag is False or bits & 0x18:
            failed.append(name)
            label = "Drive reported a possible failure"
        elif bits & 0xE0:
            history.append(name)
            label = "Drive reports past errors or failed tests"
        elif passed_flag is True:
            passed.append(name)
            label = "Drive did not report a failure in this SMART reading"
        else:
            unclear.append(name)
            label = "SMART status was not available"
        if name in unclear:
            messages = report.get("messages", [])
            if isinstance(messages, list):
                for message in messages[:2]:
                    if isinstance(message, dict) and isinstance(message.get("string"), str):
                        evidence.append(f"{name}: SMART message: {message['string'][:240]}")
                        causes.append(message['string'][:110])
        evidence.append(f"{name}: {label}; smartctl exit code: {bits}")
        nvme = report.get("nvme_smart_health_information_log", {})
        if isinstance(nvme, dict) and name not in unclear:
            warning = nvme.get("critical_warning")
            if type(warning) is int and warning > 0:
                if name in passed:
                    passed.remove(name)
                if name not in failed:
                    failed.append(name)
                evidence.append(f"{name}: NVMe controller reports critical warning code {warning}.")

    if failed:
        return _result("storage", "health", ResultStatus.PROBLEM,
                       f"A drive reported a possible serious problem: {', '.join(failed)}",
                       "A disk's built-in health information warns that something may be wrong. "
                       "It does not identify exactly which files are affected." +
                       (" Additional disks could not be checked: " + ", ".join(unclear) + "." if unclear else ""),
                       "1. Save important files to another drive or backup location as soon as you can.\n"
                       "2. Open Evidence / Logs to find the name of the affected disk.\n"
                       "3. Ask an experienced person or the disk manufacturer's support to check the drive before replacing it.\n"
                       "4. Do not run repair commands or long disk tests before safeguarding your files.", evidence,
                       specific_guidance=True)
    if history:
        return _result("storage", "health", ResultStatus.WARNING,
                       f"Some drives report earlier errors: {', '.join(history)}",
                       "The drive recorded errors or failed tests in the past. It may still be working. "
                       "These reports should be reviewed rather than ignored." +
                       (" Additional disks could not be checked: " + ", ".join(unclear) + "." if unclear else ""),
                       "1. Back up important files.\n2. Open Evidence / Logs for the disk names.\n"
                       "3. Seek advice about the individual disk before trying any repair or self-test.", evidence,
                       specific_guidance=True)
    if unclear:
        evidence.append(f"Completed SMART readings: {len(passed)}; incomplete: {len(unclear)}; warning history: {len(history)}.")
        read_only_commands = "\n".join("   smartctl -H /dev/" + name for name in unclear)
        why = "; ".join(dict.fromkeys(causes)) if causes else "the disk did not report a complete SMART health result"
        return _result("storage", "health", ResultStatus.UNKNOWN,
                       f"Could not finish the health check for {len(unclear)} of {len(selected)} disk(s)",
                       f"Linux found {len(selected)} disk(s). This check attempted to read built-in disk health information, "
                       f"but could not finish for: {', '.join('/dev/' + n for n in unclear)}. "
                       f"The reason reported was: {why[:240]}. This does not mean the disks are broken.",
                       "1. Open Evidence / Logs. Find the specific disk and the reason its health could not be read.\n"
                       "2. If it says 'smartctl is not installed', the optional smartmontools package is needed. "
                       "You can ask your distribution's software manager to install it.\n"
                       "3. Some disk controllers need administrator permission for a health reading. "
                       "This app will not request that permission. If you know how to use the terminal, "
                       "the read-only command for the disk(s) that could not be checked is:\n" +
                       read_only_commands + "\n"
                       "4. Do not assume a disk is healthy when its status is unknown. "
                       "If files disappear or a disk makes unusual noises, back up your important files first.\n"
                       "5. After the tool or permissions are available, run this check again. "
                       "No disk self-tests or repairs will be started by this app.", evidence,
                       specific_guidance=True)
    return _result("storage", "health", ResultStatus.OK,
                   f"No SMART failure was reported by the {len(passed)} disk(s) that were checked",
                   "The disks answered this short health check without reporting a known failure. "
                   "Even a good SMART result cannot guarantee that a disk will not fail later.",
                   "No repair is suggested by this reading. Keep normal backups of important files. "
                   "Open Evidence / Logs if you want to see which disks were checked.", evidence,
                   specific_guidance=True)


def check_external(host: LocalHost, *, allow_network: bool = False) -> DiagnosticResult:
    """One TLS handshake to a fixed outside hostname, only with explicit consent."""
    if not allow_network:
        return _result("network", "external", ResultStatus.NOT_RUN,
                       "The internet test was not started",
                       "You did not allow this optional internet test. No connection was made. This result does not tell us whether your internet is working.",
                       "If you want to test the internet connection, select 'External connectivity' again, click 'Run selected checks' and choose Yes. Otherwise, your other checks work offline.",
                       ["Internet connection test", "Your choice: No — the test was not started.",
                        "Website: www.mozilla.org (not contacted)",
                        "Result: No connection was attempted. No information was sent."],
                       specific_guidance=True)
    # The host adapter bounds the timeout and only contacts the fixed destination.
    try:
        reachable, detail = host.external_tls_probe()
    except (OSError, ValueError, TimeoutError):
        reachable, detail = False, "The connection could not be completed."
    evidence = ["Internet connection test", "Your choice: Yes — you allowed one connection test.",
                "Website tested: www.mozilla.org", "Connection type: secure TLS connection on port 443.",
                "Result: " + ("Connection succeeded." if reachable else "Could not confirm a connection."),
                "Technical detail: " + str(detail)[:300],
                "Privacy: No logs, system data or files were sent. The site may see your public IP address.",
                "Test scope: One secure connection to www.mozilla.org at the time of this test."]
    if reachable:
        return _result("network", "external", ResultStatus.OK,
                       "Internet connection successful",
                       "Your computer connected securely to a website on the internet. "
                       "The connection worked during this test, and no connection problem was found.",
                       "No changes needed. Your internet connection passed this test. "
                       "You can see the website and test details under Evidence / Logs.",
                       evidence, specific_guidance=True)
    return _result("network", "external", ResultStatus.UNKNOWN,
                   "The external connection could not be confirmed",
                   "The website did not answer this short test. It could be blocked, temporarily unavailable, "
                   "or your network may have a problem. This result alone cannot identify your internet provider as the cause.",
                   "1. Run 'IP configuration' and 'Local gateway' to look at local settings.\n"
                   "2. Try opening a familiar website in your normal web browser.\n"
                   "3. If it also fails on a second device, check your router's status lights and internet connection.\n"
                   "4. Contact your internet provider only if your local network appears to work but the internet remains unavailable.",
                   evidence, specific_guidance=True)
