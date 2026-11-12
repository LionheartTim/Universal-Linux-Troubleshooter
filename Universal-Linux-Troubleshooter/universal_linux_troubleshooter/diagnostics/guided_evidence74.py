"""v74: Five bounded, user-initiated local-evidence procedures.

Only observed facts are reported. A local mismatch is not a verified root cause,
not a FACT marker, not a graph route, and never a repair authorization.  User
paths are explicitly selected through the UI; no shell, subprocess, execution,
network operation or file mutation uses them.
"""
from __future__ import annotations

from dataclasses import dataclass
import ipaddress
import os
from pathlib import Path
import re
import stat

from ..results import DiagnosticResult, ResultStatus

FILE_READ_CASE = 'applications.permission-denied'
FOLDER_WRITE_CASE = 'storage.file-permission-denied'
VENV_CASE = 'software35.development.venv-wrong-python'
KDE_SHORTCUT_CASE = 'software35.desktop.shortcut-conflict'
HOSTNAME_CASE = 'software35.network.hostname-resolution'
from .guided_evidence80 import CASES80, APPIMAGE_CASE80, PATH_SHADOW_CASE80
CASES74 = frozenset((FILE_READ_CASE, FOLDER_WRITE_CASE, VENV_CASE, KDE_SHORTCUT_CASE, HOSTNAME_CASE)) | CASES80
PATH_CASES74 = frozenset((FILE_READ_CASE, FOLDER_WRITE_CASE, VENV_CASE, APPIMAGE_CASE80))
USER_SETTINGS_CASES74 = frozenset((KDE_SHORTCUT_CASE,))


@dataclass(frozen=True)
class GuidedObservation74:
    state: str  # observed, absent, unknown
    message: str
    next_steps: str


def _unknown(message: str) -> GuidedObservation74:
    return GuidedObservation74('unknown', message, 'No correction is authorized; check the exact affected target and retry.')


def _status(case_id: str, finding: GuidedObservation74) -> DiagnosticResult:
    # A measured incompatibility is still only an observation, not the confirmed
    # cause of the complaint. No FACT: markers are emitted, even if the target
    # or source file included such text.
    return DiagnosticResult('focused', 'guided_evidence74',
        ResultStatus.INFO if finding.state != 'unknown' else ResultStatus.UNKNOWN,
        'Gericht, alleen-lezenonderzoek',
        finding.message, finding.next_steps, ())


def _safe_selected_path(path: str | None, *, directory: bool) -> Path | None:
    if not isinstance(path, str) or not path.startswith('/') or len(path) > 1024 or '\x00' in path:
        return None
    item = Path(path)
    try:
        # Explicit selection only, and no symlink target surprise.
        if item.is_symlink() or not (item.is_dir() if directory else item.is_file()):
            return None
    except (OSError, ValueError):
        return None
    return item


def _file_access(path: str | None, *, write: bool) -> GuidedObservation74:
    target = _safe_selected_path(path, directory=write)
    if target is None:
        return _unknown('Geen geldig, expliciet geselecteerd ' + ('map' if write else 'bestand') + ' voor deze controle.')
    try:
        # Guard against a path being replaced between the explicit chooser,
        # the access check and the metadata lookup. The access result must
        # refer to the same device/inode; otherwise no conclusion is safe.
        before = target.lstat()
        if stat.S_ISLNK(before.st_mode):
            return _unknown('Het gekozen object is gewijzigd naar een symlink; controle afgebroken.')
        if write:
            # No test file is ever created. This probes directory search/write
            # permission and the filesystem's read-only flag.
            permitted = os.access(target, os.W_OK | os.X_OK, effective_ids=True)
            filesystem = os.statvfs(target)
            readonly = bool(filesystem.f_flag & getattr(os, 'ST_RDONLY', 1))
            if readonly:
                permitted = False
        else:
            permitted = os.access(target, os.R_OK, effective_ids=True)
            readonly = False
        s = target.lstat()
        if (before.st_dev, before.st_ino, before.st_mode, before.st_ctime_ns,
             before.st_mtime_ns, before.st_size) != (s.st_dev, s.st_ino, s.st_mode,
             s.st_ctime_ns, s.st_mtime_ns, s.st_size):
            return _unknown('Het gekozen bestand of de map is tijdens de controle veranderd.')
        owner = s.st_uid
        euid = os.geteuid()
        if not (stat.S_ISDIR(s.st_mode) if write else stat.S_ISREG(s.st_mode)):
            return _unknown('Het geselecteerde objecttype is veranderd tijdens de controle.')
    except (OSError, ValueError, TypeError, NotImplementedError):
        return _unknown('Bestandsmetadata en de effectieve toegang zijn niet eenduidig te meten.')
    if permitted:
        return GuidedObservation74('absent',
            'De huidige gebruiker heeft volgens de lokale toegangscontrole de gevraagde toegang. '
            'Dit sluit een sandboxweigering, mislukte echte bestandsbewerking of app-afhankelijke fout niet uit.',
            'Herhaal de exacte bewerking in de betrokken app; deze controle verandert geen bestanden.')
    relation = ('De eigenaar van het gekozen object verschilt van de effectieve gebruiker. '
                if owner != euid else 'De huidige gebruiker is eigenaar van het geselecteerde object. ')
    readonly_note = ('De onderliggende filesystem-mount is als alleen-lezen gerapporteerd. '
                     if readonly else '')
    return GuidedObservation74('observed',
        'De actuele gebruikerscontext krijgt volgens de lokale toegangscontrole geen '
        + ('schrijf- en zoektoegang tot deze map. ' if write else 'leestoegang tot dit bestand. ')
        + readonly_note + relation + 'Dit is geen volledig bewijs voor de fout in een andere applicatie.',
        'Controleer de toegang voor uitsluitend dit bestand of deze map in de bestandsbeheerder. '
        'Controleer desgewenst ook sandbox-/ACL-beleid. Geen automatische chmod/chown en geen recursieve wijziging.')


def _read_complete_file(path: Path, limit: int) -> str | None:
    """Bounded, no-follow complete read; never accept partial config data."""
    fd = None
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0))
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            return None
        chunks = bytearray()
        while len(chunks) <= limit:
            block = os.read(fd, min(8192, limit + 1 - len(chunks)))
            if not block:
                return chunks.decode('utf-8')
            chunks.extend(block)
        return None
    except (OSError, ValueError, UnicodeError, TypeError):
        return None
    finally:
        if fd is not None:
            os.close(fd)


def _read_first_line(path: Path, max_bytes: int = 1024) -> str | None:
    # The only selected-project file reads are fixed metadata files. Open with
    # no-follow to prevent symlinked pip wrappers or configuration escaping.
    fd = None
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0))
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            return None
        raw = os.read(fd, max_bytes)
        if b"\n" not in raw and len(raw) == max_bytes:
            return None
        return raw.decode('utf-8').splitlines()[0] if raw else ''
    except (OSError, UnicodeError, ValueError, IndexError):
        return None
    finally:
        if fd is not None:
            os.close(fd)


def _venv(path: str | None) -> GuidedObservation74:
    selected = _safe_selected_path(path, directory=True)
    if selected is None:
        return _unknown('Selecteer expliciet de map van de te onderzoeken virtuele Python-omgeving.')
    cfg = selected / 'pyvenv.cfg'
    pip = selected / 'bin' / 'pip'
    python = selected / 'bin' / 'python'
    try:
        # pyvenv.cfg must be read *fully*. Its first line alone is not proof
        # that the chosen directory is a coherent virtual environment.
        config = _read_complete_file(cfg, 8192)
        line = _read_first_line(pip)
        if (config is None or line is None or not python.exists()
                or '\x00' in config or not re.search(r'(?m)^home\s*=\s*\S+', config)):
            return _unknown('pyvenv.cfg, de pip-startregel of bin/python is niet volledig beschikbaar.')
        if not line.startswith('#!') or not line[2:].strip().startswith('/'):
            return _unknown('Het pip-startscript gebruikt geen rechtstreeks, eenduidig Python-pad.')
        # A shebang is not executed. Only syntactically compare its interpreter
        # with a symlink-resolved path already inside the selected venv.
        interpreter = line[2:].strip().split()[0]
        if '\x00' in interpreter or len(interpreter) > 1024:
            return _unknown('Het Python-interpreterpad in de pip-startregel is ongeldig.')
        expected = os.path.normpath(str(selected / 'bin'))
        actual = os.path.normpath(str(Path(interpreter).parent))
        is_python_name = bool(re.fullmatch(r'python(?:3(?:\.\d{1,2})?)?', Path(interpreter).name))
        if not (python.is_file() and os.access(python, os.X_OK)):
            return _unknown('Het geselecteerde Python-programma is niet uitvoerbaar volgens bestandsmetadata.')
    except (OSError, ValueError, RuntimeError, TypeError):
        return _unknown('De virtuele omgeving kon niet veilig als één consistent geheel worden onderzocht.')
    if actual != expected or not is_python_name:
        return GuidedObservation74('observed',
            'Het pip-startscript verwijst naar een ander Python-binairebestand dan bin/python van de gekozen omgeving. '
            'De installatiebestemming van een daadwerkelijk uitgevoerde pip-opdracht is hiermee nog niet bewezen.',
            'Gebruik voor deze omgeving uitsluitend het bijbehorende python -m pip in plaats van het pip-startscript; '
            'controleer de import daarna opnieuw. De Troubleshooter voert deze opdracht niet uit.')
    return GuidedObservation74('absent',
        'Het pip-startscript en bin/python verwijzen naar hetzelfde Python-binairebestand. '
        'Activering, imports, pakketlocaties en de interpreter van de betrokken applicatie zijn niet bewezen.',
        'Vergelijk de Python-interpreter die de app gebruikt met die van de geselecteerde omgeving; wijzig nog niets.')


_SHORTCUT = re.compile(r'[A-Za-z0-9+\- ]{2,80}\Z')


def _shortcut(target: str | None, *, config_path: str | None = None) -> GuidedObservation74:
    if not isinstance(target, str) or not _SHORTCUT.fullmatch(target) or '/' in target:
        return _unknown('Vul de exacte sneltoets in, bijvoorbeeld Ctrl+Alt+T.')
    session = os.environ.get('XDG_CURRENT_DESKTOP', '')[:100].upper()
    if 'KDE' not in re.split(r'[:; ]+', session):
        return _unknown('Voor deze controle is een actieve KDE-sessie vereist; andere desktopomgevingen worden niet als KDE geïnterpreteerd.')
    config = Path(config_path) if config_path else Path.home() / '.config' / 'kglobalshortcutsrc'
    # Do not use user-controlled paths in the production call.
    raw = _read_complete_file(config, 131072)
    if raw is None:
        return _unknown('Het KDE-sneltoetsbestand ontbreekt of kon niet volledig worden gelezen.')
    desired = target.replace(' ', '').casefold()
    matches = set()
    section = ''
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith('[') and line.endswith(']'):
            section = line[1:-1]
            continue
        if not line or line[0] in '#;' or '=' not in line or not section:
            continue
        action, binding = line.split('=', 1)
        if not action or len(binding) > 1000:
            return _unknown('Een sneltoetsregel heeft onverwachte gegevens.')
        if action.casefold() in ('_k_friendly_name',) or section.casefold() == 'general':
            continue
        first = binding.split(',', 1)[0]
        if any(t.replace(' ', '').casefold() == desired for t in first.split(';')):
            matches.add((section, action))
    if len(matches) >= 2:
        return GuidedObservation74('observed',
            'De opgegeven sneltoets komt voor bij meerdere verschillende KDE-globale acties in dezelfde configuratie. '
            'Of beide bindingen actief zijn of een toepassing de toets onderschept is niet bewezen.',
            'Open KDE System Settings → Keyboard → Shortcuts en controleer uitsluitend deze toets. '
            'Wijzig alleen de bedoelde gebruikersbinding; gebruik daarna Rescan.')
    if len(matches) == 1:
        return GuidedObservation74('absent',
            'De opgegeven sneltoets is aan één KDE-globale actie gekoppeld. '
            'Applicatiesneltoetsen en de actieve focus zijn hiermee niet gecontroleerd.',
            'Controleer of de sneltoets binnen de betrokken app een andere functie heeft; laat de globale instelling intact.')
    return GuidedObservation74('absent',
        'Geen overeenkomende KDE-globale actie in het volledig gelezen instellingenbestand. '
        'Een applicatiesneltoets of andere desktopsessie kan alsnog bestaan.',
        'Controleer de sneltoets in de actieve applicatie; geen globale wijziging uitvoeren.')


def _hostname(target: str | None, *, hosts_file: str = '/etc/hosts') -> GuidedObservation74:
    if not isinstance(target, str) or len(target) > 80 or len(target.split()) != 2:
        return _unknown('Geef één hostnaam en één verwacht IP-adres op, gescheiden door een spatie.')
    host, expected = target.split()
    if (not re.fullmatch(r'[A-Za-z0-9.-]{1,63}(?:\.[A-Za-z0-9.-]{1,63})*', host)
        or '..' in host or host.startswith('-') or any(label.endswith('-') for label in host.split('.'))):
        return _unknown('De hostnaam is niet geldig of niet eenduidig.')
    try:
        expected_ip = ipaddress.ip_address(expected)
        contents = _read_complete_file(Path(hosts_file), 16384)
    except (OSError, UnicodeError, ValueError):
        return _unknown('Het hosts-bestand is niet volledig beschikbaar.')
    if contents is None:
        return _unknown('Het hosts-bestand is niet volledig beschikbaar.')
    addresses = set()
    for line in contents.splitlines():
        fields = line.split('#', 1)[0].split()
        if not fields:
            continue
        if len(fields) < 2:
            return _unknown('Het hosts-bestand bevat een onvolledige adresregel.')
        try:
            ip = ipaddress.ip_address(fields[0])
        except ValueError:
            return _unknown('Het hosts-bestand bevat een ongeldig IP-adres.')
        if host.casefold().rstrip('.') in {field.casefold().rstrip('.') for field in fields[1:]}:
            addresses.add(ip)
    if len(addresses) > 1:
        return _unknown('Het hosts-bestand vermeldt verschillende IP-adressen voor dezelfde naam; er is geen eenduidige conclusie.')
    if not addresses:
        return GuidedObservation74('absent',
            'De hostnaam heeft geen lokale hosts-overschrijving. Het ingevoerde verwachte adres is niet onafhankelijk geverifieerd.',
            'Controleer na afzonderlijke toestemming de effectieve NSS/DNS-resolutie, voordat je configuratie wijzigt.')
    if next(iter(addresses)) != expected_ip:
        return GuidedObservation74('observed',
            'Het hosts-bestand koppelt de gekozen naam aan een ander IP-adres dan het door de gebruiker opgegeven verwachte adres. '
            'De juistheid van het verwachte adres en het effectieve NSS/DNS-resultaat zijn nog niet vastgesteld.',
            'Controleer het bedoelde adres bij de netwerkbeheerder; pas een lokale hosts-vermelding alleen met bevestiging van het juiste adres aan. Daarna Rescan.')
    return GuidedObservation74('absent',
        'De lokale hosts-vermelding komt overeen met het opgegeven verwachte IP-adres, '
        'maar de werkelijke NSS/DNS-uitkomst is niet gecontroleerd.',
        'Als het probleem blijft, onderzoek met toestemming de actuele naamresolutie en de betrokken applicatie.')


def inspect_guided74(case_id: str, *, selected_path: str | None = None,
                     target_note: str | None = None, consent: bool = False) -> DiagnosticResult:
    """An explicit per-run consent flag is mandatory for all five procedures."""
    if case_id in CASES80:
        from .guided_evidence80 import inspect_guided80
        return inspect_guided80(case_id, selected_path=selected_path, target_note=target_note, consent=consent)
    if case_id not in CASES74:
        return _status(case_id, _unknown('Geen gevalideerde gerichte controle beschikbaar.'))
    if not consent:
        return _status(case_id, _unknown('De vereiste toestemming voor deze afzonderlijke controle is niet gegeven.'))
    try:
        if case_id == FILE_READ_CASE:
            return _status(case_id, _file_access(selected_path, write=False))
        if case_id == FOLDER_WRITE_CASE:
            return _status(case_id, _file_access(selected_path, write=True))
        if case_id == VENV_CASE:
            return _status(case_id, _venv(selected_path))
        if case_id == KDE_SHORTCUT_CASE:
            return _status(case_id, _shortcut(target_note))
        if case_id == HOSTNAME_CASE:
            return _status(case_id, _hostname(target_note))
    except (OSError, ValueError, TypeError, PermissionError, OverflowError):
        pass
    return _status(case_id, _unknown('Het gerichte onderzoek is niet betrouwbaar afgerond.'))


# Fixed, user-only followups; never supplied by a result from an untrusted
# source. These do not have route approval status.
SAFE_FOLLOWUPS74 = {
    FILE_READ_CASE: 'Verify the exact denied operation and the involved application; inspect this file’s permissions only. Do not change access recursively.',
    FOLDER_WRITE_CASE: 'Use the file manager to review ownership and access on this folder only. No automatic chmod/chown or write test.',
    VENV_CASE: 'Check which interpreter the project invokes and use the selected environment’s python -m pip only after confirming its identity.',
    KDE_SHORTCUT_CASE: 'In KDE System Settings → Keyboard → Shortcuts, check the exact user binding and test again; other desktops require a separate supported inspection.',
    HOSTNAME_CASE: 'Confirm the expected IP with the network owner before changing the local hosts entry; actual DNS/NSS has not been tested.',
    APPIMAGE_CASE80: 'Compare the selected file with a independently verified release checksum. The supplied SHA-256 is not proof of origin; preserve the original.',
    PATH_SHADOW_CASE80: 'Verify executable selection in the affected host shell or application. The current process PATH may differ, particularly under Flatpak.',
}
