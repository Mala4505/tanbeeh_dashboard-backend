from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import date, timedelta
from .services.attendance_aggregator import daily, weekly, room_ranking, flagged_rooms
from attendance.models import Darajah, Hizb, HizbGroup


def _date_range(days: int):
    end = date.today()
    start = end - timedelta(days=days)
    return start.isoformat(), end.isoformat()


def build_summary(daily_data, flagged_data):
    """
    Build a role-scoped summary from the filtered daily + flagged data.
    """
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

    present_rate = daily_data["rate"][last_index] if total else 0
    absent_rate = (absent / total * 100) if total else 0
    late_rate = (late / total * 100) if total else 0
    flagged_count = len(flagged_data) if flagged_data else 0

    return {
        "totalStudents": total,
        "presentRate": present_rate,
        "absentRate": absent_rate,
        "lateRate": late_rate,
        "flaggedCount": flagged_count,
    }


def _get_float_param(request, key: str, default: float) -> float:
    """Safely parse a float query param, falling back to default if empty/invalid."""
    val = request.GET.get(key)
    if val is None or val.strip() == "":
        return default
    try:
        return float(val)
    except ValueError:
        return default

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_bootstrap(request):
    role = request.user.role

    # Support explicit from/to or fallback to days
    from_date = request.GET.get("from")
    to_date = request.GET.get("to")
    if from_date and to_date:
        start, end = from_date, to_date
    else:
        days = int(request.GET.get("days", "30"))
        start, end = _date_range(days)

    # Read filters from query string
    darajah = request.GET.get("darajah") or None
    hizb = request.GET.get("hizb") or None
    hizb_group = request.GET.get("hizb_group") or None

    # Role-based scoping overrides query filters if needed
    if role in ["prefect", "deputy_prefect"]:
        hizb = request.user.hizb
    elif role == "masool":
        darajah = request.user.darajah
    elif role == "muaddib":
        hizb_group = request.user.hizb_group
    # admin/lajnat_member keep whatever was passed in

    threshold = _get_float_param(request, "threshold", 75.0)

    # Apply filters to your aggregators
    daily_data = daily(start, end, darajah, hizb, hizb_group)
    weekly_data = weekly(start, end, darajah, hizb, hizb_group)
    rooms_data = room_ranking(
        start, end, darajah,
        limit=int(request.GET.get("limit", "20")),
        order=request.GET.get("order", "desc")
    )
    flagged_data = flagged_rooms(start, end, threshold, darajah)

    summary = build_summary(daily_data, flagged_data)

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
            "filters": {
                "darajah": darajah,
                "hizb": hizb,
                "hizb_group": hizb_group,
            },
            "options": options,
        },
    })
