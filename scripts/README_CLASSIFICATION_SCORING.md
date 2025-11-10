# Classification & Scoring Report System

## Overview

The ARMATech Pre-Qualification system consists of **two complementary reports**:

1. **Data Collection Report** - Gathers and presents raw property data (existing system)
2. **Classification & Scoring Report** - Analyzes data and provides risk scores, classifications, and recommendations (this system)

This document describes the Classification & Scoring Report system, which takes property data and applies:
- Computer Vision imagery analysis (Layer 1/2/3 tagging and quality scores)
- Market risk scoring algorithms
- NLP property risk detection
- Valuation risk assessment
- Comparative analysis
- Risk mitigation recommendations

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 DATA COLLECTION PHASE                        │
│                                                              │
│  Property APIs → Data Pipelines → JSON Reports → PDF        │
│                                                              │
│  Output: {property_id}_comprehensive_report.json + PDF      │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│           CLASSIFICATION & SCORING PHASE                     │
│                                                              │
│  Data Collection → AI/ML Analysis → Scoring → PDF           │
│                                                              │
│  Output: {property_id}_classification_scoring.json + PDF    │
└─────────────────────────────────────────────────────────────┘
```

## Classification & Scoring Components

### 1. Imagery Classification & Quality Scores

Uses ARMATech Computer Vision to analyze property images:

**Layer 1 - High-Level Classification:**
- Indoor, Outdoor, Aerial, Floorplan detection
- De-duplication

**Layer 2 - Granular Room Classification:**
- Indoor: Kitchen, Bathroom, Living Space, Entrance, Laundry, Garage/Shed
- Outdoor: Frontage, Garden, Garage/Shed, Local Scenery, Pool, Tennis Court

**Layer 3 - Quality Grading (1-5 scale):**
- Kitchen Grade - Assesses cabinetry, appliances, benchtops, tapware, style coherence
- Wet Rooms Grade - Assesses fixtures, tiling, vanity, shower/bath quality
- Street Appeal Grade - Assesses kerb appeal, landscaping, maintenance, presentation

**Completeness Score (0-100):**
- Temporal coverage
- Image quality
- Room coverage
- Recency

### 2. Market Risk Scores

Algorithmic assessment of market conditions:

**Market Trends Score (0-10):**
- Price movement direction (Rising/Falling/Flat/Volatile)
- Volatility level
- Momentum

**Local Liquidity Score (0-10):**
- Sales density
- Market absorption rate
- Listing activity

**Secondary Market Liquidity:**
- Matched pairs analysis for developments
- (N/A for detached dwellings)

**Uniqueness Score (0-10):**
- Configuration commonality
- Land area positioning
- Property type frequency
- Special features
- Market percentile

### 3. Property Risk Flags (NLP Detection)

Natural Language Processing analysis flags:

- **Acreages** - Properties > 5000m² with residential zoning
- **Display Homes** - Previous display home use
- **Holiday Rentals** - Holiday rental designation
- **Serviced Apartments** - Serviced apartment use
- **Dual Occupancy** - Second dwelling detected
- **Business Use** - Business operated from property

Each flag includes:
- Detection confidence
- Priority level (High/Medium/Low)
- Evidence details
- Valuation impact assessment
- Recommendations

### 4. Valuation Risk Assessment

Comprehensive valuation suitability analysis:

**Overall Assessment:**
- Risk rating (Low/Medium/High)
- Confidence score (0-100)
- Suitability determination

**Risk Factors:**
- Identified risks with impact scores
- Mitigation strategies

**Quality Scores:**
- Data quality (completeness, recency, accuracy, consistency)
- Comparable sales quality (quantity, proximity, recency, comparability)
- Market confidence (liquidity, trend clarity, market depth)
- Property confidence (data completeness, complexity factors, verification needs)

### 5. Comparative Analysis

Subject property vs. local market:

- Price positioning
- Land area comparison
- Configuration matching
- Property type distribution
- Age and condition
- Special features differentiation

### 6. Risk Mitigation Recommendations

Prioritized action items:
- High priority actions (critical for valuation)
- Medium priority actions (important verifications)
- Low priority actions (additional due diligence)

Each recommendation includes:
- Specific actions required
- Reason for action
- Impact on valuation
- Detailed steps

## Usage

### Step 1: Generate Data Collection Report (if not already done)

```bash
# Generate comprehensive property report
python3 scripts/comprehensive_property_report.py --property-id 13683380

# Generate Data Collection PDF
python3 scripts/generate_property_pdf.py \
    --input data/property_reports/13683380_comprehensive_report.json \
    --output data/property_reports/13683380_data_collection.pdf
```

### Step 2: Generate Classification & Scoring Report

```bash
# Generate classification & scoring JSON
python3 scripts/generate_classification_scoring_report.py \
    --property-id 13683380 \
    --output data/property_reports/13683380_classification_scoring.json

# Or from existing comprehensive report
python3 scripts/generate_classification_scoring_report.py \
    --input data/property_reports/13683380_comprehensive_report.json
```

### Step 3: Generate Classification & Scoring PDF

```bash
# Generate PDF report
python3 scripts/generate_classification_scoring_pdf.py \
    --input data/property_reports/13683380_classification_scoring.json \
    --output data/property_reports/13683380_classification_scoring.pdf
```

### Complete Workflow (All Steps)

```bash
# 1. Data Collection
python3 scripts/comprehensive_property_report.py --property-id 13683380
python3 scripts/generate_property_pdf.py \
    --input data/property_reports/13683380_comprehensive_report.json

# 2. Classification & Scoring
python3 scripts/generate_classification_scoring_report.py --property-id 13683380
python3 scripts/generate_classification_scoring_pdf.py \
    --input data/property_reports/13683380_classification_scoring.json
```

## Output Files

### JSON Output: `{property_id}_classification_scoring.json`

Complete structured data including:
- Metadata
- Imagery classification (Layer 1/2/3 + completeness)
- Market risk scores
- Property risk flags (NLP detection)
- Valuation risk assessment
- Comparative analysis
- Risk mitigation recommendations
- Report summary

### PDF Output: `{property_id}_classification_scoring_report.pdf`

Professional formatted report with 7 sections:

1. **Imagery Classification & Quality Scores** - Computer Vision analysis results
2. **Market Risk Scores** - Trends, liquidity, uniqueness assessments
3. **Property Risk Flags** - NLP detection results with priorities
4. **Valuation Risk Assessment** - Overall risk, data quality, confidence scores
5. **Comparative Analysis** - Subject vs market positioning
6. **Risk Mitigation Recommendations** - Prioritized action items
7. **Report Summary** - Overall assessment and valuation guidance

## Example Output

For property 13683380 (5 Settlers Court, Vermont South VIC 3133):

**Key Findings:**
- Overall Risk Rating: **Medium**
- Overall Confidence: **82%**
- Suitability: **Suitable with Conditions**

**Major Risk Flags Detected:**
- ⚠️ **Dual Occupancy** (High Priority) - Approved permit 430/2025 for small second dwelling
- ⚠️ **2000 Easements** (High Priority) - Exceptionally high count requiring investigation
- ⚠️ **Heritage Overlay** (Medium Priority) - Development restrictions possible

**Market Scores:**
- Market Trends: **7.5/10** (Rising market)
- Local Liquidity: **8.2/10** (High liquidity)
- Uniqueness: **6.8/10** (Moderately unique)

**Quality Scores:**
- Kitchen Grade: **3.8/5.0** (Good)
- Wet Rooms Grade: **3.5/5.0** (Good)
- Street Appeal Grade: **4.2/5.0** (Very Good)
- Imagery Completeness: **82/100** (Good)

**Estimated Valuation Range:**
- Base: $950,000 - $1,050,000 (single dwelling)
- With Dual Occupancy Premium: $1,000,000 - $1,155,000 (+5-10%)
- Confidence Interval: ±8% (pending verification)

## Current Implementation Status

### ✅ Implemented (v1.0)

- Complete JSON schema for classification & scoring data
- Classification & scoring report generator script
- PDF generator with 7 comprehensive sections
- Sample data generation for property 13683380
- Full documentation

### 🚧 Future Enhancements (Production System)

**Computer Vision Integration:**
- Replace sample scores with actual ARMATech CV API calls
- Real-time image analysis
- Confidence scoring from model outputs

**Market Risk Algorithms:**
- Time series analysis for trend detection
- Volatility calculations
- Matched pairs analysis for developments
- Statistical uniqueness scoring

**NLP Detection:**
- Train models on property descriptions and planning documents
- Expand detection categories
- Confidence calibration

**Valuation Models:**
- Automated valuation model (AVM) integration
- Risk-adjusted valuation ranges
- Comparable sales selection optimization

**Reporting:**
- Interactive HTML reports
- Visualizations (gauges, charts, heatmaps)
- Comparison dashboards

## Data Requirements

### Required Data Sources (from Data Collection phase):

- `{property_id}_comprehensive_report.json` - Main property data
- `{property_id}_property_images.json` - Image metadata for CV analysis
- `{property_id}_comparable_sales.json` - Market analysis
- `{property_id}_development_approvals.json` - NLP risk detection

### Optional Data Sources:

- `{property_id}_geospatial_layers.json` - Enhanced risk detection
- `{property_id}_mesh_block_analysis.json` - Market context

## Scoring Methodology

### Risk Score Calculation

**Overall Risk Score** = Weighted average of:
- Market Risk (30%)
- Property Risk Flags (40%)
- Data Quality (15%)
- Comparable Sales Quality (15%)

**Confidence Score** = Function of:
- Data completeness
- Data recency
- Comparable sales quantity and proximity
- Market liquidity
- Complexity factors

### Risk Rating Thresholds

- **Low Risk**: Risk Score < 4.0, Confidence > 85%
- **Medium Risk**: Risk Score 4.0-7.0, Confidence 70-85%
- **High Risk**: Risk Score > 7.0 OR Confidence < 70%

### Quality Grade Scales

**Layer 3 Quality Scores (1-5):**
- 5.0: Excellent / Premium
- 4.0-4.9: Very Good
- 3.5-3.9: Good
- 3.0-3.4: Satisfactory
- 2.5-2.9: Fair
- < 2.5: Poor

**Completeness & Confidence (0-100):**
- 90-100: Excellent
- 75-89: Good
- 60-74: Fair
- < 60: Poor

## Integration with Data Collection Report

The Classification & Scoring Report is designed to **complement, not replace** the Data Collection Report:

| Data Collection Report | Classification & Scoring Report |
|----------------------|-------------------------------|
| **What** - Raw data | **So What** - Analysis |
| Property attributes | Property scores |
| Sales history | Market risk assessment |
| Planning permits | Risk flag detection |
| Images metadata | Image quality grades |
| Comparable sales list | Comparable sales quality score |
| Market metrics | Market trend scores |

**Recommended Usage:**
1. Generate Data Collection Report → Present raw facts
2. Generate Classification & Scoring Report → Present analysis and recommendations
3. Use both reports together for comprehensive property assessment

## Troubleshooting

### Issue: Classification scoring report shows "No imagery data available"

**Solution:** Ensure `{property_id}_property_images.json` exists:
```bash
# Check if file exists
ls data/property_reports/13683380_property_images.json

# If missing, generate it from property images API
python3 scripts/get_property_images.py --property-id 13683380
```

### Issue: Market scores showing low confidence

**Cause:** Insufficient comparable sales data

**Solution:** Expand search radius or check comparable sales file:
```bash
python3 scripts/get_comparable_sales.py --property-id 13683380 --radius 10
```

### Issue: NLP detection not finding risk flags

**Status:** Expected behavior - Current implementation uses keyword matching on limited data

**Production Solution:** Implement full NLP models trained on comprehensive property descriptions and planning documents

### Issue: PDF generation fails with "Font not found"

**Solution:** Install required fonts or use reportlab's built-in fonts (already configured)

## Extending the System

### Adding New Risk Flags

1. Update `ClassificationScoringGenerator.generate_risk_flags()` in `generate_classification_scoring_report.py`
2. Add detection logic (e.g., `_check_new_risk_type()`)
3. Update JSON schema in sample data
4. Update PDF extractor in `generate_classification_scoring_pdf.py`

### Adding New Scoring Dimensions

1. Add scoring method to `ClassificationScoringGenerator`
2. Update `generate_report()` to call new method
3. Add section to PDF generator
4. Document new score in this README

### Integrating Production AI/ML Models

Replace sample score generation methods with actual model API calls:

```python
# Replace this (sample):
def _calculate_kitchen_grade(self, features):
    base_grade = 3.5
    return {...}

# With this (production):
def _calculate_kitchen_grade(self, images):
    response = armatech_cv_api.grade_kitchen(images)
    return response['grade_data']
```

## Related Documentation

- [ARCHITECTURE_ASSESSMENT.md](../documentation/claude_generated/ARCHITECTURE_ASSESSMENT.md) - PDF generation architecture
- [MAPPING_CONFIGURATION_PROPOSAL.md](../documentation/claude_generated/MAPPING_CONFIGURATION_PROPOSAL.md) - Hybrid mapping approach
- [IMPLEMENTATION_COMPLETE.md](../documentation/claude_generated/IMPLEMENTATION_COMPLETE.md) - Hybrid architecture implementation
- [prequal-concept.txt](../documentation/prequal-concept.txt) - Pre-Qualify product concept

## Support

For issues or questions:
1. Check this README and related documentation
2. Review sample output: `data/property_reports/13683380_classification_scoring.json`
3. Examine generated PDF: `data/property_reports/13683380_classification_scoring_report.pdf`
4. Contact ARMATech development team

---

**Version:** 1.0
**Last Updated:** 2025-11-10
**Author:** ARMATech Development Team
