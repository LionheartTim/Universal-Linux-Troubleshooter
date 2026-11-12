"""Supplementary local input-stack evidence for a user-reported game controller.

This is a bounded metadata-only snapshot. NEVER open /dev/input/event* or
/dev/hidraw*: those streams could contain sensitive keyboard/controller input.
It cannot claim that the user's particular controller, buttons or game work.
"""
from __future__ import annotations

import re
from ..results import DiagnosticResult, ResultStatus

_NAME = re.compile(r'^N:\s*Name="([^"\n]{1,160})"$', re.M)
_HANDLERS = re.compile(r'^H:\s*Handlers=([^\n]{1,240})$', re.M)
_ID = re.compile(r'^I:\s*Bus=([0-9a-fA-F]{4})\s+Vendor=[0-9a-fA-F]{4}\s+Product=[0-9a-fA-F]{4}\s+Version=[0-9a-fA-F]{4}', re.M)
_ABS = re.compile(r'^B:\s*ABS=([0-9a-fA-F ]+)$', re.M)
_KEY = re.compile(r'^B:\s*KEY=([0-9a-fA-F ]+)$', re.M)
_GAMEPAD = re.compile(r'\b(?:gamepad|joystick|joypad|game controller|xbox|dualshock|dualsense|steam controller)\b', re.I)
_JS = re.compile(r'(?<!\w)js\d{1,3}(?!\w)')
_EVENT = re.compile(r'(?<!\w)event\d{1,4}(?!\w)')


def probe_gamepad_path124(host) -> DiagnosticResult:
    """Observe whether controller-looking nodes expose Linux event/joystick handlers."""
    try:
        raw = host.read('/proc/bus/input/devices')
    except (OSError, ValueError, TypeError, AttributeError):
        raw = ''
    if not isinstance(raw, str) or not raw or len(raw) >= 16384:
        fact = 'input_stack=unavailable'
        description = ('The Linux input-device details could not be read fully. '
                       'This does not prove a controller or driver fault.')
        status = ResultStatus.UNKNOWN
        evidence = ('FACT:'+fact,)
    else:
        candidates = []
        for block in raw.split('\n\n')[:100]:
            name, handlers = _NAME.search(block), _HANDLERS.search(block)
            if not name or not handlers:
                continue
            is_js = bool(_JS.search(handlers.group(1)))
            if not is_js and not _GAMEPAD.search(name.group(1)):
                continue
            bus = _ID.search(block)
            candidates.append((is_js, bool(_EVENT.search(handlers.group(1))),
                               bool(_ABS.search(block)), bool(_KEY.search(block)),
                               bus.group(1).lower() if bus else 'unknown'))
        if not candidates:
            fact = 'input_stack=not_observed_in_sample'
            description = ('No controller-like entry was confirmed in the readable input snapshot. '
                           'This does not prove the controller is absent or broken.')
            status = ResultStatus.UNKNOWN
            evidence = ('FACT:'+fact,)
        else:
            # Multiple controllers may exist; these facts may not all belong to
            # the specific device the user is reporting.
            joystick = any(x[0] for x in candidates)
            event = any(x[1] for x in candidates)
            axes = any(x[2] for x in candidates)
            buttons = any(x[3] for x in candidates)
            buses = {x[4] for x in candidates}
            if buses == {'0003'}:
                transport = 'usb'
            elif len(buses) == 1 and '0005' in buses:
                transport = 'bluetooth'
            else:
                transport = 'mixed_or_unknown'
            fact = 'input_stack=observed'
            description = ('Linux lists controller-like input entries. The input handlers and '
                           'capability flags describe device registration, NOT whether '
                           'pressing a button produces events or a game receives input.')
            status = ResultStatus.INFO
            evidence = ('FACT:'+fact,
                        'FACT:controller_candidates='+str(min(len(candidates),100)),
                        'FACT:joystick_handler='+('observed' if joystick else 'not_observed'),
                        'FACT:event_handler='+('observed' if event else 'not_observed'),
                        'FACT:axis_capabilities='+('observed' if axes else 'not_observed'),
                        'FACT:key_capabilities='+('observed' if buttons else 'not_observed'),
                        'FACT:bus='+transport)
    return DiagnosticResult('focused', 'gamepad_path124', status, description,
        'Read-only registration and capabilities; no button input was recorded.',
        'Further device-specific verification requires a separate, supported test.', evidence)
