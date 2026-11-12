"""Qt background worker for first-run and incremental local profile scans."""
from PySide6.QtCore import QThread, Signal
from .system_profile119 import scan_baseline, browser_facts, os_facts

class ProfileWorker119(QThread):
    completed = Signal(object, object, object, object, object)
    progress = Signal(int, int)
    def __init__(self, checks, parent=None):
        super().__init__(parent)
        self.checks = tuple(checks)
    def run(self):
        # Local checks only, no network and no writes to the host.
        from .diagnostics.bridge import DiagnosticBridge
        bridge = DiagnosticBridge(allow_network=False)
        results = []
        for i, pair in enumerate(self.checks, 1):
            if self.isInterruptionRequested():
                break
            results.extend(scan_baseline((pair,), bridge=bridge))
            self.progress.emit(i, len(self.checks))
        if not self.isInterruptionRequested():
            facts = (browser_facts(host=bridge.host)
                     if any(area == 'applications' for area, _ in self.checks)
                     else None)
            system = os_facts() if any(area == 'system' for area, _ in self.checks) else None
            packages = None
            if any(area == 'applications' for area, _ in self.checks):
                from .diagnostics.package_sources131 import inspect_sources, public_summary
                packages = public_summary(inspect_sources(bridge.host))
            self.completed.emit(tuple(results), facts, system, tuple(self.checks), packages)
