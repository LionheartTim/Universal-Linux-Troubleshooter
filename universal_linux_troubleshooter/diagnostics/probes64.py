"""v64: bounded direct read-only facts; no physical-cause conclusions or repairs.

The hwmon `tempN_fault` ABI signals an untrustworthy temperature *reading*,
not a disconnected component. Flatpak scopes are sampled independently from
fixed commands; a duplicate application ID is not an installation conflict.
"""
from __future__ import annotations
import re
from ..results import ResultStatus
from .focused_evidence import _report

HWMON = '/sys/class/hwmon'
USER_APPS = ('flatpak', 'list', '--app', '--user', '--columns=application')
SYSTEM_APPS = ('flatpak', 'list', '--app', '--system', '--columns=application')


def probe_thermal_fault64(host):
    state = 'unknown'
    try:
        devices = host.list_names(HWMON)
        if len(devices) > 64 or any(re.fullmatch(r'hwmon\d{1,3}', d) is None for d in devices):
            raise ValueError('Unbounded or invalid hardware monitor inventory')
        values = []
        for device in devices:
            base = f'{HWMON}/{device}'
            entries = host.list_names(base)
            if len(entries) > 200:
                raise ValueError('Unbounded sensor inventory')
            for entry in entries:
                if re.fullmatch(r'temp[1-9]\d{0,2}_fault', entry) is None:
                    continue
                value = host.read(f'{base}/{entry}').strip()
                if value not in ('0', '1'):
                    raise ValueError('Invalid temperature fault marker')
                values.append(value)
                if len(values) > 256:
                    raise ValueError('Unbounded fault sensor count')
        if values:
            # A sensor fault can be genuine even when several chips are present,
            # but it does not identify a failed component or an unplugged lead.
            state = 'observed' if '1' in values else 'not_observed_in_sample'
    except (OSError, ValueError, TypeError):
        state = 'unknown'
    return _report('thermal_fault64', ResultStatus.WARNING if state=='observed' else
                   ResultStatus.INFO if state=='not_observed_in_sample' else ResultStatus.UNKNOWN,
                   'temp_sensor_fault='+state,
                   explanation=('Een begrensde sysfs-hwmon-meting meldt een temperatuursensorfout; '
                                'de betreffende temperatuurwaarde is dan niet betrouwbaar. '
                                'Geen losgeraakte sensor, defecte koeling of gevaarlijke temperatuur bewezen.'))


def _application_ids(output):
    if (type(output.code) is not int or output.code != 0 or output.truncated
            or not isinstance(output.out, str) or len(output.out)>131072):
        return None
    lines = output.out.splitlines()
    if len(lines)>4096:
        return None
    items=set()
    for line in lines:
        name=line.strip()
        if not name:
            continue
        # Flatpak app IDs use dot-delimited names. Never parse headers or a
        # human-readable multi-column table as package identity evidence.
        if (len(name)>255 or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*(?:\.[A-Za-z][A-Za-z0-9_-]*){2,}',name)):
            return None
        if name in items:
            # Repeated rows can stem from branches; without full refs refuse.
            return None
        items.add(name)
    return items


def probe_flatpak_scopes64(host):
    state='unknown'
    try:
        user = _application_ids(host.command(USER_APPS))
        system = _application_ids(host.command(SYSTEM_APPS))
        if user is not None and system is not None:
            state = 'observed' if user & system else 'not_observed_in_sample'
    except (OSError, ValueError, TypeError):
        pass
    return _report('flatpak_scopes64', ResultStatus.WARNING if state=='observed' else
                   ResultStatus.INFO if state=='not_observed_in_sample' else ResultStatus.UNKNOWN,
                   'app_both_scopes='+state,
                   explanation=('Dezelfde Flatpak-app-ID staat zowel in de gebruikersinstallatie '
                                'als de standaard systeeminstallatie. Dit bewijst geen storing, '
                                'bronconflict of noodzaak tot verwijderen; andere benoemde systeeminstallaties '
                                'vallen buiten deze steekproef.'))
