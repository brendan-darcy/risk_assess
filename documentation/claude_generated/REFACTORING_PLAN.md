# Risk Assessment System - Refactoring Plan

**Date:** 2025-11-09
**Author:** Code Analysis
**Scope:** Complete codebase refactoring for improved maintainability, consistency, and quality

---

## Executive Summary

This document outlines a comprehensive refactoring plan for the Risk Assessment System. The codebase is functional and well-structured, but several improvements will enhance maintainability, consistency, and code quality.

**Key Findings:**
- ✅ Good foundation with `pipeline_utils.py` base classes
- ✅ Well-documented pipelines with clear responsibilities
- ⚠️ Inconsistent error handling and logging patterns
- ⚠️ Code duplication in GIS operations
- ⚠️ Hard-coded configuration values
- ⚠️ No testing infrastructure

---

## 1. Priority Issues

### 1.1 Inconsistent Error Handling & Logging

**Problem:** Mixed approaches across pipelines

```python
# ❌ Current - Inconsistent patterns
# mesh_block_analysis_pipeline.py
print(f"✅ Loaded {len(self.mesh_blocks_gdf)} mesh blocks")  # Direct print
print("❌ Property not found in any mesh block")  # Direct print

# photo_visualization_pipeline.py
print(f"⚠️  Google Maps API request failed: {response.status_code}")  # Direct print
print(f"✅ Added {basemap_source} basemap")  # Direct print

# property_data_processor.py
self.reporter.success("API connectivity verified")  # Uses reporter
self.reporter.error(f"Error processing {address}: {e}")  # Uses reporter
```

**Solution:** Standardize on `ProgressReporter` throughout

```python
# ✅ Recommended pattern
class MeshBlockAnalysisPipeline:
    def __init__(self, shapefile_path, buffer_distance=2000, reporter=None):
        self.reporter = reporter or ProgressReporter("Mesh Block Analysis")
        # ... rest of init

    def load_mesh_blocks(self):
        self.reporter.info(f"Loading mesh blocks from: {self.shapefile_path}")
        self.mesh_blocks_gdf = gpd.read_file(self.shapefile_path)
        self.reporter.success(f"Loaded {len(self.mesh_blocks_gdf)} mesh blocks")
        return self.mesh_blocks_gdf
```

**Action Items:**
- [ ] Add `ProgressReporter` to all pipeline classes
- [ ] Replace all `print()` statements with reporter methods
- [ ] Add consistent error messages with context
- [ ] Implement structured logging for production use

---

### 1.2 Code Duplication in GIS Operations

**Problem:** Repeated CRS conversion and GeoDataFrame creation logic

```python
# ❌ Duplicated across multiple files
# mesh_block_analysis_pipeline.py (line 270-272)
self.property_gdf = self.property_gdf.to_crs(self.mesh_blocks_gdf.crs)

# photo_location_processor.py (line 184)
gdf = gdf.to_crs(target_crs)

# spatial_visualization_pipeline.py (line 120)
).to_crs(target_crs)
```

**Solution:** Create a GIS utilities module

```python
# pipelines/gis_utils.py
from typing import Union, Tuple
import geopandas as gpd
from shapely.geometry import Point

class GISUtils:
    """Centralized GIS utility functions"""

    # Standard CRS definitions
    WGS84 = 'EPSG:4326'
    WEB_MERCATOR = 'EPSG:3857'
    AUSTRALIAN_ALBERS = 'EPSG:3577'  # GDA2020

    @staticmethod
    def create_point_gdf(
        longitude: float,
        latitude: float,
        attributes: dict = None,
        source_crs: str = 'EPSG:4326',
        target_crs: str = None
    ) -> gpd.GeoDataFrame:
        """
        Create GeoDataFrame from point coordinates with optional reprojection.

        Args:
            longitude: Point longitude
            latitude: Point latitude
            attributes: Optional attribute dictionary
            source_crs: Source CRS (default: WGS84)
            target_crs: Target CRS for reprojection (None = no reprojection)

        Returns:
            GeoDataFrame with point geometry
        """
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
            target_crs: Target CRS
            reporter: Optional ProgressReporter for logging

        Returns:
            GeoDataFrame in target CRS
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
            point1: First point (Point or (lat, lon) tuple)
            point2: Second point (Point or (lat, lon) tuple)
            use_geodesic: Use geodesic distance for accuracy (default: True)

        Returns:
            Distance in meters
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
                point1 = Point(point1[1], point1[0])
            if not isinstance(point2, Point):
                point2 = Point(point2[1], point2[0])
            return point1.distance(point2)
```

**Action Items:**
- [ ] Create `pipelines/gis_utils.py` module
- [ ] Refactor all pipelines to use GISUtils
- [ ] Add distance calculation utilities
- [ ] Add buffer creation utilities
- [ ] Add spatial join utilities

---

### 1.3 Configuration Management

**Problem:** Hard-coded values scattered throughout codebase

```python
# ❌ Hard-coded CRS values
# mesh_block_analysis_pipeline.py (line 40-41)
metric_crs: str = 'EPSG:3577',  # GDA2020 Australian Albers
output_crs: str = 'EPSG:4326'   # WGS84

# photo_location_processor.py (line 155)
target_crs: str = 'EPSG:3577'

# photo_visualization_pipeline.py (line 163)
basemap_source: str = 'Google Satellite'
```

**Solution:** Centralized configuration

```python
# pipelines/config.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path

@dataclass
class GISConfig:
    """GIS-specific configuration"""
    default_input_crs: str = 'EPSG:4326'  # WGS84
    default_metric_crs: str = 'EPSG:3577'  # Australian Albers
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

    # Color schemes
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

@dataclass
class PathsConfig:
    """File paths configuration"""
    data_dir: Path = Path('data')
    raw_dir: Path = Path('data/raw')
    outputs_dir: Path = Path('data/outputs')
    photos_dir: Path = Path('data/photos')
    mesh_block_shapefile: Path = Path('data/raw/MB_2021_AUST_GDA2020.shp')

    def __post_init__(self):
        """Convert strings to Path objects"""
        for field_name in ['data_dir', 'raw_dir', 'outputs_dir', 'photos_dir', 'mesh_block_shapefile']:
            value = getattr(self, field_name)
            if isinstance(value, str):
                setattr(self, field_name, Path(value))

@dataclass
class AppConfig:
    """Main application configuration"""
    gis: GISConfig = field(default_factory=GISConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)

    # API settings
    google_api_rate_limit_delay: float = 0.1
    corelogic_api_rate_limit_delay: float = 0.1

    # Processing settings
    max_retry_attempts: int = 3
    request_timeout_seconds: int = 30

    @classmethod
    def from_file(cls, config_path: str) -> 'AppConfig':
        """Load configuration from JSON file"""
        import json
        with open(config_path, 'r') as f:
            config_dict = json.load(f)
        return cls(**config_dict)

    def to_file(self, config_path: str):
        """Save configuration to JSON file"""
        import json
        from dataclasses import asdict
        with open(config_path, 'w') as f:
            json.dump(asdict(self), f, indent=2, default=str)

# Global configuration instance
config = AppConfig()
```

**Action Items:**
- [ ] Create `pipelines/config.py` module
- [ ] Replace all hard-coded values with config references
- [ ] Add environment variable support for sensitive values
- [ ] Create example `config.example.json` file
- [ ] Document all configuration options

---

## 2. Code Quality Improvements

### 2.1 Enhanced Type Hints

**Current State:** Good coverage but inconsistent

```python
# ❌ Missing or incomplete type hints
def load_property_from_corelogic(self, address=None, property_id=None):  # No types

def calculate_distances_to_property(self, photos_gdf, property_coords):  # Partial types
```

**Recommended:**

```python
# ✅ Complete type hints
from typing import Optional, Tuple, Dict, Any, Union
import geopandas as gpd

def load_property_from_corelogic(
    self,
    address: Optional[str] = None,
    property_id: Optional[int] = None
) -> Tuple[gpd.GeoDataFrame, Dict[str, Any]]:
    """Load property data from CoreLogic API."""
    ...

def calculate_distances_to_property(
    self,
    photos_gdf: gpd.GeoDataFrame,
    property_coords: Tuple[float, float]
) -> gpd.GeoDataFrame:
    """Calculate distances from photos to property."""
    ...
```

---

### 2.2 Docstring Standardization

**Recommended Format:** Google Style

```python
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
        >>> gdf = create_point_gdf(151.2093, -33.8688, {'name': 'Sydney'})
        >>> gdf = create_point_gdf(
        ...     151.2093, -33.8688,
        ...     attributes={'name': 'Sydney'},
        ...     target_crs='EPSG:3577'
        ... )

    Note:
        - Input coordinates should be in (longitude, latitude) order
        - For Australian data, EPSG:3577 (Australian Albers) is recommended for metric calculations
    """
```

---

### 2.3 Error Handling Patterns

**Recommended Approach:**

```python
# pipelines/exceptions.py
class RiskAssessmentError(Exception):
    """Base exception for risk assessment system"""
    pass

class DataLoadError(RiskAssessmentError):
    """Error loading data from file or API"""
    pass

class GISOperationError(RiskAssessmentError):
    """Error during GIS operation"""
    pass

class APIError(RiskAssessmentError):
    """Error calling external API"""
    pass

class ConfigurationError(RiskAssessmentError):
    """Configuration error"""
    pass


# Usage in pipelines
from pipelines.exceptions import DataLoadError, GISOperationError

class MeshBlockAnalysisPipeline:
    def load_mesh_blocks(self) -> gpd.GeoDataFrame:
        """Load mesh block shapefile."""
        try:
            self.reporter.info(f"Loading mesh blocks from: {self.shapefile_path}")

            if not self.shapefile_path.exists():
                raise DataLoadError(
                    f"Shapefile not found: {self.shapefile_path}\n"
                    f"Please ensure MB_2021_AUST_GDA2020.shp is in {self.shapefile_path.parent}"
                )

            self.mesh_blocks_gdf = gpd.read_file(self.shapefile_path)

            if self.mesh_blocks_gdf.empty:
                raise DataLoadError(f"Shapefile is empty: {self.shapefile_path}")

            if 'MB_CAT21' not in self.mesh_blocks_gdf.columns:
                raise DataLoadError(
                    f"Shapefile missing required column 'MB_CAT21': {self.shapefile_path}"
                )

            self.reporter.success(f"Loaded {len(self.mesh_blocks_gdf)} mesh blocks")
            self.reporter.info(f"CRS: {self.mesh_blocks_gdf.crs}")
            return self.mesh_blocks_gdf

        except (DataLoadError, RiskAssessmentError):
            raise  # Re-raise our custom exceptions
        except Exception as e:
            raise DataLoadError(f"Failed to load mesh blocks: {e}") from e
```

---

## 3. Testing Infrastructure

### 3.1 Unit Tests Structure

```bash
tests/
├── __init__.py
├── conftest.py  # Pytest fixtures
├── test_gis_utils.py
├── test_mesh_block_analysis.py
├── test_photo_location_processor.py
├── test_photo_visualization.py
├── test_property_data_processor.py
├── test_spatial_visualization.py
└── fixtures/
    ├── sample_mesh_blocks.geojson
    ├── sample_property.json
    └── sample_photo_metadata.txt
```

**Example Test:**

```python
# tests/test_gis_utils.py
import pytest
import geopandas as gpd
from shapely.geometry import Point
from pipelines.gis_utils import GISUtils

class TestGISUtils:
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

    def test_create_point_gdf_with_reprojection(self):
        """Test creating point GeoDataFrame with CRS reprojection"""
        gdf = GISUtils.create_point_gdf(
            longitude=151.2093,
            latitude=-33.8688,
            target_crs='EPSG:3577'
        )

        assert gdf.crs.to_string() == 'EPSG:3577'
        # Check that coordinates changed (rough approximation)
        assert abs(gdf.geometry.iloc[0].x - 151.2093) > 100

    def test_ensure_crs_no_conversion_needed(self):
        """Test ensure_crs when already in target CRS"""
        gdf = gpd.GeoDataFrame(
            geometry=[Point(0, 0)],
            crs='EPSG:4326'
        )

        result = GISUtils.ensure_crs(gdf, 'EPSG:4326')
        assert result.crs.to_string() == 'EPSG:4326'
        assert result is gdf  # Should be same object

    def test_ensure_crs_with_conversion(self):
        """Test ensure_crs with CRS conversion"""
        gdf = gpd.GeoDataFrame(
            geometry=[Point(151.2093, -33.8688)],
            crs='EPSG:4326'
        )

        result = GISUtils.ensure_crs(gdf, 'EPSG:3577')
        assert result.crs.to_string() == 'EPSG:3577'

    def test_calculate_distance_geodesic(self):
        """Test geodesic distance calculation"""
        # Sydney to Melbourne (approx 714 km)
        sydney = (151.2093, -33.8688)
        melbourne = (144.9631, -37.8136)

        distance = GISUtils.calculate_distance_meters(sydney, melbourne, use_geodesic=True)

        # Approximate distance should be between 700-720 km
        assert 700_000 < distance < 720_000

    def test_calculate_distance_with_point_objects(self):
        """Test distance calculation with Point objects"""
        point1 = Point(151.2093, -33.8688)
        point2 = Point(144.9631, -37.8136)

        distance = GISUtils.calculate_distance_meters(point1, point2, use_geodesic=True)

        assert 700_000 < distance < 720_000
```

---

## 4. Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Create `pipelines/config.py` with AppConfig
- [ ] Create `pipelines/gis_utils.py` with GISUtils
- [ ] Create `pipelines/exceptions.py` with custom exceptions
- [ ] Add ProgressReporter to all pipelines
- [ ] Set up testing infrastructure

### Phase 2: Core Refactoring (Week 2)
- [ ] Refactor mesh_block_analysis_pipeline.py
- [ ] Refactor photo_location_processor.py
- [ ] Refactor photo_visualization_pipeline.py
- [ ] Replace all print statements with reporter methods
- [ ] Add comprehensive type hints

### Phase 3: Enhancement (Week 3)
- [ ] Refactor property_data_processor.py
- [ ] Refactor spatial_visualization_pipeline.py
- [ ] Refactor google_api_processor.py
- [ ] Add unit tests for all modules
- [ ] Add integration tests

### Phase 4: Documentation & Polish (Week 4)
- [ ] Update all docstrings to Google style
- [ ] Create API documentation
- [ ] Add usage examples
- [ ] Performance optimization
- [ ] Code review and cleanup

---

## 5. Additional Recommendations

### 5.1 Add Logging Infrastructure

```python
# pipelines/logging_config.py
import logging
from pathlib import Path

def setup_logging(
    log_file: str = 'data/logs/risk_assessment.log',
    level: int = logging.INFO
):
    """Configure logging for the application"""
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )

    # File handler
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(level)
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(console_formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return root_logger
```

### 5.2 Add Performance Monitoring

```python
# pipelines/performance.py
import time
import functools
from typing import Callable

def timer(func: Callable) -> Callable:
    """Decorator to time function execution"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"⏱️  {func.__name__} completed in {elapsed:.2f}s")
        return result
    return wrapper

# Usage
class MeshBlockAnalysisPipeline:
    @timer
    def load_mesh_blocks(self):
        # ... implementation
        pass
```

### 5.3 Add Data Validation

```python
# pipelines/validators.py
from typing import Any
import geopandas as gpd
from pipelines.exceptions import DataLoadError

class GeoDataFrameValidator:
    """Validator for GeoDataFrame objects"""

    @staticmethod
    def validate_crs(gdf: gpd.GeoDataFrame, expected_crs: str = None):
        """Validate GeoDataFrame has a CRS"""
        if gdf.crs is None:
            raise DataLoadError("GeoDataFrame has no CRS defined")

        if expected_crs and str(gdf.crs) != expected_crs:
            raise DataLoadError(
                f"GeoDataFrame CRS {gdf.crs} does not match expected {expected_crs}"
            )

    @staticmethod
    def validate_columns(gdf: gpd.GeoDataFrame, required_columns: list):
        """Validate GeoDataFrame has required columns"""
        missing = set(required_columns) - set(gdf.columns)
        if missing:
            raise DataLoadError(
                f"GeoDataFrame missing required columns: {missing}"
            )

    @staticmethod
    def validate_not_empty(gdf: gpd.GeoDataFrame):
        """Validate GeoDataFrame is not empty"""
        if len(gdf) == 0:
            raise DataLoadError("GeoDataFrame is empty")
```

---

## 6. Breaking Changes & Migration

### 6.1 API Changes

**Old:**
```python
pipeline = MeshBlockAnalysisPipeline(
    shapefile_path="data/raw/MB_2021_AUST_GDA2020.shp",
    buffer_distance=2000
)
```

**New:**
```python
from pipelines.config import config

pipeline = MeshBlockAnalysisPipeline(
    shapefile_path=config.paths.mesh_block_shapefile,
    buffer_distance=config.gis.default_buffer_distance_m,
    reporter=ProgressReporter("Mesh Block Analysis")
)
```

### 6.2 Migration Guide

1. **Update imports:**
   ```python
   # Old
   from pipelines.mesh_block_analysis_pipeline import MeshBlockAnalysisPipeline

   # New (same, but now requires reporter)
   from pipelines.mesh_block_analysis_pipeline import MeshBlockAnalysisPipeline
   from pipelines.pipeline_utils import ProgressReporter
   ```

2. **Update configuration:**
   - Create `config.json` file
   - Update scripts to use `config` object

3. **Update error handling:**
   - Replace generic exceptions with custom exceptions
   - Add try/except blocks with proper logging

---

## 7. Success Metrics

- [ ] 100% of pipelines use ProgressReporter
- [ ] 0 hard-coded configuration values
- [ ] >80% test coverage
- [ ] All public APIs have complete type hints
- [ ] All functions have Google-style docstrings
- [ ] <5% code duplication
- [ ] All scripts run without warnings

---

## 8. Resources & References

### Documentation
- GeoPandas: https://geopandas.org
- Shapely: https://shapely.readthedocs.io
- Matplotlib: https://matplotlib.org
- Python Type Hints: https://docs.python.org/3/library/typing.html

### Testing
- Pytest: https://pytest.org
- Pytest-cov: https://pytest-cov.readthedocs.io

### Code Quality
- Black (formatter): https://black.readthedocs.io
- Flake8 (linter): https://flake8.pycqa.org
- MyPy (type checker): https://mypy.readthedocs.io

---

## Conclusion

This refactoring plan provides a comprehensive roadmap for improving code quality, maintainability, and consistency. The phased approach allows for incremental improvements without disrupting existing functionality.

**Estimated Timeline:** 4 weeks
**Priority:** High (improves maintainability significantly)
**Risk:** Low (backward compatible with careful migration)
