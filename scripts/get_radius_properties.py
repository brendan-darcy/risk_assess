#!/usr/bin/env python3
"""
Get Properties in Radius using Rapid Search API

This script uses Cotality's Rapid Search API to retrieve properties within
a specified radius in a SINGLE API call with ALL property fields.

Supports two modes:
1. --sales: Only properties with sales history (comparable sales)
2. --all: ALL properties in radius (including never-sold properties)

Performance Comparison (vs Old Approach):
  Old Approach (radius search):
    - 40+ paginated calls to get property IDs
    - 800+ individual property detail calls
    - Total: ~841 API calls
    - Time: ~168 seconds (~2.8 minutes)

  New Approach (Rapid Search):
    - 1 API call with all fields
    - Total: 1 API call
    - Time: ~0.2 seconds
    - 99.875% reduction in API calls
    - 840x faster

Usage:
    # Get ALL properties in radius (including never-sold)
    python3 scripts/get_radius_properties.py --property-id 13683380 --radius 5.0 --all

    # Get only properties with sales history
    python3 scripts/get_radius_properties.py --property-id 13683380 --radius 5.0 --sales

    # By coordinates directly
    python3 scripts/get_radius_properties.py --lat -37.8588 --lon 145.1869 --radius 5.0 --all

    # With filters
    python3 scripts/get_radius_properties.py \
        --property-id 13683380 --radius 5.0 --all \
        --type "HOUSE" --beds "3-5" \
        --limit 10000

    # Show field coverage analysis
    python3 scripts/get_radius_properties.py \
        --property-id 13683380 --radius 5.0 --sales \
        --coverage

Author: ARMATech Development Team
Date: 2025-11-11
Version: 2.0
"""

import argparse
import json
import sys
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from api.rapid_search_client import RapidSearchClient
from utils.corelogic_auth import CoreLogicAuth
from utils.property_utils import get_property_coordinates, get_property_address
from utils.report_utils import generate_radius_report


def main():
    parser = argparse.ArgumentParser(
        description="Get properties in radius using Rapid Search API (single API call)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Search by property ID or coordinates
    parser.add_argument('--property-id', type=int, help='Property ID to search around')
    parser.add_argument('--lat', type=float, help='Latitude (if not using property-id)')
    parser.add_argument('--lon', type=float, help='Longitude (if not using property-id)')

    # Search mode (mutually exclusive)
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--sales', action='store_true', help='Only properties with sales history')
    mode_group.add_argument('--all', action='store_true', help='ALL properties (including never-sold)')

    # Search parameters
    parser.add_argument('--radius', type=float, default=5.0, help='Search radius in km (default: 5.0)')

    # Filters
    parser.add_argument('--beds', type=str, help='Bedroom filter (e.g., "3" or "3,4" or "3-5")')
    parser.add_argument('--type', type=str, help='Property type filter (e.g., "HOUSE" or "HOUSE,UNIT")')
    parser.add_argument('--date-range', type=str, help='Sale date range (e.g., "20230101-20251231")')
    parser.add_argument('--limit', type=int, default=10000, help='Max results (default: 10000)')

    # Output options
    parser.add_argument('--output', type=str, help='Output JSON file path')
    parser.add_argument('--coverage', action='store_true', help='Show field coverage analysis')

    args = parser.parse_args()

    # Validate inputs
    if not args.property_id and (not args.lat or not args.lon):
        print("Error: Either --property-id or both --lat and --lon must be provided")
        sys.exit(1)

    # Determine search mode
    search_mode = 'sales' if args.sales else 'all'

    print("\n" + "="*70)
    print(f"RADIUS PROPERTY SEARCH - RAPID SEARCH API ({search_mode.upper()} MODE)")
    print("="*70 + "\n")

    # Initialize auth and client
    auth = CoreLogicAuth.from_env()
    client = RapidSearchClient(auth)

    # Get search coordinates
    if args.property_id:
        print(f"Getting coordinates for property {args.property_id}...")
        try:
            lat, lon = get_property_coordinates(args.property_id, auth)
            property_address = get_property_address(args.property_id, auth)
            print(f"  Property: {property_address}")
            print(f"  Coordinates: ({lat:.6f}, {lon:.6f})")
        except Exception as e:
            print(f"Error getting property coordinates: {e}")
            sys.exit(1)
    else:
        lat = args.lat
        lon = args.lon
        property_address = None
        print(f"Using provided coordinates: ({lat:.6f}, {lon:.6f})")

    # Build filters
    filters = {}
    if args.beds:
        filters['beds'] = args.beds
    if args.type:
        filters['type'] = args.type
    if args.date_range:
        filters['salesLastSaleContractDate'] = args.date_range

    print(f"\nSearch Parameters:")
    print(f"  Mode: {search_mode.upper()}")
    print(f"  Radius: {args.radius}km")
    print(f"  Filters: {filters if filters else 'None'}")
    print(f"  Max Results: {args.limit}")

    # Perform search
    print(f"\n{'⚡ RAPID SEARCH - SINGLE API CALL' :^70}")
    print("="*70)

    start_time = time.time()

    result = client.radius_search(
        lat=lat,
        lon=lon,
        radius_km=args.radius,
        filters=filters,
        fields='all',  # Get all available fields
        sales_only=args.sales,
        limit=args.limit
    )

    end_time = time.time()
    elapsed = end_time - start_time

    properties = result.get('data', [])
    metadata = result.get('metadata', {})

    print(f"\n✓ Search completed in {elapsed:.2f} seconds")
    print(f"✓ Found {len(properties)} properties")
    print(f"✓ Total available: {metadata.get('totalElements', 'N/A'):,}")
    print(f"✓ API calls used: 1")

    if properties:
        # Show example property
        print(f"\n{'EXAMPLE PROPERTY (First Result)':^70}")
        print("="*70)
        ex = properties[0]
        print(f"  ID: {ex.get('id')}")
        print(f"  Address: {ex.get('addressComplete')}")
        print(f"  Type: {ex.get('type')} - {ex.get('subType')}")
        print(f"  Configuration: {ex.get('beds')}bd / {ex.get('baths')}ba / {ex.get('carSpaces')}car")
        print(f"  Land Area: {ex.get('landArea')} m²")
        print(f"  Year Built: {ex.get('yearBuilt')}")
        print(f"  Building Area: {ex.get('buildingArea')} m²")
        print(f"  Floor Area: {ex.get('floorArea')} m²")
        print(f"  Last Sold: ${ex.get('salesLastSoldPrice'):,} on {ex.get('salesLastSaleContractDate')}" if ex.get('salesLastSoldPrice') else "  Last Sold: N/A")
        print(f"  Distance: {ex.get('distance')}m from search center")

        # Show field coverage if requested
        if args.coverage:
            client.print_field_coverage(properties)

        # Generate report
        report = generate_radius_report(
            properties=properties,
            center_lat=lat,
            center_lon=lon,
            radius_km=args.radius,
            search_mode=search_mode,
            property_id=args.property_id,
            property_address=property_address
        )

        # Save report
        if args.output:
            output_path = Path(args.output)
        else:
            output_dir = Path('data/property_reports')
            output_dir.mkdir(parents=True, exist_ok=True)
            if args.property_id:
                output_path = output_dir / f'{args.property_id}_radius_{search_mode}.json'
            else:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_path = output_dir / f'radius_{search_mode}_{timestamp}.json'

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n✓ Report saved: {output_path}")

        # Show summary statistics
        stats = report['statistics']

        if search_mode == 'sales' and 'price_statistics' in stats and stats['price_statistics']:
            print(f"\n{'PRICE STATISTICS':^70}")
            print("="*70)
            price_stats = stats['price_statistics']
            print(f"  Properties with sales: {price_stats.get('count', 0)}")
            print(f"  Median: ${price_stats.get('median', 0):,}")
            print(f"  Mean: ${price_stats.get('mean', 0):,}")
            print(f"  Range: ${price_stats.get('min', 0):,} - ${price_stats.get('max', 0):,}")

        print(f"\n{'DISTANCE DISTRIBUTION':^70}")
        print("="*70)
        dist_dist = stats['distance_distribution']
        print(f"  Within 500m: {dist_dist['within_500m']} properties")
        print(f"  Within 1km: {dist_dist['within_1km']} properties")
        print(f"  Within 3km: {dist_dist['within_3km']} properties")
        print(f"  Within 5km: {dist_dist['within_5km']} properties")

        print(f"\n{'PROPERTY TYPE DISTRIBUTION':^70}")
        print("="*70)
        type_dist = stats['property_characteristics']['propertyType']['distribution']
        for prop_type, count in sorted(type_dist.items(), key=lambda x: -x[1])[:5]:
            print(f"  {prop_type}: {count} properties")

    print("\n" + "="*70)
    print("✓ COMPLETE")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
