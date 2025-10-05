# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Risk assessment system for Australian properties using CoreLogic APIs for property data, geospatial services, and market analysis. The codebase focuses on building reusable pipeline classes for API integration with lightweight CLI script wrappers.

## Core Architecture

### Pipeline-First Design Pattern

**All business logic lives in pipeline classes, not scripts.** Scripts are minimal CLI wrappers (typically <100 lines) that:
1. Parse command-line arguments
2. Initialize pipeline processors with reporters
3. Call pipeline methods
4. Output results

When creating new functionality:
- Add methods to existing pipeline classes (`property_data_processor.py`, `geospatial_api_client.py`, etc.)
- Create lightweight scripts in `scripts/` directory that call these methods
- Use existing scripts like `get_parcel_polygon.py` as templates

### Class Hierarchy

```
BasePipeline (ABC)
├── AuthenticatedPipeline
│   ├── PropertyDataProcessor
│   ├── MarketDataProcessor (referenced in imports)
│   └── DataProcessingPipeline
└── PipelineConfig, ProgressReporter, FileManager (utilities)
```

All pipelines requiring CoreLogic API access inherit from `AuthenticatedPipeline`, which handles:
- OAuth2 token management via `CoreLogicAuth`
- API client initialization with `CoreLogicAPIClient`
- Automatic token refresh on instantiation

### Directory Structure

```
risk_assess/
├── pipelines/                     # Reusable pipeline classes and utilities
│   ├── corelogic_auth.py         # OAuth2 authentication
│   ├── geospatial_api_client.py  # Geospatial API wrapper (property boundaries, hazards, infrastructure)
│   ├── property_data_processor.py # Property data operations (address resolution, sales history, rentals)
│   └── pipeline_utils.py         # Base classes, utilities, API client, error handling
├── scripts/                       # Executable CLI scripts (lightweight wrappers)
│   ├── get_parcel_polygon.py     # Get property polygon geometry with locality IDs
│   └── run_places_analysis.py    # Google Places impact analysis for properties
├── documentation/                 # API documentation and guides
│   ├── CLAUDE.md                 # This file - development guide for Claude Code
│   ├── geospatial_api.md         # Complete geospatial API documentation
│   └── claude_template.md        # Template for Python API integration specialist
├── notebooks/                     # Jupyter notebooks for exploration and analysis
│   └── shape.ipynb               # Shapefile analysis example
├── data/
│   ├── raw/                      # Input data (shapefiles, addresses, property lists, etc.)
│   └── outputs/                  # Generated results and outputs (CSV, JSON, images)
├── .env                          # Environment variables (not in git)
└── README.md                     # Quick start guide
```

## Key Pipeline Classes

### CoreLogicAuth (`pipelines/corelogic_auth.py`)
OAuth2 token management for CoreLogic APIs.

**Usage:**
```python
from corelogic_auth import CoreLogicAuth
auth = CoreLogicAuth.from_env()  # Reads CORELOGIC_CLIENT_ID and CORELOGIC_CLIENT_SECRET
token = auth.get_access_token()
```

### PropertyDataProcessor (`pipelines/property_data_processor.py`)
Comprehensive property data operations extending `AuthenticatedPipeline`.

**Key Methods:**
- `get_property_id_from_address(address)` - Resolve address to property ID
- `get_property_info_from_address(address)` - Get property ID with locality_id, suburb, state, postcode, LGA info
- `get_comprehensive_property_data(property_id)` - Get all property details
- `get_property_sales_history(property_id)` - Retrieve sales transactions
- `process_single_address(address)` - Full property processing pipeline
- `process_addresses_batch(addresses)` - Bulk address processing with error handling
- `get_locality_rental_listings(locality_id, filters)` - Fetch rental data with fallback to council area
- `add_indexation_to_rental_properties(rental_listings, locality_id, market_processor)` - Add AVM indexation to rentals

### GooglePlacesPipeline (`pipelines/google_places_pipeline.py`)
Complete pipeline for Google Places API impact analysis around properties.

**Key Features:**
- Multi-level radius searches (3km, 600m, 250m, 100m)
- Categorizes places by impact level (airports, industrial, retail noise, fuel, etc.)
- Batched API requests for efficiency (reduces API calls)
- Deduplication of place results
- Distance verification using geodesic calculations
- Comprehensive statistics and gap analysis

**Level Configuration:**
- Level 1 (3km): Major disruptions (airports)
- Level 2 (600m): Industrial & environmental, retail noise
- Level 3 (250m): Fuel stations, transit, medical, education, religious
- Level 4 (100m): All places (no type filter)

**Usage:**
```python
from google_places_pipeline import GooglePlacesPipeline
from pipeline_utils import PipelineConfig, ProgressReporter

config = PipelineConfig()
config.set('output_dir', 'data/places_analysis')
reporter = ProgressReporter("Places Analysis")
pipeline = GooglePlacesPipeline(config, reporter)
results = pipeline.run("123 Main St, Sydney NSW")
```

### MeshBlockAnalysisPipeline (`pipelines/mesh_block_analysis_pipeline.py`)
Pipeline for analyzing Australian Statistical Geography Standard (ASGS) mesh blocks in relation to property locations.

**Key Features:**
- Load ASGS mesh block shapefiles (MB_2021_AUST_GDA2020)
- Identify which mesh block contains a property
- Find all mesh blocks within a radius buffer (with accurate metric CRS)
- Export results to multiple formats (GeoJSON, CSV, Shapefile, TXT)
- Calculate summary statistics by mesh block category
- Support for coordinate reference system transformations

**Key Methods:**
- `load_mesh_blocks()` - Load shapefile data
- `load_property_from_parcel(parcel_json_path)` - Load property from parcel.json
- `create_property_gdf(longitude, latitude)` - Create property GeoDataFrame
- `identify_property_meshblock()` - Find containing mesh block
- `find_nearby_meshblocks()` - Find mesh blocks within buffer distance
- `export_results(output_dir)` - Export to multiple formats
- `get_summary_statistics()` - Get category counts and statistics
- `run_full_analysis(parcel_json, output_dir)` - Complete workflow

**Usage:**
```python
from mesh_block_analysis_pipeline import MeshBlockAnalysisPipeline

analysis = MeshBlockAnalysisPipeline(
    shapefile_path="data/raw/MB_2021_AUST_GDA2020.shp",
    buffer_distance=2000  # 2km radius
)
results = analysis.run_full_analysis(
    parcel_json_path="data/outputs/parcel.json",
    output_dir="data/outputs"
)
```

### SpatialVisualizationPipeline (`pipelines/spatial_visualization_pipeline.py`)
Pipeline for creating publication-quality maps and spatial visualizations.

**Key Features:**
- Visualize mesh blocks with color-coded categories
- Plot property locations with custom markers
- Display buffer zones and boundaries
- Overlay Google Places impact data with labels
- Generate comprehensive legends with counts
- Export high-resolution maps (PNG)

**Default Color Scheme:**
- Residential: Pale yellow (#FFFACD)
- Commercial: Sky blue (#87CEEB)
- Industrial: Light grey (#D3D3D3)
- Parkland: Light green (#90EE90)
- Education: Light pink (#FFB6C1)
- Transport: Orange (#FFA500)

**Key Methods:**
- `load_places_from_json(places_json_path)` - Load Google Places data
- `create_map(mesh_blocks, property_point, buffer, places)` - Create visualization
- `save_map(output_path)` - Export map to file
- `print_summary(mesh_blocks, places)` - Print category statistics
- `create_complete_visualization()` - One-call complete workflow

**Usage:**
```python
from spatial_visualization_pipeline import SpatialVisualizationPipeline

viz = SpatialVisualizationPipeline(figsize=(14, 12), dpi=200)
map_path = viz.create_complete_visualization(
    mesh_blocks=mesh_blocks_gdf,
    property_point=property_gdf,
    property_buffer=buffer_geometry,
    output_path="data/outputs/map.png",
    places_json_path="data/places_analysis/property_impacts.json",
    title="Property Risk Analysis Map"
)
```

### GeospatialAPIClient (`pipelines/geospatial_api_client.py`)
Wrapper for CoreLogic Geospatial API, inherits from `CoreLogicAuth`.

**Key Methods:**
- `query(layer, where, geometry)` - Query geospatial layers for feature data
- `export_map(layer, bbox)` - Generate map images from layers
- `get_parcel_polygon(property_id)` - Get property boundary geometry
- `get_property_boundaries(bbox, property_id)` - Get property boundaries for area
- `get_hazard_data(bbox, hazard_type)` - Get bushfire/flood/heritage overlays
- `get_easement_data(bbox, state)` - Query easement data with spatial intersection
- `query_infrastructure_features(property_id, infrastructure_type, state)` - Infrastructure near property
- `test_connection()` - Verify API connectivity

**Initialization:**
```python
from geospatial_api_client import GeospatialAPIClient
geo_client = GeospatialAPIClient.from_env()  # Uses environment variables
```

### CoreLogicAPIClient (`pipelines/pipeline_utils.py`)
Generic API client for CoreLogic REST endpoints.

**Key Features:**
- Automatic retry with exponential backoff
- Rate limiting handling
- Comprehensive error messages
- Paginated request support via `paginated_request(endpoint, params, max_pages)`
- Property details fetching with selective endpoints

### Utility Functions

**Indexation (`pipelines/pipeline_utils.py`):**
- `index_value_to_date(transaction_value, transaction_date, target_date, index_series)` - Index property values using AVM series

**Progress Reporting:**
All pipelines use `ProgressReporter` for consistent output formatting with emoji indicators (✅ success, ❌ error, ⚠️ warning, 📊 info).

## Authentication & Environment

**CoreLogic API credentials** must be set in environment variables:
```bash
export CORELOGIC_CLIENT_ID="your_client_id"
export CORELOGIC_CLIENT_SECRET="your_client_secret"
```

**Google Places API key** (for places analysis):
```bash
export GOOGLE_API_KEY="your_google_api_key"
```

Or use `.env` file (loaded by `python-dotenv`):
```
CORELOGIC_CLIENT_ID=your_client_id
CORELOGIC_CLIENT_SECRET=your_client_secret
GOOGLE_API_KEY=your_google_api_key
```

**UAT Environment:**
- Base URL: `https://api-uat.corelogic.asia`
- Token endpoint: `https://access-uat-api.corelogic.asia/access/oauth/token`
- Access limited to business hours (7AM-7PM)

## Common Development Commands

### Run Example Scripts

**Get Property Parcel Polygon:**
```bash
# From repository root - with address (includes locality_id and coordinates)
python scripts/get_parcel_polygon.py --address "123 Main St, Sydney NSW 2000" --pretty

# With property_id only (no locality info)
python scripts/get_parcel_polygon.py --property-id 1778890 --output data/outputs/parcel.json

# Save to file with locality information and lat/long
python scripts/get_parcel_polygon.py --address "3 Nymboida Street, South Coogee, NSW, 2034" --output data/outputs/parcel.json --pretty
```

**Google Places Impact Analysis:**
```bash
# Analyze nearby places (airports, industrial, retail, fuel, etc.)
python scripts/run_places_analysis.py --address "5 settlers court, vermont south, vic, 3133"

# Custom output directory
python scripts/run_places_analysis.py --address "248 Coward St, Mascot NSW 2020" --output-dir data/outputs/mascot_places

# Requires GOOGLE_API_KEY environment variable
export GOOGLE_API_KEY="your_api_key_here"
```

**Mesh Block Analysis (End-to-End):**
```bash
# Direct from address - complete end-to-end analysis
python scripts/run_mesh_block_analysis.py --address "5 Settlers Court, Vermont South VIC 3133"

# With property ID
python scripts/run_mesh_block_analysis.py --property-id 13683380

# Include Google Places analysis in same run
python scripts/run_mesh_block_analysis.py --address "123 Main St, Sydney NSW" --include-places

# Custom buffer distance (5km instead of default 2km)
python scripts/run_mesh_block_analysis.py --address "123 Main St" --buffer 5000

# Prerequisites:
# - MB_2021_AUST_GDA2020.shp in data/raw/
# - CORELOGIC_CLIENT_ID and CORELOGIC_CLIENT_SECRET in environment
# - GOOGLE_API_KEY in environment (if using --include-places)

# Outputs:
# - data/outputs/meshblocks_within_*m.geojson
# - data/outputs/meshblocks_within_*m.csv
# - data/outputs/meshblocks_within_*m.shp
# - data/outputs/meshblock_codes_*m.txt
# - data/outputs/meshblocks_map.png (with places overlay if included)
```

### Get Authentication Details
```bash
grep -E "CLIENT_ID|CLIENT_SECRET" .env | cut -d'"' -f2
```

### Test API Connection
```python
from geospatial_api_client import GeospatialAPIClient
client = GeospatialAPIClient.from_env()
result = client.test_connection()
print(result)
```

## API Integration Patterns

### Google Places Analysis Workflow
```python
from google_places_pipeline import GooglePlacesPipeline
from pipeline_utils import PipelineConfig, ProgressReporter

# Setup
config = PipelineConfig()
config.set('output_dir', 'data/outputs/places_analysis')
reporter = ProgressReporter("Places Analysis")

# Run pipeline
pipeline = GooglePlacesPipeline(config, reporter)
results = pipeline.run("3 Nymboida Street, South Coogee, NSW, 2034")

# Output files created:
# - search_results_by_level.json   (all places found per level)
# - property_impacts.json          (closest place per category)
# - statistics.json                (summary metrics)
```

**Output Structure:**
- **Level 1 (3km)**: Airports and major disruptions
- **Level 2 (600m)**: Industrial facilities, nightlife, retail noise
- **Level 3 (250m)**: Fuel stations, transit, medical, education
- **Level 4 (100m)**: All nearby places (no filter)

### Property Lookup Workflow
```python
from property_data_processor import PropertyDataProcessor
from pipeline_utils import ProgressReporter

reporter = ProgressReporter("Property Lookup")
processor = PropertyDataProcessor(reporter=reporter)

# Get property ID only
property_id = processor.get_property_id_from_address("1 Martin Place, Sydney NSW")

# Get property ID with locality information
property_info = processor.get_property_info_from_address("1 Martin Place, Sydney NSW")
# Returns: {property_id, locality_id, suburb, state, postcode, lga_id, lga_name, ...}

# Single address processing
data, success = processor.process_single_address("1 Martin Place, Sydney NSW")

# Batch processing
addresses = ["address1", "address2", "address3"]
df, processed, failed = processor.process_addresses_batch(
    addresses,
    output_file="data/outputs/results.csv",
    delay=0.1
)
```

### Geospatial Query Workflow
```python
from geospatial_api_client import GeospatialAPIClient

geo_client = GeospatialAPIClient.from_env()

# Get property polygon
parcel_data = geo_client.get_parcel_polygon(property_id="1778890")
result = geo_client.format_parcel_result(property_id, address, parcel_data)

# Query infrastructure near property
infrastructure = geo_client.query_infrastructure_features(
    property_id="1778890",
    infrastructure_type="electricTransmissionLines",
    state="nsw"
)

# Get hazard overlays
bushfire = geo_client.get_hazard_data(bbox="xmin,ymin,xmax,ymax", hazard_type="bushfire")
```

### Rental Analysis with Indexation
```python
from property_data_processor import PropertyDataProcessor

processor = PropertyDataProcessor()

# Get rental listings with fallback
rental_data = processor.get_locality_rental_listings(
    locality_id=200840,
    filters={'bedrooms': 3, 'date_from': '2022-01-01', 'date_to': '2022-12-31'},
    include_last_sale=True,
    council_area_id=12345
)

# Add indexation using market data
enriched_rentals = processor.add_indexation_to_rental_properties(
    rental_listings=rental_data['rental_listings'],
    locality_id=200840,
    market_processor=market_processor,
    target_date='2022-03-31'
)
```

## Geospatial API Reference

See [documentation/geospatial_api.md](geospatial_api.md) for comprehensive documentation. Key services:

**Property Services:**
- Property boundaries (all/select)
- Property labels (address, beds/baths, land size, last sale)
- Parcel overlays and dimensions

**Hazard Services:**
- Bushfire risk zones
- Flood overlays
- Heritage listings

**Infrastructure:**
- Electricity transmission lines, substations, power stations
- Railway, ferry, streets
- State-specific water and soil data

**Environmental:**
- Native vegetation overlays
- Regulated vegetation (NSW, QLD, VIC, WA)
- Land use classifications
- Easements (spatial intersection queries)

**Query Patterns:**
```
# Export map image
GET /geospatial/au/overlays/{layer}?bbox={coords}&format=png32&f=image&access_token={token}

# Query features
GET /geospatial/au/{state}/geometry/{layer}?where=property_id={id}&f=json&access_token={token}

# Planning aggregations (state-specific)
GET /geospatial/au/{state}/planningAggregations/{type}?where=property_id={id}&f=json&access_token={token}
```

## Error Handling Patterns

All pipelines use standardized error handling via `ErrorHandler` class:

```python
error_handler = ErrorHandler()

for item in items:
    try:
        result = process(item)
        error_handler.handle_item_success(item, result)
    except Exception as e:
        error_handler.handle_item_error(item, e)

summary = error_handler.get_summary()
# Returns: total_items, processed_count, failed_count, success_rate, errors list
```

## Creating New Scripts

1. **Add functionality to pipeline class first:**
```python
# In pipelines/geospatial_api_client.py
def new_feature(self, param1, param2):
    """Your method implementation"""
    response = self.query(...)
    return self.format_result(response)
```

2. **Create lightweight script:**
```python
#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

# Standard import pattern
sys.path.append(str(Path(__file__).parent.parent / 'pipelines'))
from geospatial_api_client import GeospatialAPIClient
from pipeline_utils import ProgressReporter

def main():
    parser = argparse.ArgumentParser(description='Your script description')
    parser.add_argument('--param', required=True)
    args = parser.parse_args()

    try:
        client = GeospatialAPIClient.from_env()
        result = client.new_feature(args.param)
        print(result)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

## Performance Considerations

- **API Rate Limiting:** Use `delay` parameter in batch processing (default 0.1s between requests)
- **Token Caching:** Tokens cached in memory, valid for ~12 hours
- **Pagination:** CoreLogic APIs typically limit to 100 records per page, use `paginated_request()` for bulk data
- **Spatial Queries:** Optimize bounding boxes to minimize data transfer
- **Property Caching:** `PropertyDataProcessor` caches property details and sales history in instance variables

## Testing & Debugging

**Test API connectivity:**
```python
geo_client = GeospatialAPIClient.from_env()
result = geo_client.test_connection()
# Returns: {'success': True, 'status_code': 200, 'token_present': True, ...}
```

**Enable API debug output:**
```python
api_client.make_request(endpoint, params, debug=True)
# Prints: request URL, payload, params
```

**Check authentication:**
```bash
grep -E "CLIENT_ID|CLIENT_SECRET" .env
```
