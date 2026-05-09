import sys
sys.stdout.reconfigure(encoding="utf-8")

import os
import time
import tempfile
from typing import Optional

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from config import API_KEY, API_SECRET
from auth import get_token
from api import search_properties, fetch_bulk_properties, export_to_csv, export_to_json

app = FastAPI(title="Idealista Rent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory token cache with expiry tracking
_token_cache: dict = {"token": None, "expires_at": 0}


def get_cached_token() -> str:
    if not _token_cache["token"] or time.time() >= _token_cache["expires_at"]:
        token = get_token(API_KEY, API_SECRET)
        _token_cache["token"] = token
        _token_cache["expires_at"] = time.time() + 3000  # refresh 10 min before expiry
    return _token_cache["token"]


def build_filters(
    min_price: Optional[float],
    max_price: Optional[float],
    min_size: Optional[float],
    max_size: Optional[float],
    bedrooms: Optional[str],
    bathrooms: Optional[str],
    furnished: Optional[str],
    preservation: Optional[str],
    since_date: Optional[str],
    order: Optional[str],
    sort: Optional[str],
    garage: Optional[bool],
    terrace: Optional[bool],
    elevator: Optional[bool],
    swimming_pool: Optional[bool],
    air_conditioning: Optional[bool],
    new_development: Optional[bool],
    has_multimedia: Optional[bool],
    builtin_wardrobes: Optional[bool],
    flat: Optional[bool],
    penthouse: Optional[bool],
    duplex: Optional[bool],
    studio: Optional[bool],
    chalet: Optional[bool],
    # --- Room-specific filters (only used when property_type=bedrooms) ---
    housemates: Optional[str],
    smoke_policy: Optional[str],
    pets_policy: Optional[bool],
    gay_partners: Optional[bool],
    new_gender: Optional[str],
) -> dict:
    """Build a dict of only the filters that were actually provided."""
    raw = {
        "minPrice": min_price,
        "maxPrice": max_price,
        "minSize": min_size,
        "maxSize": max_size,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "furnished": furnished,
        "preservation": preservation,
        "sinceDate": since_date,
        "order": order,
        "sort": sort,
        "garage": garage,
        "terrace": terrace,
        "elevator": elevator,
        "swimmingPool": swimming_pool,
        "airConditioning": air_conditioning,
        "newDevelopment": new_development,
        "hasMultimedia": has_multimedia,
        "builtinWardrobes": builtin_wardrobes,
        "flat": flat,
        "penthouse": penthouse,
        "duplex": duplex,
        "studio": studio,
        "chalet": chalet,
        # Room-specific
        "housemates": housemates,
        "smokePolicy": smoke_policy,
        "petsPolicy": pets_policy,
        "gayPartners": gay_partners,
        "newGender": new_gender,
    }
    return {k: v for k, v in raw.items() if v is not None}


@app.get("/properties")
def get_properties(
    # --- Location & pagination ---
    location_id: str = Query(default="0-EU-PT-13"),
    property_type: str = Query(default="homes", description="homes | offices | premises | garages | bedrooms"),
    max_items: int = Query(default=20, ge=1, le=50),
    page: int = Query(default=1, ge=1),
    # --- Price & size ---
    min_price: Optional[float] = Query(default=None),
    max_price: Optional[float] = Query(default=None),
    min_size: Optional[float] = Query(default=None),
    max_size: Optional[float] = Query(default=None),
    # --- Rooms ---
    bedrooms: Optional[str] = Query(default=None, description='e.g. "1,2,3" — 4 means 4+'),
    bathrooms: Optional[str] = Query(default=None, description='e.g. "1,2"'),
    # --- Condition & type ---
    furnished: Optional[str] = Query(default=None, description="furnished | furnishedKitchen"),
    preservation: Optional[str] = Query(default=None, description="good | renew"),
    since_date: Optional[str] = Query(default=None, description="T: today | W: week | M: month"),
    # --- Sorting ---
    order: Optional[str] = Query(default=None, description="price | publicationDate | size | rooms | distance"),
    sort: Optional[str] = Query(default=None, description="asc | desc"),
    # --- Amenities (boolean flags) ---
    garage: Optional[bool] = Query(default=None),
    terrace: Optional[bool] = Query(default=None),
    elevator: Optional[bool] = Query(default=None),
    swimming_pool: Optional[bool] = Query(default=None),
    air_conditioning: Optional[bool] = Query(default=None),
    new_development: Optional[bool] = Query(default=None),
    has_multimedia: Optional[bool] = Query(default=None),
    builtin_wardrobes: Optional[bool] = Query(default=None),
    # --- Subtypes ---
    flat: Optional[bool] = Query(default=None),
    penthouse: Optional[bool] = Query(default=None),
    duplex: Optional[bool] = Query(default=None),
    studio: Optional[bool] = Query(default=None),
    chalet: Optional[bool] = Query(default=None),
    # --- Room-specific (only used when property_type=bedrooms) ---
    housemates: Optional[str] = Query(default=None, description='e.g. "2,3,4" — 4 means 4+'),
    smoke_policy: Optional[str] = Query(default=None, description="allowed | disallowed"),
    pets_policy: Optional[bool] = Query(default=None),
    gay_partners: Optional[bool] = Query(default=None),
    new_gender: Optional[str] = Query(default=None, description="male | female"),
):
    """Search rental properties. All filter params are optional — only provided ones are sent to Idealista."""
    token = get_cached_token()
    filters = build_filters(
        min_price, max_price, min_size, max_size, bedrooms, bathrooms,
        furnished, preservation, since_date, order, sort,
        garage, terrace, elevator, swimming_pool, air_conditioning,
        new_development, has_multimedia, builtin_wardrobes,
        flat, penthouse, duplex, studio, chalet,
        housemates, smoke_policy, pets_policy, gay_partners, new_gender,
    )
    data = search_properties(
        token=token,
        operation="rent",
        property_type=property_type,
        location_id=location_id,
        max_items=max_items,
        page=page,
        filters=filters,
    )
    if not data:
        raise HTTPException(status_code=502, detail="Failed to fetch from Idealista API")
    return data


@app.get("/properties/export")
def export_properties(
    location_id: str = Query(default="0-EU-PT-13"),
    property_type: str = Query(default="homes"),
    format: str = Query(default="json", pattern="^(json|csv)$"),
    max_count: int = Query(default=200, ge=1, le=200),
    min_price: Optional[float] = Query(default=None),
    max_price: Optional[float] = Query(default=None),
    min_size: Optional[float] = Query(default=None),
    max_size: Optional[float] = Query(default=None),
    bedrooms: Optional[str] = Query(default=None),
    bathrooms: Optional[str] = Query(default=None),
    furnished: Optional[str] = Query(default=None),
    preservation: Optional[str] = Query(default=None),
    since_date: Optional[str] = Query(default=None),
    order: Optional[str] = Query(default=None),
    sort: Optional[str] = Query(default=None),
    garage: Optional[bool] = Query(default=None),
    terrace: Optional[bool] = Query(default=None),
    elevator: Optional[bool] = Query(default=None),
    swimming_pool: Optional[bool] = Query(default=None),
    air_conditioning: Optional[bool] = Query(default=None),
    new_development: Optional[bool] = Query(default=None),
    has_multimedia: Optional[bool] = Query(default=None),
    builtin_wardrobes: Optional[bool] = Query(default=None),
    flat: Optional[bool] = Query(default=None),
    penthouse: Optional[bool] = Query(default=None),
    duplex: Optional[bool] = Query(default=None),
    studio: Optional[bool] = Query(default=None),
    chalet: Optional[bool] = Query(default=None),
    # --- Room-specific (only used when property_type=bedrooms) ---
    housemates: Optional[str] = Query(default=None),
    smoke_policy: Optional[str] = Query(default=None),
    pets_policy: Optional[bool] = Query(default=None),
    gay_partners: Optional[bool] = Query(default=None),
    new_gender: Optional[str] = Query(default=None),
):
    """Fetch up to 200 filtered rental properties and return as a downloadable file."""
    token = get_cached_token()
    filters = build_filters(
        min_price, max_price, min_size, max_size, bedrooms, bathrooms,
        furnished, preservation, since_date, order, sort,
        garage, terrace, elevator, swimming_pool, air_conditioning,
        new_development, has_multimedia, builtin_wardrobes,
        flat, penthouse, duplex, studio, chalet,
        housemates, smoke_policy, pets_policy, gay_partners, new_gender,
    )
    properties = fetch_bulk_properties(
        token=token,
        operation="rent",
        property_type=property_type,
        location_id=location_id,
        max_count=max_count,
        filters=filters,
    )

    if not properties:
        raise HTTPException(status_code=404, detail="No properties found for the given filters")

    tmp_dir = tempfile.gettempdir()

    if format == "csv":
        filepath = os.path.join(tmp_dir, "properties.csv")
        export_to_csv(properties, filepath)
        return FileResponse(filepath, media_type="text/csv", filename="properties.csv")

    filepath = os.path.join(tmp_dir, "properties.json")
    export_to_json(properties, filepath)
    return FileResponse(filepath, media_type="application/json", filename="properties.json")
