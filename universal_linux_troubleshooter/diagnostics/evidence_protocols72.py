"""v72: independent-evidence contracts for the 16 unresolved context dossiers.

This registry is NOT a new probe, consent dialog, FACT source, diagnosis,
or repair permission. It explicitly blocks treating inventory as causal proof.
Future interactive adapters must separately implement and obtain permission.
"""
from __future__ import annotations
from dataclasses import dataclass
from types import MappingProxyType

@dataclass(frozen=True)
class EvidenceProtocol:
    case_id: str
    access_class: str
    comparison: str
    required_evidence: str
    safety_boundary: str
    permission_required: bool = True
    automated_probe_available: bool = False
    causal_verdict_available: bool = False
    repair_approved: bool = False

_PROTOCOLS = (
    EvidenceProtocol('applications.permission-denied', 'explicit_file_access', 'filesystem_metadata', 'Identify the chosen file, exact denied operation, user and effective file access context.', 'Requires exact file and operation; a filename alone is insufficient'),
    EvidenceProtocol('audio.microphone-not-recording', 'recording', 'controlled_comparison', 'Compare recording from the same device in affected versus unaffected app.', 'Audio capture must never begin without specific permission'),
    EvidenceProtocol('display.screenshare-black', 'screen_capture', 'portal_session_comparison', 'Identify screencast app, portal request, compositor and permission result with timestamp.', 'No screenshot, stream or portal access without consent'),
    EvidenceProtocol('hardware34.display.panel-physical', 'physical_guidance', 'preboot_external_comparison', 'Compare artefacts before OS loading and using alternate external display/cable.', 'Physical panel diagnosis cannot follow from OS logs'),
    EvidenceProtocol('hardware34.memory.memory-channel', 'physical_guidance', 'firmware_slot_bandwidth_comparison', 'Compare physical DIMM slot layout, firmware channel configuration and measured bandwidth.', 'Installed capacity alone does not prove channel mode'),
    EvidenceProtocol('network.dns-problem', 'network_request', 'dns_and_ip_comparison', 'With consent compare DNS resolution for one hostname against direct IP reachability.', 'Hostname or DNS query cannot be sent before authorization'),
    EvidenceProtocol('software35.appimage.update-source-change', 'explicit_file_access', 'appimage_identity_hash_comparison', 'Identify original AppImage path/hash, updater result and preserved old file identities.', 'Do not hash arbitrary user path without deliberate selection'),
    EvidenceProtocol('software35.applications.locale-encoding', 'application_comparison', 'locale_encoding_reproduction', 'Identify app encoding, locale environment and affected text/input reproduction.', 'Global locale does not determine application encoding'),
    EvidenceProtocol('software35.desktop.scaling-blur', 'application_comparison', 'compositor_backend_render_comparison', 'Compare compositor scale, per-app rendering backend and native pixel output.', 'Compositor scale alone does not prove app blur'),
    EvidenceProtocol('software35.desktop.shortcut-conflict', 'user_settings', 'session_shortcut_binding_comparison', 'Identify the exact shortcut, current bindings and active keyboard scope.', 'Key label alone does not establish active binding scope'),
    EvidenceProtocol('software35.desktop.wayland-clipboard', 'clipboard', 'two_application_mime_comparison', 'Identify two target apps, compositor, clipboard MIME types and a consented copy/paste attempt.', 'Clipboard content must not be read without consent'),
    EvidenceProtocol('software35.development.venv-wrong-python', 'explicit_project_access', 'project_interpreter_comparison', 'Identify project environment path and compare interpreter, sys.prefix and executable location.', 'Do not execute project binaries or user-provided paths'),
    EvidenceProtocol('software35.network.hostname-resolution', 'network_request', 'hosts_nss_dns_comparison', 'Identify desired hostname/address and compare local hosts, NSS and permitted resolution.', 'Local hosts and actual resolution are distinct checks'),
    EvidenceProtocol('software35.network.proxy-wrong', 'user_settings', 'app_browser_proxy_comparison', 'Compare per-application proxy environment and browser proxy settings with consent.', 'Environment proxy is not proof of browser behavior'),
    EvidenceProtocol('storage.file-permission-denied', 'explicit_file_access', 'effective_acl_access_comparison', 'Identify exact file, path, operation, user, ACL and ownership; never chmod blindly.', 'Never blindly chmod or read file contents'),
    EvidenceProtocol('system.login-one-user-fails', 'user_session_logs', 'login_session_comparison', 'Compare affected versus working user login and matching display/session logs without revealing secrets.', 'Other-user session records may be private'),
 )
PROTOCOLS72 = MappingProxyType({p.case_id: p for p in _PROTOCOLS})
assert len(PROTOCOLS72) == len(_PROTOCOLS) == 16


def pending_evidence72(case_id: str) -> EvidenceProtocol | None:
    """Describe missing evidence. Never collect it or infer a verdict."""
    return PROTOCOLS72.get(case_id)


def safe_to_automate72(case_id: str, *, consent: bool = False) -> bool:
    """Fail-closed: consent is necessary but never sufficient for an unimplemented probe."""
    protocol = pending_evidence72(case_id)
    return bool(protocol and protocol.automated_probe_available and
                (consent or not protocol.permission_required))
