"""Host-isolated tests: no external system access, no Qt required."""
import json
import shutil
import unittest
from universal_linux_troubleshooter.diagnostics.bridge import (
    DiagnosticBridge, LocalHost, CommandOutput, READY_CHECKS, GiB,
)
from universal_linux_troubleshooter.results import ResultStatus


class FakeHost(LocalHost):
    def __init__(self):
        self.names = ["lo", "eth0"]
        self.reads = {
            "/sys/class/net/eth0/operstate": "up\n",
            "/proc/meminfo": "MemTotal: 8192000 kB\nMemAvailable: 4000000 kB\n",
        }
        self.outputs = {
            ("ip", "-j", "address", "show"): CommandOutput(0, json.dumps([
                {"ifname": "lo", "addr_info": [{"family": "inet", "local": "127.0.0.1"}]},
                {"ifname": "eth0", "addr_info": [{"family": "inet", "local": "192.168.1.5"}]},
            ])),
            ("ip", "-j", "route", "show", "default"): CommandOutput(0, '[{"dst":"default","gateway":"192.168.1.1","dev":"eth0"}]'),
            ("ip", "-j", "-6", "route", "show", "default"): CommandOutput(0, '[]'),
            ("lsblk", "-J", "-b", "-o", "NAME,TYPE,SIZE,MOUNTPOINT,MODEL,RO"): CommandOutput(0, '{"blockdevices":[{"name":"sda","type":"disk","size":100000000000,"mountpoint":null}]}'),
            ("systemctl", "--failed", "--no-pager", "--no-legend", "--plain"): CommandOutput(0, ""),
            ("journalctl", "-b", "-p", "0..3", "-n", "80", "--no-pager", "--output=json"): CommandOutput(0, "-- No entries --"),
        }
        self.usage = shutil._ntuple_diskusage(100 * GiB, 50 * GiB, 50 * GiB)
        self.calls = []

    def list_names(self, path):
        if path != "/sys/class/net":
            raise AssertionError("Unexpected path")
        return tuple(self.names)

    def read(self, path):
        return self.reads[path]

    def disk_usage(self, path):
        self.calls.append(("disk_usage", path))
        return self.usage

    def load_average(self):
        return (0.3, 0.2, 0.1)

    def cpu_count(self):
        return 8

    def command(self, argv):
        self.calls.append(argv)
        return self.outputs[argv]


class TestBridge(unittest.TestCase):
    def setUp(self):
        self.host = FakeHost()
        self.bridge = DiagnosticBridge(self.host)

    def test_all_30_checks_available(self):
        self.assertEqual(len(READY_CHECKS), 30)
        self.assertIn(("network", "external"), READY_CHECKS)
        self.assertIn(("storage", "health"), READY_CHECKS)

    def test_interface_inventory_does_not_claim_connectivity(self):
        r = self.bridge.run_check("network", "adapter")
        self.assertEqual(r.status, ResultStatus.OK)
        self.assertIn("not a test of internet", r.explanation)
        self.assertIn("eth0", "\n".join(r.evidence))

    def test_no_adapters_warning_not_hardware_proof(self):
        self.host.names = ["lo"]
        r = self.bridge.run_check("network", "adapter")
        self.assertEqual(r.status, ResultStatus.WARNING)
        self.assertIn("does not prove that the device is broken", r.explanation)

    def test_ip_read_success_and_nonconclusive_explanation(self):
        r = self.bridge.run_check("network", "ip")
        self.assertEqual(r.status, ResultStatus.OK)
        self.assertIn("did not test whether websites", r.explanation)

    def test_ip_missing_tool_returns_unknown(self):
        self.host.outputs[("ip", "-j", "address", "show")] = CommandOutput(127, "", "ip missing")
        r = self.bridge.run_check("network", "ip")
        self.assertEqual(r.status, ResultStatus.UNKNOWN)

    def test_ip_without_addresses_warns(self):
        self.host.outputs[("ip", "-j", "address", "show")] = CommandOutput(0, '[{"ifname":"eth0","addr_info":[]}]')
        self.assertEqual(self.bridge.run_check("network", "ip").status, ResultStatus.WARNING)

    def test_ip_without_default_route_not_marked_ok(self):
        for cmd in [("ip", "-j", "route", "show", "default"), ("ip", "-j", "-6", "route", "show", "default")]:
            self.host.outputs[cmd] = CommandOutput(0, "[]")
        self.assertEqual(self.bridge.run_check("network", "ip").status, ResultStatus.UNKNOWN)

    def test_space_normal(self):
        self.assertEqual(self.bridge.run_check("storage", "space").status, ResultStatus.OK)
        self.assertIn(("disk_usage", "/"), self.host.calls)

    def test_space_low_warns_without_deleting(self):
        self.host.usage = shutil._ntuple_diskusage(100 * GiB, 99 * GiB, GiB)
        r = self.bridge.run_check("storage", "space")
        self.assertEqual(r.status, ResultStatus.WARNING)
        self.assertIn("Never delete Linux system files", r.solution)

    def test_space_small_disk_not_false_alarm(self):
        self.host.usage = shutil._ntuple_diskusage(3 * GiB, GiB, 2 * GiB)
        self.assertEqual(self.bridge.run_check("storage", "space").status, ResultStatus.OK)

    def test_drive_inventory_is_not_health(self):
        r = self.bridge.run_check("storage", "drives")
        self.assertEqual(r.status, ResultStatus.OK)
        self.assertIn("not a SMART", r.explanation)

    def test_bad_lsblk_json_unknown(self):
        cmd = ("lsblk", "-J", "-b", "-o", "NAME,TYPE,SIZE,MOUNTPOINT,MODEL,RO")
        self.host.outputs[cmd] = CommandOutput(0, "NOT JSON")
        self.assertEqual(self.bridge.run_check("storage", "drives").status, ResultStatus.UNKNOWN)

    def test_resources_memory_low(self):
        self.host.reads["/proc/meminfo"] = "MemTotal: 8192000 kB\nMemAvailable: 120000 kB\n"
        self.assertEqual(self.bridge.run_check("applications", "resources").status, ResultStatus.WARNING)

    def test_resources_without_meminfo_unknown(self):
        del self.host.reads["/proc/meminfo"]
        self.assertEqual(self.bridge.run_check("applications", "resources").status, ResultStatus.UNKNOWN)

    def test_services_no_failures(self):
        r = self.bridge.run_check("applications", "services")
        self.assertEqual(r.status, ResultStatus.OK)
        self.assertIn("does not examine every program", r.explanation)

    def test_services_failed_units(self):
        cmd = ("systemctl", "--failed", "--no-pager", "--no-legend", "--plain")
        self.host.outputs[cmd] = CommandOutput(0, "bad.service loaded failed failed test\n")
        self.assertEqual(self.bridge.run_check("applications", "services").status, ResultStatus.WARNING)

    def test_services_without_systemd_unknown(self):
        cmd = ("systemctl", "--failed", "--no-pager", "--no-legend", "--plain")
        self.host.outputs[cmd] = CommandOutput(1, "", "not booted with systemd")
        self.assertEqual(self.bridge.run_check("applications", "services").status, ResultStatus.UNKNOWN)

    def test_no_journal_messages_is_information_not_a_failure(self):
        self.assertEqual(self.bridge.run_check("system", "system_logs").status, ResultStatus.INFO)

    def test_missing_journal_reader_remains_unknown(self):
        self.host.outputs[("journalctl", "-b", "-p", "0..3", "-n", "80", "--no-pager", "--output=json")] = CommandOutput(127, "", "missing")
        self.assertEqual(self.bridge.run_check("system", "system_logs").status, ResultStatus.UNKNOWN)

    def test_journal_entries_warn_with_privacy_guidance(self):
        cmd = ("journalctl", "-b", "-p", "0..3", "-n", "80", "--no-pager", "--output=json")
        self.host.outputs[cmd] = CommandOutput(0, json.dumps({"SYSLOG_IDENTIFIER": "systemd", "MESSAGE": "A unit failed", "PRIORITY": "3"}) + "\n")
        r = self.bridge.run_check("system", "system_logs")
        self.assertEqual(r.status, ResultStatus.WARNING)
        self.assertIn("private data", r.solution)

    def test_missing_handler_does_not_fake_result(self):
        with self.assertRaises(ValueError):
            self.bridge.run_check("network", "nonexistent_check")

    def test_exception_during_one_check_is_caught(self):
        del self.host.outputs[("systemctl", "--failed", "--no-pager", "--no-legend", "--plain")]
        self.assertEqual(self.bridge.run_check("applications", "services").status, ResultStatus.UNKNOWN)

    def test_commands_never_accept_arbitrary_argv(self):
        with self.assertRaises(ValueError):
            LocalHost().command(("sudo", "rm", "-rf", "/"))


if __name__ == "__main__":
    unittest.main()
