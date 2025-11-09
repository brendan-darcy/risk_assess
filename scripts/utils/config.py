"""
Configuration Management for Risk Assessment System

This module provides centralized configuration using dataclasses.
All configuration values should be defined here to avoid hard-coding
throughout the codebase.

Usage:
    from pipelines.config import config

    # Access configuration
    print(config.gis.default_metric_crs)
    print(config.visualization.default_basemap)

    # Load from file
    custom_config = AppConfig.from_file('custom_config.json')
#####
Author: Brendan Darcy
Date: 2025-11-09
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path
import json


@dataclass
class GISConfig:
    """GIS-specific configuration"""
    default_input_crs: str = 'EPSG:4326'  # WGS84
    default_metric_crs: str = 'EPSG:3577'  # Australian Albers (GDA2020)
    default_output_crs: str = 'EPSG:4326'  # WGS84
    default_buffer_distance_m: int = 2000


@dataclass
class VisualizationConfig:
    """Visualization configuration"""
    default_figsize: tuple = (18, 12)
    default_dpi: int = 200
    default_basemap: str = 'Google Satellite'
    available_basemaps: List[str] = field(default_factory=lambda: [
        'Google Satellite', 'Google Hybrid', 'Google Roadmap', 'Google Terrain',
        'Esri Satellite', 'OpenStreetMap', 'CartoDB Positron', 'CartoDB Voyager'
    ])

    # Color schemes for mesh block categories
    mesh_block_colors: Dict[str, str] = field(default_factory=lambda: {
        'Residential': '#FFFACD',
        'Commercial': '#87CEEB',
        'Industrial': '#D3D3D3',
        'Parkland': '#90EE90',
        'Primary Production': '#DEB887',
        'Water': '#4682B4',
        'Education': '#FFB6C1',
        'Hospital/Medical': '#FF69B4',
        'Transport': '#FFA500',
        'Other': '#E6E6FA'
    })

    # Color schemes for photo categories
    photo_category_colors: Dict[str, str] = field(default_factory=lambda: {
        'frontage': '#1f77b4',
        'rear': '#2ca02c',
        'kitchen': '#ff7f0e',
        'bathroom': '#9467bd',
        'livingArea': '#bcbd22',
        'significantRenovation': '#d62728',
        'externalUndercoverArea': '#8c564b',
        'laundry': '#e377c2',
        'secondaryKitchen': '#ff9896',
        'additionalImagery': '#c7c7c7'
    })

    # Google Places category colors
    places_category_colors: Dict[str, str] = field(default_factory=lambda: {
        'restaurant': '#ff7f0e',
        'cafe': '#bcbd22',
        'bar': '#d62728',
        'store': '#9467bd',
        'park': '#2ca02c',
        'school': '#e377c2',
        'hospital': '#ff69b4',
        'default': '#7f7f7f'
    })


@dataclass
class PathsConfig:
    """File paths configuration"""
    data_dir: Path = Path('data')
    raw_dir: Path = Path('data/raw')
    outputs_dir: Path = Path('data/outputs')
    photos_dir: Path = Path('data/photos')
    logs_dir: Path = Path('data/logs')
    mesh_block_shapefile: Path = Path('data/raw/MB_2021_AUST_GDA2020.shp')

    def __post_init__(self):
        """Convert strings to Path objects if needed"""
        for field_name in ['data_dir', 'raw_dir', 'outputs_dir', 'photos_dir',
                          'logs_dir', 'mesh_block_shapefile']:
            value = getattr(self, field_name)
            if isinstance(value, str):
                setattr(self, field_name, Path(value))


@dataclass
class APIConfig:
    """API configuration"""
    # Rate limiting
    google_api_rate_limit_delay: float = 0.1
    corelogic_api_rate_limit_delay: float = 0.1

    # Retry settings
    max_retry_attempts: int = 3
    retry_delay_seconds: float = 1.0

    # Timeout settings
    request_timeout_seconds: int = 30

    # Google Places API settings
    google_places_radius_m: int = 500
    google_places_max_results: int = 60


@dataclass
class ProcessingConfig:
    """Data processing configuration"""
    # Photo processing
    max_photo_distance_m: Optional[int] = None  # None = no limit
    photo_metadata_encoding: str = 'utf-8'

    # Mesh block processing
    include_residential_meshblocks: bool = True
    calculate_boundary_distances: bool = True

    # Parallel processing
    enable_parallel_processing: bool = False
    max_workers: int = 4


@dataclass
class AppConfig:
    """Main application configuration"""
    gis: GISConfig = field(default_factory=GISConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    api: APIConfig = field(default_factory=APIConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)

    @classmethod
    def from_file(cls, config_path: str) -> 'AppConfig':
        """
        Load configuration from JSON file.

        Args:
            config_path: Path to JSON configuration file

        Returns:
            AppConfig instance with loaded configuration

        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file is invalid JSON
        """
        with open(config_path, 'r') as f:
            config_dict = json.load(f)

        # Handle nested dataclasses
        if 'gis' in config_dict:
            config_dict['gis'] = GISConfig(**config_dict['gis'])
        if 'visualization' in config_dict:
            config_dict['visualization'] = VisualizationConfig(**config_dict['visualization'])
        if 'paths' in config_dict:
            config_dict['paths'] = PathsConfig(**config_dict['paths'])
        if 'api' in config_dict:
            config_dict['api'] = APIConfig(**config_dict['api'])
        if 'processing' in config_dict:
            config_dict['processing'] = ProcessingConfig(**config_dict['processing'])

        return cls(**config_dict)

    def to_file(self, config_path: str):
        """
        Save configuration to JSON file.

        Args:
            config_path: Path where JSON configuration should be saved
        """
        from dataclasses import asdict

        config_dict = asdict(self)

        # Convert Path objects to strings for JSON serialization
        def convert_paths(obj):
            if isinstance(obj, Path):
                return str(obj)
            elif isinstance(obj, dict):
                return {k: convert_paths(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [convert_paths(v) for v in obj]
            return obj

        config_dict = convert_paths(config_dict)

        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)

    def ensure_directories_exist(self):
        """Create all configured directories if they don't exist"""
        for dir_path in [
            self.paths.data_dir,
            self.paths.raw_dir,
            self.paths.outputs_dir,
            self.paths.photos_dir,
            self.paths.logs_dir
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)


# Global configuration instance (singleton)
config = AppConfig()
