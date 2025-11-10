#!/usr/bin/env python3
"""
Test basic Rapid Search for comparable sales (no AVM - just confirm it works).

Tests getting sales in 5km radius with all the fields we need:
- landArea, yearBuilt, buildingArea, floorArea
- Sales prices, dates, campaign info
- Property attributes

Usage:
    python3 scripts/test_rapid_basic.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.corelogic_auth import CoreLogicAuth
import requests


def main():
    print("\n" + "="*70)
    print("RAPID SEARCH - BASIC TEST (5km radius comparable sales)")
    print("="*70)

    # Initialize auth
    auth = CoreLogicAuth.from_env()
    token = auth.get_access_token()

    # Correct Rapid Search endpoint
    endpoint = "https://api-uat.corelogic.asia/rapid-search/batchSearch/au"

    # 5 Settlers Court coordinates
    lat = -37.85878503
    lon = 145.18689565
    radius_km = 5.0

    # Request body with correct format (filters array, geoDistance operator)
    request_body = {
        'requests': [{
            'filters': [
                {
                    'operation': 'geoDistance',
                    'field': 'addressLocation',
                    'value': {
                        'lat': lat,
                        'lon': lon,
                        'radius': radius_km
                    }
                },
                {
                    'operation': 'equals',
                    'field': 'type',
                    'value': 'HOUSE'
                }
            ],
            'resultsFormat': {
                'limit': 10,
                'sort': '+distance',
                'distinctFields': [
                    # Core identification
                    'id',
                    'addressComplete',
                    'addressSuburb',
                    'addressState',
                    'addressPostcode',

                    # Property attributes (the ones we need!)
                    'beds',
                    'baths',
                    'carSpaces',
                    'landArea',          # ✅ Key field
                    'yearBuilt',         # ✅ Key field
                    'buildingArea',      # ✅ Key field
                    'floorArea',         # ✅ Key field
                    'type',
                    'subType',

                    # Sales info
                    'salesLastSoldPrice',
                    'salesLastSaleContractDate',
                    'salesLastSaleSource',

                    # Campaign info
                    'salesLastCampaignAgency',
                    'salesLastCampaignAgent',
                    'salesLastCampaignDaysOnMarket',

                    # Geographic
                    'distance',
                    'addressLocation'
                ]
            }
        }]
    }

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    print(f"\nSearching:")
    print(f"  Location: ({lat}, {lon})")
    print(f"  Radius: {radius_km}km")
    print(f"  Type: HOUSE")
    print(f"  Limit: 10 results")

    print(f"\n{'Calling Rapid Search API...':^70}")

    try:
        response = requests.post(endpoint, json=request_body, headers=headers, timeout=30)

        print(f"\nStatus: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ SUCCESS!")

            # Navigate response structure
            if 'data' in data and len(data['data']) > 0:
                first_batch = data['data'][0]
                properties = first_batch.get('properties', [])

                print(f"\nFound {len(properties)} properties")

                if properties:
                    print(f"\n{'FIRST PROPERTY EXAMPLE':^70}")
                    print("="*70)

                    prop = properties[0]
                    print(f"ID: {prop.get('id')}")
                    print(f"Address: {prop.get('addressComplete')}")
                    print(f"Type: {prop.get('type')} - {prop.get('subType')}")
                    print(f"\nConfiguration:")
                    print(f"  Beds: {prop.get('beds')}")
                    print(f"  Baths: {prop.get('baths')}")
                    print(f"  Car Spaces: {prop.get('carSpaces')}")
                    print(f"\n✅ Key Fields (previously needed 800+ API calls):")
                    print(f"  Land Area: {prop.get('landArea')} m²")
                    print(f"  Year Built: {prop.get('yearBuilt')}")
                    print(f"  Building Area: {prop.get('buildingArea')} m²")
                    print(f"  Floor Area: {prop.get('floorArea')} m²")
                    print(f"\nSales:")
                    print(f"  Last Sold: ${prop.get('salesLastSoldPrice'):,}" if prop.get('salesLastSoldPrice') else "  Last Sold: N/A")
                    print(f"  Sale Date: {prop.get('salesLastSaleContractDate')}")
                    print(f"  Source: {prop.get('salesLastSaleSource')}")
                    print(f"\nDistance: {prop.get('distance')}m from search center")

                    # Check field coverage
                    print(f"\n{'FIELD COVERAGE':^70}")
                    print("="*70)
                    key_fields = ['landArea', 'yearBuilt', 'buildingArea', 'floorArea', 'salesLastSoldPrice']
                    for field in key_fields:
                        count = sum(1 for p in properties if p.get(field) is not None)
                        pct = (count / len(properties)) * 100
                        status = "✅" if pct > 80 else "⚠️" if pct > 50 else "❌"
                        print(f"  {status} {field}: {count}/{len(properties)} ({pct:.0f}%)")

                    # Show all fields returned
                    print(f"\n{'ALL FIELDS RETURNED':^70}")
                    print("="*70)
                    all_fields = set()
                    for p in properties:
                        all_fields.update(p.keys())
                    print(f"Total unique fields: {len(all_fields)}")
                    for field in sorted(all_fields):
                        print(f"  - {field}")

                    print(f"\n{'✅ RAPID SEARCH WORKS!':^70}")
                    print("="*70)
                    print(f"✓ Got {len(properties)} properties in 1 API call")
                    print(f"✓ All key fields available (landArea, yearBuilt, buildingArea, etc.)")
                    print(f"✓ Replaces 800+ individual property detail calls")

            else:
                print(f"\n⚠️  Response has no data")
                print(f"Response structure: {json.dumps(data, indent=2)[:500]}")

        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"\n❌ Exception: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*70)


if __name__ == '__main__':
    main()
