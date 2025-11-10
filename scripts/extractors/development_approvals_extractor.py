#!/usr/bin/env python3
"""
Development Approvals Extractor

Handles extraction of development approval/permit data.
"""

from typing import Dict, Any, List, Tuple, Optional
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.extraction_utils import wrap_text


class DevelopmentApprovalsExtractor:
    """Extracts development approval data"""

    def extract(
        self,
        approvals_data: Optional[Dict[str, Any]]
    ) -> List[Tuple[str, str]]:
        """
        Extract development approvals section.

        Args:
            approvals_data: Development approvals data

        Returns:
            List of (label, value) tuples
        """
        rows = []
        rows.append(("DEVELOPMENT APPROVALS", ""))

        if not approvals_data:
            rows.append(("Status", "No development approval data available"))
            rows.append(("", ""))
            return rows

        metadata = approvals_data.get('metadata', {})
        summary = approvals_data.get('summary', {})
        permits = approvals_data.get('permits', [])

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
                # Wrap long descriptions
                lines = wrap_text(description, max_width=80)
                if lines:
                    rows.append(("  Description", lines[0]))
                    for line in lines[1:]:
                        rows.append(("", line))

            permit_type = latest_permit.get('permit_type')
            if permit_type and permit_type != "Planning Permit":
                rows.append(("  Permit Type", permit_type))

            # Show additional permits if available
            if len(permits) > 1:
                rows.append(("", ""))
                rows.append(("Additional Permits", f"{len(permits) - 1} earlier permit(s) on record"))

        rows.append(("", ""))

        return rows
