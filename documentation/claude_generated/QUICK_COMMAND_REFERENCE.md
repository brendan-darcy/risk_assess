# Quick Command Reference

**Quick reference for generating categorized property PDFs**

---

## Generate Categorized PDF (Recommended)

### Complete Workflow

```bash
# Step 1: Generate ultra-comprehensive JSON (all APIs)
python3 scripts/generate_ultra_comprehensive_json.py \
    --address "5 Settlers Court, Vermont South VIC 3133" \
    --pretty

# Step 2: Categorize JSON (organize into 10 product categories)
python3 scripts/categorize_report.py \
    --input data/property_reports/13683380_ultra_comprehensive_report.json \
    --output data/property_reports/13683380_categorized.json \
    --pretty

# Step 3: Generate final PDF (4 pages with clean metadata)
python3 scripts/generate_property_pdf.py \
    --input data/property_reports/13683380_categorized.json \
    --ultra-comprehensive \
    --output data/property_reports/13683380_final.pdf
```

**Output**: `13683380_final.pdf` (13K, 4 pages)

---

## Output Files

### Recommended File
- **`13683380_final.pdf`** - 4 pages, 13K
  - All data organized by 10 product categories
  - Clean metadata summaries for collections
  - Coverage indicators and gap markers
  - Production-ready format

### Alternative Files
- **`13683380_ultra_comprehensive.pdf`** - 7 pages, 20K
  - Original format organized by API endpoints
  - Curated field selection
  - Good for quick reference

- **`13683380_categorized_full.pdf`** - 280 pages, 671K
  - Every single field flattened and displayed
  - Useful for data audits
  - Not recommended for regular use

---

## Key Features of Final PDF

### Data Organization
1. **INSTRUCTIONS** - Client info, job details (0% captured - marked with [GAP])
2. **LOCATION AND ADMINISTRATIVE** - Address, council, coordinates (95% complete)
3. **MAPPING AND TOPOGRAPHY** - Boundaries, property type, proximity (70% complete)
4. **LEGAL** - Property ID, title info, easements (100% complete)
5. **CHARACTERISTICS** - Rooms, features, dimensions (100% complete)
6. **OCCUPANCY** - Land use, zoning (70% complete)
7. **LOCAL MARKET** - Market metrics time series (95% complete)
8. **TRANSACTION HISTORY** - Sales history (100% complete)
9. **CAMPAIGNS** - Marketing campaigns, ads (100% complete)
10. **SALES EVIDENCE** - Comparable sales (0% captured - marked with [GAP])

### Smart Summarization

Instead of showing all items, uses metadata summaries:

**Easements** (2000 items):
```
Easements > Features: 2000 found
  Example 1: PFI: 456371337, Status: Active, Length: 7.4m
  Example 2: PFI: 453638786, Status: Active, Length: 21.3m
  Example 3: PFI: 123595, Status: Active, Length: 48.4m
```

**Market Metrics** (90 data points):
```
✓ Sales Volume
  Data Points: 90 (monthly)
  Period: 2015-04 to 2022-03
  First Value: 42
  Latest Value: 38
  Growth: -9.5%
```

**Campaigns** (Timeline Format):
```
CAMPAIGN TIMELINE
Total Events: 45
  🏠 For Sale Campaign Start        2022-05-02
  🏠 For Sale Campaign End          2022-05-28
  🏘️ For Rent Campaign Start        2019-01-15
  ... (15 most recent events)

ADVERTISEMENT EXTRACTS
Total Advertisements: 12
  Advertisement #1
    Date: 2022-05-10
    Type: For Sale
    Method: Auction
    Agency: Ray White Vermont South
    Description: Beautiful family home...
  ... (5 most recent ads with full details)
```

---

## For Any Address

Replace the address and property ID:

```bash
# Step 1: Ultra-comprehensive JSON
python3 scripts/generate_ultra_comprehensive_json.py \
    --address "YOUR ADDRESS HERE" \
    --pretty

# Step 2: Find the property ID from the output, then categorize
python3 scripts/categorize_report.py \
    --input data/property_reports/{PROPERTY_ID}_ultra_comprehensive_report.json \
    --output data/property_reports/{PROPERTY_ID}_categorized.json \
    --pretty

# Step 3: Generate PDF
python3 scripts/generate_property_pdf.py \
    --input data/property_reports/{PROPERTY_ID}_categorized.json \
    --ultra-comprehensive \
    --output data/property_reports/{PROPERTY_ID}_final.pdf
```

---

## Documentation

- **[FINAL_PDF_COMPARISON.md](FINAL_PDF_COMPARISON.md)** - Detailed comparison of all PDF versions
- **[PRODUCT_CONCEPT_GAP_ANALYSIS.md](PRODUCT_CONCEPT_GAP_ANALYSIS.md)** - Complete gap analysis (600+ lines)
- **[CATEGORIZED_REPORT_COMPARISON.md](CATEGORIZED_REPORT_COMPARISON.md)** - Technical comparison

---

**Version**: 2.3 (Final with Clean Metadata)
**Last Updated**: 2025-11-10
