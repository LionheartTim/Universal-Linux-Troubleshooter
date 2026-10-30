"""Safe mocked Flatpak-host integration tests; no real host changes."""
import os
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock

from universal_linux_troubleshooter.flatpak_host138 import (
    in_flatpak, view_path, host_disk_usage, host_read, host_path_exists
)
from universal_linux_troubleshooter.diagnostics.bridge import LocalHost


class HostIntegration(unittest.TestCase):
    def test_native_paths(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(in_flatpak())
            self.assertEqual(str(view_path('/etc/os-release')), '/etc/os-release')

    def test_flatpak_host_etc_mapping(self):
        with patch.dict(os.environ, {'FLATPAK_ID': 'x'}, clear=True):
            self.assertEqual(str(view_path('/etc/os-release')), '/run/host/etc/os-release')
            self.assertEqual(str(view_path('/usr/lib/os-release')), '/run/host/usr/lib/os-release')
            self.assertEqual(str(view_path('/sys/class/net')), '/sys/class/net')

    def test_allowlisted_command_runs_on_host(self):
        with patch.dict(os.environ, {'FLATPAK_ID': 'x'}, clear=True):
            with patch('universal_linux_troubleshooter.diagnostics.bridge.subprocess.run') as run:
                run.return_value = MagicMock(returncode=0, stdout='active', stderr='')
                outcome = LocalHost().command(('systemctl', 'is-active', 'bluetooth.service'))
                self.assertEqual(outcome.out, 'active')
                self.assertEqual(run.call_args.args[0][:4],
                                 ('flatpak-spawn','--host','--env=LC_ALL=C','--env=LANG=C'))

    def test_unknown_command_is_denied_before_subprocess(self):
        with patch.dict(os.environ, {'FLATPAK_ID': 'x'}, clear=True):
            with patch('universal_linux_troubleshooter.diagnostics.bridge.subprocess.run') as run:
                with self.assertRaises(ValueError):
                    LocalHost().command(('bash','-c','rm -rf /'))
                run.assert_not_called()

    def test_no_shell_even_for_approved_commands(self):
        with patch.dict(os.environ, {'FLATPAK_ID':'x'}, clear=True):
            with patch('universal_linux_troubleshooter.diagnostics.bridge.subprocess.run') as run:
                run.return_value = MagicMock(returncode=0, stdout='',stderr='')
                LocalHost().command(('ip','-j','route','show','default'))
                self.assertFalse(run.call_args.kwargs['check'])
                self.assertFalse(run.call_args.kwargs.get('shell',False))

    def test_host_error_remains_nonzero(self):
        with patch.dict(os.environ, {'FLATPAK_ID':'x'}, clear=True):
            with patch('universal_linux_troubleshooter.diagnostics.bridge.subprocess.run') as run:
                run.return_value = MagicMock(returncode=1,stdout='',stderr='permission denied')
                response = LocalHost().command(('systemctl', 'is-active', 'bluetooth.service'))
                self.assertEqual(response.code,1)

    def test_host_read_only_fixed_proc_paths(self):
        with patch('universal_linux_troubleshooter.flatpak_host138.subprocess.run') as run:
            run.return_value = MagicMock(returncode=0,stdout='MemTotal: 1\n')
            self.assertEqual(host_read('/proc/meminfo'), 'MemTotal: 1\n')
            self.assertIn('flatpak-spawn',run.call_args.args[0])
            with self.assertRaises(ValueError):
                host_read('/home/user/.ssh/id_rsa')

    def test_host_disk_usage_parsing(self):
        with patch('universal_linux_troubleshooter.flatpak_host138.subprocess.run') as run:
            run.return_value = MagicMock(returncode=0,stdout='1B-blocks Used Avail\n100 40 60\n')
            usage = host_disk_usage('/var')
            self.assertEqual((usage.total, usage.used, usage.free),(100,40,60))
            with self.assertRaises(ValueError):
                host_disk_usage('/home/user')

    def test_path_probe_does_not_expand_scope(self):
        with self.assertRaises(ValueError):
            host_path_exists('/etc/shadow')

    def test_only_intended_diagnostic_tabs(self):
        source = (Path(__file__).resolve().parents[1]/'universal_linux_troubleshooter/ui/main_window.py').read_text()
        self.assertIn('Manual Diagnostics',source)
        self.assertIn('"Info"',source)
        self.assertNotIn('self.tabs.addTab(self.ai',source)

    def test_all_required_offline_datasets_present(self):
        import json
        root = Path(__file__).resolve().parents[1]/'knowledge_sources'
        for name in ('diagnosis_trees.json','supplemental_problem_guides127.json','steam_problem_guides128.json'):
            self.assertTrue((root/name).is_file())
            json.loads((root/name).read_text())

    def test_flatpak_manifest_is_local_test_only(self):
        import json
        root = Path(__file__).resolve().parents[1]
        manifest = json.loads(next(root.glob('io.github*.json')).read_text())
        self.assertIn('--talk-name=org.freedesktop.Flatpak',manifest['finish-args'])
        self.assertEqual(manifest['base'],'io.qt.PySide.BaseApp')
        self.assertIn('--share=network',manifest['finish-args'])


if __name__ == '__main__':unittest.main()
