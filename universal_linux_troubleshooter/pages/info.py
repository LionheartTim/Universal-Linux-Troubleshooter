"""Information and original GitHub project links; no AI dependency."""

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea


SOFTWARE_MANAGER_URL = "https://github.com/LionheartTim/Universal-Linux-Software-Manager"
TERMINAL_URL = "https://github.com/LionheartTim/Universal-Linux-Terminal"


class InfoPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 14, 14, 14)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        column = QVBoxLayout(container)
        column.setSpacing(12)
        column.addWidget(self._line("Universal Linux Troubleshooter", "SectionTitle"))
        column.addWidget(self._line(
            "Use Manual Diagnostics to investigate hardware and software problems with the built-in "
            "troubleshooting guide and safe, read-only checks. Repairs remain your decision.", "CardBody"))
        column.addWidget(self._line("Related Universal Linux applications", "SectionTitle"))
        column.addWidget(self._line(
            "Universal Linux Software Manager provides a graphical way to install, remove and update supported software. "
            "Universal Linux Terminal helps you understand and run terminal commands yourself.", "CardBody"))
        for name, url in (("Universal Linux Software Manager", SOFTWARE_MANAGER_URL),
                          ("Universal Linux Terminal", TERMINAL_URL)):
            row = QHBoxLayout()
            button = QPushButton("Open " + name + " on GitHub")
            button.setToolTip(url)
            button.clicked.connect(lambda checked=False, address=url: QDesktopServices.openUrl(QUrl(address)))
            row.addWidget(button)
            row.addStretch(1)
            column.addLayout(row)
        column.addWidget(self._line(
            "The guide covers 250 problems. Not every problem has a fully validated automatic cause assessment. "
            "An uncertain result must never be presented as a confirmed diagnosis or a successful repair.", "Muted"))
        column.addStretch(1)
        scroll.setWidget(container)
        outer.addWidget(scroll)

    @staticmethod
    def _line(value: str, style: str) -> QLabel:
        text = QLabel(value)
        text.setObjectName(style)
        text.setWordWrap(True)
        return text
