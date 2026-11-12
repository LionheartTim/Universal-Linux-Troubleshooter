"""v65 direct, bounded read-only facts for Arch orphan inventory and GPU tachometer faults.

Observation only: no pacman transaction, no root, no network, no hardware repair.
"""
from __future__ import annotations
import re
from ..results import ResultStatus
from .focused_evidence import _report

ORPHANS = ('pacman','-Qdtq')
HWMON = '/sys/class/hwmon'
GPU_MONITORS = frozenset(('amdgpu','radeon','nouveau','i915','xe'))


def probe_arch_orphans65(host):
    state = 'unknown'
    try:
        result = host.command(ORPHANS)
        if (type(result.code) is int and result.code == 0 and not result.truncated
                and isinstance(result.out, str) and len(result.out) <= 131072):
            rows = result.out.splitlines()
            # Package names originate from the local pacman database; reject
            # truncation, duplicates, malformed rows and excessive inventories.
            if (len(rows) <= 4096 and all(
                    0 < len(name) <= 255 and re.fullmatch(r'[a-z0-9][a-z0-9@._+\-]*',name)
                    for name in rows) and len(rows)==len(set(rows))):
                state = 'observed' if rows else 'not_observed_in_sample'
    except (OSError, ValueError, TypeError, AttributeError):
        pass
    return _report('arch_orphans65',
                   ResultStatus.WARNING if state=='observed' else
                   ResultStatus.INFO if state=='not_observed_in_sample' else ResultStatus.UNKNOWN,
                   'arch_orphans='+state,
                   explanation=('De lokale pacman-database meldt minstens één niet meer vereiste, als afhankelijkheid '
                                'geïnstalleerde pakketnaam. Dat bewijst niet dat deze pakketten veilig verwijderd '
                                'kunnen worden; mogelijke optionele toepassingen zijn niet gecontroleerd.'))


def probe_gpu_fan_fault65(host):
    state='unknown'
    try:
        devices=host.list_names(HWMON)
        if (len(devices)>64 or any(type(n) is not str or
                not re.fullmatch(r'hwmon(?:0|[1-9]\d{0,2})',n) for n in devices)):
            raise ValueError('invalid monitor devices')
        gpu_seen = False
        readings=[]
        for device in devices:
            base=HWMON+'/'+device
            chip=host.read(base+'/name').strip()
            if chip not in GPU_MONITORS:
                continue
            gpu_seen=True
            entries=host.list_names(base)
            if len(entries)>200:
                raise ValueError('sensor listing too large')
            if any(type(entry) is not str or len(entry)>128 for entry in entries):
                raise ValueError('sensor listing invalid')
            for entry in entries:
                if not re.fullmatch(r'fan[1-9]\d{0,2}_fault',entry):
                    continue
                value=host.read(base+'/'+entry).strip()
                if value not in ('0','1'):
                    raise ValueError('invalid fan fault value')
                readings.append(value)
                if len(readings)>256:
                    raise ValueError('too many fan sensors')
        if gpu_seen and readings:
            state='observed' if '1' in readings else 'not_observed_in_sample'
    except (OSError, ValueError, TypeError, AttributeError):
        state='unknown'
    return _report('gpu_fan_fault65',
                   ResultStatus.WARNING if state=='observed' else
                   ResultStatus.INFO if state=='not_observed_in_sample' else ResultStatus.UNKNOWN,
                   'gpu_fan_fault='+state,
                   explanation=('Een als GPU herkende Linux-hwmon-driver rapporteert een fanN_fault-status. '
                                'Dit geeft een sensorwaarschuwing, geen vaststelling dat de GPU-fan '
                                'fysiek stilstaat of dat de videokaart defect is.'))
