#!/usr/bin/env python3
"""
Planning Zone Extractor

Handles complex extraction of planning zone data including:
- Section 1 & 2 uses (numbered lists)
- Opportunities and requirements (combined multi-line)
"""

from typing import Dict, Any, List, Tuple, Optional
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.extraction_utils import (
    get_nested_value,
    truncate_text,
    wrap_text
)


class PlanningZoneExtractor:
    """Extracts complex planning zone data"""

    def extract_section_1_uses(
        self,
        zone_data: Optional[Dict[str, Any]],
        max_items: int = 10
    ) -> List[Tuple[str, str]]:
        """
        Extract Section 1 - Permit NOT Required uses.

        Args:
            zone_data: Planning zone data
            max_items: Maximum items to show

        Returns:
            List of (label, value) tuples
        """
        rows = []

        if not zone_data:
            rows.append(("Section 1 - Permit NOT Required", "Unknown"))
            rows.append(("", ""))
            return rows

        table_of_uses = zone_data.get('table_of_uses', {})
        section1_uses = table_of_uses.get('section_1_uses', [])

        if not section1_uses:
            rows.append(("Section 1 - Permit NOT Required", "Unknown"))
            rows.append(("", ""))
            return rows

        rows.append(("Section 1 - Permit NOT Required", ""))

        for i, use in enumerate(section1_uses[:max_items], 1):
            truncated_use = truncate_text(use, 100)
            rows.append((f"  {i}", truncated_use))

        if len(section1_uses) > max_items:
            rows.append(("  ...", f"+ {len(section1_uses) - max_items} more uses"))

        rows.append(("", ""))

        return rows

    def extract_section_2_uses(
        self,
        zone_data: Optional[Dict[str, Any]],
        max_items: int = 10
    ) -> List[Tuple[str, str]]:
        """
        Extract Section 2 - Permit Required uses.

        Args:
            zone_data: Planning zone data
            max_items: Maximum items to show

        Returns:
            List of (label, value) tuples
        """
        rows = []

        if not zone_data:
            rows.append(("Section 2 - Permit Required", "Unknown"))
            rows.append(("", ""))
            return rows

        table_of_uses = zone_data.get('table_of_uses', {})
        section2_uses = table_of_uses.get('section_2_uses', [])

        if not section2_uses:
            rows.append(("Section 2 - Permit Required", "Unknown"))
            rows.append(("", ""))
            return rows

        rows.append(("Section 2 - Permit Required", ""))

        for i, use in enumerate(section2_uses[:max_items], 1):
            truncated_use = truncate_text(use, 100)
            rows.append((f"  {i}", truncated_use))

        if len(section2_uses) > max_items:
            rows.append(("  ...", f"+ {len(section2_uses) - max_items} more uses"))

        rows.append(("", ""))

        return rows

    def extract_opportunities_and_requirements(
        self,
        zone_data: Optional[Dict[str, Any]],
        max_non_residential: int = 8,
        max_height_restrictions: int = 3
    ) -> List[Tuple[str, str]]:
        """
        Extract combined opportunities and requirements section.

        Args:
            zone_data: Planning zone data
            max_non_residential: Max non-residential uses to show
            max_height_restrictions: Max height restrictions to show

        Returns:
            List of (label, value) tuples
        """
        rows = []

        if not zone_data:
            rows.append(("Opportunities & Requirements", "Unknown"))
            rows.append(("", ""))
            return rows

        combined_info = []

        # Non-residential opportunities
        non_res_uses = zone_data.get('non_residential_uses', [])
        if non_res_uses:
            combined_info.append("NON-RESIDENTIAL OPPORTUNITIES:")
            for use in non_res_uses[:max_non_residential]:
                combined_info.append(f"• {use}")
            if len(non_res_uses) > max_non_residential:
                combined_info.append(f"• + {len(non_res_uses) - max_non_residential} more")

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
            for hr in height_restrictions[:max_height_restrictions]:
                height = hr.get('height', 'Unknown')
                combined_info.append(f"• {height}")

        if combined_info:
            rows.append(("Opportunities & Requirements", "\n".join(combined_info)))
        else:
            rows.append(("Opportunities & Requirements", "Unknown"))

        rows.append(("", ""))

        return rows
