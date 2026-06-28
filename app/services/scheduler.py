from datetime import datetime, timedelta
from PyQt6.QtCore import QTimer, QObject, pyqtSignal
from app.data.event_repository import EventRepository
from app.services.notifier import fire_toast


class ReminderScheduler(QObject):
    reminders_fired = pyqtSignal()
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

        now_str = now.strftime("%Y-%m-%d %H:%M")
        window_str = window_end.strftime("%Y-%m-%d %H:%M")
        print(f"Checking reminders at {now_str}")
        due = self.repo.get_due_reminders(now_str, window_str)
        print(f"Found {len(due)} due reminders")
        for event in due:
            print(f"Firing for: {event.title}")
            if event.remind_mins > 0:
                # this is the "early warning" toast
                fire_toast(
                    title=f"Upcoming: {event.title}",
                    message=f"Starting in {event.remind_mins} mins at {event.time}"
                )
            else:
                # notify exactly at event time
                fire_toast(
                    title=event.title,
                    message=f"Starting now at {event.time}"
                )
            self.repo.mark_notified(event.id)
            self.repo.mark_done(event.id)
            if due:
                self.reminders_fired.emit()