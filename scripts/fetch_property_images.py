#!/usr/bin/env python3
"""
Fetch Property Images and Generate JSON Report

Retrieves property images from CoreLogic API and generates a comprehensive
JSON report with metadata, summary statistics, and image URLs.

Usage:
    # Using property ID
    python3 scripts/fetch_property_images.py --property-id 13683380

    # With custom output directory
    python3 scripts/fetch_property_images.py --property-id 13683380 --output-dir data/images

    # Specify property address for metadata
    python3 scripts/fetch_property_images.py --property-id 13683380 --address "5 Settlers Court, Vermont South VIC 3133"

Output:
    Creates JSON file: {property_id}_property_images.json
    Contains:
    - Metadata (property ID, address, timestamp)
    - Summary statistics (total images, types, sizes)
    - Default image details with all size URLs
    - Secondary images list
    - Floor plan images list
    - Raw API response

Example Report Structure:
    {
      "metadata": {
        "property_id": 13683380,
        "property_address": "5 Settlers Court, Vermont South VIC 3133",
        "extraction_timestamp": "2025-11-10T15:30:00",
        "status": "success"
      },
      "summary": {
        "total_images": 15,
        "has_default_image": true,
        "secondary_images_count": 12,
        "floor_plan_images_count": 2,
        "available_sizes": ["large_768x512", "medium_470x313", "original", "thumbnail_320x215"],
        "oldest_scan_date": "2021-06-03",
        "newest_scan_date": "2023-08-15"
      },
      "default_image": {
        "digital_asset_type": "Image",
        "scan_date": "2021-06-03",
        "urls": {
          "original": {"url": "https://...", "size": "0x0 (original)"},
          "large": {"url": "https://...", "size": "768x512"},
          "medium": {"url": "https://...", "size": "470x313"},
          "thumbnail": {"url": "https://...", "size": "320x215"}
        }
      },
      "secondary_images": [...],
      "floor_plan_images": [...]
    }

Requirements:
    - CORELOGIC_CLIENT_ID environment variable
    - CORELOGIC_CLIENT_SECRET environment variable

Author: Property Images Report Generator
Date: 2025-11-10
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.property_images_client import PropertyImagesClient


def save_report(report: Dict[str, Any], output_path: Path) -> None:
    """
    Save report to JSON file.

    Args:
        report: Report dictionary
        output_path: Path to save JSON file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"✅ Report saved: {output_path}")


def print_summary(report: Dict[str, Any]) -> None:
    """
    Print report summary to console.

    Args:
        report: Report dictionary
    """
    metadata = report.get('metadata', {})
    summary = report.get('summary', {})

    print("\n" + "=" * 70)
    print("📸 PROPERTY IMAGES REPORT SUMMARY")
    print("=" * 70)

    # Property info
    print(f"\n🏠 Property: {metadata.get('property_id')}")
    if metadata.get('property_address'):
        print(f"   Address: {metadata.get('property_address')}")
    print(f"   Status: {metadata.get('status', 'unknown').upper()}")

    # Handle errors
    if metadata.get('status') == 'error':
        print(f"\n❌ Error: {report.get('error')}")
        if report.get('message'):
            print(f"   Message: {report.get('message')}")
        return

    # Image statistics
    print(f"\n📊 Image Statistics:")
    print(f"   Total Images: {summary.get('total_images', 0)}")
    print(f"   Default Image: {'✓ Yes' if summary.get('has_default_image') else '✗ No'}")
    print(f"   Secondary Images: {summary.get('secondary_images_count', 0)}")
    print(f"   Floor Plans: {summary.get('floor_plan_images_count', 0)}")

    # Available sizes
    if summary.get('available_sizes'):
        print(f"\n📐 Available Sizes:")
        for size in summary.get('available_sizes', []):
            print(f"   • {size}")

    # Temporal coverage
    if summary.get('oldest_scan_date'):
        print(f"\n📅 Temporal Coverage:")
        print(f"   Oldest: {summary.get('oldest_scan_date')}")
        print(f"   Newest: {summary.get('newest_scan_date')}")
        print(f"   Unique Dates: {summary.get('unique_scan_dates', 0)}")
        if summary.get('temporal_span_years') is not None:
            span_years = summary.get('temporal_span_years')
            span_days = summary.get('temporal_span_days', 0)
            print(f"   Time Span: {span_years} years ({span_days} days)")

    # Images by year
    if summary.get('images_by_year'):
        print(f"\n📊 Distribution by Year:")
        for year, count in summary.get('images_by_year', {}).items():
            print(f"   {year}: {count} images")

    # Images by date (top dates)
    if summary.get('images_by_date'):
        images_by_date = summary.get('images_by_date', {})
        print(f"\n📆 Distribution by Date:")
        # Show top 5 dates with most images
        sorted_dates = sorted(images_by_date.items(), key=lambda x: x[1]['total'], reverse=True)[:5]
        for date, counts in sorted_dates:
            breakdown = []
            if counts['default'] > 0:
                breakdown.append(f"{counts['default']} default")
            if counts['secondary'] > 0:
                breakdown.append(f"{counts['secondary']} secondary")
            if counts['floor_plan'] > 0:
                breakdown.append(f"{counts['floor_plan']} floor_plan")
            breakdown_str = ", ".join(breakdown)
            print(f"   {date}: {counts['total']} images ({breakdown_str})")
        if len(images_by_date) > 5:
            print(f"   ... and {len(images_by_date) - 5} more dates")

    # Distribution by type (enhanced)
    if summary.get('distribution_by_type'):
        print(f"\n🖼️  Distribution by Image Type:")
        type_dist = summary.get('distribution_by_type', {})
        for img_type, stats in type_dist.items():
            if stats['count'] > 0:
                print(f"   {img_type.title()}:")
                print(f"      Count: {stats['count']}")
                print(f"      Unique Dates: {stats['unique_dates']}")
                if stats['oldest_date']:
                    print(f"      Date Range: {stats['oldest_date']} to {stats['newest_date']}")

    # Digital asset type totals
    if summary.get('digital_asset_type_totals'):
        print(f"\n📷 Digital Asset Types:")
        for asset_type, count in summary.get('digital_asset_type_totals', {}).items():
            print(f"   {asset_type}: {count} images")

    # Digital asset type by year
    if summary.get('digital_asset_type_by_year'):
        print(f"\n📅 Digital Asset Type by Year:")
        asset_by_year = summary.get('digital_asset_type_by_year', {})
        for year, asset_types in asset_by_year.items():
            asset_breakdown = ", ".join([f"{asset_type}: {count}" for asset_type, count in asset_types.items()])
            print(f"   {year}: {asset_breakdown}")

    print("\n" + "=" * 70)


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description='Fetch property images from CoreLogic API and generate JSON report',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python scripts/fetch_property_images.py --property-id 13683380

  # With address metadata
  python scripts/fetch_property_images.py --property-id 13683380 --address "5 Settlers Court, Vermont South VIC 3133"

  # Custom output directory
  python scripts/fetch_property_images.py --property-id 13683380 --output-dir data/images

Environment Variables Required:
  CORELOGIC_CLIENT_ID     - CoreLogic API client ID
  CORELOGIC_CLIENT_SECRET - CoreLogic API client secret
        """
    )

    parser.add_argument(
        '--property-id',
        type=int,
        required=True,
        help='CoreLogic property ID'
    )

    parser.add_argument(
        '--address',
        type=str,
        help='Property address (optional, for metadata)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/property_reports',
        help='Output directory for JSON report (default: data/property_reports)'
    )

    parser.add_argument(
        '--base-url',
        type=str,
        default='https://api-uat.corelogic.asia',
        help='CoreLogic API base URL (default: UAT)'
    )

    args = parser.parse_args()

    try:
        print(f"\n🔄 Fetching images for property {args.property_id}...")

        # Initialize client
        client = PropertyImagesClient.from_env()
        if args.base_url:
            client.base_url = args.base_url
            client.property_details_base_url = f"{args.base_url}/property-details/au"

        # Generate report
        report = client.generate_images_report(
            property_id=args.property_id,
            property_address=args.address
        )

        # Save report
        output_dir = Path(args.output_dir)
        output_file = output_dir / f"{args.property_id}_property_images.json"
        save_report(report, output_file)

        # Print summary
        print_summary(report)

        # Success
        print(f"\n📁 Full report: {output_file}\n")
        sys.exit(0)

    except ValueError as e:
        print(f"❌ Configuration Error: {e}", file=sys.stderr)
        print("   Make sure CORELOGIC_CLIENT_ID and CORELOGIC_CLIENT_SECRET are set", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
