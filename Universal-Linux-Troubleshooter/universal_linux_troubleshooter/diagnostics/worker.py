"""Sequential read-only checks on a background Qt thread.

Run is user-initiated. A stop request is honoured between each limited-duration
check. This worker cannot perform any repair and has no AI dependency.
"""
from PySide6.QtCore import QThread, Signal
from .bridge import DiagnosticBridge


class DiagnosticWorker(QThread):
    result_ready = Signal(object)
    progress_changed = Signal(int, int)

    def __init__(self, checks: tuple[tuple[str, str], ...], parent=None, *, allow_network=False, issue="", focused_probes=(), target_case_id=None, target_note=None, guided_case_id=None, guided_path=None, guided_consent=False, guided_note=None, network75_case=None, network75_note=None, network75_consent=False):
        super().__init__(parent)
        self._checks = checks
        self._allow_network = allow_network
        self._issue = issue
        self._focused_probes = tuple(focused_probes)
        self._target_case_id = target_case_id
        self._target_note = target_note
        self._guided_case_id = guided_case_id
        self._guided_path = guided_path
        self._guided_consent = guided_consent
        self._guided_note = guided_note
        self._network75_case = network75_case
        self._network75_note = network75_note
        self._network75_consent = bool(network75_consent)

    def set_issue(self, issue: str):
        self._issue = issue

    def run(self):
        bridge = DiagnosticBridge(allow_network=self._allow_network)
        from .target_evidence69 import supports_target_probe
        target_pending = bool(self._target_case_id and self._target_note and supports_target_probe(self._target_case_id))
        total = len(self._checks) + len(self._focused_probes) + int(target_pending) + int(bool(self._guided_case_id)) + int(bool(self._network75_case))
        for index, (category, check) in enumerate(self._checks, start=1):
            if self.isInterruptionRequested():
                break
            self.result_ready.emit(bridge.run_check(category, check))
            self.progress_changed.emit(index, total)
        if self._focused_probes and not self.isInterruptionRequested():
            from .focused_evidence import run_named_focused_checks
            # The full catalog may request dozens of distinct allowlisted
            # probes. Run them ONE at a time, with cancellation between each.
            # The fixed per-call limit of two remains in force for ordinary
            # case investigations and cannot be bypassed by arbitrary input.
            for index, probe_key in enumerate(self._focused_probes, start=len(self._checks) + 1):
                if self.isInterruptionRequested():
                    break
                for finding in run_named_focused_checks(bridge.host, (probe_key,)):
                    self.result_ready.emit(finding)
                self.progress_changed.emit(index, total)
        if target_pending and not self.isInterruptionRequested():
            from .target_evidence69 import inspect_target
            self.result_ready.emit(inspect_target(bridge.host, self._target_case_id, self._target_note))
            self.progress_changed.emit(total, total)
        if self._guided_case_id and not self.isInterruptionRequested():
            from .guided_evidence74 import inspect_guided74
            self.result_ready.emit(inspect_guided74(
                self._guided_case_id, selected_path=self._guided_path,
                target_note=self._guided_note, consent=self._guided_consent))
            self.progress_changed.emit(total, total)
        if self._network75_case and not self.isInterruptionRequested():
            from .consented_network75 import inspect_network75
            self.result_ready.emit(inspect_network75(
                self._network75_case, self._network75_note,
                consent=self._network75_consent))
            self.progress_changed.emit(total, total)
        if self._issue and not self.isInterruptionRequested():
            from .focused_evidence import run_focused_checks
            for finding in run_focused_checks(bridge.host, self._issue):
                if self.isInterruptionRequested():
                    break
                self.result_ready.emit(finding)


