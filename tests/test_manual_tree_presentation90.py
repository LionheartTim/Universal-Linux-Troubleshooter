"""v90: Manual Diagnostics displays the complete case tree, without executing it."""
from pathlib import Path
import pytest
from universal_linux_troubleshooter.diagnostics.manual_cases40 import case_catalog, present_case
from universal_linux_troubleshooter.diagnostics.manual_tree_presentation90 import pages_for_case, ULT, ULSM

CASES = tuple(sorted(case_catalog()))
ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('case_id', CASES)
def test_every_case_has_three_full_pages_and_both_conditional_paths(case_id):
    doc = case_catalog()[case_id]
    pages = pages_for_case(case_id)
    assert doc['symptom'] in pages.check_info
    assert 'WHAT IS CHECKED' in pages.check_info
    assert 'POSSIBLE CAUSES' in pages.diagnosis
    assert 'USER-RUN TERMINAL TESTS' in pages.solution
    assert 'AFTER EACH ACTION' in pages.solution
    assert 'NEVER EXECUTED' in pages.solution
    assert ULT in pages.solution
    for index, route in enumerate(doc['resolution_routes'], 1):
        assert route['applicability_condition'] in pages.diagnosis
        assert f'PATH {index} — WHEN THIS APPLIES' in pages.solution
        assert route['verification_goal'][:110] in pages.solution
        for step in route['user_steps']:
            # Whitespace may be normalized for QLabel compatibility.
            assert ' '.join(step.split())[:110] in pages.solution
    assert pages.offers_ulsm == any('optional_package_gui85' in r for r in doc['resolution_routes'])
    assert (ULSM in pages.solution) == pages.offers_ulsm
    # The manual guide is not a source of accepted evidence or gates.
    assert present_case(case_id, []).proven_route is None


@pytest.mark.parametrize('case_id', CASES)
def test_all_documented_terminal_interpretations_are_visible(case_id):
    doc = case_catalog()[case_id]
    pages = pages_for_case(case_id)
    for command in doc['terminal_result_guides']:
        assert command['command'] in pages.solution
        assert command['cannot_prove'][:100] in pages.solution
        assert command['interpretation'][:100] in pages.solution
    assert 'repair' in pages.solution.lower() or 'oploss' in pages.solution.lower() or 'action' in pages.solution.lower()


def test_gamepad_hardware_and_application_paths_are_specific():
    text = pages_for_case('peripherals.gamepad-not-detected')
    assert 'lsusb' in text.solution
    assert '/proc/bus/input/devices' in text.solution
    assert 'Controller absent on connection' in text.diagnosis
    assert 'Controller enumerates but one game ignores it' in text.diagnosis
    assert 'different' in text.solution.lower() or 'another' in text.solution.lower()
    assert not text.offers_ulsm


def test_package_route_has_optional_gui_but_no_fw_or_os_image_promise():
    text = pages_for_case('applications.app-crash')
    assert text.offers_ulsm
    assert ULSM in text.solution
    assert 'Flatpak' in text.solution
    assert 'rpm-ostree' in text.solution


def test_wrong_case_is_not_silently_guessed():
    with pytest.raises(KeyError):
        pages_for_case('not-a-diagnosis')


def test_qt_manual_page_wires_selection_and_scan_to_read_only_tree_pages():
    src = (ROOT / 'universal_linux_troubleshooter/pages/manual.py').read_text()
    assert 'def _show_case_documentation(self, report=None):' in src
    assert 'self._show_case_documentation(report)' in src
    assert 'self._show_case_documentation()' in src
    assert 'setOpenExternalLinks(True)' in src
    assert 'pages_for_case(case_id)' in src
    assert 'self.evidence.setPlainText(report.evidence)' in src
