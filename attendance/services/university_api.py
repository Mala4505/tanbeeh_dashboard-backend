import requests
import logging

BASE_URL = "https://nairobi.jameasaifiyah.edu/JameaWebService/api/nairobi"

logger = logging.getLogger(__name__)


def fetch_attendance(endpoint: str, frm: str, to: str, token: str):
    """
    Fetch attendance data from Jamea API.
    Args:
        endpoint (str): API endpoint key (e.g., 'Fajr_Namaz_Talabat').
        frm (str): Start date (YYYY-MM-DD).
        to (str): End date (YYYY-MM-DD).
        token (str): API token for authentication.

    Returns:
        list[dict]: Parsed JSON response or empty list if error.
    """
    url = f"{BASE_URL}/{endpoint}?token={token}&frm={frm}&to={to}"
    try:
        response = requests.get(url, timeout=10)  # timeout prevents hanging
        response.raise_for_status()
        data = response.json()

        # Ensure response is a list
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
