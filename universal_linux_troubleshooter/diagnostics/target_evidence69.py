"""v69: bounded, target-scoped *inventory* checks for selected v68 cases.

Only compares a sanitized user label with already-approved fixed local inventories.
No raw user value is ever passed as an argv/path/URL. Observations are display-only:
NOT causation evidence and NOT accepted by the route assessor. A missing inventory,
ambiguous identity or unsupported target returns UNKNOWN, never a defect verdict.
"""
from __future__ import annotations

import json
import re
from typing import Callable

from ..results import DiagnosticResult, ResultStatus
from .bridge import LocalHost
from .context_intake68 import CONTEXT_QUESTIONS68, safe_target_note

FLATPAK_CASES = frozenset({
    'apps.flatpak-file-access', 'software35.flatpak.corrupt-user-data',
    'software35.flatpak.file-access-denied', 'system.flatpak-problem',
    'software35.packages.app-source-mismatch',
})
NETWORK_CASES = frozenset({
    'network.slow-network', 'network.proxy-captive', 'network.vpn-split-dns',
    'software35.network.vpn-route',
})
STORAGE_CASES = frozenset({'hardware34.storage.ssd-not-present-firmware'})
GPU_CASES = frozenset({'graphics.gpu-missing', 'hardware34.gpu.gpu-not-enumerated'})
AUDIO_SOURCE_CASES = frozenset({
    'audio.mic-not-working', 'hardware34.audio.mic-jack-detection',
})
AUDIO_SINK_CASES = frozenset({
    'audio.wrong-output', 'audio.audio-after-sleep', 'hardware34.audio.speaker-distortion',
})
MIME_CASES = frozenset({'software35.applications.file-association'})
SUPPORTED_CASES69 = (FLATPAK_CASES | NETWORK_CASES | STORAGE_CASES | GPU_CASES |
                     AUDIO_SOURCE_CASES | AUDIO_SINK_CASES | MIME_CASES)
assert SUPPORTED_CASES69 <= set(CONTEXT_QUESTIONS68)
assert len(SUPPORTED_CASES69) == 18

FLATPAK_USER = ('flatpak', 'list', '--app', '--user', '--columns=application')
FLATPAK_SYSTEM = ('flatpak', 'list', '--app', '--system', '--columns=application')
IP_LINK = ('ip', '-j', 'link', 'show')
IP_ADDR = ('ip', '-j', 'address', 'show')
BLOCK_DEVICES = ('lsblk', '-J', '-b', '-o', 'NAME,TYPE,SIZE,MOUNTPOINT,MODEL,RO')
PCI_DEVICES = ('lspci', '-nn')
PULSE_SOURCES = ('pactl', '--format=json', 'list', 'sources')
PULSE_SINKS = ('pactl', '--format=json', 'list', 'sinks')
DEFAULT_SOURCE = ('pactl', 'get-default-source')
DEFAULT_SINK = ('pactl', 'get-default-sink')
MIME_QUERIES = {
    'pdf': ('xdg-mime', 'query', 'default', 'application/pdf'),
    'png': ('xdg-mime', 'query', 'default', 'image/png'),
    'html': ('xdg-mime', 'query', 'default', 'text/html'),
    'txt': ('xdg-mime', 'query', 'default', 'text/plain'),
}


def _view(state: str, detail: str) -> DiagnosticResult:
    """Never emit the supplied identity, or a FACT marker, in technical evidence."""
    return DiagnosticResult('focused', 'target_inventory69',
                            ResultStatus.INFO if state == 'observed' else ResultStatus.UNKNOWN,
                            'Gerichte inventariscontrole', detail,
                            'Dit is uitsluitend een actuele inventaris, geen oorzaaksbewijs of reparatie.',
                            ())


def _json(host: LocalHost, argv: tuple[str,...]):
    out = host.command(argv)
    if out.code != 0 or out.truncated or not out.out.strip() or len(out.out) > 131072:
        return None
    try:
        value = json.loads(out.out)
        return value if isinstance(value, (dict, list)) else None
    except (ValueError, TypeError):
        return None


def _lines(host: LocalHost, argv: tuple[str,...]):
    out = host.command(argv)
    if out.code != 0 or out.truncated or len(out.out) > 131072:
        return None
    return out.out.splitlines()


def _flatpak(host: LocalHost, target: str) -> DiagnosticResult:
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*(?:\.[A-Za-z0-9][A-Za-z0-9_-]*){2,}', target):
        return _view('unknown', 'Vul de volledige Flatpak-app-ID in; een zichtbare appnaam is niet eenduidig.')
    scopes = []
    for label, argv in (('USER', FLATPAK_USER), ('SYSTEM', FLATPAK_SYSTEM)):
        rows = _lines(host, argv)
        if rows is None:
            return _view('unknown', 'Een Flatpak-installatiescope kon niet volledig worden gelezen.')
        if any(len(row) > 300 for row in rows):
            return _view('unknown', 'Flatpak-inventaris bevat ongeldige of afgekorte regels.')
        matches = sum(row.strip() == target for row in rows)
        if matches > 1:
            return _view('unknown', 'Dezelfde app-ID kwam binnen één Flatpak-scope meermaals voor.')
        if matches == 1:
            scopes.append(label)
    if not scopes:
        return _view('observed', 'De opgegeven exacte app-ID stond niet in de gelezen USER- en SYSTEM-appinventarissen. Dit sluit andere installaties of een andere app-ID niet uit.')
    return _view('observed', 'De exacte Flatpak-app-ID is lokaal gevonden in: ' + ', '.join(scopes) + '. Dit bewijst geen sandbox-, portal- of gebruikersgegevensprobleem.')


def _network(host: LocalHost, target: str) -> DiagnosticResult:
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:@-]{0,63}', target):
        return _view('unknown', 'Gebruik de exacte Linux-interfacenaam (bijvoorbeeld enp3s0 of wlp2s0), geen browsernaam of hostname.')
    links, addrs = _json(host, IP_LINK), _json(host, IP_ADDR)
    if not isinstance(links, list) or not isinstance(addrs, list):
        return _view('unknown', 'Netwerkinterface-inventaris is niet volledig leesbaar.')
    link = [item for item in links if isinstance(item, dict) and item.get('ifname') == target]
    addr = [item for item in addrs if isinstance(item, dict) and item.get('ifname') == target]
    if len(link) != 1 or len(addr) != 1:
        return _view('unknown', 'Geen eenduidige, in beide lokale netwerkinventarissen identificeerbare interface. De afwezigheid bewijst geen defect.')
    flags = link[0].get('flags')
    if not isinstance(flags, list) or any(not isinstance(f, str) for f in flags):
        return _view('unknown', 'Interfacestatus is onvolledig of niet betrouwbaar.')
    infos = addr[0].get('addr_info')
    if not isinstance(infos, list) or any(not isinstance(i,dict) for i in infos):
        return _view('unknown', 'IP-adresinformatie is niet betrouwbaar beschikbaar.')
    has_ipv4 = any(i.get('family') == 'inet' and isinstance(i.get('local'), str)
                   and i['local'] for i in infos)
    carrier = 'LOWER_UP' in flags
    return _view('observed', 'De exact geselecteerde netwerkinterface is geïdentificeerd. '
                 + ('IPv4-adres aanwezig; ' if has_ipv4 else 'geen IPv4-adres in deze meting; ')
                 + ('linklaag actief.' if carrier else 'linklaag niet als actief gemeld.')
                 + ' Dit bewijst geen internet-, VPN-, DNS- of firewalloorzaak.')


def _storage(host: LocalHost, target: str) -> DiagnosticResult:
    if not re.fullmatch(r'(?:sd[a-z]{1,3}|nvme\d{1,3}n\d{1,3}|mmcblk\d{1,3}|vd[a-z]{1,3})', target):
        return _view('unknown', 'Gebruik de Linux-blokapparaatnaam (bijvoorbeeld nvme0n1), niet een pad of modelbeschrijving.')
    data = _json(host, BLOCK_DEVICES)
    entries = data.get('blockdevices') if isinstance(data, dict) else None
    if not isinstance(entries, list):
        return _view('unknown', 'De blokapparaten konden niet volledig worden geïnventariseerd.')
    matched = [e for e in entries if isinstance(e, dict) and e.get('name') == target and e.get('type') == 'disk']
    if len(matched) != 1:
        return _view('unknown', 'De opgegeven schijf is niet eenduidig als lokale schijf aangetroffen; dit zegt niets over de firmware-inventaris.')
    entry=matched[0]
    ro=entry.get('ro')
    if type(ro) not in (bool, int) or ro not in (0,1):
        return _view('unknown', 'Schijfinventaris bevat geen betrouwbare status voor alleen-lezen.')
    return _view('observed', 'De schijf is als blokapparaat door Linux geïdentificeerd; '
                 + ('alleen-lezen.' if ro else 'niet als alleen-lezen gemeld.')
                 + ' Dit bevestigt geen aanwezigheid of afwezigheid in UEFI/BIOS en geen schijfgezondheid.')


def _gpu(host: LocalHost, target: str) -> DiagnosticResult:
    if not re.fullmatch(r'[a-fA-F0-9]{2}:[a-fA-F0-9]{2}\.[0-7]', target):
        return _view('unknown', 'Gebruik het exacte PCI-slotadres zoals 01:00.0, geen commerciële GPU-modelnaam.')
    rows = _lines(host, PCI_DEVICES)
    if rows is None:
        return _view('unknown', 'PCI-inventaris kon niet volledig worden gelezen.')
    detected = [line for line in rows if re.match(r'^' + re.escape(target) + r'\s', line)
                and re.search(r'\b(?:VGA compatible controller|3D controller|Display controller)\b', line, re.I)]
    if len(detected) != 1:
        return _view('unknown', 'Geen eenduidige GPU op dit PCI-slotadres aangetroffen; oorzaak en firmwarestatus onbekend.')
    return _view('observed', 'Op het exact opgegeven PCI-slotadres rapporteert Linux een grafische controller. '
                 'Dit bewijst niet dat de verwachte GPU werkt of dat de driver correct functioneert.')


def _audio(host: LocalHost, target: str, *, source: bool) -> DiagnosticResult:
    # Matching the complete PulseAudio/PipeWire-Pulse internal name or exact
    # description is allowed. Substring matching can select the wrong device.
    rows = _json(host, PULSE_SOURCES if source else PULSE_SINKS)
    if not isinstance(rows,list) or any(not isinstance(i,dict) for i in rows):
        return _view('unknown', 'De audioapparaatinventaris is niet volledig beschikbaar; geen oorzaak vastgesteld.')
    matched = [i for i in rows if i.get('name') == target or i.get('description') == target]
    if len(matched) != 1 or not isinstance(matched[0].get('name'),str):
        return _view('unknown', 'Geen eenduidig exact passend audioapparaat gevonden; beschrijving of apparaat-ID kan afwijken.')
    default = _lines(host, DEFAULT_SOURCE if source else DEFAULT_SINK)
    is_default = bool(default and len(default) == 1 and default[0].strip() == matched[0]['name'])
    noun='opnamebron' if source else 'afspeelapparaat'
    # Never call a recording/test command; user consent is required for that.
    return _view('observed', f'Exact gekozen {noun} komt voor in de lokale audio-inventaris. '
                 + ('Het is momenteel als standaard ingesteld.' if is_default else
                    'Of dit het huidige standaardapparaat is, kon niet bevestigd worden.')
                 + ' Dit is geen test van geluid, jackdetectie, opname of apparaatkwaliteit.')


def _mime(host: LocalHost, target: str) -> DiagnosticResult:
    key=target.casefold().lstrip('.')
    argv=MIME_QUERIES.get(key)
    if argv is None:
        return _view('unknown', 'Alleen de vooraf goedgekeurde typen PDF, PNG, HTML en TXT zijn in deze lokale controle beschikbaar.')
    rows=_lines(host,argv)
    if rows is None or len(rows)>1:
        return _view('unknown', 'MIME-standaardtoewijzing kon niet eenduidig worden gelezen.')
    if not rows or not rows[0].strip():
        return _view('observed', 'Voor dit vooraf goedgekeurde bestandstype gaf xdg-mime geen standaardprogramma op. Dit bewijst niet dat openen onmogelijk is.')
    if not re.fullmatch(r'[A-Za-z0-9_.@+-]{1,150}\.desktop', rows[0].strip()):
        return _view('unknown', 'MIME-handler bevat een onverwachte desktop-ID.')
    return _view('observed', 'Voor het gekozen bestandstype staat lokaal een standaard desktop-app-ID ingesteld. '
                 'Niet bewezen is dat die app geïnstalleerd is of het bestand kan openen.')


def supports_target_probe(case_id: str) -> bool:
    from .target_evidence70 import SUPPORTED_CASES70
    from .target_evidence73 import HOST_CASES73
    from .target_evidence71 import SUPPORTED_CASES71
    return case_id in SUPPORTED_CASES69 or case_id in SUPPORTED_CASES70 or case_id in SUPPORTED_CASES71 or case_id in HOST_CASES73


def inspect_target(host: LocalHost, case_id: str, note: str | None) -> DiagnosticResult:
    """Only the case ID selects fixed local commands. Identity is never argv."""
    if not supports_target_probe(case_id) or case_id not in CONTEXT_QUESTIONS68:
        return _view('unknown', 'Voor dit dossier is nog geen veilige, gerichte inventariscontrole beschikbaar.')
    target=safe_target_note(note)
    if target is None:
        return _view('unknown', 'Geen veilige, eenduidige doelidentiteit ingevuld; meting niet uitgevoerd.')
    try:
        from .target_evidence81 import CASES81, inspect_target81
        if case_id in CASES81: return inspect_target81(host,case_id,target)
        if case_id in FLATPAK_CASES: return _flatpak(host,target)
        if case_id in NETWORK_CASES: return _network(host,target)
        if case_id in STORAGE_CASES: return _storage(host,target)
        if case_id in GPU_CASES: return _gpu(host,target)
        if case_id in AUDIO_SOURCE_CASES: return _audio(host,target,source=True)
        if case_id in AUDIO_SINK_CASES: return _audio(host,target,source=False)
        if case_id in MIME_CASES: return _mime(host,target)
        from .target_evidence73 import HOST_CASES73, inspect_hosts73
        if case_id in HOST_CASES73:
            return inspect_hosts73(host, case_id, target)
        from .target_evidence71 import SUPPORTED_CASES71, inspect_target71
        if case_id in SUPPORTED_CASES71:
            return inspect_target71(host, case_id, target)
        from .target_evidence70 import inspect_target70
        return inspect_target70(host,case_id,target)
    except (OSError, ValueError, TypeError, AttributeError):
        return _view('unknown', 'De gerichte lokale meting is mislukt; gegevens blijven onbekend.')
    return _view('unknown', 'Geen toepasselijke gerichte controle beschikbaar.')
