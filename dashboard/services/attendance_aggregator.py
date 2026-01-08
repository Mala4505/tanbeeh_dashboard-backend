import requests
from django.conf import settings
from datetime import date, timedelta
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


def daily(start: str, end: str, role: str) -> Dict[str, Any]:
    sql = f"""
    SELECT
      a.date::date AS date,
      COUNT(*) AS total,
      SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) AS present,
      SUM(CASE WHEN a.status='absent' THEN 1 ELSE 0 END) AS absent,
      SUM(CASE WHEN a.status='late' THEN 1 ELSE 0 END) AS late
    FROM {ATT_TABLE} a
    JOIN {STU_TABLE} s ON a.student_id = s.id
    WHERE a.date BETWEEN %s AND %s
    GROUP BY a.date
    ORDER BY a.date ASC;
    """
    rows = _fetch(sql, [start, end])
    return {
        "dates": [str(r["date"]) for r in rows],
        "present": [int(r["present"]) for r in rows],
        "absent": [int(r["absent"]) for r in rows],
        "late": [int(r["late"]) for r in rows],
        "rate": [round((r["present"]/r["total"])*100, 2) if r["total"] else 0 for r in rows],
    }


def weekly(start: str, end: str, role: str) -> Dict[str, Any]:
    sql = f"""
    SELECT
      date_trunc('week', a.date)::date AS week,
      COUNT(*) AS total,
      SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) AS present,
      SUM(CASE WHEN a.status='absent' THEN 1 ELSE 0 END) AS absent,
      SUM(CASE WHEN a.status='late' THEN 1 ELSE 0 END) AS late
    FROM {ATT_TABLE} a
    JOIN {STU_TABLE} s ON a.student_id = s.id
    WHERE a.date BETWEEN %s AND %s
    GROUP BY week
    ORDER BY week ASC;
    """
    rows = _fetch(sql, [start, end])
    return {
        "weeks": [str(r["week"]) for r in rows],
        "present": [int(r["present"]) for r in rows],
        "absent": [int(r["absent"]) for r in rows],
        "late": [int(r["late"]) for r in rows],
    }


def room_ranking(start: str, end: str, role: str, limit: int = 20) -> Dict[str, Any]:
    sql = f"""
    SELECT
      s.room,
      COUNT(*) AS total,
      SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) AS present
    FROM {ATT_TABLE} a
    JOIN {STU_TABLE} s ON a.student_id = s.id
    WHERE a.date BETWEEN %s AND %s
    GROUP BY s.room
    ORDER BY (SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END)::float / NULLIF(COUNT(*),0)) DESC
    LIMIT %s;
    """
    rows = _fetch(sql, [start, end, limit])
    return {
        "labels": [str(r["room"]) for r in rows],
        "rates": [round((r["present"]/r["total"])*100, 2) if r["total"] else 0 for r in rows],
    }


def flagged_rooms(start: str, end: str, role: str, threshold: float = 75.0) -> List[Dict[str, Any]]:
    sql = f"""
    SELECT
      s.room,
      COUNT(*) AS total,
      SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) AS present
    FROM {ATT_TABLE} a
    JOIN {STU_TABLE} s ON a.student_id = s.id
    WHERE a.date BETWEEN %s AND %s
    GROUP BY s.room
    HAVING (SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END)::float / NULLIF(COUNT(*),0)) * 100 < %s
    ORDER BY (SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END)::float / NULLIF(COUNT(*),0)) ASC
    LIMIT 50;
    """
    rows = _fetch(sql, [start, end, threshold])
    return [
        {
            "room": str(r["room"]),
            "rate": round((r["present"] / r["total"]) * 100, 2) if r["total"] else 0
        }
        for r in rows
    ]


def _date_range(days: int):
    end = date.today()
    start = end - timedelta(days=days)
    return start.isoformat(), end.isoformat()


def build_summary(daily_data, flagged_data):
    if not daily_data or not daily_data.get("present"):
        return {
            "totalStudents": 0,
            "presentRate": 0,
            "absentRate": 0,
            "lateRate": 0,
            "flaggedCount": 0,
        }
    last_index = len(daily_data["present"]) - 1
    present = daily_data["present"][last_index]
    absent = daily_data["absent"][last_index]
    late = daily_data["late"][last_index]
    total = present + absent + late
    return {
        "totalStudents": total,
        "presentRate": daily_data["rate"][last_index] if total else 0,
        "absentRate": (absent / total * 100) if total else 0,
        "lateRate": (late / total * 100) if total else 0,
        "flaggedCount": len(flagged_data) if flagged_data else 0,
    }


def _get_float_param(request, key: str, default: float) -> float:
    val = request.GET.get(key)
    if val is None or val.strip() == "":
        return default
    try:
        return float(val)
    except ValueError:
        return default


def get_data_with_fallback(start, end, role):
    data = daily(start, end, role)
    if data and data.get("dates"):
        return data

    # Fallback to main API
    resp = requests.get(
        f"{settings.MAIN_API_URL}/attendance",
        params={"from": start, "to": end},
        headers={"Authorization": f"Bearer {settings.MAIN_API_TOKEN}"}
    )
    api_data = resp.json()

    # Save into Postgres as temporary records
    for row in api_data.get("attendance", []):
        try:
            student = Student.objects.get(id=row["student_id"])
        except Student.DoesNotExist:
            continue

        AttendanceRecord.objects.update_or_create(
            student=student,
            date=row.get("date"),
            attendance_type=row.get("attendance_type", "fajr"),
            defaults={
                "status": row.get("status", "present"),
                "created_by_id": row.get("created_by_id"),
                "remarks": row.get("remarks", ""),
                "is_temp": True,
            }
        )

    # Re‑query Postgres
    return daily(start, end, role)
