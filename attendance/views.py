from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import now
from datetime import date, timedelta

from .models import (
    Student,
    AttendanceRecord,
    AttendanceFlag,
    AuditLog,
    Notification,
    HizbAssignment,
    MasoolAssignment,
    MuaddibGroup,
    LajnatAssignment,
)
from .serializers import (
    AttendanceRecordSerializer,
    AttendanceFlagSerializer,
    AuditLogSerializer,
    NotificationSerializer,
    HizbAssignmentSerializer,
    MasoolAssignmentSerializer,
    MuaddibGroupSerializer,
    LajnatAssignmentSerializer,
)
from .permissions import (
    IsAdmin,
    IsFlaggingRole,
    IsDashboardRole,
    IsAssignmentRole,
    IsAuditViewer,
)
from .services.university_api import fetch_attendance
from .utils.normalizer import normalize_student_attendance
from .utils.filters import filter_by_role


# --- User Management (Admin only) ---
class UserManagementView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response({"message": "Admin access granted"})


# --- Attendance Fetching ---
class AttendanceBaseView(APIView):
    permission_classes = [IsAuthenticated]
    attendance_key = None  # override in subclasses

    def get(self, request):
        today = date.today()
        frm = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        to = today.strftime("%Y-%m-%d")
        token = "c701a5a2-f53f-4ca3-86e4-2a85657066bc"

        raw_data = fetch_attendance(self.attendance_key, frm, to, token)
        combined = [normalize_student_attendance(row, self.attendance_key) for row in raw_data]
        filtered = filter_by_role(request.user, combined)

        return Response({"attendance": filtered})


class FajrAttendanceView(AttendanceBaseView):
    attendance_key = "Fajr_Namaz_Talabat"


class MaghribAttendanceView(AttendanceBaseView):
    attendance_key = "Maghrib_Isha_Talabat"


class DuaAttendanceView(AttendanceBaseView):
    attendance_key = "Dua_Talabat"


# --- Attendance Summary ---
class AttendanceSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        type_param = request.query_params.get("type", "Fajr_Namaz_Talabat")

        today = date.today()
        frm = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        to = today.strftime("%Y-%m-%d")
        token = "c701a5a2-f53f-4ca3-86e4-2a85657066bc"

        raw_data = fetch_attendance(type_param, frm, to, token)
        combined = [normalize_student_attendance(row, type_param) for row in raw_data]
        filtered = filter_by_role(request.user, combined)

        summary = {
            "total_records": len(filtered),
            "present_count": sum(1 for r in filtered if r["status"] == "present"),
            "absent_count": sum(1 for r in filtered if r["status"] == "absent"),
            "late_count": sum(1 for r in filtered if r["status"] == "late"),
            "excused_count": sum(1 for r in filtered if r["status"] == "excused"),
        }

        return Response(summary)


# --- Flagging ---
class FlagAttendanceView(APIView):
    """
    POST: Flag an attendance record
    Body: { "attendance_id": <record_id>, "reason": "optional reason" }
    """
    permission_classes = [IsFlaggingRole]

    def post(self, request):
        attendance_id = request.data.get("attendance_id")
        reason = request.data.get("reason", "")

        if not attendance_id:
            return Response({"message": "attendance_id required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            record = AttendanceRecord.objects.get(id=attendance_id)
        except AttendanceRecord.DoesNotExist:
            return Response({"message": "Attendance record not found"}, status=status.HTTP_404_NOT_FOUND)

        # Create flag
        flag = AttendanceFlag.objects.create(
            attendance_record=record,
            flagged_by=request.user,
            reason=reason
        )

        # Assign to correct Lajnat Member (based on room allocation)
        lajnat_assignment = LajnatAssignment.objects.filter(students=record.student).first()
        if lajnat_assignment:
            flag.assigned_to = lajnat_assignment.lajnat_member
            flag.save()

            # Create notification
            Notification.objects.create(
                recipient=lajnat_assignment.lajnat_member,
                message=f"Student {record.student.trno} flagged for {record.attendance_type}",
                related_flag=flag
            )

        # Audit log
        AuditLog.objects.create(
            user=request.user,
            action="flag",
            target=str(record.id),
            metadata={"reason": reason}
        )

        return Response(AttendanceFlagSerializer(flag).data, status=status.HTTP_201_CREATED)


class FlaggedAttendanceListView(APIView):
    """
    GET: List all flagged attendance records
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        flags = AttendanceFlag.objects.select_related("attendance_record", "attendance_record__student", "flagged_by")
        serializer = AttendanceFlagSerializer(flags, many=True)
        return Response({"flags": serializer.data})


class UnflagAttendanceView(APIView):
    """
    DELETE: Remove a flag from an attendance record
    URL: /api/attendance/flag/<flag_id>/
    """
    permission_classes = [IsFlaggingRole]

    def delete(self, request, flag_id):
        try:
            flag = AttendanceFlag.objects.get(id=flag_id)
        except AttendanceFlag.DoesNotExist:
            return Response({"message": "Flag not found"}, status=status.HTTP_404_NOT_FOUND)

        if flag.flagged_by != request.user and request.user.role != "admin":
            return Response({"message": "Not authorized to remove this flag"}, status=status.HTTP_403_FORBIDDEN)

        flag.delete()

        # Audit log
        AuditLog.objects.create(
            user=request.user,
            action="unflag",
            target=str(flag_id),
            metadata={"removed_by": request.user.username}
        )

        return Response({"message": "Flag removed successfully"}, status=status.HTTP_200_OK)


# --- Dashboards ---
class RoleBasedDashboardView(APIView):
    """
    GET: Return role-specific attendance summaries
    """
    permission_classes = [IsDashboardRole]

    def get(self, request):
        user = request.user
        role = user.role

        if role == "admin":
            total_records = AttendanceRecord.objects.count()
            flagged_records = AttendanceRecord.objects.filter(flags__isnull=False).count()
            present_count = AttendanceRecord.objects.filter(status="present").count()
            absent_count = AttendanceRecord.objects.filter(status="absent").count()

            return Response({
                "role": "admin",
                "stats": {
                    "total_records": total_records,
                    "flagged_records": flagged_records,
                    "present": present_count,
                    "absent": absent_count,
                }
            })

        elif role in ["prefect", "deputy_prefect"]:
            hizb = user.hizb
            records = AttendanceRecord.objects.filter(student__hizb=hizb)
            return Response({
                "role": role,
                "hizb": hizb,
                "stats": {
                    "total_records": records.count(),
                    "present": records.filter(status="present").count(),
                    "absent": records.filter(status="absent").count(),
                }
            })

        elif role == "masool":
            assignments = MasoolAssignment.objects.filter(masool=user).first()
            records = AttendanceRecord.objects.filter(student__in=assignments.students.all()) if assignments else []
            return Response({
                "role": "masool",
                "stats": {
                    "total_records": len(records),
                    "present": sum(1 for r in records if r.status == "present"),
                    "absent": sum(1 for r in records if r.status == "absent"),
                }
            })

        elif role == "muaddib":
            groups = MuaddibGroup.objects.filter(muaddib=user)
            students = Student.objects.filter(muaddib_students__in=groups).distinct()
            records = AttendanceRecord.objects.filter(student__in=students)
            return Response({
                "role": "muaddib",
                "stats": {
                    "total_records": records.count(),
                    "present": records.filter(status="present").count(),
                    "absent": records.filter(status="absent").count(),
                }
            })

        elif role == "lajnat_member":
            # Lajnat Member: only see flagged students assigned to them
            flags = AttendanceFlag.objects.filter(assigned_to=user)
            flagged_students = [f.attendance_record.student for f in flags]

            return Response({
                "role": "lajnat_member",
                "stats": {
                    "total_flags": flags.count(),
                    "students_flagged": len(flagged_students),
                },
                "flagged_students": [
                    {"trno": s.trno, "bed_name": s.bed_name, "room": s.room}
                    for s in flagged_students
                ]
            })

        else:
            return Response({"message": "Role not authorized for dashboard"}, status=403)


# --- Notifications ---
class NotificationListView(APIView):
    """
    GET: List notifications for the logged-in user
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(recipient=request.user).order_by("-created_at")
        serializer = NotificationSerializer(notifications, many=True)
        return Response({"notifications": serializer.data})


class NotificationReadView(APIView):
    """
    POST: Mark a notification as read
    Body: { "notification_id": <id> }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        notif_id = request.data.get("notification_id")
        try:
            notif = Notification.objects.get(id=notif_id, recipient=request.user)
        except Notification.DoesNotExist:
            return Response({"message": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)

        notif.is_read = True
        notif.save()
        return Response({"message": "Notification marked as read"})


# --- Audit Logs ---
class AuditLogListView(APIView):
    """
    GET: List all audit logs (Admin only)
    """
    permission_classes = [IsAuditViewer]

    def get(self, request):
        logs = AuditLog.objects.all().order_by("-timestamp")
        serializer = AuditLogSerializer(logs, many=True)
        return Response({"audit_logs": serializer.data})


# --- Assignment Management (Admin only) ---
class HizbAssignmentView(APIView):
    permission_classes = [IsAssignmentRole]

    def post(self, request):
        hizb = request.data.get("hizb")
        prefect_id = request.data.get("prefect_id")
        deputy_id = request.data.get("deputy_id")

        if not hizb or not prefect_id or not deputy_id:
            return Response({"message": "hizb, prefect_id, and deputy_id required"}, status=400)

        assignment, created = HizbAssignment.objects.update_or_create(
            hizb=hizb,
            defaults={"prefect_id": prefect_id, "deputy_prefect_id": deputy_id}
        )
        serializer = HizbAssignmentSerializer(assignment)
        return Response(serializer.data, status=201 if created else 200)


class MasoolAssignmentView(APIView):
    permission_classes = [IsAssignmentRole]

    def post(self, request):
        masool_id = request.data.get("masool_id")
        student_ids = request.data.get("student_ids", [])

        if not masool_id or not student_ids:
            return Response({"message": "masool_id and student_ids required"}, status=400)

        assignment, created = MasoolAssignment.objects.update_or_create(
            masool_id=masool_id,
            defaults={}
        )
        assignment.students.set(student_ids)
        serializer = MasoolAssignmentSerializer(assignment)
        return Response(serializer.data, status=201 if created else 200)


class MuaddibGroupView(APIView):
    permission_classes = [IsAssignmentRole]

    def post(self, request):
        hizb = request.data.get("hizb")
        muaddib_id = request.data.get("muaddib_id")
        student_ids = request.data.get("student_ids", [])

        if not hizb or not muaddib_id or not student_ids:
            return Response({"message": "hizb, muaddib_id, and student_ids required"}, status=400)

        group, created = MuaddibGroup.objects.update_or_create(
            hizb=hizb,
            muaddib_id=muaddib_id,
            defaults={}
        )
        group.students.set(student_ids)
        serializer = MuaddibGroupSerializer(group)
        return Response(serializer.data, status=201 if created else 200)


class LajnatAssignmentView(APIView):
    permission_classes = [IsAssignmentRole]

    def post(self, request):
        lajnat_id = request.data.get("lajnat_id")
        student_ids = request.data.get("student_ids", [])

        if not lajnat_id or not student_ids:
            return Response({"message": "lajnat_id and student_ids required"}, status=400)

        assignment, created = LajnatAssignment.objects.update_or_create(
            lajnat_member_id=lajnat_id,
            defaults={}
        )
        assignment.students.set(student_ids)
        serializer = LajnatAssignmentSerializer(assignment)
        return Response(serializer.data, status=201 if created else 200)
