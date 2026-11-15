from urllib.parse import quote_plus, urljoin

from config import BASE_URL


ALLECIJFERS_BASE_URL = (
    "https://allecijfers.nl/middelbare-school/"
)


def get_portal_url(relative_url):
    """
    Convert a relative Schoolkeuze020 URL into an absolute URL.
    """

    if not relative_url:
        return None

    return urljoin(BASE_URL, relative_url)


def get_google_maps_url(school_name):
    """
    Generate a Google Maps search URL for a school.
    """

    if not school_name:
        return None

    query = quote_plus(
        f"{school_name}, Amsterdam, Netherlands"
    )

    return (
        "https://www.google.com/maps/search/"
        f"?api=1&query={query}"
    )


def get_allecijfers_url(data_name):
    """
    Generate an AlleCijfers URL using the original data-name.
    """

    if not data_name:
        return None

    return urljoin(
        ALLECIJFERS_BASE_URL,
        f"{data_name}/"
    )
