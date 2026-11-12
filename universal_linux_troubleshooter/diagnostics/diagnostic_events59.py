"""Provisional, bounded v59 application/service *event* observations.

Journald typically stores the sender in SYSLOG_IDENTIFIER or _COMM and the
message *without* the prefix. Interpret these fields separately, and do not
attribute text from another process to sshd, CUPS, PipeWire, fwupd, etc.

Events are observations, never an approved fault cause or repair. A blank
sample is UNKNOWN with respect to the symptom, not proof of normal operation.
"""
from __future__ import annotations

import re
from ..results import ResultStatus
from .focused_evidence import _journal, _report

# Error-priority-only journal samples omit many ordinary sshd, CUPS and
# user-service failure messages (which can be logged with priority INFO).
# This command is fixed in code, local, bounded and read-only; no shell.
SERVICE_EVENTS_JOURNAL = ('journalctl', '-b', '-n', '160', '--no-pager', '--output=json')


def _rx(pattern: str) -> re.Pattern:
    return re.compile(pattern, re.IGNORECASE)


# These are message patterns, evaluated in the context of a verified journal
# sender when available. Legacy prefixed journal MESSAGE formats are accepted
# as well, but *never* when they conflict with an explicit sender field.
_SYSTEM_EVENTS59 = {
    'native_library_load_error': _rx(r'^(?:[A-Za-z0-9_.+-]{1,64}(?:\[\d{1,9}\])?:\s*){0,2}error while loading shared libraries:\s+lib[\w.+-]{1,100}\.so(?:\.\d+)*:\s+cannot open shared object file\b'),
    'native_exec_format_error': _rx(r'^(?:[A-Za-z0-9_.+-]{1,64}(?:\[\d{1,9}\])?:\s*){0,2}(?:cannot execute binary file|failed at step EXEC spawning\s+\S{1,150})\b.{0,125}\bExec format error\b'),
    'application_config_parse_error': _rx(r'^(?:[A-Za-z0-9_.+-]{1,64}(?:\[\d{1,9}\])?:\s*){0,2}(?:config(?:uration)?|settings)\b.{0,100}\b(?:syntax error|parse error|parsing failed)\b.{0,100}\bline\s+\d{1,7}\b'),
    'application_core_dump': _rx(r'\b(?:systemd-coredump|systemd\[\d+\])\b.{0,200}\b(?:process\s+\d+\s+\([^)]{1,100}\)\s+(?:of\s+user\s+\d+\s+)?dumped core|core dumped for process\s+\d+)\b'),
    'appimage_fuse_unavailable': _rx(r'^(?:[A-Za-z0-9_.+-]{1,64}(?:\[\d{1,9}\])?:\s*){0,2}(?:AppImage|appimagetool)\b.{0,160}\b(?:FUSE is not available|requires FUSE to run|cannot mount AppImage.*FUSE)\b'),
    'ssh_auth_rejected': _rx(r'\bsshd(?:\[\d+\])?\s*:\s*(?:Failed (?:password|publickey) for\b|Authentication refused:\s+bad ownership or modes\b)'),
    'wallet_unlock_failed': _rx(r'\b(?:kwalletd[56]?|gnome-keyring-daemon)\b.{0,170}\b(?:failed to open wallet|cannot unlock keyring|could not unlock keyring)\b'),
    'flatpak_runtime_missing': _rx(r'\bflatpak\b.{0,170}\b(?:runtime\s+[^\s]{1,100}\s+(?:is\s+)?not installed|unable to find required runtime)\b'),
    'portal_camera_denied': _rx(r'\b(?:xdg-desktop-portal|org\.freedesktop\.portal)\b.{0,170}\b(?:camera|microphone)\b.{0,100}\b(?:access denied|permission denied|request denied)\b'),
    'fwupd_update_failed': _rx(r'\bfwupd(?:\[\d+\])?\b.{0,170}\b(?:failed to (?:update|flash) (?:device|firmware)|firmware update failed)\b'),
    'pipewire_xrun': _rx(r'\b(?:pipewire|wireplumber|pw-node)\b.{0,170}\b(?:xrun|underrun)\b'),
    'printer_job_failure': _rx(r'\b(?:cupsd|cups-browsed)\b.{0,150}\b(?:job\s+\d{1,12}\b.{0,100}\b(?:stopped|failed)|filter failed for job\s+\d{1,12})\b'),
    'ups_low_battery_event': _rx(r'\b(?:upsmon|upsd|nut-monitor)\b.{0,150}\b(?:UPS\s+[^\s]{1,80}\s+(?:battery is low|on battery)|battery low on UPS\s+[^\s]{1,80})\b'),
    'display_session_start_failed': _rx(r'\b(?:sddm|gdm|lightdm)\b.{0,160}\b(?:failed to (?:start|launch) (?:user )?session|session startup failed)\b'),
    'dpkg_interrupted_event': _rx(r'\bdpkg\b.{0,125}\b(?:was interrupted|package\s+[^\s]{1,80}\s+is in a very bad inconsistent state)\b'),
}

# Sender attribution matters even when a message quotes another service's log.
# The metadata source is NOT proof that it concerns the user's chosen device.
_SENDER59 = {
    'application_core_dump': _rx(r'^(?:systemd-coredump|systemd-coredump\.service)$'),
    'ssh_auth_rejected': _rx(r'^(?:sshd|ssh|sshd\.service|ssh\.service)$'),
    'wallet_unlock_failed': _rx(r'^(?:kwalletd[56]?|gnome-keyring-daemon|gnome-keyring-daemon\.service)$'),
    'flatpak_runtime_missing': _rx(r'^(?:flatpak|flatpak-system-helper|flatpak-system-helper\.service)$'),
    'portal_camera_denied': _rx(r'^(?:xdg-desktop-portal(?:-[\w-]+)?|org\.freedesktop\.portal[\w.-]*)$'),
    'fwupd_update_failed': _rx(r'^(?:fwupd|fwupd\.service)$'),
    'pipewire_xrun': _rx(r'^(?:pipewire|wireplumber|pw-node|pipewire\.service|wireplumber\.service)$'),
    'printer_job_failure': _rx(r'^(?:cupsd|cups-browsed|cups\.service|cups-browsed\.service)$'),
    'ups_low_battery_event': _rx(r'^(?:upsmon|upsd|nut-monitor|nut-monitor\.service)$'),
    'display_session_start_failed': _rx(r'^(?:sddm|gdm|gdm3|lightdm|display-manager\.service|sddm\.service|gdm\.service|lightdm\.service)$'),
    'dpkg_interrupted_event': _rx(r'^(?:dpkg|apt|apt-get|unattended-upgrade)$'),
}


# Kernel _COMM is the process name; SYSLOG_IDENTIFIER is supplied by the
# emitting process. Do not treat an unlabelled MESSAGE prefix as an identity.
# A bare journal record can be *informative*, but cannot authorize a FACT.
_UNIT_ALIASES59 = {
    'cups.service': 'cupsd', 'cups-browsed.service': 'cups-browsed',
    'ssh.service': 'sshd', 'sshd.service': 'sshd',
    'sddm.service': 'sddm', 'gdm.service': 'gdm',
    'fwupd.service': 'fwupd', 'pipewire.service': 'pipewire',
    'wireplumber.service': 'wireplumber',
    'systemd-coredump.service': 'systemd-coredump',
}


def _sender(row: dict) -> str | None:
    """Require explicitly structured, internally consistent journal identity.

    A caller-supplied syslog identifier alone is still only a *reported*
    sender, not cryptographic process attestation. Contradictions fail closed.
    """
    values=[]
    for field in ('_COMM', 'SYSLOG_IDENTIFIER'):
        value=row.get(field)
        if value is None:
            continue
        if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z0-9_.@+-]{1,64}',value):
            return None
        values.append(value.casefold())
    if len(set(values)) > 1:
        return None
    unit = row.get('_SYSTEMD_UNIT')
    if unit is not None:
        if not isinstance(unit,str) or not re.fullmatch(r'[A-Za-z0-9_.@-]{1,110}\.(?:service|scope)',unit):
            return None
        alias=_UNIT_ALIASES59.get(unit.casefold())
        if alias and values and values[0] != alias:
            return None
    if values:
        return values[0]
    # Only a small set of known system units is a usable alternative to the
    # process label; do not treat arbitrary unit names as process identities.
    return _UNIT_ALIASES59.get(unit.casefold()) if isinstance(unit,str) else None


def _matches(fact: str, row: dict) -> bool:
    sender=_sender(row)
    if sender is None:
        return False
    allow = _SENDER59.get(fact)
    if allow is not None and not allow.fullmatch(sender):
        return False
    # Message matching is allowed only after a separate journal identity is
    # present. This is a recorded event, never a causal or target match.
    content=row['MESSAGE'][:1200]
    candidate=content if allow is None else sender+': '+content
    return bool(_SYSTEM_EVENTS59[fact].search(candidate))


def probe_service_events59(host):
    records = _journal(host, SERVICE_EVENTS_JOURNAL)
    facts = {
        fact: ('unknown' if records is None
               else 'observed' if any(_matches(fact, item) for item in records)
               else 'not_observed_in_sample')
        for fact in _SYSTEM_EVENTS59
    }
    return _report(
        'service_events59',
        ResultStatus.UNKNOWN if records is None else
        ResultStatus.WARNING if 'observed' in facts.values() else ResultStatus.INFO,
        *(f'{fact}={status}' for fact, status in facts.items()),
        explanation=('Een begrensde, lokale journald-steekproef met informatie- en foutmeldingen. '
                     'Alleen afzonderlijk vermelde, consistente bronidentiteit geaccepteerd. Een gebeurtenis bewijst '
                     'geen oorzaak, betrokken apparaat of reparatie. Afwezige meldingen sluiten niets uit.'),
    )
