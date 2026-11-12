"""v73: safe, local-only hosts-file inventory for two unresolved name cases.

No DNS query, no network traffic, no arbitrary path access, no causal promotion.
The user label is only compared to a fixed local file's validated tokens.
"""
from __future__ import annotations
import ipaddress
import re
from .bridge import LocalHost
from .target_evidence69 import _view

HOST_CASES73 = frozenset({'network.dns-problem', 'software35.network.hostname-resolution'})
HOST_FILE = '/etc/hosts'
HOSTNAME = re.compile(r'(?=.{1,80}\Z)[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?\Z')


def inspect_hosts73(host: LocalHost, case_id: str, target: str):
    if case_id not in HOST_CASES73:
        return _view('unknown', 'Geen lokale hosts-inventaris voor dit dossier.')
    if not isinstance(target, str) or not HOSTNAME.fullmatch(target) or '..' in target or any(
        not label or len(label) > 63 or label.startswith('-') or label.endswith('-')
        for label in target.split('.')
    ):
        return _view('unknown', 'Geef één geldige hostnaam op; geen URL, IP-adres, pad of opdracht.')
    try:
        ipaddress.ip_address(target)
    except ValueError:
        pass
    else:
        return _view('unknown', 'Een IP-adres is geen hostnaam; geef een hostnaam op.')
    try:
        raw = host.read(HOST_FILE)
    except (OSError, ValueError, TypeError, UnicodeError):
        return _view('unknown', 'Het vaste lokale hosts-bestand kon niet worden gelezen.')
    # LocalHost.read() cuts after 16 KiB: never claim absence if file can be truncated.
    if not isinstance(raw, str) or len(raw) >= 16384 or '\0' in raw:
        return _view('unknown', 'Het lokale hosts-bestand is mogelijk onvolledig.')
    found = set()
    for line in raw.splitlines():
        line = line.split('#', 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2:
            return _view('unknown', 'Een hosts-regel kon niet betrouwbaar worden geïnterpreteerd.')
        try:
            ip = ipaddress.ip_address(parts[0])
        except ValueError:
            return _view('unknown', 'Het hosts-bestand bevat een ongeldige adresregel.')
        if any(name.casefold().rstrip('.') == target.casefold().rstrip('.') for name in parts[1:]):
            found.add(str(ip))
    if len(found) > 1:
        return _view('unknown', 'De opgegeven hostnaam heeft meerdere lokale hosts-adressen; geen eenduidige conclusie.')
    if found:
        return _view('observed', 'De opgegeven hostnaam heeft één vermelding in /etc/hosts. '
                     'Dit bewijst niet welke NSS-bron de toepassing gebruikt, of DNS/netwerk bereikbaar is.')
    return _view('observed', 'De opgegeven hostnaam komt niet voor in het volledig gelezen /etc/hosts. '
                 'Dat is normaal mogelijk; DNS/NSS en bereikbaarheid zijn niet getest.')
