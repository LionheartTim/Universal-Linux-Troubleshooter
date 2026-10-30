"""v94: reproduce the v93 UI crash without requiring a Qt display or PySide6.

These tests compile the *actual* ManualDiagnosticsPage methods, then run them
with minimal UI sinks. This tests the code path that formerly passed a dict's
(category, check) tuple keys to the v93 English result renderer.
"""
from __future__ import annotations

import ast
from pathlib import Path
from types import MethodType, SimpleNamespace

import pytest

from universal_linux_troubleshooter.diagnostics.manual_cases40 import plan_for_manual_case, present_case, case_catalog
from universal_linux_troubleshooter.diagnostics.manual_tree_presentation90 import pages_for_case, ULSM, ULT
from universal_linux_troubleshooter.diagnostics.presentation_english93 import display_case_report93
from universal_linux_troubleshooter.diagnostics.diagnosis_display130 import format_case_diagnosis130
from universal_linux_troubleshooter.diagnostics.readable_layout93 import html_for_manual93
from universal_linux_troubleshooter.results import DiagnosticResult, ResultStatus


SRC = Path(__file__).resolve().parents[1] / 'universal_linux_troubleshooter/pages/manual.py'


class Sink:
    def __init__(self):
        self.text = ''
        self.properties = {}
        self.index = 0
        self.items = []

    def setText(self, value): self.text = value
    def setPlainText(self, value): self.text = value
    def toPlainText(self): return self.text
    def setProperty(self, name, value): self.properties[name] = value
    def style(self): return self
    def unpolish(self, _widget): pass
    def polish(self, _widget): pass
    def setCurrentIndex(self, index): self.index = index
    def currentIndex(self): return self.index
    def verticalScrollBar(self): return self
    def setValue(self, _value): pass
    def clear(self): self.items.clear()
    def addItem(self, title, case_id): self.items.append((title, case_id))
    def setVisible(self, visible): self.visible = visible
    def show(self): self.visible = True
    def hide(self): self.visible = False


def _compile_real_method(name):
    source = ast.parse(SRC.read_text(encoding='utf-8'))
    klass = next(x for x in source.body if isinstance(x, ast.ClassDef) and x.name == 'ManualDiagnosticsPage')
    method = next(x for x in klass.body if isinstance(x, ast.FunctionDef) and x.name == name)
    ns = dict(
        pages_for_case=pages_for_case, case_catalog=case_catalog,
        display_case_report93=display_case_report93, html_for_manual93=html_for_manual93,
        format_case_diagnosis130=format_case_diagnosis130,
        ULSM=ULSM, ULT=ULT, present_case=present_case,
    )
    module = ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[]))
    exec(compile(module, str(SRC), 'exec'), ns)
    return ns[name]


def _fake_page(case_id, results):
    fields = ('info_title', 'info_purpose', 'info_detail', 'diagnosis_title',
              'diagnosis_summary', 'diagnosis_explanation', 'solution_title',
              'solution_text', 'evidence', 'manual_tool_links', 'result_badge',
              'related_cases', 'related_button', 'result_tabs',
              'diagnosis_page', 'solution_page')
    page = SimpleNamespace(**{name: Sink() for name in fields})
    page._selected_case_id = case_id
    page._active_case_id = case_id
    page._last_batch = tuple((r.category_key, r.check_key) for r in results)
    page._results = {(r.category_key, r.check_key): r for r in results}
    page._case_probe_results = []
    page._case_scan_completed = True
    page._active_topic_id = None
    page._active_target_note = None
    page._target_inventory_result = None
    page._guided_result74 = None
    page._network_result75 = None
    page._case_view = None
    page._current_batch_results = lambda: {pair: page._results[pair]
                                            for pair in page._last_batch if pair in page._results}
    page._show_case_documentation = MethodType(_compile_real_method('_show_case_documentation'), page)
    page._show_case_result = MethodType(_compile_real_method('_show_case_result'), page)
    return page


@pytest.mark.parametrize('case_id', ['graphics.gpu-crash', 'hardware34.gpu.physical-reset',
                                     'audio.mic-not-working', 'network.wifi-missing'])
def test_single_investigation_populates_all_four_tabs_and_selects_diagnosis(case_id):
    checks, probes = plan_for_manual_case(case_id)
    assert checks
    local_results = [DiagnosticResult(c, k, ResultStatus.INFO, 'Observed', 'Read-only data',
                                      'No repair authorized', ('device enumerated',))
                     for c, k in checks]
    page = _fake_page(case_id, local_results)
    if probes:
        page._case_probe_results = [DiagnosticResult('focused', p, ResultStatus.UNKNOWN,
                                    'Insufficient evidence', 'No matching event',
                                    'Do not guess a repair') for p in probes]
    # The actual scan completion callback invokes this method once.
    # In v93 it raised AttributeError on (category, check) tuple keys.
    page._show_case_result()
    assert page.result_tabs.index == 1  # Automatically show Diagnosis
    assert 'WHAT THE CHECKS FOUND' in page.diagnosis_summary.text
    assert 'CONCLUSION' in page.diagnosis_summary.text
    assert 'CURRENT ASSESSMENT' not in page.diagnosis_summary.text
    assert 'DOCUMENTED POSSIBILITIES' not in page.diagnosis_summary.text
    assert 'STEP-BY-STEP TROUBLESHOOTING' in page.solution_text.text
    assert 'USER-RUN TERMINAL TESTS' in page.solution_text.text
    assert 'READ-ONLY DIAGNOSTIC EVIDENCE' in page.evidence.text
    assert case_id in page.evidence.text
    assert case_catalog()[case_id]['title'] == page.info_title.text
    assert page._case_view is not None
    # The user can switch freely: no further scan or GUI update is required.
    for tab in (2, 3, 0, 1):
        page.result_tabs.setCurrentIndex(tab)
        assert page.result_tabs.currentIndex() == tab
        assert page.solution_text.text and page.evidence.text


@pytest.mark.parametrize('case_id', ['graphics.gpu-crash', 'audio.mic-not-working'])
def test_empty_scan_keeps_all_tabs_available_without_fake_evidence(case_id):
    page = _fake_page(case_id, [])
    page._show_case_result()
    assert page.result_tabs.currentIndex() == 1
    assert 'No matching local check results were available.' in page.diagnosis_summary.text
    assert 'NO REPAIR HAS BEEN CONFIRMED' not in page.solution_text.text
    assert 'STEP-BY-STEP TROUBLESHOOTING' in page.solution_text.text


def test_renderer_rejects_accidental_tuple_keys_and_does_not_promote_to_evidence():
    case_id = 'graphics.gpu-crash'
    checks, _ = plan_for_manual_case(case_id)
    report = present_case(case_id, [], completed=True)
    diagnosis, solution, evidence = display_case_report93(case_id, report, list(checks))
    assert 'Unavailable' in evidence
    assert 'No conclusive' in diagnosis
    assert 'NO REPAIR HAS BEEN CONFIRMED' in solution
    assert 'device enumerated' not in evidence


def test_scan_completed_still_calls_case_result_to_select_diagnosis():
    source = SRC.read_text(encoding='utf-8')
    block = source.split('    def _scan_completed(self):', 1)[1].split('    def _setup_batch_selector', 1)[0]
    assert 'if self._active_case_id:\n            self._show_case_result()' in block
    report_block = source.split('    def _show_case_result(self):', 1)[1].split('    def _copy_active_tab', 1)[0]
    assert report_block.index('self._show_case_documentation(report)') < report_block.index('self.result_tabs.setCurrentIndex(1)')
    assert '[*self._current_batch_results().values(), *self._case_probe_results]' in source
