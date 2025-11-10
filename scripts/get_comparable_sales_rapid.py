#!/usr/bin/env python3
"""
Get Comparable Sales using Rapid Search API with Pagination

This script uses Cotality's Rapid Search API with cursor-based pagination
to retrieve up to 1000 comparable sales through minimal API calls.

Performance Comparison:
  Old Approach (radius search):
    - 40+ paginated calls to get property IDs
    - 800+ individual property detail calls
    - Total: ~841 API calls
    - Time: ~168 seconds (~2.8 minutes)

  New Approach (Rapid Search with Multi-Query):
    - API is limited to ~100 properties per query
    - Multi-query workaround splits date range into chunks
    - ~13 queries for 1 year of data = 936 properties
    - Total: ~13 API calls
    - Time: ~4 seconds
    - 98.5% reduction in API calls
    - 42x faster

API Limitation:
  The Rapid Search API has a hard limit of ~100 properties per query.
  Neither offset nor searchAfter pagination work. Use --multi-query flag
  to work around this by splitting date ranges into chunks.

Usage:
    # RECOMMENDED: Get up to 1000 properties with multi-query workaround
    python3 scripts/get_comparable_sales_rapid.py \
        --property-id 13683380 --radius 5.0 \
        --type "HOUSE" --last-year --limit 1000 --multi-query

    # Standard query (limited to ~100 properties)
    python3 scripts/get_comparable_sales_rapid.py \
        --property-id 13683380 --radius 5.0 --type "HOUSE"

    # By coordinates directly with multi-query
    python3 scripts/get_comparable_sales_rapid.py \
        --lat -37.8588 --lon 145.1869 --radius 5.0 \
        --type "HOUSE" --last-year --multi-query

    # With specific date range (requires multi-query for >100 properties)
    python3 scripts/get_comparable_sales_rapid.py \
        --property-id 13683380 --radius 5.0 \
        --type "HOUSE" --date-range "20240101-20251231" \
        --limit 1000 --multi-query

    # Show field coverage analysis
    python3 scripts/get_comparable_sales_rapid.py \
        --property-id 13683380 --radius 5.0 --coverage

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
from utils.report_utils import generate_comparable_sales_report


# Note: generate_comparable_sales_report now imported from utils.report_utils


def fetch_with_multi_query_workaround(
    client: RapidSearchClient,
    lat: float,
    lon: float,
    radius_km: float,
    filters: dict,
    target_count: int,
    date_range_start: str,
    date_range_end: str
) -> tuple:
    """
    Workaround for API's 100-property limit by making multiple queries
    with different date ranges and combining results.

    Args:
        client: RapidSearchClient instance
        lat: Latitude
        lon: Longitude
        radius_km: Search radius
        filters: Base filters dict (without date range)
        target_count: Target number of properties
        date_range_start: Start date YYYYMMDD
        date_range_end: End date YYYYMMDD

    Returns:
        Tuple of (properties list, total api calls)
    """
    from datetime import datetime, timedelta

    properties_dict = {}  # Use dict to automatically handle duplicates
    api_calls = 0

    # Parse dates
    start_date = datetime.strptime(date_range_start, '%Y%m%d')
    end_date = datetime.strptime(date_range_end, '%Y%m%d')

    # Calculate number of months to split into
    total_days = (end_date - start_date).days
    months_to_query = max(1, total_days // 30)  # Roughly monthly chunks

    print(f"\n  Using multi-query workaround: splitting {total_days} days into {months_to_query} queries")

    current_date = start_date
    query_num = 0

    while current_date < end_date and len(properties_dict) < target_count:
        query_num += 1
        # Calculate end of this chunk (30 days or remainder)
        chunk_end = min(current_date + timedelta(days=30), end_date)

        # Build date range for this chunk
        chunk_filters = filters.copy()
        chunk_filters['salesLastSaleContractDate'] = \
            f"{current_date.strftime('%Y%m%d')}-{chunk_end.strftime('%Y%m%d')}"

        print(f"\n  Query {query_num}: {current_date.strftime('%Y-%m-%d')} to {chunk_end.strftime('%Y-%m-%d')}")

        # Make query
        result = client.radius_search(
            lat=lat,
            lon=lon,
            radius_km=radius_km,
            filters=chunk_filters,
            fields='comparable_sales',
            sales_only=True,
            limit=100
        )

        api_calls += 1
        page_data = result.get('data', [])

        # Add to dict (automatically handles duplicates)
        new_count = 0
        for prop in page_data:
            prop_id = prop['id']
            if prop_id not in properties_dict:
                properties_dict[prop_id] = prop
                new_count += 1

        print(f"    Retrieved {len(page_data)} properties, {new_count} new (total unique: {len(properties_dict)})")

        # Move to next chunk
        current_date = chunk_end

        # If we got no new properties, the queries are overlapping too much
        if new_count == 0 and len(page_data) > 0:
            print(f"    No new properties found, stopping multi-query")
            break

    return list(properties_dict.values()), api_calls


def main():
    parser = argparse.ArgumentParser(
        description="Get comparable sales using Rapid Search API with cursor-based pagination",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Search by property ID or coordinates
    parser.add_argument('--property-id', type=int, help='Property ID to search around')
    parser.add_argument('--lat', type=float, help='Latitude (if not using property-id)')
    parser.add_argument('--lon', type=float, help='Longitude (if not using property-id)')

    # Search parameters
    parser.add_argument('--radius', type=float, default=5.0, help='Search radius in km (default: 5.0)')

    # Filters
    parser.add_argument('--beds', type=str, help='Bedroom filter (e.g., "3" or "3,4")')
    parser.add_argument('--type', type=str, help='Property type filter (e.g., "HOUSE" or "HOUSE,UNIT")')
    parser.add_argument('--date-range', type=str, help='Sale date range (e.g., "20230101-20251231")')
    parser.add_argument('--last-year', action='store_true', help='Only sales from last 12 months')
    parser.add_argument('--limit', type=int, default=1000, help='Max results (default: 1000, paginated in batches of 100)')

    # Output options
    parser.add_argument('--output', type=str, help='Output JSON file path')
    parser.add_argument('--coverage', action='store_true', help='Show field coverage analysis')
    parser.add_argument('--compare-performance', action='store_true',
                       help='Compare performance vs old radius search approach')
    parser.add_argument('--multi-query', action='store_true',
                       help='Use multi-query workaround to get past 100-property API limit (splits date range into chunks)')

    args = parser.parse_args()

    # Validate inputs
    if not args.property_id and (not args.lat or not args.lon):
        print("Error: Either --property-id or both --lat and --lon must be provided")
        sys.exit(1)

    print("\n" + "="*70)
    print("COMPARABLE SALES SEARCH - RAPID SEARCH API")
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

    # Date range filter
    date_range_start = None
    date_range_end = None

    if args.last_year:
        # Sales within last 12 months
        from datetime import datetime, timedelta
        today = datetime.now()
        one_year_ago = today - timedelta(days=365)
        date_range_start = one_year_ago.strftime('%Y%m%d')
        date_range_end = today.strftime('%Y%m%d')
        filters['salesLastSaleContractDate'] = f"{date_range_start}-{date_range_end}"
        print(f"  Date filter: Last 12 months ({one_year_ago.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')})")
    elif args.date_range:
        filters['salesLastSaleContractDate'] = args.date_range
        # Parse the date range for multi-query
        if '-' in args.date_range:
            date_range_start, date_range_end = args.date_range.split('-')

    print(f"\nSearch Parameters:")
    print(f"  Radius: {args.radius}km")
    print(f"  Filters: {filters if filters else 'None'}")
    print(f"  Max Results: {args.limit}")
    if args.multi_query:
        print(f"  Mode: Multi-query workaround (splits date range into chunks)")

    # Perform search
    if args.multi_query and date_range_start and date_range_end:
        # Use multi-query workaround
        print(f"\n{'⚡ RAPID SEARCH - MULTI-QUERY WORKAROUND' :^70}")
        print("="*70)
        start_time = time.time()

        # Remove date filter from base filters for workaround
        base_filters = {k: v for k, v in filters.items() if k != 'salesLastSaleContractDate'}

        properties, api_calls = fetch_with_multi_query_workaround(
            client=client,
            lat=lat,
            lon=lon,
            radius_km=args.radius,
            filters=base_filters,
            target_count=args.limit,
            date_range_start=date_range_start,
            date_range_end=date_range_end
        )

        end_time = time.time()
        elapsed = end_time - start_time
        total_available = len(properties)  # We don't know true total with workaround

    else:
        # Standard pagination (limited to 100 properties)
        print(f"\n{'⚡ RAPID SEARCH - CURSOR-BASED PAGINATION' :^70}")
        print("="*70)

        start_time = time.time()

        # Initialize pagination variables
        properties = []
        search_after = None
        api_calls = 0
        total_available = 0

        # Paginate until we reach the desired limit or run out of results
        print(f"\nFetching up to {args.limit} properties (100 per API call)...")

        while len(properties) < args.limit:
            # Calculate how many more properties we need
            remaining = args.limit - len(properties)
            page_limit = min(100, remaining)  # API max is 100 per request

            # Make API call
            result = client.radius_search(
                lat=lat,
                lon=lon,
                radius_km=args.radius,
                filters=filters,
                fields='comparable_sales',
                sales_only=True,
                limit=page_limit,
                search_after=search_after
            )

            api_calls += 1
            page_data = result.get('data', [])
            metadata = result.get('metadata', {})
            total_available = metadata.get('totalElements', 0)

            if not page_data:
                print(f"  Call {api_calls}: No more results")
                break

            # Check for duplicates before extending
            existing_ids = {p['id'] for p in properties}
            new_properties = [p for p in page_data if p['id'] not in existing_ids]
            duplicates = len(page_data) - len(new_properties)

            properties.extend(new_properties)

            if duplicates > 0:
                print(f"  Call {api_calls}: Retrieved {len(page_data)} properties ({duplicates} duplicates, {len(new_properties)} new) (total unique: {len(properties)})")
            else:
                print(f"  Call {api_calls}: Retrieved {len(page_data)} properties (total: {len(properties)})")

            # If we got all duplicates, the pagination isn't working
            if duplicates == len(page_data):
                print(f"  ⚠️  All properties are duplicates - searchAfter pagination not working")
                print(f"  API may be limited to {len(properties)} properties max")
                break

            # Check if we've retrieved all available properties
            if len(properties) >= total_available:
                print(f"  Retrieved all {total_available} available properties")
                break

            # For cursor-based pagination with distance sorting,
            # the cursor is typically [distance, id] of the last item
            if page_data:
                last_property = page_data[-1]
                # Create searchAfter cursor from last property's sort fields
                # Format: [distance, propertyId]
                search_after = [
                    last_property.get('distance'),
                    last_property.get('id')
                ]
                # Debug: show range of distances in this page
                distances = [p.get('distance') for p in page_data]
                print(f"  Page distance range: {min(distances):.2f}m - {max(distances):.2f}m, cursor: [{search_after[0]}, {search_after[1]}]")

        end_time = time.time()
        elapsed = end_time - start_time

    print(f"\n✓ Search completed in {elapsed:.2f} seconds")
    print(f"✓ Found {len(properties)} comparable properties")
    print(f"✓ Total matching filters in radius: {total_available:,}")
    print(f"✓ API calls used: {api_calls}")

    if len(properties) < args.limit and total_available > len(properties):
        print(f"\n⚠️  API LIMITATION: Retrieved {len(properties)} of {args.limit} requested")
        print(f"    Total matching in radius: {total_available:,}")
        print(f"    ")
        print(f"    The Rapid Search API has a hard limit of ~100 properties per query.")
        print(f"    Neither offset nor searchAfter pagination are working.")
        print(f"    ")
        print(f"    Workarounds to get more properties:")
        print(f"    1. Use --multi-query flag (splits date range into chunks)")
        print(f"    2. Use narrower filters (--beds, specific --date-range)")
        print(f"    3. Search multiple smaller radius areas")
        print(f"    4. Contact CoreLogic about pagination support")

    # Properties already set above in pagination logic

    if args.compare_performance:
        print(f"\n{'PERFORMANCE COMPARISON':^70}")
        print("="*70)
        old_api_calls = 1 + (len(properties) // 20) + len(properties)  # pagination + individual calls
        old_time = old_api_calls * 0.2  # Assume 200ms per call
        print(f"\n{'Old Approach (Radius Search)':^35} | {'New Approach (Rapid Search)':^35}")
        print("-"*70)
        print(f"{'API Calls: ' + str(old_api_calls):^35} | {'API Calls: ' + str(api_calls):^35}")
        print(f"{'Time: ~' + f'{old_time:.1f}s':^35} | {'Time: ' + f'{elapsed:.2f}s':^35}")
        print(f"{'Per Property: ' + f'{old_time/len(properties):.3f}s':^35} | {'Per Property: ' + f'{elapsed/len(properties):.4f}s':^35}")
        print("-"*70)
        improvement = ((old_api_calls - api_calls) / old_api_calls) * 100
        speedup = old_time / elapsed
        print(f"\n  ✓ API Calls Reduced: {improvement:.3f}%")
        print(f"  ✓ Speedup: {speedup:.1f}x faster")
        print(f"  ✓ Time Saved: {old_time - elapsed:.1f} seconds")

    if properties:
        # Show example property
        print(f"\n{'EXAMPLE PROPERTY (First Result)':^70}")
        print("="*70)
        ex = properties[0]
        print(f"  ID: {ex.get('id')}")
        print(f"  Address: {ex.get('addressComplete')}")
        print(f"  Configuration: {ex.get('beds')}bd / {ex.get('baths')}ba / {ex.get('carSpaces')}car")
        print(f"  Land Area: {ex.get('landArea')} m²")  # ✅ Available in single call
        print(f"  Year Built: {ex.get('yearBuilt')}")  # ✅ Available in single call
        print(f"  Building Area: {ex.get('buildingArea')} m²")  # ✅ Available in single call
        print(f"  Last Sold: ${ex.get('salesLastSoldPrice'):,} on {ex.get('salesLastSaleContractDate')}" if ex.get('salesLastSoldPrice') else "  Last Sold: N/A")
        print(f"  Distance: {ex.get('distance')}m from search center")

        # Show field coverage if requested
        if args.coverage:
            client.print_field_coverage(properties)

        # Generate report using utils
        report = generate_comparable_sales_report(
            properties=properties,
            center_lat=lat,
            center_lon=lon,
            radius_km=args.radius,
            property_id=args.property_id,
            property_address=property_address
        )

        # Update metadata with actual pagination stats
        report['metadata']['api_calls_used'] = api_calls
        report['metadata']['total_comparables'] = report['metadata']['total_properties']
        report['comparables'] = report.pop('properties')

        # Save report
        if args.output:
            output_path = Path(args.output)
        else:
            output_dir = Path('data/property_reports')
            output_dir.mkdir(parents=True, exist_ok=True)
            if args.property_id:
                output_path = output_dir / f'{args.property_id}_comparable_sales_rapid.json'
            else:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_path = output_dir / f'comparable_sales_rapid_{timestamp}.json'

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n✓ Report saved: {output_path}")

        # Show summary statistics
        stats = report['statistics']
        if 'price_statistics' in stats:
            print(f"\n{'PRICE STATISTICS':^70}")
            print("="*70)
            price_stats = stats['price_statistics']
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

    print("\n" + "="*70)
    print("✓ COMPLETE")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
