from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QFrame, QSizePolicy, QHBoxLayout
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont


class EventCard(QFrame):
    delete_requested = pyqtSignal(int)  # emits event id when delete clicked

    def __init__(self, event, parent=None):
        super().__init__(parent)
        self.event = event
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("EventCard")

        layout = QVBoxLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(10, 8, 10, 8)

        # top row: time + delete button
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
            QPushButton:hover {
                color: #B5483D;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_requested.emit(event.id))

        top_row.addWidget(time_label)
        top_row.addStretch()
        top_row.addWidget(delete_btn)
        layout.addLayout(top_row)

        # title
        title_label = QLabel(event.title)
        title_font = QFont()
        title_font.setPointSize(10)
        title_font.setBold(not event.is_done)
        title_font.setStrikeOut(event.is_done)
        title_label.setFont(title_font)
        title_label.setWordWrap(True)
        title_label.setStyleSheet("color: #4A4258;")
        if event.is_priority and not event.is_done:
            title_label.setText("★ " + event.title)
            title_label.setStyleSheet("color: #C9A800; font-weight: bold;")
        elif event.is_done:
            title_label.setStyleSheet("color: #9B89B0;")
        else:
            title_label.setStyleSheet("color: #4A4258")
        layout.addWidget(title_label)

        # date
        date_label = QLabel(event.date)
        date_font = QFont()
        date_font.setPointSize(8)
        date_label.setFont(date_font)
        date_label.setStyleSheet("color: #9B89B0;")
        layout.addWidget(date_label)

        # notes
        if event.notes:
            notes_label = QLabel(event.notes)
            notes_label.setWordWrap(True)
            notes_label.setStyleSheet("color: #6B5F7A; font-size: 9pt;")
            layout.addWidget(notes_label)

        self.setLayout(layout)


class Sidebar(QWidget):
    event_deleted = pyqtSignal(int)  # bubbles delete signal up to MainWindow

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

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

        self.setLayout(self._layout)
        self._event_widgets = []

    def update_for_date(self, date: QDate, events: list):
        for w in self._event_widgets:
            self._layout.removeWidget(w)
            w.deleteLater()
        self._event_widgets = []

        self.date_label.setText(date.toString("MMMM d"))

        if events:
            for event in events:
                card = EventCard(event)
                card.delete_requested.connect(self.event_deleted.emit)
                self._layout.addWidget(card)
                self._event_widgets.append(card)
        else:
            empty = QLabel("No events for this day")
            empty.setStyleSheet("color: #9B89B0; font-style: italic;")
            self._layout.addWidget(empty)
            self._event_widgets.append(empty)