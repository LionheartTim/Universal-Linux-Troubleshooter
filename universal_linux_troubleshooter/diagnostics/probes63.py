"""v63 direct hardware readings, not conclusions of defective hardware.

A single identifiable sensor or ATA disk is essential; no user input, shell,
privilege, network operation, disk self-test or automatic repair is performed.
Unknown/ambiguous/malformed readings cannot become positive evidence.
"""
from __future__ import annotations

import json
import re

from ..results import ResultStatus
from .focused_evidence import _report, DRIVES

_HWMON = '/sys/class/hwmon'
_FAN_NAMES = re.compile(r'(?:cpu|chassis|case|system|sys|front|rear)(?:[_ -]?fan)?', re.I)
_PUMP_NAMES = re.compile(r'(?:pump|aio|water[_ -]?pump)', re.I)


def probe_cooling_rpm63(host):
    facts = {'fan_zero':'unknown', 'pump_zero':'unknown'}
    try:
        devices = host.list_names(_HWMON)
        if len(devices) > 64 or any(not re.fullmatch(r'hwmon\d{1,3}', d) for d in devices):
            raise ValueError('Invalid hwmon inventory')
        candidates = {'fan_zero':[], 'pump_zero':[]}
        unknown_identity=False
        for device in devices:
            base = f'{_HWMON}/{device}'
            entries = host.list_names(base)
            if len(entries)>200:
                raise ValueError('Unbounded sensor inventory')
            for entry in entries:
                m = re.fullmatch(r'fan([1-9]\d{0,2})_label', entry)
                if not m: continue
                try:
                    label = host.read(f'{base}/{entry}').strip()
                except (OSError, ValueError, TypeError):
                    # Cannot exclude this from the pump/fan population.
                    unknown_identity=True
                    continue
                if len(label)>100 or not label:
                    unknown_identity=True
                    continue
                key = ('pump_zero' if _PUMP_NAMES.search(label) else
                       'fan_zero' if _FAN_NAMES.search(label) else None)
                if key is None:
                    continue
                try:
                    raw = host.read(f'{base}/fan{m.group(1)}_input').strip()
                except (OSError, ValueError, TypeError):
                    candidates[key].append(None)
                    continue
                if not re.fullmatch(r'(?:0|[1-9]\d{0,5})',raw):
                    candidates[key].append(None)
                    continue
                rpm=int(raw)
                candidates[key].append(rpm if rpm<=100000 else None)
        if unknown_identity:
            # Never infer one unique identified fan if another channel's
            # identity could not be read.
            raise ValueError('Unidentified sensor could be an extra channel')
        for key, values in candidates.items():
            # Multiple sensor names need physical identity matching; even
            # identical readings may be duplicated hwmon aliases.
            if len(values)==1 and type(values[0]) is int:
                facts[key] = 'observed' if values[0]==0 else 'not_observed_in_sample'
    except (OSError, ValueError, TypeError):
        pass
    observed = 'observed' in facts.values()
    return _report('cooling_rpm63', ResultStatus.WARNING if observed else ResultStatus.INFO if 'unknown' not in facts.values() else ResultStatus.UNKNOWN,
                   *(f'{k}={v}' for k,v in facts.items()),
                   explanation=('Eén eenduidig benoemde sysfs-toerentalsensor per categorie bekeken. '
                                '0 RPM kan normaal fan-stopgedrag, ontbrekende tachometerbedrading of een stilstaande ventilator zijn. '
                                'Geen pompfout, temperatuurprobleem of defect bewezen.'))


def _valid_smart(output, disk):
    if (type(output.code) is not int or not 0<=output.code<=255 or output.code & 0b111
            or output.truncated or not 0<len(output.out)<=131072):
        return None
    try:
        data=json.loads(output.out)
        device=data['device']
        if (not isinstance(device,dict) or device.get('name')!='/dev/'+disk
                or device.get('protocol')!='ATA' or device.get('type') not in ('sat','ata')):
            return None
        attributes=data['ata_smart_attributes']['table']
        if not isinstance(attributes,list) or len(attributes)>256:return None
        found={}
        for row in attributes:
            if not isinstance(row,dict) or type(row.get('id')) is not int: return None
            ident=row['id']
            if ident not in (5,197,198): continue
            raw=row.get('raw')
            if not isinstance(raw,dict) or type(raw.get('value')) is not int or not 0<=raw['value']<=2**64-1:return None
            if ident in found: return None
            found[ident]=raw['value']
        return ('observed' if any(found.values()) else 'not_observed_in_sample') if found else None
    except (ValueError,TypeError,KeyError,AttributeError):
        return None


def probe_ata_sectors63(host):
    state='unknown'
    try:
        listed=host.command(DRIVES)
        if listed.code==0 and not listed.truncated and 0<len(listed.out)<=131072:
            doc=json.loads(listed.out)
            disks=doc['blockdevices']
            if isinstance(disks,list) and 1<=len(disks)<=256 and all(isinstance(d,dict) for d in disks):
                selected=[d['name'] for d in disks
                          if d.get('type')=='disk' and isinstance(d.get('name'),str)
                          and re.fullmatch(r'sd[a-z]{1,3}',d['name'])]
                if len(selected)==1:
                    disk=selected[0]
                    cmd=('smartctl','-j','-H','-A','-n','standby','/dev/'+disk)
                    state=_valid_smart(host.command(cmd),disk) or 'unknown'
    except (KeyError,ValueError,TypeError,AttributeError):
        pass
    return _report('ata_sectors63',ResultStatus.WARNING if state=='observed' else ResultStatus.INFO if state=='not_observed_in_sample' else ResultStatus.UNKNOWN,
                   'ata_problem_sectors='+state,
                   explanation=('Eén geïdentificeerd ATA/SAT-apparaat op SMART raw attribute 5/197/198 bekeken. '
                                'Een niet-nul teller is een gezondheidswaarschuwing, geen bewijs van een fysiek SATA-kabeldefect '
                                'of noodzaak tot onmiddellijke vervanging. Maak bij waarschuwing een veilige gegevenskopie.'))
