"""Offline browser inventory for beginner help; no execution of a browser.

Only fixed, allowlisted host commands, fixed system desktop directories and
recognised Flatpak IDs are inspected. This does not inspect bookmarks, profiles,
history, web traffic, private windows, credentials or arbitrary user files.
"""
from __future__ import annotations

import re
from pathlib import Path
from ..results import ResultStatus
from .focused_evidence import _report

BROWSER_NAMES = {
    'firefox': 'Firefox', 'librewolf': 'LibreWolf',
    'chromium': 'Chromium', 'google-chrome': 'Google Chrome',
    'brave-browser': 'Brave', 'vivaldi-stable': 'Vivaldi',
    'opera': 'Opera', 'microsoft-edge': 'Microsoft Edge',
    'org.mozilla.firefox': 'Firefox', 'io.gitlab.librewolf-community': 'LibreWolf',
    'org.chromium.chromium': 'Chromium', 'com.google.chrome': 'Google Chrome',
    'com.brave.browser': 'Brave', 'com.vivaldi.vivaldi': 'Vivaldi',
    'com.opera.opera': 'Opera', 'com.microsoft.edge': 'Microsoft Edge',
    'org.gnome.epiphany': 'GNOME Web', 'epiphany': 'GNOME Web',
    'org.kde.falkon': 'Falkon', 'falkon': 'Falkon',
    'org.kde.konqueror': 'Konqueror', 'konqueror': 'Konqueror',
}

DEFAULT = ('xdg-settings', 'get', 'default-web-browser')
HTTPS = ('xdg-mime', 'query', 'default', 'x-scheme-handler/https')
FLATPAK_USER = ('flatpak', 'list', '--app', '--user', '--columns=application')
FLATPAK_SYSTEM = ('flatpak', 'list', '--app', '--system', '--columns=application')


def browser_name(desktop_id: str | None) -> str | None:
    """Use only recognised names; a desktop ID is not proof the app is installed."""
    if not desktop_id or not re.fullmatch(r'[A-Za-z0-9_.+-]{1,200}\.desktop', desktop_id):
        return None
    normalized = desktop_id[:-8].lower()
    if normalized in BROWSER_NAMES:
        return BROWSER_NAMES[normalized]
    # Some desktop environments add an outer prefix to a known package ID.
    if normalized.endswith('-stable') and normalized[:-7] in BROWSER_NAMES:
        return BROWSER_NAMES[normalized[:-7]]
    return None


def _safe_desktop_id(output) -> str | None:
    if (type(getattr(output, 'code', None)) is not int or output.code != 0
            or getattr(output, 'truncated', True) or not isinstance(getattr(output, 'out', None), str)):
        return None
    val = output.out.strip()
    return val if len(val) <= 201 and re.fullmatch(r'[A-Za-z0-9_.+-]+\.desktop', val) else None


def _installed_flatpaks(output):
    if (type(getattr(output, 'code', None)) is not int or output.code != 0
            or getattr(output, 'truncated', True) or not isinstance(getattr(output, 'out', None), str)
            or len(output.out) > 131072):
        return set(), False
    apps = set()
    for line in output.out.splitlines():
        item = line.strip().lower()
        if item in BROWSER_NAMES:
            apps.add(BROWSER_NAMES[item])
    return apps, True


def probe_browser_inventory119(host):
    """Return bounded facts only; missing tools are UNKNOWN, never no browser."""
    default = https = None
    installed = set()
    sources_ok = 0
    try:
        default = _safe_desktop_id(host.command(DEFAULT))
        https = _safe_desktop_id(host.command(HTTPS))
        for argv in (FLATPAK_USER, FLATPAK_SYSTEM):
            names, ok = _installed_flatpaks(host.command(argv))
            installed.update(names)
            sources_ok += int(ok)
    except (OSError, TypeError, AttributeError, ValueError):
        pass
    name = browser_name(default) or browser_name(https)
    facts = []
    if name:
        facts.append('browser_default=' + name.replace(' ', '_'))
    elif default or https:
        facts.append('browser_default=unrecognised')
    else:
        facts.append('browser_default=unknown')
    if default and https:
        facts.append('browser_handlers=' + ('agree' if default == https else 'different'))
    else:
        facts.append('browser_handlers=unknown')
    # Desktop files have several standard locations; failure to find one here
    # is inconclusive on immutable/custom Linux installations.
    if default:
        locations = [Path('/usr/share/applications'), Path('/usr/local/share/applications'),
                     Path('/var/lib/flatpak/exports/share/applications'),
                     Path.home() / '.local/share/applications',
                     Path.home() / '.local/share/flatpak/exports/share/applications']
        try:
            if any(host.exists(str(root / default)) for root in locations):
                facts.append('browser_launcher=found')
            else:
                facts.append('browser_launcher=not_found_in_standard_locations')
        except (OSError, TypeError, ValueError):
            facts.append('browser_launcher=unknown')
    if installed:
        facts.append('browser_flatpak_apps=' + '|'.join(sorted(x.replace(' ', '_') for x in installed)))
    else:
        facts.append('browser_flatpak_apps=' + ('none_found' if sources_ok == 2 else 'unknown'))
    # Recognised default browsers can also be installed via native package
    # sources. Flatpak-only inventory is not a reliable absence check.
    # Package identities are fixed, not chosen by the model or website.
    _browser_apps = {'Firefox': 'firefox', 'Chromium': 'chromium',
                     'LibreWolf': 'librewolf'}
    if name in _browser_apps:
        from .package_sources131 import inspect_sources
        sources = inspect_sources(host, application=_browser_apps[name])
        found = [key for key, reading in sources.items() if reading.presence == 'found']
        facts.append('browser_package_sources=' + ('|'.join(found) if found else 'unknown'))
    state = ResultStatus.INFO if (name or installed) else ResultStatus.UNKNOWN
    return _report('browser_inventory119', state, *facts,
                   explanation='The default browser and available browser installations were checked locally. '
                   'A default setting is not proof that the program can start or load websites. '
                   'No application was launched, no network request was made and nothing was changed.')


PROCESS_NAMES = frozenset(('firefox', 'firefox-esr', 'librewolf', 'chrome',
                           'chromium', 'chromium-browse', 'brave', 'vivaldi-bin',
                           'opera', 'msedge', 'falkon', 'konqueror', 'epiphany'))


def probe_browser_runtime119(host):
    """A bounded /proc observation; no browser launching or PID disclosure.

    'Not seen' is *not* proof that the browser failed: permissions, sandbox
    namespaces, short-lived processes and snapshots can hide a process.
    """
    try:
        entries = host.list_names('/proc')
        pids = [entry for entry in entries if entry.isdecimal() and len(entry) <= 8]
        if len(pids) > 2000:
            return _report('browser_runtime119', ResultStatus.UNKNOWN,
                           'browser_process=unknown',
                           explanation='Too many processes to inspect in a bounded check.')
        active = set()
        unreadable = 0
        for pid in pids:
            try:
                name = host.read('/proc/' + pid + '/comm').strip().casefold()
            except (OSError, PermissionError, ValueError):
                unreadable += 1
                continue
            if name in PROCESS_NAMES:
                active.add(name)
        complete = unreadable == 0
        facts = ('browser_process=' + ('observed' if active else
                 'not_observed_in_sample' if complete else 'unknown'),)
        return _report('browser_runtime119',
                       ResultStatus.INFO if active else ResultStatus.UNKNOWN, *facts,
                       explanation=('A known browser process was observed in a local process snapshot.' if active else
                                    'No known browser process could be confirmed in this sample. '
                                    'That does not establish why a browser cannot launch.'))
    except (OSError, TypeError, ValueError, AttributeError):
        return _report('browser_runtime119', ResultStatus.UNKNOWN,
                       'browser_process=unknown',
                       explanation='The local process list could not be inspected reliably.')
