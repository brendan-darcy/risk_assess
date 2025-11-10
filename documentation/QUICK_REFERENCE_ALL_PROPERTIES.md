# Quick Reference: Finding ALL Properties in Geographic Area

## The Problem
Your current implementation using `/batchSearch/au` with `lastSale` filters only returns properties with sales history. Many properties in your search radius have never been sold and are therefore missing from your analysis.

## The Solution
Use the Rapid Search API's `/search/au` endpoint with lat/lon/radius parameters **WITHOUT any sales history filters**.

---

## Three Implementation Options

### Option 1: GET /search/au (RECOMMENDED - Simplest)

```bash
curl -X GET \
  "https://rapid-search-api-uat.ad.corelogic.asia/search/au" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -G \
  --data-urlencode "filter=PROPERTY_ID" \
  --data-urlencode "resultsFormat=FULL" \
  --data-urlencode "lat=-37.97111598" \
  --data-urlencode "lon=145.26288642" \
  --data-urlencode "radius=7.5"
```

**Response**: List of ALL properties in 7.5km radius
- Includes properties with sales history
- Includes properties with NO sales history
- Includes properties that have NEVER been sold

---

### Option 2: POST /batchSearch/au (Bulk Processing)

```bash
curl -X POST \
  "https://rapid-search-api-uat.ad.corelogic.asia/batchSearch/au" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {
      "lat": -37.97111598,
      "lon": 145.26288642,
      "radius": 7.5
    }
  }'
```

**Use Case**: When you need to search multiple radius areas in one request

---

### Option 3: Legacy GET /search/au/property/geo/radius

```bash
curl -X GET \
  "https://api-sbox.corelogic.asia/search/au/property/geo/radius" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -G \
  --data-urlencode "lat=-37.97111598" \
  --data-urlencode "lon=145.26288642" \
  --data-urlencode "radius=5" \
  --data-urlencode "page=0" \
  --data-urlencode "size=20"
```

**Use Case**: Backward compatibility with existing code

---

## Key Differences from Your Current Approach

| Your Current | New Approach | Difference |
|--------------|-------------|-----------|
| POST /batchSearch/au | GET /search/au | **Remove sales filter** |
| Filter: lastSaleSettlementDate | (No date filter) | **Filter removed** |
| isRecentlySold: true | (Not specified) | **Not filtering by recency** |
| Result: Only sold properties | Result: ALL properties | **Expansion of coverage** |

---

## What Gets Returned

### YES - All These Properties Are Included:
- Properties with 1+ sales transactions
- Properties that have never been sold
- Properties recently purchased (within last 30 days)
- Rental properties
- Properties currently for sale
- Properties currently for rent
- Inactive properties (unless you add `isActive=false`)

### Typical Response Structure:

```json
{
  "propertyList": [
    {
      "propertyId": 12345678,
      "address": {
        "singleLine": "123 Main Street, Sydney NSW 2000"
      },
      "coordinates": {
        "latitude": -33.8688,
        "longitude": 151.2093
      },
      "propertyType": "RESIDENTIAL",
      "lastSale": null,  // <-- NULL FOR NEVER-SOLD PROPERTIES
      "attributes": {
        "beds": 3,
        "baths": 2,
        "landArea": 650
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

## Getting AVMs for ALL Properties

### Step 1: Extract Property IDs from Search Results
```python
property_ids = [p["propertyId"] for p in response["propertyList"]]
```

### Step 2: Get Site Value (AVM) for Each Property
```bash
curl -X GET \
  "https://api-sbox.corelogic.asia/property-details/au/properties/{propertyId}/site" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

### Step 3: Extract AVM Value
```json
{
  "siteValueList": [
    {
      "date": "2024-06-30",
      "type": "SV",
      "value": 850000    // <-- YOUR AVM
    }
  ]
}
```

---

## Python Code Example

```python
import requests
from urllib.parse import urlencode

# Configuration
RAPID_SEARCH_URL = "https://rapid-search-api-uat.ad.corelogic.asia/search/au"
PROPERTY_API_URL = "https://api-sbox.corelogic.asia"
ACCESS_TOKEN = "your_token_here"

# Get ALL properties in radius
params = {
    "filter": "PROPERTY_ID",
    "resultsFormat": "FULL",
    "lat": -37.97111598,
    "lon": 145.26288642,
    "radius": 7.5
}

headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

# Search
response = requests.get(RAPID_SEARCH_URL, params=params, headers=headers)
properties = response.json()["propertyList"]

print(f"Found {len(properties)} total properties")

# Get AVMs
for prop in properties:
    prop_id = prop["propertyId"]
    
    # Get site value (AVM)
    site_url = f"{PROPERTY_API_URL}/property-details/au/properties/{prop_id}/site"
    site_response = requests.get(site_url, headers=headers)
    site_data = site_response.json()
    
    if "siteValueList" in site_data and site_data["siteValueList"]:
        avm = site_data["siteValueList"][0]["value"]
        address = prop["address"]["singleLine"]
        print(f"{address}: ${avm:,.0f}")
```

---

## Common Mistakes to Avoid

### WRONG - Still Filtering by Sales
```bash
# This still only returns sold properties
?filter=PROPERTY_ID&lat=...&lon=...&radius=7.5&salesLastSaleSettlementDate=20240101-
```

### CORRECT - No Sales Filter
```bash
# This returns ALL properties
?filter=PROPERTY_ID&lat=...&lon=...&radius=7.5
```

### WRONG - Using lastSale Endpoint
```bash
GET /search/au/property/geo/radius/lastSale  # WRONG - sales only
```

### CORRECT - Using Standard Radius Endpoint
```bash
GET /search/au/property/geo/radius  # CORRECT - all properties
```

---

## Migration Path

### Step 1: Identify Current Code
Find where you're using `/batchSearch/au` with `lastSale` filtering

### Step 2: Replace with New Endpoint
Use `/search/au` with lat/lon/radius instead

### Step 3: Remove Sales Filters
Delete `salesLastSaleSettlementDate`, `isRecentlySold`, and similar parameters

### Step 4: Test Coverage
Verify you're now getting properties without sales history

### Step 5: Update AVM Retrieval
Confirm AVMs are available for all returned properties

---

## Radius Limits

- **Minimum**: 0 (exact location)
- **Maximum for Rapid Search**: Not specified (typically unlimited)
- **Maximum for Legacy Search**: 100 km
- **Recommended for AVMs**: 1-10 km (manageable result sets)

---

## Response Pagination

```json
{
  "pagination": {
    "currentPage": 1,
    "pageSize": 50,
    "totalPages": 25,
    "totalProperties": 1247,
    "hasNextPage": true
  }
}
```

Use `page` parameter to retrieve additional results:
```bash
?lat=...&lon=...&radius=7.5&page=0
?lat=...&lon=...&radius=7.5&page=1
?lat=...&lon=...&radius=7.5&page=2
```

---

## Summary

1. **Current**: `/batchSearch/au` with `lastSale` → Only sold properties
2. **New**: `/search/au` with `lat/lon/radius` → ALL properties
3. **Result**: Complete coverage for comprehensive risk assessment
4. **AVMs**: Available for all property IDs via Property Details API

This gives you comprehensive property coverage for your risk assessment system, not just those with recent transactions.
