"""Reusable visual helpers - no host system access."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QScrollArea


def label(text: str, name: str = "", *, wrap: bool = True) -> QLabel:
    item = QLabel(text)
    item.setWordWrap(wrap)
    if name:
        item.setObjectName(name)
    return item


def card(*, accent: bool = False) -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame()
    frame.setObjectName("AccentCard" if accent else "Card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(19, 18, 19, 18)
    layout.setSpacing(12)
    return frame, layout


def page() -> tuple[QWidget, QVBoxLayout]:
    widget = QWidget()
    widget.setObjectName("ScrollContent")
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(10, 18, 10, 20)
    layout.setSpacing(18)
    return widget, layout


def scrollable(widget: QWidget) -> QScrollArea:
    scroller = QScrollArea()
    scroller.setObjectName("PageScroll")
    scroller.setWidgetResizable(True)
    scroller.setFrameShape(QFrame.Shape.NoFrame)
    scroller.setWidget(widget)
    return scroller
