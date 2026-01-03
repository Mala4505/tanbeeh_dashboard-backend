from rest_framework import serializers
from django.conf import settings
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


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            "id",
            "trno",
            "bed_name",
            "room",
            "pantry",
            "location",
            "darajah",
            "hizb",
        ]


class AttendanceRecordSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = [
            "id",
            "student",
            "date",
            "attendance_type",
            "status",
            "remarks",
            "created_by",
            "is_temp",
        ]


class AttendanceFlagSerializer(serializers.ModelSerializer):
    attendance_record = AttendanceRecordSerializer(read_only=True)
    flagged_by = serializers.StringRelatedField(read_only=True)
    assigned_to = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = AttendanceFlag
        fields = [
            "id",
            "attendance_record",
            "flagged_by",
            "reason",
            "created_at",
            "assigned_to",
        ]


class AuditLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "user",
            "action",
            "target",
            "metadata",
            "timestamp",
        ]


class NotificationSerializer(serializers.ModelSerializer):
    recipient = serializers.StringRelatedField(read_only=True)
    related_flag = AttendanceFlagSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "recipient",
            "message",
            "related_flag",
            "is_read",
            "created_at",
        ]


# Assignment serializers

class HizbAssignmentSerializer(serializers.ModelSerializer):
    prefect = serializers.StringRelatedField(read_only=True)
    deputy_prefect = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = HizbAssignment
        fields = [
            "id",
            "hizb",
            "prefect",
            "deputy_prefect",
        ]


class MasoolAssignmentSerializer(serializers.ModelSerializer):
    masool = serializers.StringRelatedField(read_only=True)
    students = StudentSerializer(many=True, read_only=True)

    class Meta:
        model = MasoolAssignment
        fields = [
            "id",
            "masool",
            "students",
        ]


class MuaddibGroupSerializer(serializers.ModelSerializer):
    muaddib = serializers.StringRelatedField(read_only=True)
    students = StudentSerializer(many=True, read_only=True)

    class Meta:
        model = MuaddibGroup
        fields = [
            "id",
            "hizb",
            "muaddib",
            "students",
        ]


class LajnatAssignmentSerializer(serializers.ModelSerializer):
    lajnat_member = serializers.StringRelatedField(read_only=True)
    students = StudentSerializer(many=True, read_only=True)

    class Meta:
        model = LajnatAssignment
        fields = [
            "id",
            "lajnat_member",
            "students",
        ]


# Dashboard serializers

class StudentAttendanceSummarySerializer(serializers.Serializer):
    student = StudentSerializer()
    total_present = serializers.IntegerField()
    total_absent = serializers.IntegerField()
    total_late = serializers.IntegerField()
    total_excused = serializers.IntegerField()


class DashboardSummarySerializer(serializers.Serializer):
    """
    Generic serializer for dashboard responses.
    Can be used for Prefect, Masool, Muaddib, Lajnat, Admin dashboards.
    """
    role = serializers.CharField()
    date_range = serializers.CharField()
    total_students = serializers.IntegerField()
    total_records = serializers.IntegerField()
    attendance_breakdown = serializers.DictField()
    flagged_students = AttendanceFlagSerializer(many=True)
