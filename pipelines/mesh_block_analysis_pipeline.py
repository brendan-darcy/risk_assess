"""
Mesh Block Analysis Pipeline

This pipeline analyzes Australian Statistical Geography Standard (ASGS) mesh blocks
in relation to a property location. It identifies which mesh block contains a property
and finds all mesh blocks within a specified radius.

Key Features:
- Load ASGS mesh block shapefiles
- Identify mesh block containing a property
- Find mesh blocks within a radius (with metric CRS for accurate buffering)
- Export results to multiple formats (GeoJSON, CSV, Shapefile, TXT)
- Generate visualization maps with color-coded categories

Author: Brendan Darcy
Date: 2025-10-05
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd


class MeshBlockAnalysisPipeline:
    """
    Pipeline for analyzing mesh blocks in relation to a property location.

    This class handles loading mesh block data, spatial analysis, and output generation
    for property risk assessment workflows.
    """

    def __init__(
        self,
        shapefile_path: str,
        buffer_distance: int = 2000,
        metric_crs: str = 'EPSG:3577',  # GDA2020 Australian Albers
        output_crs: str = 'EPSG:4326'   # WGS84
    ):
        """
        Initialize the mesh block analysis pipeline.

        Args:
            shapefile_path: Path to ASGS mesh block shapefile
            buffer_distance: Search radius in meters (default: 2000m / 2km)
            metric_crs: CRS for metric calculations (default: EPSG:3577 Australian Albers)
            output_crs: CRS for output files (default: EPSG:4326 WGS84)
        """
        self.shapefile_path = Path(shapefile_path)
        self.buffer_distance = buffer_distance
        self.metric_crs = metric_crs
        self.output_crs = output_crs

        self.mesh_blocks_gdf: Optional[gpd.GeoDataFrame] = None
        self.property_gdf: Optional[gpd.GeoDataFrame] = None
        self.property_meshblock: Optional[gpd.GeoDataFrame] = None
        self.nearby_meshblocks: Optional[gpd.GeoDataFrame] = None

    def load_mesh_blocks(self) -> gpd.GeoDataFrame:
        """
        Load mesh block shapefile.

        Returns:
            GeoDataFrame containing mesh block data
        """
        print(f"Loading mesh blocks from: {self.shapefile_path}")
        self.mesh_blocks_gdf = gpd.read_file(self.shapefile_path)
        print(f"✅ Loaded {len(self.mesh_blocks_gdf)} mesh blocks")
        print(f"   CRS: {self.mesh_blocks_gdf.crs}")
        print(f"   Categories: {self.mesh_blocks_gdf['MB_CAT21'].unique().tolist()}")
        return self.mesh_blocks_gdf

    def load_property_from_parcel(
        self,
        parcel_json_path: str
    ) -> gpd.GeoDataFrame:
        """
        Load property data from parcel.json file.

        Args:
            parcel_json_path: Path to parcel.json file

        Returns:
            GeoDataFrame containing property point
        """
        with open(parcel_json_path, 'r') as f:
            parcel_data = json.load(f)

        return self.create_property_gdf(
            longitude=parcel_data['coordinates']['longitude'],
            latitude=parcel_data['coordinates']['latitude'],
            property_id=parcel_data['property_id'],
            address=parcel_data['address']
        )

    def load_property_from_corelogic(
        self,
        address: Optional[str] = None,
        property_id: Optional[int] = None,
        property_processor=None,
        geo_client=None
    ) -> Tuple[gpd.GeoDataFrame, Dict[str, Any]]:
        """
        Load property data directly from CoreLogic APIs.

        Args:
            address: Property address (if known)
            property_id: CoreLogic property ID (if known)
            property_processor: PropertyDataProcessor instance (created if None)
            geo_client: GeospatialAPIClient instance (created if None)

        Returns:
            Tuple of (GeoDataFrame, property_info dict)

        Raises:
            ValueError: If neither address nor property_id provided
            RuntimeError: If property not found or coordinates unavailable
        """
        if not address and not property_id:
            raise ValueError("Must provide either address or property_id")

        # Import here to avoid circular dependency
        if property_processor is None:
            from pipelines.property_data_processor import PropertyDataProcessor
            from pipelines.pipeline_utils import ProgressReporter
            reporter = ProgressReporter("Property Lookup")
            property_processor = PropertyDataProcessor(reporter=reporter)

        if geo_client is None:
            from pipelines.geospatial_api_client import GeospatialAPIClient
            geo_client = GeospatialAPIClient.from_env()

        # Get property ID from address if needed
        if address and not property_id:
            property_info = property_processor.get_property_info_from_address(address)
            if not property_info:
                raise RuntimeError(f"Could not find property for address: {address}")
            property_id = property_info['property_id']
            print(f"✅ Found property ID: {property_id}")
        else:
            address = f"Property {property_id}"
            property_info = {'property_id': property_id}

        # Get property coordinates from location endpoint
        property_details = property_processor.api_client.get_property_details(
            property_id,
            endpoints_list=['location']
        )
        location_data = property_details.get('location', {})

        longitude = location_data.get('longitude')
        latitude = location_data.get('latitude')

        if not longitude or not latitude:
            raise RuntimeError(f"Could not get coordinates for property {property_id}")

        print(f"✅ Property coordinates: ({longitude}, {latitude})")

        # Create GeoDataFrame
        gdf = self.create_property_gdf(
            longitude=longitude,
            latitude=latitude,
            property_id=property_id,
            address=address
        )

        return gdf, property_info

    def create_property_gdf(
        self,
        longitude: float,
        latitude: float,
        property_id: Optional[int] = None,
        address: Optional[str] = None
    ) -> gpd.GeoDataFrame:
        """
        Create a GeoDataFrame from property coordinates.

        Args:
            longitude: Property longitude (WGS84)
            latitude: Property latitude (WGS84)
            property_id: Optional property ID
            address: Optional property address

        Returns:
            GeoDataFrame with property point in mesh block CRS
        """
        property_point = Point(longitude, latitude)

        self.property_gdf = gpd.GeoDataFrame(
            {
                'property_id': [property_id],
                'address': [address],
                'longitude': [longitude],
                'latitude': [latitude]
            },
            geometry=[property_point],
            crs='EPSG:4326'
        )

        # Reproject to match mesh blocks CRS
        if self.mesh_blocks_gdf is not None:
            self.property_gdf = self.property_gdf.to_crs(self.mesh_blocks_gdf.crs)

        print(f"✅ Property loaded: ({longitude}, {latitude})")
        if address:
            print(f"   Address: {address}")

        return self.property_gdf

    def identify_property_meshblock(self) -> Optional[Dict[str, Any]]:
        """
        Identify which mesh block contains the property.

        Returns:
            Dictionary with mesh block details, or None if not found
        """
        if self.property_gdf is None or self.mesh_blocks_gdf is None:
            raise ValueError("Must load property and mesh blocks first")

        self.property_meshblock = gpd.sjoin(
            self.property_gdf,
            self.mesh_blocks_gdf,
            how='left',
            predicate='within'
        )

        if not self.property_meshblock.empty and self.property_meshblock['MB_CODE21'].notna().any():
            mb_code = self.property_meshblock['MB_CODE21'].iloc[0]

            result = {
                'mb_code': mb_code,
                'mb_category': self.property_meshblock['MB_CAT21'].iloc[0],
                'sa2_name': self.property_meshblock['SA2_NAME21'].iloc[0],
                'sa3_name': self.property_meshblock['SA3_NAME21'].iloc[0],
                'state': self.property_meshblock['STE_NAME21'].iloc[0],
                'area_sqkm': self.property_meshblock['AREASQKM21'].iloc[0]
            }

            print("=" * 60)
            print("✅ PROPERTY MESH BLOCK FOUND")
            print("=" * 60)
            print(f"Mesh Block Code: {result['mb_code']}")
            print(f"Suburb/Area: {result['sa2_name']}")
            print(f"State: {result['state']}")
            print(f"Category: {result['mb_category']}")
            print(f"Area (sq km): {result['area_sqkm']}")

            return result
        else:
            print("❌ Property not found in any mesh block")
            print("Check coordinates or CRS projection")
            return None

    def find_nearby_meshblocks(self) -> gpd.GeoDataFrame:
        """
        Find all mesh blocks within buffer distance of property.

        Returns:
            GeoDataFrame of nearby mesh blocks in metric CRS
        """
        if self.property_gdf is None or self.mesh_blocks_gdf is None:
            raise ValueError("Must load property and mesh blocks first")

        # Reproject to metric CRS for accurate buffering
        property_metric = self.property_gdf.to_crs(self.metric_crs)
        mesh_blocks_metric = self.mesh_blocks_gdf.to_crs(self.metric_crs)

        # Create buffer
        property_buffer = property_metric.buffer(self.buffer_distance)

        # Find intersecting mesh blocks
        self.nearby_meshblocks = mesh_blocks_metric[
            mesh_blocks_metric.intersects(property_buffer.iloc[0])
        ]

        print("=" * 60)
        print("🔍 MESH BLOCKS WITHIN RADIUS")
        print("=" * 60)
        print(f"Buffer distance: {self.buffer_distance}m ({self.buffer_distance/1000}km)")
        print(f"✅ Found {len(self.nearby_meshblocks)} mesh blocks")
        print(f"\nSummary by category:")
        print(self.nearby_meshblocks['MB_CAT21'].value_counts())

        return self.nearby_meshblocks

    def export_results(
        self,
        output_dir: str,
        prefix: str = "meshblocks"
    ) -> Dict[str, str]:
        """
        Export nearby mesh blocks to multiple formats.

        Args:
            output_dir: Directory for output files
            prefix: Filename prefix (default: "meshblocks")

        Returns:
            Dictionary mapping format to output path
        """
        if self.nearby_meshblocks is None:
            raise ValueError("Must find nearby mesh blocks first")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Convert to output CRS
        nearby_output = self.nearby_meshblocks.to_crs(self.output_crs)

        output_files = {}

        print("=" * 60)
        print("💾 EXPORTING RESULTS")
        print("=" * 60)

        # 1. GeoJSON
        geojson_path = output_path / f"{prefix}_within_{self.buffer_distance}m.geojson"
        nearby_output.to_file(geojson_path, driver='GeoJSON')
        output_files['geojson'] = str(geojson_path)
        print(f"✅ GeoJSON: {geojson_path}")

        # 2. CSV (attributes only)
        csv_path = output_path / f"{prefix}_within_{self.buffer_distance}m.csv"
        nearby_output.drop(columns='geometry').to_csv(csv_path, index=False)
        output_files['csv'] = str(csv_path)
        print(f"✅ CSV: {csv_path}")

        # 3. Shapefile
        shp_path = output_path / f"{prefix}_within_{self.buffer_distance}m.shp"
        nearby_output.to_file(shp_path)
        output_files['shapefile'] = str(shp_path)
        print(f"✅ Shapefile: {shp_path}")

        # 4. Text file with mesh block codes
        txt_path = output_path / f"{prefix}_codes_{self.buffer_distance}m.txt"
        with open(txt_path, 'w') as f:
            if self.property_gdf is not None:
                lon = self.property_gdf['longitude'].iloc[0]
                lat = self.property_gdf['latitude'].iloc[0]
                f.write(f"Property Location: ({lon}, {lat})\n")
                if self.property_gdf['address'].iloc[0]:
                    f.write(f"Address: {self.property_gdf['address'].iloc[0]}\n")
            f.write(f"Buffer Distance: {self.buffer_distance}m\n")
            f.write(f"Total Mesh Blocks Found: {len(self.nearby_meshblocks)}\n\n")
            f.write("Mesh Block Codes:\n")
            for code in self.nearby_meshblocks['MB_CODE21'].values:
                f.write(f"{code}\n")
        output_files['txt'] = str(txt_path)
        print(f"✅ Text file: {txt_path}")

        print(f"\n📊 Exported {len(self.nearby_meshblocks)} mesh blocks")

        return output_files

    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Get summary statistics about nearby mesh blocks.

        Returns:
            Dictionary with summary statistics
        """
        if self.nearby_meshblocks is None:
            raise ValueError("Must find nearby mesh blocks first")

        category_counts = self.nearby_meshblocks['MB_CAT21'].value_counts()

        summary = {
            'total_meshblocks': len(self.nearby_meshblocks),
            'buffer_distance_m': self.buffer_distance,
            'categories': {
                cat: {
                    'count': int(count),
                    'percentage': round(count / len(self.nearby_meshblocks) * 100, 1)
                }
                for cat, count in category_counts.items()
            },
            'total_area_sqkm': round(self.nearby_meshblocks['AREASQKM21'].sum(), 4)
        }

        return summary

    def run_full_analysis(
        self,
        output_dir: str,
        parcel_json_path: Optional[str] = None,
        address: Optional[str] = None,
        property_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Run complete mesh block analysis workflow.

        Args:
            output_dir: Directory for output files
            parcel_json_path: Path to parcel.json with property data (optional)
            address: Property address (optional, fetches from CoreLogic)
            property_id: CoreLogic property ID (optional)

        Returns:
            Dictionary with analysis results and output paths

        Note:
            Must provide one of: parcel_json_path, address, or property_id
        """
        # Load mesh blocks
        self.load_mesh_blocks()

        # Load property data
        if parcel_json_path:
            self.load_property_from_parcel(parcel_json_path)
            property_info = None
        elif address or property_id:
            _, property_info = self.load_property_from_corelogic(
                address=address,
                property_id=property_id
            )
        else:
            raise ValueError("Must provide parcel_json_path, address, or property_id")

        # Analysis
        property_mb = self.identify_property_meshblock()
        self.find_nearby_meshblocks()

        # Export
        output_files = self.export_results(output_dir)

        # Statistics
        stats = self.get_summary_statistics()

        return {
            'property_meshblock': property_mb,
            'property_info': property_info,
            'statistics': stats,
            'output_files': output_files
        }
