"""
Tests for GIS Utilities

Tests for the centralized GIS utility functions including CRS conversions,
distance calculations, and GeoDataFrame operations.

Author: Brendan Darcy
Date: 2025-11-09
"""

import pytest
import geopandas as gpd
from shapely.geometry import Point
from pipelines.gis_utils import GISUtils


@pytest.mark.unit
@pytest.mark.gis
class TestCreatePointGDF:
    """Tests for create_point_gdf function"""

    def test_create_point_gdf_wgs84(self):
        """Test creating point GeoDataFrame in WGS84"""
        gdf = GISUtils.create_point_gdf(
            longitude=151.2093,
            latitude=-33.8688,
            attributes={'name': 'Sydney'}
        )

        assert isinstance(gdf, gpd.GeoDataFrame)
        assert len(gdf) == 1
        assert gdf.crs.to_string() == 'EPSG:4326'
        assert gdf['name'].iloc[0] == 'Sydney'
        assert isinstance(gdf.geometry.iloc[0], Point)
        assert gdf.geometry.iloc[0].x == pytest.approx(151.2093)
        assert gdf.geometry.iloc[0].y == pytest.approx(-33.8688)

    def test_create_point_gdf_with_reprojection(self):
        """Test creating point GeoDataFrame with CRS reprojection"""
        gdf = GISUtils.create_point_gdf(
            longitude=151.2093,
            latitude=-33.8688,
            target_crs=GISUtils.AUSTRALIAN_ALBERS
        )

        assert gdf.crs.to_string() == 'EPSG:3577'
        # Coordinates should have changed significantly (now in meters)
        assert abs(gdf.geometry.iloc[0].x - 151.2093) > 100000

    def test_create_point_gdf_no_attributes(self):
        """Test creating point without additional attributes"""
        gdf = GISUtils.create_point_gdf(
            longitude=151.2093,
            latitude=-33.8688
        )

        assert isinstance(gdf, gpd.GeoDataFrame)
        assert len(gdf) == 1
        # Should only have geometry column
        assert len(gdf.columns) == 1

    def test_create_point_gdf_invalid_longitude(self):
        """Test that invalid longitude raises ValueError"""
        with pytest.raises(ValueError, match="Invalid longitude"):
            GISUtils.create_point_gdf(
                longitude=200.0,  # Out of range
                latitude=-33.8688
            )

    def test_create_point_gdf_invalid_latitude(self):
        """Test that invalid latitude raises ValueError"""
        with pytest.raises(ValueError, match="Invalid latitude"):
            GISUtils.create_point_gdf(
                longitude=151.2093,
                latitude=95.0  # Out of range
            )


@pytest.mark.unit
@pytest.mark.gis
class TestEnsureCRS:
    """Tests for ensure_crs function"""

    def test_ensure_crs_no_conversion_needed(self, sample_point_gdf_wgs84):
        """Test ensure_crs when already in target CRS"""
        result = GISUtils.ensure_crs(sample_point_gdf_wgs84, 'EPSG:4326')

        assert result.crs.to_string() == 'EPSG:4326'
        # Should be same object (no conversion performed)
        assert result is sample_point_gdf_wgs84

    def test_ensure_crs_with_conversion(self, sample_point_gdf_wgs84):
        """Test ensure_crs with CRS conversion"""
        result = GISUtils.ensure_crs(sample_point_gdf_wgs84, GISUtils.AUSTRALIAN_ALBERS)

        assert result.crs.to_string() == 'EPSG:3577'
        # Should be different object
        assert result is not sample_point_gdf_wgs84

    def test_ensure_crs_missing_crs(self):
        """Test ensure_crs with missing CRS (should set it)"""
        gdf = gpd.GeoDataFrame(
            geometry=[Point(151.2093, -33.8688)],
            crs=None  # No CRS
        )

        result = GISUtils.ensure_crs(gdf, 'EPSG:4326')

        assert result.crs.to_string() == 'EPSG:4326'


@pytest.mark.unit
@pytest.mark.gis
class TestCalculateDistance:
    """Tests for calculate_distance_meters function"""

    def test_calculate_distance_geodesic_tuples(self):
        """Test geodesic distance calculation with tuples"""
        # Sydney to Melbourne (approx 714 km)
        sydney = (-33.8688, 151.2093)  # lat, lon
        melbourne = (-37.8136, 144.9631)  # lat, lon

        distance = GISUtils.calculate_distance_meters(
            sydney, melbourne, use_geodesic=True
        )

        # Approximate distance should be between 700-720 km
        assert 700_000 < distance < 720_000

    def test_calculate_distance_geodesic_points(self):
        """Test geodesic distance calculation with Point objects"""
        # Sydney to Melbourne
        sydney = Point(151.2093, -33.8688)  # lon, lat
        melbourne = Point(144.9631, -37.8136)  # lon, lat

        distance = GISUtils.calculate_distance_meters(
            sydney, melbourne, use_geodesic=True
        )

        # Approximate distance should be between 700-720 km
        assert 700_000 < distance < 720_000

    def test_calculate_distance_short_distance(self):
        """Test distance calculation for short distances"""
        # Two points ~1km apart
        point1 = (-33.8688, 151.2093)
        point2 = (-33.8698, 151.2093)  # ~1.1 km north

        distance = GISUtils.calculate_distance_meters(
            point1, point2, use_geodesic=True
        )

        # Should be approximately 1.1 km
        assert 1000 < distance < 1200


@pytest.mark.unit
@pytest.mark.gis
class TestCreateBuffer:
    """Tests for create_buffer function"""

    def test_create_buffer_2000m(self, sample_point_gdf_wgs84):
        """Test creating 2000m buffer around point"""
        buffered = GISUtils.create_buffer(sample_point_gdf_wgs84, distance_m=2000)

        assert isinstance(buffered, gpd.GeoDataFrame)
        assert buffered.crs.to_string() == 'EPSG:4326'  # Should be back in original CRS

        # Buffer should be a polygon
        from shapely.geometry import Polygon
        assert isinstance(buffered.geometry.iloc[0], Polygon)


@pytest.mark.unit
@pytest.mark.gis
class TestCalculateCentroid:
    """Tests for calculate_centroid function"""

    def test_calculate_centroid_multiple_points(self):
        """Test calculating centroid of multiple points"""
        points = [
            Point(151.20, -33.86),
            Point(151.22, -33.86),
            Point(151.21, -33.87)
        ]
        gdf = gpd.GeoDataFrame(geometry=points, crs='EPSG:4326')

        centroid = GISUtils.calculate_centroid(gdf)

        assert isinstance(centroid, Point)
        # Centroid should be roughly in the middle
        assert 151.20 < centroid.x < 151.22
        assert -33.87 < centroid.y < -33.86


@pytest.mark.unit
@pytest.mark.gis
class TestCalculateBoundsWithMargin:
    """Tests for calculate_bounds_with_margin function"""

    def test_calculate_bounds_single_gdf(self, sample_point_gdf_wgs84):
        """Test calculating bounds with margin for single GeoDataFrame"""
        bounds = GISUtils.calculate_bounds_with_margin(
            sample_point_gdf_wgs84,
            margin_percent=10.0
        )

        assert len(bounds) == 4
        minx, miny, maxx, maxy = bounds
        assert minx < maxx
        assert miny < maxy

    def test_calculate_bounds_multiple_gdfs(self):
        """Test calculating bounds with margin for multiple GeoDataFrames"""
        gdf1 = gpd.GeoDataFrame(
            geometry=[Point(151.20, -33.86)],
            crs='EPSG:4326'
        )
        gdf2 = gpd.GeoDataFrame(
            geometry=[Point(151.22, -33.87)],
            crs='EPSG:4326'
        )

        bounds = GISUtils.calculate_bounds_with_margin(gdf1, gdf2, margin_percent=10.0)

        minx, miny, maxx, maxy = bounds
        assert minx < maxx
        assert miny < maxy


@pytest.mark.unit
@pytest.mark.gis
class TestClampLatitude:
    """Tests for clamp_latitude function"""

    def test_clamp_latitude_valid(self):
        """Test clamping valid latitude (no change)"""
        lat = 45.0
        clamped = GISUtils.clamp_latitude(lat)
        assert clamped == 45.0

    def test_clamp_latitude_too_high(self):
        """Test clamping latitude above maximum"""
        lat = 87.5
        clamped = GISUtils.clamp_latitude(lat, max_lat=85.0511)
        assert clamped == 85.0511

    def test_clamp_latitude_too_low(self):
        """Test clamping latitude below minimum"""
        lat = -87.5
        clamped = GISUtils.clamp_latitude(lat, max_lat=85.0511)
        assert clamped == -85.0511

    def test_clamp_latitude_at_boundary(self):
        """Test clamping latitude at exact boundary"""
        lat = 85.0511
        clamped = GISUtils.clamp_latitude(lat, max_lat=85.0511)
        assert clamped == 85.0511
