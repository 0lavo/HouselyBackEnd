import subprocess
import json
import csv

from config import URL_Base


def _build_form_data(params: dict) -> str:
    """Serialize a dict to URL-encoded form data, converting Python bools to lowercase strings."""
    parts = []
    for k, v in params.items():
        if isinstance(v, bool):
            parts.append(f"{k}={'true' if v else 'false'}")
        else:
            parts.append(f"{k}={v}")
    return "&".join(parts)


def search_properties(
    token: str,
    operation: str = "rent",
    property_type: str = "homes",
    location_id: str = "0-EU-PT-13",
    max_items: int = 50,
    page: int = 1,
    order: str = "publicationDate",
    sort: str = "desc",
    filters: dict = None,
) -> dict:
    params = {
        "operation": operation,
        "propertyType": property_type,
        "locationId": location_id,
        "maxItems": max_items,
        "numPage": page,
        "order": order,
        "sort": sort,
        "locale": "pt",  # forces summary/description fields to return in Portuguese
    }
    if filters:
        params.update(filters)

    try:
        result = subprocess.run(
            [
                "curl", "-s",
                "-X", "POST",
                "-H", f"Authorization: Bearer {token}",
                "-H", "Content-Type: application/x-www-form-urlencoded",
                "-d", _build_form_data(params),
                f"{URL_Base}/3.5/pt/search",
            ],
            capture_output=True, text=True, encoding="utf-8"
        )

        return json.loads(result.stdout)

    except Exception as e:
        print(e)
        return {}


def fetch_bulk_properties(
    token: str,
    operation: str = "rent",
    property_type: str = "homes",
    location_id: str = "0-EU-PT-13",
    max_count: int = 200,
    filters: dict = None,
) -> list:
    """Paginate through Idealista API results and return up to max_count properties."""
    all_properties = []
    page = 1
    items_per_page = 50  # Idealista API hard cap per page

    while len(all_properties) < max_count:
        data = search_properties(
            token=token,
            operation=operation,
            property_type=property_type,
            location_id=location_id,
            max_items=items_per_page,
            page=page,
            filters=filters,
        )

        items = data.get("elementList", [])
        if not items:
            break

        all_properties.extend(items)

        total_pages = data.get("totalPages", 1)
        if page >= total_pages:
            break

        page += 1

    return all_properties[:max_count]


def export_to_json(properties: list, filepath: str) -> str:
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(properties, f, ensure_ascii=False, indent=2)
    return filepath


def export_to_csv(properties: list, filepath: str) -> str:
    if not properties:
        return filepath
    fieldnames = list(properties[0].keys())
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(properties)
    return filepath
