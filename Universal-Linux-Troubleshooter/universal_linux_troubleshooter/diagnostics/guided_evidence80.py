"""v80: two optional, target-specific *comparisons*, not causal event rules.

A selected AppImage may be compared against a user-supplied prior SHA256.
The exact executable name may be checked against the current process PATH,
but that environment is not necessarily a user's terminal or the Linux host
when run inside Flatpak. These probes never execute, mutate or trust a target
as a shell argument; their observations cannot promote diagnostic routes.
"""
from __future__ import annotations

import hashlib
import hmac
import os
from pathlib import Path
import re
import stat

APPIMAGE_CASE80 = 'software35.appimage.update-source-change'
PATH_SHADOW_CASE80 = 'software35.development.path-command-shadowed'
CASES80 = frozenset({APPIMAGE_CASE80, PATH_SHADOW_CASE80})
APPIMAGE_MAX_BYTES = 1024 ** 3  # Bound I/O to a 1 GiB selected file.
_FIXED_BINS = ('/usr/local/bin', '/usr/bin')
_EXE_NAME = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.+-]{0,63}\Z')
_SHA256 = re.compile(r'[a-fA-F0-9]{64}\Z')


def _appimage_sha256(path: str | None, expected_digest: str | None):
    """Compare a user-selected file to a known digest; trust neither as provenance.

    Never open a symlink; verify the same inode and metadata before and after
    reading (also after close, to detect replacement while the file was read).
    """
    from .guided_evidence74 import GuidedObservation74, _unknown, _safe_selected_path
    if not isinstance(expected_digest, str) or not _SHA256.fullmatch(expected_digest):
        return _unknown('Geef de onafhankelijk gecontroleerde SHA-256 van de originele AppImage op (64 hexadecimale tekens).')
    selected = _safe_selected_path(path, directory=False)
    if selected is None or selected.suffix.casefold() != '.appimage':
        return _unknown('Selecteer expliciet een regulier .AppImage-bestand; geen symlink of map.')
    try:
        before = selected.lstat()
        if not stat.S_ISREG(before.st_mode) or not 0 < before.st_size <= APPIMAGE_MAX_BYTES:
            return _unknown('De AppImage is leeg of groter dan de veilige meetlimiet van 1 GiB.')
        flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)
        hasher = hashlib.sha256()
        with os.fdopen(os.open(selected, flags), 'rb', buffering=0) as f:
            opened = os.fstat(f.fileno())
            signature = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mode,
                                   s.st_mtime_ns, s.st_ctime_ns)
            if not stat.S_ISREG(opened.st_mode) or signature(before) != signature(opened):
                return _unknown('De gekozen AppImage is tussen selectie en openen gewijzigd.')
            total = 0
            while total < before.st_size:
                block = f.read(min(1024 * 1024, before.st_size - total))
                if not block:
                    return _unknown('De AppImage is onvolledig gelezen; geen geldige hashvergelijking.')
                total += len(block)
                hasher.update(block)
            if f.read(1) or signature(os.fstat(f.fileno())) != signature(opened):
                return _unknown('De AppImage is tijdens de meting gewijzigd.')
        if signature(selected.lstat()) != signature(before):
            return _unknown('De AppImage is tijdens de meting vervangen of gewijzigd.')
    except (OSError, ValueError, TypeError, OverflowError):
        return _unknown('De geselecteerde AppImage kon niet volledig en veilig worden vergeleken.')
    if hmac.compare_digest(hasher.hexdigest(), expected_digest.casefold()):
        return GuidedObservation74('absent',
            'De geselecteerde AppImage heeft dezelfde SHA-256 als de door de gebruiker opgegeven referentie. '
            'De betrouwbaarheid van die referentie, pakketbron en updater is hiermee niet bewezen.',
            'Vergelijk de referentie met een onafhankelijk gecontroleerde, officiële release en test de oorspronkelijke app handmatig; Rescan na wijzigingen.')
    return GuidedObservation74('observed',
        'De SHA-256 van de geselecteerde AppImage verschilt van de opgegeven referentie. '
        'Dit bewijst niet dat de bron is gewijzigd of dat de AppImage schadelijk of defect is.',
        'Controleer de herkomst van beide hashes via de officiële projectrelease; bewaar de oorspronkelijke AppImage. Geen automatisch verwijderen of vervangen.')


def _path_precedence(executable: str | None, *, path_env: str | None = None,
                     fixed_dirs: tuple[str, str] = _FIXED_BINS):
    """Determine only the first eligible candidate in the **current process**.

    Unknown PATH elements before a candidate invalidate the observation: they
    might contain an executable which would be found first. The user-provided
    basename is never inserted into a command or an arbitrary search directory.
    """
    from .guided_evidence74 import GuidedObservation74, _unknown
    if not isinstance(executable, str) or not _EXE_NAME.fullmatch(executable) or executable in ('.', '..'):
        return _unknown('Geef uitsluitend de exacte programmabestandsnaam op, zonder pad of opties.')
    if path_env is None:
        path_env = os.environ.get('PATH')
    if not isinstance(path_env, str) or not 0 < len(path_env) <= 8192:
        return _unknown('De huidige PATH-omgeving is niet betrouwbaar beschikbaar.')
    items = path_env.split(os.pathsep)
    if len(items) > 128 or any(not v or not v.startswith('/') or '\x00' in v or '..' in v.split('/') for v in items):
        return _unknown('PATH bevat relatieve, lege of onveilige mapvermeldingen; voorrang kan niet worden bepaald.')
    normalized = [os.path.normpath(v) for v in items]
    # This check is deliberately limited to two fixed binary directories; never
    # probe arbitrary PATH entries from an environment or user-supplied string.
    found = []
    unknown_before = False
    for directory in normalized:
        if directory not in fixed_dirs:
            if not found:
                unknown_before = True
            continue
        try:
            st = os.lstat(os.path.join(directory, executable))
        except FileNotFoundError:
            continue
        except OSError:
            return _unknown('Een programmabestand in de vaste PATH-mappen kon niet veilig worden beoordeeld.')
        if stat.S_ISLNK(st.st_mode):
            return _unknown('Een gevonden programmabestand is een symlink; deze inventaris kan de uiteindelijke uitvoering niet bewijzen.')
        if not stat.S_ISREG(st.st_mode):
            return _unknown('Een gevonden naam verwijst niet naar een regulier bestand.')
        if not os.access(os.path.join(directory, executable), os.X_OK, effective_ids=True):
            continue
        found.append((directory, st.st_dev, st.st_ino))
    if unknown_before:
        return _unknown('Een niet-geïnspecteerde PATH-map heeft mogelijk voorrang; de huidige interpreter/host kan afwijken.')
    if not found:
        return _unknown('Geen uitvoerbaar programma met die naam gevonden in de twee vooraf vastgestelde programmamappen.')
    if len(found) > 1 and (found[0][1], found[0][2]) != (found[1][1], found[1][2]):
        return GuidedObservation74('observed',
            'In deze procesomgeving zijn twee verschillende uitvoerbare bestanden met dezelfde naam gevonden. '
            'De PATH-volgorde kiest één van beide als eerste. Dit bewijst niet welke binary de betrokken applicatie of host-shell gebruikt.',
            'Controleer de effectieve PATH en interpreter in de betrokken app of terminal, en bevestig de bedoelde bron vóór een wijziging; daarna Rescan.')
    return GuidedObservation74('absent',
        'In de twee vaste mappen is voor deze procesomgeving geen afwijkende tweede uitvoerbare kandidaat aangetoond. '
        'Shellfuncties, aliases, andere PATH-mappen en de Linux-host buiten een sandbox zijn niet gecontroleerd.',
        'Vergelijk het programmaverloop in de getroffen applicatie of hostterminal; verander geen PATH-instellingen op basis van deze beperkte momentopname.')


def inspect_guided80(case_id: str, *, selected_path: str | None = None,
                     target_note: str | None = None, consent: bool = False):
    from .guided_evidence74 import _status, _unknown
    if case_id not in CASES80:
        return _status(case_id, _unknown('Geen v80-procedure beschikbaar.'))
    if not consent:
        return _status(case_id, _unknown('Geen afzonderlijke toestemming voor deze gerichte meting.'))
    try:
        finding = (_appimage_sha256(selected_path, target_note) if case_id == APPIMAGE_CASE80
                   else _path_precedence(target_note))
    except (OSError, ValueError, TypeError, AttributeError):
        finding = _unknown('De gerichte meting is afgebroken; geen eenduidige conclusie.')
    return _status(case_id, finding)
