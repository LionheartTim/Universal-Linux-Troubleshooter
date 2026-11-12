"""v50: bounded read-only *event* observations; never root-cause or repair proof.

Only data from fixed, allowlisted current-boot journal commands is examined.
A journal match may involve a different device/unit or an earlier event. Thus
these observations may ONLY describe events and must never approve a route.
"""
from __future__ import annotations

import re
from ..results import ResultStatus
from .bridge import LocalHost
from .focused_evidence import _journal, _report, KERNEL_JOURNAL, APP_JOURNAL

_SYSTEM_JOURNAL = ('journalctl','-b','-p','0..4','-n','160','--no-pager','--output=json')

_KERNEL_PATTERNS = {
    'btrfs_checksum': re.compile(r'\bBTRFS\b.{0,190}\b(?:checksum (?:error|failed|mismatch)|csum (?:failed|error)|checksum verify failed)\b', re.I),
    'readonly_remount': re.compile(r'\b(?:EXT4-fs|BTRFS|XFS|F2FS-fs)\b.{0,180}\b(?:remount(?:ing|ed)? (?:filesystem )?read.only|remounted read.only)\b', re.I),
    # A successful-but-unsigned module load often reports "module verification
    # failed: signature and/or required key missing - tainting kernel". That
    # warning is NOT proof the module was rejected. Only explicit lock-down /
    # refusal messages qualify as a loading rejection event.
    'module_signature_rejected': re.compile(
        r'\b(?:Lockdown\s*:\s*.{0,140}\bunsigned module loading\b.{0,80}\b(?:restricted|denied|blocked|prohibited)\b|'
        r'(?:module loading|modprobe|insmod).{0,130}\b(?:required key not available|key was rejected|signature rejected)\b|'
        r'module signature verification failed.{0,100}\b(?:rejected|denied|blocked)\b)', re.I),
    'selinux_avc': re.compile(r'\b(?:avc\s*:\s*denied\s*\{|type=AVC\b.{0,140}\bdenied\b)', re.I),
    'tpm_init_error': re.compile(r'\b(?:tpm\s+tpm\d+|tpm_tis|tpm_crb)\b.{0,170}\b(?:failed|timeout|error\b|not responding)\b', re.I),
    'bluetooth_hci_error': re.compile(r'\b(?:Bluetooth\s*:\s*)?hci\d+\b.{0,160}\b(?:command.*timeout|reset failed|hardware error|firmware.*failed)\b', re.I),
    'firmware_load_error': re.compile(r'\b(?:direct firmware load for|failed to load firmware|firmware: failed to load)\b.{0,180}\b(?:failed|error\s+-\d+|not found)\b', re.I),
    'cpu_thermal_throttle': re.compile(r'\b(?:CPU\d*|processor\d*|core\s*\d+)\b.{0,160}\b(?:temperature above threshold.*throttl|thermal throttling|clock throttled)\b',re.I),
}

_SYSTEM_PATTERNS = {
    'service_start_limit': re.compile(r'\b(?:start request repeated too quickly|start-limit-hit)\b',re.I),
    'service_dependency_failed': re.compile(r'\bDependency failed for\s+\S+',re.I),
    'service_bind_conflict': re.compile(r'\b(?:failed to (?:bind|listen)|cannot bind|could not bind)\b.{0,140}\b(?:address already in use|EADDRINUSE)\b|\baddress already in use\b.{0,140}\b(?:bind|listen)\b',re.I),
}
_USER_PATTERNS = {
    'user_service_failed': re.compile(r'\bFailed to (?:start|restart)\b.{0,180}\b(?:service|daemon)\b',re.I),
}
_LINK = re.compile(r'\b((?:en|eth)[a-z0-9_.-]{0,30})\b.{0,130}\b(?:link is |link )(?P<state>up|down)\b', re.I)


def _observations(rows, patterns):
    if rows is None:
        return {name:'unknown' for name in patterns}
    return {name: ('observed' if any(pattern.search(row['MESSAGE'][:1200]) for row in rows)
                   else 'not_observed_in_sample') for name, pattern in patterns.items()}


def probe_kernel_events50(host:LocalHost):
    rows=_journal(host,KERNEL_JOURNAL)
    facts=_observations(rows,_KERNEL_PATTERNS)
    if rows is None:
        facts['ethernet_link_flap']='unknown'
    else:
        states={}
        for row in rows:
            msg=row['MESSAGE'][:1200]
            m=_LINK.search(msg)
            if m:
                states.setdefault(m.group(1).lower(),[]).append(m.group('state').lower())
        # Require link-down twice with a real link-up in between, *same* device.
        flap=any(any(seq[i]=='down' and 'up' in seq[i+1:j] and seq[j]=='down'
                         for i in range(len(seq)) for j in range(i+2,len(seq)))
                 for seq in states.values())
        facts['ethernet_link_flap']='observed' if flap else 'not_observed_in_sample'
    return _report('kernel_events50',
                   ResultStatus.UNKNOWN if rows is None else ResultStatus.WARNING if 'observed' in facts.values() else ResultStatus.INFO,
                   *(f'{k}={v}' for k,v in facts.items()),
                   explanation='Begrensd huidig kernel-log gelezen. Een gevonden gebeurtenis identificeert geen defect, verantwoordelijke toepassing of oorzakelijk verband.')


def probe_service_events50(host:LocalHost):
    system=_journal(host,_SYSTEM_JOURNAL)
    user=_journal(host,APP_JOURNAL)
    facts={**_observations(system,_SYSTEM_PATTERNS),**_observations(user,_USER_PATTERNS)}
    return _report('service_events50',
                   ResultStatus.WARNING if 'observed' in facts.values() else
                   ResultStatus.UNKNOWN if system is None and user is None else ResultStatus.INFO,
                   *(f'{k}={v}' for k,v in facts.items()),
                   explanation='Begrensde systemd- en gebruikerslogboeken gelezen. Identiteit en tijd van de gemelde service moeten nog overeenkomen.')
