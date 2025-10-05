# CoreLogic Property Bureau API

The Property Bureau API provides comprehensive property-level data for risk management and strategy optimization in lending applications.

## Overview

The Property Bureau may be used by lenders to manage their upfront valuation risk and strategy optimization based on property, building, location, environmental and financial factors.

The Property Bureau provides a single dwelling level record of everything known about a property. The record is unique to each customer and built from multiple data sources, including:

- CoreLogic property attributes
- Historical valuation data (customer-specific initially, potentially shared in future)
- CoreLogic market insights
- Client-specific data

**Base URL:** `https://api-sbox.corelogic.asia`

## Authentication

- **OAuth2 Bearer Token** required
- **Account-Number Header** optional for account-specific data

## Endpoints

### Get Property Bureau Data

```
GET /propertybureau/property/{propertyId}
```

Retrieve comprehensive property information for a specific property.

#### Parameters

| Parameter | Type | Location | Required | Description | Example |
|-----------|------|----------|----------|-------------|---------|
| `propertyId` | integer | path | Yes | Unique CoreLogic identifier for the target property | 41418296 |
| `Account-Number` | string | header | No | Account-Number for customer-specific data | - |

#### Complete Response Example

```json
{
  "address": {
    "propertyId": 41418296,
    "singleLineAddress": "123 Example St West End QLD 4101"
  },
  "attributes": {
    "bathrooms": 2,
    "bedrooms": 3,
    "carSpaces": 1,
    "landArea": 650,
    "livingArea": 180,
    "yearBuilt": "2004",
    "propertyType": "HOUSE",
    "propertySubTypeShort": "detached"
  },
  "corelogicAVM": {
    "estimate": 850000,
    "fsd": 125000,
    "lowEstimate": 725000,
    "highEstimate": 975000,
    "confidence": "MEDIUM",
    "valuationDate": "2023-08-25"
  },
  "consumerAVM": {
    "estimate": 825000,
    "lowEstimate": 750000,
    "highEstimate": 900000,
    "confidence": "MEDIUM",
    "valuationDate": "2023-08-25"
  },
  "rentalAVM": {
    "rentalAvmDetail": {
      "comparableProperties": [
        "41418297",
        "41418298",
        "41418299"
      ],
      "rentalAvmEstimate": 580,
      "rentalAvmEstimateFsdScore": 75,
      "rentalAvmEstimateHigh": 650,
      "rentalAvmEstimateLow": 510,
      "rentalAvmPeriod": "WEEKLY",
      "rentalAvmRunDate": "2023-08-25",
      "rentalAvmScore": 82,
      "rentalAvmValuationDate": "2023-08-25",
      "rentalAvmYield": 3.52,
      "rentalAvmYieldFsdScore": 68
    },
    "messages": [
      {
        "message": "Rental estimate based on 3 comparable properties within 500m"
      }
    ]
  },
  "previousSales": {
    "totalNumberOfTransaction": 2,
    "salesList": [
      {
        "saleDate": "2021-03-15",
        "saleAmount": 750000,
        "agencyName": "ABC Real Estate"
      },
      {
        "saleDate": "2018-09-08",
        "saleAmount": 620000,
        "agencyName": "XYZ Properties"
      }
    ]
  },
  "onTheMarket": {
    "propertyOnMarket": false,
    "daysOnMarket": 0,
    "agencyName": null
  },
  "developmentApplication": [
    {
      "daApprovalHeld": "APPROVED",
      "permitIssueDate": "2023-02-15"
    }
  ],
  "propertyDensity": {
    "numberOfDwellings": 1
  },
  "previousValuations": {
    "valuation_001": {
      "property_id": "41418296",
      "job_id": "JOB_2023_001",
      "valuation_date": "2023-01-15",
      "valuation_type": "PURCHASE"
    },
    "valuation_002": {
      "property_id": "41418296",
      "job_id": "JOB_2022_045",
      "valuation_date": "2022-06-20",
      "valuation_type": "REFINANCE"
    }
  },
  "concentration": {
    "building": {
      "ratio": 0.15
    },
    "suburb": {
      "ratio": 0.08
    },
    "postcode": {
      "ratio": 0.03
    }
  },
  "climateHazards": {
    "climateRiskScores": [
      {
        "fact": "HAZARD_FLOOD",
        "rating": "MEDIUM"
      },
      {
        "fact": "HAZARD_BUSHFIRE",
        "rating": "LOW"
      },
      {
        "fact": "HAZARD_EARTHQUAKE",
        "rating": "LOW"
      }
    ],
    "wildfireHDRiskScores": {
      "riskScore": "MEDIUM",
      "riskIndex": "3.2",
      "positionInClass": "15th percentile"
    }
  },
  "propertyRegister": {
    "totalNumberOfFacts": 5,
    "facts": [
      {
        "fact": "HERITAGE_LISTED",
        "rating": "NO"
      },
      {
        "fact": "CONTAMINATED_LAND",
        "rating": "NO"
      },
      {
        "fact": "FLOOD_AFFECTED",
        "rating": "MINOR"
      },
      {
        "fact": "BUSHFIRE_PRONE",
        "rating": "NO"
      },
      {
        "fact": "NOISE_AFFECTED",
        "rating": "MODERATE"
      }
    ]
  },
  "dataBlocks": {
    "marketInsights": {
      "medianSalePrice": 825000,
      "medianDaysOnMarket": 28,
      "salesVolume": 156
    },
    "locationAnalysis": {
      "walkScore": 75,
      "schoolRating": "B+",
      "transportAccess": "EXCELLENT"
    },
    "investmentMetrics": {
      "capitalGrowthRate": 8.2,
      "rentalYield": 3.5,
      "vacancyRate": 1.8
    }
  }
}
```

#### Response Schema

The API returns a comprehensive property record with the following sections:

##### Address Information
```json
{
  "address": {
    "propertyId": 123456,
    "singleLineAddress": "123 Example St West End QLD 4101"
  }
}
```

##### Property Attributes
```json
{
  "attributes": {
    "bathrooms": 1,
    "bedrooms": 2,
    "carSpaces": 1,
    "landArea": 0,
    "livingArea": 0,
    "yearBuilt": "2004",
    "propertyType": "UNIT",
    "propertySubTypeShort": "standard"
  }
}
```

##### Automated Valuation Models (AVMs)

**CoreLogic AVM**
```json
{
  "corelogicAVM": {
    "estimate": 0,
    "fsd": 0,
    "lowEstimate": 0,
    "highEstimate": 0,
    "confidence": "string",
    "valuationDate": "string"
  }
}
```

**Consumer AVM**
```json
{
  "consumerAVM": {
    "estimate": 0,
    "lowEstimate": 0,
    "highEstimate": 0,
    "confidence": "string",
    "valuationDate": "string"
  }
}
```

**Rental AVM**
```json
{
  "rentalAVM": {
    "rentalAvmDetail": {
      "comparableProperties": ["string"],
      "rentalAvmEstimate": 0,
      "rentalAvmEstimateFsdScore": 0,
      "rentalAvmEstimateHigh": 0,
      "rentalAvmEstimateLow": 0,
      "rentalAvmPeriod": "string",
      "rentalAvmRunDate": "string",
      "rentalAvmScore": 0,
      "rentalAvmValuationDate": "string",
      "rentalAvmYield": 0,
      "rentalAvmYieldFsdScore": 0
    },
    "messages": [
      {
        "message": "string"
      }
    ]
  }
}
```

##### Sales History
```json
{
  "previousSales": {
    "totalNumberOfTransaction": 0,
    "salesList": [
      {
        "saleDate": "string",
        "saleAmount": 0,
        "agencyName": "string"
      }
    ]
  }
}
```

##### Market Status
```json
{
  "onTheMarket": {
    "propertyOnMarket": true,
    "daysOnMarket": 0,
    "agencyName": "string"
  }
}
```

##### Development Information
```json
{
  "developmentApplication": [
    {
      "daApprovalHeld": "string",
      "permitIssueDate": "string"
    }
  ],
  "propertyDensity": {
    "numberOfDwellings": 0
  }
}
```

##### Valuation History
```json
{
  "previousValuations": {
    "additionalProp1": {
      "property_id": "string",
      "job_id": "string",
      "valuation_date": "string",
      "valuation_type": "string"
    }
  }
}
```

##### Risk Assessment

**Concentration Risk**
```json
{
  "concentration": {
    "building": {
      "ratio": 0
    },
    "suburb": {
      "ratio": 0
    },
    "postcode": {
      "ratio": 0
    }
  }
}
```

**Climate Hazards**
```json
{
  "climateHazards": {
    "climateRiskScores": [
      {
        "fact": "HAZARD_EARTHQUAKE",
        "rating": "string"
      }
    ],
    "wildfireHDRiskScores": {
      "riskScore": "string",
      "riskIndex": "string",
      "positionInClass": "string"
    }
  }
}
```

##### Property Register
```json
{
  "propertyRegister": {
    "totalNumberOfFacts": 0,
    "facts": [
      {
        "fact": "string",
        "rating": "string"
      }
    ]
  }
}
```

##### Additional Data Blocks
```json
{
  "dataBlocks": {
    "additionalProp1": {},
    "additionalProp2": {},
    "additionalProp3": {}
  }
}
```

## Response Codes

| Code | Description |
|------|-------------|
| 200 | Success - Property Bureau data returned |
| 400 | Invalid request - Bad property ID or parameters |
| 401 | Authentication failed - Authorization bearer token required |
| 403 | Authorization failed - Insufficient permissions for client |
| 404 | Property not found - Invalid property ID |
| 405 | Method Not Allowed |
| 429 | API Gateway rate limit - Retry with backoff |
| 500 | Internal Server Error |
| 503 | Upstream network error - Retry with backoff |

## Use Cases

### 1. **Lending Risk Assessment**
- Retrieve comprehensive property data for loan applications
- Assess property attributes, valuations, and environmental risks
- Analyze concentration risk across building/suburb/postcode

### 2. **Property Valuation**
- Access multiple AVM estimates (CoreLogic, Consumer, Rental)
- Review historical sales and valuation data
- Compare estimates with confidence intervals

### 3. **Due Diligence**
- Check development applications and approvals
- Review property register facts and ratings
- Assess climate hazards and environmental risks

### 4. **Portfolio Management**
- Monitor properties currently on market
- Track days on market and agency information
- Analyze property density and concentration metrics

## Data Sources

- **Property Attributes**: CoreLogic property database
- **Valuation Data**: Customer-specific historical valuations
- **Market Insights**: CoreLogic market analysis
- **Environmental Data**: Climate hazard assessments
- **Development Data**: Council applications and approvals
- **Sales History**: Property transaction records

## Rate Limiting

- API Gateway limits apply
- Use exponential backoff on 429 responses
- Monitor response headers for rate limit information

## Error Handling

All errors include:
- **Domain**: Error classification
- **Message**: Human-readable error description
- **Code**: Machine-readable error code
- **System Info**: Request date, instance, and trace ID for debugging

---

*© RP Data Pty Limited trading as Cotality (ABN 67 087 759 171) and CoreLogic NZ Limited trading as Cotality (NZCN 1129102) 2025. All rights reserved.*