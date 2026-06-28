from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QSpinBox, QDialogButtonBox,
    QTimeEdit, QDateEdit
)
from PyQt6.QtCore import QDate, QTime
from app.data.models import Event
class AddEventDialog(QDialog):
    def __init__(self, parent=None, selected_date: QDate = None):
        super().__init__(parent)
        self.setWindowTitle("Add Event")
        self.setMinimumWidth(360)

        layout = QVBoxLayout()
        layout.setSpacing(12)

        # --- Title ---
        layout.addWidget(QLabel("Title"))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g. Dentist appointment")
        layout.addWidget(self.title_input)

        # --- Date ---
        layout.addWidget(QLabel("Date"))
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(selected_date or QDate.currentDate())
        layout.addWidget(self.date_input)

        # --- Time ---
        layout.addWidget(QLabel("Time"))
        self.time_input = QTimeEdit()
        self.time_input.setTime(QTime.currentTime())
        self.time_input.setDisplayFormat("hh:mm AP")
        layout.addWidget(self.time_input)

        # --- Notes ---
        layout.addWidget(QLabel("Notes"))
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Optional notes...")
        self.notes_input.setFixedHeight(80)
        layout.addWidget(self.notes_input)

        # --- Reminder ---
        layout.addWidget(QLabel("Remind me (minutes before)"))
        self.remind_input = QSpinBox()
        self.remind_input.setRange(1, 1440)  # 1 min to 24 hours
        self.remind_input.setValue(15)
        layout.addWidget(self.remind_input)

        # --- Buttons ---
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)
    def get_event(self) -> Event | None:
            title = self.title_input.text().strip()
            if not title:
                return None  # don't save empty titles

            return Event(
                title=title,
                date=self.date_input.date().toString("yyyy-MM-dd"),
                time=self.time_input.time().toString("HH:mm"),
                notes=self.notes_input.toPlainText().strip() or None,
                remind_mins=self.remind_input.value()
            )