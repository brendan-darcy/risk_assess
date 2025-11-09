"""
GIS Utilities for Risk Assessment System

This module provides centralized GIS operations to reduce code duplication
across pipelines. All CRS conversions, distance calculations, and common
GeoDataFrame operations should use these utilities.

Usage:
    from pipelines.gis_utils import GISUtils

    # Create point GeoDataFrame
    gdf = GISUtils.create_point_gdf(151.2093, -33.8688, {'name': 'Sydney'})

    # Ensure correct CRS
    gdf = GISUtils.ensure_crs(gdf, GISUtils.AUSTRALIAN_ALBERS)

    # Calculate distance
    distance = GISUtils.calculate_distance_meters(point1, point2)

Author: Brendan Darcy
Date: 2025-11-09
"""

from typing import Union, Tuple, Dict, Any, Optional
import geopandas as gpd
from shapely.geometry import Point, Polygon
import numpy as np


class GISUtils:
    """Centralized GIS utility functions for spatial operations"""

    # Standard CRS definitions
    WGS84 = 'EPSG:4326'  # World Geodetic System 1984
    WEB_MERCATOR = 'EPSG:3857'  # Web Mercator (used by Google Maps, etc.)
    AUSTRALIAN_ALBERS = 'EPSG:3577'  # Australian Albers Equal Area (GDA2020)

    @staticmethod
    def create_point_gdf(
        longitude: float,
        latitude: float,
        attributes: Optional[Dict[str, Any]] = None,
        source_crs: str = 'EPSG:4326',
        target_crs: Optional[str] = None
    ) -> gpd.GeoDataFrame:
        """
        Create GeoDataFrame from point coordinates with optional reprojection.

        This function creates a GeoDataFrame from longitude/latitude coordinates,
        optionally reprojecting to a different coordinate reference system.

        Args:
            longitude: Point longitude in source CRS (typically WGS84)
            latitude: Point latitude in source CRS (typically WGS84)
            attributes: Optional dictionary of additional attributes to include
            source_crs: Source coordinate reference system. Defaults to 'EPSG:4326' (WGS84)
            target_crs: Target CRS for reprojection. If None, no reprojection occurs

        Returns:
            GeoDataFrame containing single point with specified attributes

        Raises:
            ValueError: If longitude/latitude are invalid or CRS conversion fails

        Example:
            >>> gdf = GISUtils.create_point_gdf(151.2093, -33.8688, {'name': 'Sydney'})
            >>> gdf = GISUtils.create_point_gdf(
            ...     151.2093, -33.8688,
            ...     attributes={'name': 'Sydney'},
            ...     target_crs=GISUtils.AUSTRALIAN_ALBERS
            ... )

        Note:
            - Input coordinates should be in (longitude, latitude) order
            - For Australian data, EPSG:3577 (Australian Albers) is recommended for metric calculations
        """
        # Validate coordinates
        if not -180 <= longitude <= 180:
            raise ValueError(f"Invalid longitude: {longitude} (must be between -180 and 180)")
        if not -90 <= latitude <= 90:
            raise ValueError(f"Invalid latitude: {latitude} (must be between -90 and 90)")

        point = Point(longitude, latitude)
        data = attributes or {}
        gdf = gpd.GeoDataFrame(data, geometry=[point], crs=source_crs)

        if target_crs and target_crs != source_crs:
            gdf = gdf.to_crs(target_crs)

        return gdf

    @staticmethod
    def ensure_crs(
        gdf: gpd.GeoDataFrame,
        target_crs: str,
        reporter = None
    ) -> gpd.GeoDataFrame:
        """
        Ensure GeoDataFrame is in target CRS, reproject if necessary.

        Args:
            gdf: Input GeoDataFrame
            target_crs: Target coordinate reference system
            reporter: Optional ProgressReporter for logging

        Returns:
            GeoDataFrame in target CRS

        Raises:
            ValueError: If GeoDataFrame has no CRS and none can be inferred

        Example:
            >>> gdf = GISUtils.ensure_crs(gdf, GISUtils.AUSTRALIAN_ALBERS)
        """
        if gdf.crs is None:
            if reporter:
                reporter.warning(f"GeoDataFrame has no CRS, assuming {target_crs}")
            gdf = gdf.set_crs(target_crs)
        elif str(gdf.crs) != target_crs:
            if reporter:
                reporter.info(f"Reprojecting from {gdf.crs} to {target_crs}")
            gdf = gdf.to_crs(target_crs)

        return gdf

    @staticmethod
    def calculate_distance_meters(
        point1: Union[Point, Tuple[float, float]],
        point2: Union[Point, Tuple[float, float]],
        use_geodesic: bool = True
    ) -> float:
        """
        Calculate distance between two points in meters.

        Args:
            point1: First point (Point object or (lat, lon) tuple)
            point2: Second point (Point object or (lat, lon) tuple)
            use_geodesic: Use geodesic distance for accuracy (default: True)
                         If False, uses Euclidean distance (assumes metric CRS)

        Returns:
            Distance in meters

        Example:
            >>> # Using tuples (lat, lon format for geodesic)
            >>> distance = GISUtils.calculate_distance_meters(
            ...     (-33.8688, 151.2093),  # Sydney
            ...     (-37.8136, 144.9631)   # Melbourne
            ... )

            >>> # Using Point objects
            >>> point1 = Point(151.2093, -33.8688)
            >>> point2 = Point(144.9631, -37.8136)
            >>> distance = GISUtils.calculate_distance_meters(point1, point2)

        Note:
            - For geodesic calculations, use (lat, lon) tuple order
            - For Euclidean calculations, points should be in a metric CRS
        """
        if use_geodesic:
            from geopy.distance import geodesic
            # Convert to (lat, lon) tuples
            if isinstance(point1, Point):
                point1 = (point1.y, point1.x)
            if isinstance(point2, Point):
                point2 = (point2.y, point2.x)
            return geodesic(point1, point2).meters
        else:
            # Euclidean distance (assumes metric CRS)
            if not isinstance(point1, Point):
                point1 = Point(point1[1], point1[0])  # lon, lat
            if not isinstance(point2, Point):
                point2 = Point(point2[1], point2[0])  # lon, lat
            return point1.distance(point2)

    @staticmethod
    def create_buffer(
        gdf: gpd.GeoDataFrame,
        distance_m: float,
        metric_crs: str = 'EPSG:3577'
    ) -> gpd.GeoDataFrame:
        """
        Create buffer around geometries in meters.

        Reprojects to metric CRS, creates buffer, then reprojects back to original CRS.

        Args:
            gdf: Input GeoDataFrame
            distance_m: Buffer distance in meters
            metric_crs: Metric CRS to use for buffering (default: Australian Albers)

        Returns:
            GeoDataFrame with buffered geometries in original CRS

        Example:
            >>> property_buffer = GISUtils.create_buffer(property_gdf, 2000)
        """
        original_crs = gdf.crs
        gdf_metric = gdf.to_crs(metric_crs)
        buffered = gdf_metric.buffer(distance_m)
        result = gpd.GeoDataFrame(gdf.drop(columns='geometry'), geometry=buffered, crs=metric_crs)

        if original_crs != metric_crs:
            result = result.to_crs(original_crs)

        return result

    @staticmethod
    def calculate_centroid(
        gdf: gpd.GeoDataFrame,
        metric_crs: str = 'EPSG:3577'
    ) -> Point:
        """
        Calculate centroid of all geometries in a GeoDataFrame.

        Args:
            gdf: Input GeoDataFrame
            metric_crs: Metric CRS to use for centroid calculation

        Returns:
            Point representing the centroid in the original CRS

        Example:
            >>> centroid = GISUtils.calculate_centroid(photos_gdf)
        """
        original_crs = gdf.crs
        gdf_metric = gdf.to_crs(metric_crs)
        centroid_metric = gdf_metric.geometry.unary_union.centroid

        # Convert back to original CRS
        centroid_gdf = gpd.GeoDataFrame(
            geometry=[centroid_metric],
            crs=metric_crs
        )
        if original_crs != metric_crs:
            centroid_gdf = centroid_gdf.to_crs(original_crs)

        return centroid_gdf.geometry.iloc[0]

    @staticmethod
    def spatial_join_within_distance(
        left_gdf: gpd.GeoDataFrame,
        right_gdf: gpd.GeoDataFrame,
        distance_m: float,
        metric_crs: str = 'EPSG:3577'
    ) -> gpd.GeoDataFrame:
        """
        Perform spatial join on features within specified distance.

        Args:
            left_gdf: Left GeoDataFrame
            right_gdf: Right GeoDataFrame
            distance_m: Distance threshold in meters
            metric_crs: Metric CRS for distance calculation

        Returns:
            GeoDataFrame with joined features within distance

        Example:
            >>> nearby = GISUtils.spatial_join_within_distance(
            ...     places_gdf, property_gdf, 500
            ... )
        """
        # Reproject to metric CRS
        left_metric = left_gdf.to_crs(metric_crs)
        right_metric = right_gdf.to_crs(metric_crs)

        # Buffer right geometries
        right_buffered = right_metric.copy()
        right_buffered.geometry = right_buffered.buffer(distance_m)

        # Spatial join
        result = gpd.sjoin(left_metric, right_buffered, predicate='within')

        # Reproject back to original CRS
        if left_gdf.crs != metric_crs:
            result = result.to_crs(left_gdf.crs)

        return result

    @staticmethod
    def calculate_bounds_with_margin(
        *gdfs: gpd.GeoDataFrame,
        margin_percent: float = 10.0,
        metric_crs: str = 'EPSG:3577'
    ) -> Tuple[float, float, float, float]:
        """
        Calculate bounds that encompass all GeoDataFrames with a margin.

        Args:
            *gdfs: Variable number of GeoDataFrames
            margin_percent: Margin as percentage of bounds (default: 10%)
            metric_crs: Metric CRS for calculation

        Returns:
            Tuple of (minx, miny, maxx, maxy) in metric CRS

        Example:
            >>> bounds = GISUtils.calculate_bounds_with_margin(
            ...     property_gdf, photos_gdf, places_gdf
            ... )
        """
        all_bounds = []
        for gdf in gdfs:
            if gdf is not None and not gdf.empty:
                gdf_metric = gdf.to_crs(metric_crs)
                all_bounds.append(gdf_metric.total_bounds)

        if not all_bounds:
            raise ValueError("No valid GeoDataFrames provided")

        # Combine all bounds
        all_bounds = np.array(all_bounds)
        minx = all_bounds[:, 0].min()
        miny = all_bounds[:, 1].min()
        maxx = all_bounds[:, 2].max()
        maxy = all_bounds[:, 3].max()

        # Add margin
        width = maxx - minx
        height = maxy - miny
        margin_x = width * (margin_percent / 100)
        margin_y = height * (margin_percent / 100)

        return (
            minx - margin_x,
            miny - margin_y,
            maxx + margin_x,
            maxy + margin_y
        )

    @staticmethod
    def clip_to_bounds(
        gdf: gpd.GeoDataFrame,
        bounds: Tuple[float, float, float, float],
        bounds_crs: Optional[str] = None
    ) -> gpd.GeoDataFrame:
        """
        Clip GeoDataFrame to specified bounds.

        Args:
            gdf: Input GeoDataFrame
            bounds: Tuple of (minx, miny, maxx, maxy)
            bounds_crs: CRS of bounds (if None, assumes same as gdf)

        Returns:
            Clipped GeoDataFrame

        Example:
            >>> clipped = GISUtils.clip_to_bounds(mesh_blocks, bounds)
        """
        # Create polygon from bounds
        minx, miny, maxx, maxy = bounds
        clip_poly = Polygon([
            (minx, miny),
            (maxx, miny),
            (maxx, maxy),
            (minx, maxy),
            (minx, miny)
        ])

        # Create GeoDataFrame for clipping
        clip_gdf = gpd.GeoDataFrame(
            geometry=[clip_poly],
            crs=bounds_crs or gdf.crs
        )

        # Ensure same CRS
        if clip_gdf.crs != gdf.crs:
            clip_gdf = clip_gdf.to_crs(gdf.crs)

        # Clip
        return gpd.clip(gdf, clip_gdf)

    @staticmethod
    def clamp_latitude(lat: float, max_lat: float = 85.0511) -> float:
        """
        Clamp latitude to valid range for Web Mercator projection.

        Web Mercator (EPSG:3857) cannot represent latitudes above ~85.05 degrees.
        This function clamps values to prevent math domain errors.

        Args:
            lat: Latitude value to clamp
            max_lat: Maximum absolute latitude (default: 85.0511 for Web Mercator)

        Returns:
            Clamped latitude value

        Example:
            >>> safe_lat = GISUtils.clamp_latitude(87.5)  # Returns 85.0511
        """
        return max(-max_lat, min(max_lat, lat))
