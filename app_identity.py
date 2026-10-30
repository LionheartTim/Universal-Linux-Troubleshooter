"""Canonical desktop identity and the selected ULTS application icon."""

from pathlib import Path

DESKTOP_ID = 'io.github.LionheartTim.UniversalLinuxTroubleshooter'
APPLICATION_NAME = 'Universal Linux Troubleshooter'
ICON_DIRECTORY = Path(__file__).resolve().parent / 'assets' / 'icons'
ICON_SIZES = (16, 24, 32, 48, 64, 128, 256, 512, 1024)

def icon_file(size: int = 256) -> Path:
    """Return the packaged raster icon; no theme or working-dir dependency."""
    return ICON_DIRECTORY / f'ults-{size}.png'

def application_icon():
    """Make a scalable QIcon from all packaged versions of the chosen artwork."""
    from PySide6.QtCore import QSize
    from PySide6.QtGui import QIcon
    icon = QIcon()
    for size in ICON_SIZES:
        filename = icon_file(size)
        if filename.is_file():
            icon.addFile(str(filename), QSize(size, size))
    return icon
