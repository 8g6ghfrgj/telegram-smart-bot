# core/distributor.py
# =========================
# توزيع الروابط على الحسابات
# منطق فقط (Pure Business Logic)
# =========================

from typing import Dict, List

from database.models import SessionModel, LinkModel, AssignmentModel
from config import LINKS_PER_SESSION


def distribute_links() -> Dict[str, int]:
    """
    توزيع الروابط الحيّة غير الموزعة على الحسابات النشطة

    القواعد:
    - كل رابط يوزّع على حساب واحد فقط
    - حد أقصى LINKS_PER_SESSION لكل حساب
    - التوزيع بالتسلسل (بدون عشوائية)

    يرجع إحصائيات:
    {
        "sessions": عدد الحسابات,
        "links": عدد الروابط الموزعة
    }
    """

    sessions = SessionModel.get_active()
    if not sessions:
        return {"sessions": 0, "links": 0}

    links = LinkModel.get_alive_unassigned()
    if not links:
        return {"sessions": len(sessions), "links": 0}

    link_index = 0
    assigned = 0

    for session in sessions:
        session_id = session["id"]

        for _ in range(LINKS_PER_SESSION):
            if link_index >= len(links):
                break

            AssignmentModel.assign(
                session_id=session_id,
                link_id=links[link_index]["id"],
            )

            assigned += 1
            link_index += 1

        if link_index >= len(links):
            break

    return {
        "sessions": len(sessions),
        "links": assigned,
    }
