from django.core.management.base import BaseCommand
from attendance.utils.normalizers import (
    fetch_and_normalize,
    normalize_student_attendance,
)
from attendance.models import AttendanceRecord, Student, Darajah, Hizb
from datetime import date, timedelta


class Command(BaseCommand):
    help = "Sync attendance data from Jamea API into Supabase (rolling 30 days)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--endpoint",
            type=str,
            choices=["Fajr_Namaz_Talabat", "Maghrib_Isha_Talabat", "Dua_Talabat"],
            default="Fajr_Namaz_Talabat",
            help="Which prayer attendance to sync (default: Fajr_Namaz_Talabat)",
        )

    def handle(self, *args, **options):
        today = date.today()
        frm = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        to = today.strftime("%Y-%m-%d")
        token = "c701a5a2-f53f-4ca3-86e4-2a85657066bc"

        endpoint = options["endpoint"]
        self.stdout.write(f"Fetching {endpoint}...")

        try:
            records = fetch_and_normalize(endpoint, frm, to, token, normalize_student_attendance)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to fetch {endpoint}: {e}"))
            return

        self.stdout.write(f"Fetched {len(records)} records from {endpoint}")

        students_created = 0
        students_updated = 0
        records_created = 0
        records_updated = 0

        for rec in records:
            self.stdout.write(
                f"Processing student {rec['trno']} with status {rec['status']} and tp {rec['tp']}"
            )

            # Look up related objects safely
            darajah_obj = None
            hizb_obj = None

            if rec.get("darajah"):
                darajah_obj = Darajah.objects.filter(name=rec["darajah"]).first()
            if rec.get("hizb"):
                hizb_obj = Hizb.objects.filter(name=rec["hizb"]).first()

            # Create or update Student
            student, created = Student.objects.update_or_create(
                trno=rec["trno"],
                defaults={
                    "room": rec.get("room"),
                    "pantry": rec.get("pantry"),
                    "location": rec.get("location"),
                    "darajah": darajah_obj,   # assign FK instance
                    "hizb": hizb_obj,         # assign FK instance
                    "bed_name": rec.get("bed_name"),
                }
            )
            if created:
                students_created += 1
                self.stdout.write(f"  → New student created: {student.trno}")
            else:
                students_updated += 1
                self.stdout.write(f"  → Student updated: {student.trno}")

            # Create or update AttendanceRecord
            record, created = AttendanceRecord.objects.update_or_create(
                student=student,
                date=rec.get("date"),
                attendance_type=rec["attendance_type"],
                tp=rec.get("tp"),
                defaults={
                    "status": rec["status"],
                    "remarks": rec.get("remarks"),
                }
            )

            if created:
                records_created += 1
                self.stdout.write(
                    f"  → Created attendance record for {student.trno} ({rec['attendance_type']})"
                )
            else:
                records_updated += 1
                self.stdout.write(
                    f"  → Updated attendance record for {student.trno} ({rec['attendance_type']})"
                )

        # Cleanup old records
        cutoff = today - timedelta(days=30)
        deleted, _ = AttendanceRecord.objects.filter(date__lt=cutoff).delete()

        # Summary
        self.stdout.write(self.style.SUCCESS(
            f"Sync complete: {students_created} students created, {students_updated} updated, "
            f"{records_created} records created, {records_updated} updated, "
            f"{deleted} old records deleted."
        ))
