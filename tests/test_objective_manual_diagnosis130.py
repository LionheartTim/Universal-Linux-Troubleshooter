"""Objective v130 Manual Diagnosis: observations must survive, not become cures."""
from __future__ import annotations

import pytest
from universal_linux_troubleshooter.diagnostics.manual_cases40 import (
    case_catalog, plan_for_manual_case, present_case)
from universal_linux_troubleshooter.diagnostics.diagnosis_display130 import format_case_diagnosis130
from universal_linux_troubleshooter.results import DiagnosticResult, ResultStatus

CASES = tuple(sorted(case_catalog()))


def sample(category, check, status=ResultStatus.OK, text='Observed a device during the scan.', evidence=()):
    return DiagnosticResult(category, check, status, text,
                            'The local interface was inspected.', 'No action was taken.', evidence)


@pytest.mark.parametrize('cid', CASES)
def test_all_cases_have_real_case_scoped_check_results_not_three_static_templates(cid):
    checks, probes = plan_for_manual_case(cid)
    results = [sample(*pair, status=ResultStatus.INFO,
                      text=f'Observed local data for {pair[1]}.') for pair in checks]
    if probes:
        results.append(sample('focused', probes[0], ResultStatus.INFO,
                              'Observed a targeted local measurement.',
                              ('FACT:input_stack=observed',)))
    report = present_case(cid, results)
    diagnosis = format_case_diagnosis130(cid, report, results)
    assert 'WHAT THE CHECKS FOUND' in diagnosis
    assert 'CONCLUSION' in diagnosis
    assert 'CURRENT ASSESSMENT' not in diagnosis
    assert 'WHAT COULD CONTRADICT IT' not in diagnosis
    assert 'These checks did not confirm a specific cause.' not in diagnosis
    assert 'No changes were made.' not in diagnosis or report.proven_route
    assert 'support this condition' not in diagnosis or report.proven_route
    assert 'Read-only data for a different problem' not in diagnosis


@pytest.mark.parametrize('cid', CASES)
def test_all_cases_ignore_unrelated_forged_system_log_noise(cid):
    checks, probes = plan_for_manual_case(cid)
    primary = sample(*checks[0], status=ResultStatus.INFO,
                     text='The selected local test returned information.')
    unrelated = sample('system', 'system_logs', ResultStatus.WARNING,
                       text='ALARM FROM AN UNRELATED PROGRAM')
    report = present_case(cid, [primary])
    diagnosis = format_case_diagnosis130(cid, report, [primary, unrelated])
    assert 'ALARM FROM AN UNRELATED PROGRAM' not in diagnosis


def test_real_gamepad_facts_become_readable_but_not_proof_buttons_work():
    cid = 'hardware34.peripherals.gamepad-controller'
    observed = sample('focused', 'peripheral_signals', ResultStatus.INFO,
                      'Automatische aanvullende feitencontrole', (
                        'FACT:controller_candidates=1', 'FACT:joystick_handler=observed',
                        'FACT:key_capabilities=observed', 'FACT:bus=usb'))
    result = format_case_diagnosis130(cid, present_case(cid, [observed]), [observed])
    assert 'Controller-like input devices: 1' in result
    assert 'Joystick interface: observed' in result
    assert 'Controller buttons: observed' in result
    assert 'Connection type: usb' in result
    assert 'buttons work' not in result.lower()
    assert 'cause of this specific problem' in result or 'related signal' in result


def test_negative_and_unknown_targeted_facts_never_become_positive_findings():
    cid = 'graphics.gpu-crash'
    obs = sample('focused', 'kernel_signals', ResultStatus.UNKNOWN,
                 'Automatische aanvullende feitencontrole', ('FACT:gpu_reset=observed',))
    diagnosis = format_case_diagnosis130(cid, present_case(cid, [obs]), [obs])
    assert 'GPU reset event: observed' not in diagnosis
    assert 'found a potentially relevant observation' not in diagnosis


def test_case_scope_ignores_other_case_result_even_if_warning():
    cid = 'audio.mic-not-working'
    microphone = sample('audio', 'audio_devices', ResultStatus.OK,
                        'A recording device is listed by the audio service.')
    storage = sample('storage', 'health', ResultStatus.PROBLEM,
                     'DISK SMART WARNING FROM ANOTHER PROBLEM')
    report = present_case(cid, [microphone, storage])
    diagnosis = format_case_diagnosis130(cid, report, [microphone, storage])
    assert 'A recording device is listed' in diagnosis
    assert 'DISK SMART WARNING' not in diagnosis


def test_steam_extra_local_inventory_is_visible_but_does_not_prove_repair():
    from universal_linux_troubleshooter.diagnostics.topic_catalog127 import all_topics
    guide = next(t for t in all_topics() if t.heading == 'Steam')
    steam = sample('focused', 'steam_inventory128', ResultStatus.INFO,
                   'Local Steam installation information',
                   ('FACT:steam_flatpak_registration=observed',
                    'FACT:steam_local_manifests=12'))
    report = present_case(guide.case_id, [], topic_id=guide.key)
    diagnosis = format_case_diagnosis130(guide.case_id, report, [steam], topic_id=guide.key)
    assert 'Steam Flatpak registration: observed' in diagnosis
    assert 'Local Steam game manifests: 12' in diagnosis
    assert 'proven repair' not in diagnosis.lower()


def test_duplicate_and_irrelevant_results_cannot_supply_a_finding():
    cid = 'audio.mic-not-working'
    r = sample('audio', 'audio_devices', ResultStatus.PROBLEM, 'DUPLICATE WARNING')
    report = present_case(cid, [r, r])
    result = format_case_diagnosis130(cid, report, [r, r])
    assert 'DUPLICATE WARNING' not in result


def test_cancelled_investigation_is_not_reported_as_complete():
    cid = 'graphics.gpu-crash'
    report = present_case(cid, [], completed=False)
    diagnosis = format_case_diagnosis130(cid, report, [], completed=False)
    assert 'interrupted' in diagnosis.lower()


def test_case_scan_is_presentation_only_and_html_escaped():
    from universal_linux_troubleshooter.diagnostics.readable_layout93 import html_for_manual93
    cid = 'audio.mic-not-working'
    r = sample('audio', 'audio_devices', ResultStatus.INFO, 'Detected <script>evil</script>')
    report = present_case(cid, [r])
    formatted = format_case_diagnosis130(cid, report, [r])
    assert '<script>' not in html_for_manual93(formatted)
    assert '&lt;script&gt;' in html_for_manual93(formatted)
