from django.core.management.base import BaseCommand
from attendance.models import Darajah, Hizb, HizbGroup

# Your extracted values
DARAJAH_VALUES = [
    "1 A M", "1 B M", "1 C M",
    "10 A M", "11 A M",
    "2 A M", "2 B M", "2 C M",
    "3 A M", "3 B M", "3 C M",
    "4 A M", "4 B M", "4 C M",
    "5 A M", "5 B M",
    "6 A M", "6 B M",
    "7 A M", "7 B M",
    "8 A M", "8 B M",
    "9 A M",
]

HIZB_VALUES = [
    "Almās", "Aqīq", "Billawr", "Fayrūzaj",
    "Lulua", "Marjān", "Yāqūt", "Zumurrud",
]


class Command(BaseCommand):
    help = "Seed Darajah, Hizb, and HizbGroup tables with extracted values"

    def handle(self, *args, **options):
        # Save Darajah
        for d in DARAJAH_VALUES:
            obj, created = Darajah.objects.get_or_create(name=d)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created Darajah: {d}"))

        # Save Hizb and Groups
        for h in HIZB_VALUES:
            hizb_obj, created = Hizb.objects.get_or_create(number=h)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created Hizb: {h}"))

            # Create 4 groups per hizb
            for g in range(1, 5):
                HizbGroup.objects.get_or_create(hizb=hizb_obj, group_number=g)
                self.stdout.write(self.style.SUCCESS(f"Ensured {h} - Group {g} exists"))
