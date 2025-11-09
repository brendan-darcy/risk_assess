import pandas as pd
import time
import requests
import json
from typing import List, Dict, Any, Optional, Tuple
import os
from datetime import datetime

class CoreLogicProcessor:
    """A class to handle CoreLogic API processing without the problematic transpose."""
    
    def __init__(self, access_token: str, base_url: str = "https://api-uat.corelogic.asia"):
        self.access_token = access_token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "accept": "application/json"
        }
    
    def read_addresses(self, file_path: str, sample_size: Optional[int] = None) -> List[str]:
        """Read addresses from a text file."""
        with open(file_path, 'r') as f:
            addresses = [line.strip() for line in f if line.strip()]
        
        if sample_size:
            return addresses[:sample_size]
        
        return addresses
    
    def get_property_id_from_address(self, address: str) -> Optional[str]:
        """Get property ID from address using CoreLogic API."""
        params = {
            "q": address,
            "suggestionTypes": "address",
            "limit": 3
        }
        
        url = f"{self.base_url}/property/au/v2/suggest.json"
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            suggestions = response.json().get("suggestions", [])
            if suggestions:
                return suggestions[0].get("propertyId")
        
        return None
    
    def get_all_units_from_street_address(self, street_address: str, limit: int = 100, max_total: int = 1000) -> List[Dict[str, Any]]:
        """Get all units/properties for a single street address using CoreLogic API.
        
        Args:
            street_address: The street address to search for
            limit: Number of results per API call (max 100)
            max_total: Maximum total results to retrieve across all calls
            
        Returns:
            List of property suggestions
        """
        all_suggestions = []
        offset = 0
        
        # Ensure limit doesn't exceed API maximum
        limit = min(limit, 100)
        
        while len(all_suggestions) < max_total:
            params = {
                "q": street_address,
                "suggestionTypes": "address",
                "limit": limit,
                "offset": offset
            }
            
            url = f"{self.base_url}/property/au/v2/suggest.json"
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                response_data = response.json()
                suggestions = response_data.get("suggestions", [])
                
                if not suggestions:
                    # No more results available
                    break
                
                all_suggestions.extend(suggestions)
                
                # Check if we got fewer results than requested (indicates end of results)
                if len(suggestions) < limit:
                    break
                
                offset += limit
                
                # Add a small delay between requests to be respectful to the API
                time.sleep(0.1)
                
                print(f"Retrieved {len(all_suggestions)} units so far...")
                
            else:
                print(f"API error: HTTP {response.status_code} - {response.text}")
                break
        
        # Truncate to max_total if we exceeded it
        if len(all_suggestions) > max_total:
            all_suggestions = all_suggestions[:max_total]
            
        # Remove duplicates based on propertyId
        seen_property_ids = set()
        unique_suggestions = []
        
        for suggestion in all_suggestions:
            property_id = suggestion.get("propertyId")
            if property_id and property_id not in seen_property_ids:
                seen_property_ids.add(property_id)
                unique_suggestions.append(suggestion)
        
        print(f"Total units retrieved: {len(all_suggestions)}")
        print(f"Unique units after deduplication: {len(unique_suggestions)}")
        
        return unique_suggestions
    
    def get_sales_for_property(self, property_id: str) -> Dict[str, Any]:
        """Get sales data for a specific property ID."""
        url = f"{self.base_url}/property-details/au/properties/{property_id}/sales"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"HTTP {response.status_code}",
                    "message": response.text
                }
        except Exception as e:
            return {
                "error": "Request failed",
                "message": str(e)
            }
    
    def get_sales_for_all_units(self, street_address: str, limit: int = 100, max_total: int = 1000, delay: float = 0.1) -> List[Dict[str, Any]]:
        """Get sales data for all units at a street address.
        
        Args:
            street_address: The street address to search for
            limit: Number of results per API call for unit search (max 100)
            max_total: Maximum total units to retrieve
            delay: Delay between sales API calls
        """
        # Get all units first
        units = self.get_all_units_from_street_address(street_address, limit, max_total)
        
        if not units:
            return []
        
        sales_data = []
        
        for i, unit in enumerate(units):
            property_id = unit.get("propertyId")
            if property_id:
                address = unit.get("suggestion", unit.get("singleLine", "Unknown address"))
                print(f"Getting sales for unit {i+1}/{len(units)}: {address}")
                
                # Get sales data
                sales = self.get_sales_for_property(property_id)
                
                # Combine unit info with sales data
                unit_sales = {
                    "property_id": property_id,
                    "address": address,
                    "unit_number": unit.get("unitNumber"),
                    "street_number": unit.get("streetNumber"),
                    "street_name": unit.get("streetName"),
                    "suburb": unit.get("suburb"),
                    "state": unit.get("state"),
                    "postcode": unit.get("postcode"),
                    "sales_data": sales
                }
                
                sales_data.append(unit_sales)
                
                # Add delay to avoid rate limiting
                time.sleep(delay)
            
        return sales_data
    
    def generate_property_results(self, property_id: str) -> Dict[str, Any]:
        """Get comprehensive property results for a given property ID."""
        endpoints = {
            "location": f"/property-details/au/properties/{property_id}/location",
            "legal": f"/property-details/au/properties/{property_id}/legal",
            "site": f"/property-details/au/properties/{property_id}/site",
            "core_attributes": f"/property-details/au/properties/{property_id}/attributes/core",
            "additional_attributes": f"/property-details/au/properties/{property_id}/attributes/additional",
            "features": f"/property-details/au/properties/{property_id}/features",
            "occupancy": f"/property-details/au/properties/{property_id}/occupancy",
            "last_sale": f"/property-details/au/properties/{property_id}/sales/last",
            "sales": f"/property-details/au/properties/{property_id}/sales",  
            "sales_otm": f"/property-details/au/properties/{property_id}/otm/campaign/sales",
            "timeline": f"/property-timeline/au/properties/{property_id}/timeline",
            "advertisements": f"/property/au/v1/property/{property_id}/advertisements.json",
        }
        
        results = {}
        
        for key, endpoint in endpoints.items():
            url = self.base_url + endpoint
            try:
                response = requests.get(url, headers=self.headers)
                if response.status_code == 200:
                    results[key] = response.json()
                else:
                    results[key] = {
                        "error": f"HTTP {response.status_code}",
                        "message": response.text
                    }
            except Exception as e:
                results[key] = {
                    "error": "Request failed",
                    "message": str(e)
                }
        
        return results
    
    def flatten_json_recursive(self, data: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
        """Flatten nested JSON structure - delegates to DataProcessor."""
        from pipeline_utils import DataProcessor
        return DataProcessor.flatten_json_recursive(data, parent_key, sep)
    
    def process_addresses(self,
                         addresses_file: str,
                         output_file: str = "./data/property_results.csv",
                         sample_size: Optional[int] = None,
                         delay: float = 0.1) -> Tuple[pd.DataFrame, List[str], List[str]]:
        """
        Process all addresses and generate comprehensive property results WITHOUT transposing.
        
        Args:
            addresses_file: Path to file containing addresses
            output_file: Output CSV file path
            sample_size: Number of addresses to process (None for all)
            delay: Delay between API calls to avoid rate limiting
            
        Returns:
            Tuple of (DataFrame, processed_addresses, failed_addresses)
        """
        print("Reading addresses from file...")
        addresses = self.read_addresses(addresses_file, sample_size)
        print(f"Found {len(addresses)} addresses")
        
        # Initialize collections
        all_flattened_results = []
        processed_addresses = []
        failed_addresses = []
        
        print("\n" + "="*60)
        print("PROCESSING WITHOUT TRANSPOSE")
        print("="*60)
        
        for i, address in enumerate(addresses):
            print(f"\nProcessing {i+1}/{len(addresses)}: {address}")
            
            # Get property ID from address
            property_id = self.get_property_id_from_address(address)
            
            if property_id:
                try:
                    # Get property results
                    property_results = self.generate_property_results(property_id)
                    
                    # Flatten the property results for DataFrame creation
                    flattened_results = self.flatten_json_recursive(property_results)
                    
                    # Add address and property_id to flattened results
                    flattened_results['address'] = address
                    flattened_results['property_id'] = property_id
                    
                    # Store results
                    all_flattened_results.append(flattened_results)
                    processed_addresses.append(address)
                    
                    print(f"✅ Successfully processed property ID: {property_id}")
                    print(f"   Retrieved {len(flattened_results)} flattened fields")
                    
                except Exception as e:
                    print(f"❌ Error processing property {property_id}: {e}")
                    failed_addresses.append(address)
                    continue
            else:
                print(f"❌ No property ID found for: {address}")
                failed_addresses.append(address)
                continue
            
            # Add delay to avoid rate limiting
            time.sleep(delay)
        
        # Create DataFrame - NO TRANSPOSE
        df = pd.DataFrame(all_flattened_results)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Save results WITHOUT transposing
        df.to_csv(output_file, index=False)
        
        # Save boolean DataFrame showing field completeness - NO TRANSPOSE
        df_filled = df.notna() & (df != '') & (df != 'None') & (df != None)
        filled_output_file = output_file.replace('.csv', '_field_completeness.csv')
        df_filled.to_csv(filled_output_file, index=False)
        
        print(f"\nTotal properties processed: {len(df)}")
        print(f"Total fields per property: {len(df.columns)}")
        print(f"Results saved to: {output_file}")
        print(f"Field completeness saved to: {filled_output_file}")
        
        return df, processed_addresses, failed_addresses

    def get_property_sales_history(self, property_id: str) -> List[Dict[str, Any]]:
        """Get complete sales history for a single property.
        
        Args:
            property_id: CoreLogic property ID
            
        Returns:
            List of sale transactions with dates, prices, types
        """
        try:
            url = f"{self.base_url}/property-details/au/properties/{property_id}/sales"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    # Sometimes API returns single sale as dict
                    return [data]
                else:
                    return []
            else:
                print(f"Sales history API error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"Error fetching sales history for property {property_id}: {e}")
            return []
    
    def get_median_avm_for_month(self, location_id: int, target_month: str) -> Optional[Dict[str, Any]]:
        """Get median AVM for specific month using market data API.
        
        Args:
            location_id: CoreLogic location ID  
            target_month: Target month in YYYY-MM format
            
        Returns:
            Dict with median AVM data for the target month, or None if not available
        """
        try:
            from datetime import datetime
            
            # Parse target month to get date range
            target_date = datetime.strptime(target_month, '%Y-%m')
            from_date = target_date.strftime('%Y-%m-01')
            to_date = target_date.strftime('%Y-%m-28')  # Safe end of month
            
            # Prepare API payload for median value (metricTypeId: 11)
            payload = {
                "seriesRequestList": [{
                    "fromDate": from_date,
                    "toDate": to_date,
                    "interval": 1,  # Monthly
                    "locationId": location_id,
                    "locationTypeId": 8,  # Suburb
                    "metricTypeId": 11,  # Median Value
                    "propertyTypeId": 1   # Houses
                }]
            }
            
            url = f"{self.base_url}/statistics/v1/statistics.json"
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                series_list = data.get('seriesResponseList', [])
                
                if series_list and series_list[0].get('seriesDataList'):
                    series_data = series_list[0]['seriesDataList']
                    if series_data:
                        return {
                            'target_month': target_month,
                            'median_avm': series_data[0].get('value'),
                            'data_date': series_data[0].get('dateTime'),
                            'location_id': location_id
                        }
            
            return {
                'target_month': target_month,
                'median_avm': None,
                'error': 'No median AVM data available for this month',
                'location_id': location_id
            }
            
        except Exception as e:
            return {
                'target_month': target_month,
                'median_avm': None,
                'error': f"Median AVM lookup error: {e}",
                'location_id': location_id
            }
    
    def get_median_avm_series(self, location_id: int, from_month: str, to_month: str = "2024-12") -> Optional[Dict[str, Any]]:
        """Get median AVM time series from start month to end month.
        
        Args:
            location_id: CoreLogic location ID (typically postcode ID)
            from_month: Start month in YYYY-MM format
            to_month: End month in YYYY-MM format (default: 2024-12)
            
        Returns:
            Dict with time series of median AVM data
        """
        try:
            from datetime import datetime
            
            print(f"🔍 AVM Series Debug - location_id: {location_id}, from: {from_month}, to: {to_month}")
            
            # Parse months to get date range
            from_date_obj = datetime.strptime(from_month, '%Y-%m')
            to_date_obj = datetime.strptime(to_month, '%Y-%m')
            
            from_date = from_date_obj.strftime('%Y-%m-01')
            to_date = to_date_obj.strftime('%Y-%m-28')  # Safe end of month
            
            # Prepare API payload for median value time series
            payload = {
                "seriesRequestList": [{
                    "fromDate": from_date,
                    "toDate": to_date,
                    "interval": 1,  # Monthly
                    "locationId": location_id,
                    "locationTypeId": 4,  # Postcode level
                    "metricTypeId": 11,  # Median Value
                    "propertyTypeId": 1   # Houses
                }]
            }
            
            url = f"{self.base_url}/statistics/v1/statistics.json"
            print(f"🔍 AVM API call - Payload: {payload}")
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            print(f"🔍 AVM API response - Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"🔍 AVM API error response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                series_list = data.get('seriesResponseList', [])
                
                if series_list and series_list[0].get('seriesDataList'):
                    series_data = series_list[0]['seriesDataList']
                    
                    # Process all data points in the series
                    time_series = []
                    for data_point in series_data:
                        if data_point.get('value'):
                            time_series.append({
                                'date': data_point.get('dateTime'),
                                'median_avm': data_point.get('value')
                            })
                    
                    return {
                        'location_id': location_id,
                        'from_month': from_month,
                        'to_month': to_month,
                        'data_points': len(time_series),
                        'time_series': time_series
                    }
            
            return {
                'location_id': location_id,
                'from_month': from_month,
                'to_month': to_month,
                'data_points': 0,
                'time_series': [],
                'error': 'No median AVM series data available'
            }
            
        except Exception as e:
            return {
                'location_id': location_id,
                'from_month': from_month,
                'to_month': to_month,
                'error': f"Median AVM series lookup error: {e}"
            }


def process_corelogic_data(access_token: str,
                         addresses_file: str = "./data/addresses_2025.txt",
                         output_file: str = "./data/property_results.csv",
                         sample_size: Optional[int] = None,
                         delay: float = 0.1) -> Tuple[pd.DataFrame, List[str], List[str]]:
    """
    Convenience function to process CoreLogic data without transposing.
    
    Args:
        access_token: CoreLogic API access token
        addresses_file: Path to file containing addresses
        output_file: Output CSV file path
        sample_size: Number of addresses to process (None for all)
        delay: Delay between API calls
        
    Returns:
        Tuple of (DataFrame, processed_addresses, failed_addresses)
    """
    processor = CoreLogicProcessor(access_token)
    return processor.process_addresses(
        addresses_file=addresses_file,
        output_file=output_file,
        sample_size=sample_size,
        delay=delay
    )


if __name__ == "__main__":
    # Example usage
    access_token = "your_access_token_here"
    
    # Process all addresses without transposing
    df, processed, failed = process_corelogic_data(
        access_token=access_token,
        sample_size=10  # Process only 10 addresses for testing
    )
    
    print(f"\nSummary:")
    print(f"Successfully processed: {len(processed)} addresses")
    print(f"Failed to process: {len(failed)} addresses")
    print(f"DataFrame shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
