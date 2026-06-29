from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QFrame, QSizePolicy, QHBoxLayout, QLineEdit, QCheckBox
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime


class EventCard(QFrame):
    delete_requested = pyqtSignal(int)

    def __init__(self, event, parent=None, is_missed: bool = False):
        super().__init__(parent)
        self.event = event
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("EventCard")

        layout = QVBoxLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(10, 8, 10, 8)

        top_row = QHBoxLayout()
        time_label = QLabel(event.time or "All day")
        time_font = QFont()
        time_font.setPointSize(8)
        time_label.setFont(time_font)
        time_label.setStyleSheet("color: #9B89B0;")

        delete_btn = QPushButton("✕")
        delete_btn.setFixedSize(20, 20)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #9B89B0;
                font-size: 10px;
                padding: 0;
            }
            QPushButton:hover { color: #B5483D; }
        """)
        delete_btn.clicked.connect(lambda: self.delete_requested.emit(event.id))
        top_row.addWidget(time_label)
        top_row.addStretch()
        top_row.addWidget(delete_btn)
        layout.addLayout(top_row)

        title_label = QLabel(event.title)
        title_font = QFont()
        title_font.setPointSize(10)
        title_font.setBold(not event.is_done and not is_missed)
        title_font.setStrikeOut(event.is_done or is_missed)
        title_label.setFont(title_font)
        title_label.setWordWrap(True)

        if event.is_priority and not event.is_done and not is_missed:
            title_label.setText("● " + event.title)
            title_label.setStyleSheet("color: #E91E8C; font-weight: bold;")
        elif event.is_done or is_missed:
            title_label.setStyleSheet("color: #9B89B0;")
        else:
            title_label.setStyleSheet("color: #4A4258;")
        layout.addWidget(title_label)

        date_label = QLabel(event.date)
        date_font = QFont()
        date_font.setPointSize(8)
        date_label.setFont(date_font)
        date_label.setStyleSheet("color: #9B89B0;")
        layout.addWidget(date_label)

        if event.notes:
            notes_label = QLabel(event.notes)
            notes_label.setWordWrap(True)
            notes_label.setStyleSheet("color: #6B5F7A; font-size: 9pt;")
            layout.addWidget(notes_label)

        self.setLayout(layout)


class MissedReminderCard(QFrame):
    dismiss_requested = pyqtSignal(int)

    def __init__(self, event, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("MissedCard")

        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(10, 6, 10, 6)

        top_row = QHBoxLayout()
        title_label = QLabel(event.title)
        title_font = QFont()
        title_font.setPointSize(9)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #B5483D;")

        dismiss_btn = QPushButton("✕")
        dismiss_btn.setFixedSize(20, 20)
        dismiss_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #9B89B0;
                font-size: 10px;
                padding: 0;
            }
            QPushButton:hover { color: #B5483D; }
        """)
        dismiss_btn.clicked.connect(lambda: self.dismiss_requested.emit(event.id))

        top_row.addWidget(title_label)
        top_row.addStretch()
        top_row.addWidget(dismiss_btn)
        layout.addLayout(top_row)

        detail_label = QLabel(f"{event.date} at {event.time}")
        detail_label.setStyleSheet("color: #9B89B0; font-size: 8pt;")
        layout.addWidget(detail_label)
        self.setLayout(layout)


class Sidebar(QWidget):
    event_deleted = pyqtSignal(int)
    reminder_dismissed = pyqtSignal(int)
    all_reminders_dismissed = pyqtSignal()
    task_added = pyqtSignal(str, str)    # ← NEW — date, text
    task_toggled = pyqtSignal(int, bool) # ← NEW — id, is_done

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(280)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self._current_date = ""  # ← NEW

        outer_layout = QVBoxLayout()
        outer_layout.setSpacing(0)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # --- TOP: checklist section ---  # ← NEW
        checklist_section = QWidget()
        checklist_layout = QVBoxLayout()
        checklist_layout.setSpacing(4)
        checklist_layout.setContentsMargins(12, 12, 12, 8)

        checklist_title = QLabel("Today's Tasks")
        checklist_title_font = QFont()
        checklist_title_font.setPointSize(10)
        checklist_title_font.setBold(True)
        checklist_title.setFont(checklist_title_font)
        checklist_title.setStyleSheet("color: #4A4258;")
        checklist_layout.addWidget(checklist_title)

        self._checklist_layout = QVBoxLayout()
        self._checklist_layout.setSpacing(2)
        checklist_layout.addLayout(self._checklist_layout)

        add_row = QHBoxLayout()
        self._task_input = QLineEdit()
        self._task_input.setPlaceholderText("Add a task and press Enter...")
        self._task_input.setFixedHeight(28)
        self._task_input.returnPressed.connect(self._on_add_task)
        add_checklist_btn = QPushButton("+")
        add_checklist_btn.setFixedSize(28, 28)
        add_checklist_btn.clicked.connect(self._on_add_task)
        add_row.addWidget(self._task_input, stretch=1)
        add_row.addWidget(add_checklist_btn)
        checklist_layout.addLayout(add_row)

        checklist_section.setLayout(checklist_layout)
        self._checklist_widgets = []

        div1 = QFrame()
        div1.setFrameShape(QFrame.Shape.HLine)
        div1.setStyleSheet("color: #E5DCEF;")

        # --- MIDDLE: events section ---
        self._top_widget = QWidget()
        self._layout = QVBoxLayout()
        self._layout.setSpacing(8)
        self._layout.setContentsMargins(12, 12, 12, 12)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.date_label = QLabel("Select a date")
        date_font = QFont()
        date_font.setPointSize(12)
        date_font.setBold(True)
        self.date_label.setFont(date_font)
        self.date_label.setStyleSheet("color: #4A4258;")

        self.add_btn = QPushButton("+ Add Event")

        self._layout.addWidget(self.date_label)
        self._layout.addWidget(self.add_btn)
        self._layout.addSpacing(8)
        self._top_widget.setLayout(self._layout)
        self._event_widgets = []

        div2 = QFrame()
        div2.setFrameShape(QFrame.Shape.HLine)
        div2.setStyleSheet("color: #E5DCEF;")

        # --- BOTTOM: missed reminders section ---
        self._missed_widget = QWidget()
        missed_layout = QVBoxLayout()
        missed_layout.setSpacing(6)
        missed_layout.setContentsMargins(12, 8, 12, 12)

        missed_header_row = QHBoxLayout()
        missed_title = QLabel("Missed Reminders")
        missed_font = QFont()
        missed_font.setPointSize(10)
        missed_font.setBold(True)
        missed_title.setFont(missed_font)
        missed_title.setStyleSheet("color: #B5483D;")

        self.clear_all_btn = QPushButton("Clear all")
        self.clear_all_btn.setFixedHeight(24)
        self.clear_all_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #B5483D;
                border-radius: 4px;
                color: #B5483D;
                font-size: 9pt;
                padding: 2px 6px;
            }
            QPushButton:hover {
                background-color: #B5483D;
                color: #FFFFFF;
            }
        """)
        self.clear_all_btn.clicked.connect(self.all_reminders_dismissed.emit)

        missed_header_row.addWidget(missed_title)
        missed_header_row.addStretch()
        missed_header_row.addWidget(self.clear_all_btn)
        missed_layout.addLayout(missed_header_row)

        self._missed_cards_layout = QVBoxLayout()
        self._missed_cards_layout.setSpacing(6)
        missed_layout.addLayout(self._missed_cards_layout)

        self._no_missed_label = QLabel("No missed reminders")
        self._no_missed_label.setStyleSheet("color: #9B89B0; font-style: italic;")
        missed_layout.addWidget(self._no_missed_label)

        self._missed_widget.setLayout(missed_layout)
        self._missed_cards = []
        self._missed_widget.setStyleSheet("background-color: #FFF8F6;")  
        checklist_section.setStyleSheet("background-color: #F8F5FF;")
        # assemble outer layout
        outer_layout.addWidget(checklist_section)    # top
        outer_layout.addWidget(div1)
        outer_layout.addWidget(self._top_widget, stretch=1)  # middle
        outer_layout.addWidget(div2)
        outer_layout.addWidget(self._missed_widget)  # bottom
        self.setLayout(outer_layout)

    def _on_add_task(self):  # ← NEW
        text = self._task_input.text().strip()
        if text and self._current_date:
            self.task_added.emit(self._current_date, text)
            self._task_input.clear()

    def update_checklist(self, items: list):  # ← NEW
        for w in self._checklist_widgets:
            self._checklist_layout.removeWidget(w)
            w.deleteLater()
        self._checklist_widgets = []

        for item in items:
            row_widget = QWidget()
            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(6)

            cb = QCheckBox()
            cb.setChecked(item.is_done)
            cb.setStyleSheet("""
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
            cb.toggled.connect(lambda checked, eid=item.id: self.task_toggled.emit(eid, checked))

            lbl = QLabel(item.title)
            lbl_font = QFont()
            lbl_font.setPointSize(9)
            lbl_font.setStrikeOut(item.is_done)
            lbl.setFont(lbl_font)
            lbl.setStyleSheet("color: #9B89B0;" if item.is_done else "color: #4A4258;")
            lbl.setWordWrap(True)

            row_layout.addWidget(cb)
            row_layout.addWidget(lbl, stretch=1)
            row_widget.setLayout(row_layout)

            self._checklist_layout.addWidget(row_widget)
            self._checklist_widgets.append(row_widget)

    def update_for_date(self, date: QDate, events: list):
        self._current_date = date.toString("yyyy-MM-dd")  # ← NEW
        now = datetime.now()
        for w in self._event_widgets:
            self._layout.removeWidget(w)
            w.deleteLater()
        self._event_widgets = []

        self.date_label.setText(date.toString("MMMM d"))

        if events:
            for event in events:
                is_missed = False
                if event.time and not event.notified:
                    try:
                        event_dt = datetime.strptime(
                            f"{event.date} {event.time}", "%Y-%m-%d %H:%M"
                        )
                        is_missed = event_dt < now
                    except ValueError:
                        pass
                card = EventCard(event, is_missed=is_missed)
                card.delete_requested.connect(self.event_deleted.emit)
                self._layout.addWidget(card)
                self._event_widgets.append(card)
        else:
            empty = QLabel("No events for this day")
            empty.setStyleSheet("color: #9B89B0; font-style: italic;")
            self._layout.addWidget(empty)
            self._event_widgets.append(empty)

    def update_missed_reminders(self, missed: list):
        for w in self._missed_cards:
            self._missed_cards_layout.removeWidget(w)
            w.deleteLater()
        self._missed_cards = []

        if missed:
            self._no_missed_label.hide()
            self.clear_all_btn.show()
            for event in missed:
                card = MissedReminderCard(event)
                card.dismiss_requested.connect(self.reminder_dismissed.emit)
                self._missed_cards_layout.addWidget(card)
                self._missed_cards.append(card)
        else:
            self._no_missed_label.show()
            self.clear_all_btn.hide()