"""System-wide package-backend regression: scope, provenance, failure and privacy."""
from __future__ import annotations
from pathlib import Path
import json
import pytest

from universal_linux_troubleshooter.diagnostics.bridge import CommandOutput, LocalHost
from universal_linux_troubleshooter.diagnostics.package_sources131 import (
    SOURCES, inspect_sources, public_summary, valid_summary, package_relevance, description)
from universal_linux_troubleshooter.diagnostics.steam_inventory128 import probe_steam_inventory128
from universal_linux_troubleshooter.diagnostics.manual_cases40 import case_catalog, present_case
from universal_linux_troubleshooter.diagnostics.diagnosis_display130 import format_case_diagnosis130
from universal_linux_troubleshooter.results import ResultStatus
from universal_linux_troubleshooter.system_profile119 import SystemProfile, LOCAL_PLAN, WATCH_PATHS

class FakeHost:
    def __init__(self, by_source=None):
        self.outputs = by_source or {}
        self.calls = []
    def command(self, args):
        assert args in SOURCES.values()  # allowlist; not an arbitrary string
        self.calls.append(args)
        source = next(k for k, v in SOURCES.items() if args == v)
        return self.outputs.get(source, CommandOutput(127, ''))
    def exists(self, path): return False
    def list_names(self, path): return ()

@pytest.mark.parametrize('source,listing', [
    ('rpm', 'steam\nfedora-release\n'),
    ('deb', 'steam\tinstall ok installed\nsteam-installer\tdeinstall ok config-files\n'),
    ('pacman', 'steam\nlinux\n'),
    ('snap', 'Name Version Rev Tracking Publisher Notes\nsteam 1.0 1 stable canonical -\n'),
    ('apk', 'steam\nbusybox\n'),
    ('xbps', 'ii steam-1.0_1 The client\nii some-other-2.2_1 Another\n'),
    ('flatpak_user', 'com.valvesoftware.Steam\n'),
    ('flatpak_system', 'com.valvesoftware.Steam\n'),
])
def test_native_and_flatpak_installations_are_detected_separately(source, listing):
    values = inspect_sources(FakeHost({source: CommandOutput(0, listing)}), application='steam')
    assert values[source].presence == 'found', source
    assert values[source].state == 'checked'
    assert all(x.presence != 'not_found' for k,x in values.items() if k != source)


def test_steam_not_confused_with_dev_tools_or_not_installed_dpkg_record():
    vals = inspect_sources(FakeHost({
        'rpm': CommandOutput(0, 'steam-devices\n'),
        'deb': CommandOutput(0, 'steam\tdeinstall ok config-files\n'),
        'pacman': CommandOutput(0, 'steam-devices\n'),
    }), application='steam')
    assert all(vals[x].presence == 'not_found' for x in ('rpm','deb','pacman'))


def test_mixed_sources_and_atomic_ostree_are_not_conflated():
    vals = inspect_sources(FakeHost({
        'flatpak_user': CommandOutput(0, 'com.valvesoftware.Steam\n'),
        'rpm': CommandOutput(0, 'steam\n'),
        'rpm_ostree': CommandOutput(0, json.dumps({'deployments': [{'booted': True}]})),
    }), application='steam')
    assert vals['rpm'].presence == vals['flatpak_user'].presence == 'found'
    assert vals['rpm_ostree'].state == 'checked'
    assert vals['rpm_ostree'].presence == 'unknown'
    assert vals['rpm_ostree'].count == 1


@pytest.mark.parametrize('broken', [CommandOutput(124, ''), CommandOutput(1, ''),
                                    CommandOutput(0, 'steam\n', truncated=True),
                                    CommandOutput(0, 'steam\n' * 40000)])
def test_failed_or_truncated_database_never_proves_package_absent(broken):
    vals = inspect_sources(FakeHost({'rpm': broken}), application='steam')
    assert vals['rpm'].state == vals['rpm'].presence == 'unknown'


def test_all_commands_are_fixed_bounded_read_only_without_online_queries():
    h = FakeHost()
    inspect_sources(h)
    assert len(h.calls) == len(SOURCES)
    assert len(set(h.calls)) == len(SOURCES)
    for argv in h.calls:
        assert all('sudo' not in word and 'install' not in word and 'refresh' not in word
                   and 'https://' not in word for word in argv)
        assert argv[0] not in ('curl', 'wget', 'sh', 'bash', 'pkexec')
    with pytest.raises(ValueError):
        inspect_sources(h, application='arbitrary-command')


def test_profile_persists_only_source_statuses_and_counts(tmp_path):
    summary = public_summary(inspect_sources(FakeHost({'rpm': CommandOutput(0, 'private-package\n')})))
    profile = SystemProfile(tmp_path/'profile.json', signature_source=lambda: {k:'x' for k in WATCH_PATHS})
    profile.update([], packages=summary)
    text = (tmp_path/'profile.json').read_text()
    assert 'private-package' not in text
    assert 'rpm' in text
    assert profile.data['packages']['rpm']['status'] == 'checked'
    assert valid_summary(profile.data['packages'])
    assert not valid_summary({'rpm': {'status': 'installed', 'count': 3}})
    assert not valid_summary({'extra_command': {'status': 'checked', 'count': 1}})
    profile2 = SystemProfile(profile.path, signature_source=lambda: {k:'x' for k in WATCH_PATHS})
    assert profile2.data['packages'] == summary


def test_existing_profile_does_not_need_full_rescan_after_upgrade(tmp_path):
    from universal_linux_troubleshooter.results import DiagnosticResult
    sig = {k:'x' for k in WATCH_PATHS}
    p = SystemProfile(tmp_path/'p.json',clock=lambda:1000.,signature_source=lambda:sig)
    checks = [DiagnosticResult(a,b,ResultStatus.OK,'ok','ok','ok',()) for a,b in LOCAL_PLAN]
    p.update(checks, scanned_areas=list(WATCH_PATHS))
    assert p.complete
    assert {a for a,b in p.pending_checks()} == {'applications'}
    p.update([r for r in checks if r.category_key == 'applications'],
             scanned_areas=['applications'], packages=public_summary(inspect_sources(FakeHost())))
    assert p.pending_checks() == ()


def test_steam_diagnosis_shows_native_installation_without_claiming_a_cause():
    h = FakeHost({'rpm': CommandOutput(0, 'steam\n')})
    result = probe_steam_inventory128(h)
    assert result.status == ResultStatus.INFO
    assert 'FACT:steam_rpm=observed' in result.evidence
    from universal_linux_troubleshooter.diagnostics.topic_catalog127 import all_topics
    guide = next(x for x in all_topics() if x.heading == 'Steam')
    report = present_case(guide.case_id, [result], topic_id=guide.key)
    diagnosis = format_case_diagnosis130(guide.case_id, report, [result], topic_id=guide.key,
        package_sources=public_summary(inspect_sources(h)))
    assert 'Steam via RPM (DNF / Zypper): observed' in diagnosis
    assert report.proven_route is None


@pytest.mark.parametrize('case_id', tuple(case_catalog()))
def test_every_dossier_uses_same_scope_policy_when_package_info_is_relevant(case_id):
    case = case_catalog()[case_id]
    relevant = package_relevance(case_id, case['title'])
    sample = {'rpm': {'status':'checked','count':42},
              'flatpak_user': {'status':'unavailable','count':None}}
    report = present_case(case_id, [])
    text = format_case_diagnosis130(case_id, report, [], package_sources=sample)
    if relevant:
        assert 'PACKAGE SOURCES ON THIS COMPUTER' in text
        assert 'RPM packages (DNF / Zypper / RPM)' in text
    else:
        assert 'PACKAGE SOURCES ON THIS COMPUTER' not in text
    assert report.proven_route is None


def test_unverified_appimage_locations_remain_partial_information():
    class AppImageHost(FakeHost):
        def exists(self, path): return path == str(Path('~/Applications').expanduser())
        def list_names(self, path): return ('Tool.AppImage', 'steam.AppImage', 'normal.txt')
    readings = inspect_sources(AppImageHost(), application='steam')
    assert readings['appimage'].state == 'checked'
    assert readings['appimage'].count == 2
    assert readings['appimage'].presence == 'unknown'  # a filename is not proof
    assert 'appimage' in public_summary(readings)


def test_native_firefox_detection_not_limited_to_flatpak():
    readings = inspect_sources(FakeHost({'rpm': CommandOutput(0,'firefox\n')}), application='firefox')
    assert readings['rpm'].presence == 'found'
    assert readings['flatpak_user'].presence == 'unavailable'


def test_default_browser_can_observe_rpm_without_misclaiming_other_sources():
    from universal_linux_troubleshooter.diagnostics.browser_inventory119 import probe_browser_inventory119
    class BrowserHost(FakeHost):
        def command(self, args):
            if args == ('xdg-settings','get','default-web-browser'):
                return CommandOutput(0, 'firefox.desktop\n')
            if args == ('xdg-mime','query','default','x-scheme-handler/https'):
                return CommandOutput(0, 'firefox.desktop\n')
            return super().command(args)
    res=probe_browser_inventory119(BrowserHost({'rpm':CommandOutput(0,'firefox\n')}))
    assert 'FACT:browser_package_sources=rpm' in res.evidence
    assert 'FACT:browser_default=Firefox' in res.evidence


def test_hardware_rpm_does_not_mean_a_package_installation():
    for case in ('hardware34.cooling.fan-rpm-zero', 'hardware34.cooling.pump-rpm'):
        assert not package_relevance(case, case_catalog()[case]['title'])


def test_gui_uses_shared_cache_for_all_software_relevant_diagnoses():
    gui = (Path(__file__).resolve().parents[1]/'universal_linux_troubleshooter/pages/manual.py').read_text()
    worker = (Path(__file__).resolve().parents[1]/'universal_linux_troubleshooter/profile_worker119.py').read_text()
    assert 'package_sources=(profile.data.get' in gui
    assert 'package_sources131 import inspect_sources, public_summary' in worker
    assert 'packages=packages' in (Path(__file__).resolve().parents[1]/'universal_linux_troubleshooter/ui/main_window.py').read_text()
