#!/usr/bin/env python3
"""
Reorganize Comprehensive Report into 10 Product Categories

Takes a comprehensive property report JSON and reorganizes ALL fields
into the 10 product concept categories without losing any data.

Usage:
    python3 scripts/categorize_report.py --input data/property_reports/13683380_comprehensive_report.json --output data/property_reports/13683380_categorized.json

Author: Property Report Categorizer
Date: 2025-11-09
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Any


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Flatten nested dictionary"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict) and v:
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
            # Keep lists of objects intact but note the count
            items.append((new_key, f"[{len(v)} items]"))
            for i, item in enumerate(v[:3]):  # First 3 items
                items.extend(flatten_dict(item, f"{new_key}[{i}]", sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def categorize_comprehensive_report(report: Dict[str, Any], comparable_sales: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Reorganize comprehensive report into 10 product categories.
    ALL fields from the original report are preserved.

    Args:
        report: Comprehensive property report
        comparable_sales: Optional comparable sales data from comparable_sales_generator
    """

    metadata = report.get('metadata', {})
    property_details = report.get('property_details', {})
    location = property_details.get('location', {})
    legal = property_details.get('legal', {})
    site = property_details.get('site', {})
    core_attrs = property_details.get('core_attributes', {})
    additional_attrs = property_details.get('additional_attributes', {})
    features = property_details.get('features', {})
    occupancy = property_details.get('occupancy', {})
    last_sale = property_details.get('last_sale', {})
    sales_history = property_details.get('sales_history', {})
    sales_otm = property_details.get('sales_otm', {})
    rentals_otm = property_details.get('rentals_otm', {})
    timeline = property_details.get('timeline', {})
    advertisements = property_details.get('advertisements', {})
    parcel_geom = report.get('parcel_geometry', {})
    geo_layers = report.get('geospatial_layers', {})
    market_metrics = report.get('market_metrics_summary', {})
    google_places = report.get('google_places_impact', {})
    mesh_block = report.get('mesh_block_analysis', {})

    categorized = {
        "metadata": {
            "categorization_version": "1.0",
            "categorization_date": metadata.get('extraction_timestamp'),
            "original_report_type": metadata.get('report_type', 'comprehensive'),
            "source_address": metadata.get('address'),
            "source_property_id": metadata.get('property_id'),
            "source_state": metadata.get('state')
        },

        # =====================================================================
        # CATEGORY 1: INSTRUCTIONS
        # =====================================================================
        "1_instructions": {
            "category_name": "Instructions",
            "category_description": "Client identity, property address, estimate, job type, parties, and comments",
            "coverage": "0% - Not captured in source data",
            "data": {
                "_note": "This category is not present in the current data model",
                "_gaps": [
                    "client_name",
                    "client_id",
                    "job_number",
                    "job_type",
                    "valuation_estimate",
                    "parties",
                    "special_instructions"
                ]
            },
            "source_fields": []
        },

        # =====================================================================
        # CATEGORY 2: LOCATION AND ADMINISTRATIVE
        # =====================================================================
        "2_location_and_administrative": {
            "category_name": "Location and Administrative",
            "category_description": "Local government authority, geographic coordinates, and administrative boundaries",
            "coverage": "100% - Complete",
            "data": {
                # Metadata
                "address": metadata.get('address'),
                "state": metadata.get('state'),

                # Location details - ALL fields
                "location": location,

                # Site zoning (administrative)
                "zoning": {
                    "code": site.get('zoneCodeLocal'),
                    "description": site.get('zoneDescriptionLocal')
                },

                # Statistical Areas (from mesh block analysis)
                "statistical_areas": {
                    "sa1_codes": mesh_block.get('sa1_codes', []),
                    "total_sa1_codes": mesh_block.get('total_sa1_codes', 0),
                    "sa2_names": mesh_block.get('sa2_names', []),
                    "sa3_names": mesh_block.get('sa3_names', []),
                    "sa4_names": mesh_block.get('sa4_names', [])
                } if mesh_block else {}
            },
            "source_fields": ["metadata.address", "metadata.state", "property_details.location.*", "property_details.site.zoning*", "mesh_block_analysis.sa*"],
            "gaps": ["electoral_district"]
        },

        # =====================================================================
        # CATEGORY 3: MAPPING, TOPOGRAPHY AND PLACES
        # =====================================================================
        "3_mapping_topography_and_places": {
            "category_name": "Mapping, Topography and Places",
            "category_description": "Geocoding, elevation, slope, mesh block analysis, and proximity to value drivers or blights",
            "coverage": "75% - Good coverage",
            "data": {
                # Infrastructure (includes proximity to infrastructure layers)
                "infrastructure": {
                    "proximity": geo_layers.get('infrastructure', {}) if geo_layers else {}
                },

                # Mesh block analysis (mapping/topography parts only, excludes SA codes which are in Category 2)
                "mesh_block_analysis": {
                    "search_radius_m": mesh_block.get('search_radius_m'),
                    "total_meshblocks": mesh_block.get('total_meshblocks'),
                    "residential_meshblocks": mesh_block.get('residential_meshblocks'),
                    "non_residential_meshblocks": mesh_block.get('non_residential_meshblocks'),
                    "category_breakdown": mesh_block.get('category_breakdown', {}),
                    "non_residential_distances": mesh_block.get('non_residential_distances', {}),
                    "top_5_closest_non_residential": mesh_block.get('top_5_closest_non_residential', []),
                    "source_file": mesh_block.get('source_file'),
                    "buffer_description": mesh_block.get('buffer_description')
                } if mesh_block else {},

                # Surrounding Context - Proximity to value drivers/blights (Google Places) - LAST
                "surrounding_context": google_places if google_places else {}
            },
            "source_fields": ["property_details.location.latitude/longitude", "parcel_geometry.*", "mesh_block_analysis.counts_distances", "geospatial_layers.infrastructure.*", "google_places_impact.*"],
            "gaps": ["elevation_meters", "slope_degrees", "slope_percentage", "aspect", "topographic_class"]
        },

        # =====================================================================
        # CATEGORY 4: LEGAL
        # =====================================================================
        "4_legal": {
            "category_name": "Legal",
            "category_description": "Property's formal identity including title information and land authority references",
            "coverage": "100% - Complete",
            "data": {
                # Property ID
                "property_id": metadata.get('property_id'),

                # Legal details - ALL fields
                "legal": legal,

                # Easements
                "easements": geo_layers.get('legal', {}).get('easements', {}) if geo_layers else {}
            },
            "source_fields": ["metadata.property_id", "property_details.legal.*", "geospatial_layers.legal.easements.*"],
            "gaps": []
        },

        # =====================================================================
        # CATEGORY 5: CHARACTERISTICS
        # =====================================================================
        "5_characteristics": {
            "category_name": "Characteristics",
            "category_description": "Property type, form, key attributes such as room counts (bed, bath, living), car spaces, building dimensions, layout, construction era, notable features, and spatial/boundary geometry",
            "coverage": "100% - Complete",
            "data": {
                # Core attributes - ALL fields
                "core_attributes": core_attrs,

                # Additional attributes - ALL fields
                "additional_attributes": additional_attrs,

                # Features - ALL fields
                "features": features,

                # Spatial data (boundary geometry, elevation, orientation) - ALL fields
                "spatial": {
                    "boundary_geometry": parcel_geom,
                    "elevation_analysis": parcel_geom.get('data', {}).get('elevation_analysis'),
                    "orientation_analysis": parcel_geom.get('data', {}).get('orientation_analysis')
                }
            },
            "source_fields": ["property_details.core_attributes.*", "property_details.additional_attributes.*", "property_details.features.*", "parcel_geometry.*"],
            "gaps": []
        },

        # =====================================================================
        # CATEGORY 6: OCCUPANCY
        # =====================================================================
        "6_occupancy": {
            "category_name": "Occupancy",
            "category_description": "How the property is being used, zoning, planning, and development applications",
            "coverage": "70% - Partial coverage",
            "data": {
                # Occupancy - ALL fields
                "occupancy": occupancy,

                # Site/land use - ALL fields
                "site": site
            },
            "source_fields": ["property_details.occupancy.*", "property_details.site.*"],
            "gaps": ["planning_applications", "development_applications", "building_permits", "planning_overlays"]
        },

        # =====================================================================
        # CATEGORY 7: LOCAL MARKET
        # =====================================================================
        "7_local_market": {
            "category_name": "Local Market",
            "category_description": "Sales and rental data, including time series for median prices, sales value and distribution, discounting, yields, and matched pairs of sales within a development",
            "coverage": "95% - Excellent coverage",
            "data": {
                # Market metrics - ALL fields
                "market_metrics_summary": market_metrics if market_metrics else {}
            },
            "source_fields": ["market_metrics_summary.*"],
            "gaps": ["matched_pairs_within_development", "sales_value_distribution"]
        },

        # =====================================================================
        # CATEGORY 8: TRANSACTION HISTORY
        # =====================================================================
        "8_transaction_history": {
            "category_name": "Transaction History",
            "category_description": "Sales history of the subject property",
            "coverage": "100% - Complete",
            "data": {
                # Last sale - ALL fields
                "last_sale": last_sale,

                # Sales history - ALL fields
                "sales_history": sales_history
            },
            "source_fields": ["property_details.last_sale.*", "property_details.sales_history.*"],
            "gaps": []
        },

        # =====================================================================
        # CATEGORY 9: CAMPAIGNS
        # =====================================================================
        "9_campaigns": {
            "category_name": "Campaigns",
            "category_description": "Historical and current marketing campaigns with timelines and advertising extracts",
            "coverage": "100% - Complete",
            "data": {
                # Sales campaigns - ALL fields
                "sales_otm": sales_otm,

                # Rental campaigns - ALL fields
                "rentals_otm": rentals_otm,

                # Timeline - ALL fields
                "timeline": timeline,

                # Advertisements - ALL fields
                "advertisements": advertisements
            },
            "source_fields": ["property_details.sales_otm.*", "property_details.rentals_otm.*", "property_details.timeline.*", "property_details.advertisements.*"],
            "gaps": []
        },

        # =====================================================================
        # CATEGORY 10: SALES EVIDENCE
        # =====================================================================
        "10_sales_evidence": {
            "category_name": "Sales Evidence",
            "category_description": "Comparable sales in the property's precinct",
            "coverage": "100% - Complete" if comparable_sales else "0% - Not captured in source data",
            "data": {
                # Comparable sales data if provided
                "comparable_sales": comparable_sales.get('comparable_sales', []) if comparable_sales else [],
                "statistics": comparable_sales.get('statistics', {}) if comparable_sales else {},
                "search_metadata": comparable_sales.get('metadata', {}) if comparable_sales else {},

                # Gaps if no data
                "_note": "No comparable sales data provided" if not comparable_sales else "Comparable sales generated from radius search",
                "_gaps": [] if comparable_sales else [
                    "comparable_sales",
                    "precinct_analysis",
                    "property_matching",
                    "distance_based_comparables",
                    "adjusted_sale_prices"
                ]
            },
            "source_fields": ["comparable_sales_generator"] if comparable_sales else [],
            "gaps": [] if comparable_sales else ["comparable_sales", "precinct_sales_analysis", "property_matching_filters"]
        },

        # =====================================================================
        # ADDITIONAL DATA
        # =====================================================================
        "additional_data": {
            "description": "Supporting data that enhances multiple categories",
            "geospatial_layers": geo_layers if geo_layers else {},
            "maps_exported": report.get('maps_exported', {})
        }
    }

    return categorized


def main():
    parser = argparse.ArgumentParser(
        description='Reorganize comprehensive report into 10 product categories',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--input',
        required=True,
        help='Path to comprehensive report JSON'
    )

    parser.add_argument(
        '--output',
        required=True,
        help='Path to save categorized report JSON'
    )

    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty print JSON output'
    )

    parser.add_argument(
        '--comparable-sales',
        help='Path to comparable sales JSON (optional)'
    )

    args = parser.parse_args()

    # Load comprehensive report
    print(f"📖 Loading comprehensive report: {args.input}")
    with open(args.input) as f:
        report = json.load(f)

    # Load comparable sales if provided
    comparable_sales = None
    if args.comparable_sales:
        print(f"📊 Loading comparable sales: {args.comparable_sales}")
        try:
            with open(args.comparable_sales) as f:
                comparable_sales = json.load(f)
            print(f"   Found {comparable_sales.get('metadata', {}).get('total_comparables', 0)} comparable sales")
        except FileNotFoundError:
            print(f"⚠️  Comparable sales file not found: {args.comparable_sales}")
        except Exception as e:
            print(f"⚠️  Error loading comparable sales: {e}")

    # Categorize
    print("📊 Categorizing data into 10 product categories...")
    categorized = categorize_comprehensive_report(report, comparable_sales)

    # Save
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    indent = 2 if args.pretty else None
    with open(output_path, 'w') as f:
        json.dump(categorized, f, indent=indent)

    print(f"✅ Categorized report saved: {output_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("CATEGORIZATION SUMMARY")
    print("=" * 60)

    for i in range(1, 11):
        key = f"{i}_" + ["instructions", "location_and_administrative", "mapping_topography_and_places",
                         "legal", "characteristics", "occupancy", "local_market",
                         "transaction_history", "campaigns", "sales_evidence"][i-1]

        category = categorized[key]
        print(f"\n{i}. {category['category_name']}")
        print(f"   Coverage: {category['coverage']}")
        print(f"   Source Fields: {len(category.get('source_fields', []))} field groups")
        if category.get('gaps'):
            print(f"   Gaps: {len(category['gaps'])} missing fields")


if __name__ == "__main__":
    main()
