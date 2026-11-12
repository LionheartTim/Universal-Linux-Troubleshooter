"""v81 corroboration: cross-check two read-only interfaces to Linux inventories.

This is deliberately NOT a new causal event rule. Fixed argv only; the target
is validated locally, never passed to subprocess or used in a filesystem path
until it has been reduced to a strict PCI BDF.
"""
from __future__ import annotations

import re
from .bridge import LocalHost
from .target_evidence69 import _view, _lines, PCI_DEVICES

GPU_CASE81 = 'hardware34.gpu.gpu-not-enumerated'
SOURCE_CASE81 = 'software35.packages.app-source-mismatch'
CASES81 = frozenset((GPU_CASE81, SOURCE_CASE81))

USER_ORIGIN81 = ('flatpak', 'list', '--app', '--user', '--columns=application,origin')
SYSTEM_ORIGIN81 = ('flatpak', 'list', '--app', '--system', '--columns=application,origin')
APP_ID81 = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]*(?:\.[A-Za-z0-9][A-Za-z0-9_-]*){2,}\Z')
BDF81 = re.compile(r'(?:[0-9a-fA-F]{4}:)?[0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.[0-7]\Z')
HEX = re.compile(r'0x[0-9a-fA-F]{4,6}\Z')
ORIGIN = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.+-]{0,127}\Z')


def _flatpak_origin(host: LocalHost, target: str):
    if not APP_ID81.fullmatch(target) or len(target) > 170:
        return _view('unknown', 'Gebruik een exacte Flatpak-app-ID; geen bestandsnaam of opdracht.')
    entries = []
    for scope, command in (('USER', USER_ORIGIN81), ('SYSTEM', SYSTEM_ORIGIN81)):
        rows = _lines(host, command)
        if rows is None or len(rows) > 20000:
            return _view('unknown', 'De twee Flatpak-installatiebronnen konden niet volledig worden gelezen.')
        scope_matches = []
        for row in rows:
            # Flatpak --columns emits tab-delimited columns; any malformed or
            # truncated record makes a negative claim unsafe.
            parts = row.split('\t')
            if len(parts) != 2 or len(row) > 512:
                return _view('unknown', 'De Flatpak-bronlijst bevat onvolledige of onleesbare kolommen.')
            app, origin = [x.strip() for x in parts]
            if app == 'Application' and origin == 'Origin':
                continue
            if not APP_ID81.fullmatch(app) or not ORIGIN.fullmatch(origin):
                return _view('unknown', 'De Flatpak-bronlijst bevat een ongeldige app-ID of herkomst.')
            if app == target:
                scope_matches.append(origin)
        if len(scope_matches) > 1:
            return _view('unknown', 'Dezelfde app-ID staat dubbel binnen één Flatpak-installatiescope.')
        if scope_matches:
            entries.append((scope, scope_matches[0]))
    if len(entries) == 2 and entries[0][1] != entries[1][1]:
        return _view('observed',
            'Dezelfde exacte Flatpak-app-ID heeft in USER en SYSTEM aantoonbaar twee verschillende remote-herkomsten. '
            'Dit is een concreet herkomstverschil, geen bewijs dat de actieve app uit de verkeerde bron start.')
    if len(entries) == 2:
        return _view('observed',
            'De exacte app-ID bestaat zowel onder USER als SYSTEM met dezelfde benoemde remote-herkomst. '
            'Welke installatie door de desktop wordt gestart en of de commit identiek is, blijft onbekend.')
    if entries:
        return _view('observed', 'De exacte app-ID is in één Flatpak-scope met een herkomst aangetroffen. '
                     'RPM-, DEB- en AppImage-installaties zijn niet met deze app gelijkgesteld.')
    return _view('observed', 'De opgegeven app-ID ontbreekt in beide volledig gelezen standaard-Flatpak-scopes. '
                 'Dit sluit andere installaties of een afwijkende app-ID niet uit.')


def _gpu_crosscheck(host: LocalHost, target: str):
    if not BDF81.fullmatch(target):
        return _view('unknown', 'Gebruik een exact PCI-slotadres zoals 01:00.0 of 0000:01:00.0.')
    bdf = target.lower()
    canonical = bdf if len(bdf) == 12 else '0000:' + bdf
    short = canonical[5:]
    rows = _lines(host, PCI_DEVICES)
    if rows is None or not 0 < len(rows) <= 20000:
        return _view('unknown', 'De volledige lokale PCI-inventaris ontbreekt.')
    hits = [line for line in rows if re.match(r'^(?:' + re.escape(canonical) + '|'
              + re.escape(short) + r')\s', line, flags=re.I)]
    if len(hits) != 1 or len(hits[0]) > 512:
        return _view('unknown', 'Het opgegeven PCI-slot is niet uniek in de PCI-lijst herkend; firmwarestatus onbekend.')
    line = hits[0]
    if not re.search(r'\b(?:VGA compatible controller|3D controller|Display controller)\b', line, re.I):
        return _view('unknown', 'Het opgegeven PCI-slot is geen eenduidig herkende grafische controller.')
    pairs = re.findall(r'\[([0-9a-fA-F]{4}):([0-9a-fA-F]{4})\]', line)
    if not pairs:
        return _view('unknown', 'Het PCI-apparaat heeft geen eenduidig leesbare vendor/device-identiteit.')
    base = '/sys/bus/pci/devices/' + canonical
    try:
        cls = host.read(base + '/class').strip()
        vendor = host.read(base + '/vendor').strip()
        device = host.read(base + '/device').strip()
        if not (HEX.fullmatch(cls) and re.fullmatch(r'0x[0-9a-fA-F]{4}', vendor)
                and re.fullmatch(r'0x[0-9a-fA-F]{4}', device)):
            return _view('unknown', 'De PCI-sysfs-identiteit is ongeldig of onvolledig.')
        if not cls.lower().startswith('0x03'):
            return _view('unknown', 'De kernel identificeert dit PCI-slot niet als beeldschermcontroller.')
        if (vendor[2:].lower(), device[2:].lower()) not in {(a.lower(), b.lower()) for a,b in pairs}:
            return _view('unknown', 'PCI-lijst en kernel-sysfs spreken elkaar tegen over de GPU-identiteit.')
        driver_bound = host.exists(base + '/driver')
    except (OSError, ValueError, TypeError, AttributeError):
        return _view('unknown', 'Het PCI-apparaat kon niet met kernel-sysfs worden vergeleken.')
    return _view('observed',
        'Dezelfde grafische controller is op exact dit PCI-slot zowel in de PCI-lijst als in kernel-sysfs vastgesteld; '
        + ('een kernel-driver is gekoppeld.' if driver_bound else 'geen gekoppelde kernel-driver is in deze meting gezien.')
        + ' Dit bewijst geen firmwareconfiguratie, beeldoutput, drivergezondheid of de verwachte fysieke GPU.')


def inspect_target81(host: LocalHost, case_id: str, target: str):
    try:
        if case_id == GPU_CASE81:
            return _gpu_crosscheck(host, target)
        if case_id == SOURCE_CASE81:
            return _flatpak_origin(host, target)
    except (OSError, ValueError, TypeError, AttributeError, OverflowError):
        return _view('unknown', 'De onafhankelijke bronvergelijking is niet volledig beschikbaar.')
    return _view('unknown', 'Geen gecontroleerde bronvergelijking voor dit dossier.')
