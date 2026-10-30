"""Full Manual catalog scan: cover all documented entries without invented diagnoses."""
from pathlib import Path
from collections import Counter

from universal_linux_troubleshooter.catalog import CATEGORIES
from universal_linux_troubleshooter.diagnostics import READY_CHECKS
from universal_linux_troubleshooter.diagnostics.plan import NETWORK_OPT_IN_CHECKS
from universal_linux_troubleshooter.diagnostics.full_catalog133 import (
    complete_catalog_plan, full_scan_pages, scan_catalog_coverage,
)
from universal_linux_troubleshooter.diagnostics.focused_evidence import PROBES, CHAT120_PROBES
from universal_linux_troubleshooter.diagnostics.manual_cases40 import (
    case_catalog, plan_for_manual_case,
)
from universal_linux_troubleshooter.diagnostics.topic_catalog127 import all_topics
from universal_linux_troubleshooter.results import DiagnosticResult, ResultStatus


def record(area, name, status=ResultStatus.OK, diagnosis='Local reading'):
    return DiagnosticResult(area, name, status, diagnosis,
                            'This is only an observation, not a proven cause.',
                            'No changes are made.', ())


def observations(plan, state=ResultStatus.INFO):
    return ({key: record(*key, state) for key in plan.checks},
            [record('focused', name, state) for name in plan.probes])


def test_all_250_cases_and_143_guides_are_included():
    plan = complete_catalog_plan(READY_CHECKS)
    assert plan.cases == len(case_catalog()) == 250
    assert plan.guides == len(all_topics()) == 143
    assert len(plan.checks) == 28
    assert len(plan.probes) == 44
    assert len(set(plan.checks)) == len(plan.checks)
    assert len(set(plan.probes)) == len(plan.probes)
    assert set(plan.probes) <= set(PROBES) | set(CHAT120_PROBES)
    for case_id in case_catalog():
        checks, focused = plan_for_manual_case(case_id)
        assert set(checks) <= set(plan.checks)
        assert set(focused) <= set(plan.probes)
    for guide in all_topics():
        assert guide.case_id in case_catalog()


def test_optional_network_never_run_by_default():
    offline = complete_catalog_plan(READY_CHECKS)
    online = complete_catalog_plan(READY_CHECKS, include_network=True)
    assert not NETWORK_OPT_IN_CHECKS.intersection(offline.checks)
    assert NETWORK_OPT_IN_CHECKS <= set(online.checks)
    assert len(online.checks) == len(offline.checks) + 2
    assert online.probes == offline.probes
    assert complete_catalog_plan(READY_CHECKS) == offline


def test_no_false_fault_for_every_case_on_informational_readings():
    plan = complete_catalog_plan(READY_CHECKS)
    readings, focused = observations(plan)
    info, diag, solution, logs, coverage = full_scan_pages(plan, readings, focused, CATEGORIES)
    assert coverage['total_cases'] == 250
    assert coverage['total_guides'] == 143
    assert sum(coverage[key] for key in ('signals','specific','general','unknown','missing')) == 250
    assert 'All scheduled local measurements completed' in diag
    assert '250 documented problems' in info
    assert 'not proven causes' in diag
    assert 'No settings were changed' in solution
    assert 'Catalog coverage' in logs
    assert 'not verified' in coverage['text']
    assert '250 failures' not in diag
    assert 'confirmed cause' not in diag.lower()


def test_inconclusive_and_missing_results_never_claim_completed():
    plan = complete_catalog_plan(READY_CHECKS)
    info, diag, solution, logs, coverage = full_scan_pages(plan, {}, [], CATEGORIES)
    assert 'did not return every scheduled result' in diag
    assert coverage['missing'] + coverage['unknown'] == 250
    assert 'Not measured' in logs
    readings, focused = observations(plan, ResultStatus.UNKNOWN)
    coverage = scan_catalog_coverage(plan, readings, focused)
    assert coverage['unknown'] == 250
    assert coverage['specific'] == 0
    assert coverage['signals'] == 0
    assert coverage['general'] == 0


def test_specific_warning_is_only_an_observation_and_full_details_separate():
    plan = complete_catalog_plan(READY_CHECKS)
    readings, focused = observations(plan)
    readings[('applications','app_crashes')] = record('applications','app_crashes',ResultStatus.WARNING,'Six old crash reports')
    focused[0] = record('focused', plan.probes[0], ResultStatus.WARNING, 'Automatische aanvullende feitencontrole')
    info,diag,solution,logs,_ = full_scan_pages(plan, readings, focused, CATEGORIES)
    assert 'Six old crash reports' in diag
    assert 'not proven causes' in diag
    assert 'Six old crash reports' in logs
    assert 'Automatische aanvullende feitencontrole' in logs
    assert 'Automatische aanvullende feitencontrole' not in diag
    assert len(diag) < 7000
    assert 'Application crashes' in solution
    assert 'Six old crash reports' in diag


def test_real_worker_and_gui_wiring_reuses_one_shared_plan():
    root=Path(__file__).resolve().parents[1]/'universal_linux_troubleshooter'
    source=(root/'pages/manual.py').read_text()
    worker=(root/'diagnostics/worker.py').read_text()
    assert 'complete_catalog_plan(READY_CHECKS' in source
    assert 'focused_probes = self._full_catalog_plan.probes' in source
    assert 'if (case_id or complete) else self.present_result' in source
    assert 'f"Complete system scan: {self._run_total} local checks"' in source
    assert '"Catalog coverage · all problems"' in source
    assert 'for index, probe_key in enumerate(self._focused_probes' in worker
    assert 'run_named_focused_checks(bridge.host, (probe_key,))' in worker
    assert 'self.isInterruptionRequested()' in worker


def test_diagnostic_guide_version_markers_do_not_reappear():
    from universal_linux_troubleshooter.diagnostics.topic_catalog127 import CURRENT_GUIDE_VERSION
    assert CURRENT_GUIDE_VERSION == 135
    assert all(guide.introduced_version != CURRENT_GUIDE_VERSION for guide in all_topics())


def test_reviewed_local_event_is_not_misreported_as_confirmed_user_failure():
    plan = complete_catalog_plan(READY_CHECKS)
    readings, probes = observations(plan)
    for i, row in enumerate(probes):
        if row.check_key == 'radio_blocks':
            probes[i] = DiagnosticResult('focused', 'radio_blocks', ResultStatus.INFO,
                                        'Local radio status', 'Observed locally',
                                        'No automatic changes.', ('FACT:wifi=blocked',))
    coverage = scan_catalog_coverage(plan, readings, probes)
    assert coverage['signals'] >= 1
    assert any('Wi-Fi' in title or 'WiFi' in title for title in coverage['signal_titles'])
    assert 'Reviewed local indicator detected; effect not confirmed' in coverage['text']
    _, diag, _, _, _ = full_scan_pages(plan, readings, probes, CATEGORIES)
    assert 'does not establish an active user problem' in diag
