# import requests
# from django.conf import settings
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from datetime import date, timedelta
# from attendance.models import Darajah, Hizb, HizbGroup, AttendanceRecord, Student


# def _date_range(days: int):
#     end = date.today()
#     start = end - timedelta(days=days)
#     return start.isoformat(), end.isoformat()


# def build_summary(daily_data, flagged_data):
#     if not daily_data or not daily_data.get("present"):
#         return {
#             "totalStudents": 0,
#             "presentRate": 0,
#             "absentRate": 0,
#             "lateRate": 0,
#             "flaggedCount": 0,
#         }

#     last_index = len(daily_data["present"]) - 1
#     present = daily_data["present"][last_index]
#     absent = daily_data["absent"][last_index]
#     late = daily_data["late"][last_index]
#     total = present + absent + late

#     return {
#         "totalStudents": total,
#         "presentRate": daily_data["rate"][last_index] if total else 0,
#         "absentRate": (absent / total * 100) if total else 0,
#         "lateRate": (late / total * 100) if total else 0,
#         "flaggedCount": len(flagged_data) if flagged_data else 0,
#     }


# def _get_float_param(request, key: str, default: float) -> float:
#     val = request.GET.get(key)
#     if val is None or val.strip() == "":
#         return default
#     try:
#         return float(val)
#     except ValueError:
#         return default


# def get_data_with_fallback(start, end, role, darajah=None, hizb=None, hizb_group=None):
#     # Lazy import to avoid circular import
#     from .services.attendance_aggregator import daily

#     data = daily(start, end, role, darajah, hizb, hizb_group)
#     if data and data.get("dates"):
#         return data

#     # Fallback to main API
#     resp = requests.get(
#         f"{settings.MAIN_API_URL}/attendance",
#         params={"from": start, "to": end,
#                 "darajah": darajah, "hizb": hizb, "hizb_group": hizb_group},
#         headers={"Authorization": f"Bearer {settings.MAIN_API_TOKEN}"}
#     )
#     api_data = resp.json()

#     # Save into Postgres as temporary records
#     for row in api_data.get("attendance", []):
#         try:
#             student = Student.objects.get(id=row["student_id"])
#         except Student.DoesNotExist:
#             continue

#         AttendanceRecord.objects.update_or_create(
#             student=student,
#             date=row.get("date"),
#             attendance_type=row.get("attendance_type", "fajr"),
#             defaults={
#                 "status": row.get("status", "present"),
#                 "created_by_id": row.get("created_by_id"),
#                 "remarks": row.get("remarks", ""),
#                 "is_temp": True,
#             }
#         )

#     # Re‑query Postgres
#     return daily(start, end, role, darajah, hizb, hizb_group)


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def dashboard_bootstrap(request):
#     # Lazy imports to avoid circular import
#     from .services.attendance_aggregator import weekly, room_ranking, flagged_rooms

#     role = request.user.role

#     from_date = request.GET.get("from")
#     to_date = request.GET.get("to")
#     if from_date and to_date:
#         start, end = from_date, to_date
#     else:
#         start, end = _date_range(30)

#     darajah = request.GET.get("darajah") or None
#     hizb = request.GET.get("hizb") or None
#     hizb_group = request.GET.get("hizb_group") or None

#     if role in ["prefect", "deputy_prefect"]:
#         hizb = request.user.hizb
#     elif role == "masool":
#         darajah = request.user.darajah
#     elif role == "muaddib":
#         hizb_group = request.user.hizb_group

#     threshold = _get_float_param(request, "threshold", 75.0)

#     daily_data = get_data_with_fallback(start, end, role, darajah, hizb, hizb_group)
#     weekly_data = weekly(start, end, role, darajah, hizb, hizb_group)
#     rooms_data = room_ranking(start, end, role, darajah, hizb, hizb_group)
#     flagged_data = flagged_rooms(start, end, role, darajah, hizb, hizb_group, threshold)

#     summary = build_summary(daily_data, flagged_data)

#     options = {
#         "darajah": list(Darajah.objects.values_list("name", flat=True).distinct()),
#         "hizb": list(Hizb.objects.values_list("name", flat=True).distinct()),
#         "hizb_group": list(HizbGroup.objects.values_list("group_number", flat=True).distinct()),
#     }

#     return Response({
#         "summary": summary,
#         "daily": daily_data,
#         "weekly": weekly_data,
#         "rooms": rooms_data,
#         "flagged": flagged_data,
#         "meta": {
#             "role": role,
#             "range": {"start": start, "end": end},
#             "filters": {"darajah": darajah, "hizb": hizb, "hizb_group": hizb_group},
#             "options": options,
#         },
#     })


import requests
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import date, timedelta
from attendance.models import Darajah, Hizb, HizbGroup, AttendanceRecord, Student


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
    # Lazy import to avoid circular import
    from .services.attendance_aggregator import daily

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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_bootstrap(request):
    # Lazy imports to avoid circular import
    from .services.attendance_aggregator import weekly, room_ranking, flagged_rooms

    role = request.user.role

    from_date = request.GET.get("from")
    to_date = request.GET.get("to")
    if from_date and to_date:
        start, end = from_date, to_date
    else:
        start, end = _date_range(30)

    threshold = _get_float_param(request, "threshold", 75.0)

    # Backend only cares about date range + role
    daily_data = get_data_with_fallback(start, end, role)
    weekly_data = weekly(start, end, role)
    rooms_data = room_ranking(start, end, role)
    flagged_data = flagged_rooms(start, end, role, threshold)

    summary = build_summary(daily_data, flagged_data)

    # Populate filter options for frontend selectors
    options = {
        "darajah": list(Darajah.objects.values_list("name", flat=True).distinct()),
        "hizb": list(Hizb.objects.values_list("name", flat=True).distinct()),
        "hizb_group": list(HizbGroup.objects.values_list("group_number", flat=True).distinct()),
    }

    return Response({
        "summary": summary,
        "daily": daily_data,
        "weekly": weekly_data,
        "rooms": rooms_data,
        "flagged": flagged_data,
        "meta": {
            "role": role,
            "range": {"start": start, "end": end},
            "options": options,
        },
    })
