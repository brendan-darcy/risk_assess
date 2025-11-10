"""
Base ETL Processor

Abstract base class for all ETL (Extract, Transform, Load) processors.
Enforces clean data flow: RAW DATA → PROCESSING → PROCESSED OUTPUT

Provides consistent patterns for:
- Data extraction from APIs
- Data transformation and validation
- Data loading (saving processed outputs)
- Error handling and logging
- Progress reporting

Author: Property Reporting System Refactoring
Date: 2025-11-10
"""

import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

from .exceptions import ETLException, ValidationException
from .base_api_client import BaseAPIClient


class BaseETLProcessor(ABC):
    """
    Abstract base class for ETL processors.

    Subclasses must implement:
    - extract(): Get raw data from source
    - transform(): Process and validate data
    - load(): Save processed data

    Provides:
    - run(): Orchestrates ETL pipeline
    - Validation methods
    - File I/O utilities
    - Error handling
    """

    def __init__(
        self,
        api_client: Optional[BaseAPIClient] = None,
        reporter=None,
        config: Dict[str, Any] = None
    ):
        """
        Initialize ETL processor.

        Args:
            api_client: API client for data extraction
            reporter: ProgressReporter for logging
            config: Configuration dictionary
        """
        self.api_client = api_client
        self.reporter = reporter
        self.config = config or {}

        # ETL state
        self._raw_data: Optional[Dict] = None
        self._transformed_data: Optional[Dict] = None
        self._output_path: Optional[Path] = None

        # Metadata
        self._start_time: Optional[datetime] = None
        self._end_time: Optional[datetime] = None
        self._errors: List[Dict] = []

    @abstractmethod
    def extract(self, **kwargs) -> Dict[str, Any]:
        """
        Extract raw data from source (API, file, database).

        Must be implemented by subclasses.

        Args:
            **kwargs: Extraction parameters (property_id, location, etc.)

        Returns:
            Raw data dictionary

        Raises:
            ETLException: On extraction failure
        """
        pass

    @abstractmethod
    def transform(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform raw data into processed format.

        Must be implemented by subclasses.

        Args:
            raw_data: Raw data from extract()

        Returns:
            Transformed data dictionary

        Raises:
            ETLException: On transformation failure
        """
        pass

    @abstractmethod
    def load(self, transformed_data: Dict[str, Any],
             output_path: Path) -> Path:
        """
        Load (save) transformed data to output.

        Must be implemented by subclasses.

        Args:
            transformed_data: Transformed data from transform()
            output_path: Path to save output

        Returns:
            Path to saved file

        Raises:
            ETLException: On load failure
        """
        pass

    def validate_raw_data(self, raw_data: Dict[str, Any]) -> bool:
        """
        Validate raw data before transformation.

        Can be overridden by subclasses for custom validation.

        Args:
            raw_data: Raw data to validate

        Returns:
            True if valid

        Raises:
            ValidationException: If validation fails
        """
        if not raw_data:
            raise ValidationException(
                "Raw data is empty",
                validation_errors={'raw_data': 'Cannot be empty'}
            )
        return True

    def validate_transformed_data(self, transformed_data: Dict[str, Any]) -> bool:
        """
        Validate transformed data before loading.

        Can be overridden by subclasses for custom validation.

        Args:
            transformed_data: Transformed data to validate

        Returns:
            True if valid

        Raises:
            ValidationException: If validation fails
        """
        if not transformed_data:
            raise ValidationException(
                "Transformed data is empty",
                validation_errors={'transformed_data': 'Cannot be empty'}
            )
        return True

    def run(
        self,
        output_path: Path,
        **extract_kwargs
    ) -> Dict[str, Any]:
        """
        Run complete ETL pipeline.

        Args:
            output_path: Path to save processed output
            **extract_kwargs: Parameters for extract()

        Returns:
            Dictionary with ETL results and metadata

        Raises:
            ETLException: On any ETL stage failure
        """
        self._start_time = datetime.now()
        self._errors = []

        try:
            # Stage 1: Extract
            if self.reporter:
                self.reporter.info(f"Extracting data...")

            try:
                self._raw_data = self.extract(**extract_kwargs)
                self.validate_raw_data(self._raw_data)
            except Exception as e:
                raise ETLException(
                    f"Extraction failed: {str(e)}",
                    stage='extract',
                    error=e
                )

            if self.reporter:
                self.reporter.success(f"Extraction complete")

            # Stage 2: Transform
            if self.reporter:
                self.reporter.info(f"Transforming data...")

            try:
                self._transformed_data = self.transform(self._raw_data)
                self.validate_transformed_data(self._transformed_data)
            except Exception as e:
                raise ETLException(
                    f"Transformation failed: {str(e)}",
                    stage='transform',
                    input_data=self._raw_data,
                    error=e
                )

            if self.reporter:
                self.reporter.success(f"Transformation complete")

            # Stage 3: Load
            if self.reporter:
                self.reporter.info(f"Loading data to {output_path}")

            try:
                self._output_path = self.load(self._transformed_data, output_path)
            except Exception as e:
                raise ETLException(
                    f"Load failed: {str(e)}",
                    stage='load',
                    error=e
                )

            if self.reporter:
                self.reporter.success(f"Data saved to {self._output_path}")

            self._end_time = datetime.now()

            # Return results
            return {
                'status': 'success',
                'output_path': str(self._output_path),
                'metadata': self._get_metadata(),
                'data': self._transformed_data
            }

        except ETLException:
            self._end_time = datetime.now()
            raise

        except Exception as e:
            self._end_time = datetime.now()
            raise ETLException(
                f"ETL pipeline failed: {str(e)}",
                error=e
            )

    def _get_metadata(self) -> Dict[str, Any]:
        """
        Get ETL metadata.

        Returns:
            Dictionary with processing metadata
        """
        duration = None
        if self._start_time and self._end_time:
            duration = (self._end_time - self._start_time).total_seconds()

        return {
            'processor': self.__class__.__name__,
            'start_time': self._start_time.isoformat() if self._start_time else None,
            'end_time': self._end_time.isoformat() if self._end_time else None,
            'duration_seconds': duration,
            'errors': self._errors,
            'output_path': str(self._output_path) if self._output_path else None
        }

    def save_json(
        self,
        data: Dict[str, Any],
        output_path: Path,
        indent: int = 2
    ) -> Path:
        """
        Save data as JSON file.

        Args:
            data: Data to save
            output_path: Output file path
            indent: JSON indentation

        Returns:
            Path to saved file

        Raises:
            ETLException: On save failure
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w') as f:
                json.dump(data, f, indent=indent, default=str)

            return output_path

        except Exception as e:
            raise ETLException(
                f"Failed to save JSON to {output_path}: {str(e)}",
                stage='load',
                error=e
            )

    def load_json(self, input_path: Path) -> Dict[str, Any]:
        """
        Load data from JSON file.

        Args:
            input_path: Input file path

        Returns:
            Loaded data dictionary

        Raises:
            ETLException: On load failure
        """
        try:
            input_path = Path(input_path)

            if not input_path.exists():
                raise FileNotFoundError(f"File not found: {input_path}")

            with open(input_path, 'r') as f:
                return json.load(f)

        except Exception as e:
            raise ETLException(
                f"Failed to load JSON from {input_path}: {str(e)}",
                stage='extract',
                error=e
            )

    def flatten_dict(
        self,
        data: Dict[str, Any],
        parent_key: str = '',
        sep: str = '_'
    ) -> Dict[str, Any]:
        """
        Flatten nested dictionary.

        Args:
            data: Dictionary to flatten
            parent_key: Parent key prefix
            sep: Separator between nested keys

        Returns:
            Flattened dictionary
        """
        items = []

        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k

            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep).items())
            elif isinstance(v, list):
                # Handle lists of primitives
                if v and not isinstance(v[0], (dict, list)):
                    items.append((new_key, v))
                # Handle lists of dicts
                elif v and isinstance(v[0], dict):
                    for i, item in enumerate(v):
                        items.extend(
                            self.flatten_dict(item, f"{new_key}{sep}{i}", sep).items()
                        )
                else:
                    items.append((new_key, v))
            else:
                items.append((new_key, v))

        return dict(items)

    def add_error(self, error: str, context: Dict = None):
        """
        Record an error without stopping execution.

        Args:
            error: Error message
            context: Additional error context
        """
        self._errors.append({
            'error': error,
            'context': context or {},
            'timestamp': datetime.now().isoformat()
        })

        if self.reporter:
            self.reporter.warning(error)

    def get_errors(self) -> List[Dict]:
        """
        Get all recorded errors.

        Returns:
            List of error dictionaries
        """
        return self._errors
