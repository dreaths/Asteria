import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow,
    QWidget, QHBoxLayout, QVBoxLayout,
    QSystemTrayIcon, QScrollArea
)
from PyQt6.QtGui import QTextCharFormat, QColor
from PyQt6.QtCore import Qt, QTimer
from app.data.database import init_db
from app.data.event_repository import EventRepository
from app.ui.add_event_dialog import AddEventDialog
from app.ui.asteria_calendar import AsteriaCalendar
from app.ui.sidebar import Sidebar
from app.services.scheduler import ReminderScheduler
from app.ui.tray import SystemTray
from app.data.models import Event


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Asteria")
        self.repo = EventRepository()
        self.scheduler = ReminderScheduler(repo=self.repo, parent=self)
        self.scheduler.reminders_fired.connect(self.refresh)
        self.scheduler.start()

        self.calendar = AsteriaCalendar()
        self.calendar.setVerticalHeaderFormat(
            AsteriaCalendar.VerticalHeaderFormat.NoVerticalHeader
        )

        weekend_format = QTextCharFormat()
        weekend_format.setForeground(QColor("#B5483D"))
        self.calendar.setWeekdayTextFormat(Qt.DayOfWeek.Saturday, weekend_format)
        self.calendar.setWeekdayTextFormat(Qt.DayOfWeek.Sunday, weekend_format)

        # wrap calendar in scroll area for clipping
        self.calendar_scroll = QScrollArea()
        self.calendar_scroll.setWidget(self.calendar)
        self.calendar_scroll.setWidgetResizable(True)
        self.calendar_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.calendar_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.calendar_scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        self.calendar.currentPageChanged.connect(self._adjust_calendar_scroll)
        QTimer.singleShot(100, self._adjust_calendar_scroll)

        self.sidebar = Sidebar()
        self.sidebar.add_btn.clicked.connect(self.open_add_event)
        self.sidebar.event_deleted.connect(self.delete_event)
        self.calendar.selectionChanged.connect(self.on_date_selected)
        self.sidebar.reminder_dismissed.connect(self.dismiss_reminder)
        self.sidebar.all_reminders_dismissed.connect(self.dismiss_all)
        self.sidebar.task_added.connect(self.add_task)
        self.sidebar.task_toggled.connect(self.toggle_task)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.calendar_scroll, stretch=3)
        main_layout.addWidget(self.sidebar, stretch=1)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        self.tray = SystemTray(main_window=self, parent=self)

        self.refresh()

    def _adjust_calendar_scroll(self):
        from PyQt6.QtCore import QDate
        cal = self.calendar
        first_day = QDate(cal.yearShown(), cal.monthShown(), 1)
        days_from_monday = first_day.dayOfWeek() - 1
        monday_of_first_row = first_day.addDays(-days_from_monday)

        all_overflow = all(
            monday_of_first_row.addDays(i).month() != cal.monthShown()
            for i in range(7)
        )

        if all_overflow:
            cell_h = cal._cell_height()
            self.calendar_scroll.verticalScrollBar().setValue(cell_h)
        else:
            self.calendar_scroll.verticalScrollBar().setValue(0)

    def refresh(self):
        all_events = self.repo.get_all_events_by_date()
        self.calendar.set_events(all_events)
        self.on_date_selected()
        self.refresh_missed()

    def on_date_selected(self):
        date = self.calendar.selectedDate()
        date_str = date.toString("yyyy-MM-dd")
        events = self.repo.get_events_for_date(date_str)
        checklist = [e for e in events if e.is_checklist]
        events = [e for e in events if not e.is_checklist]
        self.sidebar.update_for_date(date, events)
        self.sidebar.update_checklist(checklist)

    def open_add_event(self):
        selected = self.calendar.selectedDate()
        dialog = AddEventDialog(parent=self, selected_date=selected)
        if dialog.exec():
            event = dialog.get_event()
            if event:
                self.repo.add_event(event)
                self.refresh()

    def delete_event(self, event_id: int):
        self.repo.delete_event(event_id)
        self.refresh()

    def refresh_missed(self):
        missed = self.repo.get_missed_reminders()
        self.sidebar.update_missed_reminders(missed)

    def dismiss_reminder(self, event_id: int):
        self.repo.dismiss_reminder(event_id)
        self.refresh_missed()

    def dismiss_all(self):
        self.repo.dismiss_all_reminders()
        self.refresh_missed()

    def add_task(self, date_str: str, text: str):
        task = Event(
            title=text,
            date=date_str,
            time=None,
            notes=None,
            is_checklist=True
        )
        self.repo.add_event(task)
        self.on_date_selected()

    def toggle_task(self, event_id: int, is_done: bool):
        self.repo.toggle_done(event_id, is_done)
        self.on_date_selected()

    def closeEvent(self, event):
        from PyQt6.QtWidgets import QMessageBox

        msg = QMessageBox(self)
        msg.setWindowTitle("Close Asteria")
        msg.setText("What would you like to do?")

        minimize_btn = msg.addButton("Minimize to Tray", QMessageBox.ButtonRole.AcceptRole)
        quit_btn = msg.addButton("Quit", QMessageBox.ButtonRole.DestructiveRole)
        msg.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)

        msg.exec()
        clicked = msg.clickedButton()

        if clicked == minimize_btn:
            event.ignore()
            self.hide()
            self.tray.tray.showMessage(
                "Asteria",
                "Running in the background. Double-click the tray icon to reopen.",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        elif clicked == quit_btn:
            QApplication.quit()
        else:
            event.ignore()


def main():
    init_db()
    app = QApplication(sys.argv)
    app.setStyleSheet("""
    QWidget {
        background-color: #F5F1FA;
        color: #4A4258;
    }
    QCalendarWidget {
        background-color: #F5F1FA;
        border: none;
    }
    QCalendarWidget QWidget#qt_calendar_navigationbar {
        background-color: #FFFFFF;
        border-bottom: 1px solid #E5DCEF;
        padding: 4px;
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
    QFrame#MissedCard {
        background-color: #FFF0EE;
        border: 1px solid #F2C4BB;
        border-radius: 8px;
    }
    QLineEdit {
        background-color: #FFFFFF;
        border: 1px solid #E5DCEF;
        border-radius: 6px;
        padding: 4px 8px;
        color: #4A4258;
    }
    QLineEdit:focus {
        border: 1px solid #C9A8E0;
    }
    QPushButton {
        background-color: #FFFFFF;
        color: #4A4258;
        border: 1px solid #F2A88A;
        border-radius: 6px;
        padding: 6px 12px;
    }
    QPushButton:hover {
        background-color: #F2A88A;
        color: #FFFFFF;
    }
    QScrollBar:vertical {
        background: #F5F1FA;
        width: 6px;
        border-radius: 3px;
    }
    QScrollBar::handle:vertical {
        background: #C9A8E0;
        border-radius: 3px;
    }
    QScrollArea {
        background-color: #F5F1FA;
        border: none;
    }
""")
    window = MainWindow()
    window.resize(1280, 720)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()