#!/usr/bin/env python3
"""
Example: Using Comparable Sales Generator

Demonstrates various ways to use the comparable sales generator utility.

Run this script:
    python3 scripts/examples/example_comparable_sales.py
"""

import sys
from pathlib import Path

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "utils"))

from utils.comparable_sales_generator import (
    ComparableSalesGenerator,
    generate_comparable_sales_json
)


def example_1_simple_search():
    """Example 1: Simple search by property ID with default 5km radius"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Simple Search (Default 5km Radius)")
    print("="*60)

    # Simple one-liner
    data, file_path = generate_comparable_sales_json(
        property_id="13683380"
    )

    print(f"\nResults:")
    print(f"  Total comparables: {data['metadata']['total_comparables']}")
    print(f"  Output file: {file_path}")

    # Access statistics
    if 'price_statistics' in data['statistics']:
        stats = data['statistics']['price_statistics']
        print(f"\n  Price Statistics:")
        print(f"    Median: ${stats['median']:,.0f}")
        print(f"    Mean: ${stats['mean']:,.0f}")
        print(f"    Range: ${stats['min']:,.0f} - ${stats['max']:,.0f}")


def example_2_with_filters():
    """Example 2: Search with price and property filters"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Search with Filters")
    print("="*60)

    generator = ComparableSalesGenerator()

    # Create filters for similar houses
    filters = generator.create_filters(
        price="800000-1200000",
        beds="3-5",
        baths="2-3",
        property_types=["HOUSE"],
        date="20230101-"  # Sales from 2023 onwards
    )

    print(f"\nFilters applied: {filters}")

    data, file_path = generate_comparable_sales_json(
        property_id="13683380",
        radius=5.0,
        filters=filters
    )

    print(f"\nResults:")
    print(f"  Total comparables: {data['metadata']['total_comparables']}")
    print(f"  Output file: {file_path}")


def example_3_coordinate_search():
    """Example 3: Search by coordinates with custom radius"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Coordinate Search with 10km Radius")
    print("="*60)

    # Vermont South, VIC
    lat = -37.8136
    lon = 145.1772
    radius = 10.0  # 10km radius

    data, file_path = generate_comparable_sales_json(
        lat=lat,
        lon=lon,
        radius=radius
    )

    print(f"\nResults:")
    print(f"  Search location: {lat}, {lon}")
    print(f"  Radius: {radius}km")
    print(f"  Total comparables: {data['metadata']['total_comparables']}")


def example_4_custom_output():
    """Example 4: Save to custom location"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Custom Output Location")
    print("="*60)

    output_file = "data/custom/my_comparables.json"

    data, file_path = generate_comparable_sales_json(
        property_id="13683380",
        radius=5.0,
        output_file=output_file
    )

    print(f"\nResults saved to: {file_path}")


def example_5_accessing_data():
    """Example 5: Accessing and analyzing comparable data"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Accessing Comparable Data")
    print("="*60)

    data, _ = generate_comparable_sales_json(
        property_id="13683380",
        radius=5.0
    )

    # Access metadata
    metadata = data['metadata']
    print(f"\nSearch Metadata:")
    print(f"  Generated: {metadata['generated_at']}")
    print(f"  Search type: {metadata['search_type']}")
    print(f"  Total comparables: {metadata['total_comparables']}")

    # Access statistics
    stats = data['statistics']
    print(f"\nStatistics:")

    if 'price_statistics' in stats:
        price = stats['price_statistics']
        print(f"  Price:")
        print(f"    Median: ${price['median']:,.0f}")
        print(f"    Q1: ${price['q1']:,.0f}")
        print(f"    Q3: ${price['q3']:,.0f}")
        print(f"    Std Dev: ${price['std_dev']:,.0f}")

    if 'property_characteristics' in stats:
        chars = stats['property_characteristics']
        if 'beds' in chars:
            print(f"  Most common bedrooms: {chars['beds']['most_common']}")
        if 'propertyType' in chars:
            print(f"  Most common type: {chars['propertyType']['most_common']}")

    # Distance distribution
    if 'distance_distribution' in stats:
        dist = stats['distance_distribution']
        print(f"\n  Distance Distribution:")
        print(f"    Within 500m: {dist.get('within_500m', 0)}")
        print(f"    Within 1km: {dist.get('within_1km', 0)}")
        print(f"    Within 3km: {dist.get('within_3km', 0)}")
        print(f"    Total: {dist.get('total', 0)}")

    # Recent comparables date ranges
    if 'recent_25_date_range' in stats and stats['recent_25_date_range']:
        recent_25 = stats['recent_25_date_range']
        print(f"\n  Recent 25 Comparables:")
        print(f"    Date range: {recent_25['earliest']} to {recent_25['latest']}")

    if 'recent_50_date_range' in stats and stats['recent_50_date_range']:
        recent_50 = stats['recent_50_date_range']
        print(f"\n  Recent 50 Comparables:")
        print(f"    Date range: {recent_50['earliest']} to {recent_50['latest']}")

    # Access individual comparables
    comparables = data['comparable_sales']
    print(f"\nFirst 3 Comparables:")
    for i, comp in enumerate(comparables[:3], 1):
        address = comp.get('address', 'Unknown')
        price = comp.get('salePrice', 0)
        beds = comp.get('beds', 'N/A')
        print(f"  {i}. {address}")
        print(f"     Price: ${price:,.0f} | Beds: {beds}")


def example_6_advanced_usage():
    """Example 6: Advanced usage with ComparableSalesGenerator class"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Advanced Usage")
    print("="*60)

    generator = ComparableSalesGenerator()

    # Create multiple filter sets
    filter_sets = {
        "affordable": generator.create_filters(
            price="500000-800000",
            property_types=["HOUSE", "TOWNHOUSE"]
        ),
        "premium": generator.create_filters(
            price="1500000-",
            land_area="800-",
            property_types=["HOUSE"]
        ),
        "recent": generator.create_filters(
            date="20240101-",
            price="800000-1200000"
        )
    }

    # Search with each filter set
    for name, filters in filter_sets.items():
        print(f"\n{name.upper()} COMPARABLES:")
        print(f"  Filters: {filters}")

        data = generator.search_comparables_by_property_id(
            property_id="13683380",
            radius=5.0,
            filters=filters,
            get_all_pages=False,  # Just first page for demo
            max_results=20
        )

        count = data['metadata']['total_comparables']
        print(f"  Found: {count} properties")

        if 'price_statistics' in data['statistics']:
            median = data['statistics']['price_statistics'].get('median', 0)
            print(f"  Median price: ${median:,.0f}")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print(" COMPARABLE SALES GENERATOR - EXAMPLES")
    print("="*70)

    examples = [
        ("Simple Search", example_1_simple_search),
        ("With Filters", example_2_with_filters),
        ("Coordinate Search", example_3_coordinate_search),
        ("Custom Output", example_4_custom_output),
        ("Accessing Data", example_5_accessing_data),
        ("Advanced Usage", example_6_advanced_usage)
    ]

    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\nRunning all examples...\n")

    for name, example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*70)
    print(" Examples complete!")
    print("="*70)


if __name__ == "__main__":
    main()
