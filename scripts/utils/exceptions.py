"""
Custom Exceptions for Risk Assessment System

This module defines a hierarchy of custom exceptions for better error handling
and reporting throughout the application. All exceptions inherit from
RiskAssessmentError for easy catching of any application-specific error.

Usage:
    from pipelines.exceptions import DataLoadError, APIError

    try:
        gdf = load_shapefile(path)
    except DataLoadError as e:
        logger.error(f"Failed to load data: {e}")
        raise

Exception Hierarchy:
    RiskAssessmentError (base)
    ├── DataLoadError
    │   ├── ShapefileLoadError
    │   └── MetadataLoadError
    ├── DataValidationError
    ├── GISOperationError
    │   ├── CRSConversionError
    │   └── BufferCreationError
    ├── APIError
    │   ├── CoreLogicAPIError
    │   └── GoogleAPIError
    └── ConfigurationError

Author: Brendan Darcy
Date: 2025-11-09
"""


class RiskAssessmentError(Exception):
    """
    Base exception for risk assessment system.

    All custom exceptions should inherit from this class to allow
    catching any application-specific error.
    """
    pass


# ============================================================================
# Data Loading Errors
# ============================================================================

class DataLoadError(RiskAssessmentError):
    """
    Error loading data from file or API.

    Raised when:
    - File not found
    - File is corrupted or unreadable
    - File format is invalid
    - Required fields are missing
    """
    pass


class ShapefileLoadError(DataLoadError):
    """
    Error loading shapefile data.

    Raised when:
    - Shapefile components are missing (.shp, .shx, .dbf)
    - Shapefile is corrupted
    - Shapefile has invalid geometry
    - Required columns are missing
    """
    pass


class MetadataLoadError(DataLoadError):
    """
    Error loading metadata file.

    Raised when:
    - Metadata file not found
    - Metadata file has invalid format
    - Required metadata fields are missing
    - Metadata values are invalid
    """
    pass


# ============================================================================
# Data Validation Errors
# ============================================================================

class DataValidationError(RiskAssessmentError):
    """
    Error validating data.

    Raised when:
    - Data fails validation checks
    - Data is outside valid range
    - Data types are incorrect
    - Required fields are empty
    """
    pass


class GeoDataFrameValidationError(DataValidationError):
    """
    Error validating GeoDataFrame.

    Raised when:
    - GeoDataFrame is empty
    - GeoDataFrame has no CRS
    - GeoDataFrame is missing required columns
    - Geometry is invalid
    """
    pass


class CoordinateValidationError(DataValidationError):
    """
    Error validating coordinates.

    Raised when:
    - Latitude is outside [-90, 90] range
    - Longitude is outside [-180, 180] range
    - Coordinates are NaN or infinite
    """
    pass


# ============================================================================
# GIS Operation Errors
# ============================================================================

class GISOperationError(RiskAssessmentError):
    """
    Error during GIS operation.

    Raised when:
    - CRS conversion fails
    - Buffer creation fails
    - Spatial join fails
    - Geometry operation fails
    """
    pass


class CRSConversionError(GISOperationError):
    """
    Error converting between coordinate reference systems.

    Raised when:
    - Source or target CRS is invalid
    - CRS transformation fails
    - CRS is undefined
    """
    pass


class BufferCreationError(GISOperationError):
    """
    Error creating buffer around geometry.

    Raised when:
    - Buffer distance is invalid (negative or zero)
    - Geometry is invalid for buffering
    - Buffer operation fails
    """
    pass


class SpatialJoinError(GISOperationError):
    """
    Error performing spatial join.

    Raised when:
    - CRS mismatch between datasets
    - Invalid spatial predicate
    - Join operation fails
    """
    pass


# ============================================================================
# API Errors
# ============================================================================

class APIError(RiskAssessmentError):
    """
    Error calling external API.

    Raised when:
    - API request fails
    - API returns error response
    - API authentication fails
    - Rate limit exceeded
    - Network error occurs
    """

    def __init__(self, message: str, status_code: int = None, response_body: str = None):
        """
        Initialize API error with optional HTTP details.

        Args:
            message: Error message
            status_code: HTTP status code (if applicable)
            response_body: Response body (if applicable)
        """
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class CoreLogicAPIError(APIError):
    """
    Error calling CoreLogic API.

    Raised when:
    - Authentication fails
    - Property not found
    - API request fails
    - Rate limit exceeded
    """
    pass


class GoogleAPIError(APIError):
    """
    Error calling Google API (Maps, Places, Geocoding).

    Raised when:
    - API key is invalid or missing
    - Request quota exceeded
    - Geocoding fails
    - Places search fails
    - Static Maps request fails
    """
    pass


# ============================================================================
# Configuration Errors
# ============================================================================

class ConfigurationError(RiskAssessmentError):
    """
    Configuration error.

    Raised when:
    - Configuration file is invalid or missing
    - Required configuration parameter is missing
    - Configuration value is invalid
    - Environment variable is missing
    """
    pass


class MissingAPIKeyError(ConfigurationError):
    """
    Required API key is missing from environment.

    Raised when:
    - GOOGLE_API_KEY is not set
    - CORELOGIC_CLIENT_ID or CORELOGIC_CLIENT_SECRET is not set
    """

    def __init__(self, api_name: str):
        """
        Initialize with API name.

        Args:
            api_name: Name of the API (e.g., "Google", "CoreLogic")
        """
        super().__init__(
            f"{api_name} API credentials not found in environment.\n"
            f"Please set the required environment variables."
        )
        self.api_name = api_name


# ============================================================================
# Pipeline Errors
# ============================================================================

class PipelineError(RiskAssessmentError):
    """
    Error during pipeline execution.

    Raised when:
    - Pipeline step fails
    - Required input is missing
    - Output cannot be created
    """
    pass


class PipelineConfigurationError(PipelineError):
    """
    Error configuring pipeline.

    Raised when:
    - Required parameter is missing
    - Parameter value is invalid
    - Pipeline cannot be initialized
    """
    pass


# ============================================================================
# Visualization Errors
# ============================================================================

class VisualizationError(RiskAssessmentError):
    """
    Error creating visualization.

    Raised when:
    - Plot creation fails
    - Basemap loading fails
    - Image save fails
    - Invalid visualization parameters
    """
    pass


class BasemapError(VisualizationError):
    """
    Error loading or rendering basemap.

    Raised when:
    - Basemap source is invalid
    - Basemap API request fails
    - Basemap cannot be rendered
    """
    pass
