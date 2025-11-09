#!/usr/bin/env python3
"""
Single Property Sales History and Median AVM Analysis

Simple script that uses CoreLogicProcessor to:
1. Get property sales history
2. Get median AVM for the last sale month
3. Export results to JSON

Example usage:
source venv/bin/activate
python3 scripts/single_address.py --address "4 Clifton Court, Somers, VIC 3927"
python3 scripts/single_address.py --address "3 Nymboida Street, South Coogee, NSW, 2034"
python3 scripts/single_address.py --address "42 Thackeray Street, Norman Park QLD, 4170"
python3 scripts/single_address.py --address "3 Tango Close, Jordan Springs, NSW, 2747"


"""

import sys
import argparse
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

from utils.property_data_processor import PropertyDataProcessor
from utils.market_data_processor import MarketDataProcessor
from utils.pipeline_utils import ProgressReporter, index_value_to_date


def analyze_property(address: str, output_file: str = None) -> str:
    """
    Analyze a single property for sales history and median AVM.
    
    Args:
        address: Property address to analyze
        output_file: Output JSON file path (auto-generated if None)
        
    Returns:
        Path to output JSON file
    """
    print(f"🏠 Analyzing property: {address}")
    
    # Initialize processors with reporters
    property_reporter = ProgressReporter("Property Analysis")
    market_reporter = ProgressReporter("Market Data")
    
    property_processor = PropertyDataProcessor(reporter=property_reporter)
    market_processor = MarketDataProcessor(reporter=market_reporter)
    
    # Get property ID
    print("📍 Resolving address...")
    property_id = property_processor.get_property_id_from_address(address)
    if not property_id:
        raise Exception("Property ID not found")
    print(f"✅ Found property ID: {property_id}")
    
    # Get property details and sales history
    print("📋 Fetching property details...")
    property_details = property_processor.get_comprehensive_property_data(property_id)
    
    print("📚 Fetching sales history...")
    sales_history = property_processor.get_property_sales_history(property_id)
    
    # Get median AVM for last sale month
    median_avm_data = {'error': 'No sales history or property details available'}
    market_data = None  # Will hold comprehensive market data if fetched

    print(f"🔍 Debug - sales_history length: {len(sales_history) if sales_history else 0}")
    print(f"🔍 Debug - property_details exists: {property_details is not None}")
    
    if sales_history and property_details:
        try:
            # Get the most recent sale from the saleList
            recent_sale = sales_history[0]['saleList'][0] if sales_history[0].get('saleList') else None
            print(f"🔍 Recent sale keys: {list(recent_sale.keys()) if recent_sale else 'No recent sale'}")
            
            contract_date_str = (recent_sale.get('contractDate') or 
                               recent_sale.get('contract_date') or 
                               recent_sale.get('settlementDate')) if recent_sale else None
            print(f"🔍 Contract date string: {contract_date_str}")
            
            if contract_date_str:
                target_month = datetime.strptime(contract_date_str, '%Y-%m-%d').strftime('%Y-%m')
                
                # Get locality ID for median AVM lookup (like the working example)
                location_id = None
                
                # Try locality ID first (like the working 12666 example)
                if (property_details.get('location', {}).get('locality', {}).get('id')):
                    location_id = property_details['location']['locality']['id']
                    print(f"🔍 Using locality ID: {location_id}")
                # Fallback to postcode ID
                elif (property_details.get('location', {}).get('postcode', {}).get('id')):
                    location_id = property_details['location']['postcode']['id']
                    print(f"🔍 Using postcode ID: {location_id}")
                else:
                    print("🔍 No location ID found")
                
                if location_id:
                    print(f"📊 Fetching comprehensive market data for location ID {location_id} from {target_month} to 2022-03...")

                    # Use the new MarketDataProcessor
                    try:
                        # Fetch comprehensive market data
                        market_data = market_processor.fetch_comprehensive_market_data(
                            location_id=int(location_id),
                            location_type_id=8,  # Suburb level (like the working example)
                            property_type_id=1,  # Houses
                            from_date=f"{target_month}-01",
                            to_date="2022-03-31"
                        )

                        print(f"✅ Retrieved market data with {market_data['summary']['total_data_points']} total data points")

                        # Extract median value data for AVM time series
                        median_value_data = market_data.get('market_indicators', {}).get('median_value', [])

                        if median_value_data:
                            print(f"✅ Retrieved {len(median_value_data)} AVM data points")

                            # Format as time series
                            median_avm_data = {
                                'location_id': location_id,
                                'from_month': target_month,
                                'to_month': '2022-03',
                                'data_points': len(median_value_data),
                                'time_series': [
                                    {
                                        'date': point['date'],
                                        'median_avm': point['value']
                                    } for point in median_value_data
                                ]
                            }
                        else:
                            print("⚠️  No median value data found in results")
                            median_avm_data = {'error': 'No median AVM data available'}

                    except Exception as market_e:
                        print(f"⚠️  Market data processing failed: {market_e}")
                        median_avm_data = {'error': f'Market data processing failed: {market_e}'}
                        market_data = None
                else:
                    print("⚠️  No location ID found for AVM lookup")
                    median_avm_data = {'error': 'No location ID found'}
            else:
                print("⚠️  No contract date found in sales history")
                median_avm_data = {'error': 'No contract date available'}
                
        except Exception as e:
            print(f"🔍 Exception in AVM lookup: {e}")
            median_avm_data = {'error': f'Exception in AVM processing: {e}'}
    
    # Generate market metrics summary if we have market data
    market_metrics_summary = None
    if market_data:
        print("📊 Generating market metrics summary...")
        try:
            market_metrics_summary = market_processor.generate_market_metrics_summary(market_data)
            available_count = market_metrics_summary['summary']['available_metrics']
            total_count = market_metrics_summary['summary']['total_metrics']
            print(f"✅ Market metrics summary: {available_count}/{total_count} metrics available")

            # Show featured metrics if available
            if market_metrics_summary.get('featured_metrics'):
                featured = market_metrics_summary['featured_metrics']
                if 'median_value' in featured:
                    mv = featured['median_value']
                    print(f"   📈 Median Value (AVM): ${mv['last_value']:,.0f} ({mv['growth_percent']:+.1f}% growth)")
                if 'median_sale_price' in featured:
                    msp = featured['median_sale_price']
                    print(f"   💰 Median Sale Price: ${msp['last_value']:,.0f} ({msp['growth_percent']:+.1f}% growth)")
                if 'rental_market' in featured:
                    rm = featured['rental_market']
                    if 'rental_yield' in rm:
                        print(f"   🏠 Rental Yield: {rm['rental_yield']:.2f}%")
                    if 'median_rent' in rm:
                        print(f"   💵 Median Rent: ${rm['median_rent']:,.0f}/week")
        except Exception as e:
            print(f"⚠️  Failed to generate market metrics summary: {e}")
            market_metrics_summary = {'error': f'Summary generation failed: {str(e)}'}

    # Perform indexation if we have both sales data and AVM data
    indexation_data = {'status': 'not_performed', 'reason': 'Missing required data'}
    
    if (property_details and 
        median_avm_data.get('time_series') and 
        len(median_avm_data['time_series']) > 0):
        
        print("📈 Performing price indexation...")
        
        try:
            # Extract last sale information
            last_sale = property_details.get('last_sale', {}).get('lastSale', {})
            
            if last_sale.get('price') and last_sale.get('contractDate'):
                sale_price = last_sale['price']
                sale_date = last_sale['contractDate']
                
                # Use the latest date in the AVM series as target
                avm_series = median_avm_data['time_series']
                target_date = avm_series[-1]['date']  # Latest date
                
                print(f"🔄 Indexing ${sale_price:,} from {sale_date} to {target_date}...")
                
                # Perform indexation
                indexation_result = index_value_to_date(
                    transaction_value=sale_price,
                    transaction_date=sale_date,
                    target_date=target_date,
                    index_series=avm_series
                )
                
                if indexation_result['status'] == 'success':
                    growth_pct = ((indexation_result['indexed_value'] / indexation_result['original_value']) - 1) * 100
                    
                    indexation_data = {
                        'status': 'success',
                        'original_sale': {
                            'price': sale_price,
                            'date': sale_date
                        },
                        'indexed_value': indexation_result['indexed_value'],
                        'target_date': target_date,
                        'index_ratio': indexation_result['index_ratio'],
                        'growth_percentage': growth_pct,
                        'transaction_index': indexation_result['transaction_index'],
                        'target_index': indexation_result['target_index'],
                        'method': indexation_result['method'],
                        'calculation_details': {
                            'description': f"Indexed ${sale_price:,} sale price from {sale_date} to {target_date} using median AVM series",
                            'years_elapsed': (pd.to_datetime(target_date) - pd.to_datetime(sale_date)).days / 365.25,
                            'annualized_growth': (indexation_result['index_ratio'] ** (365.25 / (pd.to_datetime(target_date) - pd.to_datetime(sale_date)).days) - 1) * 100
                        }
                    }
                    
                    print(f"✅ Indexation successful!")
                    print(f"   Original: ${sale_price:,} ({sale_date})")
                    print(f"   Indexed:  ${indexation_result['indexed_value']:,.0f} ({target_date})")
                    print(f"   Growth:   {growth_pct:+.1f}%")
                    
                else:
                    indexation_data = {
                        'status': 'error',
                        'error': indexation_result['error'],
                        'original_sale': {
                            'price': sale_price,
                            'date': sale_date
                        },
                        'target_date': target_date
                    }
                    print(f"❌ Indexation failed: {indexation_result['error']}")
            else:
                indexation_data = {
                    'status': 'not_performed',
                    'reason': 'No valid last sale data found (missing price or date)'
                }
                print("⚠️  No valid last sale data for indexation")
                
        except Exception as e:
            indexation_data = {
                'status': 'error',
                'error': f'Indexation processing failed: {str(e)}'
            }
            print(f"❌ Indexation processing failed: {e}")
    else:
        reasons = []
        if not property_details:
            reasons.append("no property details")
        if not median_avm_data.get('time_series'):
            reasons.append("no AVM time series")
        elif len(median_avm_data['time_series']) == 0:
            reasons.append("empty AVM time series")
            
        indexation_data['reason'] = f"Missing required data: {', '.join(reasons)}"
        print(f"⚠️  Indexation skipped: {indexation_data['reason']}")
    
    # Compile results
    results = {
        'timestamp': datetime.now().isoformat(),
        'input_address': address,
        'property_id': property_id,
        'property_details': property_details,
        'sales_history': sales_history,
        'median_avm': median_avm_data,
        'market_metrics_summary': market_metrics_summary,
        'indexation': indexation_data
    }
    
    # Export to JSON
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"outputs/property_analysis_{timestamp}.json"
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"✅ Results saved to: {output_path}")
    return str(output_path)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Analyze single property for sales history and median AVM')
    parser.add_argument('--address', help='Property address to analyze')
    parser.add_argument('--address-file', help='File containing property address (reads first line)')
    parser.add_argument('--output', help='Output JSON file path (auto-generated if not specified)')
    
    args = parser.parse_args()
    
    # Get address
    address = None
    if args.address:
        address = args.address
    elif args.address_file:
        with open(args.address_file, 'r') as f:
            address = f.readline().strip()
    else:
        print("❌ Please provide either --address or --address-file")
        return 1
    
    if not address:
        print("❌ No address provided")
        return 1
    
    try:
        output_file = analyze_property(address, args.output)
        print(f"\n🎉 Analysis complete! Results: {Path(output_file).name}")
        return 0
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())