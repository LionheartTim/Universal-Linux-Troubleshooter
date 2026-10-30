"""v127: broad catalog additions without invented diagnosis routes.

The 57 additional entry points are guidance for the existing trees, NOT 57
extra validated diagnoses. They never grant command/repair authority.
"""
from pathlib import Path
import ast
import pytest

from universal_linux_troubleshooter.diagnostics.topic_catalog127 import (
    all_topics, BY_KEY, guide_for_topic, matching_topics,
)
from universal_linux_troubleshooter.diagnostics.case_navigation41 import (
    navigation_groups, SUBJECTS,
)
from universal_linux_troubleshooter.diagnostics.manual_cases40 import (
    case_catalog, plan_for_manual_case, present_case,
)
from universal_linux_troubleshooter.diagnostics.manual_tree_presentation90 import pages_for_case
from universal_linux_troubleshooter.diagnostics.readable_layout93 import html_for_manual93

ROOT = Path(__file__).resolve().parents[1]


def test_canonical_diagnoses_and_routes_preserved():
    cases = case_catalog()
    assert len(cases) == 250
    assert sum(len(c['resolution_routes']) for c in cases.values()) == 500
    assert len(all_topics()) == 143
    assert sum(t.key.startswith('guide127_') for t in all_topics()) == 56
    assert len(BY_KEY) == len(all_topics())
    assert not any(t.case_id not in cases for t in all_topics())
    assert all(not cases[t.case_id]['execute_commands'] for t in all_topics())


@pytest.mark.parametrize('topic', all_topics(), ids=lambda t: t.key)
def test_topic_is_reachable_english_and_non_executable(topic):
    case = case_catalog()[topic.case_id]
    assert topic.domain == case['domain']
    assert topic.heading in {heading for heading, *_ in SUBJECTS[topic.domain]}
    assert guide_for_topic(topic.key, topic.case_id) == topic
    text = topic.describe()
    assert topic.title in text
    assert all(heading in text for heading in ('BEFORE YOU START', 'WHAT TO TRY', 'WHAT THE RESULTS MEAN'))
    assert 'No changes' not in text or 'automatically' in text
    assert not any(cmd in text.casefold() for cmd in ('sudo ', 'rm -rf', 'mkfs.', 'curl ', 'wget ', 'chmod 777', 'format /'))
    assert 'geen' not in text.casefold() and 'controleer' not in text.casefold()
    assert topic in matching_topics(topic.title)
    groups = navigation_groups(topic.title)
    assert any(d == topic.domain and heading == topic.heading
               for d, sections in groups for heading, _, _ in sections)
    checks, _ = plan_for_manual_case(topic.case_id)
    assert checks


@pytest.mark.parametrize('topic', all_topics(), ids=lambda t: t.key)
def test_topic_does_not_authorize_a_repair(topic):
    report = present_case(topic.case_id, [], completed=True, topic_id=topic.key)
    assert report.proven_route is None
    assert report.status == 'unknown'
    assert 'A CLOSER LOOK AT YOUR PROBLEM' in report.solution
    assert topic.title in report.solution
    interrupted = present_case(topic.case_id, [], completed=False, topic_id=topic.key)
    assert interrupted.proven_route is None
    assert 'A CLOSER LOOK AT YOUR PROBLEM' not in interrupted.solution


def test_cross_case_injection_rejected():
    topic = all_topics()[-1]
    wrong = next(k for k in case_catalog() if k != topic.case_id)
    with pytest.raises(ValueError):
        guide_for_topic(topic.key, wrong)


@pytest.mark.parametrize('search,expect',[
    ('mouse wired', 'mouse_wired'),
    ('controller lights on', 'guide127_01'),
    ('printer blank pages', 'guide127_48'),
    ('screen sharing', 'guide127_32'),
    ('podman', 'guide127_45'),
    ('keyboard wireless', 'keyboard_wireless'),
])
def test_beginner_search_without_exact_punctuation(search, expect):
    assert expect in {t.key for t in matching_topics(search)}


def test_all_250_original_cases_still_visible_once_without_filter():
    listed = [cid for _, sections in navigation_groups() for _, _, rows in sections for cid, _ in rows]
    assert len(listed) == 250 and set(listed) == set(case_catalog())


def test_frontend_shows_selected_guide_before_and_after_scanning():
    source = (ROOT/'universal_linux_troubleshooter/pages/manual.py').read_text()
    ast.parse(source)
    assert 'guide_prefix + pages.check_info' in source
    assert 'guide_prefix + pages.solution' in source
    assert 'self._selected_topic_id' in source
    assert 'topic_catalog127 import matching_topics' in source
    assert 'self._run_case_id(case_id, topic_id=self._selected_topic_id)' in source
    assert 'AI Diagnostics' not in source


def test_english_manual_documentation_and_safe_rendering():
    for case_id in case_catalog():
        pages = pages_for_case(case_id)
        for value in (pages.check_info, pages.diagnosis, pages.solution):
            assert value and 'C:\\' not in value
            html = html_for_manual93(value)
            assert html.startswith('<html>')
    for topic in all_topics():
        html = html_for_manual93(topic.describe())
        assert '<html>' in html and 'WHAT TO TRY' in html
