#!/usr/bin/env python3
"""
Mapping Engine

Reads YAML configuration and extracts data from multiple JSON sources.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from .extraction_utils import (
    get_nested_value,
    format_missing_value,
    truncate_text,
    format_currency,
    format_percentage,
    format_area,
    format_date
)


class MappingEngine:
    """Extracts data based on YAML configuration"""

    def __init__(self, config_path: str = None):
        """
        Initialize mapping engine.

        Args:
            config_path: Path to YAML config file
        """
        if config_path is None:
            # Default to config/report_mapping.yaml relative to this file
            config_path = Path(__file__).parent.parent.parent / 'config' / 'report_mapping.yaml'

        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load YAML configuration"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def get_category(self, category_id: int) -> Optional[Dict[str, Any]]:
        """
        Get category configuration by ID.

        Args:
            category_id: Category ID (1-11)

        Returns:
            Category configuration or None
        """
        for category in self.config.get('categories', []):
            if category.get('id') == category_id:
                return category
        return None

    def get_field_value(
        self,
        all_data: Dict[str, Any],
        field_config: Dict[str, Any]
    ) -> str:
        """
        Extract field value based on configuration.

        Args:
            all_data: Dictionary containing all data sources
            field_config: Field configuration from YAML

        Returns:
            Extracted and formatted value
        """
        # Handle static values
        if 'value' in field_config:
            return field_config['value']

        # Get source data
        source = field_config.get('source', 'property_details')
        path = field_config.get('path', '')
        fallback = field_config.get('fallback', self.config.get('settings', {}).get('missing_data_fallback', 'Unknown'))

        source_data = all_data.get(source, {})

        # Extract value
        value = get_nested_value(source_data, path, fallback)

        # Apply formatter if specified
        formatter_name = field_config.get('formatter')
        if formatter_name:
            value = self._apply_formatter(value, formatter_name)

        # Format missing values consistently
        value = format_missing_value(value, fallback)

        return value

    def _apply_formatter(self, value: Any, formatter_name: str) -> str:
        """
        Apply formatter to value.

        Args:
            value: Value to format
            formatter_name: Name of formatter (from config)

        Returns:
            Formatted value
        """
        formatters = self.config.get('formatters', {})
        formatter_config = formatters.get(formatter_name, {})

        formatter_type = formatter_config.get('type', 'text')

        if formatter_type == 'numeric':
            # Currency formatter
            if formatter_config.get('prefix') == '$':
                return format_currency(value)
            # Area formatter
            elif formatter_config.get('suffix') == ' m²':
                return format_area(value)
            # Percentage formatter
            elif formatter_config.get('suffix') == '%':
                return format_percentage(value)

        elif formatter_type == 'date':
            input_fmt = formatter_config.get('input_format', '%Y-%m-%d')
            output_fmt = formatter_config.get('output_format', '%d/%m/%Y')
            return format_date(value, input_fmt, output_fmt)

        return str(value)

    def extract_subsection(
        self,
        subsection_config: Dict[str, Any],
        all_data: Dict[str, Any]
    ) -> List[Tuple[str, str]]:
        """
        Extract all fields from a subsection.

        Args:
            subsection_config: Subsection configuration
            all_data: All data sources

        Returns:
            List of (label, value) tuples
        """
        rows = []

        # Add subsection header
        subsection_name = subsection_config.get('name', '')
        if subsection_name:
            rows.append((subsection_name, ""))

        # Extract fields
        for field in subsection_config.get('fields', []):
            label = field['label']
            value = self.get_field_value(all_data, field)
            rows.append((label, value))

        rows.append(("", ""))  # Spacer

        return rows

    def extract_category_simple_fields(
        self,
        category_id: int,
        all_data: Dict[str, Any]
    ) -> List[Tuple[str, str]]:
        """
        Extract simple (config-defined) fields from a category.
        Does NOT extract custom extractor fields.

        Args:
            category_id: Category ID (1-11)
            all_data: All data sources

        Returns:
            List of (label, value) tuples
        """
        rows = []

        category = self.get_category(category_id)
        if not category:
            return rows

        # Add category header
        rows.append((category['name'], ""))

        # Add coverage if specified
        if 'coverage' in category:
            rows.append(("Coverage", category['coverage']))
            rows.append(("", ""))

        # Extract subsections
        for subsection in category.get('subsections', []):
            # Skip subsections that are fully handled by custom extractors
            if 'custom_extractors' in subsection and not subsection.get('fields'):
                continue

            rows.extend(self.extract_subsection(subsection, all_data))

        return rows

    def get_custom_extractors(
        self,
        category_id: int,
        subsection_name: Optional[str] = None
    ) -> List[str]:
        """
        Get list of custom extractor names for a category or subsection.

        Args:
            category_id: Category ID
            subsection_name: Optional subsection name

        Returns:
            List of custom extractor names
        """
        category = self.get_category(category_id)
        if not category:
            return []

        extractors = []

        # Category-level custom extractors
        if 'custom_extractors' in category:
            extractors.extend([e['name'] for e in category['custom_extractors']])

        # Subsection-level custom extractors
        if subsection_name:
            for subsection in category.get('subsections', []):
                if subsection.get('name') == subsection_name:
                    if 'custom_extractors' in subsection:
                        extractors.extend([e['name'] for e in subsection['custom_extractors']])
        else:
            # Get all subsection custom extractors
            for subsection in category.get('subsections', []):
                if 'custom_extractors' in subsection:
                    extractors.extend([e['name'] for e in subsection['custom_extractors']])

        return extractors

    def get_settings(self) -> Dict[str, Any]:
        """Get global settings from config"""
        return self.config.get('settings', {})
