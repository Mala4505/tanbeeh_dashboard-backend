# from django.contrib.auth.models import AbstractUser
# from django.db import models

# class CustomUser(AbstractUser):
#     ROLE_CHOICES = (
#         ("admin", "Admin"),
#         ("staff", "Staff"),
#         ("faculty", "Faculty"),
#         ("prefect", "Prefect"),
#     )
#     role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="staff")
#     its_number = models.CharField(max_length=50, unique=True, null=True, blank=True)

#     def __str__(self):
#         return f"{self.username} ({self.role})"
from django.contrib.auth.models import AbstractUser
from django.db import models
from attendance.models import Darajah, Hizb, Student


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("staff", "Staff"),
        ("faculty", "Faculty"),
        ("prefect", "Prefect"),
        ("deputy_prefect", "Deputy Prefect"),
        ("masool", "Masool"),
        ("muaddib", "Muaddib"),
        ("lajnat_member", "Lajnat Member"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="staff")
    its_number = models.CharField(max_length=50, unique=True, null=True, blank=True)

    darajah = models.ForeignKey(Darajah, null=True, blank=True, on_delete=models.SET_NULL)
    hizb = models.ForeignKey(Hizb, null=True, blank=True, on_delete=models.SET_NULL)
    students = models.ManyToManyField(Student, blank=True, related_name="assigned_users")

    # Account management flags
    is_verified = models.BooleanField(default=False)  # Admin can mark user as verified
    is_active = models.BooleanField(default=True)     # Standard Django field, but explicitly kept

    USERNAME_FIELD = "its_number"
    REQUIRED_FIELDS = ["username","role"]
    
    def __str__(self):
        return f"({self.its_number})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
