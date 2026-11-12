"""v61 conservative package/container journal events.

Read-only, bounded current-boot journal shared with v59. This is a *sample*
only: command-line apt/dnf/pacman/Podman output is often not sent to journald.
A missing record therefore is always an unknown symptom, not a clean bill.

No event here proves a repository, package, container, volume, or configuration
is faulty and NONE authorizes a repair route. Reject contradictory source
metadata rather than taking the more convenient identity.
"""
from __future__ import annotations

import re

from ..results import ResultStatus
from .diagnostic_events59 import SERVICE_EVENTS_JOURNAL
from .focused_evidence import _journal, _report


def rx(text: str) -> re.Pattern[str]:
    return re.compile(text, re.IGNORECASE)


# Patterns deliberately identify reported events, not their presumed cause.
# Matches operate on MESSAGE, not on sender prefixes or neighboring records.
EVENT_PATTERNS61: dict[str, re.Pattern[str]] = {
    'apt_repo_metadata_error': rx(r'(?:\brepository\b.{0,200}\bdoes not have a Release file\b|\b(?:NO_PUBKEY|EXPKEYSIG)\s+[0-9A-F]{8,40}\b)'),
    'apt_packages_kept_back': rx(r'\b(?:the following packages have been kept back|the following packages will be kept back)\s*:'),
    'dnf_depsolve_conflict': rx(r'\b(?:conflicting requests|nothing provides\s+\S{1,100}\s+needed by|problem with installed package)\b'),
    'pacman_file_conflict': rx(r'\b(?:failed to commit transaction\s*\(conflicting files\)|\S{1,150}\s+exists in filesystem\b)'),
    'ostree_layer_conflict': rx(r'\b(?:layered package|layered rpm|layered packages)\b.{0,160}\b(?:conflicts?|depsolv|cannot|failed|incompatible)\b|\b(?:conflicts?|depsolv|cannot|failed)\b.{0,160}\b(?:layered package|layered rpm)\b'),
    'zypper_package_locked': rx(r'\b(?:locked package|package\s+\S{1,120}\s+is locked|the installed\s+\S{1,120}\s+is locked)\b'),
    'zypper_vendor_conflict': rx(r'\b(?:vendor change|vendor conflict|vendor mismatch)\b.{0,130}\b(?:conflict|problem|not allowed|required|refused)\b|\b(?:conflict|problem)\b.{0,130}\b(?:vendor change|vendor mismatch)\b'),
    'flatpak_remote_error': rx(r'\b(?:remote\s+[\'\"]?[^\s\'\"]{1,90}[\'\"]?\s+(?:not found|does not exist)|unable to (?:load|fetch) summary from remote|could not (?:fetch|load) remote summary)\b'),
    'snap_refresh_error': rx(r'\b(?:cannot refresh\s+[\'\"]?\S{1,90}|refresh(?:ing)?\s+\S{1,90}\s+(?:failed|held)|refresh is held)\b'),
    'update_signature_error': rx(r'\b(?:signature verification failed|invalid (?:gpg|pgp|repository) signature|GPG error|signature from \S{1,100} is unknown trust)\b'),
    'podman_image_absent': rx(r'\b(?:no such image\s*:\s*\S{1,180}|image\s+\S{1,160}\s+not known|image\s+\S{1,160}\s+not found)\b'),
    'podman_privileged_port': rx(r'\b(?:rootlessport|rootless port|rootless container)\b.{0,160}\b(?:privileged port|port\s+(?:[1-9][0-9]{0,2}|10[0-1][0-9]|102[0-3])\b.{0,80}\b(?:permission denied|not permitted|cannot bind|cannot expose))\b'),
    'podman_volume_access_denied': rx(r'\b(?:bind mount|mounted volume|volume mount|container volume)\b.{0,180}\b(?:permission denied|operation not permitted)\b|\b(?:permission denied|operation not permitted)\b.{0,180}\b(?:bind mount|mounted volume|volume mount|container volume)\b'),
    'podman_container_dns_failure': rx(r'\b(?:container network|podman network|container dns)\b.{0,150}\b(?:no such host|name resolution failed|dns lookup failed|temporary failure in name resolution)\b'),
}

# Limit attribution to explicitly named sender families. Never interpret an
# unrelated application's quotation as a package manager's own event.
SENDERS61: dict[str, frozenset[str]] = {
    'apt_repo_metadata_error': frozenset(('apt', 'apt-get', 'packagekitd', 'pkcon')),
    'apt_packages_kept_back': frozenset(('apt', 'apt-get', 'packagekitd', 'pkcon')),
    'dnf_depsolve_conflict': frozenset(('dnf', 'dnf5', 'packagekitd', 'pkcon')),
    'pacman_file_conflict': frozenset(('pacman', 'pamac')),
    'ostree_layer_conflict': frozenset(('rpm-ostree', 'rpm-ostreed')),
    'zypper_package_locked': frozenset(('zypper', 'zypp')),
    'zypper_vendor_conflict': frozenset(('zypper', 'zypp')),
    'flatpak_remote_error': frozenset(('flatpak', 'flatpak-system-helper')),
    'snap_refresh_error': frozenset(('snap', 'snapd')),
    'update_signature_error': frozenset(('apt', 'apt-get', 'dnf', 'dnf5', 'pacman', 'zypper', 'packagekitd', 'flatpak', 'rpm-ostree', 'rpm-ostreed')),
    'podman_image_absent': frozenset(('podman', 'conmon', 'libpod')),
    'podman_privileged_port': frozenset(('podman', 'rootlessport', 'libpod')),
    'podman_volume_access_denied': frozenset(('podman', 'conmon', 'libpod')),
    'podman_container_dns_failure': frozenset(('podman', 'conmon', 'libpod')),
}


def _source61(row: dict) -> str | None:
    # _COMM is kernel-controlled; SYSLOG_IDENTIFIER can come from the emitter.
    # Reject conflicting recorded identities rather than misattribute the event.
    observed = []
    for field in ('_COMM', 'SYSLOG_IDENTIFIER'):
        val = row.get(field)
        if val is None:
            continue
        if not isinstance(val, str) or not 1 <= len(val) <= 64 or not re.fullmatch(r'[a-zA-Z0-9_-]+', val):
            return None
        observed.append(val.lower())
    if observed and len(set(observed)) > 1:
        return None
    if observed:
        return observed[0]
    # A MESSAGE prefix is unauthenticated text. v76 rejects it as an
    # identity, even when it looks like a legitimate sender plus PID.
    return None


def _match61(fact: str, row: dict) -> bool:
    sender = _source61(row)
    if sender not in SENDERS61[fact]:
        return False
    message = row['MESSAGE'][:1200]
    return bool(EVENT_PATTERNS61[fact].search(message))


def probe_package_container_events61(host):
    records = _journal(host, SERVICE_EVENTS_JOURNAL)
    facts = {
        key: ('unknown' if records is None else
              'observed' if any(_match61(key, row) for row in records) else
              'not_observed_in_sample')
        for key in EVENT_PATTERNS61
    }
    return _report('package_container_events61',
                   ResultStatus.UNKNOWN if records is None else
                   ResultStatus.WARNING if 'observed' in facts.values() else ResultStatus.INFO,
                   *(f'{name}={value}' for name, value in facts.items()),
                   explanation=('Een begrensde journald-steekproef van deze opstart met controle op '
                                'herkomst van pakket- en containerfouten. Veel terminaluitvoer wordt '
                                'niet in journald opgeslagen. Een waargenomen melding bewijst geen '
                                'huidige storing, oorzaak of goedgekeurde oplossing.'))
