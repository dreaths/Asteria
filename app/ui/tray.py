from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QObject
from pathlib import Path
import sys

def get_icon_path() -> Path: 
    if getattr(sys, 'frozen', False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).parent.parent
    return base / "assets" / "asteria.ico"
ICON_PATH = get_icon_path()


class SystemTray(QObject):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window

        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon(str(ICON_PATH)))
        self.tray.setToolTip("Asteria")

        # double click tray icon to show window
        self.tray.activated.connect(self.on_tray_activated)

        # right-click context menu
        menu = QMenu(self.main_window)

        show_action = QAction("Open Asteria")
        show_action.triggered.connect(self.show_window)
        menu.addAction(show_action)

        menu.addSeparator()

        quit_action = QAction("Quit Asteria")
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(quit_action)

        self.tray.setContextMenu(menu)
        self.tray.show()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window()

    def show_window(self):
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()