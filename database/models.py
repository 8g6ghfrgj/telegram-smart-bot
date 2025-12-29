# database/models.py
# =========================
# Models: طبقة منطق قاعدة البيانات
# كل القراءة/الكتابة من وإلى DB هنا فقط
# =========================

from typing import List, Optional
from database.db import db


# =========================
# Sessions (Telethon Accounts)
# =========================

class SessionModel:
    @staticmethod
    def add(session_string: str) -> bool:
        try:
            db.execute(
                "INSERT INTO sessions (session_string) VALUES (?)",
                (session_string,),
            )
            return True
        except Exception:
            return False

    @staticmethod
    def exists(session_string: str) -> bool:
        row = db.fetchone(
            "SELECT id FROM sessions WHERE session_string = ?",
            (session_string,),
        )
        return row is not None

    @staticmethod
    def get_active() -> List[dict]:
        rows = db.fetchall(
            "SELECT * FROM sessions WHERE is_active = 1 ORDER BY id ASC"
        )
        return [dict(r) for r in rows]

    @staticmethod
    def deactivate(session_id: int) -> None:
        db.execute(
            "UPDATE sessions SET is_active = 0 WHERE id = ?",
            (session_id,),
        )


# =========================
# Links
# =========================

class LinkModel:
    @staticmethod
    def add(link: str) -> bool:
        try:
            db.execute(
                "INSERT OR IGNORE INTO links (link) VALUES (?)",
                (link,),
            )
            return True
        except Exception:
            return False

    @staticmethod
    def bulk_add(links: List[str]) -> int:
        params = [(l,) for l in links]
        db.executemany(
            "INSERT OR IGNORE INTO links (link) VALUES (?)",
            params,
        )
        return len(params)

    @staticmethod
    def get_unchecked(limit: int = 100) -> List[dict]:
        rows = db.fetchall(
            """
            SELECT * FROM links
            WHERE is_alive = 0
            ORDER BY id ASC
            LIMIT ?
            """,
            (limit,),
        )
        return [dict(r) for r in rows]

    @staticmethod
    def mark_alive(link_id: int, category: str) -> None:
        db.execute(
            """
            UPDATE links
            SET is_alive = 1,
                category = ?,
                is_assigned = 0
            WHERE id = ?
            """,
            (category, link_id),
        )

    @staticmethod
    def mark_dead(link_id: int) -> None:
        db.execute(
            "UPDATE links SET is_alive = -1 WHERE id = ?",
            (link_id,),
        )

    @staticmethod
    def get_alive_unassigned(limit: Optional[int] = None) -> List[dict]:
        query = """
            SELECT * FROM links
            WHERE is_alive = 1 AND is_assigned = 0
            ORDER BY id ASC
        """
        params = ()
        if limit is not None:
            query += " LIMIT ?"
            params = (limit,)

        rows = db.fetchall(query, params)
        return [dict(r) for r in rows]

    @staticmethod
    def mark_assigned(link_id: int) -> None:
        db.execute(
            "UPDATE links SET is_assigned = 1 WHERE id = ?",
            (link_id,),
        )


# =========================
# Assignments (Distribution)
# =========================

class AssignmentModel:
    @staticmethod
    def assign(session_id: int, link_id: int) -> None:
        db.execute(
            """
            INSERT OR IGNORE INTO assignments (session_id, link_id)
            VALUES (?, ?)
            """,
            (session_id, link_id),
        )
        LinkModel.mark_assigned(link_id)

    @staticmethod
    def get_pending_by_session(session_id: int) -> List[dict]:
        rows = db.fetchall(
            """
            SELECT a.id, a.link_id, l.link
            FROM assignments a
            JOIN links l ON l.id = a.link_id
            WHERE a.session_id = ? AND a.joined = 0
            ORDER BY a.id ASC
            """,
            (session_id,),
        )
        return [dict(r) for r in rows]

    @staticmethod
    def mark_joined(session_id: int, link_id: int) -> None:
        db.execute(
            """
            UPDATE assignments
            SET joined = 1
            WHERE session_id = ? AND link_id = ?
            """,
            (session_id, link_id),
        )
