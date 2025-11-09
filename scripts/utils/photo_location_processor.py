#!/usr/bin/env python3
"""
Photo Location Processor

Processes photo metadata to extract GPS coordinates and categorize photos
by type for spatial visualization.

Key Features:
- Parse photo metadata JSON
- Extract GPS coordinates
- Categorize photos by field/type
- Convert to GeoDataFrame for mapping
- Calculate distances to property

Author: Brendan Darcy
Date: 2025-11-03
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from geopy.distance import geodesic


class PhotoLocationProcessor:
    """
    Processes photo metadata to prepare for spatial visualization.
    """

    # Photo category color scheme
    PHOTO_CATEGORY_COLORS = {
        'frontage': '#1f77b4',              # Blue
        'rear': '#2ca02c',                   # Green
        'kitchen': '#ff7f0e',                # Orange
        'bathroom': '#9467bd',               # Purple
        'livingArea': '#bcbd22',             # Yellow-green
        'significantRenovation': '#d62728',  # Red
        'externalUndercoverArea': '#8c564b', # Brown
        'laundry': '#e377c2',                # Pink
        'secondaryKitchen': '#ff9896',       # Light red
        'additionalImagery': '#c7c7c7'       # Gray
    }

    def __init__(self):
        """Initialize the photo location processor."""
        self.photos_data = []

    def parse_metadata_file(self, metadata_path: str) -> List[Dict]:
        """
        Parse photo metadata text file containing JSON lines.

        Args:
            metadata_path: Path to photo_meta_data.txt

        Returns:
            List of parsed photo dictionaries
        """
        photos = []

        with open(metadata_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    # Each line appears to be: path/{"metadata": {...}, "field": "...", ...}
                    # Split at first { to separate path from JSON
                    json_start = line.find('{')
                    if json_start == -1:
                        continue

                    json_str = line[json_start:]
                    photo_data = json.loads(json_str)

                    # Extract metadata
                    metadata = photo_data.get('metadata', {})
                    longitude = metadata.get('longitude')
                    latitude = metadata.get('latitude')

                    # Skip photos without coordinates
                    if longitude is None or latitude is None:
                        continue

                    # Convert to float
                    try:
                        longitude = float(longitude)
                        latitude = float(latitude)
                    except (ValueError, TypeError):
                        continue

                    # Extract field name and categorize
                    field = photo_data.get('field', 'unknown')
                    category = self._categorize_photo(field)

                    photos.append({
                        'field': field,
                        'category': category,
                        'longitude': longitude,
                        'latitude': latitude,
                        'party': photo_data.get('party', ''),
                        'survey': photo_data.get('survey', ''),
                        'line_number': line_num
                    })

                except json.JSONDecodeError as e:
                    print(f"Warning: Could not parse line {line_num}: {e}")
                    continue

        self.photos_data = photos
        print(f"✅ Parsed {len(photos)} photos with GPS coordinates")
        return photos

    def _categorize_photo(self, field_name: str) -> str:
        """
        Categorize photo based on field name.

        Args:
            field_name: Field identifier from metadata

        Returns:
            Category name
        """
        field_lower = field_name.lower()

        if 'frontage' in field_lower:
            return 'frontage'
        elif 'rear' in field_lower:
            return 'rear'
        elif 'kitchen' in field_lower:
            if 'secondary' in field_lower:
                return 'secondaryKitchen'
            return 'kitchen'
        elif 'bathroom' in field_lower:
            return 'bathroom'
        elif 'livingarea' in field_lower or 'living' in field_lower:
            return 'livingArea'
        elif 'renovation' in field_lower:
            return 'significantRenovation'
        elif 'undercover' in field_lower:
            return 'externalUndercoverArea'
        elif 'laundry' in field_lower:
            return 'laundry'
        elif 'imagery' in field_lower:
            return 'additionalImagery'
        else:
            return 'other'

    def create_geodataframe(
        self,
        photos: Optional[List[Dict]] = None,
        target_crs: str = 'EPSG:3577'
    ) -> gpd.GeoDataFrame:
        """
        Convert photo data to GeoDataFrame.

        Args:
            photos: List of photo dictionaries (uses self.photos_data if None)
            target_crs: Target coordinate reference system

        Returns:
            GeoDataFrame with photo locations
        """
        if photos is None:
            photos = self.photos_data

        if not photos:
            raise ValueError("No photo data available. Call parse_metadata_file first.")

        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(
            photos,
            geometry=gpd.points_from_xy(
                [p['longitude'] for p in photos],
                [p['latitude'] for p in photos]
            ),
            crs='EPSG:4326'  # WGS84
        )

        # Reproject to target CRS
        gdf = gdf.to_crs(target_crs)

        # Add color column based on category
        gdf['color'] = gdf['category'].map(self.PHOTO_CATEGORY_COLORS)
        gdf['color'] = gdf['color'].fillna('#808080')  # Gray for unmapped categories

        print(f"✅ Created GeoDataFrame with {len(gdf)} photos in {target_crs}")

        return gdf

    def calculate_distances_to_property(
        self,
        photos_gdf: gpd.GeoDataFrame,
        property_coords: Tuple[float, float]
    ) -> gpd.GeoDataFrame:
        """
        Calculate distances from each photo location to the property.

        Args:
            photos_gdf: GeoDataFrame with photo locations (in EPSG:4326)
            property_coords: Property coordinates as (latitude, longitude)

        Returns:
            GeoDataFrame with added 'distance_m' column
        """
        # Ensure we're working with WGS84 for geodesic calculations
        if photos_gdf.crs.to_string() != 'EPSG:4326':
            photos_gdf_wgs84 = photos_gdf.to_crs('EPSG:4326')
        else:
            photos_gdf_wgs84 = photos_gdf.copy()

        distances = []
        for idx, row in photos_gdf_wgs84.iterrows():
            photo_coords = (row.geometry.y, row.geometry.x)  # (lat, lon)
            distance = geodesic(property_coords, photo_coords).meters
            distances.append(round(distance, 1))

        photos_gdf['distance_m'] = distances

        return photos_gdf

    def get_category_summary(
        self,
        photos: Optional[List[Dict]] = None
    ) -> Dict[str, int]:
        """
        Get count of photos by category.

        Args:
            photos: List of photo dictionaries (uses self.photos_data if None)

        Returns:
            Dictionary mapping category to count
        """
        if photos is None:
            photos = self.photos_data

        category_counts = {}
        for photo in photos:
            category = photo['category']
            category_counts[category] = category_counts.get(category, 0) + 1

        return dict(sorted(category_counts.items(), key=lambda x: x[1], reverse=True))

    def print_summary(self, photos_gdf: Optional[gpd.GeoDataFrame] = None):
        """
        Print summary statistics of photo locations.

        Args:
            photos_gdf: Optional GeoDataFrame with distance calculations
        """
        print("\n" + "=" * 60)
        print("📸 PHOTO LOCATION SUMMARY")
        print("=" * 60)

        # Category counts
        category_counts = self.get_category_summary()
        print("\nPhotos by Category:")
        for category, count in category_counts.items():
            color = self.PHOTO_CATEGORY_COLORS.get(category, '#808080')
            print(f"  {category:25s}: {count:2d} photos - {color}")

        print(f"\nTotal photos: {len(self.photos_data)}")

        # Distance statistics if available
        if photos_gdf is not None and 'distance_m' in photos_gdf.columns:
            distances = photos_gdf['distance_m'].values
            print(f"\nDistance to Property:")
            print(f"  Closest: {distances.min():.1f}m")
            print(f"  Furthest: {distances.max():.1f}m")
            print(f"  Average: {distances.mean():.1f}m")
            print(f"  Median: {pd.Series(distances).median():.1f}m")

    def process_complete(
        self,
        metadata_path: str,
        property_coords: Tuple[float, float],
        target_crs: str = 'EPSG:3577'
    ) -> Tuple[gpd.GeoDataFrame, Dict[str, int]]:
        """
        Complete processing pipeline: parse, create GeoDataFrame, calculate distances.

        Args:
            metadata_path: Path to photo metadata file
            property_coords: Property coordinates as (latitude, longitude)
            target_crs: Target CRS for mapping

        Returns:
            Tuple of (GeoDataFrame with photos, category summary dict)
        """
        # Parse metadata
        photos = self.parse_metadata_file(metadata_path)

        # Create GeoDataFrame
        photos_gdf = self.create_geodataframe(photos, target_crs)

        # Calculate distances (need WGS84 for geodesic)
        photos_gdf_wgs84 = photos_gdf.to_crs('EPSG:4326')
        photos_gdf = self.calculate_distances_to_property(
            photos_gdf,
            property_coords
        )

        # Get summary
        category_summary = self.get_category_summary(photos)

        # Print summary
        self.print_summary(photos_gdf)

        return photos_gdf, category_summary


if __name__ == "__main__":
    print("Photo Location Processor - Use scripts/visualize_photo_locations.py to execute")
