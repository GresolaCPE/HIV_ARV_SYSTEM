import sys
from PyQt6.QtWidgets import QApplication
from gui import LoginWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("HIV ARV System")

    window = LoginWindow()
    window.showMaximized()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()