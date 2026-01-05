# from datetime import datetime
# import logging

# logger = logging.getLogger(__name__)

# def safe_strip(value):
#     """Safely strip strings, return empty string if None or not a str."""
#     return value.strip() if isinstance(value, str) else ""

# def normalize_student_attendance(raw_row: dict, attendance_type: str) -> dict:
#     status_map = {
#         "p": "present",
#         "a": "absent",
#         "l": "late",
#         "e": "excused",
#         "": "absent",
#         None: "absent",
#     }

#     type_map = {
#         "Fajr_Namaz_Talabat": "fajr",
#         "Maghrib_Isha_Talabat": "maghrib_isha",
#         "Dua_Talabat": "dua",
#     }

#     # Map the correct raw keys based on type
#     if attendance_type == "Fajr_Namaz_Talabat":
#         raw_status = safe_strip(raw_row.get("Fajar_Namaz")).lower()
#         remarks = raw_row.get("Fajar_Namaz_Remarks")
#         tp = raw_row.get("Fajar_Namaz_TP")
#     elif attendance_type == "Maghrib_Isha_Talabat":
#         raw_status = safe_strip(raw_row.get("Maghrib_Isha")).lower()
#         remarks = raw_row.get("Maghrib_Isha_Remarks")
#         tp = raw_row.get("Maghrib_Isha_TP")
#     elif attendance_type == "Dua_Talabat":
#         raw_status = safe_strip(raw_row.get("Dua")).lower()
#         remarks = raw_row.get("Dua_Remarks")
#         tp = raw_row.get("Dua_TP")
#     else:
#         raw_status, remarks, tp = "", "", None

#     status = status_map.get(raw_status, "absent")

#     normalized = {
#         "trno": raw_row.get("Trno"),                       # student identifier from main API
#         "bed_name": safe_strip(raw_row.get("BedName")),
#         "room": safe_strip(raw_row.get("RoomNo")),
#         "pantry": safe_strip(raw_row.get("Pantry")),
#         "location": safe_strip(raw_row.get("Location")),
#         "darajah": safe_strip(raw_row.get("Darajah")),
#         "hizb": safe_strip(raw_row.get("Hizb")),
#         "date": tp,                                        # keep TP as timestamp string for now
#         "attendance_type": type_map.get(attendance_type, attendance_type.lower()),
#         "status": status,
#         "remarks": safe_strip(remarks),
#     }

#     logger.debug("Normalized row: %s", normalized)
#     return normalized


# attendance/utils.py
import requests
import logging

BASE_URL = "https://nairobi.jameasaifiyah.edu/JameaWebService/api/nairobi"
logger = logging.getLogger(__name__)

# ---------------------------
# Fetch Helpers
# ---------------------------
def fetch_attendance(endpoint: str = "Fajr_Namaz_Talabat", frm: str = None, to: str = None, token: str = None):
    """
    Fetch attendance data from Jamea API.
    Args:
        endpoint (str): API endpoint key. Defaults to 'Fajr_Namaz_Talabat'.
        frm (str): Start date (YYYY-MM-DD).
        to (str): End date (YYYY-MM-DD).
        token (str): API token for authentication.
    Returns:
        list[dict]: Parsed JSON response or empty list if error.
    """
    if not frm or not to or not token:
        raise ValueError("frm, to, and token are required")

    url = f"{BASE_URL}/{endpoint}?token={token}&frm={frm}&to={to}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "results" in data:
            return data["results"]
        else:
            logger.warning(f"Unexpected response format from {url}: {data}")
            return []
    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching attendance from {url}")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error fetching attendance: {e}")
        return []
    except ValueError:
        logger.error(f"Invalid JSON response from {url}")
        return []

def fetch_and_normalize(endpoint: str, frm: str, to: str, token: str, normalizer_fn):
    """
    Fetch attendance and normalize using provided function.
    Args:
        endpoint (str): API endpoint key.
        frm (str): Start date.
        to (str): End date.
        token (str): API token.
        normalizer_fn (callable): Function to normalize each row.
    Returns:
        list[dict]: Normalized attendance records.
    """
    raw_data = fetch_attendance(endpoint, frm, to, token)
    return [normalizer_fn(row, endpoint) for row in raw_data]

# ---------------------------
# Normalizer
# ---------------------------
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
        "trno": raw_row.get("Trno"),
        "bed_name": safe_strip(raw_row.get("BedName")),
        "room": safe_strip(raw_row.get("RoomNo")),
        "pantry": safe_strip(raw_row.get("Pantry")),
        "location": safe_strip(raw_row.get("Location")),
        "darajah": safe_strip(raw_row.get("Darajah")),
        "hizb": safe_strip(raw_row.get("Hizb")),
        "date": None,  # placeholder until daily date endpoint is available
        "tp": tp,      # store prayer time here
        "attendance_type": type_map.get(attendance_type, attendance_type.lower()),
        "status": status,
        "remarks": safe_strip(remarks),
    }

    logger.debug("Normalized row: %s", normalized)
    return normalized
