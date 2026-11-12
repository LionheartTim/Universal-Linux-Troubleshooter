"""Manual Diagnostics UI connected to the first read-only diagnostic bridge."""

from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLineEdit, QTreeWidget, QTreeWidgetItem, QHeaderView, QPushButton,
    QFrame, QLabel, QTabWidget, QPlainTextEdit, QScrollArea, QApplication, QComboBox, QMessageBox, QCheckBox, QSizePolicy, QFileDialog,
)
from ..catalog import CATEGORIES, Category
from ..results import DiagnosticResult, ResultStatus
from ..diagnostics import READY_CHECKS
from ..diagnostics.worker import DiagnosticWorker
from ..diagnostics.plan import selected_plan, complete_system_plan
from ..diagnostics.full_catalog133 import complete_catalog_plan, full_scan_pages, scan_catalog_coverage
from ..diagnostics.selection_policy import forget_checks_on_area_change
from ..ui.components import label
from ..ui.progress import DiagnosticProgress
from ..presentation import (diagnosis_heading, diagnosis_body, solution_heading, solution_body,
                            evidence_body, batch_summary, combined_check_view,
                            prioritize_check_results, complete_scan_at_a_glance)
from ..diagnostics.cause_analysis import scan_cause_summary
from ..diagnostics.manual_cases40 import case_catalog, plan_for_manual_case, present_case
from ..diagnostics.context_intake68 import context_question, safe_target_note
from ..diagnostics.case_navigation41 import navigation_groups
from ..diagnostics.topic_catalog127 import matching_topics, BY_KEY, guide_for_topic, CURRENT_GUIDE_VERSION
from ..diagnostics.rescan import ManualScanReplay
from ..diagnostics.guided_evidence74 import CASES74, PATH_CASES74, FOLDER_WRITE_CASE, VENV_CASE
from ..diagnostics.guided_evidence80 import APPIMAGE_CASE80, PATH_SHADOW_CASE80
from ..diagnostics.manual_tree_presentation90 import pages_for_case, ULT, ULSM
from ..diagnostics.presentation_english93 import display_case_report93
from ..diagnostics.diagnosis_display130 import format_case_diagnosis130
from ..diagnostics.readable_layout93 import html_for_manual93
from ..diagnostics.device_choices91 import discover_choices, kind_for_case, DeviceChoices


class WholeRowCheckTree(QTreeWidget):
    """Click anywhere on a ready row to tick it (not just the tiny box).

    Qt already toggles the box itself. Compare the state before/after native
    handling so clicking the box never toggles twice. Planned rows can still
    be highlighted to read their description but cannot be checked.
    """

    def mousePressEvent(self, event):
        self._click_start = None
        if event.button() == Qt.MouseButton.LeftButton and self.isEnabled():
            row = self.itemAt(event.pos())
            if row is not None and bool(row.flags() & Qt.ItemFlag.ItemIsUserCheckable):
                self._click_start = (row, row.checkState(0))
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        start = getattr(self, "_click_start", None)
        self._click_start = None
        super().mouseReleaseEvent(event)
        if (event.button() == Qt.MouseButton.LeftButton and self.isEnabled()
                and start is not None):
            row, original_state = start
            if (self.itemAt(event.pos()) is row
                    and bool(row.flags() & Qt.ItemFlag.ItemIsUserCheckable)
                    and row.checkState(0) == original_state):
                # Native handling did not change the checkbox: the user
                # clicked the text or another column. Toggle it now.
                row.setCheckState(0, Qt.CheckState.Unchecked if
                                  original_state == Qt.CheckState.Checked else
                                  Qt.CheckState.Checked)


class LocalDeviceDiscovery(QThread):
    """Bounded read-only device inventory, off the Qt GUI thread."""
    discovered = Signal(str, int, object)

    def __init__(self, case_id: str, generation: int, parent=None):
        super().__init__(parent)
        self.case_id = case_id
        self.generation = generation

    def run(self):
        from ..diagnostics.bridge import LocalHost
        result = discover_choices(LocalHost(), self.case_id)
        self.discovered.emit(self.case_id, self.generation, result)


class ManualDiagnosticsPage(QWidget):
    scan_finished = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self._selection: dict[str, set[str]] = {cat.key: set() for cat in CATEGORIES}
        self._results: dict[tuple[str, str], DiagnosticResult] = {}
        self.system_profile = None  # shared by MainWindow; no external model required
        self._current: Category | None = None
        self._focused_key: str | None = None
        self._loading = False
        self._worker = None
        self._completed = 0
        self._run_total = 0
        self._last_batch: tuple[tuple[str, str], ...] = ()
        self._full_scan_batch = False
        self._full_scan_online = False
        self._full_catalog_plan = None
        self._active_case_id: str | None = None
        self._selected_case_id: str | None = None
        self._selected_topic_id: str | None = None
        self._active_topic_id: str | None = None
        self._nav_selection: tuple | None = None
        self._case_items: dict[str, QTreeWidgetItem] = {}
        self._case_probe_results: list[DiagnosticResult] = []
        self._target_inventory_result = None
        self._guided_result74 = None
        self._guided_path74 = None
        self._guided_consent74 = False
        self._case_view = None
        self._case_scan_completed = True
        self._active_target_note = None
        self._context_case_id = None
        self._last_scan: ManualScanReplay | None = None
        self._lookup_generation = 0
        self._device_workers = set()
        self._auto_device_id: str | None = None
        self._device_lookup_pending = False

        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 12, 10, 8)
        outer.setSpacing(11)
        # Deliberately no redundant "Manual Diagnostics" headline / description.
        # One search entry for existing checks AND all 250 documented cases.
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search hardware, software or a problem (e.g. GPU, Flatpak, sound)…")
        self.search.setClearButtonEnabled(True)
        self.search.setToolTip("Search documented symptoms and available read-only diagnostic checks.")
        self.search.textChanged.connect(self._populate_categories)
        outer.addWidget(self.search)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        outer.addWidget(splitter, 1)

        left = QFrame()
        left.setObjectName("Inset")
        left.setMinimumWidth(420)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(11, 13, 11, 11)
        left_layout.setSpacing(8)
        left_layout.addWidget(label("DIAGNOSTIC AREAS", "CountLabel"))
        self.categories = QTreeWidget()
        self.categories.setObjectName("DiagnosisNavigation")
        self.categories.setHeaderHidden(True)
        self.categories.setColumnCount(1)
        self.categories.setAnimated(True)
        self.categories.setUniformRowHeights(True)
        self.categories.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        # Subject headings and 250 case leaves scroll independently from scan.
        self.categories.setMinimumHeight(90)
        self.categories.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.categories.currentItemChanged.connect(self._category_changed)
        left_layout.addWidget(self.categories, 1)
        self.category_count = label("", "Muted")
        # Beginner scan belongs with the diagnostic areas, at bottom left;
        # leave the search row empty for the catalogue search.
        self.complete_scan_button = QPushButton("Complete system scan")
        self.complete_scan_button.setObjectName("Primary")
        self.complete_scan_button.setToolTip(
            "Check the entire computer without selecting individual tests. "
            "Optional online checks always require your permission."
        )
        self.complete_scan_button.clicked.connect(self._run_complete_scan)
        self.complete_scan_button.setMinimumHeight(39)
        self.complete_scan_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.complete_scan_button.setVisible(True)
        # Fixed footer stays below the scrolling category list.
        left_footer = QWidget()
        left_footer_layout = QVBoxLayout(left_footer)
        left_footer_layout.setContentsMargins(0, 0, 0, 0)
        left_footer_layout.setSpacing(6)
        left_footer_layout.addWidget(self.category_count)
        left_footer_layout.addWidget(self.complete_scan_button)
        left_footer.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        left_layout.addWidget(left_footer, 0)
        splitter.addWidget(left)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(5, 0, 0, 0)
        right_layout.setSpacing(7)
        self.title = label("Choose a diagnostic area", "SectionTitle")
        right_layout.addWidget(self.title)
        self.intro = label("", "CardBody")
        right_layout.addWidget(self.intro)

        # Only shown when an actual diagnosis case (not merely an area) is
        # selected in the left navigation. Never automatically execute a scan
        # from a search or a click on a subject heading.
        self.case_action = QWidget()
        case_action_layout = QVBoxLayout(self.case_action)
        case_action_layout.setContentsMargins(0, 0, 0, 0)
        case_action_layout.setSpacing(5)
        case_start_row = QHBoxLayout()
        self.case_start = QPushButton("Investigate selected problem")
        self.case_start.setObjectName("Primary")
        self.case_start.setToolTip("Run the available read-only checks for this problem. No internet access or automatic repairs.")
        self.case_start.clicked.connect(self._run_case)
        case_start_row.addWidget(self.case_start)
        case_start_row.addStretch(1)
        # Optional problem-specific target identity. Never passed to commands,
        # any model or cause/route evaluator; it is only a plain-text note.
        self.context_label = QLabel('')
        self.context_label.setWordWrap(True)
        self.context_input = QLineEdit()
        self.context_input.setMaxLength(80)
        self.context_input.setPlaceholderText('Optional application or device name (no passwords or file paths)')
        self.context_input.setToolTip('Legacy read-only context value; no free-form questions in Manual Diagnostics.')
        # Manual Diagnostics never interviews the user. The old free-form
        # context field remains internal for compatibility but is not shown.
        self.context_label.hide()
        self.context_input.hide()
        self.device_label = QLabel('')
        self.device_label.setWordWrap(True)
        self.device_selector = QComboBox()
        self.device_selector.setToolTip('Choose only among devices found in the local read-only inventory.')
        self.device_label.hide()
        self.device_selector.hide()
        self.device_selector.currentIndexChanged.connect(self._device_choice_changed)
        case_action_layout.addWidget(self.device_label)
        case_action_layout.addWidget(self.device_selector)
        case_action_layout.addLayout(case_start_row)
        self.case_hint = label("", "Muted")
        case_action_layout.addWidget(self.case_hint)
        related_row = QHBoxLayout()
        self.related_cases = QComboBox()
        self.related_cases.setMinimumWidth(200)
        self.related_cases.setToolTip("Linked hardware/software explanations are not proven causes.")
        self.related_cases.hide()
        self.related_button = QPushButton("Open related problem")
        self.related_button.clicked.connect(self._run_related_case)
        self.related_button.hide()
        related_row.addWidget(self.related_cases, 1)
        related_row.addWidget(self.related_button)
        case_action_layout.addLayout(related_row)
        self.case_action.hide()
        right_layout.addWidget(self.case_action)

        vertical = QSplitter(Qt.Orientation.Vertical)
        vertical.setChildrenCollapsible(False)
        right_layout.addWidget(vertical, 1)

        checks = QWidget(self)
        check_layout = QVBoxLayout(checks)
        check_layout.setContentsMargins(0, 0, 0, 4)
        check_layout.setSpacing(7)
        self.tree = WholeRowCheckTree()
        self.tree.setObjectName("DiagnosticChecks")
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["Diagnostic check", "What it examines", "Status"])
        self.tree.setRootIsDecorated(False)
        self.tree.setAlternatingRowColors(True)
        self.tree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.tree.setToolTip("Click anywhere on a ready row to select or deselect it. Click a planned row for details.")
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tree.setColumnWidth(0, 200)
        self.tree.itemChanged.connect(self._check_changed)
        self.tree.currentItemChanged.connect(self._check_focused)
        check_layout.addWidget(self.tree, 1)

        controls = QHBoxLayout()
        controls.setSpacing(7)
        self.selected_count = label("0 checks selected", "CountLabel", wrap=False)
        self.selected_count.setMinimumWidth(140)
        self.selected_count.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        controls.addWidget(self.selected_count)
        controls.addStretch(1)
        self.select_all_button = QPushButton("Select area")
        self.select_all_button.setToolTip("Select every ready check in this area.")
        self.select_all_button.clicked.connect(lambda: self._set_all(True))
        controls.addWidget(self.select_all_button)
        self.clear_button = QPushButton("Clear all")
        self.clear_button.setToolTip("Clear selected checks in every area.")
        self.clear_button.clicked.connect(self._clear_all)
        controls.addWidget(self.clear_button)
        self.run_button = QPushButton("Run selected checks")
        self.run_button.setObjectName("Primary")
        self.run_button.setEnabled(False)
        self.run_button.setToolTip("Run every selected check in the current area (read-only, no repairs).")
        self.run_button.clicked.connect(self._run_selected)
        controls.addWidget(self.run_button)
        self.rescan_button = QPushButton("Rescan")
        self.rescan_button.setObjectName("RescanButton")
        self.rescan_button.setEnabled(False)
        self.rescan_button.setToolTip(
            "Repeat the last completed or stopped scan with fresh evidence. "
            "No repairs or cached results."
        )
        self.rescan_button.clicked.connect(self._rescan)
        controls.addWidget(self.rescan_button)
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        self.stop_button.setToolTip("Stop after the current bounded-duration check completes.")
        self.stop_button.clicked.connect(self.cancel_scan)
        controls.addWidget(self.stop_button)
        check_layout.addLayout(controls)
        # Retain the proven scan/selection engine, but remove its duplicate
        # checkboxes and empty table from the user-facing Manual Diagnostics UI.
        # The documented Check info / Diagnosis / Solution pages take the space.
        checks.hide()
        controls.removeWidget(self.rescan_button)
        controls.removeWidget(self.stop_button)
        # Rescan and Stop are placed in the permanent results toolbar below,
        # including for a complete system scan with no particular case chosen.

        results = QFrame()
        results.setObjectName("ResultsPanel")
        result_layout = QVBoxLayout(results)
        result_layout.setContentsMargins(12, 10, 12, 9)
        result_layout.setSpacing(5)
        results_heading = QHBoxLayout()
        results_heading.addWidget(label("Diagnostic results", "CardTitle"))
        self.results_overview = label("Select a check to view its results.", "CountLabel")
        self.results_overview.setToolTip("Progress and results from the most recent scan.")
        self.batch_selector = QComboBox()
        self.batch_selector.setToolTip("View all results together or choose an individual check.")
        self.batch_selector.setMinimumWidth(155)
        self.batch_selector.setMaximumWidth(280)
        self.batch_selector.hide()
        self.batch_selector.currentIndexChanged.connect(self._batch_view_changed)
        results_heading.addStretch(1)
        results_heading.addWidget(self.batch_selector)
        self.copy_tab_button = QPushButton("Copy tab text")
        self.copy_tab_button.setToolTip("Copy the text from the current results tab. You can also select text and press Ctrl+C.")
        self.copy_tab_button.clicked.connect(self._copy_active_tab)
        results_heading.addWidget(self.copy_tab_button)
        results_heading.addWidget(self.rescan_button)
        results_heading.addWidget(self.stop_button)
        self.result_badge = label("NOT RUN", "ResultBadge")
        results_heading.addWidget(self.result_badge)
        result_layout.addLayout(results_heading)

        self.result_tabs = QTabWidget()
        self.result_tabs.setObjectName("ResultTabs")
        self.info_page, info_box = self._text_page()
        self.info_title = label("Choose a check", "ResultTitle")
        self.info_purpose = label("Select a check to see what it examines.", "CardBody")
        self.info_detail = label("", "CardBody")
        info_box.addWidget(self.info_title)
        info_box.addWidget(self.info_purpose)
        info_box.addWidget(self.info_detail)
        info_box.addStretch(1)
        self.result_tabs.addTab(self.info_page, "Check info")

        diagnosis_page, diagnosis_box = self._text_page()
        self.diagnosis_page = diagnosis_page
        self.diagnosis_title = label("Nothing checked yet", "ResultTitle")
        self.diagnosis_summary = label("You have not started this check yet.", "CardBody")
        self.diagnosis_explanation = label(
            "Select an available check and click Run selected checks.", "Muted"
        )
        diagnosis_box.addWidget(self.diagnosis_title)
        diagnosis_box.addWidget(self.diagnosis_summary)
        diagnosis_box.addWidget(self.diagnosis_explanation)
        diagnosis_box.addStretch(1)
        self.result_tabs.addTab(diagnosis_page, "Diagnosis")

        solution_page, solution_box = self._text_page()
        self.solution_page = solution_page
        self.solution_title = label("No suggested steps yet", "ResultTitle")
        self.solution_text = label(
            "Run an available check to see findings and manual next steps. "
            "Nothing is repaired automatically.", "CardBody"
        )
        solution_box.addWidget(self.solution_title)
        solution_box.addWidget(self.solution_text)
        # Fixed, trusted links only; never derive an href from a diagnosis or log.
        self.manual_tool_links = QLabel()
        self.manual_tool_links.setTextFormat(Qt.TextFormat.RichText)
        self.manual_tool_links.setOpenExternalLinks(True)
        self.manual_tool_links.setWordWrap(True)
        self.manual_tool_links.setVisible(False)
        solution_box.addWidget(self.manual_tool_links)
        solution_box.addStretch(1)
        self.result_tabs.addTab(solution_page, "Solution")

        log_page = QWidget()
        log_layout = QVBoxLayout(log_page)
        log_layout.setContentsMargins(5, 7, 5, 5)
        log_layout.setSpacing(5)
        self.evidence = QPlainTextEdit()
        self.evidence.setObjectName("EvidenceText")
        self.evidence.setReadOnly(True)
        self.evidence.setPlainText("No evidence collected yet. Logs are read only when their check is started.")
        log_layout.addWidget(self.evidence, 1)
        self.result_tabs.addTab(log_page, "Evidence / Logs")
        result_layout.addWidget(self.result_tabs, 1)

        # Structured headings, paragraphs and individual command blocks rather
        # than a giant paragraph. Copy uses the untouched plain-text source.
        for widget in (self.info_detail, self.diagnosis_summary, self.solution_text):
            widget.setTextFormat(Qt.TextFormat.RichText)
            # Links only appear in trusted source-authored documentation, not
            # in scan output or arbitrary user text.
            widget.setOpenExternalLinks(True)
        # Every panel, including solution commands, is selectable and copyable.
        for item in (self.info_title, self.info_purpose, self.info_detail,
                     self.diagnosis_title, self.diagnosis_summary,
                     self.diagnosis_explanation, self.solution_title, self.solution_text):
            if item not in (self.info_detail, self.diagnosis_summary, self.solution_text):
                item.setTextFormat(Qt.TextFormat.PlainText)
            flags = (Qt.TextInteractionFlag.TextSelectableByMouse |
                     Qt.TextInteractionFlag.TextSelectableByKeyboard)
            if item in (self.info_detail, self.diagnosis_summary, self.solution_text):
                flags |= (Qt.TextInteractionFlag.LinksAccessibleByMouse |
                          Qt.TextInteractionFlag.LinksAccessibleByKeyboard)
            item.setTextInteractionFlags(flags)
            item.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.evidence.setToolTip("Select a line with the mouse or use Ctrl+A / Ctrl+C to copy logs.")

        # Displayed only while a real Phase 2 task is running. Never fake a scan.
        self.progress = DiagnosticProgress()
        result_layout.addWidget(self.progress)
        # Keep the heading clean; put the run summary at the very bottom.
        result_layout.addWidget(self.results_overview)
        vertical.addWidget(results)
        vertical.setStretchFactor(0, 1)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([510, 1530])

        self._populate_categories()

    def _case_selected(self, *_):
        case_id = self._selected_case_id
        self.case_action.setVisible(bool(case_id))
        self._refresh_rescan_button()
        # No generic "Which GPU/headset/application?" questions. Read-only
        # discovery is used only where choosing an actual device can narrow
        # a target-scoped check. The GPU inventory runs automatically.
        self.context_label.hide()
        self.context_input.hide()
        if case_id != self._context_case_id:
            self.context_input.clear()
            self._context_case_id = case_id
            self._auto_device_id = None
            self.device_selector.hide()
            self.device_label.hide()
            self.device_selector.clear()
            self._lookup_generation += 1
            self._device_lookup_pending = bool(case_id and kind_for_case(case_id))
            if self._device_lookup_pending:
                worker = LocalDeviceDiscovery(case_id, self._lookup_generation, self)
                self._device_workers.add(worker)
                worker.discovered.connect(self._device_discovered)
                worker.finished.connect(lambda w=worker: self._finish_device_worker(w))
                worker.start()
        self._device_choice_changed()
        if not case_id:
            return
        self.case_hint.setText(
            'Finding connected devices…' if self._device_lookup_pending else
            'Read-only investigation. No automatic repairs.')

    def _finish_device_worker(self, worker):
        self._device_workers.discard(worker)
        worker.deleteLater()

    def _device_discovered(self, case_id: str, generation: int, choices: DeviceChoices):
        if generation != self._lookup_generation or case_id != self._selected_case_id:
            return  # Never carry the previous problem's device into a new scan.
        self._device_lookup_pending = False
        self._auto_device_id = None
        self.device_selector.blockSignals(True)
        self.device_selector.clear()
        if len(choices.options) > 1:
            self.device_label.setText(choices.label)
            self.device_selector.addItem('Choose a detected device…', None)
            for display, device_id in choices.options:
                self.device_selector.addItem(display, device_id)
            self.device_label.show()
            self.device_selector.show()
        elif len(choices.options) == 1:
            self._auto_device_id = choices.options[0][1]
            self.device_label.hide()
            self.device_selector.hide()
        else:
            # Nothing was found or a tool was missing: still run the case's
            # standard checks, never invent an empty-device diagnosis.
            self.device_label.hide()
            self.device_selector.hide()
        self.device_selector.blockSignals(False)
        if len(choices.options) > 1:
            self.case_hint.setText('Choose a listed device to narrow the read-only investigation.')
        elif len(choices.options) == 1:
            self.case_hint.setText('Detected device selected automatically. No automatic repairs.')
        else:
            self.case_hint.setText('Standard read-only checks are available; no device selection is required.')
        self._device_choice_changed()

    def _device_choice_changed(self, *_):
        chosen = self.device_selector.currentData() if self.device_selector.isVisible() else self._auto_device_id
        needs_choice = self.device_selector.isVisible() and chosen is None
        self.case_start.setEnabled(bool(self._selected_case_id) and not self._scan_running()
                                   and not self._device_lookup_pending and not needs_choice)

    def _select_case_in_navigation(self, case_id: str):
        if case_id not in case_catalog():
            return
        if case_id not in self._case_items:
            self.search.clear()  # A related case may be outside the current filter.
        item = self._case_items.get(case_id)
        if item is not None:
            self.categories.setCurrentItem(item)
            parent = item.parent()
            while parent is not None:
                parent.setExpanded(True)
                parent = parent.parent()
            self.categories.scrollToItem(item)

    def _run_related_case(self):
        case_id = self.related_cases.currentData()
        if case_id and not self._scan_running():
            # A related case may have its own detected-device choice. Navigate
            # first and let the user start that case after discovery finishes.
            self._select_case_in_navigation(case_id)

    def _run_case(self):
        case_id = self._selected_case_id
        if case_id and not self._scan_running() and self.case_start.isEnabled():
            self._run_case_id(case_id, topic_id=self._selected_topic_id)

    def _run_case_id(self, case_id, *, topic_id=None):
        if topic_id is not None:
            guide_for_topic(topic_id, case_id)  # no mismatched or invented topic
        checks, _ = plan_for_manual_case(case_id)
        from ..diagnostics.scan_plan132 import planned_case_probes
        probes = planned_case_probes(case_id, topic_id)
        self._clear_all()
        # User-approved v74 checks are scoped to this ONE run, and Rescan
        # asks again. A target path is never typed into a command or logged.
        guided_consent = False
        guided_path = None
        if case_id in CASES74:
            if case_id in PATH_CASES74:
                is_directory = case_id in (FOLDER_WRITE_CASE, VENV_CASE)
                if is_directory:
                    guided_path = QFileDialog.getExistingDirectory(
                        self, "Select only the affected folder for a read-only inspection")
                else:
                    guided_path, _ = QFileDialog.getOpenFileName(
                        self, "Select only the affected file for a read-only inspection")
                guided_consent = bool(guided_path)
                if guided_consent and case_id == APPIMAGE_CASE80:
                    reply = QMessageBox.question(
                        self, 'AppImage fingerprint — permission',
                        'Read the entire selected AppImage (up to 1 GiB) to calculate a SHA-256?\n'
                        'Only compare with the reference fingerprint you entered.\n'
                        'No upload, execution, package changes or repairs.\n'
                        'Permission applies only to this scan; Rescan asks again.',
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No)
                    guided_consent = reply == QMessageBox.StandardButton.Yes
            else:
                reply = QMessageBox.question(
                    self, 'Optional local evidence — permission',
                    'Inspect only the local process environment or selected configuration for this problem?\n'
                    'No passwords, clipboard content, network traffic, shell commands or repairs.\n'
                    'Consent applies to this scan only; Rescan asks again.',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No)
                guided_consent = reply == QMessageBox.StandardButton.Yes
        # The v75 external hostname/IP comparison cannot run without a
        # deliberate destination. Manual Diagnostics no longer asks the user
        # for a hostname/IP pair; never make an unrequested network query.
        net75_consent = False
        # A named case always runs with network OFF. Tools are selected by a
        # fixed reviewed catalog plan, not document commands or external model output.
        self._begin_scan(checks, allow_network=False, complete=False,
                         case_id=case_id, focused_probes=probes, topic_id=topic_id,
                         guided_path74=guided_path, guided_consent74=guided_consent,
                         network75_consent=net75_consent)

    def _refresh_rescan_button(self):
        previous = self._last_scan
        available = (previous is not None and not self._scan_running()
                     and previous.is_available_for(case_id=self._selected_case_id,
                                                   topic_id=self._selected_topic_id))
        self.rescan_button.setEnabled(available)
        if previous is not None and previous.case_id:
            self.rescan_button.setToolTip(
                "Repeat the last investigation with new read-only results. "
                "Select the original problem to enable Rescan."
            )
        else:
            self.rescan_button.setToolTip(
                "Repeat the last check batch with fresh measurements (not the current checkmarks). "
                "No old results are reused."
            )

    def _rescan(self):
        """Repeat only the last explicit scan plan; never act on a different case.

        The existing begin/worker path discards old check rows and focused-probe
        findings before producing a new outcome. Optional internet consent is
        requested AGAIN when applicable. No diagnostic or repair command is
        inferred from a previously displayed log or solution.
        """
        previous = self._last_scan
        if (previous is None or self._scan_running()
                or not previous.is_available_for(case_id=self._selected_case_id,
                                                  topic_id=self._selected_topic_id)):
            return
        if previous.case_id:
            # Regenerate the reviewed case plan; do not replay a user-controlled
            # command or any untrusted output from the previous scan.
            self._run_case_id(previous.case_id, topic_id=previous.topic_id)
            return
        network_permitted = False
        if previous.needs_network_permission:
            reply = QMessageBox.question(
                self, "Rescan — optional internet checks",
                "The last scan included optional website checks. Permission from "
                "that scan does not carry over.\n\n"
                "Do you allow the same optional internet checks this time? "
                "No logs or diagnostic results are uploaded.\n\n"
                "Choose No to rescan only the local checks.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            network_permitted = reply == QMessageBox.StandardButton.Yes
        checks = previous.checks_for_repeat(network_permitted=network_permitted)
        # A local-only rescan of a previously online full scan omits the two
        # optional website checks rather than treating permission as persistent.
        if not checks:
            QMessageBox.information(
                self, "Rescan", "The previous run contained only optional internet checks. "
                "No local checks remain to repeat without permission."
            )
            return
        self._begin_scan(checks, allow_network=network_permitted, complete=previous.complete)

    def _receive_case_result(self, result):
        if result.category_key == "focused" and result.check_key == "consented_dns75":
            self._network_result75 = result
        elif result.category_key == "focused" and result.check_key == "guided_evidence74":
            self._guided_result74 = result
        elif result.category_key == "focused" and result.check_key == "target_inventory69":
            self._target_inventory_result = result
        elif result.category_key == "focused":
            # Reviewed additional probes have a separate results namespace.
            self._case_probe_results.append(result)
        else:
            self.present_result(result)

    def _show_case_documentation(self, report=None):
        """Present source-authored case guidance without changing the proof gate.

        This deliberately renders conditional manual paths even for UNKNOWN
        results. It never calls shell, feeds the case assessor or changes the
        meaning of evidence in the Evidence / Logs tab.
        """
        case_id = self._selected_case_id
        if not case_id:
            self.manual_tool_links.hide()
            return
        pages = pages_for_case(case_id)
        case = case_catalog()[case_id]
        topic_key = getattr(self, '_selected_topic_id', None)
        guide = guide_for_topic(topic_key, case_id) if topic_key else None
        guide_text = guide.describe() if guide else ''
        guide_prefix = guide_text + '\n\n' if guide_text else ''
        self.info_title.setText(guide.title if guide else case['title'])
        self.info_purpose.setText('Check info — what the app checks')
        self.info_detail.setText(html_for_manual93(guide_prefix + pages.check_info))
        self.info_detail.setProperty('copyPlainText', guide_prefix + pages.check_info)
        # Show ACTUAL case-scoped check findings, while keeping generic system
        # errors, unverified links and raw logs out of this beginner summary.
        # Route approval still belongs exclusively to the reviewed assessor.
        self.diagnosis_title.setText('Diagnosis')
        translated = (display_case_report93(case_id, report, [*self._current_batch_results().values(), *self._case_probe_results])
                      if report else None)
        profile = getattr(self, 'system_profile', None)
        diagnosis_text = format_case_diagnosis130(
            case_id, report,
            [*self._current_batch_results().values(), *self._case_probe_results],
            completed=getattr(self, '_case_scan_completed', True),
            topic_id=topic_key,
            package_sources=(profile.data.get('packages')
                             if profile is not None
                             and 'applications' not in profile.due_areas()
                             else None))
        self.diagnosis_summary.setText(html_for_manual93(diagnosis_text))
        self.diagnosis_summary.setProperty('copyPlainText', diagnosis_text)
        self.diagnosis_explanation.clear()
        self.solution_title.setText('Solution — step-by-step troubleshooting')
        # Don't prepend an alarming "NO REPAIR HAS BEEN CONFIRMED" banner to a
        # useful manual guide when no particular repair was established.
        solution_content = ((translated[1] + '\n\n') if translated and report.proven_route
                            else '') + guide_prefix + pages.solution
        self.solution_text.setText(html_for_manual93(solution_content))
        self.solution_text.setProperty('copyPlainText', solution_content)
        links = [f'<a href="{ULT}">Universal Linux Terminal</a> (optional)']
        if pages.offers_ulsm:
            links.append(f'<a href="{ULSM}">Universal Linux Software Manager</a> (only for applicable package operations)')
        self.manual_tool_links.setText('Optional Linux tools: ' + ' · '.join(links))
        self.manual_tool_links.show()

    def _show_case_result(self):
        case_id = self._active_case_id
        if not case_id or self._selected_case_id != case_id:
            # A scan can finish after navigation moves to another problem.
            # Never mix its findings with the other problem's manual guide.
            return
        found = [self._results[pair] for pair in self._last_batch if pair in self._results]
        report = present_case(case_id, [*found, *self._case_probe_results],
                              completed=self._case_scan_completed, topic_id=self._active_topic_id,
                              target_note=self._active_target_note, target_inventory=self._target_inventory_result,
                              guided_result74=self._guided_result74,
                              network_result75=self._network_result75)
        self._case_view = report
        self.result_badge.setText({"supported":"EVIDENCE", "contradicted":"NOT SUPPORTED",
                                   "unknown":"UNKNOWN"}.get(report.status, "UNKNOWN"))
        self.result_badge.setProperty("resultState", "warning" if report.status == "supported" else "unknown")
        self.result_badge.style().unpolish(self.result_badge)
        self.result_badge.style().polish(self.result_badge)
        self.diagnosis_title.setText(report.title)
        self.diagnosis_summary.setText(report.diagnosis)
        self.diagnosis_explanation.setText("The Troubleshooter performed the available checks itself. No log analysis is required from you.")
        self.solution_title.setText("Evidence-based solution" if report.proven_route else
                                    "Safe physical connection check" if report.physical_check else
                                    "No proven repair yet")
        self.solution_text.setText(report.solution)
        self.evidence.setPlainText(report.evidence)
        self._show_case_documentation(report)
        self.evidence.setPlainText(display_case_report93(case_id, report, [*found, *self._case_probe_results])[2])
        self.related_cases.clear()
        for linked_id, title in report.related:
            self.related_cases.addItem(title, linked_id)
        self.related_cases.setVisible(bool(report.related))
        self.related_button.setVisible(bool(report.related))
        self.result_tabs.setCurrentIndex(1)
        self.diagnosis_page.verticalScrollBar().setValue(0)
        self.solution_page.verticalScrollBar().setValue(0)

    def _copy_active_tab(self):
        index = self.result_tabs.currentIndex()
        if index == 0:
            value = "\n\n".join((w.property("copyPlainText") or w.text()) for w in (self.info_title, self.info_purpose, self.info_detail) if w.text())
        elif index == 1:
            value = "\n\n".join((w.property("copyPlainText") or w.text()) for w in (self.diagnosis_title, self.diagnosis_summary, self.diagnosis_explanation) if w.text())
        elif index == 2:
            value = "\n\n".join((w.property("copyPlainText") or w.text()) for w in (self.solution_title, self.solution_text) if w.text())
        elif index == 3:
            value = self.evidence.toPlainText()
        else:
            value = self.evidence.toPlainText()
        QApplication.clipboard().setText(value)

    def _refresh_row_status(self, category: str, check: str):
        if not self._current or self._current.key != category:
            return
        for idx in range(self.tree.topLevelItemCount()):
            row = self.tree.topLevelItem(idx)
            if row.data(0, Qt.ItemDataRole.UserRole) != check:
                continue
            result = self._results.get((category, check))
            if result:
                row.setText(2, result.status.value)
                row.setToolTip(2, f"Last run: {result.status.value}. Click this row to view its findings.")
            else:
                row.setText(2, "Ready")
                row.setToolTip(2, "Ready for a manual read-only diagnostic scan.")
            break

    def _update_results_overview(self, running=None):
        if running is None:
            running = self._scan_running()
        if self._last_batch:
            if self._full_scan_batch and self._full_catalog_plan is not None:
                plan = self._full_catalog_plan
                done = sum(p in self._results for p in plan.checks)
                done += len({r.check_key for r in self._case_probe_results if r.check_key in plan.probes})
                total = len(plan.checks) + len(plan.probes)
                self.results_overview.setText(
                    f"Complete system scan · {done} of {total} checks completed · "
                    f"{plan.cases} problems and {plan.guides} guides in coverage report"
                    + (" · running" if running else ""))
            else:
                summary = batch_summary(self._last_batch, self._results, running=running)
                self.results_overview.setText(summary)
        else:
            self.results_overview.setText("Choose a check to see its result.")

    @staticmethod
    def _text_page():
        area = QScrollArea()
        area.setObjectName("ResultsScroll")
        area.setWidgetResizable(True)
        area.setFrameShape(QFrame.Shape.NoFrame)
        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(6, 8, 6, 6)
        layout.setSpacing(7)
        area.setWidget(inner)
        return area, layout

    def _populate_categories(self, *_):
        # Preserve current selection and expanded headings across filtering.
        previous = self._nav_selection
        expanded = set()
        for i in range(self.categories.topLevelItemCount()):
            root = self.categories.topLevelItem(i)
            if root.isExpanded():
                expanded.add(tuple(root.data(0, Qt.ItemDataRole.UserRole)))
            for j in range(root.childCount()):
                group = root.child(j)
                if group.isExpanded():
                    expanded.add(tuple(group.data(0, Qt.ItemDataRole.UserRole)))
        search = self.search.text().strip()
        groups = navigation_groups(search)
        self.categories.blockSignals(True)
        self.categories.clear()
        self._case_items = {}
        nodes: dict[tuple, QTreeWidgetItem] = {}
        shown = 0
        visible_guides = 0
        for domain, subjects in groups:
            count = sum(len(rows) for _, _, rows in subjects)
            guide_count = sum(len(matching_topics(search, domain=domain, heading=heading))
                              for heading, _, _ in subjects)
            root = QTreeWidgetItem([("Hardware" if domain == "hardware" else "Software")
                                    + f" ({count} problems, {guide_count} guides)"])
            root.setData(0, Qt.ItemDataRole.UserRole, ("domain", domain))
            self.categories.addTopLevelItem(root)
            nodes[("domain", domain)] = root
            for heading, cat_key, cases in subjects:
                topic_rows = matching_topics(search, domain=domain, heading=heading)
                visible_guides += len(topic_rows)
                group = QTreeWidgetItem([f"{heading} ({len(cases)} {'problem' if len(cases) == 1 else 'problems'} + {len(topic_rows)} guides)" if topic_rows else f"{heading} ({len(cases)})"])
                group.setData(0, Qt.ItemDataRole.UserRole, ("group", domain, heading, cat_key))
                group.setToolTip(0, f"Choose a documented problem or view {heading} checks.")
                root.addChild(group)
                nodes[("group", domain, heading, cat_key)] = group
                for topic in topic_rows:
                    leaf = QTreeWidgetItem([("• " if topic.introduced_version == CURRENT_GUIDE_VERSION else "") + topic.title])
                    leaf.setData(0, Qt.ItemDataRole.UserRole, ("topic", topic.key, topic.case_id))
                    leaf.setToolTip(0, "New in this version — " + topic.title if topic.introduced_version == CURRENT_GUIDE_VERSION
                                    else "Step-by-step guide using the existing safe diagnostic checks.")
                    group.addChild(leaf)
                    nodes[("topic", topic.key, topic.case_id)] = leaf
                for case_id, title in cases:
                    child = QTreeWidgetItem([title])
                    child.setData(0, Qt.ItemDataRole.UserRole, ("case", case_id))
                    child.setToolTip(0, case_catalog()[case_id]['symptom'])
                    group.addChild(child)
                    nodes[("case", case_id)] = child
                    self._case_items[case_id] = child
                    shown += 1
                group.setExpanded(bool(search) or (("group", domain, heading, cat_key) in expanded))
            root.setExpanded(bool(search) or (("domain", domain) in expanded)
                             or (not expanded and domain == "hardware" and not previous))
        self.categories.blockSignals(False)
        self.category_count.setText(
            f"{shown} of {len(case_catalog())} problems · {visible_guides} guides"
        )
        chosen = nodes.get(previous) if previous else None
        if chosen is None and search and (shown + visible_guides) == 1:
            chosen = next((entry for nav_key, entry in nodes.items()
                           if nav_key[0] in ('topic', 'case')), None)
        if chosen is None and groups:
            first_root = self.categories.topLevelItem(0)
            chosen = first_root.child(0) if first_root.childCount() else first_root
        if chosen is not None:
            parent = chosen.parent()
            while parent is not None:
                parent.setExpanded(True)
                parent = parent.parent()
            self.categories.blockSignals(True)
            self.categories.setCurrentItem(chosen)
            self.categories.blockSignals(False)
            self._category_changed(chosen, None)
        else:
            self._nav_selection = None
            self._selected_case_id = None
            self._current = None
            self._focused_key = None
            self._case_selected()
            self.title.setText("No matching problems")
            self.intro.setText("Try a broader search term.")
            self.tree.clear()
            self._reset_visible_results()
            self._update_count()

    def _category_changed(self, current, _previous):
        if current is None:
            return
        nav = current.data(0, Qt.ItemDataRole.UserRole)
        if not nav:
            return
        self._nav_selection = tuple(nav)
        kind = nav[0]
        self._selected_case_id = nav[1] if kind == "case" else nav[2] if kind == "topic" else None
        self._selected_topic_id = nav[1] if kind == "topic" else None
        self.related_cases.hide()
        self.related_button.hide()
        if not self._selected_case_id:
            self.manual_tool_links.hide()
        self._case_selected()
        if kind == "domain":
            domain = nav[1]
            self.title.setText("Hardware" if domain == "hardware" else "Software")
            self.intro.setText("Choose a problem or a step-by-step guide. ULTS checks what it can safely read, without changing your system.")
            self._current = None
            self.tree.clear()
            self._focused_key = None
            self._reset_visible_results()
            self._update_count()
            return
        if kind == "group":
            _, domain, heading, category_key = nav
            category = next((cat for cat in CATEGORIES if cat.key == category_key), None)
            intro = f"Choose a {domain} problem or guide, or select an individual read-only check."
            title = heading
        else:
            case_id = self._selected_case_id
            case = case_catalog()[case_id]
            # The subject is the parent of the case leaf and maps to the
            # existing check catalog; its checks are optional, not proof.
            group = current.parent().data(0, Qt.ItemDataRole.UserRole)
            category_key = group[3]
            category = next((cat for cat in CATEGORIES if cat.key == category_key), None)
            title = BY_KEY[self._selected_topic_id].title if self._selected_topic_id else case['title']
            intro = ("ULTS can run the available read-only checks for this problem. "
                     "You can also read the specific, step-by-step guide before starting."
                     if self._selected_topic_id else
                     "ULTS can investigate this problem using the available read-only checks. "
                     "The guide explains what the results can and cannot confirm.")
        if category is None:
            return
        self._show_category(category, title=title, intro=intro)
        if self._selected_case_id:
            self._show_case_documentation()
        else:
            self.manual_tool_links.hide()

    def _show_category(self, category: Category, *, title: str, intro: str):
        previous_key = self._current.key if self._current else None
        if forget_checks_on_area_change(self._selection, previous_key, category.key):
            # Switching areas forgets checkboxes, but completed results remain
            # available if the user returns to review them later.
            if not self._full_scan_batch:
                self._last_batch = ()
        self._current = category
        self.title.setText(title)
        self.intro.setText(intro)
        self._loading = True
        self.tree.clear()
        for check in category.checks:
            available = (category.key, check.key) in READY_CHECKS
            last_result = self._results.get((category.key, check.key))
            status = last_result.status.value if last_result else ("Ready · asks first" if (category.key, check.key) == ("network", "external") else "Ready") if available else "Planned"
            row = QTreeWidgetItem([check.title, check.purpose, status])
            if last_result:
                row.setToolTip(2, f"Last run: {last_result.status.value}. Click to view the result.")
            if available:
                row.setFlags(row.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            else:
                # Planned items remain focusable to read Check info, but cannot be checked.
                row.setFlags(row.flags() & ~Qt.ItemFlag.ItemIsUserCheckable)
                row.setToolTip(2, "This check has not been implemented yet; no diagnostic result will be invented.")
            if available:
                row.setCheckState(0, Qt.CheckState.Checked if check.key in self._selection[category.key] else Qt.CheckState.Unchecked)
            row.setData(0, Qt.ItemDataRole.UserRole, check.key)
            row.setToolTip(0, check.explanation)
            self.tree.addTopLevelItem(row)
        self._loading = False
        if self.tree.topLevelItemCount():
            self.tree.setCurrentItem(self.tree.topLevelItem(0))
        else:
            self._focused_key = None
            self._reset_visible_results()
        self._update_count()
        self._update_results_overview()
        self._setup_batch_selector()
        if self.batch_selector.isVisible():
            self._show_all_batch_results()

    def _check_changed(self, item, _column):
        if self._loading or self._current is None:
            return
        key = item.data(0, Qt.ItemDataRole.UserRole)
        if (self._current.key, key) not in READY_CHECKS:
            return
        selected = self._selection[self._current.key]
        if item.checkState(0) == Qt.CheckState.Checked:
            selected.add(key)
        else:
            selected.discard(key)
        # Ticking a new check is a fresh selection even when the same row
        # already has keyboard focus; show Check info rather than old logs.
        self.result_tabs.setCurrentIndex(0)
        self._update_count()

    def _check_focused(self, current, _previous):
        if current is None or self._current is None:
            self._focused_key = None
            self._reset_visible_results()
            return
        key = current.data(0, Qt.ItemDataRole.UserRole)
        check = next((candidate for candidate in self._current.checks if candidate.key == key), None)
        self._focused_key = check.key if check else None
        self.info_title.setText(check.title if check else "Choose a check")
        self.info_purpose.setText(check.purpose if check else "Select a check to learn more.")
        self.info_detail.setText(check.explanation if check else "")
        self._show_result(self._results.get((self._current.key, key)))
        if self._selected_case_id:
            self._show_case_documentation(self._case_view if self._active_case_id == self._selected_case_id else None)
        # A newly focused check begins with its plain-language explanation.
        self.result_tabs.setCurrentIndex(0)
        if self.batch_selector.isVisible():
            self.batch_selector.blockSignals(True)
            index = self.batch_selector.findData((self._current.key, key))
            if index >= 0:
                self.batch_selector.setCurrentIndex(index)
            self.batch_selector.blockSignals(False)

    def _reset_visible_results(self):
        self.info_title.setText("Choose a check")
        self.info_purpose.setText("Select a check to see what it examines.")
        self.info_detail.clear()
        self._show_result(None)

    def _current_batch_results(self):
        """Do not treat previous scans as fresh evidence for a new diagnosis."""
        return {pair: self._results[pair] for pair in self._last_batch if pair in self._results}

    def _show_result(self, result: DiagnosticResult | None):
        for page in (self.info_detail, self.diagnosis_summary, self.solution_text):
            page.setProperty('copyPlainText', None)
        if result is None:
            self.result_badge.setText("NOT RUN")
            self.result_badge.setProperty("resultState", "not-run")
            self.diagnosis_title.setText("Nothing checked yet")
            self.diagnosis_summary.setText("You have not started this check yet.")
            self.diagnosis_explanation.setText("Choose a ready check and press Run selected checks.")
            self.solution_title.setText("No suggested steps yet")
            self.solution_text.setText(
                "Run a check to see what you can try. The program will never change your computer for you."
            )
            self.evidence.setPlainText("No evidence collected yet. Logs are read only when you explicitly run the corresponding check.")
        else:
            self.result_badge.setText(result.status.value.upper())
            self.result_badge.setProperty("resultState", result.status.name.lower().replace("_", "-"))
            self.diagnosis_title.setText(diagnosis_heading(result))
            self.diagnosis_summary.setText(diagnosis_body(result, self._current_batch_results()))
            self.diagnosis_explanation.clear()
            self.solution_title.setText(solution_heading(result))
            self.solution_text.setText(solution_body(result, self._current_batch_results()))
            self.evidence.setPlainText(evidence_body(result))
        # A different check can contain much longer guidance. Always show the
        # beginning of its diagnosis/solution rather than retaining old scroll.
        self.diagnosis_page.verticalScrollBar().setValue(0)
        self.solution_page.verticalScrollBar().setValue(0)
        self.evidence.verticalScrollBar().setValue(0)
        # Refresh dynamic style when the status changes.
        self.result_badge.style().unpolish(self.result_badge)
        self.result_badge.style().polish(self.result_badge)
        self.result_badge.update()

    def present_result(self, result: DiagnosticResult):
        """Present a real, already-computed diagnostic result on the GUI thread."""
        category = next((cat for cat in CATEGORIES if cat.key == result.category_key), None)
        if category is None or not any(check.key == result.check_key for check in category.checks):
            raise ValueError("Result references an unknown diagnostic check")
        self._results[(result.category_key, result.check_key)] = result
        self._refresh_row_status(result.category_key, result.check_key)
        self._update_results_overview()
        if self._active_case_id:
            # Do not expose generic per-check remedies as a proven case remedy.
            return
        if self._full_scan_batch:
            # A complete scan may emit 72 results. Avoid re-rendering 250
            # catalog entries for every individual worker signal.
            return
        if self.batch_selector.isVisible() and self.batch_selector.currentData() == "__all__":
            self._show_all_batch_results()
        elif self._current and self._current.key == result.category_key and self._focused_key == result.check_key:
            self._show_result(result)

    def begin_diagnostic_activity(self, description="Running diagnostic checks…", *, completed=None, total=None):
        """Display activity only during a real read-only operation."""
        self.progress.start(description, completed=completed, total=total)

    def finish_diagnostic_activity(self):
        self.progress.stop()

    def _update_count(self):
        count = sum(len(selection) for selection in self._selection.values())
        self.selected_count.setText(f"{count} checks selected")
        self.run_button.setEnabled(count > 0 and not self._scan_running())

    def _set_all(self, enable: bool):
        if not self._current:
            return
        self._loading = True
        for idx in range(self.tree.topLevelItemCount()):
            row = self.tree.topLevelItem(idx)
            if (self._current.key, row.data(0, Qt.ItemDataRole.UserRole)) in READY_CHECKS:
                row.setCheckState(0, Qt.CheckState.Checked if enable else Qt.CheckState.Unchecked)
        self._loading = False
        self._selection[self._current.key] = (
            {check.key for check in self._current.checks if (self._current.key, check.key) in READY_CHECKS} if enable else set()
        )
        self._update_count()


    def _clear_all(self):
        for selection in self._selection.values():
            selection.clear()
        self._set_all(False)

    def _scan_running(self) -> bool:
        return self._worker is not None

    def _run_complete_scan(self):
        """One-click beginner scan using the same read-only diagnostic bridge."""
        if self._scan_running():
            return
        offline = complete_catalog_plan(READY_CHECKS)
        online_count = len(complete_system_plan(READY_CHECKS, include_network=True)) - len(offline.checks)
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Complete system scan")
        dialog.setIcon(QMessageBox.Icon.Information)
        dialog.setText("Check your computer automatically")
        dialog.setInformativeText(
            f"This will run {len(offline.checks)} shared system checks and "
            f"{len(offline.probes)} supplementary checks across {offline.cases} documented problems "
            f"and {offline.guides} symptom guides. Repeated measurements run only once. "
            "It only reads information: no settings, files or programs will be changed.\n\n"
            f"The {online_count} optional website checks are OFF by default. "
            "If you include them, Linux may ask its DNS service for the address "
            "of www.mozilla.org and make one secure connection to that website. "
            "Network services may see the website name and your public IP address. "
            "No logs, files or other diagnostic results are uploaded. "
            "Permission applies only to this scan.\n\n"
            "A full scan may take some time. You can stop between checks. "
            "The results do not automatically fix anything."
        )
        network_choice = QCheckBox("Include the optional website and internet checks")
        network_choice.setChecked(False)
        dialog.setCheckBox(network_choice)
        start = dialog.addButton("Start scan", QMessageBox.ButtonRole.AcceptRole)
        dialog.addButton(QMessageBox.StandardButton.Cancel)
        dialog.setDefaultButton(QMessageBox.StandardButton.Cancel)
        dialog.exec()
        if dialog.clickedButton() is not start:
            return
        include_network = network_choice.isChecked()
        checks = complete_system_plan(READY_CHECKS, include_network=include_network)
        # Complete scans need no manual checkmarks and must not carry old ones.
        self._clear_all()
        self._begin_scan(checks, allow_network=include_network, complete=True)

    def _run_selected(self):
        if self._scan_running() or self._current is None:
            return
        checks = selected_plan(self._selection, READY_CHECKS)
        if not checks:
            return
        allow_network = False
        permitted_probes = []
        if ("network", "dns") in checks:
            permitted_probes.append(
                "• Website name check: ask your normal DNS service for the address of www.mozilla.org. "
                "The DNS service may see the site name and your public network address."
            )
        if ("network", "external") in checks:
            permitted_probes.append(
                "• External connectivity: make one secure connection to www.mozilla.org (port 443). "
                "The website can see your public IP address."
            )
        if permitted_probes:
            reply = QMessageBox.question(
                self, "Optional network test — your permission",
                "You selected a test that may contact a network outside your computer:\n\n"
                + "\n\n".join(permitted_probes)
                + "\n\nNo logs, files or other diagnostic results are uploaded. "
                "You can say No: those tests will not contact the network and all other "
                "checks will still run. Permission applies only to this scan.\n\n"
                "Do you allow the listed test(s) this time?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            allow_network = reply == QMessageBox.StandardButton.Yes
        self._begin_scan(checks, allow_network=allow_network, complete=False)

    def _begin_scan(self, checks, *, allow_network=False, complete=False, case_id=None, focused_probes=(), topic_id=None, guided_path74=None, guided_consent74=False, network75_consent=False):
        """Common execution path for manually chosen and complete system scans."""
        if self._scan_running() or not checks:
            return
        if complete:
            self._full_catalog_plan = complete_catalog_plan(READY_CHECKS, include_network=allow_network)
            # A local-only Rescan may exclude network requests from the prior
            # plan; never reinstate them through a cached permission.
            focused_probes = self._full_catalog_plan.probes
        else:
            self._full_catalog_plan = None
        self._last_scan = ManualScanReplay(
            checks=tuple(checks), case_id=case_id, topic_id=topic_id if case_id else None,
            focused_probes=tuple(focused_probes), complete=complete,
            included_network=bool(allow_network),
        )
        self._active_case_id = case_id
        # Use only a locally discovered, optionally selected inventory ID.
        # Never treat an arbitrary name or an expected GPU as proof.
        chosen_device = (self.device_selector.currentData() if self.device_selector.isVisible()
                         else self._auto_device_id)
        self._active_target_note = (safe_target_note(chosen_device)
                                    if case_id and context_question(case_id) else None)
        # Preserve a separate, one-scan full input for the v74 comparison.
        # Existing target inventories receive only the hostname, never the
        # user's claimed expected IP address.
        self._guided_note74 = self._active_target_note  # v75 must use full host + IP pair
        if (case_id in ('software35.network.hostname-resolution', 'network.dns-problem') and self._active_target_note
                and len(self._active_target_note.split()) == 2):
            self._active_target_note = self._active_target_note.split()[0]
        self._active_topic_id = topic_id if case_id else None
        self._case_probe_results = []
        self._target_inventory_result = None
        self._guided_result74 = None
        self._guided_path74 = guided_path74
        self._guided_consent74 = bool(guided_consent74)
        self._network_consent75 = bool(network75_consent)
        self._network_result75 = None
        self._case_scan_completed = False
        self._case_view = None
        if case_id is None:
            self.related_cases.hide()
            self.related_button.hide()
        self._full_scan_batch = complete
        self._full_scan_online = complete and allow_network
        self._last_batch = checks
        for pair in checks:
            self._results.pop(pair, None)  # Never present stale results as current.
        self._setup_batch_selector()
        if len(checks) > 1 and not case_id:
            if complete:
                self.info_title.setText('Complete system scan')
                self.info_purpose.setText('Preparing safe local checks across the catalog…')
                self.info_detail.clear()
                self.diagnosis_title.setText('System scan in progress')
                self.diagnosis_summary.setText('Collecting local measurements. No repairs are performed.')
                self.diagnosis_explanation.clear()
                self.solution_title.setText('Waiting for the results')
                self.solution_text.setText('Results will appear when the scan finishes.')
                self.evidence.setPlainText('Measurements are being collected.')
                self.result_tabs.setCurrentIndex(1)
            else:
                self._show_all_batch_results()
        elif case_id:
            self.diagnosis_title.setText("Investigating " + (BY_KEY[topic_id].title if topic_id else case_catalog()[case_id]['title']))
            self.diagnosis_summary.setText("The Troubleshooter is collecting safe local evidence. No action is required from you.")
            self.diagnosis_explanation.clear()
            self.solution_title.setText("Investigation in progress")
            self.solution_text.setText("No repair advice before evidence has been assessed.")
            self.evidence.setPlainText("Collecting read-only evidence. No network access.")
            self.result_tabs.setCurrentIndex(1)
        for category_key, check_key in checks:
            self._refresh_row_status(category_key, check_key)
        self._update_results_overview(running=True)
        if len(checks) == 1 and not case_id and self._current and (self._current.key, self._focused_key) in checks:
            self._show_result(None)
            self.result_badge.setText("RUNNING")
        elif len(checks) > 1:
            self.result_badge.setText("RUNNING")
        from ..diagnostics.target_evidence69 import supports_target_probe
        self._target_pending = bool(case_id and self._active_target_note and supports_target_probe(case_id))
        from ..diagnostics.consented_network75 import NETWORK_CASES75
        self._completed, self._run_total = 0, (len(checks) + len(focused_probes)
            + int(self._target_pending) + int(bool(case_id in CASES74))
            + int(bool(case_id in NETWORK_CASES75 and self._guided_note74)))
        self.begin_diagnostic_activity(
            "Running complete system scan…" if complete else "Running read-only checks…",
            completed=0, total=self._run_total)
        if complete:
            self.selected_count.setText(f"Complete system scan: {self._run_total} local checks")
        self.run_button.setEnabled(False)
        self.rescan_button.setEnabled(False)
        self.complete_scan_button.setEnabled(False)
        self.case_start.setEnabled(False)
        self.related_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.search.setEnabled(False)
        self.context_input.setEnabled(False)
        self.device_selector.setEnabled(False)
        self.categories.setEnabled(False)
        self.tree.setEnabled(False)
        self.select_all_button.setEnabled(False)
        self.clear_button.setEnabled(False)
        self.batch_selector.setEnabled(False)
        self._worker = DiagnosticWorker(checks, self, allow_network=allow_network,
                                        focused_probes=focused_probes,
                                        target_case_id=case_id if self._target_pending else None,
                                        target_note=self._active_target_note if self._target_pending else None,
                                        guided_case_id=case_id if case_id in CASES74 else None,
                                        guided_note=self._guided_note74,
                                        guided_path=self._guided_path74,
                                        guided_consent=self._guided_consent74,
                                        network75_case=case_id if case_id in NETWORK_CASES75 and self._guided_note74 else None,
                                        network75_note=self._guided_note74,
                                        network75_consent=self._network_consent75)
        self._worker.result_ready.connect(self._receive_case_result if (case_id or complete) else self.present_result)
        self._worker.progress_changed.connect(self._progress_changed)
        self._worker.finished.connect(self._scan_completed)
        self._worker.start()

    def _progress_changed(self, completed: int, total: int):
        self._completed = completed
        self.progress.update_count(completed, total,
                                   "Running complete system scan…" if self._full_scan_batch
                                   else "Running read-only checks…")

    def cancel_scan(self):
        if self._worker:
            self._worker.requestInterruption()
            self.stop_button.setEnabled(False)
            self.progress.update_count(self._completed, self._run_total, "Stopping after current check…")

    def _scan_completed(self):
        self.finish_diagnostic_activity()
        self.search.setEnabled(True)
        self.context_input.setEnabled(True)
        self.device_selector.setEnabled(True)
        self.categories.setEnabled(True)
        self.tree.setEnabled(True)
        self.select_all_button.setEnabled(True)
        self.clear_button.setEnabled(True)
        self.complete_scan_button.setEnabled(True)
        self.related_button.setEnabled(True)
        self.batch_selector.setEnabled(True)
        self.stop_button.setEnabled(False)
        completed = self._completed
        total = self._run_total
        old_worker = self._worker
        if self.system_profile is not None and old_worker is not None:
            # Persist only measurements that actually completed. Cancelled,
            # external, and focused results never mark a full area fresh.
            observed = [self._results[p] for p in self._last_batch if p in self._results]
            self.system_profile.update(observed, scanned_areas=tuple({p[0] for p in self._last_batch}))
        from ..diagnostics.consented_network75 import NETWORK_CASES75
        # Compare against the exact plan RUN by this worker, including any
        # topic-specific extra probes.  Comparing against the base case plan
        # incorrectly marked every Steam guide scan as interrupted in v131.
        from ..diagnostics.scan_plan132 import scan_finished_as_planned
        self._case_scan_completed = bool(self._active_case_id and old_worker is not None
            and scan_finished_as_planned(
                requested_checks=self._last_batch,
                received_checks=(pair for pair in self._last_batch if pair in self._results),
                requested_probes=self._last_scan.focused_probes if self._last_scan else (),
                received_probes=(result.check_key for result in self._case_probe_results
                                 if result.category_key == 'focused'),
                stopped=old_worker.isInterruptionRequested(),
                progress_completed=completed,
                progress_total=total,
                target_ok=(not self._target_pending or self._target_inventory_result is not None),
                guided_ok=(self._active_case_id not in CASES74 or self._guided_result74 is not None),
                network_ok=(self._active_case_id not in NETWORK_CASES75 or not self._guided_note74
                            or self._network_result75 is not None),
            ))
        self._worker = None
        self._case_selected()  # Re-enable case action and Rescan AFTER the worker stops.
        if old_worker is not None:
            old_worker.deleteLater()
        # Always display what actually ran, rather than whatever row happened
        # to be highlighted before the scan. This matters when only one check
        # was ticked but another row (often the first row) had keyboard focus.
        if self.batch_selector.isVisible() and not self._active_case_id:
            self.batch_selector.blockSignals(True)
            self.batch_selector.setCurrentIndex(0)  # All selected results first.
            self.batch_selector.blockSignals(False)
            self._show_all_batch_results()
            if self._full_scan_batch:
                # Beginners see the high-level finding rather than a long raw log.
                self.result_tabs.setCurrentIndex(1)
        elif len(self._last_batch) == 1:
            category_key, check_key = self._last_batch[0]
            if self._current and self._current.key == category_key:
                for index in range(self.tree.topLevelItemCount()):
                    row = self.tree.topLevelItem(index)
                    if row.data(0, Qt.ItemDataRole.UserRole) == check_key:
                        self.tree.setCurrentItem(row)
                        self._focused_key = check_key
                        break
                self._show_result(self._results.get((category_key, check_key)))
        self._update_count()
        self._update_results_overview(running=False)
        if completed < total and len(self._last_batch) == 1 and self._current and self._focused_key and (self._current.key, self._focused_key) not in self._results:
            self.diagnosis_explanation.setText(
                f"Scan stopped: {completed} of {total} selected checks finished. "
                "Unfinished checks have no diagnostic result."
            )
        if self._active_case_id:
            self._show_case_result()
        self.scan_finished.emit()

    def _setup_batch_selector(self):
        """One combined result plus each named check; no check silently hidden."""
        current = self._current.key if self._current else None
        visible = bool(current and len(self._last_batch) > 1 and not self._active_case_id)
        self.batch_selector.blockSignals(True)
        self.batch_selector.clear()
        if visible:
            self.batch_selector.addItem(
                "Complete system scan" if self._full_scan_batch else "All selected checks", "__all__"
            )
            if self._full_scan_batch:
                self.batch_selector.addItem("Catalog coverage · all problems", "__catalog__")
                for key in self._full_catalog_plan.probes if self._full_catalog_plan else ():
                    self.batch_selector.addItem("Supplementary · " + key.replace('_', ' '), ('focused', key))
            for pair in self._last_batch:
                category = next((c for c in CATEGORIES if c.key == pair[0]), None)
                check = next((c for c in category.checks if c.key == pair[1]), None) if category else None
                title = (category.title + " · " if category else "") + (check.title if check else pair[1])
                self.batch_selector.addItem(title, pair)
        self.batch_selector.setVisible(visible)
        self.batch_selector.blockSignals(False)

    def _select_check_area(self, category_key: str) -> bool:
        """Move result navigation to a matching subject in the new hierarchy."""
        for i in range(self.categories.topLevelItemCount()):
            root = self.categories.topLevelItem(i)
            for j in range(root.childCount()):
                group = root.child(j)
                data = group.data(0, Qt.ItemDataRole.UserRole)
                if data and data[0] == "group" and data[3] == category_key:
                    root.setExpanded(True)
                    self.categories.setCurrentItem(group)
                    self.categories.scrollToItem(group)
                    return True
        return False

    def _batch_view_changed(self, _index):
        if self._current is None or not self.batch_selector.isVisible():
            return
        key = self.batch_selector.currentData()
        if key == "__all__":
            self._show_all_batch_results()
            return
        if key == "__catalog__" and self._full_scan_batch:
            self._show_catalog_coverage()
            return
        if isinstance(key, tuple) and len(key) == 2:
            category_key, check_key = key
            if category_key == 'focused' and self._full_scan_batch:
                focused = next((r for r in self._case_probe_results if r.check_key == check_key), None)
                if focused is None:
                    self._show_result(None)
                else:
                    self.info_title.setText('Supplementary local check · ' + check_key.replace('_', ' '))
                    self.info_purpose.setText('Additional evidence, not an automatic diagnosis.')
                    self.info_detail.clear()
                    self._show_result(focused)
                    facts = [line[5:].replace('_', ' ').replace('=', ': ')
                             for line in focused.evidence if line.startswith('FACT:')]
                    details = ('A local read-only observation was collected.\n\n'
                               + ('\n'.join('• ' + item for item in facts[:18]) if facts else
                                  'No structured measurements were available.'))
                    self.diagnosis_title.setText('Supplementary observation')
                    self.diagnosis_summary.setText(html_for_manual93(details))
                    self.diagnosis_summary.setProperty('copyPlainText', details)
                    self.solution_title.setText('How to use this result')
                    advice = ('This observation does not prove that a particular '
                              'app or device is failing. Select the matching problem '
                              'in the left-hand list for guided next steps.')
                    self.solution_text.setText(html_for_manual93(advice))
                    self.solution_text.setProperty('copyPlainText', advice)
                    self.evidence.setPlainText(evidence_body(focused))
                return
            if self._current.key != category_key:
                # A search filter may hide the selected result's category.
                # Clear it so the user can jump to that saved check.
                if not self._select_check_area(category_key):
                    self.search.clear()
                    self._select_check_area(category_key)
            for i in range(self.tree.topLevelItemCount()):
                item = self.tree.topLevelItem(i)
                if item.data(0, Qt.ItemDataRole.UserRole) == check_key:
                    self.tree.setCurrentItem(item)
                    self._show_result(self._results.get(key))
                    return

    def _show_catalog_coverage(self):
        """Every documented case is listed, without claiming its symptom exists."""
        if self._full_catalog_plan is None:
            return
        covered = scan_catalog_coverage(self._full_catalog_plan, self._results,
                                        self._case_probe_results,
                                        finished=self._worker is None)
        text = (f"{covered['total_cases']} documented problems; "
                f"{covered['total_guides']} additional guides use those same cases.\n\n"
                f"Reviewed local indicators (impact unverified): {covered['signals']}\n"
                f"Specific local evidence: {covered['specific']}\n"
                f"General observations only: {covered['general']}\n"
                f"Inconclusive: {covered['unknown']}\n"
                f"Not measured: {covered['missing']}\n\n"
                "A scan cannot prove an unreported symptom. Choose a specific "
                "problem to perform any required target-specific test.\n\n" + covered['text'])
        self.info_title.setText("Coverage of all documented problems")
        self.info_purpose.setText("Read-only measurements, reused across the catalog")
        self.info_detail.setText(html_for_manual93(text))
        self.info_detail.setProperty('copyPlainText', text)
        self.diagnosis_title.setText("Catalog coverage, not 250 individual diagnoses")
        self.diagnosis_summary.setText(html_for_manual93(text))
        self.diagnosis_summary.setProperty('copyPlainText', text)
        self.diagnosis_explanation.clear()
        self.solution_title.setText("What to do next")
        self.solution_text.setText(html_for_manual93(
            "Choose the matching problem in the left-hand list for a targeted investigation. "
            "A general scan alone does not establish a diagnosis or authorize a repair."))
        self.evidence.setPlainText(text)

    def _show_complete_catalog_results(self):
        """Compact scan overview; never concatenate full logs into QLabel."""
        plan = self._full_catalog_plan
        if plan is None:
            return
        stopped = bool(self._worker and self._worker.isInterruptionRequested())
        info, diagnosis, solution, logs, coverage = full_scan_pages(
            plan, self._results, self._case_probe_results, CATEGORIES, stopped=stopped)
        all_rows = [self._results[x] for x in self._last_batch if x in self._results]
        all_rows += [x for x in self._case_probe_results if x.check_key in plan.probes]
        if not all_rows:
            state, badge = 'not-run', 'NOT RUN'
        elif (self._worker is None and len(self._results.keys() & set(plan.checks))
              + len({r.check_key for r in self._case_probe_results if r.check_key in plan.probes})
              < len(plan.checks) + len(plan.probes)):
            state, badge = 'unknown', 'INCOMPLETE'
        elif any(x.status == ResultStatus.PROBLEM for x in all_rows):
            state, badge = 'problem', 'PROBLEM'
        elif any(x.status == ResultStatus.WARNING for x in all_rows):
            state, badge = 'warning', 'WARNING'
        elif any(x.status == ResultStatus.UNKNOWN for x in all_rows):
            state, badge = 'unknown', 'UNKNOWN'
        else:
            state, badge = 'ok', 'COMPLETE'
        self.result_badge.setText(badge)
        self.result_badge.setProperty('resultState', state)
        self.result_badge.style().unpolish(self.result_badge)
        self.result_badge.style().polish(self.result_badge)
        self.info_title.setText('Complete system scan')
        self.info_purpose.setText(f'{len(plan.checks)} shared checks + {len(plan.probes)} supplementary checks')
        self.info_detail.setText(html_for_manual93(info))
        self.info_detail.setProperty('copyPlainText', info)
        self.diagnosis_title.setText('What the complete scan found')
        self.diagnosis_summary.setText(html_for_manual93(diagnosis))
        self.diagnosis_summary.setProperty('copyPlainText', diagnosis)
        self.diagnosis_explanation.clear()
        self.solution_title.setText('Recommended next steps')
        self.solution_text.setText(html_for_manual93(solution))
        self.solution_text.setProperty('copyPlainText', solution)
        self.evidence.setPlainText(logs)
        for page in (self.diagnosis_page, self.solution_page):
            page.verticalScrollBar().setValue(0)

    def _show_all_batch_results(self):
        if not self._current or len(self._last_batch) < 2:
            return
        if self._full_scan_batch and self._full_catalog_plan is not None:
            self._show_complete_catalog_results()
            return
        report_checks = (prioritize_check_results(self._last_batch, self._results)
                         if self._full_scan_batch else self._last_batch)
        views = combined_check_view(report_checks, self._results, CATEGORIES,
                                    include_categories=self._full_scan_batch)
        if self._full_scan_batch:
            overview = complete_scan_at_a_glance(self._last_batch, self._results)
            if not self._full_scan_online:
                overview += ("\nThe two optional internet checks were not included. "
                             "No website connection tests were started.")
            views = (views[0], overview + "\n\n" + scan_cause_summary(self._last_batch, self._results) + "\n" + views[1],
                     views[2], views[3])
        from ..results import ResultStatus
        found = [self._results[pair] for pair in self._last_batch if pair in self._results]
        counts = {status: sum(r.status == status for r in found) for status in ResultStatus}
        if not found:
            state = "not-run"
            text = "RUNNING" if self._scan_running() else "NOT RUN"
        elif counts[ResultStatus.PROBLEM]:
            state, text = "problem", "PROBLEM"
        elif counts[ResultStatus.WARNING]:
            state, text = "warning", "WARNING"
        elif counts[ResultStatus.UNKNOWN]:
            state, text = "unknown", "UNKNOWN"
        elif counts[ResultStatus.INFO]:
            state, text = "info", "INFO"
        elif counts[ResultStatus.NOT_RUN]:
            state, text = "not-run", "NOT RUN"
        else:
            state, text = "ok", "OK"
        self.result_badge.setText(text)
        self.result_badge.setProperty("resultState", state)
        self.result_badge.style().unpolish(self.result_badge)
        self.result_badge.style().polish(self.result_badge)
        self.info_title.setText(
            f"Complete system scan — {len(self._last_batch)} checks" if self._full_scan_batch
            else f"All {len(self._last_batch)} selected checks"
        )
        self.info_purpose.setText(
            ("Automatic read-only checks across all areas. No changes or repairs were made. "
             "Checks needing attention appear first. Select any check in the menu above "
             "to read its own result."
             + (" The two optional internet tests were skipped." if not self._full_scan_online else ""))
            if self._full_scan_batch else
            "Every selected check runs separately. Use the menu above or click a check row to read its own result."
        )
        self.info_detail.setText(views[0])
        self.diagnosis_title.setText(
            "Complete system scan results" if self._full_scan_batch
            else "Results for every selected check"
        )
        self.diagnosis_summary.setText(views[1])
        self.diagnosis_explanation.clear()
        self.solution_title.setText("Solutions and advice for these checks" if any(r.status != ResultStatus.OK for r in found) else "No repairs suggested for these checks")
        self.solution_text.setText(views[2])
        self.evidence.setPlainText(views[3])
        for page in (self.diagnosis_page, self.solution_page):
            page.verticalScrollBar().setValue(0)
