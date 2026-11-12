"""English-only, evidence-safe public wording for Manual Diagnostics case scans.

The internal assessor keeps its immutable validated evidence and route gates.
This layer uses the English source-authored case and observation metadata;
it never converts a finding into proof, discards a repair guard or runs a command.
"""
from __future__ import annotations

from ..catalog import CATEGORIES
from ..results import DiagnosticResult, ResultStatus
from .manual_cases40 import case_catalog, plan_for_manual_case


_CHECK_NAMES = {(cat.key, check.key): (check.title, check.purpose)
                for cat in CATEGORIES for check in cat.checks}


def display_case_report93(case_id, report, results):
    """Return English text for Diagnosis, Solution and Evidence / Logs.

    In particular, never show the old mixed-language assessor prose in the
    beginner-facing panes. All facts, case IDs, statuses and route gates remain
    internal and unchanged. The full English manual tree remains on the page.
    """
    case = case_catalog()[case_id]
    expected, probes = plan_for_manual_case(case_id)
    allowed = set(expected) | {('focused', p) for p in probes}
    present = {}
    for result in results:
        # A programming error must not turn dictionary keys or malformed
        # entries into supposed evidence (or crash the GUI after a scan).
        if not isinstance(result, DiagnosticResult):
            continue
        key = (result.category_key, result.check_key)
        if key in allowed:
            present.setdefault(key, []).append(result)
    observations = []
    evidence = [
        'READ-ONLY DIAGNOSTIC EVIDENCE',
        '',
        'Technical data below is taken from local checks. Raw host logs may use',
        'the system language and may contain private device identifiers.',
        '',
        f'CASE ID: {case_id}',
        f'CHECKS PLANNED: {len(expected)} standard; {len(probes)} targeted',
        '',
    ]
    for key in (*expected, *(('focused', x) for x in probes)):
        rows = present.get(key, ())
        title = _CHECK_NAMES.get(key, (key[1].replace('_', ' ').title(), ''))[0]
        if len(rows) != 1:
            label = 'Unavailable' if not rows else 'Ambiguous (duplicate result)'
            evidence.extend([f'{key[0]}/{key[1]} — {label}', ''])
            observations.append(f'{title}: {label.lower()}')
            continue
        result = rows[0]
        observations.append(f'{title}: {result.status.value}')
        evidence.extend([f'{key[0]}/{key[1]} — {result.status.value}'])
        # Preserve original machine evidence as-is: never forge or rewrite raw
        # log lines, but keep explanatory diagnostics in the English summary.
        for raw in result.evidence[:6]:
            if isinstance(raw, str) and not raw.startswith('FACT:'):
                evidence.append('  ' + raw[:240])
        evidence.append('')

    if report.status == 'supported':
        status = ('The local results support a reviewed diagnostic condition.'
                  if report.proven_route else
                  'A potentially relevant event was found, but its cause has not been confirmed.')
    elif report.status == 'contradicted':
        status = ('The results do not support one possible explanation. '
                  'Other causes remain possible.')
    else:
        status = ('No conclusive event has been linked to this problem. '
                  'Missing or incomplete results do not mean that everything is working.')

    diagnosis = '\n\n'.join([
        'CURRENT ASSESSMENT',
        status,
        'PROBLEM BEING INVESTIGATED',
        case['title'],
        'WHAT WOULD SUPPORT THIS EXPLANATION',
        case.get('supporting_evidence') or 'A fresh, matching observation of the affected device and symptom.',
        'WHAT COULD CONTRADICT IT',
        case.get('counter_evidence') or 'A conflicting observation or another plausible cause.',
        'LOCAL CHECK RESULTS',
        ('\n'.join('• ' + line for line in observations) or
         'No matching local check results are available.'),
        'UNCERTAINTY',
        'A listed device, a warning or a successful command is not enough to confirm a hardware fault or prove that a repair worked.',
    ])
    if not report.proven_route:
        solution = '\n\n'.join([
            'NO REPAIR HAS BEEN CONFIRMED',
            'The scan has not confirmed a repair for this problem. '
            'Use the step-by-step guide below to investigate the possible causes. '
            'Follow a solution only after confirming that its prerequisites apply.',
        ])
    else:
        route = next((r for r in case['resolution_routes'] if r['id'] == report.proven_route), None)
        if route is None:
            solution = 'NO REPAIR HAS BEEN CONFIRMED\n\nNo validated matching solution route was found.'
        else:
            solution = '\n\n'.join([
                'EVIDENCE-SUPPORTED OPTION (USER-OPERATED ONLY)',
                'APPLICABILITY', route['applicability_condition'],
                'STEPS', '\n'.join(f'{i}. {line}' for i,line in enumerate(route['user_steps'],1)),
                'VERIFY AFTERWARD', route.get('verification_goal') or 'Repeat the original failing action.',
                'No repairs are made automatically. Check your backups, Linux distribution and package source before making changes.',
            ])
    return diagnosis, solution, '\n'.join(evidence)
