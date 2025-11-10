"""
Type Protocols and Interfaces

Defines protocols (structural typing) for all major components.
These can be used for type hints and dependency injection without
requiring inheritance from base classes.

Author: Property Reporting System Refactoring
Date: 2025-11-10
"""

from typing import Protocol, Dict, Any, Optional
from pathlib import Path


class APIClientProtocol(Protocol):
    """Protocol for API clients."""

    def authenticate(self) -> str:
        """Authenticate and return access token."""
        ...

    def make_request(
        self,
        endpoint: str,
        method: str = 'GET',
        params: Dict[str, Any] = None,
        data: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """Make authenticated API request."""
        ...

    def get_access_token(self) -> str:
        """Get valid access token."""
        ...


class ETLProcessorProtocol(Protocol):
    """Protocol for ETL processors."""

    def extract(self, **kwargs) -> Dict[str, Any]:
        """Extract raw data from source."""
        ...

    def transform(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform raw data."""
        ...

    def load(self, transformed_data: Dict[str, Any],
             output_path: Path) -> Path:
        """Load transformed data to output."""
        ...

    def run(self, output_path: Path, **extract_kwargs) -> Dict[str, Any]:
        """Run complete ETL pipeline."""
        ...


class ReportGeneratorProtocol(Protocol):
    """Protocol for report generators."""

    def gather_data(self) -> Dict[str, Any]:
        """Gather data from processed sources."""
        ...

    def generate(self) -> Path:
        """Generate the report."""
        ...

    def run(self) -> Path:
        """Run complete report generation."""
        ...


class DataProcessorProtocol(Protocol):
    """Protocol for data processors."""

    def process(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Process data according to business logic."""
        ...

    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data."""
        ...


class ReporterProtocol(Protocol):
    """Protocol for progress reporters."""

    def info(self, message: str) -> None:
        """Log info message."""
        ...

    def success(self, message: str) -> None:
        """Log success message."""
        ...

    def warning(self, message: str) -> None:
        """Log warning message."""
        ...

    def error(self, message: str) -> None:
        """Log error message."""
        ...

    def debug(self, message: str) -> None:
        """Log debug message."""
        ...
