"""v128 release-marked Steam Manual Diagnostics, without new repair authority."""
from pathlib import Path
import ast
import pytest

from universal_linux_troubleshooter.diagnostics.case_navigation41 import navigation_groups
from universal_linux_troubleshooter.diagnostics.topic_catalog127 import (
    all_topics, matching_topics, guide_for_topic, CURRENT_GUIDE_VERSION,
)
from universal_linux_troubleshooter.diagnostics.manual_cases40 import case_catalog, plan_for_manual_case, present_case
from universal_linux_troubleshooter.diagnostics.steam_inventory128 import probe_steam_inventory128
from universal_linux_troubleshooter.diagnostics.focused_evidence import run_named_focused_checks, PROBES
from universal_linux_troubleshooter.results import ResultStatus
from universal_linux_troubleshooter.diagnostics.bridge import CommandOutput

ROOT = Path(__file__).resolve().parents[1]
STEAM = tuple(x for x in all_topics() if x.heading == 'Steam')


def test_steam_section_retains_complete_original_case_catalog_and_removes_duplicate_wallet_guide():
    assert len(STEAM) == 69
    assert len(all_topics()) == 18 + 56 + 69
    assert {t.introduced_version for t in STEAM} == {128}
    assert CURRENT_GUIDE_VERSION == 135  # v135 links full scan solutions to existing topics, no new guides
    assert all(t.introduced_version != CURRENT_GUIDE_VERSION for t in all_topics() if t.heading != 'Steam')
    assert not any(t.key == 'guide127_38' for t in all_topics())
    cases = case_catalog()
    assert 'software35.security.secret-store' in cases
    assert cases['software35.security.secret-store']['title'] == 'App repeatedly asks for password after login'
    assert sum(len(x['resolution_routes']) for x in cases.values()) == 500
    assert len(cases) == 250
    original = [cid for _, subjects in navigation_groups() for _, _, rows in subjects for cid, _ in rows]
    assert len(original) == len(set(original)) == 250
    assert any(domain == 'software' and heading == 'Steam'
               for domain, subjects in navigation_groups()
               for heading, _, _ in subjects)


@pytest.mark.parametrize('guide', STEAM, ids=lambda g:g.key)
def test_steam_guide_is_specific_english_searchable_and_does_not_authorize_repair(guide):
    assert guide.domain == 'software'
    assert guide.case_id in case_catalog()
    assert guide_for_topic(guide.key, guide.case_id) == guide
    assert guide in matching_topics(guide.title)
    assert any(heading == 'Steam' for _, subjects in navigation_groups(guide.title)
               for heading, _, _ in subjects)
    text = guide.describe()
    assert guide.title in text
    assert len(guide.comparison) >= 2
    assert 'WHAT TO TRY' in text and 'WHAT THE RESULTS MEAN' in text
    assert not any(token in text.casefold() for token in ('sudo ', 'rm -rf', 'chmod 777', 'mkfs.', 'curl ', 'wget '))
    checks, probes = plan_for_manual_case(guide.case_id)
    assert checks
    report = present_case(guide.case_id, [], completed=True, topic_id=guide.key)
    assert report.status == 'unknown' and report.proven_route is None


def test_new_release_marker_and_steam_probe_are_connected_only_to_selected_steam_topics():
    source = (ROOT/'universal_linux_troubleshooter/pages/manual.py').read_text()
    ast.parse(source)
    assert 'topic.introduced_version == CURRENT_GUIDE_VERSION' in source
    # The GUI must use the same immutable probe plan for execution and
    # completion accounting; hardcoded version-specific plans are fragile.
    assert 'planned_case_probes(case_id, topic_id)' in source
    assert 'scan_finished_as_planned(' in source
    assert 'steam_inventory128' not in PROBES  # don't change frozen manual baseline probe set


class FakeHost:
    def __init__(self, *, exists=(), names=(), registered=False, tools=True):
        self.known=set(map(str,exists))
        self.names=names
        self.registered=registered
        self.tools=tools
        self.commands=[]
    def exists(self,path): return path in self.known
    def list_names(self,path): return tuple(self.names)
    def command(self,argv):
        self.commands.append(argv)
        from universal_linux_troubleshooter.diagnostics.package_sources131 import SOURCES
        assert argv in SOURCES.values()  # All registered local package backends are reviewed.
        if not self.tools: return CommandOutput(127, '')
        if argv in (SOURCES['flatpak_user'], SOURCES['flatpak_system']):
            return CommandOutput(0, 'com.valvesoftware.Steam\n' if self.registered else '')
        return CommandOutput(127, '')  # Other backends not installed in this fixture


def test_steam_probe_only_observes_fixed_local_paths_and_never_opens_or_changes_steam():
    home=Path.home()
    h=FakeHost(exists=[home/'.local/share/Steam',home/'.local/share/Steam/steamapps'],names=['appmanifest_123.acf', 'appmanifest_x.acf','config.vdf'],registered=True)
    result=probe_steam_inventory128(h)
    assert result.status==ResultStatus.INFO
    assert 'FACT:steam_local_manifests=1' in result.evidence
    assert 'FACT:steam_flatpak_registration=observed' in result.evidence
    from universal_linux_troubleshooter.diagnostics.package_sources131 import SOURCES
    assert set(h.commands) == set(SOURCES.values())
    assert 'does not prove' in result.explanation.lower()
    h2=FakeHost(tools=False)
    result2=run_named_focused_checks(h2,('steam_inventory128',))
    assert result2[0].status==ResultStatus.UNKNOWN
    assert 'FACT:steam_flatpak_registration=unknown' in result2[0].evidence
    with pytest.raises(ValueError):
        run_named_focused_checks(h2,('not_an_approved_probe',))


def test_steam_scope_specific_searches():
    for query in ('proton','Steam Cloud','workshop','steam controller','steam deck', 'remote play','steam flatpak','Steam VR'):
        if query == 'steam deck':
            continue  # Not marketed as hardware-specific Steam Deck troubleshooting.
        assert any(x.heading == 'Steam' for x in matching_topics(query)), query

@pytest.mark.parametrize('guide', STEAM, ids=lambda t:t.key)
def test_steam_installation_is_not_diagnostic_proof(guide):
    observed = FakeHost(registered=True)
    inventory = probe_steam_inventory128(observed)
    result = present_case(guide.case_id,[inventory],completed=True,topic_id=guide.key)
    assert result.proven_route is None, guide.key
    assert result.status != 'supported', guide.key
