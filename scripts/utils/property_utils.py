#!/usr/bin/env python3
"""
Property Utilities

Reusable functions for property data operations including:
- Fetching property coordinates
- Fetching property addresses
- Property data transformations

Author: ARMATech Development Team
Date: 2025-11-11
"""

import requests
from typing import Tuple
from .corelogic_auth import CoreLogicAuth


def get_property_coordinates(property_id: int, auth: CoreLogicAuth) -> Tuple[float, float]:
    """
    Get coordinates for a property ID.

    Args:
        property_id: CoreLogic property ID
        auth: CoreLogicAuth instance

    Returns:
        Tuple of (latitude, longitude)

    Raises:
        ValueError: If coordinates cannot be retrieved
        requests.HTTPError: If API request fails
    """
    url = f"{auth.base_url}/property-details/au/properties/{property_id}"
    headers = {
        'Authorization': f'Bearer {auth.get_access_token()}',
        'accept': 'application/json'
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()
    location = data.get('location', {})

    lat = location.get('latitude')
    lon = location.get('longitude')

    if not lat or not lon:
        raise ValueError(f"Could not get coordinates for property {property_id}")

    return lat, lon


def get_property_address(property_id: int, auth: CoreLogicAuth) -> str:
    """
    Get property address for a property ID.

    Args:
        property_id: CoreLogic property ID
        auth: CoreLogicAuth instance

    Returns:
        Property address string

    Raises:
        requests.HTTPError: If API request fails
    """
    url = f"{auth.base_url}/property-details/au/properties/{property_id}"
    headers = {
        'Authorization': f'Bearer {auth.get_access_token()}',
        'accept': 'application/json'
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()
    location = data.get('location', {})
    return location.get('singleLine', 'Unknown Address')


def get_property_details(property_id: int, auth: CoreLogicAuth) -> dict:
    """
    Get complete property details including coordinates and address.

    Args:
        property_id: CoreLogic property ID
        auth: CoreLogicAuth instance

    Returns:
        Dict with property details including:
            - latitude: float
            - longitude: float
            - address: str
            - raw_data: dict (full API response)

    Raises:
        requests.HTTPError: If API request fails
    """
    url = f"{auth.base_url}/property-details/au/properties/{property_id}"
    headers = {
        'Authorization': f'Bearer {auth.get_access_token()}',
        'accept': 'application/json'
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()
    location = data.get('location', {})

    return {
        'latitude': location.get('latitude'),
        'longitude': location.get('longitude'),
        'address': location.get('singleLine', 'Unknown Address'),
        'raw_data': data
    }
