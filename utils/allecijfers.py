
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from config import (
    HEADERS,
    REQUEST_TIMEOUT,
    IGNORE_SCHOOLS,
    ALLECIJFERS_SUFFIX
)


ALLECIJFERS_BASE_URL = (
    "https://allecijfers.nl/middelbare-school/"
)

FAILURE_PLACEHOLDER = "nan/"


def extract_slug_from_portal_url(portal_url):
    """
    Extract the school slug from a Schoolkeuze020 portal URL.
    """

    if not portal_url:
        return None

    path_parts = urlparse(portal_url).path.strip("/").split("/")

    try:
        index = path_parts.index("scholen")
        return path_parts[index + 1]
    except (ValueError, IndexError):
        return None


def generate_candidates(data_name, portal_url):
    """
    Generate possible AlleCijfers URL variations in priority order.
    """

    portal_slug = extract_slug_from_portal_url(portal_url)

    slugs = [
        data_name,
        f"het-{data_name}" if data_name else None,
        portal_slug,
        f"het-{portal_slug}" if portal_slug else None
    ]

    # Remove empty and duplicate candidates while preserving order
    unique_slugs = list(dict.fromkeys(
        slug for slug in slugs if slug
    ))

    return [
        urljoin(ALLECIJFERS_BASE_URL, f"{slug}/")
        for slug in unique_slugs
    ]


def is_valid_page(response):
    """
    Check whether the response looks like a valid school page.
    """

    if response.status_code != 200:
        return False

    final_path = urlparse(response.url).path

    if not final_path.startswith("/middelbare-school/"):
        return False

    soup = BeautifulSoup(response.text, "html.parser")

    title = (
        soup.title.get_text(" ", strip=True)
        if soup.title else ""
    )

    h1 = soup.find("h1")

    heading = (
        h1.get_text(" ", strip=True)
        if h1 else ""
    )

    page_heading = f"{title} {heading}".lower()

    error_phrases = [
        "404",
        "niet gevonden",
        "pagina bestaat niet",
        "page not found",
        "pagina niet beschikbaar"
    ]

    if any(phrase in page_heading for phrase in error_phrases):
        return False

    if not title and not heading:
        return False

    return True


def resolve_allecijfers_url(school, session):
    """
    Resolve an AlleCijfers URL using manual mappings or automatic search.
    """

    school_name = school.get("name")

    # Skip schools explicitly excluded from AlleCijfers matching
    if school_name in IGNORE_SCHOOLS:
        return FAILURE_PLACEHOLDER

    # Check manually configured URL mappings first
    if school_name in ALLECIJFERS_SUFFIX:

        suffix = ALLECIJFERS_SUFFIX[school_name]

        return urljoin(
            ALLECIJFERS_BASE_URL,
            suffix
        )

    # Generate automatic URL candidates
    candidates = generate_candidates(
        school.get("data_name"),
        school.get("portal_url")
    )

    # Try each candidate until a valid page is found
    for url in candidates:

        try:
            response = session.get(
                url,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True
            )

            if is_valid_page(response):
                return response.url

        except requests.RequestException:
            continue

    return FAILURE_PLACEHOLDER


def resolve_all_schools(schools):
    """
    Resolve AlleCijfers URLs for all schools.

    Returns failed and ignored schools separately.
    """

    failed_schools = []
    ignored_schools = []

    with requests.Session() as session:

        session.headers.update(HEADERS)

        for school in schools:

            school_name = school.get("name")

            # Handle explicitly ignored schools
            if school_name in IGNORE_SCHOOLS:

                school["allecijfers_url"] = FAILURE_PLACEHOLDER

                ignored_schools.append({
                    "name": school_name,
                    "data_name": school.get("data_name")
                })

                continue

            # Resolve the URL using manual mapping or automatic search
            resolved_url = resolve_allecijfers_url(
                school,
                session
            )

            school["allecijfers_url"] = resolved_url

            if resolved_url == FAILURE_PLACEHOLDER:

                failed_schools.append({
                    "data_name": school.get("data_name"),
                    "name": school_name,
                    "portal_url": school.get("portal_url"),
                    "candidates": generate_candidates(
                        school.get("data_name"),
                        school.get("portal_url")
                    )
                })

    return failed_schools, ignored_schools
