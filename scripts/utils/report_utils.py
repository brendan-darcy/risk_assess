#!/usr/bin/env python3
"""
Report Generation Utilities

Reusable functions for generating property reports including:
- Radius search reports
- Comparable sales reports
- Statistical analysis
- Data aggregation

Author: ARMATech Development Team
Date: 2025-11-11
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


def calculate_price_statistics(properties: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate price statistics from property list.

    Args:
        properties: List of property dicts

    Returns:
        Dict with price statistics (median, mean, min, max, count)
    """
    prices = [p.get('salesLastSoldPrice') for p in properties if p.get('salesLastSoldPrice')]

    if not prices:
        return {}

    sorted_prices = sorted(prices)
    return {
        'median': int(sorted_prices[len(sorted_prices) // 2]),
        'mean': int(sum(prices) / len(prices)),
        'min': int(min(prices)),
        'max': int(max(prices)),
        'count': len(prices)
    }


def calculate_property_distributions(properties: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate property characteristic distributions.

    Args:
        properties: List of property dicts

    Returns:
        Dict with distributions for type, beds, baths, car spaces
    """
    property_types = {}
    beds_dist = {}
    baths_dist = {}
    car_spaces_dist = {}

    for prop in properties:
        # Property types
        prop_type = prop.get('type')
        if prop_type:
            property_types[prop_type] = property_types.get(prop_type, 0) + 1

        # Beds distribution
        beds = prop.get('beds')
        if beds:
            beds_dist[str(beds)] = beds_dist.get(str(beds), 0) + 1

        # Baths distribution
        baths = prop.get('baths')
        if baths:
            baths_dist[str(baths)] = baths_dist.get(str(baths), 0) + 1

        # Car spaces distribution
        car = prop.get('carSpaces')
        if car:
            car_spaces_dist[str(car)] = car_spaces_dist.get(str(car), 0) + 1

    return {
        'beds': {
            'distribution': beds_dist,
            'most_common': max(beds_dist, key=beds_dist.get) if beds_dist else None
        },
        'baths': {
            'distribution': baths_dist,
            'most_common': max(baths_dist, key=baths_dist.get) if baths_dist else None
        },
        'carSpaces': {
            'distribution': car_spaces_dist,
            'most_common': max(car_spaces_dist, key=car_spaces_dist.get) if car_spaces_dist else None
        },
        'propertyType': {
            'distribution': property_types,
            'most_common': max(property_types, key=property_types.get) if property_types else None
        }
    }


def calculate_distance_distribution(properties: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Calculate distance distribution from search center.

    Args:
        properties: List of property dicts with 'distance' field

    Returns:
        Dict with counts within various distance thresholds
    """
    return {
        'within_500m': sum(1 for p in properties if p.get('distance', float('inf')) <= 500),
        'within_1km': sum(1 for p in properties if p.get('distance', float('inf')) <= 1000),
        'within_3km': sum(1 for p in properties if p.get('distance', float('inf')) <= 3000),
        'within_5km': sum(1 for p in properties if p.get('distance', float('inf')) <= 5000)
    }


def calculate_date_range(properties: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate sale date range from property list.

    Args:
        properties: List of property dicts

    Returns:
        Dict with earliest, latest, and count of sales
    """
    sale_dates = [p.get('salesLastSaleContractDate') for p in properties
                  if p.get('salesLastSaleContractDate')]

    if not sale_dates:
        return {}

    return {
        'earliest': min(sale_dates),
        'latest': max(sale_dates),
        'count': len(sale_dates)
    }


def generate_radius_report(
    properties: List[Dict[str, Any]],
    center_lat: float,
    center_lon: float,
    radius_km: float,
    search_mode: str,
    property_id: Optional[int] = None,
    property_address: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate comprehensive radius search report from Rapid Search results.

    Args:
        properties: List of properties from Rapid Search
        center_lat: Search center latitude
        center_lon: Search center longitude
        radius_km: Search radius in kilometers
        search_mode: 'sales' or 'all'
        property_id: Optional property ID (for subject property)
        property_address: Optional property address

    Returns:
        Comprehensive radius search report dict with:
            - metadata: Search parameters and generation info
            - statistics: Price stats, distributions, date ranges
            - properties: Full property list
    """
    # Calculate all statistics
    price_stats = calculate_price_statistics(properties)
    property_chars = calculate_property_distributions(properties)
    distance_dist = calculate_distance_distribution(properties)
    date_range = calculate_date_range(properties)

    # Build report
    report = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'generator_version': '2.0-rapid-search',
            'search_type': 'rapid_search_radius',
            'search_mode': search_mode,
            'search_parameters': {
                'property_id': property_id,
                'property_address': property_address,
                'center_lat': center_lat,
                'center_lon': center_lon,
                'radius_km': radius_km
            },
            'total_properties': len(properties),
            'api_calls_used': 1  # ⭐ Single API call!
        },
        'statistics': {
            'total_count': len(properties),
            'price_statistics': price_stats,
            'property_characteristics': property_chars,
            'date_range': date_range,
            'distance_distribution': distance_dist
        },
        'properties': properties
    }

    return report


def generate_comparable_sales_report(
    properties: List[Dict[str, Any]],
    center_lat: float,
    center_lon: float,
    radius_km: float,
    property_id: Optional[int] = None,
    property_address: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate comparable sales report (wrapper for radius report in sales mode).

    Args:
        properties: List of properties from Rapid Search
        center_lat: Search center latitude
        center_lon: Search center longitude
        radius_km: Search radius
        property_id: Optional property ID (for subject property)
        property_address: Optional property address

    Returns:
        Comparable sales report dict
    """
    return generate_radius_report(
        properties=properties,
        center_lat=center_lat,
        center_lon=center_lon,
        radius_km=radius_km,
        search_mode='comparable_sales',
        property_id=property_id,
        property_address=property_address
    )
