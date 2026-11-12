"""v79: Five conservative, source-verified *event* observations.

No event is a root cause. Messages are accepted only from a kernel transport
or an unambiguous, allowlisted journal sender. They are current-boot, bounded
and incomplete by design. No user-provided argv, network or system changes.
"""
from __future__ import annotations
from dataclasses import dataclass
import re
from ..results import ResultStatus
from .focused_evidence import _journal, _report, KERNEL_JOURNAL
from .diagnostic_events59 import SERVICE_EVENTS_JOURNAL, _sender
from .context_events77 import EVENTS77
from .context_events78 import ALL_EVENTS78

@dataclass(frozen=True)
class Event79:
    source: str
    senders: tuple[str, ...]
    pattern: str
    example: str
    event: str
    limitation: str

EVENTS79: dict[str, Event79] = {
    'audio.wrong-output': Event79('service', ('wireplumber',),
        r'\b(?:no target node available|defined target not found)\b',
        'no target node available',
        'WirePlumber heeft gemeld dat voor een audiostream geen doelnode beschikbaar was.',
        'Dit bewijst geen verkeerde standaarduitgang of welke luidspreker de gebruiker verwachtte.'),
    'hardware.fan-noise': Event79('kernel', (),
        r'\b(?:fan\d{1,3}|fan|tachometer)\b.{0,100}\b(?:stalled|stall detected|tachometer fault|fan failure|failed to spin)\b',
        'hwmon: fan1 stalled',
        'De kernel meldt een ventilator- of toerentalsensorstoring.',
        'Een fanstoring bewijst geen hoorbaar geluid, defect lager of identiteit van de lawaaiige ventilator.'),
    'network.slow-network': Event79('kernel', (),
        r'\bNETDEV WATCHDOG:\s*.{0,130}\btransmit queue\s+\d{1,4}\s+timed out\b',
        'NETDEV WATCHDOG: eth0 (e1000e): transmit queue 0 timed out',
        'De kernel heeft een verlopen transmissiewachttijd van een netwerkqueue gemeld.',
        'Dit is geen meting van internetsnelheid, round-trip latency of storing op een opgegeven website.'),
    'software35.packages.pacman-partial-upgrade': Event79('service', ('pacman',),
        r'\bfailed to prepare transaction\s*\(could not satisfy dependencies\)(?![A-Za-z0-9_])|'
        r'\b(?:breaks dependency|unresolvable package conflicts)\b',
        'installing example breaks dependency example=1 required by anotherpkg',
        'Pacman rapporteert een afhankelijkheids- of pakkettransactieconflict.',
        'Een afhankelijkheidsconflict bewijst geen gedeeltelijke update, betrokken pakketversies of veilige reparatie.'),
    'network.vpn-split-dns': Event79('service', ('resolvconf','resolvectl'),
        r'\bFailed to (?:set DNS configuration|resolve interface)\b.{0,120}\b(?:wg\d{1,3}|tun\d{1,3}|ppp\d{1,3}|nordlynx)\b|'
        r'\b(?:wg\d{1,3}|tun\d{1,3}|ppp\d{1,3}|nordlynx)\b.{0,120}\bFailed to set DNS configuration\b',
        'Failed to resolve interface "tun0": No such device',
        'Een resolverhulpprogramma rapporteert een DNS-instellingsfout op een tunnelinterface.',
        'Dit bewijst niet welke VPN actief is, welke domeinsuffix gebruikt wordt of dat split-DNS de oorzaak is.'),
}
assert len(EVENTS79) == 5 and not (set(EVENTS79) & (set(EVENTS77) | ALL_EVENTS78))
COMPILED79 = {case: re.compile(item.pattern, re.I) for case,item in EVENTS79.items()}


def _matches(case_id: str, row: dict) -> bool:
    spec = EVENTS79[case_id]
    message = row.get('MESSAGE')
    if not isinstance(message,str) or len(message)>4096:
        return False
    if spec.source == 'kernel':
        if row.get('_TRANSPORT') != 'kernel':
            return False
    else:
        sender = _sender(row)
        if sender is None or sender.casefold() not in {s.casefold() for s in spec.senders}:
            return False
    # Do not allow quotation of an old error in a benign diagnostic narrative.
    if re.search(r'\b(?:example|quoted|sample message)\s*:', message[:70], re.I):
        return False
    return bool(COMPILED79[case_id].search(message[:1200]))


def probe_context_events79(host):
    service = _journal(host,SERVICE_EVENTS_JOURNAL)
    kernel = _journal(host,KERNEL_JOURNAL)
    facts={}
    for case,spec in EVENTS79.items():
        rows=kernel if spec.source=='kernel' else service
        status=('unknown' if rows is None else 'observed' if any(_matches(case,row) for row in rows)
                else 'not_observed_in_sample')
        facts['event79_'+case.replace('.','_').replace('-','_')] = status
    return _report('context_events79',
        ResultStatus.WARNING if 'observed' in facts.values() else
        ResultStatus.UNKNOWN if 'unknown' in facts.values() else ResultStatus.INFO,
        *(key+'='+val for key,val in facts.items()),
        explanation='Afgebakende actuele journalsteekproef van vijf brongebonden foutgebeurtenissen. '
                    'Geen koppeling met de opgegeven doelidentiteit, geen oorzaak, geen reparatievrijgave. '
                    'Afwezigheid in de steekproef sluit de storing niet uit.')
