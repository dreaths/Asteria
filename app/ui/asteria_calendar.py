from PyQt6.QtWidgets import QCalendarWidget
from PyQt6.QtGui import QColor, QPainter, QFont
from PyQt6.QtCore import QDate, Qt, QTimer, QSize
from datetime import datetime


class AsteriaCalendar(QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._events: dict[str, list] = {}
        self._hide_top_row = False
        self.currentPageChanged.connect(self._update_margins)
        QTimer.singleShot(0, self._update_margins)

    def set_events(self, events: dict[str, list]):
        self._events = events
        self.updateCells()

    def sizeHint(self) -> QSize:
        hint = super().sizeHint()
        if self._hide_top_row:
            hint.setHeight(hint.height() - self._cell_height())
        return hint

    def minimumSizeHint(self) -> QSize:
        hint = super().minimumSizeHint()
        if self._hide_top_row:
            hint.setHeight(hint.height() - self._cell_height())
        return hint

    def paintCell(self, painter: QPainter, rect, date: QDate):
        if rect.height() <= 0 or rect.width() <= 0:
            return

        painter.save()

        if self._is_overflow_row(date):
            painter.fillRect(rect, QColor("#F5F1FA"))
            painter.restore()
            return

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # --- background ---
        today = QDate.currentDate()
        selected = self.selectedDate()

        if date == selected:
            painter.fillRect(rect, QColor("#C9A8E0"))
        elif date == today:
            painter.fillRect(rect, QColor("#F2E6FF"))
        else:
            painter.fillRect(rect, QColor("#F5F1FA"))

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

        if date == selected:
            painter.setPen(QColor("#FFFFFF"))
        elif date.month() != self.monthShown():
            painter.setPen(QColor("#B7ABC6"))
        elif date.dayOfWeek() in (6, 7):
            painter.setPen(QColor("#B5483D"))
        else:
            painter.setPen(QColor("#4A4258"))

        date_rect = rect.adjusted(8, 4, 0, 0)
        painter.drawText(
            date_rect,
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
            str(date.day())
        )

        # --- event text ---
        date_str = date.toString("yyyy-MM-dd")
        events = self._events.get(date_str, [])

        if events:
            real_events = [e for e in events if not e.is_checklist]
            checklist_items = [e for e in events if e.is_checklist and not e.is_done]
            items_to_show = real_events if real_events else checklist_items

            event_font = QFont()
            event_font.setPointSize(event_font_size)
            painter.setFont(event_font)

            max_shown = 3
            shown = items_to_show[:max_shown]
            extra = len(items_to_show) - max_shown

            for i, event in enumerate(shown):
                title = event.title
                if len(title) > max_chars:
                    title = title[:max_chars] + "…"

                if event.is_checklist:
                    prefix = "☐ "
                elif event.is_priority:
                    prefix = "● "
                else:
                    prefix = ""
                label = prefix + title

                is_missed = False
                if event.time and not event.notified:
                    try:
                        event_dt = datetime.strptime(
                            f"{event.date} {event.time}", "%Y-%m-%d %H:%M"
                        )
                        is_missed = event_dt < datetime.now()
                    except ValueError:
                        pass

                y = y_start + i * line_height
                text_rect = rect.adjusted(6, y - rect.top(), -3, 0)
                text_rect.setHeight(line_height)

                event_font_copy = QFont()
                event_font_copy.setPointSize(event_font_size)
                event_font_copy.setStrikeOut(event.is_done or is_missed)

                if event.is_checklist:
                    painter.setPen(QColor("#9B89B0"))
                elif event.is_priority and not event.is_done and not is_missed:
                    event_font_copy.setBold(True)
                    painter.setPen(QColor("#E91E8C"))
                elif date == selected:
                    painter.setPen(QColor("#FFFFFF"))
                else:
                    painter.setPen(QColor("#4A4258"))

                painter.setFont(event_font_copy)
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft, label)

            if extra > 0:
                y = y_start + max_shown * line_height
                text_rect = rect.adjusted(6, y - rect.top(), -3, 0)
                text_rect.setHeight(line_height)
                painter.setPen(QColor("#9B89B0"))
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft, f"+{extra} more")

        painter.restore()

    def _is_overflow_row(self, date: QDate) -> bool:
        days_from_monday = date.dayOfWeek() - 1
        monday = date.addDays(-days_from_monday)
        for i in range(7):
            if monday.addDays(i).month() == self.monthShown():
                return False
        return True

    def _update_margins(self):
        pass

    def _cell_height(self) -> int:
        header_height = 30
        row_header_height = 25
        available = self.height() - header_height - row_header_height
        return available // 6