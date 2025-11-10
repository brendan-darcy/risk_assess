# Property Reporting System Refactoring Plan
## Strict DRY Principles & Proper Data Flow Architecture

**Date:** 2025-11-10
**Status:** Implementation Plan
**Priority:** High - Foundation for maintainable system

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Current State Analysis](#current-state-analysis)
3. [Identified Issues](#identified-issues)
4. [Proposed Architecture](#proposed-architecture)
5. [Data Flow Design](#data-flow-design)
6. [Implementation Plan](#implementation-plan)
7. [Migration Strategy](#migration-strategy)
8. [Before/After Examples](#beforeafter-examples)

---

## Executive Summary

The current property reporting system has grown organically with ~40 scripts and significant code duplication. This refactoring establishes a clean, maintainable architecture based on:

- **Strict DRY (Don't Repeat Yourself)** - Zero code duplication through proper abstraction
- **Clear Data Flow** - Separation of RAW DATA → ETL → PROCESSED → REPORTS layers
- **Base Class Architecture** - Reusable abstractions for all components
- **Dependency Injection** - Loose coupling and testability

**Key Metrics:**
- Current: 40+ scripts, ~9,222 lines of utilities, significant duplication
- Target: ~20 core scripts, base classes reduce duplication by 60-70%

---

## Current State Analysis

### File Structure
```
scripts/
├── comprehensive_property_report.py      # 661 lines - orchestrates reports
├── generate_property_pdf.py              # 3,770+ lines - PDF generation
├── fetch_property_images.py              # ~300 lines - image fetching
├── analyze_planning_zones.py             # ~600 lines - planning analysis
├── check_geospatial_layers.py           # ~600 lines - geospatial checks
├── run_places_analysis.py               # ~100 lines - Google Places
├── comparable_data_processor.py         # ~600 lines - comparables
├── run_full_analysis.py                 # ~200 lines - orchestration
├── utils/                               # 9,222 total lines
│   ├── corelogic_processor_updated.py   # 538 lines
│   ├── property_data_processor.py       # 924 lines
│   ├── geospatial_api_client.py         # 318 lines
│   ├── google_api_processor.py          # 737 lines
│   ├── comparable_sales_generator.py    # ~400 lines
│   ├── market_data_processor.py         # ~500 lines
│   ├── mesh_block_analysis_pipeline.py  # ~500 lines
│   ├── mapping_engine.py                # ~400 lines
│   ├── pipeline_utils.py                # Large base utilities
│   └── ... (10+ more utilities)
└── extractors/
    ├── planning_zone_extractor.py       # ~180 lines
    ├── development_approvals_extractor.py # ~100 lines
    └── encumbrances_extractor.py        # ~80 lines
```

### Output Files (Data Flow Endpoints)
```
data/property_reports/{property_id}_*:
├── comprehensive_report.json            # Complete aggregated report
├── property_details.json                # CoreLogic API raw data
├── geospatial_layers.json              # Geospatial analysis
├── mesh_block_analysis.json            # Demographic data
├── comparable_sales.json               # Sales comparables
├── property_images.json                # Image metadata
├── property_impacts.json               # Google Places analysis
├── development_approvals.json          # Planning permits
└── final_saved_rebuild.pdf             # Final PDF report
```

---

## Identified Issues

### 1. Code Duplication (Violates DRY)

#### API Client Patterns (Repeated 3-4 times)
```python
# Found in: corelogic_processor_updated.py, property_data_processor.py,
#           geospatial_api_client.py, google_api_processor.py

# Pattern 1: Authentication (repeated in 4 files)
def __init__(self, client_id: str, client_secret: str):
    self.client_id = client_id
    self.client_secret = client_secret
    self.access_token = None
    self.token_expiry = None

def get_access_token(self):
    if self.access_token and time.time() < self.token_expiry:
        return self.access_token
    # ... token refresh logic (duplicated 4 times)

# Pattern 2: HTTP requests (repeated in 4 files)
headers = {
    "Authorization": f"Bearer {self.access_token}",
    "accept": "application/json"
}
response = requests.get(url, headers=headers, timeout=30)
if response.status_code == 200:
    return response.json()
# ... error handling (duplicated 4 times)
```

#### Data Flattening (Repeated 3 times)
```python
# Found in: corelogic_processor_updated.py, property_data_processor.py,
#           comprehensive_property_report.py

def flatten_json_recursive(data: Dict, parent_key='', sep='_'):
    items = []
    for k, v in data.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_json_recursive(v, new_key, sep).items())
        elif isinstance(v, list):
            # ... list handling logic (duplicated)
        else:
            items.append((new_key, v))
    return dict(items)
```

#### File Operations (Repeated 5+ times)
```python
# Found in: Every processor file

# Saving JSON (repeated pattern)
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_path, 'w') as f:
    json.dump(data, f, indent=2)

# Loading JSON (repeated pattern)
with open(input_path, 'r') as f:
    data = json.load(f)
```

#### Progress Reporting (Repeated everywhere)
```python
# Found in: Every script file

print(f"✅ {message}")  # Success (inconsistent emoji usage)
print(f"❌ {message}")  # Error
print(f"⚠️  {message}") # Warning
```

### 2. Data Flow Violations

#### Missing Layer Separation
Current flow mixes concerns:
```python
# comprehensive_property_report.py (lines 88-144)
# PROBLEM: Mixes RAW API calls with PROCESSING in same method
def get_comprehensive_property_details(self, property_id: str):
    # RAW DATA EXTRACTION (should be in ETL layer)
    endpoints = {...}
    results = {}
    for key, endpoint in endpoints.items():
        response = requests.get(url, headers=headers)  # Raw API call
        if response.status_code == 200:
            results[key] = response.json()

    # PROCESSING (mixing concerns)
    return results  # Returns raw + processed mixed together
```

Should be:
```python
# Layer 1: RAW DATA
raw_data = api_client.fetch_property_details(property_id)

# Layer 2: ETL (separate class)
processed_data = etl_processor.transform_property_data(raw_data)

# Layer 3: REPORT GENERATION
report = report_generator.generate_comprehensive_report(processed_data)
```

#### Direct API Calls in Reports
```python
# generate_property_pdf.py makes direct API calls
# Should consume pre-processed data files instead
response = requests.get(f"{base_url}/property-details/...")  # BAD
```

### 3. Missing Abstractions

#### No Base API Client
All API clients reimplement:
- Authentication logic
- Request handling
- Error handling
- Retry logic
- Rate limiting

#### No Base Processor
All processors reimplement:
- Data loading
- Data transformation
- Error handling
- Logging
- Validation

#### No Base Report Generator
All report generators reimplement:
- Data aggregation
- File I/O
- Progress reporting
- Error handling

### 4. Utility Organization Issues

Current `utils/` is flat and mixed:
```
utils/
├── corelogic_processor_updated.py      # API client + processor mixed
├── property_data_processor.py          # Processor with embedded API calls
├── geospatial_api_client.py           # Pure API client (good)
├── google_api_processor.py            # API client + processor mixed
├── comparable_sales_generator.py       # Generator + API calls mixed
├── market_data_processor.py           # Processor + API calls mixed
├── mesh_block_analysis_pipeline.py    # Pipeline + GIS mixed
└── pipeline_utils.py                  # Kitchen sink (good base utilities)
```

Should be organized by purpose:
```
scripts/
├── core/                    # Base classes & interfaces
├── api/                     # API clients only
├── etl/                     # Data transformation pipelines
├── processors/              # Business logic processors
├── generators/              # Report generators
└── extractors/              # PDF extractors (already good)
```

---

## Proposed Architecture

### Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    REPORTS & ANALYSIS                       │
│  (PDF reports, comprehensive reports, visualizations)       │
│  Files: generate_property_pdf.py, comprehensive_report.py   │
└────────────────────────┬────────────────────────────────────┘
                         │ Consumes processed data
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   PROCESSED OUTPUTS                         │
│  (Intermediate JSON reports in data/property_reports/)      │
│  - property_details.json (processed CoreLogic data)         │
│  - geospatial_layers.json (processed geospatial)           │
│  - comparable_sales.json (processed comparables)           │
│  - property_impacts.json (processed Google Places)         │
└────────────────────────┬────────────────────────────────────┘
                         │ Generated by
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                       ETL LAYER                             │
│  (Extract, Transform, Load pipelines)                       │
│  Classes: PropertyETL, GeospatialETL, ComparableETL        │
│  Location: scripts/etl/                                     │
└────────────────────────┬────────────────────────────────────┘
                         │ Uses
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                      RAW DATA                               │
│  (Direct API responses, no processing)                      │
│  Sources: CoreLogic API, Google Places API, Vicmap API     │
│  Accessed via: scripts/api/ clients                        │
└─────────────────────────────────────────────────────────────┘
```

### Class Hierarchy

```python
# scripts/core/base_api_client.py
class BaseAPIClient(ABC):
    """Base for all API clients"""
    - Authentication management
    - Request handling with retry
    - Rate limiting
    - Error handling
    - Response caching

    @abstractmethod
    def authenticate() -> str
    @abstractmethod
    def make_request() -> Dict

# scripts/core/base_etl_processor.py
class BaseETLProcessor(ABC):
    """Base for all ETL processors"""
    - Data validation
    - Transformation pipelines
    - Error handling
    - Progress reporting

    @abstractmethod
    def extract() -> Dict
    @abstractmethod
    def transform() -> Dict
    @abstractmethod
    def load() -> Path

# scripts/core/base_report_generator.py
class BaseReportGenerator(ABC):
    """Base for all report generators"""
    - Data aggregation
    - Template rendering
    - File output
    - Validation

    @abstractmethod
    def gather_data() -> Dict
    @abstractmethod
    def generate() -> Path

# scripts/core/base_data_processor.py
class BaseDataProcessor(ABC):
    """Base for business logic processors"""
    - Data transformation
    - Business rules application
    - Validation

    @abstractmethod
    def process() -> Dict
```

### Concrete Implementations

```python
# scripts/api/corelogic_client.py
class CoreLogicClient(BaseAPIClient):
    """CoreLogic API client (authentication + requests only)"""
    - OAuth2 token management
    - Endpoint wrappers
    - NO data processing

# scripts/api/google_places_client.py
class GooglePlacesClient(BaseAPIClient):
    """Google Places API client"""
    - API key authentication
    - Search endpoints
    - NO impact analysis

# scripts/api/vicmap_client.py
class VicmapClient(BaseAPIClient):
    """Vicmap geospatial API client"""
    - Token management
    - Layer queries
    - NO spatial analysis

# scripts/etl/property_etl.py
class PropertyETL(BaseETLProcessor):
    """ETL for property data from CoreLogic"""
    def extract():  # Get raw data from CoreLogicClient
    def transform():  # Flatten, validate, enrich
    def load():  # Save property_details.json

# scripts/etl/geospatial_etl.py
class GeospatialETL(BaseETLProcessor):
    """ETL for geospatial layers"""
    def extract():  # Get raw data from VicmapClient
    def transform():  # Process layers, calculate features
    def load():  # Save geospatial_layers.json

# scripts/etl/comparable_sales_etl.py
class ComparableSalesETL(BaseETLProcessor):
    """ETL for comparable sales analysis"""
    def extract():  # Get raw sales data
    def transform():  # Calculate comparables, ranking
    def load():  # Save comparable_sales.json

# scripts/etl/places_impact_etl.py
class PlacesImpactETL(BaseETLProcessor):
    """ETL for Google Places impact analysis"""
    def extract():  # Get raw places data
    def transform():  # Categorize, calculate impacts
    def load():  # Save property_impacts.json

# scripts/processors/comparable_processor.py
class ComparableProcessor(BaseDataProcessor):
    """Business logic for comparable analysis"""
    - Ranking algorithms
    - Similarity calculations
    - Distance weighting

# scripts/processors/impact_processor.py
class ImpactProcessor(BaseDataProcessor):
    """Business logic for impact categorization"""
    - Impact level rules
    - Distance thresholds
    - Severity calculations

# scripts/generators/comprehensive_report_generator.py
class ComprehensiveReportGenerator(BaseReportGenerator):
    """Generate comprehensive JSON report"""
    def gather_data():  # Load all processed JSON files
    def generate():  # Aggregate into comprehensive_report.json

# scripts/generators/pdf_report_generator.py
class PDFReportGenerator(BaseReportGenerator):
    """Generate PDF report"""
    def gather_data():  # Load processed JSON files
    def generate():  # Render PDF from template
```

---

## Data Flow Design

### Proper Flow Implementation

```python
# Step 1: RAW DATA EXTRACTION (API Layer)
from scripts.api.corelogic_client import CoreLogicClient

client = CoreLogicClient.from_env()
raw_property_data = client.get_property_details(property_id)
raw_sales_data = client.get_sales_history(property_id)
# Returns: Pure API responses, no processing

# Step 2: ETL TRANSFORMATION (ETL Layer)
from scripts.etl.property_etl import PropertyETL

etl = PropertyETL(client=client, reporter=reporter)
processed_data = etl.run(
    property_id=property_id,
    output_path="data/property_reports/{property_id}_property_details.json"
)
# Returns: Processed, validated, enriched data saved to file

# Step 3: BUSINESS PROCESSING (Processors Layer)
from scripts.processors.comparable_processor import ComparableProcessor

processor = ComparableProcessor()
comparables = processor.find_comparables(
    property_data=processed_data,
    search_radius=2000,
    min_matches=5
)
# Returns: Business logic results

# Step 4: REPORT GENERATION (Generators Layer)
from scripts.generators.comprehensive_report_generator import ComprehensiveReportGenerator

generator = ComprehensiveReportGenerator(
    property_id=property_id,
    data_dir="data/property_reports"
)
report_path = generator.generate()
# Returns: Path to comprehensive_report.json (aggregates all processed files)

# Step 5: PDF GENERATION (Generators Layer)
from scripts.generators.pdf_report_generator import PDFReportGenerator

pdf_generator = PDFReportGenerator(
    report_data=report_path,
    template="templates/property_report.html"
)
pdf_path = pdf_generator.generate()
# Returns: Path to final PDF
```

### Data Dependencies

```
CoreLogic API
    ├─→ PropertyETL → property_details.json
    └─→ ComparableSalesETL → comparable_sales.json

Vicmap API
    └─→ GeospatialETL → geospatial_layers.json

Google Places API
    └─→ PlacesImpactETL → property_impacts.json

CoreLogic Images API
    └─→ PropertyImagesETL → property_images.json

All Processed JSON files
    └─→ ComprehensiveReportGenerator → comprehensive_report.json
        └─→ PDFReportGenerator → final_report.pdf
```

---

## Implementation Plan

### Phase 1: Foundation (Week 1)

#### Task 1.1: Create Base Classes
```bash
scripts/core/
├── __init__.py
├── base_api_client.py          # BaseAPIClient abstract class
├── base_etl_processor.py       # BaseETLProcessor abstract class
├── base_report_generator.py    # BaseReportGenerator abstract class
├── base_data_processor.py      # BaseDataProcessor abstract class
├── interfaces.py               # Type definitions and protocols
└── exceptions.py               # Custom exception hierarchy
```

**Files to create:**
- `/scripts/core/base_api_client.py`
- `/scripts/core/base_etl_processor.py`
- `/scripts/core/base_report_generator.py`
- `/scripts/core/base_data_processor.py`

#### Task 1.2: Create API Clients (Refactor Existing)
```bash
scripts/api/
├── __init__.py
├── corelogic_client.py         # Refactor from corelogic_processor_updated.py
├── google_places_client.py     # Refactor from google_api_processor.py
├── vicmap_client.py            # Refactor from geospatial_api_client.py
└── corelogic_images_client.py  # Refactor from property_images_client.py
```

**Refactoring work:**
- Extract pure API logic from `utils/corelogic_processor_updated.py`
- Extract pure API logic from `utils/google_api_processor.py`
- Move `utils/geospatial_api_client.py` → `api/vicmap_client.py`
- Move `utils/property_images_client.py` → `api/corelogic_images_client.py`

### Phase 2: ETL Layer (Week 2)

#### Task 2.1: Create ETL Processors
```bash
scripts/etl/
├── __init__.py
├── property_etl.py             # Property data ETL
├── geospatial_etl.py           # Geospatial layers ETL
├── comparable_sales_etl.py     # Comparable sales ETL
├── places_impact_etl.py        # Google Places impact ETL
├── mesh_block_etl.py           # Mesh block analysis ETL
└── property_images_etl.py      # Property images ETL
```

**Implementation:**
- Move transformation logic from processors to ETL
- Implement extract/transform/load pattern
- Standardize output formats

#### Task 2.2: Create Data Processors
```bash
scripts/processors/
├── __init__.py
├── comparable_processor.py     # Comparable ranking logic
├── impact_processor.py         # Impact categorization logic
├── market_processor.py         # Market analysis logic
└── spatial_processor.py        # Spatial analysis logic
```

### Phase 3: Report Generation (Week 3)

#### Task 3.1: Create Report Generators
```bash
scripts/generators/
├── __init__.py
├── comprehensive_report_generator.py  # Aggregate all data
├── pdf_report_generator.py            # PDF rendering
└── visualization_generator.py         # Map/chart generation
```

#### Task 3.2: Reorganize Existing Extractors
```bash
scripts/extractors/
├── __init__.py
├── planning_zone_extractor.py         # (already exists)
├── development_approvals_extractor.py # (already exists)
└── encumbrances_extractor.py          # (already exists)
```

### Phase 4: Migration (Week 4)

#### Task 4.1: Update Entry Scripts
Refactor main orchestration scripts:
- `comprehensive_property_report.py` → Use new architecture
- `run_full_analysis.py` → Use new architecture
- `generate_property_pdf.py` → Use new generators

#### Task 4.2: Deprecate Old Files
Mark old utilities as deprecated:
```python
# utils/corelogic_processor_updated.py
import warnings
warnings.warn(
    "This module is deprecated. Use scripts.api.corelogic_client instead.",
    DeprecationWarning,
    stacklevel=2
)
```

---

## Migration Strategy

### Parallel Operation

Run old and new systems in parallel during migration:

```python
# Feature flag for gradual migration
USE_NEW_ARCHITECTURE = os.getenv('USE_NEW_ARCHITECTURE', 'false').lower() == 'true'

if USE_NEW_ARCHITECTURE:
    from scripts.api.corelogic_client import CoreLogicClient
    from scripts.etl.property_etl import PropertyETL
    client = CoreLogicClient.from_env()
    etl = PropertyETL(client=client)
    data = etl.run(property_id)
else:
    # Old implementation
    from utils.corelogic_processor_updated import CoreLogicProcessor
    processor = CoreLogicProcessor(access_token)
    data = processor.generate_property_results(property_id)
```

### Deprecation Timeline

1. **Week 1-2**: New base classes + API clients available
2. **Week 3-4**: ETL layer complete, mark old processors deprecated
3. **Week 5-6**: Report generators complete, all new features use new arch
4. **Week 7-8**: Migration complete, remove old code

---

## Before/After Examples

### Example 1: Fetching Property Data

#### BEFORE (Current - Duplicated Code)
```python
# In comprehensive_property_report.py (lines 88-144)
def get_comprehensive_property_details(self, property_id: str) -> Dict[str, Any]:
    endpoints = {
        "location": f"/property-details/au/properties/{property_id}/location",
        "legal": f"/property-details/au/properties/{property_id}/legal",
        # ... 11 more endpoints
    }

    headers = {
        "Authorization": f"Bearer {self.access_token}",
        "accept": "application/json"
    }

    results = {}
    for key, endpoint in endpoints.items():
        url = self.base_url + endpoint
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                results[key] = response.json()
            else:
                results[key] = {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            results[key] = {"error": str(e)}

    return results

# PROBLEM: Same pattern duplicated in:
# - corelogic_processor_updated.py (generate_property_results)
# - property_data_processor.py (get_comprehensive_property_data)
# - Multiple other files
```

#### AFTER (New Architecture - DRY)
```python
# scripts/api/corelogic_client.py
class CoreLogicClient(BaseAPIClient):
    """Handles ALL CoreLogic API communication"""

    def get_property_details(self, property_id: str,
                           endpoints: List[str] = None) -> Dict[str, Any]:
        """Fetch property details from specified endpoints.

        Uses base class for:
        - Authentication
        - Request handling
        - Error handling
        - Retry logic
        - Rate limiting
        """
        if endpoints is None:
            endpoints = self.DEFAULT_ENDPOINTS  # Defined once

        results = {}
        for endpoint_key in endpoints:
            endpoint = self.ENDPOINTS[endpoint_key]  # Centralized mapping
            results[endpoint_key] = self.make_request(endpoint)

        return results

# Usage in comprehensive_property_report.py (reduced to 3 lines)
from scripts.api.corelogic_client import CoreLogicClient

client = CoreLogicClient.from_env()
property_details = client.get_property_details(property_id)
# BENEFITS:
# - No duplication
# - Consistent error handling
# - Centralized authentication
# - Easy to test and maintain
```

### Example 2: Comprehensive Report Generation

#### BEFORE (Current - Mixed Concerns)
```python
# comprehensive_property_report.py (lines 325-461)
def generate_comprehensive_report(self, address: str, ...) -> Dict[str, Any]:
    # PROBLEM 1: Mixes API calls with report generation
    property_id = self.property_processor.get_property_id_from_address(address)
    property_details = self.get_comprehensive_property_details(property_id)  # Raw API

    # PROBLEM 2: Mixes ETL with report generation
    parcel_data = self.geo_client.get_parcel_polygon(property_id)  # Raw API
    bbox = self.calculate_bbox(parcel_data)  # Processing
    geospatial_layers = self.get_geospatial_layers(property_id, bbox, state)  # Raw API + Processing

    # PROBLEM 3: Mixes market analysis with report generation
    market_processor = MarketDataProcessor(...)
    market_data = market_processor.fetch_comprehensive_market_data(...)  # API call
    market_metrics = market_processor.generate_market_metrics_summary(market_data)  # Processing

    # PROBLEM 4: Inline data aggregation (should be in separate generator)
    report = {
        'metadata': {...},
        'property_details': {...},
        'parcel_geometry': {...},
        'geospatial_layers': geospatial_layers,
        'market_metrics_summary': market_metrics_summary
    }

    return report

# Result: 137 lines of mixed concerns, hard to test, hard to maintain
```

#### AFTER (New Architecture - Separated Concerns)
```python
# scripts/generators/comprehensive_report_generator.py
class ComprehensiveReportGenerator(BaseReportGenerator):
    """Generates comprehensive property report by aggregating processed data."""

    def __init__(self, property_id: str, data_dir: Path):
        self.property_id = property_id
        self.data_dir = data_dir

    def gather_data(self) -> Dict[str, Any]:
        """Load all processed data files.

        No API calls - consumes ETL outputs only.
        """
        data = {}

        # Load processed data files
        files = {
            'property_details': f'{self.property_id}_property_details.json',
            'geospatial_layers': f'{self.property_id}_geospatial_layers.json',
            'comparable_sales': f'{self.property_id}_comparable_sales.json',
            'property_impacts': f'{self.property_id}_property_impacts.json',
            'mesh_block_analysis': f'{self.property_id}_mesh_block_analysis.json',
            'property_images': f'{self.property_id}_property_images.json',
        }

        for key, filename in files.items():
            filepath = self.data_dir / filename
            if filepath.exists():
                data[key] = self.load_json(filepath)
            else:
                data[key] = None
                self.reporter.warning(f"Missing data file: {filename}")

        return data

    def generate(self) -> Path:
        """Generate comprehensive report."""
        data = self.gather_data()

        # Aggregate into comprehensive report
        report = {
            'metadata': {
                'property_id': self.property_id,
                'generation_timestamp': datetime.now().isoformat(),
                'data_sources': list(data.keys())
            },
            **data  # Merge all processed data
        }

        # Validate report structure
        self.validate_report(report)

        # Save comprehensive report
        output_path = self.data_dir / f'{self.property_id}_comprehensive_report.json'
        self.save_json(report, output_path)

        return output_path

# Usage in comprehensive_property_report.py (orchestration script)
from scripts.api.corelogic_client import CoreLogicClient
from scripts.etl.property_etl import PropertyETL
from scripts.etl.geospatial_etl import GeospatialETL
from scripts.etl.comparable_sales_etl import ComparableSalesETL
from scripts.generators.comprehensive_report_generator import ComprehensiveReportGenerator

# Step 1: ETL - Generate all processed data files
client = CoreLogicClient.from_env()

property_etl = PropertyETL(client=client)
property_etl.run(property_id, output_dir)

geospatial_etl = GeospatialETL(client=client)
geospatial_etl.run(property_id, output_dir)

comparable_etl = ComparableSalesETL(client=client)
comparable_etl.run(property_id, output_dir)

# Step 2: Generate comprehensive report (aggregates processed files)
generator = ComprehensiveReportGenerator(property_id, output_dir)
report_path = generator.generate()

# BENEFITS:
# - Clear separation of concerns
# - Each ETL can be run independently
# - Generator only aggregates (no API calls)
# - Easy to test each component
# - Easy to add new data sources (just add new ETL)
# - Report generation is pure (no side effects)
```

### Example 3: PDF Generation

#### BEFORE (Current - Embedded API Calls)
```python
# generate_property_pdf.py (lines distributed throughout 3,770+ line file)

def generate_pdf(property_id: str):
    # PROBLEM: Makes API calls during PDF generation
    client = CoreLogicClient(...)
    property_data = client.get_property_details(property_id)  # API call

    # PROBLEM: Processes data during PDF generation
    comparable_processor = ComparableProcessor(...)
    comparables = comparable_processor.find_comparables(...)  # Processing

    # PROBLEM: Mixed PDF rendering with data fetching
    pdf = FPDF()
    pdf.add_page()

    # Inline data transformation mixed with PDF rendering
    if property_data.get('location'):
        location = property_data['location']
        address = f"{location.get('street')} {location.get('suburb')}"
        pdf.cell(0, 10, address)

    # ... 3,700 more lines of mixed logic
```

#### AFTER (New Architecture - Pure Generation)
```python
# scripts/generators/pdf_report_generator.py
class PDFReportGenerator(BaseReportGenerator):
    """Generates PDF from processed data only."""

    def __init__(self, report_path: Path, template: Path):
        self.report_path = report_path
        self.template = template

    def gather_data(self) -> Dict[str, Any]:
        """Load comprehensive report.

        No API calls - consumes comprehensive_report.json only.
        """
        return self.load_json(self.report_path)

    def generate(self) -> Path:
        """Generate PDF from report data."""
        data = self.gather_data()

        # Validate data completeness
        self.validate_required_fields(data)

        # Render PDF using template
        pdf = self.render_template(self.template, data)

        # Save PDF
        output_path = self.report_path.parent / f"{data['metadata']['property_id']}_report.pdf"
        self.save_pdf(pdf, output_path)

        return output_path

    def render_template(self, template: Path, data: Dict) -> FPDF:
        """Render PDF from template and data.

        Pure function - no side effects.
        """
        pdf = FPDF()
        pdf.add_page()

        # Use template engine or structured rendering
        sections = [
            PropertySection(data['property_details']),
            GeospatialSection(data['geospatial_layers']),
            ComparablesSection(data['comparable_sales']),
            ImpactsSection(data['property_impacts'])
        ]

        for section in sections:
            section.render(pdf)

        return pdf

# Usage
from scripts.generators.pdf_report_generator import PDFReportGenerator

generator = PDFReportGenerator(
    report_path=Path('data/property_reports/13683380_comprehensive_report.json'),
    template=Path('templates/property_report_template.html')
)
pdf_path = generator.generate()

# BENEFITS:
# - No API calls during PDF generation
# - Consumes pre-processed data only
# - Easy to test (just need sample JSON)
# - Fast (no network calls)
# - Can regenerate PDFs without re-fetching data
# - Template-based rendering (separation of presentation and data)
```

---

## Success Metrics

### Code Quality Metrics
- **Duplication Reduction**: Target 60-70% reduction in duplicated code
- **Lines of Code**: Reduce utility code from 9,222 to ~4,000-5,000 lines
- **Test Coverage**: Increase from 0% to 80%+ (enabled by DI and base classes)

### Maintainability Metrics
- **Time to Add New Data Source**: From 2-3 days to 4-6 hours
- **Time to Fix Bug**: From hours to minutes (isolated components)
- **Time to Onboard Developer**: From 2 weeks to 3 days (clear architecture)

### Performance Metrics
- **PDF Regeneration**: From 30s to 2s (no API calls, uses cached data)
- **Report Generation**: From 60s to 40s (parallel ETL execution)
- **API Call Reduction**: 20-30% reduction through intelligent caching

---

## Next Steps

1. **Review and Approve** this refactoring plan
2. **Create Base Classes** (Phase 1, Task 1.1) - Week 1
3. **Refactor API Clients** (Phase 1, Task 1.2) - Week 1
4. **Implement ETL Layer** (Phase 2) - Week 2
5. **Create Generators** (Phase 3) - Week 3
6. **Migrate Entry Scripts** (Phase 4) - Week 4

---

## Appendix A: File Mapping

### Files to Refactor
```
OLD → NEW

utils/corelogic_processor_updated.py → api/corelogic_client.py (API only)
                                     → etl/property_etl.py (ETL only)

utils/property_data_processor.py → api/corelogic_client.py (extract API)
                                 → etl/property_etl.py (use common ETL)

utils/geospatial_api_client.py → api/vicmap_client.py (rename + inherit base)

utils/google_api_processor.py → api/google_places_client.py (API only)
                               → etl/places_impact_etl.py (ETL only)
                               → processors/impact_processor.py (business logic)

utils/comparable_sales_generator.py → etl/comparable_sales_etl.py (ETL)
                                    → processors/comparable_processor.py (logic)

scripts/comprehensive_property_report.py → generators/comprehensive_report_generator.py
                                         + orchestration script (thin wrapper)

scripts/generate_property_pdf.py → generators/pdf_report_generator.py
                                 + rendering/sections/ (modular sections)
```

### Files to Keep (Already Good)
```
scripts/extractors/planning_zone_extractor.py     ✓ Already follows good patterns
scripts/extractors/development_approvals_extractor.py  ✓
scripts/extractors/encumbrances_extractor.py      ✓
scripts/utils/pipeline_utils.py                   ✓ Good base utilities
scripts/utils/config.py                          ✓ Good config management
scripts/utils/exceptions.py                       ✓ Good exception hierarchy
```

---

**Document Version:** 1.0
**Last Updated:** 2025-11-10
**Status:** Ready for Implementation
