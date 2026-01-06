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
#     date = models.DateField(null=True, blank=True)
#     tp = models.TimeField(null=True, blank=True)  # prayer time from prayer endpoints
#     attendance_type = models.CharField(max_length=20, choices=ATTENDANCE_TYPES)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES)
#     remarks = models.TextField(null=True, blank=True)

#     created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

#     # Flag to mark temporary records fetched outside rolling 30 days
#     is_temp = models.BooleanField(default=False)

#     class Meta:
#         constraints = [
#             # Ensure uniqueness per student/date/prayer type
#             models.UniqueConstraint(fields=["student", "date", "attendance_type"], name="unique_attendance_record")
#         ]
#         indexes = [
#             models.Index(fields=["date", "attendance_type"]),
#             models.Index(fields=["status"]),
#             models.Index(fields=["-date"]),
#         ]

#     def __str__(self):
#         return f"{self.student.trno} - {self.date} - {self.attendance_type} ({self.status})"


# class AttendanceFlag(models.Model):
#     attendance_record = models.ForeignKey(AttendanceRecord, on_delete=models.CASCADE, related_name="flags")
#     flagged_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
#     reason = models.TextField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     assigned_to = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="assigned_flags"
#     )

#     def __str__(self):
#         return f"Flag on {self.attendance_record} by {self.flagged_by} ({self.created_at.date()})"


# class AuditLog(models.Model):
#     ACTION_CHOICES = (
#         ("flag", "Flagged student"),
#         ("unflag", "Unflagged student"),
#         ("login", "User login"),
#         ("logout", "User logout"),
#         ("password_change", "Password change"),
#         ("data_view", "Viewed attendance data"),
#         ("user_create", "Created new user"),
#         ("user_reset_password", "Admin reset user password"),
#     )

#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
#     action = models.CharField(max_length=50, choices=ACTION_CHOICES)
#     target = models.CharField(max_length=255, null=True, blank=True)
#     metadata = models.JSONField(null=True, blank=True)
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user} - {self.action} ({self.timestamp})"


# class Notification(models.Model):
#     recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
#     message = models.TextField()
#     related_flag = models.ForeignKey(AttendanceFlag, on_delete=models.CASCADE, null=True, blank=True)
#     is_read = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Notification for {self.recipient} - {self.message[:30]}..."


# class HizbAssignment(models.Model):
#     hizb = models.CharField(max_length=50, unique=True)
#     prefect = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="prefect_hizb")
#     deputy_prefect = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="deputy_prefect_hizb")

#     def __str__(self):
#         return f"Hizb {self.hizb} - Prefect: {self.prefect.username}, Deputy: {self.deputy_prefect.username}"


# class MasoolAssignment(models.Model):
#     masool = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="masool_assignments")
#     students = models.ManyToManyField(Student, related_name="masool_students")

#     def __str__(self):
#         return f"Masool {self.masool.username}"


# class MuaddibGroup(models.Model):
#     hizb = models.CharField(max_length=50)
#     muaddib = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="muaddib_groups")
#     students = models.ManyToManyField(Student, related_name="muaddib_students")

#     def __str__(self):
#         return f"Muaddib {self.muaddib.username} - Hizb {self.hizb}"


# class LajnatAssignment(models.Model):
#     lajnat_member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lajnat_assignments")
#     students = models.ManyToManyField(Student, related_name="lajnat_students")

#     def __str__(self):
#         return f"Lajnat Member {self.lajnat_member.username}"


from django.db import models
from django.conf import settings


# -----------------------------
# Core Academic Structures
# -----------------------------

class Darajah(models.Model):
    """Represents a class (darajah)"""
    name = models.CharField(max_length=100, unique=True, default="Unknown Class")

    def __str__(self):
        return self.name


class Hizb(models.Model):
    name = models.CharField(max_length=100, unique=True, default="Unknown Hizb")

    def __str__(self):
        return self.name


class HizbGroup(models.Model):
    """Each hizb is split into 4 groups"""
    hizb = models.ForeignKey(Hizb, on_delete=models.CASCADE, related_name="groups")
    group_number = models.PositiveIntegerField(default=1)  # 1–4

    class Meta:
        unique_together = ("hizb", "group_number")

    def __str__(self):
        return f"{self.hizb} - Group {self.group_number}"


# -----------------------------
# Student & Attendance
# -----------------------------

class Student(models.Model):
    """Master student table with normalized links"""
    trno = models.CharField(max_length=50, unique=True, default="0000")
    bed_name = models.CharField(max_length=100, null=True, blank=True, default="")
    room = models.CharField(max_length=50, null=True, blank=True, default="")
    pantry = models.CharField(max_length=50, null=True, blank=True, default="")
    location = models.CharField(max_length=100, null=True, blank=True, default="")

    darajah = models.ForeignKey(Darajah, on_delete=models.SET_NULL, null=True, blank=True, related_name="students")
    hizb = models.ForeignKey(Hizb, on_delete=models.SET_NULL, null=True, blank=True, related_name="students")
    hizb_group = models.ForeignKey(HizbGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name="students")

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
    date = models.DateField(null=True, blank=True)
    tp = models.TimeField(null=True, blank=True)
    attendance_type = models.CharField(max_length=20, choices=ATTENDANCE_TYPES, default="fajr")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="present")
    remarks = models.TextField(null=True, blank=True, default="")

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    is_temp = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["student", "date", "attendance_type"], name="unique_attendance_record")
        ]
        indexes = [
            models.Index(fields=["date", "attendance_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["-date"]),
        ]

    def __str__(self):
        return f"{self.student.trno} - {self.date} - {self.attendance_type} ({self.status})"


class AttendanceFlag(models.Model):
    attendance_record = models.ForeignKey(AttendanceRecord, on_delete=models.CASCADE, related_name="flags")
    flagged_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.TextField(null=True, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

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
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, default="login")
    target = models.CharField(max_length=255, null=True, blank=True, default="")
    metadata = models.JSONField(null=True, blank=True, default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action} ({self.timestamp})"


class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField(default="Notification")
    related_flag = models.ForeignKey(AttendanceFlag, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient} - {self.message[:30]}..."


# -----------------------------
# Role Assignments
# -----------------------------

class HizbAssignment(models.Model):
    """Prefect & Deputy assigned to a Hizb"""
    hizb = models.ForeignKey(
        Hizb,
        on_delete=models.CASCADE,
        related_name="assignments",
        default=1  # assumes Hizb with pk=1 exists
    )
    prefect = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="prefect_hizb",
        default=1  # assumes User with pk=1 exists
    )
    deputy_prefect = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="deputy_prefect_hizb",
        default=1  # assumes User with pk=1 exists
    )

    def __str__(self):
        return f"{self.hizb} - Prefect: {self.prefect.username}, Deputy: {self.deputy_prefect.username}"


class MasoolAssignment(models.Model):
    """Masool assigned to a Darajah (class)"""
    masool = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="masool_assignments",
        default=1  # assumes User with pk=1 exists
    )
    darajah = models.ForeignKey(
        Darajah,
        on_delete=models.CASCADE,
        related_name="masool_assignments",
        default=1  # assumes Darajah with pk=1 exists
    )
    students = models.ManyToManyField(Student, related_name="masool_students")

    def __str__(self):
        return f"Masool {self.masool.username} - {self.darajah.name}"


class MuaddibGroupAssignment(models.Model):
    """Muaddib assigned to a HizbGroup"""
    muaddib = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="muaddib_groups",
        default=1  # assumes User with pk=1 exists
    )
    hizb_group = models.ForeignKey(
        HizbGroup,
        on_delete=models.CASCADE,
        related_name="muaddib_assignments",
        default=1  # assumes HizbGroup with pk=1 exists
    )
    students = models.ManyToManyField(Student, related_name="muaddib_students")

    def __str__(self):
        return f"Muaddib {self.muaddib.username} - {self.hizb_group}"


class LajnatAssignment(models.Model):
    """Lajnat member has global access to students"""
    lajnat_member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lajnat_assignments",
        default=1  # assumes User with pk=1 exists
    )
    students = models.ManyToManyField(Student, related_name="lajnat_students")

    def __str__(self):
        return f"Lajnat Member {self.lajnat_member.username}"
