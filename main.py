import sys
import os
import ctypes

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from gui import LoginWindow


def resource_path(relative_path):
    """Find resources in development and in the packaged application."""
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("HIV ARV System")

    icon_path = resource_path(
        os.path.join("assets", "hiv_arv_system_logo.png")
    )
    app_icon = QIcon(icon_path)
    app.setWindowIcon(app_icon)

    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "hivarv.system.app"
        )

    window = LoginWindow()
    window.setWindowIcon(app_icon)
    window.showMaximized()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
