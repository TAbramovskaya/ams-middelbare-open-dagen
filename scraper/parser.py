import re
from bs4 import BeautifulSoup
from config import SCHOOL_TYPES, STADSDEEL_FILTERS
from utils.urls import get_portal_url, get_google_maps_url


def parse_schools(html):
    soup = BeautifulSoup(html, "html.parser")

    schools = []
    school_items = soup.select("div.scholen-item")

    for item in school_items:
        classes = item.get("class", [])

        school_types = []
        stadsdeel = None

        for cls in classes:
            match = re.match(r"cat-[a-z]-(.+)", cls)  # cat-b-vmbo-basis | cat-f-havo | cat-g-vwo ...

            if not match:
                continue

            filter_name = match.group(1)

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
        title_element = item.select_one("h3 a")
        school_name = (title_element.get_text(" ", strip=True) if title_element else None)
        relative_portal_url = (title_element.get("href") if title_element else None)

        portal_url = get_portal_url(relative_portal_url)

        website_element = item.select_one(".scholen-button a[href]")
        school_website = (website_element.get("href") if website_element else None)

        date_element = item.select_one(".scholen-date")
        open_day_date = (date_element.get_text(" ", strip=True) if date_element else None)

        # Extract all additional event details
        details = []

        for li in item.select(".scholen-details li"):
            text_element = li.select_one( ".school-detail p")

            text = text_element.get_text(" ", strip=True)
            if text_element:
                details.append(text)

        # Generate external search links
        google_maps_url = get_google_maps_url(school_name)

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