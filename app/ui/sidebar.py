from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont


class EventCard(QFrame):
    def __init__(self, time: str, title: str, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("EventCard")

        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(8, 6, 8, 6)

        time_label = QLabel(time or "All day")
        time_font = QFont()
        time_font.setPointSize(8)
        time_label.setFont(time_font)
        time_label.setStyleSheet("color: #9B89B0;")

        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(10)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setWordWrap(True)

        layout.addWidget(time_label)
        layout.addWidget(title_label)
        self.setLayout(layout)


class Sidebar(QWidget):
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
        # clear previous event cards
        for w in self._event_widgets:
            self._layout.removeWidget(w)
            w.deleteLater()
        self._event_widgets = []

        # update heading
        self.date_label.setText(date.toString("MMMM d"))

        # add event cards or empty message
        if events:
            for event in events:
                card = EventCard(time=event.time, title=event.title)
                self._layout.addWidget(card)
                self._event_widgets.append(card)
        else:
            empty = QLabel("No events for this day")
            empty.setStyleSheet("color: #9B89B0; font-style: italic;")
            self._layout.addWidget(empty)
            self._event_widgets.append(empty)