#!/usr/bin/env python3
"""
Visualize Photo Locations

This script creates a map visualization showing where photos were taken
relative to a property location, with color-coded markers and distance lines.

Usage:
    # Basic usage with Google Satellite basemap (default)
    python3 scripts/visualize_photo_locations.py \
        --address "32 Way Street, Kingsgrove, NSW 2208" \
        --metadata data/photos/photo_meta_data.txt

    # Custom output location
    python3 scripts/visualize_photo_locations.py \
        --address "32 Way Street, Kingsgrove, NSW 2208" \
        --metadata data/photos/photo_meta_data.txt \
        --output data/outputs/custom_photo_map.png

    # Use different basemap
    python3 scripts/visualize_photo_locations.py \
        --address "32 Way Street, Kingsgrove, NSW 2208" \
        --metadata data/photos/photo_meta_data.txt \
        --basemap-source "Google Hybrid"

    # Disable basemap
    python3 scripts/visualize_photo_locations.py \
        --address "32 Way Street, Kingsgrove, NSW 2208" \
        --metadata data/photos/photo_meta_data.txt \
        --no-basemap

Available basemap sources:
    Google Maps (via Static API):
        - Google Satellite (default): High-resolution satellite imagery
        - Google Hybrid: Satellite imagery with labels and roads
        - Google Roadmap: Standard road map
        - Google Terrain: Terrain map with elevation
    Other providers (via contextily):
        - Esri Satellite: High-quality satellite imagery
        - OpenStreetMap: Free street map
        - CartoDB Positron: Clean, minimal basemap
        - CartoDB Voyager: Colorful detailed street map

Requirements:
    - GOOGLE_API_KEY in environment (for geocoding and Google Maps basemaps)
    - Photo metadata file with GPS coordinates
    - Python packages: pip install geopandas shapely geopy matplotlib requests pillow contextily

Outputs:
    - data/outputs/photo_locations_map.png (or custom path)

Author: Brendan Darcy
Date: 2025-11-03
"""

import sys
import os
import argparse
from pathlib import Path

# Import from utils subdirectory
from utils.photo_location_processor import PhotoLocationProcessor
from utils.photo_visualization_pipeline import PhotoVisualizationPipeline
from utils.google_api_processor import GooglePlacesSearcher
from utils.pipeline_utils import ProgressReporter, PipelineError
import geopandas as gpd
from shapely.geometry import Point


def main():
    """Run photo location visualization workflow."""

    parser = argparse.ArgumentParser(
        description='Visualize photo locations relative to a property',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--address', required=True,
                       help='Property address (will be geocoded)')
    parser.add_argument('--metadata', default='data/photos/photo_meta_data.txt',
                       help='Path to photo metadata file (default: data/photos/photo_meta_data.txt)')
    parser.add_argument('--output', default='data/outputs/photo_locations_map.png',
                       help='Output path for map image (default: data/outputs/photo_locations_map.png)')
    parser.add_argument('--show', action='store_true',
                       help='Display map interactively (in addition to saving)')
    parser.add_argument('--no-distance-lines', action='store_true',
                       help='Do not draw lines from photos to property')
    parser.add_argument('--no-distance-labels', action='store_true',
                       help='Do not show distance values on lines')
    parser.add_argument('--max-labels', type=int, default=10,
                       help='Maximum number of distance labels to show (default: 10)')
    parser.add_argument('--no-basemap', action='store_true',
                       help='Do not add a basemap underneath')
    parser.add_argument('--basemap-source', default='Google Satellite',
                       choices=['Google Satellite', 'Google Hybrid', 'Google Roadmap', 'Google Terrain',
                               'Esri Satellite', 'OpenStreetMap', 'CartoDB Positron', 'CartoDB Voyager'],
                       help='Basemap style (default: Google Satellite)')

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("📸 PHOTO LOCATION VISUALIZATION")
    print("=" * 70 + "\n")

    # Check metadata file exists
    if not Path(args.metadata).exists():
        print(f"❌ Error: Metadata file not found at {args.metadata}")
        sys.exit(1)

    # Check for Google API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY not found in environment")
        print("   Required for geocoding the property address")
        sys.exit(1)

    try:
        # Step 1: Geocode property address
        print("=" * 70)
        print("STEP 1: GEOCODING PROPERTY ADDRESS")
        print("=" * 70)
        print(f"Address: {args.address}\n")

        reporter = ProgressReporter("Geocoding")
        geocoder = GooglePlacesSearcher(api_key, reporter)

        property_coords = geocoder.geocode_address(args.address)
        print(f"✅ Property coordinates: {property_coords[0]:.6f}, {property_coords[1]:.6f}")

        # Create property GeoDataFrame
        property_point_wgs84 = gpd.GeoDataFrame(
            {'name': ['Property']},
            geometry=[Point(property_coords[1], property_coords[0])],  # lon, lat
            crs='EPSG:4326'
        )
        property_point_metric = property_point_wgs84.to_crs('EPSG:3577')

        # Step 2: Process photo metadata
        print("\n" + "=" * 70)
        print("STEP 2: PROCESSING PHOTO METADATA")
        print("=" * 70)
        print(f"Metadata file: {args.metadata}\n")

        processor = PhotoLocationProcessor()
        photos_gdf, category_summary = processor.process_complete(
            metadata_path=args.metadata,
            property_coords=property_coords,  # (lat, lon)
            target_crs='EPSG:3577'
        )

        if len(photos_gdf) == 0:
            print("❌ Error: No photos with valid GPS coordinates found")
            sys.exit(1)

        # Step 3: Create visualization
        print("\n" + "=" * 70)
        print("STEP 3: CREATING VISUALIZATION")
        print("=" * 70)
        print(f"Output: {args.output}\n")

        viz = PhotoVisualizationPipeline(figsize=(16, 12), dpi=200, google_api_key=api_key)

        title = (
            f"Photo Locations: {args.address}\n"
            f"({len(photos_gdf)} photos, {len(category_summary)} categories)"
        )

        result = viz.create_complete_visualization(
            photos_gdf=photos_gdf,
            property_point=property_point_metric,
            output_path=args.output,
            property_address=args.address,
            title=title,
            show=args.show,
            show_distance_lines=not args.no_distance_lines,
            show_distance_labels=not args.no_distance_labels,
            max_distance_labels=args.max_labels,
            add_basemap=not args.no_basemap,
            basemap_source=args.basemap_source,
            export_metadata=True
        )

        # Final summary
        print("\n" + "=" * 70)
        print("✅ VISUALIZATION COMPLETE")
        print("=" * 70)
        print(f"\nOutput files:")
        print(f"  Image: {result['image']}")
        if 'metadata' in result:
            print(f"  Metadata: {result['metadata']}")
        print(f"Total photos: {len(photos_gdf)}")
        print(f"Categories: {len(category_summary)}")

        # Distance summary
        if 'distance_m' in photos_gdf.columns:
            distances = photos_gdf['distance_m']
            print(f"\nDistance Statistics:")
            print(f"  Closest photo: {distances.min():.1f}m")
            print(f"  Furthest photo: {distances.max():.1f}m")
            print(f"  Average distance: {distances.mean():.1f}m")

            # Calculate centroid distance
            from geopy.distance import geodesic
            photos_gdf_wgs84 = photos_gdf.to_crs(epsg=4326)
            centroid = photos_gdf_wgs84.geometry.unary_union.centroid
            centroid_distance = geodesic(
                property_coords,  # (lat, lon)
                (centroid.y, centroid.x)
            ).meters
            print(f"\n  Photo centroid distance: {centroid_distance:.1f}m")

        print("\n" + "=" * 70)

    except PipelineError as e:
        print(f"\n❌ Pipeline Error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during visualization: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
