import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QCalendarWidget,
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
)
from PyQt6.QtGui import QTextCharFormat, QColor
from PyQt6.QtCore import Qt
from app.data.database import init_db
from app.data.event_repository import EventRepository
from app.ui.add_event_dialog import AddEventDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Asteria")
        self.repo = EventRepository()

        self.calendar = QCalendarWidget()
        self.calendar.setVerticalHeaderFormat(
            QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader
        )

        weekend_format = QTextCharFormat()
        weekend_format.setForeground(QColor("#B5483D"))
        self.calendar.setWeekdayTextFormat(Qt.DayOfWeek.Saturday, weekend_format)
        self.calendar.setWeekdayTextFormat(Qt.DayOfWeek.Sunday, weekend_format)

        self.add_btn = QPushButton("Add Event")
        self.add_btn.clicked.connect(self.open_add_event)

        sidebar = QVBoxLayout()
        sidebar.addWidget(QLabel("Today's Reminders"))
        sidebar.addWidget(self.add_btn)
        sidebar.addStretch()

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.calendar, stretch=3)
        main_layout.addLayout(sidebar, stretch=1)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def open_add_event(self):
        selected = self.calendar.selectedDate()
        dialog = AddEventDialog(parent=self, selected_date=selected)
        if dialog.exec():
            event = dialog.get_event()
            if event:
                self.repo.add_event(event)


def main():
    init_db()
    app = QApplication(sys.argv)
    app.setStyleSheet("""
    QMainWindow {
        background-color: #F5F1FA;
    }
    QCalendarWidget {
        background-color: #F5F1FA;
        border: none;
    }
    QCalendarWidget QWidget#qt_calendar_navigationbar {
        background-color: #FFFFFF;
        border-bottom: 1px solid #E5DCEF;
    }
    QCalendarWidget QToolButton {
        color: #4A4258;
        background-color: transparent;
        border: none;
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 13px;
    }
    QCalendarWidget QToolButton:hover {
        background-color: #C9A8E0;
        color: #FFFFFF;
    }
    QCalendarWidget QAbstractItemView:enabled {
        background-color: #F5F1FA;
        color: #4A4258;
        selection-background-color: #C9A8E0;
        selection-color: #FFFFFF;
        outline: none;
        gridline-color: #E5DCEF;
    }
    QCalendarWidget QAbstractItemView:disabled {
        color: #B7ABC6;
    }
    QPushButton {
        background-color: #FFFFFF;
        color: #4A4258;
        border: 1px solid #F2A88A;
        border-radius: 6px;
        padding: 6px;
    }
    QPushButton:hover {
        background-color: #F2A88A;
        color: #FFFFFF;
    }
""")
    window = MainWindow()
    window.resize(900, 650)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()