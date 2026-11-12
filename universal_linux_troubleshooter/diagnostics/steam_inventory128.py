"""Bounded, strictly read-only Steam presence/library inventory for Manual guides.

This is an observation, not a diagnosis. It never reads credentials, game saves,
account data, appmanifest contents or arbitrary logs, and never starts Steam.
"""
from __future__ import annotations

from pathlib import Path
import re

from ..results import DiagnosticResult, ResultStatus
from .package_sources131 import inspect_sources, description

STEAM_APP_ID = 'com.valvesoftware.Steam'
FLATPAK_LISTS = (
    ('flatpak', 'list', '--app', '--user', '--columns=application'),
    ('flatpak', 'list', '--app', '--system', '--columns=application'),
)


def probe_steam_inventory128(host) -> DiagnosticResult:
    home = Path.home()
    native_roots = (home/'.local/share/Steam', home/'.steam/steam', home/'.steam/root')
    flatpak_roots = (
        home/'.var/app/com.valvesoftware.Steam/data/Steam',
        home/'.var/app/com.valvesoftware.Steam/.local/share/Steam',
    )
    native = any(host.exists(str(p)) for p in native_roots)
    sandbox = any(host.exists(str(p)) for p in flatpak_roots)
    sources = inspect_sources(host, application='steam')
    flatpak_registered = any(sources[k].presence == 'found' for k in ('flatpak_user', 'flatpak_system'))
    installed_native = any(sources[k].presence == 'found' for k in ('rpm', 'deb', 'pacman', 'snap', 'apk'))
    found_manifests = 0
    has_manifest_info = False
    # Fixed roots only, bounded directory listing, no reading manifest contents.
    for root in (native_roots[0], flatpak_roots[0]):
        apps = root/'steamapps'
        if not host.exists(str(apps)):
            continue
        try:
            names = host.list_names(str(apps))
        except (OSError, PermissionError):
            continue
        if len(names) > 20000:
            continue
        has_manifest_info = True
        found_manifests += sum(1 for name in names if re.fullmatch(r'appmanifest_[0-9]{1,12}\.acf',name))
    evidence = (
        'FACT:steam_flatpak_registration=' + ('observed' if flatpak_registered else 'not_observed_in_checked_scopes' if all(sources[k].state == 'checked' for k in ('flatpak_user', 'flatpak_system')) else 'unknown'),
        'FACT:steam_native_user_data=' + ('observed' if native else 'not_observed_in_checked_paths'),
        'FACT:steam_flatpak_user_data=' + ('observed' if sandbox else 'not_observed_in_checked_paths'),
        'FACT:steam_local_manifests=' + (str(found_manifests) if has_manifest_info else 'unknown'),
        *(f'FACT:steam_{key}=' + ('observed' if value.presence == 'found' else 'not_observed_in_checked_scopes' if value.presence == 'not_found' else 'unknown') for key, value in sources.items()),
        'NOTE:Package availability is checked through separate local databases, including RPM (DNF/Zypper), DEB, Pacman, Snap and APK. Failed/unavailable sources never prove absence.',
        'NOTE:Only fixed user-local Steam directories were inspected. Other Steam libraries and Steam services were not checked.',
    )
    discovered = native or sandbox or flatpak_registered or installed_native
    return DiagnosticResult(
        'focused', 'steam_inventory128',
        ResultStatus.INFO if discovered else ResultStatus.UNKNOWN,
        'Local Steam installation information',
        ('Steam-related local data was observed. This does not prove the client or any game works.'
         if discovered else 'Steam was not confirmed by the available local sources. Unavailable sources were not ruled out.'),
        'The selected troubleshooting guide can help narrow the issue. No files or settings were changed.',
        evidence,
    )
