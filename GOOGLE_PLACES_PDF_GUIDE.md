# Google Places Impact Analysis in PDF Reports

Complete guide to add Google Places analysis to your property PDF reports.

## Quick Start - Complete Workflow

```bash
# 1. Run Google Places analysis
source venv/bin/activate
python3 scripts/run_places_analysis.py --address "18 Fowler Crescent, South Coogee NSW 2034"

# 2. Generate comprehensive property report
python3 scripts/comprehensive_property_report.py --address "18 Fowler Crescent, South Coogee NSW 2034"

# 3. Add Places data to comprehensive report
python3 scripts/add_places_to_report.py \
    --report data/property_reports/6256699_comprehensive_report.json \
    --places data/places_analysis

# 4. Generate PDF with Places section
python3 scripts/generate_property_pdf.py \
    --input data/property_reports/6256699_comprehensive_report.json \
    --output outputs/property_with_places.pdf
```

## What Gets Included in the PDF

The PDF will now include a **GOOGLE PLACES IMPACT ANALYSIS** section with:

### Summary Statistics
- Total Categories Analyzed: 29
- Categories with Nearby Places: 3/29

### Distance Summary
- Closest Impact: 181m
- Furthest Impact: 2360m
- Median Distance: 552m
- Within 100m: 0
- Within 250m: 1
- Within 600m: 2
- Within 3000m: 3

### Closest Places by Category (Top 10)
Lists the nearest place in each impact category:
- **Transport And Connectivity**: South Coogee Ferry Wharf (181m)
- **Schools Primary**: Coogee Public School (552m)
- **Airport**: Sydney Kingsford Smith Airport (2360m)

## Data Structure

The `add_places_to_report.py` script adds this structure to your comprehensive report:

```json
{
  "google_places_impact": {
    "total_categories": 29,
    "categories_with_matches": 3,
    "categories_without_matches": 26,
    "distance_distribution": {
      "closest_meters": 181.2,
      "furthest_meters": 2360.2,
      "median_meters": 551.8,
      "within_100m": 0,
      "within_250m": 1,
      "within_600m": 2,
      "within_3000m": 3
    },
    "closest_impacts": [
      {
        "category": "transport_and_connectivity",
        "name": "South Coogee Ferry Wharf",
        "distance_meters": 181.2,
        "level": "Level_3_Impacts",
        "address": "Coogee NSW 2034"
      }
    ]
  }
}
```

## Customization

### Change Number of Places Shown

Edit `scripts/generate_property_pdf.py` line 1113:

```python
# Show top 10 (default)
closest_impacts = places_impact.get('closest_impacts', [])[:10]

# Show top 20
closest_impacts = places_impact.get('closest_impacts', [])[:20]

# Show all
closest_impacts = places_impact.get('closest_impacts', [])
```

### Add Category Level Labels

Modify line 1122 to include the impact level:

```python
data_rows.append((f"{category} ({level})", f"{name} ({distance:.0f}m)"))
```

## For Existing Reports

If you already have comprehensive reports without Places data:

```bash
# Add Places data retroactively
python3 scripts/add_places_to_report.py \
    --report data/property_reports/13683380_comprehensive_report.json \
    --places data/places_analysis \
    --output data/property_reports/13683380_with_places.json

# Then generate PDF
python3 scripts/generate_property_pdf.py \
    --input data/property_reports/13683380_with_places.json
```

## Integration with Comprehensive Property Report Pipeline

To automatically include Places analysis, modify `comprehensive_property_report.py`:

1. Add Places analysis call after property details fetch
2. Add Places data to the report structure
3. PDF generation will automatically include it

Example modification:
```python
# In generate_comprehensive_report method, after market metrics:

# 7. Run Google Places Analysis
try:
    from utils.google_api_processor import GooglePlacesPipeline
    places_pipeline = GooglePlacesPipeline(config, ProgressReporter("Places"))
    places_results = places_pipeline.run(address, radius=3000)

    # Format for PDF
    report['google_places_impact'] = {
        'total_categories': places_results['statistics']['total_categories'],
        'categories_with_matches': places_results['statistics']['categories_with_matches'],
        # ... etc
    }
except Exception as e:
    self.reporter.warning(f"Places analysis failed: {e}")
```

## Tips

- Run Places analysis in the same location as property reports for easy reference
- Use `--output-dir data/places_analysis` to keep Places data organized
- The PDF generator handles missing Places data gracefully (won't show section if not present)
- Distance metrics are automatically formatted in meters

## Troubleshooting

**Places section not appearing?**
- Check that `google_places_impact` key exists in JSON
- Verify no `error` field in the places data
- Ensure `add_places_to_report.py` completed successfully

**Distance distribution missing?**
- Check that statistics.json exists in places directory
- Verify at least one category has matches

**Wrong places data?**
- Ensure places analysis was run for the correct address
- Check timestamps in statistics.json match your report date
