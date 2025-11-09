"""
Tests for Configuration Module

Tests for the centralized configuration management system.

Author: Brendan Darcy
Date: 2025-11-09
"""

import pytest
import json
from pathlib import Path
from pipelines.config import (
    GISConfig, VisualizationConfig, PathsConfig,
    APIConfig, ProcessingConfig, AppConfig
)


@pytest.mark.unit
class TestGISConfig:
    """Tests for GISConfig"""

    def test_gis_config_defaults(self):
        """Test GISConfig default values"""
        config = GISConfig()

        assert config.default_input_crs == 'EPSG:4326'
        assert config.default_metric_crs == 'EPSG:3577'
        assert config.default_output_crs == 'EPSG:4326'
        assert config.default_buffer_distance_m == 2000


@pytest.mark.unit
class TestVisualizationConfig:
    """Tests for VisualizationConfig"""

    def test_visualization_config_defaults(self):
        """Test VisualizationConfig default values"""
        config = VisualizationConfig()

        assert config.default_figsize == (18, 12)
        assert config.default_dpi == 200
        assert config.default_basemap == 'Google Satellite'
        assert 'Google Satellite' in config.available_basemaps
        assert 'Esri Satellite' in config.available_basemaps

    def test_visualization_config_color_schemes(self):
        """Test color scheme dictionaries"""
        config = VisualizationConfig()

        # Check mesh block colors
        assert 'Residential' in config.mesh_block_colors
        assert 'Commercial' in config.mesh_block_colors

        # Check photo category colors
        assert 'frontage' in config.photo_category_colors
        assert 'kitchen' in config.photo_category_colors


@pytest.mark.unit
class TestPathsConfig:
    """Tests for PathsConfig"""

    def test_paths_config_defaults(self):
        """Test PathsConfig default values"""
        config = PathsConfig()

        assert config.data_dir == Path('data')
        assert config.raw_dir == Path('data/raw')
        assert config.outputs_dir == Path('data/outputs')
        assert config.photos_dir == Path('data/photos')
        assert config.logs_dir == Path('data/logs')

        # Check that all are Path objects
        assert isinstance(config.data_dir, Path)
        assert isinstance(config.raw_dir, Path)

    def test_paths_config_string_conversion(self):
        """Test that string paths are converted to Path objects"""
        config = PathsConfig(
            data_dir='test_data',
            raw_dir='test_data/raw'
        )

        assert isinstance(config.data_dir, Path)
        assert isinstance(config.raw_dir, Path)
        assert config.data_dir == Path('test_data')


@pytest.mark.unit
class TestAPIConfig:
    """Tests for APIConfig"""

    def test_api_config_defaults(self):
        """Test APIConfig default values"""
        config = APIConfig()

        assert config.google_api_rate_limit_delay == 0.1
        assert config.corelogic_api_rate_limit_delay == 0.1
        assert config.max_retry_attempts == 3
        assert config.retry_delay_seconds == 1.0
        assert config.request_timeout_seconds == 30
        assert config.google_places_radius_m == 500


@pytest.mark.unit
class TestProcessingConfig:
    """Tests for ProcessingConfig"""

    def test_processing_config_defaults(self):
        """Test ProcessingConfig default values"""
        config = ProcessingConfig()

        assert config.max_photo_distance_m is None
        assert config.photo_metadata_encoding == 'utf-8'
        assert config.include_residential_meshblocks is True
        assert config.calculate_boundary_distances is True
        assert config.enable_parallel_processing is False
        assert config.max_workers == 4


@pytest.mark.unit
class TestAppConfig:
    """Tests for AppConfig"""

    def test_app_config_defaults(self):
        """Test AppConfig creates all sub-configs"""
        config = AppConfig()

        assert isinstance(config.gis, GISConfig)
        assert isinstance(config.visualization, VisualizationConfig)
        assert isinstance(config.paths, PathsConfig)
        assert isinstance(config.api, APIConfig)
        assert isinstance(config.processing, ProcessingConfig)

    def test_app_config_to_file(self, temp_dir):
        """Test saving AppConfig to file"""
        config = AppConfig()
        config_path = temp_dir / 'test_config.json'

        config.to_file(str(config_path))

        assert config_path.exists()

        # Load and verify structure
        with open(config_path, 'r') as f:
            loaded = json.load(f)

        assert 'gis' in loaded
        assert 'visualization' in loaded
        assert 'paths' in loaded
        assert 'api' in loaded
        assert 'processing' in loaded

    def test_app_config_from_file(self, temp_dir):
        """Test loading AppConfig from file"""
        # Create a test config file
        config_data = {
            'gis': {
                'default_buffer_distance_m': 5000
            },
            'visualization': {
                'default_dpi': 300
            }
        }

        config_path = temp_dir / 'test_config.json'
        with open(config_path, 'w') as f:
            json.dump(config_data, f)

        # Load config
        config = AppConfig.from_file(str(config_path))

        assert isinstance(config, AppConfig)
        assert config.gis.default_buffer_distance_m == 5000
        assert config.visualization.default_dpi == 300

    def test_app_config_ensure_directories_exist(self, temp_dir):
        """Test ensure_directories_exist creates all directories"""
        config = AppConfig()
        config.paths.data_dir = temp_dir / 'data'
        config.paths.raw_dir = temp_dir / 'data' / 'raw'
        config.paths.outputs_dir = temp_dir / 'data' / 'outputs'
        config.paths.photos_dir = temp_dir / 'data' / 'photos'
        config.paths.logs_dir = temp_dir / 'data' / 'logs'

        config.ensure_directories_exist()

        assert config.paths.data_dir.exists()
        assert config.paths.raw_dir.exists()
        assert config.paths.outputs_dir.exists()
        assert config.paths.photos_dir.exists()
        assert config.paths.logs_dir.exists()
