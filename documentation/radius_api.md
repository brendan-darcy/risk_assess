# CoreLogic Search by Radius API

## Endpoint
```
GET /search/au/property/geo/radius
```

## Description
The Search by Radius operation allows users to retrieve a list of properties that surround a central geographical point (latitude, longitude). Users can filter by various basic attributes and will receive a sorted list that includes summary data for each property record. The default sort of the results is ascending by the property's distance from the center point.

## Parameters

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `radius` | query | **Required.** The radius, in kilometres, used to perform the search around the latitude and longitude provided. Maximum value: 100. |

### Location Parameters (Choose One)

| Parameter | Type | Description |
|-----------|------|-------------|
| `propertyId` | query | The unique ID of the property. Mandatory if lat&lon are not provided. |
| `lat` + `lon` | query | The latitude and longitude coordinates of the central point. Both are mandatory if propertyId is not provided. |

### Filter Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `localityId` | query | Locality search filter. Single value or comma-separated values: `localityId={id},{id}...` |
| `postCodeId` | query | Postcode search filter. Single value or comma-separated values: `postCodeId={id},{id}...` |
| `streetId` | query | Street search filter. Single value or comma-separated values: `streetId={id},{id}...` |
| `baths` | query | Number of bathrooms. Exact value or range (e.g., `4`, `2-5`, `3-`, `-4`) |
| `beds` | query | Number of bedrooms. Exact value or range (e.g., `4`, `2-5`, `3-`, `-4`) |
| `carSpaces` | query | Number of car spaces. Exact value or range (e.g., `2`, `1-3`, `1-`, `-3`) |
| `landArea` | query | Land area in m². Exact value or range (e.g., `300`, `300-600`, `300-`, `-600`) |
| `pTypes` | query | Property types. Single or comma-separated values from available types below |
| `includeHistoric` | query | Include historic properties |

### Available Property Types
- BUSINESS
- COMMERCIAL
- COMMUNITY
- FARM
- FLATS
- HOUSE
- LAND
- OTHER
- STORAGE_UNIT
- UNIT

### Sorting Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `sort` | query | Sort criteria: `{attribute},{order}`. Multiple sorts: `sort={attr1},{order}&sort={attr2},{order}` |

**Available sort attributes:**
- `bath`, `beds`, `carSpaces`, `landArea`, `pType`

**Sort orders:**
- `asc` (ascending, default)
- `desc` (descending)

**Example:** `sort=beds,desc` sorts by bedrooms in descending order.

### Pagination Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | query | Page number to return (default: 0) |
| `size` | query | Records per page (default: 20, maximum: 20) |

## Examples

### Search by Coordinates
```
GET /search/au/property/geo/radius?lat=-33.8688&lon=151.2093&radius=5&beds=3&pTypes=HOUSE,UNIT
```

### Search by Property ID
```
GET /search/au/property/geo/radius?propertyId=1234567&radius=2&baths=2-&sort=landArea,desc
```

## Response Codes

| Code | Description |
|------|-------------|
| **200** | OK - Successful response |
| **400** | Bad Request - Invalid parameters |
| **401** | Unauthorized - Authentication required |
| **403** | Forbidden - Access denied |
| **404** | Not Found - Property/coordinates not found |
| **500** | Internal Server Error |
| **502** | Bad Gateway |

## Common Error Messages

### 400 Bad Request
- "Page size cannot exceed 20"
- "Invalid request parameter value for `<parameterName>` provided"
- "Either lat&lon or propertyId is mandatory"
- "radius: Missing mandatory parameter, radius"
- "radius: Exceeds the limit of 100"

### 404 Not Found
- "Property id does not exist"
- "Geo coordinates not available for the requested propertyId"

## Usage Notes

- Maximum radius is 100 kilometres
- Maximum page size is 20 records
- Either `propertyId` OR both `lat` and `lon` must be provided
- Results are sorted by distance from center point by default
- Property types can be filtered using comma-separated values
- Numeric filters support exact values or ranges using `-` syntax
- **No default age/date limit** - returns all historical sales unless `date` parameter is specified
- Use `date` parameter to filter by sale date in `YYYYMMDD` format (e.g., `20240101-` for sales from 2024 onwards)

