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

# Import new mapping engine and utilities
try:
    from utils.mapping_engine import MappingEngine
    from utils.extraction_utils import (
        get_nested_value,
        format_missing_value,
        truncate_text,
        wrap_text,
        format_currency,
        format_area
    )
    from extractors.planning_zone_extractor import PlanningZoneExtractor
    from extractors.development_approvals_extractor import DevelopmentApprovalsExtractor
    from extractors.encumbrances_extractor import EncumbrancesExtractor
    MAPPING_ENGINE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Mapping engine not available: {e}", file=sys.stderr)
    MAPPING_ENGINE_AVAILABLE = False

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

        # Initialize mapping engine and extractors
        if MAPPING_ENGINE_AVAILABLE:
            try:
                self.mapping_engine = MappingEngine()
                self.planning_extractor = PlanningZoneExtractor()
                self.approvals_extractor = DevelopmentApprovalsExtractor()
                self.encumbrances_extractor = EncumbrancesExtractor()
            except Exception as e:
                print(f"⚠️  Warning: Failed to initialize mapping engine: {e}", file=sys.stderr)
                self.mapping_engine = None
        else:
            self.mapping_engine = None

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

        # Google Places Impact Analysis
        places_impact = report.get('google_places_impact')
        if places_impact and not places_impact.get('error'):
            data_rows.append(("GOOGLE PLACES IMPACT ANALYSIS", ""))

            # Summary statistics
            total_cats = places_impact.get('total_categories', 0)
            with_matches = places_impact.get('categories_with_matches', 0)
            data_rows.append(("Total Categories Analyzed", str(total_cats)))
            data_rows.append(("Categories with Nearby Places", f"{with_matches}/{total_cats}"))
            data_rows.append(("", ""))

            # Distance distribution
            dist_dist = places_impact.get('distance_distribution', {})
            if dist_dist:
                data_rows.append(("DISTANCE SUMMARY", ""))
                if 'closest_meters' in dist_dist:
                    data_rows.append(("Closest Impact", f"{dist_dist['closest_meters']:.0f}m"))
                if 'furthest_meters' in dist_dist:
                    data_rows.append(("Furthest Impact", f"{dist_dist['furthest_meters']:.0f}m"))
                if 'median_meters' in dist_dist:
                    data_rows.append(("Median Distance", f"{dist_dist['median_meters']:.0f}m"))

                # Distance ranges
                data_rows.append(("Within 100m", str(dist_dist.get('within_100m', 0))))
                data_rows.append(("Within 250m", str(dist_dist.get('within_250m', 0))))
                data_rows.append(("Within 600m", str(dist_dist.get('within_600m', 0))))
                data_rows.append(("Within 3000m", str(dist_dist.get('within_3000m', 0))))
                data_rows.append(("", ""))

            # Top 10 closest impacts
            closest_impacts = places_impact.get('closest_impacts', [])[:10]
            if closest_impacts:
                data_rows.append(("CLOSEST PLACES BY CATEGORY", ""))
                for impact in closest_impacts:
                    category = impact.get('category', 'Unknown').replace('_', ' ').title()
                    name = impact.get('name', 'N/A')
                    distance = impact.get('distance_meters', 0)
                    level = impact.get('level', 'N/A')

                    data_rows.append((f"{category}", f"{name} ({distance:.0f}m)"))
                data_rows.append(("", ""))

        return data_rows

    def extract_data_categorized(self, report: Dict[str, Any]) -> List[Tuple[str, str]]:
        """
        Extract data using the 11-category Pre-Qualification Data Collection structure.
        Returns list of (label, value) tuples organized by categories.

        Categories:
        1. INSTRUCTIONS
        2. LOCATION AND ADMINISTRATIVE
        3. MAPPING, TOPOGRAPHY AND PLACES
        4. LEGAL
        5. CHARACTERISTICS
        6. IMAGERY
        7. OCCUPANCY
        8. LOCAL MARKET
        9. TRANSACTION HISTORY
        10. CAMPAIGNS
        11. SALES EVIDENCE
        """
        data_rows = []

        # Load additional data files
        property_id = report.get('metadata', {}).get('property_id', 'N/A')
        output_dir = Path('data/property_reports')

        # Load comparable sales
        comparable_sales = self._load_comparable_sales(property_id, output_dir)

        # Load mesh block analysis
        mesh_block_data = self._load_mesh_block_data(property_id, output_dir)

        # Load parcel elevation/orientation
        parcel_elev_orient = self._load_parcel_elevation_orientation(property_id, output_dir)

        # Load Google Places impact analysis (from run_places_analysis.py)
        places_impact = self._load_places_impact(property_id, output_dir)

        # Load property images (from fetch_property_images.py)
        property_images = self._load_property_images(property_id, output_dir)

        # Load planning zones summary (from analyze_planning_zones.py)
        planning_zones = self._load_planning_zones(output_dir)

        # Load development approvals (from generate_development_approval_report.py)
        development_approvals = self._load_development_approvals(output_dir, property_id)

        # === CATEGORY 1: INSTRUCTIONS ===
        data_rows.extend(self._extract_category_1_instructions(report))

        # === CATEGORY 2: LOCATION AND ADMINISTRATIVE ===
        data_rows.extend(self._extract_category_2_location_admin(report, mesh_block_data, planning_zones, development_approvals))

        # === CATEGORY 3: MAPPING, TOPOGRAPHY AND PLACES ===
        data_rows.extend(self._extract_category_3_mapping(report, mesh_block_data, places_impact))

        # === CATEGORY 4: LEGAL ===
        data_rows.extend(self._extract_category_4_legal(report))

        # === CATEGORY 5: CHARACTERISTICS ===
        data_rows.extend(self._extract_category_5_characteristics(report, parcel_elev_orient))

        # === CATEGORY 6: IMAGERY ===
        data_rows.extend(self._extract_category_6_imagery(property_images))

        # === CATEGORY 7: OCCUPANCY ===
        data_rows.extend(self._extract_category_7_occupancy(report))

        # === CATEGORY 8: LOCAL MARKET ===
        data_rows.extend(self._extract_category_8_local_market(report))

        # === CATEGORY 9: TRANSACTION HISTORY ===
        data_rows.extend(self._extract_category_9_transaction_history(report))

        # === CATEGORY 10: CAMPAIGNS ===
        data_rows.extend(self._extract_category_10_campaigns(report))

        # === CATEGORY 11: SALES EVIDENCE ===
        data_rows.extend(self._extract_category_11_sales_evidence(comparable_sales))

        return data_rows

    def _load_comparable_sales(self, property_id: str, output_dir: Path) -> Optional[Dict[str, Any]]:
        """Load comparable sales JSON file"""
        comp_file = output_dir / f"{property_id}_comparable_sales.json"
        if comp_file.exists():
            try:
                with open(comp_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load comparable sales: {e}", file=sys.stderr)
        return None

    def _load_mesh_block_data(self, property_id: str, output_dir: Path) -> Optional[Dict[str, Any]]:
        """Load mesh block analysis JSON file"""
        mesh_file = output_dir / f"{property_id}_mesh_block_analysis_2000m.json"
        if mesh_file.exists():
            try:
                with open(mesh_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load mesh block data: {e}", file=sys.stderr)
        return None

    def _load_parcel_elevation_orientation(self, property_id: str, output_dir: Path) -> Optional[Dict[str, Any]]:
        """Load parcel elevation and orientation JSON file"""
        parcel_file = output_dir / f"{property_id}_parcel_elevation_orientation.json"
        if parcel_file.exists():
            try:
                with open(parcel_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load parcel elevation/orientation: {e}", file=sys.stderr)
        return None

    def _load_places_impact(self, property_id: str, output_dir: Path) -> Optional[Dict[str, Any]]:
        """Load Google Places impact analysis from property-specific JSON file

        Looks for {property_id}_property_impacts.json from run_places_analysis.py script.
        Tries multiple possible locations:
        1. {output_dir}/{property_id}_property_impacts.json (property-specific)
        2. {output_dir}/../places_analysis/property_impacts.json (generic)
        3. data/places_analysis/property_impacts.json (generic fallback)
        """
        # Try property-specific file first (recommended architecture)
        places_file = output_dir / f"{property_id}_property_impacts.json"
        if places_file.exists():
            try:
                with open(places_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load places impact from {places_file}: {e}", file=sys.stderr)

    def _load_property_images(self, property_id: str, output_dir: Path) -> Optional[Dict[str, Any]]:
        """Load property images metadata JSON file

        Looks for {property_id}_property_images.json from fetch_property_images.py script.
        """
        images_file = output_dir / f"{property_id}_property_images.json"
        if images_file.exists():
            try:
                with open(images_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load property images: {e}", file=sys.stderr)
        return None

    def _load_planning_zones(self, output_dir: Path) -> Optional[Dict[str, Any]]:
        """Load planning zones summary from analyze_planning_zones.py script.

        Looks for planning_zones_summary.json in data/ directory.
        """
        zones_file = output_dir.parent / 'planning_zones_summary.json'
        if zones_file.exists():
            try:
                with open(zones_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load planning zones: {e}", file=sys.stderr)
        return None

    def _load_development_approvals(self, output_dir: Path, property_id: int) -> Optional[Dict[str, Any]]:
        """Load development approvals from generate_development_approval_report.py script.

        Looks for {property_id}_development_approvals.json in output directory.
        """
        approvals_file = output_dir / f'{property_id}_development_approvals.json'
        if approvals_file.exists():
            try:
                with open(approvals_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load development approvals: {e}", file=sys.stderr)
        return None

    def _match_planning_zone(self, zone_code: str, zones_data: Optional[Dict]) -> Optional[Dict[str, Any]]:
        """Match zone code to planning zone data.

        Args:
            zone_code: Zone code from property (e.g., "NRZ5")
            zones_data: Planning zones summary data

        Returns:
            Matched zone data or None
        """
        if not zones_data or not zone_code:
            return None

        # Try to find matching zone in schemes
        schemes = zones_data.get('schemes', {})

        # Try exact match first (case-insensitive)
        for scheme_key, scheme_data in schemes.items():
            if zone_code.lower() in scheme_key.lower():
                return scheme_data

        # Try partial match on zone name
        for scheme_key, scheme_data in schemes.items():
            zone_name = scheme_data.get('zone_name', '').lower()
            if 'neighbourhood' in zone_name and zone_code.lower().startswith('nrz'):
                return scheme_data

        return None

        # Try generic file in places_analysis directory (legacy)
        places_file = output_dir.parent / 'places_analysis' / 'property_impacts.json'
        if places_file.exists():
            try:
                with open(places_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load places impact from {places_file}: {e}", file=sys.stderr)

        # Try absolute path to generic file (legacy fallback)
        places_file = Path('data/places_analysis/property_impacts.json')
        if places_file.exists():
            try:
                with open(places_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load places impact from {places_file}: {e}", file=sys.stderr)

        return None

    def _extract_category_1_instructions(self, report: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Category 1: INSTRUCTIONS - Coverage 0%"""
        rows = [
            ("1. INSTRUCTIONS", ""),
            ("Coverage", "0% - Not captured in source data"),
            ("", ""),
            ("[GAP] Note", "This category is not present in the current data model"),
            ("", ""),
            ("[GAP] Client Name", "Not captured"),
            ("[GAP] Client Id", "Not captured"),
            ("", ""),
            ("[GAP] Job Number", "Not captured"),
            ("[GAP] Job Type", "Not captured"),
            ("[GAP] Valuation Estimate", "Not captured"),
            ("", ""),
            ("[GAP] Parties", "Not captured"),
            ("[GAP] Special Instructions", "Not captured"),
            ("", ""),
        ]
        return rows

    def _extract_category_2_location_admin(self, report: Dict[str, Any], mesh_block_data: Optional[Dict],
                                           planning_zones: Optional[Dict] = None,
                                           development_approvals: Optional[Dict] = None) -> List[Tuple[str, str]]:
        """Category 2: LOCATION AND ADMINISTRATIVE - Coverage 100%

        Uses hybrid approach:
        - Simple fields extracted via mapping engine (YAML config)
        - Complex logic handled by specialized extractors
        """
        rows = []

        # Use mapping engine if available, otherwise fall back to legacy code
        if self.mapping_engine and MAPPING_ENGINE_AVAILABLE:
            return self._extract_category_2_hybrid(report, mesh_block_data, planning_zones, development_approvals)

        # Legacy extraction (original code)
        return self._extract_category_2_legacy(report, mesh_block_data, planning_zones, development_approvals)

    def _extract_category_2_hybrid(self, report: Dict[str, Any], mesh_block_data: Optional[Dict],
                                   planning_zones: Optional[Dict] = None,
                                   development_approvals: Optional[Dict] = None) -> List[Tuple[str, str]]:
        """Hybrid extraction using mapping engine + extractors"""
        rows = []

        # Prepare all data sources
        all_data = {
            'property_details': report.get('property_details', {}),
            'mesh_block_data': mesh_block_data,
            'planning_zones': planning_zones,
            'development_approvals': development_approvals,
            'metadata': report.get('metadata', {})
        }

        # Extract simple fields from config
        rows.extend(self.mapping_engine.extract_category_simple_fields(2, all_data))

        # Extract complex fields using specialized extractors
        site = all_data['property_details'].get('site', {})
        zone_code = site.get('zoneCodeLocal', 'Unknown')

        # Match planning zone data
        zone_data = self._match_planning_zone(zone_code, planning_zones) if planning_zones else None

        # Planning zone sections (complex extraction)
        if zone_data:
            rows.extend(self.planning_extractor.extract_section_1_uses(zone_data))
            rows.extend(self.planning_extractor.extract_section_2_uses(zone_data))
            rows.extend(self.planning_extractor.extract_opportunities_and_requirements(zone_data))
        else:
            # No zone data available
            rows.append(("Section 1 - Permit NOT Required", "Unknown"))
            rows.append(("Section 2 - Permit Required", "Unknown"))
            rows.append(("Opportunities & Requirements", "Unknown"))
            rows.append(("", ""))

        # Development approvals (complex extraction)
        rows.extend(self.approvals_extractor.extract(development_approvals))

        return rows

    def _extract_category_2_legacy(self, report: Dict[str, Any], mesh_block_data: Optional[Dict],
                                   planning_zones: Optional[Dict] = None,
                                   development_approvals: Optional[Dict] = None) -> List[Tuple[str, str]]:
        """Legacy category 2 extraction (original code - used as fallback)"""
        rows = [
            ("2. LOCATION AND ADMINISTRATIVE", ""),
            ("Coverage", "100% - Complete"),
            ("", ""),
        ]

        property_details = report.get('property_details', {})
        location = property_details.get('location', {})
        site = property_details.get('site', {})

        # ADDRESS sub-section
        rows.append(("ADDRESS", ""))
        address = report.get('metadata', {}).get('address', 'N/A')
        rows.append(("Address", address))
        rows.append(("", ""))

        # LOCATION sub-section
        rows.append(("LOCATION", ""))
        rows.append(("Council Area", location.get('councilArea', 'N/A')))
        rows.append(("Postcode", location.get('postcode', {}).get('name', 'N/A')))
        rows.append(("Locality", location.get('locality', {}).get('name', 'N/A')))

        # Coordinates
        lat = location.get('latitude')
        lon = location.get('longitude')
        if lat and lon:
            rows.append(("Coordinates", f"{lat}, {lon}"))
        rows.append(("", ""))

        # STATISTICAL AREAS sub-section
        if mesh_block_data:
            mesh_analysis = mesh_block_data.get('mesh_block_analysis', {})

            rows.append(("STATISTICAL AREAS", ""))

            # SA1 Codes
            sa1_codes = mesh_analysis.get('sa1_codes', [])
            total_sa1 = mesh_analysis.get('total_sa1_codes', len(sa1_codes))
            if sa1_codes:
                first_5 = sa1_codes[:5]
                remaining = total_sa1 - 5
                sa1_str = f"{total_sa1} codes: {', '.join(map(str, first_5))}"
                if remaining > 0:
                    sa1_str += f" (+ {remaining} more)"
                rows.append(("SA1 Codes", sa1_str))

            # SA2 Areas
            sa2_names = mesh_analysis.get('sa2_names', [])
            if sa2_names:
                rows.append(("SA2 Areas", ", ".join(sa2_names)))

            # SA3 Areas
            sa3_names = mesh_analysis.get('sa3_names', [])
            if sa3_names:
                rows.append(("SA3 Areas", ", ".join(sa3_names)))

            # SA4 Areas
            sa4_names = mesh_analysis.get('sa4_names', [])
            if sa4_names:
                rows.append(("SA4 Areas", ", ".join(sa4_names)))

            rows.append(("", ""))

        # Top-level fields
        rows.append(("State", report.get('metadata', {}).get('state', 'N/A')))

        # PLANNING AND ZONING sub-section
        rows.append(("PLANNING AND ZONING", ""))

        zone_code = site.get('zoneCodeLocal', 'Unknown')
        zone_description = site.get('zoneDescriptionLocal', 'Unknown')

        rows.append(("Zoning > Code", zone_code))
        rows.append(("Zoning > Description", zone_description))
        rows.append(("", ""))

        # Try to match planning zone data
        zone_data = self._match_planning_zone(zone_code, planning_zones) if planning_zones else None

        if zone_data:
            table_of_uses = zone_data.get('table_of_uses', {})

            # Section 1 - Permit NOT required (structured data)
            section1_uses = table_of_uses.get('section_1_uses', [])
            if section1_uses:
                rows.append(("Section 1 - Permit NOT Required", ""))
                for i, use in enumerate(section1_uses[:10], 1):  # Limit to first 10
                    rows.append((f"  {i}", use[:100]))  # Truncate long uses
                if len(section1_uses) > 10:
                    rows.append(("  ...", f"+ {len(section1_uses) - 10} more uses"))
                rows.append(("", ""))
            else:
                rows.append(("Section 1 - Permit NOT Required", "Unknown"))
                rows.append(("", ""))

            # Section 2 - Permit required (structured data)
            section2_uses = table_of_uses.get('section_2_uses', [])
            if section2_uses:
                rows.append(("Section 2 - Permit Required", ""))
                for i, use in enumerate(section2_uses[:10], 1):  # Limit to first 10
                    rows.append((f"  {i}", use[:100]))  # Truncate long uses
                if len(section2_uses) > 10:
                    rows.append(("  ...", f"+ {len(section2_uses) - 10} more uses"))
                rows.append(("", ""))
            else:
                rows.append(("Section 2 - Permit Required", "Unknown"))
                rows.append(("", ""))

            # Sections 3 & 4 combined - Non-residential opportunities + Site requirements
            combined_info = []

            # Non-residential uses
            non_res_uses = zone_data.get('non_residential_uses', [])
            if non_res_uses:
                combined_info.append("NON-RESIDENTIAL OPPORTUNITIES:")
                for use in non_res_uses[:8]:  # Limit to 8
                    combined_info.append(f"• {use}")
                if len(non_res_uses) > 8:
                    combined_info.append(f"• + {len(non_res_uses) - 8} more")

            # Site requirements
            site_reqs = zone_data.get('site_requirements', {})
            if site_reqs:
                if combined_info:
                    combined_info.append("")  # Blank line separator
                combined_info.append("SITE REQUIREMENTS:")
                if site_reqs.get('minimum_lot_size'):
                    combined_info.append(f"• Min Lot Size: {site_reqs['minimum_lot_size']}")
                if site_reqs.get('site_coverage'):
                    combined_info.append(f"• Site Coverage: {site_reqs['site_coverage']}")
                if site_reqs.get('permeability'):
                    combined_info.append(f"• Permeability: {site_reqs['permeability']}")

            # Height restrictions
            height_restrictions = zone_data.get('height_restrictions', [])
            if height_restrictions:
                if combined_info:
                    combined_info.append("")
                combined_info.append("HEIGHT RESTRICTIONS:")
                for hr in height_restrictions[:3]:  # Limit to 3
                    height = hr.get('height', 'Unknown')
                    combined_info.append(f"• {height}")

            if combined_info:
                rows.append(("Opportunities & Requirements", "\n".join(combined_info)))
            else:
                rows.append(("Opportunities & Requirements", "Unknown"))

        else:
            # No planning zone data available
            rows.append(("Section 1 - Permit NOT Required", "Unknown"))
            rows.append(("Section 2 - Permit Required", "Unknown"))
            rows.append(("Opportunities & Requirements", "Unknown"))

        rows.append(("", ""))

        # DEVELOPMENT APPROVALS sub-section
        rows.append(("DEVELOPMENT APPROVALS", ""))

        if development_approvals:
            metadata = development_approvals.get('metadata', {})
            summary = development_approvals.get('summary', {})
            permits = development_approvals.get('permits', [])

            # Summary statistics
            rows.append(("Total Permits", str(metadata.get('total_permits', 0))))
            rows.append(("Approved", str(summary.get('approved_permits', 0))))
            rows.append(("Pending", str(summary.get('pending_permits', 0))))
            rows.append(("Refused", str(summary.get('refused_permits', 0))))

            if summary.get('latest_permit_date'):
                rows.append(("Latest Permit Date", summary.get('latest_permit_date')))

            rows.append(("", ""))

            # Latest permit details
            if permits:
                latest_permit = permits[0]  # Already sorted by date in report
                rows.append(("Latest Permit Details", ""))
                rows.append(("  Permit Number", latest_permit.get('permit_number', 'Unknown')))
                rows.append(("  Status", latest_permit.get('status', 'Unknown')))

                decision_date = latest_permit.get('decision_date') or latest_permit.get('lodgement_date')
                if decision_date:
                    rows.append(("  Date", decision_date))

                description = latest_permit.get('description')
                if description:
                    # Split long descriptions across multiple lines if needed
                    if len(description) > 80:
                        # Split into chunks
                        words = description.split()
                        lines = []
                        current_line = []
                        current_length = 0

                        for word in words:
                            if current_length + len(word) + 1 <= 80:
                                current_line.append(word)
                                current_length += len(word) + 1
                            else:
                                if current_line:
                                    lines.append(' '.join(current_line))
                                current_line = [word]
                                current_length = len(word)

                        if current_line:
                            lines.append(' '.join(current_line))

                        rows.append(("  Description", lines[0] if lines else description[:80]))
                        for line in lines[1:]:
                            rows.append(("", line))
                    else:
                        rows.append(("  Description", description))

                permit_type = latest_permit.get('permit_type')
                if permit_type and permit_type != "Planning Permit":
                    rows.append(("  Permit Type", permit_type))

                # Show additional permits if available
                if len(permits) > 1:
                    rows.append(("", ""))
                    rows.append(("Additional Permits", f"{len(permits) - 1} earlier permit(s) on record"))
        else:
            rows.append(("Status", "No development approval data available"))

        rows.append(("", ""))

        return rows

    def _extract_category_3_mapping(self, report: Dict[str, Any], mesh_block_data: Optional[Dict],
                                   places_impact: Optional[Dict] = None) -> List[Tuple[str, str]]:
        """Category 3: MAPPING, TOPOGRAPHY AND PLACES - Coverage 75%"""
        rows = [
            ("3. MAPPING, TOPOGRAPHY AND PLACES", ""),
            ("Coverage", "75% - Good coverage"),
            ("", ""),
        ]

        geo_layers = report.get('geospatial_layers', {})

        # INFRASTRUCTURE sub-section
        infrastructure = geo_layers.get('infrastructure', {})
        if infrastructure:
            rows.append(("INFRASTRUCTURE", ""))

            # Check each infrastructure type
            for key, label in [
                ('electric_transmission_lines', 'Electric Transmission'),
                ('ferry', 'Ferry'),
                ('railway', 'Railway'),
                ('railway_stations', 'Railway Stations'),
                ('streets', 'Streets')
            ]:
                infra_data = infrastructure.get(key, {})
                if infra_data.get('available'):
                    rows.append((label, "Available (image_check)"))

            rows.append(("", ""))

        # GEOSPATIAL LAYERS sub-section
        if geo_layers:
            rows.append(("GEOSPATIAL LAYERS", ""))

            # Hazards (excluding heritage - shown in ENCUMBRANCES)
            hazards = geo_layers.get('hazards', {})
            if hazards:
                rows.append(("Hazards", ""))
                for hazard_name, hazard_data in hazards.items():
                    # Skip heritage - it's shown in ENCUMBRANCES section
                    if hazard_name == 'heritage':
                        continue
                    if isinstance(hazard_data, dict) and hazard_data.get('available'):
                        method = hazard_data.get('method', 'N/A')
                        rows.append((f"{hazard_name.title()}", f"Available ({method})"))
                rows.append(("", ""))

        # MESH BLOCK sub-section
        if mesh_block_data:
            mesh_analysis = mesh_block_data.get('mesh_block_analysis', {})

            rows.append(("MESH BLOCK", ""))
            rows.append(("Search Radius M", str(mesh_analysis.get('search_radius_m', 'N/A'))))
            rows.append(("Total Meshblocks", str(mesh_analysis.get('total_meshblocks', 'N/A'))))
            rows.append(("Residential Meshblocks", str(mesh_analysis.get('residential_meshblocks', 'N/A'))))
            rows.append(("Non Residential Meshblocks", str(mesh_analysis.get('non_residential_meshblocks', 'N/A'))))

            # Category Breakdown
            category_breakdown = mesh_analysis.get('category_breakdown', {})
            if category_breakdown:
                breakdown_str = ", ".join([f"{cat}: {count}" for cat, count in category_breakdown.items()])
                rows.append(("Category Breakdown", breakdown_str))

            # Non-Residential Distances
            nonres_distances = mesh_analysis.get('non_residential_distances', {})
            if nonres_distances:
                rows.append(("", ""))
                rows.append(("Non-Residential Distances", ""))
                rows.append(("Closest", f"{nonres_distances.get('closest_m', 'N/A')}m"))
                rows.append(("Average", f"{nonres_distances.get('average_m', 'N/A')}m"))
                rows.append(("Farthest", f"{nonres_distances.get('farthest_m', 'N/A')}m"))

            # Top 5 Closest Non-Residential
            top_5 = mesh_analysis.get('top_5_closest_non_residential', [])
            if top_5:
                top_5_str = "; ".join([
                    f"{i+1}. {block['category']} ({block['distance_m']}m, {block['sa2_name']})"
                    for i, block in enumerate(top_5)
                ])
                rows.append(("Top 5 Closest Non-Residential", top_5_str))

            rows.append(("", ""))

        # SURROUNDING sub-section
        # Try to use loaded places_impact from separate file first, otherwise fall back to embedded data
        if not places_impact:
            places_impact = report.get('google_places_impact', {})

        if places_impact and not places_impact.get('error'):
            rows.append(("SURROUNDING", ""))

            # Handle multiple data structures:
            # 1. Property-specific file with 'summary' and 'closest_impacts' at top level
            # 2. Full property_impacts.json with 'summary' and 'impact_analysis'
            # 3. Embedded comprehensive_report.json structure

            # Check if this is property-specific file structure (has 'summary' at top level)
            if 'summary' in places_impact:
                summary = places_impact.get('summary', {})
                rows.append(("Total Categories", str(summary.get('total_categories', 'N/A'))))
                rows.append(("Categories With Matches", str(summary.get('categories_with_matches', 'N/A'))))
                rows.append(("Categories Without Matches", str(summary.get('categories_without_matches', 'N/A'))))

                # Check if we have 'closest_impacts' at top level (property-specific file)
                closest_impacts = places_impact.get('closest_impacts', [])

                # Or if we have 'impact_analysis' structure (full property_impacts.json)
                if not closest_impacts and 'impact_analysis' in places_impact:
                    impact_analysis = places_impact.get('impact_analysis', {})
                    closest_places = []
                    for level_name, level_data in impact_analysis.items():
                        for category_name, category_data in level_data.items():
                            closest_place = category_data.get('closest_place')
                            if closest_place:
                                closest_places.append({
                                    'category': category_name,
                                    'name': closest_place.get('name'),
                                    'distance_meters': closest_place.get('distance_meters'),
                                    'level': level_name
                                })
                    closest_places.sort(key=lambda x: x.get('distance_meters', float('inf')))
                    if closest_places:
                        closest_impacts = [closest_places[0]]

                # Display closest impact
                if closest_impacts:
                    closest = closest_impacts[0]
                    rows.append(("Closest Impact Category", closest.get('category', 'N/A')))
                    rows.append(("Closest Impact Name", closest.get('name', 'N/A')))
                    rows.append(("Closest Impact Distance", f"{closest.get('distance_meters', 0):.1f}m"))
                    rows.append(("Closest Impact Level", closest.get('level', 'N/A')))
            else:
                # Old embedded structure from comprehensive_report.json
                rows.append(("Total Categories", str(places_impact.get('total_categories', 'N/A'))))
                rows.append(("Categories With Matches", str(places_impact.get('categories_with_matches', 'N/A'))))
                rows.append(("Categories Without Matches", str(places_impact.get('categories_without_matches', 'N/A'))))

                # Closest Impacts
                closest_impacts = places_impact.get('closest_impacts', [])
                if closest_impacts:
                    closest = closest_impacts[0]
                    rows.append(("Closest Impact Category", closest.get('category', 'N/A')))
                    rows.append(("Closest Impact Name", closest.get('name', 'N/A')))
                    rows.append(("Closest Impact Distance", f"{closest.get('distance_meters', 0):.1f}m"))
                    rows.append(("Closest Impact Level", closest.get('level', 'N/A')))

            rows.append(("", ""))

        return rows

    def _extract_category_4_legal(self, report: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Category 4: LEGAL - Coverage 100%"""
        rows = [
            ("4. LEGAL", ""),
            ("Coverage", "100% - Complete"),
            ("", ""),
        ]

        property_details = report.get('property_details', {})
        legal = property_details.get('legal', {})
        geo_layers = report.get('geospatial_layers', {})

        # ENCUMBRANCES sub-section - use extractor if available
        if self.mapping_engine and MAPPING_ENGINE_AVAILABLE:
            rows.extend(self.encumbrances_extractor.extract(geo_layers))
        else:
            # Legacy encumbrances extraction
            rows.append(("ENCUMBRANCES", ""))

            # Easements
            easements = geo_layers.get('legal', {}).get('easements', {})
            if easements and easements.get('available'):
                rows.append(("Easements > Available", "Yes"))
                rows.append(("Easements > Count", str(easements.get('count', 0))))
                rows.append(("Easements > Features", f"{easements.get('count', 0)} found"))

                # Show first 3 examples
                features = easements.get('features', [])[:3]
                for i, feat in enumerate(features, 1):
                    attrs = feat.get('attributes', {})
                    status_map = {'A': 'Active', 'I': 'Inactive'}
                    status = status_map.get(attrs.get('status', ''), attrs.get('status', 'N/A'))
                    pfi = attrs.get('pfi', 'N/A')
                    ufi = attrs.get('ufi', 'N/A')
                    rows.append((f"Example {i}", f"Status: {status}, PFI: {pfi}, UFI: {ufi}"))
            else:
                rows.append(("Easements > Available", "No"))

            rows.append(("", ""))

            # Heritage
            hazards = geo_layers.get('hazards', {})
            heritage = hazards.get('heritage', {})
            if heritage:
                heritage_available = heritage.get('available', False)
                heritage_method = heritage.get('method', 'N/A')
                rows.append(("Heritage > Available", "Yes" if heritage_available else "No"))
                if heritage_available:
                    rows.append(("Heritage > Detection Method", heritage_method))
            else:
                rows.append(("Heritage > Available", "No"))

            rows.append(("", ""))

        # Legal fields
        rows.append(("Legal > Isactiveproperty", "Yes" if legal.get('isActiveProperty') else "No"))

        legal_info = legal.get('legal', {})
        rows.append(("Legal > Legal > Dateissued", str(legal_info.get('dateIssued', 'N/A'))))
        rows.append(("Legal > Legal > Frontage", str(legal_info.get('frontage', 'N/A'))))
        rows.append(("Legal > Legal > Realpropertydescription", legal_info.get('realPropertyDescription', 'N/A')))

        # Parcels
        parcels = legal.get('parcels', [])
        if parcels:
            parcel = parcels[0]
            parcel_str = f"parcelId: {parcel.get('parcelId', 'N/A')}, landAuthority: {parcel.get('landAuthority', 'N/A')}"
            rows.append(("Legal > Parcels #1", parcel_str))

        # Title
        title = legal.get('title', {})
        rows.append(("Legal > Title > Titleindicator", title.get('titleIndicator', 'N/A')))

        rows.append(("", ""))

        # Property ID
        rows.append(("Property Id", str(report.get('metadata', {}).get('property_id', 'N/A'))))
        rows.append(("", ""))

        return rows

    def _extract_category_5_characteristics(self, report: Dict[str, Any], parcel_elev_orient: Optional[Dict]) -> List[Tuple[str, str]]:
        """Category 5: CHARACTERISTICS - Coverage 100%"""
        rows = [
            ("5. CHARACTERISTICS", ""),
            ("Coverage", "100% - Complete"),
            ("", ""),
        ]

        property_details = report.get('property_details', {})
        core_attrs = property_details.get('core_attributes', {})
        additional_attrs = property_details.get('additional_attributes', {})
        features = property_details.get('features', {})

        # CORE ATTRIBUTES sub-section
        rows.append(("CORE ATTRIBUTES", ""))
        rows.append(("Baths", str(core_attrs.get('baths', 'N/A'))))
        rows.append(("Beds", str(core_attrs.get('beds', 'N/A'))))
        rows.append(("Carspaces", str(core_attrs.get('carSpaces', 'N/A'))))
        rows.append(("Iscalculatedlandarea", "Yes" if core_attrs.get('isCalculatedLandArea') else "No"))
        rows.append(("Landarea", str(core_attrs.get('landArea', 'N/A'))))
        rows.append(("Landareasource", core_attrs.get('landAreaSource', 'N/A')))
        rows.append(("Lockupgarages", str(core_attrs.get('lockUpGarages', 'N/A'))))
        rows.append(("Propertysubtype", core_attrs.get('propertySubType', 'N/A')))
        rows.append(("Propertysubtypeshort", core_attrs.get('propertySubTypeShort', 'N/A')))
        rows.append(("Propertytype", core_attrs.get('propertyType', 'N/A')))
        rows.append(("", ""))

        # ADDITIONAL ATTRIBUTES sub-section
        rows.append(("ADDITIONAL ATTRIBUTES", ""))
        rows.append(("Airconditioned", "Yes" if additional_attrs.get('airConditioned') else "No"))
        rows.append(("Ductedheating", "Yes" if additional_attrs.get('ductedHeating') else "No"))
        rows.append(("Ensuite", str(additional_attrs.get('ensuite', 'N/A'))))
        rows.append(("Fireplace", "Yes" if additional_attrs.get('fireplace') else "No"))
        rows.append(("Floorarea", str(additional_attrs.get('floorArea', 'N/A'))))
        rows.append(("Roofmaterial", additional_attrs.get('roofMaterial', 'N/A')))
        rows.append(("Solarpower", "Yes" if additional_attrs.get('solarPower') else "No"))
        rows.append(("Wallmaterial", additional_attrs.get('wallMaterial', 'N/A')))
        rows.append(("Yearbuilt", str(additional_attrs.get('yearBuilt', 'N/A'))))
        rows.append(("", ""))

        # FEATURES sub-section
        rows.append(("FEATURES", ""))

        # Bullet point features
        feature_list = features.get('features', [])
        for feat in feature_list:
            rows.append(("•", feat))

        # Feature attributes
        feature_attrs = features.get('featureAttributes', [])
        for feat_attr in feature_attrs:
            name = feat_attr.get('name', 'Unknown')
            value = feat_attr.get('value', 'N/A')
            rows.append((name, str(value)))

        rows.append(("", ""))

        # SPATIAL sub-section
        if parcel_elev_orient:
            rows.append(("SPATIAL", ""))

            # Geometry basics
            rows.append(("Geometry Type", parcel_elev_orient.get('geometry_type', 'N/A')))

            spatial_ref = parcel_elev_orient.get('spatial_reference', {})
            rows.append(("Spatial Reference", f"WKID {spatial_ref.get('wkid', 'N/A')}"))

            parcel_attrs = parcel_elev_orient.get('parcel_attributes', {})
            rows.append(("Property Area", f"{parcel_attrs.get('property_m2', 'N/A')} m²"))
            rows.append(("Calculated Area", f"{parcel_attrs.get('st_area(geom)', 'N/A')} m²"))
            rows.append(("Perimeter", f"{parcel_attrs.get('st_perimeter(geom)', 'N/A')} m"))

            geometry = parcel_elev_orient.get('geometry', {})
            rings = geometry.get('rings', [])
            rows.append(("Polygon Rings", str(len(rings))))
            if rings:
                rows.append(("Vertices", str(len(rings[0]))))

            rows.append(("", ""))

            # Raw Geometry Coordinates (CONSOLIDATED)
            rows.append(("Raw Geometry Coordinates (Web Mercator)", ""))
            if rings:
                ring = rings[0]
                rows.append(("Ring 1", f"{len(ring)} vertices"))

                # Consolidated X coordinates
                x_coords = [str(coord[0]) for coord in ring]
                rows.append(("X Coordinates", ", ".join(x_coords)))

                # Consolidated Y coordinates
                y_coords = [str(coord[1]) for coord in ring]
                rows.append(("Y Coordinates", ", ".join(y_coords)))

            rows.append(("", ""))

            # Elevation
            elev_analysis = parcel_elev_orient.get('elevation_analysis', {})
            if elev_analysis:
                rows.append(("Elevation", ""))

                elev_stats = elev_analysis.get('elevation_statistics', {})
                rows.append(("Min Elevation", f"{elev_stats.get('min_elevation_m', 'N/A')}m"))
                rows.append(("Max Elevation", f"{elev_stats.get('max_elevation_m', 'N/A')}m"))
                rows.append(("Avg Elevation", f"{elev_stats.get('avg_elevation_m', 'N/A')}m"))
                rows.append(("Elevation Range", f"{elev_stats.get('elevation_range_m', 'N/A')}m"))

                slope_analysis = elev_analysis.get('slope_analysis', {})
                max_slope = slope_analysis.get('max_slope', {})
                rows.append(("Max Slope", f"{max_slope.get('slope_degrees', 'N/A')}° ({max_slope.get('slope_percent', 'N/A')}%)"))
                rows.append(("Avg Slope", f"{slope_analysis.get('avg_slope_degrees', 'N/A')}° ({slope_analysis.get('avg_slope_percent', 'N/A')}%)"))

                rows.append(("", ""))

                # Center Point
                center_elev = elev_analysis.get('center_elevation', {})
                rows.append(("Center Point (WGS84)", ""))
                rows.append(("Latitude", str(center_elev.get('lat', 'N/A'))))
                rows.append(("Longitude", str(center_elev.get('lon', 'N/A'))))
                rows.append(("Elevation", f"{center_elev.get('elevation_m', 'N/A')}m"))
                rows.append(("Resolution", f"{center_elev.get('resolution_m', 'N/A')}m"))

                rows.append(("", ""))

                # Vertex Coordinates (CONSOLIDATED)
                vertex_elevations = elev_analysis.get('vertex_elevations', [])
                if vertex_elevations:
                    rows.append(("Vertex Coordinates (WGS84 + Elevation)", ""))
                    rows.append(("Total Vertices", str(len(vertex_elevations))))

                    # Consolidated latitudes
                    lats = [f"{v['lat']:.8f}" for v in vertex_elevations]
                    rows.append(("Latitudes", ", ".join(lats)))

                    # Consolidated longitudes
                    lons = [f"{v['lon']:.8f}" for v in vertex_elevations]
                    rows.append(("Longitudes", ", ".join(lons)))

                    # Consolidated elevations
                    elevs = [f"{v['elevation_m']:.2f}m" for v in vertex_elevations]
                    rows.append(("Elevations", ", ".join(elevs)))

                rows.append(("", ""))

            # Orientation
            orient_analysis = parcel_elev_orient.get('orientation_analysis', {})
            if orient_analysis:
                rows.append(("Orientation", ""))

                frontage_edge = orient_analysis.get('frontage_edge', {})
                rows.append(("Frontage Length", f"{frontage_edge.get('length_m', 'N/A')}m"))

                frontage_orient = orient_analysis.get('frontage_orientation', {})
                rows.append(("Frontage Direction", f"{frontage_orient.get('cardinal_direction', 'N/A')} ({frontage_orient.get('bearing_degrees', 'N/A')}°)"))

                property_orient = orient_analysis.get('property_orientation', {})
                rows.append(("Property Faces", f"{property_orient.get('cardinal_direction', 'N/A')} ({property_orient.get('bearing_degrees', 'N/A')}°)"))

                rows.append(("", ""))

                # Frontage Edge Vertices (NOT CONSOLIDATED)
                rows.append(("Frontage Edge Vertices", ""))
                vertex_1 = frontage_edge.get('vertex_1', {})
                rows.append(("Vertex 1 (WGS84)", ""))
                rows.append(("Latitude", str(vertex_1.get('lat', 'N/A'))))
                rows.append(("Longitude", str(vertex_1.get('lon', 'N/A'))))

                vertex_2 = frontage_edge.get('vertex_2', {})
                rows.append(("Vertex 2 (WGS84)", ""))
                rows.append(("Latitude", str(vertex_2.get('lat', 'N/A'))))
                rows.append(("Longitude", str(vertex_2.get('lon', 'N/A'))))

                rows.append(("", ""))

                # Street Location
                street_loc = orient_analysis.get('street_location', {})
                rows.append(("Street Location (WGS84)", ""))
                rows.append(("Latitude", str(street_loc.get('lat', 'N/A'))))
                rows.append(("Longitude", str(street_loc.get('lon', 'N/A'))))
                rows.append(("Detection Method", street_loc.get('method', 'N/A')))

            rows.append(("", ""))

        return rows

    def _extract_category_6_imagery(self, property_images: Optional[Dict[str, Any]]) -> List[Tuple[str, str]]:
        """Category 6: IMAGERY - Property Images"""
        rows = [
            ("6. IMAGERY", ""),
            ("Coverage", "100% - Complete image metadata"),
            ("", ""),
        ]

        if not property_images:
            rows.append(("Status", "No image data available"))
            rows.append(("", ""))
            return rows

        metadata = property_images.get('metadata', {})
        summary = property_images.get('summary', {})

        # Check for errors
        if metadata.get('status') == 'error':
            rows.append(("Status", "Error retrieving images"))
            rows.append(("Error", str(property_images.get('error', 'Unknown error'))))
            rows.append(("", ""))
            return rows

        # Image counts
        rows.append(("IMAGE SUMMARY", ""))
        rows.append(("Total Images", str(summary.get('total_images', 0))))
        rows.append(("Has Default Image", "Yes" if summary.get('has_default_image') else "No"))
        rows.append(("Secondary Images", str(summary.get('secondary_images_count', 0))))
        rows.append(("Floor Plan Images", str(summary.get('floor_plan_images_count', 0))))
        rows.append(("", ""))

        # Image types
        image_types = summary.get('image_types', [])
        if image_types:
            rows.append(("Image Types", ", ".join(image_types)))
            rows.append(("", ""))

        # Available sizes
        available_sizes = summary.get('available_sizes', [])
        if available_sizes:
            rows.append(("AVAILABLE SIZES", ""))
            for size in available_sizes:
                rows.append(("", size))
            rows.append(("", ""))

        # Temporal coverage
        if summary.get('oldest_scan_date'):
            rows.append(("TEMPORAL COVERAGE", ""))
            rows.append(("Oldest Scan Date", summary.get('oldest_scan_date', 'N/A')))
            rows.append(("Newest Scan Date", summary.get('newest_scan_date', 'N/A')))
            rows.append(("Unique Scan Dates", str(summary.get('unique_scan_dates', 0))))

            if summary.get('temporal_span_years') is not None:
                span_years = summary.get('temporal_span_years')
                span_days = summary.get('temporal_span_days', 0)
                rows.append(("Time Span", f"{span_years} years ({span_days} days)"))
            rows.append(("", ""))

        # Distribution by year
        images_by_year = summary.get('images_by_year', {})
        if images_by_year:
            rows.append(("DISTRIBUTION BY YEAR", ""))
            for year, count in images_by_year.items():
                rows.append((year, f"{count} images"))
            rows.append(("", ""))

        # Digital asset types
        asset_type_totals = summary.get('digital_asset_type_totals', {})
        if asset_type_totals:
            rows.append(("DIGITAL ASSET TYPES", ""))
            for asset_type, count in asset_type_totals.items():
                rows.append((asset_type, str(count)))
            rows.append(("", ""))

        # Distribution by type (enhanced)
        distribution_by_type = summary.get('distribution_by_type', {})
        if distribution_by_type:
            rows.append(("DISTRIBUTION BY TYPE", ""))
            for img_type, stats in distribution_by_type.items():
                if stats.get('count', 0) > 0:
                    rows.append((f"{img_type.title()} Images", ""))
                    rows.append(("Count", str(stats.get('count', 0))))
                    rows.append(("Unique Dates", str(stats.get('unique_dates', 0))))
                    if stats.get('oldest_date'):
                        date_range = f"{stats.get('oldest_date')} to {stats.get('newest_date')}"
                        rows.append(("Date Range", date_range))
                    rows.append(("", ""))

        # Images by date (top 5)
        images_by_date = summary.get('images_by_date', {})
        if images_by_date:
            rows.append(("TOP DATES WITH MOST IMAGES", ""))
            # Sort by total count, descending
            sorted_dates = sorted(images_by_date.items(), key=lambda x: x[1]['total'], reverse=True)[:5]
            for date, counts in sorted_dates:
                breakdown = []
                if counts.get('default', 0) > 0:
                    breakdown.append(f"{counts['default']} default")
                if counts.get('secondary', 0) > 0:
                    breakdown.append(f"{counts['secondary']} secondary")
                if counts.get('floor_plan', 0) > 0:
                    breakdown.append(f"{counts['floor_plan']} floor_plan")
                breakdown_str = ", ".join(breakdown) if breakdown else "0"
                rows.append((date, f"{counts['total']} images ({breakdown_str})"))
            rows.append(("", ""))

        return rows

    def _extract_category_7_occupancy(self, report: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Category 7: OCCUPANCY - Coverage 70%"""
        rows = [
            ("7. OCCUPANCY", ""),
            ("Coverage", "70% - Partial coverage"),
            ("", ""),
        ]

        property_details = report.get('property_details', {})
        occupancy = property_details.get('occupancy', {})
        site = property_details.get('site', {})

        rows.append(("Occupancy > Confidencescore", occupancy.get('confidenceScore', 'N/A')))
        rows.append(("Occupancy > Isactiveproperty", "Yes" if occupancy.get('isActiveProperty') else "No"))
        rows.append(("Occupancy > Occupancytype", occupancy.get('occupancyType', 'N/A')))
        rows.append(("Site > Isactiveproperty", "Yes" if site.get('isActiveProperty') else "No"))
        rows.append(("Site > Landuseprimary", site.get('landUsePrimary', 'N/A')))

        site_values = site.get('siteValueList', [])
        rows.append(("Site > Sitevaluelist", "None" if not site_values else f"{len(site_values)} values"))

        rows.append(("Site > Zonecodelocal", site.get('zoneCodeLocal', 'N/A')))
        rows.append(("Site > Zonedescriptionlocal", site.get('zoneDescriptionLocal', 'N/A')))
        rows.append(("", ""))

        return rows

    def _extract_category_8_local_market(self, report: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Category 8: LOCAL MARKET - Coverage 95%"""
        rows = [
            ("8. LOCAL MARKET", ""),
            ("Coverage", "95% - Excellent coverage"),
            ("", ""),
        ]

        market_metrics = report.get('market_metrics_summary', {})
        if market_metrics and not market_metrics.get('error'):
            availability = market_metrics.get('availability', {})

            rows.append(("MARKET METRICS AVAILABILITY", ""))
            rows.append(("", ""))

            # Show each metric with checkmark or X
            for metric_name, metric_info in availability.items():
                description = metric_info.get('description', metric_name.replace('_', ' ').title())

                if metric_info.get('available'):
                    data_points = metric_info.get('data_points', 0)
                    interval = metric_info.get('interval', 'N/A')
                    date_range = metric_info.get('date_range', 'N/A')

                    rows.append((f"✓ {description}", ""))
                    rows.append(("Data Points", f"{data_points} ({interval})"))
                    rows.append(("Period", date_range))

                    first_val = metric_info.get('first_value')
                    last_val = metric_info.get('last_value')
                    growth = metric_info.get('growth_percent')

                    if first_val is not None:
                        if 'price' in metric_name or 'value' in metric_name or 'rent' in metric_name:
                            rows.append(("First Value", self._format_currency(first_val)))
                            if last_val is not None:
                                rows.append(("Latest Value", self._format_currency(last_val)))
                        else:
                            rows.append(("First Value", str(first_val)))
                            if last_val is not None:
                                rows.append(("Latest Value", str(last_val)))

                    if growth is not None:
                        rows.append(("Growth", f"{growth:+.1f}%"))
                    elif 'latest_value' in metric_info:
                        rows.append(("Latest Value", f"{metric_info['latest_value']:.2f}%"))
                else:
                    reason = metric_info.get('reason', 'No data returned from API')
                    rows.append((f"✗ {description}", reason))

                rows.append(("", ""))

        return rows

    def _extract_category_9_transaction_history(self, report: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Category 9: TRANSACTION HISTORY - Coverage 100%"""
        rows = [
            ("9. TRANSACTION HISTORY", ""),
            ("Coverage", "100% - Complete"),
            ("", ""),
        ]

        property_details = report.get('property_details', {})
        last_sale = property_details.get('last_sale', {})
        sales_history = property_details.get('sales_history', {})

        # Last Sale fields
        if last_sale:
            rows.append(("Last Sale > Isactiveproperty", "Yes" if last_sale.get('isActiveProperty') else "No"))

            last_sale_data = last_sale.get('lastSale', {})
            if last_sale_data:
                rows.append(("Last Sale > Lastsale > Agencyname", last_sale_data.get('agencyName', 'N/A')))
                rows.append(("Last Sale > Lastsale > Agentname", last_sale_data.get('agentName', 'N/A')))
                rows.append(("Last Sale > Lastsale > Contractdate", last_sale_data.get('contractDate', 'N/A')))
                rows.append(("Last Sale > Lastsale > Isagentsadvice", "Yes" if last_sale_data.get('isAgentsAdvice') else "No"))
                rows.append(("Last Sale > Lastsale > Isarmslength", "Yes" if last_sale_data.get('isArmsLength') else "No"))
                rows.append(("Last Sale > Lastsale > Isderivedagency", "Yes" if last_sale_data.get('isDerivedAgency') else "No"))
                rows.append(("Last Sale > Lastsale > Isderivedagent", "Yes" if last_sale_data.get('isDerivedAgent') else "No"))
                rows.append(("Last Sale > Lastsale > Ismultisale", "Yes" if last_sale_data.get('isMultiSale') else "No"))
                rows.append(("Last Sale > Lastsale > Ispricewithheld", "Yes" if last_sale_data.get('isPriceWithheld') else "No"))
                rows.append(("Last Sale > Lastsale > Isrearecentsale", "Yes" if last_sale_data.get('isReaRecentSale') else "No"))
                rows.append(("Last Sale > Lastsale > Isstandardtransfer", "Yes" if last_sale_data.get('isStandardTransfer') else "No"))
                rows.append(("Last Sale > Lastsale > Landuseprimary", last_sale_data.get('landUsePrimary', 'N/A')))
                rows.append(("Last Sale > Lastsale > Price", self._format_currency(last_sale_data.get('price', 0))))
                rows.append(("Last Sale > Lastsale > Salemethod", last_sale_data.get('saleMethod', 'N/A')))
                rows.append(("Last Sale > Lastsale > Settlementdate", last_sale_data.get('settlementDate', 'N/A')))
                rows.append(("Last Sale > Lastsale > Transferid", str(last_sale_data.get('transferId', 'N/A'))))
                rows.append(("Last Sale > Lastsale > Type", last_sale_data.get('type', 'N/A')))
                rows.append(("Last Sale > Lastsale > Zonecodelocal", last_sale_data.get('zoneCodeLocal', 'N/A')))
                rows.append(("Last Sale > Lastsale > Zonedescriptionlocal", last_sale_data.get('zoneDescriptionLocal', 'N/A')))

        rows.append(("", ""))

        # Sales History
        if sales_history:
            rows.append(("Sales History > Isactiveproperty", "Yes" if sales_history.get('isActiveProperty') else "No"))

            sale_list = sales_history.get('saleList', [])
            for i, sale in enumerate(sale_list[:2], 1):  # First 2
                sale_str = f"type: {sale.get('type', 'N/A')}, Price: {self._format_currency(sale.get('price', 0))}, contractDate: {sale.get('contractDate', 'N/A')}"
                rows.append((f"Sales History > Salelist #{i}", sale_str))

        rows.append(("", ""))

        return rows

    def _extract_category_10_campaigns(self, report: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Category 10: CAMPAIGNS - Coverage 100%"""
        rows = [
            ("10. CAMPAIGNS", ""),
            ("Coverage", "100% - Complete"),
            ("", ""),
        ]

        property_details = report.get('property_details', {})
        sales_otm = property_details.get('sales_otm', {})
        sales_history = property_details.get('sales_history', {})
        rentals_otm = property_details.get('rentals_otm', {})

        # CAMPAIGN TIMELINE sub-section
        rows.append(("CAMPAIGN TIMELINE", ""))

        # Collect all campaign events
        events = []

        # From sales campaigns
        for_sale_campaign = sales_otm.get('forSalePropertyCampaign', {})
        campaigns = for_sale_campaign.get('campaigns', [])
        for campaign in campaigns:
            if campaign.get('fromDate'):
                events.append(("■ Forsale Campaignstart", campaign['fromDate']))
            if campaign.get('toDate'):
                events.append(("■ Forsale Campaignend", campaign['toDate']))

        # From rentals campaigns
        for_rent_campaign = rentals_otm.get('forRentPropertyCampaign', {})
        if for_rent_campaign:
            rent_campaigns = for_rent_campaign.get('campaigns', [])
            for campaign in rent_campaigns:
                if campaign.get('fromDate'):
                    events.append(("■ Forrent Campaignstart", campaign['fromDate']))
                if campaign.get('toDate'):
                    events.append(("■ Forrent Campaignend", campaign['toDate']))

        # From sales history
        sale_list = sales_history.get('saleList', [])
        for sale in sale_list:
            if sale.get('contractDate'):
                events.append(("■ Sale", sale['contractDate']))

        rows.append(("Total Events", str(len(events))))
        rows.extend(events)
        rows.append(("", ""))

        # ADVERTISEMENT EXTRACTS sub-section
        advertisements_data = property_details.get('advertisements', {})
        ad_list = []

        # Check if advertisements is a dict with advertisementList
        if isinstance(advertisements_data, dict):
            ad_list = advertisements_data.get('advertisementList', [])
        elif isinstance(advertisements_data, list):
            ad_list = advertisements_data

        rows.append(("ADVERTISEMENT EXTRACTS", ""))
        rows.append(("Total Advertisements", str(len(ad_list))))

        for i, ad in enumerate(ad_list, 1):
            rows.append(("", ""))
            rows.append((f"Advertisement #{i}", ""))
            rows.append(("Date", ad.get('date', 'N/A')))
            rows.append(("Type", ad.get('advertisementType', ad.get('type', 'N/A'))))
            price_desc = ad.get('priceDescription', '')
            if not price_desc and 'price' in ad:
                price_desc = f"${ad.get('price', 'N/A')} {ad.get('period', '')}"
            rows.append(("Price", price_desc if price_desc else 'N/A'))
            rows.append(("Method", ad.get('method', 'N/A')))
            description = ad.get('advertisementDescription', ad.get('description', 'N/A'))
            if len(description) > 100:
                description = description[:100] + "..."
            rows.append(("Description", description))

        rows.append(("", ""))

        return rows

    def _extract_category_11_sales_evidence(self, comparable_sales: Optional[Dict]) -> List[Tuple[str, str]]:
        """Category 11: SALES EVIDENCE - Coverage 100%"""
        rows = [
            ("11. SALES EVIDENCE", ""),
            ("Coverage", "100% - Complete"),
            ("", ""),
        ]

        if not comparable_sales:
            rows.append(("[GAP] Note", "Comparable sales data not available"))
            rows.append(("", ""))
            return rows

        rows.append(("[GAP] Note", "Comparable sales generated from radius search"))
        rows.append(("", ""))

        metadata = comparable_sales.get('metadata', {})
        statistics = comparable_sales.get('statistics', {})
        comp_list = comparable_sales.get('comparable_sales', [])

        # COMPARABLE SALES SUMMARY sub-section
        rows.append(("COMPARABLE SALES SUMMARY", ""))
        rows.append(("Total Comparables", f"{metadata.get('total_comparables', len(comp_list))} properties"))
        rows.append(("", ""))

        # Price Statistics
        price_stats = statistics.get('price_statistics', {})
        rows.append(("Price Statistics", ""))
        rows.append(("Median Price", self._format_currency(price_stats.get('median', 0))))
        rows.append(("Mean Price", self._format_currency(price_stats.get('mean', 0))))
        rows.append(("Price Range", f"{self._format_currency(price_stats.get('min', 0))} - {self._format_currency(price_stats.get('max', 0))}"))
        rows.append(("", ""))

        # Sale Date Range
        date_range = statistics.get('date_range', {})
        recent_25 = statistics.get('recent_25_date_range', {})
        recent_50 = statistics.get('recent_50_date_range', {})

        rows.append(("Sale Date Range", ""))
        rows.append(("Overall Period", f"{date_range.get('earliest', 'N/A')} to {date_range.get('latest', 'N/A')}"))
        rows.append(("Recent 25 Period", f"{recent_25.get('earliest', 'N/A')} to {recent_25.get('latest', 'N/A')} ({recent_25.get('count', 0)} sales)"))
        rows.append(("Recent 50 Period", f"{recent_50.get('earliest', 'N/A')} to {recent_50.get('latest', 'N/A')} ({recent_50.get('count', 0)} sales)"))
        rows.append(("", ""))

        # Distance Distribution
        dist_dist = statistics.get('distance_distribution', {})
        rows.append(("Distance Distribution", ""))
        rows.append(("Within 500m", f"{dist_dist.get('within_500m', 0)} properties"))
        rows.append(("Within 1km", f"{dist_dist.get('within_1km', 0)} properties"))
        rows.append(("Within 3km", f"{dist_dist.get('within_3km', 0)} properties"))
        rows.append(("", ""))

        # Property Characteristics
        prop_chars = statistics.get('property_characteristics', {})
        rows.append(("Property Characteristics", ""))

        # Property Types
        prop_types = prop_chars.get('propertyType', {}).get('distribution', {})
        if prop_types:
            types_str = ", ".join([f"{count} {ptype}" for ptype, count in prop_types.items()])
            rows.append(("Property Types", types_str))

        # Bedrooms
        beds_dist = prop_chars.get('beds', {}).get('distribution', {})
        if beds_dist:
            beds_str = ", ".join([f"{count}×{beds}bd" for beds, count in sorted(beds_dist.items())])
            rows.append(("Bedrooms", beds_str))

        # Bathrooms
        baths_dist = prop_chars.get('baths', {}).get('distribution', {})
        if baths_dist:
            baths_str = ", ".join([f"{count}×{baths}ba" for baths, count in sorted(baths_dist.items())])
            rows.append(("Bathrooms", baths_str))

        rows.append(("", ""))

        # INDIVIDUAL COMPARABLES sub-section
        rows.append(("INDIVIDUAL COMPARABLES", ""))
        rows.append(("", ""))

        # List ALL comparables
        for i, comp in enumerate(comp_list, 1):
            rows.append((f"Comparable #{i}", ""))
            rows.append(("Address", comp.get('address', 'N/A')))
            rows.append(("Sale Price", self._format_currency(comp.get('salePrice', 0))))

            # Property format: "4bd / 2ba / 2car | HOUSE"
            beds = comp.get('beds', 'N/A')
            baths = comp.get('baths', 'N/A')
            cars = comp.get('carSpaces', 'N/A')
            ptype = comp.get('propertyType', 'N/A')
            property_str = f"{beds}bd / {baths}ba / {cars}car | {ptype}"
            rows.append(("Property", property_str))

            rows.append(("Land Area", f"{comp.get('landArea', 'N/A')} m²"))
            rows.append(("Distance", f"{comp.get('distance', 'N/A')} km"))
            rows.append(("Sale Date", comp.get('lastSaleDate', 'N/A')))
            rows.append(("", ""))

        # SEARCH PARAMETERS sub-section
        search_params = metadata.get('search_parameters', {})
        rows.append(("SEARCH PARAMETERS", ""))
        rows.append(("Search Radius", f"{search_params.get('radius', metadata.get('default_radius_km', 'N/A'))} km"))
        rows.append(("", ""))

        return rows

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

    def generate_pdf(self, report: Dict[str, Any], output_path: str, ultra_comprehensive: bool = False, categorized: bool = False):
        """Generate PDF report from property data

        Args:
            report: Comprehensive property report dictionary
            output_path: Path to save PDF
            ultra_comprehensive: If True, uses flatten_json_recursive to extract ALL fields
            categorized: If True, uses 10-category Pre-Qualification Data Collection structure
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
        if categorized:
            title_text = f"Pre-Qualification - Data Collection Example"
        else:
            title_text = f"Property Data Report"
        title = Paragraph(title_text, self.title_style)
        story.append(title)

        # Subtitle with address
        address = metadata.get('address', 'N/A')
        subtitle_style = ParagraphStyle('Subtitle', parent=self.normal_style, alignment=TA_CENTER, fontSize=8)
        subtitle = Paragraph(f"<b>{address}</b>", subtitle_style)
        story.append(subtitle)
        story.append(Spacer(1, 0.1*inch))

        # Extract data - choose extraction method based on flags
        if categorized:
            data_rows = self.extract_data_categorized(report)
        elif ultra_comprehensive:
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

    parser.add_argument(
        '--categorized',
        action='store_true',
        help='Use 10-category Pre-Qualification Data Collection structure (matches prequal-concept.txt)'
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
        generator.generate_pdf(
            report,
            output_pdf,
            ultra_comprehensive=args.ultra_comprehensive,
            categorized=args.categorized
        )

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
