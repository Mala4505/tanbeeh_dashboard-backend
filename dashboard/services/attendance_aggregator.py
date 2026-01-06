from typing import Dict, Any, List, Optional
from django.db import connection

def _fetch(sql: str, params: List[Any]) -> List[Dict[str, Any]]:
    with connection.cursor() as cur:
        cur.execute(sql, params)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

def daily(start: str, end: str, grade: Optional[str]=None, room: Optional[str]=None, teacher: Optional[str]=None) -> Dict[str, Any]:
    sql = """
    SELECT
      att_date::date AS date,
      COUNT(*) AS total,
      SUM(CASE WHEN status='present' THEN 1 ELSE 0 END) AS present,
      SUM(CASE WHEN status='absent' THEN 1 ELSE 0 END) AS absent,
      SUM(CASE WHEN status='late' THEN 1 ELSE 0 END) AS late
    FROM attendance
    WHERE att_date::date BETWEEN %s AND %s
      AND (%s IS NULL OR grade=%s)
      AND (%s IS NULL OR room_id=%s)
      AND (%s IS NULL OR teacher_id=%s)
    GROUP BY att_date::date
    ORDER BY att_date::date ASC;
    """
    rows = _fetch(sql, [start, end, grade, grade, room, room, teacher, teacher])
    return {
        "dates": [str(r["date"]) for r in rows],
        "present": [int(r["present"]) for r in rows],
        "absent": [int(r["absent"]) for r in rows],
        "late": [int(r["late"]) for r in rows],
        "rate": [round((r["present"]/r["total"])*100,2) if r["total"] else 0 for r in rows],
    }

def weekly(start: str, end: str, grade: Optional[str]=None, room: Optional[str]=None, teacher: Optional[str]=None) -> Dict[str, Any]:
    sql = """
    SELECT
      date_trunc('week', att_date)::date AS week,
      COUNT(*) AS total,
      SUM(CASE WHEN status='present' THEN 1 ELSE 0 END) AS present,
      SUM(CASE WHEN status='absent' THEN 1 ELSE 0 END) AS absent,
      SUM(CASE WHEN status='late' THEN 1 ELSE 0 END) AS late
    FROM attendance
    WHERE att_date::date BETWEEN %s AND %s
      AND (%s IS NULL OR grade=%s)
      AND (%s IS NULL OR room_id=%s)
      AND (%s IS NULL OR teacher_id=%s)
    GROUP BY date_trunc('week', att_date)::date
    ORDER BY week ASC;
    """
    rows = _fetch(sql, [start, end, grade, grade, room, room, teacher, teacher])
    return {
        "weeks": [str(r["week"]) for r in rows],
        "present": [int(r["present"]) for r in rows],
        "absent": [int(r["absent"]) for r in rows],
        "late": [int(r["late"]) for r in rows],
    }

def room_ranking(start: str, end: str, grade: Optional[str]=None, limit:int=20, order:str="desc") -> Dict[str, Any]:
    order_sql = "DESC" if order.lower() == "desc" else "ASC"
    sql = f"""
    SELECT
      room_id,
      COUNT(*) AS total,
      SUM(CASE WHEN status='present' THEN 1 ELSE 0 END) AS present
    FROM attendance
    WHERE att_date::date BETWEEN %s AND %s
      AND (%s IS NULL OR grade=%s)
    GROUP BY room_id
    ORDER BY (SUM(CASE WHEN status='present' THEN 1 ELSE 0 END)::float / NULLIF(COUNT(*),0)) {order_sql}
    LIMIT %s;
    """
    rows = _fetch(sql, [start, end, grade, grade, limit])
    return {
        "labels": [str(r["room_id"]) for r in rows],
        "rates": [round((r["present"]/r["total"])*100,2) if r["total"] else 0 for r in rows],
    }

def flagged_rooms(start: str, end: str, threshold: float=75.0, grade: Optional[str]=None) -> List[Dict[str, Any]]:
    sql = """
    SELECT
      room_id,
      COUNT(*) AS total,
      SUM(CASE WHEN status='present' THEN 1 ELSE 0 END) AS present
    FROM attendance
    WHERE att_date::date BETWEEN %s AND %s
      AND (%s IS NULL OR grade=%s)
    GROUP BY room_id
    HAVING (SUM(CASE WHEN status='present' THEN 1 ELSE 0 END)::float / NULLIF(COUNT(*),0)) * 100 < %s
    ORDER BY (SUM(CASE WHEN status='present' THEN 1 ELSE 0 END)::float / NULLIF(COUNT(*),0)) ASC
    LIMIT 50;
    """
    rows = _fetch(sql, [start, end, grade, grade, threshold])
    return [{"room_id": str(r["room_id"]), "rate": round((r["present"]/r["total"])*100,2)} for r in rows]
