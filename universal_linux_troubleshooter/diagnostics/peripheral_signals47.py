"""Read-only, bounded USB/DRM kernel observations (not physical-cause proofs).

A kernel event can be evidence of an event. It cannot identify a defective
cable, port, monitor, app, USB device or responsible cause without an explicit
identity-matched comparison and suitable counterevidence. No shell, network,
privileges, system changes or USB reset commands are allowed.
"""
from __future__ import annotations

import re

from ..results import ResultStatus
from .bridge import LocalHost
from .focused_evidence import _journal, _report, KERNEL_JOURNAL

# Require a USB/DRM subsystem context in the same journal MESSAGE: casual
# mentions of USB, 'device error', or other PCIe faults are not enough.
_PATTERNS = {
    'usb_descriptor_error': re.compile(
        # A bare USB -71/-110 is not necessarily a descriptor/enumeration
        # failure. Require a named enumeration/descriptor operation or a
        # refused USB device address in this *same* message.
        r'\busb\s+[0-9]+-[0-9.]+\b.{0,200}(?:device descriptor read(?:/\d+)?.{0,80}\b(?:error\s+-\d+|failed|timed out)\b|unable to enumerate(?: USB device)?\b|device not accepting address\b.{0,100}\berror\s+-(?:71|110)\b)', re.I),
    'usb_overcurrent': re.compile(
        r'\b(?:usb|hub|usb-port|usb port)\b.{0,140}\b(?:over.current|overcurrent|over.current condition)\b', re.I),
    'usb_disconnect': re.compile(
        r'\busb\s+[0-9]+-[0-9.]+\b.{0,160}\bUSB disconnect\b', re.I),
    'drm_edid_error': re.compile(
        r'\b(?:drm|edid|i915|amdgpu|nouveau)\b.{0,140}\b(?:EDID.*(?:failed|invalid|checksum|corrupt)|failed.*EDID|EDID.*unreadable)\b', re.I),
    'drm_link_failure': re.compile(
        r'\b(?:drm|i915|amdgpu|nouveau|displayport)\b.{0,180}\b(?:link training failed|DP link training failed|failed to train link)\b', re.I),
}


def probe_peripheral_signals(host: LocalHost):
    rows = _journal(host, KERNEL_JOURNAL)
    if rows is None:
        return _report('peripheral_signals', ResultStatus.UNKNOWN,
                       *(f'{name}=unknown' for name in _PATTERNS),
                       explanation='Het begrensde kernel-log was niet betrouwbaar beschikbaar.')
    # Do not expose raw journal text, which may contain sensitive device names.
    # Empty / bounded logs are not proof that a failure never happened.
    matches = {name: False for name in _PATTERNS}
    for row in rows:
        message = row['MESSAGE'][:1200]
        for name, pattern in _PATTERNS.items():
            if not matches[name] and pattern.search(message):
                matches[name] = True
    return _report('peripheral_signals',
                   ResultStatus.WARNING if any(matches.values()) else ResultStatus.INFO,
                   *(f'{name}={"observed" if found else "not_observed_in_sample"}'
                     for name, found in matches.items()),
                   explanation='Specifieke USB-/DRM-kernelgebeurtenissen in het huidige begrensde log gecontroleerd; geen defecte poort of kabel vastgesteld.')
