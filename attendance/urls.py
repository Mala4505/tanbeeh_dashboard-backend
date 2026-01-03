from django.urls import path
from .views import *


urlpatterns = [
    path("attendance/admin/", UserManagementView.as_view(), name="attendance-admin"),
    # path("attendance/hizb/", HizbStudentsView.as_view(), name="attendance-hizb"),
    path("attendance/fajr/", FajrAttendanceView.as_view(), name="attendance-fajr"),
    path("attendance/maghrib_isha/", MaghribAttendanceView.as_view(), name="attendance-maghrib"),
    path("attendance/dua/", DuaAttendanceView.as_view(), name="attendance-dua"),
    path("attendance/summary/", AttendanceSummaryView.as_view(), name="attendance-summary"),
    path("attendance/flag/", FlagAttendanceView.as_view(), name="attendance-flag"), # ✅ new
    path("attendance/flags/", FlaggedAttendanceListView.as_view(), name="attendance-flags"), # ✅ new
    path("attendance/flag/<int:flag_id>/", UnflagAttendanceView.as_view(), name="attendance-unflag"), # ✅ new
    path("attendance/dashboard/", RoleBasedDashboardView.as_view(), name="attendance-dashboard"),
]
