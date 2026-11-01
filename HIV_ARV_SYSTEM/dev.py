
import sys
 
from PyQt6.QtWidgets import QApplication
 
from gui import DashboardWindow
 
 
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("HIV ARV System")
 
    user = {
        "staff_id": "STF-001",
        "full_name": "Angel Ramirez",
        "username": "angel",
    }
 
    window = DashboardWindow(user)
    window.showMaximized()
 
    sys.exit(app.exec())
 
 
if __name__ == "__main__":
    main()
 


