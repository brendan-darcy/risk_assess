# CoreLogic Property Data API

**Base URL:** `https://api-sbox.corelogic.asia`  
**OAS Version:** 3.0  
**Authorization:** Bearer token required

## Overview

The Property Data API provides comprehensive property information across Australia and New Zealand, including property details, sales history, advertisements, ownership, and development applications.

## Advertisement Services

### Get Latest Advertisement

```
GET /property/au/v1/property/{propertyId}/advertisements.json
```

Allows users to obtain the most recent advertisement description for a single property. *This is not available for NZ properties.*

**Parameters:**
- `propertyId` (path, required) - Property ID
- `advertisementType` (query, optional) - Type of latest advertisement (`FORSALE` or `FORRENT`)

### Get For Rent Advertisements

```
GET /property/au/v1/property/{propertyId}/for-rent-advertisements.json
```

Obtain detailed for rent advertisement information for a single property. *This is not available for NZ properties.*

**Parameters:**
- `propertyId` (path, required) - Property ID
- `fromDate` (query, optional) - Start date (YYYY-MM-DD)
- `toDate` (query, optional) - End date (YYYY-MM-DD)
- `includeAdvertisementDescription` (query, optional) - Include description (default: false)

### Get For Sale Advertisements

```
GET /property/au/v1/property/{propertyId}/for-sale-advertisements.json
```

Obtain detailed for sale advertisement information for a single property.

**Parameters:**
- `propertyId` (path, required) - Property ID
- `fromDate` (query, optional) - Start date (YYYY-MM-DD)
- `toDate` (query, optional) - End date (YYYY-MM-DD)
- `agencyPhoneNumber` (query, optional) - Filter by agency phone number
- `agencyName` (query, optional) - Filter by agency name
- `includeAdvertisementDescription` (query, optional) - Include description (default: false)

### Get Specific Advertisement

```
GET /property/au/v1/property/{propertyId}/for-rent-advertisement/{advertisementId}.json
GET /property/au/v1/property/{propertyId}/for-sale-advertisement/{advertisementId}.json
```

Get advertisement detail for a single advertisement by ID.

**Parameters:**
- `propertyId` (path, required) - Property ID
- `advertisementId` (path, required) - Advertisement ID
- `includeAdvertisementDescription` (query, optional) - Include description (default: false)

## On The Market (OTM) Services

### Property OTM Sales Campaigns

```
GET /property-details/au/properties/{propertyId}/otm/campaign/sales
```

Get detailed information on the target property's OTM SALE and RENT_AND_SALE campaigns.

**Parameters:**
- `propertyId` (path, required) - CoreLogic unique property identifier
- `includeHistoric` (query, optional) - View historical data (default: false)

**Response Example:**
```json
{
  "forSalePropertyCampaign": {
    "isActiveProperty": true,
    "campaigns": [
      {
        "advertisementId": 7781727,
        "agency": {
          "companyName": "Ray White Real Estate",
          "phoneNumber": "0406 564 619"
        },
        "agent": {
          "agent": "Melinda",
          "phoneNumber": "0413 074 955"
        },
        "auctionDate": "2025-08-28",
        "daysListed": 40,
        "daysOnMarket": 33,
        "firstAdvertisementPrice": "279000",
        "listingMethod": "Normal Sale",
        "saleDate": "2006-02-15"
      }
    ]
  }
}
```

### Property OTM Rent Campaigns

```
GET /property-details/au/properties/{propertyId}/otm/campaign/rent
```

Get detailed information on the target property's RENT and RENT_AND_SALE campaigns.

**Parameters:**
- `propertyId` (path, required) - CoreLogic unique property identifier
- `includeHistoric` (query, optional) - View historical data (default: false)

**Response Example:**
```json
{
  "forRentPropertyCampaign": {
    "campaigns": [
      {
        "advertisementId": 126435443,
        "agency": {
          "companyName": "Ray White Real Estate",
          "phoneNumber": "0406 564 619"
        },
        "daysOnMarket": 36,
        "fromDate": "2016-07-18",
        "period": "W",
        "price": 500,
        "priceDescription": "$500 PER WEEK"
      }
    ],
    "isActiveProperty": true
  }
}
```

## Property Timeline Service

### Property Timeline

```
GET /property-timeline/au/properties/{propertyId}/timeline
```

See a chronological timeline of a property's sale, building consents, for sale and for rent campaign history.

**Parameters:**
- `propertyId` (path, required) - CoreLogic unique property ID
- `withDevelopmentApplications` (query, optional) - Include development applications in timeline

**Response Example:**
```json
{
  "eventTimeline": [
    {
      "type": "string",
      "date": "2025-08-28",
      "detail": {
        "agency": "string",
        "agent": "string",
        "daysOnMarket": 0,
        "method": "string",
        "saleClassification": "string",
        "saleMethod": "string"
      },
      "consentDetail": {
        "consentValue": 0,
        "description": "string",
        "consentNumber": "string"
      }
    }
  ]
}
```

## Property Validation

### Property Validation

```
GET /property/au/property/{id}/validation
```

Obtain the matching Property Id of a saved or cached Id that may have changed (e.g. following a merge or split of a property).

**Parameters:**
- `id` (path, required) - Property ID to validate

**Use Case:**
PropertyIds do not change frequently, however there are real-world scenarios that do cause properties to change, for example the subdivision of a block of land. Use this service to check the validity of a previously used Property Id.

## Property Details Services

### Property Legal Information

```
GET /property-details/au/properties/{propertyId}/legal
```

Obtain legal, title and parcel information on a single property.

**Parameters:**
- `propertyId` (path, required) - CoreLogic unique property identifier
- `includeHistoric` (query, optional) - View historical data (default: false)

**Response Example:**
```json
{
  "legal": {
    "realPropertyDescription": "LOT 1 DP 86383-SUBJ TO SERVICE ESMT",
    "frontage": 27.8,
    "heritageRegistered": "Local Heritage"
  },
  "title": {
    "volume": "1600",
    "folio": "53",
    "titleReference": "WN54A/592",
    "tenureReference": "Freehold"
  },
  "parcels": [
    {
      "parcelId": 2175161,
      "plan": "186160",
      "lot": "117",
      "area": "325 m²",
      "displayValue": "Lot 1 DP 86383"
    }
  ]
}
```

### Property Contacts

```
GET /property-details/au/properties/{propertyId}/contacts
```

Obtain detailed information on contacts of a single property.

**Response Example:**
```json
{
  "contacts": [
    {
      "contactType": "Owner",
      "person": {
        "firstName": "Graham William",
        "lastName": "Kinghorn"
      },
      "postalAddress": {
        "addressLine1": "99 TAYLOR ST",
        "suburb": "Eagle Farm",
        "state": "Queensland",
        "postcode": "4407"
      },
      "phoneNumber": "(07) 3714 9812"
    }
  ]
}
```

### Property Occupancy

```
GET /property-details/au/properties/{propertyId}/occupancy
```

Obtain information on the occupancy type of a single property.

**Response Example:**
```json
{
  "occupancyType": "Owner Occupied",
  "confidenceScore": "Medium",
  "isActiveProperty": true
}
```

### Development Applications

```
GET /property-details/au/properties/{propertyId}/developmentApplication
```

Returns the development permits available on the target property. *This data does not exist for Australian properties in NT & ACT and all New Zealand properties.*

**Response Example:**
```json
{
  "developmentApplications": [
    {
      "approvingAuthority": "PORT ADELAIDE ENFIELD",
      "buildValue": 280000,
      "buildArea": 995,
      "wallMaterial": "Brick",
      "roofMaterial": "Metal",
      "constructionType": "2 Dwellings",
      "developmentApplicationType": "Multi Dwelling/Flats",
      "permitNumber": "2807",
      "permitIssueDate": "2011-10-31"
    }
  ]
}
```

### Property Location

```
GET /property-details/au/properties/{propertyId}/location
```

Obtain detailed information about the location of a property including address, coordinates and external references.

**Response Example:**
```json
{
  "singleLine": "1A-1B Alexandra Street Kurri Kurri NSW 2327",
  "buildingComplexName": "CAPRI VILLAS",
  "councilArea": "Cessnock",
  "state": "NSW",
  "street": {
    "id": 226126,
    "name": "ALEXANDRA",
    "extension": "STREET"
  },
  "postcode": {
    "id": 102255,
    "name": "2327"
  },
  "locality": {
    "id": 12397,
    "name": "KURRI KURRI"
  },
  "longitude": 151.47887047,
  "latitude": -32.82469012
}
```

### Property Images

```
GET /property-details/au/properties/{propertyId}/images
GET /property-details/au/properties/{propertyId}/images/default
```

Obtain all image URLs or just the default image of a single property.

**Response Example:**
```json
{
  "defaultImage": {
    "digitalAssetType": "Image",
    "basePhotoUrl": "https://images.corelogic.asia/0x0/assets/perm/...",
    "largePhotoUrl": "https://images.corelogic.asia/768x512/...",
    "mediumPhotoUrl": "https://images.corelogic.asia/470x313/...",
    "thumbnailPhotoUrl": "https://images.corelogic.asia/320x215/...",
    "scanDate": "2021-06-03"
  },
  "secondaryImageList": [...],
  "floorPlanImageList": [...]
}
```

### Property Site Information

```
GET /property-details/au/properties/{propertyId}/site
```

Obtain site information on a single property including land use and zoning.

**Response Example:**
```json
{
  "landUsePrimary": "Single Unit Dwelling",
  "landUseSecondary": "None",
  "zoneCodeLocal": "SD",
  "zoneDescriptionLocal": "RESIDENTIAL A",
  "siteValueList": [
    {
      "date": "2020-06-30",
      "type": "SV",
      "value": 265000,
      "assessmentDate": "2020-04-26"
    }
  ]
}
```

### Property Attributes

#### Core Attributes

```
GET /property-details/au/properties/{propertyId}/attributes/core
```

Obtain the list of core attributes of a single property.

**Response Example:**
```json
{
  "propertyType": "RESIDENTIAL",
  "propertySubType": "Residential: Dwelling",
  "beds": 2,
  "baths": 4,
  "carSpaces": 3,
  "lockUpGarages": 2,
  "landArea": 324,
  "isCalculatedLandArea": false
}
```

#### Additional Attributes

```
GET /property-details/au/properties/{propertyId}/attributes/additional
```

Obtain the list of additional attributes of a single property.

**Response Example:**
```json
{
  "airConditioned": true,
  "airConditioningFeatures": "Split System",
  "ductedHeating": false,
  "ensuite": 1,
  "fireplace": false,
  "floorArea": 198,
  "pool": false,
  "roofMaterial": "Colorbond",
  "wallMaterial": "Brick",
  "yearBuilt": "2022"
}
```

### Property Features

```
GET /property-details/au/properties/{propertyId}/features
```

Obtain a full list of attributes and features for a single property.

**Response Example:**
```json
{
  "features": "Fenced",
  "featureAttributes": [
    {
      "name": "Materials in Floor",
      "value": "Tiled Floor",
      "type": "String"
    }
  ]
}
```

## Property Sales Services

### All Property Sales

```
GET /property-details/au/properties/{propertyId}/sales
```

Obtain detailed information on the current ownership and sales history of a single property.

**Response Example:**
```json
{
  "currentOwnershipList": [
    {
      "person": {
        "firstName": "Graham William",
        "lastName": "Kinghorn"
      },
      "mailingAddress": {
        "line1": "1 BIRKENHEAD CRES",
        "suburb": "Eagle Farm",
        "state": "QLD",
        "postcode": "4078"
      }
    }
  ],
  "saleList": [
    {
      "agencyName": "RE/MAX Community Realty",
      "agentName": "Scott Moore",
      "contractDate": "2006-07-02",
      "price": 239000,
      "settlementDate": "2006-07-31",
      "type": "Normal Sale",
      "saleMethod": "Normal Sale",
      "saleClassification": "Freehold market level"
    }
  ]
}
```

### Last Property Sale

```
GET /property-details/au/properties/{propertyId}/sales/last
```

Obtain detailed information about the last sale on the target property.

**Response Example:**
```json
{
  "currentOwnershipList": [...],
  "lastSale": {
    "agencyName": "RE/MAX Community Realty",
    "contractDate": "2006-07-02",
    "price": 239000,
    "settlementDate": "2006-07-31",
    "type": "Normal Sale"
  }
}
```

## Ownership Verification

### Ownership Verification Service

```
POST /verification/ownership
```

Utilizes name matching techniques to match name inputs with current owner details. Service coverage is limited to AU properties in QLD, NSW and WA.

**Request Body:**
```json
{
  "propertyId": 11517303,
  "firstName": "Fred",
  "middleName": "Percival",
  "lastName": "Smith"
}
```

**Response Example:**
```json
{
  "matchScore": 85,
  "numberOfOwners": 1,
  "recentlyOnMarket": true,
  "advertisementDate": "2025-08-28",
  "occupancyType": "Owner Occupied",
  "matchCode": 1,
  "matchCodeDescription": "Exact match found"
}
```

**Match Score:**
- **100** = Exact match
- **Lower scores** = Decline in name match quality

## Error Responses

All endpoints return standard HTTP status codes:

| Status Code | Description |
|-------------|-------------|
| `200` | OK - Request successful |
| `400` | Bad Request - Invalid parameters |
| `401` | Unauthorized - Invalid or expired token |
| `403` | Forbidden - Access denied for service |
| `404` | Not Found - Resource does not exist |
| `429` | Too Many Requests - Rate limit exceeded |
| `500` | Internal Server Error |
| `502` | Bad Gateway - Service unavailable |

**Error Response Format:**
```json
{
  "errors": [
    {
      "key": "string",
      "msg": "string"
    }
  ]
}
```

## Authentication

All endpoints require OAuth2 Bearer token authentication. Some endpoints specifically require tokens generated using the `authorization_code` grant_type.

**Header Format:**
```
Authorization: Bearer {access_token}
```

## Coverage Notes

- **Australia**: Full coverage across all states
- **New Zealand**: Limited coverage for some services
- **Ownership Verification**: QLD, NSW, WA only
- **Development Applications**: Not available for NT, ACT (AU) and all NZ properties
- **Advertisement Descriptions**: Not available for NZ endpoints

---

*© RP Data Pty Limited trading as CoreLogic (ABN 67 087 759 171) and CoreLogic NZ Limited trading as CoreLogic (NZCN 1129102) 2025. All rights reserved.*