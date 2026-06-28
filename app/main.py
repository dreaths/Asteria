import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow,
    QWidget, QHBoxLayout
)
from PyQt6.QtGui import QTextCharFormat, QColor
from PyQt6.QtCore import Qt
from app.data.database import init_db
from app.data.event_repository import EventRepository
from app.ui.add_event_dialog import AddEventDialog
from app.ui.asteria_calendar import AsteriaCalendar
from app.ui.sidebar import Sidebar
from app.services.scheduler import ReminderScheduler


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Asteria")
        self.repo = EventRepository()
        self.scheduler = ReminderScheduler(repo=self.repo, parent=self)
        self.scheduler.start()

        self.calendar = AsteriaCalendar()
        self.calendar.setVerticalHeaderFormat(
            AsteriaCalendar.VerticalHeaderFormat.NoVerticalHeader
        )

        weekend_format = QTextCharFormat()
        weekend_format.setForeground(QColor("#B5483D"))
        self.calendar.setWeekdayTextFormat(Qt.DayOfWeek.Saturday, weekend_format)
        self.calendar.setWeekdayTextFormat(Qt.DayOfWeek.Sunday, weekend_format)

        self.sidebar = Sidebar()
        self.sidebar.add_btn.clicked.connect(self.open_add_event)
        self.calendar.selectionChanged.connect(self.on_date_selected)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.calendar, stretch=3)
        main_layout.addWidget(self.sidebar, stretch=1)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.refresh()

    def refresh(self):
        all_events = self.repo.get_all_events_by_date()
        self.calendar.set_events(all_events)
        self.on_date_selected()

    def on_date_selected(self):
        date = self.calendar.selectedDate()
        date_str = date.toString("yyyy-MM-dd")
        events = self.repo.get_events_for_date(date_str)
        self.sidebar.update_for_date(date, events)

    def open_add_event(self):
        selected = self.calendar.selectedDate()
        dialog = AddEventDialog(parent=self, selected_date=selected)
        if dialog.exec():
            event = dialog.get_event()
            if event:
                self.repo.add_event(event)
                self.refresh()


def main():
    init_db()
    app = QApplication(sys.argv)
    app.setStyleSheet("""
    QWidget {
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
    QFrame#EventCard {
        background-color: #FFFFFF;
        border: 1px solid #E5DCEF;
        border-radius: 8px;
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
    window.resize(1280, 720)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()