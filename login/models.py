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

    # Extra fields for role-based assignments
    hizb = models.CharField(max_length=50, null=True, blank=True)   # For Prefect/Deputy/Muaddib
    room = models.CharField(max_length=50, null=True, blank=True)   # For Lajnat Member allocation

    # Account management flags
    is_verified = models.BooleanField(default=False)  # Admin can mark user as verified
    is_active = models.BooleanField(default=True)     # Standard Django field, but explicitly kept

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
