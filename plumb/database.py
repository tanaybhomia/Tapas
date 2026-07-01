import sqlite3
import os
from datetime import datetime


class Database:
    def __init__(self):
        data_dir = os.path.join(os.path.expanduser("~"), ".local", "share", "plumb")
        os.makedirs(data_dir, exist_ok=True)
        self.db_path = os.path.join(data_dir, "plumb.db")
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            """)

            # Ensure at least one default project exists
            conn.execute(
                'INSERT OR IGNORE INTO projects (id, name) VALUES (1, "Default Project")'
            )

            conn.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    type TEXT NOT NULL,
                    duration_seconds INTEGER NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                )
            """)

    def get_projects(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id, name FROM projects ORDER BY id")
            return cursor.fetchall()

    def add_project(self, name):
        with sqlite3.connect(self.db_path) as conn:
            try:
                cursor = conn.execute("INSERT INTO projects (name) VALUES (?)", (name,))
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                return None

    def log_session(self, project_id, session_type, duration_seconds):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO sessions (project_id, type, duration_seconds)
                VALUES (?, ?, ?)
            """,
                (project_id, session_type, duration_seconds),
            )

    def get_setting(self, key, default=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else default

    def set_setting(self, key, value):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, str(value)),
            )


db = Database()
