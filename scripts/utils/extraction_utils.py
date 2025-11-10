#!/usr/bin/env python3
"""
Data Extraction Utilities

Provides robust utilities for extracting and formatting data from nested dictionaries.
"""

from typing import Any, Optional, List
import textwrap


def get_nested_value(data: dict, path: str, fallback: Any = "Unknown") -> Any:
    """
    Get value from nested dictionary using dot notation.

    Args:
        data: Dictionary to extract from
        path: Dot-notation path (e.g., "site.zoneCodeLocal")
        fallback: Value to return if path not found

    Returns:
        Extracted value or fallback

    Examples:
        >>> data = {'site': {'zoneCodeLocal': 'NRZ5'}}
        >>> get_nested_value(data, 'site.zoneCodeLocal')
        'NRZ5'
        >>> get_nested_value(data, 'site.missing', 'N/A')
        'N/A'
    """
    if not data or not isinstance(data, dict):
        return fallback

    keys = path.split('.')
    current = data

    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
            if current is None:
                return fallback
        else:
            return fallback

    return current if current is not None else fallback


def format_missing_value(value: Any, fallback: str = "Unknown") -> str:
    """
    Consistently handle missing, None, or empty values.

    Args:
        value: Value to check
        fallback: Value to return if missing

    Returns:
        Formatted string value or fallback

    Examples:
        >>> format_missing_value(None)
        'Unknown'
        >>> format_missing_value('')
        'Unknown'
        >>> format_missing_value('NRZ5')
        'NRZ5'
        >>> format_missing_value(0)
        '0'
    """
    if value is None:
        return fallback

    # Handle empty strings
    if isinstance(value, str) and value.strip() == '':
        return fallback

    # Handle empty collections
    if isinstance(value, (list, dict, tuple)) and len(value) == 0:
        return fallback

    return str(value)


def truncate_text(text: str, max_length: int = 100, ellipsis: str = "...") -> str:
    """
    Truncate text to maximum length with ellipsis.

    Args:
        text: Text to truncate
        max_length: Maximum length (including ellipsis)
        ellipsis: String to append when truncated

    Returns:
        Truncated text with ellipsis if needed

    Examples:
        >>> truncate_text("Short text", 100)
        'Short text'
        >>> truncate_text("This is a very long text", 15)
        'This is a ve...'
    """
    if not text:
        return ""

    text = str(text).strip()

    if len(text) <= max_length:
        return text

    return text[:max_length - len(ellipsis)] + ellipsis


def wrap_text(text: str, max_width: int = 80, break_long_words: bool = True) -> List[str]:
    """
    Wrap text to multiple lines at word boundaries.

    Args:
        text: Text to wrap
        max_width: Maximum width per line
        break_long_words: Whether to break words longer than max_width

    Returns:
        List of wrapped lines

    Examples:
        >>> wrap_text("Short text", 80)
        ['Short text']
        >>> wrap_text("This is a long text that should wrap", 20)
        ['This is a long text', 'that should wrap']
    """
    if not text:
        return []

    text = str(text).strip()

    # Use textwrap for proper word boundary detection
    wrapper = textwrap.TextWrapper(
        width=max_width,
        break_long_words=break_long_words,
        break_on_hyphens=True
    )

    return wrapper.wrap(text)


def format_currency(value: Any, currency: str = "$", thousands_sep: str = ",") -> str:
    """
    Format numeric value as currency.

    Args:
        value: Numeric value
        currency: Currency symbol
        thousands_sep: Thousands separator

    Returns:
        Formatted currency string

    Examples:
        >>> format_currency(1500000)
        '$1,500,000'
        >>> format_currency(None)
        'Unknown'
    """
    try:
        num = float(value)
        return f"{currency}{num:,.0f}".replace(",", thousands_sep)
    except (ValueError, TypeError):
        return "Unknown"


def format_percentage(value: Any, decimal_places: int = 1) -> str:
    """
    Format numeric value as percentage.

    Args:
        value: Numeric value (0-100 or 0-1)
        decimal_places: Number of decimal places

    Returns:
        Formatted percentage string

    Examples:
        >>> format_percentage(75.5)
        '75.5%'
        >>> format_percentage(0.755)
        '75.5%'
    """
    try:
        num = float(value)

        # Auto-detect if value is 0-1 range or 0-100 range
        if 0 <= num <= 1:
            num = num * 100

        return f"{num:.{decimal_places}f}%"
    except (ValueError, TypeError):
        return "Unknown"


def format_area(value: Any, unit: str = "m²") -> str:
    """
    Format area with units.

    Args:
        value: Numeric area value
        unit: Unit of measurement

    Returns:
        Formatted area string

    Examples:
        >>> format_area(450)
        '450 m²'
        >>> format_area(None)
        'Unknown'
    """
    try:
        num = float(value)
        return f"{num:,.0f} {unit}"
    except (ValueError, TypeError):
        return "Unknown"


def format_date(value: Any, input_format: str = "%Y-%m-%d", output_format: str = "%d/%m/%Y") -> str:
    """
    Format date string to different format.

    Args:
        value: Date string or datetime object
        input_format: Input date format
        output_format: Output date format

    Returns:
        Formatted date string

    Examples:
        >>> format_date("2025-03-20")
        '20/03/2025'
    """
    from datetime import datetime

    if not value:
        return "Unknown"

    try:
        if isinstance(value, datetime):
            return value.strftime(output_format)

        dt = datetime.strptime(str(value), input_format)
        return dt.strftime(output_format)
    except (ValueError, TypeError):
        return str(value)


def safe_list_get(lst: List[Any], index: int, fallback: Any = None) -> Any:
    """
    Safely get item from list by index.

    Args:
        lst: List to get from
        index: Index to retrieve
        fallback: Value to return if index out of bounds

    Returns:
        List item or fallback

    Examples:
        >>> safe_list_get([1, 2, 3], 1)
        2
        >>> safe_list_get([1, 2, 3], 10, 'N/A')
        'N/A'
    """
    try:
        return lst[index]
    except (IndexError, TypeError):
        return fallback


def validate_type(value: Any, expected_type: type, fallback: Any = None) -> Any:
    """
    Validate that value is of expected type.

    Args:
        value: Value to validate
        expected_type: Expected type
        fallback: Value to return if type mismatch

    Returns:
        Value if correct type, otherwise fallback

    Examples:
        >>> validate_type("text", str)
        'text'
        >>> validate_type("text", int, 0)
        0
    """
    if isinstance(value, expected_type):
        return value
    return fallback


def extract_list_summary(lst: List[Any], max_items: int = 5,
                         show_total: bool = True) -> str:
    """
    Create summary of list contents.

    Args:
        lst: List to summarize
        max_items: Maximum items to show
        show_total: Whether to show total count

    Returns:
        Summary string

    Examples:
        >>> extract_list_summary(['a', 'b', 'c'], max_items=2)
        'a, b (+ 1 more)'
        >>> extract_list_summary([1, 2, 3])
        '1, 2, 3'
    """
    if not lst or not isinstance(lst, list):
        return "None"

    if len(lst) == 0:
        return "None"

    items_to_show = lst[:max_items]
    items_str = ", ".join(str(item) for item in items_to_show)

    if len(lst) > max_items:
        items_str += f" (+ {len(lst) - max_items} more)"
    elif show_total and len(lst) > 1:
        items_str += f" ({len(lst)} total)"

    return items_str
