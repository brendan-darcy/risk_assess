import pandas as pd
import time
import requests
import json
from typing import List, Dict, Any, Optional, Tuple, Union
import os
from datetime import datetime

class ComparableProcessor:
    """A class to handle CoreLogic Comparable/Radius Search API processing."""
    
    def __init__(self, access_token: str, base_url: str = "https://api-uat.corelogic.asia"):
        self.access_token = access_token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "accept": "application/json"
        }
        self.endpoint = "/search/au/property/geo/radius/lastSale"
    
    def search_by_coordinates(self, 
                            lat: float, 
                            lon: float, 
                            radius: float,
                            filters: Optional[Dict[str, Any]] = None,
                            sort_params: Optional[List[str]] = None,
                            page: int = 0,
                            size: int = 20) -> Dict[str, Any]:
        """
        Search for comparable properties by coordinates and radius.
        
        Args:
            lat: Latitude coordinate
            lon: Longitude coordinate  
            radius: Search radius in kilometres (max 100)
            filters: Optional filters (price, date, beds, baths, etc.)
            sort_params: Optional sort parameters
            page: Page number (default 0)
            size: Results per page (max 20)
            
        Returns:
            API response as dictionary
        """
        params = {
            "lat": lat,
            "lon": lon,
            "radius": radius,
            "page": page,
            "size": min(size, 20)  # API max is 20
        }
        
        # Add filters if provided
        if filters:
            params.update(filters)
        
        # Add sort parameters
        if sort_params:
            params.update({"sort": sort_params})
        
        url = f"{self.base_url}{self.endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"HTTP {response.status_code}",
                    "message": response.text,
                    "params": params
                }
        except Exception as e:
            return {
                "error": "Request failed",
                "message": str(e),
                "params": params
            }
    
    def search_by_property_id(self,
                            property_id: str,
                            radius: float,
                            filters: Optional[Dict[str, Any]] = None,
                            sort_params: Optional[List[str]] = None,
                            page: int = 0,
                            size: int = 20) -> Dict[str, Any]:
        """
        Search for comparable properties by property ID and radius.
        
        Args:
            property_id: CoreLogic property ID
            radius: Search radius in kilometres (max 100)
            filters: Optional filters (price, date, beds, baths, etc.)
            sort_params: Optional sort parameters
            page: Page number (default 0)
            size: Results per page (max 20)
            
        Returns:
            API response as dictionary
        """
        params = {
            "propertyId": property_id,
            "radius": radius,
            "page": page,
            "size": min(size, 20)  # API max is 20
        }
        
        # Add filters if provided
        if filters:
            params.update(filters)
        
        # Add sort parameters
        if sort_params:
            params.update({"sort": sort_params})
        
        url = f"{self.base_url}{self.endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"HTTP {response.status_code}",
                    "message": response.text,
                    "params": params
                }
        except Exception as e:
            return {
                "error": "Request failed",
                "message": str(e),
                "params": params
            }
    
    def create_filter_dict(self,
                          price: Optional[str] = None,
                          date: Optional[str] = None,
                          source: Optional[str] = None,
                          beds: Optional[str] = None,
                          baths: Optional[str] = None,
                          car_spaces: Optional[str] = None,
                          land_area: Optional[str] = None,
                          property_types: Optional[List[str]] = None,
                          locality_ids: Optional[List[str]] = None,
                          postcode_ids: Optional[List[str]] = None,
                          street_ids: Optional[List[str]] = None,
                          include_historic: Optional[bool] = None) -> Dict[str, Any]:
        """
        Create a filter dictionary for API parameters.
        
        Args:
            price: Price filter (e.g., "500000", "515000-550000", "550000-", "-550000")
            date: Date filter in YYYYMMDD format (e.g., "20160101", "20151201-20151231")
            source: Source filter ("AA", "ALL", "VG")
            beds: Bedroom filter (e.g., "4", "2-5", "3-", "-4")
            baths: Bathroom filter (e.g., "4", "2-5", "3-", "-4")
            car_spaces: Car spaces filter (e.g., "2", "1-3", "1-", "-3")
            land_area: Land area filter in m² (e.g., "300", "300-600", "300-", "-600")
            property_types: List of property types (HOUSE, UNIT, LAND, etc.)
            locality_ids: List of locality IDs
            postcode_ids: List of postcode IDs
            street_ids: List of street IDs
            include_historic: Include historic sales
            
        Returns:
            Dictionary of filter parameters
        """
        filters = {}
        
        if price is not None:
            filters["price"] = price
        if date is not None:
            filters["date"] = date
        if source is not None:
            filters["source"] = source
        if beds is not None:
            filters["beds"] = beds
        if baths is not None:
            filters["baths"] = baths
        if car_spaces is not None:
            filters["carSpaces"] = car_spaces
        if land_area is not None:
            filters["landArea"] = land_area
        if property_types is not None:
            filters["pTypes"] = ",".join(property_types)
        if locality_ids is not None:
            filters["localityId"] = ",".join(locality_ids)
        if postcode_ids is not None:
            filters["postCodeId"] = ",".join(postcode_ids)
        if street_ids is not None:
            filters["streetId"] = ",".join(street_ids)
        if include_historic is not None:
            filters["includeHistoric"] = str(include_historic).lower()
        
        return filters
    
    def create_sort_params(self, sort_criteria: List[Tuple[str, str]]) -> List[str]:
        """
        Create sort parameters for API.
        
        Args:
            sort_criteria: List of tuples (attribute, order) where:
                          attribute: bath, beds, carSpaces, landArea, pType
                          order: asc or desc
        
        Returns:
            List of sort parameter strings
        """
        sort_params = []
        for attribute, order in sort_criteria:
            sort_params.append(f"{attribute},{order}")
        return sort_params
    
    def flatten_json_recursive(self, data: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
        """Flatten nested JSON structure - delegates to DataProcessor."""
        from pipeline_utils import DataProcessor
        return DataProcessor.flatten_json_recursive(data, parent_key, sep)
    
    def get_all_pages(self,
                     search_function,
                     search_params: Dict[str, Any],
                     max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all pages of results from a search function.
        
        Args:
            search_function: Either search_by_coordinates or search_by_property_id
            search_params: Parameters for the search function
            max_pages: Maximum number of pages to retrieve (None for all)
            
        Returns:
            List of all result dictionaries
        """
        all_results = []
        page = 0
        
        while True:
            if max_pages and page >= max_pages:
                break
                
            search_params["page"] = page
            result = search_function(**search_params)
            
            if "error" in result:
                print(f"Error on page {page}: {result}")
                break
            
            # Extract properties from the correct API response structure
            embedded = result.get("_embedded", {})
            property_list = embedded.get("propertySummaryList", [])
            
            # Extract actual property data from the nested structure
            properties = []
            for item in property_list:
                if "propertySummary" in item:
                    properties.append(item["propertySummary"])
            
            if not properties:
                break
            
            all_results.extend(properties)
            
            # Check if there are more pages using page info
            page_info = result.get("page", {})
            total_elements = page_info.get("totalElements", 0)
            current_page = page_info.get("number", 0)
            total_pages = page_info.get("totalPages", 1)
            
            if current_page >= total_pages - 1:  # Pages are 0-indexed
                break
                
            page += 1
            time.sleep(0.1)  # Rate limiting
        
        return all_results
    
    def process_comparable_search(self,
                                search_type: str,
                                search_params: Dict[str, Any],
                                output_file: str = "./data/comparable_results.csv",
                                flatten_results: bool = True,
                                get_all_pages: bool = False,
                                max_pages: Optional[int] = None,
                                delay: float = 0.1) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Process comparable search and save results.
        
        Args:
            search_type: "coordinates" or "property_id"
            search_params: Parameters for the search
            output_file: Output CSV file path
            flatten_results: Whether to flatten nested JSON
            get_all_pages: Whether to retrieve all pages
            max_pages: Maximum pages to retrieve
            delay: Delay between API calls
            
        Returns:
            Tuple of (DataFrame, search_metadata)
        """
        print(f"Starting comparable search by {search_type}")
        print(f"Search parameters: {search_params}")
        
        if search_type == "coordinates":
            search_function = self.search_by_coordinates
        elif search_type == "property_id":
            search_function = self.search_by_property_id
        else:
            raise ValueError("search_type must be 'coordinates' or 'property_id'")
        
        if get_all_pages:
            print("Retrieving all pages...")
            results = self.get_all_pages(search_function, search_params, max_pages)
            metadata = {"total_properties": len(results), "pages_retrieved": "all"}
        else:
            print("Retrieving single page...")
            response = search_function(**search_params)
            
            if "error" in response:
                print(f"Search failed: {response}")
                return pd.DataFrame(), response
            
            # Extract properties from the correct API response structure
            embedded = response.get("_embedded", {})
            property_list = embedded.get("propertySummaryList", [])
            
            # Extract actual property data from the nested structure
            results = []
            for item in property_list:
                if "propertySummary" in item:
                    results.append(item["propertySummary"])
            
            # Get pagination info
            page_info = response.get("page", {})
            total_elements = page_info.get("totalElements", len(results))
            
            metadata = {
                "total_properties": len(results),
                "total_available": total_elements,
                "pages_retrieved": 1,
                "api_response": response
            }
        
        if not results:
            print("No comparable properties found")
            return pd.DataFrame(), metadata
        
        print(f"Found {len(results)} comparable properties")
        
        # Process results
        if flatten_results:
            print("Flattening results...")
            flattened_results = [self.flatten_json_recursive(result) for result in results]
            df = pd.DataFrame(flattened_results)
        else:
            df = pd.DataFrame(results)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Save results
        df.to_csv(output_file, index=False)
        print(f"Results saved to: {output_file}")
        
        # Save metadata
        metadata_file = output_file.replace('.csv', '_metadata.json')
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        print(f"Metadata saved to: {metadata_file}")
        
        return df, metadata


def search_comparables_by_coordinates(access_token: str,
                                    lat: float,
                                    lon: float,
                                    radius: float,
                                    filters: Optional[Dict[str, Any]] = None,
                                    output_file: str = "./data/comparable_results.csv",
                                    get_all_pages: bool = False) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Convenience function to search comparables by coordinates.
    
    Args:
        access_token: CoreLogic API access token
        lat: Latitude
        lon: Longitude  
        radius: Search radius in km
        filters: Optional filter parameters
        output_file: Output file path
        get_all_pages: Whether to get all pages
        
    Returns:
        Tuple of (DataFrame, metadata)
    """
    processor = ComparableProcessor(access_token)
    
    search_params = {
        "lat": lat,
        "lon": lon,
        "radius": radius
    }
    
    if filters:
        search_params["filters"] = filters
    
    return processor.process_comparable_search(
        search_type="coordinates",
        search_params=search_params,
        output_file=output_file,
        get_all_pages=get_all_pages
    )


def search_comparables_by_property_id(access_token: str,
                                    property_id: str,
                                    radius: float,
                                    filters: Optional[Dict[str, Any]] = None,
                                    output_file: str = "./data/comparable_results.csv",
                                    get_all_pages: bool = False) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Convenience function to search comparables by property ID.
    
    Args:
        access_token: CoreLogic API access token
        property_id: CoreLogic property ID
        radius: Search radius in km
        filters: Optional filter parameters
        output_file: Output file path
        get_all_pages: Whether to get all pages
        
    Returns:
        Tuple of (DataFrame, metadata)
    """
    processor = ComparableProcessor(access_token)
    
    search_params = {
        "property_id": property_id,
        "radius": radius
    }
    
    if filters:
        search_params["filters"] = filters
    
    return processor.process_comparable_search(
        search_type="property_id",
        search_params=search_params,
        output_file=output_file,
        get_all_pages=get_all_pages
    )


if __name__ == "__main__":
    # Example usage
    access_token = "your_access_token_here"
    
    # Example 1: Search by coordinates
    filters = {
        "price": "500000-1000000",  # Price range
        "beds": "3-4",             # 3-4 bedrooms
        "property_types": ["HOUSE"] # Houses only
    }
    
    df, metadata = search_comparables_by_coordinates(
        access_token=access_token,
        lat=-33.8688,  # Sydney CBD
        lon=151.2093,
        radius=5.0,    # 5km radius
        filters=filters,
        get_all_pages=True
    )
    
    print(f"Found {len(df)} comparable properties")
    print(f"DataFrame columns: {list(df.columns)}")