from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import date, timedelta
from .services.attendance_aggregator import daily, weekly, room_ranking, flagged_rooms

def _date_range(days: int):
    end = date.today()
    start = end - timedelta(days=days)
    return start.isoformat(), end.isoformat()

@api_view(["GET"])
def dashboard_bootstrap(request):
    role = request.GET.get("role", "prefect")
    days = int(request.GET.get("days", "30"))
    start, end = _date_range(days)

    grade = request.GET.get("grade")
    room = request.GET.get("room")
    teacher = request.GET.get("teacher")
    threshold = float(request.GET.get("threshold", "75"))

    return Response({
        "daily": daily(start, end, grade, room, teacher),
        "weekly": weekly(start, end, grade, room, teacher),
        "rooms": room_ranking(start, end, grade, limit=int(request.GET.get("limit","20")), order=request.GET.get("order","desc")),
        "flagged": flagged_rooms(start, end, threshold, grade),
        "meta": {"role": role, "range": {"start": start, "end": end}},
    })
