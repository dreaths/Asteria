from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QLineEdit, QTextEdit, QDialogButtonBox,
    QDateEdit, QCheckBox, QComboBox, QHBoxLayout, QMessageBox
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

        # --- Time --- replaced QTimeEdit with dropdowns  # ← CHANGED
        layout.addWidget(QLabel("Time"))
        time_row = QHBoxLayout()

        self.hour_combo = QComboBox()
        self.hour_combo.addItems([str(h).zfill(2) for h in range(1, 13)])

        self.minute_combo = QComboBox()
        self.minute_combo.addItems([str(m).zfill(2) for m in range(0, 60, 5)])
        self.minute_combo.setEditable(True)  # allow typing custom minutes

        self.ampm_combo = QComboBox()
        self.ampm_combo.addItems(["AM", "PM"])

        # pre-fill with current time
        now = QTime.currentTime()
        hour_12 = now.hour() % 12 or 12
        self.hour_combo.setCurrentText(str(hour_12).zfill(2))
        nearest_min = (now.minute() // 5) * 5
        self.minute_combo.setCurrentText(str(nearest_min).zfill(2))
        self.ampm_combo.setCurrentText("AM" if now.hour() < 12 else "PM")

        time_row.addWidget(self.hour_combo)
        time_row.addWidget(QLabel(":"))
        time_row.addWidget(self.minute_combo)
        time_row.addWidget(self.ampm_combo)
        time_row.addStretch()
        layout.addLayout(time_row)

        # --- Notes ---
        layout.addWidget(QLabel("Notes"))
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Optional notes...")
        self.notes_input.setFixedHeight(80)
        layout.addWidget(self.notes_input)

        # --- Reminder row ---
        reminder_row = QHBoxLayout()
        self.remind_checkbox = QCheckBox("Remind me before")
        self.remind_checkbox.setChecked(False)
        self.remind_checkbox.toggled.connect(self.on_remind_toggled)
        self.remind_checkbox.setStyleSheet("""
        QCheckBox::indicator:checked {
            background-color: #C9A8E0;
            border: 2px solid #C9A8E0;
            border-radius: 3px;
        }
        QCheckBox::indicator:unchecked {
            border: 2px solid #C9A8E0;
            border-radius: 3px;
            background-color: transparent;
        }
    """)

        self.remind_combo = QComboBox()
        self.remind_combo.setEditable(True)
        self.remind_combo.addItems(["5", "10", "15", "30", "60"])
        self.remind_combo.setCurrentText("15")
        self.remind_combo.setEnabled(False)
        self.remind_combo.lineEdit().setPlaceholderText("mins")

        reminder_row.addWidget(self.remind_checkbox)
        reminder_row.addWidget(self.remind_combo)
        reminder_row.addWidget(QLabel("mins"))
        reminder_row.addStretch()
        layout.addLayout(reminder_row)

        # --- Priority ---
        self.priority_checkbox = QCheckBox("Mark as priority")
        self.priority_checkbox.setChecked(False)
        layout.addWidget(self.priority_checkbox)
        self.priority_checkbox.setStyleSheet("""
        QCheckBox::indicator:checked {
            background-color: #C9A8E0;
            border: 2px solid #C9A8E0;
            border-radius: 3px;
        }
        QCheckBox::indicator:unchecked {
            border: 2px solid #C9A8E0;
            border-radius: 3px;
            background-color: transparent;
        }
    """)

        # --- Buttons ---
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.on_save)  # ← CHANGED — custom save handler
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def on_remind_toggled(self, checked: bool):
        self.remind_combo.setEnabled(checked)

    def on_save(self):  # ← NEW — validates before accepting
        if not self.title_input.text().strip():
            QMessageBox.warning(self, "Missing Title", "Please enter a title for the event.")
            return
        self.accept()

    def get_event(self) -> Event | None:
        title = self.title_input.text().strip()
        if not title:
            return None

        # build 24hr time string from dropdowns  # ← CHANGED
        hour = int(self.hour_combo.currentText())
        minute_text = self.minute_combo.currentText().strip()
        try:
            minute = int(minute_text)
        except ValueError:
            minute = 0
        ampm = self.ampm_combo.currentText()
        if ampm == "PM" and hour != 12:
            hour += 12
        elif ampm == "AM" and hour == 12:
            hour = 0
        time_str = f"{hour:02d}:{minute:02d}"

        if self.remind_checkbox.isChecked():
            try:
                remind_mins = int(self.remind_combo.currentText())
            except ValueError:
                remind_mins = 0
        else:
            remind_mins = 0

        return Event(
            title=title,
            date=self.date_input.date().toString("yyyy-MM-dd"),
            time=time_str,
            notes=self.notes_input.toPlainText().strip() or None,
            remind_mins=remind_mins,
            is_priority=self.priority_checkbox.isChecked()
        )