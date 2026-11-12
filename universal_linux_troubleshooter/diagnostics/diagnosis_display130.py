"""Short, objective, case-scoped Manual Diagnostics result presentation.

Consumes only read-only DiagnosticResult objects supplied by the existing bridge.
Never evaluates repairs, performs I/O, or treats exploratory journal warnings as
proof that the user's reported device/application has failed.
"""
from __future__ import annotations

import re
from ..catalog import CATEGORIES
from ..results import DiagnosticResult, ResultStatus
from .manual_cases40 import case_catalog, plan_for_manual_case

_NAMES = {(cat.key, check.key): check.title for cat in CATEGORIES for check in cat.checks}
_BROAD = frozenset({('system', 'system_logs'), ('hardware', 'hardware_logs'),
                    ('applications', 'app_crashes')})
_FACT = re.compile(r'^FACT:([a-z][a-z0-9_]*)=([a-z0-9_]+)$')
_UNCERTAIN = frozenset({'unknown', 'undetermined', 'not_observed_in_sample',
                        'not_observed_in_checked_paths', 'not_observed_in_checked_scopes'})
# These local technical descriptions are identifiers, never unverified diagnoses.
_FACT_TITLES = {
    'controller_candidates': 'Controller-like input devices',
    'gamepad_input': 'Game-controller input registration',
    'joystick_handler': 'Joystick interface',
    'event_handler': 'Input-event interface',
    'axis_capabilities': 'Joystick axes',
    'key_capabilities': 'Controller buttons',
    'input_stack': 'Linux input subsystem',
    'bus': 'Connection type',
    'gpu_reset': 'GPU reset event',
    'oom_kill': 'Out-of-memory termination',
    'fs_error': 'Filesystem error event',
    'ecc_ue': 'Uncorrectable memory event',
    'battery_wear': 'Battery wear',
    'battery_charge': 'Battery charging status',
    'radio': 'Wireless radio status',
    'link': 'Network link state',
    'ipv4': 'IPv4 addressing',
    'dhcp': 'DHCP status',
    'pipewire_inactive': 'PipeWire service state',
    'steam_flatpak_registration': 'Steam Flatpak registration',
    'steam_flatpak_user': 'Steam via Flatpak (user)',
    'steam_flatpak_system': 'Steam via Flatpak (system)',
    'steam_rpm': 'Steam via RPM (DNF / Zypper)',
    'steam_deb': 'Steam via DEB (APT / dpkg)',
    'steam_pacman': 'Steam via Pacman',
    'steam_snap': 'Steam via Snap',
    'steam_apk': 'Steam via Alpine APK',
    'steam_xbps': 'Steam via Void Linux XBPS',
    'steam_native_user_data': 'Steam native user files',
    'steam_flatpak_user_data': 'Steam Flatpak user files',
    'steam_local_manifests': 'Local Steam game manifests',
}
_ENGLISH_DIAGNOSIS = re.compile(
    r'\b(?:een|geen|niet|wordt|zijn|gezien|waargenomen|aangetroffen|onbekend|'
    r'aanvullende|controle|melding|meldt|meerdere|dezelfde|beschikbaar|gebruiker)\b', re.I)


def _natural(value: str, limit: int = 190) -> str:
    """Preserve an English diagnostic summary without raw logs or HTML."""
    text = ' '.join(value.split()).strip()
    if not text or _ENGLISH_DIAGNOSIS.search(text):
        return ''
    if len(text) > limit:
        text = text[:limit].rsplit(' ', 1)[0].rstrip(' ,;:') + '…'
    return text


def _focused_facts(result: DiagnosticResult) -> tuple[str, ...]:
    """Render a bounded subset of ACTUAL structured observations, not repairs."""
    if result.status in (ResultStatus.UNKNOWN, ResultStatus.NOT_RUN):
        return ()
    lines = []
    for raw in result.evidence:
        match = _FACT.fullmatch(raw)
        if not match:
            continue
        key, value = match.groups()
        if value in ('unknown', 'undetermined') or len(lines) >= 18:
            continue
        title = _FACT_TITLES.get(key, key.replace('_', ' ').capitalize())
        if value == 'not_observed_in_sample':
            lines.append(f'{title}: not seen in the checked sample')
        elif value == 'not_observed_in_checked_paths':
            lines.append(f'{title}: not found in the checked locations')
        elif value == 'not_observed_in_checked_scopes':
            lines.append(f'{title}: not found in the checked installation scopes')
        elif value == 'observed':
            lines.append(f'{title}: observed in this check')
        elif value == 'not_observed':
            lines.append(f'{title}: not observed in this check')
        elif value in ('up', 'down', 'active', 'inactive', 'blocked', 'unblocked',
                       'degraded', 'offline', 'online', 'usb', 'not_charging'):
            lines.append(f'{title}: {value.replace("_", " ")}')
        elif value.isdecimal():
            # Bounded, device-local counts, NOT an indication that functions work.
            lines.append(f'{title}: {value}')
        else:
            # Avoid exposing unreviewed technical enums or treating them as a cause.
            continue
    return tuple(lines)


def _check_heading(key, result) -> str:
    title = _NAMES.get(key, key[1].replace('_', ' ').title())
    if result.status == ResultStatus.OK:
        return f'{title} — checked'
    if result.status in (ResultStatus.WARNING, ResultStatus.PROBLEM):
        return f'{title} — observation needs review'
    if result.status == ResultStatus.INFO:
        return f'{title} — checked'
    if result.status == ResultStatus.NOT_RUN:
        return f'{title} — not run'
    return f'{title} — result unavailable'


def format_case_diagnosis130(case_id: str, report, results, *, completed: bool = True,
                             topic_id: str | None = None, package_sources=None) -> str:
    """Present the checked issue, concrete readings, and the assessor's proof level.

    A broad fallback check is background context, not evidence that a named
    program or device is faulty. Keep it in Evidence / Logs; choose locally
    relevant checks and targeted FACT markers for the beginner summary.
    """
    case = case_catalog()[case_id]
    expected, _ = plan_for_manual_case(case_id)
    from .scan_plan132 import planned_case_probes
    targeted = planned_case_probes(case_id, topic_id)
    if topic_id:
        from .topic_catalog127 import BY_KEY
    ordered = (*expected, *(('focused', probe) for probe in targeted))
    permitted = set(ordered)
    seen: dict[tuple[str, str], list[DiagnosticResult]] = {}
    for result in results:
        if isinstance(result, DiagnosticResult):
            key = (result.category_key, result.check_key)
            if key in permitted:
                seen.setdefault(key, []).append(result)

    if report is None:
        return 'Select Investigate selected problem to run the available read-only checks.'

    # These sections only describe data actually returned for THIS scan.
    lines = ['WHAT THE CHECKS FOUND']
    details = []
    for key in ordered:
        readings = seen.get(key, ())
        if len(readings) != 1:
            continue
        result = readings[0]
        # Broad exploratory logs and generic unrelated crash records are not
        # a case-specific event. Still available unchanged in Evidence / Logs.
        if key in _BROAD:
            continue
        if key[0] == 'focused':
            facts = _focused_facts(result)
            if facts:
                # A FACT describes what the local check saw, not why it happened.
                details.append(_check_heading(key, result))
                details.extend('- ' + fact for fact in facts)
            else:
                summary = _natural(result.diagnosis)
                explanation = _natural(result.explanation)
                if summary or explanation:
                    details.append(_check_heading(key, result))
                    details.append('- ' + (explanation or summary))
                else:
                    details.append(_check_heading(key, result))
            continue
        details.append(_check_heading(key, result))
        summary = _natural(result.diagnosis)
        explanation = _natural(result.explanation)
        if result.status not in (ResultStatus.UNKNOWN, ResultStatus.NOT_RUN):
            if summary:
                details.append('- ' + summary)
            elif explanation:
                details.append('- ' + explanation)
        elif explanation and 'does not tell us whether' not in explanation:
            details.append('- ' + explanation)
    if not details:
        # Do NOT invent a measured observation or show a general journal error.
        if any(len(seen.get(key, ())) == 1 for key in ordered):
            details.append('The available checks did not return a specific finding for this problem.')
        else:
            details.append('No matching local check results were available.')
    lines.extend(details)

    # The shared profile describes available package SOURCES, not which app is
    # installed. Only show it when package provenance is relevant.
    if package_sources is not None:
        from .package_sources131 import package_relevance, description, valid_summary, SOURCES
        guide_title = BY_KEY[topic_id].title if topic_id else ''
        if package_relevance(case_id, case['title'], guide_title) and valid_summary(package_sources):
            lines.extend(['', 'PACKAGE SOURCES ON THIS COMPUTER'])
            for source in (*SOURCES, 'appimage'):
                item = package_sources.get(source)
                if item is None:
                    lines.append('- ' + description(source) + ': not checked')
                elif item['status'] == 'checked':
                    lines.append('- ' + description(source) + ': local information checked (not proof this app is installed)')
                elif item['status'] == 'unavailable':
                    lines.append('- ' + description(source) + ': tool unavailable in this environment')
                else:
                    lines.append('- ' + description(source) + ': could not check')
    lines.extend(['', 'CONCLUSION'])
    if not completed:
        lines.append('This investigation was interrupted. The results are incomplete.')
    elif report.proven_route:
        route = next((r for r in case['resolution_routes']
                      if r['id'] == report.proven_route), None)
        if route is not None:
            lines.append('The reviewed evidence supports this condition: ' + route['applicability_condition'])
            lines.append('See Solution for the steps and precautions. No changes were made.')
        else:
            lines.append('The checked evidence supports a specific condition. See Solution.')
    elif report.status == 'supported':
        lines.append('A related signal was observed, but the cause of the reported problem is not confirmed.')
    elif report.status == 'contradicted':
        lines.append('The results do not support one possible explanation. This does not rule out other causes.')
    else:
        lines.append('The available results have not established the cause of this specific problem.')
    return '\n'.join(lines)
