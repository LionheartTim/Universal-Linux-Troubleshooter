"""Compact, reusable 12-block activity indicator; purely UI-driven.

The widget is hidden when idle. A future read-only diagnostics controller may
call start(), update_count(), and stop(). It does not execute or simulate checks.
"""

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget, QFrame


class DiagnosticProgress(QWidget):
    BLOCK_COUNT = 12
    # Light blue, blue, dark blue, blue in a continuous repeating wave.
    SHADES = ("#63c0ff", "#328dd4", "#1d4b7a", "#328dd4")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DiagnosticProgress")
        self._phase = 0
        self._running = False
        self._completed = None
        self._total = None
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 5, 0, 4)
        row.setSpacing(7)
        self.caption = QLabel("Running diagnostic checks…")
        self.caption.setObjectName("ProgressLabel")
        row.addWidget(self.caption, 1)
        self.blocks = []
        for index in range(self.BLOCK_COUNT):
            block = QFrame(self)
            block.setFixedSize(13, 9)
            block.setObjectName("ProgressBlock")
            self.blocks.append(block)
            row.addWidget(block)
        self.timer = QTimer(self)
        self.timer.setInterval(105)
        self.timer.timeout.connect(self._advance)
        self._paint_blocks()
        self.hide()

    def _paint_blocks(self):
        for index, block in enumerate(self.blocks):
            shade = self.SHADES[(index - self._phase) % len(self.SHADES)]
            block.setStyleSheet(f"background-color: {shade}; border-radius: 2px;")

    def _advance(self):
        self._phase = (self._phase + 1) % len(self.SHADES)
        self._paint_blocks()

    def start(self, description="Running diagnostic checks…", *, completed=None, total=None):
        """Display an indeterminate activity indicator for a real running task."""
        self._running = True
        self._phase = 0
        self._completed = completed
        self._total = total
        self._update_caption(description)
        self._paint_blocks()
        self.show()
        self.timer.start()

    def _update_caption(self, description):
        if self._completed is not None and self._total is not None and self._total > 0:
            self.caption.setText(f"{description}  ·  {self._completed} of {self._total} completed")
        else:
            # No invented percentages when progress cannot be measured.
            self.caption.setText(description)

    def update_count(self, completed, total, description="Running diagnostic checks…"):
        """Update a true item count supplied by a future diagnostic controller."""
        if not self._running:
            return
        if not isinstance(total, int) or total < 1:
            raise ValueError("total must be a positive integer")
        if not isinstance(completed, int) or not 0 <= completed <= total:
            raise ValueError("completed must be within [0, total]")
        self._completed, self._total = completed, total
        self._update_caption(description)

    def stop(self):
        self._running = False
        self.timer.stop()
        self.hide()
