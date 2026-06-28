import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QCalendarWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calendar App")
        self.setCentralWidget(QCalendarWidget())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())