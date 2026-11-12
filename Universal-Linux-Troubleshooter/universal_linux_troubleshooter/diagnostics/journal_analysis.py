"""Conservative, non-AI grouping of structured journald events.

This module does not declare a system defect based on log severity alone and
never turns a log message into a system-modifying shell command.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from .journal_solutions import classify_system_message
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import re


@dataclass(frozen=True)
class JournalReport:
    count: int
    diagnosis: str
    explanation: str
    solution: str
    evidence: tuple[str, ...]
    recognized_areas: tuple[str, ...] = ()
    observed_areas: tuple[str, ...] = ()


def _as_string(value: object, max_chars: int = 650) -> str:
    if isinstance(value, str):
        return value[:max_chars]
    return ""


def _subsystem(entry: dict) -> str:
    message = _as_string(entry.get("MESSAGE")).lower()
    tag = _as_string(entry.get("SYSLOG_IDENTIFIER"), 120).lower()
    unit = _as_string(entry.get("_SYSTEMD_UNIT"), 120).lower()
    hay = f"{tag} {unit} {message}"
    if any(marker in hay for marker in ("selinux", "setroubleshoot", "avc: denied", "audit: avc")):
        return "SELinux / access control"
    if any(marker in hay for marker in ("bluetooth", "bluez", "avctp", "a2dp", "l2cap")):
        return "Bluetooth"
    if any(marker in hay for marker in ("i/o error", "btrfs", "ext4-fs error", "nvme", "ata error")):
        return "Storage / filesystem"
    if any(marker in hay for marker in ("networkmanager", "wpa_supplicant", "iwd", "dhcp")):
        return "Network"
    if any(marker in hay for marker in ("amdgpu", "nvidia", "i915", "nouveau", "drm:")):
        return "Graphics"
    if tag:
        return "Service: " + tag
    if unit:
        return "Unit: " + unit
    if entry.get("_TRANSPORT") == "kernel":
        return "Kernel"
    return "Other / unidentified"


def _fingerprint(message: str) -> str:
    """Collapse only obvious volatile IDs; keep semantically different errors separate."""
    value = message.lower()
    value = re.sub(r"\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b", "<id>", value)
    value = re.sub(r"\b0x[0-9a-f]+\b", "<hex>", value)
    value = re.sub(r"\b(?:pid|process)\s*[:=]?\s*\d+\b", "pid <number>", value)
    return value[:350]


def _timestamp(entry: dict) -> str:
    raw = entry.get("__REALTIME_TIMESTAMP")
    if raw is None:
        return "time unavailable"
    try:
        stamp = int(raw) / 1_000_000
        return datetime.fromtimestamp(stamp, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    except (OverflowError, ValueError, TypeError, OSError):
        return "time unavailable"


def analyze_journal_json(raw: str) -> JournalReport:
    """Parse `journalctl --output=json`, one event per line.

    Raises ValueError for malformed/truncated JSON instead of returning a
    potentially misleading partial diagnosis.
    """
    entries: list[dict] = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError("Journal data was incomplete or not valid JSON") from exc
        if not isinstance(event, dict):
            raise ValueError("Journal contained an unexpected record")
        entries.append(event)
    if not entries:
        raise ValueError("No journal events were visible")

    grouped: dict[str, list[dict]] = defaultdict(list)
    for event in entries:
        grouped[_subsystem(event)].append(event)
    ranked = sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0]))
    # List every group. The journal query is already limited to 80 events, so
    # there cannot be more than 80 groups. Never silently hide the last groups.
    group_lines = [
        f"{index}. {len(events)} message{'s' if len(events) != 1 else ''} → {name}"
        for index, (name, events) in enumerate(ranked, start=1)
    ]

    headline = (f"Found {len(entries)} visible important system messages "
                f"from {len(ranked)} areas of the computer")
    explanation = [
        "These messages were recorded during the current startup. A message does not automatically mean a device is broken.",
        "Where the messages came from (every area found):\n" + "\n".join(group_lines),
        "Repeated copies of the same error are counted together, not treated as separate defects.",
    ]
    actions = []
    findings = []
    recognized_areas = []
    for index, (name, events) in enumerate(ranked, 1):
        seen = set()
        matched = None
        for event in reversed(events):
            message = _as_string(event.get("MESSAGE"))
            fingerprint = _fingerprint(message)
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
            matched = classify_system_message(name, message)
            if matched:
                break
        if matched:
            recognized_areas.append(name)
            findings.append(
                f"{name}\n"
                f"   What caused this message: {matched.cause}\n"
                f"   Possible effect: {matched.effect}\n"
                f"   How certain is this: {matched.confidence}"
            )
            actions.append(
                f"{index}. {name} — recommended steps\n{matched.action}"
            )
        else:
            findings.append(
                f"{name}\n"
                "   This message was recorded, but its exact cause cannot be identified safely "
                "from the available text alone."
            )
            next_area = ("Applications & Services → Service status"
                         if name.startswith(("Service: ", "Unit: ")) else
                         "Graphics & Display → Graphics errors" if name == "Graphics" else
                         "Internet & Network → IP configuration" if name == "Network" else
                         "Storage & Filesystems → Drive health indicators" if name == "Storage / filesystem" else
                         "Applications & Services → Application crashes")
            if name == "Graphics":
                actions.append(
                    f"{index}. Graphics — alternative solutions based on the next measurements\n"
                    "Option 1 (only one app is affected): Check whether an update is available for that app "
                    "from its original software manager. Save your work, update the app yourself, and repeat the failing action.\n"
                    "Option 2 (several apps freeze or GPU resets are confirmed): Use your distribution's "
                    "normal system updater to check for supported graphics updates, then retest. "
                    "Do not replace drivers manually.\n"
                    "Option 3 (only the monitor loses its signal): Check display power, input selection "
                    "and an accessible cable without opening the computer.\n"
                    "If these options do not isolate the fault, send the device name, symptoms, time and a "
                    "short redacted error excerpt to the affected application's developer or device support. "
                    "The automatic related checks below help decide which option applies; a generic "
                    "log message is NOT proof of a defective graphics card."
                )
            else:
                actions.append(
                    f"{index}. {name} — safe next actions\n"
                    f"The application will attempt any suitable related local check automatically. "
                    f"If that still cannot identify a cause, preserve the message and time and report "
                    f"the repeatable issue to the relevant application developer or hardware support. "
                    f"A specific repair cannot be justified from this message alone."
                )
    explanation.append("Cause and effect by area:\n" + "\n\n".join(findings))
    explanation.append("Only the messages available to this account were examined. The details and times are in Evidence / Logs.")
    instructions = [
        "Suggested solutions based on the actual messages (all detected areas):",
        *actions,
        "Run the affected check again after any manual change to verify whether the problem is resolved.",
        "Evidence / Logs shows which parts of your computer recorded messages, how often, and when. Original messages provide evidence for these steps; you do not have to diagnose the raw logs yourself.",
        "These logs are shown locally. This app does not send them online. If you choose to share logs online, first redact (hide) private data such as names or addresses.",
        "No changes or repairs are made automatically.",
    ]

    evidence = [
        "Details below are for advanced users. You do not need to understand every line.",
        "Source: journalctl -b -p 0..3 -n 80 --no-pager --output=json (current boot)",
        f"Visible events analyzed: {len(entries)}. Subsystem groups: {len(ranked)}.",
        "Every detected area is listed below. Up to two example messages appear per area; "
        "repeated messages are counted instead of copied dozens of times.",
        "Groups are based on service identifiers and message patterns; classification is provisional.",
    ]
    for index, (name, events) in enumerate(ranked, start=1):
        patterns = Counter(_fingerprint(_as_string(e.get("MESSAGE"))) for e in events)
        evidence.append(
            f"{index}. {len(events)} message{'s' if len(events) != 1 else ''} → {name} "
            f"({len(patterns)} type{'s' if len(patterns) != 1 else ''} of message)"
        )
        # At most two representative messages per group, alongside UTC timestamps.
        seen = set()
        for entry in reversed(events):
            fingerprint = _fingerprint(_as_string(entry.get("MESSAGE")))
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
            msg = _as_string(entry.get("MESSAGE")).replace("\n", " ")
            who = _as_string(entry.get("SYSLOG_IDENTIFIER") or entry.get("_SYSTEMD_UNIT") or "unknown", 120)
            evidence.append(f"  {_timestamp(entry)} | {who} | {msg or '(message unavailable)'}")
            if len(seen) >= 2:
                break
    evidence.append("Journal sample only; severity and repetition do not identify root cause.")

    return JournalReport(len(entries), headline, "\n".join(explanation), "\n\n".join(instructions), tuple(evidence), tuple(recognized_areas), tuple(name for name, _ in ranked))
