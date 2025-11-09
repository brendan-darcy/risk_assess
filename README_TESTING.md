# Testing Guide for Risk Assessment System

This document describes the testing infrastructure and how to run tests.

## Test Structure

```
tests/
├── __init__.py                      # Test package init
├── conftest.py                      # Pytest fixtures and configuration
├── test_config.py                   # Configuration tests
├── test_gis_utils.py               # GIS utility tests
├── test_exceptions.py              # Exception hierarchy tests (TODO)
├── test_pipeline_utils.py          # Pipeline utility tests (TODO)
├── test_mesh_block_analysis.py     # Mesh block pipeline tests (TODO)
├── test_photo_location_processor.py # Photo processor tests (TODO)
├── test_photo_visualization.py     # Photo visualization tests (TODO)
├── test_property_data_processor.py # Property processor tests (TODO)
└── test_spatial_visualization.py   # Spatial visualization tests (TODO)
```

## Installation

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=pipelines --cov-report=html --cov-report=term
```

### Run specific test categories

```bash
# Run only unit tests
pytest -m unit

# Run only GIS tests
pytest -m gis

# Run integration tests
pytest -m integration

# Run all except slow/API tests
pytest -m "not slow and not api"
```

### Run specific test files
```bash
pytest tests/test_gis_utils.py
pytest tests/test_config.py
```

### Run specific test classes or functions
```bash
pytest tests/test_gis_utils.py::TestCreatePointGDF
pytest tests/test_gis_utils.py::TestCreatePointGDF::test_create_point_gdf_wgs84
```

### Run with verbose output
```bash
pytest -v
pytest -vv  # Extra verbose
```

## Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Unit tests for individual functions
- `@pytest.mark.integration` - Integration tests requiring multiple components
- `@pytest.mark.api` - Tests that make real API calls (slow, requires credentials)
- `@pytest.mark.gis` - Tests involving GIS operations and GeoDataFrames
- `@pytest.mark.slow` - Slow tests that take more than a few seconds
- `@pytest.mark.skip_ci` - Tests to skip in CI environment

## Test Fixtures

Common fixtures are defined in `conftest.py`:

### Temporary Directories
- `temp_dir` - Creates a temporary directory for test outputs

### Sample Data
- `sample_point_wgs84` - Sample Point in WGS84
- `sample_point_gdf_wgs84` - Sample GeoDataFrame with single point
- `sample_polygon_wgs84` - Sample Polygon in WGS84
- `sample_property_coords` - Sample property coordinates
- `sample_mesh_blocks_gdf` - Sample mesh blocks GeoDataFrame
- `sample_photo_metadata` - Sample photo metadata dictionary
- `sample_photo_metadata_file` - Temporary photo metadata file

### Configuration
- `sample_config_dict` - Sample configuration dictionary
- `sample_config_file` - Temporary config file

### Mock API Responses
- `mock_corelogic_response` - Mock CoreLogic API response
- `mock_google_places_response` - Mock Google Places API response

## Writing New Tests

### Example Unit Test

```python
import pytest
from pipelines.gis_utils import GISUtils

@pytest.mark.unit
@pytest.mark.gis
class TestMyFunction:
    """Tests for my_function"""

    def test_basic_functionality(self):
        """Test basic functionality"""
        result = GISUtils.my_function(input_value)
        assert result == expected_value

    def test_edge_case(self):
        """Test edge case"""
        with pytest.raises(ValueError):
            GISUtils.my_function(invalid_input)
```

### Example Integration Test

```python
import pytest
from pipelines.mesh_block_analysis_pipeline import MeshBlockAnalysisPipeline

@pytest.mark.integration
@pytest.mark.gis
class TestMeshBlockAnalysis:
    """Integration tests for mesh block analysis"""

    def test_full_analysis_workflow(self, temp_dir, sample_mesh_blocks_gdf):
        """Test complete analysis workflow"""
        pipeline = MeshBlockAnalysisPipeline(
            shapefile_path=temp_dir / 'test.shp',
            buffer_distance=2000
        )
        # ... test implementation
```

## Code Coverage

View coverage report:

```bash
# Generate HTML coverage report
pytest --cov=pipelines --cov-report=html

# Open in browser (macOS)
open htmlcov/index.html

# Open in browser (Linux)
xdg-open htmlcov/index.html
```

Coverage goals:
- Overall: >80%
- Critical modules (gis_utils, config): >90%
- New code: 100%

## Code Quality

### Run linter (flake8)
```bash
flake8 pipelines/
```

### Run type checker (mypy)
```bash
mypy pipelines/
```

### Run code formatter (black)
```bash
# Check formatting
black --check pipelines/

# Apply formatting
black pipelines/
```

### Run import sorter (isort)
```bash
# Check import order
isort --check pipelines/

# Apply import sorting
isort pipelines/
```

## Continuous Integration

All tests are run automatically on:
- Every commit (local pre-commit hooks)
- Every pull request (GitHub Actions)
- Before deployment

Slow and API tests are skipped in CI:
```bash
pytest -m "not slow and not api"
```

## Test Data

Test data files are located in `tests/fixtures/`:
- `sample_mesh_blocks.geojson` - Sample mesh block data
- `sample_property.json` - Sample property data
- `sample_photo_metadata.txt` - Sample photo metadata

## Debugging Tests

### Run with debugging
```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger on first failure
pytest -x --pdb
```

### Use IPython for debugging
```python
import pytest

def test_my_function():
    result = my_function()

    # Drop into IPython shell
    import IPython; IPython.embed()

    assert result == expected
```

## Best Practices

1. **Test Organization**
   - One test file per module
   - Group related tests in classes
   - Use descriptive test names

2. **Test Independence**
   - Each test should be independent
   - Use fixtures for setup/teardown
   - Don't rely on test execution order

3. **Test Coverage**
   - Test happy paths
   - Test edge cases
   - Test error conditions
   - Test boundary values

4. **Performance**
   - Keep unit tests fast (<1s each)
   - Mark slow tests with `@pytest.mark.slow`
   - Use mocks for external dependencies

5. **Documentation**
   - Add docstrings to test classes/functions
   - Explain what is being tested
   - Document any non-obvious behavior

## Troubleshooting

### ImportError: No module named 'pipelines'
Add project root to PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### GIS tests failing
Ensure GDAL and geopandas are properly installed:
```bash
conda install -c conda-forge geopandas
```

### API tests requiring credentials
Set environment variables:
```bash
export GOOGLE_API_KEY="your_key"
export CORELOGIC_CLIENT_ID="your_id"
export CORELOGIC_CLIENT_SECRET="your_secret"
```

Or skip API tests:
```bash
pytest -m "not api"
```

## Future Enhancements

- [ ] Add integration tests for all pipelines
- [ ] Add performance benchmarks
- [ ] Add visual regression tests for plots
- [ ] Set up automated test data generation
- [ ] Add contract tests for API integrations
- [ ] Set up mutation testing
- [ ] Add property-based tests with Hypothesis
