# database/models.py
# طبقة التعامل مع الجداول (CRUD)
# هذا الملف يعتمد على database/db.py فقط ولن يتم تعديله لاحقًا

from typing import List, Optional
from database.db import db


# =========================
# Sessions
# =========================

class SessionModel:

    @staticmethod
    def add(session_string: str) -> bool:
        try:
            db.execute(
                "INSERT INTO sessions (session_string) VALUES (?)",
                (session_string,),
                commit=True
            )
            return True
        except Exception:
            return False

    @staticmethod
    def get_active() -> List[dict]:
        rows = db.fetchall(
            "SELECT * FROM sessions WHERE is_active = 1"
        )
        return [dict(row) for row in rows]

    @staticmethod
    def deactivate(session_id: int):
        db.execute(
            "UPDATE sessions SET is_active = 0 WHERE id = ?",
            (session_id,),
            commit=True
        )

    @staticmethod
    def exists(session_string: str) -> bool:
        row = db.fetchone(
            "SELECT id FROM sessions WHERE session_string = ?",
            (session_string,)
        )
        return row is not None


# =========================
# Links
# =========================

class LinkModel:

    @staticmethod
    def add(link: str, category: str, is_alive: int = 1):
        try:
            db.execute(
                """
                INSERT INTO links (link, category, is_alive)
                VALUES (?, ?, ?)
                """,
                (link, category, is_alive),
                commit=True
            )
        except Exception:
            pass

    @staticmethod
    def bulk_add(data: List[tuple]):
        """
        data = [(link, category, is_alive), ...]
        """
        try:
            db.executemany(
                """
                INSERT OR IGNORE INTO links (link, category, is_alive)
                VALUES (?, ?, ?)
                """,
                data,
                commit=True
            )
        except Exception:
            pass

    @staticmethod
    def get_alive_unassigned(category: Optional[str] = None) -> List[dict]:
        if category:
            rows = db.fetchall(
                """
                SELECT * FROM links
                WHERE is_alive = 1 AND assigned = 0 AND category = ?
                """,
                (category,)
            )
        else:
            rows = db.fetchall(
                """
                SELECT * FROM links
                WHERE is_alive = 1 AND assigned = 0
                """
            )
        return [dict(row) for row in rows]

    @staticmethod
    def mark_dead(link_id: int):
        db.execute(
            "UPDATE links SET is_alive = 0 WHERE id = ?",
            (link_id,),
            commit=True
        )

    @staticmethod
    def mark_assigned(link_id: int):
        db.execute(
            "UPDATE links SET assigned = 1 WHERE id = ?",
            (link_id,),
            commit=True
        )


# =========================
# Assignments
# =========================

class AssignmentModel:

    @staticmethod
    def add(session_id: int, link_id: int):
        try:
            db.execute(
                """
                INSERT OR IGNORE INTO assignments (session_id, link_id)
                VALUES (?, ?)
                """,
                (session_id, link_id),
                commit=True
            )
        except Exception:
            pass

    @staticmethod
    def mark_joined(session_id: int, link_id: int):
        db.execute(
            """
            UPDATE assignments
            SET joined = 1
            WHERE session_id = ? AND link_id = ?
            """,
            (session_id, link_id),
            commit=True
        )

    @staticmethod
    def get_pending_by_session(session_id: int) -> List[dict]:
        rows = db.fetchall(
            """
            SELECT a.link_id, l.link
            FROM assignments a
            JOIN links l ON l.id = a.link_id
            WHERE a.session_id = ? AND a.joined = 0 AND l.is_alive = 1
            """,
            (session_id,)
        )
        return [dict(row) for row in rows]
