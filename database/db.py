# database/db.py
# =========================
# طبقة قاعدة البيانات (SQLite)
# مصدر واحد للاتصال + تهيئة الجداول
# =========================

import os
import sqlite3
from typing import Any, Iterable, Optional

from config import DB_PATH


class Database:
    def __init__(self, path: str):
        self.path = path
        self._ensure_dir()

    def _ensure_dir(self):
        directory = os.path.dirname(self.path)
        if directory:
            os.makedirs(directory, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def execute(
        self,
        query: str,
        params: Iterable[Any] = (),
        commit: bool = True,
    ) -> None:
        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            if commit:
                conn.commit()

    def executemany(
        self,
        query: str,
        params: Iterable[Iterable[Any]],
        commit: bool = True,
    ) -> None:
        with self.connect() as conn:
            cur = conn.cursor()
            cur.executemany(query, params)
            if commit:
                conn.commit()

    def fetchone(
        self,
        query: str,
        params: Iterable[Any] = (),
    ) -> Optional[sqlite3.Row]:
        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            return cur.fetchone()

    def fetchall(
        self,
        query: str,
        params: Iterable[Any] = (),
    ) -> list[sqlite3.Row]:
        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            return cur.fetchall()


# كائن قاعدة البيانات العام
db = Database(DB_PATH)


def init_db() -> None:
    """
    تهيئة جميع الجداول المطلوبة للبوت
    تُستدعى مرة واحدة عند تشغيل البوت
    """

    # =========================
    # Sessions (Telethon accounts)
    # =========================
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_string TEXT UNIQUE NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # =========================
    # Links
    # =========================
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            link TEXT UNIQUE NOT NULL,
            category TEXT,
            is_alive INTEGER DEFAULT 0,
            is_assigned INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # =========================
    # Assignments (distribution)
    # =========================
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            link_id INTEGER NOT NULL,
            joined INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(session_id, link_id),
            FOREIGN KEY(session_id) REFERENCES sessions(id),
            FOREIGN KEY(link_id) REFERENCES links(id)
        )
        """
    )
