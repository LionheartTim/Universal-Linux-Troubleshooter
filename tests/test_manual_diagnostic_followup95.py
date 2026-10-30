"""v95: actionable Diagnosis with official source references, no false proof."""
from pathlib import Path
import re
import pytest
from universal_linux_troubleshooter.diagnostics.manual_cases40 import case_catalog, present_case
from universal_linux_troubleshooter.diagnostics.manual_tree_presentation90 import pages_for_case
from universal_linux_troubleshooter.diagnostics.readable_layout93 import html_for_manual93

CASES = tuple(sorted(case_catalog()))
ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('case_id', CASES)
def test_all_250_diagnoses_offer_manual_tests_outcome_interpretation_and_sources(case_id):
    case = case_catalog()[case_id]
    page = pages_for_case(case_id)
    diagnosis = page.diagnosis
    assert 'CHECKS YOU CAN TRY' in diagnosis
    assert 'MANUAL TEST 1' in diagnosis
    assert 'HOW TO INTERPRET YOUR TESTS' in diagnosis
    assert 'WHAT THE RESULT CAN SHOW' in diagnosis
    assert 'WHAT IT DOES NOT PROVE' in diagnosis
    assert 'Compare the outcome with the possible causes' in diagnosis
    assert 'IF THE RESULT IS STILL UNCLEAR' in diagnosis
    assert 'REFERENCE URL' in diagnosis
    assert case['source_links'][0] in diagnosis
    assert 'UNKNOWN' in diagnosis
    assert 'COMMAND' in diagnosis
    assert 'RELEVANT TECHNICAL DOCUMENTATION' in diagnosis
    assert ('HARDWARE AND MANUFACTURER SUPPORT' in diagnosis) == (case['domain'] == 'hardware')
    assert ('APPLICATION / DISTRIBUTION SUPPORT' in diagnosis) == (case['domain'] == 'software')
    assert present_case(case_id, []).proven_route is None
    for ref in case['terminal_result_guides'][:2]:
        assert ref['command'] in diagnosis
        assert ref['interpretation'][:90] in diagnosis
        assert ref['cannot_prove'][:90] in diagnosis
    html = html_for_manual93(diagnosis)
    assert '<a href=' in html
    assert '<pre ' in html
    assert 'OFFICIAL DOCUMENTATION' in html


def test_gpu_reset_has_real_device_driver_and_log_tests_not_just_statuses():
    text = pages_for_case('hardware34.gpu.physical-reset').diagnosis
    assert 'lspci -nnk' in text
    assert 'journalctl -b -k --no-pager -n 240' in text
    assert 'HARDWARE AND MANUFACTURER SUPPORT' in text
    assert 'docs.kernel.org' in text
    assert 'do not infer a defect' in text.lower()


def test_gamepad_has_hardware_vendor_and_second_system_diagnostic_path():
    text = pages_for_case('hardware34.peripherals.gamepad-controller').diagnosis
    assert 'lsusb' in text
    assert 'bluetoothctl devices' in text
    assert 'another computer' in text
    assert 'official manufacturer support page' in text.lower()
    assert 'docs.kernel.org/input/input.html' in text


def test_formatter_does_not_link_non_https_or_embed_html():
    for bad in ('javascript:alert(1)', 'https://bad.example/" onclick="alert(1)',
                'https://evil.example/<b>x</b>', 'https://[invalid'):
        html = html_for_manual93('REFERENCE URL\n' + bad)
        assert '<a href=' not in html
        assert '<script' not in html
    html = html_for_manual93('REFERENCE URL\nhttps://docs.kernel.org/input/input.html')
    assert '<a href="https://docs.kernel.org/input/input.html"' in html


def test_gui_keeps_detailed_manual_tree_without_dumping_it_in_beginner_diagnosis():
    source = (ROOT/'universal_linux_troubleshooter/pages/manual.py').read_text()
    assert 'pages.diagnosis' not in source
    assert 'guide_prefix + pages.solution' in source
    assert 'self.evidence.setPlainText(display_case_report93' in source
    assert 'format_case_diagnosis130(' in source
    assert 'self.result_tabs.setCurrentIndex(1)' in source
    assert 'self._show_case_documentation(report)' in source
    assert 'LinksAccessibleByMouse' in source
    assert 'self._current_batch_results().values()' in source
