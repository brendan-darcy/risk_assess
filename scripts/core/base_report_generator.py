"""
Base Report Generator

Abstract base class for all report generators (PDF, JSON, HTML, etc.).
Report generators consume processed data (ETL outputs) only - no API calls.

Provides consistent patterns for:
- Data aggregation from multiple sources
- Report validation
- Template rendering
- File output
- Progress reporting

Author: Property Reporting System Refactoring
Date: 2025-11-10
"""

import json
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from .exceptions import ReportGenerationException, ValidationException


class BaseReportGenerator(ABC):
    """
    Abstract base class for report generators.

    Subclasses must implement:
    - gather_data(): Collect data from processed sources
    - generate(): Create the report

    Provides:
    - Data loading utilities
    - Validation methods
    - File I/O
    - Error handling
    """

    def __init__(
        self,
        property_id: str,
        data_dir: Path,
        reporter=None,
        config: Dict[str, Any] = None
    ):
        """
        Initialize report generator.

        Args:
            property_id: Property ID for report
            data_dir: Directory containing processed data files
            reporter: ProgressReporter for logging
            config: Configuration dictionary
        """
        self.property_id = property_id
        self.data_dir = Path(data_dir)
        self.reporter = reporter
        self.config = config or {}

        # Report state
        self._gathered_data: Optional[Dict] = None
        self._output_path: Optional[Path] = None
        self._missing_data: List[str] = []

        # Metadata
        self._start_time: Optional[datetime] = None
        self._end_time: Optional[datetime] = None

    @abstractmethod
    def gather_data(self) -> Dict[str, Any]:
        """
        Gather data from processed sources.

        Must be implemented by subclasses.

        Should load data from ETL output files, not make API calls.

        Returns:
            Dictionary with all required data

        Raises:
            ReportGenerationException: On data gathering failure
        """
        pass

    @abstractmethod
    def generate(self) -> Path:
        """
        Generate the report.

        Must be implemented by subclasses.

        Returns:
            Path to generated report file

        Raises:
            ReportGenerationException: On generation failure
        """
        pass

    def validate_required_fields(
        self,
        data: Dict[str, Any],
        required_fields: List[str]
    ) -> bool:
        """
        Validate that required fields are present in data.

        Args:
            data: Data dictionary to validate
            required_fields: List of required field names

        Returns:
            True if all fields present

        Raises:
            ValidationException: If required fields missing
        """
        missing = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing.append(field)

        if missing:
            raise ValidationException(
                f"Missing required fields: {', '.join(missing)}",
                validation_errors={'missing_fields': missing}
            )

        return True

    def load_processed_file(
        self,
        filename: str,
        required: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Load processed data file.

        Args:
            filename: Name of file to load (e.g., 'property_details.json')
            required: Whether file is required

        Returns:
            Loaded data dictionary or None if file doesn't exist

        Raises:
            ReportGenerationException: If required file missing
        """
        filepath = self.data_dir / filename

        if not filepath.exists():
            if required:
                raise ReportGenerationException(
                    f"Required data file not found: {filename}",
                    missing_data=[filename]
                )
            else:
                if self.reporter:
                    self.reporter.warning(f"Optional data file not found: {filename}")
                self._missing_data.append(filename)
                return None

        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            if self.reporter:
                self.reporter.debug(f"Loaded data from {filename}")

            return data

        except Exception as e:
            raise ReportGenerationException(
                f"Failed to load {filename}: {str(e)}"
            )

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
            ReportGenerationException: On save failure
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w') as f:
                json.dump(data, f, indent=indent, default=str)

            return output_path

        except Exception as e:
            raise ReportGenerationException(
                f"Failed to save report to {output_path}: {str(e)}"
            )

    def run(self) -> Path:
        """
        Run complete report generation.

        Returns:
            Path to generated report

        Raises:
            ReportGenerationException: On generation failure
        """
        self._start_time = datetime.now()

        try:
            # Gather data
            if self.reporter:
                self.reporter.info("Gathering report data...")

            self._gathered_data = self.gather_data()

            if self.reporter:
                self.reporter.success("Data gathered successfully")

            # Generate report
            if self.reporter:
                self.reporter.info("Generating report...")

            self._output_path = self.generate()

            if self.reporter:
                self.reporter.success(f"Report generated: {self._output_path}")

            self._end_time = datetime.now()

            return self._output_path

        except ReportGenerationException:
            self._end_time = datetime.now()
            raise

        except Exception as e:
            self._end_time = datetime.now()
            raise ReportGenerationException(
                f"Report generation failed: {str(e)}"
            )

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get report generation metadata.

        Returns:
            Dictionary with generation metadata
        """
        duration = None
        if self._start_time and self._end_time:
            duration = (self._end_time - self._start_time).total_seconds()

        return {
            'generator': self.__class__.__name__,
            'property_id': self.property_id,
            'start_time': self._start_time.isoformat() if self._start_time else None,
            'end_time': self._end_time.isoformat() if self._end_time else None,
            'duration_seconds': duration,
            'output_path': str(self._output_path) if self._output_path else None,
            'missing_data': self._missing_data
        }

    def get_property_files(self) -> Dict[str, Path]:
        """
        Get all property data files in data directory.

        Returns:
            Dictionary mapping data types to file paths
        """
        files = {}
        patterns = {
            'property_details': f'{self.property_id}_property_details.json',
            'geospatial_layers': f'{self.property_id}_geospatial_layers.json',
            'comparable_sales': f'{self.property_id}_comparable_sales.json',
            'property_impacts': f'{self.property_id}_property_impacts.json',
            'mesh_block_analysis': f'{self.property_id}_mesh_block_analysis.json',
            'property_images': f'{self.property_id}_property_images.json',
            'development_approvals': f'{self.property_id}_development_approvals.json',
            'comprehensive_report': f'{self.property_id}_comprehensive_report.json'
        }

        for data_type, filename in patterns.items():
            filepath = self.data_dir / filename
            if filepath.exists():
                files[data_type] = filepath

        return files


class BaseDataProcessor(ABC):
    """
    Abstract base class for business logic processors.

    Processors implement business logic without direct API calls:
    - Comparable ranking
    - Impact categorization
    - Risk scoring
    - Market analysis

    Subclasses must implement:
    - process(): Apply business logic to data
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

    def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data.

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
                "Input data is empty",
                validation_errors={'data': 'Cannot be empty'}
            )
        return True
