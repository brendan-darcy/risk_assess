#!/usr/bin/env python3
"""
Entry point for Google Places Impact Analysis Pipeline

Usage:
    python3 scripts/run_places_analysis.py --address "5 settlers court, vermont south, vic, 3133"
    python3 scripts/run_places_analysis.py --address "248 Coward St, Mascot NSW 2020, Australia"
Author: Google Places Analysis Pipeline
Date: 2025-10-04
"""

import sys
import argparse
from pathlib import Path

# Add pipelines to path
sys.path.append(str(Path(__file__).parent.parent / 'pipelines'))

from pipeline_utils import PipelineConfig, ProgressReporter, PipelineError
from google_places_pipeline import GooglePlacesPipeline


def main():
    parser = argparse.ArgumentParser(
        description='Google Places Impact Analysis Pipeline - Level-based search with configurable radii',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with level-based radii
  python scripts/run_places_analysis.py --address "5 settlers court, vermont south, vic, 3133"

  # Custom output directory
  python scripts/run_places_analysis.py --address "18 Fowler Crescent, South Coogee NSW 2034" --output-dir data/coogee_analysis

Output:
  Creates 3 JSON files in output directory:
    - search_results_by_level.json   (all places found per level)
    - property_impacts.json          (closest place per category)
    - statistics.json                (summary metrics)

Level Radii:
  - Level 1: 3000m (Major disruptions)
  - Level 2: 600m  (Significant impacts)
  - Level 3: 250m  (Moderate impacts)
  - Level 4: 100m  (All places, no type filter)

Requirements:
  - GOOGLE_API_KEY environment variable must be set
  - Requires: requests, geopy (from requirements.txt)
        """
    )

    parser.add_argument(
        '--address',
        required=True,
        help='Property address to analyze (full address recommended)'
    )

    parser.add_argument(
        '--output-dir',
        default='data/places_analysis',
        help='Output directory for results (default: data/places_analysis)'
    )

    args = parser.parse_args()

    # Initialize configuration
    config = PipelineConfig()
    config.set('output_dir', args.output_dir)

    # Create output directory
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Initialize reporter
    reporter = ProgressReporter("🗺️  GOOGLE PLACES IMPACT ANALYSIS PIPELINE")

    # Run pipeline
    try:
        pipeline = GooglePlacesPipeline(config, reporter)
        results = pipeline.run(args.address)

        print("\n" + "=" * 70)
        reporter.success("✅ Pipeline completed successfully!")
        print("=" * 70)
        print(f"\n📁 Output files:")
        for key, path in results.items():
            print(f"   {key:15s}: {path}")
        print()

    except PipelineError as e:
        reporter.error(f"❌ Pipeline failed: {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        reporter.error("\n❌ Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        reporter.error(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
