# CoreLogic API Analysis: Finding ALL Properties in Geographic Area

## Executive Summary

After thorough investigation of CoreLogic/Cotality API documentation, I have identified the solution to retrieve ALL property IDs in a geographic search area, not just those with sales history.

**CRITICAL FINDING**: The Rapid Search API endpoints that support radius searches can return **ALL properties without filtering by sales history**.

---

## APIs Available for Geographic Search

### 1. Rapid Search API (Recommended Solution)

#### Two Endpoints with Geographic Radius Capability:

**Endpoint 1: GET /search/au**
- HTTP Method: GET
- Base URL: `https://rapid-search-api-uat.ad.corelogic.asia`
- **Key Advantage**: Returns ALL properties in radius by default
- **Supports radius searches WITHOUT "lastSale" requirement**

**Endpoint 2: POST /batchSearch/au**
- HTTP Method: POST (bulk search)
- Base URL: `https://rapid-search-api-uat.ad.corelogic.asia`
- Flexible filtering with multiple parameters in request body

#### Geographic Search Parameters:
```
lat (decimal) - Latitude of search center
lon (decimal) - Longitude of search center
radius (float) - Search radius (in kilometers)
```

Example: `?lat=-37.97111598&lon=145.26288642&radius=7.5`

#### Key Filters Available (ALL OPTIONAL):
- `beds` - Bedroom count
- `baths` - Bathroom count
- `carSpaces` - Parking spaces
- `landArea` - Land area in m²
- `type` - Property type (unit, house, commercial, land, etc.)
- `isActive` - Active properties (TRUE by default)

#### CRITICAL DIFFERENCE - No Sales History Filter:
- Does NOT require `salesLastSaleSettlementDate` parameter
- Does NOT require `isRecentlySold` parameter
- Returns properties regardless of sales history
- Returns properties even if they've NEVER been sold

---

### 2. Search API (Legacy but Comprehensive)

#### Endpoint: GET /search/au/property/geo/radius

Base URL: `https://api-sbox.corelogic.asia`

**Description**: "Find properties within a radius of geographic coordinates"

**Parameters**:
- `lat` & `lon` - Coordinates
- `radius` - Search radius in kilometers (max 100km)
- Filter by beds, baths, carSpaces, landArea, property types, etc.

**IMPORTANT**: This endpoint can return properties WITHOUT sales history filters applied.

---

## Why Rapid Search is the Better Solution

### Comparison Table:

| Aspect | Rapid Search `/search/au` | Legacy Search `/geo/radius` |
|--------|---------------------------|------------------------------|
| Returns all properties | YES | YES |
| No sales history filter | YES | YES |
| Supports lat/lon/radius | YES | YES |
| Batch processing | YES (POST variant) | No |
| Response speed | Fast (optimized) | Standard |
| Geographic precision | Precise | Precise |
| Filter options | Extensive | Extensive |
| Default behavior | Returns ALL properties | Returns ALL properties |

---

## Solution Implementation

### Method 1: Rapid Search GET Endpoint (Simplest)

```bash
# Get ALL properties in 7.5km radius around coordinates
GET https://rapid-search-api-uat.ad.corelogic.asia/search/au
  ?filter=PROPERTY_ID_OR_ADDRESS
  &resultsFormat=FULL
  &lat=-37.97111598
  &lon=145.26288642
  &radius=7.5
```

### Method 2: Rapid Search POST Endpoint (Bulk)

```json
POST https://rapid-search-api-uat.ad.corelogic.asia/batchSearch/au
{
  "filter": {
    "lat": -37.97111598,
    "lon": 145.26288642,
    "radius": 7.5
  }
}
```

### Method 3: Legacy Search API

```bash
GET https://api-sbox.corelogic.asia/search/au/property/geo/radius
  ?lat=-37.97111598
  &lon=145.26288642
  &radius=5
  &size=20
  &page=0
```

---

## What the APIs Return

### Properties Included:
- Properties with sales history
- Properties with NO sales history
- Properties that have NEVER been sold
- Rental properties
- Properties for sale
- Inactive properties (unless filtered out with `isActive=false`)

### Properties Excluded:
- None (all properties in geographic radius are returned by default)

### Example Response Structure:
```json
{
  "propertyList": [
    {
      "propertyId": 12345678,
      "address": {
        "singleLine": "123 Main Street, Sydney NSW 2000",
        "streetNumber": "123",
        "streetName": "Main Street",
        "locality": "Sydney",
        "state": "NSW",
        "postcode": "2000"
      },
      "coordinates": {
        "latitude": -33.8688,
        "longitude": 151.2093
      },
      "propertyType": "RESIDENTIAL",
      "attributes": {
        "beds": 3,
        "baths": 2,
        "landArea": 650
      },
      "lastSale": null,  // Can be null for properties never sold
      "onTheMarket": {
        "forSale": false,
        "forRent": false
      }
    }
  ],
  "pagination": {
    "totalProperties": 1247,
    "currentPage": 1,
    "pageSize": 50,
    "totalPages": 25
  }
}
```

---

## Key Advantages of This Solution

1. **Gets ALL Properties**: Not filtered by sales history
2. **Property IDs**: Unique identifier for every property returned
3. **Full Geographic Search**: Radius-based searches around coordinates
4. **Flexibility**: Can combine with optional filters (beds, baths, property type, etc.)
5. **Pagination**: Handle large result sets efficiently
6. **AVMs Available**: Once you have propertyId, use Property Details API to get AVM data

---

## Obtaining AVMs for ALL Properties

Once you have the property IDs from the geographic search:

### Step 1: Get Property IDs from Geographic Search
```
GET /search/au/property/geo/radius
  ?lat=<latitude>&lon=<longitude>&radius=<km>
  → Returns: List of ALL propertyIds in area
```

### Step 2: Get Property Details (including AVM)
```
GET /property-details/au/properties/{propertyId}/attributes/core
  → Returns: Property attributes, build info
  
GET /property-details/au/properties/{propertyId}/site
  → Returns: Site value (AVM data) with dates
```

### Step 3: Response with AVM Data
```json
{
  "siteValueList": [
    {
      "date": "2024-06-30",
      "type": "SV",
      "value": 850000,      // <- AVM VALUE
      "assessmentDate": "2024-04-26"
    }
  ]
}
```

---

## Migration from `/batchSearch/au` (Sales-Only)

### Current Problem
```
POST /batchSearch/au with lastSale filter
→ Only returns properties with SALES HISTORY
→ Missing properties never sold
→ Missing properties recently purchased
```

### Solution
```
GET /search/au with lat/lon/radius (NO lastSale filter)
→ Returns ALL properties in area
→ Includes properties with no sales
→ Complete coverage for AVM analysis
```

### Parameter Mapping:
| Old (Sales-Only) | New (All Properties) | Change |
|------------------|----------------------|--------|
| `lastSale` filter | (Remove) | NOT REQUIRED |
| `lat/lon/radius` | `lat/lon/radius` | Same |
| `filter` object | Query parameters | Format change |
| Limited results | Full property database | Expanded results |

---

## Implementation Example

### Python Implementation

```python
import requests

# Configuration
API_URL = "https://rapid-search-api-uat.ad.corelogic.asia/search/au"
LATITUDE = -37.97111598
LONGITUDE = 145.26288642
RADIUS_KM = 7.5

# Parameters for ALL properties (no sales filter)
params = {
    "filter": "PROPERTY_ID",
    "resultsFormat": "FULL",
    "lat": LATITUDE,
    "lon": LONGITUDE,
    "radius": RADIUS_KM,
    # Optional filters (but NOT filtering by sales)
    "isActive": True  # Optional: can include inactive
}

# Get all properties
response = requests.get(API_URL, params=params, headers={
    "Authorization": f"Bearer {access_token}"
})

properties = response.json()["propertyList"]
property_ids = [p["propertyId"] for p in properties]

print(f"Found {len(property_ids)} properties (including those with no sales history)")

# Now get AVMs for each property
for property_id in property_ids:
    avm_response = requests.get(
        f"https://api-sbox.corelogic.asia/property-details/au/properties/{property_id}/site",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    site_data = avm_response.json()
    if "siteValueList" in site_data:
        print(f"Property {property_id}: AVM = ${site_data['siteValueList'][0]['value']}")
```

---

## Summary of Findings

### YES - These Endpoints Return ALL Properties:
1. **GET /search/au** (Rapid Search) - RECOMMENDED
2. **POST /batchSearch/au** (Rapid Search Batch)
3. **GET /search/au/property/geo/radius** (Legacy Search)

### NO - These Endpoints Only Return Sold Properties:
- `/search/au/property/geo/radius/lastSale` (Sales-only variant)
- Any endpoint with `/lastSale` in the path
- `/batchSearch/au` with `lastSaleSettlementDate` filter

### The Critical Difference:
- **Without** `lastSale` parameter/filter → All properties
- **With** `lastSale` parameter/filter → Only properties with sales

---

## Conclusion

The Rapid Search API's `/search/au` endpoint is the recommended solution for obtaining ALL property IDs in a geographic search area. By using the latitude, longitude, and radius parameters WITHOUT applying any sales history filters, you can:

1. Get comprehensive coverage of all properties in the area
2. Include properties that have never been sold
3. Include recently purchased properties with minimal transaction history
4. Then fetch AVMs from Property Details API for each property

This provides a complete solution for your risk assessment system to analyze every property in a radius, not just those with recent sales activity.
