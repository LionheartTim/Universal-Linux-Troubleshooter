"""Shared Manual Diagnostics probe plan and scan-completion contract.

Probe extensions belong to the reviewed GUI scan plan, never to inferred
model commands.  The exact same plan must drive scan execution, evidence
presentation and completion accounting.  A probe reporting UNKNOWN is still a
completed attempt; an absent probe result is not.
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

from .manual_cases40 import plan_for_manual_case
from .topic_catalog127 import guide_for_topic


def planned_case_probes(case_id: str, topic_id: str | None = None) -> tuple[str, ...]:
    """Return all reviewed case probes plus topic-specific read-only probes."""
    _, original = plan_for_manual_case(case_id)
    if topic_id is None:
        return tuple(dict.fromkeys(original))
    guide = guide_for_topic(topic_id, case_id)  # Reject mismatched case/topic.
    if guide.heading == 'Steam':
        return tuple(dict.fromkeys(('steam_inventory128', *original)))
    return tuple(dict.fromkeys(original))


def scan_finished_as_planned(
    *,
    requested_checks: Iterable[tuple[str, str]],
    received_checks: Iterable[tuple[str, str]],
    requested_probes: Iterable[str],
    received_probes: Iterable[str],
    stopped: bool,
    progress_completed: int,
    progress_total: int,
    target_ok: bool = True,
    guided_ok: bool = True,
    network_ok: bool = True,
) -> bool:
    """Only claim completion when EVERY requested check returned once.

    A result with status UNKNOWN is a genuine completed measurement attempt;
    an absent, duplicate or extra check is not.  A cancelled/incomplete scan
    remains incomplete even if some evidence can still be presented.
    """
    if stopped or progress_completed != progress_total or progress_total <= 0:
        return False
    if not (target_ok and guided_ok and network_ok):
        return False
    checks = tuple(requested_checks)
    probes = tuple(requested_probes)
    if len(checks) != len(set(checks)) or len(probes) != len(set(probes)):
        return False
    return (Counter(received_checks) == Counter(checks)
            and Counter(received_probes) == Counter(probes))
