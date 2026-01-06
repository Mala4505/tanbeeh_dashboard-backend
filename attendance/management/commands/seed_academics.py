from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from attendance.models import Darajah, Hizb, HizbGroup

User = get_user_model()

class Command(BaseCommand):
    help = "Create one test user for each role using its_number + password and assign role-specific scope"

    def handle(self, *args, **options):
        # ITS numbers + clean passwords for each role
        test_users = [
            {"its_number": "9001", "password": "admin", "role": "admin"},
            {"its_number": "9002", "password": "prefect", "role": "prefect"},
            {"its_number": "9003", "password": "deputy", "role": "deputy_prefect"},
            {"its_number": "9004", "password": "masool", "role": "masool"},
            {"its_number": "9005", "password": "muaddib", "role": "muaddib"},
            {"its_number": "9006", "password": "lajnat", "role": "lajnat_member"},
        ]

        for u in test_users:
            user, created = User.objects.get_or_create(
                its_number=u["its_number"],
                defaults={
                    "username": u["its_number"],  # avoid IntegrityError
                    "role": u["role"],
                }
            )
            if created:
                user.set_password(u["password"])
                user.save()
                self.stdout.write(self.style.SUCCESS(
                    f"Created {u['role']} test user with ITS {u['its_number']}"
                ))
            else:
                self.stdout.write(f"{u['role']} user already exists (ITS {u['its_number']})")

        # Assign role-specific scopes (using strings, since fields are CharFields)
        darajah = Darajah.objects.first()
        hizb = Hizb.objects.first()
        hizb_group = HizbGroup.objects.filter(hizb=hizb).first()

        # Prefect & Deputy → Hizb (store hizb.name string)
        for role in ["prefect", "deputy_prefect"]:
            user = User.objects.filter(role=role).first()
            if user and hizb:
                user.hizb = hizb.name
                user.save()
                self.stdout.write(self.style.SUCCESS(
                    f"Assigned {role} ITS {user.its_number} → Hizb {hizb.name}"
                ))

        # Masool → Darajah (store darajah.name string)
        masool_user = User.objects.filter(role="masool").first()
        if masool_user and darajah:
            masool_user.darajah = darajah.name
            masool_user.save()
            self.stdout.write(self.style.SUCCESS(
                f"Assigned Masool ITS {masool_user.its_number} → Darajah {darajah.name}"
            ))

        # Muaddib → HizbGroup (store group_number as string)
        muaddib_user = User.objects.filter(role="muaddib").first()
        if muaddib_user and hizb_group:
            muaddib_user.hizb_group = str(hizb_group.group_number)
            muaddib_user.save()
            self.stdout.write(self.style.SUCCESS(
                f"Assigned Muaddib ITS {muaddib_user.its_number} → HizbGroup {hizb_group.hizb.name} - Group {hizb_group.group_number}"
            ))
