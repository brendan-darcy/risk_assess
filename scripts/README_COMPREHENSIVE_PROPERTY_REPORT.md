# Comprehensive Property Data Report

**Script:** [comprehensive_property_report.py](comprehensive_property_report.py)

The most complete property data extraction tool - pulls ALL available data from CoreLogic APIs for a single address.

## What It Extracts

### 1. Property Details (12 API Endpoints)
From `generate_property_results` pattern in corelogic_processor_updated.py:

- **location** - Address, council area, street details, postcode
- **legal** - Legal description, title information
- **site** - Land area, dimensions, zoning
- **core_attributes** - Bedrooms, bathrooms, parking, property type
- **additional_attributes** - Additional property characteristics
- **features** - Pool, air conditioning, etc.
- **occupancy** - Occupancy status
- **last_sale** - Most recent sale details
- **sales** - Complete sales history
- **sales_otm** - On-the-market campaign history
- **timeline** - Property timeline events
- **advertisements** - Advertisement history

### 2. Geospatial Data (11+ Layers)
From geospatial_api_client pattern:

**Hazard Overlays (with features):**
- Bushfire hazard zones (feature count + first 10 features)
- Flood hazard zones (feature count + first 10 features)
- Heritage overlay zones (feature count + first 10 features)

**Legal:**
- Easements (complete list with geometries)

**Infrastructure (with features):**
- Streets (feature count + first 10 features)
- Railway lines (feature count + first 10 features)
- Railway stations (feature count + first 10 features)
- Ferry routes (feature count + first 10 features)
- Electric transmission lines (feature count + first 10 features)

### 3. Parcel Geometry
- Complete property parcel polygon
- Calculated 5km bounding box for spatial queries

### 4. Optional: Map Exports
With `--include-maps` flag:
- Property boundaries map (PNG)
- Bushfire hazard map (PNG)
- Flood hazard map (PNG)
- Heritage overlay map (PNG)
- Streets infrastructure map (PNG)
- Railway infrastructure map (PNG)

## Usage

### Basic Usage

```bash
# Extract all available data
python3 scripts/comprehensive_property_report.py --address "5 Settlers Court, Vermont South VIC 3133"

# Pretty print JSON
python3 scripts/comprehensive_property_report.py --address "5 Settlers Court, Vermont South VIC 3133" --pretty
```

### With Maps

```bash
# Include map image exports
python3 scripts/comprehensive_property_report.py \
    --address "16 Fowler Crescent, South Coogee, NSW, 2034" \
    --include-maps
```

### Custom Output Directory

```bash
# Save to specific directory
python3 scripts/comprehensive_property_report.py \
    --address "123 Collins St, Melbourne VIC" \
    --output-dir reports/client_name \
    --include-maps \
    --pretty
```

### Specify State (Optional)

```bash
# Manually specify state (auto-detects by default)
python3 scripts/comprehensive_property_report.py \
    --address "123 Main Street" \
    --state nsw
```

## Output Files

All files are saved to `data/property_reports/` (or custom directory):

### 1. Comprehensive Report
**{property_id}_comprehensive_report.json**
- Contains ALL data from all sources combined
- Typical size: 1-2 MB
- Structured with metadata, property_details, parcel_geometry, geospatial_layers

### 2. Property Details
**{property_id}_property_details.json**
- Just the 12 property API endpoints
- Typical size: 10-20 KB
- Easier to work with if you only need property details

### 3. Geospatial Layers
**{property_id}_geospatial_layers.json**
- Just the geospatial data (hazards, easements, infrastructure)
- Typical size: 1-2 MB (includes full feature geometries)
- Useful for GIS analysis

### 4. Map Exports (if --include-maps)
**{property_id}_*.png**
- Property boundaries map
- Hazard overlay maps
- Infrastructure maps
- Typical size: 50-200 KB per map

## Output Structure

### Comprehensive Report JSON

```json
{
  "metadata": {
    "extraction_timestamp": "2025-11-09T15:10:07",
    "address": "5 Settlers Court, Vermont South VIC 3133",
    "property_id": 13683380,
    "state": "VIC",
    "bbox": "...",
    "bbox_buffer_meters": 5000
  },
  "property_details": {
    "location": { ... },
    "legal": { ... },
    "site": { ... },
    "core_attributes": { ... },
    "additional_attributes": { ... },
    "features": { ... },
    "occupancy": { ... },
    "last_sale": { ... },
    "sales_history": [ ... ],
    "sales_otm": { ... },
    "timeline": { ... },
    "advertisements": { ... }
  },
  "parcel_geometry": {
    "success": true,
    "data": {
      "features": [ ... ],
      "geometryType": "esriGeometryPolygon",
      "spatialReference": { ... }
    }
  },
  "geospatial_layers": {
    "hazards": {
      "bushfire": {
        "available": true,
        "feature_count": 5,
        "features": [ ... ]
      },
      "flood": { ... },
      "heritage": { ... }
    },
    "legal": {
      "easements": {
        "available": true,
        "count": 2000,
        "features": [ ... ]
      }
    },
    "infrastructure": {
      "streets": {
        "available": true,
        "feature_count": 47,
        "method": "feature_query",
        "features": [ ... ]
      },
      "railway": { ... },
      ...
    }
  },
  "maps_exported": {
    "property_boundaries": "path/to/map.png",
    ...
  }
}
```

## Requirements

### Environment Variables
```bash
export CORELOGIC_CLIENT_ID="your_client_id"
export CORELOGIC_CLIENT_SECRET="your_client_secret"
```

### Python Dependencies
All handled by the existing project requirements:
- requests
- utils.property_data_processor
- utils.geospatial_api_client
- utils.pipeline_utils

## Examples

### Example 1: Quick Report
```bash
python3 scripts/comprehensive_property_report.py \
    --address "5 Settlers Court, Vermont South VIC 3133"
```

**Output:**
- 13683380_comprehensive_report.json (1.4 MB)
- 13683380_property_details.json (13 KB)
- 13683380_geospatial_layers.json (1.2 MB)

### Example 2: With Maps
```bash
python3 scripts/comprehensive_property_report.py \
    --address "16 Fowler Crescent, South Coogee, NSW, 2034" \
    --include-maps \
    --pretty
```

**Output:**
- All JSON files (pretty printed)
- 6+ PNG map files

### Example 3: Custom Directory
```bash
python3 scripts/comprehensive_property_report.py \
    --address "123 Collins St, Melbourne VIC" \
    --output-dir reports/2025-11-09 \
    --pretty
```

**Output saved to:** `reports/2025-11-09/`

## Comparison with Other Scripts

### vs. single_address.py
- **single_address.py**: Sales history + AVM analysis + indexation
- **comprehensive_property_report.py**: Everything (12 property endpoints + geospatial + optionally maps)

### vs. check_geospatial_layers.py
- **check_geospatial_layers.py**: Just geospatial layer availability checklist
- **comprehensive_property_report.py**: Full geospatial data + property details + parcel geometry

### vs. get_parcel_polygon.py
- **get_parcel_polygon.py**: Just parcel polygon geometry
- **comprehensive_property_report.py**: Parcel + everything else

## When to Use

Use **comprehensive_property_report.py** when you need:
- Complete property assessment report
- Maximum available data for due diligence
- Combined property + geospatial analysis
- Professional property reports
- Data for downstream analysis/modeling

Use other scripts when you only need specific data:
- **single_address.py** for sales/market analysis only
- **check_geospatial_layers.py** for quick layer availability check
- **get_parcel_polygon.py** for just geometry data

## Performance

**Typical Execution Time:**
- Property details (12 endpoints): ~5-10 seconds
- Parcel geometry: ~1-2 seconds
- Geospatial layers: ~10-15 seconds
- Map exports (if enabled): +5-10 seconds

**Total:** ~20-30 seconds without maps, ~30-40 seconds with maps

## Error Handling

The script is designed to be resilient:
- If property endpoints fail, they're marked with error messages but script continues
- If geospatial queries fail, falls back to image-based checks
- If bounding box can't be calculated, skips geospatial layers but continues
- State is auto-detected, with NSW as fallback

## Integration

### Use in Pipeline
```python
from comprehensive_property_report import ComprehensivePropertyReporter
from utils.property_data_processor import PropertyDataProcessor
from utils.geospatial_api_client import GeospatialAPIClient

# Initialize
property_processor = PropertyDataProcessor()
geo_client = GeospatialAPIClient.from_env()
reporter = ComprehensivePropertyReporter(geo_client, property_processor)

# Generate report
report = reporter.generate_comprehensive_report(
    address="5 Settlers Court, Vermont South VIC 3133",
    include_maps=False,
    output_dir=Path("reports")
)
```

### Parse Output
```bash
# Extract just property ID
jq -r '.metadata.property_id' 13683380_comprehensive_report.json

# Check what endpoints succeeded
jq '.property_details | with_entries(select(.value.error == null)) | keys' 13683380_property_details.json

# Count infrastructure features
jq '.geospatial_layers.infrastructure | map_values(.feature_count // 0)' 13683380_geospatial_layers.json

# List all easements
jq '.geospatial_layers.legal.easements.features[]' 13683380_geospatial_layers.json
```

## Related Scripts

- [single_address.py](single_address.py) - Sales history and AVM analysis
- [check_geospatial_layers.py](check_geospatial_layers.py) - Geospatial layer availability checklist
- [get_parcel_polygon.py](get_parcel_polygon.py) - Parcel geometry only
- [run_full_analysis.py](run_full_analysis.py) - Mesh block analysis

## See Also

- [GeospatialAPIClient](utils/geospatial_api_client.py) - Geospatial API client
- [PropertyDataProcessor](utils/property_data_processor.py) - Property lookup
- [corelogic_processor_updated.py](utils/corelogic_processor_updated.py) - Original generate_property_results pattern
