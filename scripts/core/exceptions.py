"""
Custom Exception Hierarchy for Property Reporting System

Provides structured exception handling across all layers:
- API Layer: APIException
- ETL Layer: ETLException
- Report Generation: ReportGenerationException
- Data Processing: ProcessingException

All exceptions inherit from CoreException for consistent catching.

Author: Property Reporting System Refactoring
Date: 2025-11-10
"""

class CoreException(Exception):
    """Base exception for all property reporting system errors."""

    def __init__(self, message: str, details: dict = None):
        """
        Initialize exception with message and optional details.

        Args:
            message: Human-readable error message
            details: Additional error context (dict)
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict:
        """Convert exception to dictionary for logging/serialization."""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'details': self.details
        }


class APIException(CoreException):
    """Raised when API calls fail."""

    def __init__(self, message: str, status_code: int = None,
                 response_text: str = None, endpoint: str = None):
        """
        Initialize API exception.

        Args:
            message: Error message
            status_code: HTTP status code
            response_text: Raw response text
            endpoint: API endpoint that failed
        """
        details = {
            'status_code': status_code,
            'response_text': response_text,
            'endpoint': endpoint
        }
        super().__init__(message, details)
        self.status_code = status_code
        self.response_text = response_text
        self.endpoint = endpoint


class ETLException(CoreException):
    """Raised when ETL processing fails."""

    def __init__(self, message: str, stage: str = None,
                 input_data: dict = None, error: Exception = None):
        """
        Initialize ETL exception.

        Args:
            message: Error message
            stage: ETL stage where error occurred (extract/transform/load)
            input_data: Input data that caused the error (for debugging)
            error: Original exception if re-raising
        """
        details = {
            'stage': stage,
            'input_data_keys': list(input_data.keys()) if input_data else None,
            'original_error': str(error) if error else None
        }
        super().__init__(message, details)
        self.stage = stage
        self.original_error = error


class ReportGenerationException(CoreException):
    """Raised when report generation fails."""

    def __init__(self, message: str, report_type: str = None,
                 missing_data: list = None, validation_errors: dict = None):
        """
        Initialize report generation exception.

        Args:
            message: Error message
            report_type: Type of report being generated
            missing_data: List of missing required data fields
            validation_errors: Dictionary of validation errors
        """
        details = {
            'report_type': report_type,
            'missing_data': missing_data,
            'validation_errors': validation_errors
        }
        super().__init__(message, details)
        self.report_type = report_type
        self.missing_data = missing_data
        self.validation_errors = validation_errors


class ProcessingException(CoreException):
    """Raised when data processing fails."""

    def __init__(self, message: str, processor: str = None,
                 input_data: dict = None, error: Exception = None):
        """
        Initialize processing exception.

        Args:
            message: Error message
            processor: Name of processor that failed
            input_data: Input data that caused the error
            error: Original exception if re-raising
        """
        details = {
            'processor': processor,
            'input_data_keys': list(input_data.keys()) if input_data else None,
            'original_error': str(error) if error else None
        }
        super().__init__(message, details)
        self.processor = processor
        self.original_error = error


class ValidationException(CoreException):
    """Raised when data validation fails."""

    def __init__(self, message: str, validation_errors: dict = None,
                 schema: str = None):
        """
        Initialize validation exception.

        Args:
            message: Error message
            validation_errors: Dictionary of field validation errors
            schema: Schema that failed validation
        """
        details = {
            'validation_errors': validation_errors,
            'schema': schema
        }
        super().__init__(message, details)
        self.validation_errors = validation_errors
        self.schema = schema


class AuthenticationException(APIException):
    """Raised when API authentication fails."""

    def __init__(self, message: str, api_name: str = None):
        """
        Initialize authentication exception.

        Args:
            message: Error message
            api_name: Name of API that failed authentication
        """
        super().__init__(
            message=message,
            status_code=401,
            endpoint='authentication'
        )
        self.details['api_name'] = api_name


class RateLimitException(APIException):
    """Raised when API rate limit is exceeded."""

    def __init__(self, message: str, retry_after: int = None):
        """
        Initialize rate limit exception.

        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
        """
        super().__init__(
            message=message,
            status_code=429,
            endpoint=None
        )
        self.details['retry_after'] = retry_after
        self.retry_after = retry_after


class DataNotFoundException(CoreException):
    """Raised when required data is not found."""

    def __init__(self, message: str, resource_type: str = None,
                 resource_id: str = None):
        """
        Initialize data not found exception.

        Args:
            message: Error message
            resource_type: Type of resource not found
            resource_id: ID of resource not found
        """
        details = {
            'resource_type': resource_type,
            'resource_id': resource_id
        }
        super().__init__(message, details)
        self.resource_type = resource_type
        self.resource_id = resource_id


class ConfigurationException(CoreException):
    """Raised when configuration is invalid or missing."""

    def __init__(self, message: str, config_key: str = None,
                 required_keys: list = None):
        """
        Initialize configuration exception.

        Args:
            message: Error message
            config_key: Configuration key that failed
            required_keys: List of required configuration keys
        """
        details = {
            'config_key': config_key,
            'required_keys': required_keys
        }
        super().__init__(message, details)
        self.config_key = config_key
        self.required_keys = required_keys
