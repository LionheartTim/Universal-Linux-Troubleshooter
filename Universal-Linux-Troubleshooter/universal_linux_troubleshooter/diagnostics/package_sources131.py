"""Distro-neutral, strictly offline and read-only package-source inventory.

Every source is queried separately. A missing utility, failed/truncated query, or
sandbox-inaccessible host database is UNKNOWN / unavailable, NEVER 'not installed'.
Only source status/counts are persisted in the local profile; package names and
unrelated application data are never written to disk. The shared API can be
used by any future Manual Diagnostics case, not just Steam.

RPM is the installed package database used by DNF and Zypper; neither frontend
is an additional installed-package database. On atomic systems, RPM records do
not distinguish base image from layered packages; rpm-ostree is a separate
image/deployment observation, not a second package list.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import re

# Fixed commands only: do not accept commands or package names from users/files.
# 131072 bytes is the existing LocalHost command output bound; when truncated,
# the source is UNKNOWN (never a proof of absence).
SOURCES = {
    'flatpak_user': ('flatpak', 'list', '--app', '--user', '--columns=application'),
    'flatpak_system': ('flatpak', 'list', '--app', '--system', '--columns=application'),
    'rpm': ('rpm', '-qa', '--qf', '%{NAME}\\n'),
    'deb': ('dpkg-query', '-W', '-f=${binary:Package}\\t${Status}\\n'),
    'pacman': ('pacman', '-Qq'),
    'snap': ('snap', 'list'),
    'apk': ('apk', 'info', '-q'),
    'xbps': ('xbps-query', '-l'),
    'nix_user': ('nix-env', '-q'),
    'rpm_ostree': ('rpm-ostree', 'status', '--json'),
}
APP_IDS = {
    'firefox': {
        'flatpak_user': frozenset(('org.mozilla.firefox',)),
        'flatpak_system': frozenset(('org.mozilla.firefox',)),
        'rpm': frozenset(('firefox',)), 'deb': frozenset(('firefox', 'firefox-esr')),
        'pacman': frozenset(('firefox',)), 'snap': frozenset(('firefox',)),
        'apk': frozenset(('firefox',)), 'xbps': frozenset(('firefox',)),
    },
    'chromium': {
        'flatpak_user': frozenset(('org.chromium.chromium',)),
        'flatpak_system': frozenset(('org.chromium.chromium',)),
        'rpm': frozenset(('chromium', 'chromium-browser')),
        'deb': frozenset(('chromium', 'chromium-browser')),
        'pacman': frozenset(('chromium',)), 'snap': frozenset(('chromium',)),
        'apk': frozenset(('chromium',)), 'xbps': frozenset(('chromium',)),
    },
    'librewolf': {
        'flatpak_user': frozenset(('io.gitlab.librewolf-community',)),
        'flatpak_system': frozenset(('io.gitlab.librewolf-community',)),
        'rpm': frozenset(('librewolf',)), 'deb': frozenset(('librewolf',)),
        'pacman': frozenset(('librewolf',)),
    },
    'vlc': {
        'flatpak_user': frozenset(('org.videolan.vlc',)),
        'flatpak_system': frozenset(('org.videolan.vlc',)),
        'rpm': frozenset(('vlc',)), 'deb': frozenset(('vlc',)),
        'pacman': frozenset(('vlc',)), 'snap': frozenset(('vlc',)),
    },
    'gimp': {
        'flatpak_user': frozenset(('org.gimp.gimp',)),
        'flatpak_system': frozenset(('org.gimp.gimp',)),
        'rpm': frozenset(('gimp',)), 'deb': frozenset(('gimp',)),
        'pacman': frozenset(('gimp',)), 'snap': frozenset(('gimp',)),
    },
    'thunderbird': {
        'flatpak_user': frozenset(('org.mozilla.thunderbird',)),
        'flatpak_system': frozenset(('org.mozilla.thunderbird',)),
        'rpm': frozenset(('thunderbird',)), 'deb': frozenset(('thunderbird',)),
        'pacman': frozenset(('thunderbird',)), 'snap': frozenset(('thunderbird',)),
    },
    'blender': {
        'flatpak_user': frozenset(('org.blender.blender',)),
        'flatpak_system': frozenset(('org.blender.blender',)),
        'rpm': frozenset(('blender',)), 'deb': frozenset(('blender',)),
        'pacman': frozenset(('blender',)), 'snap': frozenset(('blender',)),
    },
    'steam': {
        'flatpak_user': frozenset(('com.valvesoftware.steam',)),
        'flatpak_system': frozenset(('com.valvesoftware.steam',)),
        'rpm': frozenset(('steam', 'steam-launcher', 'steam-installer')),
        'deb': frozenset(('steam', 'steam-launcher', 'steam-installer', 'steam:i386')),
        'pacman': frozenset(('steam',)),
        'snap': frozenset(('steam',)),
        'apk': frozenset(('steam',)),
        'xbps': frozenset(('steam',)),
        # Nix user profiles and ostree deployments are not complete host
        # package databases, so neither can prove a package is absent.
    },
}
VALID_STATES = frozenset(('checked', 'unavailable', 'unknown'))
VALID_PRESENCE = frozenset(('found', 'not_found', 'unknown', 'unavailable'))
APPIMAGE_ROOTS = ('~/Applications', '~/.local/bin')
ALL_SOURCE_KEYS = frozenset((*SOURCES, 'appimage'))
_SAFE_NAME = re.compile(r'[A-Za-z0-9][A-Za-z0-9._:+-]{0,160}')

@dataclass(frozen=True)
class SourceReading:
    source: str
    state: str
    count: int | None
    presence: str = 'unknown'


def _read_names(source: str, text: str) -> tuple[str, ...]:
    names = []
    for line in text.splitlines():
        if source == 'deb':
            parts = line.split('\t')
            if len(parts) != 2 or parts[1].strip() != 'install ok installed':
                continue  # A dpkg record is not necessarily installed.
            name = parts[0].strip()
        elif source == 'xbps':
            # XBPS output starts with ii / uu; a version suffix is part of
            # its display, not necessarily a package identity.
            parts = line.split()
            if len(parts) < 2 or parts[0] != 'ii':
                continue
            name = re.sub(r'-[0-9][A-Za-z0-9._+-]*$', '', parts[1])
        elif source == 'snap':
            # Human-readable `snap list` has a column header and can be
            # localized. Our command runs under LC_ALL=C in LocalHost.
            if (line.strip().startswith('Name ') or not line.strip()
                    or line.strip().startswith('No snaps are installed')):
                continue
            name = line.split()[0]
        else:
            name = line.strip()
        if _SAFE_NAME.fullmatch(name):
            names.append(name.casefold())
    return tuple(dict.fromkeys(names))


def inspect_sources(host, *, application: str | None = None) -> dict[str, SourceReading]:
    """Inspect known package databases; `application` is an APPROVED registry key.

    A platform can have multiple valid sources simultaneously. Avoid choosing
    one based on /etc/os-release or treating the absence of a tool as a negative.
    """
    if application is not None and application not in APP_IDS:
        raise ValueError('Application has no reviewed package-identity mapping')
    data = {}
    for source, argv in SOURCES.items():
        try:
            out = host.command(argv)
        except (OSError, RuntimeError, ValueError, AttributeError, AssertionError):
            data[source] = SourceReading(source, 'unknown', None)
            continue
        if out.code == 127:
            data[source] = SourceReading(source, 'unavailable', None, 'unavailable')
            continue
        if out.code != 0 or out.truncated or len(out.out) > 131072:
            data[source] = SourceReading(source, 'unknown', None)
            continue
        if source == 'rpm_ostree':
            try:
                payload = json.loads(out.out)
                deployments = payload['deployments']
                if not isinstance(deployments, list): raise ValueError('Not a deployment list')
                data[source] = SourceReading(source, 'checked', len(deployments), 'unknown')
            except (ValueError, KeyError, TypeError):
                data[source] = SourceReading(source, 'unknown', None)
            continue
        names = _read_names(source, out.out)
        target = APP_IDS[application].get(source) if application else None
        presence = ('found' if any(n in target for n in names) else 'not_found') if target else 'unknown'
        data[source] = SourceReading(source, 'checked', len(names), presence)
    # AppImages do not have a universal installation database. Only inspect
    # two conventional local locations; never claim absence elsewhere.
    count = 0
    visited = 0
    for root in APPIMAGE_ROOTS:
        path = str(Path(root).expanduser())
        try:
            if not host.exists(path):
                continue
            names = host.list_names(path)
            if len(names) > 2000:
                continue
            visited += 1
            count += sum(1 for name in names
                         if name.lower().endswith('.appimage') and len(name) <= 180)
        except (OSError, PermissionError, ValueError, AttributeError):
            continue
    data['appimage'] = SourceReading('appimage', 'checked' if visited else 'unknown',
                                   count if visited else None, 'unknown')
    return data


def public_summary(readings: dict[str, SourceReading]) -> dict[str, dict]:
    """Persist only small, non-personal availability and count summaries."""
    return {k: {'status': v.state, 'count': v.count}
            for k, v in readings.items() if k in ALL_SOURCE_KEYS}


def valid_summary(data) -> bool:
    return (isinstance(data, dict) and len(data) <= len(ALL_SOURCE_KEYS)
            and all(k in ALL_SOURCE_KEYS and isinstance(v, dict)
                    and set(v) == {'status', 'count'}
                    and v['status'] in VALID_STATES
                    and (v['count'] is None or (type(v['count']) is int and 0 <= v['count'] <= 100000))
                    for k, v in data.items()))


def description(source: str) -> str:
    return {
        'flatpak_user': 'Flatpak (user)', 'flatpak_system': 'Flatpak (system)',
        'rpm': 'RPM packages (DNF / Zypper / RPM)', 'deb': 'DEB packages (APT / dpkg)',
        'pacman': 'Arch packages (Pacman)', 'snap': 'Snap packages',
        'apk': 'Alpine APK packages',
        'xbps': 'Void Linux XBPS packages',
        'nix_user': 'Nix user-profile packages',
        'rpm_ostree': 'rpm-ostree image deployments (not an app list)',
        'appimage': 'AppImage files in common user folders (partial check)',
    }[source]


def package_relevance(case_id: str, title: str = '', guide_title: str = '') -> bool:
    """Source availability matters only to package/install/update diagnoses."""
    # Hardware fan/pump RPM means revolutions per minute, not RPM packages.
    # Firmware/BIOS warnings also must not accidentally show package databases.
    from .manual_cases40 import case_catalog
    if case_catalog()[case_id]['domain'] != 'software' and not case_id.startswith('system.update'):
        return False
    value = ' '.join((case_id, title, guide_title)).casefold()
    return bool(re.search(r'package|flatpak|appimage|snap|pacman|zypper|apt[.-]|dpkg|dnf|\brpm-ostree\b|'
                          r'install|uninstall|steam|update|upgrade|repository|source mismatch', value))
