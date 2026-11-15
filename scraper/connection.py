import requests
from config import OPEN_DAYS_URL, HEADERS, REQUEST_TIMEOUT


def fetch_open_days():
    response = requests.get(
        OPEN_DAYS_URL,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT
    )

    response.raise_for_status()
    response.encoding = response.apparent_encoding

    return response.text