"""v135: authentic case-source solutions, per-topic presentation and safety."""
from universal_linux_troubleshooter.catalog import CATEGORIES
from universal_linux_troubleshooter.diagnostics import READY_CHECKS
from universal_linux_troubleshooter.diagnostics.full_catalog133 import complete_catalog_plan, full_scan_pages
from universal_linux_troubleshooter.diagnostics.full_scan_topic_solutions135 import (
    CHECK_TOPIC, PROBE_TOPIC, _unambiguous_probe_topics, make_topic_solutions,
)
from universal_linux_troubleshooter.diagnostics.manual_cases40 import case_catalog
from universal_linux_troubleshooter.diagnostics.readable_layout93 import html_for_manual93
from universal_linux_troubleshooter.results import DiagnosticResult, ResultStatus


def result(pair, status=ResultStatus.OK, diagnosis='Available', explanation='Local observation only.',
           solution='Never run random repair commands.', evidence=()):
    return DiagnosticResult(pair[0], pair[1], status, diagnosis, explanation, solution, evidence)


def snapshot():
    plan = complete_catalog_plan(READY_CHECKS)
    readings = {key: result(key) for key in plan.checks}
    focused = [result(('focused', key), ResultStatus.INFO) for key in plan.probes]
    return plan, readings, focused


def pages(readings, focused):
    plan = complete_catalog_plan(READY_CHECKS)
    return full_scan_pages(plan, readings, focused, CATEGORIES)


def test_specific_base_checks_have_existing_topics_and_ambiguous_remain_unmapped():
    plan = complete_catalog_plan(READY_CHECKS)
    assert len(plan.checks) == 28
    assert set(CHECK_TOPIC).issubset(set(plan.checks))
    assert set(plan.checks) - set(CHECK_TOPIC) == {('hardware', 'power'), ('hardware', 'hardware_logs')}
    catalog = case_catalog()
    assert set(CHECK_TOPIC.values()) <= set(catalog)
    assert set(PROBE_TOPIC.values()) <= set(catalog)


def test_every_base_warning_uses_a_known_topic_not_scan_generic():
    plan, readings, focused = snapshot()
    for key in CHECK_TOPIC:
        changed = dict(readings)
        changed[key] = result(key, ResultStatus.WARNING, 'A relevant local observation',
                              solution='DO-NOT-RENDER-RAW-FIX')
        _, diagnosis, solution, _, _ = pages(changed, focused)
        assert 'TOPIC 1 — ' + case_catalog()[CHECK_TOPIC[key]]['title'] in solution, key
        assert 'CHECK THIS FIRST' in solution
        assert 'PATH 1 — ' in solution
        assert 'When this applies:' in solution
        assert 'Verify afterward:' in solution
        assert 'Do not apply this path unless' in solution or 'REVIEWED LOCAL EVIDENCE' in solution
        assert 'DO-NOT-RENDER-RAW-FIX' not in solution
        assert 'A relevant local observation' in diagnosis


def test_multiple_topics_separated_and_provenance_comes_from_original_cases():
    plan, readings, focused = snapshot()
    readings[('applications', 'app_crashes')] = result(('applications', 'app_crashes'),
        ResultStatus.WARNING, 'Saved crash records for 2 programs',
        '1. /usr/bin/firefox (2 saved reports)\n2. /usr/bin/example (1 saved report)')
    readings[('system', 'system_logs')] = result(('system', 'system_logs'),
        ResultStatus.WARNING, '80 important messages')
    focused = [result(('focused', x.check_key), ResultStatus.WARNING, 'Boot timing observed')
               if x.check_key == 'slow_boot66' else x for x in focused]
    _, diagnosis, solution, _, _ = pages(readings, focused)
    assert solution.count('TOPIC ') == 3
    assert solution.count('CHECK THIS FIRST') == 3
    assert solution.count('POSSIBLE SOLUTIONS FROM THIS TOPIC') == 3
    assert solution.index('Application closes unexpectedly') < solution.index('Many red errors in system journal')
    assert 'Computer boots slowly' in solution
    assert '/usr/bin/firefox' in solution
    assert 'Reproduce the crash with the exact application/version' in solution
    assert 'Separate unrelated historical warnings' in solution
    assert 'Boot timing observation' in diagnosis
    html = html_for_manual93(solution)
    assert html.count('<hr') >= 3
    assert 'TOPIC 1' in html and 'TOPIC 2' in html and 'TOPIC 3' in html


def test_unrelated_solution_and_unsafe_raw_reading_never_copied():
    _, readings, focused = snapshot()
    readings[('audio', 'bluetooth')] = result(('audio', 'bluetooth'), ResultStatus.WARNING,
        'Local Bluetooth inventory missing expected adapter',
        solution='REMOVE ALL SYSTEM SECURITY NOW')
    _, _, solution, logs, _ = pages(readings, focused)
    assert 'Bluetooth adapter cannot be found' in solution
    assert 'Adapter radio is switched off or blocked' in solution
    assert 'REMOVE ALL SYSTEM SECURITY NOW' not in solution
    assert 'REMOVE ALL SYSTEM SECURITY NOW' in logs
    assert 'Application closes unexpectedly' not in solution


def test_unknown_disk_health_stays_uncertain_not_drive_failure():
    _, readings, focused = snapshot()
    readings[('storage', 'health')] = result(('storage', 'health'), ResultStatus.UNKNOWN,
                                            'SMART status could not be read')
    _, diagnosis, solution, _, _ = pages(readings, focused)
    assert 'SMART status could not be read' in diagnosis
    assert 'MEASUREMENTS NEEDING MORE INFORMATION' in solution
    assert 'do not prove that a device is healthy or defective' in solution
    assert 'Back up important data now' not in solution


def test_duplicate_related_journal_readings_not_independent_repairs():
    _, readings, focused = snapshot()
    readings[('system', 'system_logs')] = result(('system', 'system_logs'),
                                                 ResultStatus.WARNING, 'Some warnings')
    focused = [result(('focused', x.check_key), ResultStatus.WARNING, 'Same journal event')
               if x.check_key == 'critical_journal66' else x for x in focused]
    _, _, solution, _, _ = pages(readings, focused)
    assert solution.count('TOPIC 1') == 1
    assert solution.count('TOPIC 2') == 0
    assert 'Many red errors in system journal' in solution


def test_unique_probe_uses_its_existing_case_not_unrelated_broad_logs():
    _, readings, focused = snapshot()
    focused = [result(('focused', x.check_key), ResultStatus.WARNING,
                      'Arch dependency event') if x.check_key == 'arch_orphans65' else x
               for x in focused]
    _, _, solution, _, _ = pages(readings, focused)
    cid = _unambiguous_probe_topics()['arch_orphans65']
    assert case_catalog()[cid]['title'] in solution
    assert 'When this applies:' in solution


def test_ambiguous_probe_does_not_invent_a_single_topic():
    _, readings, focused = snapshot()
    focused = [result(('focused', x.check_key), ResultStatus.WARNING,
                      'A generic event') if x.check_key == 'kernel_events50' else x
               for x in focused]
    _, _, solution, _, _ = pages(readings, focused)
    assert 'SUPPLEMENTARY WARNINGS WITHOUT ONE MATCHING TOPIC' in solution
    assert 'kernel_events50' in solution
    assert 'PATH 1' not in solution


def test_no_warnings_never_claims_repair():
    _, readings, focused = snapshot()
    _, _, solution, _, _ = pages(readings, focused)
    assert 'No repair is suggested' in solution
    assert 'TOPIC 1' not in solution


def test_250_case_plans_and_existing_routes_untouched():
    assert len(case_catalog()) == 250
    assert sum(len(c['resolution_routes']) for c in case_catalog().values()) == 500
    assert all(c['resolution_routes'][0]['user_steps'] for c in case_catalog().values())


def test_html_escapes_hostile_readings():
    _, readings, focused = snapshot()
    readings[('applications', 'app_crashes')] = result(('applications', 'app_crashes'),
        ResultStatus.WARNING, '<script>alert(1)</script> unexpected crash')
    _, _, solution, _, _ = pages(readings, focused)
    html = html_for_manual93(solution)
    assert '<script>' not in html
    assert '&lt;script&gt;' in html


def test_ambiguous_power_warning_not_treated_as_battery_fault():
    _, readings, focused = snapshot()
    readings[('hardware', 'power')] = result(('hardware', 'power'), ResultStatus.WARNING,
                                             'Suspend log mentioned an event')
    _, _, solution, _, _ = pages(readings, focused)
    assert 'SUPPLEMENTARY WARNINGS WITHOUT ONE MATCHING TOPIC' in solution
    assert 'Laptop battery is not charging' not in solution
    assert 'Suspend log mentioned an event' in solution


def test_two_warnings_same_topic_keep_both_observations_without_duplicate_paths():
    _, readings, focused = snapshot()
    readings[('audio', 'audio_devices')] = result(('audio', 'audio_devices'),
                                                   ResultStatus.WARNING, 'Speaker endpoint missing')
    readings[('audio', 'audio_services')] = result(('audio', 'audio_services'),
                                                    ResultStatus.WARNING, 'PipeWire user session warning')
    _, _, solution, _, _ = pages(readings, focused)
    assert solution.count('TOPIC ') == 1
    assert solution.count('POSSIBLE SOLUTIONS FROM THIS TOPIC') == 1
    assert 'Speaker endpoint missing' in solution
    assert 'PipeWire user session warning' in solution
