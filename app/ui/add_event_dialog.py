from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QLineEdit, QTextEdit, QDialogButtonBox,
    QTimeEdit, QDateEdit, QCheckBox, QComboBox, QHBoxLayout
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

        layout.addWidget(QLabel("Title"))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g. Dentist appointment")
        layout.addWidget(self.title_input)

        layout.addWidget(QLabel("Date"))
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(selected_date or QDate.currentDate())
        layout.addWidget(self.date_input)

        layout.addWidget(QLabel("Time"))
        self.time_input = QTimeEdit()
        self.time_input.setTime(QTime.currentTime())
        self.time_input.setDisplayFormat("hh:mm AP")
        layout.addWidget(self.time_input)

        layout.addWidget(QLabel("Notes"))
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Optional notes...")
        self.notes_input.setFixedHeight(80)
        layout.addWidget(self.notes_input)

        # --- reminder row ---
        reminder_row = QHBoxLayout()

        self.remind_checkbox = QCheckBox("Remind me before")
        self.remind_checkbox.setChecked(False)
        self.remind_checkbox.toggled.connect(self.on_remind_toggled)

        self.remind_combo = QComboBox()
        self.remind_combo.setEditable(True)
        self.remind_combo.addItems(["5", "10", "15", "30", "60"])
        self.remind_combo.setCurrentText("15")
        self.remind_combo.setEnabled(False)  # disabled until checkbox ticked
        self.remind_combo.lineEdit().setPlaceholderText("mins")

        reminder_row.addWidget(self.remind_checkbox)
        reminder_row.addWidget(self.remind_combo)
        reminder_row.addWidget(QLabel("mins"))
        reminder_row.addStretch()
        layout.addLayout(reminder_row)

        # --- Checkbox row ---#
        self.priority_checkbox = QCheckBox("Mark as priority")
        self.priority_checkbox.setChecked(False)
        layout.addWidget(self.priority_checkbox)

        # --- buttons ---
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def on_remind_toggled(self, checked: bool):
        self.remind_combo.setEnabled(checked)

    def get_event(self) -> Event | None:
        title = self.title_input.text().strip()
        if not title:
            return None

        # if checkbox unticked, remind_mins = 0 (notify exactly at event time)
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
            time=self.time_input.time().toString("HH:mm"),
            notes=self.notes_input.toPlainText().strip() or None,
            remind_mins=remind_mins,
            is_priority=self.priority_checkbox.isChecked()  
        )