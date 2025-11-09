# Property Data PDF Report Generator

**Script:** [generate_property_pdf.py](generate_property_pdf.py)

Generates professional PDF reports from comprehensive property data in a clean two-column table format.

## Recent Improvements (2025-11-09)

**Compact Landscape Layout:**
- ✅ **Landscape orientation** for better screen viewing
- ✅ **3-panel layout** (6 columns) fitting more data on each page
- ✅ **Smaller fonts** (7pt) for compact presentation
- ✅ **Reduced margins** (0.4") for maximum content density
- ✅ **Result:** Compact PDFs are ~6KB vs original 4.2KB but with 75% more data

**Enhanced Data Extraction:**
- ✅ ALL core_attributes fields now shown (was showing only 4, now shows all 9+ fields)
- ✅ Additional attributes section added (pool, floor area)
- ✅ Feature attributes properly extracted from API (Development Zone, Special Features, etc.)
- ✅ Last sale now includes contract date, settlement date, sale method, agency, and agent
- ✅ Sales history properly extracts from `saleList` array with metadata (total value, average price)
- ✅ **NEW:** Last advertising campaign section added (days on market, listing method, listing price, auction date)
- ✅ Location enhanced with locality and coordinates
- ✅ Site details now includes zone code/description, site value, valuation date, and dimensions
- ✅ Legal section greatly expanded (title info, parcel details, legal description)
- ✅ Occupancy shows type and confidence score
- ✅ All field names corrected to match actual API responses (beds/baths/carSpaces vs bedrooms/bathrooms/parkingSpaces)

**Ultra-Comprehensive Mode:**
- ✅ **NEW:** `--ultra-comprehensive` flag uses `flatten_json_recursive` to extract EVERY field from API
- ✅ Automatically detects and formats currency, measurements, booleans
- ✅ Shows nested field paths (e.g., "Location > Postcode > Name")
- ✅ **INCLUDES** all geospatial metadata sections (parcel geometry, layers, market data, comparables)
- ✅ **Result:** Ultra-comprehensive PDFs are ~13-16KB with exhaustive field coverage + geospatial context

**Geospatial Metadata Sections (NEW):**
- ✅ **Parcel Geometry Details:** Geometry type, spatial reference, area, perimeter, polygon rings, vertices
- ✅ **Geospatial Layers Summary:** Hazard layers (bushfire, flood, heritage), easements with details, infrastructure availability
- ✅ **Market Data:** Market trends and statistics (if available in report)
- ✅ **Comparables:** Summary of comparable properties (if available in report)
- ✅ **Result:** Standard PDFs now ~6.7-6.9KB with comprehensive geospatial context

**Mesh Block Analysis Integration (NEW - 2025-11-09):**
- ✅ **Automatic Detection:** Reads mesh block CSV files from data/outputs/ directory
- ✅ **Analysis Buffer:** Shows buffer distance used for analysis (e.g., 2000 meters)
- ✅ **Total Blocks:** Count of all mesh blocks within buffer
- ✅ **Category Breakdown:** Count by category (Residential, Commercial, Parkland, Education, Other)
- ✅ **Non-Residential Statistics:** Min, max, mean, median distances to non-residential blocks
- ✅ **Top 5 Closest:** Shows the 5 closest non-residential blocks with category, distance, and suburb
- ✅ **Result:** Standard PDFs now ~7.5KB, Ultra PDFs now ~16KB with mesh block context

## Features

### Compact Landscape Layout (Default)
- **Orientation:** Landscape A4 (11.7" × 8.3")
- **Layout:** 3-panel format (6 columns: label-value, label-value, label-value)
- **Font Size:** 7pt for data, 8pt for section headers, 11pt for title
- **Margins:** 0.4 inches (compact)
- **Result:** More data visible at once, better for screen viewing

### Two Data Extraction Modes

**Standard Mode (Default):**
- Curated extraction of important fields
- Organized by logical sections
- Smart formatting with units
- ~6KB PDF size

**Ultra-Comprehensive Mode (`--ultra-comprehensive`):**
- Extracts EVERY field from JSON using `flatten_json_recursive`
- Shows all nested fields with path notation
- Auto-detects and formats currencies, measurements, booleans
- **INCLUDES** geospatial metadata sections (parcel geometry, layers, market data, comparables)
- ~13-16KB PDF size (100% field coverage + geospatial context)

### Smart Data Formatting
- **Single Values:** Shows value with units (e.g., "791.9 m²", "$850,000")
- **Complex Data:** Shows metadata summaries:
  - Sales history: "5 sales" + "2018-01-15 to 2023-06-30"
  - Parcel geometry: "1 ring(s)" + "8 points"
  - Easements: "2000 easements"
  - Infrastructure: "Streets (47), Railway (12)" etc.

### Organized Sections
- Property Identification
- Location
- Site Details
- Property Attributes
- Features
- Last Sale
- Sales History
- Parcel Geometry
- Hazard Overlays
- Easements
- Infrastructure
- Occupancy
- Legal
- Mesh Block Analysis (if available)

## Requirements

```bash
pip install reportlab
```

Or with user install:
```bash
pip3 install --user reportlab
```

Or with system packages (macOS):
```bash
pip3 install --break-system-packages reportlab
```

## Usage

### Method 1: From Existing JSON Report (Standard Mode)

```bash
# Generate compact landscape PDF (6KB, curated fields)
python3 scripts/generate_property_pdf.py \
    --input data/property_reports/13683380_comprehensive_report.json
```

**Output:** `data/property_reports/13683380_property_report.pdf` (compact landscape, ~6KB)

### Method 1b: Ultra-Comprehensive Mode

```bash
# Generate with ALL fields extracted via flatten method + geospatial metadata (13-16KB)
python3 scripts/generate_property_pdf.py \
    --input data/property_reports/13683380_comprehensive_report.json \
    --ultra-comprehensive
```

**Output:** `data/property_reports/13683380_property_report.pdf` (landscape, ~13-16KB, every field + geospatial)

### Method 2: Directly from Address

```bash
# Generate comprehensive report AND PDF in one step
python3 scripts/generate_property_pdf.py \
    --address "5 Settlers Court, Vermont South VIC 3133"
```

This will:
1. Generate comprehensive property report (JSON)
2. Create PDF from the report
3. Save both files

**Output:**
- `data/property_reports/13683380_comprehensive_report.json`
- `data/property_reports/13683380_property_report.pdf`

### Custom Output Location

```bash
# Custom PDF output path
python3 scripts/generate_property_pdf.py \
    --input report.json \
    --output reports/client_name_2025-11-09.pdf
```

### Custom Output Directory

```bash
# All files go to custom directory
python3 scripts/generate_property_pdf.py \
    --address "123 Main St, Sydney NSW" \
    --output-dir reports/2025-11-09
```

## Output Format

### PDF Structure

**Page 1-2: Property Data Table**
- Clean two-column format
- Section headers (bold, shaded)
- Alternating row colors for readability
- Grid lines for clarity

**Header:**
- Title: "Property Data Report"
- Subtitle: Property address

**Footer:**
- Report generation timestamp
- Property ID

### Example Table Entries

| **Property Attribute** | **Value** |
|------------------------|-----------|
| **PROPERTY IDENTIFICATION** | |
| **Address** | 16 Fowler Crescent, South Coogee, NSW, 2034 |
| **Property ID** | 6255066 |
| **State** | NSW |
| **Report Date** | 2025-11-09 |
| | |
| **LOCATION** | |
| **Council Area** | Randwick |
| **Postcode** | 2034 |
| **Locality** | SOUTH COOGEE |
| **Coordinates** | -33.936272, 151.254700 |
| | |
| **SITE DETAILS** | |
| **Zone Code** | A |
| **Zone Description** | Residential |
| **Site Value** | $506,000 |
| **Valuation Date** | 1998-07-01 |
| **Dimensions** | ARC15.55/17.37X42.23/39.01 |
| | |
| **PROPERTY ATTRIBUTES** | |
| **Property Type** | HOUSE |
| **Property Sub Type** | House |
| **Bedrooms** | 4 |
| **Bathrooms** | 3 |
| **Car Spaces** | 4 |
| **Lock-Up Garages** | 0 |
| **Land Area** | 666.0 m² |
| **Calculated Land Area** | No |
| **Land Area Source** | Other |
| | |
| **ADDITIONAL ATTRIBUTES** | |
| **Pool** | Yes |
| | |
| **FEATURES** | |
| **Development Zone** | Low Density Residential |
| **Other Special Features** | Built-In Wardrobes, Close to Schools, Close to Shops, Close to Transport, Garden |
| **Property Improvements** | RESIDENTIAL |
| | |
| **LAST SALE** | |
| **Sale Price** | $3,600,000 |
| **Contract Date** | 2017-07-25 |
| **Settlement Date** | 2017-09-05 |
| **Sale Method** | Sold Prior To Auction |
| **Sale Type** | Unknown |
| **Agency** | N G Farah Real Estate - Kingsford |
| **Agent** | Martin Farah |
| | |
| **SALES HISTORY** | |
| **Total Sales** | 2 sales |
| **Date Range** | 2016-12-29 to 2017-07-25 |
| **Total Transaction Value** | $3,600,000 |
| **Average Sale Price** | $3,600,000 |
| | |
| **LAST ADVERTISING CAMPAIGN** | |
| **Campaign Start** | 2017-07-12 |
| **Campaign End** | 2017-07-26 |
| **Days on Market** | 14 |
| **Listing Method** | Auction |
| **Listing Price** | $3,000,000 |
| **Price Description** | AUCTION |
| **Auction Date** | 2017-08-12 |
| **Campaign Agency** | N G Farah Real Estate - Kingsford |
| | |
| **PARCEL GEOMETRY** | |
| **Polygon Rings** | 1 ring(s) |
| **Coordinate Points** | 9 points |
| **Geometry Type** | esriGeometryPolygon |
| | |
| **HAZARD OVERLAYS** | |
| **Detected Hazards** | Bushfire, Flood, Heritage |
| | |
| **EASEMENTS** | |
| **Total Easements** | 43 easements |
| | |
| **INFRASTRUCTURE (5km radius)** | |
| **Available Infrastructure** | Streets (47), Railway (12), Railway Stations (3) |
| | |
| **OCCUPANCY** | |
| **Occupancy Type** | Owner Occupied |
| **Confidence Score** | Low |
| | |
| **LEGAL** | |
| **Title Reference** | 24/111912 |
| **Title Indicator** | No More Titles |
| **Fee Code** | Sole Owner |
| **Owner Code** | Private |
| **Lot/Plan** | 24/DP111912 |
| **Parcel Area** | 666 m² |
| **Land Authority** | Randwick |
| **Legal Description** | LOT 24 DP111912 |
| | |
| **MESH BLOCK ANALYSIS** | |
| **Analysis Buffer** | 2000 meters |
| **Total Mesh Blocks** | 167 blocks |
| | |
| **Category Breakdown** | |
| **  Residential** | 121 blocks |
| **  Parkland** | 27 blocks |
| **  Education** | 7 blocks |
| **  Commercial** | 4 blocks |
| **  Other** | 8 blocks |
| | |
| **Non-Residential Distances** | |
| **  Total Non-Residential** | 46 blocks |
| **  Closest** | 180.0 m |
| **  Farthest** | 1941.2 m |
| **  Average** | 1069.3 m |
| **  Median** | 1041.0 m |
| | |
| **Top 5 Closest Non-Residential** | |
| **  #1 Commercial** | 180.0 m (Vermont South) |
| **  #2 Parkland** | 293.9 m (Vermont South) |
| **  #3 Parkland** | 378.3 m (Vermont South) |
| **  #4 Commercial** | 423.0 m (Vermont South) |
| **  #5 Parkland** | 541.1 m (Vermont South) |

## Workflow Integration

### Complete Workflow: Address → JSON → PDF

```bash
# All in one command
python3 scripts/generate_property_pdf.py \
    --address "5 Settlers Court, Vermont South VIC 3133"
```

### With Mesh Block Analysis

To include mesh block analysis in the PDF, run the mesh block analysis first:

```bash
# Step 1: Run mesh block analysis (generates CSV files in data/outputs/)
python3 scripts/run_full_analysis.py --address "5 Settlers Court, Vermont South VIC 3133"

# Step 2: Generate comprehensive property report
python3 scripts/comprehensive_property_report.py \
    --address "5 Settlers Court, Vermont South VIC 3133"

# Step 3: Generate PDF (automatically includes mesh block data if available)
python3 scripts/generate_property_pdf.py \
    --input data/property_reports/13683380_comprehensive_report.json
```

The PDF generator automatically detects mesh block CSV files in `data/outputs/` and includes them if found.

### Separate Steps: Maximum Control

```bash
# Step 1: Generate comprehensive data
python3 scripts/comprehensive_property_report.py \
    --address "5 Settlers Court, Vermont South VIC 3133" \
    --include-maps \
    --pretty

# Step 2: Generate PDF from comprehensive data
python3 scripts/generate_property_pdf.py \
    --input data/property_reports/13683380_comprehensive_report.json
```

## Data Formatting Rules

### Measurements
- **Area:** `791.9 m²`
- **Distance:** `18.5 m`
- **Currency:** `$850,000`

### Counts
- **Sales:** `5 sales`
- **Easements:** `2000 easements`
- **Features:** `47 features`

### Date Ranges
- **Single Date:** `2021-03-15`
- **Date Range:** `2001-06-20 to 2021-03-15`

### Lists
- **Features:** `Pool, Air Conditioning, Garage`
- **Infrastructure:** `Streets (47), Railway (12), Ferry (2)`
- **Hazards:** `Bushfire, Flood, Heritage`

### Geometry
- **Parcel:** `1 ring(s), 8 points`
- **Type:** `esriGeometryPolygon`

### Missing Data
- Shows as: `N/A`

## Examples

### Example 1: Quick PDF from Address

```bash
python3 scripts/generate_property_pdf.py \
    --address "5 Settlers Court, Vermont South VIC 3133"
```

**Result:** Generates both JSON and PDF in `data/property_reports/`

### Example 2: Batch Processing

```bash
# Generate reports for multiple addresses
for address in "5 Settlers Court, Vermont South VIC" \
               "16 Fowler Crescent, South Coogee NSW" \
               "123 Collins St, Melbourne VIC"; do
    python3 scripts/generate_property_pdf.py --address "$address"
done
```

### Example 3: Custom Directory Structure

```bash
# Client-specific directory
python3 scripts/generate_property_pdf.py \
    --address "5 Settlers Court, Vermont South VIC 3133" \
    --output-dir "reports/client_smith/2025-11-09"
```

**Output:**
```
reports/client_smith/2025-11-09/
├── 13683380_comprehensive_report.json
└── 13683380_property_report.pdf
```

## File Sizes

**PDF Modes:**
- **Compact Landscape (default):** ~7.5 KB (2-3 pages, curated fields + geospatial + mesh blocks)
- **Ultra-Comprehensive:** ~16 KB (4-8 pages, ALL fields via flatten + geospatial + mesh blocks)
- **Without Mesh Blocks:** ~6.7-6.9 KB (standard) or ~13-16 KB (ultra)
- **Original Portrait (legacy):** ~4.2 KB (2 pages, limited fields, no geospatial)

**JSON Files:**
- Comprehensive JSON: 1-2 MB (with all data)
- Property Details JSON: 10-20 KB (property endpoints only)

**Comparison:**
- Original → Compact: 43% increase in size, 75% more data
- Compact → Ultra: 120% increase in size, 100% field coverage + full geospatial context

## Technical Details

### PDF Generation
- **Library:** ReportLab
- **Page Size:** Landscape A4 (297 x 210 mm / 11.7" x 8.3")
- **Margins:** 0.4 inches (compact)
- **Font:** Helvetica (built-in)
  - Title: 11pt
  - Section headers: 8pt
  - Data: 7pt
- **Colors:** Grayscale with light shading

### Table Styling
- **Layout:** 6 columns (3 panels of label-value pairs)
- **Column Widths:** 1.6" (label) + 2.0" (value) per panel
- **Row Height:** Auto (based on content)
- **Grid:** 0.25pt gray lines (thin for compactness)
- **Section Headers:** Span all 6 columns, gray background (#e8e8e8)
- **Padding:** 3px horizontal, 2px vertical (compact)

### Data Extraction
Pulls from comprehensive report sections:
- `metadata.*`
- `property_details.*` (12 endpoints)
- `parcel_geometry.*`
- `geospatial_layers.*`

## Error Handling

### Missing Data
- Shows "N/A" for missing values
- Skips entire sections if no data available
- Never crashes on missing fields

### API Failures
- If property endpoint fails, shows "N/A" but continues
- If geospatial data missing, skips that section
- Always generates PDF even with partial data

## Comparison with Other Formats

### PDF vs JSON
- **PDF:** Human-readable, printable, shareable
- **JSON:** Machine-readable, programmatic access, complete data

### When to Use PDF
- Client reports
- Due diligence documentation
- Printable property summaries
- Email attachments

### When to Use JSON
- Programmatic analysis
- Data pipelines
- GIS integration
- Custom processing

## Integration

### Use in Python

```python
from generate_property_pdf import PropertyDataPDFGenerator, load_report

# Load comprehensive report
report = load_report('data/property_reports/13683380_comprehensive_report.json')

# Generate PDF
generator = PropertyDataPDFGenerator()
generator.generate_pdf(report, 'output.pdf')
```

### Batch Processing Script

```python
import json
from pathlib import Path
from generate_property_pdf import PropertyDataPDFGenerator

# Process all JSON reports in directory
reports_dir = Path('data/property_reports')
generator = PropertyDataPDFGenerator()

for json_file in reports_dir.glob('*_comprehensive_report.json'):
    with open(json_file) as f:
        report = json.load(f)

    pdf_file = json_file.with_name(json_file.stem.replace('_comprehensive_report', '_property_report') + '.pdf')
    generator.generate_pdf(report, str(pdf_file))
    print(f"Generated: {pdf_file}")
```

## Troubleshooting

### reportlab Not Installed
```bash
# Error message
⚠️  Warning: reportlab not installed

# Solution
pip install reportlab
# or
pip3 install --user reportlab
```

### File Not Found
```bash
# Error
FileNotFoundError: 'data/property_reports/xxx.json'

# Check file exists
ls -l data/property_reports/

# Use absolute path
python3 scripts/generate_property_pdf.py \
    --input /full/path/to/report.json
```

### Permission Denied
```bash
# Error
PermissionError: data/property_reports/

# Create directory
mkdir -p data/property_reports

# Or use different directory
python3 scripts/generate_property_pdf.py \
    --address "..." \
    --output-dir ~/reports
```

## Related Scripts

- [comprehensive_property_report.py](comprehensive_property_report.py) - Generate comprehensive JSON reports
- [check_geospatial_layers.py](check_geospatial_layers.py) - Check layer availability
- [single_address.py](single_address.py) - Sales history analysis

## See Also

- [README_COMPREHENSIVE_PROPERTY_REPORT.md](README_COMPREHENSIVE_PROPERTY_REPORT.md) - Comprehensive report documentation
- [ReportLab Documentation](https://www.reportlab.com/docs/reportlab-userguide.pdf) - PDF generation library
