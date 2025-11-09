"""
Spatial Visualization Pipeline

This pipeline creates visualizations of spatial analysis results including mesh blocks,
property locations, and Google Places data. It generates publication-quality maps with
color-coded categories and detailed legends.

Key Features:
- Visualize mesh blocks with color-coded categories
- Plot property locations and buffer zones
- Overlay Google Places impact data
- Generate comprehensive legends
- Export high-resolution maps

Author: Brendan Darcy
Date: 2025-10-05
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import pandas as pd
from shapely.geometry import LineString, Point
from shapely.ops import nearest_points


class SpatialVisualizationPipeline:
    """
    Pipeline for creating spatial visualizations of property risk analysis.

    This class handles map generation with mesh blocks, properties, buffers,
    and Google Places data overlay.
    """

    # Default color scheme for mesh block categories
    DEFAULT_CATEGORY_COLORS = {
        'Residential': '#FFFACD',      # Pale yellow (LemonChiffon)
        'Commercial': '#87CEEB',       # Sky blue
        'Industrial': '#D3D3D3',       # Light grey
        'Parkland': '#90EE90',         # Light green
        'Primary Production': '#DEB887', # Tan/brown
        'Water': '#4682B4',            # Steel blue
        'Education': '#FFB6C1',        # Light pink
        'Hospital/Medical': '#FF69B4', # Hot pink
        'Transport': '#FFA500',        # Orange
        'Other': '#E6E6FA'            # Lavender
    }

    def __init__(
        self,
        figsize: Tuple[int, int] = (18, 12),
        dpi: int = 200,
        category_colors: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the spatial visualization pipeline.

        Args:
            figsize: Figure size in inches (width, height)
            dpi: Resolution for saved images
            category_colors: Custom color mapping for mesh block categories
        """
        self.figsize = figsize
        self.dpi = dpi
        self.category_colors = category_colors or self.DEFAULT_CATEGORY_COLORS

        self.fig: Optional[plt.Figure] = None
        self.ax: Optional[plt.Axes] = None

    def load_places_from_json(
        self,
        places_json_path: str,
        target_crs: str = 'EPSG:3577'
    ) -> Optional[gpd.GeoDataFrame]:
        """
        Load Google Places data from property_impacts.json.

        Args:
            places_json_path: Path to property_impacts.json
            target_crs: CRS to reproject places to (for metric visualization)

        Returns:
            GeoDataFrame with places, or None if no places found
        """
        with open(places_json_path, 'r') as f:
            places_data = json.load(f)

        places_list = []
        for level, categories in places_data['impact_analysis'].items():
            radius = places_data['level_radii'][level]
            for category, details in categories.items():
                if details['closest_place']:
                    place = details['closest_place']
                    places_list.append({
                        'name': place['name'],
                        'latitude': place['latitude'],
                        'longitude': place['longitude'],
                        'category': category,
                        'level': level,
                        'radius': radius,
                        'distance_m': place['distance_meters'],
                        'address': place.get('formatted_address', '')
                    })

        if not places_list:
            print("No places found in analysis data")
            return None

        places_gdf = gpd.GeoDataFrame(
            places_list,
            geometry=gpd.points_from_xy(
                [p['longitude'] for p in places_list],
                [p['latitude'] for p in places_list]
            ),
            crs='EPSG:4326'
        ).to_crs(target_crs)

        print(f"✅ Loaded {len(places_gdf)} places from Google Places API")

        return places_gdf

    def create_map(
        self,
        mesh_blocks: gpd.GeoDataFrame,
        property_point: gpd.GeoDataFrame,
        property_buffer: gpd.GeoSeries,
        places: Optional[gpd.GeoDataFrame] = None,
        title: Optional[str] = None,
        property_boundary: Optional[gpd.GeoDataFrame] = None,
        non_residential_distances: Optional[gpd.GeoDataFrame] = None,
        show_distance_lines: bool = True,
        max_distance_lines: int = 5
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        Create visualization map with all spatial layers.

        Args:
            mesh_blocks: GeoDataFrame of mesh blocks in metric CRS
            property_point: GeoDataFrame with property location in metric CRS
            property_buffer: GeoSeries with buffer geometry in metric CRS
            places: Optional GeoDataFrame with Google Places data
            title: Optional custom title
            property_boundary: Optional GeoDataFrame with property boundary polygon
            non_residential_distances: Optional GeoDataFrame with distance calculations
            show_distance_lines: Whether to draw distance lines (default: True)
            max_distance_lines: Maximum number of distance lines to show (default: 5)

        Returns:
            Tuple of (figure, axes)
        """
        self.fig, self.ax = plt.subplots(figsize=self.figsize)

        # Reserve space on the right for tables (map takes left 70%, tables get right 30%)
        self.fig.subplots_adjust(left=0.05, right=0.68, top=0.93, bottom=0.07)

        # Plot mesh blocks by category
        for category in mesh_blocks['MB_CAT21'].unique():
            subset = mesh_blocks[mesh_blocks['MB_CAT21'] == category]
            color = self.category_colors.get(category, '#CCCCCC')
            subset.plot(
                ax=self.ax,
                color=color,
                alpha=0.7,
                edgecolor='black',
                linewidth=0.5
            )

        # Plot Google Places points with labels
        if places is not None and len(places) > 0:
            places.plot(
                ax=self.ax,
                color='blue',
                markersize=50,
                marker='o',
                edgecolor='white',
                linewidth=1,
                zorder=4,
                alpha=0.8
            )

            # Add labels for each place
            for idx, row in places.iterrows():
                self.ax.annotate(
                    f"{row['name']}\n({row['category']})",
                    xy=(row.geometry.x, row.geometry.y),
                    xytext=(5, 5),
                    textcoords='offset points',
                    fontsize=8,
                    bbox=dict(
                        boxstyle='round,pad=0.3',
                        facecolor='white',
                        alpha=0.7,
                        edgecolor='blue'
                    ),
                    ha='left'
                )

        # Plot buffer boundary
        buffer_gdf = gpd.GeoDataFrame(geometry=property_buffer, crs=mesh_blocks.crs)
        buffer_gdf.boundary.plot(
            ax=self.ax,
            color='red',
            linewidth=3,
            linestyle='--'
        )

        # Plot property boundary if available
        if property_boundary is not None and not property_boundary.empty:
            property_boundary.boundary.plot(
                ax=self.ax,
                color='darkred',
                linewidth=2,
                linestyle='-',
                zorder=4
            )

        # Plot property point (star marker)
        property_point.plot(
            ax=self.ax,
            color='red',
            markersize=200,
            marker='*',
            edgecolor='black',
            linewidth=1.5,
            zorder=5
        )

        # Draw distance lines to non-residential mesh blocks
        if show_distance_lines and non_residential_distances is not None and len(non_residential_distances) > 0:
            self._draw_distance_lines(
                property_point if property_boundary is None else property_boundary,
                non_residential_distances,
                max_lines=max_distance_lines
            )

        # Configure plot
        if title is None:
            title = f'Mesh Blocks Analysis\n({len(mesh_blocks)} mesh blocks found)'
        self.ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        self.ax.set_xlabel('Easting (m)', fontsize=12, fontweight='bold')
        self.ax.set_ylabel('Northing (m)', fontsize=12, fontweight='bold')
        self.ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)

        # Add data tables if available
        self._add_data_tables(places, non_residential_distances)

        # Create legend
        self._add_legend(
            mesh_blocks,
            places,
            show_distance_lines=(show_distance_lines and non_residential_distances is not None),
            has_boundary=(property_boundary is not None and not property_boundary.empty)
        )

        return self.fig, self.ax

    def _draw_distance_lines(
        self,
        property_geom: gpd.GeoDataFrame,
        non_residential_distances: gpd.GeoDataFrame,
        max_lines: int = 5
    ):
        """
        Draw distance lines from property boundary to nearest non-residential mesh blocks.

        Args:
            property_geom: GeoDataFrame with property boundary or point
            non_residential_distances: GeoDataFrame with non-residential mesh blocks and distances
            max_lines: Maximum number of distance lines to draw
        """
        # Get the property geometry (boundary or point)
        prop_geom = property_geom.geometry.iloc[0]

        # Get the closest mesh block for each unique category (not just top 5 overall)
        # Group by category and take the first (closest) from each group
        closest_per_category = non_residential_distances.groupby('MB_CAT21').first().reset_index()

        # Sort by distance and take top N
        closest_per_category = closest_per_category.sort_values('distance_to_property_m').head(max_lines)

        for idx, row in closest_per_category.iterrows():
            mesh_geom = row.geometry
            distance_m = row['distance_to_property_m']
            category = row['MB_CAT21']

            # Find the nearest points between property and mesh block
            nearest_prop, nearest_mesh = nearest_points(prop_geom, mesh_geom)

            # Create line between nearest points
            line = LineString([nearest_prop, nearest_mesh])

            # Plot the line
            line_gdf = gpd.GeoDataFrame(geometry=[line], crs=property_geom.crs)
            line_gdf.plot(
                ax=self.ax,
                color='purple',
                linewidth=2,
                linestyle='-',
                alpha=0.7,
                zorder=3
            )

            # Calculate midpoint for label
            midpoint = line.interpolate(0.5, normalized=True)

            # Add distance label
            self.ax.annotate(
                f'{distance_m:.0f}m\n{category}',
                xy=(midpoint.x, midpoint.y),
                xytext=(0, 0),
                textcoords='offset points',
                fontsize=9,
                fontweight='bold',
                bbox=dict(
                    boxstyle='round,pad=0.4',
                    facecolor='white',
                    alpha=0.9,
                    edgecolor='purple',
                    linewidth=1.5
                ),
                ha='center',
                va='center',
                zorder=6
            )

            # Highlight the mesh block centroid
            centroid = mesh_geom.centroid
            self.ax.plot(
                centroid.x,
                centroid.y,
                marker='o',
                color='purple',
                markersize=8,
                markeredgecolor='white',
                markeredgewidth=1.5,
                zorder=5
            )

    def _add_data_tables(
        self,
        places: Optional[gpd.GeoDataFrame],
        non_residential_distances: Optional[gpd.GeoDataFrame]
    ):
        """
        Add data tables showing impacts and distances.

        Args:
            places: Optional GeoDataFrame with Google Places data
            non_residential_distances: Optional GeoDataFrame with distance calculations
        """
        # Position tables in the whitespace to the right of the axes
        # Tables use axes coordinates, and we've reserved space to the right
        # Since axes only goes to 68% of figure, we position tables beyond axes (>1.0)
        table_x_pos = 1.05  # Just beyond the right edge of the axes
        table_width = 0.45  # Width relative to axes
        current_y_pos = 0.95  # Start from top

        # Table 1: Non-Residential Mesh Block Distances
        if non_residential_distances is not None and len(non_residential_distances) > 0:
            # Get closest per category
            closest_per_category = non_residential_distances.groupby('MB_CAT21').first().reset_index()
            closest_per_category = closest_per_category.sort_values('distance_to_property_m').head(10)

            # Prepare table data
            table_data = []
            table_data.append(['Category', 'Distance (m)'])
            for idx, row in closest_per_category.iterrows():
                table_data.append([
                    row['MB_CAT21'],
                    f"{row['distance_to_property_m']:.0f}"
                ])

            # Calculate table height based on number of rows
            table_height = min(0.25, len(table_data) * 0.025)

            # Position table going downward from current position
            table_y_pos = current_y_pos - table_height

            # Create table
            table = self.ax.table(
                cellText=table_data,
                cellLoc='left',
                loc='center',
                bbox=[table_x_pos, table_y_pos, table_width, table_height]
            )

            # Style the table
            table.auto_set_font_size(False)
            table.set_fontsize(8)
            table.scale(1, 1.5)

            # Header styling
            for i in range(2):
                cell = table[(0, i)]
                cell.set_facecolor('#8B7EC8')
                cell.set_text_props(weight='bold', color='white')

            # Alternating row colors
            for i in range(1, len(table_data)):
                for j in range(2):
                    cell = table[(i, j)]
                    if i % 2 == 0:
                        cell.set_facecolor('#F0F0F0')
                    else:
                        cell.set_facecolor('white')
                    cell.set_alpha(0.9)

            # Add title above table using axes coordinates to match table position
            title_x = table_x_pos + table_width / 2
            title_y = current_y_pos + 0.02
            self.ax.text(
                title_x, title_y,
                'Non-Residential Distances',
                fontsize=10,
                fontweight='bold',
                ha='center',
                transform=self.ax.transAxes,
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, edgecolor='purple')
            )

            # Move position down for next table
            current_y_pos = table_y_pos - 0.05

        # Table 2: Google Places Impacts
        if places is not None and len(places) > 0:
            # Prepare table data
            table_data = []
            table_data.append(['Place', 'Category', 'Distance (m)'])

            # Sort by distance and take top 10
            places_sorted = places.sort_values('distance_m').head(10)

            for idx, row in places_sorted.iterrows():
                # Truncate name if too long
                name = row['name']
                if len(name) > 20:
                    name = name[:17] + '...'

                table_data.append([
                    name,
                    row['category'],
                    f"{row['distance_m']:.0f}"
                ])

            # Calculate table height based on number of rows
            table_height = min(0.35, len(table_data) * 0.03)

            # Position table going downward from current position
            table_y_pos = current_y_pos - table_height

            # Create table
            table = self.ax.table(
                cellText=table_data,
                cellLoc='left',
                loc='center',
                bbox=[table_x_pos, table_y_pos, table_width, table_height]
            )

            # Style the table
            table.auto_set_font_size(False)
            table.set_fontsize(7)
            table.scale(1, 1.5)

            # Header styling
            for i in range(3):
                cell = table[(0, i)]
                cell.set_facecolor('#4169E1')
                cell.set_text_props(weight='bold', color='white')

            # Alternating row colors
            for i in range(1, len(table_data)):
                for j in range(3):
                    cell = table[(i, j)]
                    if i % 2 == 0:
                        cell.set_facecolor('#F0F0F0')
                    else:
                        cell.set_facecolor('white')
                    cell.set_alpha(0.9)

            # Add title above table using axes coordinates to match table position
            title_x = table_x_pos + table_width / 2
            title_y = current_y_pos + 0.02
            self.ax.text(
                title_x, title_y,
                'Google Places',
                fontsize=10,
                fontweight='bold',
                ha='center',
                transform=self.ax.transAxes,
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, edgecolor='blue')
            )

    def _add_legend(
        self,
        mesh_blocks: gpd.GeoDataFrame,
        places: Optional[gpd.GeoDataFrame],
        show_distance_lines: bool = False,
        has_boundary: bool = False
    ):
        """
        Add comprehensive legend to the map.

        Args:
            mesh_blocks: GeoDataFrame of mesh blocks
            places: Optional GeoDataFrame with places
            show_distance_lines: Whether distance lines are shown
            has_boundary: Whether property boundary is shown
        """
        legend_elements = []

        # Mesh block categories
        category_counts = mesh_blocks['MB_CAT21'].value_counts()
        for category, count in category_counts.items():
            color = self.category_colors.get(category, '#CCCCCC')
            legend_elements.append(
                Patch(
                    facecolor=color,
                    edgecolor='black',
                    alpha=0.7,
                    linewidth=0.5,
                    label=f'{category} ({count})'
                )
            )

        # Separator
        legend_elements.append(Patch(facecolor='none', edgecolor='none', label=''))

        # Places
        if places is not None and len(places) > 0:
            legend_elements.append(
                Line2D(
                    [0], [0],
                    marker='o',
                    color='w',
                    markerfacecolor='blue',
                    markersize=10,
                    markeredgecolor='white',
                    markeredgewidth=1,
                    label=f'Google Places ({len(places)})'
                )
            )

        # Property marker
        legend_elements.append(
            Line2D(
                [0], [0],
                marker='*',
                color='w',
                markerfacecolor='red',
                markersize=15,
                markeredgecolor='black',
                markeredgewidth=1.5,
                label='Your Property'
            )
        )

        # Buffer
        legend_elements.append(
            Line2D(
                [0], [0],
                color='red',
                linewidth=3,
                linestyle='--',
                label='Search Buffer'
            )
        )

        # Property boundary
        if has_boundary:
            legend_elements.append(
                Line2D(
                    [0], [0],
                    color='darkred',
                    linewidth=2,
                    linestyle='-',
                    label='Property Boundary'
                )
            )

        # Distance lines
        if show_distance_lines:
            legend_elements.append(
                Line2D(
                    [0], [0],
                    color='purple',
                    linewidth=2,
                    linestyle='-',
                    alpha=0.7,
                    label='Distance to Non-Residential'
                )
            )

        self.ax.legend(
            handles=legend_elements,
            loc='upper left',
            fontsize=10,
            frameon=True,
            fancybox=True,
            shadow=True,
            title='Legend',
            title_fontsize=12
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

        # Subplot adjustment is already done in create_map()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        print(f"✅ Map saved: {output_path}")

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

    def print_summary(
        self,
        mesh_blocks: gpd.GeoDataFrame,
        places: Optional[gpd.GeoDataFrame] = None
    ):
        """
        Print summary statistics for the visualization.

        Args:
            mesh_blocks: GeoDataFrame of mesh blocks
            places: Optional GeoDataFrame with places
        """
        print("\n" + "=" * 60)
        print("📊 VISUALIZATION SUMMARY")
        print("=" * 60)

        # Mesh blocks by category
        category_counts = mesh_blocks['MB_CAT21'].value_counts()
        print("\nMesh Block Categories:")
        for category, count in category_counts.items():
            color = self.category_colors.get(category, '#CCCCCC')
            pct = count / len(mesh_blocks) * 100
            print(f"  {category:25s}: {count:3d} blocks ({pct:5.1f}%) - {color}")

        # Places summary
        if places is not None and len(places) > 0:
            print(f"\nGoogle Places: {len(places)} locations")
            level_counts = places['level'].value_counts()
            for level, count in level_counts.items():
                print(f"  {level}: {count} places")

    def create_complete_visualization(
        self,
        mesh_blocks: gpd.GeoDataFrame,
        property_point: gpd.GeoDataFrame,
        property_buffer: gpd.GeoSeries,
        output_path: str,
        places_json_path: Optional[str] = None,
        title: Optional[str] = None,
        show: bool = False,
        property_boundary: Optional[gpd.GeoDataFrame] = None,
        non_residential_distances: Optional[gpd.GeoDataFrame] = None,
        show_distance_lines: bool = True,
        max_distance_lines: int = 5
    ) -> str:
        """
        Create and save complete visualization in one call.

        Args:
            mesh_blocks: GeoDataFrame of mesh blocks in metric CRS
            property_point: GeoDataFrame with property location in metric CRS
            property_buffer: GeoSeries with buffer geometry in metric CRS
            output_path: Path for output image file
            places_json_path: Optional path to property_impacts.json
            title: Optional custom title
            show: Whether to display map interactively
            property_boundary: Optional GeoDataFrame with property boundary polygon
            non_residential_distances: Optional GeoDataFrame with distance calculations
            show_distance_lines: Whether to draw distance lines (default: True)
            max_distance_lines: Maximum number of distance lines to show (default: 5)

        Returns:
            Path to saved image file
        """
        # Load places if provided
        places = None
        if places_json_path:
            places = self.load_places_from_json(
                places_json_path,
                target_crs=str(mesh_blocks.crs)
            )

        # Create map
        self.create_map(
            mesh_blocks,
            property_point,
            property_buffer,
            places,
            title,
            property_boundary=property_boundary,
            non_residential_distances=non_residential_distances,
            show_distance_lines=show_distance_lines,
            max_distance_lines=max_distance_lines
        )

        # Print summary
        self.print_summary(mesh_blocks, places)

        # Save
        self.save_map(output_path)

        # Show if requested
        if show:
            self.show_map()
        else:
            self.close_map()

        return str(output_path)
