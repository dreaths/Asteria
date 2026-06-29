import sqlite3
from typing import Optional
from app.data.database import get_connection, DB_PATH
from app.data.models import Event

class EventRepository:
    def __init__(self, conn: sqlite3.Connection = None, db_path: str = None):
        if conn: 
            self._conn_obj = conn #If a connection was passed in directly (for tests)
        else:
            # No connection passed, open one from the filepath
            self._conn_obj = sqlite3.connect(db_path or str(DB_PATH))
            self._conn_obj.row_factory = sqlite3.Row

    def _conn(self) -> sqlite3.Connection:
        return self._conn_obj

    def add_event(self, event: Event) -> int:
        with self._conn() as conn:
            cursor = conn.execute(
                """INSERT INTO events (title, date, time, notes, remind_mins, is_priority, is_silent, is_checklist)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (event.title, event.date, event.time, event.notes, event.remind_mins, int(event.is_priority), int(event.is_silent), int(event.is_checklist))
            )
            conn.commit()
            return cursor.lastrowid   # the auto-assigned ID

    def get_events_for_date(self, date: str) -> list[Event]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM events WHERE date = ? ORDER BY time",
                (date,)
            ).fetchall()
        return [self._row_to_event(r) for r in rows]

    def get_all_event_dates(self) -> set[str]:
        # used by the calendar to know which cells to highlight
        with self._conn() as conn:
            rows = conn.execute("SELECT DISTINCT date FROM events").fetchall()
        return {row["date"] for row in rows}

    def get_due_reminders(self, now_str: str, window_str: str) -> list[Event]:
        # returns events where the reminder time falls within the current minute
        # reminder time = event datetime minus remind_mins
        # this query calculates that entirely in SQLite
        with self._conn() as conn:
            rows = conn.execute("""
                SELECT * FROM events
                WHERE notified = 0
                  AND time IS NOT NULL
                  AND datetime(date || ' ' || time, '-' || remind_mins || ' minutes')
                      BETWEEN ? AND ?
            """, (now_str, window_str)).fetchall()
        return [self._row_to_event(r) for r in rows]

    def mark_notified(self, event_id: int):
        with self._conn() as conn:
            conn.execute("UPDATE events SET notified = 1 WHERE id = ?", (event_id,))
            conn.commit()

    def delete_event(self, event_id: int):
        with self._conn() as conn:
            conn.execute("DELETE FROM events WHERE id = ?", (event_id,))
            conn.commit()

    def _row_to_event(self, row) -> Event:
        return Event(
            id=row["id"],
            title=row["title"],
            date=row["date"],
            time=row["time"],
            notes=row["notes"],
            remind_mins=row["remind_mins"],
            is_priority=bool(row["is_priority"]),
            is_done=bool(row["is_done"]),
            notified=bool(row["notified"]),
            is_silent=bool(row["is_silent"]),
            is_checklist=bool(row["is_checklist"])
        )
    def toggle_done(self, event_id: int, is_done: bool):  # ← NEW
        with self._conn() as conn:
            conn.execute(
                "UPDATE events SET is_done = ? WHERE id = ?",
                (int(is_done), event_id)
            )
            conn.commit()
    def get_all_events_by_date(self) -> dict[str, list]:
        """Returns all events grouped by date string."""
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM events ORDER BY date, is_checklist ASC, is_priority DESC, time"
            ).fetchall()
        result: dict[str, list] = {}
        for row in rows:
            event = self._row_to_event(row)
            result.setdefault(event.date, []).append(event)
        return result
    
    def mark_done(self, event_id: int):  
        with self._conn() as conn:
            conn.execute("UPDATE events SET is_done = 1 WHERE id = ?", (event_id,))
            conn.commit()
    def get_missed_reminders(self) -> list[Event]:  
        """Events that were never notified and whose time has already passed."""
        from datetime import datetime
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        rows = self._conn().execute("""
            SELECT * FROM events
            WHERE notified = 0
            AND time IS NOT NULL
            AND datetime(date || ' ' || time) < ?
            ORDER BY date DESC, time DESC
        """, (now_str,)).fetchall()
        return [self._row_to_event(r) for r in rows]

    def dismiss_reminder(self, event_id: int):  
        """Mark a missed reminder as notified so it leaves the missed list."""
        with self._conn() as conn:
            conn.execute("UPDATE events SET notified = 1 WHERE id = ?", (event_id,))
            conn.commit()

    def dismiss_all_reminders(self): 
        """Dismiss all missed reminders at once."""
        from datetime import datetime
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self._conn() as conn:
            conn.execute("""
                UPDATE events SET notified = 1
                WHERE notified = 0
                AND time IS NOT NULL
                AND datetime(date || ' ' || time) < ?
            """, (now_str,))
        conn.commit()