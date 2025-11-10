# JSON to PDF Mapping Configuration - Analysis & Proposal

## Current State: Hardcoded in Python

### Current Implementation Example:

```python
# scripts/generate_property_pdf.py - Lines ~1422-1430
def _extract_category_2_location_admin(self, report, mesh_block_data, planning_zones, development_approvals):
    site = property_details.get('site', {})
    zone_code = site.get('zoneCodeLocal', 'Unknown')
    zone_description = site.get('zoneDescriptionLocal', 'Unknown')

    rows.append(("Zoning > Code", zone_code))
    rows.append(("Zoning > Description", zone_description))
```

**Mapping is embedded in code:**
- Path: `property_details.site.zoneCodeLocal`
- Label: `"Zoning > Code"`
- Fallback: `'Unknown'`
- All defined in Python code

## Question: Should Mapping Be in a Separate File?

### Answer: **IT DEPENDS** - Let me break down the tradeoffs

## When Configuration Files Make Sense

### ✅ Use Configuration File When:

1. **Non-technical users need to modify mappings**
   - Business analysts want to add/remove fields
   - Clients want custom report layouts
   - QA team needs to test different configurations

2. **Multiple mapping profiles needed**
   - Residential property reports
   - Commercial property reports
   - Industrial property reports
   - Different markets (VIC, NSW, QLD)

3. **Frequent mapping changes**
   - Data source changes regularly
   - Field names evolve
   - Client requirements shift often

4. **A/B testing report layouts**
   - Test different field orderings
   - Compare different groupings
   - Measure which fields users value

5. **Multi-tenant system**
   - Different clients see different fields
   - Custom branding per client
   - Regional variations

### ❌ Keep in Code When:

1. **Stable, single-purpose tool**
   - One report format
   - Infrequent changes
   - Single user/team

2. **Complex conditional logic**
   - Field visibility depends on data values
   - Calculations between fields
   - Dynamic grouping based on property type

3. **Tight integration with business logic**
   - Data transformations
   - Validation rules
   - Computed fields

4. **Performance critical**
   - Need to optimize data access
   - Caching strategies
   - Database query optimization

## Your Situation Analysis

### Current Context:
- **Purpose:** Internal valuation tool
- **Users:** Residential valuers (technical enough to read Python)
- **Change frequency:** Moderate (adding new data sources)
- **Complexity:** High (11 categories, 7 JSON sources, conditional logic)
- **Number of formats:** 1 main format (Pre-Qualification Data Collection)

### Recommendation: **HYBRID APPROACH**

Use configuration for **simple field mappings**, keep **complex logic in code**.

## Proposed Hybrid Architecture

### 1. Simple Field Mappings → YAML Configuration

```yaml
# config/report_mapping.yaml

categories:
  - id: 2
    name: "LOCATION AND ADMINISTRATIVE"
    subsections:

      - name: "ADDRESS"
        fields:
          - label: "Full Address"
            source: "property_details"
            path: "address.singleLine"
            fallback: "Unknown"

          - label: "Street Number"
            source: "property_details"
            path: "address.streetNumber"
            fallback: ""

      - name: "PLANNING AND ZONING"
        fields:
          - label: "Zoning > Code"
            source: "property_details"
            path: "site.zoneCodeLocal"
            fallback: "Unknown"

          - label: "Zoning > Description"
            source: "property_details"
            path: "site.zoneDescriptionLocal"
            fallback: "Unknown"

  - id: 4
    name: "LEGAL"
    subsections:

      - name: "TITLE"
        fields:
          - label: "Title Type"
            source: "property_details"
            path: "title.titleType"
            fallback: "N/A"

          - label: "Certificate of Title"
            source: "property_details"
            path: "title.certificateOfTitle"
            fallback: "N/A"
```

### 2. Complex Logic → Python Code

```python
# scripts/extractors/planning_zone_extractor.py

class PlanningZoneExtractor:
    """Complex extraction logic that can't be in config"""

    def extract_section_1_uses(self, zone_data):
        """
        Extract Section 1 permits with:
        - Numbered list formatting
        - Limit to 10 items
        - Show overflow count
        """
        section1_uses = zone_data.get('table_of_uses', {}).get('section_1_uses', [])

        if not section1_uses:
            return [("Section 1 - Permit NOT Required", "Unknown")]

        rows = [("Section 1 - Permit NOT Required", "")]
        for i, use in enumerate(section1_uses[:10], 1):
            rows.append((f"  {i}", self._truncate_text(use, 100)))

        if len(section1_uses) > 10:
            rows.append(("  ...", f"+ {len(section1_uses) - 10} more uses"))

        return rows
```

### 3. Mapping Engine → Python Code

```python
# scripts/utils/mapping_engine.py

import yaml
from pathlib import Path
from typing import Dict, Any, List, Tuple

class MappingEngine:
    """Reads YAML config and extracts simple field mappings"""

    def __init__(self, config_path: str = "config/report_mapping.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

    def get_field_value(self, data: Dict[str, Any], source: str, path: str, fallback: Any = None):
        """
        Extract value from nested dict using dot notation path.

        Args:
            data: Full data dictionary containing all sources
            source: Source data file (e.g., "property_details", "planning_zones")
            path: Dot-notation path (e.g., "site.zoneCodeLocal")
            fallback: Value to return if not found

        Returns:
            Extracted value or fallback
        """
        # Get the source data
        source_data = data.get(source, {})

        # Navigate the path
        keys = path.split('.')
        current = source_data

        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
                if current is None:
                    return fallback
            else:
                return fallback

        return current if current is not None else fallback

    def extract_category(self, category_id: int, data: Dict[str, Any]) -> List[Tuple[str, str]]:
        """
        Extract all fields for a category using config.

        Args:
            category_id: Category ID (1-11)
            data: Dictionary containing all data sources

        Returns:
            List of (label, value) tuples
        """
        rows = []

        # Find category in config
        category = next((c for c in self.config['categories'] if c['id'] == category_id), None)
        if not category:
            return rows

        # Add category header
        rows.append((category['name'], ""))

        # Process subsections
        for subsection in category.get('subsections', []):
            rows.append((subsection['name'], ""))

            # Extract fields
            for field in subsection.get('fields', []):
                label = field['label']
                value = self.get_field_value(
                    data=data,
                    source=field['source'],
                    path=field['path'],
                    fallback=field.get('fallback', 'Unknown')
                )
                rows.append((label, str(value)))

            rows.append(("", ""))  # Spacer

        return rows
```

## Example: Refactored Category 2 (Hybrid)

### YAML Config (Simple Fields):

```yaml
# config/report_mapping.yaml
categories:
  - id: 2
    name: "LOCATION AND ADMINISTRATIVE"
    subsections:
      - name: "ADDRESS"
        fields:
          - {label: "Full Address", source: "property_details", path: "address.singleLine", fallback: "Unknown"}
          - {label: "Street Number", source: "property_details", path: "address.streetNumber", fallback: ""}
          - {label: "Street Name", source: "property_details", path: "address.streetName", fallback: ""}
          - {label: "Suburb", source: "property_details", path: "address.suburb", fallback: ""}
          - {label: "Postcode", source: "property_details", path: "address.postcode", fallback: ""}

      - name: "LOCATION"
        fields:
          - {label: "Latitude", source: "property_details", path: "location.latitude", fallback: "N/A"}
          - {label: "Longitude", source: "property_details", path: "location.longitude", fallback: "N/A"}
          - {label: "Council", source: "property_details", path: "location.councilArea", fallback: "N/A"}

      - name: "PLANNING AND ZONING"
        fields:
          - {label: "Zoning > Code", source: "property_details", path: "site.zoneCodeLocal", fallback: "Unknown"}
          - {label: "Zoning > Description", source: "property_details", path: "site.zoneDescriptionLocal", fallback: "Unknown"}

        # Complex fields handled by custom extractors (defined separately)
        custom_extractors:
          - name: "planning_zone_section_1"
            method: "extract_section_1_uses"
          - name: "planning_zone_section_2"
            method: "extract_section_2_uses"
          - name: "planning_zone_opportunities"
            method: "extract_opportunities_and_requirements"

      - name: "DEVELOPMENT APPROVALS"
        custom_extractors:
          - name: "development_approvals_summary"
            method: "extract_development_approvals"
```

### Python Code (Complex Logic):

```python
# scripts/generate_property_pdf.py

from utils.mapping_engine import MappingEngine
from extractors.planning_zone_extractor import PlanningZoneExtractor
from extractors.development_approvals_extractor import DevelopmentApprovalsExtractor

class PropertyDataPDFGenerator:

    def __init__(self):
        self.mapping_engine = MappingEngine()
        self.planning_extractor = PlanningZoneExtractor()
        self.approvals_extractor = DevelopmentApprovalsExtractor()

    def extract_data_categorized(self, report: Dict[str, Any]) -> List[Tuple[str, str]]:
        data_rows = []

        # Load all data sources
        all_data = {
            'property_details': report.get('property_details', {}),
            'planning_zones': self._load_planning_zones(output_dir),
            'development_approvals': self._load_development_approvals(output_dir, property_id),
            # ... other sources
        }

        # Extract Category 2 using hybrid approach
        category_2_rows = self._extract_category_2_hybrid(all_data)
        data_rows.extend(category_2_rows)

        return data_rows

    def _extract_category_2_hybrid(self, all_data: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Extract Category 2 using config + custom extractors"""
        rows = []

        # Get category config
        category = next(c for c in self.mapping_engine.config['categories'] if c['id'] == 2)

        rows.append((category['name'], ""))

        for subsection in category['subsections']:
            rows.append((subsection['name'], ""))

            # Extract simple fields from config
            for field in subsection.get('fields', []):
                label = field['label']
                value = self.mapping_engine.get_field_value(
                    data=all_data,
                    source=field['source'],
                    path=field['path'],
                    fallback=field.get('fallback', 'Unknown')
                )
                rows.append((label, str(value)))

            # Run custom extractors for complex logic
            for extractor_config in subsection.get('custom_extractors', []):
                method_name = extractor_config['method']

                if method_name == 'extract_section_1_uses':
                    rows.extend(self.planning_extractor.extract_section_1_uses(
                        all_data.get('planning_zones')
                    ))

                elif method_name == 'extract_section_2_uses':
                    rows.extend(self.planning_extractor.extract_section_2_uses(
                        all_data.get('planning_zones')
                    ))

                elif method_name == 'extract_opportunities_and_requirements':
                    rows.extend(self.planning_extractor.extract_opportunities_and_requirements(
                        all_data.get('planning_zones')
                    ))

                elif method_name == 'extract_development_approvals':
                    rows.extend(self.approvals_extractor.extract_summary(
                        all_data.get('development_approvals')
                    ))

            rows.append(("", ""))  # Spacer

        return rows
```

## Benefits of Hybrid Approach

### ✅ Configuration File Benefits:
1. **Visibility** - All simple field mappings in one place
2. **Non-programmer editable** - Can modify field labels, paths without Python knowledge
3. **Documentation** - Config serves as documentation of data structure
4. **Version control** - Easy to see what changed in mappings
5. **Validation** - Can validate YAML schema separately
6. **Testing** - Can test with different configs

### ✅ Code Benefits:
1. **Complex logic** - Conditional formatting, calculations, transformations
2. **Type safety** - Python type hints and validation
3. **Debugging** - Can step through with debugger
4. **Performance** - Can optimize hot paths
5. **Reusability** - Complex extractors can be shared across categories

## Comparison Table

| Aspect | All Hardcoded | All Config | Hybrid (Recommended) |
|--------|---------------|------------|----------------------|
| **Simple fields** | ❌ Scattered in code | ✅ Centralized in YAML | ✅ Centralized in YAML |
| **Complex logic** | ✅ Full Python power | ❌ Limited by config format | ✅ Full Python power |
| **Maintainability** | ❌ Hard to find mappings | ⚠️ Config can get complex | ✅ Clear separation |
| **Flexibility** | ✅ Can do anything | ❌ Limited to config schema | ✅ Best of both |
| **Testing** | ⚠️ Need to test all code | ⚠️ Config parsing fragile | ✅ Test config + logic separately |
| **Performance** | ✅ Fast | ⚠️ Config parsing overhead | ✅ Cache config |
| **Learning curve** | ⚠️ Must read all code | ⚠️ Must learn config schema | ✅ Config is self-documenting |

## Implementation Recommendation for Your Project

### Phase 1: Quick Wins (1-2 days)
1. **Extract utility methods** (high priority):
   ```python
   # utils/data_utils.py
   def get_nested_value(data: dict, path: str, fallback: Any = "Unknown") -> Any:
       """Get value from nested dict using 'site.zoneCodeLocal' notation"""

   def format_missing_value(value: Any, fallback: str = "Unknown") -> str:
       """Consistent handling of missing/None values"""

   def truncate_text(text: str, max_length: int = 100, ellipsis: str = "...") -> str:
       """Truncate text with ellipsis"""
   ```

2. **Refactor one category** as proof of concept using hybrid approach

### Phase 2: Structured Improvement (1 week)
3. Create YAML config for **simple field mappings only** (ADDRESS, LOCATION, basic fields)
4. Keep **complex logic in Python** (planning zones, development approvals, imagery)
5. Build `MappingEngine` class to read config and extract simple fields

### Phase 3: Full Migration (2-3 weeks)
6. Migrate all simple fields to config
7. Create specialized extractors for complex fields
8. Add validation and error handling
9. Write comprehensive tests

## My Specific Recommendation for You

**Start with utilities, delay full config file**

### Rationale:
1. **Your system is evolving rapidly** - Adding development approvals, planning zones, etc.
2. **Complex extraction logic** - Planning zones have conditional formatting, numbered lists, overflow handling
3. **Single user/team** - You can read Python code
4. **Performance acceptable** - No need to optimize config parsing yet

### What to do NOW:
```python
# Step 1: Extract these utilities (2 hours of work)
# utils/extraction_utils.py

def get_nested_value(data: dict, path: str, fallback: Any = "Unknown") -> Any:
    """Navigate nested dict with 'site.zoneCodeLocal' notation"""
    keys = path.split('.')
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
            if current is None:
                return fallback
        else:
            return fallback
    return current if current is not None else fallback

# Then refactor your code to use it:
zone_code = get_nested_value(site, 'zoneCodeLocal', 'Unknown')
# Instead of: zone_code = site.get('zoneCodeLocal', 'Unknown')
```

This gives you **80% of the benefits** with **20% of the effort**.

### What to do LATER (when stable):
- Create YAML config for simple fields
- Keep complex logic in Python
- Use hybrid approach

## Bottom Line

**For your current project:**
- ✅ Extract utility functions NOW (high ROI)
- ⏸️ Delay config file UNTIL system stabilizes
- ✅ Use hybrid approach WHEN you add multiple report formats

**Config files are valuable, but premature optimization for a single-format, rapidly-evolving tool.**

---

**Date:** 2025-11-10
**Analysis by:** Claude (Sonnet 4.5)
