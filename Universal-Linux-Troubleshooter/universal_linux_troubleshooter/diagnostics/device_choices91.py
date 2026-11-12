"""Optional local device selection for Manual Diagnostics (no interview or free text).

Only fixed, previously allowlisted, read-only commands are used. Their output is
inventory, never a diagnosis or a repair authorization. Target values are never
passed into a shell, path, network connection or subprocess argv.
"""
from __future__ import annotations
from dataclasses import dataclass
import json

from .bridge import LocalHost
from .context_intake68 import safe_target_note
from .target_evidence69 import (AUDIO_SOURCE_CASES, AUDIO_SINK_CASES, FLATPAK_CASES,
                                NETWORK_CASES, STORAGE_CASES, PULSE_SOURCES, PULSE_SINKS,
                                FLATPAK_USER, FLATPAK_SYSTEM, IP_LINK, BLOCK_DEVICES)
from .target_evidence71 import PODMAN_CASES, VIRTUAL_MACHINE_CASES, PODMAN_PS, VIRSH_NAMES


@dataclass(frozen=True)
class DeviceChoices:
    label: str
    options: tuple[tuple[str, str], ...] = ()  # (friendly display, exact trusted inventory ID)
    status: str = 'unavailable'  # found, empty, unavailable


def kind_for_case(case_id: str) -> str | None:
    if case_id in AUDIO_SOURCE_CASES or case_id == 'hardware34.audio.mic-jack-detection':
        return 'microphone'
    if case_id in AUDIO_SINK_CASES or case_id == 'hardware34.audio.speaker-distortion':
        return 'output'
    if case_id in FLATPAK_CASES:
        return 'flatpak'
    if case_id in NETWORK_CASES:
        return 'network'
    if case_id in STORAGE_CASES:
        return 'disk'
    if case_id in PODMAN_CASES:
        return 'container'
    if case_id in VIRTUAL_MACHINE_CASES:
        return 'vm'
    # For missing GPUs, enumerate the hardware in the normal GPU check. An
    # absent GPU cannot be selected from a list of devices Linux already sees.
    return None


LABELS = {
    'microphone': 'Select the affected microphone',
    'output': 'Select the affected sound output',
    'flatpak': 'Select the affected installed Flatpak',
    'network': 'Select the affected network interface',
    'disk': 'Select the affected disk',
    'container': 'Select the affected container',
    'vm': 'Select the affected virtual machine',
}


def _command_lines(host: LocalHost, argv: tuple[str, ...]) -> list[str] | None:
    try:
        result = host.command(argv)
    except (OSError, ValueError, TypeError):
        return None
    if result.code or result.truncated or len(result.out) > 131072:
        return None
    return result.out.splitlines()


def _json(host: LocalHost, argv: tuple[str, ...]):
    lines = _command_lines(host, argv)
    if lines is None:
        return None
    try:
        return json.loads('\n'.join(lines))
    except (ValueError, TypeError):
        return None


def discover_choices(host: LocalHost, case_id: str) -> DeviceChoices:
    kind = kind_for_case(case_id)
    if kind is None:
        return DeviceChoices('')
    label = LABELS[kind]
    found: dict[str, str] = {}
    try:
        if kind in ('microphone', 'output'):
            data = _json(host, PULSE_SOURCES if kind == 'microphone' else PULSE_SINKS)
            if not isinstance(data, list) or len(data) > 256:
                return DeviceChoices(label)
            for row in data:
                if not isinstance(row, dict):
                    return DeviceChoices(label)
                name = row.get('name')
                if not isinstance(name, str) or safe_target_note(name) != name:
                    continue
                # Monitor sources are software recording loops, not microphones.
                if kind == 'microphone' and (name.endswith('.monitor') or row.get('monitor_of_sink') not in (None, -1, 4294967295, '4294967295')):
                    continue
                desc = row.get('description')
                display = desc.strip() if isinstance(desc, str) and 0 < len(desc.strip()) <= 110 else name
                found[name] = display
        elif kind == 'flatpak':
            for argv in (FLATPAK_USER, FLATPAK_SYSTEM):
                lines = _command_lines(host, argv)
                if lines is None or len(lines) > 5000:
                    return DeviceChoices(label)
                for item in lines:
                    name = item.strip()
                    if name and safe_target_note(name) == name:
                        found[name] = name
        elif kind == 'network':
            data = _json(host, IP_LINK)
            if not isinstance(data, list) or len(data) > 512:
                return DeviceChoices(label)
            for item in data:
                if not isinstance(item, dict):
                    return DeviceChoices(label)
                name = item.get('ifname')
                if name and name != 'lo' and safe_target_note(name) == name:
                    found[name] = name
        elif kind == 'disk':
            data = _json(host, BLOCK_DEVICES)
            rows = data.get('blockdevices') if isinstance(data, dict) else None
            if not isinstance(rows, list) or len(rows) > 512:
                return DeviceChoices(label)
            for item in rows:
                if not isinstance(item, dict):
                    return DeviceChoices(label)
                name = item.get('name')
                if item.get('type') == 'disk' and isinstance(name, str) and safe_target_note(name) == name:
                    model = item.get('model')
                    found[name] = name + (' — ' + model.strip()[:70] if isinstance(model, str) and model.strip() else '')
        elif kind == 'container':
            data = _json(host, PODMAN_PS)
            if not isinstance(data, list) or len(data) > 1000:
                return DeviceChoices(label)
            for item in data:
                if not isinstance(item, dict):
                    return DeviceChoices(label)
                names = item.get('Names')
                names = [names] if isinstance(names, str) else names
                if not isinstance(names, list):
                    return DeviceChoices(label)
                for name in names:
                    if isinstance(name, str) and safe_target_note(name) == name:
                        found[name] = name
        elif kind == 'vm':
            lines = _command_lines(host, VIRSH_NAMES)
            if lines is None or len(lines) > 1000:
                return DeviceChoices(label)
            for name in lines:
                name = name.strip()
                if name and safe_target_note(name) == name:
                    found[name] = name
    except (OSError, ValueError, TypeError, AttributeError):
        return DeviceChoices(label)
    values = tuple(sorted(((text, identifier) for identifier, text in found.items()), key=lambda item: (item[0].casefold(), item[1])))
    return DeviceChoices(label, values, 'found' if values else 'empty')
