"""
Pytest Configuration and Fixtures

This module provides shared fixtures and configuration for all tests.

Author: Brendan Darcy
Date: 2025-11-09
"""

import pytest
import geopandas as gpd
from shapely.geometry import Point, Polygon
from pathlib import Path
import json
import tempfile
import shutil


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs"""
    tmp = tempfile.mkdtemp()
    yield Path(tmp)
    shutil.rmtree(tmp)


@pytest.fixture
def sample_point_wgs84():
    """Sample point in WGS84 (Sydney Opera House)"""
    return Point(151.2153, -33.8568)


@pytest.fixture
def sample_point_gdf_wgs84(sample_point_wgs84):
    """Sample GeoDataFrame with single point in WGS84"""
    return gpd.GeoDataFrame(
        {'name': ['Sydney Opera House']},
        geometry=[sample_point_wgs84],
        crs='EPSG:4326'
    )


@pytest.fixture
def sample_polygon_wgs84():
    """Sample polygon in WGS84 (rectangle around Sydney CBD)"""
    return Polygon([
        (151.2, -33.87),
        (151.22, -33.87),
        (151.22, -33.85),
        (151.2, -33.85),
        (151.2, -33.87)
    ])


@pytest.fixture
def sample_property_coords():
    """Sample property coordinates (lat, lon)"""
    return (-33.8568, 151.2153)  # Sydney Opera House


@pytest.fixture
def sample_mesh_blocks_gdf():
    """
    Sample mesh blocks GeoDataFrame for testing.

    Creates a small dataset with different mesh block categories
    around a central point.
    """
    # Create sample mesh blocks around Sydney Opera House
    points = [
        Point(151.215, -33.856),   # Near center
        Point(151.216, -33.857),   # East
        Point(151.214, -33.855),   # West
        Point(151.215, -33.858),   # South
        Point(151.215, -33.854),   # North
    ]

    # Create small polygons (buffers) around each point
    polygons = [p.buffer(0.001) for p in points]  # ~100m buffer

    return gpd.GeoDataFrame({
        'MB_CODE21': ['1234567890', '1234567891', '1234567892', '1234567893', '1234567894'],
        'MB_CAT21': ['Residential', 'Commercial', 'Parkland', 'Residential', 'Industrial'],
        'SA1_CODE21': ['11234567890', '11234567890', '11234567890', '11234567890', '11234567890'],
        'area_sqkm': [0.01, 0.01, 0.015, 0.008, 0.012]
    }, geometry=polygons, crs='EPSG:4326')


@pytest.fixture
def sample_photo_metadata():
    """Sample photo metadata as dict"""
    return {
        'photos/photo1.jpg': {
            'category': 'frontage',
            'latitude': -33.8568,
            'longitude': 151.2153
        },
        'photos/photo2.jpg': {
            'category': 'rear',
            'latitude': -33.8570,
            'longitude': 151.2155
        },
        'photos/photo3.jpg': {
            'category': 'kitchen',
            'latitude': -33.8568,
            'longitude': 151.2153
        }
    }


@pytest.fixture
def sample_photo_metadata_file(temp_dir, sample_photo_metadata):
    """Create a temporary photo metadata file"""
    metadata_path = temp_dir / 'photo_metadata.txt'

    with open(metadata_path, 'w') as f:
        for filepath, data in sample_photo_metadata.items():
            f.write(f"{filepath}\n")
            f.write(f"Category: {data['category']}\n")
            f.write(f"GPS: {data['latitude']}, {data['longitude']}\n")
            f.write("\n")

    return metadata_path


@pytest.fixture
def sample_config_dict():
    """Sample configuration dictionary"""
    return {
        'gis': {
            'default_input_crs': 'EPSG:4326',
            'default_metric_crs': 'EPSG:3577',
            'default_output_crs': 'EPSG:4326',
            'default_buffer_distance_m': 2000
        },
        'visualization': {
            'default_figsize': [18, 12],
            'default_dpi': 200,
            'default_basemap': 'Google Satellite'
        },
        'paths': {
            'data_dir': 'data',
            'raw_dir': 'data/raw',
            'outputs_dir': 'data/outputs',
            'photos_dir': 'data/photos',
            'logs_dir': 'data/logs'
        }
    }


@pytest.fixture
def sample_config_file(temp_dir, sample_config_dict):
    """Create a temporary config file"""
    config_path = temp_dir / 'test_config.json'

    with open(config_path, 'w') as f:
        json.dump(sample_config_dict, f, indent=2)

    return config_path


@pytest.fixture
def mock_corelogic_response():
    """Mock CoreLogic API response"""
    return {
        'propertyId': 13683380,
        'address': {
            'singleLineAddress': '5 Settlers Court, Vermont South VIC 3133'
        },
        'location': {
            'latitude': -37.8492,
            'longitude': 145.1725
        }
    }


@pytest.fixture
def mock_google_places_response():
    """Mock Google Places API response"""
    return {
        'results': [
            {
                'name': 'Sample Restaurant',
                'types': ['restaurant', 'food', 'point_of_interest'],
                'geometry': {
                    'location': {
                        'lat': -33.8568,
                        'lng': 151.2153
                    }
                },
                'rating': 4.5,
                'user_ratings_total': 123
            },
            {
                'name': 'Sample Cafe',
                'types': ['cafe', 'food', 'point_of_interest'],
                'geometry': {
                    'location': {
                        'lat': -33.8570,
                        'lng': 151.2155
                    }
                },
                'rating': 4.2,
                'user_ratings_total': 87
            }
        ],
        'status': 'OK'
    }


# Test markers for different test categories
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual functions"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests requiring multiple components"
    )
    config.addinivalue_line(
        "markers", "api: Tests that make real API calls (slow)"
    )
    config.addinivalue_line(
        "markers", "gis: Tests involving GIS operations and GeoDataFrames"
    )
    config.addinivalue_line(
        "markers", "slow: Slow tests that take more than a few seconds"
    )
