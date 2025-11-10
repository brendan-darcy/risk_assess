#!/usr/bin/env python3
"""
CoreLogic Property Images API Client

Fetches property images and generates comprehensive metadata reports.
"""

import requests
from typing import Optional, Dict, Any, List
from datetime import datetime
from .corelogic_auth import CoreLogicAuth


class PropertyImagesClient(CoreLogicAuth):
    """Client for CoreLogic Property Images API"""

    def __init__(self, client_id: str, client_secret: str, base_url: str = "https://api-uat.corelogic.asia"):
        """
        Initialize the Property Images API client.

        Args:
            client_id: CoreLogic API client ID
            client_secret: CoreLogic API client secret
            base_url: The base URL for CoreLogic API (default: UAT)
        """
        super().__init__(client_id, client_secret, base_url)
        self.property_details_base_url = f"{self.base_url}/property-details/au"

    def get_property_images(self, property_id: int) -> Dict[str, Any]:
        """
        Fetch all images for a property.

        Args:
            property_id: CoreLogic property ID

        Returns:
            Dictionary containing all property images
        """
        url = f"{self.property_details_base_url}/properties/{property_id}/images"

        headers = {
            'Authorization': f'Bearer {self.get_access_token()}',
            'Content-Type': 'application/json'
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return {"error": "Property not found", "status_code": 404}
        else:
            return {"error": f"API error: {response.status_code}", "message": response.text, "status_code": response.status_code}

    def get_default_image(self, property_id: int) -> Dict[str, Any]:
        """
        Fetch only the default image for a property.

        Args:
            property_id: CoreLogic property ID

        Returns:
            Dictionary containing default property image
        """
        url = f"{self.property_details_base_url}/properties/{property_id}/images/default"

        headers = {
            'Authorization': f'Bearer {self.get_access_token()}',
            'Content-Type': 'application/json'
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return {"error": "Property not found or no default image", "status_code": 404}
        else:
            return {"error": f"API error: {response.status_code}", "message": response.text, "status_code": response.status_code}

    def generate_images_report(self, property_id: int, property_address: str = None) -> Dict[str, Any]:
        """
        Generate comprehensive images report with metadata and summary statistics.

        Args:
            property_id: CoreLogic property ID
            property_address: Optional property address for metadata

        Returns:
            Comprehensive report dictionary
        """
        # Fetch all images
        images_data = self.get_property_images(property_id)

        # Handle errors
        if "error" in images_data:
            return {
                "property_id": property_id,
                "property_address": property_address,
                "extraction_timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": images_data.get("error"),
                "message": images_data.get("message"),
                "summary": {
                    "total_images": 0,
                    "has_default_image": False,
                    "secondary_images_count": 0,
                    "floor_plan_images_count": 0
                }
            }

        # Extract data
        default_image = images_data.get('defaultImage', {})
        secondary_images = images_data.get('secondaryImageList', [])
        floor_plan_images = images_data.get('floorPlanImageList', [])

        # Generate summary statistics
        summary = {
            "total_images": 1 + len(secondary_images) + len(floor_plan_images) if default_image else len(secondary_images) + len(floor_plan_images),
            "has_default_image": bool(default_image),
            "secondary_images_count": len(secondary_images),
            "floor_plan_images_count": len(floor_plan_images),
            "image_types": []
        }

        if default_image:
            summary["image_types"].append("default")
        if secondary_images:
            summary["image_types"].append("secondary")
        if floor_plan_images:
            summary["image_types"].append("floor_plans")

        # Available sizes analysis
        available_sizes = set()
        if default_image:
            if default_image.get('basePhotoUrl'):
                available_sizes.add('original')
            if default_image.get('largePhotoUrl'):
                available_sizes.add('large_768x512')
            if default_image.get('mediumPhotoUrl'):
                available_sizes.add('medium_470x313')
            if default_image.get('thumbnailPhotoUrl'):
                available_sizes.add('thumbnail_320x215')

        summary["available_sizes"] = sorted(list(available_sizes))

        # Scan date analysis - Enhanced with distribution stats
        scan_dates = []
        images_by_date = {}  # {date: {'default': 0, 'secondary': 0, 'floor_plan': 0}}
        images_by_type_and_date = {'default': [], 'secondary': [], 'floor_plan': []}
        # Track digital_asset_type by year
        asset_type_by_year = {}  # {year: {asset_type: count}}
        all_images_with_metadata = []  # Store all images with their metadata

        # Collect default image date
        if default_image and default_image.get('scanDate'):
            date = default_image.get('scanDate')
            asset_type = default_image.get('digitalAssetType', 'Unknown')
            scan_dates.append(date)
            images_by_type_and_date['default'].append(date)
            all_images_with_metadata.append({'date': date, 'asset_type': asset_type, 'category': 'default'})

            if date not in images_by_date:
                images_by_date[date] = {'default': 0, 'secondary': 0, 'floor_plan': 0, 'total': 0}
            images_by_date[date]['default'] += 1
            images_by_date[date]['total'] += 1

        # Collect secondary images dates
        for img in secondary_images:
            if img.get('scanDate'):
                date = img.get('scanDate')
                asset_type = img.get('digitalAssetType', 'Unknown')
                scan_dates.append(date)
                images_by_type_and_date['secondary'].append(date)
                all_images_with_metadata.append({'date': date, 'asset_type': asset_type, 'category': 'secondary'})

                if date not in images_by_date:
                    images_by_date[date] = {'default': 0, 'secondary': 0, 'floor_plan': 0, 'total': 0}
                images_by_date[date]['secondary'] += 1
                images_by_date[date]['total'] += 1

        # Collect floor plan images dates
        for img in floor_plan_images:
            if img.get('scanDate'):
                date = img.get('scanDate')
                asset_type = img.get('digitalAssetType', 'Unknown')
                scan_dates.append(date)
                images_by_type_and_date['floor_plan'].append(date)
                all_images_with_metadata.append({'date': date, 'asset_type': asset_type, 'category': 'floor_plan'})

                if date not in images_by_date:
                    images_by_date[date] = {'default': 0, 'secondary': 0, 'floor_plan': 0, 'total': 0}
                images_by_date[date]['floor_plan'] += 1
                images_by_date[date]['total'] += 1

        if scan_dates:
            scan_dates_sorted = sorted(scan_dates)
            summary["oldest_scan_date"] = scan_dates_sorted[0]
            summary["newest_scan_date"] = scan_dates_sorted[-1]
            summary["unique_scan_dates"] = len(set(scan_dates))

            # Calculate temporal span
            try:
                from datetime import datetime as dt
                oldest = dt.fromisoformat(scan_dates_sorted[0])
                newest = dt.fromisoformat(scan_dates_sorted[-1])
                span_days = (newest - oldest).days
                span_years = round(span_days / 365.25, 1)
                summary["temporal_span_days"] = span_days
                summary["temporal_span_years"] = span_years
            except:
                pass

            # Images by date distribution (sorted by date)
            images_by_date_sorted = {k: images_by_date[k] for k in sorted(images_by_date.keys())}
            summary["images_by_date"] = images_by_date_sorted

            # Year-based distribution
            year_distribution = {}
            for date in scan_dates:
                try:
                    year = date.split('-')[0]
                    year_distribution[year] = year_distribution.get(year, 0) + 1
                except:
                    pass
            summary["images_by_year"] = dict(sorted(year_distribution.items()))

            # Digital asset type by year distribution
            for img_metadata in all_images_with_metadata:
                try:
                    year = img_metadata['date'].split('-')[0]
                    asset_type = img_metadata['asset_type']

                    if year not in asset_type_by_year:
                        asset_type_by_year[year] = {}
                    if asset_type not in asset_type_by_year[year]:
                        asset_type_by_year[year][asset_type] = 0
                    asset_type_by_year[year][asset_type] += 1
                except:
                    pass

            summary["digital_asset_type_by_year"] = dict(sorted(asset_type_by_year.items()))

            # Overall digital_asset_type distribution
            asset_type_totals = {}
            for img_metadata in all_images_with_metadata:
                asset_type = img_metadata['asset_type']
                asset_type_totals[asset_type] = asset_type_totals.get(asset_type, 0) + 1
            summary["digital_asset_type_totals"] = dict(sorted(asset_type_totals.items()))

            # Type distribution statistics
            type_stats = {
                'default': {
                    'count': len(images_by_type_and_date['default']),
                    'unique_dates': len(set(images_by_type_and_date['default'])),
                    'oldest_date': min(images_by_type_and_date['default']) if images_by_type_and_date['default'] else None,
                    'newest_date': max(images_by_type_and_date['default']) if images_by_type_and_date['default'] else None
                },
                'secondary': {
                    'count': len(images_by_type_and_date['secondary']),
                    'unique_dates': len(set(images_by_type_and_date['secondary'])),
                    'oldest_date': min(images_by_type_and_date['secondary']) if images_by_type_and_date['secondary'] else None,
                    'newest_date': max(images_by_type_and_date['secondary']) if images_by_type_and_date['secondary'] else None
                },
                'floor_plan': {
                    'count': len(images_by_type_and_date['floor_plan']),
                    'unique_dates': len(set(images_by_type_and_date['floor_plan'])),
                    'oldest_date': min(images_by_type_and_date['floor_plan']) if images_by_type_and_date['floor_plan'] else None,
                    'newest_date': max(images_by_type_and_date['floor_plan']) if images_by_type_and_date['floor_plan'] else None
                }
            }
            summary["distribution_by_type"] = type_stats

        # Build detailed report
        report = {
            "metadata": {
                "property_id": property_id,
                "property_address": property_address,
                "extraction_timestamp": datetime.now().isoformat(),
                "api_endpoint": f"/property-details/au/properties/{property_id}/images",
                "status": "success"
            },
            "summary": summary,
            "default_image": self._format_image_details(default_image) if default_image else None,
            "secondary_images": [self._format_image_details(img) for img in secondary_images],
            "floor_plan_images": [self._format_image_details(img) for img in floor_plan_images],
            "raw_response": images_data  # Include raw response for reference
        }

        return report

    def _format_image_details(self, image: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format image details into structured metadata.

        Args:
            image: Raw image dictionary

        Returns:
            Formatted image details
        """
        if not image:
            return {}

        details = {
            "digital_asset_type": image.get('digitalAssetType'),
            "scan_date": image.get('scanDate'),
            "urls": {}
        }

        # Add all available URLs
        if image.get('basePhotoUrl'):
            details["urls"]["original"] = {
                "url": image.get('basePhotoUrl'),
                "size": "0x0 (original)"
            }
        if image.get('largePhotoUrl'):
            details["urls"]["large"] = {
                "url": image.get('largePhotoUrl'),
                "size": "768x512"
            }
        if image.get('mediumPhotoUrl'):
            details["urls"]["medium"] = {
                "url": image.get('mediumPhotoUrl'),
                "size": "470x313"
            }
        if image.get('thumbnailPhotoUrl'):
            details["urls"]["thumbnail"] = {
                "url": image.get('thumbnailPhotoUrl'),
                "size": "320x215"
            }

        # Add any additional fields from the response
        for key, value in image.items():
            if key not in ['digitalAssetType', 'scanDate', 'basePhotoUrl', 'largePhotoUrl', 'mediumPhotoUrl', 'thumbnailPhotoUrl']:
                details[key] = value

        return details
