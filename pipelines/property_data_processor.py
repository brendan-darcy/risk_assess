#!/usr/bin/env python3
"""
Property Data Processor

Consolidated class for all property data operations including:
- Address to property ID resolution
- Property details retrieval and processing
- Sales history analysis
- Bulk property processing with error handling

Consolidates functionality from:
- corelogic_processor_updated.py
- Parts of analysis_pipeline.py
"""

import pandas as pd
import time
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from pipeline_utils import AuthenticatedPipeline, DataProcessor, PipelineError, ErrorHandler


class PropertyDataProcessor(AuthenticatedPipeline):
    """Comprehensive processor for CoreLogic property data operations."""
    
    def __init__(self, config=None, reporter=None):
        super().__init__(config, reporter, "Property Data Processor")
        self.processed_properties = {}
        self.sales_cache = {}
    
    def validate_inputs(self) -> bool:
        """Validate that we have API access"""
        # Test API connectivity with a simple request
        test_response = self.api_client.make_request("/property/au/v2/suggest.json", 
                                                   params={"q": "Sydney", "limit": 1})
        if test_response is None:
            self.reporter.error("Cannot connect to CoreLogic API")
            return False
        
        self.reporter.success("API connectivity verified")
        return True
    
    def execute_pipeline(self) -> Dict[str, Any]:
        """Execute property data processing pipeline"""
        return {"status": "Use process_addresses or process_single_address methods"}
    
    def get_property_id_from_address(self, address: str) -> Optional[str]:
        """
        Get property ID from address using CoreLogic suggest API.

        Args:
            address: Full address string

        Returns:
            Property ID if found, None otherwise
        """
        suggestions = self.api_client.get_property_suggestions(address, limit=1)

        if suggestions:
            property_id = suggestions[0].get("propertyId")
            if property_id:
                self.reporter.info(f"Found property ID {property_id} for: {address}")
                return property_id

        self.reporter.warning(f"No property ID found for: {address}")
        return None

    def get_property_info_from_address(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive property information from address including locality IDs.

        Args:
            address: Full address string

        Returns:
            Dictionary with property_id, locality_id, suburb, state, postcode, etc., or None
        """
        suggestions = self.api_client.get_property_suggestions(address, limit=1)

        if suggestions:
            property_info = suggestions[0]
            property_id = property_info.get("propertyId")
            if property_id:
                result = {
                    "property_id": property_id,
                    "locality_id": property_info.get("localityId"),
                    "council_area_id": property_info.get("councilAreaId"),
                    "postcode_id": property_info.get("postcodeId"),
                    "state_id": property_info.get("stateId"),
                    "street_id": property_info.get("streetId"),
                    "country_id": property_info.get("countryId"),
                    "full_address": property_info.get("suggestion", property_info.get("singleLine")),
                    "suggestion_type": property_info.get("suggestionType"),
                    "is_unit": property_info.get("isUnit"),
                    "is_active_property": property_info.get("isActiveProperty"),
                    "is_body_corporate": property_info.get("isBodyCorporate")
                }
                self.reporter.info(f"Found property ID {property_id} for: {address}")
                self.reporter.info(f"Locality ID: {result.get('locality_id')}, Council Area ID: {result.get('council_area_id')}")
                return result

        self.reporter.warning(f"No property information found for: {address}")
        return None
    
    def get_comprehensive_property_data(self, property_id: str) -> Dict[str, Any]:
        """
        Get comprehensive property data for a property ID.
        
        Args:
            property_id: CoreLogic property ID
            
        Returns:
            Dictionary with all property data sections
        """
        if property_id in self.processed_properties:
            return self.processed_properties[property_id]
        
        property_data = self.api_client.get_property_details(property_id)
        
        # Cache the result
        self.processed_properties[property_id] = property_data
        
        return property_data
    
    def get_property_sales_history(self, property_id: str) -> List[Dict[str, Any]]:
        """
        Get complete sales history for a property.
        
        Args:
            property_id: CoreLogic property ID
            
        Returns:
            List of sale transactions
        """
        if property_id in self.sales_cache:
            return self.sales_cache[property_id]
        
        response = self.api_client.make_request(
            f"/property-details/au/properties/{property_id}/sales"
        )
        
        if response:
            if isinstance(response, list):
                sales_history = response
            elif isinstance(response, dict):
                sales_history = [response]  # Single sale as dict
            else:
                sales_history = []
        else:
            sales_history = []
        
        # Cache the result
        self.sales_cache[property_id] = sales_history
        
        return sales_history
    
    def flatten_property_data(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Flatten nested property data structure for DataFrame creation.
        
        Args:
            property_data: Raw property data from API
            
        Returns:
            Flattened dictionary suitable for CSV export
        """
        return self.data_processor.flatten_json_recursive(property_data)
    
    def process_single_address(self, address: str, include_sales: bool = True,
                             flatten_data: bool = True) -> Tuple[Optional[Dict[str, Any]], bool]:
        """
        Process a single address to get comprehensive property data.
        
        Args:
            address: Full address string
            include_sales: Whether to include sales history
            flatten_data: Whether to flatten nested data
            
        Returns:
            Tuple of (property_data, success)
        """
        self.reporter.info(f"Processing address: {address}")
        
        try:
            # Step 1: Get property ID
            property_id = self.get_property_id_from_address(address)
            if not property_id:
                return None, False
            
            # Step 2: Get property details
            property_data = self.get_comprehensive_property_data(property_id)
            
            # Step 3: Add sales history if requested
            if include_sales:
                sales_history = self.get_property_sales_history(property_id)
                property_data['sales_history'] = sales_history
            
            # Step 4: Add metadata
            property_data['address'] = address
            property_data['property_id'] = property_id
            property_data['processing_timestamp'] = time.time()
            
            # Step 5: Flatten if requested
            if flatten_data:
                property_data = self.flatten_property_data(property_data)
            
            self.reporter.success(f"Successfully processed: {address}")
            return property_data, True
            
        except Exception as e:
            self.reporter.error(f"Error processing {address}: {e}")
            return None, False
    
    def process_addresses_batch(self, addresses: List[str], 
                              output_file: str = None,
                              sample_size: Optional[int] = None,
                              delay: float = 0.1,
                              include_sales: bool = True,
                              save_field_completeness: bool = True) -> Tuple[pd.DataFrame, List[str], List[str]]:
        """
        Process multiple addresses with comprehensive error handling.
        
        Args:
            addresses: List of address strings
            output_file: CSV output file path
            sample_size: Limit processing to N addresses
            delay: Delay between API calls
            include_sales: Whether to include sales history
            save_field_completeness: Whether to save field completeness report
            
        Returns:
            Tuple of (results_df, processed_addresses, failed_addresses)
        """
        if sample_size:
            addresses = addresses[:sample_size]
        
        self.reporter.print_step(1, f"PROCESSING {len(addresses)} ADDRESSES")
        
        error_handler = ErrorHandler()
        all_results = []
        
        for i, address in enumerate(addresses, 1):
            self.reporter.info(f"Processing {i}/{len(addresses)}: {address}")
            
            property_data, success = self.process_single_address(
                address, include_sales=include_sales, flatten_data=True
            )
            
            if success and property_data:
                all_results.append(property_data)
                error_handler.handle_item_success(address, property_data)
            else:
                error_handler.handle_item_error(address, Exception("Processing failed"))
            
            # Rate limiting
            if delay > 0:
                time.sleep(delay)
        
        # Create DataFrame
        if all_results:
            df = pd.DataFrame(all_results)
            self.reporter.success(f"Created DataFrame with {len(df)} properties and {len(df.columns)} fields")
        else:
            df = pd.DataFrame()
            self.reporter.warning("No successful results to create DataFrame")
        
        # Save results if output file specified
        if output_file and not df.empty:
            self.data_processor.save_dataframe(df, output_file)
            
            # Save field completeness analysis
            if save_field_completeness:
                completeness_df = df.notna() & (df != '') & (df != 'None')
                completeness_file = str(Path(output_file).with_suffix('')) + '_field_completeness.csv'
                self.data_processor.save_dataframe(completeness_df, completeness_file, verbose=False)
                self.reporter.info(f"Field completeness saved to: {Path(completeness_file).name}")
        
        # Get summary from error handler
        summary = error_handler.get_summary()
        
        return df, summary['processed_items'], summary['failed_items']
    
    def process_addresses_from_file(self, addresses_file: str,
                                  output_file: str = None,
                                  sample_size: Optional[int] = None,
                                  delay: float = 0.1) -> Tuple[pd.DataFrame, List[str], List[str]]:
        """
        Process addresses from a text file.
        
        Args:
            addresses_file: Path to file containing addresses (one per line)
            output_file: CSV output file path
            sample_size: Limit processing to N addresses
            delay: Delay between API calls
            
        Returns:
            Tuple of (results_df, processed_addresses, failed_addresses)
        """
        # Read addresses
        addresses = self.data_processor.read_text_file_lines(addresses_file)
        self.reporter.success(f"Loaded {len(addresses)} addresses from file")
        
        # Auto-generate output file if not provided
        if not output_file:
            timestamp = self.file_ops.generate_timestamp()
            output_file = f"data/outputs/property_results_{timestamp}.csv"
        
        return self.process_addresses_batch(
            addresses, output_file, sample_size, delay
        )
    
    def get_street_properties(self, street_address: str, 
                            limit: int = 100, 
                            max_total: int = 1000) -> List[Dict[str, Any]]:
        """
        Get all properties on a street using pagination.
        
        Args:
            street_address: Street address to search
            limit: Results per page
            max_total: Maximum total results
            
        Returns:
            List of property suggestions
        """
        all_suggestions = []
        offset = 0
        limit = min(limit, 100)  # API maximum
        
        self.reporter.info(f"Searching for properties on: {street_address}")
        
        while len(all_suggestions) < max_total:
            suggestions = self.api_client.get_property_suggestions(
                street_address, limit=limit, offset=offset
            )
            
            if not suggestions:
                break
            
            all_suggestions.extend(suggestions)
            
            # Check if we got fewer results than requested
            if len(suggestions) < limit:
                break
            
            offset += limit
            self.reporter.info(f"Retrieved {len(all_suggestions)} properties so far...")
        
        # Remove duplicates based on property ID
        unique_suggestions = []
        seen_ids = set()
        
        for suggestion in all_suggestions:
            property_id = suggestion.get("propertyId")
            if property_id and property_id not in seen_ids:
                seen_ids.add(property_id)
                unique_suggestions.append(suggestion)
        
        self.reporter.success(f"Found {len(unique_suggestions)} unique properties on street")
        
        return unique_suggestions
    
    def analyze_street_sales(self, street_address: str, 
                           include_property_details: bool = False,
                           delay: float = 0.1) -> List[Dict[str, Any]]:
        """
        Analyze all sales on a street.
        
        Args:
            street_address: Street address to analyze
            include_property_details: Whether to fetch full property details
            delay: Delay between API calls
            
        Returns:
            List of property sales data
        """
        properties = self.get_street_properties(street_address)
        
        if not properties:
            return []
        
        sales_data = []
        
        for i, property_info in enumerate(properties, 1):
            property_id = property_info.get("propertyId")
            if not property_id:
                continue
            
            address = property_info.get("suggestion", property_info.get("singleLine", "Unknown"))
            self.reporter.info(f"Getting sales for property {i}/{len(properties)}: {address}")
            
            # Get sales history
            sales = self.get_property_sales_history(property_id)
            
            property_sales = {
                "property_id": property_id,
                "address": address,
                "unit_number": property_info.get("unitNumber"),
                "street_number": property_info.get("streetNumber"),
                "street_name": property_info.get("streetName"),
                "suburb": property_info.get("suburb"),
                "state": property_info.get("state"),
                "postcode": property_info.get("postcode"),
                "sales_data": sales,
                "sales_count": len(sales) if sales else 0
            }
            
            # Add full property details if requested
            if include_property_details:
                property_details = self.get_comprehensive_property_data(property_id)
                property_sales["property_details"] = property_details
            
            sales_data.append(property_sales)
            
            if delay > 0:
                time.sleep(delay)
        
        self.reporter.success(f"Analyzed sales for {len(sales_data)} properties on street")
        
        return sales_data
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """Get summary of processing operations."""
        return {
            "processed_properties_count": len(self.processed_properties),
            "cached_sales_count": len(self.sales_cache),
            "memory_usage": {
                "properties_cache_kb": len(str(self.processed_properties)) / 1024,
                "sales_cache_kb": len(str(self.sales_cache)) / 1024
            }
        }
    
    def clear_cache(self):
        """Clear internal caches to free memory."""
        self.processed_properties.clear()
        self.sales_cache.clear()
        self.reporter.info("Property and sales caches cleared")
    
    def get_locality_rental_listings(self, locality_id: int, filters: dict = None, include_last_sale: bool = False, council_area_id: int = None) -> dict:
        """
        Get rental listings for a locality using the CoreLogic Search API.
        Falls back to council area search if locality has fewer than 3 results.
        
        Args:
            locality_id: The locality ID to search for rentals
            filters: Dictionary with optional filters (bedrooms, property_type, date_range)
            include_last_sale: Whether to fetch last sale data for each rental property
            council_area_id: Council area ID for fallback search (if provided)
            
        Returns:
            Dictionary with rental listings or error information
        """
        endpoint = f"/search/au/property/locality/{locality_id}/otmForRent"
        search_level = "locality"
        
        try:
            self.reporter.info(f"Fetching rental listings for locality ID: {locality_id}")
            
            # Build API parameters with optional filters
            params = {}
            
            # Add filters if provided (using correct CoreLogic API parameter names)
            if filters:
                if 'bedrooms' in filters and filters['bedrooms']:
                    params['beds'] = filters['bedrooms']  # API uses 'beds' not 'bedrooms'
                if 'property_type' in filters and filters['property_type']:
                    params['pTypes'] = filters['property_type']  # API uses 'pTypes' (plural)
                
                # Add server-side date filtering (requires YYYYMMDD format)
                if ('date_from' in filters and filters['date_from']) or ('date_to' in filters and filters['date_to']):
                    date_from = filters.get('date_from')
                    date_to = filters.get('date_to')
                    
                    # Convert YYYY-MM-DD to YYYYMMDD format for API
                    if date_from:
                        date_from = date_from.replace('-', '')
                    if date_to:
                        date_to = date_to.replace('-', '')
                    
                    # Build date parameter based on what's provided
                    if date_from and date_to:
                        params['date'] = f"{date_from}-{date_to}"  # Range
                        self.reporter.info(f"Server-side date filtering: {date_from} to {date_to}")
                    elif date_from:
                        params['date'] = f"{date_from}-"  # From date onwards
                        self.reporter.info(f"Server-side date filtering: from {date_from}")
                    elif date_to:
                        params['date'] = f"-{date_to}"  # Until date
                        self.reporter.info(f"Server-side date filtering: until {date_to}")
            
            # Use the paginated_request method to get all rental listings
            # Note: This API has a page size limit of 20
            rental_listings = self.api_client.paginated_request(
                endpoint=endpoint,
                params=params,
                max_pages=10,  # Limit to prevent excessive requests
                page_size=20,  # Maximum allowed by this endpoint
                delay=0.1
            )
            
            # Check if we need to fallback to council area search
            if rental_listings and len(rental_listings) < 3 and council_area_id:
                self.reporter.warning(f"Only {len(rental_listings)} rental listings found at locality level")
                self.reporter.info(f"Falling back to council area search (ID: {council_area_id})")
                
                # Try council area search
                council_endpoint = f"/search/au/property/councilArea/{council_area_id}/otmForRent"
                council_listings = self.api_client.paginated_request(
                    endpoint=council_endpoint,
                    params=params,
                    max_pages=10,
                    page_size=20,
                    delay=0.1
                )
                
                if council_listings and len(council_listings) > len(rental_listings):
                    self.reporter.success(f"Council area search found {len(council_listings)} rental listings (expanded from {len(rental_listings)})")
                    rental_listings = council_listings
                    endpoint = council_endpoint
                    search_level = "council_area"
                else:
                    self.reporter.info(f"Council area search did not improve results, using {len(rental_listings)} locality listings")
            
            if rental_listings:
                self.reporter.success(f"Found {len(rental_listings)} rental listings at {search_level} level")
                
                # Enrich with last sale data if requested
                if include_last_sale:
                    self.reporter.info("Fetching last sale data for each rental property...")
                    enriched_listings = []
                    
                    for i, listing in enumerate(rental_listings, 1):
                        property_id = listing.get('id')
                        if property_id:
                            self.reporter.info(f"Fetching last sale for property {i}/{len(rental_listings)}: {property_id}")
                            
                            # Get last sale data using the method from pipeline_utils.py
                            last_sale_data = self.api_client.get_property_details(
                                str(property_id), 
                                endpoints_list=['last_sale']
                            )
                            
                            # Add last sale info to listing
                            listing_copy = listing.copy()
                            if last_sale_data and 'last_sale' in last_sale_data:
                                listing_copy['last_sale_data'] = last_sale_data['last_sale']
                            else:
                                listing_copy['last_sale_data'] = {'error': 'No last sale data available'}
                            
                            enriched_listings.append(listing_copy)
                            
                            # Small delay to avoid rate limiting
                            time.sleep(0.1)
                        else:
                            listing_copy = listing.copy()
                            listing_copy['last_sale_data'] = {'error': 'No property ID available'}
                            enriched_listings.append(listing_copy)
                    
                    rental_listings = enriched_listings
                    self.reporter.success(f"Enriched all rental listings with last sale data")
                
                return {
                    'status': 'success',
                    'locality_id': locality_id,
                    'council_area_id': council_area_id,
                    'search_level': search_level,
                    'total_listings': len(rental_listings),
                    'rental_listings': rental_listings,
                    'endpoint_used': endpoint,
                    'filters_applied': filters or {},
                    'enriched_with_last_sale': include_last_sale
                }
            else:
                return {
                    'status': 'no_data',
                    'locality_id': locality_id,
                    'message': 'No rental listings found for this locality',
                    'endpoint_used': endpoint,
                    'filters_applied': filters or {}
                }
                
        except Exception as e:
            self.reporter.error(f"Error fetching rental data: {e}")
            return {
                'status': 'error',
                'locality_id': locality_id,
                'error': str(e),
                'endpoint_used': endpoint,
                'filters_applied': filters or {}
            }
    
    def analyze_rental_statistics(self, rental_listings: list) -> dict:
        """
        Analyze rental data for statistics and distributions.
        
        Args:
            rental_listings: List of rental listing dictionaries
            
        Returns:
            Dictionary with rental analysis results
        """
        if not rental_listings:
            return {
                'status': 'no_analysis',
                'reason': 'No rental data provided'
            }
        
        try:
            # Extract key rental information
            rental_prices = []
            property_types = []
            bedroom_counts = []
            
            for listing in rental_listings:
                # Handle different response structures
                if isinstance(listing, dict):
                    # Extract rental price if available
                    price = None
                    if 'rent' in listing:
                        price = listing.get('rent', {}).get('price')
                    elif 'otmForRentDetail' in listing:
                        price = listing.get('otmForRentDetail', {}).get('price')
                    elif 'price' in listing:
                        price = listing.get('price')
                    
                    if price and isinstance(price, (int, float)) and price > 0:
                        rental_prices.append(price)
                    
                    # Extract property characteristics
                    attrs = listing.get('attributes', {})
                    if 'bedrooms' in attrs:
                        bedroom_counts.append(attrs['bedrooms'])
                    
                    prop_type = listing.get('propertyType') or listing.get('propertySubType')
                    if prop_type:
                        property_types.append(prop_type)
            
            # Calculate rental statistics
            analysis = {
                'status': 'success',
                'total_listings_analyzed': len(rental_listings),
            }
            
            if rental_prices:
                import pandas as pd
                analysis['rental_price_stats'] = {
                    'count': len(rental_prices),
                    'min_price': min(rental_prices),
                    'max_price': max(rental_prices),
                    'median_price': pd.Series(rental_prices).median(),
                    'mean_price': pd.Series(rental_prices).mean(),
                    'std_price': pd.Series(rental_prices).std()
                }
            
            if bedroom_counts:
                import pandas as pd
                bedroom_distribution = pd.Series(bedroom_counts).value_counts().to_dict()
                analysis['bedroom_distribution'] = bedroom_distribution
            
            if property_types:
                import pandas as pd
                type_counts = pd.Series(property_types).value_counts().to_dict()
                analysis['property_type_distribution'] = type_counts
            
            return analysis
            
        except Exception as e:
            self.reporter.error(f"Rental analysis failed: {e}")
            return {
                'status': 'error',
                'error': f'Analysis failed: {str(e)}'
            }

    def add_indexation_to_rental_properties(self, rental_listings: list, locality_id: int, 
                                           market_processor, target_date: str = "2022-03-31",
                                           date_to_fallback: str = None) -> list:
        """
        Add indexation analysis to rental properties that have last sale data.
        
        Args:
            rental_listings: List of rental properties with last_sale_data
            locality_id: Locality ID for AVM lookup
            market_processor: MarketDataProcessor instance
            target_date: Target date for indexation (default: 2022-03-31)
            date_to_fallback: Fallback date if rental listing date not available
            
        Returns:
            List of rental properties enriched with indexation data
        """
        from pipeline_utils import index_value_to_date
        import pandas as pd
        
        enriched_rentals = []
        
        for i, rental_property in enumerate(rental_listings, 1):
            self.reporter.info(f"Adding indexation to rental {i}/{len(rental_listings)}")
            
            # Check if rental property has last sale data
            last_sale_data = rental_property.get('last_sale_data', {})
            if not last_sale_data or 'error' in last_sale_data:
                enriched_rental = rental_property.copy()
                enriched_rental['indexation'] = {
                    'status': 'no_last_sale', 
                    'reason': 'No last sale data available for this property'
                }
                enriched_rentals.append(enriched_rental)
                continue
            
            try:
                # Extract last sale information
                last_sale = last_sale_data.get('lastSale', {})
                
                if not (last_sale.get('price') and last_sale.get('contractDate')):
                    enriched_rental = rental_property.copy()
                    enriched_rental['indexation'] = {
                        'status': 'not_performed',
                        'reason': 'No valid last sale data found (missing price or date)'
                    }
                    enriched_rentals.append(enriched_rental)
                    continue
                
                sale_price = last_sale['price']
                sale_date = last_sale['contractDate']
                
                # Determine indexation target date using hierarchy:
                # 1. Rental listing date from otmForRentDetail (if available)
                # 2. User's date_to parameter (if provided)  
                # 3. Default target_date parameter
                indexation_target_date = target_date  # Default
                date_source = "default"
                
                # Check for rental listing date first
                otm_detail = rental_property.get('otmForRentDetail', {})
                if 'date' in otm_detail and otm_detail['date']:
                    indexation_target_date = otm_detail['date']
                    date_source = "rental_listing"
                # Fallback to user's date_to parameter
                elif date_to_fallback:
                    indexation_target_date = date_to_fallback
                    date_source = "date_to_parameter"
                
                # Get AVM data for indexation
                target_month = pd.to_datetime(sale_date).strftime('%Y-%m')
                
                # Get only the AVM series needed for indexation (much more efficient)
                avm_series = market_processor.fetch_avm_series_for_indexation(
                    location_id=int(locality_id),
                    location_type_id=8,  # Suburb level
                    property_type_id=1,  # Houses
                    from_date=f"{target_month}-01",
                    to_date=indexation_target_date
                )
                
                if not avm_series:
                    enriched_rental = rental_property.copy()
                    enriched_rental['indexation'] = {
                        'status': 'error',
                        'error': 'No median AVM data available for indexation'
                    }
                    enriched_rentals.append(enriched_rental)
                    continue
                
                # Use the latest date in the AVM series as actual target
                actual_target_date = avm_series[-1]['date']
                
                # Perform indexation
                indexation_result = index_value_to_date(
                    transaction_value=sale_price,
                    transaction_date=sale_date,
                    target_date=actual_target_date,
                    index_series=avm_series
                )
                
                if indexation_result['status'] == 'success':
                    growth_pct = ((indexation_result['indexed_value'] / indexation_result['original_value']) - 1) * 100
                    
                    indexation_data = {
                        'status': 'success',
                        'original_sale': {'price': sale_price, 'date': sale_date},
                        'indexed_value': indexation_result['indexed_value'],
                        'target_date': actual_target_date,
                        'index_ratio': indexation_result['index_ratio'],
                        'growth_percentage': growth_pct,
                        'transaction_index': indexation_result['transaction_index'],
                        'target_index': indexation_result['target_index'],
                        'method': indexation_result['method'],
                        'calculation_details': {
                            'description': f"Indexed ${sale_price:,} sale price from {sale_date} to {actual_target_date} using median AVM series",
                            'years_elapsed': (pd.to_datetime(actual_target_date) - pd.to_datetime(sale_date)).days / 365.25,
                            'annualized_growth': (indexation_result['index_ratio'] ** (365.25 / (pd.to_datetime(actual_target_date) - pd.to_datetime(sale_date)).days) - 1) * 100
                        },
                        'target_date_source': date_source,
                        'target_date_requested': indexation_target_date
                    }
                else:
                    indexation_data = {
                        'status': 'error',
                        'error': indexation_result['error'],
                        'original_sale': {'price': sale_price, 'date': sale_date},
                        'target_date': actual_target_date,
                        'target_date_source': date_source,
                        'target_date_requested': indexation_target_date
                    }
                
                enriched_rental = rental_property.copy()
                enriched_rental['indexation'] = indexation_data
                
                # Calculate rental yield if we have both rent price and indexed value
                yield_data = self._calculate_rental_yield(rental_property, indexation_data)
                enriched_rental['rental_yield'] = yield_data
                
                enriched_rentals.append(enriched_rental)
                
            except Exception as e:
                enriched_rental = rental_property.copy()
                indexation_data = {
                    'status': 'error',
                    'error': f'Indexation processing failed: {str(e)}'
                }
                enriched_rental['indexation'] = indexation_data
                
                # Calculate rental yield even if indexation failed
                yield_data = self._calculate_rental_yield(rental_property, indexation_data)
                enriched_rental['rental_yield'] = yield_data
                
                enriched_rentals.append(enriched_rental)
        
        return enriched_rentals

    def _calculate_rental_yield(self, rental_property, indexation_data):
        """
        Calculate rental yield using formula: otmForRentDetail.price / 7 * 365 / indexation.indexed_value
        
        Args:
            rental_property: Rental property data with otmForRentDetail
            indexation_data: Indexation data with indexed_value
            
        Returns:
            Dictionary with yield calculation details
        """
        try:
            # Get weekly rent from otmForRentDetail
            otm_detail = rental_property.get('otmForRentDetail', {})
            weekly_rent = otm_detail.get('price')
            
            if not weekly_rent:
                return {
                    'status': 'no_calculation',
                    'reason': 'No rental price available in otmForRentDetail'
                }
            
            # Check if indexation was successful and has indexed_value
            if indexation_data.get('status') != 'success' or not indexation_data.get('indexed_value'):
                return {
                    'status': 'no_calculation', 
                    'reason': 'No indexed value available (indexation failed or not performed)'
                }
            
            indexed_value = indexation_data['indexed_value']
            
            # Apply your formula: price / 7 * 365 / indexed_value
            annual_rent = weekly_rent / 7 * 365
            rental_yield = annual_rent / indexed_value
            rental_yield_percentage = rental_yield * 100
            
            return {
                'status': 'success',
                'weekly_rent': weekly_rent,
                'annual_rent': annual_rent,
                'indexed_property_value': indexed_value,
                'rental_yield': rental_yield,
                'rental_yield_percentage': rental_yield_percentage,
                'calculation_details': {
                    'formula': 'weekly_rent / 7 * 365 / indexed_value',
                    'description': f'${weekly_rent} ÷ 7 × 365 ÷ ${indexed_value:,.0f} = {rental_yield_percentage:.2f}%'
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': f'Yield calculation failed: {str(e)}'
            }


def process_addresses_from_file(addresses_file: str, 
                              output_file: str = None,
                              sample_size: Optional[int] = None,
                              delay: float = 0.1) -> Tuple[pd.DataFrame, List[str], List[str]]:
    """
    Convenience function for processing addresses from file.
    
    Args:
        addresses_file: Path to addresses file
        output_file: Output CSV file
        sample_size: Limit processing 
        delay: API delay
        
    Returns:
        Tuple of (DataFrame, processed_addresses, failed_addresses)
    """
    processor = PropertyDataProcessor()
    return processor.process_addresses_from_file(
        addresses_file, output_file, sample_size, delay
    )


if __name__ == "__main__":
    # Example usage
    processor = PropertyDataProcessor()
    
    # Process single address
    data, success = processor.process_single_address("1 Martin Place, Sydney NSW 2000")
    if success:
        print(f"Successfully processed address with {len(data)} fields")
    
    # Process addresses from file
    df, processed, failed = processor.process_addresses_from_file(
        "data/raw/addresses.txt",
        output_file="data/outputs/property_results.csv",
        sample_size=5
    )
    
    print(f"Processed {len(processed)} addresses, failed {len(failed)}")