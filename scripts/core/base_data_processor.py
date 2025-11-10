"""
Base Data Processor

Abstract base class for business logic processors.
Processors transform data according to business rules without making API calls.

Examples:
- ComparableProcessor: Ranks comparable properties
- ImpactProcessor: Categorizes property impacts
- RiskProcessor: Calculates risk scores
- MarketProcessor: Analyzes market trends

Author: Property Reporting System Refactoring
Date: 2025-11-10
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from .exceptions import ProcessingException, ValidationException


class BaseDataProcessor(ABC):
    """
    Abstract base class for business logic processors.

    Subclasses must implement:
    - process(): Apply business logic to data

    Provides:
    - Input validation
    - Error handling
    - Configuration management
    """

    def __init__(self, reporter=None, config: Dict[str, Any] = None):
        """
        Initialize processor.

        Args:
            reporter: ProgressReporter for logging
            config: Configuration dictionary
        """
        self.reporter = reporter
        self.config = config or {}

    @abstractmethod
    def process(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Process data according to business logic.

        Must be implemented by subclasses.

        Args:
            data: Input data
            **kwargs: Additional processing parameters

        Returns:
            Processed data

        Raises:
            ProcessingException: On processing failure
        """
        pass

    def validate_input(self, data: Dict[str, Any],
                      required_fields: list = None) -> bool:
        """
        Validate input data.

        Can be overridden by subclasses.

        Args:
            data: Data to validate
            required_fields: List of required field names

        Returns:
            True if valid

        Raises:
            ValidationException: If validation fails
        """
        if not data:
            raise ValidationException(
                "Input data is empty",
                validation_errors={'data': 'Cannot be empty'}
            )

        if required_fields:
            missing = [field for field in required_fields if field not in data]
            if missing:
                raise ValidationException(
                    f"Missing required fields: {', '.join(missing)}",
                    validation_errors={'missing_fields': missing}
                )

        return True

    def validate_output(self, data: Dict[str, Any]) -> bool:
        """
        Validate output data.

        Can be overridden by subclasses.

        Args:
            data: Data to validate

        Returns:
            True if valid

        Raises:
            ValidationException: If validation fails
        """
        if not data:
            raise ValidationException(
                "Output data is empty",
                validation_errors={'data': 'Cannot be empty'}
            )
        return True
