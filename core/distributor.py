# core/distributor.py
# توزيع الروابط النشطة على الحسابات بدون تكرار
# هذا الملف يعتمد على database/models.py و bot/config.py

from typing import Dict, List

from database.models import LinkModel, AssignmentModel, SessionModel
from bot.config import MAX_LINKS_PER_ACCOUNT


def distribute_links() -> Dict[int, List[int]]:
    """
    توزيع الروابط الحية غير الموزعة على الحسابات النشطة

    يرجع:
    {
        session_id: [link_id, link_id, ...],
        ...
    }
    """

    sessions = SessionModel.get_active()
    if not sessions:
        return {}

    links = LinkModel.get_alive_unassigned()
    if not links:
        return {}

    distribution: Dict[int, List[int]] = {s["id"]: [] for s in sessions}

    session_index = 0
    sessions_count = len(sessions)

    for link in links:
        session = sessions[session_index]
        sid = session["id"]

        # حد 500 رابط لكل حساب
        if len(distribution[sid]) >= MAX_LINKS_PER_ACCOUNT:
            session_index += 1
            if session_index >= sessions_count:
                break
            session = sessions[session_index]
            sid = session["id"]

        AssignmentModel.add(sid, link["id"])
        LinkModel.mark_assigned(link["id"])
        distribution[sid].append(link["id"])

    return distribution
