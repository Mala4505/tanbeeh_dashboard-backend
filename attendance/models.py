# from django.db import models
# from django.conf import settings

# class Student(models.Model):
#     trno = models.CharField(max_length=50, unique=True)   # ITS/TRNO from API
#     bed_name = models.CharField(max_length=100, null=True, blank=True)
#     room = models.CharField(max_length=50, null=True, blank=True)
#     pantry = models.CharField(max_length=50, null=True, blank=True)
#     location = models.CharField(max_length=100, null=True, blank=True)
#     darajah = models.CharField(max_length=50, null=True, blank=True)
#     hizb = models.CharField(max_length=50, null=True, blank=True)

#     def __str__(self):
#         return f"{self.trno} - {self.bed_name or ''}"


# class AttendanceRecord(models.Model):
#     ATTENDANCE_TYPES = (
#         ("fajr", "Fajr"),
#         ("maghrib_isha", "Maghrib & Isha"),
#         ("dua", "Du'a"),
#     )

#     STATUS_CHOICES = (
#         ("present", "Present"),
#         ("absent", "Absent"),
#         ("late", "Late"),
#         ("excused", "Excused"),
#     )

#     student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendance_records")
#     date = models.DateField()
#     attendance_type = models.CharField(max_length=20, choices=ATTENDANCE_TYPES)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES)
#     remarks = models.TextField(null=True, blank=True)

#     created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

#     class Meta:
#         unique_together = ("student", "date", "attendance_type")

#     def __str__(self):
#         return f"{self.student.trno} - {self.date} - {self.attendance_type} ({self.status})"


# class AttendanceFlag(models.Model):
#     """
#     Separate table to track flags on attendance records.
#     Allows multiple flags per record, with reasons and who flagged it.
#     """
#     attendance_record = models.ForeignKey(AttendanceRecord, on_delete=models.CASCADE, related_name="flags")
#     flagged_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
#     reason = models.TextField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Flag on {self.attendance_record} by {self.flagged_by} ({self.created_at.date()})"


from django.db import models
from django.conf import settings


class Student(models.Model):
    trno = models.CharField(max_length=50, unique=True)   # ITS/TRNO from API
    bed_name = models.CharField(max_length=100, null=True, blank=True)
    room = models.CharField(max_length=50, null=True, blank=True)
    pantry = models.CharField(max_length=50, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    darajah = models.CharField(max_length=50, null=True, blank=True)
    hizb = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.trno} - {self.bed_name or ''}"


class AttendanceRecord(models.Model):
    ATTENDANCE_TYPES = (
        ("fajr", "Fajr"),
        ("maghrib_isha", "Maghrib & Isha"),
        ("dua", "Du'a"),
    )

    STATUS_CHOICES = (
        ("present", "Present"),
        ("absent", "Absent"),
        ("late", "Late"),
        ("excused", "Excused"),
    )

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendance_records")
    date = models.DateField()
    attendance_type = models.CharField(max_length=20, choices=ATTENDANCE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    remarks = models.TextField(null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    # Flag to mark temporary records fetched outside rolling 30 days
    is_temp = models.BooleanField(default=False)

    class Meta:
        unique_together = ("student", "date", "attendance_type")

    def __str__(self):
        return f"{self.student.trno} - {self.date} - {self.attendance_type} ({self.status})"


class AttendanceFlag(models.Model):
    """
    Tracks flags on attendance records.
    Flagged by Prefect/Deputy/Masool/Muaddib.
    Assigned to Lajnat Member based on room allocation.
    """
    attendance_record = models.ForeignKey(AttendanceRecord, on_delete=models.CASCADE, related_name="flags")
    flagged_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Assigned Lajnat Member responsible for flagged student
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_flags"
    )

    def __str__(self):
        return f"Flag on {self.attendance_record} by {self.flagged_by} ({self.created_at.date()})"


class AuditLog(models.Model):
    """
    Records all important actions for accountability.
    Examples: flagging, unflagging, login, logout, password change, data view.
    """
    ACTION_CHOICES = (
        ("flag", "Flagged student"),
        ("unflag", "Unflagged student"),
        ("login", "User login"),
        ("logout", "User logout"),
        ("password_change", "Password change"),
        ("data_view", "Viewed attendance data"),
        ("user_create", "Created new user"),
        ("user_reset_password", "Admin reset user password"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    target = models.CharField(max_length=255, null=True, blank=True)  # e.g., student TRNO or record ID
    metadata = models.JSONField(null=True, blank=True)  # extra context
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action} ({self.timestamp})"


class Notification(models.Model):
    """
    Alerts for flagged students or other role-based events.
    Typically sent to Lajnat Members when a student is flagged.
    """
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    related_flag = models.ForeignKey(AttendanceFlag, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient} - {self.message[:30]}..."


# Assignment tables

class HizbAssignment(models.Model):
    """
    One Prefect + one Deputy Prefect per Hizb.
    """
    hizb = models.CharField(max_length=50, unique=True)
    prefect = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="prefect_hizb")
    deputy_prefect = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="deputy_prefect_hizb")

    def __str__(self):
        return f"Hizb {self.hizb} - Prefect: {self.prefect.username}, Deputy: {self.deputy_prefect.username}"


class MasoolAssignment(models.Model):
    """
    Many Masools, each assigned to multiple students.
    """
    masool = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="masool_assignments")
    students = models.ManyToManyField(Student, related_name="masool_students")

    def __str__(self):
        return f"Masool {self.masool.username}"


class MuaddibGroup(models.Model):
    """
    Each Hizb can have multiple Muaddib groups.
    Each group is assigned to one Muaddib and contains multiple students.
    """
    hizb = models.CharField(max_length=50)
    muaddib = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="muaddib_groups")
    students = models.ManyToManyField(Student, related_name="muaddib_students")

    def __str__(self):
        return f"Muaddib {self.muaddib.username} - Hizb {self.hizb}"


class LajnatAssignment(models.Model):
    """
    Many Lajnat Members, each assigned to multiple students.
    Flagged students are routed here.
    """
    lajnat_member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lajnat_assignments")
    students = models.ManyToManyField(Student, related_name="lajnat_students")

    def __str__(self):
        return f"Lajnat Member {self.lajnat_member.username}"
