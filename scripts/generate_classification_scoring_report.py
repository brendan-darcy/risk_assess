#!/usr/bin/env python3
"""
Generate Classification & Scoring Report

Creates a classification and scoring report from property data collection report.
This report includes:
- Computer Vision imagery classification & quality scores (Layer 1/2/3)
- Market risk scores (trends, liquidity, uniqueness)
- Property risk flags (NLP detection)
- Valuation risk assessment
- Comparative analysis
- Risk mitigation recommendations

Usage:
    # Generate from property ID (loads comprehensive report)
    python3 scripts/generate_classification_scoring_report.py --property-id 13683380

    # Generate from comprehensive report JSON
    python3 scripts/generate_classification_scoring_report.py \
        --input data/property_reports/13683380_comprehensive_report.json

    # Custom output location
    python3 scripts/generate_classification_scoring_report.py \
        --property-id 13683380 \
        --output data/property_reports/13683380_classification_scoring_custom.json

Author: ARMATech Classification & Scoring System
Date: 2025-11-10
Version: 1.0
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import re

class ClassificationScoringGenerator:
    """Generate classification and scoring reports from property data"""

    def __init__(self):
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.current_timestamp = datetime.now().isoformat()

    def load_comprehensive_report(self, property_id: int, data_dir: Path = None) -> Dict[str, Any]:
        """Load comprehensive data collection report"""
        if data_dir is None:
            data_dir = Path("data/property_reports")

        report_file = data_dir / f"{property_id}_comprehensive_report.json"
        if not report_file.exists():
            raise FileNotFoundError(f"Comprehensive report not found: {report_file}")

        with open(report_file, 'r') as f:
            return json.load(f)

    def load_property_images(self, property_id: int, data_dir: Path = None) -> Optional[Dict[str, Any]]:
        """Load property images metadata"""
        if data_dir is None:
            data_dir = Path("data/property_reports")

        images_file = data_dir / f"{property_id}_property_images.json"
        if images_file.exists():
            with open(images_file, 'r') as f:
                return json.load(f)
        return None

    def load_comparable_sales(self, property_id: int, data_dir: Path = None) -> Optional[Dict[str, Any]]:
        """Load comparable sales data"""
        if data_dir is None:
            data_dir = Path("data/property_reports")

        comps_file = data_dir / f"{property_id}_comparable_sales.json"
        if comps_file.exists():
            with open(comps_file, 'r') as f:
                return json.load(f)
        return None

    def load_development_approvals(self, property_id: int, data_dir: Path = None) -> Optional[Dict[str, Any]]:
        """Load development approvals data"""
        if data_dir is None:
            data_dir = Path("data/property_reports")

        approvals_file = data_dir / f"{property_id}_development_approvals.json"
        if approvals_file.exists():
            with open(approvals_file, 'r') as f:
                return json.load(f)
        return None

    def generate_imagery_classification(self, images_data: Optional[Dict[str, Any]],
                                       property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate imagery classification scores.

        In production, this would call ARMATech Computer Vision API.
        For now, generates realistic sample scores based on image metadata.
        """
        if not images_data:
            return {
                "summary": {
                    "total_images": 0,
                    "images_processed": 0,
                    "processing_method": "ARMATech Computer Vision v2.1",
                    "processing_date": self.current_date,
                    "status": "No imagery data available"
                }
            }

        total_images = images_data.get('summary', {}).get('total_images', 0)

        # Generate realistic Layer 1 tagging
        # TODO: Replace with actual Computer Vision API call
        indoor_pct = 0.70  # 70% indoor typical for residential
        outdoor_pct = 0.25
        aerial_pct = 0.05

        indoor_count = int(total_images * indoor_pct)
        outdoor_count = int(total_images * outdoor_pct)
        aerial_count = total_images - indoor_count - outdoor_count

        # Generate Layer 2 tagging
        # TODO: Replace with actual Computer Vision API call
        layer_2_indoor = {
            "kitchen": {"count": int(indoor_count * 0.286), "percentage": 28.6, "eligible_for_layer_3": True},
            "bathroom": {"count": int(indoor_count * 0.214), "percentage": 21.4, "eligible_for_layer_3": True},
            "living_space": {"count": int(indoor_count * 0.250), "percentage": 25.0, "eligible_for_layer_3": False},
            "entrance": {"count": int(indoor_count * 0.107), "percentage": 10.7, "eligible_for_layer_3": False},
            "laundry": {"count": int(indoor_count * 0.071), "percentage": 7.1, "eligible_for_layer_3": True},
            "garage_shed": {"count": int(indoor_count * 0.071), "percentage": 7.1, "eligible_for_layer_3": False}
        }

        layer_2_outdoor = {
            "frontage": {"count": int(outdoor_count * 0.30), "percentage": 30.0, "eligible_for_layer_3": True},
            "garden": {"count": int(outdoor_count * 0.40), "percentage": 40.0, "eligible_for_layer_3": False},
            "garage_shed": {"count": int(outdoor_count * 0.20), "percentage": 20.0, "eligible_for_layer_3": False},
            "local_scenery": {"count": int(outdoor_count * 0.10), "percentage": 10.0, "eligible_for_layer_3": False}
        }

        # Generate Layer 3 quality scores
        # TODO: Replace with actual Computer Vision API call
        # Sample scores based on property features
        features = property_data.get('property_details', {}).get('features', {})

        kitchen_grade = self._calculate_kitchen_grade(features)
        wet_rooms_grade = self._calculate_wet_rooms_grade(property_data)
        frontage_grade = self._calculate_frontage_grade(property_data)

        # Calculate completeness score
        completeness = self._calculate_completeness_score(images_data)

        return {
            "summary": {
                "total_images": total_images,
                "images_processed": total_images,
                "processing_method": "ARMATech Computer Vision v2.1",
                "processing_date": self.current_date
            },
            "layer_1_tagging": {
                "description": "High-level image classification",
                "categories": {
                    "indoor": {"count": indoor_count, "percentage": round(indoor_pct * 100, 1)},
                    "outdoor": {"count": outdoor_count, "percentage": round(outdoor_pct * 100, 1)},
                    "aerial": {"count": aerial_count, "percentage": round(aerial_pct * 100, 1)},
                    "floorplan": {"count": 0, "percentage": 0.0},
                    "under_construction": {"count": 0, "percentage": 0.0},
                    "not_property_image": {"count": 0, "percentage": 0.0}
                },
                "deduplication": {
                    "original_count": total_images,
                    "after_deduplication": max(total_images - 2, 0),
                    "duplicates_removed": min(2, total_images)
                }
            },
            "layer_2_tagging": {
                "description": "Granular room-level classification",
                "indoor_categories": layer_2_indoor,
                "outdoor_categories": layer_2_outdoor
            },
            "layer_3_quality_scores": {
                "description": "Quality grading for value-driver images (1-5 scale)",
                "kitchen": kitchen_grade,
                "wet_rooms": wet_rooms_grade,
                "frontage": frontage_grade
            },
            "completeness_score": completeness,
            "strata_plan_analysis": self._analyze_strata_plan(property_data)
        }

    def _calculate_kitchen_grade(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate kitchen quality grade based on features"""
        # Look for premium features
        base_grade = 3.5
        if "stainless steel" in str(features.get('kitchenFeatures', '')).lower():
            base_grade += 0.5
        if "dishwasher" in str(features.get('otherSpecialFeatures', '')).lower():
            base_grade += 0.3

        return {
            "images_graded": 8,
            "overall_grade": round(base_grade, 1),
            "overall_grade_label": self._grade_label(base_grade),
            "dimension_scores": {
                "cabinetry": round(base_grade + 0.2, 1),
                "appliances": round(base_grade + 0.4, 1),
                "benchtops": round(base_grade, 1),
                "tapware": round(base_grade + 0.1, 1),
                "lighting": round(base_grade + 0.05, 1),
                "overall_style_coherence": round(base_grade + 0.2, 1)
            },
            "best_image_grade": round(base_grade + 0.5, 1),
            "worst_image_grade": round(base_grade - 0.6, 1),
            "confidence": 0.87
        }

    def _calculate_wet_rooms_grade(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate wet rooms (bathroom/laundry) quality grade"""
        baths = property_data.get('property_details', {}).get('core_attributes', {}).get('baths', 2)
        base_grade = 3.5 if baths >= 2 else 3.0

        return {
            "images_graded": baths * 3,
            "overall_grade": base_grade,
            "overall_grade_label": self._grade_label(base_grade),
            "dimension_scores": {
                "fixtures": round(base_grade + 0.3, 1),
                "tiling": round(base_grade - 0.2, 1),
                "vanity": round(base_grade + 0.1, 1),
                "shower_bath": round(base_grade - 0.1, 1),
                "overall_style": base_grade
            },
            "best_image_grade": round(base_grade + 0.5, 1),
            "worst_image_grade": round(base_grade - 0.5, 1),
            "confidence": 0.82
        }

    def _calculate_frontage_grade(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate frontage/street appeal quality grade"""
        # Frontage typically higher grade for established properties
        year_built = property_data.get('property_details', {}).get('additional_attributes', {}).get('yearBuilt')
        base_grade = 4.0

        # Older properties with character can have higher street appeal
        if year_built and int(year_built) < 1990:
            base_grade += 0.2

        return {
            "images_graded": 3,
            "overall_grade": round(base_grade, 1),
            "overall_grade_label": self._grade_label(base_grade),
            "dimension_scores": {
                "kerb_appeal": round(base_grade + 0.3, 1),
                "landscaping": round(base_grade + 0.1, 1),
                "maintenance": base_grade,
                "street_presentation": round(base_grade, 1)
            },
            "best_image_grade": round(base_grade + 0.3, 1),
            "worst_image_grade": round(base_grade - 0.3, 1),
            "confidence": 0.91
        }

    def _grade_label(self, score: float) -> str:
        """Convert numeric grade to label"""
        if score >= 4.5:
            return "Excellent"
        elif score >= 4.0:
            return "Very Good"
        elif score >= 3.5:
            return "Good"
        elif score >= 3.0:
            return "Satisfactory"
        elif score >= 2.5:
            return "Fair"
        else:
            return "Poor"

    def _calculate_completeness_score(self, images_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate imagery completeness score"""
        summary = images_data.get('summary', {})
        total_images = summary.get('total_images', 0)
        temporal_span_years = summary.get('temporal_span_years', 0)
        newest_date = summary.get('newest_scan_date', '')

        # Temporal coverage score
        temporal_score = min(90, 60 + (temporal_span_years * 2))

        # Image quality score (based on total count and recency)
        quality_score = min(90, 50 + (total_images * 1.5))

        # Room coverage score
        room_coverage_score = 75 if total_images >= 30 else 60

        # Recency score
        recency_score = 90 if newest_date >= "2020-01-01" else 70

        overall_score = int((temporal_score + quality_score + room_coverage_score + recency_score) / 4)

        return {
            "overall_score": overall_score,
            "overall_label": "Excellent" if overall_score >= 90 else "Good" if overall_score >= 75 else "Fair",
            "factors": {
                "temporal_coverage": {
                    "score": int(temporal_score),
                    "description": f"{'Excellent' if temporal_span_years > 10 else 'Good'} - {temporal_span_years:.1f} years of imagery"
                },
                "image_quality": {
                    "score": int(quality_score),
                    "description": f"{'Very Good' if total_images > 40 else 'Good'} - {total_images} images available"
                },
                "room_coverage": {
                    "score": room_coverage_score,
                    "description": "Good - Most rooms covered" + (", no floorplan" if room_coverage_score < 80 else "")
                },
                "recency": {
                    "score": recency_score,
                    "description": f"{'Good' if newest_date >= '2020-01-01' else 'Fair'} - Latest images from {newest_date}"
                }
            },
            "recommendation": "Good imagery coverage. Consider obtaining floorplan for complete spatial understanding." if room_coverage_score < 80 else "Excellent imagery coverage."
        }

    def _analyze_strata_plan(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze if strata plan analysis is applicable"""
        property_type = property_data.get('property_details', {}).get('core_attributes', {}).get('propertyType', '')

        if property_type.upper() in ['UNIT', 'APARTMENT', 'TOWNHOUSE']:
            return {
                "applicable": True,
                "status": "Strata plan analysis recommended",
                "derived_characteristics": "TODO: Implement strata plan extraction"
            }
        else:
            return {
                "available": False,
                "reason": f"Not applicable - {property_type}, not strata title",
                "derived_characteristics": None
            }

    def generate_market_risk_scores(self, comprehensive_report: Dict[str, Any],
                                    comparable_sales: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate market risk scores.

        In production, this would call ARMATech market analysis algorithms.
        For now, generates scores based on available market data.
        """
        # Extract market metrics from comprehensive report
        market_metrics = comprehensive_report.get('market_metrics', {})

        # Calculate trend score
        trends_score = self._calculate_trends_score(market_metrics)

        # Calculate liquidity score
        liquidity_score = self._calculate_liquidity_score(comprehensive_report, comparable_sales)

        # Calculate uniqueness score
        uniqueness_score = self._calculate_uniqueness_score(comprehensive_report, comparable_sales)

        # Overall market risk score
        overall_risk_score = (trends_score['score'] + liquidity_score['score']) / 2

        return {
            "summary": {
                "overall_market_risk": "Low" if overall_risk_score >= 7.5 else "Medium" if overall_risk_score >= 5.0 else "High",
                "overall_market_risk_score": round(overall_risk_score, 1),
                "analysis_period": "2014-2022",
                "confidence": 0.89
            },
            "market_trends": trends_score,
            "local_liquidity": liquidity_score,
            "secondary_market_liquidity": {
                "applicable": False,
                "score": None,
                "reason": "Not a high-density or new development - matched pairs analysis not applicable",
                "description": "Subject is detached dwelling in established suburb."
            },
            "uniqueness_score": uniqueness_score
        }

    def _calculate_trends_score(self, market_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate market trends score"""
        # Extract growth rates from market metrics
        # TODO: Implement actual time series analysis

        return {
            "score": 7.5,
            "score_label": "Rising",
            "rating": "Positive",
            "factors": {
                "price_movement": {
                    "direction": "Rising",
                    "growth_rate": 87.3,
                    "period": "2014-09 to 2022-03",
                    "description": "Strong capital growth"
                },
                "volatility": {
                    "level": "Low to Moderate",
                    "description": "Steady growth with minor fluctuations"
                },
                "momentum": {
                    "current": "Positive",
                    "description": "Continued upward trajectory"
                }
            }
        }

    def _calculate_liquidity_score(self, comprehensive_report: Dict[str, Any],
                                  comparable_sales: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate local liquidity score"""
        if comparable_sales:
            total_sales = comparable_sales.get('metadata', {}).get('total_comparables', 0)
        else:
            total_sales = 0

        # Calculate score based on sales volume
        if total_sales >= 40:
            base_score = 8.5
        elif total_sales >= 20:
            base_score = 7.0
        elif total_sales >= 10:
            base_score = 5.5
        else:
            base_score = 4.0

        return {
            "score": base_score,
            "score_label": "High" if base_score >= 7.5 else "Medium",
            "rating": "Low Risk" if base_score >= 7.5 else "Medium Risk",
            "factors": {
                "sales_density": {
                    "score": base_score,
                    "recent_sales_count": total_sales,
                    "period": "Recent 2-3 years",
                    "description": f"{'Very high' if total_sales >= 40 else 'Moderate'} sales activity"
                }
            },
            "summary": f"{'High' if base_score >= 7.5 else 'Medium'} liquidity market with {'strong' if total_sales >= 40 else 'moderate'} sales activity."
        }

    def _calculate_uniqueness_score(self, comprehensive_report: Dict[str, Any],
                                   comparable_sales: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate property uniqueness score"""
        # TODO: Implement sophisticated uniqueness algorithm

        return {
            "score": 6.8,
            "score_label": "Moderate Uniqueness",
            "rating": "Medium Risk",
            "percentile": 55,
            "factors": {
                "configuration": {
                    "score": 5.0,
                    "description": "4bd/2ba/2car - common configuration",
                    "commonality": "Very Common"
                }
            },
            "summary": "Moderately unique property.",
            "valuation_impact": "Standard comparability"
        }

    def generate_risk_flags(self, comprehensive_report: Dict[str, Any],
                          development_approvals: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate property risk flags using NLP detection"""

        flags = {
            "summary": {
                "total_flags": 0,
                "high_priority_flags": 0,
                "medium_priority_flags": 0,
                "low_priority_flags": 0
            },
            "nlp_detection": {
                "analysis_date": self.current_date,
                "sources_analyzed": ["property_description", "campaign_text", "planning_permits"]
            }
        }

        # Check for dual occupancy
        dual_occ_flag = self._check_dual_occupancy(development_approvals)
        if dual_occ_flag:
            flags["nlp_detection"]["dual_occupancy"] = dual_occ_flag
            flags["summary"]["total_flags"] += 1
            if dual_occ_flag.get("priority") == "High":
                flags["summary"]["high_priority_flags"] += 1

        # TODO: Implement other NLP checks (acreages, display homes, etc.)

        return flags

    def _check_dual_occupancy(self, development_approvals: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Check for dual occupancy indicators"""
        if not development_approvals:
            return None

        permits = development_approvals.get('permits', [])
        for permit in permits:
            description = permit.get('description', '').lower()
            if any(keyword in description for keyword in ['dual', 'second dwelling', 'dependant']):
                return {
                    "detected": True,
                    "flag_status": "High Priority",
                    "priority": "High",
                    "confidence": 0.92,
                    "evidence": {
                        "permit_number": permit.get('permit_number'),
                        "permit_date": permit.get('approval_date'),
                        "permit_status": permit.get('status'),
                        "permit_description": permit.get('description')
                    },
                    "description": "CONFIRMED: Approved planning permit for dual occupancy",
                    "valuation_impact": "+5% to +10% premium for dual income/living potential",
                    "recommendation": "CRITICAL: Review permit conditions and verify construction status"
                }

        return None

    def generate_report(self, property_id: int, data_dir: Path = None) -> Dict[str, Any]:
        """Generate complete classification and scoring report"""

        # Load all data sources
        comprehensive_report = self.load_comprehensive_report(property_id, data_dir)
        images_data = self.load_property_images(property_id, data_dir)
        comparable_sales = self.load_comparable_sales(property_id, data_dir)
        development_approvals = self.load_development_approvals(property_id, data_dir)

        # Extract property address
        property_address = comprehensive_report.get('metadata', {}).get('address', 'Unknown')

        # Generate all sections
        imagery_classification = self.generate_imagery_classification(images_data, comprehensive_report)
        market_risk_scores = self.generate_market_risk_scores(comprehensive_report, comparable_sales)
        risk_flags = self.generate_risk_flags(comprehensive_report, development_approvals)

        # Build complete report
        report = {
            "metadata": {
                "property_id": property_id,
                "property_address": property_address,
                "generation_timestamp": self.current_timestamp,
                "report_type": "classification_scoring",
                "report_version": "1.0",
                "data_collection_report_id": f"{property_id}_comprehensive_report",
                "analysis_date": self.current_date
            },
            "imagery_classification": imagery_classification,
            "market_risk_scores": market_risk_scores,
            "property_risk_flags": risk_flags,
            "report_summary": {
                "overall_risk_rating": "Medium",
                "overall_confidence": 82,
                "suitability_for_valuation": "Suitable with Conditions",
                "note": "This is a sample classification and scoring report. In production, scores would be generated by ARMATech AI/ML models."
            }
        }

        return report

    def save_report(self, report: Dict[str, Any], output_path: Path):
        """Save report to JSON file"""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"✓ Classification & Scoring report saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate Classification & Scoring Report",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--property-id', type=int,
                       help='Property ID (e.g., 13683380)')
    parser.add_argument('--input', type=str,
                       help='Path to comprehensive report JSON')
    parser.add_argument('--output', type=str,
                       help='Output path for classification scoring JSON')
    parser.add_argument('--data-dir', type=str, default='data/property_reports',
                       help='Directory containing property data files')

    args = parser.parse_args()

    if not args.property_id and not args.input:
        print("Error: Either --property-id or --input must be specified")
        sys.exit(1)

    # Determine property ID
    if args.property_id:
        property_id = args.property_id
    else:
        # Extract property ID from input filename
        match = re.search(r'(\d+)_comprehensive_report', args.input)
        if match:
            property_id = int(match.group(1))
        else:
            print("Error: Could not determine property ID from input filename")
            sys.exit(1)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        data_dir = Path(args.data_dir)
        output_path = data_dir / f"{property_id}_classification_scoring.json"

    # Generate report
    try:
        generator = ClassificationScoringGenerator()
        report = generator.generate_report(property_id, Path(args.data_dir))
        generator.save_report(report, output_path)

        print("\n✓ Classification & Scoring Report Generated Successfully")
        print(f"  Property ID: {property_id}")
        print(f"  Output: {output_path}")
        print(f"\n  Summary:")
        print(f"  - Overall Risk Rating: {report['report_summary']['overall_risk_rating']}")
        print(f"  - Overall Confidence: {report['report_summary']['overall_confidence']}%")
        print(f"  - Suitability: {report['report_summary']['suitability_for_valuation']}")

    except Exception as e:
        print(f"✗ Error generating classification scoring report: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
