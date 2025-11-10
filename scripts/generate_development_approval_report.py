#!/usr/bin/env python3
"""
Generate Development Approval JSON Report

Creates a comprehensive JSON report for planning permits and development approvals.

Usage:
    # Basic usage
    python3 scripts/generate_development_approval_report.py --property-id 13683380

    # With permit details
    python3 scripts/generate_development_approval_report.py \
        --property-id 13683380 \
        --permit-number "430/2025" \
        --approval-date "2025-03-20" \
        --status "Approved" \
        --description "Change of use from dependant person's unit to small second dwelling"

    # Add multiple permits via JSON input file
    python3 scripts/generate_development_approval_report.py \
        --property-id 13683380 \
        --input-json permits.json

Output:
    Creates: {property_id}_development_approvals.json

Example JSON Structure:
    {
      "metadata": {
        "property_id": 13683380,
        "property_address": "5 Settlers Court, Vermont South VIC 3133",
        "report_timestamp": "2025-11-10T15:30:00",
        "total_permits": 2
      },
      "summary": {
        "approved_permits": 1,
        "pending_permits": 0,
        "refused_permits": 0,
        "withdrawn_permits": 0,
        "latest_permit_date": "2025-03-20",
        "oldest_permit_date": "2022-01-15"
      },
      "permits": [
        {
          "permit_number": "430/2025",
          "status": "Approved",
          "lodgement_date": null,
          "decision_date": "2025-03-20",
          "description": "Change of use from dependant person's unit to small second dwelling",
          "permit_type": "Planning Permit",
          "applicant": null,
          "estimated_cost": null,
          "conditions": []
        }
      ]
    }

Author: Development Approval Report Generator
Date: 2025-11-10
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


def create_permit_entry(
    permit_number: str,
    status: str = "Unknown",
    approval_date: Optional[str] = None,
    lodgement_date: Optional[str] = None,
    description: Optional[str] = None,
    permit_type: str = "Planning Permit",
    applicant: Optional[str] = None,
    estimated_cost: Optional[float] = None,
    conditions: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create a permit entry dictionary.

    Args:
        permit_number: Permit/application number
        status: Approval status (Approved, Pending, Refused, Withdrawn)
        approval_date: Decision/approval date (ISO format: YYYY-MM-DD)
        lodgement_date: Application lodgement date (ISO format: YYYY-MM-DD)
        description: Description of the development
        permit_type: Type of permit (Planning Permit, Building Permit, etc.)
        applicant: Applicant name
        estimated_cost: Estimated development cost
        conditions: List of permit conditions

    Returns:
        Permit entry dictionary
    """
    return {
        "permit_number": permit_number,
        "status": status,
        "lodgement_date": lodgement_date,
        "decision_date": approval_date,
        "description": description,
        "permit_type": permit_type,
        "applicant": applicant,
        "estimated_cost": estimated_cost,
        "conditions": conditions or []
    }


def generate_summary(permits: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate summary statistics for permits.

    Args:
        permits: List of permit entries

    Returns:
        Summary statistics dictionary
    """
    summary = {
        "approved_permits": 0,
        "pending_permits": 0,
        "refused_permits": 0,
        "withdrawn_permits": 0,
        "latest_permit_date": None,
        "oldest_permit_date": None,
        "permit_types": {},
        "total_estimated_cost": 0.0
    }

    dates = []

    for permit in permits:
        # Count by status
        status = permit.get('status', 'Unknown').lower()
        if 'approved' in status or 'issued' in status:
            summary['approved_permits'] += 1
        elif 'pending' in status or 'submitted' in status:
            summary['pending_permits'] += 1
        elif 'refused' in status or 'rejected' in status:
            summary['refused_permits'] += 1
        elif 'withdrawn' in status:
            summary['withdrawn_permits'] += 1

        # Collect dates
        if permit.get('decision_date'):
            dates.append(permit['decision_date'])
        if permit.get('lodgement_date'):
            dates.append(permit['lodgement_date'])

        # Count permit types
        permit_type = permit.get('permit_type', 'Unknown')
        summary['permit_types'][permit_type] = summary['permit_types'].get(permit_type, 0) + 1

        # Sum estimated costs
        if permit.get('estimated_cost'):
            summary['total_estimated_cost'] += permit['estimated_cost']

    # Find date range
    if dates:
        dates.sort()
        summary['oldest_permit_date'] = dates[0]
        summary['latest_permit_date'] = dates[-1]

    return summary


def generate_report(
    property_id: int,
    permits: List[Dict[str, Any]],
    property_address: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate comprehensive development approval report.

    Args:
        property_id: Property ID
        permits: List of permit entries
        property_address: Optional property address

    Returns:
        Comprehensive report dictionary
    """
    summary = generate_summary(permits)

    report = {
        "metadata": {
            "property_id": property_id,
            "property_address": property_address,
            "report_timestamp": datetime.now().isoformat(),
            "total_permits": len(permits),
            "report_type": "Development Approvals"
        },
        "summary": summary,
        "permits": sorted(permits, key=lambda x: x.get('decision_date') or x.get('lodgement_date') or '', reverse=True)
    }

    return report


def save_report(report: Dict[str, Any], output_path: Path) -> None:
    """
    Save report to JSON file.

    Args:
        report: Report dictionary
        output_path: Path to save JSON file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"✅ Report saved: {output_path}")


def print_summary(report: Dict[str, Any]) -> None:
    """
    Print report summary to console.

    Args:
        report: Report dictionary
    """
    metadata = report.get('metadata', {})
    summary = report.get('summary', {})
    permits = report.get('permits', [])

    print("\n" + "=" * 70)
    print("🏗️  DEVELOPMENT APPROVALS REPORT")
    print("=" * 70)

    # Property info
    print(f"\n🏠 Property: {metadata.get('property_id')}")
    if metadata.get('property_address'):
        print(f"   Address: {metadata.get('property_address')}")

    # Permit statistics
    print(f"\n📊 Permit Statistics:")
    print(f"   Total Permits: {metadata.get('total_permits', 0)}")
    print(f"   Approved: {summary.get('approved_permits', 0)}")
    print(f"   Pending: {summary.get('pending_permits', 0)}")
    print(f"   Refused: {summary.get('refused_permits', 0)}")
    print(f"   Withdrawn: {summary.get('withdrawn_permits', 0)}")

    # Temporal coverage
    if summary.get('oldest_permit_date'):
        print(f"\n📅 Date Range:")
        print(f"   Oldest: {summary.get('oldest_permit_date')}")
        print(f"   Latest: {summary.get('latest_permit_date')}")

    # Permit types
    if summary.get('permit_types'):
        print(f"\n📋 Permit Types:")
        for permit_type, count in summary.get('permit_types', {}).items():
            print(f"   {permit_type}: {count}")

    # Total cost
    if summary.get('total_estimated_cost', 0) > 0:
        print(f"\n💰 Total Estimated Cost: ${summary.get('total_estimated_cost', 0):,.2f}")

    # Recent permits
    if permits:
        print(f"\n📄 Recent Permits:")
        for permit in permits[:5]:
            print(f"\n   Permit: {permit.get('permit_number')}")
            print(f"   Status: {permit.get('status')}")
            print(f"   Date: {permit.get('decision_date') or permit.get('lodgement_date') or 'Unknown'}")
            if permit.get('description'):
                desc = permit.get('description', '')
                if len(desc) > 70:
                    desc = desc[:67] + "..."
                print(f"   Description: {desc}")

        if len(permits) > 5:
            print(f"\n   ... and {len(permits) - 5} more permits")

    print("\n" + "=" * 70)


def load_permits_from_json(json_path: Path) -> List[Dict[str, Any]]:
    """
    Load permits from JSON input file.

    Expected format:
    {
      "permits": [
        {
          "permit_number": "430/2025",
          "status": "Approved",
          "approval_date": "2025-03-20",
          "description": "Change of use..."
        }
      ]
    }

    Args:
        json_path: Path to JSON file

    Returns:
        List of permit entries
    """
    with open(json_path, 'r') as f:
        data = json.load(f)

    permits = []
    for permit_data in data.get('permits', []):
        permit = create_permit_entry(
            permit_number=permit_data.get('permit_number'),
            status=permit_data.get('status', 'Unknown'),
            approval_date=permit_data.get('approval_date') or permit_data.get('decision_date'),
            lodgement_date=permit_data.get('lodgement_date'),
            description=permit_data.get('description'),
            permit_type=permit_data.get('permit_type', 'Planning Permit'),
            applicant=permit_data.get('applicant'),
            estimated_cost=permit_data.get('estimated_cost'),
            conditions=permit_data.get('conditions', [])
        )
        permits.append(permit)

    return permits


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description='Generate development approval JSON report for a property',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single permit entry
  python scripts/generate_development_approval_report.py \\
      --property-id 13683380 \\
      --permit-number "430/2025" \\
      --approval-date "2025-03-20" \\
      --status "Approved" \\
      --description "Change of use from dependant person's unit to small second dwelling"

  # Load from JSON file
  python scripts/generate_development_approval_report.py \\
      --property-id 13683380 \\
      --input-json data/permits/13683380_permits.json
        """
    )

    parser.add_argument(
        '--property-id',
        type=int,
        required=True,
        help='Property ID'
    )

    parser.add_argument(
        '--address',
        type=str,
        help='Property address (optional, for metadata)'
    )

    parser.add_argument(
        '--permit-number',
        type=str,
        help='Permit/application number'
    )

    parser.add_argument(
        '--status',
        type=str,
        choices=['Approved', 'Pending', 'Refused', 'Withdrawn', 'Issued', 'Submitted'],
        help='Approval status'
    )

    parser.add_argument(
        '--approval-date',
        type=str,
        help='Approval/decision date (YYYY-MM-DD)'
    )

    parser.add_argument(
        '--lodgement-date',
        type=str,
        help='Lodgement date (YYYY-MM-DD)'
    )

    parser.add_argument(
        '--description',
        type=str,
        help='Development description'
    )

    parser.add_argument(
        '--permit-type',
        type=str,
        default='Planning Permit',
        help='Permit type (default: Planning Permit)'
    )

    parser.add_argument(
        '--applicant',
        type=str,
        help='Applicant name'
    )

    parser.add_argument(
        '--estimated-cost',
        type=float,
        help='Estimated development cost'
    )

    parser.add_argument(
        '--input-json',
        type=str,
        help='Load permits from JSON file'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/property_reports',
        help='Output directory for JSON report (default: data/property_reports)'
    )

    args = parser.parse_args()

    try:
        permits = []

        # Load from JSON file if provided
        if args.input_json:
            input_path = Path(args.input_json)
            if not input_path.exists():
                print(f"❌ Error: Input JSON file not found: {input_path}", file=sys.stderr)
                sys.exit(1)
            permits = load_permits_from_json(input_path)
            print(f"✅ Loaded {len(permits)} permits from {input_path}")

        # Add single permit from command line args
        elif args.permit_number:
            permit = create_permit_entry(
                permit_number=args.permit_number,
                status=args.status or "Unknown",
                approval_date=args.approval_date,
                lodgement_date=args.lodgement_date,
                description=args.description,
                permit_type=args.permit_type,
                applicant=args.applicant,
                estimated_cost=args.estimated_cost
            )
            permits.append(permit)
            print(f"✅ Created permit entry: {args.permit_number}")
        else:
            print("❌ Error: Either --permit-number or --input-json must be provided", file=sys.stderr)
            parser.print_help()
            sys.exit(1)

        # Generate report
        report = generate_report(
            property_id=args.property_id,
            permits=permits,
            property_address=args.address
        )

        # Save report
        output_dir = Path(args.output_dir)
        output_file = output_dir / f"{args.property_id}_development_approvals.json"
        save_report(report, output_file)

        # Print summary
        print_summary(report)

        # Success
        print(f"\n📁 Full report: {output_file}\n")
        sys.exit(0)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
