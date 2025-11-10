# Comparable Sales Generator

Utility for generating JSON output of comparable sales data with configurable radius search. **Default radius: 5km**.

## Overview

The Comparable Sales Generator (`comparable_sales_generator.py`) consolidates functionality from `comparable_data_processor.py` and `comparable_processor.py` into a simple-to-use utility focused on JSON output.

## Key Features

- **Default 5km radius** search
- **JSON output format** (not CSV)
- Search by property ID or coordinates
- Configurable filters (price, beds, baths, property type, etc.)
- Automatic pagination (retrieves all pages by default)
- Includes statistics and metadata
- Can be used as a script or Python module

## Installation

No additional dependencies beyond the existing project requirements:
```bash
pip install pandas requests
```

## Usage

### Command Line

#### 1. Search by Property ID (Default 5km)

```bash
python3 scripts/utils/comparable_sales_generator.py --property-id 13683380
```

Output:
```
🔍 Searching comparable sales for property ID: 13683380
📏 Radius: 5.0km
📄 Page 1/3: 20 properties
📄 Page 2/3: 20 properties
📄 Page 3/3: 15 properties
✅ Found 55 comparable sales
💾 Saved to: data/comparable_sales/comparable_sales_13683380_20251110_123456.json
```

#### 2. Search by Property ID with Custom Radius

```bash
python3 scripts/utils/comparable_sales_generator.py --property-id 13683380 --radius 10
```

#### 3. Search by Coordinates

```bash
python3 scripts/utils/comparable_sales_generator.py --lat -37.8136 --lon 145.1772 --radius 5
```

#### 4. With Filters

```bash
python3 scripts/utils/comparable_sales_generator.py --property-id 13683380 \
    --price "500000-1000000" \
    --beds "3-4" \
    --baths "2-3" \
    --property-types HOUSE \
    --radius 5
```

#### 5. Custom Output File

```bash
python3 scripts/utils/comparable_sales_generator.py --property-id 13683380 \
    --output data/property_reports/13683380_comparable_sales.json
```

### Python Module

#### Example 1: Simple Usage

```python
from scripts.utils.comparable_sales_generator import generate_comparable_sales_json

# Search by property ID (default 5km)
data, file_path = generate_comparable_sales_json(property_id="13683380")

print(f"Found {data['metadata']['total_comparables']} comparables")
print(f"Saved to: {file_path}")
```

#### Example 2: With Filters

```python
from scripts.utils.comparable_sales_generator import generate_comparable_sales_json, ComparableSalesGenerator

# Create generator
generator = ComparableSalesGenerator()

# Create filters
filters = generator.create_filters(
    price="500000-1000000",
    beds="3-4",
    baths="2-3",
    property_types=["HOUSE"],
    date="20230101-"  # Sales from 2023 onwards
)

# Search with filters
data, file_path = generate_comparable_sales_json(
    property_id="13683380",
    radius=5.0,
    filters=filters
)

# Access statistics
stats = data['statistics']
if 'price_statistics' in stats:
    print(f"Median price: ${stats['price_statistics']['median']:,.0f}")
    print(f"Mean price: ${stats['price_statistics']['mean']:,.0f}")
```

#### Example 3: Advanced Usage

```python
from scripts.utils.comparable_sales_generator import ComparableSalesGenerator

generator = ComparableSalesGenerator()

# Search by coordinates
data = generator.search_comparables_by_coordinates(
    lat=-37.8136,
    lon=145.1772,
    radius=5.0,
    filters={"price": "800000-1200000", "beds": "4"},
    get_all_pages=True,
    max_results=100  # Limit to 100 results
)

# Save to custom location
file_path = generator.save_to_json(
    data,
    output_file="data/custom_comparables.json"
)

# Access comparable sales
for sale in data['comparable_sales']:
    print(f"{sale['address']}: ${sale['salePrice']:,.0f}")
```

## Output Format

### JSON Structure

```json
{
  "metadata": {
    "generated_at": "2025-11-10T12:34:56",
    "generator_version": "1.0",
    "search_type": "property_id",
    "search_parameters": {
      "property_id": "13683380",
      "radius": 5.0,
      "filters": {}
    },
    "total_comparables": 55,
    "default_radius_km": 5.0
  },
  "statistics": {
    "total_count": 55,
    "price_statistics": {
      "median": 920000,
      "mean": 945000,
      "min": 750000,
      "max": 1200000,
      "std_dev": 125000,
      "q1": 850000,
      "q3": 1050000,
      "count": 55
    },
    "property_characteristics": {
      "beds": {
        "distribution": {"3": 15, "4": 30, "5": 10},
        "most_common": "4"
      },
      "propertyType": {
        "distribution": {"HOUSE": 50, "TOWNHOUSE": 5},
        "most_common": "HOUSE"
      }
    },
    "date_range": {
      "earliest": "2023-01-15",
      "latest": "2025-10-30",
      "count": 55
    },
    "distance_distribution": {
      "within_500m": 8,
      "within_1km": 15,
      "within_3km": 42,
      "total": 55
    },
    "recent_25_date_range": {
      "earliest": "2024-08-10",
      "latest": "2025-10-30",
      "count": 25
    },
    "recent_50_date_range": {
      "earliest": "2024-01-05",
      "latest": "2025-10-30",
      "count": 50
    }
  },
  "comparable_sales": [
    {
      "propertyId": 12345678,
      "address": "10 Example Street, Suburb VIC 3133",
      "salePrice": 920000,
      "lastSaleDate": "2025-05-15",
      "beds": 4,
      "baths": 2,
      "carSpaces": 2,
      "landArea": 650,
      "propertyType": "HOUSE",
      ...
    },
    ...
  ]
}
```

## Statistics Explained

The comparable sales generator automatically calculates comprehensive statistics:

### Price Statistics
- **median**: Median sale price
- **mean**: Average sale price
- **min/max**: Lowest and highest sale prices
- **std_dev**: Standard deviation of prices
- **q1/q3**: First and third quartiles (25th and 75th percentiles)
- **count**: Number of properties with sale prices

### Property Characteristics
Distribution and most common values for:
- **beds**: Bedroom count
- **baths**: Bathroom count
- **carSpaces**: Car spaces
- **propertyType**: Property type (HOUSE, UNIT, etc.)

### Date Range (Overall)
- **earliest**: Oldest sale date in the dataset
- **latest**: Most recent sale date in the dataset
- **count**: Number of properties with sale dates

### Distance Distribution
Number of comparables within specific distance bands:
- **within_500m**: Comparables within 500 meters
- **within_1km**: Comparables within 1 kilometer
- **within_3km**: Comparables within 3 kilometers
- **total**: Total number of comparables with distance data

### Recent Comparables Date Ranges
Date ranges for the most recent sales (useful for market trend analysis):
- **recent_25_date_range**: Date range for the 25 most recent sales
- **recent_50_date_range**: Date range for the 50 most recent sales

Each includes:
- **earliest**: Oldest date in the subset
- **latest**: Most recent date in the subset
- **count**: Number of sales in the subset

## Available Filters

### Create Filters

```python
filters = generator.create_filters(
    price="500000-1000000",      # Price range
    date="20230101-20231231",    # Date range (YYYYMMDD)
    beds="3-4",                  # Bedroom range
    baths="2-3",                 # Bathroom range
    car_spaces="2",              # Car spaces
    land_area="600-1000",        # Land area in m²
    property_types=["HOUSE", "TOWNHOUSE"],  # Property types
    source="AA",                 # Data source (AA, ALL, VG)
    include_historic=False       # Include historic sales
)
```

### Filter Syntax

| Filter | Example | Description |
|--------|---------|-------------|
| **Exact value** | `"4"` | Exactly 4 |
| **Range** | `"3-5"` | Between 3 and 5 inclusive |
| **Greater than** | `"3-"` | 3 or more |
| **Less than** | `"-5"` | 5 or less |

## Property Types

Available property types:
- `HOUSE` - Detached house
- `UNIT` - Unit/apartment
- `TOWNHOUSE` - Townhouse
- `LAND` - Vacant land
- `APARTMENT` - Apartment
- `VILLA` - Villa
- `DUPLEX` - Duplex
- `TERRACE` - Terrace
- `FLAT` - Flat

## Configuration

### Default Settings

```python
ComparableSalesGenerator.DEFAULT_RADIUS = 5.0  # Default radius in km
ComparableSalesGenerator.DEFAULT_OUTPUT_DIR = "data/comparable_sales"
```

### Using with Pipeline Infrastructure

If `pipeline_utils` is available, the generator uses the authenticated pipeline:

```python
# Automatic authentication using pipeline
generator = ComparableSalesGenerator()
```

### Standalone Mode

For standalone use without pipeline:

```python
from scripts.utils.comparable_sales_generator import ComparableSalesGenerator

generator = ComparableSalesGenerator(use_pipeline=False)
generator.set_access_token("your_access_token_here")

# Now use normally
data = generator.search_comparables_by_property_id("13683380")
```

## Command-Line Options

```
usage: comparable_sales_generator.py [-h] (--property-id PROPERTY_ID | --lat LAT)
                                      [--lon LON] [--radius RADIUS]
                                      [--price PRICE] [--date DATE] [--beds BEDS]
                                      [--baths BATHS] [--car-spaces CAR_SPACES]
                                      [--land-area LAND_AREA]
                                      [--property-types PROPERTY_TYPES [PROPERTY_TYPES ...]]
                                      [--source SOURCE] [--output OUTPUT]
                                      [--single-page] [--max-results MAX_RESULTS]

Search Parameters:
  --property-id         CoreLogic property ID
  --lat                 Latitude for coordinate search
  --lon                 Longitude (required with --lat)
  --radius             Search radius in km (default: 5.0)

Filters:
  --price              Price filter (e.g., '500000-1000000')
  --date               Date filter YYYYMMDD (e.g., '20230101-20231231')
  --beds               Bedroom count (e.g., '3-4')
  --baths              Bathroom count (e.g., '2-3')
  --car-spaces         Car spaces (e.g., '2')
  --land-area          Land area in m² (e.g., '600-1000')
  --property-types     Property types (e.g., HOUSE UNIT)
  --source             Data source (default: AA)

Output Options:
  --output, -o         Output JSON file path
  --single-page        Retrieve only first page (default: all pages)
  --max-results        Maximum results to retrieve
```

## Integration with Report Generation

To integrate comparable sales into the property report:

### 1. Generate Comparable Sales JSON

```bash
python3 scripts/utils/comparable_sales_generator.py \
    --property-id 13683380 \
    --radius 5 \
    --output data/property_reports/13683380_comparable_sales.json
```

### 2. Add to Categorized Report

Edit `scripts/categorize_report.py`:

```python
# Load comparable sales if available
comparable_sales_file = Path(f"data/property_reports/{property_id}_comparable_sales.json")
comparable_sales = {}
if comparable_sales_file.exists():
    with open(comparable_sales_file) as f:
        comparable_sales = json.load(f)

# Add to category 10
"10_sales_evidence": {
    "category_name": "Sales Evidence",
    "coverage": "100% - Complete",
    "data": {
        "comparable_sales": comparable_sales.get('comparable_sales', []),
        "statistics": comparable_sales.get('statistics', {}),
        "search_metadata": comparable_sales.get('metadata', {})
    }
}
```

### 3. Generate Final PDF

```bash
python3 scripts/categorize_report.py \
    --input data/property_reports/13683380_ultra_comprehensive_report.json \
    --output data/property_reports/13683380_categorized.json \
    --pretty

python3 scripts/generate_property_pdf.py \
    --input data/property_reports/13683380_categorized.json \
    --ultra-comprehensive \
    --output data/property_reports/13683380_final.pdf
```

## Complete Workflow Example

```bash
#!/bin/bash
# Complete property analysis workflow with comparable sales

PROPERTY_ID="13683380"
RADIUS=5  # km

# Step 1: Generate ultra-comprehensive JSON
python3 scripts/generate_ultra_comprehensive_json.py \
    --property-id $PROPERTY_ID \
    --pretty

# Step 2: Generate comparable sales
python3 scripts/utils/comparable_sales_generator.py \
    --property-id $PROPERTY_ID \
    --radius $RADIUS \
    --price "500000-1500000" \
    --beds "3-5" \
    --output data/property_reports/${PROPERTY_ID}_comparable_sales.json

# Step 3: Categorize report (includes comparable sales)
python3 scripts/categorize_report.py \
    --input data/property_reports/${PROPERTY_ID}_ultra_comprehensive_report.json \
    --output data/property_reports/${PROPERTY_ID}_categorized.json \
    --pretty

# Step 4: Generate final PDF
python3 scripts/generate_property_pdf.py \
    --input data/property_reports/${PROPERTY_ID}_categorized.json \
    --ultra-comprehensive \
    --output data/property_reports/${PROPERTY_ID}_final.pdf

echo "✅ Complete property analysis ready: data/property_reports/${PROPERTY_ID}_final.pdf"
```

## Troubleshooting

### Issue: "Access token not set"
**Solution**: Ensure `pipeline_utils` is available or set access token manually:
```python
generator.set_access_token("your_token_here")
```

### Issue: "No comparable properties found"
**Solutions**:
- Increase radius (default is 5km, try 10km or 20km)
- Remove or loosen filters
- Check that property location is valid

### Issue: "API request failed"
**Solutions**:
- Check internet connection
- Verify API credentials
- Check CoreLogic API status

## Files Created

- **`scripts/utils/comparable_sales_generator.py`** - Main generator script
- **`scripts/utils/README_COMPARABLE_SALES.md`** - This documentation

## Comparison with Existing Scripts

| Feature | `comparable_processor.py` | `comparable_data_processor.py` | `comparable_sales_generator.py` |
|---------|---------------------------|-------------------------------|--------------------------------|
| **Output Format** | CSV | CSV | **JSON** ✅ |
| **Default Radius** | None | None | **5km** ✅ |
| **Statistics** | No | Yes | **Yes** ✅ |
| **CLI Support** | No | No | **Yes** ✅ |
| **Pipeline Integration** | No | Yes | **Yes** ✅ |
| **Standalone Use** | Yes | No | **Yes** ✅ |
| **Auto Pagination** | Optional | Optional | **Default** ✅ |

---

**Version**: 1.0
**Last Updated**: 2025-11-10
**Author**: Comparable Sales Utility
