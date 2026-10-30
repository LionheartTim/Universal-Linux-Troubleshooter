"""Check permission-safe Qt watcher selection without requiring a GUI runtime."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from universal_linux_troubleshooter.system_profile119 import (
    AREA_TTLS, SystemProfile, WATCH_PATHS, readable_profile_watch_paths,
)


class WatchPermissions137Tests(unittest.TestCase):
    def test_unreadable_libvirt_is_excluded_while_readable_paths_survive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            privileged = root / 'libvirt'
            privileged.mkdir()
            other = root / 'network'
            other.mkdir()
            readable_file = root / 'os-release'
            readable_file.write_text('NAME=Example\n')
            groups = {'virtualization': (str(privileged),),
                      'network': (str(other), str(readable_file), str(readable_file))}
            real_access = os.access

            def allowed(path, mode):
                if Path(path) == privileged:
                    return False
                return real_access(path, mode)

            with patch('universal_linux_troubleshooter.system_profile119.os.access', side_effect=allowed):
                selected = readable_profile_watch_paths(groups)
            self.assertNotIn(str(privileged), selected)
            self.assertIn(str(readable_file), selected)
            self.assertIn(str(other), selected)
            self.assertEqual(len(selected), 2)

    def test_unavailable_targets_never_added(self):
        with tempfile.TemporaryDirectory() as tmp:
            selected = readable_profile_watch_paths({'virtualization': (str(Path(tmp) / 'missing'),)})
            self.assertEqual(selected, ())

    def test_directory_requires_both_read_and_traverse_access(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / 'private'
            folder.mkdir()
            with patch('universal_linux_troubleshooter.system_profile119.os.access') as access:
                access.return_value = True
                self.assertEqual(readable_profile_watch_paths({'virtualization': (str(folder),)}), (str(folder),))
                access.assert_called_once_with(folder, os.R_OK | os.X_OK)

    def test_polling_unchanged_when_watcher_skips_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            now = [1_800_000_000.0]
            sig = {k: 'initial' for k in WATCH_PATHS}
            profile = SystemProfile(Path(tmp) / 'profile.json', clock=lambda: now[0],
                                    signature_source=lambda: dict(sig))
            self.assertIn('virtualization', {a for a, _ in profile.pending_checks()})
            from universal_linux_troubleshooter.results import DiagnosticResult, ResultStatus
            checks = [DiagnosticResult(a, c, ResultStatus.OK, 'ok', 'read only', 'none', ())
                      for a, c in profile.pending_checks()]
            profile.update(checks, scanned_areas=list(WATCH_PATHS),
                           packages={'rpm': {'status': 'unavailable', 'count': None}})
            self.assertEqual(profile.pending_checks(), ())
            sig['virtualization'] = 'changed'
            self.assertIn('virtualization', {a for a, _ in profile.pending_checks()})
            sig['virtualization'] = 'initial'
            now[0] += AREA_TTLS['virtualization'] + 1
            self.assertIn('virtualization', {a for a, _ in profile.pending_checks()})

    def test_main_window_uses_permission_filter_not_raw_exists_list(self):
        import inspect
        from pathlib import Path
        source = (Path(__file__).resolve().parents[1] / 'universal_linux_troubleshooter' / 'ui' / 'main_window.py').read_text()
        self.assertIn('readable_profile_watch_paths()', source)
        self.assertIn('self._profile_timer.setInterval(60_000)', source)
        self.assertNotIn('if Path(p).expanduser().exists()', source)


if __name__ == '__main__':
    unittest.main()
