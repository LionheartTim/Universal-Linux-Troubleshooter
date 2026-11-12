"""Bounded, strictly read-only Linux input-device inventory for controller help.

A recognized input node is evidence that Linux lists a controller-like device,
NOT evidence that buttons, USB cable, game integration or driver work. No
private per-device names, raw paths, hardware serials or logs are displayed.
"""
from __future__ import annotations
import re
from ..results import DiagnosticResult, ResultStatus

_JS = re.compile(r'\bjs\d{1,3}\b')
_GAMEPAD = re.compile(r'\b(?:gamepad|joystick|joypad|game controller|xbox|dualshock|dualsense|steam controller)\b', re.I)

def probe_gamepad_inventory120(host) -> DiagnosticResult:
    try:
        raw = host.read('/proc/bus/input/devices')
        if not isinstance(raw, str) or not raw or len(raw) > 16384:
            raise ValueError('Unusable input inventory')
    except (OSError, ValueError, TypeError, AttributeError):
        status, fact, explanation = (ResultStatus.UNKNOWN, 'gamepad_input=unknown',
            'The current input-device list was not available. This is not proof that a controller is missing.')
    else:
        # Only complete input device blocks; reject data that was cut off.
        blocks = raw.split('\n\n')
        found = False
        for block in blocks:
            handlers = re.search(r'(?m)^H:\s*Handlers=([^\n]{1,400})$', block)
            name = re.search(r'(?m)^N:\s*Name="([^"\n]{1,200})"$', block)
            if handlers and _JS.search(handlers.group(1)):
                found = True
            elif name and handlers and _GAMEPAD.search(name.group(1)):
                found = True
        status = ResultStatus.INFO if found else ResultStatus.UNKNOWN
        fact = 'gamepad_input=observed' if found else 'gamepad_input=not_observed_in_sample'
        explanation = ('Linux lists a controller-like input device right now. This does not show that its buttons work.'
                       if found else 'No controller-like input entry was confirmed in this snapshot. This does not prove that the controller is disconnected.')
    return DiagnosticResult('focused', 'gamepad_inventory120', status, explanation,
        'Read-only inventory of local input devices, not a functional test.',
        'Continue with one relevant controller observation; no changes were made.',
        ('FACT:'+fact,))
