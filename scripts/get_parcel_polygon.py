#!/usr/bin/env python3
"""
Simple script to get parcel polygon geometry for an address with elevation and slope analysis.

Usage:
    python3 scripts/get_parcel_polygon.py --address "123 Main St, Sydney NSW"
    python3 scripts/get_parcel_polygon.py --property-id 1778890
    python3 scripts/get_parcel_polygon.py --address "3 Nymboida Street, South Coogee, NSW, 2034" --output data/outputs/parcel.json --pretty
    python3 scripts/get_parcel_polygon.py --address "16 Fowler Crescent, South Coogee, NSW, 2034" --output data/outputs/parcel.json --pretty
    python3 scripts/get_parcel_polygon.py --address "5 settlers court,vermont south, vic, 3133" --output data/outputs/parcel.json --pretty

    # With elevation and slope analysis
    python3 scripts/get_parcel_polygon.py --address "5 settlers court,vermont south, vic, 3133" --with-elevation --output data/outputs/parcel.json --pretty
"""

import argparse
import json
import sys
import os
import requests
import math
from typing import List, Tuple, Dict, Any, Optional
from geopy.distance import geodesic
from geopy.geocoders import GoogleV3

# Import from utils subdirectory
from utils.property_data_processor import PropertyDataProcessor
from utils.geospatial_api_client import GeospatialAPIClient
from utils.pipeline_utils import ProgressReporter


def web_mercator_to_wgs84(x: float, y: float) -> Tuple[float, float]:
    """
    Convert Web Mercator (EPSG:3857) coordinates to WGS84 lat/lon (EPSG:4326).

    Args:
        x: X coordinate in Web Mercator (easting)
        y: Y coordinate in Web Mercator (northing)

    Returns:
        (latitude, longitude) tuple in WGS84
    """
    # Web Mercator constants
    EARTH_RADIUS = 6378137.0  # meters

    # Convert to longitude
    lon = (x / EARTH_RADIUS) * (180.0 / math.pi)

    # Convert to latitude
    lat = (2.0 * math.atan(math.exp(y / EARTH_RADIUS)) - math.pi / 2.0) * (180.0 / math.pi)

    return (lat, lon)


def get_elevation_for_locations(locations: List[Tuple[float, float]], api_key: str) -> List[Dict[str, Any]]:
    """
    Get elevation data from Google Maps Elevation API for a list of locations.

    Args:
        locations: List of (latitude, longitude) tuples
        api_key: Google Maps API key

    Returns:
        List of elevation data dictionaries with 'lat', 'lon', 'elevation', 'resolution'
    """
    if not locations:
        return []

    # Google Maps API can handle up to 512 locations per request
    # We'll batch in groups of 100 for safety
    batch_size = 100
    all_results = []

    for i in range(0, len(locations), batch_size):
        batch = locations[i:i+batch_size]

        # Format locations as "lat,lng|lat,lng|..."
        locations_str = "|".join([f"{lat},{lon}" for lat, lon in batch])

        url = "https://maps.googleapis.com/maps/api/elevation/json"
        params = {
            "locations": locations_str,
            "key": api_key
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if data.get('status') == 'OK':
                for result in data.get('results', []):
                    all_results.append({
                        "lat": result['location']['lat'],
                        "lon": result['location']['lng'],
                        "elevation_m": result['elevation'],
                        "resolution_m": result.get('resolution', None)
                    })
            else:
                error_msg = data.get('error_message', data.get('status'))
                raise Exception(f"Google Maps API error: {error_msg}")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch elevation data: {str(e)}")

    return all_results


def calculate_slope_between_points(
    point1: Tuple[float, float, float],
    point2: Tuple[float, float, float]
) -> Dict[str, float]:
    """
    Calculate slope between two points with elevation.

    Args:
        point1: (latitude, longitude, elevation) tuple
        point2: (latitude, longitude, elevation) tuple

    Returns:
        Dictionary with slope_degrees, slope_percent, elevation_change_m, horizontal_distance_m
    """
    lat1, lon1, elev1 = point1
    lat2, lon2, elev2 = point2

    # Calculate horizontal distance in meters using geodesic
    horizontal_distance_m = geodesic((lat1, lon1), (lat2, lon2)).meters

    if horizontal_distance_m == 0:
        return {
            "slope_degrees": 0.0,
            "slope_percent": 0.0,
            "elevation_change_m": 0.0,
            "horizontal_distance_m": 0.0
        }

    # Calculate elevation change
    elevation_change_m = abs(elev2 - elev1)

    # Calculate slope
    slope_ratio = elevation_change_m / horizontal_distance_m
    slope_degrees = math.degrees(math.atan(slope_ratio))
    slope_percent = slope_ratio * 100

    return {
        "slope_degrees": round(slope_degrees, 2),
        "slope_percent": round(slope_percent, 2),
        "elevation_change_m": round(elevation_change_m, 2),
        "horizontal_distance_m": round(horizontal_distance_m, 2)
    }


def calculate_bearing(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """
    Calculate the bearing between two points.

    Args:
        point1: (latitude, longitude) tuple
        point2: (latitude, longitude) tuple

    Returns:
        Bearing in degrees from north (0-360)
    """
    lat1, lon1 = point1
    lat2, lon2 = point2

    # Convert to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    lon_diff_rad = math.radians(lon2 - lon1)

    # Calculate bearing
    x = math.sin(lon_diff_rad) * math.cos(lat2_rad)
    y = math.cos(lat1_rad) * math.sin(lat2_rad) - \
        math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(lon_diff_rad)

    bearing_rad = math.atan2(x, y)
    bearing_deg = math.degrees(bearing_rad)

    # Normalize to 0-360
    bearing_deg = (bearing_deg + 360) % 360

    return round(bearing_deg, 2)


def bearing_to_cardinal(bearing: float) -> str:
    """
    Convert bearing to cardinal direction.

    Args:
        bearing: Bearing in degrees (0-360)

    Returns:
        Cardinal direction (N, NE, E, SE, S, SW, W, NW)
    """
    directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    index = round(bearing / 45) % 8
    return directions[index]


def geocode_street(address: str, api_key: str) -> Optional[Tuple[float, float]]:
    """
    Geocode the street/road from the address.

    Args:
        address: Property address
        api_key: Google Maps API key

    Returns:
        (latitude, longitude) of the street, or None if not found
    """
    try:
        # Extract street name from address (before first comma)
        parts = address.split(',')
        if len(parts) >= 2:
            # Try to get just the street name (remove house number)
            street_parts = parts[0].strip().split()
            if len(street_parts) > 1 and street_parts[0].isdigit():
                street_name = ' '.join(street_parts[1:])
            else:
                street_name = parts[0].strip()

            # Combine with suburb/city for better geocoding
            street_query = f"{street_name}, {parts[1].strip()}"
            if len(parts) > 2:
                street_query += f", {parts[2].strip()}"

            geolocator = GoogleV3(api_key=api_key)
            location = geolocator.geocode(street_query)

            if location:
                return (location.latitude, location.longitude)

    except Exception as e:
        print(f"Warning: Could not geocode street: {e}", file=sys.stderr)

    return None


def find_street_frontage_and_orientation(
    geometry: Dict[str, Any],
    address: str,
    api_key: str
) -> Dict[str, Any]:
    """
    Find the street frontage edge and calculate its orientation.

    Args:
        geometry: Parcel geometry with 'rings' containing vertices
        address: Property address
        api_key: Google Maps API key

    Returns:
        Dictionary with frontage analysis
    """
    print("\nAnalyzing street frontage and orientation...", file=sys.stderr)

    if not geometry or 'rings' not in geometry or not geometry['rings']:
        raise ValueError("Invalid geometry: no rings found")

    # Get vertices and convert from Web Mercator to WGS84
    outer_ring = geometry['rings'][0]
    vertices = [web_mercator_to_wgs84(x, y) for x, y in outer_ring]

    # Try to geocode the street
    street_location = geocode_street(address, api_key)

    if not street_location:
        print("  Warning: Could not geocode street, using longest edge as frontage", file=sys.stderr)
        # Fallback: use longest edge as street frontage
        max_length = 0
        frontage_edge = None
        frontage_index = 0

        for i in range(len(vertices)):
            j = (i + 1) % len(vertices)
            length = geodesic(vertices[i], vertices[j]).meters
            if length > max_length:
                max_length = length
                frontage_edge = (i, j)
                frontage_index = i
    else:
        print(f"  Street location: {street_location[0]:.6f}, {street_location[1]:.6f}", file=sys.stderr)

        # Find edge closest to street location
        min_distance = float('inf')
        frontage_edge = None
        frontage_index = 0

        for i in range(len(vertices)):
            j = (i + 1) % len(vertices)

            # Calculate midpoint of edge
            mid_lat = (vertices[i][0] + vertices[j][0]) / 2
            mid_lon = (vertices[i][1] + vertices[j][1]) / 2

            # Distance from edge midpoint to street
            distance = geodesic((mid_lat, mid_lon), street_location).meters

            if distance < min_distance:
                min_distance = distance
                frontage_edge = (i, j)
                frontage_index = i

        print(f"  Frontage edge distance to street: {min_distance:.1f}m", file=sys.stderr)

    # Calculate properties of frontage edge
    i, j = frontage_edge
    point1 = vertices[i]
    point2 = vertices[j]

    # Edge length
    edge_length = geodesic(point1, point2).meters

    # Calculate bearing of the edge
    bearing = calculate_bearing(point1, point2)
    cardinal = bearing_to_cardinal(bearing)

    # Calculate perpendicular bearing (property faces this direction)
    property_faces_bearing = (bearing + 90) % 360
    property_faces_cardinal = bearing_to_cardinal(property_faces_bearing)

    print(f"  ✓ Street frontage: {edge_length:.1f}m", file=sys.stderr)
    print(f"  ✓ Frontage orientation: {bearing:.1f}° ({cardinal})", file=sys.stderr)
    print(f"  ✓ Property faces: {property_faces_bearing:.1f}° ({property_faces_cardinal})", file=sys.stderr)

    return {
        "frontage_edge": {
            "vertex_1_index": i,
            "vertex_2_index": j,
            "vertex_1": {"lat": point1[0], "lon": point1[1]},
            "vertex_2": {"lat": point2[0], "lon": point2[1]},
            "length_m": round(edge_length, 2)
        },
        "frontage_orientation": {
            "bearing_degrees": bearing,
            "cardinal_direction": cardinal,
            "description": f"Frontage runs {cardinal}"
        },
        "property_orientation": {
            "bearing_degrees": property_faces_bearing,
            "cardinal_direction": property_faces_cardinal,
            "description": f"Property faces {property_faces_cardinal}"
        },
        "street_location": {
            "lat": street_location[0] if street_location else None,
            "lon": street_location[1] if street_location else None,
            "method": "geocoded" if street_location else "longest_edge_fallback"
        }
    }


def analyze_parcel_elevation_and_slope(
    geometry: Dict[str, Any],
    center_lat: float,
    center_lon: float,
    api_key: str
) -> Dict[str, Any]:
    """
    Analyze elevation and slope for a parcel geometry.

    Args:
        geometry: Parcel geometry with 'rings' containing vertices (in Web Mercator)
        center_lat: Center latitude of the property (in WGS84)
        center_lon: Center longitude of the property (in WGS84)
        api_key: Google Maps API key

    Returns:
        Dictionary with elevation analysis results
    """
    print("Fetching elevation data from Google Maps API...", file=sys.stderr)

    # Extract vertices from geometry
    if not geometry or 'rings' not in geometry or not geometry['rings']:
        raise ValueError("Invalid geometry: no rings found")

    # Get the outer ring (first ring) and convert from Web Mercator to WGS84
    outer_ring = geometry['rings'][0]
    vertices = [web_mercator_to_wgs84(x, y) for x, y in outer_ring]

    print(f"Analyzing {len(vertices)} vertices...", file=sys.stderr)

    # Prepare all locations (center + vertices) - all in WGS84
    all_locations = [(center_lat, center_lon)] + vertices

    # Get elevation data for all locations
    elevation_data = get_elevation_for_locations(all_locations, api_key)

    if not elevation_data:
        raise ValueError("No elevation data returned from API")

    # Separate center and vertex elevations
    center_elevation = elevation_data[0]
    vertex_elevations = elevation_data[1:]

    # Calculate statistics for vertices
    vertex_elev_values = [v['elevation_m'] for v in vertex_elevations]
    min_elevation = min(vertex_elev_values)
    max_elevation = max(vertex_elev_values)
    avg_elevation = sum(vertex_elev_values) / len(vertex_elev_values)
    elevation_range = max_elevation - min_elevation

    print(f"Calculating slopes between vertices...", file=sys.stderr)

    # Calculate slopes between adjacent vertices
    slopes = []
    max_slope = {"slope_degrees": 0.0, "slope_percent": 0.0}
    max_slope_vertices = None

    for i in range(len(vertices)):
        j = (i + 1) % len(vertices)  # Wrap around to first vertex

        point1 = (vertices[i][0], vertices[i][1], vertex_elevations[i]['elevation_m'])
        point2 = (vertices[j][0], vertices[j][1], vertex_elevations[j]['elevation_m'])

        slope = calculate_slope_between_points(point1, point2)
        slopes.append(slope)

        # Track maximum slope
        if slope['slope_degrees'] > max_slope['slope_degrees']:
            max_slope = slope
            max_slope_vertices = {
                "vertex_1": {"index": i, "lat": vertices[i][0], "lon": vertices[i][1], "elevation_m": point1[2]},
                "vertex_2": {"index": j, "lat": vertices[j][0], "lon": vertices[j][1], "elevation_m": point2[2]}
            }

    # Calculate average slope
    avg_slope_degrees = sum(s['slope_degrees'] for s in slopes) / len(slopes)
    avg_slope_percent = sum(s['slope_percent'] for s in slopes) / len(slopes)

    print(f"✓ Elevation analysis complete", file=sys.stderr)
    print(f"  Max slope: {max_slope['slope_degrees']}° ({max_slope['slope_percent']}%)", file=sys.stderr)
    print(f"  Elevation range: {elevation_range:.2f}m", file=sys.stderr)

    return {
        "center_elevation": center_elevation,
        "vertex_elevations": vertex_elevations,
        "elevation_statistics": {
            "min_elevation_m": round(min_elevation, 2),
            "max_elevation_m": round(max_elevation, 2),
            "avg_elevation_m": round(avg_elevation, 2),
            "elevation_range_m": round(elevation_range, 2)
        },
        "slope_analysis": {
            "max_slope": max_slope,
            "max_slope_vertices": max_slope_vertices,
            "avg_slope_degrees": round(avg_slope_degrees, 2),
            "avg_slope_percent": round(avg_slope_percent, 2),
            "total_slopes_calculated": len(slopes)
        },
        "all_slopes": slopes
    }


def main():
    parser = argparse.ArgumentParser(
        description='Get parcel polygon geometry for an address or property ID with optional elevation and slope analysis'
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

    parser.add_argument(
        '--with-elevation',
        action='store_true',
        help='Include elevation and slope analysis using Google Maps API'
    )

    parser.add_argument(
        '--google-api-key',
        type=str,
        help='Google Maps API key (optional, reads from GOOGLE_MAPS_API_KEY env var if not provided)'
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

        # Add elevation and slope analysis if requested
        if args.with_elevation:
            # Get Google Maps API key - check multiple environment variables
            google_api_key = args.google_api_key or os.environ.get('GOOGLE_MAPS_API_KEY') or os.environ.get('GOOGLE_API_KEY')

            if not google_api_key:
                raise ValueError(
                    "Google Maps API key required for elevation analysis. "
                    "Provide via --google-api-key or set GOOGLE_MAPS_API_KEY or GOOGLE_API_KEY environment variable."
                )

            # Get property location (center point) in WGS84
            # Try to get from property details first (these are already in WGS84 lat/lon)
            try:
                property_details = property_processor.get_property_details(property_id)
                location = property_details.get('location', {})
                center_lat_wgs84 = location.get('latitude')
                center_lon_wgs84 = location.get('longitude')
            except:
                center_lat_wgs84 = None
                center_lon_wgs84 = None

            # If not available, calculate centroid from geometry and convert from Web Mercator to WGS84
            if not center_lat_wgs84 or not center_lon_wgs84:
                if result.get('geometry') and result['geometry'].get('rings'):
                    ring = result['geometry']['rings'][0]
                    xs = [coord[0] for coord in ring]  # Web Mercator X (easting)
                    ys = [coord[1] for coord in ring]  # Web Mercator Y (northing)
                    center_x = sum(xs) / len(xs)
                    center_y = sum(ys) / len(ys)
                    # Convert from Web Mercator to WGS84
                    center_lat_wgs84, center_lon_wgs84 = web_mercator_to_wgs84(center_x, center_y)
                else:
                    raise ValueError("Cannot determine property center location")

            print(f"\nProperty center (WGS84): {center_lat_wgs84:.6f}, {center_lon_wgs84:.6f}", file=sys.stderr)

            # Perform elevation and slope analysis
            elevation_analysis = analyze_parcel_elevation_and_slope(
                result['geometry'],
                center_lat_wgs84,
                center_lon_wgs84,
                google_api_key
            )

            # Add to result
            result['elevation_analysis'] = elevation_analysis

            # Perform street frontage and orientation analysis
            orientation_analysis = find_street_frontage_and_orientation(
                result['geometry'],
                address,
                google_api_key
            )

            # Add to result
            result['orientation_analysis'] = orientation_analysis

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

        # Print elevation summary if available
        if 'elevation_analysis' in result:
            elev_stats = result['elevation_analysis']['elevation_statistics']
            slope_analysis = result['elevation_analysis']['slope_analysis']

            print(f"\n=== Elevation & Slope Analysis ===", file=sys.stderr)
            print(f"Elevation Range: {elev_stats['min_elevation_m']:.2f}m - {elev_stats['max_elevation_m']:.2f}m", file=sys.stderr)
            print(f"Average Elevation: {elev_stats['avg_elevation_m']:.2f}m", file=sys.stderr)
            print(f"Elevation Change: {elev_stats['elevation_range_m']:.2f}m", file=sys.stderr)
            print(f"\nMaximum Slope: {slope_analysis['max_slope']['slope_degrees']:.2f}° ({slope_analysis['max_slope']['slope_percent']:.2f}%)", file=sys.stderr)
            print(f"Average Slope: {slope_analysis['avg_slope_degrees']:.2f}° ({slope_analysis['avg_slope_percent']:.2f}%)", file=sys.stderr)
            print(f"Slopes Calculated: {slope_analysis['total_slopes_calculated']}", file=sys.stderr)

        # Print orientation summary if available
        if 'orientation_analysis' in result:
            orient = result['orientation_analysis']
            frontage = orient['frontage_edge']
            frontage_orient = orient['frontage_orientation']
            property_orient = orient['property_orientation']

            print(f"\n=== Orientation Analysis ===", file=sys.stderr)
            print(f"Street Frontage: {frontage['length_m']:.1f}m", file=sys.stderr)
            print(f"Frontage Runs: {frontage_orient['cardinal_direction']} ({frontage_orient['bearing_degrees']:.1f}°)", file=sys.stderr)
            print(f"Property Faces: {property_orient['cardinal_direction']} ({property_orient['bearing_degrees']:.1f}°)", file=sys.stderr)
            print(f"Detection Method: {orient['street_location']['method']}", file=sys.stderr)

        return 0

    except Exception as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
