"""v67 context-limited, offline observations; facts are NOT proof of causes.

No process execution beyond fixed allowlisted read-only commands. Missing or
incomplete measurements fail closed. All routes remain independently guarded.
"""
from __future__ import annotations
import json
import re
from ..results import ResultStatus
from .focused_evidence import _report

CPU_PSI = '/proc/pressure/cpu'
BROWSER_SETTING = ('xdg-settings','get','default-web-browser')
HTTPS_HANDLER = ('xdg-mime','query','default','x-scheme-handler/https')
ROLLBACK = ('rpm-ostree','status','--json')


def _result(probe, fact, state, message):
    return _report(probe, ResultStatus.WARNING if state == 'observed' else
                   ResultStatus.INFO if state == 'not_observed_in_sample' else ResultStatus.UNKNOWN,
                   fact+'='+state, explanation=message)


def probe_cpu_pressure67(host):
    """PSI estimates runnable task stall pressure, not process CPU usage."""
    state='unknown'
    try:
        value=host.read(CPU_PSI)
        if isinstance(value,str) and 0<len(value)<=512:
            rows=value.splitlines()
            some=[x for x in rows if x.startswith('some ')]
            if len(some)==1:
                fields=some[0].split()
                expected=('avg10','avg60','avg300','total')
                if len(fields)==5 and fields[0]=='some' and all(
                    fields[i+1].startswith(key+'=') for i,key in enumerate(expected)):
                    nums=[fields[i+1].partition('=')[2] for i in range(4)]
                    if (all(re.fullmatch(r'\d{1,3}(?:\.\d{1,3})?',v) for v in nums[:3])
                            and re.fullmatch(r'\d{1,20}',nums[3])
                            and all(0 <= float(v) <= 100 for v in nums[:3])):
                        state='observed' if float(nums[0])>=30 else 'not_observed_in_sample'
    except (OSError,TypeError,ValueError,AttributeError):
        pass
    return _result('cpu_pressure67','cpu_pressure',state,
                   'Linux PSI meldt hoge CPU-wachtdruk in de laatste tien seconden. '
                   'Dit bewijst geen specifieke toepassing, CPU-overbelasting of oorzaak van VM-vertraging; '
                   'PSI kan ontbreken of niet representatief zijn voor het gemelde moment.')


def _desktop_id(output):
    if (type(output.code) is not int or output.code!=0 or output.truncated
            or not isinstance(output.out,str) or len(output.out)>512):
        return None
    value=output.out.strip()
    if re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.+\-]{0,180}\.desktop',value) and '/' not in value and '\n' not in value:
        return value
    return None


def probe_browser_handlers67(host):
    """Only reports two differing local *settings*; not user's preferred app."""
    state='unknown'
    try:
        one=_desktop_id(host.command(BROWSER_SETTING))
        two=_desktop_id(host.command(HTTPS_HANDLER))
        if one is not None and two is not None:
            state='observed' if one!=two else 'not_observed_in_sample'
    except (OSError,TypeError,ValueError,AttributeError):
        pass
    return _result('browser_handlers67','browser_handler_difference',state,
                   'xdg-settings en de HTTPS MIME-handler geven verschillende desktop-bestanden terug. '
                   'Dat bewijst niet welke browser de gebruiker wil of welke app daadwerkelijk links opent.')


def probe_rollback_slot67(host):
    """A rollback deployment *exists*; a regression is never inferred."""
    state='unknown'
    try:
        out=host.command(ROLLBACK)
        if (type(out.code) is int and out.code==0 and not out.truncated
                and isinstance(out.out,str) and 0<len(out.out)<=131072):
            doc=json.loads(out.out)
            rows=doc.get('deployments') if isinstance(doc,dict) else None
            if isinstance(rows,list) and 1<=len(rows)<=40 and all(isinstance(x,dict) for x in rows):
                checksums=[]
                valid=True
                for row in rows:
                    boot=row.get('booted',False);staged=row.get('staged',False)
                    checksum=row.get('checksum')
                    if (type(boot) is not bool or type(staged) is not bool or
                        not isinstance(checksum,str) or not re.fullmatch(r'[a-f0-9]{64}',checksum) or
                        (boot and staged)):
                        valid=False;break
                    checksums.append(checksum)
                if valid and len(set(checksums))==len(checksums) and sum(r.get('booted') is True for r in rows)==1:
                    # The existence of any *nonstaged* alternate is all we know.
                    # Never claim it is the immediately prior deployment.
                    state=('observed' if any(not r.get('booted',False) and
                                             not r.get('staged',False) for r in rows)
                           else 'not_observed_in_sample')
    except (OSError,TypeError,ValueError,AttributeError):
        pass
    return _result('rollback_slot67','alternate_deployment',state,
                   'Er staat een andere niet-gestagede rpm-ostree-deployment in de lokale status. '
                   'Niet bewezen is dat die het vorige werkende systeem is, veilig is om op te starten, '
                   'of dat een update de huidige klacht veroorzaakt.')
