#!/usr/bin/env python3
"""
Generate Property Data PDF Report

Creates a professional PDF report from comprehensive property data in a two-column table format.
For single data points: shows value and units
For complex data: shows metadata summaries (e.g., sales history: # sales, date range)

Usage:
    # From comprehensive report JSON
    python3 scripts/generate_property_pdf.py --input data/property_reports/13683380_comprehensive_report.json

    # Or generate from address directly
    python3 scripts/generate_property_pdf.py --address "5 Settlers Court, Vermont South VIC 3133"

    # Custom output
    python3 scripts/generate_property_pdf.py --input report.json --output custom_report.pdf

    # Generate ultra-comprehensive PDF with ALL fields + geospatial metadata
    python3 scripts/generate_property_pdf.py \
    --input data/property_reports/13683380_comprehensive_report.json \
    --ultra-comprehensive


Requirements:
    pip install reportlab

Author: Property Report Generator
Date: 2025-11-09
"""

import argparse
import json
import sys
import csv
import statistics
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional

# Import DataProcessor for flatten utility
try:
    from utils.pipeline_utils import DataProcessor
    DATAPROCESSOR_AVAILABLE = True
except ImportError:
    DATAPROCESSOR_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️  Warning: reportlab not installed. Install with: pip install reportlab", file=sys.stderr)


class PropertyDataPDFGenerator:
    """Generate PDF reports from comprehensive property data"""

    def __init__(self):
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab is required. Install with: pip install reportlab")

        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=11,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=6,
            alignment=TA_CENTER
        )
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=8,
            textColor=colors.HexColor('#333333'),
            spaceAfter=2,
            spaceBefore=4
        )
        self.normal_style = ParagraphStyle(
            'CompactNormal',
            parent=self.styles['Normal'],
            fontSize=7,
            leading=8
        )
        self.label_style = ParagraphStyle(
            'CompactLabel',
            parent=self.styles['Normal'],
            fontSize=7,
            leading=8,
            fontName='Helvetica-Bold'
        )

    def extract_data_flattened(self, report: Dict[str, Any]) -> List[Tuple[str, str]]:
        """
        Extract ALL fields using flatten_json_recursive for ultra-comprehensive reports.
        Returns list of (label, value) tuples.
        """
        if not DATAPROCESSOR_AVAILABLE:
            return self.extract_data_summary(report)  # Fallback

        data_rows = []

        # Process property_details section with flattening
        property_details = report.get('property_details', {})

        for endpoint_name, endpoint_data in property_details.items():
            if isinstance(endpoint_data, dict) and not endpoint_data.get('error'):
                # Add section header
                data_rows.append((endpoint_name.upper().replace('_', ' '), ""))

                # Flatten the endpoint data
                flattened = DataProcessor.flatten_json_recursive(endpoint_data, sep='.')

                # Add each field
                for key, value in sorted(flattened.items()):
                    # Skip error fields and metadata
                    if key in ['error', 'isActiveProperty', 'systemInfo']:
                        continue

                    # Format the label nicely
                    label = key.replace('.', ' > ').replace('_', ' ').title()

                    # Format the value appropriately
                    if isinstance(value, bool):
                        value_str = "Yes" if value else "No"
                    elif isinstance(value, (int, float)):
                        # Try to detect currency or measurements
                        if 'price' in key.lower() or 'value' in key.lower() or 'amount' in key.lower():
                            value_str = self._format_currency(value)
                        elif 'area' in key.lower() and not 'code' in key.lower():
                            value_str = self._format_area(value)
                        else:
                            value_str = str(value)
                    else:
                        value_str = str(value) if value else 'N/A'

                    data_rows.append((label, value_str))

                data_rows.append(("", ""))  # Spacer

        # ======= GEOSPATIAL DATA SECTIONS (same as standard mode) =======

        # Parcel Geometry Details
        parcel_geom = report.get('parcel_geometry', {})
        if parcel_geom.get('success'):
            data_rows.append(("PARCEL GEOMETRY DETAILS", ""))

            parcel_data = parcel_geom.get('data', {})

            # Geometry Type
            if 'geometryType' in parcel_data:
                data_rows.append(("Geometry Type", parcel_data.get('geometryType', 'N/A')))

            # Spatial Reference
            spatial_ref = parcel_data.get('spatialReference', {})
            if spatial_ref:
                if 'wkid' in spatial_ref:
                    data_rows.append(("Spatial Reference WKID", str(spatial_ref.get('wkid', 'N/A'))))
                if 'latestWkid' in spatial_ref:
                    data_rows.append(("Latest WKID", str(spatial_ref.get('latestWkid', 'N/A'))))

            # Feature attributes
            features = parcel_data.get('features', [])
            if features:
                attrs = features[0].get('attributes', {})
                if 'property_m2' in attrs:
                    data_rows.append(("Property Area (m²)", f"{attrs.get('property_m2', 0):.2f} m²"))
                if 'st_area(geom)' in attrs:
                    data_rows.append(("Geometry Area", f"{attrs.get('st_area(geom)', 0):.2f} m²"))
                if 'st_perimeter(geom)' in attrs:
                    data_rows.append(("Geometry Perimeter", f"{attrs.get('st_perimeter(geom)', 0):.2f} m"))

                # Polygon details
                geometry = features[0].get('geometry', {})
                rings = geometry.get('rings', [])
                if rings:
                    data_rows.append(("Polygon Rings", f"{len(rings)} ring(s)"))
                    total_vertices = sum(len(ring) for ring in rings)
                    data_rows.append(("Total Vertices", f"{total_vertices} points"))

            data_rows.append(("", ""))

        # Geospatial Layers Summary
        geo_layers = report.get('geospatial_layers', {})
        if geo_layers:
            data_rows.append(("GEOSPATIAL LAYERS SUMMARY", ""))

            # Hazards
            hazards = geo_layers.get('hazards', {})
            if hazards:
                hazard_count = sum(1 for h in hazards.values() if h.get('available'))
                data_rows.append(("Hazard Layers Available", f"{hazard_count} layers"))

                for hazard_name, hazard_data in hazards.items():
                    if hazard_data.get('available'):
                        method = hazard_data.get('method', 'N/A')
                        feature_count = hazard_data.get('feature_count', 0)
                        label = f"  {hazard_name.title()}"
                        if feature_count > 0:
                            data_rows.append((label, f"{feature_count} features ({method})"))
                        else:
                            data_rows.append((label, f"Available ({method})"))

            # Legal layers (easements)
            legal = geo_layers.get('legal', {})
            if legal:
                easements = legal.get('easements', {})
                if easements.get('available'):
                    count = easements.get('count', 0)
                    data_rows.append(("Easements", f"{count} easements found"))
                    if count > 0 and 'features' in easements:
                        # Show summary of first few easements
                        features = easements.get('features', [])[:3]  # First 3
                        for i, feat in enumerate(features, 1):
                            attrs = feat.get('attributes', {})
                            area = attrs.get('easement_area_sqm', 0)
                            locality = attrs.get('locality_name', 'N/A')
                            data_rows.append((f"  Easement {i}", f"{area:.0f} m² in {locality}"))

            # Infrastructure
            infrastructure = geo_layers.get('infrastructure', {})
            if infrastructure:
                infra_count = sum(1 for i in infrastructure.values() if i.get('available'))
                data_rows.append(("Infrastructure Layers", f"{infra_count} layers"))

                for infra_name, infra_data in infrastructure.items():
                    if infra_data.get('available'):
                        method = infra_data.get('method', 'N/A')
                        feature_count = infra_data.get('feature_count', 0)
                        label = f"  {infra_name.replace('_', ' ').title()}"
                        if feature_count > 0:
                            data_rows.append((label, f"{feature_count} features"))
                        else:
                            data_rows.append((label, "Available"))

            data_rows.append(("", ""))

        # Market Data (if available)
        market_data = report.get('market_data', {})
        if market_data and isinstance(market_data, dict):
            data_rows.append(("MARKET DATA", ""))

            # Check for market trends
            if 'trends' in market_data:
                trends = market_data['trends']
                data_rows.append(("Market Trends Available", "Yes"))
                if isinstance(trends, dict) and 'period' in trends:
                    data_rows.append(("Period", str(trends.get('period', 'N/A'))))

            # Check for market statistics
            if 'statistics' in market_data:
                stats = market_data['statistics']
                if isinstance(stats, dict):
                    for key, value in stats.items():
                        if isinstance(value, (int, float)):
                            data_rows.append((key.replace('_', ' ').title(), str(value)))

            data_rows.append(("", ""))

        # Comparables (if available)
        comparables = report.get('comparables', {})
        if comparables and isinstance(comparables, (dict, list)):
            data_rows.append(("COMPARABLE PROPERTIES", ""))

            if isinstance(comparables, dict):
                comp_list = comparables.get('properties', comparables.get('sales', []))
            else:
                comp_list = comparables

            if comp_list:
                data_rows.append(("Total Comparables", f"{len(comp_list)} properties"))

                # Show summary of first few comparables
                for i, comp in enumerate(comp_list[:5], 1):  # First 5
                    if isinstance(comp, dict):
                        address = comp.get('address', comp.get('singleLine', 'N/A'))
                        price = comp.get('price', comp.get('salePrice', 0))
                        if price:
                            data_rows.append((f"Comp {i}", f"{address[:40]}... - {self._format_currency(price)}"))
                        else:
                            data_rows.append((f"Comp {i}", address[:50]))

            data_rows.append(("", ""))

        # Mesh Block Analysis (if available)
        mesh_summary = self._load_mesh_block_summary()
        if mesh_summary:
            data_rows.append(("MESH BLOCK ANALYSIS", ""))
            data_rows.append(("Analysis Buffer", f"{mesh_summary['buffer_meters']} meters"))
            data_rows.append(("Total Mesh Blocks", f"{mesh_summary['total_blocks']} blocks"))

            # Category breakdown
            categories = mesh_summary.get('categories', {})
            if categories:
                data_rows.append(("", ""))
                data_rows.append(("Category Breakdown", ""))
                for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                    data_rows.append((f"  {category}", f"{count} blocks"))

            # Non-residential statistics
            nonres_stats = mesh_summary.get('nonresidential_stats')
            if nonres_stats:
                data_rows.append(("", ""))
                data_rows.append(("Non-Residential Distances", ""))
                data_rows.append(("  Total Non-Residential", f"{nonres_stats['count']} blocks"))
                data_rows.append(("  Closest", f"{nonres_stats['min_m']:.1f} m"))
                data_rows.append(("  Farthest", f"{nonres_stats['max_m']:.1f} m"))
                data_rows.append(("  Average", f"{nonres_stats['mean_m']:.1f} m"))
                data_rows.append(("  Median", f"{nonres_stats['median_m']:.1f} m"))

            # Top 5 closest non-residential blocks
            top_blocks = mesh_summary.get('top_nonresidential', [])
            if top_blocks:
                data_rows.append(("", ""))
                data_rows.append(("Top 5 Closest Non-Residential", ""))
                for i, block in enumerate(top_blocks, 1):
                    category = block['category']
                    distance = block['distance_m']
                    suburb = block['suburb']
                    data_rows.append((f"  #{i} {category}", f"{distance:.1f} m ({suburb})"))

            data_rows.append(("", ""))

        # Market Metrics Summary (if available)
        market_metrics = report.get('market_metrics_summary')
        if market_metrics and not market_metrics.get('error'):
            availability = market_metrics.get('availability', {})
            featured = market_metrics.get('featured_metrics', {})
            summary = market_metrics.get('summary', {})

            data_rows.append(("MARKET METRICS AVAILABILITY", ""))

            # Summary stats
            if summary:
                available = summary.get('available_metrics', 0)
                total = summary.get('total_metrics', 0)
                data_rows.append(("Metrics Available", f"{available}/{total} metrics"))
                data_rows.append(("", ""))

            # Show availability for each metric
            for metric_name, metric_info in availability.items():
                description = metric_info.get('description', metric_name.replace('_', ' ').title())

                if metric_info.get('available'):
                    data_points = metric_info.get('data_points', 0)
                    date_range = metric_info.get('date_range', 'N/A')
                    interval = metric_info.get('interval', 'N/A')

                    data_rows.append((f"✓ {description}", ""))
                    data_rows.append((f"  Data Points", f"{data_points} ({interval})"))
                    data_rows.append((f"  Date Range", date_range))

                    # Show trend if available
                    if 'growth_percent' in metric_info:
                        growth = metric_info['growth_percent']
                        first_val = metric_info.get('first_value', 0)
                        last_val = metric_info.get('last_value', 0)

                        # Format values based on metric type
                        if 'price' in metric_name or 'value' in metric_name or 'rent' in metric_name:
                            data_rows.append((f"  First Value", self._format_currency(first_val)))
                            data_rows.append((f"  Latest Value", self._format_currency(last_val)))
                        else:
                            data_rows.append((f"  First Value", f"{first_val:,.0f}"))
                            data_rows.append((f"  Latest Value", f"{last_val:,.0f}"))

                        data_rows.append((f"  Growth", f"{growth:+.1f}%"))
                    elif 'latest_value' in metric_info:
                        # For percentage metrics like rental_yield
                        latest = metric_info['latest_value']
                        if isinstance(latest, (int, float)):
                            data_rows.append((f"  Latest Value", f"{latest:.2f}%"))
                else:
                    reason = metric_info.get('reason', 'No data available')
                    data_rows.append((f"✗ {description}", reason))

                data_rows.append(("", ""))

            # Featured metrics section
            if featured:
                # Median Value (AVM) Trend
                if 'median_value' in featured:
                    mv = featured['median_value']
                    data_rows.append(("MEDIAN VALUE (AVM) TREND", ""))
                    data_rows.append(("Description", mv.get('description', 'N/A')))
                    data_rows.append(("Period", f"{mv.get('first_date', 'N/A')} to {mv.get('last_date', 'N/A')}"))
                    data_rows.append(("Data Points", f"{mv.get('data_points', 0)} ({mv.get('interval', 'N/A')})"))
                    data_rows.append(("Starting Value", self._format_currency(mv.get('first_value', 0))))
                    data_rows.append(("Current Value", self._format_currency(mv.get('last_value', 0))))
                    data_rows.append(("Growth", f"{mv.get('growth_percent', 0):+.1f}%"))
                    data_rows.append(("", ""))

                # Median Sale Price Trend
                if 'median_sale_price' in featured:
                    msp = featured['median_sale_price']
                    data_rows.append(("MEDIAN SALE PRICE TREND", ""))
                    data_rows.append(("Description", msp.get('description', 'N/A')))
                    data_rows.append(("Period", f"{msp.get('first_date', 'N/A')} to {msp.get('last_date', 'N/A')}"))
                    data_rows.append(("Data Points", f"{msp.get('data_points', 0)} ({msp.get('interval', 'N/A')})"))
                    data_rows.append(("Starting Price", self._format_currency(msp.get('first_value', 0))))
                    data_rows.append(("Current Price", self._format_currency(msp.get('last_value', 0))))
                    data_rows.append(("Growth", f"{msp.get('growth_percent', 0):+.1f}%"))
                    data_rows.append(("", ""))

                # Rental Market
                if 'rental_market' in featured:
                    rm = featured['rental_market']
                    data_rows.append(("RENTAL MARKET", ""))
                    if 'rental_yield' in rm:
                        data_rows.append(("Rental Yield", f"{rm['rental_yield']:.2f}%"))
                        if 'rental_yield_date' in rm:
                            data_rows.append(("Yield Date", rm['rental_yield_date']))
                    if 'median_rent' in rm:
                        data_rows.append(("Median Rent", f"{self._format_currency(rm['median_rent'])}/week"))
                        if 'median_rent_date' in rm:
                            data_rows.append(("Rent Date", rm['median_rent_date']))
                    data_rows.append(("", ""))

        return data_rows

    def extract_data_summary(self, report: Dict[str, Any]) -> List[Tuple[str, str]]:
        """
        Extract key data points and create two-column summaries.
        Returns list of (label, value) tuples.
        """
        data_rows = []

        # Metadata section
        metadata = report.get('metadata', {})
        data_rows.extend([
            ("PROPERTY IDENTIFICATION", ""),
            ("Address", metadata.get('address', 'N/A')),
            ("Property ID", str(metadata.get('property_id', 'N/A'))),
            ("State", metadata.get('state', 'N/A')),
            ("Report Date", metadata.get('extraction_timestamp', '')[:10]),
            ("", ""),
        ])

        # Location details
        property_details = report.get('property_details', {})
        location = property_details.get('location', {})

        if location and not location.get('error'):
            data_rows.append(("LOCATION", ""))

            if 'councilArea' in location:
                data_rows.append(("Council Area", location.get('councilArea', 'N/A')))

            # Postcode
            postcode_info = location.get('postcode', {})
            if postcode_info and 'name' in postcode_info:
                data_rows.append(("Postcode", postcode_info.get('name', 'N/A')))

            # Locality
            locality_info = location.get('locality', {})
            if locality_info and 'name' in locality_info:
                data_rows.append(("Locality", locality_info.get('name', 'N/A')))

            # Coordinates
            if 'longitude' in location and 'latitude' in location:
                coords = f"{location.get('latitude', 0):.6f}, {location.get('longitude', 0):.6f}"
                data_rows.append(("Coordinates", coords))

            data_rows.append(("", ""))

        # Site details
        site = property_details.get('site', {})
        legal = property_details.get('legal', {})

        # Combine site and legal info for site details section
        has_site_info = False
        site_rows = [("SITE DETAILS", "")]

        if site and not site.get('error'):
            # Zoning
            if 'zoneCodeLocal' in site:
                site_rows.append(("Zone Code", site.get('zoneCodeLocal', 'N/A')))
                has_site_info = True
            if 'zoneDescriptionLocal' in site:
                site_rows.append(("Zone Description", site.get('zoneDescriptionLocal', 'N/A')))
                has_site_info = True

            # Site valuation
            site_values = site.get('siteValueList', [])
            if site_values:
                latest_val = site_values[0]  # Most recent
                if 'value' in latest_val:
                    site_rows.append(("Site Value", self._format_currency(latest_val.get('value'))))
                    has_site_info = True
                if 'date' in latest_val:
                    site_rows.append(("Valuation Date", latest_val.get('date', 'N/A')))
                    has_site_info = True

        # Get dimensions from legal
        if legal and not legal.get('error'):
            legal_info = legal.get('legal', {})
            if legal_info:
                if 'frontage' in legal_info and legal_info.get('frontage'):
                    site_rows.append(("Frontage", self._format_measurement(legal_info.get('frontage'), 'm')))
                    has_site_info = True
                if 'vgMeasurement' in legal_info:
                    site_rows.append(("Dimensions", legal_info.get('vgMeasurement', 'N/A')))
                    has_site_info = True

        if has_site_info:
            site_rows.append(("", ""))
            data_rows.extend(site_rows)

        # Core attributes - show ALL fields
        core_attrs = property_details.get('core_attributes', {})
        if core_attrs and not core_attrs.get('error'):
            data_rows.append(("PROPERTY ATTRIBUTES", ""))

            # Property Type
            if 'propertyType' in core_attrs:
                data_rows.append(("Property Type", str(core_attrs.get('propertyType', 'N/A'))))
            if 'propertySubType' in core_attrs:
                data_rows.append(("Property Sub Type", str(core_attrs.get('propertySubType', 'N/A'))))

            # Bedrooms/Bathrooms/Parking
            if 'beds' in core_attrs:
                data_rows.append(("Bedrooms", str(core_attrs.get('beds', 'N/A'))))
            if 'baths' in core_attrs:
                data_rows.append(("Bathrooms", str(core_attrs.get('baths', 'N/A'))))
            if 'carSpaces' in core_attrs:
                data_rows.append(("Car Spaces", str(core_attrs.get('carSpaces', 'N/A'))))
            if 'lockUpGarages' in core_attrs:
                data_rows.append(("Lock-Up Garages", str(core_attrs.get('lockUpGarages', 'N/A'))))

            # Land Area
            if 'landArea' in core_attrs:
                data_rows.append(("Land Area", self._format_area(core_attrs.get('landArea'))))
            if 'isCalculatedLandArea' in core_attrs:
                is_calc = core_attrs.get('isCalculatedLandArea')
                data_rows.append(("Calculated Land Area", "Yes" if is_calc else "No"))
            if 'landAreaSource' in core_attrs:
                data_rows.append(("Land Area Source", str(core_attrs.get('landAreaSource', 'N/A'))))

            data_rows.append(("", ""))

        # Additional attributes
        additional_attrs = property_details.get('additional_attributes', {})
        if additional_attrs and not additional_attrs.get('error'):
            has_attrs = False
            attr_rows = [("ADDITIONAL ATTRIBUTES", "")]

            if 'floorArea' in additional_attrs and additional_attrs.get('floorArea'):
                attr_rows.append(("Floor Area", self._format_area(additional_attrs.get('floorArea'))))
                has_attrs = True
            if 'pool' in additional_attrs:
                attr_rows.append(("Pool", "Yes" if additional_attrs.get('pool') else "No"))
                has_attrs = True

            if has_attrs:
                attr_rows.append(("", ""))
                data_rows.extend(attr_rows)

        # Features
        features = property_details.get('features', {})
        if features and not features.get('error'):
            # Check for featureAttributes array
            feature_attrs = features.get('featureAttributes', [])
            if feature_attrs:
                data_rows.append(("FEATURES", ""))
                for feat in feature_attrs:
                    feat_name = feat.get('name', 'Unknown')
                    feat_value = feat.get('value', 'N/A')
                    data_rows.append((feat_name, str(feat_value)))
                data_rows.append(("", ""))
            else:
                # Fallback to boolean features
                feature_list = []
                if features.get('pool'): feature_list.append('Pool')
                if features.get('airConditioning'): feature_list.append('Air Conditioning')
                if features.get('alarm'): feature_list.append('Alarm')
                if features.get('balcony'): feature_list.append('Balcony')
                if features.get('deck'): feature_list.append('Deck')
                if features.get('garage'): feature_list.append('Garage')

                if feature_list:
                    data_rows.extend([
                        ("FEATURES", ""),
                        ("Available Features", ", ".join(feature_list)),
                        ("", ""),
                    ])

        # Last sale
        last_sale = property_details.get('last_sale', {})
        if last_sale and not last_sale.get('error'):
            sale_info = last_sale.get('lastSale', {})
            if sale_info:
                data_rows.append(("LAST SALE", ""))

                # Sale price and dates
                if 'price' in sale_info:
                    data_rows.append(("Sale Price", self._format_currency(sale_info.get('price'))))
                if 'contractDate' in sale_info:
                    data_rows.append(("Contract Date", sale_info.get('contractDate', 'N/A')))
                if 'settlementDate' in sale_info:
                    data_rows.append(("Settlement Date", sale_info.get('settlementDate', 'N/A')))

                # Sale details
                if 'saleMethod' in sale_info:
                    data_rows.append(("Sale Method", sale_info.get('saleMethod', 'N/A')))
                if 'type' in sale_info:
                    data_rows.append(("Sale Type", sale_info.get('type', 'N/A')))

                # Agency details
                if 'agencyName' in sale_info:
                    data_rows.append(("Agency", sale_info.get('agencyName', 'N/A')))
                if 'agentName' in sale_info:
                    data_rows.append(("Agent", sale_info.get('agentName', 'N/A')))

                data_rows.append(("", ""))

        # Sales history summary
        sales_history = property_details.get('sales_history', {})
        if sales_history and not sales_history.get('error'):
            sale_list = sales_history.get('saleList', [])
            if sale_list:
                # Extract dates and prices
                sales_dates = []
                sales_prices = []
                for sale in sale_list:
                    if sale.get('contractDate'):
                        sales_dates.append(sale['contractDate'])
                    if sale.get('price') and sale.get('price') > 0:
                        sales_prices.append(sale['price'])

                if sales_dates:
                    sales_dates.sort()
                    data_rows.append(("SALES HISTORY", ""))
                    data_rows.append(("Total Sales", f"{len(sale_list)} sales"))
                    data_rows.append(("Date Range", f"{sales_dates[0]} to {sales_dates[-1]}"))

                    # Show total value if we have valid prices
                    if sales_prices:
                        total_value = sum(sales_prices)
                        data_rows.append(("Total Transaction Value", self._format_currency(total_value)))
                        avg_value = total_value / len(sales_prices)
                        data_rows.append(("Average Sale Price", self._format_currency(avg_value)))

                    data_rows.append(("", ""))

        # Last advertising campaign
        sales_otm = property_details.get('sales_otm', {})
        advertisements = property_details.get('advertisements', {})

        # Try to get campaign from sales_otm first
        campaign_info = None
        if sales_otm and not sales_otm.get('error'):
            for_sale_campaign = sales_otm.get('forSalePropertyCampaign', {})
            campaigns = for_sale_campaign.get('campaigns', [])
            if campaigns:
                # Get most recent campaign
                campaign_info = campaigns[0]

        # Add last ad details if available
        if campaign_info:
            data_rows.append(("LAST ADVERTISING CAMPAIGN", ""))

            if 'fromDate' in campaign_info:
                data_rows.append(("Campaign Start", campaign_info.get('fromDate', 'N/A')))
            if 'toDate' in campaign_info:
                data_rows.append(("Campaign End", campaign_info.get('toDate', 'N/A')))
            if 'daysOnMarket' in campaign_info:
                data_rows.append(("Days on Market", str(campaign_info.get('daysOnMarket', 'N/A'))))
            if 'listingMethod' in campaign_info:
                data_rows.append(("Listing Method", campaign_info.get('listingMethod', 'N/A')))
            if 'firstPublishedPrice' in campaign_info:
                price = campaign_info.get('firstPublishedPrice')
                if price and price != '0':
                    data_rows.append(("Listing Price", self._format_currency(price)))
            if 'priceDescription' in campaign_info:
                data_rows.append(("Price Description", campaign_info.get('priceDescription', 'N/A')))
            if 'auctionDate' in campaign_info:
                data_rows.append(("Auction Date", campaign_info.get('auctionDate', 'N/A')))

            # Agency from campaign
            agency = campaign_info.get('agency', {})
            if agency and agency.get('companyName'):
                data_rows.append(("Campaign Agency", agency.get('companyName', 'N/A')))

            data_rows.append(("", ""))

        # Parcel geometry
        parcel = report.get('parcel_geometry', {})
        if parcel.get('success'):
            parcel_data = parcel.get('data', {})
            features = parcel_data.get('features', [])
            if features:
                geometry = features[0].get('geometry', {})
                rings = geometry.get('rings', [])
                if rings:
                    total_points = sum(len(ring) for ring in rings)
                    data_rows.extend([
                        ("PARCEL GEOMETRY", ""),
                        ("Polygon Rings", f"{len(rings)} ring(s)"),
                        ("Coordinate Points", f"{total_points} points"),
                        ("Geometry Type", parcel_data.get('geometryType', 'N/A')),
                        ("", ""),
                    ])

        # Geospatial layers summary
        geo_layers = report.get('geospatial_layers', {})
        if geo_layers:
            # Hazards
            hazards = geo_layers.get('hazards', {})
            hazard_summary = []
            for hazard_type, data in hazards.items():
                if data.get('available'):
                    count = data.get('feature_count', 0)
                    if count:
                        hazard_summary.append(f"{hazard_type.title()} ({count})")
                    else:
                        hazard_summary.append(hazard_type.title())

            if hazard_summary:
                data_rows.extend([
                    ("HAZARD OVERLAYS", ""),
                    ("Detected Hazards", ", ".join(hazard_summary)),
                    ("", ""),
                ])

            # Easements
            easements = geo_layers.get('legal', {}).get('easements', {})
            if easements.get('available'):
                data_rows.extend([
                    ("EASEMENTS", ""),
                    ("Total Easements", f"{easements.get('count', 0)} easements"),
                    ("", ""),
                ])

            # Infrastructure
            infrastructure = geo_layers.get('infrastructure', {})
            infra_summary = []
            for infra_type, data in infrastructure.items():
                if data.get('available'):
                    count = data.get('feature_count', 0)
                    name = infra_type.replace('_', ' ').title()
                    if count:
                        infra_summary.append(f"{name} ({count})")
                    else:
                        infra_summary.append(name)

            if infra_summary:
                data_rows.extend([
                    ("INFRASTRUCTURE (5km radius)", ""),
                    ("Available Infrastructure", ", ".join(infra_summary)),
                    ("", ""),
                ])

        # Occupancy
        occupancy = property_details.get('occupancy', {})
        if occupancy and not occupancy.get('error'):
            data_rows.append(("OCCUPANCY", ""))
            if 'occupancyType' in occupancy:
                data_rows.append(("Occupancy Type", occupancy.get('occupancyType', 'N/A')))
            if 'confidenceScore' in occupancy:
                data_rows.append(("Confidence Score", occupancy.get('confidenceScore', 'N/A')))
            data_rows.append(("", ""))

        # Legal details (already accessed earlier, reuse or re-access)
        legal_details = property_details.get('legal', {})
        if legal_details and not legal_details.get('error'):
            data_rows.append(("LEGAL", ""))

            # Title information
            title_info = legal_details.get('title', {})
            if title_info:
                if 'titleReference' in title_info:
                    data_rows.append(("Title Reference", title_info.get('titleReference', 'N/A')))
                if 'titleIndicator' in title_info:
                    data_rows.append(("Title Indicator", title_info.get('titleIndicator', 'N/A')))
                if 'feeCode' in title_info:
                    data_rows.append(("Fee Code", title_info.get('feeCode', 'N/A')))
                if 'ownerCode' in title_info:
                    data_rows.append(("Owner Code", title_info.get('ownerCode', 'N/A')))

            # Parcel information
            parcels = legal_details.get('parcels', [])
            if parcels:
                parcel = parcels[0]  # Primary parcel
                if 'displayValue' in parcel:
                    data_rows.append(("Lot/Plan", parcel.get('displayValue', 'N/A')))
                if 'area' in parcel:
                    data_rows.append(("Parcel Area", parcel.get('area', 'N/A')))
                if 'landAuthority' in parcel:
                    data_rows.append(("Land Authority", parcel.get('landAuthority', 'N/A')))

            # Legal description
            legal_desc = legal_details.get('legal', {})
            if legal_desc and 'realPropertyDescription' in legal_desc:
                data_rows.append(("Legal Description", legal_desc.get('realPropertyDescription', 'N/A')))

            data_rows.append(("", ""))

        # ======= GEOSPATIAL DATA SECTIONS =======

        # Parcel Geometry Details
        parcel_geom = report.get('parcel_geometry', {})
        if parcel_geom.get('success'):
            data_rows.append(("PARCEL GEOMETRY DETAILS", ""))

            parcel_data = parcel_geom.get('data', {})

            # Geometry Type
            if 'geometryType' in parcel_data:
                data_rows.append(("Geometry Type", parcel_data.get('geometryType', 'N/A')))

            # Spatial Reference
            spatial_ref = parcel_data.get('spatialReference', {})
            if spatial_ref:
                if 'wkid' in spatial_ref:
                    data_rows.append(("Spatial Reference WKID", str(spatial_ref.get('wkid', 'N/A'))))
                if 'latestWkid' in spatial_ref:
                    data_rows.append(("Latest WKID", str(spatial_ref.get('latestWkid', 'N/A'))))

            # Feature attributes
            features = parcel_data.get('features', [])
            if features:
                attrs = features[0].get('attributes', {})
                if 'property_m2' in attrs:
                    data_rows.append(("Property Area (m²)", f"{attrs.get('property_m2', 0):.2f} m²"))
                if 'st_area(geom)' in attrs:
                    data_rows.append(("Geometry Area", f"{attrs.get('st_area(geom)', 0):.2f} m²"))
                if 'st_perimeter(geom)' in attrs:
                    data_rows.append(("Geometry Perimeter", f"{attrs.get('st_perimeter(geom)', 0):.2f} m"))

                # Polygon details
                geometry = features[0].get('geometry', {})
                rings = geometry.get('rings', [])
                if rings:
                    data_rows.append(("Polygon Rings", f"{len(rings)} ring(s)"))
                    total_vertices = sum(len(ring) for ring in rings)
                    data_rows.append(("Total Vertices", f"{total_vertices} points"))

            data_rows.append(("", ""))

        # Geospatial Layers Summary
        geo_layers = report.get('geospatial_layers', {})
        if geo_layers:
            data_rows.append(("GEOSPATIAL LAYERS SUMMARY", ""))

            # Hazards
            hazards = geo_layers.get('hazards', {})
            if hazards:
                hazard_count = sum(1 for h in hazards.values() if h.get('available'))
                data_rows.append(("Hazard Layers Available", f"{hazard_count} layers"))

                for hazard_name, hazard_data in hazards.items():
                    if hazard_data.get('available'):
                        method = hazard_data.get('method', 'N/A')
                        feature_count = hazard_data.get('feature_count', 0)
                        label = f"  {hazard_name.title()}"
                        if feature_count > 0:
                            data_rows.append((label, f"{feature_count} features ({method})"))
                        else:
                            data_rows.append((label, f"Available ({method})"))

            # Legal layers (easements)
            legal = geo_layers.get('legal', {})
            if legal:
                easements = legal.get('easements', {})
                if easements.get('available'):
                    count = easements.get('count', 0)
                    data_rows.append(("Easements", f"{count} easements found"))
                    if count > 0 and 'features' in easements:
                        # Show summary of first few easements
                        features = easements.get('features', [])[:3]  # First 3
                        for i, feat in enumerate(features, 1):
                            attrs = feat.get('attributes', {})
                            area = attrs.get('easement_area_sqm', 0)
                            locality = attrs.get('locality_name', 'N/A')
                            data_rows.append((f"  Easement {i}", f"{area:.0f} m² in {locality}"))

            # Infrastructure
            infrastructure = geo_layers.get('infrastructure', {})
            if infrastructure:
                infra_count = sum(1 for i in infrastructure.values() if i.get('available'))
                data_rows.append(("Infrastructure Layers", f"{infra_count} layers"))

                for infra_name, infra_data in infrastructure.items():
                    if infra_data.get('available'):
                        method = infra_data.get('method', 'N/A')
                        feature_count = infra_data.get('feature_count', 0)
                        label = f"  {infra_name.replace('_', ' ').title()}"
                        if feature_count > 0:
                            data_rows.append((label, f"{feature_count} features"))
                        else:
                            data_rows.append((label, "Available"))

            data_rows.append(("", ""))

        # Market Data (if available)
        market_data = report.get('market_data', {})
        if market_data and isinstance(market_data, dict):
            data_rows.append(("MARKET DATA", ""))

            # Check for market trends
            if 'trends' in market_data:
                trends = market_data['trends']
                data_rows.append(("Market Trends Available", "Yes"))
                if isinstance(trends, dict) and 'period' in trends:
                    data_rows.append(("Period", str(trends.get('period', 'N/A'))))

            # Check for market statistics
            if 'statistics' in market_data:
                stats = market_data['statistics']
                if isinstance(stats, dict):
                    for key, value in stats.items():
                        if isinstance(value, (int, float)):
                            data_rows.append((key.replace('_', ' ').title(), str(value)))

            data_rows.append(("", ""))

        # Comparables (if available)
        comparables = report.get('comparables', {})
        if comparables and isinstance(comparables, (dict, list)):
            data_rows.append(("COMPARABLE PROPERTIES", ""))

            if isinstance(comparables, dict):
                comp_list = comparables.get('properties', comparables.get('sales', []))
            else:
                comp_list = comparables

            if comp_list:
                data_rows.append(("Total Comparables", f"{len(comp_list)} properties"))

                # Show summary of first few comparables
                for i, comp in enumerate(comp_list[:5], 1):  # First 5
                    if isinstance(comp, dict):
                        address = comp.get('address', comp.get('singleLine', 'N/A'))
                        price = comp.get('price', comp.get('salePrice', 0))
                        if price:
                            data_rows.append((f"Comp {i}", f"{address[:40]}... - {self._format_currency(price)}"))
                        else:
                            data_rows.append((f"Comp {i}", address[:50]))

            data_rows.append(("", ""))

        # Mesh Block Analysis (if available)
        mesh_summary = self._load_mesh_block_summary()
        if mesh_summary:
            data_rows.append(("MESH BLOCK ANALYSIS", ""))
            data_rows.append(("Analysis Buffer", f"{mesh_summary['buffer_meters']} meters"))
            data_rows.append(("Total Mesh Blocks", f"{mesh_summary['total_blocks']} blocks"))

            # Category breakdown
            categories = mesh_summary.get('categories', {})
            if categories:
                data_rows.append(("", ""))
                data_rows.append(("Category Breakdown", ""))
                for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                    data_rows.append((f"  {category}", f"{count} blocks"))

            # Non-residential statistics
            nonres_stats = mesh_summary.get('nonresidential_stats')
            if nonres_stats:
                data_rows.append(("", ""))
                data_rows.append(("Non-Residential Distances", ""))
                data_rows.append(("  Total Non-Residential", f"{nonres_stats['count']} blocks"))
                data_rows.append(("  Closest", f"{nonres_stats['min_m']:.1f} m"))
                data_rows.append(("  Farthest", f"{nonres_stats['max_m']:.1f} m"))
                data_rows.append(("  Average", f"{nonres_stats['mean_m']:.1f} m"))
                data_rows.append(("  Median", f"{nonres_stats['median_m']:.1f} m"))

            # Top 5 closest non-residential blocks
            top_blocks = mesh_summary.get('top_nonresidential', [])
            if top_blocks:
                data_rows.append(("", ""))
                data_rows.append(("Top 5 Closest Non-Residential", ""))
                for i, block in enumerate(top_blocks, 1):
                    category = block['category']
                    distance = block['distance_m']
                    suburb = block['suburb']
                    data_rows.append((f"  #{i} {category}", f"{distance:.1f} m ({suburb})"))

            data_rows.append(("", ""))

        # Market Metrics Summary (if available)
        market_metrics = report.get('market_metrics_summary')
        if market_metrics and not market_metrics.get('error'):
            availability = market_metrics.get('availability', {})
            featured = market_metrics.get('featured_metrics', {})
            summary = market_metrics.get('summary', {})

            data_rows.append(("MARKET METRICS AVAILABILITY", ""))

            # Summary stats
            if summary:
                available = summary.get('available_metrics', 0)
                total = summary.get('total_metrics', 0)
                data_rows.append(("Metrics Available", f"{available}/{total} metrics"))
                data_rows.append(("", ""))

            # Show availability for each metric
            for metric_name, metric_info in availability.items():
                description = metric_info.get('description', metric_name.replace('_', ' ').title())

                if metric_info.get('available'):
                    data_points = metric_info.get('data_points', 0)
                    date_range = metric_info.get('date_range', 'N/A')
                    interval = metric_info.get('interval', 'N/A')

                    data_rows.append((f"✓ {description}", ""))
                    data_rows.append((f"  Data Points", f"{data_points} ({interval})"))
                    data_rows.append((f"  Date Range", date_range))

                    # Show trend if available
                    if 'growth_percent' in metric_info:
                        growth = metric_info['growth_percent']
                        first_val = metric_info.get('first_value', 0)
                        last_val = metric_info.get('last_value', 0)

                        # Format values based on metric type
                        if 'price' in metric_name or 'value' in metric_name or 'rent' in metric_name:
                            data_rows.append((f"  First Value", self._format_currency(first_val)))
                            data_rows.append((f"  Latest Value", self._format_currency(last_val)))
                        else:
                            data_rows.append((f"  First Value", f"{first_val:,.0f}"))
                            data_rows.append((f"  Latest Value", f"{last_val:,.0f}"))

                        data_rows.append((f"  Growth", f"{growth:+.1f}%"))
                    elif 'latest_value' in metric_info:
                        # For percentage metrics like rental_yield
                        latest = metric_info['latest_value']
                        if isinstance(latest, (int, float)):
                            data_rows.append((f"  Latest Value", f"{latest:.2f}%"))
                else:
                    reason = metric_info.get('reason', 'No data available')
                    data_rows.append((f"✗ {description}", reason))

                data_rows.append(("", ""))

            # Featured metrics section
            if featured:
                # Median Value (AVM) Trend
                if 'median_value' in featured:
                    mv = featured['median_value']
                    data_rows.append(("MEDIAN VALUE (AVM) TREND", ""))
                    data_rows.append(("Description", mv.get('description', 'N/A')))
                    data_rows.append(("Period", f"{mv.get('first_date', 'N/A')} to {mv.get('last_date', 'N/A')}"))
                    data_rows.append(("Data Points", f"{mv.get('data_points', 0)} ({mv.get('interval', 'N/A')})"))
                    data_rows.append(("Starting Value", self._format_currency(mv.get('first_value', 0))))
                    data_rows.append(("Current Value", self._format_currency(mv.get('last_value', 0))))
                    data_rows.append(("Growth", f"{mv.get('growth_percent', 0):+.1f}%"))
                    data_rows.append(("", ""))

                # Median Sale Price Trend
                if 'median_sale_price' in featured:
                    msp = featured['median_sale_price']
                    data_rows.append(("MEDIAN SALE PRICE TREND", ""))
                    data_rows.append(("Description", msp.get('description', 'N/A')))
                    data_rows.append(("Period", f"{msp.get('first_date', 'N/A')} to {msp.get('last_date', 'N/A')}"))
                    data_rows.append(("Data Points", f"{msp.get('data_points', 0)} ({msp.get('interval', 'N/A')})"))
                    data_rows.append(("Starting Price", self._format_currency(msp.get('first_value', 0))))
                    data_rows.append(("Current Price", self._format_currency(msp.get('last_value', 0))))
                    data_rows.append(("Growth", f"{msp.get('growth_percent', 0):+.1f}%"))
                    data_rows.append(("", ""))

                # Rental Market
                if 'rental_market' in featured:
                    rm = featured['rental_market']
                    data_rows.append(("RENTAL MARKET", ""))
                    if 'rental_yield' in rm:
                        data_rows.append(("Rental Yield", f"{rm['rental_yield']:.2f}%"))
                        if 'rental_yield_date' in rm:
                            data_rows.append(("Yield Date", rm['rental_yield_date']))
                    if 'median_rent' in rm:
                        data_rows.append(("Median Rent", f"{self._format_currency(rm['median_rent'])}/week"))
                        if 'median_rent_date' in rm:
                            data_rows.append(("Rent Date", rm['median_rent_date']))
                    data_rows.append(("", ""))

        return data_rows

    def _load_mesh_block_summary(self, output_dir: Path = None) -> Optional[Dict[str, Any]]:
        """
        Load and summarize mesh block analysis data from CSV files.

        Returns:
            Dict with mesh block summary data or None if files not found
        """
        if output_dir is None:
            output_dir = Path('data/outputs')

        # Check for mesh block CSV files
        all_blocks_file = output_dir / 'meshblocks_within_2000m.csv'
        nonres_file = output_dir / 'meshblocks_nonresidential_distances_2000m.csv'

        if not all_blocks_file.exists():
            return None

        summary = {
            'buffer_meters': 2000,
            'total_blocks': 0,
            'categories': {},
            'nonresidential_stats': None,
            'top_nonresidential': []
        }

        try:
            # Load all mesh blocks
            with open(all_blocks_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    summary['total_blocks'] += 1
                    category = row.get('MB_CAT21', 'Unknown')
                    summary['categories'][category] = summary['categories'].get(category, 0) + 1

            # Load non-residential distances
            if nonres_file.exists():
                distances = []
                top_blocks = []

                with open(nonres_file, 'r') as f:
                    reader = csv.DictReader(f)
                    for i, row in enumerate(reader):
                        try:
                            dist = float(row.get('distance_to_property_m', 0))
                            distances.append(dist)

                            # Keep top 5 closest
                            if i < 5:
                                top_blocks.append({
                                    'category': row.get('MB_CAT21', 'Unknown'),
                                    'distance_m': dist,
                                    'suburb': row.get('SA2_NAME21', 'Unknown'),
                                    'area_sqkm': float(row.get('AREASQKM21', 0))
                                })
                        except (ValueError, TypeError):
                            continue

                if distances:
                    summary['nonresidential_stats'] = {
                        'count': len(distances),
                        'min_m': min(distances),
                        'max_m': max(distances),
                        'mean_m': statistics.mean(distances),
                        'median_m': statistics.median(distances)
                    }
                    summary['top_nonresidential'] = top_blocks

            return summary

        except Exception as e:
            print(f"Warning: Could not load mesh block data: {e}")
            return None

    def _get_nested(self, data: Dict, path: str, default: Any = None) -> Any:
        """Get nested dictionary value using dot notation"""
        keys = path.split('.')
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        return value or default

    def _format_area(self, area: Any) -> str:
        """Format area measurement"""
        if area is None or area == '':
            return 'N/A'
        try:
            return f"{float(area):,.1f} m²"
        except:
            return str(area)

    def _format_measurement(self, value: Any, unit: str) -> str:
        """Format measurement with unit"""
        if value is None or value == '':
            return 'N/A'
        try:
            return f"{float(value):,.1f} {unit}"
        except:
            return str(value)

    def _format_currency(self, amount: Any) -> str:
        """Format currency"""
        if amount is None or amount == '':
            return 'N/A'
        try:
            return f"${float(amount):,.0f}"
        except:
            return str(amount)

    def generate_pdf(self, report: Dict[str, Any], output_path: str, ultra_comprehensive: bool = False):
        """Generate PDF report from property data

        Args:
            report: Comprehensive property report dictionary
            output_path: Path to save PDF
            ultra_comprehensive: If True, uses flatten_json_recursive to extract ALL fields
        """

        # Create PDF document with landscape orientation
        from reportlab.lib.pagesizes import landscape

        doc = SimpleDocTemplate(
            output_path,
            pagesize=landscape(A4),
            rightMargin=0.4*inch,
            leftMargin=0.4*inch,
            topMargin=0.4*inch,
            bottomMargin=0.4*inch
        )

        # Build document content
        story = []

        # Title
        metadata = report.get('metadata', {})
        title_text = f"Property Data Report"
        title = Paragraph(title_text, self.title_style)
        story.append(title)

        # Subtitle with address
        address = metadata.get('address', 'N/A')
        subtitle_style = ParagraphStyle('Subtitle', parent=self.normal_style, alignment=TA_CENTER, fontSize=8)
        subtitle = Paragraph(f"<b>{address}</b>", subtitle_style)
        story.append(subtitle)
        story.append(Spacer(1, 0.1*inch))

        # Extract data - use flattened mode if requested
        if ultra_comprehensive:
            data_rows = self.extract_data_flattened(report)
        else:
            data_rows = self.extract_data_summary(report)

        # Convert to 3-panel layout (6 columns total: label-value, label-value, label-value)
        table_data = []
        current_row = []
        section_header_row = None

        for label, value in data_rows:
            # Check if this is a section header
            if value == "" and label == label.upper() and label != "":
                # Flush current row if it has content
                if current_row:
                    while len(current_row) < 6:
                        current_row.append("")
                    table_data.append(current_row)
                    current_row = []

                # Section header spans all 6 columns
                header_para = Paragraph(f"<b>{label}</b>", self.heading_style)
                table_data.append([header_para, "", "", "", "", ""])

            elif label == "" and value == "":
                # Spacer - flush current row and add empty row
                if current_row:
                    while len(current_row) < 6:
                        current_row.append("")
                    table_data.append(current_row)
                    current_row = []
                # Skip empty rows for compactness

            else:
                # Regular data row - add to current row (building 3 panels)
                label_para = Paragraph(f"<b>{label}</b>", self.label_style)
                value_para = Paragraph(str(value), self.normal_style)
                current_row.extend([label_para, value_para])

                # If we have 3 complete panels (6 items), add to table
                if len(current_row) >= 6:
                    table_data.append(current_row[:6])
                    current_row = current_row[6:]

        # Add any remaining items
        if current_row:
            while len(current_row) < 6:
                current_row.append("")
            table_data.append(current_row)

        # Create table with 6 columns (3 label-value pairs)
        # Landscape A4 is 11.7" x 8.3", with 0.4" margins = 10.9" usable width
        label_width = 1.6*inch
        value_width = 2.0*inch
        col_widths = [label_width, value_width, label_width, value_width, label_width, value_width]

        table = Table(table_data, colWidths=col_widths, repeatRows=0)

        # Compact table styling
        table.setStyle(TableStyle([
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))

        # Style section headers (span across all columns)
        for i, row in enumerate(table_data):
            if len(row) > 0 and isinstance(row[0], Paragraph):
                # Check if this looks like a header
                if len([cell for cell in row[1:] if cell == ""]) == 5:
                    table.setStyle(TableStyle([
                        ('SPAN', (0, i), (5, i)),
                        ('BACKGROUND', (0, i), (5, i), colors.HexColor('#e8e8e8')),
                        ('LEFTPADDING', (0, i), (5, i), 4),
                    ]))

        story.append(table)

        # Footer
        story.append(Spacer(1, 0.15*inch))
        timestamp = metadata.get('extraction_timestamp', datetime.now().isoformat())
        footer_text = f"Report generated: {timestamp[:19].replace('T', ' ')} | Property ID: {metadata.get('property_id', 'N/A')}"
        footer_style = ParagraphStyle('Footer', parent=self.normal_style, fontSize=6, alignment=TA_CENTER)
        footer = Paragraph(footer_text, footer_style)
        story.append(footer)

        # Build PDF
        doc.build(story)
        print(f"✅ PDF report saved: {output_path}", file=sys.stderr)


def load_report(input_path: str) -> Dict[str, Any]:
    """Load comprehensive report JSON"""
    with open(input_path, 'r') as f:
        return json.load(f)


def generate_report_from_address(address: str, output_dir: Path) -> str:
    """Generate comprehensive report and PDF from address"""
    # Import here to avoid circular dependencies
    from utils.property_data_processor import PropertyDataProcessor
    from utils.geospatial_api_client import GeospatialAPIClient
    from utils.pipeline_utils import ProgressReporter

    # Import the comprehensive reporter
    sys.path.insert(0, str(Path(__file__).parent))
    from comprehensive_property_report import ComprehensivePropertyReporter

    print("🚀 Initializing CoreLogic clients...", file=sys.stderr)
    property_reporter = ProgressReporter("Property Lookup")
    property_processor = PropertyDataProcessor(reporter=property_reporter)
    geo_client = GeospatialAPIClient.from_env()

    reporter = ComprehensivePropertyReporter(geo_client, property_processor)

    print("📊 Generating comprehensive report...", file=sys.stderr)
    report = reporter.generate_comprehensive_report(
        address,
        include_maps=False,
        output_dir=output_dir
    )

    property_id = report['metadata']['property_id']

    # Save JSON report
    json_path = output_dir / f"{property_id}_comprehensive_report.json"
    with open(json_path, 'w') as f:
        json.dump(report, f, indent=2)

    return str(json_path)


def main():
    parser = argparse.ArgumentParser(
        description='Generate PDF report from comprehensive property data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # From existing JSON report
  python3 scripts/generate_property_pdf.py --input data/property_reports/13683380_comprehensive_report.json

  # Generate from address directly
  python3 scripts/generate_property_pdf.py --address "5 Settlers Court, Vermont South VIC 3133"

  # Custom output location
  python3 scripts/generate_property_pdf.py --input report.json --output custom_report.pdf

Requirements:
  pip install reportlab
        """
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--input',
        type=str,
        help='Path to comprehensive report JSON file'
    )
    group.add_argument(
        '--address',
        type=str,
        help='Property address (will generate report first)'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Output PDF file path (default: auto-generated from property ID)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/property_reports',
        help='Output directory for reports (default: data/property_reports)'
    )

    parser.add_argument(
        '--ultra-comprehensive',
        action='store_true',
        help='Extract ALL fields using flatten method (generates larger PDFs with every field)'
    )

    args = parser.parse_args()

    try:
        if not REPORTLAB_AVAILABLE:
            print("❌ Error: reportlab is required", file=sys.stderr)
            print("Install with: pip install reportlab", file=sys.stderr)
            return 1

        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Get input JSON path
        if args.address:
            print(f"📍 Generating report for: {args.address}", file=sys.stderr)
            input_json = generate_report_from_address(args.address, output_dir)
        else:
            input_json = args.input

        # Load report
        print(f"📖 Loading report: {input_json}", file=sys.stderr)
        report = load_report(input_json)

        # Determine output path
        if args.output:
            output_pdf = args.output
        else:
            property_id = report.get('metadata', {}).get('property_id', 'unknown')
            output_pdf = str(output_dir / f"{property_id}_property_report.pdf")

        # Generate PDF
        print(f"📄 Generating PDF report...", file=sys.stderr)
        generator = PropertyDataPDFGenerator()
        generator.generate_pdf(report, output_pdf, ultra_comprehensive=args.ultra_comprehensive)

        print(f"\n✅ Report complete!", file=sys.stderr)
        print(f"📁 PDF saved to: {output_pdf}", file=sys.stderr)

        return 0

    except Exception as e:
        print(f"\n❌ Error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
