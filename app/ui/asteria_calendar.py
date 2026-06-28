from PyQt6.QtWidgets import QCalendarWidget
from PyQt6.QtGui import QColor, QPainter, QFont, QBrush
from PyQt6.QtCore import QDate, Qt


class AsteriaCalendar(QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._events: dict[str, list] = {}

    def set_events(self, events: dict[str, list]):
        self._events = events
        self.updateCells()

    def paintCell(self, painter: QPainter, rect, date: QDate):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # --- background ---
        today = QDate.currentDate()
        selected = self.selectedDate()

        if date == selected:
            painter.fillRect(rect, QColor("#C9A8E0"))  # lilac for selected
        elif date == today:
            painter.fillRect(rect, QColor("#F2E6FF"))  # soft highlight for today
        else:
            painter.fillRect(rect, QColor("#F5F1FA"))  # default background

        # --- cell border ---
        painter.setPen(QColor("#E5DCEF"))
        painter.drawRect(rect.adjusted(0, 0, -1, -1))

        # --- scale sizes from cell dimensions ---
        cell_height = rect.height()
        cell_width = rect.width()
        date_font_size = max(6, int(cell_height * 0.18))
        event_font_size = max(5, int(cell_height * 0.10))
        line_height = max(10, int(cell_height * 0.16))
        y_start = rect.top() + int(cell_height * 0.32)
        max_chars = max(8, int(cell_width / 8))

        # --- date number top-left ---
        date_font = QFont()
        date_font.setPointSize(date_font_size)
        date_font.setBold(True)
        painter.setFont(date_font)

        # pick date number color
        if date == selected:
            painter.setPen(QColor("#FFFFFF"))
        elif date.month() != self.monthShown():
            painter.setPen(QColor("#B7ABC6"))  # grayed out for other months
        elif date.dayOfWeek() in (6, 7):
            painter.setPen(QColor("#B5483D"))  # weekend rust color
        else:
            painter.setPen(QColor("#4A4258"))

        date_rect = rect.adjusted(6, 4, 0, 0)
        painter.drawText(
            date_rect,
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
            str(date.day())
        )

        # --- event text ---
        date_str = date.toString("yyyy-MM-dd")
        events = self._events.get(date_str, [])

        if events:
            event_font = QFont()
            event_font.setPointSize(event_font_size)
            painter.setFont(event_font)

            max_shown = 3
            shown = events[:max_shown]
            extra = len(events) - max_shown

            for i, event in enumerate(shown):
                title = event.title
                if len(title) > max_chars:
                    title = title[:max_chars] + "…"
                y = y_start + i * line_height
                text_rect = rect.adjusted(6, y - rect.top(), -3, 0)
                text_rect.setHeight(line_height)
                if date == selected:
                    painter.setPen(QColor("#FFFFFF"))
                else:
                    painter.setPen(QColor("#4A4258"))
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft, title)

            if extra > 0:
                y = y_start + max_shown * line_height
                text_rect = rect.adjusted(6, y - rect.top(), -3, 0)
                text_rect.setHeight(line_height)
                painter.setPen(QColor("#9B89B0"))
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft, f"+{extra} more")

        painter.restore()