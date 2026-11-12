"""v68 guided context for the 49 cases without target-independent evidence.

This is a *question and evidence-requirement catalog*, NOT a diagnosis rule,
command constructor, permission grant or evidence authenticator. User input
never changes a solution route and is never sent to a host command or model.
"""
from __future__ import annotations
from dataclasses import dataclass
import re

@dataclass(frozen=True)
class ContextQuestion:
    case_id: str
    question: str
    required_evidence: str

CONTEXT_QUESTIONS68 = {
    'applications.app-wont-open': ContextQuestion('applications.app-wont-open', 'Which executable name cannot start (without a file path)?', 'Identify the exact executable, user/session, invocation result and matching crash timestamp.'),
    'applications.permission-denied': ContextQuestion('applications.permission-denied', 'Which application is denied access?', 'Identify the chosen file, exact denied operation, user and effective file access context.'),
    'apps.flatpak-file-access': ContextQuestion('apps.flatpak-file-access', 'Which Flatpak application (app ID if known)?', 'Identify exact Flatpak app ID, file/URI, permissions and corresponding portal transaction.'),
    'audio.audio-after-sleep': ContextQuestion('audio.audio-after-sleep', 'Which sound device stops working?', 'Compare active audio device and service state before suspend and after resume.'),
    'audio.mic-not-working': ContextQuestion('audio.mic-not-working', 'Which microphone or input device?', 'Identify input device, selected source, mute/level state and permitted recording test.'),
    'audio.microphone-not-recording': ContextQuestion('audio.microphone-not-recording', 'Which application fails to record?', 'Compare recording from the same device in affected versus unaffected app.'),
    'audio.wrong-output': ContextQuestion('audio.wrong-output', 'Which audio output should be used?', 'Compare default output and active stream routing to the output the user intended.'),
    'display.screenshare-black': ContextQuestion('display.screenshare-black', 'Which screen-sharing application?', 'Identify screencast app, portal request, compositor and permission result with timestamp.'),
    'graphics.gpu-missing': ContextQuestion('graphics.gpu-missing', 'Which GPU is expected?', 'Identify expected PCI GPU or integrated graphics hardware and compare UEFI and OS enumeration.'),
    'hardware.fan-noise': ContextQuestion('hardware.fan-noise', 'What is the exact fan sensor label (e.g. CPU_FAN)?', 'Identify noisy fan physically and compare tachometer/RPM and temperatures under two loads.'),
    'hardware34.audio.mic-jack-detection': ContextQuestion('hardware34.audio.mic-jack-detection', 'Which headset or audio jack?', 'Compare jack detection before/after physical connection and known working headset.'),
    'hardware34.audio.speaker-distortion': ContextQuestion('hardware34.audio.speaker-distortion', 'Which speakers or output?', 'Compare amplifier volume, alternate output, and same recording on different speakers.'),
    'hardware34.board.sensor-controller': ContextQuestion('hardware34.board.sensor-controller', 'What is the exact hwmon sensor controller name?', 'Identify expected motherboard monitoring chip and compare firmware/driver enumeration.'),
    'hardware34.display.panel-physical': ContextQuestion('hardware34.display.panel-physical', 'Which display is affected?', 'Compare artefacts before OS loading and using alternate external display/cable.'),
    'hardware34.gpu.gpu-not-enumerated': ContextQuestion('hardware34.gpu.gpu-not-enumerated', 'Which dedicated GPU is expected?', 'Identify expected PCI device and compare firmware PCI inventory with the Linux inventory.'),
    'hardware34.memory.dimm-size-mismatch': ContextQuestion('hardware34.memory.dimm-size-mismatch', 'What installed RAM capacity do you expect (e.g. 16 GiB)?', 'Compare installed DIMM labels, UEFI reported memory and Linux recognized size.'),
    'hardware34.memory.memory-channel': ContextQuestion('hardware34.memory.memory-channel', 'Which RAM slot/channel arrangement?', 'Compare physical DIMM slot layout, firmware channel configuration and measured bandwidth.'),
    'hardware34.power.charging-port-damaged': ContextQuestion('hardware34.power.charging-port-damaged', 'What is the external power supply ID (e.g. AC or ACAD)?', 'User compares safe known-good charger/port contact and observes temperature without unsafe handling.'),
    'hardware34.storage.ssd-not-present-firmware': ContextQuestion('hardware34.storage.ssd-not-present-firmware', 'Which SSD should be detected?', 'Compare drive presence in UEFI setup and Linux block inventory; never claim firmware state from lsblk alone.'),
    'network.dns-problem': ContextQuestion('network.dns-problem', 'Which hostname fails to resolve?', 'With consent compare DNS resolution for one hostname against direct IP reachability.'),
    'network.proxy-captive': ContextQuestion('network.proxy-captive', 'Which network or browser is affected?', 'With consent identify captive portal/proxy settings and compare browser versus local network path.'),
    'network.slow-network': ContextQuestion('network.slow-network', 'Which network connection is slow?', 'With consent perform bounded throughput/latency comparisons to known endpoints and LAN.'),
    'network.vpn-split-dns': ContextQuestion('network.vpn-split-dns', 'Which VPN or internal hostname?', 'Identify active VPN, internal DNS suffix, split-DNS routes and authorized name-resolution test.'),
    'security.firewall-blocks-one-app': ContextQuestion('security.firewall-blocks-one-app', 'Which local TCP/UDP port number is affected?', 'Identify listening application port, selected firewall policy and local client test without rule changes.'),
    'software35.appimage.update-source-change': ContextQuestion('software35.appimage.update-source-change', 'Which AppImage application?', 'Identify original AppImage path/hash, updater result and preserved old file identities.'),
    'software35.applications.file-association': ContextQuestion('software35.applications.file-association', 'Which file type (e.g. PDF, not a private filename)?', 'Identify actual MIME type, selected app, and user/system default associations.'),
    'software35.applications.locale-encoding': ContextQuestion('software35.applications.locale-encoding', 'Which application displays wrong text?', 'Identify app encoding, locale environment and affected text/input reproduction.'),
    'software35.applications.segfault-plugin': ContextQuestion('software35.applications.segfault-plugin', 'Which executable name crashes (without a file path)?', 'Compare the same app/version with plugin enabled versus disabled and collect matching crash identity.'),
    'software35.containers.disk-space': ContextQuestion('software35.containers.disk-space', 'Which Podman container name is affected?', 'Identify rootless Podman storage root and compare bounded filesystem usage to free space.'),
    'software35.desktop.font-missing': ContextQuestion('software35.desktop.font-missing', 'Which exact font family is missing?', 'Identify required font family or icon theme and the affected application lookup.'),
    'software35.desktop.scaling-blur': ContextQuestion('software35.desktop.scaling-blur', 'Which application looks blurry?', 'Compare compositor scale, per-app rendering backend and native pixel output.'),
    'software35.desktop.shortcut-conflict': ContextQuestion('software35.desktop.shortcut-conflict', 'Which keyboard shortcut?', 'Identify the exact shortcut, current bindings and active keyboard scope.'),
    'software35.desktop.wayland-clipboard': ContextQuestion('software35.desktop.wayland-clipboard', 'Which two applications are involved?', 'Identify two target apps, compositor, clipboard MIME types and a consented copy/paste attempt.'),
    'software35.development.path-command-shadowed': ContextQuestion('software35.development.path-command-shadowed', 'Which command name is affected?', 'Identify the command name and compare exact resolved executable paths without executing them.'),
    'software35.development.venv-wrong-python': ContextQuestion('software35.development.venv-wrong-python', 'Which virtual environment/project?', 'Identify project environment path and compare interpreter, sys.prefix and executable location.'),
    'software35.flatpak.corrupt-user-data': ContextQuestion('software35.flatpak.corrupt-user-data', 'Which Flatpak application?', 'Identify app ID and compare user-data state in a safe backup-based reproduction.'),
    'software35.flatpak.file-access-denied': ContextQuestion('software35.flatpak.file-access-denied', 'Which Flatpak application?', 'Identify exact app ID, sandbox file grant and portal refusal with timestamps.'),
    'software35.network.firewall-blocks': ContextQuestion('software35.network.firewall-blocks', 'Which local TCP/UDP port number is affected?', 'Identify exact local address/port, listening socket and effective firewall policy.'),
    'software35.network.hostname-resolution': ContextQuestion('software35.network.hostname-resolution', 'Which hostname?', 'Identify desired hostname/address and compare local hosts, NSS and permitted resolution.'),
    'software35.network.proxy-wrong': ContextQuestion('software35.network.proxy-wrong', 'Which browser or application?', 'Compare per-application proxy environment and browser proxy settings with consent.'),
    'software35.network.vpn-route': ContextQuestion('software35.network.vpn-route', 'Which VPN and destination?', 'Identify VPN tunnel and intended destination before comparing route selection.'),
    'software35.packages.app-source-mismatch': ContextQuestion('software35.packages.app-source-mismatch', 'Which application has multiple sources?', 'Identify the same app across actual Flatpak/RPM/DEB/AppImage install origins before changing sources.'),
    'software35.packages.pacman-partial-upgrade': ContextQuestion('software35.packages.pacman-partial-upgrade', 'Which affected package?', 'Identify installed package versions and exact ABI incompatibility before claiming partial upgrade.'),
    'storage.file-permission-denied': ContextQuestion('storage.file-permission-denied', 'Which application is denied file access?', 'Identify exact file, path, operation, user, ACL and ownership; never chmod blindly.'),
    'system.flatpak-problem': ContextQuestion('system.flatpak-problem', 'Which Flatpak application?', 'Identify app ID, affected path, portal request and current permission scope.'),
    'system.laptop-lid-suspend': ContextQuestion('system.laptop-lid-suspend', 'What is the exact lid sensor name (e.g. LID0)?', 'Correlate lid or dock state changes with suspend events for the exact laptop.'),
    'system.login-one-user-fails': ContextQuestion('system.login-one-user-fails', 'Which desktop session type (not a username)?', 'Compare affected versus working user login and matching display/session logs without revealing secrets.'),
    'virtualization.container-disk': ContextQuestion('virtualization.container-disk', 'Which Podman container name is affected?', 'Identify container storage root, quota and filesystem usage independent of host root.'),
    'virtualization.vm-no-network': ContextQuestion('virtualization.vm-no-network', 'What is the exact local libvirt VM name?', 'Identify guest adapter, virtual switch, guest IP and permitted reachability tests.'),
}


def context_question(case_id: str) -> ContextQuestion | None:
    return CONTEXT_QUESTIONS68.get(case_id)


def safe_target_note(value: str | None) -> str | None:
    """One optional, unverified description, never a command or path.

    Omit potentially private data and dangerous control characters. This is
    only shown in a plain-text Qt label, not included in the evidence log.
    """
    if not isinstance(value, str):
        return None
    target=value.strip()
    if not (1 <= len(target) <= 80) or any(ord(x) < 32 or ord(x) == 127 for x in target):
        return None
    if any(x in target for x in ('/', '\\', '`', '$', '<', '>', '{', '}', ';', '|')):
        return None
    if re.search(r'(?i)\b(password|passwd|token|secret|api.?key|bearer|private key)\b',target):
        return None
    return target


def context_explanation(case_id: str, target: str | None) -> str:
    spec=context_question(case_id)
    if spec is None:
        return ''
    label=safe_target_note(target)
    text=('Extra context for this problem (not proof of a cause):\n'
          +spec.question+'\n'
          +('User-supplied target: '+label+' (not independently verified).\n' if label else
             'No specific target was provided; the diagnosis cannot link generic measurements to one target.\n')
          +'Evidence the Troubleshooter still needs to establish: '+spec.required_evidence+'\n'
          +'You do not need to inspect logs yourself. This text cannot trigger commands, prove a cause, or authorize repairs.')
    return text
