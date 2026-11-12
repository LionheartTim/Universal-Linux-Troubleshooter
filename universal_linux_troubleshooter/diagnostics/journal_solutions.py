"""Evidence-specific, conservative journal explanations.

Rules interpret only actual journal text, not category labels or message counts.
No execution, online calls, privilege escalation or repair commands.
Unrecognized messages remain explicitly unclassified.
"""
from __future__ import annotations
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class JournalAdvice:
    cause: str
    effect: str
    action: str
    confidence: str


def classify_system_message(group: str, message: str) -> JournalAdvice | None:
    text = message.casefold()
    if any(s in text for s in ("selinux is preventing", "selinux denied", "avc: denied", "denied {")):
        # The denial is real; whether it breaks the user's program is unknown.
        program = re.search(r"selinux is preventing\s+([\w.+-]{1,55})\s+from", text)
        affected = program.group(1) if program else "an application"
        return JournalAdvice(
            f"Linux security blocked a request made by {affected}.",
            "That particular request was denied. The affected program might still work normally.",
            "1. Linux security (SELinux): if the affected program works, no change is needed.\n"
            "2. If it fails, check for an available update using your usual software manager.\n"
            "3. Run Permissions clues in Applications & Services to check for related denials.\n"
            "4. Do not disable SELinux or weaken file permissions to silence the message.\n"
            "5. The exact blocked operation is recorded in Evidence / Logs.",
            "Confirmed blocked request; effect on the program is not established.",
        )
    if "Bluetooth" in group:
        if any(s in text for s in ("unable to load key file", "no such file or directory")):
            return JournalAdvice(
                "A Bluetooth configuration file could not be opened.",
                "A particular Bluetooth function may not load its preferences; this does not prove all Bluetooth is broken.",
                "1. Open System Settings → Bluetooth on KDE Plasma, or Bluetooth settings on your desktop.\n"
                "2. Check whether Bluetooth is enabled and your device connects.\n"
                "3. If the device does not connect, remove only that device's pairing in settings and pair it again.\n"
                "4. Run Bluetooth status again and compare the result.\n"
                "5. Optional read-only check: systemctl status bluetooth.service --no-pager\n"
                "6. The missing file path is available in Evidence / Logs.",
                "Confirmed missing file; impact on the Bluetooth connection is unverified.",
            )
        if any(s in text for s in ("failed to set mode", "l2cap server failed", "connection refused", "failed to connect")):
            return JournalAdvice(
                "Bluetooth could not finish one of its connection or audio operations.",
                "A headset, mouse or other Bluetooth device may have trouble connecting or using audio.",
                "1. If everything works, no setting needs to change. Otherwise, open your desktop's Bluetooth settings and verify that Bluetooth is switched on.\n"
                "2. Confirm that the affected device is powered on and nearby.\n"
                "3. Disconnect and reconnect that device in Bluetooth settings.\n"
                "4. Run Bluetooth status again; the exact error remains available in Evidence / Logs.\n"
                "5. Optional read-only service check: systemctl status bluetooth.service --no-pager",
                "A failed Bluetooth operation was recorded; the affected device is not identified conclusively.",
            )
    if group == "Storage / filesystem":
        if any(s in text for s in ("i/o error", "buffer i/o error", "ext4-fs error", "btrfs error", "read-only file system", "nvme timeout")):
            return JournalAdvice(
                "Linux recorded a problem reading or writing storage data.",
                "Files may fail to open, save or copy. The log alone cannot prove the physical disk is defective.",
                "1. Back up important personal files to another drive before troubleshooting further.\n"
                "2. Run Storage & Filesystems → Drive health indicators and Disk space.\n"
                "3. If a disk health warning appears, consult the drive manufacturer or a technician.\n"
                "4. Do not format the disk or start filesystem repair without a verified recovery plan.\n"
                "5. The affected disk and original message, if given, are shown in Evidence / Logs.",
                "Confirmed recorded storage error; hardware cause still needs verification.",
            )
    if group == "Graphics":
        if any(s in text for s in ("gpu reset", "gpu hang", "ring timeout", "amdgpu error", "drm:gpu fault", "nvrm: x id", "nvrm: xid")):
            return JournalAdvice(
                "The graphics driver reported a GPU hang, reset or timeout.",
                "This can explain a temporary black screen, flickering, or a game freezing around that time.",
                "1. Save your work before repeating a graphics-heavy task.\n"
                "2. Run Graphics & Display → GPU inventory and Graphics errors.\n"
                "3. Check your distribution's normal system update tool for supported graphics driver updates.\n"
                "4. Test again and compare when the fault occurs; avoid randomly reinstalling GPU drivers.\n"
                "5. The exact driver error is available in Evidence / Logs.",
                "Graphics-driver error reported; whether it caused the symptom needs timing confirmation.",
            )
    if group == "Network":
        if any(s in text for s in ("deauth", "disconnected", "dhcp timeout", "ip configuration failed", "activation failed")):
            return JournalAdvice(
                "The network service reported a connection interruption or setup failure.",
                "This may explain losing access to a network or the internet.",
                "1. Open your desktop's Wi-Fi & Internet settings and check the selected connection.\n"
                "2. Run Internet & Network → Wi-Fi connection, IP configuration and Local gateway.\n"
                "3. If those checks succeed, run External connectivity with permission to check outside the router.\n"
                "4. Compare the result with other devices before resetting the router.\n"
                "5. The precise disconnection event remains in Evidence / Logs.",
                "Connection-related error reported; router, driver and provider are not distinguished yet.",
            )
    if group.startswith(("Service: ", "Unit: ")):
        if any(s in text for s in ("failed", "cannot start", "timed out", "permission denied", "no such file or directory")):
            service = group.split(": ", 1)[1]
            # Never copy arbitrary journal content into commands or executable syntax.
            service_name = service if re.fullmatch(r"[A-Za-z0-9_.@-]{1,80}", service) else ""
            steps = ("1. Run Applications & Services → Service status to see whether Linux marked a service as failed.\n"
                     "2. Use your normal software manager to check for updates for the affected application.\n"
                     "3. Run Application crashes to check whether this program stopped unexpectedly.\n"
                     "4. Compare the new results with the original message in Evidence / Logs.")
            if service_name.endswith(".service"):
                steps += "\n5. Optional read-only status command: systemctl status " + service_name + " --no-pager"
            return JournalAdvice(
                f"A background program ({service}) reported an unsuccessful operation.",
                "The related feature may not start or may stop working. This does not prove other services are affected.",
                steps,
                "Program error reported; the underlying reason has not yet been confirmed.",
            )
    return None
