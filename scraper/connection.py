import requests
from config import OPEN_DAYS_URL, HEADERS, REQUEST_TIMEOUT


def fetch_open_days():
    """
    Fetch the open days page and return its HTML content.
    """

    response = requests.get(
        OPEN_DAYS_URL,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT
    )

    # Raise an exception if the HTTP request failed
    response.raise_for_status()

    # Detect the correct page encoding
    response.encoding = response.apparent_encoding

    return response.text