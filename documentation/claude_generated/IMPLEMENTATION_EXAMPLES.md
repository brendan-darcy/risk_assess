# Implementation Examples
## Refactored Property Reporting System

This document shows concrete before/after examples demonstrating the benefits of the new architecture.

---

## Example 1: CoreLogic API Client

### BEFORE: Duplication Across Multiple Files

**File 1: `utils/corelogic_processor_updated.py` (lines 185-220)**
```python
class CoreLogicProcessor:
    def __init__(self, access_token: str, base_url: str = "https://api-uat.corelogic.asia"):
        self.access_token = access_token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "accept": "application/json"
        }

    def generate_property_results(self, property_id: str) -> Dict[str, Any]:
        endpoints = {
            "location": f"/property-details/au/properties/{property_id}/location",
            "legal": f"/property-details/au/properties/{property_id}/legal",
            # ... 10 more endpoints
        }

        results = {}
        for key, endpoint in endpoints.items():
            url = self.base_url + endpoint
            try:
                response = requests.get(url, headers=self.headers)
                if response.status_code == 200:
                    results[key] = response.json()
                else:
                    results[key] = {"error": f"HTTP {response.status_code}"}
            except Exception as e:
                results[key] = {"error": str(e)}

        return results
```

**File 2: `utils/property_data_processor.py` (lines 106-124)**
```python
# DUPLICATED: Same logic as above
def get_comprehensive_property_data(self, property_id: str) -> Dict[str, Any]:
    property_data = self.api_client.get_property_details(property_id)
    # More duplication...
```

**File 3: `comprehensive_property_report.py` (lines 88-144)**
```python
# DUPLICATED: Same logic again!
def get_comprehensive_property_details(self, property_id: str) -> Dict[str, Any]:
    endpoints = {...}  # Same 13 endpoints
    headers = {"Authorization": f"Bearer {self.access_token}"}  # Same auth
    # Same request loop...
```

**Problems:**
- Authentication logic duplicated 3+ times
- Request handling duplicated 3+ times
- Endpoint definitions duplicated 3+ times
- Error handling inconsistent
- No retry logic
- No rate limiting
- No caching

### AFTER: Single Implementation

**File: `scripts/api/corelogic_client.py`**
```python
"""
CoreLogic API Client

Pure API client - no data processing.
Handles all CoreLogic API communication with consistent patterns.
"""

import os
import requests
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from ..core import BaseAPIClient
from ..core.exceptions import APIException, AuthenticationException


class CoreLogicClient(BaseAPIClient):
    """
    CoreLogic API client.

    Handles:
    - OAuth2 authentication
    - Property details endpoints
    - Geospatial endpoints
    - Sales data endpoints
    - Market statistics endpoints
    """

    # Define endpoints once
    PROPERTY_ENDPOINTS = {
        'location': '/property-details/au/properties/{property_id}/location',
        'legal': '/property-details/au/properties/{property_id}/legal',
        'site': '/property-details/au/properties/{property_id}/site',
        'core_attributes': '/property-details/au/properties/{property_id}/attributes/core',
        'additional_attributes': '/property-details/au/properties/{property_id}/attributes/additional',
        'features': '/property-details/au/properties/{property_id}/features',
        'occupancy': '/property-details/au/properties/{property_id}/occupancy',
        'last_sale': '/property-details/au/properties/{property_id}/sales/last',
        'sales': '/property-details/au/properties/{property_id}/sales',
        'sales_otm': '/property-details/au/properties/{property_id}/otm/campaign/sales',
        'rentals_otm': '/property-details/au/properties/{property_id}/otm/campaign/rentals',
        'timeline': '/property-timeline/au/properties/{property_id}/timeline',
        'advertisements': '/property/au/v1/property/{property_id}/advertisements.json'
    }

    def __init__(self, client_id: str, client_secret: str, reporter=None, config: Dict = None):
        """
        Initialize CoreLogic API client.

        Args:
            client_id: CoreLogic client ID
            client_secret: CoreLogic client secret
            reporter: ProgressReporter for logging
            config: Additional configuration
        """
        super().__init__(reporter=reporter, config=config)
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = f"{self._get_base_url()}/access/oauth/token"

    def authenticate(self) -> str:
        """
        Authenticate with CoreLogic OAuth2.

        Returns:
            Access token

        Raises:
            AuthenticationException: On authentication failure
        """
        try:
            response = requests.post(
                self.token_url,
                data={
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'grant_type': 'client_credentials'
                },
                timeout=30
            )

            if response.status_code != 200:
                raise AuthenticationException(
                    f"Authentication failed: {response.status_code}",
                    api_name="CoreLogic"
                )

            token_data = response.json()
            access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 3600)

            # Set token expiry
            self._token_expiry = datetime.now() + timedelta(seconds=expires_in - 60)

            return access_token

        except requests.RequestException as e:
            raise AuthenticationException(
                f"Authentication request failed: {str(e)}",
                api_name="CoreLogic"
            )

    def _get_base_url(self) -> str:
        """Get CoreLogic API base URL."""
        return "https://api-uat.corelogic.asia"

    def get_property_details(
        self,
        property_id: str,
        endpoints: List[str] = None
    ) -> Dict[str, Any]:
        """
        Get property details from specified endpoints.

        Args:
            property_id: CoreLogic property ID
            endpoints: List of endpoint keys to fetch (default: all)

        Returns:
            Dictionary mapping endpoint keys to responses

        Example:
            >>> client = CoreLogicClient.from_env()
            >>> data = client.get_property_details('12345', ['location', 'legal'])
            >>> print(data['location']['address'])
        """
        if endpoints is None:
            endpoints = list(self.PROPERTY_ENDPOINTS.keys())

        results = {}

        for endpoint_key in endpoints:
            if endpoint_key not in self.PROPERTY_ENDPOINTS:
                if self.reporter:
                    self.reporter.warning(f"Unknown endpoint: {endpoint_key}")
                continue

            endpoint = self.PROPERTY_ENDPOINTS[endpoint_key].format(property_id=property_id)

            try:
                response = self.make_request(endpoint)
                results[endpoint_key] = response
            except APIException as e:
                if self.reporter:
                    self.reporter.warning(f"Failed to fetch {endpoint_key}: {e.message}")
                results[endpoint_key] = {'error': e.message}

        return results

    def get_property_suggestions(
        self,
        query: str,
        limit: int = 3,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search for properties by address.

        Args:
            query: Address search query
            limit: Maximum results
            offset: Pagination offset

        Returns:
            List of property suggestions
        """
        response = self.make_request(
            '/property/au/v2/suggest.json',
            params={
                'q': query,
                'suggestionTypes': 'address',
                'limit': limit,
                'offset': offset
            }
        )

        return response.get('suggestions', []) if response else []

    def get_sales_history(self, property_id: str) -> List[Dict[str, Any]]:
        """
        Get sales history for property.

        Args:
            property_id: CoreLogic property ID

        Returns:
            List of sale transactions
        """
        response = self.make_request(
            f'/property-details/au/properties/{property_id}/sales'
        )

        if isinstance(response, list):
            return response
        elif isinstance(response, dict):
            return [response]
        else:
            return []

    @classmethod
    def from_env(cls, reporter=None, config: Dict = None):
        """
        Create CoreLogic client from environment variables.

        Environment variables:
        - CORELOGIC_CLIENT_ID: Client ID
        - CORELOGIC_CLIENT_SECRET: Client secret

        Args:
            reporter: ProgressReporter for logging
            config: Additional configuration

        Returns:
            CoreLogicClient instance

        Raises:
            ConfigurationException: If credentials not found
        """
        from ..core.exceptions import ConfigurationException

        client_id = os.getenv('CORELOGIC_CLIENT_ID')
        client_secret = os.getenv('CORELOGIC_CLIENT_SECRET')

        if not client_id or not client_secret:
            raise ConfigurationException(
                "CoreLogic credentials not found in environment",
                required_keys=['CORELOGIC_CLIENT_ID', 'CORELOGIC_CLIENT_SECRET']
            )

        return cls(client_id, client_secret, reporter=reporter, config=config)


# Example usage
if __name__ == "__main__":
    from ..utils.pipeline_utils import ProgressReporter

    reporter = ProgressReporter("CoreLogic Test")
    client = CoreLogicClient.from_env(reporter=reporter)

    # Get property details
    data = client.get_property_details('13683380', ['location', 'legal'])
    print(f"Property at: {data['location']['address']['singleLine']}")

    # Get statistics
    stats = client.get_statistics()
    print(f"API calls: {stats['request_count']}, Cache hits: {stats['cache_hits']}")
```

**Benefits:**
- ✅ Authentication logic: Written ONCE
- ✅ Request handling: Written ONCE
- ✅ Error handling: Consistent everywhere
- ✅ Retry logic: Automatic
- ✅ Rate limiting: Automatic
- ✅ Caching: Available
- ✅ Testing: Easy (mock BaseAPIClient methods)
- ✅ Maintenance: Change once, affects all usage

---

## Example 2: Property ETL Pipeline

### BEFORE: Mixed Concerns

**File: `comprehensive_property_report.py` (lines 325-461)**
```python
def generate_comprehensive_report(self, address: str, ...) -> Dict[str, Any]:
    # PROBLEM: Mixes API calls, ETL, and report generation

    # API call (should be in API client)
    property_id = self.property_processor.get_property_id_from_address(address)

    # Raw API call (should be in API client)
    property_details = self.get_comprehensive_property_details(property_id)

    # Another raw API call (should be in API client)
    parcel_data = self.geo_client.get_parcel_polygon(property_id)

    # Processing (should be in ETL)
    bbox = self.calculate_bbox(parcel_data)

    # More API calls (should be in API client)
    geospatial_layers = self.get_geospatial_layers(property_id, bbox, state)

    # Market processing (should be in separate ETL)
    market_processor = MarketDataProcessor(...)
    market_data = market_processor.fetch_comprehensive_market_data(...)

    # Report aggregation (this is the only thing that should be here!)
    report = {
        'metadata': {...},
        'property_details': property_details,
        'parcel_geometry': parcel_data,
        'geospatial_layers': geospatial_layers
    }

    return report
```

**Problems:**
- API calls mixed with report generation
- ETL mixed with report generation
- Hard to test (needs live API)
- Can't regenerate report without re-fetching data
- No separation of concerns

### AFTER: Clean Separation

**File 1: `scripts/etl/property_etl.py`**
```python
"""
Property ETL Pipeline

Extracts property data from CoreLogic API, transforms it,
and saves to processed JSON file.
"""

from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from ..core import BaseETLProcessor
from ..api.corelogic_client import CoreLogicClient


class PropertyETL(BaseETLProcessor):
    """
    ETL processor for CoreLogic property data.

    Extract: Get raw data from CoreLogic API
    Transform: Flatten, validate, enrich
    Load: Save to property_details.json
    """

    def __init__(self, api_client: CoreLogicClient, reporter=None, config: Dict = None):
        super().__init__(api_client=api_client, reporter=reporter, config=config)

    def extract(self, property_id: str, address: str = None) -> Dict[str, Any]:
        """
        Extract raw property data from CoreLogic API.

        Args:
            property_id: CoreLogic property ID
            address: Property address (for metadata)

        Returns:
            Raw property data from API
        """
        if self.reporter:
            self.reporter.info(f"Fetching property data for ID: {property_id}")

        # Get all property endpoints
        property_details = self.api_client.get_property_details(property_id)

        # Get sales history
        sales_history = self.api_client.get_sales_history(property_id)

        return {
            'property_id': property_id,
            'address': address,
            'details': property_details,
            'sales_history': sales_history,
            'extraction_timestamp': datetime.now().isoformat()
        }

    def transform(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform raw property data.

        Args:
            raw_data: Raw data from extract()

        Returns:
            Transformed property data
        """
        if self.reporter:
            self.reporter.info("Transforming property data...")

        # Extract core fields
        property_id = raw_data['property_id']
        address = raw_data.get('address')
        details = raw_data['details']
        sales_history = raw_data['sales_history']

        # Build transformed structure
        transformed = {
            'metadata': {
                'property_id': property_id,
                'address': address,
                'extraction_timestamp': raw_data['extraction_timestamp'],
                'processing_timestamp': datetime.now().isoformat()
            },
            'location': details.get('location'),
            'legal': details.get('legal'),
            'site': details.get('site'),
            'core_attributes': details.get('core_attributes'),
            'additional_attributes': details.get('additional_attributes'),
            'features': details.get('features'),
            'occupancy': details.get('occupancy'),
            'last_sale': details.get('last_sale'),
            'sales_history': sales_history,
            'sales_otm': details.get('sales_otm'),
            'rentals_otm': details.get('rentals_otm'),
            'timeline': details.get('timeline'),
            'advertisements': details.get('advertisements')
        }

        # Add derived fields
        if sales_history:
            transformed['sales_count'] = len(sales_history)
            if sales_history[0].get('price'):
                transformed['latest_sale_price'] = sales_history[0]['price']

        # Add validation metadata
        transformed['validation'] = {
            'has_location': bool(transformed.get('location')),
            'has_legal': bool(transformed.get('legal')),
            'has_sales': bool(sales_history),
            'completeness_score': self._calculate_completeness(transformed)
        }

        return transformed

    def load(self, transformed_data: Dict[str, Any], output_path: Path) -> Path:
        """
        Save transformed property data.

        Args:
            transformed_data: Transformed data from transform()
            output_path: Path to save JSON file

        Returns:
            Path to saved file
        """
        return self.save_json(transformed_data, output_path)

    def _calculate_completeness(self, data: Dict) -> float:
        """Calculate data completeness score (0-1)."""
        required_fields = [
            'location', 'legal', 'site', 'core_attributes',
            'features', 'sales_history'
        ]
        present = sum(1 for field in required_fields if data.get(field))
        return present / len(required_fields)


# Example usage
if __name__ == "__main__":
    from ..api.corelogic_client import CoreLogicClient
    from ..utils.pipeline_utils import ProgressReporter

    reporter = ProgressReporter("Property ETL")
    client = CoreLogicClient.from_env(reporter=reporter)
    etl = PropertyETL(api_client=client, reporter=reporter)

    result = etl.run(
        output_path=Path('data/property_reports/13683380_property_details.json'),
        property_id='13683380',
        address='5 Settlers Court, Vermont South VIC 3133'
    )

    print(f"✅ Property data saved to: {result['output_path']}")
```

**File 2: `scripts/generators/comprehensive_report_generator.py`**
```python
"""
Comprehensive Report Generator

Aggregates all processed data files into comprehensive JSON report.
NO API calls - consumes ETL outputs only.
"""

from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from ..core import BaseReportGenerator


class ComprehensiveReportGenerator(BaseReportGenerator):
    """
    Generate comprehensive property report by aggregating processed data.

    Inputs (from ETL outputs):
    - property_details.json
    - geospatial_layers.json
    - comparable_sales.json
    - property_impacts.json
    - mesh_block_analysis.json
    - property_images.json
    - development_approvals.json

    Output:
    - comprehensive_report.json
    """

    def gather_data(self) -> Dict[str, Any]:
        """
        Load all processed data files.

        Returns:
            Dictionary with all available data
        """
        if self.reporter:
            self.reporter.info("Loading processed data files...")

        # Load all available data files
        data = {
            'property_details': self.load_processed_file(
                f'{self.property_id}_property_details.json',
                required=True
            ),
            'geospatial_layers': self.load_processed_file(
                f'{self.property_id}_geospatial_layers.json'
            ),
            'comparable_sales': self.load_processed_file(
                f'{self.property_id}_comparable_sales.json'
            ),
            'property_impacts': self.load_processed_file(
                f'{self.property_id}_property_impacts.json'
            ),
            'mesh_block_analysis': self.load_processed_file(
                f'{self.property_id}_mesh_block_analysis.json'
            ),
            'property_images': self.load_processed_file(
                f'{self.property_id}_property_images.json'
            ),
            'development_approvals': self.load_processed_file(
                f'{self.property_id}_development_approvals.json'
            )
        }

        # Log data availability
        available = [k for k, v in data.items() if v is not None]
        if self.reporter:
            self.reporter.info(f"Loaded {len(available)}/{len(data)} data sources")

        return data

    def generate(self) -> Path:
        """
        Generate comprehensive report.

        Returns:
            Path to comprehensive report JSON
        """
        data = self.gather_data()

        # Build comprehensive report
        report = {
            'metadata': {
                'property_id': self.property_id,
                'report_type': 'comprehensive',
                'generation_timestamp': datetime.now().isoformat(),
                'data_sources': [k for k, v in data.items() if v is not None],
                'missing_data': self._missing_data
            }
        }

        # Merge all data
        report.update(data)

        # Add summary statistics
        report['summary'] = self._generate_summary(data)

        # Validate report
        self.validate_required_fields(report, ['metadata', 'property_details'])

        # Save report
        output_path = self.data_dir / f'{self.property_id}_comprehensive_report.json'
        return self.save_json(report, output_path)

    def _generate_summary(self, data: Dict) -> Dict:
        """Generate summary statistics."""
        return {
            'data_completeness': {
                k: 'present' if v else 'missing'
                for k, v in data.items()
            },
            'total_data_sources': len([v for v in data.values() if v])
        }


# Example usage
if __name__ == "__main__":
    from ..utils.pipeline_utils import ProgressReporter

    reporter = ProgressReporter("Comprehensive Report Generator")
    generator = ComprehensiveReportGenerator(
        property_id='13683380',
        data_dir=Path('data/property_reports'),
        reporter=reporter
    )

    report_path = generator.run()
    print(f"✅ Comprehensive report: {report_path}")
```

**Benefits:**
- ✅ Clean separation: API → ETL → Report
- ✅ Can test ETL without API (mock client)
- ✅ Can test report generator without API (use fixture files)
- ✅ Can regenerate reports instantly (no API calls)
- ✅ Can run ETL independently
- ✅ Clear data flow
- ✅ Easy to add new data sources (just add new ETL)

---

## Example 3: Complete Orchestration

### NEW: Clean Entry Script

**File: `scripts/run_comprehensive_analysis.py`**
```python
#!/usr/bin/env python3
"""
Run Comprehensive Property Analysis

Orchestrates complete property analysis using new architecture:
1. Run all ETL pipelines (generate processed data files)
2. Generate comprehensive report (aggregate processed files)
3. Generate PDF report (from comprehensive report)

Usage:
    python scripts/run_comprehensive_analysis.py --address "5 Settlers Court, Vermont South VIC 3133"
    python scripts/run_comprehensive_analysis.py --property-id 13683380
"""

import argparse
import sys
from pathlib import Path

# Import new architecture components
from scripts.api.corelogic_client import CoreLogicClient
from scripts.api.google_places_client import GooglePlacesClient
from scripts.api.vicmap_client import VicmapClient

from scripts.etl.property_etl import PropertyETL
from scripts.etl.geospatial_etl import GeospatialETL
from scripts.etl.comparable_sales_etl import ComparableSalesETL
from scripts.etl.places_impact_etl import PlacesImpactETL

from scripts.generators.comprehensive_report_generator import ComprehensiveReportGenerator
from scripts.generators.pdf_report_generator import PDFReportGenerator

from scripts.utils.pipeline_utils import ProgressReporter


def main():
    parser = argparse.ArgumentParser(description='Run comprehensive property analysis')
    parser.add_argument('--address', help='Property address')
    parser.add_argument('--property-id', help='Property ID')
    parser.add_argument('--output-dir', default='data/property_reports',
                       help='Output directory')
    parser.add_argument('--skip-pdf', action='store_true',
                       help='Skip PDF generation')

    args = parser.parse_args()

    if not args.address and not args.property_id:
        parser.error("Must provide either --address or --property-id")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    reporter = ProgressReporter("Comprehensive Property Analysis")
    reporter.print_header()

    try:
        # Step 1: Initialize API clients
        reporter.print_step(1, "Initialize API Clients")
        corelogic_client = CoreLogicClient.from_env(reporter=reporter)
        google_client = GooglePlacesClient.from_env(reporter=reporter)
        vicmap_client = VicmapClient.from_env(reporter=reporter)
        reporter.success("All API clients initialized")

        # Step 2: Resolve property ID
        reporter.print_step(2, "Resolve Property ID")
        if args.property_id:
            property_id = args.property_id
            address = args.address or "Unknown"
        else:
            suggestions = corelogic_client.get_property_suggestions(args.address, limit=1)
            if not suggestions:
                raise ValueError(f"No property found for address: {args.address}")
            property_id = suggestions[0]['propertyId']
            address = args.address

        reporter.success(f"Property ID: {property_id}")

        # Step 3: Run ETL pipelines (parallel possible)
        reporter.print_step(3, "Run ETL Pipelines")

        # Property data ETL
        reporter.info("Running Property ETL...")
        property_etl = PropertyETL(api_client=corelogic_client, reporter=reporter)
        property_result = property_etl.run(
            output_path=output_dir / f'{property_id}_property_details.json',
            property_id=property_id,
            address=address
        )
        reporter.success(f"Property ETL complete: {property_result['output_path']}")

        # Geospatial ETL
        reporter.info("Running Geospatial ETL...")
        geospatial_etl = GeospatialETL(api_client=vicmap_client, reporter=reporter)
        geospatial_result = geospatial_etl.run(
            output_path=output_dir / f'{property_id}_geospatial_layers.json',
            property_id=property_id
        )
        reporter.success(f"Geospatial ETL complete: {geospatial_result['output_path']}")

        # Comparable sales ETL
        reporter.info("Running Comparable Sales ETL...")
        comparable_etl = ComparableSalesETL(api_client=corelogic_client, reporter=reporter)
        comparable_result = comparable_etl.run(
            output_path=output_dir / f'{property_id}_comparable_sales.json',
            property_id=property_id
        )
        reporter.success(f"Comparable Sales ETL complete: {comparable_result['output_path']}")

        # Google Places impact ETL
        reporter.info("Running Places Impact ETL...")
        places_etl = PlacesImpactETL(api_client=google_client, reporter=reporter)
        places_result = places_etl.run(
            output_path=output_dir / f'{property_id}_property_impacts.json',
            address=address
        )
        reporter.success(f"Places Impact ETL complete: {places_result['output_path']}")

        # Step 4: Generate comprehensive report
        reporter.print_step(4, "Generate Comprehensive Report")
        report_generator = ComprehensiveReportGenerator(
            property_id=property_id,
            data_dir=output_dir,
            reporter=reporter
        )
        report_path = report_generator.run()
        reporter.success(f"Comprehensive report: {report_path}")

        # Step 5: Generate PDF report
        if not args.skip_pdf:
            reporter.print_step(5, "Generate PDF Report")
            pdf_generator = PDFReportGenerator(
                report_path=report_path,
                template=Path('templates/property_report_template.html'),
                reporter=reporter
            )
            pdf_path = pdf_generator.run()
            reporter.success(f"PDF report: {pdf_path}")

        # Final summary
        reporter.print_summary()
        print("\n✅ Analysis complete!")
        print(f"\nOutput files in: {output_dir}")

        return 0

    except Exception as e:
        reporter.error(f"Analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

**Benefits:**
- ✅ Clear orchestration flow
- ✅ Each step is independent
- ✅ Easy to run individual steps
- ✅ Easy to add new ETL pipelines
- ✅ Proper error handling
- ✅ Progress reporting
- ✅ Can skip steps (e.g., --skip-pdf)

---

## Summary: Key Improvements

### 1. Code Reduction
- **Before:** 9,222 lines in utils/
- **After:** ~4,000-5,000 lines (60% reduction through abstraction)

### 2. Duplication Elimination
- Authentication: 4 implementations → 1 base implementation
- Request handling: 4 implementations → 1 base implementation
- JSON I/O: 10+ implementations → 2 base implementations
- Error handling: Inconsistent → Structured exception hierarchy

### 3. Data Flow Clarity
```
BEFORE: API calls mixed everywhere
AFTER: API Client → ETL → Processed JSON → Report Generator
```

### 4. Testability
```python
# Before: Hard to test (needs live API)
def test_report():
    report = generate_report(address="...")  # Makes API calls!

# After: Easy to test (use fixtures)
def test_etl_transform():
    etl = PropertyETL(api_client=None)  # No API needed!
    raw = load_fixture('raw_data.json')
    result = etl.transform(raw)
    assert result['property_id'] == '12345'
```

### 5. Maintainability
- Add authentication feature: Change 1 file (BaseAPIClient)
- Add new data source: Create 1 ETL class
- Change report format: Modify 1 generator
- Fix bug: Change once, affects all usage

---

**Version:** 1.0
**Date:** 2025-11-10
**Status:** Implementation Ready
