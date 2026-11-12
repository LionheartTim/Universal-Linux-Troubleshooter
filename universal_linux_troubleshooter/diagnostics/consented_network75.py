"""Per-run consented, bounded network comparison for two *unresolved* cases.

This never proves a DNS-server failure, changes settings, or approves a repair.
A paired user-selected host/IP is necessary so a failed name resolution has a
bounded numerical TCP comparison. No raw identifiers or exception text in output.
"""
from __future__ import annotations

import ipaddress
import re
import socket
import threading
from dataclasses import dataclass

from ..results import DiagnosticResult, ResultStatus

NETWORK_CASES75 = frozenset({'network.dns-problem', 'software35.network.hostname-resolution'})
# A libc/NSS resolver is not guaranteed to respect socket timeouts. Bound UI
# blocking independently and permit at most one unfinished daemon lookup.
_RESOLVE_SLOT = threading.BoundedSemaphore(1)


def _bounded_resolve75(hostname: str, *, timeout: float = 5.0):
    if not _RESOLVE_SLOT.acquire(blocking=False):
        raise TimeoutError('a previous resolver attempt is still active')
    done = threading.Event()
    outcome = []

    def task():
        try:
            try:
                outcome.append((True, socket.getaddrinfo(hostname, 443, type=socket.SOCK_STREAM)))
            except BaseException as exc:
                outcome.append((False, exc))
        finally:
            _RESOLVE_SLOT.release()
            done.set()

    try:
        threading.Thread(target=task, name='ULT-consented-resolver', daemon=True).start()
    except Exception:
        _RESOLVE_SLOT.release()
        raise
    if not done.wait(timeout):
        raise TimeoutError('resolver timed out')
    ok, value = outcome[0]
    if not ok:
        raise value
    return value


@dataclass(frozen=True)
class NameTest75:
    state: str
    summary: str
    followup: str


def parse_target75(note: str | None):
    if not isinstance(note, str) or len(note) > 80:
        return None
    pieces = note.split()
    if len(pieces) != 2:
        return None
    hostname, numeric = pieces
    if len(hostname) > 63 or not re.fullmatch(r'[A-Za-z0-9.-]+', hostname):
        return None
    if hostname.startswith('-') or hostname.endswith('-') or any(
            not item or len(item) > 63 or item.startswith('-') or item.endswith('-')
            for item in hostname.split('.')):
        return None
    try:
        ip = ipaddress.ip_address(numeric)
    except ValueError:
        return None
    if hostname.casefold() == 'localhost' or ip.is_unspecified or ip.is_multicast or ip.is_loopback or ip.is_link_local:
        return None
    try:
        ipaddress.ip_address(hostname)
    except ValueError:
        pass
    else:
        return None
    return hostname, str(ip)


def _outcome(state: str, summary: str, followup: str) -> DiagnosticResult:
    return DiagnosticResult('focused', 'consented_dns75',
        ResultStatus.INFO if state != 'unknown' else ResultStatus.UNKNOWN,
        'Optional name-to-IP comparison', summary, followup, ())


def _direct_tcp75(ip: str, *, dial=None) -> bool | None:
    # Single user-requested numeric target, fixed port, bounded timeout. Not an
    # HTTP request, TLS validation or an open-ended port scanner.
    if dial is None:
        dial = socket.create_connection
    try:
        with dial((ip, 443), timeout=3.0):
            return True
    except (OSError, TimeoutError):
        return False
    except (TypeError, ValueError):
        return None


def inspect_network75(case_id: str, note: str | None, *, consent: bool,
                      resolve=None, dial=None) -> DiagnosticResult:
    if case_id not in NETWORK_CASES75:
        return _outcome('unknown', 'No supported opt-in name test for this case.', 'No network action.')
    if not consent:
        return _outcome('unknown', 'Toestemming voor netwerkverkeer is niet gegeven. Er is niets verzonden.',
                        'De lokale controles kunnen zonder netwerk worden uitgevoerd.')
    pair = parse_target75(note)
    if pair is None:
        return _outcome('unknown', 'Vul een geldige hostnaam en een afzonderlijk bevestigd IP-adres in.',
                        'Zonder deze twee doelidentiteiten wordt geen netwerkverzoek uitgevoerd.')
    hostname, ip = pair
    if resolve is None:
        resolve = _bounded_resolve75
    # The user authorizes exactly these two targets. A resolver may query the
    # system DNS/NSS chain; the numeric TCP handshake may contact the service.
    resolved = None
    try:
        if resolve is _bounded_resolve75:
            answer = resolve(hostname)
        else:
            answer = resolve(hostname, 443, type=socket.SOCK_STREAM)
        if not isinstance(answer, (list, tuple)) or not answer or len(answer) > 256:
            return _outcome('unknown', 'De systeemresolver gaf geen volledig interpreteerbaar resultaat.',
                            'Controleer de lokale naamresolutie; er volgt geen wijziging.')
        addresses = set()
        for record in answer:
            if not isinstance(record, (tuple, list)) or len(record) < 5 or not isinstance(record[4], (tuple, list)):
                return _outcome('unknown', 'De resolveruitvoer is onvolledig.', 'Geen wijziging uitvoeren.')
            addresses.add(str(ipaddress.ip_address(record[4][0])))
        if not addresses or len(addresses) > 256:
            return _outcome('unknown', 'De resolveruitvoer is onvolledig.', 'Geen wijziging uitvoeren.')
        resolved = addresses
    except socket.gaierror:
        resolved = set()
    except (OSError, ValueError, TypeError, IndexError, OverflowError, UnicodeError, TimeoutError):
        return _outcome('unknown', 'Het resolveronderzoek is mislukt of kon niet veilig worden geïnterpreteerd.',
                        'Geen configuratiewijziging uitvoeren.')
    direct = _direct_tcp75(ip, dial=dial)
    if direct is None:
        return _outcome('unknown', 'De directe verbindingstest leverde geen betrouwbaar resultaat.',
                        'Geen configuratiewijziging uitvoeren.')
    if not resolved and direct:
        return _outcome('observed',
            'De systeemresolver kon de gekozen naam niet vinden, terwijl een TCP-verbinding naar het afzonderlijk opgegeven IP op poort 443 lukte. '
            'Dat onderbouwt een naamresolutieprobleem in deze meetcontext, niet de exacte oorzaak of de juistheid van het opgegeven adres.',
            'Controleer eerst de doelnaam en het bedoelde IP bij de beheerder; inspecteer daarna lokale NSS-, hosts- en DNS-instellingen. '
            'Verander niets automatisch; kies Rescan voor een nieuwe vergelijking.')
    if not resolved and not direct:
        return _outcome('unknown',
            'De naam kon niet worden opgelost en de opgegeven IP-service op poort 443 was ook niet bereikbaar. '
            'Daardoor kan geen geïsoleerd naamresolutieprobleem worden aangetoond.',
            'Controleer netwerkbereikbaarheid, de bedoelde servicepoort en het gekozen doel zonder DNS als oorzaak aan te nemen.')
    if resolved and not direct:
        return _outcome('unknown',
            'De systeemresolver gaf een naamantwoord, maar de afzonderlijk opgegeven IP-service op poort 443 was niet bereikbaar. '
            'Dit bewijst geen DNS- of proxyfout; de service kan een andere poort gebruiken.',
            'Controleer de relevante service en het verwachte IP voordat je DNS wijzigt.')
    if ip in resolved:
        return _outcome('observed',
            'De systeemresolver noemt het opgegeven IP en de directe TCP-poort 443 is bereikbaar. '
            'Een eerdere storing, applicatie-specifiek gedrag en de werkelijke HTTPS-dienst zijn niet bewezen of uitgesloten.',
            'Herhaal de oorspronkelijke probleemhandeling en gebruik Rescan voor een actuele vergelijking.')
    return _outcome('unknown',
        'De systeemresolver gaf een of meer andere IP-adressen dan het opgegeven adres. '
        'Dat kan normaal zijn bij CDN, round-robin, IPv4/IPv6 of load balancing; een fout is niet bewezen.',
        'Controleer de verwachte netwerkbestemming bij de beheerder, zonder hosts- of DNS-instellingen blind te wijzigen.')
