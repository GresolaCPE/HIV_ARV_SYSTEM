import sys, os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from gui import LoginWindow
import ctypes 


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("HIV ARV System")
    app.setWindowIcon(QIcon(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "hiv_arv_system_logo.png")))
    
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "hivarv.system.app"
    )

    window = LoginWindow()
    window.showMaximized()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
