#!/usr/bin/env python3
"""
Planning Zone Analyzer for Residential Valuers

Reads planning zone documents and extracts key information relevant to
residential property valuation, including:
- Use restrictions and allowances
- Non-residential uses permitted
- Height, setback, and dimensional requirements
- Building envelope constraints

Usage:
    python3 scripts/analyze_planning_zones.py
    python3 scripts/analyze_planning_zones.py --output data/planning_zones_summary.json
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import PyPDF2


class PlanningZoneAnalyzer:
    """Analyzes planning zone PDFs for valuation-relevant information"""

    def __init__(self, schemes_dir: Path):
        """
        Initialize analyzer.

        Args:
            schemes_dir: Directory containing planning scheme PDFs
        """
        self.schemes_dir = Path(schemes_dir)
        self.schemes = {}

    def analyze_all_schemes(self) -> Dict[str, Any]:
        """
        Analyze all planning scheme PDFs in the directory.

        Returns:
            Dictionary with analysis results for all schemes
        """
        pdf_files = sorted(self.schemes_dir.glob("*.pdf"))

        if not pdf_files:
            print(f"⚠️  No PDF files found in {self.schemes_dir}")
            return {}

        print(f"\n📄 Found {len(pdf_files)} planning scheme documents\n")

        for pdf_file in pdf_files:
            print(f"🔍 Analyzing: {pdf_file.name}")
            scheme_data = self.analyze_scheme(pdf_file)
            self.schemes[pdf_file.stem] = scheme_data

        return self.create_summary()

    def analyze_scheme(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Analyze a single planning scheme PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with extracted scheme information
        """
        text = self.extract_pdf_text(pdf_path)

        if not text:
            return {
                "file": pdf_path.name,
                "error": "Could not extract text from PDF"
            }

        return {
            "file": pdf_path.name,
            "zone_name": self.extract_zone_name(text, pdf_path.name),
            "purpose": self.extract_purpose(text),
            "table_of_uses": self.extract_table_of_uses(text),
            "building_requirements": self.extract_building_requirements(text),
            "height_restrictions": self.extract_height_restrictions(text),
            "setback_requirements": self.extract_setback_requirements(text),
            "site_requirements": self.extract_site_requirements(text),
            "non_residential_uses": self.extract_non_residential_uses(text),
            "prohibitions": self.extract_prohibitions(text),
            "key_terms": self.extract_key_terms(text),
            "raw_text_length": len(text)
        }

    def extract_pdf_text(self, pdf_path: Path) -> str:
        """Extract all text from PDF file."""
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"  ⚠️  Error reading {pdf_path.name}: {e}")
            return ""

    def extract_zone_name(self, text: str, filename: str) -> str:
        """Extract zone name from text or filename."""
        # Try to find zone name in text
        zone_patterns = [
            r'(Neighbourhood Residential Zone)',
            r'(Low Density Residential)',
            r'(Medium Density Residential)',
            r'(General Residential Zone)',
            r'Clause\s+[\d.]+\s+([A-Z][A-Za-z\s]+Zone)',
        ]

        for pattern in zone_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # Fall back to filename
        return filename.replace('-', ' ').replace('.pdf', '').title()

    def extract_purpose(self, text: str) -> List[str]:
        """Extract zone purpose/objectives."""
        purposes = []

        # Look for purpose section
        purpose_patterns = [
            r'Purpose[:\s]+(.*?)(?=\n\s*\n|\n[A-Z]|\Z)',
            r'(?:Zone\s+)?[Pp]urpose[:\s]+(.*?)(?=Table|Permit|Decision|Application|\Z)',
            r'[Tt]o\s+(implement[^.]+\.|provide[^.]+\.|encourage[^.]+\.)',
        ]

        for pattern in purpose_patterns:
            matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                purpose_text = match.group(1).strip()
                # Split into bullet points
                points = re.split(r'\n+\s*[•▪▸-]\s*|\n+\s*To\s+', purpose_text)
                for point in points:
                    point = point.strip()
                    if len(point) > 20 and len(point) < 500:
                        purposes.append(point)

        return purposes[:10]  # Limit to first 10 purposes

    def extract_table_of_uses(self, text: str) -> Dict[str, List[str]]:
        """Extract table of uses showing permitted/conditional/prohibited uses."""
        uses = {
            "section_1_uses": [],
            "section_2_uses": [],
            "section_3_uses": [],
            "permit_required": [],
            "permit_not_required": [],
            "prohibited": []
        }

        # Look for use sections
        # Section 1 - typically permit not required
        section1_match = re.search(
            r'Section\s+1[:\s\-]+[^\n]*\n(.*?)(?=Section\s+[23]|\Z)',
            text, re.DOTALL | re.IGNORECASE
        )
        if section1_match:
            section1_text = section1_match.group(1)
            section1_uses = self.parse_use_list(section1_text)
            uses["section_1_uses"] = section1_uses
            uses["permit_not_required"].extend(section1_uses)

        # Section 2 - typically permit required
        section2_match = re.search(
            r'Section\s+2[:\s\-]+[^\n]*\n(.*?)(?=Section\s+3|\Z)',
            text, re.DOTALL | re.IGNORECASE
        )
        if section2_match:
            section2_text = section2_match.group(1)
            section2_uses = self.parse_use_list(section2_text)
            uses["section_2_uses"] = section2_uses
            uses["permit_required"].extend(section2_uses)

        # Section 3 - typically prohibited
        section3_match = re.search(
            r'Section\s+3[:\s\-]+[^\n]*\n(.*?)(?=\n\s*\n[A-Z]|\Z)',
            text, re.DOTALL | re.IGNORECASE
        )
        if section3_match:
            section3_text = section3_match.group(1)
            section3_uses = self.parse_use_list(section3_text)
            uses["section_3_uses"] = section3_uses
            uses["prohibited"].extend(section3_uses)

        return uses

    def parse_use_list(self, text: str) -> List[str]:
        """Parse a list of uses from text."""
        uses = []

        # Look for bullet points or line items
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            # Remove bullet points and numbering
            line = re.sub(r'^[•▪▸\-\d.]+\s*', '', line)
            # Skip empty lines and very short lines
            if len(line) < 3 or len(line) > 100:
                continue
            # Skip lines that look like headings
            if re.match(r'^[A-Z\s]{10,}$', line):
                continue
            # Add use if it looks valid
            if line and not line.startswith('Section'):
                uses.append(line)

        return uses[:50]  # Limit to 50 uses

    def extract_building_requirements(self, text: str) -> Dict[str, Any]:
        """Extract building and design requirements."""
        requirements = {}

        # Building height
        height_matches = re.finditer(
            r'[Bb]uilding\s+height[:\s]+([^\n]+)',
            text
        )
        for match in height_matches:
            requirements["building_height"] = match.group(1).strip()

        # Street setback
        setback_matches = re.finditer(
            r'[Ss]treet\s+setback[:\s]+([^\n]+)',
            text
        )
        for match in setback_matches:
            requirements["street_setback"] = match.group(1).strip()

        # Site coverage
        coverage_matches = re.finditer(
            r'[Ss]ite\s+coverage[:\s]+([^\n]+)',
            text
        )
        for match in coverage_matches:
            requirements["site_coverage"] = match.group(1).strip()

        # Permeability
        perm_matches = re.finditer(
            r'[Pp]ermeab(?:le|ility)[:\s]+([^\n]+)',
            text
        )
        for match in perm_matches:
            requirements["permeability"] = match.group(1).strip()

        return requirements

    def extract_height_restrictions(self, text: str) -> List[Dict[str, str]]:
        """Extract height restrictions and requirements."""
        restrictions = []

        # Look for height mentions with numbers
        height_patterns = [
            r'(?:maximum\s+)?height[:\s]+(?:of\s+)?([0-9.]+\s*(?:metres?|m)\b[^\n]*)',
            r'(?:not\s+)?exceed[:\s]+([0-9.]+\s*(?:metres?|m)\b[^\n]*)',
            r'([0-9.]+\s*(?:metres?|m))[^\n]*height',
        ]

        for pattern in height_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                restriction = {
                    "requirement": match.group(0).strip(),
                    "height": match.group(1).strip()
                }
                # Avoid duplicates
                if restriction not in restrictions:
                    restrictions.append(restriction)

        return restrictions[:10]

    def extract_setback_requirements(self, text: str) -> List[Dict[str, str]]:
        """Extract setback requirements."""
        setbacks = []

        # Look for setback mentions
        setback_patterns = [
            r'(?:street|front|side|rear)\s+setback[:\s]+([0-9.]+\s*(?:metres?|m)\b[^\n]*)',
            r'setback[:\s]+(?:of\s+)?([0-9.]+\s*(?:metres?|m)\b[^\n]*)',
            r'([0-9.]+\s*(?:metres?|m))[^\n]*setback',
        ]

        for pattern in setback_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                setback = {
                    "requirement": match.group(0).strip(),
                    "distance": match.group(1).strip()
                }
                if setback not in setbacks:
                    setbacks.append(setback)

        return setbacks[:15]

    def extract_site_requirements(self, text: str) -> Dict[str, Any]:
        """Extract site-related requirements (lot size, coverage, etc)."""
        requirements = {}

        # Minimum lot size
        lot_patterns = [
            r'minimum\s+lot\s+(?:size|area)[:\s]+([0-9,]+\s*(?:square\s+metres?|m[²2]|sqm)\b)',
            r'lot\s+(?:size|area)[:\s]+(?:of\s+)?([0-9,]+\s*(?:square\s+metres?|m[²2]|sqm)\b)',
        ]
        for pattern in lot_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                requirements["minimum_lot_size"] = match.group(1).strip()
                break

        # Site coverage
        coverage_patterns = [
            r'site\s+coverage[:\s]+(?:of\s+)?([0-9]+%?[^\n]{0,50})',
            r'maximum\s+site\s+coverage[:\s]+([0-9]+%?)',
        ]
        for pattern in coverage_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                requirements["site_coverage"] = match.group(1).strip()
                break

        # Permeability
        perm_patterns = [
            r'permeab(?:le|ility)[:\s]+(?:of\s+)?([0-9]+%?[^\n]{0,50})',
            r'minimum\s+permeab(?:le|ility)[:\s]+([0-9]+%?)',
        ]
        for pattern in perm_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                requirements["permeability"] = match.group(1).strip()
                break

        return requirements

    def extract_non_residential_uses(self, text: str) -> List[str]:
        """Extract non-residential uses that may be permitted."""
        non_res_uses = []

        # Common non-residential uses to look for
        non_res_keywords = [
            'home occupation', 'home business', 'child care',
            'medical centre', 'consulting room', 'office',
            'convenience shop', 'retail', 'food and drink',
            'place of assembly', 'education centre', 'community',
            'bed and breakfast', 'accommodation'
        ]

        for keyword in non_res_keywords:
            # Look for this use in the text
            pattern = rf'\b{re.escape(keyword)}\b[^\n]*'
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                use_text = match.group(0).strip()
                # Check if it's in section 1 or 2 (not prohibited)
                if use_text and 'section 3' not in text[max(0, match.start()-200):match.end()].lower():
                    non_res_uses.append(use_text)

        # Remove duplicates while preserving order
        seen = set()
        unique_uses = []
        for use in non_res_uses:
            use_lower = use.lower()
            if use_lower not in seen:
                seen.add(use_lower)
                unique_uses.append(use)

        return unique_uses[:20]

    def extract_prohibitions(self, text: str) -> List[str]:
        """Extract prohibited uses and restrictions."""
        prohibitions = []

        # Look for prohibition keywords
        prohibition_patterns = [
            r'prohibited[:\s]+([^\n]+)',
            r'must\s+not\s+(?:be\s+)?([^\n]+)',
            r'no\s+permit[^\n]+for\s+([^\n]+)',
        ]

        for pattern in prohibition_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                prohibition = match.group(1).strip()
                if len(prohibition) > 10 and len(prohibition) < 200:
                    prohibitions.append(prohibition)

        return prohibitions[:10]

    def extract_key_terms(self, text: str) -> Dict[str, int]:
        """Extract and count key valuation-relevant terms."""
        key_terms = {
            'dwelling': 0,
            'residential': 0,
            'subdivision': 0,
            'permit': 0,
            'height': 0,
            'setback': 0,
            'lot': 0,
            'building': 0,
            'site': 0,
            'use': 0
        }

        text_lower = text.lower()
        for term in key_terms:
            key_terms[term] = len(re.findall(rf'\b{term}\b', text_lower))

        return key_terms

    def create_summary(self) -> Dict[str, Any]:
        """Create final summary report."""
        return {
            "metadata": {
                "total_schemes_analyzed": len(self.schemes),
                "schemes_directory": str(self.schemes_dir),
            },
            "schemes": self.schemes,
            "valuer_summary": self.generate_valuer_summary()
        }

    def generate_valuer_summary(self) -> Dict[str, Any]:
        """Generate valuer-focused summary across all schemes."""
        summary = {
            "residential_zones_analyzed": len(self.schemes),
            "common_restrictions": self.find_common_restrictions(),
            "height_range": self.get_height_range(),
            "non_residential_opportunities": self.summarize_non_residential(),
            "key_considerations": self.generate_key_considerations()
        }
        return summary

    def find_common_restrictions(self) -> List[str]:
        """Find restrictions common across multiple schemes."""
        common = []

        # Check for height restrictions
        height_count = sum(1 for s in self.schemes.values()
                          if s.get('height_restrictions'))
        if height_count > 0:
            common.append(f"Height restrictions found in {height_count}/{len(self.schemes)} zones")

        # Check for setback requirements
        setback_count = sum(1 for s in self.schemes.values()
                           if s.get('setback_requirements'))
        if setback_count > 0:
            common.append(f"Setback requirements found in {setback_count}/{len(self.schemes)} zones")

        return common

    def get_height_range(self) -> Dict[str, Any]:
        """Get range of height restrictions across schemes."""
        heights = []

        for scheme in self.schemes.values():
            height_restrictions = scheme.get('height_restrictions', [])
            for restriction in height_restrictions:
                height_str = restriction.get('height', '')
                # Extract numeric value
                match = re.search(r'([0-9.]+)', height_str)
                if match:
                    heights.append(float(match.group(1)))

        if heights:
            return {
                "min_metres": min(heights),
                "max_metres": max(heights),
                "average_metres": round(sum(heights) / len(heights), 1)
            }
        return {}

    def summarize_non_residential(self) -> Dict[str, Any]:
        """Summarize non-residential use opportunities."""
        all_uses = []

        for scheme in self.schemes.values():
            non_res = scheme.get('non_residential_uses', [])
            all_uses.extend(non_res)

        # Count frequency
        from collections import Counter
        use_counter = Counter([use.lower() for use in all_uses])

        return {
            "total_opportunities": len(all_uses),
            "unique_use_types": len(use_counter),
            "most_common": [{"use": use, "count": count}
                           for use, count in use_counter.most_common(10)]
        }

    def generate_key_considerations(self) -> List[str]:
        """Generate key considerations for valuers."""
        considerations = [
            "Review specific zone schedule for property-specific variations",
            "Check if property falls under multiple zones or overlays",
            "Verify current permit status and any existing use rights",
            "Consider non-residential use potential for value-add opportunities",
            "Assess building envelope constraints on development potential"
        ]
        return considerations


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Analyze planning zones for residential valuation insights',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--input-dir',
        type=str,
        default='data/planning_scheme',
        help='Directory containing planning scheme PDFs (default: data/planning_scheme)'
    )

    parser.add_argument(
        '--output',
        type=str,
        default='data/planning_zones_summary.json',
        help='Output JSON file path (default: data/planning_zones_summary.json)'
    )

    args = parser.parse_args()

    try:
        print("\n" + "=" * 70)
        print("PLANNING ZONE ANALYZER FOR RESIDENTIAL VALUERS")
        print("=" * 70)

        # Initialize analyzer
        analyzer = PlanningZoneAnalyzer(args.input_dir)

        # Analyze all schemes
        summary = analyzer.analyze_all_schemes()

        if not summary:
            print("\n❌ No schemes analyzed")
            sys.exit(1)

        # Save to JSON
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\n✅ Analysis complete!")
        print(f"📁 Summary saved to: {output_path}")

        # Print brief summary
        print("\n" + "=" * 70)
        print("SUMMARY FOR VALUERS")
        print("=" * 70)

        valuer_summary = summary.get('valuer_summary', {})
        print(f"\n📊 Zones Analyzed: {valuer_summary.get('residential_zones_analyzed', 0)}")

        print("\n🔒 Common Restrictions:")
        for restriction in valuer_summary.get('common_restrictions', []):
            print(f"   • {restriction}")

        height_range = valuer_summary.get('height_range', {})
        if height_range:
            print(f"\n📏 Height Restrictions Range:")
            print(f"   Min: {height_range.get('min_metres')}m")
            print(f"   Max: {height_range.get('max_metres')}m")
            print(f"   Avg: {height_range.get('average_metres')}m")

        non_res = valuer_summary.get('non_residential_opportunities', {})
        if non_res.get('total_opportunities', 0) > 0:
            print(f"\n🏢 Non-Residential Opportunities: {non_res.get('total_opportunities')}")
            print(f"   Unique Use Types: {non_res.get('unique_use_types')}")

        print("\n💡 Key Considerations:")
        for consideration in valuer_summary.get('key_considerations', []):
            print(f"   • {consideration}")

        print("\n" + "=" * 70)
        print(f"\n📄 Full details available in: {output_path}\n")

        sys.exit(0)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
