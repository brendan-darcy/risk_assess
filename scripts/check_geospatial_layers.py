#!/usr/bin/env python3
"""
Check Available Geospatial Layers for an Address

This script checks which CoreLogic geospatial layers are available for a given address
and returns a comprehensive checklist of data availability.

Usage:
    # Check all layers for an address
    python3 scripts/check_geospatial_layers.py --address "5 Settlers Court, Vermont South VIC 3133"

    # Save results to JSON file
    python3 scripts/check_geospatial_layers.py --address "16 Fowler Crescent, South Coogee, NSW, 2034" --output data/outputs/layers.json

    # Pretty print JSON output
    python3 scripts/check_geospatial_layers.py --address "3 Nymboida Street, South Coogee, NSW, 2034" --pretty

    # Check specific state (for state-specific layers)
    python3 scripts/check_geospatial_layers.py --address "123 Main St, Melbourne VIC" --state vic

Available Layers Checked:
    - Property Parcel Geometry
    - Property Boundaries
    - Hazard Overlays (Bushfire, Flood, Heritage)
    - Easements
    - Infrastructure (Streets, Railway, Electric Transmission, etc.)

Requirements:
    - CORELOGIC_CLIENT_ID and CORELOGIC_CLIENT_SECRET in environment

Author: Brendan Darcy
Date: 2025-11-09
"""

import argparse
import json
import sys
from typing import Dict, List, Any, Optional

# Import from utils subdirectory
from utils.property_data_processor import PropertyDataProcessor
from utils.geospatial_api_client import GeospatialAPIClient
from utils.pipeline_utils import ProgressReporter


class GeospatialLayerChecker:
    """Check availability of geospatial layers for a property"""

    # Define all layer types to check
    LAYER_DEFINITIONS = {
        'core_property': {
            'name': 'Property Parcel Geometry',
            'description': 'Basic property parcel polygon and attributes',
            'category': 'Property'
        },
        'property_boundaries': {
            'name': 'Property Boundaries',
            'description': 'Detailed property boundary data',
            'category': 'Property'
        },
        'hazard_bushfire': {
            'name': 'Bushfire Hazard',
            'description': 'Bushfire risk and hazard zones',
            'category': 'Hazards'
        },
        'hazard_flood': {
            'name': 'Flood Hazard',
            'description': 'Flood risk and planning zones',
            'category': 'Hazards'
        },
        'hazard_heritage': {
            'name': 'Heritage Overlay',
            'description': 'Heritage and conservation zones',
            'category': 'Hazards'
        },
        'easements': {
            'name': 'Easements',
            'description': 'Property easements and rights of way',
            'category': 'Legal'
        },
        'infrastructure_streets': {
            'name': 'Streets',
            'description': 'Road and street network',
            'category': 'Infrastructure'
        },
        'infrastructure_railway': {
            'name': 'Railway',
            'description': 'Railway lines and corridors',
            'category': 'Infrastructure'
        },
        'infrastructure_railway_stations': {
            'name': 'Railway Stations',
            'description': 'Railway station locations',
            'category': 'Infrastructure'
        },
        'infrastructure_ferry': {
            'name': 'Ferry',
            'description': 'Ferry routes and terminals',
            'category': 'Infrastructure'
        },
        'infrastructure_transmission': {
            'name': 'Electric Transmission Lines',
            'description': 'High voltage transmission infrastructure',
            'category': 'Infrastructure'
        }
    }

    def __init__(self, geo_client: GeospatialAPIClient, property_processor: PropertyDataProcessor):
        """
        Initialize layer checker.

        Args:
            geo_client: Authenticated geospatial API client
            property_processor: Property data processor for address resolution
        """
        self.geo_client = geo_client
        self.property_processor = property_processor

    def get_property_bbox(self, property_id: str) -> Optional[str]:
        """
        Get bounding box for a property.

        Args:
            property_id: Property identifier

        Returns:
            Bounding box string in format 'xmin,ymin,xmax,ymax' or None if not available
        """
        try:
            # Get property data to determine bbox
            response = self.geo_client.get_property_data(property_id)

            if response.status_code != 200:
                return None

            data = response.json()

            if 'features' not in data or not data['features']:
                return None

            feature = data['features'][0]
            geometry = feature.get('geometry', {})

            if 'rings' in geometry and geometry['rings']:
                # Calculate bbox from polygon rings
                all_coords = []
                for ring in geometry['rings']:
                    all_coords.extend(ring)

                if all_coords:
                    xs = [coord[0] for coord in all_coords]
                    ys = [coord[1] for coord in all_coords]

                    # Add 5km buffer for queries (search radius around property)
                    buffer = 5000  # meters
                    xmin = min(xs) - buffer
                    ymin = min(ys) - buffer
                    xmax = max(xs) + buffer
                    ymax = max(ys) + buffer

                    return f"{xmin},{ymin},{xmax},{ymax}"

        except Exception as e:
            print(f"Warning: Could not determine property bbox: {e}", file=sys.stderr)

        return None

    def check_layer(self, layer_key: str, property_id: str, bbox: Optional[str], state: str) -> Dict[str, Any]:
        """
        Check if a specific layer has data available.

        Args:
            layer_key: Layer identifier key
            property_id: Property identifier
            bbox: Property bounding box
            state: State code (lowercase)

        Returns:
            Dictionary with layer status information
        """
        layer_def = self.LAYER_DEFINITIONS[layer_key]

        result = {
            'layer_key': layer_key,
            'name': layer_def['name'],
            'description': layer_def['description'],
            'category': layer_def['category'],
            'available': False,
            'status': 'unknown',
            'message': '',
            'feature_count': 0,
            'error': None
        }

        try:
            if layer_key == 'core_property':
                # Check parcel polygon
                data = self.geo_client.get_parcel_polygon(property_id)
                if data and 'features' in data and data['features']:
                    result['available'] = True
                    result['status'] = 'success'
                    result['feature_count'] = len(data['features'])
                    result['message'] = 'Property parcel geometry available'
                else:
                    result['status'] = 'no_data'
                    result['message'] = 'No parcel geometry found'

            elif layer_key == 'property_boundaries':
                if not bbox:
                    result['status'] = 'no_bbox'
                    result['message'] = 'Could not determine property location'
                else:
                    response = self.geo_client.get_property_boundaries(bbox, property_id)
                    if response.status_code == 200:
                        result['available'] = True
                        result['status'] = 'success'
                        result['message'] = 'Property boundary data available'
                    else:
                        result['status'] = 'error'
                        result['message'] = f'API returned status {response.status_code}'

            elif layer_key.startswith('hazard_'):
                hazard_type = layer_key.replace('hazard_', '')
                if not bbox:
                    result['status'] = 'no_bbox'
                    result['message'] = 'Could not determine property location'
                else:
                    # Try to query features first (more accurate)
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
                            if 'features' in data and data['features']:
                                result['available'] = True
                                result['status'] = 'success'
                                result['feature_count'] = len(data['features'])
                                result['message'] = f'{len(data["features"])} {hazard_type} feature(s) found'
                            else:
                                result['status'] = 'no_data'
                                result['message'] = f'No {hazard_type} hazard data in area'
                        else:
                            # Fallback to image check
                            raise Exception("Feature query returned non-200 status")

                    except Exception:
                        # Fallback to image-based check for raster/overlay layers
                        response = self.geo_client.get_hazard_data(bbox, hazard_type)
                        if response.status_code == 200 and len(response.content) > 1000:
                            result['available'] = True
                            result['status'] = 'success'
                            result['message'] = f'{hazard_type.title()} hazard overlay available'
                        else:
                            result['status'] = 'no_data'
                            result['message'] = f'No {hazard_type} hazard data in area'

            elif layer_key == 'easements':
                if not bbox:
                    result['status'] = 'no_bbox'
                    result['message'] = 'Could not determine property location'
                else:
                    response = self.geo_client.get_easement_data(bbox, state)
                    if response.status_code == 200:
                        data = response.json()
                        if 'features' in data and data['features']:
                            result['available'] = True
                            result['status'] = 'success'
                            result['feature_count'] = len(data['features'])
                            result['message'] = f'{len(data["features"])} easement(s) found'
                        else:
                            result['status'] = 'no_data'
                            result['message'] = 'No easements found in area'
                    else:
                        result['status'] = 'error'
                        result['message'] = f'API returned status {response.status_code}'

            elif layer_key.startswith('infrastructure_'):
                infra_type = layer_key.replace('infrastructure_', '')

                # Map to API infrastructure type names
                infra_type_map = {
                    'streets': 'streets',
                    'railway': 'railway',
                    'railway_stations': 'railwayStations',
                    'ferry': 'ferry',
                    'transmission': 'electricTransmissionLines'
                }

                api_infra_type = infra_type_map.get(infra_type, infra_type)

                # Query actual features instead of checking image size
                try:
                    response = self.geo_client.query_infrastructure_features(
                        property_id, api_infra_type, state
                    )

                    if response.status_code == 200:
                        data = response.json()
                        if 'features' in data and data['features']:
                            result['available'] = True
                            result['status'] = 'success'
                            result['feature_count'] = len(data['features'])
                            result['message'] = f'{len(data["features"])} {layer_def["name"].lower()} found'
                        else:
                            result['status'] = 'no_data'
                            result['message'] = f'No {layer_def["name"].lower()} in area'
                    else:
                        # Non-200 status (like 404) - trigger fallback to bbox check
                        raise Exception(f'Feature query returned status {response.status_code}')
                except Exception as infra_error:
                    # Fallback to image-based check if feature query fails
                    if bbox:
                        response = self.geo_client.get_infrastructure_data(bbox, api_infra_type, state)

                        if response.status_code == 200:
                            # Use 500 byte threshold to detect actual infrastructure data
                            if len(response.content) > 500:
                                result['available'] = True
                                result['status'] = 'success'
                                result['message'] = f'{layer_def["name"]} data available'
                            else:
                                result['status'] = 'no_data'
                                result['message'] = f'No {layer_def["name"].lower()} in area'
                        else:
                            result['status'] = 'error'
                            result['message'] = f'Image check failed with status {response.status_code}'
                    else:
                        result['status'] = 'error'
                        result['error'] = str(infra_error)
                        result['message'] = f'Error checking infrastructure: {str(infra_error)[:50]}'

        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            result['message'] = f'Error checking layer: {str(e)[:100]}'

        return result

    def detect_state_from_address(self, address: str) -> str:
        """
        Detect Australian state from address string.

        Args:
            address: Property address string

        Returns:
            Lowercase state code (nsw, vic, qld, sa, wa, tas, act, nt)
        """
        address_upper = address.upper()

        # State mappings
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

        # Default to NSW if can't detect
        print("Warning: Could not detect state from address, defaulting to NSW", file=sys.stderr)
        return 'nsw'

    def check_all_layers(self, address: str, state: str = None) -> Dict[str, Any]:
        """
        Check all available layers for an address.

        Args:
            address: Property address
            state: State code (lowercase, optional - will auto-detect if not provided)

        Returns:
            Dictionary with comprehensive layer availability information
        """
        print(f"Resolving address: {address}", file=sys.stderr)

        # Auto-detect state if not provided
        if state is None:
            state = self.detect_state_from_address(address)
            print(f"Auto-detected state: {state.upper()}", file=sys.stderr)
        else:
            print(f"Using provided state: {state.upper()}", file=sys.stderr)

        # Get property ID from address
        property_id = self.property_processor.get_property_id_from_address(address)

        if not property_id:
            return {
                'success': False,
                'error': f'No property found for address: {address}',
                'address': address
            }

        print(f"Found property_id: {property_id}", file=sys.stderr)

        # Get property bounding box
        print("Determining property location...", file=sys.stderr)
        bbox = self.get_property_bbox(property_id)

        if bbox:
            print(f"Property bbox: {bbox}", file=sys.stderr)
        else:
            print("Warning: Could not determine bbox, some checks may be limited", file=sys.stderr)

        # Check each layer
        print(f"\nChecking {len(self.LAYER_DEFINITIONS)} geospatial layers...", file=sys.stderr)

        layer_results = []
        for layer_key in self.LAYER_DEFINITIONS.keys():
            print(f"  Checking: {self.LAYER_DEFINITIONS[layer_key]['name']}...", file=sys.stderr)
            result = self.check_layer(layer_key, property_id, bbox, state)
            layer_results.append(result)

        # Organize results by category
        by_category = {}
        available_count = 0

        for result in layer_results:
            category = result['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(result)

            if result['available']:
                available_count += 1

        return {
            'success': True,
            'address': address,
            'property_id': property_id,
            'state': state.upper(),
            'bbox': bbox,
            'summary': {
                'total_layers': len(layer_results),
                'available_layers': available_count,
                'unavailable_layers': len(layer_results) - available_count,
                'availability_percentage': round((available_count / len(layer_results)) * 100, 1)
            },
            'layers_by_category': by_category,
            'layers': layer_results
        }


def print_summary(results: Dict[str, Any]):
    """Print human-readable summary of layer availability"""

    if not results['success']:
        print(f"\n❌ Error: {results.get('error', 'Unknown error')}", file=sys.stderr)
        return

    summary = results['summary']

    print("\n" + "=" * 70, file=sys.stderr)
    print("GEOSPATIAL LAYER AVAILABILITY SUMMARY", file=sys.stderr)
    print("=" * 70, file=sys.stderr)

    print(f"\nProperty: {results['address']}", file=sys.stderr)
    print(f"Property ID: {results['property_id']}", file=sys.stderr)
    print(f"State: {results['state']}", file=sys.stderr)

    print(f"\nAvailability: {summary['available_layers']}/{summary['total_layers']} layers " +
          f"({summary['availability_percentage']}%)", file=sys.stderr)

    # Print by category
    for category, layers in results['layers_by_category'].items():
        print(f"\n{category}:", file=sys.stderr)
        for layer in layers:
            status_icon = "✅" if layer['available'] else "❌"
            print(f"  {status_icon} {layer['name']}: {layer['message']}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description='Check available geospatial layers for a property address',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--address',
        required=True,
        type=str,
        help='Property address to check'
    )

    parser.add_argument(
        '--state',
        type=str,
        default=None,
        choices=['nsw', 'vic', 'qld', 'sa', 'wa', 'tas', 'act', 'nt'],
        help='State code for state-specific layers (default: auto-detect from address)'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Output file path for JSON results (optional, defaults to stdout)'
    )

    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty print JSON output'
    )

    args = parser.parse_args()

    try:
        # Initialize processors
        print("Initializing CoreLogic clients...", file=sys.stderr)
        property_reporter = ProgressReporter("Property Lookup")
        property_processor = PropertyDataProcessor(reporter=property_reporter)
        geo_client = GeospatialAPIClient.from_env()

        # Create checker
        checker = GeospatialLayerChecker(geo_client, property_processor)

        # Check all layers (state will be auto-detected if None)
        state = args.state.lower() if args.state else None
        results = checker.check_all_layers(args.address, state)

        # Print human-readable summary to stderr
        print_summary(results)

        # Output JSON results
        indent = 2 if args.pretty else None
        json_output = json.dumps(results, indent=indent)

        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(json_output)
            print(f"\n✅ Results saved to: {args.output}", file=sys.stderr)
        else:
            print("\n" + json_output)

        return 0

    except Exception as e:
        print(f"\n❌ Error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
