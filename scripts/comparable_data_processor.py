#!/usr/bin/env python3
"""
Comparable Data Processor

Consolidated class for comparable property operations including:
- Radius-based property searches
- Property comparison analysis  
- Filter management and search optimization
- Bulk comparable processing

Consolidates functionality from:
- comparable_processor.py
- Parts of analysis_pipeline.py
"""

import pandas as pd
import time
import json
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path

from pipeline_utils import AuthenticatedPipeline, DataProcessor, PipelineError, ErrorHandler


class ComparableDataProcessor(AuthenticatedPipeline):
    """Comprehensive processor for comparable property search and analysis."""
    
    def __init__(self, config=None, reporter=None):
        super().__init__(config, reporter, "Comparable Data Processor")
        self.search_cache = {}
        self.filter_templates = self._get_default_filter_templates()
    
    def validate_inputs(self) -> bool:
        """Validate API connectivity for comparable searches"""
        # Test comparable search API with simple request
        test_params = {
            "lat": -33.8688,  # Sydney CBD
            "lon": 151.2093,
            "radius": 1,
            "size": 1
        }
        
        test_response = self.api_client.search_comparable_properties(test_params)
        if test_response is None:
            self.reporter.error("Cannot connect to CoreLogic Comparable Search API")
            return False
        
        self.reporter.success("Comparable Search API connectivity verified")
        return True
    
    def execute_pipeline(self) -> Dict[str, Any]:
        """Execute comparable data processing pipeline"""
        return {"status": "Use search_by_coordinates or search_by_property_id methods"}
    
    def _get_default_filter_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get default filter templates for common search scenarios."""
        return {
            "similar_houses": {
                "pTypes": "HOUSE",
                "beds": "3-5",
                "baths": "2-3",
                "price": "500000-1500000"
            },
            "similar_units": {
                "pTypes": "UNIT",
                "beds": "2-4", 
                "baths": "1-2",
                "price": "400000-1000000"
            },
            "recent_sales": {
                "date": "20230101-",  # Sales from 2023 onwards
                "source": "AA"  # All authenticated sources
            },
            "high_value": {
                "price": "2000000-",
                "landArea": "600-"
            },
            "investment_properties": {
                "pTypes": "HOUSE,UNIT",
                "price": "400000-800000",
                "includeHistoric": "false"
            }
        }
    
    def create_search_filters(self, template: str = None, **custom_filters) -> Dict[str, Any]:
        """
        Create search filters from template or custom parameters.
        
        Args:
            template: Template name from default templates
            **custom_filters: Custom filter parameters
            
        Returns:
            Dictionary of search filters
        """
        filters = {}
        
        # Start with template if provided
        if template and template in self.filter_templates:
            filters.update(self.filter_templates[template])
            self.reporter.info(f"Applied filter template: {template}")
        
        # Apply custom filters
        filter_mappings = {
            'price': 'price',
            'date': 'date', 
            'source': 'source',
            'beds': 'beds',
            'baths': 'baths',
            'car_spaces': 'carSpaces',
            'land_area': 'landArea',
            'property_types': 'pTypes',
            'locality_ids': 'localityId',
            'postcode_ids': 'postCodeId', 
            'street_ids': 'streetId',
            'include_historic': 'includeHistoric'
        }
        
        for key, api_key in filter_mappings.items():
            if key in custom_filters:
                value = custom_filters[key]
                if isinstance(value, list):
                    value = ",".join(str(v) for v in value)
                elif isinstance(value, bool):
                    value = str(value).lower()
                filters[api_key] = str(value)
        
        # Handle property types specially
        if 'property_types' in custom_filters:
            pt_list = custom_filters['property_types']
            if isinstance(pt_list, list):
                filters['pTypes'] = ",".join(pt_list)
        
        if filters:
            self.reporter.info(f"Created filters: {filters}")
        
        return filters
    
    def search_by_coordinates(self, lat: float, lon: float, radius: float,
                            filters: Dict[str, Any] = None,
                            sort_by: List[Tuple[str, str]] = None,
                            page: int = 0, size: int = 20,
                            cache_results: bool = True) -> Dict[str, Any]:
        """
        Search for comparable properties by coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
            radius: Search radius in kilometers (max 100)
            filters: Search filters dict
            sort_by: List of (field, order) tuples for sorting
            page: Page number (0-indexed)
            size: Results per page (max 20)
            cache_results: Whether to cache results
            
        Returns:
            API response dictionary
        """
        params = {
            "lat": lat,
            "lon": lon,
            "radius": min(radius, 100),  # API max
            "page": page,
            "size": min(size, 20)  # API max
        }
        
        # Add filters
        if filters:
            params.update(filters)
        
        # Add sorting
        if sort_by:
            sort_params = []
            for field, order in sort_by:
                sort_params.append(f"{field},{order}")
            params["sort"] = sort_params
        
        # Check cache first
        cache_key = f"coords_{lat}_{lon}_{radius}_{hash(str(sorted(params.items())))}"
        if cache_results and cache_key in self.search_cache:
            self.reporter.info("Using cached search results")
            return self.search_cache[cache_key]
        
        # Make API request
        response = self.api_client.search_comparable_properties(params)
        
        if response and cache_results:
            self.search_cache[cache_key] = response
        
        return response or {"error": "API request failed"}
    
    def search_by_property_id(self, property_id: str, radius: float,
                            filters: Dict[str, Any] = None,
                            sort_by: List[Tuple[str, str]] = None,
                            page: int = 0, size: int = 20,
                            cache_results: bool = True) -> Dict[str, Any]:
        """
        Search for comparable properties by property ID.
        
        Args:
            property_id: CoreLogic property ID
            radius: Search radius in kilometers
            filters: Search filters dict
            sort_by: Sorting criteria
            page: Page number
            size: Results per page
            cache_results: Whether to cache results
            
        Returns:
            API response dictionary
        """
        params = {
            "propertyId": property_id,
            "radius": min(radius, 100),
            "page": page,
            "size": min(size, 20)
        }
        
        if filters:
            params.update(filters)
        
        if sort_by:
            sort_params = []
            for field, order in sort_by:
                sort_params.append(f"{field},{order}")
            params["sort"] = sort_params
        
        # Check cache
        cache_key = f"prop_{property_id}_{radius}_{hash(str(sorted(params.items())))}"
        if cache_results and cache_key in self.search_cache:
            self.reporter.info("Using cached search results")
            return self.search_cache[cache_key]
        
        response = self.api_client.search_comparable_properties(params)
        
        if response and cache_results:
            self.search_cache[cache_key] = response
        
        return response or {"error": "API request failed"}
    
    def get_all_pages(self, search_function, search_params: Dict[str, Any],
                     max_pages: Optional[int] = None,
                     delay: float = 0.1) -> List[Dict[str, Any]]:
        """
        Get all pages of search results.
        
        Args:
            search_function: Either search_by_coordinates or search_by_property_id
            search_params: Parameters for the search function
            max_pages: Maximum pages to retrieve
            delay: Delay between requests
            
        Returns:
            List of all property results
        """
        all_properties = []
        page = 0
        
        while True:
            if max_pages and page >= max_pages:
                break
            
            # Update page in search params
            search_params = search_params.copy()
            search_params["page"] = page
            search_params["cache_results"] = False  # Don't cache individual pages
            
            response = search_function(**search_params)
            
            if "error" in response:
                self.reporter.error(f"Search failed on page {page}: {response['error']}")
                break
            
            # Extract properties from response
            properties = self._extract_properties_from_response(response)
            
            if not properties:
                self.reporter.info(f"No more properties found at page {page}")
                break
            
            all_properties.extend(properties)
            
            # Check pagination info
            page_info = response.get("page", {})
            current_page = page_info.get("number", page)
            total_pages = page_info.get("totalPages", 1)
            
            self.reporter.info(f"Retrieved page {current_page + 1}/{total_pages}: {len(properties)} properties")
            
            if current_page >= total_pages - 1:
                break
            
            page += 1
            
            if delay > 0:
                time.sleep(delay)
        
        return all_properties
    
    def _extract_properties_from_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract property data from API response."""
        if "_embedded" not in response:
            return []
        
        embedded = response["_embedded"]
        property_list = embedded.get("propertySummaryList", [])
        
        properties = []
        for item in property_list:
            if "propertySummary" in item:
                properties.append(item["propertySummary"])
            else:
                properties.append(item)  # Fallback
        
        return properties
    
    def analyze_comparable_properties(self, search_results: List[Dict[str, Any]],
                                    subject_property: Dict[str, Any] = None,
                                    analysis_metrics: List[str] = None) -> Dict[str, Any]:
        """
        Analyze comparable properties and generate insights.
        
        Args:
            search_results: List of comparable property results
            subject_property: Subject property data for comparison
            analysis_metrics: Metrics to analyze
            
        Returns:
            Dictionary with analysis results
        """
        if not search_results:
            return {"error": "No comparable properties to analyze"}
        
        self.reporter.print_step(1, f"ANALYZING {len(search_results)} COMPARABLE PROPERTIES")
        
        # Default metrics to analyze
        if not analysis_metrics:
            analysis_metrics = ["salePrice", "beds", "baths", "carSpaces", "landArea", 
                              "lastSaleDate", "daysOnMarket"]
        
        analysis = {
            "total_comparables": len(search_results),
            "analysis_date": time.time(),
            "metrics_analyzed": analysis_metrics,
            "summary_stats": {},
            "price_analysis": {},
            "property_characteristics": {},
            "market_insights": {}
        }
        
        # Extract data for analysis
        df_data = []
        for prop in search_results:
            # Flatten property data
            flat_prop = self.data_processor.flatten_json_recursive(prop)
            df_data.append(flat_prop)
        
        if not df_data:
            return {"error": "No property data could be extracted for analysis"}
        
        df = pd.DataFrame(df_data)
        
        # Numeric columns for statistical analysis
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        # Summary statistics for numeric columns
        for col in numeric_cols:
            if col in analysis_metrics or any(metric in col for metric in analysis_metrics):
                analysis["summary_stats"][col] = {
                    "mean": float(df[col].mean()) if not df[col].isna().all() else None,
                    "median": float(df[col].median()) if not df[col].isna().all() else None,
                    "min": float(df[col].min()) if not df[col].isna().all() else None,
                    "max": float(df[col].max()) if not df[col].isna().all() else None,
                    "std": float(df[col].std()) if not df[col].isna().all() else None,
                    "count": int(df[col].count())
                }
        
        # Price analysis
        price_cols = [col for col in df.columns if 'price' in col.lower() or 'salePrice' in col]
        if price_cols:
            price_col = price_cols[0]  # Use first price column
            prices = df[price_col].dropna()
            
            if len(prices) > 0:
                analysis["price_analysis"] = {
                    "median_price": float(prices.median()),
                    "mean_price": float(prices.mean()),
                    "price_range": {
                        "min": float(prices.min()),
                        "max": float(prices.max())
                    },
                    "quartiles": {
                        "q1": float(prices.quantile(0.25)),
                        "q2": float(prices.quantile(0.50)),
                        "q3": float(prices.quantile(0.75))
                    },
                    "price_distribution": prices.describe().to_dict()
                }
        
        # Property characteristics analysis
        categorical_cols = ["propertyType", "beds", "baths", "carSpaces"]
        for col in categorical_cols:
            matching_cols = [c for c in df.columns if col in c]
            if matching_cols:
                col_name = matching_cols[0]
                value_counts = df[col_name].value_counts()
                analysis["property_characteristics"][col] = {
                    "distribution": value_counts.to_dict(),
                    "most_common": value_counts.index[0] if len(value_counts) > 0 else None
                }
        
        # Market insights
        analysis["market_insights"] = {
            "total_properties_analyzed": len(search_results),
            "data_completeness": {
                col: (df[col].count() / len(df) * 100) for col in df.columns 
                if col in analysis_metrics
            },
            "unique_suburbs": df.get('suburb', pd.Series()).nunique() if 'suburb' in df.columns else 0,
            "date_range": {
                "earliest": df['lastSaleDate'].min() if 'lastSaleDate' in df.columns else None,
                "latest": df['lastSaleDate'].max() if 'lastSaleDate' in df.columns else None
            } if 'lastSaleDate' in df.columns else {}
        }
        
        self.reporter.success("Comparable property analysis completed")
        
        return analysis
    
    def process_comparable_search(self, search_type: str, search_params: Dict[str, Any],
                                output_file: str = None, flatten_results: bool = True,
                                get_all_pages: bool = False, max_pages: Optional[int] = None,
                                include_analysis: bool = True,
                                delay: float = 0.1) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Process a complete comparable search with analysis.
        
        Args:
            search_type: "coordinates" or "property_id"
            search_params: Parameters for search
            output_file: Output CSV file path
            flatten_results: Whether to flatten JSON results
            get_all_pages: Whether to retrieve all pages
            max_pages: Maximum pages to retrieve
            include_analysis: Whether to include comparable analysis
            delay: Delay between API calls
            
        Returns:
            Tuple of (results_df, metadata_with_analysis)
        """
        self.reporter.print_step(1, f"PROCESSING COMPARABLE SEARCH BY {search_type.upper()}")
        self.reporter.info(f"Search parameters: {search_params}")
        
        # Select search function
        if search_type == "coordinates":
            search_function = self.search_by_coordinates
        elif search_type == "property_id":
            search_function = self.search_by_property_id
        else:
            raise PipelineError(f"Invalid search_type: {search_type}")
        
        # Execute search
        if get_all_pages:
            properties = self.get_all_pages(search_function, search_params, max_pages, delay)
            metadata = {
                "search_type": search_type,
                "search_params": search_params,
                "total_properties": len(properties),
                "pages_retrieved": "all",
                "all_pages_search": True
            }
        else:
            response = search_function(**search_params)
            
            if "error" in response:
                self.reporter.error(f"Search failed: {response['error']}")
                return pd.DataFrame(), response
            
            properties = self._extract_properties_from_response(response)
            page_info = response.get("page", {})
            
            metadata = {
                "search_type": search_type,
                "search_params": search_params,
                "total_properties": len(properties),
                "total_available": page_info.get("totalElements", len(properties)),
                "pages_retrieved": 1,
                "page_info": page_info,
                "api_response_keys": list(response.keys())
            }
        
        if not properties:
            self.reporter.warning("No comparable properties found")
            return pd.DataFrame(), metadata
        
        self.reporter.success(f"Found {len(properties)} comparable properties")
        
        # Process results into DataFrame
        if flatten_results:
            self.reporter.info("Flattening property data...")
            flattened_properties = []
            for prop in properties:
                flattened_properties.append(self.data_processor.flatten_json_recursive(prop))
            df = pd.DataFrame(flattened_properties)
        else:
            df = pd.DataFrame(properties)
        
        # Add analysis if requested
        analysis_results = {}
        if include_analysis and not df.empty:
            self.reporter.info("Running comparable property analysis...")
            analysis_results = self.analyze_comparable_properties(properties)
            metadata["analysis"] = analysis_results
        
        # Save results
        if output_file and not df.empty:
            self.data_processor.save_dataframe(df, output_file)
            
            # Save metadata
            metadata_file = str(Path(output_file).with_suffix('.json'))
            self.data_processor.save_json(metadata, metadata_file, verbose=False)
            self.reporter.info(f"Metadata saved to: {Path(metadata_file).name}")
        
        return df, metadata
    
    def batch_comparable_analysis(self, properties_list: List[Dict[str, Any]],
                                output_dir: str = "data/test_results",
                                radius: float = 5.0,
                                common_filters: Dict[str, Any] = None,
                                delay: float = 0.2) -> Dict[str, Any]:
        """
        Run comparable analysis for multiple properties.
        
        Args:
            properties_list: List of properties with lat/lon or property_id
            output_dir: Output directory for results
            radius: Search radius for each property
            common_filters: Common filters to apply to all searches
            delay: Delay between searches
            
        Returns:
            Dictionary with batch analysis results
        """
        self.reporter.print_step(1, f"BATCH COMPARABLE ANALYSIS FOR {len(properties_list)} PROPERTIES")
        
        batch_results = {
            "total_properties": len(properties_list),
            "successful_searches": 0,
            "failed_searches": 0,
            "results": [],
            "summary": {}
        }
        
        error_handler = ErrorHandler()
        
        for i, property_info in enumerate(properties_list, 1):
            self.reporter.info(f"Processing property {i}/{len(properties_list)}")
            
            try:
                # Determine search type and parameters
                if "property_id" in property_info:
                    search_type = "property_id"
                    search_params = {
                        "property_id": property_info["property_id"],
                        "radius": radius,
                        "filters": common_filters or {}
                    }
                elif "lat" in property_info and "lon" in property_info:
                    search_type = "coordinates"
                    search_params = {
                        "lat": property_info["lat"],
                        "lon": property_info["lon"],
                        "radius": radius,
                        "filters": common_filters or {}
                    }
                else:
                    raise ValueError("Property must have either property_id or lat/lon")
                
                # Generate output filename
                timestamp = self.file_ops.generate_timestamp()
                prop_id = property_info.get("property_id", f"lat{property_info.get('lat', 'unknown')}")
                output_file = Path(output_dir) / f"comparable_analysis_{prop_id}_{timestamp}.csv"
                
                # Run search and analysis
                df, metadata = self.process_comparable_search(
                    search_type, search_params, str(output_file),
                    include_analysis=True, delay=0
                )
                
                property_result = {
                    "property_info": property_info,
                    "search_metadata": metadata,
                    "results_file": str(output_file) if not df.empty else None,
                    "comparable_count": len(df),
                    "success": True
                }
                
                batch_results["results"].append(property_result)
                batch_results["successful_searches"] += 1
                error_handler.handle_item_success(str(property_info), property_result)
                
                self.reporter.success(f"Property {i}: {len(df)} comparables found")
                
            except Exception as e:
                property_result = {
                    "property_info": property_info,
                    "error": str(e),
                    "success": False
                }
                
                batch_results["results"].append(property_result)
                batch_results["failed_searches"] += 1
                error_handler.handle_item_error(str(property_info), e)
            
            if delay > 0:
                time.sleep(delay)
        
        # Generate batch summary
        if batch_results["successful_searches"] > 0:
            total_comparables = sum(r.get("comparable_count", 0) for r in batch_results["results"] if r["success"])
            avg_comparables = total_comparables / batch_results["successful_searches"]
            
            batch_results["summary"] = {
                "total_comparables_found": total_comparables,
                "average_comparables_per_property": avg_comparables,
                "success_rate": batch_results["successful_searches"] / len(properties_list) * 100
            }
        
        # Save batch results
        batch_file = Path(output_dir) / f"batch_comparable_analysis_{self.file_ops.generate_timestamp()}.json"
        self.data_processor.save_json(batch_results, batch_file)
        
        error_handler.print_summary()
        
        return batch_results
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """Get summary of comparable processing operations."""
        return {
            "cached_searches": len(self.search_cache),
            "available_filter_templates": list(self.filter_templates.keys()),
            "cache_size_kb": len(str(self.search_cache)) / 1024
        }
    
    def clear_cache(self):
        """Clear search cache."""
        self.search_cache.clear()
        self.reporter.info("Comparable search cache cleared")


def search_comparables_by_coordinates(lat: float, lon: float, radius: float,
                                    filters: Dict[str, Any] = None,
                                    output_file: str = None,
                                    get_all_pages: bool = False) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Convenience function for coordinate-based comparable search.
    
    Args:
        lat: Latitude
        lon: Longitude
        radius: Search radius in km
        filters: Optional filters
        output_file: Output file path
        get_all_pages: Whether to get all pages
        
    Returns:
        Tuple of (DataFrame, metadata)
    """
    processor = ComparableDataProcessor()
    
    search_params = {
        "lat": lat,
        "lon": lon,
        "radius": radius,
        "filters": filters or {}
    }
    
    return processor.process_comparable_search(
        "coordinates", search_params, output_file, get_all_pages=get_all_pages
    )


if __name__ == "__main__":
    # Example usage
    processor = ComparableDataProcessor()
    
    # Search by coordinates with filters
    filters = processor.create_search_filters(
        template="similar_houses",
        price="800000-1200000",
        beds="4-5"
    )
    
    df, metadata = processor.process_comparable_search(
        "coordinates",
        {
            "lat": -33.8688,
            "lon": 151.2093,
            "radius": 5.0,
            "filters": filters
        },
        output_file="data/comparable_analysis_sydney.csv",
        include_analysis=True
    )
    
    print(f"Found {len(df)} comparable properties")
    if metadata.get("analysis"):
        price_stats = metadata["analysis"].get("price_analysis", {})
        print(f"Median price: ${price_stats.get('median_price', 0):,.0f}")