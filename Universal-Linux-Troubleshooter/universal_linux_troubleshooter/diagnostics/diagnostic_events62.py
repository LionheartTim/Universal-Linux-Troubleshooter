"""v62: Ten provisional, source-attributed event observations for existing cases.

The bounded current-boot journal is an opportunistic sample. Ordinary
terminal failures may never enter journald. Every fact is either an observed
explicit event, not observed in this sample, or unknown; NONE is a cause or
an approved repair. _COMM and SYSLOG_IDENTIFIER conflicts are rejected.
"""
from __future__ import annotations

import re
from ..results import ResultStatus
from .focused_evidence import _journal, _report
from .diagnostic_events59 import SERVICE_EVENTS_JOURNAL
from .diagnostic_events61 import _source61


def rx(value: str):
    return re.compile(value, re.IGNORECASE)


EVENT_PATTERNS62 = {
    'git_auth_rejected': rx(r"\b(?:authentication failed for|fatal:\s+could not read Username for|remote:\s+(?:permission denied|access denied)|fatal:\s+could not read from remote repository)\b"),
    'git_local_changes_protected': rx(r"\b(?:your local changes to the following files would be overwritten by checkout|please commit your changes or stash them before you (?:switch branches|merge)|the following untracked working tree files would be overwritten by checkout)\b"),
    'pip_externally_managed': rx(r"\b(?:error:\s+externally-managed-environment|this environment is externally managed)\b"),
    'build_executable_missing': rx(r"(?:^|\s)(?:make|ninja):\s+(?:[0-9]+:\s+)?(?:/bin/sh:\s+)?(?:[A-Za-z0-9_+.-]{1,80}:\s+)?(?:command not found|not found|No such file or directory)\b"),
    'appimage_noexec_block': rx(r"\b(?:appimage|appimagetool)\b.{0,150}\b(?:noexec|filesystem mounted with noexec|permission denied while executing)\b"),
    'desktop_entry_invalid': rx(r"\b(?:desktop-file-validate|desktop entry)\b.{0,180}\b(?:invalid|parse error|syntax error|error: required key|does not have a group)\b"),
    'flatpak_launch_failure': rx(r"\b(?:error:\s+failed to start (?:application|app)|unable to launch flatpak application|failed to launch application\s+\S{1,120})\b"),
    'podman_container_start_failure': rx(r"\b(?:failed to (?:start|create) container|container\s+\S{1,120}\s+failed to start|error starting container)\b"),
    'podman_rootless_userns_error': rx(r"\b(?:rootless|user namespace|userns)\b.{0,140}\b(?:cannot clone|permission denied|operation not permitted|not available|failed to create)\b|\b(?:cannot clone|permission denied|operation not permitted|failed to create)\b.{0,140}\b(?:rootless|user namespace|userns)\b"),
    'shutdown_stop_timeout': rx(r"\b(?:stop(?:ping)? (?:job|operation)|timed out (?:stopping|waiting for) (?:unit|service)|unit\s+\S{1,130}\s+stop-sigterm timed out)\b.{0,130}\b(?:timed out|timeout|failed)\b|\bstop-sigterm timed out\b"),
}

SENDERS62 = {
    'git_auth_rejected': frozenset(('git','git-remote-https','git-remote-http')),
    'git_local_changes_protected': frozenset(('git',)),
    'pip_externally_managed': frozenset(('pip','pip3')),
    'build_executable_missing': frozenset(('make','ninja')),
    'appimage_noexec_block': frozenset(('appimage','appimagetool')),
    'desktop_entry_invalid': frozenset(('desktop-file-validate','desktop-file-instal','desktop-file-install')),
    'flatpak_launch_failure': frozenset(('flatpak','flatpak-system-helper')),
    'podman_container_start_failure': frozenset(('podman','conmon','libpod')),
    'podman_rootless_userns_error': frozenset(('podman','conmon','libpod','rootlessport')),
    'shutdown_stop_timeout': frozenset(('systemd',)),
}


def _match62(fact: str, row: dict) -> bool:
    # Unlike older legacy log formats, a message prefix alone is not trusted
    # as a sender for this new rule set. A process may quote another tool.
    if not (row.get('_COMM') or row.get('SYSLOG_IDENTIFIER')):
        return False
    return _source61(row) in SENDERS62[fact] and bool(EVENT_PATTERNS62[fact].search(row['MESSAGE'][:1200]))


def probe_application_events62(host):
    records = _journal(host, SERVICE_EVENTS_JOURNAL)
    facts = {fact: ('unknown' if records is None else
                    'observed' if any(_match62(fact, row) for row in records) else
                    'not_observed_in_sample')
             for fact in EVENT_PATTERNS62}
    return _report('application_events62',
                   ResultStatus.UNKNOWN if records is None else
                   ResultStatus.WARNING if 'observed' in facts.values() else ResultStatus.INFO,
                   *(f'{name}={value}' for name, value in facts.items()),
                   explanation=('Gebeurtenissen uit een begrensde lokale journald-steekproef. '
                                'Alleen expliciete foutteksten met passende afzender worden gemarkeerd. '
                                'Terminaluitvoer verschijnt vaak NIET in journald; afwezigheid bewijst niets. '
                                'Geen account, betrokken pakket, huidige toestand of oorzaak onafhankelijk vastgesteld.'))
