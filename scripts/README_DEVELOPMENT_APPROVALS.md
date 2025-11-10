# Development Approvals Report Generator

Creates comprehensive JSON reports for planning permits and development approvals for properties.

## Overview

This tool generates structured JSON reports containing planning permit and development approval information, including:
- **Permit details** (number, status, dates)
- **Development descriptions**
- **Applicant information**
- **Estimated costs**
- **Permit conditions**
- **Summary statistics** (approved/pending/refused counts, date ranges)

## Files

- **`scripts/generate_development_approval_report.py`** - Main report generator
- **Output**: `data/property_reports/{property_id}_development_approvals.json`

## Usage

### Single Permit Entry (Command Line)

```bash
python3 scripts/generate_development_approval_report.py \
    --property-id 13683380 \
    --permit-number "430/2025" \
    --approval-date "2025-03-20" \
    --status "Approved" \
    --description "Change of use from dependant person's unit to small second dwelling" \
    --address "5 Settlers Court, Vermont South VIC 3133"
```

### Multiple Permits (JSON Input)

Create a JSON input file:

```json
{
  "permits": [
    {
      "permit_number": "430/2025",
      "status": "Approved",
      "approval_date": "2025-03-20",
      "description": "Change of use from dependant person's unit to small second dwelling",
      "applicant": "John Smith",
      "estimated_cost": 50000,
      "conditions": [
        "Works must commence within 2 years",
        "Landscaping plan required"
      ]
    },
    {
      "permit_number": "285/2023",
      "status": "Approved",
      "lodgement_date": "2023-04-15",
      "approval_date": "2023-06-20",
      "description": "Two storey rear extension",
      "permit_type": "Planning Permit",
      "estimated_cost": 150000
    }
  ]
}
```

Then run:

```bash
python3 scripts/generate_development_approval_report.py \
    --property-id 13683380 \
    --input-json data/permits/13683380_permits.json \
    --address "5 Settlers Court, Vermont South VIC 3133"
```

## Command Line Arguments

### Required
- `--property-id` - Property ID (integer)

### Optional
- `--address` - Property address (for metadata)
- `--permit-number` - Permit/application number
- `--status` - Approval status (Approved, Pending, Refused, Withdrawn, Issued, Submitted)
- `--approval-date` - Approval/decision date (YYYY-MM-DD format)
- `--lodgement-date` - Application lodgement date (YYYY-MM-DD format)
- `--description` - Development description
- `--permit-type` - Permit type (default: Planning Permit)
- `--applicant` - Applicant name
- `--estimated-cost` - Estimated development cost (float)
- `--input-json` - Load permits from JSON file
- `--output-dir` - Output directory (default: data/property_reports)

## Output Structure

```json
{
  "metadata": {
    "property_id": 13683380,
    "property_address": "5 Settlers Court, Vermont South VIC 3133",
    "report_timestamp": "2025-11-10T16:26:51.312638",
    "total_permits": 1,
    "report_type": "Development Approvals"
  },
  "summary": {
    "approved_permits": 1,
    "pending_permits": 0,
    "refused_permits": 0,
    "withdrawn_permits": 0,
    "latest_permit_date": "2025-03-20",
    "oldest_permit_date": "2025-03-20",
    "permit_types": {
      "Planning Permit": 1
    },
    "total_estimated_cost": 0.0
  },
  "permits": [
    {
      "permit_number": "430/2025",
      "status": "Approved",
      "lodgement_date": null,
      "decision_date": "2025-03-20",
      "description": "Change of use from dependant person's unit to small second dwelling",
      "permit_type": "Planning Permit",
      "applicant": null,
      "estimated_cost": null,
      "conditions": []
    }
  ]
}
```

## Console Output

```
======================================================================
🏗️  DEVELOPMENT APPROVALS REPORT
======================================================================

🏠 Property: 13683380
   Address: 5 Settlers Court, Vermont South VIC 3133

📊 Permit Statistics:
   Total Permits: 1
   Approved: 1
   Pending: 0
   Refused: 0
   Withdrawn: 0

📅 Date Range:
   Oldest: 2025-03-20
   Latest: 2025-03-20

📋 Permit Types:
   Planning Permit: 1

📄 Recent Permits:

   Permit: 430/2025
   Status: Approved
   Date: 2025-03-20
   Description: Change of use from dependant person's unit to small second dwelling

======================================================================
```

## Integration with Property Reports

The development approvals can be integrated into comprehensive property reports:

```python
from scripts.generate_development_approval_report import generate_report
import json

# Load development approvals
with open('data/property_reports/13683380_development_approvals.json') as f:
    approvals = json.load(f)

# Add to property report
report['development_approvals'] = {
    'total_permits': approvals['metadata']['total_permits'],
    'approved': approvals['summary']['approved_permits'],
    'latest_permit': approvals['permits'][0] if approvals['permits'] else None
}
```

## Data Sources

Development approval data can be sourced from:

1. **Council Planning Registers**
   - Online planning permit search
   - Council planning department

2. **State Planning Portals**
   - VicPlan (Victoria)
   - PlanningPortal (NSW)

3. **Property Information Reports**
   - Title searches
   - Building reports

4. **Manual Entry**
   - Site inspections
   - Owner/agent disclosure

## Permit Status Types

- **Approved/Issued** - Permit granted
- **Pending/Submitted** - Application under review
- **Refused/Rejected** - Application denied
- **Withdrawn** - Application withdrawn by applicant

## Permit Types

Common permit types include:
- Planning Permit
- Building Permit
- Subdivision Permit
- Demolition Permit
- Development Approval
- VicSmart Application

## Use Cases for Valuers

### 1. **Development Potential Assessment**
   - Recent approvals indicate development feasibility
   - Approved but uncommenced permits show potential
   - Refused permits identify planning constraints

### 2. **Highest and Best Use Analysis**
   - Approved non-conforming uses
   - Development approval history
   - Demonstrated council support for uses

### 3. **Due Diligence**
   - Verify legal compliance
   - Identify unauthorized works
   - Check permit conditions compliance

### 4. **Market Value Impact**
   - Recent approvals may increase value
   - Pending permits create uncertainty
   - Multiple refusals suggest constraints

### 5. **Risk Assessment**
   - Identify expired permits
   - Check condition compliance
   - Assess enforcement risk

## Example Queries

After generating the report, use the JSON to answer:

1. **"Are there any approved planning permits?"**
   → Check `summary.approved_permits`

2. **"What was the most recent development approval?"**
   → Check first item in `permits` array (sorted by date)

3. **"What is the total estimated development cost?"**
   → Check `summary.total_estimated_cost`

4. **"Are there any pending applications?"**
   → Check `summary.pending_permits`

5. **"What types of permits have been issued?"**
   → Check `summary.permit_types`

## Future Enhancements

- [ ] Automatic council planning register scraping
- [ ] Link to VicPlan/PlanningPortal APIs
- [ ] Permit condition compliance tracking
- [ ] Expiry date alerts
- [ ] Compare against as-built conditions
- [ ] Integration with building permit data
- [ ] Permit value estimation (for older permits without costs)
- [ ] Neighbour objection tracking

## Related Tools

- **Property Report Generator**: [scripts/comprehensive_property_report.py](./comprehensive_property_report.py)
- **PDF Generator**: [scripts/generate_property_pdf.py](./generate_property_pdf.py)
- **Planning Zones**: [scripts/analyze_planning_zones.py](./analyze_planning_zones.py)

---

**Author**: Development Approval Report Generator
**Date**: 2025-11-10
**Purpose**: Track and analyze planning permits and development approvals
