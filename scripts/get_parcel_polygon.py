#!/usr/bin/env python3
"""
Simple script to get parcel polygon geometry for an address.

Usage:
    python3 scripts/get_parcel_polygon.py --address "123 Main St, Sydney NSW"
    python3 scripts/get_parcel_polygon.py --property-id 1778890
    python3 scripts/get_parcel_polygon.py --address "3 Nymboida Street, South Coogee, NSW, 2034" --output data/outputs/parcel.json --pretty
    python3 scripts/get_parcel_polygon.py --address "16 Fowler Crescent, South Coogee, NSW, 2034" --output data/outputs/parcel.json --pretty
    python3 scripts/get_parcel_polygon.py --address "5 settlers court,vermont south, vic, 3133" --output data/outputs/parcel.json --pretty
"""

import argparse
import json
import sys

# Import from utils subdirectory
from utils.property_data_processor import PropertyDataProcessor
from utils.geospatial_api_client import GeospatialAPIClient
from utils.pipeline_utils import ProgressReporter


def main():
    parser = argparse.ArgumentParser(
        description='Get parcel polygon geometry for an address or property ID'
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--address', type=str, help='Property address to search')
    group.add_argument('--property-id', type=str, help='CoreLogic property ID')

    parser.add_argument(
        '--output',
        type=str,
        help='Output file path (optional, defaults to stdout)'
    )

    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty print JSON output'
    )

    args = parser.parse_args()

    try:
        # Initialize processors
        print("Initializing CoreLogic processors...", file=sys.stderr)
        property_reporter = ProgressReporter("Property Lookup")
        property_processor = PropertyDataProcessor(reporter=property_reporter)
        geo_client = GeospatialAPIClient.from_env()

        # Get property ID and address
        if args.address:
            print(f"Resolving address: {args.address}", file=sys.stderr)
            property_id = property_processor.get_property_id_from_address(args.address)

            if not property_id:
                raise ValueError(f"No property found for address: {args.address}")

            print(f"Found property_id: {property_id}", file=sys.stderr)
            address = args.address
        else:
            property_id = args.property_id
            address = 'N/A (direct property_id lookup)'
            print(f"Using property_id: {property_id}", file=sys.stderr)

        # Get parcel polygon using pipeline method
        print("Fetching parcel geometry...", file=sys.stderr)
        parcel_data = geo_client.get_parcel_polygon(property_id)

        # Format result using pipeline method
        result = geo_client.format_parcel_result(property_id, address, parcel_data)

        # Output results
        indent = 2 if args.pretty else None
        json_output = json.dumps(result, indent=indent)

        if args.output:
            with open(args.output, 'w') as f:
                f.write(json_output)
            print(f"\nResults saved to: {args.output}", file=sys.stderr)
        else:
            print("\n" + json_output)

        # Print summary
        print("\n=== Summary ===", file=sys.stderr)
        print(f"Property ID: {result['property_id']}", file=sys.stderr)
        print(f"Address: {result['address']}", file=sys.stderr)
        print(f"Geometry Type: {result.get('geometry_type', 'N/A')}", file=sys.stderr)

        if 'geometry' in result and result['geometry']:
            geom = result['geometry']
            if 'rings' in geom:
                print(f"Polygon Rings: {len(geom['rings'])}", file=sys.stderr)
                print(f"Vertices: {len(geom['rings'][0]) if geom['rings'] else 0}", file=sys.stderr)

        return 0

    except Exception as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
