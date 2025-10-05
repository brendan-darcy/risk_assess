# CoreLogic On The Market (OTM) Rental Data Analysis

Analysis of rental market data for **South Coogee, NSW 2034** using CoreLogic Search API endpoint `/search/au/property/locality/{localityId}/otmForRent`.

**Generated:** 2025-09-01 19:32:14  
**Source Property:** 16 Fowler Crescent, South Coogee, NSW, 2034  
**Property ID:** 6255066  
**Locality:** South Coogee (ID: 12763)  

---

## Market Overview

**Total Active Rental Listings:** 13 properties

### Property Type Distribution
- **Houses:** 9 properties (69.2%)
- **Units:** 4 properties (30.8%)

### Bedroom Distribution
- **3 Bedrooms:** 4 properties (30.8%)
- **5 Bedrooms:** 3 properties (23.1%)
- **4 Bedrooms:** 3 properties (23.1%)
- **2 Bedrooms:** 2 properties (15.4%)
- **1 Bedroom:** 1 property (7.7%)

---

## Current Rental Listings

### 1. Unit - 1/2 Hendy Avenue
- **Type:** Unit (Standard)
- **Bedrooms:** 3 | **Bathrooms:** 1 | **Car Spaces:** 2
- **Rent:** $1,100 per week
- **Agent:** Mobin Ahamed, Century 21 Randwick
- **Coordinates:** -33.927, 151.248

### 2. House - 10 Molloy Avenue
- **Type:** House (One Storey / Lowset)
- **Bedrooms:** 5 | **Bathrooms:** 3 | **Car Spaces:** 4 | **Garages:** 4
- **Land Area:** 471 m²
- **Rent:** $2,500 per week ($2590 pw)
- **Agent:** James Daniel, NGFarah Pty Limited
- **Coordinates:** -33.935, 151.255

### 3. House - 131 Malabar Road
- **Type:** House (One Storey / Lowset)
- **Bedrooms:** 3 | **Bathrooms:** 2
- **Land Area:** 439 m²
- **Rent:** $1,295 per week
- **Agent:** Sean Kramer, Wyatt Realty
- **Coordinates:** -33.931, 151.256

### 4. House - 18a Hendy Avenue
- **Type:** House (One Storey / Lowset)
- **Bedrooms:** 3 | **Bathrooms:** 1 | **Car Spaces:** 1
- **Land Area:** 201 m²
- **Rent:** $1,275 per week
- **Agent:** David Ibanez, Belle Property Randwick
- **Listed:** 2024-08-15
- **Coordinates:** -33.928, 151.248

### 5. Unit - 2/142 Malabar Road
- **Type:** Unit (Standard)
- **Bedrooms:** 2 | **Bathrooms:** 1 | **Car Spaces:** 2
- **Status:** **Deposit Taken**
- **Agent:** Peter Gribilas, Power Property
- **Coordinates:** -33.931, 151.256

### 6. Studio - 216s Malabar Road
- **Type:** Unit (Studio)
- **Bedrooms:** 1 | **Bathrooms:** 1
- **Land Area:** 166 m²
- **Rent:** $395 per week
- **Agent:** Paris Kritikos
- **Coordinates:** -33.934, 151.258

### 7. House - 22 Cedar Place
- **Type:** House (One Storey / Lowset)
- **Bedrooms:** 4 | **Bathrooms:** 2 | **Car Spaces:** 2 | **Garages:** 2
- **Land Area:** 368 m²
- **Rent:** $1,450 per week
- **Agent:** Raphael Djohan, Ray White Kingsford
- **Available:** 2025-01-15
- **Coordinates:** -33.934, 151.251

### 8. House - 24 Cuzco Street
- **Type:** House (One Storey / Lowset)
- **Bedrooms:** 3 | **Bathrooms:** 1
- **Land Area:** 367 m²
- **Rent:** $1,950 per week
- **Agent:** James Papachristou
- **Listed:** 2024-04-19
- **Coordinates:** -33.934, 151.260

### 9. House - 28 Tucabia Street
- **Type:** House
- **Bedrooms:** 4 | **Bathrooms:** 2 | **Car Spaces:** 4 | **Garages:** 2
- **Land Area:** 578 m²
- **Rent:** $1,500 per week
- **Agent:** Eleni Roumanous, Agents and Co Property Group
- **Coordinates:** -33.936, 151.254

### 10. Unit - 3/231 Malabar Road
- **Type:** Unit (Standard)
- **Bedrooms:** 2 | **Bathrooms:** 1
- **Rent:** $880 per week
- **Agency:** NGFarah
- **Available:** 2025-06-19
- **Coordinates:** Not available

### 11. House - 30 Denning Street
- **Type:** House (One Storey / Lowset)
- **Bedrooms:** 5 | **Bathrooms:** 3 | **Car Spaces:** 1 | **Garages:** 1
- **Land Area:** 422 m²
- **Rent:** $2,700 per week
- **Agency:** Belle Property Randwick
- **Available:** 2025-06-19
- **Coordinates:** -33.930, 151.257

### 12. House - 47 Denning Street
- **Type:** House (One Storey / Lowset)
- **Bedrooms:** 4 | **Bathrooms:** 2 | **Car Spaces:** 1 | **Garages:** 1
- **Land Area:** 592 m²
- **Rent:** $2,700 per week
- **Agent:** Property Now
- **Coordinates:** -33.932, 151.259

### 13. House - 9 Denning Street
- **Type:** House (One Storey / Lowset)
- **Bedrooms:** 5 | **Bathrooms:** 3 | **Car Spaces:** 2 | **Garages:** 2
- **Land Area:** 398 m²
- **Rent:** $5,000 per week
- **Agent:** Asha Askarly, The Property Edit
- **Coordinates:** -33.929, 151.258

---

## Rental Price Analysis

### Weekly Rent Range
- **Minimum:** $395 (1BR studio)
- **Maximum:** $5,000 (5BR house)

### Price by Property Type
- **Houses:** $1,275 - $5,000 per week
- **Units:** $395 - $1,100 per week

### Geographic Concentration
Most rental properties are concentrated along:
- **Malabar Road** (4 properties)
- **Denning Street** (3 properties)
- **Hendy Avenue** (2 properties)

---

## API Technical Details

**Endpoint Used:** `/search/au/property/locality/12763/otmForRent`  
**Maximum Page Size:** 20 results  
**Total Results Retrieved:** 13 properties  

### Data Fields Available
Each rental listing includes:
- Property address and coordinates
- Property attributes (bedrooms, bathrooms, car spaces, land area)
- Rental pricing and descriptions
- Agency and agent information
- Property photos (thumbnail, medium, large)
- Property status and campaign details
- Location identifiers (council, locality, postcode, street IDs)

---

## Usage Example

```bash
# Basic rental lookup
python3 scripts/rental_lookup.py --address "16 Fowler Crescent, South Coogee, NSW, 2034"

# Filter by property characteristics
python3 scripts/rental_lookup.py --address "Your Address" --bedrooms 3 --property-type HOUSE

# Include last sale data with indexation analysis
python3 scripts/rental_lookup.py --address "Your Address" --include-last-sale --date-to "2024-12-31"

# Use address from file
python3 scripts/rental_lookup.py --address-file addresses.txt --output custom_report.json
```

---

## API Reference

### Endpoint
**GET** `/search/au/property/locality/{localityId}/otmForRent`

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `method` | string | Listing method filter: `S` (Normal Sale), `A` (Auction), `T` (Tender), `M` (Mortgagee Sale), `MA` (Mortgagee Auction), `O` (Offers) |
| `activeCampaign` | boolean | Filter for active OTM campaigns only (`true`/`false`) |
| `date` | string | Advertisement date filter in `YYYYMMDD` format<br/>• Exact: `20160101`<br/>• Range: `20151201-20151231`<br/>• From: `20160101-`<br/>• Until: `-20160101`<br/>**Note:** Date filtering appears to be non-functional in current API |
| `price` | string/integer | Weekly rent filter<br/>• Exact: `500`<br/>• Range: `400-600`<br/>• Minimum: `350-`<br/>• Maximum: `-500` |
| `beds` | string/integer | Bedroom count filter<br/>• Exact: `3`<br/>• Range: `2-4`<br/>• Minimum: `3-`<br/>• Maximum: `-4` |
| `baths` | string/integer | Bathroom count filter (same format as beds) |
| `carSpaces` | string/integer | Car spaces filter (same format as beds) |
| `landArea` | string/integer | Land area in m² filter (same format as beds) |
| `pTypes` | string | Property type filter: `HOUSE`, `UNIT`, `BUSINESS`, `COMMERCIAL`, `COMMUNITY`, `FARM`, `FLATS`, `LAND`, `OTHER`, `STORAGE_UNIT`<br/>Multiple values: comma-separated |
| `sort` | string | Sort criteria: `beds`, `baths`, `carSpaces`, `landArea`, `pType`<br/>Order: `asc` or `desc`<br/>Example: `beds,desc` |
| `size` | integer | Results per page (max 20, default 20) |
| `page` | integer | Page number (0-indexed, default 0) |
| `includeHistoric` | boolean | Include historic listings |

### Response Codes

| Code | Description |
|------|-------------|
| 200 | OK - Results returned |
| 400 | Bad Request - Invalid parameters or locationId |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Internal Server Error |
| 502 | Bad Gateway |

### Response Structure

The API returns paginated results with the following structure:
- `_embedded.propertySummaryList[]` - Array of rental properties
- `_links` - HATEOAS navigation links  
- `page` - Pagination metadata (number, size, totalElements, totalPages)

*This analysis was generated using the CoreLogic Search API and processed by the custom rental_lookup.py script. Data is current as of the timestamp shown and reflects active rental campaigns in the CoreLogic database.*