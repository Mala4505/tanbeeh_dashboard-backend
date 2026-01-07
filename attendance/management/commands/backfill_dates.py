from django.core.management.base import BaseCommand
from django.utils import timezone
from attendance.models import AttendanceRecord
from django.db import IntegrityError

class Command(BaseCommand):
    help = "Backfill synthetic dates into AttendanceRecord rows where date is NULL"

    def add_arguments(self, parser):
        parser.add_argument(
            "--spread",
            action="store_true",
            help="Spread synthetic dates across the last 30 days instead of using today"
        )

    def handle(self, *args, **options):
        qs = AttendanceRecord.objects.filter(date__isnull=True)
        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS("No records with NULL date found."))
            return

        today = timezone.now().date()
        updated = 0
        skipped = 0

        self.stdout.write(f"Processing {total} records...")

        for i, rec in enumerate(qs.iterator()):
            synthetic_date = today - timezone.timedelta(days=(i % 30)) if options["spread"] else today
            rec.date = synthetic_date

            try:
                rec.save(update_fields=["date"])
                updated += 1
            except IntegrityError:
                skipped += 1
                # Just skip duplicates, no rollback needed

            if (i + 1) % 100 == 0 or (i + 1) == total:
                self.stdout.write(
                    f"Processed {i+1}/{total} records... Updated={updated}, Skipped={skipped}"
                )

        self.stdout.write(self.style.SUCCESS(
            f"Finished! Updated {updated} records, skipped {skipped} duplicates."
        ))
