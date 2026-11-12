"""Bounded, evidence-only cross-check of saved app crashes and current journal GPU faults.

Correlation is a *time clue*, not root-cause proof. No additional host reads, network
requests or repairs. Raw diagnostics remain accessible through Evidence / Logs.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Mapping

from ..results import DiagnosticResult, ResultStatus

# GPU failures must occur in a timestamped *original journal example*, not an
# explanatory paragraph naming GPU errors or a generic group label.
_GPU_SIGNAL = re.compile(r'(?i)(?:amdgpu.*(?:ring\s+\S+\s+timeout|gpu reset|gpu fault|gpu hang)|'
                        r'nvrm:.*\bxid\b|i915.*(?:gpu hang|reset))')
_JOURNAL_TIME = re.compile(r'(?P<day>20\d\d-\d\d-\d\d) (?P<clock>\d\d:\d\d:\d\d) UTC\s*\|')
_CRASH_ROW = re.compile(r'^Crash record \d+:\s*\w{3}\s+(?P<day>20\d\d-\d\d-\d\d) '
                        r'(?P<clock>\d\d:\d\d:\d\d).*?(?P<path>/(?:usr|opt|app|var|home|run)/\S+)',re.I)


@dataclass(frozen=True)
class IncidentConnection:
    program: str
    seconds_apart: int
    diagnosis: str
    solution: str
    evidence: str


def correlate_graphics_app_crash(results: Mapping[tuple[str, str], DiagnosticResult],
                                 *, window_seconds: int = 300) -> IncidentConnection | None:
    """Only present a connection for a genuine journal GPU error close to a saved app crash.

    coredumpctl prints times in the computer's local timezone. journald examples
    here are UTC; local times are converted before comparison. A matching time
    is still an association, never evidence that the app broke the GPU/driver.
    """
    crash = results.get(('applications', 'app_crashes'))
    system = results.get(('system', 'system_logs'))
    if not crash or not system or crash.status not in (ResultStatus.WARNING, ResultStatus.PROBLEM) or system.status not in (ResultStatus.WARNING, ResultStatus.PROBLEM):
        return None
    graphics = []
    for line in system.evidence[:160]:
        match = _JOURNAL_TIME.search(line)
        if not match or not _GPU_SIGNAL.search(line):
            continue
        try:
            when = datetime.fromisoformat(match['day']+'T'+match['clock']).replace(tzinfo=timezone.utc)
            graphics.append((when, line[:600]))
        except ValueError:
            continue
    if not graphics:
        return None
    crashes = []
    for line in crash.evidence[:90]:
        match = _CRASH_ROW.search(line)
        if not match:
            continue
        try:
            local_dt = datetime.fromisoformat(match['day']+'T'+match['clock']).astimezone(timezone.utc)
        except ValueError:
            continue
        program = match['path'].rstrip(',:') .split('/')[-1]
        if not re.fullmatch(r'[A-Za-z0-9._+-]{2,72}', program):
            continue
        crashes.append((local_dt, program, line[:600]))
    possibilities = sorted((abs((a[0]-g[0]).total_seconds()), a[1], a[2], g[1])
                           for a in crashes for g in graphics)
    if not possibilities or possibilities[0][0] > max(1, min(window_seconds, 600)):
        return None
    seconds, name, crash_line, journal_line = possibilities[0]
    return IncidentConnection(
        name, round(seconds),
        f"A saved crash of {name} and a graphics-driver error were recorded about {round(seconds)} seconds apart. "
        "These events could be related, but timing alone cannot show which one caused the other. "
        "The saved crash may also be from an earlier session.",
        f"Suggested order for {name} and the graphics error:\n"
        f"1. Save your work and close {name}. If possible, repeat the affected task without it running.\n"
        "2. If the trouble only occurs with that optional app, check for its supported update through the original software manager. Do not remove system components.\n"
        "3. If several unrelated apps also freeze or the GPU reset returns, use your distribution's supported system updater for graphics/kernel updates. Do not apply forum-suggested GPU voltage, clock or kernel tweaks.\n"
        "4. Repeat the original task after changing ONE thing yourself. Compare NEW crash and GPU events, not old saved reports.\n"
        "5. If it persists, send the app developer the version, reproduction steps and redacted crash/GPU timestamps. The program never sends a report automatically.",
        'Saved application crash: ' + crash_line + '\nGraphics-driver event: ' + journal_line,
    )
