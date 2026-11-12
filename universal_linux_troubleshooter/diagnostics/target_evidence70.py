"""v70: additional bounded inventories for target-dependent problem dossiers.

This never executes user values, tests causal hypotheses or supplies FACT tokens.
Targets are matched only against fixed read-only local snapshots. Missing,
partial, ambiguous, or malformed evidence is UNKNOWN.
"""
from __future__ import annotations

import re
from .bridge import LocalHost
from .target_evidence69 import _view, _lines

HWMON_CONTROLLER_CASES = frozenset({'hardware34.board.sensor-controller'})
FAN_CASES = frozenset({'hardware.fan-noise'})
POWER_CASES = frozenset({'hardware34.power.charging-port-damaged'})
LID_CASES = frozenset({'system.laptop-lid-suspend'})
FONT_CASES = frozenset({'software35.desktop.font-missing'})
CORE_CASES = frozenset({'applications.app-wont-open', 'software35.applications.segfault-plugin'})
PORT_CASES = frozenset({'security.firewall-blocks-one-app', 'software35.network.firewall-blocks'})
MEMORY_CASES = frozenset({'hardware34.memory.dimm-size-mismatch'})
SUPPORTED_CASES70 = (HWMON_CONTROLLER_CASES | FAN_CASES | POWER_CASES | LID_CASES
                     | FONT_CASES | CORE_CASES | PORT_CASES | MEMORY_CASES)
assert len(SUPPORTED_CASES70) == 10

FONT_LIST = ('fc-list', '--format=%{family}\\n')
CORES = ('coredumpctl', '--no-legend', '--no-pager', '-n', '30', 'list')
LISTENERS = ('ss', '-H', '-ltnu')


def _names(host: LocalHost, path: str, rx: str, limit: int = 64):
    names = host.list_names(path)
    if len(names) > limit or any(not re.fullmatch(rx, n) for n in names):
        return None
    return sorted(names)


def _read(host: LocalHost, path: str):
    value = host.read(path)
    if not isinstance(value, str) or len(value) > 1024:
        return None
    return value.strip()


def _hwmon(host: LocalHost, target: str, fan: bool):
    if not re.fullmatch(r'[A-Za-z0-9_+.-]{1,64}', target):
        return _view('unknown', 'Gebruik de exacte hwmon-chipnaam of ventilatorlabel, zonder bestandspad.')
    chips = _names(host, '/sys/class/hwmon', r'hwmon\d{1,3}')
    if chips is None or not chips:
        return _view('unknown', 'De hardwaremonitor-inventaris is niet volledig beschikbaar.')
    matches = []
    for chip in chips:
        base = f'/sys/class/hwmon/{chip}'
        name = _read(host, base + '/name')
        if name is None:
            return _view('unknown', 'Een hardwaremonitor-chip kon niet worden gelezen; meting onvolledig.')
        if not fan:
            if name == target:
                matches.append(chip)
            continue
        files = _names(host, base, r'(?:fan\d{1,3}_(?:input|label)|[A-Za-z0-9_.-]{1,64})', 256)
        if files is None:
            return _view('unknown', 'De ventilatorinventaris is niet volledig beschikbaar.')
        for filename in files:
            if not re.fullmatch(r'fan\d{1,3}_input',filename):
                continue
            sensor = filename.split('_')[0]
            label_path=base + '/' + sensor + '_label'
            try:
                label = _read(host,label_path) if sensor + '_label' in files else None
            except OSError:
                return _view('unknown', 'Ventilatorlabel kon niet betrouwbaar worden gelezen.')
            if label != target:
                continue
            rpm = _read(host,base+'/'+filename)
            if rpm is None or not re.fullmatch(r'\d{1,6}',rpm) or int(rpm)>100000:
                return _view('unknown', 'Ventilatorwaarde ontbreekt of is niet geldig.')
            matches.append((chip,sensor,int(rpm)))
    if len(matches)!=1:
        return _view('unknown', 'Geen unieke bijpassende chip of ventilatorlabel gevonden. Dit bewijst geen defect.')
    if not fan:
        return _view('observed','De exact gekozen hwmon-chipnaam staat in de lokale sensorinventaris. Dat bewijst niet dat een ontbrekende sensor of driver defect is.')
    return _view('observed',f'De exact gekozen ventilatorsensor rapporteert {matches[0][2]} RPM in deze momentopname. Dit meet geen geluid en bewijst geen mechanische storing.')


def _power(host: LocalHost, target: str):
    if not re.fullmatch(r'[A-Za-z0-9_.-]{1,50}',target):
        return _view('unknown','Gebruik de exacte naam van de netvoedingsbron, bijvoorbeeld AC of ACAD.')
    supplies=_names(host,'/sys/class/power_supply',r'[A-Za-z0-9_.-]{1,50}')
    if supplies is None or target not in supplies:
        return _view('unknown','De gekozen voedingsbron staat niet eenduidig in de lokale inventaris.')
    # The path component comes from the checked kernel inventory, not raw input.
    selected = next(n for n in supplies if n == target)
    base='/sys/class/power_supply/'+selected
    kind=_read(host,base+'/type')
    if kind not in ('Mains','USB','USB_C','USB_PD','USB_PD_DRP'):
        return _view('unknown','De gekozen bron is geen bevestigde externe netvoedingsbron.')
    online=_read(host,base+'/online')
    if online not in ('0','1'):
        return _view('unknown','Online-status van de voedingsbron is niet betrouwbaar leesbaar.')
    return _view('observed', 'De externe voedingsbron rapporteert momenteel '
                 + ('verbonden.' if online=='1' else 'niet verbonden.')
                 + ' Dit is geen fysieke controle van laadpoort, kabel of laadvermogen.')


def _lid(host: LocalHost,target: str):
    if not re.fullmatch(r'[A-Za-z0-9_.-]{1,50}',target):
        return _view('unknown','Gebruik de exacte lid-sensornaam (bijvoorbeeld LID0).')
    names=_names(host,'/proc/acpi/button/lid',r'[A-Za-z0-9_.-]{1,50}')
    if names is None or target not in names:
        return _view('unknown','De gekozen lid-sensor is niet eenduidig beschikbaar.')
    # Use only an exact entry returned by the kernel's bounded inventory.
    selected = next(n for n in names if n == target)
    value=_read(host,'/proc/acpi/button/lid/'+selected+'/state')
    if value is None:
        return _view('unknown','De laptopklepstatus kon niet worden gelezen.')
    match=re.fullmatch(r'state:\s*(open|closed)',value,re.I)
    if not match:
        return _view('unknown','De laptopklepstatus bevatte een onverwachte waarde.')
    return _view('observed','De lokale klepsensor meldt momenteel '
                 + ('open.' if match.group(1).lower()=='open' else 'gesloten.')
                 + ' Een momentopname legt geen verband met eerdere slaapgebeurtenissen.')


def _font(host: LocalHost,target: str):
    if not re.fullmatch(r'[A-Za-z0-9 +_.-]{1,80}',target):
        return _view('unknown','Gebruik de exacte lettertypefamilie, zonder opdrachten of paden.')
    lines=_lines(host,FONT_LIST)
    if lines is None or len(lines)>20000 or any(len(line)>1024 for line in lines):
        return _view('unknown','De lokale lettertypelijst is onvolledig of onleesbaar.')
    matches = [family.strip() for line in lines for family in line.split(',') if family.strip()==target]
    return _view('observed', 'De exact gekozen lettertypefamilie '
                 + ('komt voor in de lokale fontconfig-lijst.' if matches else 'komt niet voor in deze lokale fontconfig-lijst.')
                 + ' Dat bewijst niet dat een specifieke app het lettertype correct gebruikt.')


def _cores(host: LocalHost,target: str):
    if not re.fullmatch(r'[A-Za-z0-9_.+-]{1,64}',target) or target in ('.','..'):
        return _view('unknown','Gebruik alleen een exacte programmabestandsnaam, zonder pad.')
    rows=_lines(host,CORES)
    if rows is None or len(rows)>30:
        return _view('unknown','De begrensde crashinventaris kon niet volledig worden gelezen.')
    for row in rows:
        if len(row)>1024:
            return _view('unknown','De crashinventaris bevat een ongeldige regel.')
    # coredumpctl list: DATE PID UID GID SIG COREFILE EXE. Only exact final
    # executable basename counts; no substring / process-name matching.
    entries=[]
    for row in rows:
        fields=row.split()
        if len(fields)<7:
            return _view('unknown','Crashregistratie bevat een onbekend kolomformaat.')
        exe=fields[-1]
        if exe.startswith('/') and len(exe)<=256:
            entries.append(exe.rsplit('/',1)[-1])
        elif exe not in ('-','n/a'):
            return _view('unknown','Crashregistratie bevat een ongeldige uitvoerbare-bestandsnaam.')
    return _view('observed','Voor de exact gekozen programmabestandsnaam '
                 + ('staat een crash in de begrensde lokale registratie.' if target in entries else 'staat geen crash in de laatste 30 lokale registraties.')
                 + ' Geen registratie bewijst geen gezonde app; een crash bewijst geen plug-in-oorzaak.')


def _ports(host: LocalHost,target: str):
    if not re.fullmatch(r'\d{1,5}',target) or not 1 <= int(target) <= 65535:
        return _view('unknown','Gebruik uitsluitend een lokaal TCP/UDP-poortnummer tussen 1 en 65535.')
    lines=_lines(host,LISTENERS)
    if lines is None or len(lines)>10000 or any(len(x)>1024 for x in lines):
        return _view('unknown','De lokale luisterpoortinventaris is onleesbaar of onvolledig.')
    matched=0
    for line in lines:
        fields=line.split()
        if len(fields)<5 or fields[0] not in ('tcp','udp'):
            return _view('unknown','De socketinventaris bevat een onbekend kolomformaat.')
        local=fields[4]
        port=local.rsplit(':',1)[-1] if ':' in local else ''
        if not port.isdigit():
            return _view('unknown','De luisterpoortinventaris bevat een ongeldige poort.')
        if int(port)==int(target):
            matched+=1
    return _view('observed','Voor het gekozen poortnummer '
                 + ('is een lokale luistersocket gevonden.' if matched else 'is in deze momentopname geen luistersocket gevonden.')
                 + ' Dit test geen firewallbeleid, externe toegang of welke app de socket bezit.')


def _memory(host:LocalHost,target:str):
    if not re.fullmatch(r'(?:\d{1,4})\s*(?:GiB|GB)',target,re.I):
        return _view('unknown','Vul de verwachte capaciteit in als bijvoorbeeld 16 GiB, zonder privégegevens.')
    value=host.read('/proc/meminfo')
    # LocalHost.read caps the file at 16 KiB. Never parse partial long data.
    if not isinstance(value,str) or not (0 < len(value) <= 16384):
        return _view('unknown','Linux-geheugeninventaris kon niet worden gelezen.')
    fields=re.findall(r'^MemTotal:\s*(\d+) kB$',value,re.M)
    if len(fields)!=1 or int(fields[0])<=0:
        return _view('unknown','Linux rapporteerde geen unieke geldige MemTotal-waarde.')
    return _view('observed','Linux rapporteert momenteel een totale hoeveelheid werkgeheugen van '
                 + str(round(int(fields[0])/1048576,2)) + ' GiB. '
                 'De ingevoerde capaciteit is een verwachting, geen geverifieerd DIMM-label. '
                 'Firmware, gereserveerd geheugen en fysieke slotbezetting zijn hiermee niet gecontroleerd.')


def inspect_target70(host:LocalHost,case_id:str,target:str):
    try:
        if case_id in HWMON_CONTROLLER_CASES: return _hwmon(host,target,False)
        if case_id in FAN_CASES: return _hwmon(host,target,True)
        if case_id in POWER_CASES: return _power(host,target)
        if case_id in LID_CASES: return _lid(host,target)
        if case_id in FONT_CASES: return _font(host,target)
        if case_id in CORE_CASES: return _cores(host,target)
        if case_id in PORT_CASES: return _ports(host,target)
        if case_id in MEMORY_CASES: return _memory(host,target)
    except (OSError,ValueError,TypeError,AttributeError):
        return _view('unknown','De gerichte lokale inventaris is mislukt; oorzaak onbekend.')
    return _view('unknown','Geen veilige inventariscontrole voor dit probleem.')
