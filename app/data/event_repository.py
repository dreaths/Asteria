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
                """INSERT INTO events (title, date, time, notes, remind_mins)
                   VALUES (?, ?, ?, ?, ?)""",
                (event.title, event.date, event.time, event.notes, event.remind_mins)
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
            remind_mins=row["remind_mins"]
        )