"""v66 narrow read-only facts. Positive facts describe events, never their causes.

All invocations use existing fixed LocalHost allowlists or a public read-only
Linux kernel proc file. No privilege escalation, network, shell or writes.
"""
from __future__ import annotations
import re
from ..results import ResultStatus
from .focused_evidence import _report, probe_boot, _journal

FAILED_UNITS = ('systemctl', '--failed', '--no-pager', '--no-legend', '--plain')
CRITICAL_LOG = ('journalctl', '-b', '-p', '0..3', '-n', '80', '--no-pager', '--output=json')
PIPEWIRE = ('systemctl', '--user', 'is-active', 'pipewire.service')
CPUINFO = '/proc/cpuinfo'
KNOWN_DISPLAY_UNITS = frozenset(('display-manager.service', 'sddm.service', 'sddm-plymouth.service',
                                  'gdm.service', 'gdm3.service', 'lightdm.service', 'greetd.service', 'ly.service'))


def _outcome(probe, fact, state, description):
    return _report(probe, (ResultStatus.WARNING if state == 'observed' else
                           ResultStatus.INFO if state == 'not_observed_in_sample' else ResultStatus.UNKNOWN),
                   fact+'='+state, explanation=description)


def probe_display_manager66(host):
    """Only a named failed display manager unit, not a diagnosis of login loop."""
    state = 'unknown'
    try:
        out = host.command(FAILED_UNITS)
        if type(out.code) is int and out.code == 0 and not out.truncated and len(out.out) <= 131072:
            rows = [x.strip() for x in out.out.splitlines() if x.strip()]
            if len(rows) <= 256:
                matches=[]
                for line in rows:
                    cols=line.split(maxsplit=4)
                    if (len(cols)<4 or not re.fullmatch(r'[A-Za-z0-9_.@-]{1,180}\.[A-Za-z]{2,20}',cols[0])
                            or cols[2].lower()!='failed' or cols[3].lower()!='failed'):
                        break
                    if cols[0] in KNOWN_DISPLAY_UNITS:
                        matches.append(cols[0])
                else:
                    state='observed' if len(matches) == 1 else ('not_observed_in_sample' if not matches else 'unknown')
    except (AttributeError, OSError, TypeError, ValueError):
        pass
    return _outcome('display_manager66','display_manager_failed',state,
                    'Een expliciet benoemde displaymanager-unit heeft momenteel systemd-status failed. '
                    'Dit bewijst geen oorzaak, gebruiker, driverprobleem of login-loop.')


def probe_slow_boot66(host):
    """Reuses reviewed staged boot-timing parser; thresholds are heuristic."""
    state='unknown'
    try:
        outcome=probe_boot(host)
        facts=tuple(x for x in outcome.evidence if x.startswith('FACT:boot_stage='))
        if len(facts)==1:
            stage=facts[0].removeprefix('FACT:boot_stage=')
            if stage in ('pre_userspace','userspace'):
                state='observed'
            elif stage=='undetermined':
                state='not_observed_in_sample'
    except (AttributeError, TypeError, ValueError, OSError):
        pass
    return _outcome('slow_boot66','boot_delay',state,
                    'Een opvallend lange vroege of userspace-opstartfase is gemeten. '
                    'Een wachttijd, concrete service of hardwarefout is daarmee niet bewezen.')


def probe_critical_journal66(host):
    """Counts only explicitly high-priority local current-boot journal records."""
    state='unknown'
    try:
        rows=_journal(host,CRITICAL_LOG)
        if rows is not None and len(rows) <= 80:
            # Require explicit PRIORITY, regardless of journalctl filter:
            # a fake/inconsistent output may not authenticate priority.
            if all(isinstance(row.get('PRIORITY'),str) and row['PRIORITY'] in ('0','1','2','3')
                   and 0<len(row['MESSAGE'])<=16384 for row in rows):
                state='observed' if len(rows)>=3 else 'not_observed_in_sample'
    except (AttributeError, ValueError, TypeError, OSError):
        pass
    return _outcome('critical_journal66','critical_events',state,
                    'Drie of meer meldingen met journald-prioriteit 0–3 zijn in de huidige, '
                    'begrensde bootsteekproef gezien. Ernst, relevantie en afzonderlijke oorzaken zijn onbekend.')


def probe_pipewire_state66(host):
    state='unknown'
    try:
        r=host.command(PIPEWIRE)
        if not r.truncated and type(r.code) is int and isinstance(r.out,str):
            value=r.out.strip()
            if r.code==0 and value=='active':
                state='not_observed_in_sample'
            elif r.code==3 and value in ('inactive','failed'):
                state='observed'
    except (OSError, ValueError, TypeError, AttributeError):
        pass
    return _outcome('pipewire_state66','pipewire_inactive',state,
                    'PipeWire-gebruikersservice is op dit moment inactive of failed. '
                    'Niet bewezen is dat PipeWire op dit systeem de geluidsserver is of dat dit de geluidsklacht verklaart.')


def probe_virtualization_cpu_flags66(host):
    state='unknown'
    try:
        info=host.read(CPUINFO)
        if isinstance(info,str) and 0<len(info)<=16384:
            lines=[x for x in info.splitlines() if re.match(r'^flags\s*:',x)]
            if lines:
                flags=lines[0].partition(':')[2].strip().split()
                if 0<len(flags)<=256 and all(re.fullmatch('[A-Za-z0-9_]{1,48}',f) for f in flags):
                    state=('not_observed_in_sample' if 'svm' in flags or 'vmx' in flags else 'observed')
    except (OSError, TypeError, AttributeError, ValueError):
        pass
    return _outcome('virt_cpu_flags66','virt_flag_not_exposed',state,
                    'De zichtbare CPU-flags in deze Linux-omgeving noemen geen vmx/svm. '
                    'Dit bewijst niet of de fysieke CPU virtualisatie ondersteunt, of firmware-instellingen '
                    'de oorzaak zijn; virtuele machines kunnen flags verbergen.')
