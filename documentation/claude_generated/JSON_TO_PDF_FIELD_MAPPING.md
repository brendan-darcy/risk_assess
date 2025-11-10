# JSON-to-PDF Field Mapping

This document maps every field in the PDF to its source in the JSON data files.

## Data Source Files

1. **Comprehensive Report**: `13683380_comprehensive_report.json`
2. **Comparable Sales**: `13683380_comparable_sales.json`
3. **Mesh Block Analysis**: `13683380_mesh_block_analysis_2000m.json`
4. **Parcel Elevation/Orientation**: `13683380_parcel_elevation_orientation.json`

---

## Category 1: INSTRUCTIONS

**Coverage Calculation**: 0% (no data available)

| PDF Field | JSON Source | Notes |
|-----------|-------------|-------|
| [GAP] Note | N/A | Hardcoded: "This category is not present in the current data model" |
| [GAP] Client Name | N/A | Not in data |
| [GAP] Client Id | N/A | Not in data |
| [GAP] Job Number | N/A | Not in data |
| [GAP] Job Type | N/A | Not in data |
| [GAP] Valuation Estimate | N/A | Not in data |
| [GAP] Parties | N/A | Not in data |
| [GAP] Special Instructions | N/A | Not in data |

---

## Category 2: LOCATION AND ADMINISTRATIVE

**Coverage Calculation**: 100% (all fields available)

### Sub-section: ADDRESS

| PDF Field | JSON Source | JSON Path |
|-----------|-------------|-----------|
| Address | Comprehensive | `property_details.location.singleLine` or `metadata.address` |

### Sub-section: LOCATION

| PDF Field | JSON Source | JSON Path |
|-----------|-------------|-----------|
| Council Area | Comprehensive | `property_details.location.councilArea` |
| Postcode | Comprehensive | `property_details.location.postcode.name` |
| Locality | Comprehensive | `property_details.location.locality.name` |
| Coordinates | Comprehensive | `property_details.location.latitude`, `property_details.location.longitude` |

### Sub-section: STATISTICAL AREAS

| PDF Field | JSON Source | JSON Path | Format |
|-----------|-------------|-----------|--------|
| SA1 Codes | Mesh Block (2000m) | `mesh_block_analysis.sa1_codes` (array), `mesh_block_analysis.total_sa1_codes` | "76 codes: {first 5 codes} (+ {remaining} more)" |
| SA2 Areas | Mesh Block (2000m) | `mesh_block_analysis.sa2_names` | Comma-separated list |
| SA3 Areas | Mesh Block (2000m) | `mesh_block_analysis.sa3_names` | Comma-separated list |
| SA4 Areas | Mesh Block (2000m) | `mesh_block_analysis.sa4_names` | Comma-separated list |

### Top-level Fields

| PDF Field | JSON Source | JSON Path |
|-----------|-------------|-----------|
| State | Comprehensive | `property_details.location.state` OR `metadata.state` |
| Zoning > Code | Comprehensive | `property_details.site.zoneCodeLocal` |
| Zoning > Description | Comprehensive | `property_details.site.zoneDescriptionLocal` |

---

## Category 3: MAPPING, TOPOGRAPHY AND PLACES

**Coverage Calculation**: 75% (infrastructure + mesh block + places available)

### Sub-section: INFRASTRUCTURE

All infrastructure fields come from: `geospatial_layers.infrastructure`

| PDF Field | JSON Source | JSON Path | Format |
|-----------|-------------|-----------|--------|
| Electric Transmission | Comprehensive | `geospatial_layers.infrastructure.electric_transmission_lines.available` | "Available (image_check)" if true |
| Ferry | Comprehensive | `geospatial_layers.infrastructure.ferry.available` | "Available (image_check)" if true |
| Railway | Comprehensive | `geospatial_layers.infrastructure.railway.available` | "Available (image_check)" if true |
| Railway Stations | Comprehensive | `geospatial_layers.infrastructure.railway_stations.available` | "Available (image_check)" if true |
| Streets | Comprehensive | `geospatial_layers.infrastructure.streets.available` | "Available (image_check)" if true |

### Sub-section: MESH BLOCK

All mesh block fields come from: `mesh_block_analysis_2000m.json`

| PDF Field | JSON Source | JSON Path |
|-----------|-------------|-----------|
| Search Radius M | Mesh Block | `mesh_block_analysis.search_radius_m` |
| Total Meshblocks | Mesh Block | `mesh_block_analysis.total_meshblocks` |
| Residential Meshblocks | Mesh Block | `mesh_block_analysis.residential_meshblocks` |
| Non Residential Meshblocks | Mesh Block | `mesh_block_analysis.non_residential_meshblocks` |
| Category Breakdown | Mesh Block | `mesh_block_analysis.category_breakdown` (dict) | Format: "Category: count, Category: count, ..." |
| Non-Residential Distances > Closest | Mesh Block | `mesh_block_analysis.non_residential_distances.closest_m` | Format: "{value}m" |
| Non-Residential Distances > Average | Mesh Block | `mesh_block_analysis.non_residential_distances.average_m` | Format: "{value}m" |
| Non-Residential Distances > Farthest | Mesh Block | `mesh_block_analysis.non_residential_distances.farthest_m` | Format: "{value}m" |
| Top 5 Closest Non-Residential | Mesh Block | `mesh_block_analysis.top_5_closest_non_residential` (array) | Format: "1. {category} ({distance}m, {sa2_name}); 2. ..." |

### Sub-section: SURROUNDING

All surrounding fields come from: `google_places_impact`

| PDF Field | JSON Source | JSON Path |
|-----------|-------------|-----------|
| Total Categories | Comprehensive | `google_places_impact.analysis.total_categories` |
| Categories With Matches | Comprehensive | `google_places_impact.analysis.categories_with_matches` |
| Categories Without Matches | Comprehensive | `google_places_impact.analysis.categories_without_matches` |
| Distance Distribution | Comprehensive | `google_places_impact.analysis.distance_stats` | Format: "closest_meters: {value}, furthest_meters: {value}" |
| Level Statistics | Comprehensive | `google_places_impact.analysis.level_stats` | "[Complex object]" |
| Closest Impacts | Comprehensive | `google_places_impact.analysis.closest_impacts` | Display first impact as dict string |

---

## Category 4: LEGAL

**Coverage Calculation**: 100% (all fields available)

### Easements Group

| PDF Field | JSON Source | JSON Path |
|-----------|-------------|-----------|
| Easements > Available | Comprehensive | `geospatial_layers.legal.easements.available` |
| Easements > Count | Comprehensive | `geospatial_layers.legal.easements.count` |
| Easements > Features | Comprehensive | `geospatial_layers.legal.easements.count` | Format: "{count} found" |
| Example 1 | Comprehensive | `geospatial_layers.legal.easements.features[0].attributes` | Format: "Status: {status}, PFI: {pfi}, UFI: {ufi}" |
| Example 2 | Comprehensive | `geospatial_layers.legal.easements.features[1].attributes` | Format: "Status: {status}, PFI: {pfi}, UFI: {ufi}" |
| Example 3 | Comprehensive | `geospatial_layers.legal.easements.features[2].attributes` | Format: "Status: {status}, PFI: {pfi}, UFI: {ufi}" |

### Legal Group

| PDF Field | JSON Source | JSON Path |
|-----------|-------------|-----------|
| Legal > Isactiveproperty | Comprehensive | `property_details.legal.isActiveProperty` |
| Legal > Legal > Dateissued | Comprehensive | `property_details.legal.legal.dateIssued` |
| Legal > Legal > Frontage | Comprehensive | `property_details.legal.legal.frontage` |
| Legal > Legal > Realpropertydescription | Comprehensive | `property_details.legal.legal.realPropertyDescription` |
| Legal > Parcels #1 | Comprehensive | `property_details.legal.parcels[0]` | Format: "parcelId: {parcelId}, landAuthority: {landAuthority}" |
| Legal > Title > Titleindicator | Comprehensive | `property_details.legal.title.titleIndicator` |

### Top-level

| PDF Field | JSON Source | JSON Path |
|-----------|-------------|-----------|
| Property Id | Comprehensive | `metadata.property_id` |

---

## Category 5: CHARACTERISTICS

**Coverage Calculation**: 100% (all fields available)

### Sub-section: CORE ATTRIBUTES

All from `property_details.core_attributes`:

| PDF Field | JSON Path |
|-----------|-----------|
| Baths | `baths` |
| Beds | `beds` |
| Carspaces | `carSpaces` |
| Iscalculatedlandarea | `isCalculatedLandArea` |
| Landarea | `landArea` |
| Landareasource | `landAreaSource` |
| Lockupgarages | `lockUpGarages` |
| Propertysubtype | `propertySubType` |
| Propertysubtypeshort | `propertySubTypeShort` |
| Propertytype | `propertyType` |

### Sub-section: ADDITIONAL ATTRIBUTES

All from `property_details.additional_attributes`:

| PDF Field | JSON Path |
|-----------|-----------|
| Airconditioned | `airConditioned` |
| Ductedheating | `ductedHeating` |
| Ensuite | `ensuite` |
| Fireplace | `fireplace` |
| Floorarea | `floorArea` |
| Roofmaterial | `roofMaterial` |
| Solarpower | `solarPower` |
| Wallmaterial | `wallMaterial` |
| Yearbuilt | `yearBuilt` |

### Sub-section: FEATURES

| PDF Field | JSON Source | JSON Path | Format |
|-----------|-------------|-----------|--------|
| • Close To Public Transport | Comprehensive | `property_details.features.features[0]` | Bullet point |
| • Renovated | Comprehensive | `property_details.features.features[1]` | Bullet point |
| Building Area | Comprehensive | `property_details.features.featureAttributes` (find name="Building Area") | `.value` |
| Development Zone | Comprehensive | `property_details.features.featureAttributes` (find name="Development Zone") | `.value` |
| Dining Rooms | Comprehensive | `property_details.features.featureAttributes` (find name="Dining Rooms") | `.value` |
| Family / Rumpus Rooms | Comprehensive | `property_details.features.featureAttributes` (find name="Family / Rumpus Rooms") | `.value` |
| Kitchen Features | Comprehensive | `property_details.features.featureAttributes` (find name="Kitchen Features") | `.value` |
| Laundry Features | Comprehensive | `property_details.features.featureAttributes` (find name="Laundry Features") | `.value` |
| Lounge Rooms | Comprehensive | `property_details.features.featureAttributes` (find name="Lounge Rooms") | `.value` |
| Materials in Floor | Comprehensive | `property_details.features.featureAttributes` (find name="Materials in Floor") | `.value` |
| Other Rooms | Comprehensive | `property_details.features.featureAttributes` (find name="Other Rooms") | `.value` |
| Other Special Features | Comprehensive | `property_details.features.featureAttributes` (find name="Other Special Features") | `.value` |
| Toilets | Comprehensive | `property_details.features.featureAttributes` (find name="Toilets") | `.value` |
| Total Floors In Building | Comprehensive | `property_details.features.featureAttributes` (find name="Total Floors In Building") | `.value` |
| Workshop Features | Comprehensive | `property_details.features.featureAttributes` (find name="Workshop Features") | `.value` |

### Sub-section: SPATIAL

#### Geometry Basics (from parcel_elevation_orientation.json):

| PDF Field | JSON Path |
|-----------|-----------|
| Geometry Type | `geometry_type` |
| Spatial Reference | `spatial_reference.wkid` |
| Property Area | `parcel_attributes.property_m2` | Format: "{value} m²" |
| Calculated Area | `parcel_attributes["st_area(geom)"]` | Format: "{value} m²" |
| Perimeter | `parcel_attributes["st_perimeter(geom)"]` | Format: "{value} m" |
| Polygon Rings | Count of `geometry.rings` array |
| Vertices | Count of vertices in first ring |

#### Raw Geometry Coordinates (Web Mercator):

| PDF Field | JSON Path | Format |
|-----------|-----------|--------|
| Ring 1 | `geometry.rings[0]` | "{count} vertices" |
| X Coordinates | `geometry.rings[0]` | CONSOLIDATED: comma-separated list of all X coordinates |
| Y Coordinates | `geometry.rings[0]` | CONSOLIDATED: comma-separated list of all Y coordinates |

#### Elevation:

| PDF Field | JSON Path | Format |
|-----------|-----------|--------|
| Min Elevation | `elevation_analysis.elevation_statistics.min_elevation_m` | "{value}m" |
| Max Elevation | `elevation_analysis.elevation_statistics.max_elevation_m` | "{value}m" |
| Avg Elevation | `elevation_analysis.elevation_statistics.avg_elevation_m` | "{value}m" |
| Elevation Range | `elevation_analysis.elevation_statistics.elevation_range_m` | "{value}m" |
| Max Slope | `elevation_analysis.slope_analysis.max_slope.slope_degrees`, `slope_percent` | "{degrees}° ({percent}%)" |
| Avg Slope | `elevation_analysis.slope_analysis.avg_slope_degrees`, `avg_slope_percent` | "{degrees}° ({percent}%)" |

#### Center Point (WGS84):

| PDF Field | JSON Path |
|-----------|-----------|
| Latitude | `elevation_analysis.center_elevation.lat` |
| Longitude | `elevation_analysis.center_elevation.lon` |
| Elevation | `elevation_analysis.center_elevation.elevation_m` | Format: "{value}m" |
| Resolution | `elevation_analysis.center_elevation.resolution_m` | Format: "{value}m" |

#### Vertex Coordinates (WGS84 + Elevation):

| PDF Field | JSON Path | Format |
|-----------|-----------|--------|
| Total Vertices | Count of `elevation_analysis.vertex_elevations` |
| Latitudes | `elevation_analysis.vertex_elevations[].lat` | CONSOLIDATED: comma-separated list |
| Longitudes | `elevation_analysis.vertex_elevations[].lon` | CONSOLIDATED: comma-separated list |
| Elevations | `elevation_analysis.vertex_elevations[].elevation_m` | CONSOLIDATED: comma-separated list with "m" suffix |

#### Orientation:

| PDF Field | JSON Path |
|-----------|-----------|
| Frontage Length | `orientation_analysis.frontage_edge.length_m` | Format: "{value}m" |
| Frontage Direction | `orientation_analysis.frontage_orientation.cardinal_direction`, `bearing_degrees` | Format: "{cardinal} ({degrees}°)" |
| Property Faces | `orientation_analysis.property_orientation.cardinal_direction`, `bearing_degrees` | Format: "{cardinal} ({degrees}°)" |

#### Frontage Edge Vertices:

**IMPORTANT**: NOT CONSOLIDATED - show as separate entries

| PDF Field | JSON Path |
|-----------|-----------|
| Vertex 1 (WGS84) > Latitude | `orientation_analysis.frontage_edge.vertex_1.lat` |
| Vertex 1 (WGS84) > Longitude | `orientation_analysis.frontage_edge.vertex_1.lon` |
| Vertex 2 (WGS84) > Latitude | `orientation_analysis.frontage_edge.vertex_2.lat` |
| Vertex 2 (WGS84) > Longitude | `orientation_analysis.frontage_edge.vertex_2.lon` |

#### Street Location (WGS84):

| PDF Field | JSON Path |
|-----------|-----------|
| Latitude | `orientation_analysis.street_location.lat` |
| Longitude | `orientation_analysis.street_location.lon` |
| Detection Method | `orientation_analysis.street_location.method` |

---

## Category 6: OCCUPANCY

**Coverage Calculation**: 70% (partial - occupancy fields available, some site fields available)

| PDF Field | JSON Source | JSON Path |
|-----------|-------------|-----------|
| Occupancy > Confidencescore | Comprehensive | `property_details.occupancy.confidenceScore` |
| Occupancy > Isactiveproperty | Comprehensive | `property_details.occupancy.isActiveProperty` |
| Occupancy > Occupancytype | Comprehensive | `property_details.occupancy.occupancyType` |
| Site > Isactiveproperty | Comprehensive | `property_details.site.isActiveProperty` |
| Site > Landuseprimary | Comprehensive | `property_details.site.landUsePrimary` |
| Site > Sitevaluelist | Comprehensive | `property_details.site.siteValueList` | Display "None" if empty array |
| Site > Zonecodelocal | Comprehensive | `property_details.site.zoneCodeLocal` |
| Site > Zonedescriptionlocal | Comprehensive | `property_details.site.zoneDescriptionLocal` |

---

## Category 7: LOCAL MARKET

**Coverage Calculation**: 95% (most market metrics available)

### Sub-section: MARKET METRICS AVAILABILITY

All from `market_metrics_summary` in comprehensive report.

Each metric should display:
- ✓ or ✗ indicator
- Metric name
- Data Points: "{count} ({interval})"
- Period: "{first_date} to {last_date}"
- First Value, Latest Value, Growth (if available)

| PDF Field | JSON Path |
|-----------|-----------|
| Median Days on Market | `market_metrics_summary.median_days_on_market` |
| Median Asking Rent | `market_metrics_summary.median_asking_rent` |
| Median Sale Price | `market_metrics_summary.median_sale_price` |
| Median Value | `market_metrics_summary.median_value` |
| Rental Yield | `market_metrics_summary.rental_yield` |
| Sales Volume | `market_metrics_summary.sales_volume` |
| Total Listings | `market_metrics_summary.total_listings` |
| Median Vendor Discount | `market_metrics_summary.median_vendor_discount` |

### Sub-section: FEATURED METRICS

These show raw dictionary representations:

| PDF Field | JSON Path |
|-----------|-----------|
| Median Rent | `market_metrics_summary.median_asking_rent` | Display as dict string |
| Median Sale Price | `market_metrics_summary.median_sale_price` | Display as dict string |
| Median Value | `market_metrics_summary.median_value` | Display as dict string |
| Rental Market | Calculate from `rental_yield` data | Display as dict string |

---

## Category 8: TRANSACTION HISTORY

**Coverage Calculation**: 100% (all fields available)

### Last Sale Group

All from `property_details.last_sale.lastSale`:

| PDF Field | JSON Path |
|-----------|-----------|
| Last Sale > Isactiveproperty | `../isActiveProperty` |
| Last Sale > Lastsale > Agencyname | `agencyName` |
| Last Sale > Lastsale > Agentname | `agentName` |
| Last Sale > Lastsale > Contractdate | `contractDate` |
| Last Sale > Lastsale > Isagentsadvice | `isAgentsAdvice` |
| Last Sale > Lastsale > Isarmslength | `isArmsLength` |
| Last Sale > Lastsale > Isderivedagency | `isDerivedAgency` |
| Last Sale > Lastsale > Isderivedagent | `isDerivedAgent` |
| Last Sale > Lastsale > Ismultisale | `isMultiSale` |
| Last Sale > Lastsale > Ispricewithheld | `isPriceWithheld` |
| Last Sale > Lastsale > Isrearecentsale | `isReaRecentSale` |
| Last Sale > Lastsale > Isstandardtransfer | `isStandardTransfer` |
| Last Sale > Lastsale > Landuseprimary | `landUsePrimary` |
| Last Sale > Lastsale > Price | `price` | Format: "${value:,}" |
| Last Sale > Lastsale > Salemethod | `saleMethod` |
| Last Sale > Lastsale > Settlementdate | `settlementDate` |
| Last Sale > Lastsale > Transferid | `transferId` |
| Last Sale > Lastsale > Type | `type` |
| Last Sale > Lastsale > Zonecodelocal | `zoneCodeLocal` |
| Last Sale > Lastsale > Zonedescriptionlocal | `zoneDescriptionLocal` |

### Sales History Group

| PDF Field | JSON Path |
|-----------|-----------|
| Sales History > Isactiveproperty | `property_details.sales_history.isActiveProperty` |
| Sales History > Salelist #1 | `property_details.sales_history.saleList[0]` | Format: "type: {type}, Price: ${price}, contractDate: {contractDate}" |
| Sales History > Salelist #2 | `property_details.sales_history.saleList[1]` | Format: "type: {type}, Price: ${price}, contractDate: {contractDate}" |

---

## Category 9: CAMPAIGNS

**Coverage Calculation**: 100% (all fields available)

### Sub-section: CAMPAIGN TIMELINE

| PDF Field | JSON Source | JSON Path |
|-----------|-------------|-----------|
| Total Events | Comprehensive | Count all campaign events from `property_details.sales_otm` and `rentals_otm` |

#### Timeline Events:

Events come from:
- `property_details.sales_otm.forSalePropertyCampaign.campaigns[]`
- `property_details.rentals_otm` (if available)

For each campaign, extract:
- `fromDate` → "■ Forsale Campaignstart"
- `toDate` → "■ Forsale Campaignend"
- Sale dates from `sales_history` → "■ Sale"

### Sub-section: ADVERTISEMENT EXTRACTS

| PDF Field | JSON Source | JSON Path |
|-----------|-------------|-----------|
| Total Advertisements | Comprehensive | Count of `property_details.advertisements` |
| Advertisement #1 > Date | `property_details.advertisements[0].date` |
| Advertisement #1 > Type | `property_details.advertisements[0].type` |
| Advertisement #1 > Price | `property_details.advertisements[0].price` |
| Advertisement #1 > Method | `property_details.advertisements[0].method` |
| Advertisement #1 > Description | `property_details.advertisements[0].description` |

---

## Category 10: SALES EVIDENCE

**Coverage Calculation**: 100% (all fields available)

**Source**: `13683380_comparable_sales.json`

### Special Note:

| PDF Field | JSON Path |
|-----------|-----------|
| [GAP] Note | Hardcoded or from `metadata.search_type` | "Comparable sales generated from radius search" |

### Sub-section: COMPARABLE SALES SUMMARY

| PDF Field | JSON Path |
|-----------|-----------|
| Total Comparables | `metadata.total_comparables` OR `statistics.total_count` | Format: "{count} properties" |

#### Price Statistics:

| PDF Field | JSON Path | Format |
|-----------|-----------|--------|
| Median Price | `statistics.price_statistics.median` | "${value:,}" |
| Mean Price | `statistics.price_statistics.mean` | "${value:,}" |
| Price Range | `statistics.price_statistics.min`, `max` | "${min:,} - ${max:,}" |

#### Sale Date Range:

| PDF Field | JSON Path |
|-----------|-----------|
| Overall Period | `statistics.date_range.earliest` to `latest` | Format: "YYYY-MM-DD to YYYY-MM-DD" |
| Recent 25 Period | `statistics.recent_25_date_range.earliest` to `latest` | Format: "YYYY-MM-DD to YYYY-MM-DD ({count} sales)" |
| Recent 50 Period | `statistics.recent_50_date_range.earliest` to `latest` | Format: "YYYY-MM-DD to YYYY-MM-DD ({count} sales)" |

#### Distance Distribution:

| PDF Field | JSON Path | Format |
|-----------|-----------|--------|
| Within 500m | `statistics.distance_distribution.within_500m` | "{count} properties" |
| Within 1km | `statistics.distance_distribution.within_1km` | "{count} properties" |
| Within 3km | `statistics.distance_distribution.within_3km` | "{count} properties" |

#### Property Characteristics:

| PDF Field | JSON Path | Format |
|-----------|-----------|--------|
| Property Types | `statistics.property_characteristics.propertyType.distribution` | "{count} {TYPE}, {count} {TYPE}" |
| Bedrooms | `statistics.property_characteristics.beds.distribution` | "{count}×{beds}bd, ..." |
| Bathrooms | `statistics.property_characteristics.baths.distribution` | "{count}×{baths}ba, ..." |

### Sub-section: INDIVIDUAL COMPARABLES

**CRITICAL**: List ALL 48 comparables individually

| PDF Field | JSON Path | Format |
|-----------|-----------|--------|
| Comparable #{n} > Address | `comparable_sales[n-1].address` |
| Comparable #{n} > Sale Price | `comparable_sales[n-1].salePrice` | "${value:,}" |
| Comparable #{n} > Property | `comparable_sales[n-1].beds`, `baths`, `carSpaces`, `propertyType` | "{beds}bd / {baths}ba / {carSpaces}car \| {propertyType}" |
| Comparable #{n} > Land Area | `comparable_sales[n-1].landArea` | "{value} m²" |
| Comparable #{n} > Distance | `comparable_sales[n-1].distance` | "{value} km" |
| Comparable #{n} > Sale Date | `comparable_sales[n-1].lastSaleDate` |

### Sub-section: SEARCH PARAMETERS

| PDF Field | JSON Path |
|-----------|-----------|
| Search Radius | `metadata.search_parameters.radius` OR `metadata.default_radius_km` | Format: "{value} km" |

---

## COVERAGE CALCULATION LOGIC

```python
def calculate_coverage(category_name, data):
    """
    Calculate coverage percentage for each category based on available fields.

    Returns: (percentage, description)
    Examples:
    - (0, "Not captured in source data")
    - (70, "Partial coverage")
    - (75, "Good coverage")
    - (95, "Excellent coverage")
    - (100, "Complete")
    """

    coverage_rules = {
        "INSTRUCTIONS": lambda: (0, "Not captured in source data"),
        "LOCATION AND ADMINISTRATIVE": lambda: check_location_fields(data),
        "MAPPING, TOPOGRAPHY AND PLACES": lambda: check_mapping_fields(data),
        "LEGAL": lambda: check_legal_fields(data),
        "CHARACTERISTICS": lambda: check_characteristics_fields(data),
        "OCCUPANCY": lambda: check_occupancy_fields(data),
        "LOCAL MARKET": lambda: check_market_fields(data),
        "TRANSACTION HISTORY": lambda: check_transaction_fields(data),
        "CAMPAIGNS": lambda: check_campaigns_fields(data),
        "SALES EVIDENCE": lambda: check_comparables_fields(data),
    }

    return coverage_rules[category_name]()
```

---

## CRITICAL FORMATTING RULES

### 1. Consolidated vs Non-Consolidated Data

**CONSOLIDATED** (comma-separated lists):
- Raw Geometry X Coordinates: `", ".join(str(coord) for coord in x_coords)`
- Raw Geometry Y Coordinates: `", ".join(str(coord) for coord in y_coords)`
- Vertex Latitudes: `", ".join(f"{lat:.8f}" for lat in lats)`
- Vertex Longitudes: `", ".join(f"{lon:.8f}" for lon in lons)`
- Vertex Elevations: `", ".join(f"{elev:.2f}m" for elev in elevs)`

**NOT CONSOLIDATED** (separate entries):
- Frontage Edge Vertices: Show as separate "Vertex 1" and "Vertex 2" with individual Latitude/Longitude fields

### 2. SA1 Codes Format

```python
total_codes = len(sa1_codes)
first_5 = sa1_codes[:5]
remaining = total_codes - 5

formatted = f"{total_codes} codes: {', '.join(map(str, first_5))}"
if remaining > 0:
    formatted += f" (+ {remaining} more)"
```

### 3. Comparable Sales Format

**MUST list ALL comparables individually**, not just a summary. Use the format:
```
Comparable #1:
  Address: {address}
  Sale Price: ${price:,}
  Property: {beds}bd / {baths}ba / {carSpaces}car | {propertyType}
  Land Area: {landArea} m²
  Distance: {distance} km
  Sale Date: {lastSaleDate}
```

### 4. Market Metrics Format

For each metric, show:
- ✓ or ✗ indicator
- Metric name in bold
- "Data Points: {count} ({interval})" e.g., "8 (yearly)"
- "Period: YYYY-MM-DD to YYYY-MM-DD"
- "First Value: {value}"
- "Latest Value: {value}"
- "Growth: +/-{percent}%"

---

## FOOTER FORMAT

```
Report generated: {timestamp} | Property ID: {property_id or "N/A"}
```
