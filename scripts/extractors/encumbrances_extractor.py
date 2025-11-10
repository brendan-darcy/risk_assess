#!/usr/bin/env python3
"""
Encumbrances Extractor

Handles extraction of easements and heritage encumbrances.
"""

from typing import Dict, Any, List, Tuple, Optional


class EncumbrancesExtractor:
    """Extracts encumbrances (easements and heritage) data"""

    def extract(
        self,
        geo_layers: Optional[Dict[str, Any]]
    ) -> List[Tuple[str, str]]:
        """
        Extract encumbrances section.

        Args:
            geo_layers: Geospatial layers data

        Returns:
            List of (label, value) tuples
        """
        rows = []
        rows.append(("ENCUMBRANCES", ""))

        if not geo_layers:
            rows.append(("Status", "No geospatial data available"))
            rows.append(("", ""))
            return rows

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

        return rows
