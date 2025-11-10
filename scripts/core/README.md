# Core Base Classes

This module provides the foundation for the entire property reporting system through abstract base classes that enforce DRY principles and proper data flow.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     BaseReportGenerator                      │
│  (Aggregates processed data → generates reports)            │
└────────────────────────┬────────────────────────────────────┘
                         │ Consumes
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                      BaseETLProcessor                        │
│  (Extract → Transform → Load processed data)                │
└────────────────────────┬────────────────────────────────────┘
                         │ Uses
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                      BaseAPIClient                           │
│  (Authenticates → Makes requests → Handles errors)          │
└─────────────────────────────────────────────────────────────┘
```

## Base Classes

### 1. BaseAPIClient

Base class for all API clients (CoreLogic, Google Places, Vicmap).

**Provides:**
- Authentication management with token refresh
- Request handling with automatic retry logic
- Rate limiting between requests
- Response caching
- Consistent error handling

**Subclasses must implement:**
- `authenticate()` - Authentication logic
- `_get_base_url()` - Base URL for API
- `from_env()` - Factory method from environment variables

**Example:**

```python
from scripts.core import BaseAPIClient

class CoreLogicClient(BaseAPIClient):
    def authenticate(self) -> str:
        # OAuth2 token logic
        response = requests.post(self.token_url, ...)
        return response.json()['access_token']

    def _get_base_url(self) -> str:
        return "https://api-uat.corelogic.asia"

    @classmethod
    def from_env(cls, reporter=None):
        client_id = os.getenv('CORELOGIC_CLIENT_ID')
        client_secret = os.getenv('CORELOGIC_CLIENT_SECRET')
        return cls(client_id, client_secret, reporter=reporter)

# Usage
client = CoreLogicClient.from_env()
property_data = client.make_request('/property-details/au/properties/12345/location')
```

### 2. BaseETLProcessor

Base class for all ETL (Extract, Transform, Load) pipelines.

**Provides:**
- Structured ETL pipeline execution
- Data validation at each stage
- Error handling and recovery
- Progress reporting
- Metadata generation

**Subclasses must implement:**
- `extract(**kwargs)` - Get raw data from API
- `transform(raw_data)` - Process and validate data
- `load(transformed_data, output_path)` - Save processed data

**Example:**

```python
from scripts.core import BaseETLProcessor

class PropertyETL(BaseETLProcessor):
    def extract(self, property_id: str) -> Dict:
        # Get raw data from API client
        return self.api_client.get_property_details(property_id)

    def transform(self, raw_data: Dict) -> Dict:
        # Flatten, validate, enrich
        transformed = self.flatten_dict(raw_data)
        transformed['processing_timestamp'] = datetime.now().isoformat()
        return transformed

    def load(self, transformed_data: Dict, output_path: Path) -> Path:
        # Save as JSON
        return self.save_json(transformed_data, output_path)

# Usage
etl = PropertyETL(api_client=client, reporter=reporter)
result = etl.run(
    output_path=Path('data/property_reports/12345_property_details.json'),
    property_id='12345'
)
```

### 3. BaseReportGenerator

Base class for all report generators (PDF, JSON, comprehensive reports).

**Provides:**
- Data aggregation from multiple processed sources
- Report validation
- File I/O utilities
- Progress reporting

**Subclasses must implement:**
- `gather_data()` - Load processed data files (no API calls!)
- `generate()` - Create the report

**Example:**

```python
from scripts.core import BaseReportGenerator

class ComprehensiveReportGenerator(BaseReportGenerator):
    def gather_data(self) -> Dict:
        # Load all processed data files
        return {
            'property_details': self.load_processed_file(
                f'{self.property_id}_property_details.json',
                required=True
            ),
            'geospatial_layers': self.load_processed_file(
                f'{self.property_id}_geospatial_layers.json'
            ),
            'comparable_sales': self.load_processed_file(
                f'{self.property_id}_comparable_sales.json'
            )
        }

    def generate(self) -> Path:
        data = self.gather_data()

        # Aggregate into comprehensive report
        report = {
            'metadata': {
                'property_id': self.property_id,
                'timestamp': datetime.now().isoformat()
            },
            **data
        }

        # Save and return path
        output_path = self.data_dir / f'{self.property_id}_comprehensive_report.json'
        return self.save_json(report, output_path)

# Usage
generator = ComprehensiveReportGenerator(
    property_id='12345',
    data_dir=Path('data/property_reports'),
    reporter=reporter
)
report_path = generator.run()
```

### 4. BaseDataProcessor

Base class for business logic processors.

**Provides:**
- Input/output validation
- Error handling
- Configuration management

**Subclasses must implement:**
- `process(data, **kwargs)` - Apply business logic

**Example:**

```python
from scripts.core import BaseDataProcessor

class ComparableProcessor(BaseDataProcessor):
    def process(self, property_data: Dict, **kwargs) -> Dict:
        # Rank comparables by similarity
        search_radius = kwargs.get('search_radius', 2000)
        comparables = self.find_comparables(property_data, search_radius)
        ranked = self.rank_by_similarity(comparables, property_data)
        return {
            'comparables': ranked,
            'search_radius': search_radius,
            'match_count': len(ranked)
        }

# Usage
processor = ComparableProcessor(reporter=reporter)
result = processor.process(property_data, search_radius=2000)
```

## Exception Hierarchy

```
CoreException (base for all exceptions)
├── APIException
│   ├── AuthenticationException
│   └── RateLimitException
├── ETLException
├── ReportGenerationException
├── ProcessingException
├── ValidationException
├── DataNotFoundException
└── ConfigurationException
```

**Usage:**

```python
from scripts.core import APIException, ETLException

try:
    data = api_client.make_request('/endpoint')
except APIException as e:
    # Structured error information
    print(f"API Error: {e.message}")
    print(f"Status Code: {e.status_code}")
    print(f"Endpoint: {e.endpoint}")
    # Convert to dict for logging
    log_data = e.to_dict()
```

## Benefits of This Architecture

### 1. Zero Code Duplication

**Before:**
- Authentication logic duplicated in 4 files
- Request handling duplicated in 4 files
- JSON I/O duplicated in 10+ files
- Progress reporting duplicated everywhere

**After:**
- Authentication: Once in BaseAPIClient
- Request handling: Once in BaseAPIClient
- JSON I/O: Once in BaseETLProcessor/BaseReportGenerator
- Progress reporting: Injected ProgressReporter

### 2. Clear Data Flow

```
API Client → ETL → Processed JSON → Report Generator → Final Report
   ↓           ↓         ↓                ↓                ↓
 Raw Data   Transform  Save File      Load Files      PDF/JSON
```

Each layer has one responsibility.

### 3. Easy to Test

```python
# Test ETL without API calls
def test_property_etl_transform():
    etl = PropertyETL(api_client=None)  # No API needed
    raw_data = load_fixture('raw_property_data.json')
    transformed = etl.transform(raw_data)
    assert 'property_id' in transformed
```

### 4. Easy to Extend

```python
# Add new data source: Just create new ETL
class PlanningZoneETL(BaseETLProcessor):
    def extract(self, property_id: str) -> Dict:
        return self.api_client.get_planning_zones(property_id)

    def transform(self, raw_data: Dict) -> Dict:
        return self.categorize_zones(raw_data)

    def load(self, transformed_data: Dict, output_path: Path) -> Path:
        return self.save_json(transformed_data, output_path)
```

### 5. Consistent Error Handling

All exceptions have:
- Structured error information
- Original exception context
- Easy serialization for logging

## Quick Start

### Step 1: Create API Client

```python
from scripts.core import BaseAPIClient

class MyAPIClient(BaseAPIClient):
    def authenticate(self) -> str:
        # Your auth logic
        pass

    def _get_base_url(self) -> str:
        return "https://api.example.com"

    @classmethod
    def from_env(cls, reporter=None):
        api_key = os.getenv('MY_API_KEY')
        return cls(api_key=api_key, reporter=reporter)
```

### Step 2: Create ETL

```python
from scripts.core import BaseETLProcessor

class MyDataETL(BaseETLProcessor):
    def extract(self, resource_id: str) -> Dict:
        return self.api_client.make_request(f'/resource/{resource_id}')

    def transform(self, raw_data: Dict) -> Dict:
        return self.flatten_dict(raw_data)

    def load(self, transformed_data: Dict, output_path: Path) -> Path:
        return self.save_json(transformed_data, output_path)
```

### Step 3: Create Report Generator

```python
from scripts.core import BaseReportGenerator

class MyReportGenerator(BaseReportGenerator):
    def gather_data(self) -> Dict:
        return {
            'data': self.load_processed_file(f'{self.property_id}_data.json')
        }

    def generate(self) -> Path:
        data = self.gather_data()
        output_path = self.data_dir / f'{self.property_id}_report.json'
        return self.save_json(data, output_path)
```

### Step 4: Orchestrate

```python
# Initialize
client = MyAPIClient.from_env(reporter=reporter)
etl = MyDataETL(api_client=client, reporter=reporter)
generator = MyReportGenerator(
    property_id='12345',
    data_dir=Path('data/reports'),
    reporter=reporter
)

# Run pipeline
etl_result = etl.run(
    output_path=Path('data/reports/12345_data.json'),
    resource_id='12345'
)

report_path = generator.run()
```

## Migration Guide

See `REFACTORING_PLAN_DRY_ARCHITECTURE.md` for detailed migration strategy.

---

**Version:** 1.0
**Date:** 2025-11-10
**Author:** Property Reporting System Refactoring
