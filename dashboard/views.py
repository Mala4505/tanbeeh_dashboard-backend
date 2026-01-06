from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import date, timedelta
from .services.attendance_aggregator import daily, weekly, room_ranking, flagged_rooms

def _date_range(days: int):
    end = date.today()
    start = end - timedelta(days=days)
    return start.isoformat(), end.isoformat()

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_bootstrap(request):
    # Always trust the authenticated user
    role = request.user.role
    days = int(request.GET.get("days", "30"))
    start, end = _date_range(days)

    # Default filters
    grade = None
    room = None
    teacher = None

    # Role-based scoping
    if role in ["prefect", "deputy_prefect"]:
        # Prefect/Deputy → filter by Hizb
        grade = request.user.hizb   # stored as string in CustomUser
    elif role == "masool":
        # Masool → filter by Darajah
        grade = request.user.darajah
    elif role == "muaddib":
        # Muaddib → filter by HizbGroup
        room = request.user.hizb_group
    elif role == "admin":
        # Admin → no filter, see everything
        pass
    elif role == "lajnat_member":
        # Lajnat → later integration
        pass

    threshold = float(request.GET.get("threshold", "75"))

    return Response({
        "daily": daily(start, end, grade, room, teacher),
        "weekly": weekly(start, end, grade, room, teacher),
        "rooms": room_ranking(
            start, end, grade,
            limit=int(request.GET.get("limit", "20")),
            order=request.GET.get("order", "desc")
        ),
        "flagged": flagged_rooms(start, end, threshold, grade),
        "meta": {
            "role": role,
            "range": {"start": start, "end": end},
            "filters": {"grade": grade, "room": room}
        },
    })
