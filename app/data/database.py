import sqlite3
from pathlib import Path
import sys
import os

def get_db_path() -> Path: 
    """Returns persistent DB path in AppData for packaged app, local for dev."""
    if getattr(sys, 'frozen', False):

        app_data = Path(os.environ.get("APPDATA", Path.home())) / "Asteria"
        app_data.mkdir(exist_ok=True)
        return app_data / "asteria.db"
    else:
    
        return Path(__file__).parent / "asteria.db"

DB_PATH = get_db_path()  # ← CHANGED

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
                remind_mins         INTEGER DEFAULT 0,
                is_priority         INTEGER DEFAULT 0,
                is_done     INTEGER DEFAULT 0,
                notified        INTEGER DEFAULT 0,
                created_at      TEXT DEFAULT (datetime('now')),
                is_silent       INTEGER DEFAULT 0,
                is_checklist    INTEGER DEFAULT 0
                      )
                """)
        conn.commit()

def init_db():
      with get_connection() as conn:
            create_schema(conn)