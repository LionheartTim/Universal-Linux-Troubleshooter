"""Complete system scan: full coverage, explicit network opt-in and clear reporting.

These tests are pure Python so they can run without a local Qt display.
"""
import unittest
from pathlib import Path
from universal_linux_troubleshooter.catalog import CATEGORIES
from universal_linux_troubleshooter.diagnostics.bridge import READY_CHECKS, DiagnosticBridge
from universal_linux_troubleshooter.diagnostics.plan import (
    NETWORK_OPT_IN_CHECKS, complete_system_plan, selected_plan,
)
from universal_linux_troubleshooter.presentation import (
    batch_summary, combined_check_view, complete_scan_at_a_glance, prioritize_check_results,
)
from universal_linux_troubleshooter.results import DiagnosticResult, ResultStatus


def result(pair, status):
    return DiagnosticResult(pair[0], pair[1], status, "Finding", "Explanation", "Advice", ("Log",))


class CompleteScanTests(unittest.TestCase):
    def test_default_is_every_local_check_exactly_once(self):
        plan = complete_system_plan(READY_CHECKS)
        self.assertEqual(len(plan), 28)
        self.assertEqual(len(plan), len(set(plan)))
        self.assertEqual(set(plan), set(READY_CHECKS) - NETWORK_OPT_IN_CHECKS)
        self.assertEqual(set(p[0] for p in plan), {c.key for c in CATEGORIES})

    def test_network_opt_in_includes_both_checks_and_only_after_opt_in(self):
        offline = complete_system_plan(READY_CHECKS)
        full = complete_system_plan(READY_CHECKS, include_network=True)
        self.assertEqual(len(full), 30)
        self.assertEqual(set(full) - set(offline), NETWORK_OPT_IN_CHECKS)
        self.assertNotIn(("network", "external"), offline)
        self.assertNotIn(("network", "dns"), offline)

    def test_catalogue_order_stable_and_ignores_stale_manual_selection(self):
        expected = [(c.key, k.key) for c in CATEGORIES for k in c.checks
                    if (c.key, k.key) not in NETWORK_OPT_IN_CHECKS]
        self.assertEqual(list(complete_system_plan(READY_CHECKS)), expected)
        chosen = selected_plan({"network": {"adapter"}}, READY_CHECKS)
        self.assertEqual(chosen, (("network", "adapter"),))
        self.assertNotEqual(chosen, complete_system_plan(READY_CHECKS))

    def test_unsupported_checks_not_scheduled(self):
        plan = complete_system_plan({("network", "adapter"), ("network", "dns")})
        self.assertEqual(plan, (("network", "adapter"),))

    def test_prio_allows_no_result_and_shows_problems_before_ok(self):
        keys = complete_system_plan(READY_CHECKS)[:6]
        states = [ResultStatus.OK, ResultStatus.WARNING, ResultStatus.UNKNOWN,
                  ResultStatus.PROBLEM, ResultStatus.INFO]
        results = {k: result(k, s) for k, s in zip(keys, states)}
        ordered = prioritize_check_results(keys, results)
        self.assertEqual(ordered[0], keys[5])  # unfinished not falsely called OK
        self.assertEqual(ordered[1], keys[3])  # PROBLEM
        self.assertEqual(ordered[2], keys[1])  # WARNING
        self.assertEqual(ordered[-1], keys[0])  # OK
        self.assertEqual(set(keys), set(ordered))

    def test_full_report_includes_all_checks_categories_and_truthful_summary(self):
        plan = complete_system_plan(READY_CHECKS)
        results = {p: result(p, ResultStatus.OK) for p in plan}
        results[plan[0]] = result(plan[0], ResultStatus.WARNING)
        results[plan[1]] = result(plan[1], ResultStatus.UNKNOWN)
        views = combined_check_view(prioritize_check_results(plan, results), results,
                                    CATEGORIES, include_categories=True)
        self.assertEqual(views[0].count("Status:"), len(plan))
        self.assertEqual(views[1].count("What was found:"), len(plan))
        self.assertIn("Internet & Network >", views[0])
        self.assertIn("System, Boot & Updates >", views[0])
        overview = complete_scan_at_a_glance(plan, results)
        self.assertIn("28 of 28 checks finished", overview)
        self.assertIn("worth investigating", overview)
        self.assertIn("could not get enough information", overview)
        self.assertNotIn("No problems were identified", overview)
        self.assertIn("1 warning", batch_summary(plan, results))

    def test_not_running_is_not_a_fault_and_interrupted_is_never_all_ok(self):
        plan = complete_system_plan(READY_CHECKS)
        part = {plan[0]: result(plan[0], ResultStatus.OK)}
        partial = complete_scan_at_a_glance(plan, part)
        self.assertIn("1 of 28 checks finished", partial)
        self.assertIn("still running or were stopped", partial)
        self.assertNotIn("No problems were identified", partial)

    def test_all_28_handlers_return_results_offline(self):
        # The production bridge defaults to allow_network=False. Avoid a real
        # network connection but exercise every local handler in this process.
        bridge = DiagnosticBridge(allow_network=False)
        for pair in complete_system_plan(READY_CHECKS):
            with self.subTest(pair=pair):
                ans = bridge.run_check(*pair)
                self.assertIsInstance(ans, DiagnosticResult)
                self.assertEqual((ans.category_key, ans.check_key), pair)

    def test_gui_contains_separate_full_scan_button_and_summary_below_tabs(self):
        source = (Path(__file__).resolve().parents[1] /
                  "universal_linux_troubleshooter/pages/manual.py").read_text()
        self.assertIn('QPushButton("Complete system scan")', source)
        self.assertIn('dialog.setCheckBox(network_choice)', source)
        self.assertIn('self._begin_scan(checks, allow_network=include_network, complete=True)', source)
        self.assertLess(source.index('result_layout.addWidget(self.result_tabs, 1)'),
                        source.index('result_layout.addWidget(self.results_overview)'))
        self.assertIn('self.complete_scan_button.setEnabled(False)', source)
        self.assertIn('self.complete_scan_button.setEnabled(True)', source)


if __name__ == '__main__':
    unittest.main()
