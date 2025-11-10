#!/usr/bin/env python3
"""
Generate Ultra-Comprehensive Property Report JSON

Consolidates all data sources into a single JSON file:
- CoreLogic property data (13 endpoints)
- Geospatial layers (hazards, legal, infrastructure)
- Parcel geometry
- Market metrics
- Google Places impact analysis

This script combines the functionality of:
- comprehensive_property_report.py
- run_places_analysis.py
- add_places_to_report.py

Usage:
    python3 scripts/generate_ultra_comprehensive_json.py --address "5 Settlers Court, Vermont South VIC 3133"

    # With map exports
    python3 scripts/generate_ultra_comprehensive_json.py --address "16 Fowler Crescent, South Coogee, NSW, 2034" --include-maps

    # Custom output directory
    python3 scripts/generate_ultra_comprehensive_json.py --address "123 Main St" --output-dir reports/

Requirements:
    - CORELOGIC_CLIENT_ID and CORELOGIC_CLIENT_SECRET environment variables
    - GOOGLE_API_KEY environment variable

Outputs:
    - {property_id}_ultra_comprehensive_report.json (all data combined)

Author: Ultra-Comprehensive Property Analysis System
Date: 2025-11-09
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Import from utils subdirectory
from utils.property_data_processor import PropertyDataProcessor
from utils.market_data_processor import MarketDataProcessor
from utils.geospatial_api_client import GeospatialAPIClient
from utils.google_api_processor import GooglePlacesPipeline
from utils.pipeline_utils import ProgressReporter, PipelineConfig, PipelineError
import requests


class UltraComprehensivePropertyReporter:
    """Extract and consolidate all available property data from all APIs"""

    def __init__(self, geo_client: GeospatialAPIClient, property_processor: PropertyDataProcessor):
        self.geo_client = geo_client
        self.property_processor = property_processor
        self.reporter = ProgressReporter("Ultra-Comprehensive Property Report")
        self.base_url = geo_client.base_url
        self.access_token = geo_client.get_access_token()

    def detect_state_from_address(self, address: str) -> str:
        """Detect Australian state from address string"""
        address_upper = address.upper()
        state_patterns = {
            'NSW': ['NSW', 'NEW SOUTH WALES'],
            'VIC': ['VIC', 'VICTORIA'],
            'QLD': ['QLD', 'QUEENSLAND'],
            'SA': ['SA', 'SOUTH AUSTRALIA'],
            'WA': ['WA', 'WESTERN AUSTRALIA'],
            'TAS': ['TAS', 'TASMANIA'],
            'ACT': ['ACT', 'AUSTRALIAN CAPITAL TERRITORY'],
            'NT': ['NT', 'NORTHERN TERRITORY']
        }

        for state_code, patterns in state_patterns.items():
            for pattern in patterns:
                if pattern in address_upper:
                    return state_code.lower()

        self.reporter.warning("Could not detect state from address, defaulting to NSW")
        return 'nsw'

    def get_comprehensive_property_details(self, property_id: str) -> Dict[str, Any]:
        """
        Get all property details from 13 CoreLogic API endpoints.
        """
        self.reporter.info("📋 Fetching comprehensive property details from 13 API endpoints...")

        endpoints = {
            "location": f"/property-details/au/properties/{property_id}/location",
            "legal": f"/property-details/au/properties/{property_id}/legal",
            "site": f"/property-details/au/properties/{property_id}/site",
            "core_attributes": f"/property-details/au/properties/{property_id}/attributes/core",
            "additional_attributes": f"/property-details/au/properties/{property_id}/attributes/additional",
            "features": f"/property-details/au/properties/{property_id}/features",
            "occupancy": f"/property-details/au/properties/{property_id}/occupancy",
            "last_sale": f"/property-details/au/properties/{property_id}/sales/last",
            "sales": f"/property-details/au/properties/{property_id}/sales",
            "sales_otm": f"/property-details/au/properties/{property_id}/otm/campaign/sales",
            "rentals_otm": f"/property-details/au/properties/{property_id}/otm/campaign/rentals",
            "timeline": f"/property-timeline/au/properties/{property_id}/timeline",
            "advertisements": f"/property/au/v1/property/{property_id}/advertisements.json",
        }

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "accept": "application/json"
        }

        results = {}
        successful = 0
        failed = 0

        for key, endpoint in endpoints.items():
            url = self.base_url + endpoint
            try:
                response = requests.get(url, headers=headers, timeout=30)
                if response.status_code == 200:
                    results[key] = response.json()
                    successful += 1
                    self.reporter.info(f"  ✓ {key}")
                else:
                    results[key] = {
                        "error": f"HTTP {response.status_code}",
                        "message": response.text[:200]
                    }
                    failed += 1
                    self.reporter.warning(f"  ✗ {key}: HTTP {response.status_code}")
            except Exception as e:
                results[key] = {
                    "error": "Request failed",
                    "message": str(e)
                }
                failed += 1
                self.reporter.error(f"  ✗ {key}: {str(e)}")

        self.reporter.success(f"Property details: {successful} successful, {failed} failed")
        return results

    def calculate_bbox(self, parcel_data: Dict[str, Any], buffer_meters: int = 5000) -> Optional[str]:
        """Calculate bounding box from parcel geometry with buffer"""
        try:
            features = parcel_data.get('features', [])
            if not features:
                return None

            geometry = features[0].get('geometry', {})
            if geometry.get('rings'):
                all_coords = []
                for ring in geometry['rings']:
                    all_coords.extend(ring)

                if all_coords:
                    xs = [coord[0] for coord in all_coords]
                    ys = [coord[1] for coord in all_coords]

                    xmin = min(xs) - buffer_meters
                    ymin = min(ys) - buffer_meters
                    xmax = max(xs) + buffer_meters
                    ymax = max(ys) + buffer_meters

                    return f"{xmin},{ymin},{xmax},{ymax}"
        except Exception as e:
            self.reporter.error(f"Error calculating bbox: {e}")

        return None

    def get_geospatial_layers(self, property_id: str, bbox: str, state: str) -> Dict[str, Any]:
        """Get all geospatial layer data with feature details"""
        self.reporter.info("🗺️  Fetching geospatial layers...")

        layers = {
            'hazards': {},
            'legal': {},
            'infrastructure': {}
        }

        # Hazard overlays
        self.reporter.info("  Checking hazard overlays...")
        hazard_types = ['bushfire', 'flood', 'heritage']
        for hazard_type in hazard_types:
            try:
                response = self.geo_client.query(
                    layer=f"overlays/{hazard_type}",
                    geometry=bbox,
                    geometry_type="esriGeometryEnvelope",
                    where="1=1",
                    return_geometry=True,
                    format="json"
                )

                if response.status_code == 200:
                    data = response.json()
                    features = data.get('features', [])
                    layers['hazards'][hazard_type] = {
                        'available': len(features) > 0,
                        'feature_count': len(features),
                        'features': features[:10] if features else []  # First 10
                    }
                    if features:
                        self.reporter.info(f"    ✓ {hazard_type}: {len(features)} features")
                else:
                    # Fallback to image check
                    img_response = self.geo_client.get_hazard_data(bbox, hazard_type)
                    layers['hazards'][hazard_type] = {
                        'available': img_response.status_code == 200 and len(img_response.content) > 1000,
                        'method': 'image_check'
                    }
            except Exception as e:
                layers['hazards'][hazard_type] = {'available': False, 'error': str(e)}
                self.reporter.warning(f"    ✗ {hazard_type}: {str(e)}")

        # Easements
        self.reporter.info("  Checking easements...")
        try:
            response = self.geo_client.get_easement_data(bbox, state)
            if response.status_code == 200:
                data = response.json()
                features = data.get('features', [])
                layers['legal']['easements'] = {
                    'available': len(features) > 0,
                    'count': len(features),
                    'features': features  # All easements
                }
                if features:
                    self.reporter.info(f"    ✓ easements: {len(features)} found")
            else:
                layers['legal']['easements'] = {'available': False, 'error': f'HTTP {response.status_code}'}
        except Exception as e:
            layers['legal']['easements'] = {'available': False, 'error': str(e)}
            self.reporter.warning(f"    ✗ easements: {str(e)}")

        # Infrastructure
        self.reporter.info("  Checking infrastructure...")
        infra_types = {
            'streets': 'streets',
            'railway': 'railway',
            'railway_stations': 'railwayStations',
            'ferry': 'ferry',
            'electric_transmission': 'electricTransmissionLines'
        }

        for key, api_type in infra_types.items():
            try:
                response = self.geo_client.query_infrastructure_features(property_id, api_type, state)

                if response.status_code == 200:
                    data = response.json()
                    features = data.get('features', [])
                    layers['infrastructure'][key] = {
                        'available': len(features) > 0,
                        'feature_count': len(features),
                        'method': 'feature_query',
                        'features': features[:10] if features else []  # First 10
                    }
                    if features:
                        self.reporter.info(f"    ✓ {key}: {len(features)} features")
                else:
                    # Fallback to image check
                    img_response = self.geo_client.get_infrastructure_data(bbox, api_type, state)
                    available = img_response.status_code == 200 and len(img_response.content) > 500
                    layers['infrastructure'][key] = {
                        'available': available,
                        'method': 'image_check',
                        'image_size': len(img_response.content) if img_response.status_code == 200 else 0
                    }
            except Exception as e:
                layers['infrastructure'][key] = {'available': False, 'error': str(e)}
                self.reporter.warning(f"    ✗ {key}: {str(e)}")

        return layers

    def save_map_exports(self, property_id: str, bbox: str, state: str, output_dir: Path) -> Dict[str, str]:
        """Save map image exports"""
        self.reporter.info("🗺️  Exporting maps...")

        saved_maps = {}

        # Property boundaries map
        try:
            response = self.geo_client.get_property_boundaries(bbox, property_id)
            if response.status_code == 200 and len(response.content) > 1000:
                map_path = output_dir / f"{property_id}_property_boundaries.png"
                with open(map_path, 'wb') as f:
                    f.write(response.content)
                saved_maps['property_boundaries'] = str(map_path)
                self.reporter.info(f"  ✓ Property boundaries map")
        except Exception as e:
            self.reporter.warning(f"  ✗ Property boundaries: {e}")

        # Hazard maps
        for hazard_type in ['bushfire', 'flood', 'heritage']:
            try:
                response = self.geo_client.get_hazard_data(bbox, hazard_type)
                if response.status_code == 200 and len(response.content) > 1000:
                    map_path = output_dir / f"{property_id}_{hazard_type}_hazard.png"
                    with open(map_path, 'wb') as f:
                        f.write(response.content)
                    saved_maps[f'{hazard_type}_hazard'] = str(map_path)
                    self.reporter.info(f"  ✓ {hazard_type.title()} hazard map")
            except Exception as e:
                self.reporter.warning(f"  ✗ {hazard_type}: {e}")

        # Infrastructure maps
        for infra_type in ['streets', 'railway']:
            try:
                response = self.geo_client.get_infrastructure_data(bbox, infra_type, state)
                if response.status_code == 200 and len(response.content) > 500:
                    map_path = output_dir / f"{property_id}_infrastructure_{infra_type}.png"
                    with open(map_path, 'wb') as f:
                        f.write(response.content)
                    saved_maps[f'infrastructure_{infra_type}'] = str(map_path)
                    self.reporter.info(f"  ✓ Infrastructure {infra_type} map")
            except Exception as e:
                self.reporter.warning(f"  ✗ {infra_type}: {e}")

        return saved_maps

    def get_market_metrics(self, property_details: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get market metrics for the property location"""
        try:
            self.reporter.info("📊 Fetching market metrics...")
            market_processor = MarketDataProcessor(reporter=ProgressReporter("Market Metrics"))

            # Get location ID from property details
            location = property_details.get('location', {})
            location_id = None

            # Try locality ID first (suburb level)
            if location.get('locality', {}).get('id'):
                location_id = location['locality']['id']
                self.reporter.info(f"   Using locality ID: {location_id}")
            # Fallback to postcode ID
            elif location.get('postcode', {}).get('id'):
                location_id = location['postcode']['id']
                self.reporter.info(f"   Using postcode ID: {location_id}")

            if location_id:
                # Get most recent sale date for date range
                sales_history = property_details.get('sales', {})
                from_date = "2020-01-01"  # Default lookback

                if sales_history and sales_history.get('saleList'):
                    recent_sale = sales_history['saleList'][0]
                    if recent_sale.get('contractDate'):
                        from_date = recent_sale['contractDate'][:7] + "-01"  # First of month

                # Fetch comprehensive market data
                market_data = market_processor.fetch_comprehensive_market_data(
                    location_id=int(location_id),
                    location_type_id=8,  # Suburb level
                    property_type_id=1,  # Houses
                    from_date=from_date,
                    to_date="2022-03-31"  # Latest available
                )

                # Generate market metrics summary
                market_metrics_summary = market_processor.generate_market_metrics_summary(market_data)

                available_count = market_metrics_summary['summary']['available_metrics']
                total_count = market_metrics_summary['summary']['total_metrics']
                self.reporter.success(f"✓ Market metrics: {available_count}/{total_count} available")

                return market_metrics_summary
            else:
                self.reporter.warning("⚠️  No location ID found for market metrics")
                return None

        except Exception as e:
            self.reporter.error(f"✗ Market metrics failed: {e}")
            return {'error': str(e)}

    def run_google_places_analysis(self, address: str, output_dir: Path, property_id: str) -> Optional[Dict[str, Any]]:
        """Run Google Places analysis and return processed data"""
        try:
            self.reporter.info("🔍 Running Google Places impact analysis...")

            # Create temporary subdirectory for Places data
            places_dir = output_dir / f"places_analysis_{property_id}"
            places_dir.mkdir(parents=True, exist_ok=True)

            # Configure Places pipeline
            config = PipelineConfig()
            config.set('output_dir', str(places_dir))

            places_reporter = ProgressReporter("Google Places")
            places_pipeline = GooglePlacesPipeline(config, places_reporter)

            # Run Places analysis
            places_pipeline.run(address)

            # Load and process results
            statistics_file = places_dir / 'statistics.json'
            impacts_file = places_dir / 'property_impacts.json'

            if not statistics_file.exists() or not impacts_file.exists():
                self.reporter.warning("⚠️  Places data files not found")
                return None

            with open(statistics_file) as f:
                stats = json.load(f)

            with open(impacts_file) as f:
                impacts = json.load(f)

            # Process and normalize data
            if 'summary' in stats:
                # New structure with nested summary
                summary_data = stats['summary']
                dist_dist = stats.get('closest_places_distance_distribution', {})
                distance_distribution = {
                    'closest_meters': dist_dist.get('closest_m', 0),
                    'furthest_meters': dist_dist.get('furthest_m', 0),
                    'median_meters': dist_dist.get('median_m', 0),
                    'within_100m': dist_dist.get('within_100m', 0),
                    'within_250m': dist_dist.get('within_250m', 0),
                    'within_600m': dist_dist.get('within_600m', 0),
                    'within_3000m': dist_dist.get('within_3000m', 0)
                }
            else:
                # Old structure with top-level keys
                summary_data = stats
                distance_distribution = stats.get('distance_distribution', {})

            # Extract key metrics
            places_summary = {
                'total_categories': summary_data.get('total_categories', 0),
                'categories_with_matches': summary_data.get('categories_with_matches', 0),
                'categories_without_matches': summary_data.get('categories_without_matches', 0),
                'distance_distribution': distance_distribution,
                'level_statistics': stats.get('level_statistics', {}),
                'closest_impacts': []
            }

            # Parse impacts structure: level -> category -> data
            impact_analysis = impacts.get('impact_analysis', {})
            for level, categories in impact_analysis.items():
                for category, category_data in categories.items():
                    closest_place = category_data.get('closest_place')
                    if closest_place is not None:
                        places_summary['closest_impacts'].append({
                            'category': category,
                            'name': closest_place.get('name', 'N/A'),
                            'distance_meters': closest_place.get('distance_meters', 0),
                            'level': level,
                            'address': closest_place.get('formatted_address', 'N/A')
                        })

            # Sort by distance
            places_summary['closest_impacts'].sort(key=lambda x: x['distance_meters'])

            categories_with = places_summary['categories_with_matches']
            total_categories = places_summary['total_categories']
            self.reporter.success(f"✓ Google Places: {categories_with}/{total_categories} categories with matches")

            return places_summary

        except Exception as e:
            self.reporter.error(f"✗ Google Places analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e)}

    def generate_ultra_comprehensive_report(self, address: str, state: Optional[str] = None,
                                           include_maps: bool = False, output_dir: Path = None) -> Dict[str, Any]:
        """Generate complete ultra-comprehensive report with ALL available data"""

        # Auto-detect state if not provided
        if state is None:
            state = self.detect_state_from_address(address)
            self.reporter.info(f"🌏 Auto-detected state: {state.upper()}")

        # 1. Get property ID
        self.reporter.info("📍 Resolving property ID...")
        property_id = self.property_processor.get_property_id_from_address(address)

        if not property_id:
            raise ValueError(f"No property found for address: {address}")

        self.reporter.success(f"✓ Found property ID: {property_id}")

        # 2. Get comprehensive property details (13 API endpoints)
        property_details = self.get_comprehensive_property_details(property_id)

        # 3. Get parcel geometry
        self.reporter.info("📐 Getting parcel geometry...")
        try:
            parcel_data = self.geo_client.get_parcel_polygon(property_id)
            parcel_success = True
        except Exception as e:
            parcel_data = {'error': str(e)}
            parcel_success = False
            self.reporter.error(f"✗ Parcel geometry failed: {e}")

        # 4. Calculate bounding box
        bbox = None
        if parcel_success:
            bbox = self.calculate_bbox(parcel_data, buffer_meters=5000)
            if bbox:
                self.reporter.info(f"📦 Bounding box (5km): {bbox}")
            else:
                self.reporter.warning("⚠️  Could not calculate bounding box")

        # 5. Get geospatial layers
        geospatial_layers = {}
        if bbox:
            geospatial_layers = self.get_geospatial_layers(property_id, bbox, state)

        # 6. Get market metrics
        market_metrics_summary = self.get_market_metrics(property_details)

        # 7. Run Google Places analysis
        google_places_impact = self.run_google_places_analysis(address, output_dir, property_id)

        # 8. Save map exports if requested
        saved_maps = {}
        if include_maps and bbox and output_dir:
            saved_maps = self.save_map_exports(property_id, bbox, state, output_dir)

        # Compile ultra-comprehensive report
        report = {
            'metadata': {
                'extraction_timestamp': datetime.now().isoformat(),
                'address': address,
                'property_id': property_id,
                'state': state.upper(),
                'bbox': bbox,
                'bbox_buffer_meters': 5000 if bbox else None,
                'report_type': 'ultra_comprehensive'
            },
            'property_details': {
                'location': property_details.get('location'),
                'legal': property_details.get('legal'),
                'site': property_details.get('site'),
                'core_attributes': property_details.get('core_attributes'),
                'additional_attributes': property_details.get('additional_attributes'),
                'features': property_details.get('features'),
                'occupancy': property_details.get('occupancy'),
                'last_sale': property_details.get('last_sale'),
                'sales_history': property_details.get('sales'),
                'sales_otm': property_details.get('sales_otm'),
                'rentals_otm': property_details.get('rentals_otm'),
                'timeline': property_details.get('timeline'),
                'advertisements': property_details.get('advertisements')
            },
            'parcel_geometry': {
                'success': parcel_success,
                'data': parcel_data if parcel_success else None,
                'error': parcel_data.get('error') if not parcel_success else None
            },
            'geospatial_layers': geospatial_layers,
            'market_metrics_summary': market_metrics_summary,
            'google_places_impact': google_places_impact,
            'maps_exported': saved_maps if include_maps else None
        }

        return report


def print_summary(report: Dict[str, Any]):
    """Print human-readable summary"""

    print("\n" + "=" * 80)
    print("ULTRA-COMPREHENSIVE PROPERTY DATA REPORT")
    print("=" * 80)

    metadata = report['metadata']
    print(f"\n📍 Address: {metadata['address']}")
    print(f"🆔 Property ID: {metadata['property_id']}")
    print(f"🌏 State: {metadata['state']}")
    print(f"⏰ Extracted: {metadata['extraction_timestamp']}")

    # Property Details Summary
    print(f"\n📋 PROPERTY DETAILS (13 API ENDPOINTS)")
    details = report['property_details']
    for key, value in details.items():
        if value and not isinstance(value, dict) or (isinstance(value, dict) and not value.get('error')):
            print(f"  ✅ {key.replace('_', ' ').title()}")
        else:
            print(f"  ❌ {key.replace('_', ' ').title()}")

    # Parcel Geometry
    print(f"\n📐 PARCEL GEOMETRY")
    if report['parcel_geometry']['success']:
        print(f"  ✅ Parcel polygon available")
    else:
        print(f"  ❌ Parcel geometry failed")

    # Geospatial Layers
    if report['geospatial_layers']:
        layers = report['geospatial_layers']

        print(f"\n⚠️  HAZARD OVERLAYS")
        for hazard_type, data in layers.get('hazards', {}).items():
            if data.get('available'):
                count = data.get('feature_count', 0)
                print(f"  ✅ {hazard_type.title()}: {count} feature(s)" if count else f"  ✅ {hazard_type.title()}")
            else:
                print(f"  ❌ {hazard_type.title()}")

        print(f"\n📋 LEGAL")
        easements = layers.get('legal', {}).get('easements', {})
        if easements.get('available'):
            print(f"  ✅ Easements: {easements['count']} found")
        else:
            print(f"  ❌ Easements: Not available")

        print(f"\n🏗️  INFRASTRUCTURE")
        for infra_type, data in layers.get('infrastructure', {}).items():
            name = infra_type.replace('_', ' ').title()
            if data.get('available'):
                count = data.get('feature_count', 0)
                print(f"  ✅ {name}: {count} feature(s)" if count else f"  ✅ {name}")
            else:
                print(f"  ❌ {name}")

    # Market Metrics
    if report.get('market_metrics_summary') and not report['market_metrics_summary'].get('error'):
        metrics = report['market_metrics_summary']
        summary = metrics.get('summary', {})
        print(f"\n📊 MARKET METRICS")
        print(f"  Available: {summary.get('available_metrics', 0)}/{summary.get('total_metrics', 0)}")

    # Google Places Impact
    places = report.get('google_places_impact')
    if places and not places.get('error'):
        print(f"\n🔍 GOOGLE PLACES IMPACT ANALYSIS")
        total_cats = places.get('total_categories', 0)
        with_matches = places.get('categories_with_matches', 0)
        print(f"  Categories Analyzed: {total_cats}")
        print(f"  Categories with Matches: {with_matches}/{total_cats}")

        closest_impacts = places.get('closest_impacts', [])[:5]
        if closest_impacts:
            print(f"  Top 5 Closest:")
            for impact in closest_impacts:
                category = impact.get('category', 'Unknown').replace('_', ' ').title()
                name = impact.get('name', 'N/A')
                distance = impact.get('distance_meters', 0)
                print(f"    • {category}: {name} ({distance:.0f}m)")

    # Maps
    if report.get('maps_exported'):
        print(f"\n🗺️  MAPS EXPORTED")
        for map_type, path in report['maps_exported'].items():
            print(f"  ✓ {map_type.replace('_', ' ').title()}")

    print("\n" + "=" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Generate ultra-comprehensive property data report with ALL available data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Complete extraction
  python3 scripts/generate_ultra_comprehensive_json.py --address "5 Settlers Court, Vermont South VIC 3133"

  # With map exports
  python3 scripts/generate_ultra_comprehensive_json.py --address "16 Fowler Crescent, South Coogee, NSW, 2034" --include-maps

  # Custom output directory
  python3 scripts/generate_ultra_comprehensive_json.py --address "123 Main St" --output-dir reports/property_data

Output Files:
  - {property_id}_ultra_comprehensive_report.json (all data combined)

Data Sources:
  - CoreLogic Property Details (13 API endpoints)
  - Geospatial Layers (hazards, legal, infrastructure)
  - Parcel Geometry
  - Market Metrics
  - Google Places Impact Analysis
        """
    )

    parser.add_argument(
        '--address',
        required=True,
        type=str,
        help='Property address to analyze'
    )

    parser.add_argument(
        '--state',
        type=str,
        default=None,
        choices=['nsw', 'vic', 'qld', 'sa', 'wa', 'tas', 'act', 'nt'],
        help='State code (default: auto-detect from address)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/property_reports',
        help='Output directory for results (default: data/property_reports)'
    )

    parser.add_argument(
        '--include-maps',
        action='store_true',
        help='Export map images (PNG files)'
    )

    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty print JSON output'
    )

    args = parser.parse_args()

    try:
        # Create output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        print("\n🚀 Initializing API clients...")

        # Initialize processors
        property_reporter = ProgressReporter("Property Lookup")
        property_processor = PropertyDataProcessor(reporter=property_reporter)
        geo_client = GeospatialAPIClient.from_env()

        # Create reporter
        reporter = UltraComprehensivePropertyReporter(geo_client, property_processor)

        # Generate ultra-comprehensive report
        report = reporter.generate_ultra_comprehensive_report(
            args.address,
            state=args.state,
            include_maps=args.include_maps,
            output_dir=output_dir
        )

        property_id = report['metadata']['property_id']

        # Save ultra-comprehensive report
        indent = 2 if args.pretty else None
        report_path = output_dir / f"{property_id}_ultra_comprehensive_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=indent)

        # Print summary
        print_summary(report)

        # Print file location
        print("📁 Output File:")
        print(f"   📄 Ultra-Comprehensive Report: {report_path}")

        if args.include_maps and report.get('maps_exported'):
            print(f"\n🗺️  Maps:")
            for map_type, path in report['maps_exported'].items():
                print(f"   {map_type.replace('_', ' ').title()}: {path}")

        print("\n✅ Ultra-comprehensive report complete!")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
