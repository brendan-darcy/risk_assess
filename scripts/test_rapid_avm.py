#!/usr/bin/env python3
"""
Test script to check if Rapid Search API supports AVM data via displayedListings parameter.

Similar to how displayedListings: ['propertyCampaigns'] returns campaign data,
this script tests if displayedListings accepts AVM-related values like:
- 'corelogicAVM'
- 'propertyBureau'
- 'avm'
- 'valuation'
- 'intellival'

Usage:
    python3 scripts/test_rapid_avm.py

Author: ARMATech Development Team
Date: 2025-11-10
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.corelogic_auth import CoreLogicAuth
import requests


def test_displayed_listings_option(auth: CoreLogicAuth, option: str, lat: float, lon: float):
    """
    Test a specific displayedListings option to see if it returns AVM data.

    Args:
        auth: CoreLogicAuth instance
        option: displayedListings value to test (e.g., 'corelogicAVM')
        lat: Latitude for search
        lon: Longitude for search

    Returns:
        Dict with test results
    """
    # Rapid Search uses its own base URL
    base_url = "https://rapid-search-api-uat.ad.corelogic.asia"
    url = f"{base_url}/batchSearch/au"

    request_body = {
        'requests': [{
            'filter': {
                'lat': lat,
                'lon': lon,
                'radius': 0.5  # Small radius for quick test
            },
            'resultsFormat': {
                'limit': 1,  # Just need 1 property to test
                'distinctFields': ['id', 'addressComplete'],
                'displayedListings': [option]  # Test this option
            }
        }]
    }

    headers = {
        'Authorization': f'Bearer {auth.get_access_token()}',
        'Content-Type': 'application/json'
    }

    print(f"\n{'='*70}")
    print(f"Testing displayedListings: ['{option}']")
    print(f"{'='*70}")

    try:
        response = requests.post(url, json=request_body, headers=headers)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # Check response structure
            print(f"\n✓ Request succeeded!")
            print(f"Response keys: {list(data.keys())}")

            # Look for the first request's response
            if 'data' in data and len(data['data']) > 0:
                first_batch = data['data'][0]
                print(f"\nFirst batch keys: {list(first_batch.keys())}")

                if 'properties' in first_batch and len(first_batch['properties']) > 0:
                    first_prop = first_batch['properties'][0]
                    print(f"\nFirst property keys ({len(first_prop.keys())} fields):")

                    # Look for AVM-related fields
                    avm_fields = [k for k in first_prop.keys() if any(term in k.lower()
                                  for term in ['avm', 'valuation', 'estimate', 'intellival', 'bureau'])]

                    if avm_fields:
                        print(f"\n🎯 FOUND AVM-RELATED FIELDS:")
                        for field in avm_fields:
                            print(f"  {field}: {first_prop[field]}")
                        return {'option': option, 'status': 'SUCCESS', 'avm_fields': avm_fields, 'data': first_prop}
                    else:
                        print(f"\n❌ No AVM fields found. Available fields:")
                        for key in sorted(first_prop.keys()):
                            print(f"  - {key}")
                        return {'option': option, 'status': 'NO_AVM_FIELDS', 'available_fields': list(first_prop.keys())}

            return {'option': option, 'status': 'SUCCESS_BUT_NO_PROPERTIES'}

        elif response.status_code == 400:
            error_data = response.json() if response.text else {}
            print(f"\n❌ Bad Request (400)")
            print(f"Error: {json.dumps(error_data, indent=2)}")
            return {'option': option, 'status': 'BAD_REQUEST', 'error': error_data}

        elif response.status_code == 401:
            print(f"\n❌ Unauthorized (401) - Auth token issue")
            return {'option': option, 'status': 'UNAUTHORIZED'}

        else:
            print(f"\n❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return {'option': option, 'status': f'HTTP_{response.status_code}'}

    except Exception as e:
        print(f"\n❌ Exception occurred: {e}")
        return {'option': option, 'status': 'EXCEPTION', 'error': str(e)}


def main():
    print("\n" + "="*70)
    print("RAPID SEARCH AVM FIELD DISCOVERY TEST")
    print("="*70)
    print("\nTesting if Rapid Search API supports AVM data via displayedListings...")
    print("Location: 5 Settlers Court, Vermont South VIC 3133")

    # Initialize auth
    try:
        auth = CoreLogicAuth.from_env()
    except Exception as e:
        print(f"\n❌ Failed to initialize auth: {e}")
        print("\nPlease ensure UAT credentials are configured in .env:")
        print("  CORELOGIC_CLIENT_ID_UAT=...")
        print("  CORELOGIC_CLIENT_SECRET_UAT=...")
        sys.exit(1)

    # Known coordinates for 5 Settlers Court
    lat = -37.85878503
    lon = 145.18689565

    # Test various displayedListings options
    options_to_test = [
        'corelogicAVM',
        'propertyBureau',
        'avm',
        'valuation',
        'intellival',
        'IntelliVal',
        'estimate',
        'automated_valuation',
        'marketValue',
        'currentValue'
    ]

    results = []

    for option in options_to_test:
        result = test_displayed_listings_option(auth, option, lat, lon)
        results.append(result)

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    success_with_avm = [r for r in results if r['status'] == 'SUCCESS' and 'avm_fields' in r]
    success_no_avm = [r for r in results if r['status'] in ['SUCCESS_BUT_NO_PROPERTIES', 'NO_AVM_FIELDS']]
    failed = [r for r in results if r['status'] not in ['SUCCESS', 'SUCCESS_BUT_NO_PROPERTIES', 'NO_AVM_FIELDS']]

    if success_with_avm:
        print(f"\n✅ FOUND AVM SUPPORT! ({len(success_with_avm)} option(s)):")
        for r in success_with_avm:
            print(f"  - displayedListings: ['{r['option']}']")
            print(f"    AVM Fields: {r['avm_fields']}")
    else:
        print(f"\n❌ No AVM support found")

    if success_no_avm:
        print(f"\n⚠️  Successful but no AVM fields ({len(success_no_avm)} option(s)):")
        for r in success_no_avm:
            print(f"  - '{r['option']}': {r['status']}")

    if failed:
        print(f"\n❌ Failed requests ({len(failed)} option(s)):")
        for r in failed:
            print(f"  - '{r['option']}': {r['status']}")

    # Save detailed results
    output_file = Path('data/property_reports/rapid_avm_test_results.json')
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump({
            'test_info': {
                'location': '5 Settlers Court, Vermont South VIC 3133',
                'lat': lat,
                'lon': lon,
                'options_tested': options_to_test
            },
            'results': results
        }, f, indent=2)

    print(f"\n✓ Detailed results saved: {output_file}")
    print("\n" + "="*70)


if __name__ == '__main__':
    main()
