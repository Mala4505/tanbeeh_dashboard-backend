from datetime import timedelta
from django.utils.timezone import now
from attendance.models import AttendanceRecord
import logging

logger = logging.getLogger(__name__)


def purge_expired_temp_records(days: int = 7):
    """
    Delete temporary attendance records older than `days`.
    These are records marked with is_temp=True, fetched outside rolling 30 days.
    """
    cutoff_date = now().date() - timedelta(days=days)
    expired_records = AttendanceRecord.objects.filter(is_temp=True, date__lt=cutoff_date)

    count = expired_records.count()
    if count > 0:
        logger.info(f"Purging {count} expired temporary attendance records (older than {days} days).")
        expired_records.delete()
    else:
        logger.info("No expired temporary attendance records found.")

    return count
