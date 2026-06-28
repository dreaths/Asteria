import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "asteria.db"

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # rows behave like dicts: row["title"] not row[0]
    return conn

def create_schema(conn: sqlite3.connection):
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events(
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                date        TEXT NOT NULL,
                time        TEXT,
                notes       TEXT,
                remind_mins         INTEGER,
                notified        INTEGER DEFAULT 0,
                created_at      TEXT DEFAULT (datetime('now'))
                      )
                """)
        conn.commit()

def init_db():
      with get_connection() as conn:
            create_schema(conn)