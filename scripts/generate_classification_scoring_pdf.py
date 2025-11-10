#!/usr/bin/env python3
"""
Generate Classification & Scoring PDF Report

Creates a professional PDF report from classification and scoring data.
Mirrors the structure of the Data Collection PDF but displays scores,
classifications, and risk assessments instead of raw data.

Usage:
    # Generate from classification_scoring JSON
    python3 scripts/generate_classification_scoring_pdf.py \
        --input data/property_reports/13683380_classification_scoring.json

    # Custom output
    python3 scripts/generate_classification_scoring_pdf.py \
        --input data/property_reports/13683380_classification_scoring.json \
        --output reports/scoring_report.pdf

Author: ARMATech Classification & Scoring System
Date: 2025-11-10
Version: 1.0
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️  Warning: reportlab not installed. Install with: pip install reportlab", file=sys.stderr)


class ClassificationScoringPDFGenerator:
    """Generate PDF reports from classification and scoring data"""

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

    def extract_imagery_classification_section(self, report: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Extract imagery classification data for PDF"""
        rows = []
        imagery = report.get('imagery_classification', {})

        rows.append(("1. IMAGERY CLASSIFICATION & QUALITY SCORES", ""))
        rows.append(("", ""))

        # Summary
        summary = imagery.get('summary', {})
        rows.append(("Coverage", f"{summary.get('images_processed', 0)} images processed"))
        rows.append(("Processing Method", summary.get('processing_method', 'N/A')))
        rows.append(("", ""))

        # Layer 1 Tagging
        layer_1 = imagery.get('layer_1_tagging', {})
        if layer_1:
            rows.append(("LAYER 1 - HIGH-LEVEL CLASSIFICATION", ""))
            categories = layer_1.get('categories', {})
            for cat_name, cat_data in categories.items():
                if cat_data.get('count', 0) > 0:
                    rows.append((
                        f"{cat_name.title()}",
                        f"{cat_data['count']} images ({cat_data['percentage']}%)"
                    ))
            rows.append(("", ""))

        # Layer 2 Tagging
        layer_2 = imagery.get('layer_2_tagging', {})
        if layer_2:
            rows.append(("LAYER 2 - ROOM CLASSIFICATION", ""))

            # Indoor categories
            indoor = layer_2.get('indoor_categories', {})
            if indoor:
                rows.append(("Indoor Rooms", ""))
                for room, data in indoor.items():
                    if data.get('count', 0) > 0:
                        eligible = " ✓ L3" if data.get('eligible_for_layer_3') else ""
                        rows.append((
                            f"  {room.replace('_', ' ').title()}",
                            f"{data['count']} images ({data['percentage']:.1f}%){eligible}"
                        ))

            # Outdoor categories
            outdoor = layer_2.get('outdoor_categories', {})
            if outdoor:
                rows.append(("Outdoor Areas", ""))
                for area, data in outdoor.items():
                    if data.get('count', 0) > 0:
                        eligible = " ✓ L3" if data.get('eligible_for_layer_3') else ""
                        rows.append((
                            f"  {area.replace('_', ' ').title()}",
                            f"{data['count']} images ({data['percentage']:.1f}%){eligible}"
                        ))
            rows.append(("", ""))

        # Layer 3 Quality Scores
        layer_3 = imagery.get('layer_3_quality_scores', {})
        if layer_3:
            rows.append(("LAYER 3 - QUALITY GRADING (1-5 SCALE)", ""))

            # Kitchen score
            kitchen = layer_3.get('kitchen', {})
            if kitchen:
                rows.append(("Kitchen Grade", f"{kitchen.get('overall_grade', 0):.1f}/5.0 ({kitchen.get('overall_grade_label', 'N/A')})"))
                dim_scores = kitchen.get('dimension_scores', {})
                for dim, score in dim_scores.items():
                    rows.append((f"  {dim.replace('_', ' ').title()}", f"{score:.1f}/5.0"))
                rows.append(("  Confidence", f"{kitchen.get('confidence', 0):.0%}"))
                rows.append(("", ""))

            # Wet rooms score
            wet_rooms = layer_3.get('wet_rooms', {})
            if wet_rooms:
                rows.append(("Wet Rooms Grade", f"{wet_rooms.get('overall_grade', 0):.1f}/5.0 ({wet_rooms.get('overall_grade_label', 'N/A')})"))
                dim_scores = wet_rooms.get('dimension_scores', {})
                for dim, score in dim_scores.items():
                    rows.append((f"  {dim.replace('_', ' ').title()}", f"{score:.1f}/5.0"))
                rows.append(("  Confidence", f"{wet_rooms.get('confidence', 0):.0%}"))
                rows.append(("", ""))

            # Frontage score
            frontage = layer_3.get('frontage', {})
            if frontage:
                rows.append(("Street Appeal Grade", f"{frontage.get('overall_grade', 0):.1f}/5.0 ({frontage.get('overall_grade_label', 'N/A')})"))
                dim_scores = frontage.get('dimension_scores', {})
                for dim, score in dim_scores.items():
                    rows.append((f"  {dim.replace('_', ' ').title()}", f"{score:.1f}/5.0"))
                rows.append(("  Confidence", f"{frontage.get('confidence', 0):.0%}"))
                rows.append(("", ""))

        # Completeness Score
        completeness = imagery.get('completeness_score', {})
        if completeness:
            rows.append(("COMPLETENESS SCORE", ""))
            rows.append(("Overall Score", f"{completeness.get('overall_score', 0)}/100 ({completeness.get('overall_label', 'N/A')})"))
            factors = completeness.get('factors', {})
            for factor_name, factor_data in factors.items():
                rows.append((
                    f"  {factor_name.replace('_', ' ').title()}",
                    f"{factor_data.get('score', 0)}/100 - {factor_data.get('description', '')}"
                ))
            if completeness.get('recommendation'):
                rows.append(("  Recommendation", completeness['recommendation']))

        rows.append(("", ""))
        return rows

    def extract_market_risk_scores_section(self, report: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Extract market risk scores for PDF"""
        rows = []
        market = report.get('market_risk_scores', {})

        rows.append(("2. MARKET RISK SCORES", ""))
        rows.append(("", ""))

        # Summary
        summary = market.get('summary', {})
        rows.append(("Coverage", "100% - Complete"))
        rows.append(("", ""))

        rows.append(("OVERALL MARKET ASSESSMENT", ""))
        rows.append(("Market Risk Level", summary.get('overall_market_risk', 'N/A')))
        rows.append(("Market Risk Score", f"{summary.get('overall_market_risk_score', 0):.1f}/10.0"))
        rows.append(("Analysis Period", summary.get('analysis_period', 'N/A')))
        rows.append(("Confidence", f"{summary.get('confidence', 0):.0%}"))
        rows.append(("", ""))

        # Market Trends
        trends = market.get('market_trends', {})
        if trends:
            rows.append(("MARKET TRENDS", ""))
            rows.append(("Trend Score", f"{trends.get('score', 0):.1f}/10.0 ({trends.get('score_label', 'N/A')})"))
            rows.append(("Rating", trends.get('rating', 'N/A')))

            factors = trends.get('factors', {})
            if 'price_movement' in factors:
                pm = factors['price_movement']
                rows.append(("Price Movement", f"{pm.get('direction', 'N/A')} (+{pm.get('growth_rate', 0):.1f}%)"))
                rows.append(("  Period", pm.get('period', 'N/A')))

            if 'volatility' in factors:
                vol = factors['volatility']
                rows.append(("Volatility", vol.get('level', 'N/A')))

            if 'momentum' in factors:
                mom = factors['momentum']
                rows.append(("Current Momentum", mom.get('current', 'N/A')))

            rows.append(("", ""))

        # Local Liquidity
        liquidity = market.get('local_liquidity', {})
        if liquidity:
            rows.append(("LOCAL LIQUIDITY", ""))
            rows.append(("Liquidity Score", f"{liquidity.get('score', 0):.1f}/10.0 ({liquidity.get('score_label', 'N/A')})"))
            rows.append(("Rating", liquidity.get('rating', 'N/A')))

            factors = liquidity.get('factors', {})
            if 'sales_density' in factors:
                sd = factors['sales_density']
                rows.append(("Sales Density Score", f"{sd.get('score', 0):.1f}/10.0"))
                rows.append(("  Recent Sales", str(sd.get('recent_sales_count', 0))))
                rows.append(("  Period", sd.get('period', 'N/A')))

            rows.append(("Summary", liquidity.get('summary', '')))
            rows.append(("", ""))

        # Uniqueness Score
        uniqueness = market.get('uniqueness_score', {})
        if uniqueness:
            rows.append(("PROPERTY UNIQUENESS", ""))
            rows.append(("Uniqueness Score", f"{uniqueness.get('score', 0):.1f}/10.0 ({uniqueness.get('score_label', 'N/A')})"))
            rows.append(("Rating", uniqueness.get('rating', 'N/A')))
            rows.append(("Market Percentile", f"{uniqueness.get('percentile', 0)}th percentile"))

            factors = uniqueness.get('factors', {})
            for factor_name, factor_data in factors.items():
                rows.append((
                    f"  {factor_name.replace('_', ' ').title()}",
                    f"{factor_data.get('score', 0):.1f}/10.0 - {factor_data.get('description', '')}"
                ))

            rows.append(("Summary", uniqueness.get('summary', '')))
            if uniqueness.get('valuation_impact'):
                rows.append(("Valuation Impact", uniqueness['valuation_impact']))

        rows.append(("", ""))
        return rows

    def extract_risk_flags_section(self, report: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Extract property risk flags for PDF"""
        rows = []
        risk_flags = report.get('property_risk_flags', {})

        rows.append(("3. PROPERTY RISK FLAGS", ""))
        rows.append(("", ""))

        # Summary
        summary = risk_flags.get('summary', {})
        rows.append(("RISK FLAGS SUMMARY", ""))
        rows.append(("Total Flags Detected", str(summary.get('total_flags', 0))))
        rows.append(("  High Priority", str(summary.get('high_priority_flags', 0))))
        rows.append(("  Medium Priority", str(summary.get('medium_priority_flags', 0))))
        rows.append(("  Low Priority", str(summary.get('low_priority_flags', 0))))
        rows.append(("", ""))

        # NLP Detection Results
        nlp = risk_flags.get('nlp_detection', {})
        if nlp:
            rows.append(("NLP DETECTION RESULTS", ""))
            rows.append(("Analysis Date", nlp.get('analysis_date', 'N/A')))
            rows.append(("", ""))

            # Check each flag type
            flag_types = ['acreages', 'display_home', 'holiday_rental', 'serviced_apartments',
                         'dual_occupancy', 'business_use']

            for flag_type in flag_types:
                flag_data = nlp.get(flag_type, {})
                if flag_data:
                    flag_name = flag_type.replace('_', ' ').title()
                    detected = flag_data.get('detected', False)
                    status_symbol = "⚠️ " if detected else "✓ "

                    rows.append((f"{flag_name}", f"{status_symbol}{flag_data.get('flag_status', 'N/A')}"))

                    if detected:
                        if flag_data.get('priority'):
                            rows.append(("  Priority", flag_data['priority']))
                        if flag_data.get('confidence'):
                            rows.append(("  Confidence", f"{flag_data['confidence']:.0%}"))
                        if flag_data.get('description'):
                            rows.append(("  Description", flag_data['description']))
                        if flag_data.get('valuation_impact'):
                            rows.append(("  Valuation Impact", flag_data['valuation_impact']))
                        if flag_data.get('recommendation'):
                            rows.append(("  Recommendation", flag_data['recommendation']))
                        rows.append(("", ""))

        return rows

    def extract_valuation_assessment_section(self, report: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Extract valuation risk assessment for PDF"""
        rows = []
        assessment = report.get('valuation_risk_assessment', {})

        rows.append(("4. VALUATION RISK ASSESSMENT", ""))
        rows.append(("", ""))

        # Overall Assessment
        overall = assessment.get('overall_assessment', {})
        if overall:
            rows.append(("OVERALL ASSESSMENT", ""))
            rows.append(("Risk Rating", overall.get('risk_rating', 'N/A')))
            rows.append(("Risk Score", f"{overall.get('risk_score', 0):.1f}/10.0"))
            rows.append(("Confidence Score", f"{overall.get('confidence_score', 0)}%"))
            rows.append(("Confidence Label", overall.get('confidence_label', 'N/A')))
            rows.append(("Recommendation", overall.get('recommendation', '')))
            rows.append(("", ""))

        # Risk Factors
        risk_factors = assessment.get('risk_factors', {})
        if risk_factors:
            rows.append(("IDENTIFIED RISK FACTORS", ""))
            for factor_name, factor_data in risk_factors.items():
                if factor_data.get('present'):
                    rows.append((
                        factor_name.replace('_', ' ').title(),
                        f"{factor_data.get('risk_level', 'N/A')} (Impact: {factor_data.get('impact_score', 0):.1f}/10)"
                    ))
                    rows.append(("  Description", factor_data.get('description', '')))
                    rows.append(("  Mitigation", factor_data.get('mitigation', '')))
                    rows.append(("", ""))

        # Data Quality Score
        data_quality = assessment.get('data_quality_score', {})
        if data_quality:
            rows.append(("DATA QUALITY SCORE", ""))
            rows.append(("Overall Score", f"{data_quality.get('overall_score', 0)}/100 ({data_quality.get('overall_label', 'N/A')})"))
            breakdown = data_quality.get('breakdown', {})
            for metric, data in breakdown.items():
                rows.append((
                    f"  {metric.title()}",
                    f"{data.get('score', 0)}/100 - {data.get('description', '')}"
                ))
            rows.append(("", ""))

        # Comparable Sales Quality
        comp_quality = assessment.get('comparable_sales_quality', {})
        if comp_quality:
            rows.append(("COMPARABLE SALES QUALITY", ""))
            rows.append(("Overall Score", f"{comp_quality.get('overall_score', 0)}/100 ({comp_quality.get('overall_label', 'N/A')})"))
            breakdown = comp_quality.get('breakdown', {})
            for metric, data in breakdown.items():
                rows.append((
                    f"  {metric.title()}",
                    f"{data.get('score', 0)}/100 - {data.get('description', '')}"
                ))
            rows.append(("", ""))

        # Market Confidence
        market_conf = assessment.get('market_confidence', {})
        if market_conf:
            rows.append(("MARKET CONFIDENCE", ""))
            rows.append(("Score", f"{market_conf.get('score', 0)}/100 ({market_conf.get('score_label', 'N/A')})"))
            factors = market_conf.get('factors', {})
            for factor, data in factors.items():
                rows.append((
                    f"  {factor.replace('_', ' ').title()}",
                    f"{data.get('score', 0)}/100 - {data.get('description', '')}"
                ))
            rows.append(("", ""))

        # Property Confidence
        prop_conf = assessment.get('property_confidence', {})
        if prop_conf:
            rows.append(("PROPERTY CONFIDENCE", ""))
            rows.append(("Score", f"{prop_conf.get('score', 0)}/100 ({prop_conf.get('score_label', 'N/A')})"))
            factors = prop_conf.get('factors', {})
            for factor, data in factors.items():
                if factor != 'verification_required':
                    rows.append((
                        f"  {factor.replace('_', ' ').title()}",
                        f"{data.get('score', 0)}/100 - {data.get('description', '')}"
                    ))
                else:
                    rows.append(("  Verification Required", ", ".join(data.get('items', []))))

        rows.append(("", ""))
        return rows

    def extract_comparative_analysis_section(self, report: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Extract comparative analysis for PDF"""
        rows = []
        comp_analysis = report.get('comparative_analysis', {})

        rows.append(("5. COMPARATIVE ANALYSIS", ""))
        rows.append(("", ""))

        subject_vs_market = comp_analysis.get('subject_vs_market', {})

        # Price Position
        price_pos = subject_vs_market.get('price_position', {})
        if price_pos:
            rows.append(("PRICE POSITION", ""))
            rows.append(("Subject Last Sale", f"${price_pos.get('subject_last_sale', 0):,} ({price_pos.get('subject_last_sale_date', 'N/A')})"))
            rows.append(("Current Market Median", f"${price_pos.get('current_market_median', 0):,}"))
            rows.append(("Analysis", price_pos.get('analysis', '')))

            est_range = price_pos.get('estimated_current_value_range', {})
            if est_range:
                rows.append(("Estimated Current Value", f"${est_range.get('lower', 0):,} - ${est_range.get('upper', 0):,}"))
                if est_range.get('adjustment_for_dual_occupancy'):
                    rows.append(("  Dual Occupancy Adjustment", est_range['adjustment_for_dual_occupancy']))
            rows.append(("", ""))

        # Land Area
        land_area = subject_vs_market.get('land_area', {})
        if land_area:
            rows.append(("LAND AREA COMPARISON", ""))
            rows.append(("Subject", f"{land_area.get('subject', 0)} m²"))
            rows.append(("Market Median", f"{land_area.get('market_median', 0)} m²"))
            rows.append(("Market Range", f"{land_area.get('market_range_min', 0)} - {land_area.get('market_range_max', 0)} m²"))
            rows.append(("Position", f"{land_area.get('position', 'N/A')} ({land_area.get('percentile', 0)}th percentile)"))
            rows.append(("Analysis", land_area.get('analysis', '')))
            rows.append(("", ""))

        # Configuration
        config = subject_vs_market.get('configuration', {})
        if config:
            rows.append(("CONFIGURATION COMPARISON", ""))
            rows.append(("Subject", config.get('subject', 'N/A')))
            rows.append(("Market Match Rate", f"{config.get('match_rate', 0):.1f}%"))
            rows.append(("Analysis", config.get('analysis', '')))
            rows.append(("", ""))

        # Special Features
        features = subject_vs_market.get('special_features', {})
        if features:
            rows.append(("SPECIAL FEATURES", ""))
            subject_features = features.get('subject_features', [])
            for feat in subject_features:
                rows.append(("  Subject Feature", feat))

            differentiators = features.get('market_differentiators', [])
            for diff in differentiators:
                rows.append(("  Market Differentiator", diff))

            rows.append(("Analysis", features.get('analysis', '')))

        rows.append(("", ""))
        return rows

    def extract_recommendations_section(self, report: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Extract risk mitigation recommendations for PDF"""
        rows = []
        recommendations = report.get('risk_mitigation_recommendations', {})

        rows.append(("6. RISK MITIGATION RECOMMENDATIONS", ""))
        rows.append(("", ""))

        # High Priority
        high_priority = recommendations.get('high_priority', [])
        if high_priority:
            rows.append(("HIGH PRIORITY ACTIONS", ""))
            for rec in high_priority:
                rows.append((f"Priority {rec.get('priority', 'N/A')}: {rec.get('category', 'N/A')}", ""))
                rows.append(("  Action", rec.get('action', '')))
                rows.append(("  Reason", rec.get('reason', '')))
                rows.append(("  Impact on Valuation", rec.get('impact_on_valuation', '')))
                rows.append(("", ""))

        # Medium Priority
        medium_priority = recommendations.get('medium_priority', [])
        if medium_priority:
            rows.append(("MEDIUM PRIORITY ACTIONS", ""))
            for rec in medium_priority:
                rows.append((f"Priority {rec.get('priority', 'N/A')}: {rec.get('category', 'N/A')}", ""))
                rows.append(("  Action", rec.get('action', '')))
                rows.append(("  Impact on Valuation", rec.get('impact_on_valuation', '')))
                rows.append(("", ""))

        # Summary
        if recommendations.get('summary'):
            rows.append(("SUMMARY", recommendations['summary']))

        rows.append(("", ""))
        return rows

    def extract_report_summary_section(self, report: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Extract report summary for PDF"""
        rows = []
        summary = report.get('report_summary', {})

        rows.append(("7. REPORT SUMMARY", ""))
        rows.append(("", ""))

        rows.append(("Coverage", "100% - Complete"))
        rows.append(("", ""))

        rows.append(("OVERALL ASSESSMENT", ""))
        rows.append(("Overall Risk Rating", summary.get('overall_risk_rating', 'N/A')))
        rows.append(("Overall Confidence", f"{summary.get('overall_confidence', 0)}%"))
        rows.append(("Suitability for Valuation", summary.get('suitability_for_valuation', 'N/A')))
        rows.append(("", ""))

        # Conditions
        conditions = summary.get('conditions', [])
        if conditions:
            rows.append(("CONDITIONS", ""))
            for i, condition in enumerate(conditions, 1):
                rows.append((f"  {i}.", condition))
            rows.append(("", ""))

        # Key Value Drivers
        value_drivers = summary.get('key_value_drivers', [])
        if value_drivers:
            rows.append(("KEY VALUE DRIVERS", ""))
            for driver in value_drivers:
                rows.append(("  •", driver))
            rows.append(("", ""))

        # Key Risk Factors
        risk_factors = summary.get('key_risk_factors', [])
        if risk_factors:
            rows.append(("KEY RISK FACTORS", ""))
            for risk in risk_factors:
                rows.append(("  •", risk))
            rows.append(("", ""))

        # Recommended Valuation Approach
        if summary.get('recommended_valuation_approach'):
            rows.append(("RECOMMENDED VALUATION APPROACH", ""))
            rows.append(("", summary['recommended_valuation_approach']))
            rows.append(("", ""))

        # Estimated Valuation Range
        val_range = summary.get('estimated_valuation_range', {})
        if val_range:
            rows.append(("ESTIMATED VALUATION RANGE", ""))

            base_range = val_range.get('base_range', {})
            if base_range:
                rows.append(("Base Range (Single Dwelling)", f"${base_range.get('lower', 0):,} - ${base_range.get('upper', 0):,}"))
                rows.append(("  Basis", base_range.get('basis', 'N/A')))

            dual_range = val_range.get('with_dual_occupancy_premium', {})
            if dual_range:
                rows.append(("With Dual Occupancy Premium", f"${dual_range.get('lower', 0):,} - ${dual_range.get('upper', 0):,}"))
                rows.append(("  Adjustment", dual_range.get('adjustment', 'N/A')))

            if val_range.get('confidence_interval'):
                rows.append(("Confidence Interval", val_range['confidence_interval']))

        return rows

    def generate_pdf(self, report: Dict[str, Any], output_path: Path):
        """Generate PDF from classification scoring report"""

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )

        elements = []

        # Title
        metadata = report.get('metadata', {})
        title_text = f"Pre-Qualification - Classification & Scoring"
        title = Paragraph(title_text, self.title_style)
        elements.append(title)

        address_text = metadata.get('property_address', 'Unknown Address')
        address = Paragraph(address_text, self.title_style)
        elements.append(address)
        elements.append(Spacer(1, 0.1*inch))

        # Extract all sections
        all_rows = []

        all_rows.extend(self.extract_imagery_classification_section(report))
        all_rows.extend(self.extract_market_risk_scores_section(report))
        all_rows.extend(self.extract_risk_flags_section(report))
        all_rows.extend(self.extract_valuation_assessment_section(report))
        all_rows.extend(self.extract_comparative_analysis_section(report))
        all_rows.extend(self.extract_recommendations_section(report))
        all_rows.extend(self.extract_report_summary_section(report))

        # Create table data with Paragraph objects
        table_data = []
        for label, value in all_rows:
            label_para = Paragraph(label, self.label_style if label and not label.startswith(' ') else self.normal_style)
            value_para = Paragraph(str(value), self.normal_style)
            table_data.append([label_para, value_para])

        # Create table
        col_widths = [2.5*inch, 4.5*inch]
        table = Table(table_data, colWidths=col_widths, repeatRows=0)

        # Table style
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ]))

        elements.append(table)

        # Footer
        elements.append(Spacer(1, 0.2*inch))
        footer_text = f"Report generated: {metadata.get('generation_timestamp', 'N/A')} | Property ID: {metadata.get('property_id', 'N/A')}"
        footer = Paragraph(footer_text, self.normal_style)
        elements.append(footer)

        # Build PDF
        doc.build(elements)
        print(f"✓ PDF generated: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate Classification & Scoring PDF Report",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--input', type=str, required=True,
                       help='Path to classification_scoring JSON file')
    parser.add_argument('--output', type=str,
                       help='Output path for PDF (default: same location as input with .pdf extension)')

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"✗ Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_suffix('.pdf')
        output_path = output_path.parent / f"{input_path.stem}_report.pdf"

    try:
        # Load classification scoring report
        with open(input_path, 'r') as f:
            report = json.load(f)

        # Generate PDF
        generator = ClassificationScoringPDFGenerator()
        generator.generate_pdf(report, output_path)

        print("\n✓ Classification & Scoring PDF Generated Successfully")
        print(f"  Input: {input_path}")
        print(f"  Output: {output_path}")

        # Display summary
        summary = report.get('report_summary', {})
        print(f"\n  Summary:")
        print(f"  - Overall Risk Rating: {summary.get('overall_risk_rating', 'N/A')}")
        print(f"  - Overall Confidence: {summary.get('overall_confidence', 0)}%")
        print(f"  - Suitability: {summary.get('suitability_for_valuation', 'N/A')}")

    except Exception as e:
        print(f"✗ Error generating PDF: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
