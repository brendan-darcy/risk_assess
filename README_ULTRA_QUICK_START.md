# Ultra-Comprehensive Report - Quick Start

## TL;DR

Two scripts, two steps:

```bash
# Step 1: Generate complete JSON (all data sources)
python3 scripts/generate_ultra_comprehensive_json.py --address "YOUR ADDRESS"

# Step 2: Generate PDF from JSON
python3 scripts/generate_property_pdf.py data/property_reports/{PROPERTY_ID}_ultra_comprehensive_report.json --ultra-comprehensive
```

## Setup (One Time)

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export CORELOGIC_CLIENT_ID="your_client_id"
export CORELOGIC_CLIENT_SECRET="your_client_secret"
export GOOGLE_API_KEY="your_google_api_key"
```

## Complete Example

```bash
# Generate JSON with ALL data
python3 scripts/generate_ultra_comprehensive_json.py \
    --address "5 Settlers Court, Vermont South VIC 3133" \
    --pretty

# Output: data/property_reports/13683380_ultra_comprehensive_report.json
# Contains:
#   ✅ 13 CoreLogic API endpoints
#   ✅ Geospatial layers (hazards, legal, infrastructure)
#   ✅ Parcel geometry
#   ✅ Market metrics
#   ✅ Google Places impact analysis (29 categories)

# Generate ultra-comprehensive PDF
python3 scripts/generate_property_pdf.py \
    data/property_reports/13683380_ultra_comprehensive_report.json \
    --ultra-comprehensive

# Output: data/property_reports/13683380_property_report.pdf
```

## What's New?

**Before** (3 separate scripts):
1. `comprehensive_property_report.py` - CoreLogic + geospatial
2. `run_places_analysis.py` - Google Places
3. `add_places_to_report.py` - Merge data

**Now** (1 consolidated script):
1. `generate_ultra_comprehensive_json.py` - Everything in one go!

## Files

- **`scripts/generate_ultra_comprehensive_json.py`** - NEW! Consolidated JSON generator
- **`scripts/generate_property_pdf.py`** - Existing PDF generator (unchanged)
- **`ULTRA_COMPREHENSIVE_WORKFLOW.md`** - Full documentation

## Data Included

| Data Source | Endpoints | Description |
|------------|-----------|-------------|
| **Property Details** | 13 | Location, legal, sales, OTM campaigns, timeline |
| **Geospatial** | 11+ | Hazards, easements, infrastructure |
| **Market Metrics** | 10+ | Sales trends, median prices, DOM, auction rates |
| **Google Places** | 29 | Impact analysis at 100m/250m/600m/3000m radii |
| **Parcel Geometry** | 1 | Property boundary polygon |

## Troubleshooting

**Missing geopy/geopandas?**
```bash
pip install -r requirements.txt
```

**Virtual environment?**
```bash
source venv/bin/activate  # if you have a venv
python3 scripts/generate_ultra_comprehensive_json.py --address "..."
```

**Google Places failing?**
```bash
export GOOGLE_API_KEY="your_key"
```

## Benefits

✅ **Single command** - No manual data merging
✅ **Complete data** - All sources in one JSON
✅ **Reusable** - JSON can be used for multiple purposes
✅ **Separated** - JSON generation separate from PDF rendering
✅ **Progress tracking** - Detailed logging at each step

---

See [ULTRA_COMPREHENSIVE_WORKFLOW.md](ULTRA_COMPREHENSIVE_WORKFLOW.md) for full documentation.
