import os
import sys
import django
from django.db.models import Count

# --- Configure Django environment ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")  # <-- match your manage.py
django.setup()

from attendance.models import AttendanceRecord

def clean_duplicates():
    print("Scanning for duplicate AttendanceRecords...")

    duplicates = (
        AttendanceRecord.objects
        .values("student", "date", "attendance_type")
        .annotate(count=Count("id"))
        .filter(count__gt=1)
    )

    total_deleted = 0

    for dup in duplicates:
        records = AttendanceRecord.objects.filter(
            student=dup["student"],
            date=dup["date"],
            attendance_type=dup["attendance_type"]
        ).order_by("id")

        # Keep the first record, delete the rest by ID
        ids_to_delete = list(records.values_list("id", flat=True))[1:]
        if ids_to_delete:
            deleted_count, _ = AttendanceRecord.objects.filter(id__in=ids_to_delete).delete()
            total_deleted += deleted_count
            print(f"Cleaned {deleted_count} duplicate(s) for student={dup['student']} date={dup['date']} type={dup['attendance_type']}")

    print(f"✅ Cleanup complete. Total duplicates removed: {total_deleted}")

if __name__ == "__main__":
    clean_duplicates()
