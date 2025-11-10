"""
Core Base Classes and Interfaces

This module provides the foundation for the entire property reporting system
through abstract base classes that enforce DRY principles and proper data flow.

Base Classes:
- BaseAPIClient: For all API clients (CoreLogic, Google, Vicmap)
- BaseETLProcessor: For all ETL pipelines (Extract, Transform, Load)
- BaseReportGenerator: For all report generators
- BaseDataProcessor: For business logic processors

Author: Property Reporting System Refactoring
Date: 2025-11-10
"""

from .base_api_client import BaseAPIClient
from .base_etl_processor import BaseETLProcessor
from .base_report_generator import BaseReportGenerator
from .base_data_processor import BaseDataProcessor
from .interfaces import (
    APIClientProtocol,
    ETLProcessorProtocol,
    ReportGeneratorProtocol,
    DataProcessorProtocol
)
from .exceptions import (
    CoreException,
    APIException,
    ETLException,
    ReportGenerationException,
    ProcessingException,
    ValidationException
)

__all__ = [
    'BaseAPIClient',
    'BaseETLProcessor',
    'BaseReportGenerator',
    'BaseDataProcessor',
    'APIClientProtocol',
    'ETLProcessorProtocol',
    'ReportGeneratorProtocol',
    'DataProcessorProtocol',
    'CoreException',
    'APIException',
    'ETLException',
    'ReportGenerationException',
    'ProcessingException',
    'ValidationException'
]
