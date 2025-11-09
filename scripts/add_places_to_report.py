#!/usr/bin/env python3
"""
Add Google Places Impact Analysis to existing comprehensive report.

Usage:
    python3 scripts/add_places_to_report.py \
        --report data/property_reports/6256699_comprehensive_report.json \
        --places data/places_analysis
"""

import json
import argparse
from pathlib import Path


def load_places_data(places_dir: str) -> dict:
    """Load and summarize Google Places analysis data"""
    places_path = Path(places_dir)

    # Load the three JSON files
    statistics_file = places_path / 'statistics.json'
    impacts_file = places_path / 'property_impacts.json'

    if not statistics_file.exists():
        return {'error': 'Statistics file not found'}

    if not impacts_file.exists():
        return {'error': 'Impacts file not found'}

    with open(statistics_file) as f:
        stats = json.load(f)

    with open(impacts_file) as f:
        impacts = json.load(f)

    # Handle different statistics file structures
    if 'summary' in stats:
        # New structure with nested summary
        summary_data = stats['summary']
        dist_dist = stats.get('closest_places_distance_distribution', {})
        # Normalize keys
        distance_distribution = {
            'closest_meters': dist_dist.get('closest_m', 0),
            'furthest_meters': dist_dist.get('furthest_m', 0),
            'median_meters': dist_dist.get('median_m', 0),
            'within_100m': dist_dist.get('within_100m', 0),
            'within_250m': dist_dist.get('within_250m', 0),
            'within_600m': dist_dist.get('within_600m', 0),
            'within_3000m': dist_dist.get('within_3000m', 0)
        }
    else:
        # Old structure with top-level keys
        summary_data = stats
        distance_distribution = stats.get('distance_distribution', {})

    # Extract key metrics
    summary = {
        'total_categories': summary_data.get('total_categories', 0),
        'categories_with_matches': summary_data.get('categories_with_matches', 0),
        'categories_without_matches': summary_data.get('categories_without_matches', 0),
        'distance_distribution': distance_distribution,
        'level_statistics': stats.get('level_statistics', {}),
        'closest_impacts': []
    }

    # Parse impacts structure: level -> category -> data
    impact_analysis = impacts.get('impact_analysis', {})
    for level, categories in impact_analysis.items():
        for category, category_data in categories.items():
            closest_place = category_data.get('closest_place')
            if closest_place is not None:
                summary['closest_impacts'].append({
                    'category': category,
                    'name': closest_place.get('name', 'N/A'),
                    'distance_meters': closest_place.get('distance_meters', 0),
                    'level': level,
                    'address': closest_place.get('formatted_address', 'N/A')
                })

    # Sort by distance
    summary['closest_impacts'].sort(key=lambda x: x['distance_meters'])

    return summary


def main():
    parser = argparse.ArgumentParser(description='Add Google Places data to comprehensive report')
    parser.add_argument('--report', required=True, help='Path to comprehensive report JSON')
    parser.add_argument('--places', required=True, help='Path to places analysis directory')
    parser.add_argument('--output', help='Output path (defaults to overwriting input)')

    args = parser.parse_args()

    # Load existing report
    with open(args.report) as f:
        report = json.load(f)

    # Load places data
    places_data = load_places_data(args.places)

    # Add to report
    report['google_places_impact'] = places_data

    # Save
    output_path = args.output or args.report
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"✅ Added Google Places Impact data to: {output_path}")

    # Print summary
    if 'error' not in places_data:
        print(f"\n📊 Summary:")
        print(f"   Total Categories: {places_data['total_categories']}")
        print(f"   With Matches: {places_data['categories_with_matches']}")
        print(f"   Top 5 Closest:")
        for impact in places_data['closest_impacts'][:5]:
            print(f"     • {impact['category']}: {impact['name']} ({impact['distance_meters']:.0f}m)")


if __name__ == "__main__":
    main()
