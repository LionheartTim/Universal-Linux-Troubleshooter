"""Evidence-grounded, read-only cause analysis for existing diagnostic results.

A finding here is about a *measured condition*, not a claim that we know the
user's symptoms. When data only suggests a link, say so. No invented tests,
no machine-changing commands, no automatic repairs and no AI dependency.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Mapping

from ..results import DiagnosticResult, ResultStatus

Key = tuple[str, str]


@dataclass(frozen=True)
class CauseFinding:
    heading: str
    observation: str
    connection: str
    next_steps: str
    confirmed: bool

    def diagnosis_text(self) -> str:
        label = "Confirmed finding" if self.confirmed else "Possible explanation — needs checking"
        return (f"{label}: {self.heading}\n"
                f"Evidence: {self.observation}\n"
                f"Why it may matter: {self.connection}")


def _failed_service(result: DiagnosticResult) -> str | None:
    if result.status != ResultStatus.WARNING or not any("systemctl --failed" in x for x in result.evidence):
        return None
    for text in result.evidence:
        # systemctl --failed emits e.g. 'foo.service loaded failed failed Description'.
        matched = re.match(r"^\s*([A-Za-z0-9_.@-]+\.service)\s+\S+\s+failed\s+", text)
        if matched:
            return matched.group(1)
    return None


def analyze_cause(result: DiagnosticResult) -> CauseFinding | None:
    """Offer explanations only for conditions proved by this specific check."""
    pair = (result.category_key, result.check_key)
    if result.status == ResultStatus.PROBLEM and pair == ("storage", "health"):
        return CauseFinding(
            "A disk reported a health warning",
            result.diagnosis,
            "This is a warning from the drive itself. It can explain missing files or read/write failures, "
            "but the affected files have not been identified.",
            "1. Save a copy of important files to another drive before doing anything else.\n"
            "2. Open Evidence / Logs to identify the exact drive.\n"
            "3. Arrange a professional check or contact the disk maker for that drive.\n"
            "4. Do not erase, format or attempt a repair before securing your files.",
            confirmed=True,
        )
    if pair == ("storage", "space") and result.status == ResultStatus.WARNING and any(
            "free of" in line or "root filesystem" in line.lower() for line in result.evidence):
        return CauseFinding(
            "Low free space in the area used to save files",
            result.diagnosis,
            "A shortage of free space may explain why downloads, updates or saves fail. "
            "It does not prove why another program crashed.",
            "1. Open Evidence / Logs to see which storage area is short of space.\n"
            "2. Open your file manager and inspect large files you recognize, such as old downloads.\n"
            "3. Remove only personal files you no longer need, or use your distribution's supported cleanup tool.\n"
            "4. Run Disk space again to confirm the free space has increased.\n"
            "Do not manually delete system deployments or format anything.",
            confirmed=True,
        )
    if pair == ("network", "ip") and result.status == ResultStatus.WARNING and (
        "No network address" in result.diagnosis or "No usable network" in result.diagnosis
    ):
        return CauseFinding(
            "Your computer does not have a usable network address",
            result.diagnosis,
            "Without an address on the connection you want to use, that connection normally cannot "
            "reach your router or the internet. This does not prove that your router is faulty.",
            "1. Open your computer's Wi-Fi or wired-network settings.\n"
            "2. Check that the connection you want to use is switched on and says Connected.\n"
            "3. If it is not connected, reconnect it using the network settings.\n"
            "4. Run IP configuration again; then try External connectivity if you want an online test.\n"
            "No network settings have been changed by this app.",
            confirmed=True,
        )
    if pair == ("applications", "services") and result.status == ResultStatus.WARNING:
        name = _failed_service(result)
        if name:
            return CauseFinding(
                f"The background service {name} failed",
                f"Linux listed {name} as a failed service.",
                "This confirms the service did not start correctly; it may explain an issue with the "
                "feature controlled by that service. It is not proof that other failures have the same cause.",
                "1. Open Evidence / Logs to see which service failed.\n"
                "2. Open a terminal and copy this read-only status check:\n"
                f"   systemctl status {name} --no-pager\n"
                "3. Look at its recent messages using:\n"
                f"   journalctl -b -u {name} --no-pager -n 50\n"
                "4. Identify the exact error before changing or restarting anything. Then rerun Service status.",
                confirmed=True,
            )
    if pair == ("applications", "resources") and result.status == ResultStatus.WARNING and "memory" in result.diagnosis.lower():
        return CauseFinding(
            "Very little working memory was available at the time of the scan",
            result.diagnosis,
            "A computer with little free working memory can become slow or freeze. The scan "
            "does not tell us which app is using it or whether it caused a particular freeze.",
            "1. Open your desktop's System Monitor and sort applications by memory use.\n"
            "2. If one application uses unusually large amounts, save your work before closing it yourself.\n"
            "3. Run Resource pressure again while the slowness occurs and compare the readings.",
            confirmed=True,
        )
    if pair == ("system", "system_logs") and result.status == ResultStatus.WARNING:
        # A specific SELinux denial is a *confirmed denied action*, NOT a
        # diagnosis that all unrelated desktop symptoms stem from SELinux.
        actual_messages = [line for line in result.evidence if " | " in line]
        if any("selinux is preventing" in line.casefold() or "avc: denied" in line.casefold()
               for line in actual_messages):
            return CauseFinding(
                "Linux security blocked an action reported in the logs",
                "At least one recorded system message explicitly says an action was denied by SELinux.",
                "This explains why that particular request was not permitted. It does not prove that "
                "the security setting caused a different problem you are experiencing.",
                "1. Open Evidence / Logs and find the message containing 'SELinux is preventing' or 'avc: denied'.\n"
                "2. Identify the affected program and what it was trying to do.\n"
                "3. If that program is actually failing, open a terminal and inspect recent messages using:\n"
                "   journalctl -b -t setroubleshoot --no-pager -n 50\n"
                "4. Use the software's official instructions or ask for help about that specific blocked action.\n"
                "5. Do not disable SELinux or relax system permissions simply to silence the log.",
                confirmed=True,
            )
    if pair == ("storage", "fs_logs") and result.status == ResultStatus.WARNING:
        proof = " ".join(result.evidence).lower()
        if any(x in proof for x in ("i/o error", "buffer i/o error", "read-only file system", "corrupt")):
            return CauseFinding(
                "Linux recorded a disk or file-system error",
                "At least one stored message refers to a file or disk access problem.",
                "This may explain files failing to open, save or copy. The log alone does not "
                "identify which piece of hardware, program or setting caused it.",
                "1. Back up important files if saving or reading them has started failing.\n"
                "2. Open Evidence / Logs to find the affected drive and the message time.\n"
                "3. Run Drive health indicators and Disk space for further clues.\n"
                "4. Do not format or repair a disk based on one log line.",
                confirmed=False,
            )
    return None


FOLLOWUPS: dict[Key, tuple[str, ...]] = {
    ("network", "wifi"): ("IP configuration", "System errors"),
    ("network", "dns"): ("IP configuration", "External connectivity"),
    ("network", "external"): ("IP configuration", "Local gateway", "Website name check"),
    ("network", "gateway"): ("IP configuration", "Network adapters"),
    ("storage", "health"): ("Drive inventory", "Filesystem warnings"),
    ("storage", "fs_logs"): ("Drive health indicators", "Disk space"),
    ("graphics", "render"): ("GPU inventory", "System errors"),
    ("applications", "app_crashes"): ("Service status", "System errors"),
    ("applications", "permissions"): ("System errors", "Service status"),
    ("system", "system_logs"): ("Service status", "Graphics errors", "Bluetooth status"),
}


def what_to_check_next(result: DiagnosticResult) -> str:
    """Specific honest next check when a cause cannot yet be supported."""
    if result.status not in (ResultStatus.WARNING, ResultStatus.PROBLEM, ResultStatus.UNKNOWN):
        return ""
    finding = analyze_cause(result)
    if finding:
        return finding.diagnosis_text()
    names = FOLLOWUPS.get((result.category_key, result.check_key))
    if names:
        return ("Cause not confirmed yet. Suggested next checks: " + ", ".join(names) + ". "
                "Compare those results with the exact message and time in Evidence / Logs. "
                "Only change a setting after a specific cause has been identified.")
    return ("Cause not confirmed yet. Open Evidence / Logs and note the affected program, "
            "device or time. Compare it with the problem you actually experienced before changing anything.")


def scan_cause_summary(checks: tuple[Key, ...], results: Mapping[Key, DiagnosticResult]) -> str:
    """Provide evidence-based leads for a batch without claiming unrelated symptoms."""
    found = []
    for pair in checks:
        result = results.get(pair)
        if result is None:
            continue
        finding = analyze_cause(result)
        if finding:
            found.append((pair, finding))
    if not found:
        # The result list already shows each warning, its evidence and its
        # action plan. Do not insert vague promises to 'investigate further'.
        return ""
    lines = ["Possible causes and confirmed findings"]
    for i, (_pair, f) in enumerate(found, 1):
        level = "Measured condition" if f.confirmed else "Possible cause"
        lines.append(f"{i}. {level}: {f.heading}\n   {f.connection}")
    lines.append("Recommended steps for these findings are listed first in the Solution tab.")
    return "\n\n".join(lines) + "\n"
