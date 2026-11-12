"""v71 fixed-argv, target-scoped inventories for five previously pending cases.

These are *observations*, never causes, FACT markers, repair permissions or
consent for network access. User-provided strings are never argv or paths.
"""
from __future__ import annotations

import re
from .bridge import LocalHost
from .target_evidence69 import _view, _json, _lines

PODMAN_CASES = frozenset({
    'software35.containers.disk-space',
    'virtualization.container-disk',
})
VIRTUAL_MACHINE_CASES = frozenset({'virtualization.vm-no-network'})
PACMAN_CASES = frozenset({'software35.packages.pacman-partial-upgrade'})
PATH_CASES = frozenset({'software35.development.path-command-shadowed'})
SUPPORTED_CASES71 = PODMAN_CASES | VIRTUAL_MACHINE_CASES | PACMAN_CASES | PATH_CASES
assert len(SUPPORTED_CASES71) == 5

PODMAN_PS = ('podman', 'ps', '-a', '--format', 'json')
PODMAN_INFO = ('podman', 'info', '--format', 'json')
VIRSH_NAMES = ('virsh', 'list', '--all', '--name')
PACMAN_NAMES = ('pacman', '-Qq')
KNOWN_BIN_DIRS = ('/usr/local/bin', '/usr/bin')

# No paths, options, shell syntax or special colon-based Podman identifiers.
NAME = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.+-]{0,63}\Z')
PACKAGE = re.compile(r'[A-Za-z0-9][A-Za-z0-9@._+-]{0,127}\Z')


def _podman(host: LocalHost, target: str):
    if not NAME.fullmatch(target):
        return _view('unknown', 'Geef een exacte, eenvoudige containernaam op; geen opslagpad of opdracht.')
    containers = _json(host, PODMAN_PS)
    info = _json(host, PODMAN_INFO)
    if not isinstance(containers, list) or len(containers) > 1000 or not isinstance(info, dict):
        return _view('unknown', 'De Podman-container- of opslaginventaris is niet volledig beschikbaar.')
    store = info.get('store')
    if not isinstance(store, dict) or not isinstance(store.get('graphRoot'), str):
        return _view('unknown', 'Podman heeft geen eenduidige lokale opslaglocatie gerapporteerd.')
    # Do not use a returned location to construct a read or shell command.
    root = store['graphRoot']
    if not root.startswith('/') or '..' in root.split('/') or len(root) > 1024:
        return _view('unknown', 'De Podman-opslaglocatie is niet veilig te interpreteren.')
    matches = 0
    for item in containers:
        if not isinstance(item, dict):
            return _view('unknown', 'Een Podman-containerrecord heeft een onverwacht formaat.')
        names = item.get('Names')
        if isinstance(names, str):
            names = [names]
        if not isinstance(names, list) or not names or any(
            not isinstance(n, str) or not NAME.fullmatch(n) for n in names
        ):
            return _view('unknown', 'Podman rapporteerde een onvolledige containeridentiteit.')
        if target in names:
            matches += 1
    if matches > 1:
        return _view('unknown', 'De containernaam is niet uniek in de Podman-inventaris.')
    if matches == 0:
        return _view('observed', 'De gekozen containernaam komt niet voor in de volledige lokaal gelezen Podman-lijst. '
                     'Dit bewijst geen ontbrekende data of mislukte containerstart.')
    # Measure the backing filesystem (not the container's own storage).
    # The path is system-reported and validated; no user note becomes a path.
    try:
        usage = host.disk_usage(root)
        total, free = usage.total, usage.free
        if (type(total) is not int or type(free) is not int or
                total <= 0 or not 0 <= free <= total):
            raise ValueError('invalid disk usage')
    except (OSError, ValueError, TypeError, AttributeError, OverflowError):
        return _view('unknown', 'Podman is aangetroffen maar het bestandssysteem van de opslag '
                     'kon niet veilig worden gemeten; opslagstatus onbekend.')
    pct = round(100 * free / total, 1)
    return _view('observed', 'De gekozen container is aangetroffen. Het bestandssysteem '
                 f'waarop Podman de opslag bewaart rapporteert {pct}% vrije ruimte. '
                 'Dit is niet de opslagomvang of quota van deze individuele container; '
                 'een containergerelateerd opslagprobleem is niet bewezen.')


def _vm(host: LocalHost, target: str):
    if not NAME.fullmatch(target):
        return _view('unknown', 'Geef een exacte VM-naam zonder pad of opdrachten op.')
    rows = _lines(host, VIRSH_NAMES)
    if rows is None or len(rows) > 1000 or any(len(row) > 128 for row in rows):
        return _view('unknown', 'De lokale libvirt-domeininventaris is niet volledig leesbaar.')
    names = [r.strip() for r in rows if r.strip()]
    if any(not NAME.fullmatch(n) for n in names) or len(names) != len(set(names)):
        return _view('unknown', 'De libvirt-domeinidentiteiten zijn onvolledig of niet uniek.')
    return _view('observed', 'De opgegeven VM-naam '
                 + ('is in de lokale libvirt-inventaris gevonden.' if target in names
                    else 'staat niet in de lokaal opgevraagde libvirt-inventaris.')
                 + ' Dit test geen virtuele netwerkadapter, guest-IP of bereikbaarheid; '
                   'andere hypervisors kunnen buiten beeld vallen.')


def _pacman(host: LocalHost, target: str):
    if not PACKAGE.fullmatch(target) or target.startswith('-'):
        return _view('unknown', 'Gebruik de exacte pacman-pakketnaam zonder pad of opdracht.')
    rows = _lines(host, PACMAN_NAMES)
    if rows is None or len(rows) > 100000 or any(len(row) > 256 for row in rows):
        return _view('unknown', 'De lokale pacman-pakketlijst is onleesbaar of onvolledig.')
    names = [r.strip() for r in rows if r.strip()]
    if any(not PACKAGE.fullmatch(n) for n in names) or len(names) != len(set(names)):
        return _view('unknown', 'De pacman-inventaris bevat ongeldige of dubbele pakketnamen.')
    return _view('observed', 'De gekozen pakketnaam '
                 + ('staat in de lokale pacman-pakketlijst.' if target in names
                    else 'staat niet in deze lokale pacman-pakketlijst.')
                 + ' Versiecompatibiliteit, repositorytoestand en gedeeltelijke upgrades '
                   'zijn hierdoor niet bewezen; er wordt niets bijgewerkt.')


def _path_inventory(host: LocalHost, target: str):
    if not NAME.fullmatch(target) or target in ('.', '..'):
        return _view('unknown', 'Gebruik alleen de exacte programmabestandsnaam, zonder pad of opdracht.')
    found = []
    for directory in KNOWN_BIN_DIRS:
        try:
            names = host.list_names(directory)
        except OSError:
            return _view('unknown', 'Niet alle vaste programmamappen konden worden geïnventariseerd.')
        if len(names) > 100000 or any(not isinstance(n, str) or len(n) > 256 for n in names):
            return _view('unknown', 'Een programmamap bevat ongeldige of te veel vermeldingen.')
        if len(names) != len(set(names)):
            return _view('unknown', 'Een programmamap bevat dubbele vermeldingen.')
        if target in names:
            found.append(directory)
    return _view('observed', 'De exacte programmabestandsnaam komt voor in '
                 + ('beide vaste programmamappen.' if len(found) == 2 else
                    'één vaste programmamap.' if found else 'geen van de twee vaste programmamappen.')
                 + ' Dit controleert geen uitvoerrechten, symlinks, actieve PATH-volgorde '
                   'of het daadwerkelijk gestarte programma; command shadowing is niet bewezen.')


def inspect_target71(host: LocalHost, case_id: str, target: str):
    try:
        if case_id in PODMAN_CASES:
            return _podman(host, target)
        if case_id in VIRTUAL_MACHINE_CASES:
            return _vm(host, target)
        if case_id in PACMAN_CASES:
            return _pacman(host, target)
        if case_id in PATH_CASES:
            return _path_inventory(host, target)
    except (OSError, ValueError, TypeError, AttributeError, OverflowError):
        return _view('unknown', 'De gerichte lokale inventaris is mislukt; oorzaak onbekend.')
    return _view('unknown', 'Geen veilige inventariscontrole voor dit dossier beschikbaar.')
