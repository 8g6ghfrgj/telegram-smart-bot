# database/db.py
# إدارة الاتصال بقاعدة بيانات SQLite
# هذا الملف أساسي ولن يتم تعديله لاحقًا

import sqlite3
from pathlib import Path
from threading import Lock

from bot.config import DB_PATH

# قفل لمنع تعارض الكتابة
_db_lock = Lock()


class Database:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._connection = None

    def connect(self):
        if self._connection is None:
            self._connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False
            )
            self._connection.row_factory = sqlite3.Row
        return self._connection

    def execute(self, query: str, params: tuple = (), commit: bool = False):
        with _db_lock:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(query, params)
            if commit:
                conn.commit()
            return cursor

    def executemany(self, query: str, params_list: list, commit: bool = False):
        with _db_lock:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            if commit:
                conn.commit()
            return cursor

    def fetchone(self, query: str, params: tuple = ()):
        cursor = self.execute(query, params)
        return cursor.fetchone()

    def fetchall(self, query: str, params: tuple = ()):
        cursor = self.execute(query, params)
        return cursor.fetchall()

    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None


# كائن قاعدة بيانات عام يستخدم في جميع المشروع
db = Database()


def init_db():
    """
    إنشاء الجداول الأساسية إذا لم تكن موجودة
    """
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_string TEXT UNIQUE NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        commit=True
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            link TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            is_alive INTEGER DEFAULT 1,
            assigned INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        commit=True
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            link_id INTEGER NOT NULL,
            joined INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(session_id, link_id)
        )
        """,
        commit=True
    )
