#!/usr/bin/env python3
"""
Simple script to get parcel polygon geometry for an address.

Usage:
    python scripts/get_parcel_polygon.py --address "123 Main St, Sydney NSW"
    python scripts/get_parcel_polygon.py --property-id 1778890
    python scripts/get_parcel_polygon.py --address "3 Nymboida Street, South Coogee, NSW, 2034" --output data/outputs/parcel.json --pretty
"""

import argparse
import json
import sys
from pathlib import Path

# Add pipelines directory to path
sys.path.append(str(Path(__file__).parent.parent / 'pipelines'))

from property_data_processor import PropertyDataProcessor
from geospatial_api_client import GeospatialAPIClient
from pipeline_utils import ProgressReporter


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

        # Get property ID, address, and locality information
        property_info = None
        if args.address:
            print(f"Resolving address: {args.address}", file=sys.stderr)
            property_info = property_processor.get_property_info_from_address(args.address)

            if not property_info:
                raise ValueError(f"No property found for address: {args.address}")

            property_id = property_info["property_id"]
            address = property_info["full_address"]
            print(f"Found property_id: {property_id}", file=sys.stderr)
        else:
            property_id = args.property_id
            address = 'N/A (direct property_id lookup)'
            print(f"Using property_id: {property_id}", file=sys.stderr)

        # Get property location details (includes lat/long)
        print("Fetching property location details...", file=sys.stderr)
        property_details = property_processor.api_client.get_property_details(
            property_id,
            endpoints_list=['location']
        )
        location_data = property_details.get('location', {})

        # Get parcel polygon using pipeline method
        print("Fetching parcel geometry...", file=sys.stderr)
        parcel_data = geo_client.get_parcel_polygon(property_id)

        # Format result using pipeline method
        result = geo_client.format_parcel_result(property_id, address, parcel_data)

        # Add coordinates from location data
        if location_data:
            result['coordinates'] = {
                'longitude': location_data.get('longitude'),
                'latitude': location_data.get('latitude')
            }

        # Add locality information if available
        if property_info:
            result['locality_info'] = {
                'locality_id': property_info.get('locality_id'),
                'council_area_id': property_info.get('council_area_id'),
                'postcode_id': property_info.get('postcode_id'),
                'state_id': property_info.get('state_id'),
                'street_id': property_info.get('street_id'),
                'country_id': property_info.get('country_id'),
                'is_unit': property_info.get('is_unit'),
                'is_active_property': property_info.get('is_active_property'),
                'is_body_corporate': property_info.get('is_body_corporate')
            }

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

        if 'coordinates' in result:
            coords = result['coordinates']
            if coords.get('longitude') and coords.get('latitude'):
                print(f"Coordinates: ({coords['longitude']}, {coords['latitude']})", file=sys.stderr)

        if 'locality_info' in result:
            locality = result['locality_info']
            if locality.get('locality_id'):
                print(f"Locality ID: {locality['locality_id']}", file=sys.stderr)
            if locality.get('council_area_id'):
                print(f"Council Area ID: {locality['council_area_id']}", file=sys.stderr)
            if locality.get('postcode_id'):
                print(f"Postcode ID: {locality['postcode_id']}", file=sys.stderr)
            if locality.get('state_id'):
                print(f"State ID: {locality['state_id']}", file=sys.stderr)
            if locality.get('is_unit'):
                print(f"Is Unit: {locality['is_unit']}", file=sys.stderr)

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
