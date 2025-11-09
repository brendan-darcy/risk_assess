# Geospatial Layer Checker Script

**Script:** [check_geospatial_layers.py](check_geospatial_layers.py)

This script checks which CoreLogic geospatial layers are available for a given property address and returns a comprehensive checklist of data availability.

## Features

- ✅ Checks 11 different geospatial layer types
- ✅ Provides detailed availability status for each layer
- ✅ Organizes results by category (Property, Hazards, Legal, Infrastructure)
- ✅ Returns JSON output with complete details
- ✅ Human-readable summary printed to stderr
- ✅ State-specific layer support

## Layers Checked

### Property Layers
- **Property Parcel Geometry** - Basic property parcel polygon and attributes
- **Property Boundaries** - Detailed property boundary data

### Hazard Layers
- **Bushfire Hazard** - Bushfire risk and hazard zones
- **Flood Hazard** - Flood risk and planning zones
- **Heritage Overlay** - Heritage and conservation zones

### Legal Layers
- **Easements** - Property easements and rights of way

### Infrastructure Layers
- **Streets** - Road and street network
- **Railway** - Railway lines and corridors
- **Railway Stations** - Railway station locations
- **Ferry** - Ferry routes and terminals
- **Electric Transmission Lines** - High voltage transmission infrastructure

## Usage

### Basic Usage

```bash
# Check all layers for an address
python3 scripts/check_geospatial_layers.py --address "5 Settlers Court, Vermont South VIC 3133"
```

### Save Results to File

```bash
# Save JSON results to file
python3 scripts/check_geospatial_layers.py \
    --address "16 Fowler Crescent, South Coogee, NSW, 2034" \
    --output data/outputs/layers_check.json
```

### Pretty Print JSON

```bash
# Pretty print JSON output
python3 scripts/check_geospatial_layers.py \
    --address "3 Nymboida Street, South Coogee, NSW, 2034" \
    --pretty
```

### Specify State

```bash
# Check with specific state for state-specific layers
python3 scripts/check_geospatial_layers.py \
    --address "123 Collins St, Melbourne VIC 3000" \
    --state vic
```

## Output Format

### Human-Readable Summary (stderr)

The script prints a human-readable summary to stderr:

```
======================================================================
GEOSPATIAL LAYER AVAILABILITY SUMMARY
======================================================================

Property: 5 Settlers Court, Vermont South VIC 3133
Property ID: 13683380
State: NSW

Availability: 8/11 layers (72.7%)

Property:
  ✅ Property Parcel Geometry: Property parcel geometry available
  ✅ Property Boundaries: Property boundary data available

Hazards:
  ✅ Bushfire Hazard: Bushfire hazard data available
  ❌ Flood Hazard: No flood hazard data in area
  ✅ Heritage Overlay: Heritage hazard data available

Legal:
  ✅ Easements: 2 easement(s) found

Infrastructure:
  ✅ Streets: Streets data available
  ✅ Railway: Railway data available
  ✅ Railway Stations: Railway Stations data available
  ❌ Ferry: No ferry in area
  ❌ Electric Transmission Lines: No electric transmission lines in area
```

### JSON Output (stdout)

The script outputs detailed JSON to stdout:

```json
{
  "success": true,
  "address": "5 Settlers Court, Vermont South VIC 3133",
  "property_id": "13683380",
  "state": "NSW",
  "bbox": "145.172,145.173,-37.850,-37.849",
  "summary": {
    "total_layers": 11,
    "available_layers": 8,
    "unavailable_layers": 3,
    "availability_percentage": 72.7
  },
  "layers_by_category": {
    "Property": [
      {
        "layer_key": "core_property",
        "name": "Property Parcel Geometry",
        "description": "Basic property parcel polygon and attributes",
        "category": "Property",
        "available": true,
        "status": "success",
        "message": "Property parcel geometry available",
        "feature_count": 1,
        "error": null
      }
    ],
    "Hazards": [...],
    "Legal": [...],
    "Infrastructure": [...]
  },
  "layers": [...]
}
```

## JSON Schema

### Top Level
```json
{
  "success": boolean,          // Whether the check completed successfully
  "address": string,           // Input address
  "property_id": string,       // CoreLogic property ID
  "state": string,             // State code (uppercase)
  "bbox": string,              // Bounding box "xmin,ymin,xmax,ymax"
  "summary": {...},            // Summary statistics
  "layers_by_category": {...}, // Layers organized by category
  "layers": [...]              // All layers in flat array
}
```

### Summary Object
```json
{
  "total_layers": number,            // Total number of layers checked
  "available_layers": number,        // Number of available layers
  "unavailable_layers": number,      // Number of unavailable layers
  "availability_percentage": number  // Percentage of available layers
}
```

### Layer Result Object
```json
{
  "layer_key": string,          // Unique layer identifier
  "name": string,               // Human-readable layer name
  "description": string,        // Layer description
  "category": string,           // Category (Property, Hazards, Legal, Infrastructure)
  "available": boolean,         // Whether layer has data
  "status": string,             // Status code (success, no_data, error, no_bbox, unknown)
  "message": string,            // Human-readable status message
  "feature_count": number,      // Number of features found (if applicable)
  "error": string|null          // Error message if status is 'error'
}
```

### Status Codes
- `success` - Layer is available and has data
- `no_data` - Layer check completed but no data found
- `error` - Error occurred during layer check
- `no_bbox` - Could not determine property location (required for check)
- `unknown` - Layer check not completed

## Requirements

### Environment Variables
```bash
export CORELOGIC_CLIENT_ID="your_client_id"
export CORELOGIC_CLIENT_SECRET="your_client_secret"
```

### Python Dependencies
- requests
- pathlib (built-in)
- json (built-in)

All dependencies should be installed from the project's requirements.txt.

## Examples

### Example 1: Quick Check
```bash
python3 scripts/check_geospatial_layers.py \
    --address "5 Settlers Court, Vermont South VIC 3133"
```

### Example 2: Save and Pretty Print
```bash
python3 scripts/check_geospatial_layers.py \
    --address "16 Fowler Crescent, South Coogee, NSW, 2034" \
    --output data/outputs/coogee_layers.json \
    --pretty
```

### Example 3: Process in Pipeline
```bash
# Check layers and save to file
python3 scripts/check_geospatial_layers.py \
    --address "123 Main St, Sydney NSW" \
    --output data/outputs/layers.json

# Process the results with jq
cat data/outputs/layers.json | jq '.layers[] | select(.available == true) | .name'
```

### Example 4: Check Multiple Addresses
```bash
# Create a simple loop to check multiple addresses
for address in "5 Settlers Court, Vermont South VIC" "16 Fowler Crescent, South Coogee NSW"; do
    echo "Checking: $address"
    python3 scripts/check_geospatial_layers.py \
        --address "$address" \
        --pretty > "data/outputs/layers_${address// /_}.json"
done
```

## Integration with Other Scripts

This script can be used as part of a larger workflow:

1. **Get Property ID**
   ```bash
   python3 scripts/check_geospatial_layers.py --address "..." --output layers.json
   PROPERTY_ID=$(jq -r '.property_id' layers.json)
   ```

2. **Get Available Layers**
   ```bash
   AVAILABLE_LAYERS=$(jq -r '.layers[] | select(.available == true) | .layer_key' layers.json)
   ```

3. **Fetch Specific Layer Data**
   ```bash
   # If easements are available, fetch them
   if echo "$AVAILABLE_LAYERS" | grep -q "easements"; then
       # Use another script to fetch detailed easement data
       python3 scripts/get_easements.py --property-id "$PROPERTY_ID"
   fi
   ```

## Error Handling

### Address Not Found
```bash
$ python3 scripts/check_geospatial_layers.py --address "Invalid Address"

❌ Error: No property found for address: Invalid Address
```

### Missing Credentials
```bash
$ python3 scripts/check_geospatial_layers.py --address "..."

❌ Error: CORELOGIC_CLIENT_ID and CORELOGIC_CLIENT_SECRET environment variables are required
```

### API Errors
If individual layer checks fail, they will be marked with status `error` in the results, but the script will continue checking other layers.

## Notes

- The script checks layers in parallel where possible for better performance
- Some layers may not be available in all states or regions
- The bbox (bounding box) is automatically calculated from the property parcel geometry
- If bbox cannot be determined, some spatial checks will be skipped

## Related Scripts

- [get_parcel_polygon.py](get_parcel_polygon.py) - Get property parcel polygon geometry
- [run_full_analysis.py](run_full_analysis.py) - Run complete mesh block analysis
- [visualize_photo_locations.py](visualize_photo_locations.py) - Visualize photo locations on map

## See Also

- [GeospatialAPIClient](utils/geospatial_api_client.py) - Underlying API client
- [PropertyDataProcessor](utils/property_data_processor.py) - Property lookup functionality
