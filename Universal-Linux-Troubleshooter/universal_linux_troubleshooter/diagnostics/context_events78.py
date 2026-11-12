"""v78: strictly sourced, provisional events for previously context-only cases.

A journal observation is an event, not a target match, symptom proof, cause,
permission to act, or indication that a later rescan proves a repair.
The metadata and message must agree. Never copy journal payload to FACTs.
"""
from __future__ import annotations

from dataclasses import dataclass
import re

from ..results import ResultStatus
from .focused_evidence import _journal, _report, KERNEL_JOURNAL
from .diagnostic_events59 import SERVICE_EVENTS_JOURNAL, _sender
from .context_events77 import EVENTS77


@dataclass(frozen=True)
class Event78:
    source: str
    senders: tuple[str, ...]
    pattern: str
    example: str
    event: str
    limitation: str


# Important: a GPU driver probing a PCI device actually confirms that the PCI
# device WAS enumerated: never reuse that event for gpu-not-enumerated.
EVENTS78: dict[str, Event78] = {
    'applications.permission-denied': Event78(
        'kernel', (), r'\b(?:apparmor="DENIED"\s+operation="(?:exec|file_mmap)"|avc:\s*denied\s+\{\s*(?:execute|execute_no_trans)\s*\})',
        'audit: type=1400 apparmor="DENIED" operation="exec" name="/bin/example"',
        'Een beveiligingsbeleid weigerde een uitvoer- of executable-mappinghandeling.',
        'Het betrokken programma, de doelhandeling, gebruiker en reden zijn nog niet gekoppeld.'),
    'storage.file-permission-denied': Event78(
        'kernel', (), r'\b(?:apparmor="DENIED"\s+operation="(?:open|file_perm|create|unlink|rename)"|avc:\s*denied\s+\{\s*(?:read|write|open|create|unlink|rename)\s*\})',
        'audit: type=1400 apparmor="DENIED" operation="open" name="/tmp/example"',
        'Een beveiligingsbeleid heeft een bestandsbewerking geweigerd.',
        'De gekozen bestandsidentiteit, werkelijke Unix-rechten, ACL en gebruiker ontbreken.'),
    'network.proxy-captive': Event78(
        'service', ('NetworkManager',),
        r'\b(?:connectivity(?:\s+(?:check|state))?(?:\s+changed\s+to|\s*[:=])\s*(?:portal|captive)|captive\s+portal\s+(?:detected|found))\b',
        'connectivity: portal',
        'NetworkManager heeft een portal-/captive-connectiviteitsstatus geregistreerd.',
        'Een captive portal is hiermee niet aan de gekozen applicatie of proxy gekoppeld.'),
    'software35.network.proxy-wrong': Event78(
        'service', ('curl','wget'),
        r'\b(?:proxy\s+(?:connect\s+)?(?:authentication\s+required|returned\s+(?:http\s+)?(?:code\s+)?407)|received\s+http\s+code\s+407\s+from\s+proxy|407\s+proxy\s+authentication\s+required)\b',
        'Received HTTP code 407 from proxy after CONNECT',
        'Een netwerkclient heeft een HTTP-407-proxyweigering gemeld.',
        'Dit bewijst niet dat de geselecteerde applicatie een verkeerde proxyconfiguratie gebruikt.'),
    'graphics.gpu-missing': Event78(
        'kernel', (),
        r'\b(?:amdgpu|i915|nouveau|nvidia|xe)\b.{0,160}\b(?:probe\s+(?:with\s+driver\s+\S{1,32}\s+)?failed|failed\s+to\s+initiali[sz]e\s+(?:the\s+)?(?:gpu|device))\b',
        'amdgpu 0000:03:00.0: probe with driver amdgpu failed with error -22',
        'Een GPU-driver heeft een initialisatie- of probe-fout vastgelegd.',
        'Een probe-fout bevestigt juist dat een apparaat is gezien; geen bewijs dat een GPU fysiek ontbreekt.'),
    'security.firewall-blocks-one-app': Event78(
        'kernel', (),
        r'\[UFW\s+BLOCK\].{0,400}\bPROTO=(?:TCP|UDP)\b.{0,150}\bDPT=\d{1,5}\b',
        '[UFW BLOCK] IN=eth0 OUT= SRC=192.0.2.1 DST=192.0.2.2 PROTO=TCP SPT=45000 DPT=443',
        'De lokale firewall registreerde een geblokkeerd TCP-/UDP-pakket naar een bestemmingpoort.',
        'Een poortidentiteit bewijst niet welke applicatie of welk netwerkverzoek getroffen is.'),
    'software35.applications.locale-encoding': Event78(
        'service', ('python','python3','python3.12','python3.13','python3.14','python3.15'),
        r'\b(?:Unicode(?:Decode|Encode)Error|LookupError):\s*.{0,150}(?:codec|encoding|cannot\s+(?:decode|encode)|unknown\s+encoding)\b',
        "UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff",
        'Een Python-proces heeft een Unicode-coderingsfout gerapporteerd.',
        'Dit koppelt geen gekozen applicatie aan de fout en bewijst geen onjuiste systeemlocale.'),
    'hardware34.audio.speaker-distortion': Event78(
        'service', ('pipewire','wireplumber','pw-node'),
        r'\b(?:xrun|underrun|buffer\s+underrun)\b',
        'Audio stream xrun detected',
        'Een audiostream heeft een xrun/underrun geregistreerd.',
        'Een buffer-underrun bewijst geen vervorming of defecte luidspreker.'),
    'hardware34.memory.dimm-size-mismatch': Event78(
        'kernel', (),
        r'\b(?:EDAC|DIMM)\b.{0,140}\b(?:DIMM\s+size\s+mismatch|(?:DIMM|memory)\s+size\s+(?:does\s+not\s+match|mismatch))\b',
        'EDAC MC0: DIMM size mismatch',
        'De kernel meldt expliciet een DIMM-geheugengrootteverschil.',
        'Een logregel identificeert nog geen juiste fysieke DIMM, slot of firmwarewaarde.'),
}

# Temporal rule: a source-authenticated resume followed by a separate audio
# error within 120 s. Does not infer that suspend caused the audio failure.
AFTER_SLEEP_CASE = 'audio.audio-after-sleep'
ALL_EVENTS78 = frozenset(EVENTS78) | {AFTER_SLEEP_CASE}
assert len(ALL_EVENTS78) == 10
assert not (set(EVENTS77) & ALL_EVENTS78)
COMPILED78 = {cid: re.compile(item.pattern, re.I) for cid,item in EVENTS78.items()}


def _matches(case: str, row: dict) -> bool:
    spec=EVENTS78[case]
    message=row.get('MESSAGE')
    if not isinstance(message,str) or len(message)>4096:
        return False
    if spec.source == 'kernel':
        if row.get('_TRANSPORT') != 'kernel':
            return False
    else:
        sender=_sender(row)
        if sender is None or sender.casefold() not in (s.casefold() for s in spec.senders):
            return False
    return bool(COMPILED78[case].search(message[:1200]))


def _timestamp(record: dict) -> int | None:
    # systemd's journal timestamp is microseconds; not seconds and not a
    # timestamp quoted in the untrusted MESSAGE. Require explicit metadata.
    value=record.get('__REALTIME_TIMESTAMP')
    if not isinstance(value,str) or not re.fullmatch(r'\d{15,17}',value):
        return None
    n=int(value)
    return n if 100000000000000 <= n <= 99999999999999999 else None


def _resumed_audio_error(rows: list[dict]) -> bool:
    resumed=[]
    errors=[]
    for record in rows:
        message=record.get('MESSAGE')
        if not isinstance(message,str) or len(message)>4096:
            continue
        sender=_sender(record)
        t=_timestamp(record)
        if sender is None or t is None:
            continue
        if (sender == 'systemd-sleep'
                and re.search(r'\bSystem returned from sleep (?:operation|state)\b',message[:1200],re.I)):
            resumed.append(t)
        elif (sender in ('pipewire','wireplumber','pw-node') and
              re.search(r'\b(?:xrun|underrun|stream\s+(?:disconnected|failed))\b', message[:1200], re.I)):
            errors.append(t)
    # A journal sample is limited; missed resume events remain UNKNOWN.
    return any(0 < err - wake <= 120_000_000 for wake in resumed for err in errors)


def probe_context_events78(host):
    system=_journal(host,SERVICE_EVENTS_JOURNAL)
    kernel=_journal(host,KERNEL_JOURNAL)
    facts={}
    for case,spec in EVENTS78.items():
        rows=kernel if spec.source=='kernel' else system
        state=('unknown' if rows is None else 'observed' if any(_matches(case,row) for row in rows)
               else 'not_observed_in_sample')
        facts['event78_'+case.replace('.','_').replace('-','_')]=state
    facts['event78_'+AFTER_SLEEP_CASE.replace('.','_').replace('-','_')] = (
        'unknown' if system is None else 'observed' if _resumed_audio_error(system)
        else 'not_observed_in_sample')
    return _report('context_events78',
                   ResultStatus.WARNING if 'observed' in facts.values() else
                   ResultStatus.UNKNOWN if 'unknown' in facts.values() else ResultStatus.INFO,
                   *(key+'='+value for key,value in facts.items()),
                   explanation=('Begrensde lokale journalsteekproef met afzonderlijk vastgestelde afzender '
                                'of kerneloorsprong. Tijdkoppeling van audio vereist een echte '
                                'journaltijdstempel. Meldingen zijn niet aan de opgegeven doelidentiteit '
                                'gekoppeld. Geen bewezen oorzaak, automatische reparatie of herstelbewijs.'))
