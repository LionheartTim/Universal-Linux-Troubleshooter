"""Launch from `python -m universal_linux_troubleshooter`."""

import sys


def main():
    from PySide6.QtWidgets import QApplication
    from .ui.main_window import MainWindow
    from .ui.theme import STYLESHEET
    from .app_identity import APPLICATION_NAME, DESKTOP_ID, application_icon

    app = QApplication(sys.argv)
    app.setApplicationName(APPLICATION_NAME)
    app.setDesktopFileName(DESKTOP_ID)
    app.setWindowIcon(application_icon())
    app.setOrganizationName("LionheartTim")
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)
    window = MainWindow()
    window.showMaximized()  # Open with both the checks and the results clearly visible.
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
