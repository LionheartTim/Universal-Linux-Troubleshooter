"""v96: no arbitrary cap on necessary self-guided tests or official sources."""
from copy import deepcopy

import pytest

from universal_linux_troubleshooter.diagnostics.manual_cases40 import case_catalog
from universal_linux_troubleshooter.diagnostics import manual_tree_presentation90 as presenter
from universal_linux_troubleshooter.diagnostics.readable_layout93 import html_for_manual93

CASES = tuple(sorted(case_catalog()))


@pytest.mark.parametrize('case_id', CASES)
def test_every_documented_terminal_test_is_visible_once_and_in_order(case_id):
    case = case_catalog()[case_id]
    diagnosis = presenter.pages_for_case(case_id).diagnosis
    solution = presenter.pages_for_case(case_id).solution
    commands = [row['command'] for row in case['terminal_result_guides']]
    # Commands appear individually in the page, not merely as one pasted prose block.
    lines = diagnosis.splitlines()
    command_values = [lines[i + 2] if i + 2 < len(lines) and lines[i + 2] else lines[i + 3]
                      for i, line in enumerate(lines[:-3])
                      if line == 'COMMAND' and lines[i + 1] == '']
    assert command_values == commands
    assert diagnosis.count('WHAT THE RESULT CAN SHOW') == len(commands)
    assert diagnosis.count('WHAT IT DOES NOT PROVE') == len(commands)
    assert diagnosis.count('MANUAL TEST ') == len(commands) + len(
        case.get('supplemental_investigation_steps83') or
        [step for step in case['manual_investigation_guide84']['steps']
         if step.get('phase') == 'independent_comparison'])
    for row in case['terminal_result_guides']:
        assert row['interpretation'] in diagnosis
        assert row['cannot_prove'] in diagnosis
        for precaution in row.get('precautions', ()):
            assert precaution in diagnosis or precaution[:380] in diagnosis
    assert solution.count('TERMINAL TEST ') == len(commands)
    assert html_for_manual93(diagnosis).count('<pre ') == len(commands)


@pytest.mark.parametrize('case_id', CASES)
def test_all_curated_comparisons_and_official_links_remain_visible(case_id):
    case = case_catalog()[case_id]
    diagnosis = presenter.pages_for_case(case_id).diagnosis
    for text in case.get('supplemental_investigation_steps83', ()):
        assert text in diagnosis
    for url in case.get('source_links', ()):
        if url.startswith('https://'):
            assert url in diagnosis


def test_real_four_command_case_and_six_comparison_case():
    four = presenter.pages_for_case('graphics.game-stutter').diagnosis
    assert four.count('COMMAND\n\n') == 4
    six_case = case_catalog()['peripherals.gamepad-not-detected']
    assert len(six_case['supplemental_investigation_steps83']) == 6
    diagnosis = presenter.pages_for_case('peripherals.gamepad-not-detected').diagnosis
    for item in six_case['supplemental_investigation_steps83']:
        assert item in diagnosis


def test_synthetic_six_plus_commands_and_supplemental_steps_not_truncated(monkeypatch):
    case_id = 'hardware34.gpu.physical-reset'
    replacement = deepcopy(case_catalog()[case_id])
    original = replacement['terminal_result_guides'][0]
    replacement['terminal_result_guides'] = [
        {**original, 'command': f'example-read-only-diagnostic-{i}',
         'purpose': f'Inspect component {i}',
         'interpretation': f'Observed component {i}',
         'cannot_prove': f'Does not prove fault {i}'}
        for i in range(1, 8)
    ]
    replacement['supplemental_investigation_steps83'] = [
        f'Compare relevant independent component {i}.' for i in range(1, 7)]
    replacement['source_links'] = [f'https://docs.kernel.org/example/{i}' for i in range(1, 5)]
    original_catalog = presenter.case_catalog
    monkeypatch.setattr(presenter, 'case_catalog', lambda: {**original_catalog(), case_id: replacement})
    page = presenter.pages_for_case(case_id)
    assert page.diagnosis.count('COMMAND\n\n') == 7
    assert page.diagnosis.count('MANUAL TEST ') == 13
    for i in range(1, 8):
        assert f'example-read-only-diagnostic-{i}' in page.diagnosis
    for i in range(1, 7):
        assert f'Compare relevant independent component {i}.' in page.diagnosis
    for i in range(1, 5):
        assert f'https://docs.kernel.org/example/{i}' in page.diagnosis
    assert html_for_manual93(page.diagnosis).count('<pre ') == 7
