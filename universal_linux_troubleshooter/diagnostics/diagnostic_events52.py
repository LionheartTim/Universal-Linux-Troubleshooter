"""v52 independent, local read-only event probes.

Every signal is a *reported event* within a bounded current-boot sample,
never a diagnosis of a broken component or permission to repair. Distinct
record types are not silently fused into causal conclusions. No network I/O.
"""
from __future__ import annotations

import re
from ..results import ResultStatus
from .focused_evidence import _journal, _report, KERNEL_JOURNAL, DHCP_JOURNAL
from .diagnostic_events50 import _SYSTEM_JOURNAL


def _rx(pattern: str):
    return re.compile(pattern, re.IGNORECASE)

# Patterns require a specific subsystem marker and a specific fault signal.
# Avoid generic 'failed', 'down', 'error' or 'disconnect' classification.
_KERNEL = {
    'sata_crc': _rx(r'\b(?:ata\d+(?:\.\d+)?|SATA)\b.{0,160}\b(?:ICRC|CRC error|interface CRC)\b'),
    'nvme_timeout': _rx(r'\bnvme\d+(?:n\d+)?\b.{0,160}\b(?:I/O \d+ QID \d+ timeout|I/O timeout|reset controller|controller is down)\b'),
    'nvme_thermal_warning': _rx(r'\b(?:nvme\d+|NVMe)\b.{0,160}\b(?:critical temperature|thermal throttling|temperature threshold exceeded)\b'),
    'md_raid_degraded': _rx(r'\b(?:md\d+|md/raid\w*|raid\d+)\b.{0,150}\b(?:array degraded|degraded array|not enough operational devices)\b'),
    'mmc_io_error': _rx(r'\bmmc\d+(?::\w+)?\b.{0,160}\b(?:error -\d+|I/O error|card never left busy state)\b'),
    'thunderbolt_authorization': _rx(r'\b(?:thunderbolt|usb4)\b.{0,170}\b(?:not authorized|authorization required|security level.*authorization)\b'),
    'usb_bandwidth': _rx(r'\b(?:usb|xhci[_ -]?hcd|xhci_hcd)\b.{0,170}\b(?:not enough bandwidth|bandwidth allocation failed|insufficient bandwidth)\b'),
    'hid_io_error': _rx(r'\b(?:usbhid|hid-generic|i2c_hid)\b.{0,160}\b(?:failed to (?:read|send|fetch) report|I/O error|transfer failed)\b'),
    'rtc_error': _rx(r'\b(?:rtc\d+|rtc_cmos|real.time clock)\b.{0,140}\b(?:failed to read|invalid time|read failed|I/O error)\b'),
    'acpi_brightness_error': _rx(r'\b(?:acpi_video\d*|backlight|brightness)\b.{0,170}\b(?:failed to set|failed to get|error setting|interface unavailable)\b'),
    'cpufreq_error': _rx(r'\b(?:cpufreq|amd_pstate|intel_pstate)\b.{0,165}\b(?:failed to (?:set|update|initialize)|initialization failed|unsupported frequency)\b'),
    'ata_io_error': _rx(r'\b(?:ata\d+(?:\.\d+)?|sd [a-z]{2,4})\b.{0,150}\b(?:failed command: (?:READ|WRITE)|I/O error|COMRESET failed)\b'),
    'storage_io_error': _rx(r'\b(?:blk_update_request|Buffer I/O error|I/O error, dev)\b.{0,150}\b(?:dev\s+\w+|logical block|sector\s+\d+)\b'),
}

_NETWORK = {
    'nm_unmanaged': _rx(r'\b(?:device\s*\([^)]{1,100}\)|NetworkManager).{0,150}\b(?:unmanaged(?:\s+by\s+policy)?|state change:\s*\w+\s*->\s*unmanaged)\b'),
    'wifi_auth_failure': _rx(r'\b(?:wlan\w*|wlp[\w.-]+|802-11-wireless|wifi|wi-fi|supplicant)\b.{0,180}\b(?:authentication failed|4-way handshake failed|wrong key|authentication timed out)\b'),
    'wifi_disconnect': _rx(r'\b(?:wlan\w*|wlp[\w.-]+|802-11-wireless|wifi|wi-fi|supplicant)\b.{0,160}\b(?:disassociated|deauthenticated|connection lost|supplicant disconnected)\b'),
    'wifi_secrets_missing': _rx(r'\b(?:wifi|wi-fi|802-11-wireless|wlan\w*|wlp[\w.-]+)\b.{0,160}\b(?:secrets were required, but not provided|no secrets|missing secrets)\b'),
    'vpn_activation_failed': _rx(r'\b(?:vpn|wireguard|openvpn)\b.{0,165}\b(?:activation failed|connection failed|authentication failed|timeout during activation)\b'),
}

_SYSTEM = {
    'mount_unit_failed': _rx(r'\b(?:Failed to mount|mount\[\d+\]:)\b.{0,160}\b(?:/\S+|mount|failed|timed out)\b'),
    'timer_unit_failed': _rx(r'\b(?:[\w@.-]+\.timer)\b.{0,160}\b(?:failed|trigger failed|invalid calendar specification)\b|\bFailed to (?:start|load)\b.{0,120}\.timer\b'),
    'socket_activation_failed': _rx(r'\b(?:[\w@.-]+\.socket)\b.{0,160}\b(?:failed to (?:listen|start)|activation failed|failed with result)\b'),
    'dbus_activation_failed': _rx(r'\b(?:dbus-daemon|dbus-broker|D-Bus)\b.{0,170}\b(?:activation failed|failed to activate|service .*timed out)\b'),
    'polkit_denied': _rx(r'\b(?:polkitd|polkit-agent-helper)\b.{0,170}\b(?:authorization failed|not authorized|authentication failed|authentication agent unavailable)\b'),
    'portal_failed': _rx(r'\b(?:xdg-desktop-portal|org\.freedesktop\.portal)\b.{0,160}\b(?:failed to (?:start|activate|create)|activation failed|timed out)\b'),
    'libvirt_start_failed': _rx(r'\b(?:libvirtd|virtqemud|qemu-system)\b.{0,180}\b(?:failed to start|domain startup failed|cannot start|start failed)\b'),
    'libvirt_network_failed': _rx(r'\b(?:libvirt|virbr\d+)\b.{0,165}\b(?:network .*inactive|failed to start network|network not found|network .* failed)\b'),
    'snapd_failed': _rx(r'\bsnapd\b.{0,170}\b(?:failed to (?:start|connect)|daemon unavailable|activation failed)\b'),
    'journald_no_space': _rx(r'\b(?:systemd-journald|journald)\b.{0,155}\b(?:no space left on device|failed to write entry.*(?:ENOSPC|disk full))\b'),
}


def _probe(host, *, key: str, cmd: tuple[str, ...], patterns: dict):
    records = _journal(host, cmd)
    facts = {}
    for name, pattern in patterns.items():
        facts[name] = ('unknown' if records is None else
                       'observed' if any(pattern.search(row['MESSAGE'][:1200]) for row in records)
                       else 'not_observed_in_sample')
    return _report(key, ResultStatus.UNKNOWN if records is None else
                   ResultStatus.WARNING if 'observed' in facts.values() else ResultStatus.INFO,
                   *(f'{name}={value}' for name, value in facts.items()),
                   explanation=('Alleen-lezensteekproef uit huidig bootlog. Een gebeurtenis is geen bewezen oorzaak; '
                                'ook afwezige patronen sluiten problemen niet uit.'))


def probe_kernel_events52(host):
    return _probe(host, key='kernel_events52', cmd=KERNEL_JOURNAL, patterns=_KERNEL)


def probe_network_events52(host):
    return _probe(host, key='network_events52', cmd=DHCP_JOURNAL, patterns=_NETWORK)


def probe_service_events52(host):
    return _probe(host, key='service_events52', cmd=_SYSTEM_JOURNAL, patterns=_SYSTEM)
