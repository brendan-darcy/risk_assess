#!/usr/bin/env python3
"""
Comparable Sales Generator

Utility script for generating JSON output of comparable sales with configurable
radius search. Default radius is 5km.

Usage:
    # As a script
    python3 scripts/utils/comparable_sales_generator.py --property-id 13683380
    python3 scripts/utils/comparable_sales_generator.py --lat -37.8136 --lon 145.1772

    # As a module
    from scripts.utils.comparable_sales_generator import generate_comparable_sales_json

    results = generate_comparable_sales_json(property_id="13683380", radius=5.0)

Features:
    - Default 5km radius search
    - JSON output format
    - Support for both property ID and coordinate-based searches
    - Configurable filters (price, beds, baths, property type, etc.)
    - All pages retrieval option
    - Metadata and statistics included

Author: Comparable Sales Utility
Date: 2025-11-10
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

import json
import argparse
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import pandas as pd

try:
    from pipeline_utils import AuthenticatedPipeline, DataProcessor
    USING_PIPELINE = True
except ImportError:
    # Fallback for standalone use
    USING_PIPELINE = False
    import requests


class ComparableSalesGenerator:
    """
    Generator for comparable sales data with JSON output.
    Default radius: 5km
    """

    DEFAULT_RADIUS = 5.0  # kilometers
    DEFAULT_OUTPUT_DIR = "data/comparable_sales"

    def __init__(self, config=None, use_pipeline=True):
        """
        Initialize comparable sales generator.

        Args:
            config: Configuration dict or file path
            use_pipeline: Use AuthenticatedPipeline infrastructure
        """
        self.use_pipeline = use_pipeline and USING_PIPELINE

        if self.use_pipeline:
            # Use authenticated pipeline
            from pipeline_utils import ProgressReporter
            self.reporter = ProgressReporter("Comparable Sales Generator")

            # Simple pipeline for API access
            class SimplePipeline(AuthenticatedPipeline):
                def validate_inputs(self):
                    return True
                def execute_pipeline(self):
                    return {}

            self.pipeline = SimplePipeline(config, self.reporter, "Comparable Sales Generator")
            self.api_client = self.pipeline.api_client
            self.data_processor = DataProcessor
        else:
            # Standalone mode - requires manual auth
            self.access_token = None
            self.base_url = "https://api-uat.corelogic.asia"

    def set_access_token(self, access_token: str, base_url: str = None):
        """Set access token for standalone mode."""
        self.access_token = access_token
        if base_url:
            self.base_url = base_url

    def _make_api_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request (handles both pipeline and standalone modes)."""
        if self.use_pipeline:
            return self.api_client.search_comparable_properties(params)
        else:
            if not self.access_token:
                return {"error": "Access token not set. Use set_access_token() method."}

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "accept": "application/json"
            }

            endpoint = "/search/au/property/geo/radius/lastSale"
            url = f"{self.base_url}{endpoint}"

            try:
                response = requests.get(url, headers=headers, params=params)
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "error": f"HTTP {response.status_code}",
                        "message": response.text
                    }
            except Exception as e:
                return {"error": str(e)}

    def create_filters(self,
                      price: Optional[str] = None,
                      date: Optional[str] = None,
                      beds: Optional[str] = None,
                      baths: Optional[str] = None,
                      car_spaces: Optional[str] = None,
                      land_area: Optional[str] = None,
                      property_types: Optional[List[str]] = None,
                      source: str = "AA",
                      include_historic: bool = False) -> Dict[str, Any]:
        """
        Create filter dictionary for comparable search.

        Args:
            price: Price filter (e.g., "500000", "500000-1000000", "500000-", "-1000000")
            date: Date filter YYYYMMDD format (e.g., "20230101", "20230101-20231231")
            beds: Bedroom count (e.g., "3", "3-4", "3-", "-4")
            baths: Bathroom count (e.g., "2", "2-3", "2-", "-3")
            car_spaces: Car spaces (e.g., "2", "1-2", "2-", "-2")
            land_area: Land area in m² (e.g., "600", "600-1000", "600-", "-1000")
            property_types: List of types (HOUSE, UNIT, TOWNHOUSE, LAND, etc.)
            source: Data source ("AA" = All Authenticated, "ALL", "VG")
            include_historic: Include historic sales

        Returns:
            Dictionary of filter parameters
        """
        filters = {}

        if price:
            filters["price"] = price
        if date:
            filters["date"] = date
        if beds:
            filters["beds"] = beds
        if baths:
            filters["baths"] = baths
        if car_spaces:
            filters["carSpaces"] = car_spaces
        if land_area:
            filters["landArea"] = land_area
        if property_types:
            filters["pTypes"] = ",".join(property_types)

        filters["source"] = source
        filters["includeHistoric"] = str(include_historic).lower()

        return filters

    def search_comparables_by_coordinates(self,
                                         lat: float,
                                         lon: float,
                                         radius: float = None,
                                         filters: Dict[str, Any] = None,
                                         get_all_pages: bool = True,
                                         max_results: int = None) -> Dict[str, Any]:
        """
        Search for comparable sales by coordinates.

        Args:
            lat: Latitude
            lon: Longitude
            radius: Search radius in km (default: 5.0km)
            filters: Filter dictionary (use create_filters())
            get_all_pages: Retrieve all pages of results
            max_results: Maximum results to retrieve

        Returns:
            Dictionary with comparable sales data and metadata
        """
        if radius is None:
            radius = self.DEFAULT_RADIUS

        print(f"🔍 Searching comparable sales within {radius}km radius")
        print(f"📍 Coordinates: {lat}, {lon}")

        params = {
            "lat": lat,
            "lon": lon,
            "radius": min(radius, 100),  # API max is 100km
            "page": 0,
            "size": 20  # API max per page
        }

        if filters:
            params.update(filters)
            print(f"🔧 Applied filters: {filters}")

        # Collect all results
        all_properties = []
        page = 0

        while True:
            params["page"] = page
            response = self._make_api_request(params)

            if "error" in response:
                print(f"❌ Error on page {page}: {response['error']}")
                break

            # Extract properties
            embedded = response.get("_embedded", {})
            property_list = embedded.get("propertySummaryList", [])

            properties = []
            for item in property_list:
                if "propertySummary" in item:
                    properties.append(item["propertySummary"])
                else:
                    properties.append(item)

            if not properties:
                break

            all_properties.extend(properties)

            # Get pagination info
            page_info = response.get("page", {})
            total_elements = page_info.get("totalElements", 0)
            current_page = page_info.get("number", 0)
            total_pages = page_info.get("totalPages", 1)

            print(f"📄 Page {current_page + 1}/{total_pages}: {len(properties)} properties")

            # Check if we should continue
            if not get_all_pages or current_page >= total_pages - 1:
                break

            if max_results and len(all_properties) >= max_results:
                all_properties = all_properties[:max_results]
                break

            page += 1

        print(f"✅ Found {len(all_properties)} comparable sales")

        return self._create_output_json(
            properties=all_properties,
            search_params={
                "search_type": "coordinates",
                "lat": lat,
                "lon": lon,
                "radius": radius,
                "filters": filters or {}
            }
        )

    def search_comparables_by_property_id(self,
                                         property_id: str,
                                         radius: float = None,
                                         filters: Dict[str, Any] = None,
                                         get_all_pages: bool = True,
                                         max_results: int = None) -> Dict[str, Any]:
        """
        Search for comparable sales by property ID.

        Args:
            property_id: CoreLogic property ID
            radius: Search radius in km (default: 5.0km)
            filters: Filter dictionary (use create_filters())
            get_all_pages: Retrieve all pages of results
            max_results: Maximum results to retrieve

        Returns:
            Dictionary with comparable sales data and metadata
        """
        if radius is None:
            radius = self.DEFAULT_RADIUS

        print(f"🔍 Searching comparable sales for property ID: {property_id}")
        print(f"📏 Radius: {radius}km")

        params = {
            "propertyId": property_id,
            "radius": min(radius, 100),
            "page": 0,
            "size": 20
        }

        if filters:
            params.update(filters)
            print(f"🔧 Applied filters: {filters}")

        # Collect all results
        all_properties = []
        page = 0

        while True:
            params["page"] = page
            response = self._make_api_request(params)

            if "error" in response:
                print(f"❌ Error on page {page}: {response['error']}")
                break

            # Extract properties
            embedded = response.get("_embedded", {})
            property_list = embedded.get("propertySummaryList", [])

            properties = []
            for item in property_list:
                if "propertySummary" in item:
                    properties.append(item["propertySummary"])
                else:
                    properties.append(item)

            if not properties:
                break

            all_properties.extend(properties)

            # Get pagination info
            page_info = response.get("page", {})
            total_elements = page_info.get("totalElements", 0)
            current_page = page_info.get("number", 0)
            total_pages = page_info.get("totalPages", 1)

            print(f"📄 Page {current_page + 1}/{total_pages}: {len(properties)} properties")

            if not get_all_pages or current_page >= total_pages - 1:
                break

            if max_results and len(all_properties) >= max_results:
                all_properties = all_properties[:max_results]
                break

            page += 1

        print(f"✅ Found {len(all_properties)} comparable sales")

        return self._create_output_json(
            properties=all_properties,
            search_params={
                "search_type": "property_id",
                "property_id": property_id,
                "radius": radius,
                "filters": filters or {}
            }
        )

    def _create_output_json(self, properties: List[Dict[str, Any]],
                           search_params: Dict[str, Any]) -> Dict[str, Any]:
        """Create structured JSON output with metadata and statistics."""

        # Calculate statistics
        stats = self._calculate_statistics(properties)

        output = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "generator_version": "1.0",
                "search_type": search_params.get("search_type"),
                "search_parameters": search_params,
                "total_comparables": len(properties),
                "default_radius_km": self.DEFAULT_RADIUS
            },
            "statistics": stats,
            "comparable_sales": properties
        }

        return output

    def _calculate_statistics(self, properties: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics from comparable sales."""
        if not properties:
            return {}

        # Convert to DataFrame for analysis
        df = pd.DataFrame(properties)

        stats = {
            "total_count": len(properties),
            "price_statistics": {},
            "property_characteristics": {},
            "date_range": {},
            "distance_distribution": {},
            "recent_25_date_range": {},
            "recent_50_date_range": {}
        }

        # Price statistics
        if "salePrice" in df.columns:
            prices = df["salePrice"].dropna()
            if len(prices) > 0:
                stats["price_statistics"] = {
                    "median": float(prices.median()),
                    "mean": float(prices.mean()),
                    "min": float(prices.min()),
                    "max": float(prices.max()),
                    "std_dev": float(prices.std()),
                    "q1": float(prices.quantile(0.25)),
                    "q3": float(prices.quantile(0.75)),
                    "count": int(prices.count())
                }

        # Property characteristics
        for col in ["beds", "baths", "carSpaces", "propertyType"]:
            if col in df.columns:
                value_counts = df[col].value_counts()
                if len(value_counts) > 0:
                    stats["property_characteristics"][col] = {
                        "distribution": value_counts.to_dict(),
                        "most_common": str(value_counts.index[0]) if len(value_counts) > 0 else None
                    }

        # Date range (overall)
        if "lastSaleDate" in df.columns:
            dates = df["lastSaleDate"].dropna()
            if len(dates) > 0:
                stats["date_range"] = {
                    "earliest": str(dates.min()),
                    "latest": str(dates.max()),
                    "count": int(dates.count())
                }

        # Distance-based distribution
        if "distance" in df.columns:
            distances = df["distance"].dropna()
            if len(distances) > 0:
                # Count properties within distance bands
                within_500m = int((distances <= 0.5).sum())
                within_1km = int((distances <= 1.0).sum())
                within_3km = int((distances <= 3.0).sum())

                stats["distance_distribution"] = {
                    "within_500m": within_500m,
                    "within_1km": within_1km,
                    "within_3km": within_3km,
                    "total": int(distances.count())
                }

        # Date ranges for most recent comparables
        if "lastSaleDate" in df.columns:
            # Sort by date descending (most recent first)
            df_sorted = df.sort_values("lastSaleDate", ascending=False)
            dates_sorted = df_sorted["lastSaleDate"].dropna()

            # Most recent 25 comparables
            if len(dates_sorted) >= 25:
                recent_25_dates = dates_sorted.head(25)
                stats["recent_25_date_range"] = {
                    "earliest": str(recent_25_dates.min()),
                    "latest": str(recent_25_dates.max()),
                    "count": 25
                }
            elif len(dates_sorted) > 0:
                stats["recent_25_date_range"] = {
                    "earliest": str(dates_sorted.min()),
                    "latest": str(dates_sorted.max()),
                    "count": int(dates_sorted.count())
                }

            # Most recent 50 comparables
            if len(dates_sorted) >= 50:
                recent_50_dates = dates_sorted.head(50)
                stats["recent_50_date_range"] = {
                    "earliest": str(recent_50_dates.min()),
                    "latest": str(recent_50_dates.max()),
                    "count": 50
                }
            elif len(dates_sorted) > 0:
                stats["recent_50_date_range"] = {
                    "earliest": str(dates_sorted.min()),
                    "latest": str(dates_sorted.max()),
                    "count": int(dates_sorted.count())
                }

        return stats

    def save_to_json(self, data: Dict[str, Any], output_file: str = None) -> str:
        """
        Save comparable sales data to JSON file.

        Args:
            data: Data dictionary from search methods
            output_file: Output file path (auto-generated if None)

        Returns:
            Path to saved file
        """
        if output_file is None:
            # Auto-generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            search_type = data["metadata"]["search_type"]

            if search_type == "property_id":
                prop_id = data["metadata"]["search_parameters"]["property_id"]
                filename = f"comparable_sales_{prop_id}_{timestamp}.json"
            else:
                lat = data["metadata"]["search_parameters"]["lat"]
                lon = data["metadata"]["search_parameters"]["lon"]
                filename = f"comparable_sales_lat{lat}_lon{lon}_{timestamp}.json"

            # Create output directory
            output_dir = Path(self.DEFAULT_OUTPUT_DIR)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / filename
        else:
            output_file = Path(output_file)
            output_file.parent.mkdir(parents=True, exist_ok=True)

        # Save JSON with pretty formatting
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        print(f"💾 Saved to: {output_file}")
        print(f"📊 File size: {output_file.stat().st_size / 1024:.1f} KB")

        return str(output_file)


def generate_comparable_sales_json(property_id: str = None,
                                   lat: float = None,
                                   lon: float = None,
                                   radius: float = 5.0,
                                   filters: Dict[str, Any] = None,
                                   output_file: str = None,
                                   get_all_pages: bool = True) -> Tuple[Dict[str, Any], str]:
    """
    Convenience function to generate comparable sales JSON.

    Args:
        property_id: CoreLogic property ID (for property ID search)
        lat: Latitude (for coordinate search)
        lon: Longitude (for coordinate search)
        radius: Search radius in km (default: 5.0)
        filters: Filter dictionary
        output_file: Output JSON file path (auto-generated if None)
        get_all_pages: Retrieve all pages

    Returns:
        Tuple of (data_dict, output_file_path)

    Examples:
        # By property ID (default 5km radius)
        data, file = generate_comparable_sales_json(property_id="13683380")

        # By coordinates with custom radius
        data, file = generate_comparable_sales_json(
            lat=-37.8136, lon=145.1772, radius=10.0
        )

        # With filters
        filters = {"price": "500000-1000000", "beds": "3-4", "property_types": ["HOUSE"]}
        data, file = generate_comparable_sales_json(
            property_id="13683380", filters=filters
        )
    """
    generator = ComparableSalesGenerator()

    if property_id:
        data = generator.search_comparables_by_property_id(
            property_id, radius, filters, get_all_pages
        )
    elif lat is not None and lon is not None:
        data = generator.search_comparables_by_coordinates(
            lat, lon, radius, filters, get_all_pages
        )
    else:
        raise ValueError("Must provide either property_id or (lat, lon)")

    file_path = generator.save_to_json(data, output_file)

    return data, file_path


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Generate comparable sales JSON with default 5km radius",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search by property ID (default 5km radius)
  python3 scripts/utils/comparable_sales_generator.py --property-id 13683380

  # Search by coordinates with custom radius
  python3 scripts/utils/comparable_sales_generator.py --lat -37.8136 --lon 145.1772 --radius 10

  # With filters
  python3 scripts/utils/comparable_sales_generator.py --property-id 13683380 \\
      --price "500000-1000000" --beds "3-4" --property-types HOUSE

  # Save to specific file
  python3 scripts/utils/comparable_sales_generator.py --property-id 13683380 \\
      --output data/my_comparables.json
        """
    )

    # Search parameters
    search_group = parser.add_mutually_exclusive_group(required=True)
    search_group.add_argument("--property-id", help="CoreLogic property ID")
    search_group.add_argument("--lat", type=float, help="Latitude for coordinate search")

    parser.add_argument("--lon", type=float, help="Longitude (required with --lat)")
    parser.add_argument("--radius", type=float, default=5.0,
                       help="Search radius in km (default: 5.0)")

    # Filters
    parser.add_argument("--price", help="Price filter (e.g., '500000-1000000')")
    parser.add_argument("--date", help="Date filter YYYYMMDD (e.g., '20230101-20231231')")
    parser.add_argument("--beds", help="Bedroom count (e.g., '3-4')")
    parser.add_argument("--baths", help="Bathroom count (e.g., '2-3')")
    parser.add_argument("--car-spaces", help="Car spaces (e.g., '2')")
    parser.add_argument("--land-area", help="Land area in m² (e.g., '600-1000')")
    parser.add_argument("--property-types", nargs="+",
                       help="Property types (e.g., HOUSE UNIT)")
    parser.add_argument("--source", default="AA", help="Data source (default: AA)")

    # Output
    parser.add_argument("--output", "-o", help="Output JSON file path")
    parser.add_argument("--single-page", action="store_true",
                       help="Retrieve only first page (default: all pages)")
    parser.add_argument("--max-results", type=int, help="Maximum results to retrieve")

    args = parser.parse_args()

    # Validate lat/lon
    if args.lat is not None and args.lon is None:
        parser.error("--lon is required when using --lat")

    # Build filters
    filters = None
    if any([args.price, args.date, args.beds, args.baths, args.car_spaces,
            args.land_area, args.property_types]):
        generator = ComparableSalesGenerator()
        filters = generator.create_filters(
            price=args.price,
            date=args.date,
            beds=args.beds,
            baths=args.baths,
            car_spaces=args.car_spaces,
            land_area=args.land_area,
            property_types=args.property_types,
            source=args.source
        )

    # Execute search
    try:
        if args.property_id:
            data, file_path = generate_comparable_sales_json(
                property_id=args.property_id,
                radius=args.radius,
                filters=filters,
                output_file=args.output,
                get_all_pages=not args.single_page
            )
        else:
            data, file_path = generate_comparable_sales_json(
                lat=args.lat,
                lon=args.lon,
                radius=args.radius,
                filters=filters,
                output_file=args.output,
                get_all_pages=not args.single_page
            )

        # Print summary
        print("\n" + "="*60)
        print("COMPARABLE SALES SUMMARY")
        print("="*60)
        print(f"Total comparables: {data['metadata']['total_comparables']}")

        if "price_statistics" in data["statistics"]:
            price_stats = data["statistics"]["price_statistics"]
            if price_stats:
                print(f"Median price: ${price_stats['median']:,.0f}")
                print(f"Price range: ${price_stats['min']:,.0f} - ${price_stats['max']:,.0f}")

        print(f"Output file: {file_path}")
        print("="*60)

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
