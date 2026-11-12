"""Read-only, case-scoped system observations for manual diagnosis.

These report narrow *facts*, never approve a solution route. Missing utilities,
truncated/inconsistent output, and unsupported environments produce UNKNOWN.
"""
from __future__ import annotations
import json
import re
import ipaddress
from ..results import ResultStatus
from .bridge import LocalHost
from .focused_evidence import _report, _json_list, ADDR

_ROUTE = ('ip', '-j', 'route', 'show', 'default')
_TIME = ('timedatectl', 'show', '-p', 'NTPSynchronized', '--value')
_ATOMIC = ('rpm-ostree', 'status', '--json')


def probe_host_ipv4(host: LocalHost):
    """Report IPv4 on a *single active* non-loopback interface and default route.

    These are independent observations: local-only machines need neither.
    Do not infer DHCP or an internet outage from either absence.
    """
    addresses = _json_list(host, ADDR)
    routes = _json_list(host, _ROUTE)
    if addresses is None or routes is None or len(addresses) > 256 or len(routes) > 128:
        return _report('host_ipv4', ResultStatus.UNKNOWN, 'primary_ipv4=unknown', 'ipv4_default_route=unknown',
                       explanation='IP- of routetabel niet volledig en betrouwbaar beschikbaar.')
    up = []
    for item in addresses:
        if not isinstance(item, dict):
            return _report('host_ipv4',ResultStatus.UNKNOWN,'primary_ipv4=unknown','ipv4_default_route=unknown',
                           explanation='Ongeldige netwerkinterfacegegevens.')
        name = item.get('ifname')
        flags = item.get('flags')
        if (isinstance(name,str) and re.fullmatch(r'[A-Za-z0-9_.:@-]{1,64}',name) and name!='lo'
                and isinstance(flags,list) and 'UP' in flags and 'LOOPBACK' not in flags):
            up.append(item)
    primary = 'unknown'
    if len(up) == 1:
        infos = up[0].get('addr_info')
        if isinstance(infos,list) and all(isinstance(x,dict) for x in infos):
            valid=[]
            invalid=False
            for info in infos:
                if info.get('family')=='inet':
                    try:
                        value=ipaddress.IPv4Address(info.get('local'))
                        valid.append(value)
                    except (ValueError, TypeError, ipaddress.AddressValueError):
                        invalid=True
            primary = 'unknown' if invalid else 'present' if valid else 'absent'
    default = 'unknown'
    if all(isinstance(x,dict) for x in routes):
        # The queried command is explicitly 'default', but malformed items are not trusted.
        if not routes:
            default='absent'
        elif all(x.get('dst')=='default' and
                 isinstance(x.get('dev'),str) and re.fullmatch(r'[A-Za-z0-9_.:@-]{1,64}',x['dev'])
                 for x in routes):
            default='present'
    return _report('host_ipv4',ResultStatus.INFO,
                   'primary_ipv4='+primary, 'ipv4_default_route='+default,
                   explanation='Lokale IPv4-configuratie en default-route gelezen; geen netwerkverzoek en geen bewijs voor een DHCP-, DNS- of routerdefect.')


def probe_time_sync(host: LocalHost):
    output = host.command(_TIME)
    status = 'unknown'
    if output.code==0 and not output.truncated:
        value=output.out.strip().lower()
        status={'yes':'synchronized','no':'unsynchronized'}.get(value,'unknown')
    return _report('time_sync',ResultStatus.INFO if status!='unknown' else ResultStatus.UNKNOWN,
                   'ntp_status='+status,
                   explanation='Alleen de door systemd gemelde NTP-synchronisatiestatus; geen bewijs voor foutieve kloktijd of TLS-certificaat.')


def probe_atomic_pending(host: LocalHost):
    output=host.command(_ATOMIC)
    pending='unknown'
    # rpm-ostree alone does not establish that the host is Bazzite.
    bazzite='unknown'
    try:
        os_release=host.read('/etc/os-release')
        if 0 < len(os_release) < 16384:
            ids=re.findall(r'(?m)^ID=(?:\"([a-z0-9_-]+)\"|([a-z0-9_-]+))\s*$',os_release)
            if len(ids)==1:
                value=ids[0][0] or ids[0][1]
                bazzite='observed' if value=='bazzite' else 'not_observed_in_sample'
    except (OSError, ValueError, TypeError):
        pass
    if output.code==0 and not output.truncated and 0 < len(output.out) <= 131072:
        try:
            record=json.loads(output.out)
            deps=record.get('deployments') if isinstance(record,dict) else None
            if isinstance(deps,list) and 1<=len(deps)<=40 and all(isinstance(d,dict) for d in deps):
                if (sum(d.get('booted') is True for d in deps)==1
                    and all(type(d.get('booted',False)) is bool
                            and type(d.get('staged',False)) is bool for d in deps)):
                    pending='observed' if any(d.get('staged') is True for d in deps if not d.get('booted')) else 'not_observed_in_sample'
        except (ValueError, TypeError):
            pass
    return _report('atomic_pending',ResultStatus.INFO if pending!='unknown' else ResultStatus.UNKNOWN,
                   'staged_deployment='+pending, 'bazzite_os='+bazzite,
                   explanation='rpm-ostree status gelezen; een staged deployment betekent niet dat de update defect is of al draait.')
