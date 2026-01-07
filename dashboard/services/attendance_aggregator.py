from typing import Dict, Any, List, Optional
from django.db import connection
from attendance.models import AttendanceRecord, Student

ATT_TABLE = AttendanceRecord._meta.db_table
STU_TABLE = Student._meta.db_table


def _fetch(sql: str, params: List[Any]) -> List[Dict[str, Any]]:
    with connection.cursor() as cur:
        cur.execute(sql, params)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def _role_filter(role: str) -> Optional[str]:
    if role == "masool":
        return "s.darajah_id"
    elif role in ["prefect", "deputy_prefect"]:
        return "s.hizb_id"
    elif role == "muaddib":
        return "s.hizb_group_id"
    return None


def daily(start: str, end: str, role: str,
          darajah: Optional[int] = None,
          hizb: Optional[int] = None,
          hizb_group: Optional[int] = None,
          room: Optional[str] = None,
          teacher: Optional[int] = None) -> Dict[str, Any]:

    filter_col = _role_filter(role)
    filter_val = darajah if role == "masool" else hizb if role in ["prefect", "deputy_prefect"] else hizb_group

    sql = f"""
    SELECT
      a.date::date AS date,
      COUNT(*) AS total,
      SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) AS present,
      SUM(CASE WHEN a.status='absent' THEN 1 ELSE 0 END) AS absent,
      SUM(CASE WHEN a.status='late' THEN 1 ELSE 0 END) AS late
    FROM {ATT_TABLE} a
    JOIN {STU_TABLE} s ON a.student_id = s.id
    WHERE a.date IS NOT NULL
      AND a.date BETWEEN %s AND %s
      {"AND (%s IS NULL OR " + filter_col + "=%s)" if filter_col else ""}
      AND (%s IS NULL OR s.room=%s)
      AND (%s IS NULL OR a.created_by_id=%s)
    GROUP BY a.date
    ORDER BY a.date ASC;
    """

    params = [start, end]
    if filter_col:
        params.extend([filter_val, filter_val])
    params.extend([room, room, teacher, teacher])

    rows = _fetch(sql, params)
    return {
        "dates": [str(r["date"]) for r in rows],
        "present": [int(r["present"]) for r in rows],
        "absent": [int(r["absent"]) for r in rows],
        "late": [int(r["late"]) for r in rows],
        "rate": [round((r["present"]/r["total"])*100, 2) if r["total"] else 0 for r in rows],
    }


def weekly(start: str, end: str, role: str,
           darajah: Optional[int] = None,
           hizb: Optional[int] = None,
           hizb_group: Optional[int] = None,
           room: Optional[str] = None,
           teacher: Optional[int] = None) -> Dict[str, Any]:

    filter_col = _role_filter(role)
    filter_val = darajah if role == "masool" else hizb if role in ["prefect", "deputy_prefect"] else hizb_group

    sql = f"""
    SELECT
      date_trunc('week', a.date)::date AS week,
      COUNT(*) AS total,
      SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) AS present,
      SUM(CASE WHEN a.status='absent' THEN 1 ELSE 0 END) AS absent,
      SUM(CASE WHEN a.status='late' THEN 1 ELSE 0 END) AS late
    FROM {ATT_TABLE} a
    JOIN {STU_TABLE} s ON a.student_id = s.id
    WHERE a.date IS NOT NULL
      AND a.date BETWEEN %s AND %s
      {"AND (%s IS NULL OR " + filter_col + "=%s)" if filter_col else ""}
      AND (%s IS NULL OR s.room=%s)
      AND (%s IS NULL OR a.created_by_id=%s)
    GROUP BY date_trunc('week', a.date)::date
    ORDER BY week ASC;
    """

    params = [start, end]
    if filter_col:
        params.extend([filter_val, filter_val])
    params.extend([room, room, teacher, teacher])

    rows = _fetch(sql, params)
    return {
        "weeks": [str(r["week"]) for r in rows],
        "present": [int(r["present"]) for r in rows],
        "absent": [int(r["absent"]) for r in rows],
        "late": [int(r["late"]) for r in rows],
    }


def room_ranking(start: str, end: str, role: str,
                 darajah: Optional[int] = None,
                 hizb: Optional[int] = None,
                 hizb_group: Optional[int] = None,
                 limit: int = 20,
                 order: str = "desc") -> Dict[str, Any]:

    order_sql = "DESC" if order.lower() == "desc" else "ASC"
    filter_col = _role_filter(role)
    filter_val = darajah if role == "masool" else hizb if role in ["prefect", "deputy_prefect"] else hizb_group

    sql = f"""
    SELECT
      s.room,
      COUNT(*) AS total,
      SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) AS present
    FROM {ATT_TABLE} a
    JOIN {STU_TABLE} s ON a.student_id = s.id
    WHERE a.date IS NOT NULL
      AND a.date BETWEEN %s AND %s
      {"AND (%s IS NULL OR " + filter_col + "=%s)" if filter_col else ""}
    GROUP BY s.room
    ORDER BY (SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END)::float / NULLIF(COUNT(*),0)) {order_sql}
    LIMIT %s;
    """

    params = [start, end]
    if filter_col:
        params.extend([filter_val, filter_val])
    params.append(limit)

    rows = _fetch(sql, params)
    return {
        "labels": [str(r["room"]) for r in rows],
        "rates": [round((r["present"]/r["total"])*100, 2) if r["total"] else 0 for r in rows],
    }


def flagged_rooms(start: str, end: str, role: str,
                  darajah: Optional[int] = None,
                  hizb: Optional[int] = None,
                  hizb_group: Optional[int] = None,
                  threshold: float = 75.0) -> List[Dict[str, Any]]:

    filter_col = _role_filter(role)
    filter_val = darajah if role == "masool" else hizb if role in ["prefect", "deputy_prefect"] else hizb_group

    sql = f"""
    SELECT
      s.room,
      COUNT(*) AS total,
      SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) AS present
    FROM {ATT_TABLE} a
    JOIN {STU_TABLE} s ON a.student_id = s.id
    WHERE a.date IS NOT NULL
      AND a.date BETWEEN %s AND %s
      {"AND (%s IS NULL OR " + filter_col + "=%s)" if filter_col else ""}
    GROUP BY s.room
    HAVING (SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END)::float / NULLIF(COUNT(*),0)) * 100 < %s
    ORDER BY (SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END)::float / NULLIF(COUNT(*),0)) ASC
    LIMIT 50;
    """

    params = [start, end]
    if filter_col:
        params.extend([filter_val, filter_val])
    params.append(threshold)

    rows = _fetch(sql, params)
    return [
        {
            "room": str(r["room"]),
            "rate": round((r["present"] / r["total"]) * 100, 2) if r["total"] else 0
        }
        for r in rows
    ]
