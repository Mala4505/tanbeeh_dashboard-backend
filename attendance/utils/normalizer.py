from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def normalize_student_attendance(raw_row: dict, attendance_type: str) -> dict:
    """
    Normalize a raw attendance row from Jamea API into a consistent dict.
    Args:
        raw_row (dict): Raw API row.
        attendance_type (str): Key for attendance type (e.g., 'Fajr_Namaz_Talabat').
    Returns:
        dict: Normalized student attendance record.
    """

    status_map = {
        "present": "present",
        "absent": "absent",
        "late": "late",
        "excused": "excused",
        "": "absent",
        None: "absent",
    }

    type_map = {
        "Fajr_Namaz_Talabat": "fajr",
        "Maghrib_Isha_Talabat": "maghrib_isha",
        "Dua_Talabat": "dua",
    }

    # Normalize status (case-insensitive, strip spaces)
    raw_status = str(raw_row.get(attendance_type, "")).strip().lower()
    status = status_map.get(raw_status, "absent")

    # Normalize date
    raw_date = raw_row.get("Date")
    try:
        date_val = datetime.strptime(raw_date, "%Y-%m-%d").date().isoformat() if raw_date else None
    except Exception:
        logger.warning(f"Unexpected date format: {raw_date}")
        date_val = raw_date  # fallback to raw

    return {
        "id": raw_row.get("TRNO"),
        "bed_name": raw_row.get("BedName", "").strip(),
        "room": raw_row.get("RoomNo", "").strip(),
        "pantry": raw_row.get("Pantry", "").strip(),
        "location": raw_row.get("Location", "").strip(),
        "darajah": raw_row.get("Darajah", "").strip(),
        "hizb": raw_row.get("Hizb", "").strip(),
        "date": date_val,
        "attendance_type": type_map.get(attendance_type, attendance_type.lower()),
        "status": status,
        "remarks": raw_row.get("Remarks", "").strip(),
    }
