#!/usr/bin/env python3
"""
Photo Location Visualization Pipeline

Creates standalone visualizations showing photo locations relative to a property,
with color-coded markers, connecting lines, and distance annotations.

Key Features:
- Plot property location and photo points
- Color-code photos by category
- Draw connecting lines from photos to property
- Annotate distances on lines
- Generate comprehensive legend

Author: Brendan Darcy
Date: 2025-11-03
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from shapely.geometry import LineString, Point
import requests
from io import BytesIO
from PIL import Image
import numpy as np

try:
    import contextily as ctx
    CONTEXTILY_AVAILABLE = True
except ImportError:
    CONTEXTILY_AVAILABLE = False
    print("Warning: contextily not available. Will use Google Maps Static API if available.")

from .photo_location_processor import PhotoLocationProcessor


class PhotoVisualizationPipeline:
    """
    Pipeline for creating photo location visualizations.
    """

    def __init__(
        self,
        figsize: Tuple[int, int] = (16, 12),
        dpi: int = 200,
        google_api_key: Optional[str] = None
    ):
        """
        Initialize the photo visualization pipeline.

        Args:
            figsize: Figure size in inches (width, height)
            dpi: Resolution for saved images
            google_api_key: Google Maps API key (for Google Maps basemaps)
        """
        self.figsize = figsize
        self.dpi = dpi
        self.google_api_key = google_api_key
        self.fig: Optional[plt.Figure] = None
        self.ax: Optional[plt.Axes] = None

    def _get_google_maps_basemap(
        self,
        center_lat: float,
        center_lon: float,
        zoom: int = 19,
        size: str = "640x640",
        maptype: str = "satellite"
    ) -> Tuple[Optional[np.ndarray], Optional[List[float]]]:
        """
        Fetch a Google Maps Static API image as basemap.

        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            zoom: Zoom level (1-20, higher = more zoomed in)
            size: Image size in pixels (max 640x640 for free tier)
            maptype: Map type ('satellite', 'roadmap', 'hybrid', 'terrain')

        Returns:
            Tuple of (image_array, extent) where extent is [left, right, bottom, top] in Web Mercator
        """
        if not self.google_api_key:
            return None, None

        try:
            # Build Google Maps Static API URL
            url = "https://maps.googleapis.com/maps/api/staticmap"
            params = {
                'center': f"{center_lat},{center_lon}",
                'zoom': zoom,
                'size': size,
                'maptype': maptype,
                'key': self.google_api_key,
                'format': 'png',
                'scale': 2  # Get higher resolution image
            }

            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"⚠️  Google Maps API request failed: {response.status_code}")
                print(f"    URL: {response.url}")
                print(f"    Response: {response.text[:500]}")
                return None, None

            # Load image
            img = Image.open(BytesIO(response.content))
            img_array = np.array(img)

            # Calculate extent in Web Mercator (EPSG:3857)
            # This is approximate but works well for small areas
            from math import pi, cos, log, tan, radians

            def lat_lon_to_web_mercator(lat, lon):
                """Convert WGS84 lat/lon to Web Mercator (EPSG:3857)"""
                x = lon * 20037508.34 / 180.0
                # Clamp latitude to valid range for Web Mercator
                lat = max(-85.0511, min(85.0511, lat))
                y = log(tan((90.0 + lat) * pi / 360.0)) / (pi / 180.0)
                y = y * 20037508.34 / 180.0
                return x, y

            # Calculate meters per pixel at this zoom level and latitude
            meters_per_pixel = 156543.03392 * cos(radians(center_lat)) / (2 ** zoom)

            # Get image dimensions
            width_px, height_px = img.size

            # Calculate extent in meters
            half_width_m = (width_px / 2) * meters_per_pixel
            half_height_m = (height_px / 2) * meters_per_pixel

            center_x, center_y = lat_lon_to_web_mercator(center_lat, center_lon)

            extent = [
                center_x - half_width_m,  # left
                center_x + half_width_m,  # right
                center_y - half_height_m, # bottom
                center_y + half_height_m  # top
            ]

            return img_array, extent

        except Exception as e:
            print(f"⚠️  Error fetching Google Maps basemap: {e}")
            import traceback
            traceback.print_exc()
            return None, None

    def create_map(
        self,
        photos_gdf: gpd.GeoDataFrame,
        property_point: gpd.GeoDataFrame,
        title: Optional[str] = None,
        show_distance_lines: bool = True,
        show_distance_labels: bool = True,
        max_distance_labels: int = 10,
        add_basemap: bool = True,
        basemap_source: str = 'Google Satellite'
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        Create visualization map with photo locations and property.

        Args:
            photos_gdf: GeoDataFrame with photo locations (must have 'category', 'color' columns)
            property_point: GeoDataFrame with property location
            title: Optional custom title
            show_distance_lines: Whether to draw lines from photos to property
            show_distance_labels: Whether to show distance values on lines
            max_distance_labels: Maximum number of distance labels to show
            add_basemap: Whether to add a basemap underneath (default: True)
            basemap_source: Basemap style - 'Google Satellite', 'Google Streets', 'OpenStreetMap' (default: 'Google Satellite')

        Returns:
            Tuple of (figure, axes)
        """
        self.fig, self.ax = plt.subplots(figsize=self.figsize)

        # Convert to Web Mercator for basemap compatibility if basemap is requested
        if add_basemap:
            photos_gdf_plot = photos_gdf.to_crs(epsg=3857)
            property_point_plot = property_point.to_crs(epsg=3857)
        else:
            photos_gdf_plot = photos_gdf
            property_point_plot = property_point

        # Get property geometry and center coordinates
        prop_geom = property_point_plot.geometry.iloc[0]

        # Get center in WGS84 (EPSG:4326) for Google Maps
        # Ensure we convert to WGS84 explicitly
        property_wgs84 = property_point.to_crs(epsg=4326)
        prop_wgs84 = property_wgs84.geometry.iloc[0]
        center_lat = prop_wgs84.y
        center_lon = prop_wgs84.x
        print(f"🌍 Center coordinates: {center_lat:.6f}, {center_lon:.6f}")

        # Add basemap FIRST (so it's the bottom layer)
        if add_basemap:
            basemap_added = False

            # Try Google Maps Static API first for Google options
            if basemap_source.startswith('Google') and self.google_api_key:
                try:
                    maptype_map = {
                        'Google Satellite': 'satellite',
                        'Google Hybrid': 'hybrid',
                        'Google Roadmap': 'roadmap',
                        'Google Terrain': 'terrain'
                    }
                    maptype = maptype_map.get(basemap_source, 'satellite')

                    # Calculate appropriate zoom level based on photo spread AND property location
                    photos_wgs84 = photos_gdf.to_crs(epsg=4326)

                    # Combine photos and property to get complete bounds
                    import pandas as pd
                    all_points = pd.concat([photos_wgs84, property_wgs84])
                    bounds_wgs84 = all_points.total_bounds  # [minx, miny, maxx, maxy]

                    lat_range = bounds_wgs84[3] - bounds_wgs84[1]
                    lon_range = bounds_wgs84[2] - bounds_wgs84[0]
                    max_range = max(lat_range, lon_range)

                    # Choose zoom level based on range (zoom out more to show context)
                    # Lower zoom = more area shown
                    if max_range < 0.0005:  # ~50m
                        zoom = 18  # Reduced from 20
                    elif max_range < 0.001:  # ~100m
                        zoom = 17  # Reduced from 19
                    elif max_range < 0.002:  # ~200m
                        zoom = 16  # Reduced from 18
                    else:
                        zoom = 15

                    print(f"📍 Photo spread: {max_range:.6f}° (~{max_range * 111000:.0f}m), using zoom level {zoom}")

                    # Use maximum size for better quality and coverage
                    img_array, extent = self._get_google_maps_basemap(
                        center_lat=center_lat,
                        center_lon=center_lon,
                        zoom=zoom,
                        size="640x640",  # Max for free tier with scale=2
                        maptype=maptype
                    )

                    if img_array is not None and extent is not None:
                        # First, set the data bounds based on all photos AND property
                        import pandas as pd
                        all_geoms = pd.concat([photos_gdf_plot, property_point_plot])
                        all_bounds = all_geoms.total_bounds  # [minx, miny, maxx, maxy]
                        x_range = all_bounds[2] - all_bounds[0]
                        y_range = all_bounds[3] - all_bounds[1]
                        padding = 0.15

                        # Set axis limits to show all data
                        self.ax.set_xlim(all_bounds[0] - x_range * padding, all_bounds[2] + x_range * padding)
                        self.ax.set_ylim(all_bounds[1] - y_range * padding, all_bounds[3] + y_range * padding)

                        # Now add the basemap image
                        self.ax.imshow(img_array, extent=extent, aspect='auto', alpha=0.8, zorder=0, interpolation='bilinear')
                        self.ax.set_aspect('equal')

                        print(f"✅ Added {basemap_source} basemap via Google Maps Static API (zoom: {zoom})")
                        basemap_added = True

                except Exception as e:
                    print(f"⚠️  Google Maps basemap failed: {e}")
                    import traceback
                    traceback.print_exc()

            # Fall back to contextily if Google Maps didn't work
            if not basemap_added and CONTEXTILY_AVAILABLE:
                try:
                    # Map basemap source names to contextily providers
                    basemap_providers = {
                        'Esri Satellite': ctx.providers.Esri.WorldImagery,
                        'OpenStreetMap': ctx.providers.OpenStreetMap.Mapnik,
                        'CartoDB Positron': ctx.providers.CartoDB.Positron,
                        'CartoDB Voyager': ctx.providers.CartoDB.Voyager,
                    }
                    provider = basemap_providers.get(basemap_source, ctx.providers.Esri.WorldImagery)

                    # Get bounds from all data (photos AND property) to set proper extent
                    import pandas as pd
                    all_geoms = pd.concat([photos_gdf_plot, property_point_plot])
                    all_bounds = all_geoms.total_bounds  # [minx, miny, maxx, maxy]

                    # Add some padding (15% on each side)
                    x_range = all_bounds[2] - all_bounds[0]
                    y_range = all_bounds[3] - all_bounds[1]
                    padding = 0.15

                    self.ax.set_xlim(all_bounds[0] - x_range * padding, all_bounds[2] + x_range * padding)
                    self.ax.set_ylim(all_bounds[1] - y_range * padding, all_bounds[3] + y_range * padding)
                    self.ax.set_aspect('equal')

                    ctx.add_basemap(
                        self.ax,
                        source=provider,
                        zoom='auto',
                        alpha=0.7,
                        attribution=False
                    )
                    print(f"✅ Added {basemap_source} basemap via contextily")
                    basemap_added = True
                except Exception as e:
                    print(f"⚠️  Contextily basemap failed: {e}")
                    import traceback
                    traceback.print_exc()

            if not basemap_added:
                print("⚠️  No basemap could be added")

        # Plot connecting lines (so they're behind markers but above basemap)
        if show_distance_lines:
            self._draw_distance_lines(
                photos_gdf_plot,
                prop_geom,
                show_labels=show_distance_labels,
                max_labels=max_distance_labels
            )

        # Plot photo points by category
        categories = photos_gdf_plot['category'].unique()
        for category in categories:
            subset = photos_gdf_plot[photos_gdf_plot['category'] == category]
            color = subset['color'].iloc[0] if len(subset) > 0 else '#808080'

            subset.plot(
                ax=self.ax,
                color=color,
                markersize=100,
                marker='o',
                edgecolor='white',
                linewidth=2,
                zorder=4,
                alpha=0.8,
                label=f'{category} ({len(subset)})'
            )

            # Add photo labels
            for idx, row in subset.iterrows():
                # Create shortened label (remove "Photo" suffix for cleaner display)
                field = row['field']
                label = field.replace('Photo', '').replace('photo', '')
                if len(label) > 20:
                    label = label[:17] + '...'

                self.ax.annotate(
                    label,
                    xy=(row.geometry.x, row.geometry.y),
                    xytext=(5, 5),
                    textcoords='offset points',
                    fontsize=7,
                    bbox=dict(
                        boxstyle='round,pad=0.3',
                        facecolor='white',
                        alpha=0.7,
                        edgecolor=row['color']
                    ),
                    ha='left',
                    zorder=5
                )

        # Calculate photo centroid
        photos_centroid = photos_gdf_plot.geometry.unary_union.centroid

        # Draw line from property to photo centroid
        centroid_line = LineString([prop_geom, photos_centroid])
        centroid_line_gdf = gpd.GeoDataFrame(geometry=[centroid_line], crs=photos_gdf_plot.crs)
        centroid_line_gdf.plot(
            ax=self.ax,
            color='orange',
            linewidth=3,
            linestyle='-',
            alpha=0.9,
            zorder=3
        )

        # Calculate distance to centroid in WGS84
        photos_wgs84_for_centroid = photos_gdf.to_crs(epsg=4326)
        centroid_wgs84 = photos_wgs84_for_centroid.geometry.unary_union.centroid
        property_wgs84_point = property_wgs84.geometry.iloc[0]

        from geopy.distance import geodesic
        centroid_distance = geodesic(
            (property_wgs84_point.y, property_wgs84_point.x),
            (centroid_wgs84.y, centroid_wgs84.x)
        ).meters

        # Add distance label on the line
        centroid_line_midpoint = centroid_line.interpolate(0.5, normalized=True)
        self.ax.annotate(
            f'{centroid_distance:.1f}m\nto photo\ncentroid',
            xy=(centroid_line_midpoint.x, centroid_line_midpoint.y),
            xytext=(0, 0),
            textcoords='offset points',
            fontsize=10,
            fontweight='bold',
            bbox=dict(
                boxstyle='round,pad=0.5',
                facecolor='orange',
                alpha=0.9,
                edgecolor='darkorange',
                linewidth=2
            ),
            ha='center',
            va='center',
            zorder=7
        )

        # Plot photo centroid marker
        self.ax.plot(
            photos_centroid.x,
            photos_centroid.y,
            marker='D',
            color='orange',
            markersize=15,
            markeredgecolor='black',
            markeredgewidth=2,
            zorder=6,
            label='Photo Centroid'
        )

        # Plot property point (large star marker)
        property_point_plot.plot(
            ax=self.ax,
            color='red',
            markersize=300,
            marker='*',
            edgecolor='black',
            linewidth=2,
            zorder=6
        )

        # Configure plot
        if title is None:
            title = f'Photo Locations Analysis\n({len(photos_gdf_plot)} photos captured)'
        self.ax.set_title(title, fontsize=16, fontweight='bold', pad=20)

        # Update axis labels based on CRS
        if add_basemap and CONTEXTILY_AVAILABLE:
            self.ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')
            self.ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
        else:
            self.ax.set_xlabel('Easting (m)', fontsize=12, fontweight='bold')
            self.ax.set_ylabel('Northing (m)', fontsize=12, fontweight='bold')

        self.ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)

        # Add legend
        self._add_legend(photos_gdf, show_distance_lines)

        # Adjust layout
        plt.tight_layout()

        return self.fig, self.ax

    def _draw_distance_lines(
        self,
        photos_gdf: gpd.GeoDataFrame,
        property_geom: Point,
        show_labels: bool = True,
        max_labels: int = 10
    ):
        """
        Draw lines connecting photo locations to property.

        Args:
            photos_gdf: GeoDataFrame with photo locations
            property_geom: Property geometry point
            show_labels: Whether to show distance labels
            max_labels: Maximum number of labels to show (for readability)
        """
        # Sort by distance to show labels on closest photos
        photos_sorted = photos_gdf.sort_values('distance_m') if 'distance_m' in photos_gdf.columns else photos_gdf

        for idx, (i, row) in enumerate(photos_sorted.iterrows()):
            photo_geom = row.geometry

            # Create line
            line = LineString([property_geom, photo_geom])

            # Plot the line
            line_gdf = gpd.GeoDataFrame(geometry=[line], crs=photos_gdf.crs)
            line_gdf.plot(
                ax=self.ax,
                color='gray',
                linewidth=1,
                linestyle='--',
                alpha=0.4,
                zorder=1
            )

            # Add distance label (only for first N photos for readability)
            if show_labels and idx < max_labels and 'distance_m' in photos_gdf.columns:
                midpoint = line.interpolate(0.5, normalized=True)

                self.ax.annotate(
                    f'{row["distance_m"]:.0f}m',
                    xy=(midpoint.x, midpoint.y),
                    xytext=(0, 0),
                    textcoords='offset points',
                    fontsize=7,
                    bbox=dict(
                        boxstyle='round,pad=0.2',
                        facecolor='white',
                        alpha=0.7,
                        edgecolor='gray'
                    ),
                    ha='center',
                    va='center',
                    zorder=3
                )

    def _add_legend(
        self,
        photos_gdf: gpd.GeoDataFrame,
        show_distance_lines: bool = False
    ):
        """
        Add comprehensive legend to the map.

        Args:
            photos_gdf: GeoDataFrame with photos
            show_distance_lines: Whether distance lines are shown
        """
        legend_elements = []

        # Photo categories
        category_counts = photos_gdf['category'].value_counts()
        for category, count in category_counts.items():
            color = photos_gdf[photos_gdf['category'] == category]['color'].iloc[0]
            legend_elements.append(
                Line2D(
                    [0], [0],
                    marker='o',
                    color='w',
                    markerfacecolor=color,
                    markersize=10,
                    markeredgecolor='white',
                    markeredgewidth=2,
                    label=f'{category} ({count})'
                )
            )

        # Separator
        legend_elements.append(Patch(facecolor='none', edgecolor='none', label=''))

        # Property marker
        legend_elements.append(
            Line2D(
                [0], [0],
                marker='*',
                color='w',
                markerfacecolor='red',
                markersize=15,
                markeredgecolor='black',
                markeredgewidth=2,
                label='Property Location'
            )
        )

        # Photo centroid marker
        legend_elements.append(
            Line2D(
                [0], [0],
                marker='D',
                color='w',
                markerfacecolor='orange',
                markersize=10,
                markeredgecolor='black',
                markeredgewidth=2,
                label='Photo Centroid'
            )
        )

        # Centroid distance line
        legend_elements.append(
            Line2D(
                [0], [0],
                color='orange',
                linewidth=3,
                linestyle='-',
                alpha=0.9,
                label='Distance to Centroid'
            )
        )

        # Distance lines
        if show_distance_lines:
            legend_elements.append(
                Line2D(
                    [0], [0],
                    color='gray',
                    linewidth=1,
                    linestyle='--',
                    alpha=0.4,
                    label='Distance to Property'
                )
            )

        self.ax.legend(
            handles=legend_elements,
            loc='upper right',
            fontsize=9,
            frameon=True,
            fancybox=True,
            shadow=True,
            title='Legend',
            title_fontsize=11
        )

    def save_map(self, output_path: str):
        """
        Save the current map to file.

        Args:
            output_path: Path for output image file
        """
        if self.fig is None:
            raise ValueError("Must create map first using create_map()")

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        print(f"✅ Map saved: {output_path}")

    def export_metadata(
        self,
        photos_gdf: gpd.GeoDataFrame,
        property_point: gpd.GeoDataFrame,
        property_address: str,
        output_path: str
    ) -> str:
        """
        Export photo location metadata to JSON.

        Args:
            photos_gdf: GeoDataFrame with photo locations
            property_point: GeoDataFrame with property location
            property_address: Property address string
            output_path: Path for output JSON file

        Returns:
            Path to saved JSON file
        """
        from datetime import datetime
        from geopy.distance import geodesic
        import json

        # Convert to WGS84 for lat/lon output
        photos_wgs84 = photos_gdf.to_crs(epsg=4326)
        property_wgs84 = property_point.to_crs(epsg=4326)
        prop_point = property_wgs84.geometry.iloc[0]

        # Calculate centroid
        centroid = photos_wgs84.geometry.unary_union.centroid
        centroid_distance = geodesic(
            (prop_point.y, prop_point.x),
            (centroid.y, centroid.x)
        ).meters

        # Prepare photo data
        photos_list = []
        for idx, row in photos_wgs84.iterrows():
            photos_list.append({
                'field': row['field'],
                'category': row['category'],
                'latitude': round(row.geometry.y, 7),
                'longitude': round(row.geometry.x, 7),
                'distance_to_property_m': round(row['distance_m'], 2) if 'distance_m' in row else None,
                'color': row['color']
            })

        # Category summary
        category_summary = {}
        for category in photos_wgs84['category'].unique():
            subset = photos_wgs84[photos_wgs84['category'] == category]
            category_summary[category] = {
                'count': len(subset),
                'color': subset['color'].iloc[0],
                'average_distance_m': round(subset['distance_m'].mean(), 2) if 'distance_m' in subset else None
            }

        # Build metadata structure
        metadata = {
            'generated_at': datetime.now().isoformat(),
            'property': {
                'address': property_address,
                'latitude': round(prop_point.y, 7),
                'longitude': round(prop_point.x, 7)
            },
            'photos': {
                'total_count': len(photos_wgs84),
                'category_count': len(photos_wgs84['category'].unique()),
                'items': photos_list
            },
            'photo_centroid': {
                'latitude': round(centroid.y, 7),
                'longitude': round(centroid.x, 7),
                'distance_to_property_m': round(centroid_distance, 2)
            },
            'distance_statistics': {
                'closest_photo_m': round(photos_wgs84['distance_m'].min(), 2) if 'distance_m' in photos_wgs84 else None,
                'furthest_photo_m': round(photos_wgs84['distance_m'].max(), 2) if 'distance_m' in photos_wgs84 else None,
                'average_distance_m': round(photos_wgs84['distance_m'].mean(), 2) if 'distance_m' in photos_wgs84 else None,
                'median_distance_m': round(photos_wgs84['distance_m'].median(), 2) if 'distance_m' in photos_wgs84 else None
            },
            'categories': category_summary,
            'bounds': {
                'north': round(photos_wgs84.total_bounds[3], 7),
                'south': round(photos_wgs84.total_bounds[1], 7),
                'east': round(photos_wgs84.total_bounds[2], 7),
                'west': round(photos_wgs84.total_bounds[0], 7)
            }
        }

        # Save to JSON
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"✅ Metadata saved: {output_path}")
        return str(output_path)

    def show_map(self):
        """Display the map interactively."""
        if self.fig is None:
            raise ValueError("Must create map first using create_map()")
        plt.show()

    def close_map(self):
        """Close the current figure."""
        if self.fig is not None:
            plt.close(self.fig)
            self.fig = None
            self.ax = None

    def create_complete_visualization(
        self,
        photos_gdf: gpd.GeoDataFrame,
        property_point: gpd.GeoDataFrame,
        output_path: str,
        property_address: Optional[str] = None,
        title: Optional[str] = None,
        show: bool = False,
        show_distance_lines: bool = True,
        show_distance_labels: bool = True,
        max_distance_labels: int = 10,
        add_basemap: bool = True,
        basemap_source: str = 'Google Satellite',
        export_metadata: bool = True
    ) -> Dict[str, str]:
        """
        Create and save complete visualization in one call.

        Args:
            photos_gdf: GeoDataFrame with photo locations
            property_point: GeoDataFrame with property location
            output_path: Path for output image file
            property_address: Property address string (for metadata)
            title: Optional custom title
            show: Whether to display map interactively
            show_distance_lines: Whether to draw connecting lines
            show_distance_labels: Whether to show distance values
            max_distance_labels: Maximum number of distance labels
            add_basemap: Whether to add a basemap underneath (default: True)
            basemap_source: Basemap style (default: 'Google Satellite')
            export_metadata: Whether to export metadata JSON (default: True)

        Returns:
            Dict with paths to saved files {'image': path, 'metadata': path}
        """
        # Create map
        self.create_map(
            photos_gdf,
            property_point,
            title,
            show_distance_lines=show_distance_lines,
            show_distance_labels=show_distance_labels,
            max_distance_labels=max_distance_labels,
            add_basemap=add_basemap,
            basemap_source=basemap_source
        )

        # Save image
        self.save_map(output_path)

        # Export metadata JSON
        result = {'image': str(output_path)}
        if export_metadata and property_address:
            metadata_path = str(Path(output_path).with_suffix('.json'))
            self.export_metadata(photos_gdf, property_point, property_address, metadata_path)
            result['metadata'] = metadata_path

        # Show if requested
        if show:
            self.show_map()
        else:
            self.close_map()

        return result


if __name__ == "__main__":
    print("Photo Visualization Pipeline - Use scripts/visualize_photo_locations.py to execute")
