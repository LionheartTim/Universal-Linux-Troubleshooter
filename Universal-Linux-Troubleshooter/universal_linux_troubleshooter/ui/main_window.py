"""Main GUI shell. Read-only diagnostics; changes only after direct approval."""

from PySide6.QtCore import Qt, QTimer, QFileSystemWatcher
from PySide6.QtWidgets import (
    QHBoxLayout, QMainWindow, QTabWidget,
    QVBoxLayout, QWidget, QLabel,
)
from ..pages.manual import ManualDiagnosticsPage
from ..pages.info import InfoPage
from ..system_profile119 import SystemProfile, signatures, readable_profile_watch_paths
from ..profile_worker119 import ProfileWorker119
from ..app_identity import APPLICATION_NAME, application_icon


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APPLICATION_NAME)
        self.setWindowIcon(application_icon())
        self.resize(1270, 800)
        self.setMinimumSize(960, 660)
        self._close_when_done = False
        # One shared, private, saved baseline for ALL pages; never an AI-owned
        # source of privileged commands or repair permission.
        self.system_profile = SystemProfile()
        self._profile_worker = None
        self._profile_close_queued = False
        self._profile_scanned_signatures = None

        root = QWidget()
        root.setObjectName("Root")
        self.setCentralWidget(root)
        main_layout = QVBoxLayout(root)
        main_layout.setContentsMargins(12, 10, 12, 0)
        main_layout.setSpacing(0)

        # Manual Diagnostics is the complete application; no AI tab, model or runtime.
        self.tabs = QTabWidget()
        self.tabs.setObjectName("MainTabs")
        self.manual = ManualDiagnosticsPage()
        self.manual.system_profile = self.system_profile
        self.tabs.addTab(self.manual, "Manual Diagnostics")
        self.info = InfoPage()
        self.tabs.addTab(self.info, "Info")
        main_layout.addWidget(self.tabs, 1)
        self.profile_notice = QLabel('')
        self.profile_notice.setObjectName('CountLabel')
        self.profile_notice.setWordWrap(True)
        main_layout.addWidget(self.profile_notice)

        footer = QWidget()
        footer.setObjectName("AppFooter")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(10, 5, 10, 5)
        footer_layout.setSpacing(8)
        credit = QLabel(
            'Universal Linux Troubleshooter v1.0.0 · by '
            '<a href="https://github.com/LionheartTim">LionheartTim</a>'
        )
        credit.setObjectName("FooterCredit")
        credit.setTextFormat(Qt.TextFormat.RichText)
        credit.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        credit.setOpenExternalLinks(True)
        credit.setToolTip("Open the LionheartTim GitHub profile")
        footer_layout.addWidget(credit)
        footer_layout.addStretch(1)
        preview = QLabel("READ-ONLY DIAGNOSTICS · NO CHANGES WITHOUT APPROVAL")
        preview.setObjectName("FooterPreview")
        footer_layout.addWidget(preview)
        main_layout.addWidget(footer)

        # File/directory changes are cheap hints; periodic polling handles
        # missed events and changes that have no file notification. No scan
        # runs from an AI message; the profile is not rebuilt per prompt.
        self._profile_watcher = QFileSystemWatcher(self)
        self._profile_watcher.fileChanged.connect(self._profile_changed)
        self._profile_watcher.directoryChanged.connect(self._profile_changed)
        # Watching protected system folders is optional; many Linux distros
        # restrict /etc/libvirt to administrators. Do not attempt Qt inotify
        # on an unreadable path, request privileges, or disable diagnostics.
        # The existing 60-second signature/TTL refresh remains the fallback.
        watchable = readable_profile_watch_paths()
        if watchable:
            self._profile_watcher.addPaths(list(watchable))
        self._profile_timer = QTimer(self)
        self._profile_timer.setInterval(60_000)
        self._profile_timer.timeout.connect(self._maybe_refresh_profile)
        self._profile_timer.start()
        QTimer.singleShot(0, self._maybe_refresh_profile)


    def _profile_changed(self, _path):
        # Coalesce bursts during package installations; the heavy work stays
        # off the GUI thread. No network is ever permitted in this worker.
        QTimer.singleShot(1200, self._maybe_refresh_profile)

    def _maybe_refresh_profile(self):
        if self._profile_worker is not None:
            return
        pending = self.system_profile.pending_checks()
        if not pending:
            self.profile_notice.setText('Local system profile up to date · No automatic online checks')
            return
        self._profile_scanned_signatures = signatures()
        self.profile_notice.setText(
            'Creating your local system profile…' if not self.system_profile.complete
            else 'Updating changed system information…'
        )
        worker = ProfileWorker119(pending, self)
        self._profile_worker = worker
        worker.completed.connect(self._profile_scan_complete)
        worker.progress.connect(self._profile_scan_progress)
        worker.finished.connect(self._profile_scan_finished)
        worker.start()

    def _profile_scan_progress(self, completed, total):
        if self.system_profile.complete:
            self.profile_notice.setText(
                f'Updating changed system information… {completed} of {total} checks'
            )
        else:
            self.profile_notice.setText(
                f'Creating your local system profile… {completed} of {total} checks'
            )

    def _profile_scan_complete(self, results, browser, osinfo, checks, packages=None):
        groups = tuple(sorted({area for area, _ in checks}))
        self.system_profile.update(results, scanned_areas=groups,
                                   new_signatures=self._profile_scanned_signatures,
                                   browser=browser, osinfo=osinfo, packages=packages)
        self.profile_notice.setText(
            'Local system profile ready · ' + str(len(self.system_profile.data['checks'])) +
            ' offline checks saved · Network requests off'
        )

    def _profile_scan_finished(self):
        worker = self._profile_worker
        self._profile_worker = None
        if worker:
            worker.deleteLater()
        # Any changes during a scan are picked up on the next timer/watch tick.

    def closeEvent(self, event):
        if self._profile_worker is not None:
            self._profile_worker.requestInterruption()
            if not self._profile_close_queued:
                self._profile_close_queued = True
                self._profile_worker.finished.connect(lambda: QTimer.singleShot(0, self.close))
            event.ignore()
            return
        # Keep the widget alive until the active QThread stops; never tear down a
        # running QThread (which can crash the process).
        if self.manual._scan_running():
            self.manual.cancel_scan()
            if not self._close_when_done:
                self._close_when_done = True
                self.manual.scan_finished.connect(lambda: QTimer.singleShot(0, self.close))
            event.ignore()
            return
        super().closeEvent(event)
