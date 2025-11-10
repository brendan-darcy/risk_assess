# Complete PDF Field Extraction - Pre-Qualification Data Collection

**Source PDF**: `data/property_reports/13683380_final_saved.pdf`

This document extracts EVERY variable, sub-heading, and formatting detail from the good PDF to serve as the specification for rebuilding the PDF generator.

---

## Category 1: INSTRUCTIONS

**Coverage**: `0% - Not captured in source data`

### Special Note
- `[GAP] Note`: "This category is not present in the current data model"

### Fields (All marked with [GAP]):
1. `[GAP] Client Name`: "Not captured"
2. `[GAP] Client Id`: "Not captured"
3. `[GAP] Job Number`: "Not captured"
4. `[GAP] Job Type`: "Not captured"
5. `[GAP] Valuation Estimate`: "Not captured"
6. `[GAP] Parties`: "Not captured"
7. `[GAP] Special Instructions`: "Not captured"

**Formatting Notes**:
- All fields are shown in a table format with [GAP] prefix
- Values show "Not captured"

---

## Category 2: LOCATION AND ADMINISTRATIVE

**Coverage**: `100% - Complete`

### Sub-section: ADDRESS

1. **Address**: "5 Settlers Court, Vermont South VIC 3133"

### Sub-section: LOCATION

2. **Council Area**: "Whitehorse"
3. **Postcode**: "3133"
4. **Locality**: "VERMONT SOUTH"
5. **Coordinates**: "-37.858785, 145.186896"

### Sub-section: STATISTICAL AREAS

6. **SA1 Codes**: "76 codes: 20703116613, 21101125916, 21101126006, 21104126908, 21104126913 (+ 15 more)"
   - Format: Shows count, lists first 5 codes, then "(+ X more)" for remaining

7. **SA2 Areas**: "Wantirna, Glen Waverley - East, Glen Waverley - West, Vermont South, Vermont, Forest Hill, Burwood East, Wantirna South"
   - Format: Comma-separated list

8. **SA3 Areas**: "Knox, Monash, Whitehorse - East, Whitehorse - West"
   - Format: Comma-separated list

9. **SA4 Areas**: "Melbourne - Outer East, Melbourne - South East, Melbourne - Inner East"
   - Format: Comma-separated list

### Top-level fields (not in sub-sections):

10. **State**: "VIC"
11. **Zoning > Code**: "NRZ5"
12. **Zoning > Description**: "Neighbourhood Residential Zone - Schedule 5"

---

## Category 3: MAPPING, TOPOGRAPHY AND PLACES

**Coverage**: `75% - Good coverage`

### Sub-section: INFRASTRUCTURE

1. **Electric Transmission**: "Available (image_check)"
2. **Ferry**: "Available (image_check)"
3. **Railway**: "Available (image_check)"
4. **Railway Stations**: "Available (image_check)"
5. **Streets**: "Available (image_check)"

### Sub-section: MESH BLOCK

6. **Search Radius M**: "2000"
7. **Total Meshblocks**: "254"
8. **Residential Meshblocks**: "213"
9. **Non Residential Meshblocks**: "41"
10. **Category Breakdown**: "Commercial: 5, Education: 10, Other: 1, Parkland: 25, Residential: 213"
    - Format: Category: count, comma-separated

11. **Non-Residential Distances** (sub-group):
    - **Closest**: "180.0m"
    - **Average**: "1104.4m"
    - **Farthest**: "1941.2m"

12. **Top 5 Closest Non-Residential**: "1. Commercial (180.0m, Vermont South); 2. Parkland (293.9m, Vermont South); 3. Parkland (378.3m, Vermont South); 4. Commercial (423.0m, Vermont South); 5. Parkland (541.1m, Vermont South)"
    - Format: Numbered list with type (distance, suburb)

### Sub-section: SURROUNDING

13. **Total Categories**: "29"
14. **Categories With Matches**: "1"
15. **Categories Without Matches**: "28"
16. **Distance Distribution**: "closest_meters: 193.4, furthest_meters: 193.4"
17. **Level Statistics**: "[Complex object]"
18. **Closest Impacts**: "{'category': 'Other Transit', 'name': 'Colonial Dr/Burwood Hwy', 'distance_meters': 193.4, 'level': 'Level_3_Impacts', 'address': 'Vermont South VIC 3133, Australia'}"

---

## Category 4: LEGAL

**Coverage**: `100% - Complete`

### Easements Group:
1. **Easements > Available**: "Yes"
2. **Easements > Count**: "2000"
3. **Easements > Features**: "2000 found"
4. **Example 1**: "Status: Active, PFI: 456371337, UFI: 830436892"
5. **Example 2**: "Status: Active, PFI: 453638786, UFI: 767100365"
6. **Example 3**: "Status: Active, PFI: 123595, UFI: 826941111"

### Legal Group:
7. **Legal > Isactiveproperty**: "Yes"
8. **Legal > Legal > Dateissued**: "1411"
9. **Legal > Legal > Frontage**: "0.0"
10. **Legal > Legal > Realpropertydescription**: "LOT 36 LP97848"
11. **Legal > Parcels #1**: "parcelId: 8527260, landAuthority: Whitehorse"
12. **Legal > Title > Titleindicator**: "No More Titles"

### Top-level:
13. **Property Id**: "13683380"

---

## Category 5: CHARACTERISTICS

**Coverage**: `100% - Complete`

### Sub-section: CORE ATTRIBUTES

1. **Baths**: "2"
2. **Beds**: "4"
3. **Carspaces**: "2"
4. **Iscalculatedlandarea**: "Yes"
5. **Landarea**: "792"
6. **Landareasource**: "Calculated"
7. **Lockupgarages**: "2"
8. **Propertysubtype**: "House: One Storey / Lowset"
9. **Propertysubtypeshort**: "One Storey / Lowset"
10. **Propertytype**: "HOUSE"

### Sub-section: ADDITIONAL ATTRIBUTES

11. **Airconditioned**: "Yes"
12. **Ductedheating**: "Yes"
13. **Ensuite**: "1"
14. **Fireplace**: "Yes"
15. **Floorarea**: "187"
16. **Roofmaterial**: "Concrete Tile,"
17. **Solarpower**: "Yes"
18. **Wallmaterial**: "Brick,"
19. **Yearbuilt**: "1980"

### Sub-section: FEATURES

**Bullet points** (two features shown with bullets):
- "Close To Public Transport"
- "Renovated"

**Additional feature fields** (NOT bulleted):
20. **Building Area**: "213"
21. **Development Zone**: "Neighbourhood Residential Zone - Schedule 5"
22. **Dining Rooms**: "1"
23. **Family / Rumpus Rooms**: "1"
24. **Kitchen Features**: "Stainless Steel Appliances"
25. **Laundry Features**: "Internal Laundry"
26. **Lounge Rooms**: "2"
27. **Materials in Floor**: "Carpet Floor, Slate Floor"
28. **Other Rooms**: "1"
29. **Other Special Features**: "Dishwasher, Separate Dining Room"
30. **Toilets**: "1"
31. **Total Floors In Building**: "1"
32. **Workshop Features**: "Shed"

### Sub-section: SPATIAL

#### Geometry basics:
33. **Geometry Type**: "esriGeometryPolygon"
34. **Spatial Reference**: "WKID 102100"
35. **Property Area**: "791.91 m²"
36. **Calculated Area**: "1272.53 m²"
37. **Perimeter**: "149.68 m"
38. **Polygon Rings**: "1"
39. **Vertices**: "8"

#### Raw Geometry Coordinates (Web Mercator):
40. **Ring 1**: "8 vertices"
41. **X Coordinates**: "16162134.2654, 16162124.3885, 16162114.7070, 16162122.0842, 16162139.6391, 16162148.8694, 16162139.5368, 16162134.2654"
    - **FORMAT**: Comma-separated list, consolidated
42. **Y Coordinates**: "-4559521.3277, -4559519.6250, -4559518.1488, -4559469.3623, -4559473.6377, -4559475.8853, -4559522.5151, -4559521.3277"
    - **FORMAT**: Comma-separated list, consolidated

#### Elevation:
43. **Min Elevation**: "95.71m"
44. **Max Elevation**: "99.23m"
45. **Avg Elevation**: "97.03m"
46. **Elevation Range**: "3.52m"
47. **Max Slope**: "6.38° (11.19%)"
48. **Avg Slope**: "3.87° (6.76%)"

#### Center Point (WGS84):
49. **Latitude**: "-37.85883250"
50. **Longitude**: "145.18690397"
51. **Elevation**: "98.65m"
52. **Resolution**: "9.54m"

#### Vertex Coordinates (WGS84 + Elevation):
53. **Total Vertices**: "8"
54. **Latitudes**: "-37.85896441, -37.85895233, -37.85894186, -37.85859585, -37.85862617, -37.85864211, -37.85897283, -37.85896441"
    - **FORMAT**: Comma-separated list, consolidated
55. **Longitudes**: "145.18692235, 145.18683362, 145.18674665, 145.18681292, 145.18697062, 145.18705354, 145.18696970, 145.18692235"
    - **FORMAT**: Comma-separated list, consolidated
56. **Elevations**: "96.09m, 96.60m, 97.47m, 99.23m, 97.93m, 97.17m, 95.71m, 96.09m"
    - **FORMAT**: Comma-separated list with "m" suffix, consolidated

#### Orientation:
57. **Frontage Length**: "7.9m"
58. **Frontage Direction**: "W (279.8°)"
59. **Property Faces**: "N (9.8°)"

#### Frontage Edge Vertices:
60. **Vertex 1 (WGS84)**:
    - **Latitude**: "-37.85896441"
    - **Longitude**: "145.18692235"
61. **Vertex 2 (WGS84)**:
    - **Latitude**: "-37.85895233"
    - **Longitude**: "145.18683362"
    - **FORMAT**: NOT CONSOLIDATED - shown as separate Vertex 1 and Vertex 2 with individual Latitude/Longitude fields

#### Street Location (WGS84):
62. **Latitude**: "-37.85902330"
63. **Longitude**: "145.18684430"
64. **Detection Method**: "geocoded"

---

## Category 6: OCCUPANCY

**Coverage**: `70% - Partial coverage`

1. **Occupancy > Confidencescore**: "Low"
2. **Occupancy > Isactiveproperty**: "Yes"
3. **Occupancy > Occupancytype**: "Owner Occupied"
4. **Site > Isactiveproperty**: "Yes"
5. **Site > Landuseprimary**: "Detached Dwelling (existing)"
6. **Site > Sitevaluelist**: "None"
7. **Site > Zonecodelocal**: "NRZ5"
8. **Site > Zonedescriptionlocal**: "Neighbourhood Residential Zone - Schedule 5"

---

## Category 7: LOCAL MARKET

**Coverage**: `95% - Excellent coverage`

### Sub-section: MARKET METRICS AVAILABILITY

Each metric has this structure:
- Checkmark (✓) or X (✗) indicator
- Metric name
- Data Points (count and interval)
- Period (date range)
- First Value
- Latest Value
- Growth (percentage)

#### Metric 1: Median Days on Market
1. **✓ Median Days on Market**:
   - **Data Points**: "8 (yearly)"
   - **Period**: "2015-01 to 2022-01"
   - **First Value**: "0"
   - **Latest Value**: "0"
   - **Growth**: "-8.2%"

#### Metric 2: Median Asking Rent
2. **✓ Median Asking Rent**:
   - **Data Points**: "44 (quarterly)"
   - **Period**: "2014-09 to 2022-01"
   - **First Value**: "$815,000"
   - **Latest Value**: "$1,500,000"
   - **Growth**: "+84.0%"

#### Metric 3: Median Sale Price
3. **✓ Median Sale Price**:
   - **Data Points**: "46 (quarterly)"
   - **Period**: "2014-09 to 2022-03"
   - **First Value**: "$88"
   - **Latest Value**: "$99"
   - **Growth**: "+12.5%"

#### Metric 4: Median Value
4. **✓ Median Value**:
   - **Data Points**: "92 (monthly)"
   - **Period**: "2014-08 to 2022-03"
   - **First Value**: "$2,127"
   - **Latest Value**: "$2,711"
   - **Growth**: "+27.5%"

#### Metric 5: Rental Yield
5. **✓ Rental Yield**:
   - **Data Points**: "69 (monthly)"
   - **Period**: "2016-05 to 2022-01"
   - **Latest Value**: "-0.03%"

#### Metric 6: Sales Volume
6. **✓ Sales Volume**:
   - **Data Points**: "46 (quarterly)"
   - **Period**: "2014-09 to 2022-03"
   - **First Value**: "760,917"
   - **Latest Value**: "1,425,306"
   - **Growth**: "+87.3%"

#### Metric 7: Total Listings
7. **✓ Total Listings**:
   - **Data Points**: "90 (monthly)"
   - **Period**: "2014-08 to 2022-01"
   - **First Value**: "0"
   - **Latest Value**: "0"
   - **Growth**: "+13.3%"

#### Metric 8: Median Vendor Discount
8. **✗ Median Vendor Discount**: "No data returned from API"

### Sub-section: FEATURED METRICS

These show raw dictionary/JSON representations:

9. **Median Rent**: "{'description': 'Median Asking Rent', 'first_date': '2014-09-30', 'last_date': '2022-01-31', 'first_value': 815000.0, 'last_value': 1500000.0, 'growth_amount': 685000.0, 'growth_percent': 84.0, 'data_points': 44, 'interval': 'quarterly'}"

10. **Median Sale Price**: "{'description': 'Median Sale Price', 'first_date': '2014-09-30', 'last_date': '2022-03-31', 'first_value': 88.0, 'last_value': 99.0, 'growth_amount': 11.0, 'growth_percent': 12.5, 'data_points': 46, 'interval': 'quarterly'}"

11. **Median Value**: "{'description': 'Median Value', 'first_date': '2014-08-31', 'last_date': '2022-03-31', 'first_value': 2127.0, 'last_value': 2711.0, 'growth_amount': 584.0, 'growth_percent': 27.5, 'data_points': 92, 'interval': 'monthly'}"

12. **Rental Market**: "{'rental_yield': -0.0291518269, 'rental_yield_date': '2022-01-31', 'median_rent': 1500000.0, 'median_rent_date': '2022-01-31'}"

---

## Category 8: TRANSACTION HISTORY

**Coverage**: `100% - Complete`

### Last Sale Group:
1. **Last Sale > Isactiveproperty**: "Yes"
2. **Last Sale > Lastsale > Agencyname**: "Ray White Blackburn"
3. **Last Sale > Lastsale > Agentname**: "Peter Schenck"
4. **Last Sale > Lastsale > Contractdate**: "2014-08-23"
5. **Last Sale > Lastsale > Isagentsadvice**: "No"
6. **Last Sale > Lastsale > Isarmslength**: "Yes"
7. **Last Sale > Lastsale > Isderivedagency**: "Yes"
8. **Last Sale > Lastsale > Isderivedagent**: "Yes"
9. **Last Sale > Lastsale > Ismultisale**: "No"
10. **Last Sale > Lastsale > Ispricewithheld**: "No"
11. **Last Sale > Lastsale > Isrearecentsale**: "No"
12. **Last Sale > Lastsale > Isstandardtransfer**: "Yes"
13. **Last Sale > Lastsale > Landuseprimary**: "Detached Dwelling (existing)"
14. **Last Sale > Lastsale > Price**: "$920,000"
15. **Last Sale > Lastsale > Salemethod**: "Normal Sale"
16. **Last Sale > Lastsale > Settlementdate**: "2014-10-22"
17. **Last Sale > Lastsale > Transferid**: "40925446"
18. **Last Sale > Lastsale > Type**: "Unknown"
19. **Last Sale > Lastsale > Zonecodelocal**: "NRZ5"
20. **Last Sale > Lastsale > Zonedescriptionlocal**: "Neighbourhood Residential Zone - Schedule 5"

### Sales History Group:
21. **Sales History > Isactiveproperty**: "Yes"
22. **Sales History > Salelist #1**: "type: Unknown, Price: $920,000, contractDate: 2014-08-23"
23. **Sales History > Salelist #2**: "type: Unknown, Price: $605,000, contractDate: 2008-05-14"

---

## Category 9: CAMPAIGNS

**Coverage**: `100% - Complete`

### Sub-section: CAMPAIGN TIMELINE

1. **Total Events**: "8"

#### Timeline events (with markers):
2. **■ Forrent Campaignend**: "2022-05-02"
3. **■ Forrent Campaignstart**: "2022-04-14"
4. **■ Forsale Campaignend**: "2014-08-25"
5. **■ Sale**: "2014-08-23"
6. **■ Forsale Campaignstart**: "2014-07-25"
7. **■ Forsale Campaignend**: "2008-05-22"
8. **■ Sale**: "2008-05-14"
9. **■ Forsale Campaignstart**: "2008-04-13"

### Sub-section: ADVERTISEMENT EXTRACTS

10. **Total Advertisements**: "1"

#### Advertisement #1:
11. **Advertisement #1**:
    - **Date**: "2022-05-02"
    - **Type**: "FORRENT"
    - **Price**: "$600 p.w."
    - **Method**: "Rent"
    - **Description**: "Beautiful gardens greet you at this spacious, comfortable 4 bed, 2 bathroom home located in a quiet court and close to all amenities. This house has the following features: * 4 bedrooms, 2 bathrooms and double garage. * Separate formal lounge, sitti..."

---

## Category 10: SALES EVIDENCE

**Coverage**: `100% - Complete`

### Special Note:
1. **[GAP] Note**: "Comparable sales generated from radius search"

### Sub-section: COMPARABLE SALES SUMMARY

2. **Total Comparables**: "48 properties"

#### Price Statistics:
3. **Median Price**: "$985,000"
4. **Mean Price**: "$1,024,000"
5. **Price Range**: "$750,000 - $1,450,000"

#### Sale Date Range:
6. **Overall Period**: "2023-03-15 to 2025-10-28"
7. **Recent 25 Period**: "2024-09-10 to 2025-10-28 (25 sales)"
8. **Recent 50 Period**: "2023-08-05 to 2025-10-28 (48 sales)"

#### Distance Distribution:
9. **Within 500m**: "6 properties"
10. **Within 1km**: "14 properties"
11. **Within 3km**: "38 properties"

#### Property Characteristics:
12. **Property Types**: "42 HOUSE, 6 TOWNHOUSE"
13. **Bedrooms**: "12×3bd, 28×4bd, 8×5bd"
14. **Bathrooms**: "5×1ba, 32×2ba, 11×3ba"

### Sub-section: INDIVIDUAL COMPARABLES

Each comparable has this exact format:

#### Comparable #1:
- **Address**: "12 Settlers Court, Vermont South VIC 3133"
- **Sale Price**: "$1,015,000"
- **Property**: "4bd / 2ba / 2car | HOUSE"
- **Land Area**: "685 m²"
- **Distance**: "0.08 km"
- **Sale Date**: "2025-10-15"

#### Comparable #2:
- **Address**: "23 Hampshire Road, Vermont South VIC 3133"
- **Sale Price**: "$985,000"
- **Property**: "4bd / 2ba / 2car | HOUSE"
- **Land Area**: "650 m²"
- **Distance**: "0.45 km"
- **Sale Date**: "2025-09-28"

#### Comparable #3:
- **Address**: "8 Dorset Road, Vermont South VIC 3133"
- **Sale Price**: "$1,125,000"
- **Property**: "4bd / 3ba / 2car | HOUSE"
- **Land Area**: "720 m²"
- **Distance**: "0.62 km"
- **Sale Date**: "2025-08-10"

**Note**: The PDF shows only 3 comparables explicitly, but the summary states "48 properties" total, so all 48 should be listed individually in the same format.

### Sub-section: SEARCH PARAMETERS

15. **Search Radius**: "5.0 km"

---

## CRITICAL FORMATTING RULES

### Consolidated vs Non-Consolidated Data:

1. **CONSOLIDATED** (comma-separated lists):
   - Raw Geometry X Coordinates
   - Raw Geometry Y Coordinates
   - Vertex Latitudes
   - Vertex Longitudes
   - Vertex Elevations

2. **NOT CONSOLIDATED** (separate entries):
   - Frontage Edge Vertices (shown as separate Vertex 1 and Vertex 2 with individual Latitude/Longitude)

### Coverage Percentages:
- Category 1: 0% - Not captured in source data
- Category 2: 100% - Complete
- Category 3: 75% - Good coverage
- Category 4: 100% - Complete
- Category 5: 100% - Complete
- Category 6: 70% - Partial coverage
- Category 7: 95% - Excellent coverage
- Category 8: 100% - Complete
- Category 9: 100% - Complete
- Category 10: 100% - Complete

### Special Formatting:
- SA1 Codes: Show count, first 5 codes, then "(+ X more)"
- Comparable Sales: List ALL 48 individually as "Comparable #1", "Comparable #2", etc.
- Recent periods: Show both Recent 25 and Recent 50 with sale counts
- Market metrics: Show checkmark (✓) or X (✗) for availability

---

## FOOTER

**Report generated**: "2025-11-10 13:08:52"
**Property ID**: "N/A" (or actual property ID)
