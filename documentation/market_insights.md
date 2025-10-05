# CoreLogic Market Insights API

CoreLogic Market Insights API provides comprehensive market data and statistics for Australian and New Zealand property markets.

## Overview

Get data and insights on market characteristics and health by area. Combine individual property-level information with geographic-level information to create overall statistics and insights into the real estate market, for both Australia and New Zealand, on a monthly basis.

**Base URL:** `https://api-sbox.corelogic.asia`

## Key Features

- **Market Statistics**: Time series data for market metrics, geographies, property types or periods
- **Census Data**: Australian Bureau of Statistics (ABS) and Statistics New Zealand data
- **Auction Insights**: Comprehensive auction results and trends
- **Chart Generation**: Visual representations of market data
- **Geographic Analysis**: Multiple location granularity levels

## API Categories

### 1. Auction Services

#### Auction Summaries
- **Endpoint**: `GET /auction/au/summaries/state/{state}`
- **Description**: List of suburbs with auction properties in latest auction week
- **Parameters**: 
  - `state` (required): State identifier
  - `capitalCityOnly` (optional): Limit to capital city only

#### Auction Results
- **Endpoint**: `GET /auction/au/results/state/{state}`
- **Description**: Latest state or capital city auction results
- **Stats Available**: total-scheduled-auctions, total-auction-results, sold-prior-to-auctions, sold-at-auction, sold-after-auction, passed-in, withdrawn, clearance-rate

#### Historical Auction Results
- **Endpoint**: `GET /auction/au/results/state/{state}/search`
- **Parameters**:
  - `fromDate` (required): Start date (YYYY-MM-DD)
  - `toDate` (required): End date (YYYY-MM-DD)
  - Max 1 year date range, max 10 years historical data

#### Auction Comparisons
- **Endpoint**: `GET /auction/au/results/state/{state}/compare/years/{years}`
- **Description**: Compare latest results with same week n years ago
- **Parameters**: `years` (2-10): Number of years to compare

#### Auction Details
- **Endpoint**: `GET /auction/au/details/state/{state}/postcode/{postcode}/suburb/{suburb}`
- **Description**: Detailed auction property information for specific suburb

### 2. Census Services

#### Census Statistics
- **Endpoint**: `POST /census/v1/geographic`
- **Description**: Population and housing statistical breakdowns from latest census
- **Data Sources**: Australian Bureau of Statistics (ABS)
- **Parameters**:
  - `forLatestCensusYear` (default: true): Use most recent census data
  - Request body with location and metric specifications

#### Census Summary
- **Endpoint**: `GET /census/v1/geographic/summary`
- **Description**: Locality summary using latest census data
- **Parameters**:
  - `locationId` (required): Location identifier
  - `locationTypeId` (required): Location type (2=Country, 3=Council Area, 4=Postcode, 7=State, 8=Locality, 9=Territorial Authority NZ)

### 3. Statistics Services

#### Time Series Statistics
- **Endpoint**: `POST /statistics/v1/statistics.json`
- **Description**: Time series data for multiple metrics, geographies, property types
- **Request Body**: Array of series requests with location, metric, and date parameters

### 4. Charts Services

#### Census Charts
- **Endpoint**: `GET /charts/census`
- **Description**: Chart images for census statistical breakdowns
- **Parameters**:
  - `chartSize` (required): Format {height}x{width} (e.g., 400x700)
  - `metricTypeGroupId` (required): Metric type group
  - Chart types: 1=spline, 2=line, 3=column, 4=area, 5=pie, 6=bar

#### Time Series Charts
- **Endpoint**: `GET /charts/v2/chart.png`
- **Description**: Chart images for time series data
- **Parameters**:
  - `chartSize` (required): Chart dimensions
  - `scale` (optional): Image quality scale (0-5)
  - `fromDate`/`toDate`: Date range
  - Series parameters (s1.lId, s1.lTId, s1.pTId, s1.mTId, etc.)

## Location Types

| ID | Type |
|----|------|
| 2 | Country |
| 3 | Council Area |
| 4 | Postcode |
| 7 | State |
| 8 | Locality |
| 9 | Territorial Authority (NZ Only) |

## Property Types

| ID | Type |
|----|------|
| 1 | Houses |
| 2 | Units |
| 3 | Land |
| 4 | Apartments |
| 5 | Flats |
| 6 | Residential dwellings (Houses, Apartments, Flats) |

## Authentication

- **OAuth2**: Client credentials flow
- **Authorization Code**: Required for some services (auction endpoints)
- **Rate Limiting**: API Gateway limits apply - use backoff strategies

## Response Formats

- **JSON**: Primary response format
- **PNG**: Chart/image responses
- **Error Handling**: Standardized error messages with trace IDs for investigation

## Common Response Codes

- **200**: Success
- **400**: Bad Request - Invalid parameters
- **401**: Unauthorized - Invalid/expired token
- **403**: Forbidden - Insufficient permissions
- **404**: Not Found - Unknown location/no data
- **429**: Rate limit exceeded
- **500**: Internal Server Error
- **503**: Service Unavailable

## Response Schemas

### Auction Results Response
```json
{
  "auctionResults": {
    "totalScheduledAuctions": 245,
    "totalAuctionResults": 198,
    "soldPriorToAuctions": 15,
    "soldAtAuction": 125,
    "soldAfterAuction": 8,
    "passedIn": 45,
    "withdrawn": 5,
    "clearanceRate": 75.25,
    "reportingPeriod": {
      "fromDate": "2023-08-12",
      "toDate": "2023-08-19"
    },
    "location": {
      "state": "NSW",
      "capitalCityOnly": true
    }
  },
  "historicalComparison": {
    "previousWeek": {
      "clearanceRate": 72.8,
      "changePercent": 3.36
    },
    "sameWeekLastYear": {
      "clearanceRate": 68.5,
      "changePercent": 9.85
    }
  }
}
```

### Auction Details Response
```json
{
  "auctionDetails": [
    {
      "propertyId": 12345678,
      "address": "123 Main Street, Sydney NSW 2000",
      "auctionDate": "2023-08-19",
      "auctionTime": "11:00 AM",
      "result": "SOLD_AT_AUCTION",
      "soldPrice": 875000,
      "reservePrice": 820000,
      "bidderCount": 8,
      "agency": {
        "name": "ABC Real Estate",
        "phone": "02 9876 5432"
      },
      "agent": {
        "name": "John Smith",
        "phone": "0412 345 678"
      },
      "propertyDetails": {
        "propertyType": "House",
        "beds": 3,
        "baths": 2,
        "carSpaces": 1,
        "landArea": 650
      }
    }
  ],
  "summary": {
    "totalProperties": 15,
    "averageSoldPrice": 825000,
    "medianSoldPrice": 780000,
    "priceRange": {
      "minimum": 650000,
      "maximum": 1200000
    }
  }
}
```

### Census Statistics Response
```json
{
  "censusData": {
    "locationInfo": {
      "locationId": 12345,
      "locationName": "Sydney",
      "locationType": "Locality",
      "censusYear": 2021
    },
    "demographics": {
      "population": {
        "totalPersons": 5312163,
        "males": 2605330,
        "females": 2706833,
        "medianAge": 37
      },
      "households": {
        "totalHouseholds": 2048609,
        "averageHouseholdSize": 2.6,
        "familyHouseholds": 1445821,
        "nonFamilyHouseholds": 602788
      },
      "housing": {
        "totalDwellings": 2192496,
        "occupiedDwellings": 2048609,
        "vacantDwellings": 143887,
        "medianRent": 450,
        "medianMortgage": 2167
      }
    },
    "economics": {
      "medianHouseholdIncome": 91000,
      "medianIndividualIncome": 49000,
      "unemploymentRate": 4.2,
      "labourForceParticipation": 65.8
    },
    "education": {
      "bachelorDegreeOrHigher": 42.5,
      "vocationalQualification": 18.3,
      "noQualification": 15.2
    }
  }
}
```

### Time Series Statistics Response
```json
{
  "timeSeries": {
    "metadata": {
      "locationId": 12345,
      "locationName": "Sydney",
      "metricType": "MEDIAN_SALE_PRICE",
      "propertyType": "HOUSES",
      "frequency": "MONTHLY",
      "dateRange": {
        "fromDate": "2022-01-01",
        "toDate": "2023-08-31"
      }
    },
    "dataPoints": [
      {
        "date": "2023-08-01",
        "value": 1250000,
        "salesVolume": 156,
        "daysOnMarket": 28,
        "vendorDiscount": -2.1,
        "changeFromPreviousPeriod": {
          "absolute": 15000,
          "percentage": 1.2
        }
      },
      {
        "date": "2023-07-01",
        "value": 1235000,
        "salesVolume": 142,
        "daysOnMarket": 31,
        "vendorDiscount": -1.8,
        "changeFromPreviousPeriod": {
          "absolute": -8000,
          "percentage": -0.6
        }
      }
    ],
    "summary": {
      "currentValue": 1250000,
      "yearToDateChange": {
        "absolute": 85000,
        "percentage": 7.3
      },
      "twelveMonthChange": {
        "absolute": 125000,
        "percentage": 11.1
      },
      "peakValue": {
        "value": 1285000,
        "date": "2023-03-01"
      },
      "troughValue": {
        "value": 1125000,
        "date": "2022-09-01"
      }
    }
  }
}
```

### Chart Generation Response
```json
{
  "chartInfo": {
    "chartType": "TIME_SERIES_LINE",
    "title": "Median House Prices - Sydney",
    "chartSize": "800x600",
    "dateRange": "Jan 2022 - Aug 2023",
    "imageUrl": "https://charts.corelogic.asia/images/ts_12345_houses_monthly.png",
    "metadata": {
      "generatedAt": "2023-08-27T10:30:00Z",
      "expiresAt": "2023-08-27T22:30:00Z",
      "format": "PNG",
      "watermarked": true
    }
  },
  "chartData": {
    "series": [
      {
        "name": "Median Sale Price",
        "color": "#1f77b4",
        "dataPoints": 20
      }
    ],
    "yAxis": {
      "title": "Price ($)",
      "minimum": 1100000,
      "maximum": 1300000
    },
    "xAxis": {
      "title": "Month",
      "labels": ["Jan 2022", "Feb 2022", "..."]
    }
  }
}
```

## Example Use Cases

1. **Market Analysis**: Get median prices and sales volumes for specific suburbs
2. **Auction Monitoring**: Track auction clearance rates and results across states
3. **Demographic Research**: Access census data for location-based insights
4. **Trend Visualization**: Generate charts showing market performance over time
5. **Comparative Analysis**: Compare market metrics across different time periods

## Data Limitations

- **Date Ranges**: Historical data limited to 10 years
- **Query Limits**: Maximum 1 year range for historical searches
- **Geographic Scope**: Australia and New Zealand coverage
- **Update Frequency**: Monthly snapshots for market data, census data by census periods

---

*© RP Data Pty Limited trading as Cotality (ABN 67 087 759 171) and CoreLogic NZ Limited trading as Cotality (NZCN 1129102) 2025. All rights reserved.*