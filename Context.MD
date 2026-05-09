# Project Context

## Changes made

**api.py**
- `operation` default changed from `"sale"` → `"rent"`
- Added `page` parameter to `search_properties`
- Added `fetch_bulk_properties()` — paginates automatically (50/page × 4 pages = 200)
- Added `export_to_json()` and `export_to_csv()` helpers
- Added `_build_form_data()` helper — converts Python booleans to `"true"`/`"false"` strings (required by Idealista's form encoding)
- `search_properties` now accepts a `filters: dict` param — only the keys present in the dict are sent to the API
- `fetch_bulk_properties` now forwards filters through pagination
- Added `locale=pt` to all requests — forces summary/description fields to return in Portuguese

**server.py** — FastAPI server with:
- `GET /properties` — paginated rental search with filters
- `GET /properties/export?format=json|csv` — downloads up to 200 properties as a file
- Token auto-refresh before it expires
- `build_filters()` — collects only the query params the user actually provided (skips `None` values)
- All supported filter params exposed: price range, size range, bedrooms, bathrooms, furnished, preservation, since_date, sorting, boolean amenity/subtype flags, and room-specific filters

**SearchScreen.jsx** — React Native template with:
- Type toggle: `Apartamento` vs `Quarto` — switches `property_type` and shows different filter sections
- Homes section: bedrooms, bathrooms, amenity toggles
- Rooms section: housemates count, smoke policy, pet policy, gender preference
- `buildQueryString` skips any filter left empty
- `AsyncStorage` saves last used filters automatically on submit
- `FlatList` of property cards with thumbnail, price, details, and `url` for landlord contact

---

## Idealista API — All available filter parameters

### Common (apply to all property types)

| API param | Our server param | Type | Description | Example values |
|---|---|---|---|---|
| `operation` | hardcoded | string | Type of transaction | `"rent"` (always) |
| `propertyType` | `property_type` | string | Property category | `"homes"`, `"bedrooms"`, `"offices"`, `"premises"`, `"garages"` |
| `locationId` | `location_id` | string | Idealista location code | `"0-EU-PT-13"` (Portugal) |
| `maxItems` | `max_items` | integer | Results per page (max 50) | `20` |
| `numPage` | `page` | integer | Page number | `1`, `2`, `3` |
| `minPrice` | `min_price` | double | Minimum price | `400.0` |
| `maxPrice` | `max_price` | double | Maximum price | `1200.0` |
| `sinceDate` | `since_date` | string | Property listing age | `"T"` today, `"W"` last week, `"M"` last month |
| `order` | `order` | string | Sort field | `"price"`, `"publicationDate"`, `"size"`, `"distance"` |
| `sort` | `sort` | string | Sort direction | `"asc"`, `"desc"` |
| `hasMultimedia` | `has_multimedia` | boolean | Only listings with photos/video | `true` |
| `locale` | hardcoded | string | Language of text fields | `"pt"` (always — fixes Spanish descriptions) |

---

### Homes-specific (`propertyType=homes`)

| API param | Our server param | Type | Description | Example values |
|---|---|---|---|---|
| `minSize` | `min_size` | double | Minimum size in m² | `40.0` |
| `maxSize` | `max_size` | double | Maximum size in m² | `120.0` |
| `bedrooms` | `bedrooms` | string | Number of bedrooms (multivalued) | `"1"`, `"2"`, `"1,2,3"`, `"4"` (4+) |
| `bathrooms` | `bathrooms` | string | Number of bathrooms (multivalued) | `"1"`, `"2"`, `"1,2"` |
| `furnished` | `furnished` | string | Furnished state | `"furnished"`, `"furnishedKitchen"` |
| `preservation` | `preservation` | string | Property condition | `"good"`, `"renew"` |
| `newDevelopment` | `new_development` | boolean | New build only | `true` |
| `garage` | `garage` | boolean | Has garage | `true` |
| `terrace` | `terrace` | boolean | Has terrace | `true` |
| `elevator` | `elevator` | boolean | Has elevator | `true` |
| `swimmingPool` | `swimming_pool` | boolean | Has swimming pool | `true` |
| `airConditioning` | `air_conditioning` | boolean | Has air conditioning | `true` |
| `builtinWardrobes` | `builtin_wardrobes` | boolean | Has built-in wardrobes | `true` |
| `flat` | `flat` | boolean | Subtype: flat | `true` |
| `penthouse` | `penthouse` | boolean | Subtype: penthouse | `true` |
| `duplex` | `duplex` | boolean | Subtype: duplex | `true` |
| `studio` | `studio` | boolean | Subtype: studio | `true` |
| `chalet` | `chalet` | boolean | Subtype: chalet | `true` |

---

### Rooms-specific (`propertyType=bedrooms`)

| API param | Our server param | Type | Description | Example values |
|---|---|---|---|---|
| `housemates` | `housemates` | string | Number of people already living there | `"2"`, `"3"`, `"4"` (4+) |
| `smokePolicy` | `smoke_policy` | string | Smoking policy | `"allowed"`, `"disallowed"` |
| `petsPolicy` | `pets_policy` | boolean | Pets allowed | `true` |
| `gayPartners` | `gay_partners` | boolean | LGBTQ+ friendly room | `true` |
| `newGender` | `new_gender` | string | Landlord's preferred gender for new tenant | `"male"`, `"female"` |

---

## API response fields (elementList items)

| Field | Type | Description |
|---|---|---|
| `propertyCode` | integer | Unique property ID |
| `url` | string | Full Idealista listing URL — use this to open contact page |
| `thumbnail` | string | Thumbnail image URL |
| `numPhotos` | integer | Number of photos |
| `price` | integer | Monthly rent in € |
| `priceByArea` | double | Price per m² |
| `size` | integer | Size in m² |
| `rooms` | integer | Number of rooms |
| `bathrooms` | integer | Number of bathrooms |
| `floor` | string | Floor number |
| `address` | string | Street address |
| `district` | string | District |
| `neighborhood` | string | Neighborhood |
| `municipality` | string | City |
| `province` | string | Province |
| `latitude` / `longitude` | double | Coordinates |
| `propertyType` | string | e.g. `"studio"`, `"flat"` |
| `operation` | string | `"rent"` |
| `status` | string | `"good"`, `"renew"`, `"newdevelopment"` |
| `exterior` | boolean | Is exterior facing |
| `hasLift` | boolean | Has elevator |
| `hasVideo` | boolean | Has video tour |
| `newDevelopment` | boolean | Is new development |
| `showAddress` | boolean | Owner allows showing address |
| `agency` | boolean | `false` = private owner, `true` = agency |
| `parkingSpace` | object | `hasParkingSpace`, `isParkingSpaceIncludedInPrice`, `parkingSpacePrice` |
| `detailedType` | object | `typology` + `subtypology` |
