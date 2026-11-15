import json
import hashlib
import re
import time

from datetime import datetime, date, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


BASE_DIR = Path(__file__).resolve().parent

SCOPES = [
    "https://www.googleapis.com/auth/calendar.events"
]

TARGET_TYPES = {"havo", "vwo"}

MONTHS_NL = {
    "januari": 1,
    "februari": 2,
    "maart": 3,
    "april": 4,
    "mei": 5,
    "juni": 6,
    "juli": 7,
    "augustus": 8,
    "september": 9,
    "oktober": 10,
    "november": 11,
    "december": 12,
}


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def authenticate():
    """Authenticate using Google OAuth 2.0."""

    credentials_path = BASE_DIR / "credentials.json"
    token_path = BASE_DIR / "token.json"

    creds = None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(
            str(token_path), SCOPES
        )

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(credentials_path), SCOPES
        )

        creds = flow.run_local_server(port=0)

        with open(token_path, "w", encoding="utf-8") as file:
            file.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def parse_date(date_string):
    """Parse dates in Dutch format, e.g. 25 november 2026."""

    parts = date_string.strip().lower().split()

    if len(parts) != 3:
        raise ValueError(f"Invalid date: {date_string}")

    day = int(parts[0])
    month = MONTHS_NL[parts[1]]
    year = int(parts[2])

    return date(year, month, day)


def get_time_range(details):
    """Extract a time range from school details."""

    for detail in details:
        match = re.search(
            r"(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})",
            detail
        )

        if match:
            return match.group(1), match.group(2)

    return None, None


def filter_school_types(school):
    """Keep only schools offering HAVO and/or VWO."""

    school_types = set(school.get("school_types", []))

    return sorted(school_types & TARGET_TYPES)


def build_event(school, timezone):
    """Convert a school record into a Google Calendar event."""

    event_date = parse_date(school["open_day_date"])

    matched_types = filter_school_types(school)

    if not matched_types:
        return None

    details = school.get("details", [])

    start_time, end_time = get_time_range(details)

    summary = (
        f"[{', '.join(t.upper() for t in matched_types)}] "
        f"{school['name']} — Open Day"
    )

    description_parts = [
        f"School: {school['name']}",
        f"School types: {', '.join(t.upper() for t in matched_types)}",
        f"District: {school.get('stadsdeel', '')}",
        "",
        "Details:",
    ]

    description_parts.extend(details)

    description_parts.extend([
        "",
        f"School portal: {school.get('portal_url', '')}",
        f"School website: {school.get('school_website', '')}",
        f"Google Maps: {school.get('google_maps_url', '')}",
        f"AlleCijfers: {school.get('allecijfers_url', '')}",
    ])

    event = {
        "summary": summary,
        "description": "\n".join(description_parts),
        "extendedProperties": {
            "private": {
                "source_id": school["data_name"]
            }
        }
    }

    # Use the first detail as the school address, if available.
    if details:
        event["location"] = details[0]

    # Create a timed event when a time range is available.
    if start_time and end_time:
        start_datetime = datetime.strptime(
            f"{event_date} {start_time}",
            "%Y-%m-%d %H:%M"
        )

        end_datetime = datetime.strptime(
            f"{event_date} {end_time}",
            "%Y-%m-%d %H:%M"
        )

        event["start"] = {
            "dateTime": start_datetime.isoformat(),
            "timeZone": timezone
        }

        event["end"] = {
            "dateTime": end_datetime.isoformat(),
            "timeZone": timezone
        }

    else:
        # Use an all-day event when no time is provided.
        event["start"] = {
            "date": event_date.isoformat()
        }

        event["end"] = {
            "date": (event_date + timedelta(days=1)).isoformat()
        }

    # Generate a stable event ID to prevent duplicates on reruns.
    unique_key = f"{school['data_name']}-{event_date.isoformat()}"

    event["id"] = hashlib.sha256(
        unique_key.encode("utf-8")
    ).hexdigest()

    return event


def import_schools():
    """Import eligible school events into Google Calendar."""

    config = load_json(BASE_DIR / "import_config.json")

    calendar_id = config["calendar_id"]
    timezone = config.get("timezone", "Europe/Amsterdam")

    # Validate the configured timezone.
    ZoneInfo(timezone)

    schools = load_json(BASE_DIR / config["input_file"])

    service = authenticate()

    added = 0
    skipped = 0
    errors = 0

    for school in schools:
        matched_types = filter_school_types(school)

        if not matched_types:
            skipped += 1
            continue

        try:
            event = build_event(school, timezone)

            service.events().insert(
                calendarId=calendar_id,
                body=event
            ).execute()

            added += 1

            print(f"Added: {school['name']}")

            time.sleep(1)

        except HttpError as error:
            if error.resp.status == 409:
                print(f"Already exists: {school['name']}")
                skipped += 1
                time.sleep(1)
            else:
                print(f"Google API error: {school['name']}: {error}")
                errors += 1
                time.sleep(1)

        except Exception as error:
            print(f"Error: {school.get('name', 'Unknown')}: {error}")
            errors += 1
            time.sleep(1)

    print("\nImport completed!")
    print(f"Added: {added}")
    print(f"Skipped: {skipped}")
    print(f"Errors: {errors}")


if __name__ == "__main__":
    import_schools()