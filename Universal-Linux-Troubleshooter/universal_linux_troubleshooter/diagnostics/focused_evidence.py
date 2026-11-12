"""Narrow, read-only observations for automatic *case investigation*.

No shell, no privilege, no internet, no repair and no commands taken from the
knowledge base or AI. Each emitted FACT is computed from validated local output.
A missing/inaccessible/truncated source is UNKNOWN, never a negative finding.
"""
from __future__ import annotations

import json
import re
from collections import Counter

from ..results import DiagnosticResult, ResultStatus
from .bridge import LocalHost

BOOT = ('systemd-analyze', 'time')
LINK = ('ip', '-j', 'link', 'show')
ADDR = ('ip', '-j', 'address', 'show')
DHCP_JOURNAL = ('journalctl', '-b', '-u', 'NetworkManager', '-n', '80', '--no-pager', '--output=json')
KERNEL_JOURNAL = ('journalctl', '-b', '-k', '-n', '120', '--no-pager', '--output=json')
APP_JOURNAL = ('journalctl', '--user', '-b', '-n', '100', '--no-pager', '--output=json')
DRIVES=('lsblk', '-J', '-b', '-o', 'NAME,TYPE,SIZE,MOUNTPOINT,MODEL,RO')


def _report(key: str, status: ResultStatus, *facts: str, explanation: str) -> DiagnosticResult:
    return DiagnosticResult('focused', key, status, 'Automatische aanvullende feitencontrole',
                            explanation, 'De Troubleshooter beoordeelt dit zelf; er wordt niets gewijzigd.',
                            tuple('FACT:' + f for f in facts))


def _json_list(host: LocalHost, cmd: tuple[str, ...]):
    output = host.command(cmd)
    if output.code != 0 or output.truncated or not output.out.strip():
        return None
    try:
        data = json.loads(output.out)
        return data if isinstance(data,list) else None
    except (ValueError,TypeError):
        return None


def _journal(host: LocalHost, cmd: tuple[str,...]):
    output = host.command(cmd)
    if output.code != 0 or output.truncated:
        return None
    if not output.out.strip() or output.out.strip() == '-- No entries --':
        return []
    records=[]
    try:
        for line in output.out.splitlines():
            item=json.loads(line)
            if not isinstance(item,dict) or not isinstance(item.get('MESSAGE'),str):
                return None
            records.append(item)
    except (ValueError,TypeError):
        return None
    return records


def _messages(rows):
    return '\n'.join(str(e['MESSAGE'])[:1200] for e in rows)


def probe_dhcp(host: LocalHost) -> DiagnosticResult:
    links=_json_list(host,LINK)
    ips=_json_list(host,ADDR)
    rows=_journal(host,DHCP_JOURNAL)
    if links is None or ips is None:
        return _report('dhcp',ResultStatus.UNKNOWN, 'link=unknown','ipv4=unknown','dhcp=unknown',
                       explanation='Netwerkinterfacegegevens zijn niet volledig leesbaar.')
    wired=[]
    for item in links:
        if not isinstance(item,dict):continue
        name=item.get('ifname','')
        if isinstance(name,str) and re.fullmatch(r'(?:en|eth)[\w.:@-]{0,58}',name) and name!='lo':
            wired.append((name,item))
    if len(wired)!=1:
        return _report('dhcp',ResultStatus.UNKNOWN,'link=unknown','ipv4=unknown','dhcp=unknown',
                       explanation='Er is geen eenduidige bekabelde netwerkinterface gevonden.')
    name,link=wired[0]
    # operstate=DOWN alone does not prove a missing *physical* carrier:
    # NetworkManager (or the user) can administratively disable an interface.
    # Require independent administrative and lower-layer flags before making a
    # physical link assertion. Contradictory or absent flags remain UNKNOWN.
    flags=link.get('flags')
    if (not isinstance(flags,list) or not flags
            or any(not isinstance(flag,str) for flag in flags)):
        link_state='unknown'
    else:
        admin_up='UP' in flags
        lower_up='LOWER_UP' in flags
        operstate=str(link.get('operstate','')).upper()
        if not admin_up:
            link_state='admin_down'
        elif lower_up and operstate=='UP':
            link_state='up'
        elif not lower_up and operstate=='DOWN':
            link_state='down'
        else:
            link_state='unknown'
    addresses=[i for e in ips if isinstance(e,dict) and e.get('ifname')==name
                  for i in (e.get('addr_info') or []) if isinstance(i,dict) and i.get('family')=='inet'
                  and i.get('local')]
    ipv4='present' if addresses else 'absent'
    dhcp='unknown'
    if rows is not None:
        # Interface identifiers must match complete tokens, never substrings:
        # enp1s0 is NOT enp1s01, and a DHCP timeout on the latter cannot
        # authenticate the former. The journal is still a bounded sample.
        interface_token = re.compile(
            rf'(?<![A-Za-z0-9_.:@-]){re.escape(name)}(?![A-Za-z0-9_.:@-])', re.I)
        matching=[str(e['MESSAGE']).lower() for e in rows
                  if interface_token.search(str(e['MESSAGE']))]
        if any(re.search(r'dhcp\w*.*(?:timed? out|timeout|no lease|failed)',m) for m in matching):
            dhcp='timeout'
        # No DHCP logs is not proof of no DHCP failure.
    return _report('dhcp',ResultStatus.WARNING if link_state!='up' or ipv4=='absent' else ResultStatus.INFO,
                   'link='+link_state,'ipv4='+ipv4,'dhcp='+dhcp,
                   explanation='Bekabelde interface, IPv4 en beschikbare DHCP-gebeurtenissen zijn gecontroleerd.')


def probe_nvme(host:LocalHost) -> DiagnosticResult:
    rows=_journal(host,KERNEL_JOURNAL)
    if rows is None:
        return _report('nvme',ResultStatus.UNKNOWN,'nvme_reset=unknown','media_health=unknown',
                       explanation='Kernelgebeurtenissen niet betrouwbaar leesbaar.')
    messages=_messages(rows).lower()
    # Device association is mandatory; not every PCIe reset is storage-related.
    reset=bool(re.search(r'\bnvme\d+\b.{0,160}(?:timeout|reset|aer|i/o error)',messages))
    reset |= bool(re.search(r'\bnvme\s+nvme\d+.{0,160}(?:timeout|reset|aer)',messages))
    # Get current health only from a well-formed SMART response for one identified NVMe.
    # A hidden drive, a permission error or a missing utility is UNKNOWN.
    health='unknown'
    cmd=host.command(DRIVES)
    if cmd.code==0 and not cmd.truncated:
        try:
            devices=json.loads(cmd.out)['blockdevices']
            nvmes=[v['name'] for v in devices if isinstance(v,dict) and v.get('type')=='disk'
                and isinstance(v.get('name'),str) and re.fullmatch(r'nvme\d{1,3}n\d{1,3}',v['name'])]
            if len(nvmes)==1:
                query=('smartctl','-j','-H','-A','-n','standby','/dev/'+nvmes[0])
                smart=host.command(query)
                # smartctl uses an exit-status bitmask. Nonfatal SMART
                # *health* bits may make the command nonzero even when the
                # JSON measurements are readable. Bits 0..2 instead report
                # command/device/read failures and must not authenticate data.
                if (type(smart.code) is int and 0 <= smart.code <= 255
                        and not (smart.code & 0b111)
                        and not smart.truncated and 0 < len(smart.out) <= 131072):
                    data=json.loads(smart.out)['nvme_smart_health_information_log']
                    critical=data.get('critical_warning')
                    errors=data.get('media_errors')
                    if type(critical) is int and type(errors) is int and critical>=0 and errors>=0:
                        health='critical' if critical>0 else ('media_errors_present' if errors>0 else 'healthy_counters')
        except (ValueError,KeyError,TypeError,AttributeError):
            pass
    return _report('nvme',ResultStatus.WARNING if reset or health=='critical' else ResultStatus.INFO,
                   'nvme_reset='+('observed' if reset else 'not_observed_in_sample'),
                   'media_health='+health,
                   explanation='NVMe-controllergebeurtenissen bekeken; zonder SMART geen media-oordeel.')


def probe_boot(host:LocalHost) -> DiagnosticResult:
    output=host.command(BOOT)
    if output.code!=0 or output.truncated:
        return _report('boot_phases',ResultStatus.UNKNOWN,'boot_stage=unknown',
                       explanation='Opstarttijden zijn niet betrouwbaar beschikbaar.')
    # systemd-analyze reports multiple serial stages. Add all measured
    # pre-userspace stages, including initrd; taking their maximum (as before)
    # undercounts boot delays and may select the wrong branch. Refuse duplicate
    # labels, malformed samples, or impossible timing instead of guessing.
    parts = re.findall(r'(\d+(?:\.\d+)?)\s*(ms|s|min)\s*\((firmware|loader|kernel|initrd|userspace)\)',
                       output.out, re.I)
    phases={}
    for number, unit, name in parts:
        stage_name=name.lower()
        if stage_name in phases:
            return _report('boot_phases',ResultStatus.UNKNOWN,'boot_stage=unknown',
                           explanation='Dezelfde opstartfase wordt meerdere keren gerapporteerd.')
        n=float(number) * (60 if unit.lower()=='min' else .001 if unit.lower()=='ms' else 1)
        if not (0 <= n <= 86400):
            return _report('boot_phases',ResultStatus.UNKNOWN,'boot_stage=unknown',
                           explanation='Ongeldige opstarttijd; oorzaak onbekend.')
        phases[stage_name]=n
    if 'userspace' not in phases or len(phases)<2:
        return _report('boot_phases',ResultStatus.UNKNOWN,'boot_stage=unknown',
                       explanation='Tijdverdeling ontbreekt of is onleesbaar (geen aannames over firmware).')
    early=sum(v for k,v in phases.items() if k!='userspace')
    stage='pre_userspace' if early>=20 and early>phases['userspace']*2 else (
        'userspace' if phases['userspace']>=20 and phases['userspace']>early*2 else 'undetermined')
    return _report('boot_phases',ResultStatus.INFO,'boot_stage='+stage,
                   explanation='Opstarttijden per fase lokaal uitgelezen; oorzaak nog niet bewezen.')


def probe_app_dns(host:LocalHost) -> DiagnosticResult:
    # No DNS lookup here: that could contact a network resolver without consent.
    # A per-app DNS cause cannot be established from generic host IP status.
    return _report('app_dns',ResultStatus.UNKNOWN,'app_dns=unverified',
                   explanation='Zonder exacte app-identiteit en toestemming voor resolverchecks blijft het toepassingsverschil onbewezen.')


def probe_gpu_app(host:LocalHost) -> DiagnosticResult:
    # Both logs must be readable. Contemporaneous messages never prove causality.
    kernel=_journal(host,KERNEL_JOURNAL)
    user=_journal(host,APP_JOURNAL)
    if kernel is None or user is None:
        return _report('gpu_app',ResultStatus.UNKNOWN,'gpu_reset=unknown','app_crash=unknown','causation=unknown',
                       explanation='GPU- en toepassingslogboeken zijn niet beide betrouwbaar toegankelijk.')
    def times(rows,pattern):
        hits=[]
        for x in rows:
            if not re.search(pattern,x['MESSAGE'],re.I):
                continue
            try:
                stamp=int(x['__REALTIME_TIMESTAMP'])
            except (ValueError,TypeError,KeyError):
                continue
            if stamp>0:
                hits.append(stamp)
        return hits
    gpu=times(kernel,r'\b(?:amdgpu|nvidia|i915|drm)\b.{0,180}(?:gpu reset|ring timeout|gpu hang|resetting)')
    app=times(user,r'(?:deepcool|mystique).{0,160}(?:segfault|sigsegv|crash)')
    correlated=bool(gpu and app and min(abs(a-g) for a in app for g in gpu)<=5_000_000)
    return _report('gpu_app',ResultStatus.WARNING if gpu or app else ResultStatus.INFO,
                   'gpu_reset='+('observed' if gpu else 'not_observed_in_sample'),
                   'app_crash='+('observed' if app else 'not_observed_in_sample'),
                   'time_overlap='+('observed' if correlated else 'unverified'),
                   'causation=unknown',
                   explanation='Tijdstippen vergeleken; samenloop bewijst geen oorzakelijk verband.')




def probe_radio_blocks(host: LocalHost) -> DiagnosticResult:
    """Read rfkill sysfs state only, keeping absent and unreadable devices UNKNOWN.

    Radio blocking is observable; hardware presence/health is *not* inferred.
    For multiple matching controllers, ambiguity blocks an automated route.
    """
    states: dict[str, list[str]] = {'wifi': [], 'bluetooth': []}
    try:
        names = host.list_names('/sys/class/rfkill')
        if len(names) > 64:
            raise ValueError('Too many radio devices')
        for item in names:
            if not re.fullmatch(r'rfkill[0-9]{1,4}', item):
                continue
            base = '/sys/class/rfkill/' + item + '/'
            typ = host.read(base + 'type').strip().lower()
            key = 'wifi' if typ == 'wlan' else 'bluetooth' if typ == 'bluetooth' else None
            if key is None:
                continue
            soft = host.read(base + 'soft').strip()
            hard = host.read(base + 'hard').strip()
            if soft not in ('0', '1') or hard not in ('0', '1'):
                states[key].append('unknown')
            else:
                states[key].append('blocked' if '1' in (soft, hard) else 'unblocked')
    except (OSError, ValueError, TypeError):
        return _report('radio_blocks', ResultStatus.UNKNOWN, 'wifi=unknown',
                       'bluetooth=unknown', explanation='Radio-informatie onleesbaar; niet als uitgeschakeld of defect beschouwd.')

    def summary(rows):
        if not rows or 'unknown' in rows:
            return 'unknown'
        if all(x == 'blocked' for x in rows):
            return 'blocked'
        if all(x == 'unblocked' for x in rows):
            return 'unblocked'
        return 'mixed'

    wifi = summary(states['wifi'])
    bt = summary(states['bluetooth'])
    return _report('radio_blocks', ResultStatus.INFO,
                   'wifi=' + wifi, 'bluetooth=' + bt,
                   explanation='Rfkill-blokkering voor zichtbare Wi-Fi- en Bluetooth-radio’s lokaal uitgelezen; ontbreken van radio is geen bewijs voor defecte hardware.')


def probe_kernel_signals(host: LocalHost) -> DiagnosticResult:
    """Conservative, bounded signal extraction from this boot's kernel journal.

    Individual signals are observations, not root cause. Empty or truncated
    logs cannot rule out a fault. Repeatable ECC requires a named EDAC controller
    and events at least a minute apart; adjacent log lines are one incident.
    """
    records = _journal(host, KERNEL_JOURNAL)
    if records is None:
        return _report('kernel_signals', ResultStatus.UNKNOWN,
                       'ecc_ue=unknown', 'ecc_ue_repeated=unknown',
                       'gpu_reset=unknown', 'oom_kill=unknown', 'fs_error=unknown',
                       explanation='Kernellogboek niet betrouwbaar leesbaar.')
    ue_times: set[int] = set()
    # Separate events on the SAME EDAC controller are needed before suggesting
    # a repeatable-memory-error route. Adjacent journal lines can describe one
    # physical event, even with slightly different timestamps.
    ue_by_controller: dict[str, set[int]] = {}
    gpu = oom = fs = pcie_fatal = pcie_corrected = cpu_mce = gpu_vram = False
    corrected_times: set[int] = set()
    for entry in records[:120]:
        msg = entry['MESSAGE'][:1200]
        lower = msg.lower()
        uncorrectable = bool(re.search(
            r'\bEDAC\b[^\n]{0,140}\b(?:[1-9][0-9]*\s+)?UE\b|\buncorrectable\s+(?:ecc|memory)\b|\becc\b[^\n]{0,100}\buncorrectable\b',
            msg, re.I))
        if uncorrectable and 'correctable' not in lower.replace('uncorrectable', ''):
            try:
                stamp = int(entry['__REALTIME_TIMESTAMP'])
                if stamp > 0:
                    ue_times.add(stamp)
                    controller = re.search(r"\bEDAC\s+MC([0-9]{1,3})\b", msg, re.I)
                    if controller:
                        ue_by_controller.setdefault(controller.group(1), set()).add(stamp)
            except (ValueError, KeyError, TypeError):
                # Unstamped event is not suitable to prove repeated failures.
                pass
        # Match exact domain-specific events, not generic 'hardware error'.
        corrected = bool(re.search(r'\bEDAC\b[^\n]{0,120}\b(?:[1-9][0-9]*\s+)?CE\b|\bcorrected\s+(?:ecc|memory)\b|\becc\b[^\n]{0,100}\bcorrected\b', msg, re.I))
        if corrected and 'uncorrectable' not in lower:
            try:
                stamp = int(entry['__REALTIME_TIMESTAMP'])
                if stamp > 0:corrected_times.add(stamp)
            except (KeyError, TypeError, ValueError): pass
        pcie_corrected |= bool(re.search(r'\b(?:AER|PCIe Bus Error)\b[^\n]{0,120}\b(?:corrected|correctable)\b',msg,re.I))
        pcie_fatal |= bool(re.search(r'\b(?:AER|PCIe Bus Error|pcieport|DPC)\b[^\n]{0,140}\b(?:fatal|uncorrectable|containment event)\b',msg,re.I))
        cpu_mce |= bool(re.search(r'(?:\bmce:|\bmachine check(?: exception| event)?\b|\bhardware error:)' ,msg,re.I))
        gpu_vram |= bool(re.search(r'\b(?:amdgpu|nvidia|i915|xe|drm)\b[^\n]{0,140}\b(?:uncorrectable vram|vram uncorrectable|vram ecc error|vram memory error)\b',msg,re.I))
        gpu |= bool(re.search(r'\b(?:amdgpu|nvidia|i915|xe|drm)\b[^\n]{0,160}\b(?:gpu reset|gpu hang|ring timeout|resetting gpu)\b', msg, re.I))
        oom |= bool(re.search(r'\b(?:out of memory|memory cgroup out of memory)\b[^\n]{0,160}\bkilled process\s+[0-9]+\b', msg, re.I))
        fs |= bool(re.search(r'\b(?:EXT4-fs error|BTRFS error|XFS[^\n]{0,90}corruption|F2FS-fs[^\n]{0,90}error)\b', msg, re.I))
    repeated_ue = any((max(times) - min(times)) >= 60_000_000
                      for times in ue_by_controller.values() if len(times) >= 2)
    return _report('kernel_signals', ResultStatus.WARNING if (ue_times or corrected_times or gpu or oom or fs or pcie_fatal or pcie_corrected or cpu_mce or gpu_vram) else ResultStatus.INFO,
                   'ecc_ue=' + ('observed' if ue_times else 'not_observed_in_sample'),
                   'ecc_ue_repeated=' + ('observed' if repeated_ue else 'unverified'),
                   'gpu_reset=' + ('observed' if gpu else 'not_observed_in_sample'),
                   'oom_kill=' + ('observed' if oom else 'not_observed_in_sample'),
                   'fs_error=' + ('observed' if fs else 'not_observed_in_sample'),
                   'ecc_ce=' + ('observed' if corrected_times else 'not_observed_in_sample'),
                   'ecc_ce_repeated=' + ('observed' if len(corrected_times)>=2 else 'unverified'),
                   'pcie_corrected=' + ('observed' if pcie_corrected else 'not_observed_in_sample'),
                   'pcie_fatal=' + ('observed' if pcie_fatal else 'not_observed_in_sample'),
                   'cpu_mce=' + ('observed' if cpu_mce else 'not_observed_in_sample'),
                   'gpu_vram_error=' + ('observed' if gpu_vram else 'not_observed_in_sample'),
                   explanation='Afgebakend kernellogboek op specifieke gebeurtenissen gecontroleerd; afwezigheid in dit fragment sluit fouten niet uit.')


def probe_failed_units(host: LocalHost) -> DiagnosticResult:
    """Observe current failed systemd units; ownership and cause remain UNKNOWN."""
    output = host.command(('systemctl', '--failed', '--no-pager', '--no-legend', '--plain'))
    if output.code != 0 or output.truncated:
        return _report('failed_units', ResultStatus.UNKNOWN, 'failed=unknown',
                       explanation='Mislukte systemd-units konden niet betrouwbaar worden gelezen.')
    lines = [line for line in output.out.splitlines() if line.strip()]
    if not lines:
        return _report('failed_units', ResultStatus.INFO, 'failed=not_observed_in_sample',
                       explanation='Op dit moment zijn geen mislukte systemd-units gerapporteerd; dit sluit eerdere fouten niet uit.')
    # systemctl --failed --plain output: unit LOAD ACTIVE SUB DESCRIPTION.
    valid = [line.split() for line in lines]
    if not all(len(parts) >= 4 and re.fullmatch(r'[A-Za-z0-9_.@-]{1,180}\.[A-Za-z]{2,20}', parts[0])
               and parts[2].lower() == 'failed' and parts[3].lower() == 'failed'
               for parts in valid):
        return _report('failed_units', ResultStatus.UNKNOWN, 'failed=unknown',
                       explanation='Systemd gaf een niet-eenduidige service-indeling terug.')
    return _report('failed_units', ResultStatus.WARNING, 'failed=observed',
                   explanation='Een of meer systemd-units hebben momenteel de status failed; oorzaak en relevantie voor de gemelde applicatie zijn nog onbekend.')


# A fixed, reviewed list: neither a model nor a JSON tree can add a command.
from .probes44 import probe_power_supply, probe_cpu_boot_limit
from .peripheral_signals47 import probe_peripheral_signals
from .diagnostic_events50 import probe_kernel_events50, probe_service_events50
from .probes51 import probe_host_ipv4, probe_time_sync, probe_atomic_pending
from .diagnostic_events52 import probe_kernel_events52, probe_network_events52, probe_service_events52
from .diagnostic_events59 import probe_service_events59
from .diagnostic_events61 import probe_package_container_events61
from .diagnostic_events62 import probe_application_events62
from .probes63 import probe_cooling_rpm63, probe_ata_sectors63
from .probes64 import probe_thermal_fault64, probe_flatpak_scopes64
from .probes65 import probe_arch_orphans65, probe_gpu_fan_fault65
from .probes66 import (probe_display_manager66, probe_slow_boot66, probe_critical_journal66,
                       probe_pipewire_state66, probe_virtualization_cpu_flags66)

from .probes67 import probe_cpu_pressure67, probe_browser_handlers67, probe_rollback_slot67
def probe_context_events78(host):
    from .context_events78 import probe_context_events78 as perform
    return perform(host)

def probe_context_events79(host):
    from .context_events79 import probe_context_events79 as perform
    return perform(host)

def probe_context_events77(host):
    from .context_events77 import probe_context_events77 as perform
    return perform(host)

from .gamepad_inventory120 import probe_gamepad_inventory120
from .gamepad_path124 import probe_gamepad_path124
from .browser_inventory119 import probe_browser_inventory119, probe_browser_runtime119
from .steam_inventory128 import probe_steam_inventory128

PROBES={'power_supply':probe_power_supply,'cpu_boot_limit':probe_cpu_boot_limit,'dhcp':probe_dhcp,'nvme':probe_nvme,'boot_phases':probe_boot,
        'app_dns':probe_app_dns,'gpu_app':probe_gpu_app,
        'radio_blocks':probe_radio_blocks,'kernel_signals':probe_kernel_signals,
        'failed_units':probe_failed_units,'peripheral_signals':probe_peripheral_signals,
        'kernel_events50':probe_kernel_events50,'service_events50':probe_service_events50,
        'host_ipv4':probe_host_ipv4, 'time_sync':probe_time_sync, 'atomic_pending':probe_atomic_pending,
        'kernel_events52':probe_kernel_events52, 'network_events52':probe_network_events52,
        'service_events52':probe_service_events52, 'service_events59':probe_service_events59,
        'package_container_events61':probe_package_container_events61,
        'application_events62':probe_application_events62,
        'cooling_rpm63':probe_cooling_rpm63, 'ata_sectors63':probe_ata_sectors63,
        'thermal_fault64':probe_thermal_fault64,'flatpak_scopes64':probe_flatpak_scopes64,
        'arch_orphans65':probe_arch_orphans65,'gpu_fan_fault65':probe_gpu_fan_fault65,
        'display_manager66':probe_display_manager66,'slow_boot66':probe_slow_boot66,
        'critical_journal66':probe_critical_journal66,'pipewire_state66':probe_pipewire_state66,
        'virt_cpu_flags66':probe_virtualization_cpu_flags66,
        'cpu_pressure67':probe_cpu_pressure67,'browser_handlers67':probe_browser_handlers67,
        'rollback_slot67':probe_rollback_slot67, 'context_events77':probe_context_events77,'context_events78':probe_context_events78, 'context_events79':probe_context_events79}


def focused_check_names(question:str) -> tuple[str,...]:
    q=question.casefold()
    if any(x in q for x in ('ethernet','wired','cable','bekabeld','dhcp','netwerkkabel')):
        return ('dhcp',)
    if any(x in q for x in ('nvme','ssd controller')):
        return ('nvme',)
    if any(x in q for x in ('slow boot','startup','opstart','boot is slow','traag opstart')):
        return ('boot_phases',)
    if any(x in q for x in ('flatpak','sandbox')) and any(x in q for x in ('dns','network','internet','netwerk')):
        return ('app_dns',)
    if any(x in q for x in ('gpu','graphics','videokaart')) and any(x in q for x in ('deepcool','mystique')):
        return ('gpu_app',)
    return ()


def run_focused_checks(host:LocalHost,question:str) -> tuple[DiagnosticResult,...]:
    results=[]
    for key in focused_check_names(question)[:2]:
        try:
            results.append(PROBES[key](host))
        except Exception as exc:
            results.append(_report(key,ResultStatus.UNKNOWN,'probe=unknown',
                                   explanation=f'Veilige controle is niet gelukt ({type(exc).__name__}).'))
    return tuple(results)


CHAT120_PROBES = {
    'steam_inventory128': probe_steam_inventory128,
    'browser_inventory119': probe_browser_inventory119,
    'browser_runtime119': probe_browser_runtime119,
    'gamepad_inventory120': probe_gamepad_inventory120,
    'gamepad_path124': probe_gamepad_path124,
}

def run_named_focused_checks(host: LocalHost, probe_keys: tuple[str, ...]) -> tuple[DiagnosticResult, ...]:
    """Only locally approved fixed probes; no JSON-defined commands.

    Keep the v42 Manual Diagnostics registry frozen; the separate chat-only
    allowlist is narrow, explicit, read-only and cannot authorize repairs.
    """
    permitted = {**PROBES, **CHAT120_PROBES}
    if len(probe_keys) > 2 or len(set(probe_keys)) != len(probe_keys) or any(k not in permitted for k in probe_keys):
        raise ValueError("Unknown or excessive focused probe")
    outcomes=[]
    for key in probe_keys:
        try:
            outcomes.append(permitted[key](host))
        except Exception as exc:
            outcomes.append(_report(key,ResultStatus.UNKNOWN,'probe=unknown',
                                    explanation=f'Veilige controle is niet gelukt ({type(exc).__name__}).'))
    return tuple(outcomes)
