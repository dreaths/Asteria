from datetime import datetime, timedelta
from PyQt6.QtCore import QTimer, QObject
from app.data.event_repository import EventRepository
from app.services.notifier import fire_toast


class ReminderScheduler(QObject):
    def __init__(self, repo: EventRepository, parent=None):
        super().__init__(parent)
        self.repo = repo

        self._timer = QTimer(self)
        self._timer.setInterval(60_000)  # every 60 seconds
        self._timer.timeout.connect(self.check_reminders)

    def start(self):
        self.check_reminders()  # run once immediately on startup
        self._timer.start()

    def check_reminders(self):
        now = datetime.now()
        window_end = now + timedelta(seconds=59)

        # format as SQLite datetime strings
        now_str = now.strftime("%Y-%m-%d %H:%M")
        window_str = window_end.strftime("%Y-%m-%d %H:%M")

        due = self.repo.get_due_reminders(now_str, window_str)
        for event in due:
            fire_toast(
                title=event.title,
                message=f"Reminder — starts at {event.time}"
            )
            self.repo.mark_notified(event.id)