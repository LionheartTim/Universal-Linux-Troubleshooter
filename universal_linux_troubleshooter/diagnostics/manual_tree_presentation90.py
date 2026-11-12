"""v90: static, copyable Manual Diagnostics pages built from the existing tree.

Only user-facing text: NEVER executes documentary shell commands, makes an
assessment, unlocks routes, or reuses evidence from a previous scan.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from .manual_cases40 import case_catalog, plan_for_manual_case
from ..catalog import CATEGORIES

ULT = 'https://github.com/LionheartTim/Universal-Linux-Terminal'
ULSM = 'https://github.com/LionheartTim/Universal-Linux-Software-Manager'


@dataclass(frozen=True)
class ManualTreePages:
    check_info: str
    diagnosis: str
    solution: str
    offers_ulsm: bool


def _txt(value, limit=1200):
    """Tree data are authored documentation, not markup or executable code."""
    if not isinstance(value, str):
        return ''
    return ' '.join(value.split())[:limit]


def _readable_step(value: str, limit: int = 1800) -> str:
    """Place each authored instruction sentence on a separate line.

    Preserve the wording, commands and conditional requirements.  Only plain
    documentary prose is split; terminal commands use their own renderer.
    Do not split dotted filenames, domain names or version numbers: only
    sentence punctuation followed by a capitalized new sentence qualifies.
    """
    text = _txt(value, limit)
    return re.sub(r'(?<=[.!?])\s+(?=[A-Z0-9])|(?<=;)\s+(?=[A-Z])', '\n', text)


def _enumerate(items):
    return '\n'.join(f'{i}. {_txt(item)}' for i, item in enumerate(items, 1) if _txt(item))


def _format_terminal_step(instruction: str, command: str) -> str:
    """Put a documentary terminal command on its own copyable line.

    Only a command already present in the trusted per-case terminal reference is
    separated. Never infer a command by splitting at a period (e.g. .service),
    nor interpret/execute these instructional strings.
    """
    text = _txt(instruction, 1800)
    command = _txt(command, 500)
    before, sep, remainder = text.partition(': ')
    if not command or not sep or not remainder.startswith(command):
        return '• ' + text
    before += ':'
    after = remainder[len(command):].strip()
    if after.startswith('. '):
        after = after[2:]
    return '\n'.join((
        '• ' + before,
        '',
        '    ' + command,
        '',
        '  ' + after,
    ))



def _focused_comparison(instruction: str) -> str:
    """Keep the specific user test; omit the huge unrelated case-ID catalog."""
    detail = instruction.split('Case-specific supplementary check:', 1)[-1]
    detail = detail.split('Also consider documented hardware/software alternatives:', 1)[0]
    return _txt(detail.strip(), 490)


def _diagnostic_actions(case: dict, guide: dict) -> list[str]:
    """Actions a user can try to distinguish explanations, not proof or repairs.

    All technical instructions originate in the authored case catalog. They
    never become runtime commands; only official case source URLs are offered.
    """
    actions = [
        'CHECKS YOU CAN TRY',
        'Try the steps that apply to your situation. ULTS does not perform these manual actions for you.',
    ]
    curated = [v for v in case.get('supplemental_investigation_steps83', ())
               if isinstance(v, str) and v.strip()]
    comparisons = [v.get('instruction', '') for v in guide.get('steps', ())
                   if v.get('phase') == 'independent_comparison'
                   and isinstance(v.get('instruction'), str)]
    # Preserve every authored, relevant independent comparison. A fixed display
    # cap silently hides necessary steps (some cases need four to six).
    # Use the authored v83 comparisons if available; otherwise use all specific
    # v84 comparisons while omitting generic cross-case-ID catalog boilerplate.
    comparisons = curated if curated else [_focused_comparison(x) for x in comparisons]
    number = 0
    for instruction in comparisons:
        number += 1
        actions += [
            '',
            f'MANUAL TEST {number} — Compare device or application behavior',
            _txt(instruction, 490),
        ]
    # Render every documented terminal test, in authored order, with its own
    # interpretation/precautions. The case data determine the count, not UI.
    for command in case.get('terminal_result_guides', ()):
        command_text = _txt(command.get('command'), 500)
        if not command_text:
            continue
        number += 1
        actions += [
            '',
            f'MANUAL TEST {number} — {_txt(command.get("purpose"), 150) or "Inspect the system"}',
            'Optional: run this command yourself only if you understand what it does. Check any example paths, required permissions and safety notes first.',
            'COMMAND',
            command_text,
            'WHAT THE RESULT CAN SHOW',
            _txt(command.get('interpretation'), 600),
            'WHAT IT DOES NOT PROVE',
            _txt(command.get('cannot_prove'), 600),
        ]
        precautions = [_txt(p, 1200) for p in command.get('precautions', ()) if _txt(p, 1200)]
        if precautions:
            actions += ['SAFETY NOTE', '\n'.join(f'- {item}' for item in precautions)]
    actions += ['', 'HOW TO INTERPRET YOUR TESTS',
                'Compare the outcome with the possible causes and any conflicting evidence above. Follow a solution only when you have verified that its conditions apply.']
    if case.get('domain') == 'hardware':
        actions += [
            '', 'HARDWARE AND MANUFACTURER SUPPORT',
            'Identify the exact manufacturer and model from the device label or hardware IDs in the terminal results.',
            'If safe, compare a known working cable/port or another computer for removable devices.',
            'Visit the official manufacturer support page for your exact model. Check its manual, compatibility guidance, approved firmware instructions and warranty. A lit status light or a detected device does not guarantee that it works.',
        ]
    else:
        actions += [
            '', 'APPLICATION / DISTRIBUTION SUPPORT',
            'Compare with a trusted second application where relevant; check the official maintainer or distribution instructions for your installed version and package source.',
        ]
    sources = [x for x in case.get('source_links', ())
               if isinstance(x, str) and x.startswith('https://')]
    if sources:
        actions += ['', 'RELEVANT TECHNICAL DOCUMENTATION',
                    'General project documentation; this is not a device-model vendor page:']
        for url in sources:
            actions += ['REFERENCE URL', url]
    actions += ['', 'IF THE RESULT IS STILL UNCLEAR',
                'If the tests are inconclusive, the cause remains UNKNOWN. Continue with Solution. Do not infer a defect from inventory alone. If you suspect a hardware fault, contact the manufacturer with the exact model and relevant, non-sensitive test results.']
    return actions


def pages_for_case(case_id: str) -> ManualTreePages:
    """Render all 250 cases identically in depth, not identically in claims.

    A documentary route is explicitly conditional, even if a scan has produced
    an observation. The separate case assessor remains the *sole* route gate.
    """
    case = case_catalog()[case_id]  # raises KeyError on an unknown case
    guide = case.get('manual_investigation_guide84', {})
    steps = guide.get('steps', ())
    commands = case.get('terminal_result_guides', ())
    routes = case['resolution_routes']

    info = [
        f'Reported problem: {_txt(case["symptom"])}',
        'WHAT IS CHECKED',
        'The app runs the available read-only Linux checks. Commands shown in this guide are for you to run manually; they are not executed automatically.',
    ]
    for step in steps:
        if step.get('phase') in ('scope', 'automatic_evidence'):
            info.append('• ' + _txt(step.get('instruction'), 1600))
    checks, probes = plan_for_manual_case(case_id)
    by_check = {(cat.key, item.key): item for cat in CATEGORIES for item in cat.checks}
    if checks or probes:
        info.append('AUTOMATIC READ-ONLY CHECK PLAN')
        for pair in checks:
            spec = by_check.get(pair)
            info.append('• ' + (_txt(spec.title) + ': ' + _txt(spec.purpose) if spec else '/'.join(pair)))
        for probe in probes:
            info.append('• Additional local check: ' + _txt(probe))
    info += [
        'Evidence that may support this explanation: ' + _txt(case.get('supporting_evidence')),
        'Evidence that may point to another cause: ' + _txt(case.get('counter_evidence')),
        'If a check was skipped, could not finish or produced unclear results, its outcome remains unknown. This does not confirm or rule out a fault.',
    ]
    if case.get('cross_domain_case_ids'):
        links = [case_catalog()[linked]['title'] for linked in case['cross_domain_case_ids']]
        info.append('Related hardware and software checks: ' + '; '.join(links))

    diagnoses = [
        'POSSIBLE CAUSES — NOT YET CONFIRMED',
        'These are possible explanations, not confirmed faults. Compare them with the checks and observations for your own device.',
    ]
    for i, route in enumerate(routes, 1):
        diagnoses.append(f'{i}. Possible explanation — {_txt(route["applicability_condition"])}')
    diagnoses += [
        'Supporting observations: ' + _txt(case.get('supporting_evidence')),
        'Counter-evidence and alternatives: ' + _txt(case.get('counter_evidence')),
        'Match findings to the affected device, user session and time. Even a relevant result does not necessarily reveal the root cause.',
    ]
    diagnoses += ['', *_diagnostic_actions(case, guide)]
    prov = case.get('event_provenance88', {})
    if prov.get('status') and prov['status'] != 'no_individual_event_rule':
        diagnoses.append('Individual event observation: a case-specific signal may be present, but the matching device, source and event time must be verified. An event does not establish the underlying cause or authorize a repair.')

    # v93: One consistent terminal section, not the same commands buried in
    # prose and then printed again. Each activity has its own titled block.
    solutions = [
        'STEP-BY-STEP TROUBLESHOOTING',
        '',
        'Follow the steps that match your situation. Skip anything that does not apply to your device,',
        'distribution or connection. Stop when a safety precaution applies.',
        '',
        'INVESTIGATION STEPS',
    ]
    step_number = 0
    for item in steps:
        phase = item.get('phase', '')
        if phase in ('scope', 'automatic_evidence', 'terminal_first', 'terminal_second'):
            continue
        instruction = _txt(item.get('instruction'), 1800)
        if not instruction:
            continue
        step_number += 1
        solutions += ['', f'STEP {step_number}', _readable_step(instruction), '']

    curated = case.get('supplemental_investigation_steps83', ())
    if curated:
        solutions += ['', 'ADDITIONAL DEVICE / APPLICATION CHECKS', '']
        for i, instruction in enumerate(curated, 1):
            solutions += [f'CHECK {i}', _readable_step(instruction, 1500), '']

    solutions += ['', 'USER-RUN TERMINAL TESTS (DISPLAY ONLY; NEVER EXECUTED BY THE APP)',
                  '', 'Run only the commands relevant to your situation. They are provided as',
                  'manual instructions; the Troubleshooter never executes them.', '']
    if not commands:
        solutions += ['No extra terminal checks are needed for this guide.', '']
    for idx, cmd in enumerate(commands, 1):
        solutions += [
            f'TERMINAL TEST {idx} — {_txt(cmd.get("purpose"), 220) or "Additional check"}',
            'Optional: run this command yourself only if you understand what it does. Check any example paths, required permissions and safety notes first.',
            'COMMAND',
            _txt(cmd.get('command'), 500),
            'WHAT THE RESULT CAN SHOW',
            _txt(cmd.get('interpretation')),
            'WHAT IT DOES NOT PROVE',
            _txt(cmd.get('cannot_prove')),
        ]
        precautions = [_txt(caution) for caution in cmd.get('precautions', ()) if _txt(caution)]
        if precautions:
            solutions += ['SAFETY NOTE', '\n'.join(f'- {item}' for item in precautions)]
        solutions += ['']

    solutions += [
        'OPTIONAL TERMINAL HELPER',
        'You can use your regular Linux terminal or Universal Linux Terminal:',
        ULT,
        'Before running a command, check its permissions, file paths and example placeholders.',
        'Remove private details from any output before sharing it.',
        '', 'POSSIBLE SOLUTIONS',
        'Choose a solution only when you have confirmed that its conditions match your problem.',
        'You decide whether to make a change. ULTS will never repair your system automatically.',
    ]
    offers_ulsm = False
    for idx, route in enumerate(routes, 1):
        solutions += ['', f'PATH {idx} — WHEN THIS APPLIES',
                      _txt(route['applicability_condition']), '',
                      'BEFORE TAKING ACTION',
                      'First confirm that the condition applies to the affected device or application. '
                      'If the condition is unknown or contradicted by other evidence, do not follow this solution.', '',
                      'STEPS']
        for i, step in enumerate(route.get('user_steps', ()), 1):
            solutions += [f'{i}. {_readable_step(step, 1300)}', '']
        action = _txt(route.get('user_executed_command'), 500)
        if action:
            solutions += ['USER-OPERATED ACTION — CHECK RISKS AND BACKUPS FIRST', '',
                          'COMMAND', action, '']
        gui = route.get('optional_package_gui85')
        if gui:
            offers_ulsm = True
            solutions += ['OPTIONAL PACKAGE-MANAGEMENT GUI',
                          'Universal Linux Software Manager (only for supported package operations):',
                          ULSM, '']
            for j, step in enumerate(gui.get('steps', ()), 1):
                solutions += [f'{j}. {_txt(step)}', '']
            solutions += ['LIMITATIONS', _txt(gui.get('not_supported')), '']
        solutions += ['VERIFY THE ORIGINAL PROBLEM',
                      _txt(route.get('verification_goal'), 950), '']

    solutions += [
        '', 'AFTER EACH ACTION',
        'Try the original action again under the same relevant conditions.',
        'Use Rescan to collect fresh, read-only system results.',
        'If the result is unclear or the symptom persists, investigate the other plausible causes.',
        'A successful command or an empty log does not, by itself, mean the problem is fixed.',
        'These instructions do not execute commands or make changes for you.',
    ]
    return ManualTreePages('\n\n'.join(info), '\n\n'.join(diagnoses), '\n'.join(solutions), offers_ulsm)
