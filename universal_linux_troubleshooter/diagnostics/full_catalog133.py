"""Full-catalog, read-only Manual Diagnostics scan (no AI or repair).

There are 250 documented *symptoms*, not 250 independent hardware tests.
Run the union of existing reviewed, bounded local checks once, then show which
symptoms have usable evidence and which still require a focused user selection.
Never turn a generic warning into a confirmed cause for an unreported symptom.
"""
from __future__ import annotations

from dataclasses import dataclass
from collections import Counter
import re
from .plan import complete_system_plan
from .manual_cases40 import case_catalog, plan_for_manual_case
from .focused_evidence import PROBES, CHAT120_PROBES
from .topic_catalog127 import all_topics
from .case_assessment import assess_case_id
from .full_scan_topic_solutions135 import make_topic_solutions
from ..results import ResultStatus

# Independent, safe local inventories shared by multiple guide categories.
# The same allowlist is enforced again by the worker at execution time.
_SHARED_GUIDE_PROBES = (
    'steam_inventory128', 'browser_inventory119', 'browser_runtime119',
    'gamepad_inventory120', 'gamepad_path124',
)

@dataclass(frozen=True)
class FullCatalogPlan:
    checks: tuple[tuple[str, str], ...]
    probes: tuple[str, ...]
    cases: int
    guides: int


def complete_catalog_plan(ready, *, include_network=False) -> FullCatalogPlan:
    """Unique existing bridge checks + unique named, allowlisted local probes."""
    checks = complete_system_plan(ready, include_network=include_network)
    registry = {**PROBES, **CHAT120_PROBES}
    probes = set(_SHARED_GUIDE_PROBES)
    cases = case_catalog()
    for cid in cases:
        _, names = plan_for_manual_case(cid)
        probes.update(names)
    if not probes.issubset(registry):
        raise ValueError('Catalog has an unreviewed focused probe')
    return FullCatalogPlan(checks, tuple(sorted(probes)), len(cases), len(all_topics()))


def scan_catalog_coverage(plan: FullCatalogPlan, results, probe_results, *, finished=False):
    """Describe measured coverage, NOT 250 confirmed or disproven failures.

    Unknown probe outcomes still count as attempted but not usable evidence.
    A missing measurement never becomes OK or an absence-of-fault assertion.
    """
    base = {key: value for key, value in results.items() if key in plan.checks}
    focused = {r.check_key: r for r in probe_results if r.category_key == 'focused'
               and r.check_key in plan.probes}
    lines = []
    counts = Counter()
    signals = []
    previous_group = None
    for cid, case in sorted(case_catalog().items(),
                            key=lambda item: (item[1]['domain'], item[1]['category'], item[1]['title'])):
        group = (case['domain'], case['category'])
        if group != previous_group:
            lines.extend(('', f"{group[0].upper()} — {group[1].replace('_', ' ').upper()}"))
            previous_group = group
        checks, probes = plan_for_manual_case(cid)
        # The original case can use its reviewed checks. Additional user input,
        # fresh event correlation and symptom reproduction are separate steps.
        required = [*checks, *(('focused', name) for name in probes)]
        available = [base.get(pair) if pair[0] != 'focused' else focused.get(pair[1])
                     for pair in required]
        attempted = sum(r is not None for r in available)
        readable = sum(r is not None and r.status not in (ResultStatus.UNKNOWN, ResultStatus.NOT_RUN)
                       for r in available)
        explicit = bool(probes or case.get('diagnostic_check_ids'))
        # Review each case against its own validated evidence only. This
        # identifies event signatures, not a proven current user complaint.
        case_evidence = [r for r in available if r is not None]
        assessment = assess_case_id(cid, case_evidence)
        if assessment.symptom == 'supported' and assessment.proof:
            state = 'Reviewed local indicator detected; effect not confirmed'
            signals.append(case['title'])
            counts['signals'] += 1
        elif readable and explicit:
            state = 'Specific local evidence available; symptom not verified'
            counts['specific'] += 1
        elif readable:
            state = 'General system evidence only; symptom not verified'
            counts['general'] += 1
        elif attempted:
            state = 'Checks attempted; evidence inconclusive'
            counts['unknown'] += 1
        else:
            state = 'Not measured yet'
            counts['missing'] += 1
        lines.append(f"{case['title']} — {state} ({attempted}/{len(required)} measurements)")
    # Each supplemental guide is an entry point to an existing documented
    # case, not an extra independent system-health measurement. Listing them
    # explicitly lets users inspect *all* 393 catalog entries after the scan.
    lines.extend(('', f'ADDITIONAL SYMPTOM GUIDES ({plan.guides}; share parent-case evidence)'))
    last_heading = None
    for guide in sorted(all_topics(), key=lambda t: (t.domain, t.heading, t.title)):
        heading = (guide.domain, guide.heading)
        if heading != last_heading:
            lines.extend(('', f'{heading[0].upper()} — {heading[1].upper()}'))
            last_heading = heading
        lines.append(f'{guide.title} — relates to {case_catalog()[guide.case_id]["title"]}; '
                     'select the guide to test the exact symptom')
    return {
        'total_cases': len(case_catalog()), 'total_guides': plan.guides,
        'specific': counts['specific'], 'general': counts['general'],
        'signals': counts['signals'], 'signal_titles': tuple(signals),
        'unknown': counts['unknown'], 'missing': counts['missing'],
        'text': '\n'.join(lines), 'finished': bool(finished),
    }


# A supplementary journal observation is supporting evidence for the primary
# journal check, NOT an independent failing service. Keep the relationship
# here rather than turning a duplicate event into a second fault.
_SUPPLEMENTARY_PARENTS = {
    'critical_journal66': ('system', 'system_logs'),
    'slow_boot66': ('system', 'boot'),
}
_SUPPLEMENTARY_LABELS = {
    'critical_journal66': 'High-priority messages from this boot',
    'slow_boot66': 'Boot timing observation',
}


def _plain_excerpt(message: str, limit=190) -> str:
    """One readable result sentence, never raw logs or truncated shell steps."""
    value = ' '.join(str(message).split())
    if len(value) <= limit:
        return value
    candidates = re.split(r'(?<=[.!?])\s+', value)
    out = ''
    for sentence in candidates:
        if len(out) + len(sentence) + 1 > limit:
            break
        out = (out + ' ' + sentence).strip()
    return out if out else value[:limit].rsplit(' ', 1)[0] + '…'


def _named_crash_programs(result):
    """Use the program names already parsed by the trusted coredump reader."""
    names = []
    for line in result.explanation.splitlines():
        match = re.match(r'^\s*\d+\.\s+(.+?)\s+\(\d+ saved reports?\)\s*$', line)
        if match:
            names.append(match.group(1))
    return names[:8]


def full_scan_pages(plan: FullCatalogPlan, results, probes, categories, *, stopped=False):
    """Evidence-led complete scan: each flagged measurement gets next steps.

    A result is a measured *signal*. Do not turn an old journal event into a
    confirmed current failure, and do not merge unrelated technical events.
    """
    labels = {(c.key, x.key): f'{c.title} / {x.title}' for c in categories for x in c.checks}
    found = [results[p] for p in plan.checks if p in results]
    focused_by_key = {r.check_key: r for r in probes
                      if r.category_key == 'focused' and r.check_key in plan.probes}
    seen_probes = [focused_by_key[k] for k in plan.probes if k in focused_by_key]
    all_results = [*found, *seen_probes]
    expected = len(plan.checks) + len(plan.probes)
    attempted = len(found) + len(focused_by_key)
    finished = not stopped and attempted == expected
    counts = Counter(r.status for r in all_results)
    coverage = scan_catalog_coverage(plan, results, seen_probes, finished=finished)
    info = ('Complete system scan — whole Manual Diagnostics catalog\n\n'
            f'{plan.cases} documented problems and {plan.guides} symptom guides are included in the coverage review.\n'
            f'{len(plan.checks)} shared system checks and {len(plan.probes)} unique supplementary local checks are scheduled.\n'
            f'{attempted}/{expected} measurements returned.\n\n'
            'Measurements are shared where several problems use the same check.\n'
            'A catalog entry does not mean a fault was found. Select a specific problem to verify its symptom, device and solution.')
    state = ('All scheduled local measurements completed.' if finished else
             'This scan was stopped or did not return every scheduled result.')

    concerning = [(labels.get(p, '/'.join(p)), results[p]) for p in plan.checks
                  if p in results and results[p].status in (ResultStatus.PROBLEM, ResultStatus.WARNING)]
    focused_warning = [(key, row) for key, row in focused_by_key.items()
                       if row.status in (ResultStatus.PROBLEM, ResultStatus.WARNING)]
    # Associate duplicate signals with their primary check when both were
    # measured; otherwise show them as their own, explicitly tentative finding.
    supporting = {}
    stand_alone = []
    for key, row in focused_warning:
        parent = _SUPPLEMENTARY_PARENTS.get(key)
        if parent is not None and parent in results:
            supporting.setdefault(parent, []).append((key, row))
        else:
            stand_alone.append((key, row))

    diagnosis = [state, '', 'Findings that may need attention (not proven causes)', '']
    item = 0
    for title, row in concerning:
        item += 1
        diagnosis += [f'{item}. {title} — {row.status.value}',
                      'What was found: ' + _plain_excerpt(row.diagnosis, 270)]
        if (row.category_key, row.check_key) == ('applications', 'app_crashes'):
            names = _named_crash_programs(row)
            if names:
                diagnosis.append('Programs with saved reports: ' + ', '.join(names))
        for key, extra in supporting.pop((row.category_key, row.check_key), []):
            diagnosis.append('Related reading: ' + _SUPPLEMENTARY_LABELS.get(key, key.replace('_', ' ')) +
                             ' — an additional observation, not a separate confirmed fault.')
        diagnosis.append('')
    # E.g. boot timing accompanied an OK boot-events sample; neither result
    # should be silently discarded, nor should they count as two faults.
    for pairs in supporting.values():
        stand_alone.extend(pairs)
    for key, row in sorted(stand_alone):
        item += 1
        label = _SUPPLEMENTARY_LABELS.get(key, key.replace('_',' ').removesuffix('66').strip().capitalize())
        diagnosis += [f'{item}. {label} — additional observation',
                      'What was found: ' + _plain_excerpt(row.explanation, 190), '']
    if not item:
        diagnosis.append('No local check reported a warning or problem status.')


    unknown = [(labels.get(p, '/'.join(p)), results[p]) for p in plan.checks
               if p in results and results[p].status == ResultStatus.UNKNOWN]
    if unknown:
        diagnosis += ['Measurements that could not establish a result (not faults)',
                      *('• ' + title + ': ' + _plain_excerpt(row.diagnosis, 175) for title, row in unknown[:8]), '']
        if len(unknown) > 8:
            diagnosis.append(f'{len(unknown)-8} more inconclusive results are available in Evidence / Logs.')
    diagnosis += ['Other measured outcomes',
                  f'• {counts[ResultStatus.OK]} OK; {counts[ResultStatus.INFO]} information only; '
                  f'{counts[ResultStatus.UNKNOWN]} inconclusive; {counts[ResultStatus.NOT_RUN]} not run.', '',
                  'Coverage of the 250 documented problems',
                  f'• {coverage["signals"]} matching local event signatures; this does not establish an active user problem.',
                  f'• {coverage["specific"]} have specific observations; {coverage["general"]} have only general observations.',
                  f'• {coverage["unknown"]} inconclusive; {coverage["missing"]} not measured.',
                  '• See Catalog coverage in the results menu for individual entries.', '',
                  'The scan does not reproduce every symptom or prove that every installed app works.']

    # Render exact authored investigation steps and conditional solution routes
    # from the linked existing cases, not broad, manually-written previews.
    warning_topics = [(title, row) for title, row in concerning]
    warning_topics.extend(((_SUPPLEMENTARY_LABELS.get(key, key), row))
                          for key, row in sorted(stand_alone))
    solution = make_topic_solutions(warning_topics, results=results, probes=focused_by_key,
                                    unknown=unknown)

    evidence = ['Complete system scan — original results', f'{attempted}/{expected} attempts returned.', '']
    for key in plan.checks:
        result = results.get(key)
        name = labels.get(key, '/'.join(key))
        evidence.extend((name, f'Status: {result.status.value}' if result else 'Status: Not measured'))
        if result:
            evidence.extend((result.diagnosis, result.explanation, result.solution, *result.evidence))
        evidence.append('')
    for key in plan.probes:
        result = focused_by_key.get(key)
        evidence.extend((f'Supplementary / {key}', f'Status: {result.status.value}' if result else 'Status: Not measured'))
        if result:
            evidence.extend((result.diagnosis, result.explanation, *result.evidence))
        evidence.append('')
    evidence.extend(('Catalog coverage (not individual diagnoses)', coverage['text']))
    return info, '\n'.join(diagnosis), solution, '\n'.join(evidence), coverage
