# CoreLogic Geospatial API

Comprehensive geospatial mapping and analysis services for Australian property and environmental data.

## Overview

The CoreLogic Geospatial API provides access to extensive mapping data, spatial analysis capabilities, and geographic information across Australia. Built on ArcGIS Enterprise infrastructure with 99.9% uptime availability.

**Base URLs:**
- **UAT**: `https://api-uat.corelogic.asia`
- **Production**: `https://api.corelogic.asia`

## Authentication

### Token Request
All service requests require a token for authorization:

**UAT Token Endpoint:**
```bash
https://access-uat-api.corelogic.asia/access/oauth/token?grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}
```

**Production Token Endpoint:**
```bash
https://access-api.corelogic.asia/access/oauth/token?grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}
```

### Token Response Example
```json
{
  "access_token": "access_token_here",
  "token_type": "bearer",
  "expires_in": 43199,
  "scope": "CRT MAP PTY SGT STS TTL",
  "iss": "https://access-api.corelogic.asia",
  "env_access_restrict": true,
  "geo_codes": [
    "ACT - Full State",
    "NSW - Metro",
    "NSW - Regional",
    "NT - Full State",
    "QLD - Metro",
    "QLD - Regional",
    "SA - Metro", 
    "SA - Regional",
    "TAS - Full State",
    "VIC - Full State",
    "VIC - Metro",
    "VIC - Regional",
    "WA - Metro",
    "WA - Regional",
    "North Island",
    "South Island"
  ],
  "roles": [],
  "source_exclusion": []
}
```

## Core Capabilities

### 1. Export Map (Image Generation)

Generate map images from geospatial layers with customizable parameters.

#### Required Parameters
| Parameter | Description | Example |
|-----------|-------------|---------|
| `bbox` | Bounding box coordinates (xmin,ymin,xmax,ymax) | `1.681E7,-3990918.3,1.681E7,-3990766.4` |
| `format` | Image format (png32 recommended for contours) | `png32`, `jpg`, `pdf`, `svg` |
| `f` | Response format for map requests | `image` |

#### Optional Parameters
| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `size` | Image dimensions (width,height) | 400x400 | `600,550` |
| `dpi` | Dots per inch resolution | 96 | `96` |
| `bboxSR` | Spatial reference system | Map SR | `4326` (WGS84) |
| `layerDefs` | Layer definition filters | None | `0:property_id=1784824` |
| `transparent` | Transparent background | false | `true`, `false` |

#### Export Map Examples

**Basic Property Boundaries:**
```
https://api-uat.corelogic.asia/geospatial/au/overlays/propertyOverlay/propertyAll?bbox=17052291.478188463%2C-3208875.9602157352%2C17052655.748401336%2C-3208633.511516675&format=png32&transparent=true&size=455%2C406&dpi=96&f=image&access_token={token}
```

**Filtered Property Selection:**
```
https://api-uat.corelogic.asia/geospatial/au/overlays/propertyOverlay/propertySelect?layerDefs=0:property_id=15960119&bbox=17052291.478188463%2C-3208875.9602157352%2C17052655.748401336%2C-3208633.511516675&format=png32&transparent=true&size=455%2C406&dpi=96&f=image&access_token={token}
```

### 2. Spatial Query (Feature Data)

Query geospatial layers for feature data with spatial and attribute filters.

#### Query Parameters
| Parameter | Required | Description | Options |
|-----------|----------|-------------|---------|
| `f` | Yes | Response format | `json`, `html` |
| `where` | Yes | SQL WHERE clause | `1=1`, `property_id=1778890` |
| `geometry` | No | Spatial filter geometry | Geometry JSON or simple syntax |
| `geometryType` | No | Type of geometry filter | `esriGeometryEnvelope`, `esriGeometryPoint` |
| `spatialRel` | No | Spatial relationship | `esriSpatialRelIntersects` (default) |
| `outFields` | No | Fields to return | `*` (all fields) |
| `returnGeometry` | No | Include geometry in results | `true` (default) |
| `resultRecordCount` | No | Limit result count | No limit (default) |

#### Query Example
```
https://api-uat.corelogic.asia/geospatial/au/nsw/planningAggregations/electricTransmissionLines?where=property_id=1778890&outFields=*&returnGeometry=false&returnDistinctValues=true&f=json&access_token={token}
```

#### Query Response Example
```json
{
  "displayFieldName": "name",
  "fieldAliases": {
    "objectid": "objectid",
    "property_id": "property_id",
    "parcel_id": "parcel_id",
    "jurisdiction_id": "jurisdiction_id",
    "predicate": "predicate",
    "distance": "distance",
    "featuretype": "featuretype",
    "description": "description",
    "class": "class",
    "esridb.sde.nsw_pa_et_lines.fid": "esridb.sde.nsw_pa_et_lines.fid",
    "name": "name",
    "operationalstatus": "operationalstatus",
    "capacitykv": "capacitykv",
    "state": "state",
    "spatialconfidence": "spatialconfidence",
    "revised": "revised"
  },
  "fields": [
    {
      "name": "objectid",
      "type": "esriFieldTypeOID",
      "alias": "objectid"
    },
    {
      "name": "property_id",
      "type": "esriFieldTypeInteger",
      "alias": "property_id"
    },
    {
      "name": "parcel_id",
      "type": "esriFieldTypeInteger",
      "alias": "parcel_id"
    },
    {
      "name": "jurisdiction_id",
      "type": "esriFieldTypeString",
      "alias": "jurisdiction_id",
      "length": 50
    },
    {
      "name": "predicate",
      "type": "esriFieldTypeString",
      "alias": "predicate",
      "length": 15
    },
    {
      "name": "distance",
      "type": "esriFieldTypeSingle",
      "alias": "distance"
    },
    {
      "name": "featuretype",
      "type": "esriFieldTypeString",
      "alias": "featuretype",
      "length": 20
    },
    {
      "name": "description",
      "type": "esriFieldTypeString",
      "alias": "description",
      "length": 200
    },
    {
      "name": "class",
      "type": "esriFieldTypeString",
      "alias": "class",
      "length": 20
    },
    {
      "name": "esridb.sde.nsw_pa_et_lines.fid",
      "type": "esriFieldTypeDouble",
      "alias": "esridb.sde.nsw_pa_et_lines.fid"
    },
    {
      "name": "name",
      "type": "esriFieldTypeString",
      "alias": "name",
      "length": 100
    },
    {
      "name": "operationalstatus",
      "type": "esriFieldTypeString",
      "alias": "operationalstatus",
      "length": 20
    },
    {
      "name": "capacitykv",
      "type": "esriFieldTypeDouble",
      "alias": "capacitykv"
    },
    {
      "name": "state",
      "type": "esriFieldTypeString",
      "alias": "state",
      "length": 30
    },
    {
      "name": "spatialconfidence",
      "type": "esriFieldTypeDouble",
      "alias": "spatialconfidence"
    },
    {
      "name": "revised",
      "type": "esriFieldTypeDate",
      "alias": "revised",
      "length": 8
    }
  ],
  "features": [
    {
      "attributes": {
        "objectid": 69839,
        "property_id": 1778890,
        "parcel_id": 4467635,
        "jurisdiction_id": "22/SP14483",
        "predicate": "intersecting",
        "distance": 0,
        "featuretype": "Transmission Line",
        "description": "A network of wires and insulators used to connect and transport high voltage electricity from generators to large demand customers and the lower voltage electricity distribution network",
        "class": "Overhead",
        "esridb.sde.nsw_pa_et_lines.fid": 2325,
        "name": "Carlingford to Castle Hill",
        "operationalstatus": "Operational",
        "capacitykv": 66,
        "state": "New South Wales",
        "spatialconfidence": 4,
        "revised": 1481587200000
      }
    },
    {
      "attributes": {
        "objectid": 69840,
        "property_id": 1778890,
        "parcel_id": 4467635,
        "jurisdiction_id": "22/SP14483",
        "predicate": "intersecting",
        "distance": 0,
        "featuretype": "Transmission Line",
        "description": "A network of wires and insulators used to connect and transport high voltage electricity from generators to large demand customers and the lower voltage electricity distribution network",
        "class": "Overhead",
        "esridb.sde.nsw_pa_et_lines.fid": 2326,
        "name": "West Pennant Hills to Castle Hill",
        "operationalstatus": "Operational",
        "capacitykv": 66,
        "state": "New South Wales",
        "spatialconfidence": 4,
        "revised": 1481587200000
      }
    },
    {
      "attributes": {
        "objectid": 69841,
        "property_id": 1778890,
        "parcel_id": 4467635,
        "jurisdiction_id": "22/SP14483",
        "predicate": "intersecting",
        "distance": 0,
        "featuretype": "Transmission Line",
        "description": "A network of wires and insulators used to connect and transport high voltage electricity from generators to large demand customers and the lower voltage electricity distribution network",
        "class": "Overhead",
        "esridb.sde.nsw_pa_et_lines.fid": 2327,
        "name": "West Pennant Hills to Kenthurst",
        "operationalstatus": "Operational",
        "capacitykv": 66,
        "state": "New South Wales",
        "spatialconfidence": 4,
        "revised": 1481587200000
      }
    }
  ],
  "exceededTransferLimit": false,
  "geometryType": "esriGeometryPolyline",
  "spatialReference": {
    "wkid": 4326,
    "latestWkid": 4326
  }
}
```

### 3. Layer Information

Retrieve metadata and configuration details for geospatial layers.

#### Layer Info Example
```
https://api-uat.corelogic.asia/geospatial/au/info/propertyOverlay/propertyAll?access_token={token}
```

#### Layer Info Response Example
```
Layer: propertyAll (ID: 1)

Name: propertyAll

Display Field: property_id

Type: Feature Layer

Geometry Type: esriGeometryPolygon

Description:

Copyright Text:

Default Visibility: false

MaxRecordCount: 2000

Supported Query Formats: JSON, geoJSON, PBF

Min Scale: 9244648.868618

Max Scale: 0

Supports Advanced Queries: true

Supports Statistics: true

Has Labels: false

Can Modify Layer: true

Can Scale Symbols: false

Use Standardized Queries: true

Supports Datum Transformation: true

Extent:
XMin: 1.07775987811E7
YMin: -5401090.8442
XMax: 1.71029965192E7
YMax: -1022023.2589999996

Spatial Reference: 102100 (3857)
```

## API Categories

### 1. Archistar Services

#### Spatial Hazards
| Service | Capabilities | Base URL |
|---------|-------------|----------|
| **Bushfire** | Export Map, Query, Info | `/geospatial/au/overlays/bushfire` |
| **Flood** | Export Map, Query, Info | `/geospatial/au/overlays/flood` |
| **Heritage** | Export Map, Query, Info | `/geospatial/au/overlays/heritage` |

#### Planning Aggregation Tables
| Service | Capability | Endpoint |
|---------|------------|----------|
| Archistar Planning Overlay | Query | `/geospatial/au/overlays/archistarPlanningOverlay` |
| Archistar Planning Parcel | Query | `/geospatial/au/overlays/archistarPlanningParcel` |
| Archistar Planning Use | Query | `/geospatial/au/overlays/archistarPlanningUse` |
| Archistar Zoning | Query | `/geospatial/au/overlays/archistarZoning` |

### 2. Property Services

#### Property Boundaries
| Service | Capabilities | Endpoint |
|---------|-------------|----------|
| **Property All** | Export Map, Query, Info | `/geospatial/au/overlays/propertyOverlay/propertyAll` |
| **Property Select** | Export Map | `/geospatial/au/overlays/propertyOverlay/propertySelect` |

#### Property Information Labels
| Service | Capabilities | Endpoint |
|---------|-------------|----------|
| Address (Street Designator) | Export Map, Query, Info | `/geospatial/au/overlays/propertyLabels/address` |
| Bed Bath Car | Export Map, Query, Info | `/geospatial/au/overlays/propertyLabels/bedBathAndCar` |
| Land Area | Export Map, Query, Info | `/geospatial/au/overlays/propertyLabels/landSize` |
| Last Sale Summary | Export Map, Query, Info | `/geospatial/au/overlays/propertyLabels/lastSaleSummary` |
| Primary Land Use | Export Map, Query, Info | `/geospatial/au/overlays/propertyLabels/primaryLandUse` |
| Property Ownership | Export Map, Query, Info | `/geospatial/au/geometry/parcelLabels/lotOwnership` |

#### Property Dimensions
| Service | Capabilities | Endpoint |
|---------|-------------|----------|
| Dimensions | Export Map, Query, Info | `/geospatial/au/overlays/dimensions/legalLines` |
| Target Property Dimensions | Export Map | `/geospatial/au/overlays/dimensions/legalLines` |

### 3. Boundaries & Administrative

#### Boundaries
| Service | Capabilities | Endpoint |
|---------|-------------|----------|
| **LGA Boundaries** | Export Map, Query, Info | `/geospatial/au/overlays/lga` |
| **Suburb Boundaries** | Export Map, Query, Info | `/geospatial/au/overlays/locality` |

#### Parcel Services
| Service | Capabilities | Endpoint |
|---------|-------------|----------|
| Parcel All | Export Map, Query, Info | `/geospatial/au/overlays/parcelOverlay/parcelAll` |
| Parcel Select | Export Map, Query, Info | `/geospatial/au/overlays/parcelOverlay/parcelSelect` |
| Lot Area Labels | Export Map, Query, Info | `/geospatial/au/overlays/parcelLabels/lotArea` |
| Lot Plan Labels | Export Map, Query, Info | `/geospatial/au/overlays/parcelLabels/lotPlan` |

### 4. Infrastructure & Utilities

#### Electricity Services
| Service | Coverage | Capabilities |
|---------|----------|-------------|
| **Transmission Lines** | Nationwide | Export Map, Query, Info |
| **Power Stations** | Nationwide | Export Map, Query, Info |
| **Substations** | Nationwide | Export Map, Query, Info |
| **50m Buffer Zones** | All electricity services | Export Map, Query, Info |

**State-Level Planning Aggregations Available for:**
- ACT, NSW, NT, QLD, SA, TAS, VIC, WA

#### Transportation
| Service | Capabilities | Endpoint |
|---------|-------------|----------|
| Streets | Export Map | `/geospatial/au/overlays/streets` |
| Railway | Export Map | `/geospatial/au/overlays/railway` |
| Railway Stations | Export Map | `/geospatial/au/overlays/railwayStations` |
| Ferry | Export Map | `/geospatial/au/overlays/ferry` |

### 5. Environmental Services

#### Hazard & Environmental Data
| Category | Services | State Coverage |
|----------|----------|----------------|
| **Native Vegetation** | Export Map, Query, Info | All states + territories |
| **Regulated Vegetation** | Export Map, Query, Info | NSW, QLD, VIC, WA |
| **Land Use** | Export Map, Query | All states + territories |
| **Easements** | Export Map, Query, Info | All states + territories |

#### State-Specific Environmental Services

**Queensland:**
- Property Map of Assessable Vegetation (PMAV)
- Grazing Land Management Types

**Victoria:**
- Environmental Significance Overlay (ESO)
- Significant Landscape Overlay (SLO) 
- Vegetation Protection Overlay (VPO)
- Bushfire Management Overlay (BMO)
- Erosion Management Overlay (EMO)
- Irrigation Districts
- Dryland Salinity Discharge Areas
- Floodway

**Western Australia:**
- Pre-European Vegetation (Super Groups)

### 6. Physical Geography

#### Topographic Services
| Service | Capabilities | Endpoint |
|---------|-------------|----------|
| Landform | Export Map | `/geospatial/au/overlays/landform` |
| Spot Heights | Export Map | `/geospatial/au/overlays/spotElevations` |
| Surface Water | Export Map | `/geospatial/au/overlays/surfacewater` |
| Drainage Lines | Export Map | `/geospatial/au/overlays/drainageLine` |
| Drainage Polygon | Export Map | `/geospatial/au/overlays/drainagePolygon` |
| Contours | Export Map, Info | `/geospatial/au/overlays/contours` |

#### Water Features (State-Level)
| State | Services | Capabilities |
|-------|----------|-------------|
| **QLD** | Water Bores | Export Map, Query, Info |
| **SA** | Water Main | Export Map, Query, Info |
| **WA** | Water Meter, Harvey Water Pipelines, Water Pipe | Export Map, Query, Info |

#### Soil Data (State-Level)
| State | Services | Capabilities |
|-------|----------|-------------|
| **SA** | Soil Subgroup | Export Map, Query, Info |
| **WA** | Soil Sites, Soil Landscape | Export Map, Query, Info |

### 7. Climate & Weather

#### Rainfall Services
| Service | Coverage | Capabilities |
|---------|----------|-------------|
| Rainfall | Nationwide | Export Map |
| Rainfall No Labels | Nationwide | Export Map |
| Planning Aggregations | All states + territories | Query |

### 8. Sales & Listings

#### Sales Overlays
| Service | Time Period | Endpoint |
|---------|------------|----------|
| Sold Last 6 Months | 0-6 months | `/geospatial/au/overlays/sales/soldLastSixMonths` |
| Sold Last 6-12 Months | 6-12 months | `/geospatial/au/overlays/sales/soldLastSixTwelveMonths` |
| Sold Last 12-24 Months | 12-24 months | `/geospatial/au/overlays/sales/soldLastTwelveTwentyFourMonths` |
| Sold Last 24-36 Months | 24-36 months | `/geospatial/au/overlays/sales/soldLastTwentyFourThirtySixMonths` |
| Multiple Sales Last 3 Years | 3 years | `/geospatial/au/overlays/sales/multipleSalesLastThreeYears` |

#### Current Listings
| Service | Endpoint |
|---------|----------|
| Sale Listings | `/geospatial/au/overlays/listings/sale` |
| Rental Listings | `/geospatial/au/overlays/listings/rental` |

### 9. Points of Interest

#### POI Services
| Service | Capabilities | Endpoint |
|---------|-------------|----------|
| Points of Interest | Export Map | `/geospatial/au/overlays/poi/pointOfInterests` |
| Homesteads | Export Map, Query, Info | `/geospatial/au/overlays/homesteads` |

### 10. Basemaps

#### CoreLogic Basemaps
| Service | Endpoint |
|---------|----------|
| Aerial Overlay | `/geospatial/au/basemaps/aerialOverlay/mapServer` |
| Base Property | `/geospatial/au/basemaps/baseProperty/mapServer` |

## Geographic Coverage

### Australia
- **Full State Coverage**: ACT, NT, TAS
- **Metro + Regional**: NSW, QLD, SA, VIC, WA

### New Zealand
- **North Island** and **South Island** coverage for selected services

## Access Restrictions

- **UAT Access**: Business hours only (7AM - 7PM)
- **Geographic Limitations**: Based on client geo_codes in token
- **Service Availability**: 99.9% uptime SLA

## Best Practices

### Performance Optimization
1. **Cache Tokens**: Store access tokens securely until expiry
2. **Batch Requests**: Combine multiple layer requests where possible
3. **Optimize Bounding Boxes**: Use precise coordinates for faster rendering
4. **Image Formats**: Use PNG32 for high-quality overlays, JPG for larger areas

### Error Handling
1. **Token Expiry**: Monitor `expires_in` and refresh proactively
2. **Rate Limiting**: Implement backoff strategies for high-volume requests
3. **Bbox Validation**: Ensure coordinates are in correct spatial reference
4. **Layer Availability**: Check layer info endpoints for service status

### Integration Patterns

#### Property Analysis Workflow
```bash
# 1. Get property boundaries
GET /geospatial/au/overlays/propertyOverlay/propertyAll?bbox={coords}&f=image&access_token={token}

# 2. Query hazard overlays
GET /geospatial/au/overlays/flood?bbox={coords}&f=image&access_token={token}
GET /geospatial/au/overlays/bushfire?bbox={coords}&f=image&access_token={token}

# 3. Get infrastructure data
GET /geospatial/au/overlays/electricTransmissionLines?bbox={coords}&f=image&access_token={token}
```

#### Property Query Response Example
```json
{
  "displayFieldName": "address",
  "fieldAliases": {
    "OBJECTID": "Object ID",
    "property_id": "Property ID", 
    "address": "Address",
    "land_area_sqm": "Land Area (sqm)",
    "property_type": "Property Type",
    "bedrooms": "Bedrooms",
    "bathrooms": "Bathrooms",
    "car_spaces": "Car Spaces",
    "last_sale_price": "Last Sale Price",
    "last_sale_date": "Last Sale Date"
  },
  "geometryType": "esriGeometryPolygon",
  "spatialReference": {
    "wkid": 4326,
    "latestWkid": 4326
  },
  "features": [
    {
      "attributes": {
        "OBJECTID": 12345,
        "property_id": 47872329,
        "address": "123 Albert Avenue Broadbeach QLD 4218",
        "land_area_sqm": 650.5,
        "property_type": "House",
        "bedrooms": 4,
        "bathrooms": 2,
        "car_spaces": 2,
        "last_sale_price": 850000,
        "last_sale_date": "2023-03-15T00:00:00.000Z",
        "postcode": "4218",
        "council_area": "Gold Coast City",
        "locality": "Broadbeach"
      },
      "geometry": {
        "type": "polygon",
        "coordinates": [[
          [153.4295, -28.0333],
          [153.4298, -28.0333], 
          [153.4298, -28.0336],
          [153.4295, -28.0336],
          [153.4295, -28.0333]
        ]]
      }
    }
  ],
  "exceededTransferLimit": false
}
```

#### Hazard Assessment Response Example
```json
{
  "displayFieldName": "hazard_type",
  "features": [
    {
      "attributes": {
        "OBJECTID": 1,
        "property_id": 47872329,
        "hazard_type": "FLOOD",
        "risk_level": "MEDIUM", 
        "flood_zone": "AE",
        "annual_exceedance_probability": "1%",
        "flood_depth_meters": 0.8,
        "data_source": "Queensland Government",
        "last_updated": "2023-06-01T00:00:00.000Z"
      }
    },
    {
      "attributes": {
        "OBJECTID": 2,
        "property_id": 47872329,
        "hazard_type": "BUSHFIRE",
        "risk_level": "LOW",
        "bushfire_attack_level": "BAL-LOW",
        "vegetation_type": "Urban",
        "slope_classification": "FLAT",
        "data_source": "Australian Building Codes Board",
        "last_updated": "2023-05-15T00:00:00.000Z"
      }
    }
  ]
}
```

#### Planning Analysis Workflow
```bash
# 1. Query planning aggregations
GET /geospatial/au/{state}/planningAggregations/landuse?where=property_id={id}&f=json&access_token={token}

# 2. Get environmental overlays
GET /geospatial/au/{state}/overlays/nativeVegetation?bbox={coords}&f=image&access_token={token}

# 3. Check easements and restrictions
GET /geospatial/au/{state}/geometry/easements?where=property_id={id}&f=json&access_token={token}
```

## Comprehensive Endpoint Reference

### State-Specific Planning Aggregations

All planning aggregation endpoints provide Query capabilities with property-based filtering:

#### Electricity Infrastructure (All States)
```
/geospatial/au/{state}/planningAggregations/electricTransmissionLines
/geospatial/au/{state}/planningAggregations/electricTransmissionSubstations  
/geospatial/au/{state}/planningAggregations/electricTransmissionPowerStations
```

#### Land Use Analysis (All States)
```
/geospatial/au/{state}/planningAggregations/landuse
/geospatial/au/{state}/planningAggregations/nativeVegetation
/geospatial/au/{state}/planningAggregations/rainfall
/geospatial/au/{state}/planningAggregations/easements
```

### Enhanced Service Matrix

#### Complete Easement Services
| Level | Export Map | Query | Info | Planning Aggregation |
|-------|------------|-------|------|---------------------|
| **Nationwide** | ✅ | ✅ | ✅ | ❌ |
| **State-Level** | ✅ | ✅ | ✅ | ✅ |

All states support easement services: ACT, NSW, QLD, VIC, WA

#### Native Vegetation Coverage  
| State | Spatial Layers | Planning Aggregations | Regulatory Data |
|-------|---------------|---------------------|----------------|
| **All States** | Export, Query, Info | ✅ | Varies |
| **NSW** | ✅ | ✅ | Regulatory overlay |
| **QLD** | ✅ | ✅ | Management zones |
| **VIC** | ✅ | ✅ | Regulatory mapping |
| **WA** | ✅ | ✅ | Management areas |

#### Water Infrastructure
| State | Services | Full Coverage |
|-------|----------|--------------|
| **QLD** | Water Bores | Export, Query, Info, Planning |
| **SA** | Water Main | Export, Query, Info |
| **WA** | Water Meter, Harvey Pipelines, Water Pipe | Export, Query, Info |

#### Soil Analysis
| State | Services | Planning Support |
|-------|----------|-----------------|
| **SA** | Soil Subgroup | Detailed + Breakup analysis |
| **WA** | Soil Sites, Soil Landscape | Full aggregation support |

---

*© 2025 CoreLogic. All Rights Reserved.*