"""All findings in Complete system scan must have an actionable, safe path."""
from universal_linux_troubleshooter.catalog import CATEGORIES
from universal_linux_troubleshooter.diagnostics import READY_CHECKS
from universal_linux_troubleshooter.diagnostics.full_catalog133 import (
    complete_catalog_plan, full_scan_pages,
)
from universal_linux_troubleshooter.results import DiagnosticResult, ResultStatus


def result(category, key, status=ResultStatus.OK, diagnosis='Local inventory completed',
           explanation='Only this observation was measured.',
           solution='Review the relevant device and rerun the check.', evidence=()):
    return DiagnosticResult(category, key, status, diagnosis, explanation, solution, evidence)


def snapshot():
    plan = complete_catalog_plan(READY_CHECKS)
    readings = {pair: result(*pair) for pair in plan.checks}
    focused = [result('focused', key, ResultStatus.INFO) for key in plan.probes]
    return plan, readings, focused


def replace_probe(focused, key, row):
    focused[focused.index(next(r for r in focused if r.check_key == key))] = row


def test_full_scan_actually_recommends_steps_for_affected_programs_and_logs():
    plan, readings, focused = snapshot()
    readings[('applications', 'app_crashes')] = result(
        'applications', 'app_crashes', ResultStatus.WARNING,
        'Saved crash records were found for 2 named program(s)',
        'These programs stopped unexpectedly at the times listed in Evidence / Logs:\n'
        '1. /usr/bin/firefox (3 saved reports)\n2. /usr/bin/example (1 saved report)\n'
        'Old reports do not confirm a current problem.',
        'Update only the original affected application after reproducing a fresh crash.')
    readings[('system', 'system_logs')] = result(
        'system', 'system_logs', ResultStatus.WARNING,
        'Found 80 visible important system messages from 10 areas of the computer.',
        'Some messages are historical.', 'Disable some unrelated security controls.')
    replace_probe(focused, 'critical_journal66',
                  result('focused','critical_journal66', ResultStatus.WARNING,
                         'Extra observation','Current-boot important messages measured.'))
    replace_probe(focused, 'slow_boot66',
                  result('focused','slow_boot66', ResultStatus.WARNING,
                         'Extra observation','Boot timing observation made.'))
    _,diag,solution,logs,_ = full_scan_pages(plan, readings, focused, CATEGORIES)
    assert '/usr/bin/firefox' in diag and '/usr/bin/example' in diag
    assert '80 visible important system messages' in diag
    assert 'current-boot' not in diag.lower() or 'Related reading:' in diag
    assert 'High-priority messages from this boot' in diag
    assert diag.count('System, Boot & Updates / System errors') == 1
    assert 'Boot timing observation' in diag
    assert 'TOPIC 1 — Application closes unexpectedly' in solution
    assert 'Reproduce the crash with the exact application/version' in solution
    assert '/usr/bin/firefox' in solution
    assert 'When this applies: Only one optional application crashes' in solution
    assert 'Many red errors in system journal' in solution
    assert 'When this applies: Specific named service/device error repeats at symptom time' in solution
    assert 'Computer boots slowly' in solution
    assert 'Disable some unrelated security controls' not in solution
    assert 'settings were changed' in solution or 'changed settings' in solution
    assert 'Disable some unrelated security controls' in logs # historical original evidence preserved


def test_no_cause_does_not_invent_repairs_or_trigger_network():
    plan, readings, focused = snapshot()
    _,diag,solution,_,_ = full_scan_pages(plan, readings, focused, CATEGORIES)
    assert 'No local check reported a warning' in diag
    assert 'No repair is suggested' in solution
    assert 'settings were changed' in solution or 'changed settings' in solution
    assert ('network', 'dns') not in plan.checks
    assert ('network', 'external') not in plan.checks


def test_unknown_is_explicitly_not_a_disk_failure():
    plan, readings, focused = snapshot()
    readings[('storage','health')] = result('storage', 'health', ResultStatus.UNKNOWN,
                                             'Cannot read built-in health for two drives')
    _,diag,solution,_,_ = full_scan_pages(plan, readings, focused, CATEGORIES)
    assert 'Measurements that could not establish a result (not faults)' in diag
    assert 'Cannot read built-in health' in diag
    assert 'Unknown disk' not in diag
    assert 'do not prove that a device is healthy or defective' in solution


def test_warning_with_no_explicit_special_case_uses_reviewed_result_guidance():
    plan, readings, focused = snapshot()
    readings[('audio','bluetooth')] = result('audio','bluetooth',ResultStatus.WARNING,
        'Bluetooth adapter was not found in this inventory',
        solution='Check whether the adapter is physically connected before changing settings.')
    _,diag,solution,_,_ = full_scan_pages(plan, readings, focused, CATEGORIES)
    assert 'Bluetooth adapter was not found' in diag
    assert 'TOPIC 1 — Bluetooth adapter cannot be found' in solution
    assert 'When this applies: Adapter radio is switched off or blocked' in solution


def test_interrupted_scan_never_implies_all_checks_complete():
    plan, readings, focused = snapshot()
    readings.pop(plan.checks[-1])
    _,diag,_,_,_ = full_scan_pages(plan, readings, focused, CATEGORIES, stopped=True)
    assert 'did not return every scheduled result' in diag
    assert 'All scheduled local measurements completed' not in diag


def test_unlinked_supplementary_warning_shows_separate_next_step_without_repair():
    plan, readings, focused = snapshot()
    replace_probe(focused, 'critical_journal66', result('focused','critical_journal66',ResultStatus.WARNING,
                                     'Local warning','High priority messages observed'))
    readings.pop(('system','system_logs'))
    _,diag,solution,_,_=full_scan_pages(plan,readings,focused,CATEGORIES)
    assert 'High-priority messages from this boot — additional observation' in diag
    assert 'Many red errors in system journal' in solution
    assert 'When this applies: Specific named service/device error repeats at symptom time' in solution
    assert 'settings were changed' in solution or 'changed settings' in solution
