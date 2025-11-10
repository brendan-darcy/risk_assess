#!/usr/bin/env python3
"""
Enhanced VSCode Extension Security Audit Script
Features:
- Marketplace API checks (ratings, downloads)
- Permission analysis from package.json
- Known malicious extension database
- Comprehensive threat scoring
"""

import os
import json
import subprocess
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Known malicious extension patterns (updated regularly)
KNOWN_THREATS = {
    # Format: "publisher.name": "reason"
    # Add known malicious extensions here
}

# Suspicious patterns in extension names
SUSPICIOUS_PATTERNS = [
    'crack', 'keygen', 'nulled', 'pirate', 'warez',
    'hack', 'exploit', 'backdoor', 'trojan'
]

# Whitelisted extensions (approved for use)
# Extensions not on this list require management approval
WHITELISTED_EXTENSIONS = [
    'anthropic.claude-code',
    'databricks.databricks',
    'github.copilot',
    'github.copilot-chat',
    'github.remotehub',
    'mechatroner.rainbow-csv',
    'ms-python.debugpy',
    'ms-python.python',
    'ms-python.vscode-pylance',
    'ms-python.vscode-python-envs',
    'ms-toolsai.jupyter',
    'ms-toolsai.jupyter-keymap',
    'ms-toolsai.jupyter-renderers',
    'ms-toolsai.vscode-jupyter-cell-tags',
    'ms-toolsai.vscode-jupyter-slideshow',
    'ms-vscode.azure-repos',
    'ms-vscode.makefile-tools',
    'ms-vscode.remote-repositories',
    'postman.postman-for-vscode',
    'redhat.vscode-yaml',
    'saoudrizwan.claude-dev',
]

# High-risk permissions
HIGH_RISK_PERMISSIONS = {
    'workspace.fs': 'File system access (read/write files)',
    'workspace.rootPath': 'Access to workspace root',
    'env.': 'Environment variable access',
    'executeCommand': 'Execute VSCode commands',
    'webview': 'Create webviews (can run arbitrary JS)',
}

class ExtensionAnalyzer:
    def __init__(self):
        self.extensions = []
        self.marketplace_cache = {}

    def find_extensions(self):
        """Find all installed extensions"""
        # Try using code command first
        extensions = self._get_from_code_command()
        if not extensions:
            extensions = self._get_from_directory()

        return extensions

    def _get_from_code_command(self):
        """Get extensions using code command"""
        code_paths = [
            "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code",
            "/usr/local/bin/code",
        ]

        for code_path in code_paths:
            if os.path.exists(code_path):
                try:
                    result = subprocess.run(
                        [code_path, '--list-extensions', '--show-versions'],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        extensions = []
                        for line in result.stdout.strip().split('\n'):
                            if '@' in line:
                                full_name, version = line.split('@')
                                extensions.append({
                                    'id': full_name,
                                    'version': version,
                                    'path': None
                                })
                        return extensions
                except Exception as e:
                    continue
        return None

    def _get_from_directory(self):
        """Get extensions from directory"""
        ext_dirs = [
            Path.home() / ".vscode" / "extensions",
            Path.home() / ".vscode-insiders" / "extensions",
        ]

        extensions = []
        for ext_dir in ext_dirs:
            if ext_dir.exists():
                for item in ext_dir.iterdir():
                    if item.is_dir() and not item.name.startswith('.'):
                        # Parse publisher.name-version format
                        name = item.name
                        if '-' in name:
                            parts = name.rsplit('-', 1)
                            ext_id = parts[0]
                            version = parts[1] if len(parts) > 1 else "unknown"

                            extensions.append({
                                'id': ext_id,
                                'version': version,
                                'path': str(item)
                            })
        return extensions

    def check_marketplace(self, ext_id: str) -> Optional[Dict]:
        """Check extension on VS Code Marketplace"""
        if ext_id in self.marketplace_cache:
            return self.marketplace_cache[ext_id]

        try:
            # VS Code Marketplace API
            url = f"https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery"

            payload = {
                "filters": [{
                    "criteria": [{"filterType": 7, "value": ext_id}],
                    "pageNumber": 1,
                    "pageSize": 1,
                    "sortBy": 0,
                    "sortOrder": 0
                }],
                "flags": 914
            }

            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json;api-version=3.0-preview.1'
            }

            response = requests.post(url, json=payload, headers=headers, timeout=5)

            if response.status_code == 200:
                data = response.json()
                if data.get('results') and data['results'][0].get('extensions'):
                    ext_data = data['results'][0]['extensions'][0]

                    # Extract key metrics
                    stats = ext_data.get('statistics', [])
                    rating_count = next((s['value'] for s in stats if s['statisticName'] == 'ratingcount'), 0)
                    avg_rating = next((s['value'] for s in stats if s['statisticName'] == 'averagerating'), 0)
                    install_count = next((s['value'] for s in stats if s['statisticName'] == 'install'), 0)

                    result = {
                        'rating': avg_rating,
                        'rating_count': rating_count,
                        'installs': install_count,
                        'last_updated': ext_data.get('lastUpdated'),
                        'publisher': ext_data.get('publisher', {}).get('displayName'),
                        'verified': ext_data.get('publisher', {}).get('isDomainVerified', False)
                    }

                    self.marketplace_cache[ext_id] = result
                    return result
        except Exception as e:
            # Silently fail - marketplace checks are nice-to-have
            pass

        return None

    def analyze_permissions(self, ext_path: str) -> Dict:
        """Analyze extension permissions from package.json"""
        if not ext_path:
            return {}

        package_json = Path(ext_path) / "package.json"
        if not package_json.exists():
            return {}

        try:
            with open(package_json, 'r') as f:
                manifest = json.load(f)

            permissions = {
                'activation_events': manifest.get('activationEvents', []),
                'contributes': list(manifest.get('contributes', {}).keys()),
                'main': manifest.get('main'),
                'scripts': list(manifest.get('scripts', {}).keys()) if manifest.get('scripts') else []
            }

            return permissions
        except Exception:
            return {}

    def calculate_threat_score(self, ext_id: str, version: str, path: Optional[str],
                              marketplace_data: Optional[Dict], permissions: Dict) -> Dict:
        """Calculate threat score based on various factors"""
        score = 0
        warnings = []
        quality_warnings = []  # Separate quality issues from security issues

        # Trusted publishers (reduce false positives)
        TRUSTED_PUBLISHERS = ['ms-python', 'ms-toolsai', 'ms-vscode', 'github',
                             'microsoft', 'redhat', 'anthropic', 'databricks']

        publisher = ext_id.split('.')[0] if '.' in ext_id else ""
        is_trusted = publisher.lower() in TRUSTED_PUBLISHERS

        # Check known threats
        if ext_id in KNOWN_THREATS:
            score += 100
            warnings.append(f"CRITICAL: Known malicious extension - {KNOWN_THREATS[ext_id]}")

        # Check suspicious name patterns
        ext_lower = ext_id.lower()
        for pattern in SUSPICIOUS_PATTERNS:
            if pattern in ext_lower:
                score += 20
                warnings.append(f"Suspicious name pattern: '{pattern}'")

        # Check publisher
        if '.' in ext_id:
            if publisher.isdigit():
                score += 30
                warnings.append("Publisher is all numbers (suspicious)")
            elif len(publisher) < 3 and not is_trusted:
                score += 20
                warnings.append("Very short publisher name")

        # Check marketplace data
        if marketplace_data:
            # Low install count is concerning for unknown publishers
            if marketplace_data['installs'] < 100 and not is_trusted:
                score += 15
                warnings.append(f"Very low install count: {marketplace_data['installs']}")

            # Poor rating is a QUALITY issue, not a SECURITY issue for trusted publishers
            if marketplace_data['rating_count'] > 0 and marketplace_data['rating'] < 2.0:
                if is_trusted or marketplace_data['verified']:
                    # Don't penalize trusted publishers for poor quality
                    quality_warnings.append(f"Poor user rating: {marketplace_data['rating']:.1f}/5 (quality issue, not security)")
                else:
                    # For untrusted publishers, poor rating could indicate malware
                    score += 25
                    warnings.append(f"Poor rating from unverified publisher: {marketplace_data['rating']:.1f}/5")

            # Unverified publisher is only concerning for unknown publishers
            if not marketplace_data['verified'] and not is_trusted:
                score += 10
                warnings.append("Publisher not verified")
        else:
            if not is_trusted:
                score += 5
                warnings.append("Could not verify on marketplace")

        # Check permissions
        if permissions:
            activation = permissions.get('activation_events', [])

            # Check for risky activation events
            if '*' in activation or 'onStartupFinished' in activation:
                if not is_trusted:
                    score += 15
                    warnings.append("Activates on startup (high resource usage)")

            # Check contributes
            contributes = permissions.get('contributes', [])
            if 'commands' in contributes and len(contributes) > 10:
                quality_warnings.append("Contributes many features (complex extension)")

        # Risk levels
        if score >= 50:
            risk = "HIGH"
        elif score >= 25:
            risk = "MEDIUM"
        elif score >= 10:
            risk = "LOW"
        else:
            risk = "MINIMAL"

        return {
            'score': score,
            'risk': risk,
            'warnings': warnings,
            'quality_warnings': quality_warnings,
            'is_trusted': is_trusted
        }

def main():
    print("=" * 70)
    print("Enhanced VSCode Extension Security Audit")
    print("=" * 70)
    print()

    analyzer = ExtensionAnalyzer()
    extensions = analyzer.find_extensions()

    if not extensions:
        print("❌ No extensions found")
        return

    print(f"📦 Analyzing {len(extensions)} extensions...")
    print()

    # Analyze each extension
    results = []
    for ext in extensions:
        ext_id = ext['id']
        print(f"  Checking {ext_id}...", end='\r')

        marketplace_data = analyzer.check_marketplace(ext_id)
        permissions = analyzer.analyze_permissions(ext['path']) if ext['path'] else {}
        threat_analysis = analyzer.calculate_threat_score(
            ext_id, ext['version'], ext['path'], marketplace_data, permissions
        )

        results.append({
            'ext': ext,
            'marketplace': marketplace_data,
            'permissions': permissions,
            'threat': threat_analysis
        })

    print(" " * 70)  # Clear the progress line
    print()

    # Display results
    print("=" * 70)
    print("SECURITY ANALYSIS RESULTS")
    print("=" * 70)
    print()

    # Group by risk level
    high_risk = [r for r in results if r['threat']['risk'] == 'HIGH']
    medium_risk = [r for r in results if r['threat']['risk'] == 'MEDIUM']
    low_risk = [r for r in results if r['threat']['risk'] == 'LOW']
    minimal_risk = [r for r in results if r['threat']['risk'] == 'MINIMAL']

    if high_risk:
        print("🚨 HIGH RISK EXTENSIONS (SECURITY CONCERN)")
        print("-" * 70)
        for r in high_risk:
            ext = r['ext']
            print(f"\n  ⚠️  {ext['id']} ({ext['version']})")
            print(f"      Threat Score: {r['threat']['score']}")
            for warning in r['threat']['warnings']:
                print(f"      - {warning}")
            if r['marketplace']:
                print(f"      Installs: {r['marketplace']['installs']:,}")
                print(f"      Rating: {r['marketplace']['rating']:.1f}/5 ({r['marketplace']['rating_count']} reviews)")
        print()

    if medium_risk:
        print("⚠️  MEDIUM RISK EXTENSIONS (SECURITY CONCERN)")
        print("-" * 70)
        for r in medium_risk:
            ext = r['ext']
            print(f"\n  ⚡ {ext['id']} ({ext['version']})")
            print(f"      Threat Score: {r['threat']['score']}")
            if r['threat']['is_trusted']:
                print(f"      ✓ From trusted publisher")
            for warning in r['threat']['warnings'][:3]:  # Show top 3 warnings
                print(f"      - {warning}")
        print()

    # Show quality warnings separately
    quality_issues = [r for r in results if r['threat'].get('quality_warnings')]
    if quality_issues:
        print("📊 QUALITY ISSUES (Not Security Threats)")
        print("-" * 70)
        for r in quality_issues:
            ext = r['ext']
            print(f"\n  ℹ️  {ext['id']} ({ext['version']})")
            if r['threat']['is_trusted']:
                print(f"      ✓ From trusted publisher (verified)")
            for warning in r['threat']['quality_warnings']:
                print(f"      - {warning}")
        print()

    # Check for unapproved extensions (not on whitelist)
    unapproved = [r for r in results if r['ext']['id'] not in WHITELISTED_EXTENSIONS]
    if unapproved:
        print("🔒 UNAPPROVED EXTENSIONS (Require Management Approval)")
        print("-" * 70)
        for r in unapproved:
            ext = r['ext']
            print(f"\n  🚫 {ext['id']} ({ext['version']})")
            print(f"      Status: NOT ON APPROVED LIST")
            print(f"      Risk Level: {r['threat']['risk']} (Threat Score: {r['threat']['score']})")
            if r['marketplace']:
                print(f"      Publisher: {r['marketplace']['publisher']}")
                if r['marketplace']['verified']:
                    print(f"      ✓ Verified publisher")
                print(f"      Installs: {r['marketplace']['installs']:,}")
                print(f"      Rating: {r['marketplace']['rating']:.1f}/5")
            if r['threat']['warnings']:
                print(f"      Security Concerns:")
                for warning in r['threat']['warnings'][:3]:
                    print(f"        - {warning}")
            print(f"      ⚠️  ACTION REQUIRED: Obtain management approval or uninstall")
        print()

    print("✅ LOW/MINIMAL RISK EXTENSIONS")
    print("-" * 70)
    safe_count = len(low_risk) + len(minimal_risk)
    print(f"  {safe_count} extensions appear safe")
    print()

    # Summary statistics
    print("=" * 70)
    print("MARKETPLACE STATISTICS")
    print("=" * 70)
    print()

    verified_count = sum(1 for r in results if r['marketplace'] and r['marketplace']['verified'])
    avg_rating = sum(r['marketplace']['rating'] for r in results if r['marketplace']) / len([r for r in results if r['marketplace']])
    total_installs = sum(r['marketplace']['installs'] for r in results if r['marketplace'])

    print(f"  Verified Publishers: {verified_count}/{len(results)}")
    print(f"  Average Rating: {avg_rating:.2f}/5")
    print(f"  Total Installs: {total_installs:,}")
    print()

    # Recommendations
    print("=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    print()

    if high_risk:
        print("  🚨 IMMEDIATE ACTION REQUIRED:")
        print("     - Review and uninstall HIGH RISK extensions")
        print("     - Check for similar legitimate alternatives")
        print()

    if medium_risk:
        print("  ⚠️  SUGGESTED ACTIONS:")
        print("     - Review MEDIUM RISK extensions carefully")
        print("     - Check marketplace reviews and ratings")
        print("     - Consider if you actually use these extensions")
        print()

    # Count unapproved extensions
    unapproved_count = len([r for r in results if r['ext']['id'] not in WHITELISTED_EXTENSIONS])
    if unapproved_count > 0:
        print("  🔒 UNAPPROVED EXTENSIONS DETECTED:")
        print(f"     - Found {unapproved_count} extension(s) not on approved list")
        print("     - Obtain management approval before using")
        print("     - Document business justification")
        print("     - Consider security implications")
        print("     - Uninstall if not business-critical")
        print()

    print("  📋 GENERAL SECURITY PRACTICES:")
    print("     - Keep extensions updated")
    print("     - Remove unused extensions")
    print("     - Review permissions before installing")
    print("     - Only install from trusted publishers")
    print("     - Check marketplace ratings and reviews")
    print()

    # Save detailed report
    report_path = "/tmp/vscode_security_audit.json"
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"  💾 Detailed report saved: {report_path}")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Audit interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
