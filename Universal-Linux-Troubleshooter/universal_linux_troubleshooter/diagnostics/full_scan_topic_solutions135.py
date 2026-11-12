"""v135: Full-scan findings linked to the *existing* Manual Diagnostics topics.

This presentation has no diagnostic authority. It never selects a repair because
of a broad warning; conditional paths come verbatim from the already-authored
250-case catalog. Only the reviewed case assessor may independently approve a
route, and no action/command is executed by this module.
"""
from __future__ import annotations

from textwrap import shorten
from functools import lru_cache

from .case_assessment import assess_case_id
from .manual_cases40 import case_catalog, plan_for_manual_case
from ..results import DiagnosticResult, ResultStatus

# Curated PRIMARY topic for each shared check. A shared check can be used by
# dozens of different cases: it must not automatically propose all of them.
# The topic is a relevant place to investigate the observation, not a claim
# that the user's symptom or either of its routes is proven.
CHECK_TOPIC = {
    ('network', 'adapter'): 'network.internet-outage',
    ('network', 'wifi'): 'network.wifi-missing',
    ('network', 'ip'): 'network.ip-missing',
    ('network', 'gateway'): 'network.no-gateway',
    ('hardware', 'sensors'): 'hardware.hot-computer',
    ('hardware', 'memory'): 'hardware.memory-error',
    ('storage', 'space'): 'storage.disk-full',
    ('storage', 'drives'): 'storage.disk-not-found',
    ('storage', 'health'): 'storage.disk-smart',
    ('storage', 'fs_logs'): 'storage.filesystem-errors',
    ('applications', 'services'): 'system.failed-service',
    ('applications', 'app_crashes'): 'applications.app-crash',
    ('applications', 'resources'): 'applications.ram-low',
    ('applications', 'permissions'): 'system.permissions-system',
    ('graphics', 'gpu'): 'graphics.gpu-missing',
    ('graphics', 'render'): 'graphics.gpu-crash',
    ('graphics', 'display'): 'graphics.resolution-wrong',
    ('audio', 'audio_devices'): 'audio.sound-missing',
    ('audio', 'audio_services'): 'audio.sound-missing',
    ('audio', 'bluetooth'): 'audio.bluetooth-not-found',
    ('virtualization', 'vm_backend'): 'virtualization.vm-feature-absent',
    ('virtualization', 'vm_network'): 'virtualization.vm-no-network',
    ('virtualization', 'containers'): 'virtualization.container-fail',
    ('system', 'boot'): 'system.boot-failure',
    ('system', 'updates'): 'system.update-error',
    ('system', 'system_logs'): 'system.system-logs',
}

# Supplementary probes are shown only when their parent was not already
# displayed. Never treat a supplementary journal event as an independent fault.
PROBE_TOPIC = {
    'critical_journal66': 'system.system-logs',
    'slow_boot66': 'system.slow-boot',
    'failed_units': 'system.failed-service',
    'boot_phases': 'software35.services.high-boot-time',
    'nvme': 'hardware34.storage.nvme-critical-warning',
    'dhcp': 'network.wired-link-no-carrier',
}

# These two are additional observations describing the same symptom topic as a
# shared check. The extra finding still belongs in Evidence / Logs unchanged.
SUPPORTS_PARENT = {
    'critical_journal66': ('system', 'system_logs'),
    'slow_boot66': ('system', 'boot'),
}


@lru_cache(maxsize=1)
def _unambiguous_probe_topics():
    """Unique case-to-probe links from the existing catalog (no guessed topics)."""
    linked: dict[str, set[str]] = {}
    for cid in case_catalog():
        _, probes = plan_for_manual_case(cid)
        for probe in probes:
            linked.setdefault(probe, set()).add(cid)
    return {key: next(iter(ids)) for key, ids in linked.items() if len(ids) == 1}


def _sentence(text: str, max_chars=360) -> str:
    """Brief, copyable text from a trusted result or existing case guidance."""
    return shorten(' '.join(str(text or '').split()), width=max_chars, placeholder='…')


def _topic_steps(case: dict) -> tuple[str, ...]:
    """Use actual case-authored, human investigative actions; not generic tips."""
    authored = case.get('supplemental_investigation_steps83') or ()
    if not authored:
        authored = [step.get('instruction', '')
                    for step in case.get('manual_investigation_guide84', {}).get('steps', ())
                    if step.get('phase') == 'independent_comparison']
    actions = []
    for raw in authored:
        if not isinstance(raw, str) or not raw.strip():
            continue
        # The original guide sometimes embeds a long catalog of cross-domain
        # alternatives. Keep its *specific* instruction only in the overview.
        value = raw.split('Case-specific supplementary check:')[-1]
        value = value.split('Also consider documented hardware/software alternatives:')[0]
        value = _sentence(value, 430)
        if value and value not in actions:
            actions.append(value)
    return tuple(actions[:3])


def _relevant_evidence(cid: str, results: dict, probes: dict):
    """Only the case's own planned check/probe keys can support assessment."""
    checks, targets = plan_for_manual_case(cid)
    relevant = [results[key] for key in checks if key in results]
    relevant.extend(probes[key] for key in targets if key in probes)
    return relevant


def solution_for_topic(cid: str, *, results: dict, probes: dict, observation: DiagnosticResult,
                       label: str, number: int, additional=()) -> str:
    """Clearly separated documented topic and *conditional* solution choices."""
    case = case_catalog()[cid]
    assessed = assess_case_id(cid, _relevant_evidence(cid, results, probes))
    lines = [
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
        f'TOPIC {number} — {case["title"]}',
        f'Related scan result: {label}',
        f'Observed: {_sentence(observation.diagnosis, 320)}',
        '',
        'CHECK THIS FIRST',
    ]
    checks = _topic_steps(case)
    if checks:
        lines.extend(f'{i}. {step}' for i, step in enumerate(checks, 1))
    else:
        lines.append('1. Match the exact affected device, program and event time to the measured result.')
    for i, (other_label, other) in enumerate(additional):
        lines.insert(5 + i, 'Also observed: ' + other_label + ' — ' + _sentence(other.diagnosis, 210))
    if (observation.category_key, observation.check_key) == ('applications', 'app_crashes'):
        import re
        programs = re.findall(r'^\s*\d+\.\s+(.+?)\s+\(\d+ saved reports?\)',
                              observation.explanation, re.M)
        if programs:
            lines.append('Programs named in the saved reports: ' + ', '.join(programs[:8]))
    lines.extend(('', 'POSSIBLE SOLUTIONS FROM THIS TOPIC'))
    if assessed.route:
        lines.append('A reviewed local condition supports one route below; confirm the affected device and symptom before acting.')
    else:
        lines.append('No repair condition has been independently confirmed by this scan. The documented paths below apply ONLY if their condition is verified.')
    for i, route in enumerate(case['resolution_routes'], 1):
        proven = (assessed.route == route['id'])
        lines += ['', f'PATH {i} — ' + ('REVIEWED LOCAL EVIDENCE' if proven else 'CONDITIONAL'),
                  'When this applies: ' + _sentence(route['applicability_condition'], 350)]
        if not proven:
            lines.append('Do not apply this path unless the stated condition is verified for the affected device or program.')
        for j, step in enumerate(route.get('user_steps', ()), 1):
            if isinstance(step, str) and step.strip():
                lines.append(f'  {j}. {_sentence(step, 580)}')
        goal = route.get('verification_goal')
        if isinstance(goal, str) and goal.strip():
            lines.append('Verify afterward: ' + _sentence(goal, 300))
    lines.extend(('', 'To view the complete source guidance and precautions, select "'
                  + case['title'] + '" in the problem list.',
                  'No commands or repairs were run by the scan.', ''))
    return '\n'.join(lines)


def make_topic_solutions(findings, *, results, probes, unknown=()):
    """Findings: ordered (label, DiagnosticResult) from the complete scan.

    Cover all shared checks using a curated index and additional probe signals
    where safe. Keep each result attached to its own topic; no cross-contamination.
    """
    case_index = case_catalog()
    unique = []
    seen_cases = set()
    related: dict[str, list] = {}
    unlinked = []
    for label, observation in findings:
        key = (observation.category_key, observation.check_key)
        cid = (CHECK_TOPIC.get(key) if key[0] != 'focused'
               else PROBE_TOPIC.get(key[1], _unambiguous_probe_topics().get(key[1])))
        if cid not in case_index:
            unlinked.append((label, observation))
            continue
        if key[0] == 'focused':
            # Radio blocks is shared by Wi-Fi and Bluetooth and could describe
            # either; never guess one from a generic inventory warning.
            if key[1] == 'radio_blocks':
                unlinked.append((label, observation))
                continue
            parent = SUPPORTS_PARENT.get(key[1])
            if (parent is not None and parent in results
                    and results[parent].status in (ResultStatus.PROBLEM, ResultStatus.WARNING)):
                continue
        if cid in seen_cases:
            # Preserve other warning observations while using just one coherent
            # topic and one set of documented conditional solution routes.
            related.setdefault(cid, []).append((label, observation))
            continue
        seen_cases.add(cid)
        unique.append((cid, label, observation))
    if not unique:
        if unknown or unlinked:
            lines = ['NO CONFIRMED CAUSE OR REPAIR',
                     'No warning was linked to a single relevant solution topic.']
            if unknown:
                lines.extend(['', 'MEASUREMENTS NEEDING MORE INFORMATION',
                              'These results do not prove that a device is healthy or defective.'])
                lines.extend('• ' + label + ': ' + _sentence(row.diagnosis, 230)
                             for label, row in unknown[:8])
            if unlinked:
                lines.extend(['', 'SUPPLEMENTARY WARNINGS WITHOUT ONE MATCHING TOPIC'])
                lines.extend('• ' + label + ': ' + _sentence(row.diagnosis, 200)
                             for label, row in unlinked[:8])
            lines.extend(['', 'Select the affected individual check for its documented next steps.',
                          'No settings were changed or repairs performed.'])
            return '\n'.join(lines)
        return ('No repair is suggested by these completed local checks.\n'
                'Select the affected symptom if something is not working.\n'
                'No settings were changed or repairs performed.')
    blocks = ['SOLUTIONS FROM EXISTING MANUAL DIAGNOSTICS TOPICS',
              'Each section below refers to a separate measured finding.\n'
              'A warning is not automatically a confirmed cause, and the solution paths remain conditional.', '']
    for index, (cid, label, observation) in enumerate(unique, 1):
        blocks.append(solution_for_topic(cid, results=results, probes=probes,
                                         observation=observation, label=label, number=index,
                                         additional=related.get(cid, ())))
    if unlinked:
        blocks.extend(['━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
                       'SUPPLEMENTARY WARNINGS WITHOUT A UNIQUE TOPIC',
                       'These observations can relate to different symptoms. Select the affected problem before choosing a solution.'])
        blocks.extend('• ' + label + ': ' + _sentence(row.diagnosis, 180)
                      for label, row in unlinked[:8])
    if unknown:
        blocks.extend(['━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
                       'MEASUREMENTS NEEDING MORE INFORMATION',
                       'These checks were inconclusive, not proven faults.'])
        for label, observation in unknown[:8]:
            blocks.append('• ' + label + ': ' + _sentence(observation.diagnosis, 180))
        blocks.append('For an inconclusive measurement, open its individual check to see the exact limitation.')
    blocks += ['━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
               'The Troubleshooter has not changed settings, installed software or repaired anything.']
    return '\n'.join(blocks)
