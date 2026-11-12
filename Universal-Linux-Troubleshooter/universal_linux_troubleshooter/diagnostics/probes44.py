"""Fixed sysfs/proc read-only probes, without shell, privileges or network."""
from __future__ import annotations
import re
from ..results import ResultStatus
from .focused_evidence import _report
from .bridge import LocalHost


def probe_power_supply(host: LocalHost):
    try:
        names = host.list_names('/sys/class/power_supply')
        if len(names) > 64:
            raise ValueError('Too many power devices')
        bat=[]; mains=[]
        for entry in names:
            if not re.fullmatch(r'[A-Za-z0-9_-]{1,40}', entry):
                continue
            base='/sys/class/power_supply/'+entry+'/'
            kind=host.read(base+'type').strip().lower()
            if kind=='battery':bat.append(base)
            if kind=='mains':mains.append(base)
        wear='unknown';charging='unknown';ac='unknown'
        if len(bat)==1:
            base=bat[0]
            try:
                state=host.read(base+'status').strip().lower()
                if state in ('not charging', 'discharging'): charging='not_charging'
                elif state=='charging':charging='charging'
                # Full is not automatically healthy, and is not "not charging".
            except (OSError,ValueError):pass
            ratios=[]
            for unit in ('energy','charge'):
                try:
                    full=int(host.read(base+unit+'_full').strip())
                    design=int(host.read(base+unit+'_full_design').strip())
                    if full>0 and design>0 and full<=design*2:
                        ratios.append(full/design)
                except (OSError, ValueError, TypeError):pass
            if ratios and max(ratios)-min(ratios)<=0.08:
                wear='degraded' if max(ratios)<=0.60 else 'not_severely_degraded' if min(ratios)>=0.80 else 'uncertain'
        if len(mains)==1:
            value=host.read(mains[0]+'online').strip()
            if value in ('0','1'):
                ac='online' if value=='1' else 'offline'
        return _report('power_supply',ResultStatus.INFO,'battery_wear='+wear,
                       'battery_charge='+charging,'ac='+ac,
                       explanation='Eenduidige lokale batterij- en voedingsstatus gelezen; ontbrekende of conflicterende velden blijven onbekend.')
    except (OSError, ValueError, TypeError):
        return _report('power_supply',ResultStatus.UNKNOWN,'battery_wear=unknown',
                       'battery_charge=unknown','ac=unknown',
                       explanation='Batterijgegevens ontbreken, zijn ontoegankelijk of conflicteren.')


def _cpus(text: str) -> set[int] | None:
    result=set()
    if not re.fullmatch(r'[0-9,\-]{1,1024}',text):return None
    for part in text.split(','):
        if not part:return None
        pieces=part.split('-')
        if len(pieces)>2:return None
        try:
            a=int(pieces[0]); b=int(pieces[-1]);
        except ValueError:return None
        if a>b or b>4095 or b-a>4096:return None
        result.update(range(a,b+1))
    return result if result else None


def probe_cpu_boot_limit(host: LocalHost):
    try:
        cmdline=host.read('/proc/cmdline')[:4096]
        present=_cpus(host.read('/sys/devices/system/cpu/present').strip())
        online=_cpus(host.read('/sys/devices/system/cpu/online').strip())
        if not present or not online or not online.issubset(present):
            raise ValueError('Invalid topology')
        flags=re.findall(r'(?<!\S)maxcpus=([^\s]+)',cmdline)
        if len(flags)>1 or any(not f.isdigit() for f in flags):
            raise ValueError('Ambiguous CPU limit')
        configured=int(flags[0]) if flags else None
        # A specified limit is meaningful only if CPUs actually appear offline.
        actual=('active' if configured is not None and 0<configured<len(present)
                and len(online)<=configured and len(online)<len(present)
                else 'not_observed_in_sample' if configured is None or len(online)==len(present)
                else 'unknown')
        return _report('cpu_boot_limit',ResultStatus.INFO,'cpu_limit='+actual,
                       explanation='Bootparameter maxcpus en huidige online/present CPU-verzameling gecontroleerd.')
    except (OSError,ValueError,TypeError):
        return _report('cpu_boot_limit',ResultStatus.UNKNOWN,'cpu_limit=unknown',
                       explanation='CPU-topologie of kernelparameters niet betrouwbaar beschikbaar.')
