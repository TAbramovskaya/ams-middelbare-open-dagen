import re
from bs4 import BeautifulSoup
from config import SCHOOL_TYPES, STADSDEEL_FILTERS
from utils.urls import get_portal_url, get_google_maps_url


def parse_schools(html):
    """
    Parse all school items from the Schoolkeuze020 HTML page.

    Returns a list of dictionaries containing school information.
    """

    soup = BeautifulSoup(html, "html.parser")

    schools = []

    # Find all school containers
    school_items = soup.select("div.scholen-item")

    for item in school_items:

        classes = item.get("class", [])

        # Extract school types and district from CSS classes
        school_types = []
        stadsdeel = None

        for cls in classes:

            match = re.match(r"cat-[a-z]-(.+)", cls)

            if not match:
                continue

            filter_name = match.group(1)

            # Identify school types
            if filter_name in SCHOOL_TYPES:
                school_types.append(
                    SCHOOL_TYPES[filter_name]
                )

            # Identify Amsterdam districts
            if filter_name in STADSDEEL_FILTERS:
                stadsdeel = STADSDEEL_FILTERS[filter_name]

        # Extract the original school identifier
        data_name = item.get("data-name")

        # Extract school name and portal link
        title_link = item.select_one("h3 a")

        school_name = (
            title_link.get_text(" ", strip=True)
            if title_link else None
        )

        relative_portal_url = (
            title_link.get("href")
            if title_link else None
        )

        portal_url = get_portal_url(
            relative_portal_url
        )

        # Extract the school's external website
        website_link = item.select_one(
            ".scholen-button a[href]"
        )

        school_website = (
            website_link.get("href")
            if website_link else None
        )

        # Extract open day date
        date_element = item.select_one(
            ".scholen-date"
        )

        open_day_date = (
            date_element.get_text(" ", strip=True)
            if date_element else None
        )

        # Extract all additional event details
        details = []

        for li in item.select(".scholen-details li"):

            text_element = li.select_one(
                ".school-detail p"
            )

            if text_element:

                # Preserve readable text while removing HTML tags
                text = text_element.get_text(
                    " ",
                    strip=True
                )

                details.append(text)

        # Generate external search links
        google_maps_url = get_google_maps_url(
            school_name
        )


        # Build the final school dictionary
        school = {
            "data_name": data_name,
            "name": school_name,
            "school_types": school_types,
            "stadsdeel": stadsdeel,
            "portal_url": portal_url,
            "school_website": school_website,
            "google_maps_url": google_maps_url,
            "allecijfers_url": None,
            "open_day_date": open_day_date,
            "details": details
        }

        schools.append(school)

    return schools