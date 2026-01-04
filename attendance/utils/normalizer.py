from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def safe_strip(value):
    """Safely strip strings, return empty string if None or not a str."""
    return value.strip() if isinstance(value, str) else ""

def normalize_student_attendance(raw_row: dict, attendance_type: str) -> dict:
    status_map = {
        "p": "present",
        "a": "absent",
        "l": "late",
        "e": "excused",
        "": "absent",
        None: "absent",
    }

    type_map = {
        "Fajr_Namaz_Talabat": "fajr",
        "Maghrib_Isha_Talabat": "maghrib_isha",
        "Dua_Talabat": "dua",
    }

    # Map the correct raw keys based on type
    if attendance_type == "Fajr_Namaz_Talabat":
        raw_status = safe_strip(raw_row.get("Fajar_Namaz")).lower()
        remarks = raw_row.get("Fajar_Namaz_Remarks")
        tp = raw_row.get("Fajar_Namaz_TP")
    elif attendance_type == "Maghrib_Isha_Talabat":
        raw_status = safe_strip(raw_row.get("Maghrib_Isha")).lower()
        remarks = raw_row.get("Maghrib_Isha_Remarks")
        tp = raw_row.get("Maghrib_Isha_TP")
    elif attendance_type == "Dua_Talabat":
        raw_status = safe_strip(raw_row.get("Dua")).lower()
        remarks = raw_row.get("Dua_Remarks")
        tp = raw_row.get("Dua_TP")
    else:
        raw_status, remarks, tp = "", "", None

    status = status_map.get(raw_status, "absent")

    normalized = {
        "trno": raw_row.get("Trno"),                       # student identifier from main API
        "bed_name": safe_strip(raw_row.get("BedName")),
        "room": safe_strip(raw_row.get("RoomNo")),
        "pantry": safe_strip(raw_row.get("Pantry")),
        "location": safe_strip(raw_row.get("Location")),
        "darajah": safe_strip(raw_row.get("Darajah")),
        "hizb": safe_strip(raw_row.get("Hizb")),
        "date": tp,                                        # keep TP as timestamp string for now
        "attendance_type": type_map.get(attendance_type, attendance_type.lower()),
        "status": status,
        "remarks": safe_strip(remarks),
    }

    logger.debug("Normalized row: %s", normalized)
    return normalized

