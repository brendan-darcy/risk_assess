# CoreLogic Search API

Comprehensive search services for properties, addresses, locations, and geographic queries across Australia and New Zealand.

## Overview

The Search API enables you to find properties, addresses, and locations based on various criteria. Search services return sorted lists with summary data and are designed to support both overview displays and detailed data service requests.

**Base URL:** `https://api-sbox.corelogic.asia`

## Key Capabilities

- **Location Search**: Find properties by council area, locality, postcode, street
- **Geographic Search**: Radius-based property searches around coordinates
- **Address Matching**: Resolve addresses to property records
- **Market-Specific Search**: Filter by sales history or on-the-market status
- **Suggestion Services**: Auto-complete for addresses and locations

## Authentication

- **OAuth2 Bearer Token** required
- Standard HTTP response codes for authentication errors

## API Categories

### 1. Address Services

#### Address Search
```
GET /search/au/address
```
**Description**: Retrieve properties matching an address search string
**Parameters**:
- `singleLineAddress` (required): Full address string to match
- `includeHistoric` (optional): Include historical records

#### Address Matcher
```
GET /search/au/matcher/address
```
**Description**: Enhanced address matching with scoring and validation
**Use Case**: Address standardization and validation workflows

### 2. Location-Based Property Search

#### By Council Area
```
GET /search/au/property/councilArea/{councilAreaId}
```
**Description**: Find all properties within a specific council area

#### By Locality (Suburb)
```
GET /search/au/property/locality/{localityId}
```
**Description**: Find properties within a specific suburb/locality

#### By Postcode
```
GET /search/au/property/postcode/{postcodeId}
```
**Description**: Find properties within a postcode area

#### By Street
```
GET /search/au/property/street/{streetId}
```
**Description**: Find all properties on a specific street

#### By Place
```
GET /search/au/property/place/{placeId}
```
**Description**: Find properties within a defined place/region

### 3. Sales History Search

Filter properties based on recent sales activity:

#### Council Area Sales
```
GET /search/au/property/councilArea/{councilAreaId}/lastSale
```

#### Locality Sales
```
GET /search/au/property/locality/{localityId}/lastSale
```

#### Postcode Sales
```
GET /search/au/property/postcode/{postcodeId}/lastSale
```

#### Street Sales
```
GET /search/au/property/street/{streetId}/lastSale
```

#### Place Sales
```
GET /search/au/property/place/{placeId}/lastSale
```

### 4. On The Market (OTM) - For Rent

Find properties currently listed for rent:

#### Council Area Rentals
```
GET /search/au/property/councilArea/{councilAreaId}/otmForRent
```

#### Locality Rentals
```
GET /search/au/property/locality/{localityId}/otmForRent
```

#### Postcode Rentals
```
GET /search/au/property/postcode/{postcodeId}/otmForRent
```

#### Street Rentals
```
GET /search/au/property/street/{streetId}/otmForRent
```

#### Place Rentals
```
GET /search/au/property/place/{placeId}/otmForRent
```

### 5. On The Market (OTM) - For Sale

Find properties currently listed for sale:

#### Council Area Sales
```
GET /search/au/property/councilArea/{councilAreaId}/otmForSale
```

#### Locality Sales
```
GET /search/au/property/locality/{localityId}/otmForSale
```

#### Postcode Sales
```
GET /search/au/property/postcode/{postcodeId}/otmForSale
```

#### Street Sales
```
GET /search/au/property/street/{streetId}/otmForSale
```

#### Place Sales
```
GET /search/au/property/place/{placeId}/otmForSale
```

### 6. Geographic Search (Radius-Based)

#### All Properties by Radius
```
GET /search/au/property/geo/radius
```
**Description**: Find properties within a radius of geographic coordinates
**Parameters**:
- Latitude/longitude coordinates
- Search radius (meters/kilometers)
- Property type filters

#### Recent Sales by Radius
```
GET /search/au/property/geo/radius/lastSale
```
**Description**: Find recently sold properties within geographic radius

#### Rentals by Radius
```
GET /search/au/property/geo/radius/otmForRent
```
**Description**: Find rental properties within geographic radius

#### Sales by Radius
```
GET /search/au/property/geo/radius/otmForSale
```
**Description**: Find properties for sale within geographic radius

### 7. Specialized Search

#### Vendor Search
```
GET /search/au/property/vendor/{vendorId}
```
**Description**: Find properties associated with specific vendors/sellers

### 8. Suggestion Services

#### Property/Parcel Suggestions
```
GET /property/au/parcel/suggest.json
```
**Description**: Auto-complete suggestions for property/parcel searches
**Use Case**: Search interface auto-complete functionality

#### Enhanced Property Suggestions (v2)
```
GET /property/au/v2/suggest.json
```
**Description**: Improved suggestion service with enhanced matching
**Features**:
- Better address parsing
- Fuzzy matching capabilities
- Multiple result types

#### Point Search
```
GET /property/au/v2/search/point
```
**Description**: Search properties by precise geographic points
**Use Case**: Map-based property selection

## Common Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `councilAreaId` | integer | Council area identifier | 123 |
| `localityId` | integer | Locality/suburb identifier | 456 |
| `postcodeId` | integer | Postcode identifier | 789 |
| `streetId` | integer | Street identifier | 101112 |
| `placeId` | integer | Place/region identifier | 131415 |
| `vendorId` | integer | Vendor/seller identifier | 161718 |
| `singleLineAddress` | string | Complete address string | "123 Main St Sydney NSW 2000" |
| `includeHistoric` | boolean | Include historical records | true/false |
| `latitude` | decimal | Geographic latitude | -33.8688 |
| `longitude` | decimal | Geographic longitude | 151.2093 |
| `radius` | integer | Search radius in meters | 1000 |

## Search Result Structure

Search results include detailed response schemas with comprehensive property and market data:

### Comparable Analysis Response
```json
{
  "comparableRule": {
    "ruleId": 0,
    "ruleName": "string",
    "ruleSource": "string"
  },
  "comparablesSummaryList": [
    {
      "averageForRentListingPrice": 0,
      "averageForSaleListingPrice": 0,
      "averageSalePrice": 0,
      "comparableCategory": "string",
      "comparableCategoryId": 0,
      "maximumContractDate": "string",
      "maximumForRentCampaignDate": "string",
      "maximumForRentListingPrice": 0,
      "maximumForSaleCampaignDate": "string",
      "maximumForSaleListingPrice": 0,
      "maximumSalePrice": 0,
      "medianForRentListingPrice": 0,
      "medianForSaleListingPrice": 0,
      "medianSalePrice": 0,
      "minimumContractDate": "string",
      "minimumForRentCampaignDate": "string",
      "minimumForRentListingPrice": 0,
      "minimumForSaleCampaignDate": "string",
      "minimumForSaleListingPrice": 0,
      "minimumSalePrice": 0,
      "numberOfForRentListings": 0,
      "numberOfForSaleListings": 0,
      "numberOfSales": 0
    }
  ],
  "propertyList": [
    {
      "propertyId": 12345678,
      "address": {
        "singleLine": "123 Main Street, Sydney NSW 2000",
        "unitNumber": "2A",
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
        "carSpaces": 1,
        "landArea": 650,
        "floorArea": 120
      },
      "lastSale": {
        "price": 850000,
        "contractDate": "2023-06-15",
        "settlementDate": "2023-07-15",
        "type": "Normal Sale",
        "agencyName": "ABC Real Estate",
        "agentName": "John Smith"
      },
      "onTheMarket": {
        "forSale": {
          "isListed": true,
          "listingDate": "2023-08-01",
          "price": "$900,000",
          "priceDescription": "$900,000",
          "agency": "ABC Real Estate",
          "agent": "Jane Doe",
          "daysOnMarket": 30
        },
        "forRent": {
          "isListed": false,
          "listingDate": null,
          "price": null,
          "agency": null
        }
      },
      "comparableCategory": "Excellent Match",
      "comparableCategoryId": 1,
      "distanceInMeters": 250
    }
  ]
}
```

### Address Search Response
```json
{
  "addressList": [
    {
      "propertyId": 12345678,
      "singleLineAddress": "123 Main Street, Sydney NSW 2000",
      "formattedAddress": {
        "unitNumber": "2A",
        "streetNumber": "123",
        "streetName": "Main Street",
        "streetType": "Street",
        "locality": "Sydney",
        "state": "NSW",
        "postcode": "2000"
      },
      "coordinates": {
        "latitude": -33.8688,
        "longitude": 151.2093
      },
      "propertyType": "RESIDENTIAL",
      "isHistoric": false
    }
  ],
  "totalCount": 15,
  "hasMoreResults": true
}
```

### Geographic Radius Search Response
```json
{
  "searchCriteria": {
    "latitude": -33.8688,
    "longitude": 151.2093,
    "radiusInMeters": 1000,
    "propertyTypes": ["RESIDENTIAL"],
    "includeOnTheMarket": true,
    "includeRecentSales": true
  },
  "resultSummary": {
    "totalProperties": 247,
    "propertiesForSale": 12,
    "propertiesForRent": 8,
    "recentSales": 15,
    "averageSalePrice": 825000,
    "medianSalePrice": 780000
  },
  "propertyList": [
    {
      "propertyId": 12345678,
      "distanceInMeters": 150,
      "address": {
        "singleLine": "123 Main Street, Sydney NSW 2000"
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
      "marketStatus": {
        "onTheMarket": true,
        "marketType": "FOR_SALE",
        "listingPrice": 850000,
        "daysOnMarket": 25
      },
      "lastSale": {
        "price": 750000,
        "contractDate": "2021-03-15"
      }
    }
  ],
  "pagination": {
    "currentPage": 1,
    "pageSize": 50,
    "totalPages": 5,
    "hasNextPage": true
  }
}
```

### Suggestion Service Response
```json
{
  "suggestions": [
    {
      "id": "12345678",
      "type": "PROPERTY",
      "displayText": "123 Main Street, Sydney NSW 2000",
      "fullAddress": "123 Main Street, Sydney NSW 2000",
      "propertyId": 12345678,
      "coordinates": {
        "latitude": -33.8688,
        "longitude": 151.2093
      },
      "score": 0.95
    },
    {
      "id": "LOCALITY_456",
      "type": "LOCALITY",
      "displayText": "Sydney, NSW",
      "localityId": 456,
      "localityName": "Sydney",
      "state": "NSW",
      "postcode": "2000",
      "score": 0.88
    },
    {
      "id": "STREET_789",
      "type": "STREET",
      "displayText": "Main Street, Sydney NSW",
      "streetId": 789,
      "streetName": "Main Street",
      "locality": "Sydney",
      "state": "NSW",
      "score": 0.82
    }
  ],
  "totalSuggestions": 3,
  "query": "123 main st sydney"
}
```

## Search Filters & Sorting

### Available Filters
- **Property Type**: Residential, Commercial, Land
- **Price Range**: Min/max price filters for sales and rentals
- **Date Range**: Recent sales within specified periods
- **Bedroom/Bathroom Count**: Property attribute filters
- **Land Size**: Minimum/maximum land area

### Default Sorting
- **Address Search**: Ascending by unit number
- **Geographic Search**: Distance from center point
- **Sales Search**: Most recent sale date
- **OTM Search**: Listing date (most recent first)

## Response Codes

| Code | Description |
|------|-------------|
| 200 | OK - Search results returned |
| 400 | Bad Request - Invalid search parameters |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - No results for search criteria |
| 500 | Internal Server Error |
| 502 | Bad Gateway - Service temporarily unavailable |

## Use Cases

### 1. **Property Discovery**
- Find properties in specific areas for buyers/investors
- Locate comparable properties for valuation purposes
- Identify investment opportunities in target locations

### 2. **Market Analysis**
- Analyze recent sales in specific areas
- Monitor current rental/sales inventory
- Track market activity by location

### 3. **Address Validation**
- Standardize and validate addresses
- Resolve partial addresses to complete records
- Match addresses to property identifiers

### 4. **Geographic Analysis**
- Find properties within walking distance of amenities
- Radius-based competitor analysis
- Location-based investment research

### 5. **Lead Generation**
- Identify properties currently on the market
- Find recently sold properties for follow-up
- Target specific vendor relationships

## Performance Optimization

### Caching Strategy
- Cache location IDs (council area, locality, postcode, street)
- Store frequently accessed property lists
- Implement pagination for large result sets

### Rate Limiting
- Implement backoff strategies for high-volume requests
- Use geographic search for precise targeting vs. broad location searches
- Combine multiple criteria in single requests where possible

### Best Practices
- Use specific location IDs rather than address strings when possible
- Implement progressive search (start broad, narrow with filters)
- Cache suggestion service results for user interface responsiveness
- Use v2 suggest service for improved accuracy

## Integration Examples

### 1. Property Search Widget
```javascript
// Get suggestions for auto-complete
GET /property/au/v2/suggest.json?q="123 Main"

// Search properties in locality
GET /search/au/property/locality/{localityId}
```

### 2. Map-Based Search
```javascript
// Find properties around clicked point
GET /search/au/property/geo/radius?lat=-33.8688&lon=151.2093&radius=1000

// Get detailed property info
GET /property-details/au/properties/{propertyId}
```

### 3. Market Research Dashboard
```javascript
// Recent sales in area
GET /search/au/property/locality/{localityId}/lastSale

// Current listings
GET /search/au/property/locality/{localityId}/otmForSale
GET /search/au/property/locality/{localityId}/otmForRent
```

## Data Coverage

- **Australia**: Full coverage for all search services
- **New Zealand**: Limited coverage (check service-specific documentation)
- **Historical Data**: Available with `includeHistoric` parameter
- **Real-time Updates**: On-the-market status updated regularly
- **Geographic Precision**: Coordinates accurate to property level

---

*© RP Data Pty Limited trading as Cotality (ABN 67 087 759 171) and CoreLogic NZ Limited trading as Cotality (NZCN 1129102) 2025. All rights reserved.*