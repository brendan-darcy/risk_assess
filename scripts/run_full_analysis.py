#!/usr/bin/env python3
"""
Run Mesh Block Analysis

This script performs end-to-end spatial analysis of Australian mesh blocks in relation
to a property. Optionally includes Google Places impact analysis.

Usage:
    # Direct from address (end-to-end)
    python3 scripts/run_mesh_block_analysis.py --address "5 Settlers Court, Vermont South VIC 3133"

    # With property ID
    python3 scripts/run_mesh_block_analysis.py --property-id 13683380

    # Include Google Places analysis
    python3 scripts/run_mesh_block_analysis.py --address "16 Fowler Crescent, South Coogee, NSW, 2034" --include-places
    python3 scripts/run_mesh_block_analysis.py --address "2 Wolli Ave, Earlwood, NSW, 2206" --include-places
    python3 scripts/run_mesh_block_analysis.py --address "2 Wolli Ave, Earlwood, NSW, 2206" --include-places --buffer 200

    # Custom buffer distance
    python3 scripts/run_mesh_block_analysis.py --address "123 Main St" --buffer 5000


Requirements:
    - data/raw/MB_2021_AUST_GDA2020.shp (Australian mesh block shapefile)
    - CORELOGIC_CLIENT_ID and CORELOGIC_CLIENT_SECRET in environment
    - GOOGLE_API_KEY in environment (if using --include-places)

Outputs:
    - data/outputs/meshblocks_within_*m.geojson
    - data/outputs/meshblocks_within_*m.csv
    - data/outputs/meshblocks_within_*m.shp
    - data/outputs/meshblock_codes_*m.txt
    - data/outputs/meshblocks_map.png

Author: Brendan Darcy
Date: 2025-10-05
"""

import sys
import argparse
from pathlib import Path

# Import from utils subdirectory
from utils.mesh_block_analysis_pipeline import MeshBlockAnalysisPipeline
from utils.spatial_visualization_pipeline import SpatialVisualizationPipeline
from utils.pipeline_utils import ProgressReporter


def main():
    """Run mesh block analysis workflow."""

    parser = argparse.ArgumentParser(
        description='Analyze mesh blocks around a property location',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--address', help='Property address')
    parser.add_argument('--property-id', type=int, help='CoreLogic property ID')
    parser.add_argument('--buffer', type=int, default=2000,
                       help='Buffer distance in meters (default: 2000)')
    parser.add_argument('--output-dir', default='data/outputs',
                       help='Output directory (default: data/outputs)')
    parser.add_argument('--include-places', action='store_true',
                       help='Include Google Places analysis')

    args = parser.parse_args()

    if not args.address and not args.property_id:
        parser.error("Must provide either --address or --property-id")

    print("\n" + "=" * 60)
    print("🗺️  MESH BLOCK ANALYSIS")
    print("=" * 60 + "\n")

    # Configuration
    SHAPEFILE_PATH = "data/raw/MB_2021_AUST_GDA2020.shp"

    # Check shapefile exists
    if not Path(SHAPEFILE_PATH).exists():
        print(f"❌ Error: Shapefile not found at {SHAPEFILE_PATH}")
        print("   Please ensure MB_2021_AUST_GDA2020.shp is in data/raw/")
        sys.exit(1)

    try:
        # Step 1: Run mesh block analysis (handles CoreLogic API calls internally)
        print("📍 Fetching property data from CoreLogic...")
        analysis = MeshBlockAnalysisPipeline(
            shapefile_path=SHAPEFILE_PATH,
            buffer_distance=args.buffer
        )

        results = analysis.run_full_analysis(
            output_dir=args.output_dir,
            address=args.address,
            property_id=args.property_id
        )

        # Print results
        print("\n" + "=" * 60)
        print("📊 ANALYSIS RESULTS")
        print("=" * 60)

        if results['property_meshblock']:
            print("\nProperty Mesh Block:")
            for key, value in results['property_meshblock'].items():
                print(f"  {key}: {value}")

        stats = results['statistics']
        print("\nStatistics:")
        print(f"  Total mesh blocks: {stats['total_meshblocks']}")
        print(f"  Buffer distance: {stats['buffer_distance_m']}m")
        print(f"  Total area: {stats['total_area_sqkm']} sq km")

        # Print distance statistics if available
        if 'non_residential_distances' in stats:
            dist_stats = stats['non_residential_distances']
            print("\nNon-Residential Distance Statistics:")
            print(f"  Count: {dist_stats['count']}")
            print(f"  Minimum distance: {dist_stats['min_distance_m']:.2f}m")
            print(f"  Maximum distance: {dist_stats['max_distance_m']:.2f}m")
            print(f"  Mean distance: {dist_stats['mean_distance_m']:.2f}m")
            print(f"  Median distance: {dist_stats['median_distance_m']:.2f}m")

        # Step 2: Optional Google Places analysis (end-to-end in memory)
        places_json_path = None
        if args.include_places:
            print("\n" + "=" * 60)
            print("🔍 RUNNING GOOGLE PLACES ANALYSIS")
            print("=" * 60)

            try:
                from pipelines.google_api_processor import GooglePlacesPipeline
                from pipelines.pipeline_utils import PipelineConfig

                config = PipelineConfig()
                config.set('output_dir', args.output_dir)
                places_reporter = ProgressReporter("Places Analysis")
                places_pipeline = GooglePlacesPipeline(config, places_reporter)

                # Use address from analysis if available
                address = args.address or f"Property {args.property_id}"
                places_pipeline.run(address)
                places_json_path = f"{args.output_dir}/property_impacts.json"
                print("✅ Google Places analysis complete")
            except ImportError:
                print("⚠️  Google Places pipeline not available")
            except Exception as e:
                print(f"⚠️  Google Places analysis failed: {e}")

        # Step 3: Create visualization
        print("\n" + "=" * 60)
        print("🎨 CREATING VISUALIZATION")
        print("=" * 60)

        if places_json_path is None:
            print("ℹ️  No Google Places data found, creating map without places")

        viz = SpatialVisualizationPipeline()

        # Get data in metric CRS for visualization
        property_metric = analysis.property_gdf.to_crs('EPSG:3577')
        property_buffer = property_metric.buffer(args.buffer)

        # Get property boundary in metric CRS if available
        property_boundary_metric = None
        if analysis.property_boundary_gdf is not None and not analysis.property_boundary_gdf.empty:
            property_boundary_metric = analysis.property_boundary_gdf.to_crs('EPSG:3577')

        # Get non-residential distances
        non_residential_distances = results.get('non_residential_distances')

        map_path = viz.create_complete_visualization(
            mesh_blocks=analysis.nearby_meshblocks,
            property_point=property_metric,
            property_buffer=property_buffer,
            output_path=f"{args.output_dir}/meshblocks_map.png",
            places_json_path=places_json_path,
            title=f"Mesh Blocks within {args.buffer}m of Property\n({stats['total_meshblocks']} mesh blocks found)",
            property_boundary=property_boundary_metric,
            non_residential_distances=non_residential_distances,
            show_distance_lines=True,
            max_distance_lines=5
        )

        # Final summary
        print("\n" + "=" * 60)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 60)
        print("\nOutput files:")
        for format_type, path in results['output_files'].items():
            print(f"  {format_type}: {path}")
        print(f"  map: {map_path}")

    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
