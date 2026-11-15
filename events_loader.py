
import json
import os

from scraper.connection import fetch_open_days
from scraper.parser import parse_schools

from utils.allecijfers import resolve_all_schools

from config import OUTPUT_FILE


def save_schools(schools):
    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            schools,
            file,
            ensure_ascii=False,
            indent=4
        )


def print_failed_schools(failed_schools):
    if not failed_schools:
        print("\nAll schools matched successfully!")
        return

    print("\n" + "=" * 60)
    print("SCHOOLS NOT FOUND ON ALLECIJFERS")
    print("=" * 60)

    for school in failed_schools:

        print(f"\nName: {school['name']}")
        print(f"Data name: {school['data_name']}")
        print(f"Portal URL: {school['portal_url']}")

        print("Tried URLs:")

        for url in school["candidates"]:
            print(f"  - {url}")

    print("\n" + "=" * 60)
    print(f"Total unresolved schools: {len(failed_schools)}")
    print("=" * 60)


def main():

    print("Fetching Schoolkeuze020 open days page...")

    html = fetch_open_days()

    print("Parsing schools...")

    schools = parse_schools(html)

    print(f"Found {len(schools)} schools.")

    print("\nResolving AlleCijfers URLs...")

    failed_schools, ignored_schools = resolve_all_schools(schools)

    matched_count = (
            len(schools)
            - len(failed_schools)
            - len(ignored_schools)
    )

    print(f"Successfully matched: {matched_count}")
    print(f"Could not match: {len(failed_schools)}")
    print(f"Ignored: {len(ignored_schools)}")

    print_failed_schools(failed_schools)

    # Save all schools, including unresolved ones
    save_schools(schools)

    print(f"\nResults saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
