# Planning Zone Analyzer for Residential Valuers

Analyzes planning zone documents (PDFs) and extracts key information relevant to residential property valuation.

## Overview

This tool reads planning scheme PDFs and generates a comprehensive JSON summary focused on information critical for residential valuers:
- **Use restrictions and allowances**
- **Non-residential uses permitted** (value-add opportunities)
- **Height restrictions** (building envelope)
- **Setback requirements** (front, side, rear)
- **Site requirements** (lot size, coverage, permeability)
- **Prohibited uses and activities**
- **Key terms and definitions**

## Files

- **`scripts/analyze_planning_zones.py`** - Main analyzer script
- **Input**: `data/planning_scheme/*.pdf` - Planning zone PDFs
- **Output**: `data/planning_zones_summary.json` - Structured analysis

## Requirements

```bash
pip3 install --break-system-packages PyPDF2
```

## Usage

### Basic Usage

```bash
python3 scripts/analyze_planning_zones.py
```

### Custom Directories

```bash
# Custom input directory
python3 scripts/analyze_planning_zones.py --input-dir path/to/pdfs

# Custom output file
python3 scripts/analyze_planning_zones.py --output output/summary.json

# Both
python3 scripts/analyze_planning_zones.py \
  --input-dir data/planning_scheme \
  --output data/planning_zones_summary.json
```

## Output Structure

The generated JSON file contains:

### 1. Metadata
```json
{
  "metadata": {
    "total_schemes_analyzed": 4,
    "schemes_directory": "data/planning_scheme"
  }
}
```

### 2. Individual Scheme Analysis

For each planning zone PDF:

```json
{
  "file": "32.09-neighbourhood-residential-zone.pdf",
  "zone_name": "NEIGHBOURHOOD RESIDENTIAL ZONE",

  "purpose": [
    "To implement the Municipal Planning Strategy...",
    "To recognise areas of predominantly single and double storey..."
  ],

  "table_of_uses": {
    "section_1_uses": ["Dwelling", "Home based business", ...],
    "section_2_uses": ["Car park", "Convenience shop", ...],
    "section_3_uses": ["Industry", "Nightclub", "Warehouse", ...],
    "permit_not_required": [...],
    "permit_required": [...],
    "prohibited": [...]
  },

  "height_restrictions": [
    {
      "requirement": "maximum height of 9 metres",
      "height": "9 metres"
    }
  ],

  "setback_requirements": [
    {
      "requirement": "street setback of 9 metres",
      "distance": "9 metres"
    }
  ],

  "site_requirements": {
    "minimum_lot_size": "400 square metres",
    "site_coverage": "60%",
    "permeability": "20%"
  },

  "non_residential_uses": [
    "home occupation",
    "medical centre",
    "child care",
    "convenience shop"
  ],

  "prohibitions": [
    "Industry (other than Automated collection point)",
    "Warehouse (other than Store)"
  ]
}
```

### 3. Valuer Summary

Cross-zone analysis for quick reference:

```json
{
  "valuer_summary": {
    "residential_zones_analyzed": 4,

    "common_restrictions": [
      "Height restrictions found in 3/4 zones",
      "Setback requirements found in 4/4 zones"
    ],

    "height_range": {
      "min_metres": 9.0,
      "max_metres": 11.0,
      "average_metres": 9.8
    },

    "non_residential_opportunities": {
      "total_opportunities": 38,
      "unique_use_types": 15,
      "most_common": [
        {"use": "home occupation", "count": 4},
        {"use": "medical centre", "count": 3},
        {"use": "child care", "count": 2}
      ]
    },

    "key_considerations": [
      "Review specific zone schedule for property-specific variations",
      "Check if property falls under multiple zones or overlays",
      "Verify current permit status and any existing use rights"
    ]
  }
}
```

## Console Output

The script provides a formatted summary to console:

```
======================================================================
PLANNING ZONE ANALYZER FOR RESIDENTIAL VALUERS
======================================================================

📄 Found 4 planning scheme documents

🔍 Analyzing: 32.09-neighbourhood-residential-zone.pdf
🔍 Analyzing: low-density-residential.pdf
🔍 Analyzing: medium-density-residential.pdf

✅ Analysis complete!
📁 Summary saved to: data/planning_zones_summary.json

======================================================================
SUMMARY FOR VALUERS
======================================================================

📊 Zones Analyzed: 4

🔒 Common Restrictions:
   • Height restrictions found in 3/4 zones
   • Setback requirements found in 4/4 zones

📏 Height Restrictions Range:
   Min: 9.0m
   Max: 11.0m
   Avg: 9.8m

🏢 Non-Residential Opportunities: 38
   Unique Use Types: 15

💡 Key Considerations:
   • Review specific zone schedule for property-specific variations
   • Check if property falls under multiple zones or overlays
   • Verify current permit status and any existing use rights
   • Consider non-residential use potential for value-add opportunities
   • Assess building envelope constraints on development potential

======================================================================
```

## Key Information Extracted

### For Residential Valuers

#### 1. **Use Restrictions**
   - **Section 1**: Permit NOT required (as-of-right uses)
   - **Section 2**: Permit required (conditional uses)
   - **Section 3**: Prohibited uses

#### 2. **Building Envelope**
   - Height restrictions (metres)
   - Street setbacks (front, side, rear)
   - Site coverage (%)
   - Permeability requirements (%)
   - Building separation

#### 3. **Site Requirements**
   - Minimum lot size
   - Minimum garden area (%)
   - Maximum site coverage
   - Parking requirements

#### 4. **Non-Residential Opportunities**
   - Home-based business
   - Medical centre/consulting rooms
   - Child care centre
   - Convenience shop
   - Food and drink premises
   - Bed and breakfast
   - Office uses

#### 5. **Development Potential**
   - Subdivision restrictions
   - Dwelling density limits
   - Multi-dwelling approval requirements
   - Affordable housing provisions

## Valuation Use Cases

### 1. **Highest and Best Use Analysis**
   - Identify permitted non-residential uses
   - Assess value-add conversion opportunities
   - Evaluate development potential within constraints

### 2. **Site Analysis**
   - Building envelope constraints
   - Maximum developable area
   - Height and setback limitations
   - Parking requirements impact

### 3. **Market Value Impact**
   - Compare zone restrictions across comparable properties
   - Assess development potential premium
   - Identify constraint-related value adjustments

### 4. **Due Diligence**
   - Verify use compliance
   - Identify non-conforming uses
   - Assess rezoning potential
   - Planning permit requirements

## Example Queries

After running the analyzer, use the JSON output to answer:

1. **"What non-residential uses are allowed in this zone?"**
   → Check `non_residential_uses` array

2. **"What's the maximum building height?"**
   → Check `height_restrictions` array

3. **"Is subdivision permitted?"**
   → Check `table_of_uses` → `prohibited` for "subdivision"

4. **"What's the minimum lot size?"**
   → Check `site_requirements` → `minimum_lot_size`

5. **"Can I operate a home business?"**
   → Check if "home based business" or "home occupation" in `section_1_uses`

## Integration with Property Reports

The planning zone summary can be integrated into comprehensive property reports:

```python
from scripts.utils.planning_zone_lookup import get_zone_summary

# Load zone summary
with open('data/planning_zones_summary.json') as f:
    zones = json.load(f)

# Get specific zone
zone = zones['schemes']['32.09-neighbourhood-residential-zone']

# Add to property report
report['planning'] = {
    'zone': zone['zone_name'],
    'height_limit': zone['height_restrictions'][0]['height'],
    'non_residential_opportunities': zone['non_residential_uses'],
    'key_restrictions': zone['prohibitions'][:5]
}
```

## Limitations

1. **PDF Text Extraction**: Some PDFs with complex formatting may not extract perfectly
2. **Pattern Matching**: Uses regex patterns that may not capture all variations in planning document language
3. **Schedule-Specific Variations**: Individual property schedules may have different requirements
4. **Overlays Not Included**: Heritage, environmental, and other overlays require separate analysis
5. **Updates**: Planning schemes change - always verify with current planning authority documents

## Troubleshooting

### No Text Extracted
```
⚠️ Error reading xyz.pdf: Could not extract text
```
**Solution**: PDF may be image-based. Use OCR tool or get text-based version.

### Missing Information
Some fields empty or incomplete.

**Solution**:
- PDF formatting may vary
- Manually review PDF for specific requirements
- Update regex patterns in script for your local council's format

### Incorrect Height/Setback Values
Values seem wrong or out of range.

**Solution**:
- Check `height_restrictions` array for context
- Some values may be for specific elements (fences, sheds) not buildings
- Verify against PDF manually

## Future Enhancements

- [ ] Add overlay analysis (Heritage, Environmental Significance, etc.)
- [ ] Parse specific schedule variations by address
- [ ] Extract car parking requirements
- [ ] Identify planning permit exemptions
- [ ] Add VicSmart application criteria
- [ ] Support image-based PDFs with OCR
- [ ] Interactive web interface for queries

## Related Tools

- **Property Report Generator**: [scripts/comprehensive_property_report.py](./comprehensive_property_report.py)
- **PDF Generator**: [scripts/generate_property_pdf.py](./generate_property_pdf.py)
- **Geospatial Layers**: [scripts/check_geospatial_layers.py](./check_geospatial_layers.py)

---

**Author**: Planning Zone Analysis Tool
**Date**: 2025-11-10
**Purpose**: Extract valuation-relevant planning information from zone PDFs
