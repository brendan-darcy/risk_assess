#!/usr/bin/env python3
"""
Market Data Pipeline

Generic pipeline for fetching market data from CoreLogic Statistics API.
Handles authentication, API requests, data processing, and storage.

Abstracted from scripts/market_trend_pipeline.py to create reusable components.
"""

import json
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

from .pipeline_utils import AuthenticatedPipeline, DataProcessor, PipelineError


class MarketDataPipeline(AuthenticatedPipeline):
    """Pipeline for fetching and processing market data from CoreLogic Statistics API."""
    
    def __init__(self, config=None, reporter=None):
        super().__init__(config, reporter, "Market Data Pipeline")
        self.base_url = "https://api-uat.corelogic.asia"
        self.market_metrics = []
        self.raw_data = {}
        self.processed_data = {}
    
    def validate_inputs(self) -> bool:
        """Validate pipeline inputs"""
        return True
    
    def execute_pipeline(self) -> Dict[str, Any]:
        """Execute complete market data pipeline"""
        return {"status": "implemented as methods for script consumption"}
    
    def set_market_metrics(self, metrics: List[Dict[str, Any]]):
        """
        Set the market metrics to fetch.
        
        Args:
            metrics: List of metric definitions with name, metricTypeId, display_name
        """
        self.market_metrics = metrics
        self.reporter.info(f"Configured {len(metrics)} market metrics")
    
    def get_default_metrics(self) -> List[Dict[str, Any]]:
        """Get default market metrics configuration."""
        return [
            {"name": "median_sale_price", "metricTypeId": 21, "display_name": "Median Sale Price (12 months)"},
            {"name": "days_on_market", "metricTypeId": 32, "display_name": "Median Days on Market (12 months)"},
            {"name": "vendor_discount", "metricTypeId": 20, "display_name": "Median Vendor Discount (12 months)"},
            {"name": "median_value", "metricTypeId": 11, "display_name": "Median Value (monthly)"},
            {"name": "total_listings", "metricTypeId": 65, "display_name": "Total Listings (monthly)"}
        ]
    
    def fetch_market_data(self, location_id: int, location_type_id: int = 8, 
                         property_type_id: int = 1, from_date: str = None, 
                         to_date: str = None, interval: int = 1) -> bool:
        """
        Fetch market data from CoreLogic Statistics API.
        
        Args:
            location_id: CoreLogic location ID
            location_type_id: Location type (8=Suburb, 4=Postcode, 3=Council)
            property_type_id: Property type (1=Houses, 2=Units, 3=Land)
            from_date: Start date (YYYY-MM-DD), defaults to 2 years ago
            to_date: End date (YYYY-MM-DD), defaults to today
            interval: Data interval (1=monthly, 2=quarterly, 3=yearly)
            
        Returns:
            True if successful, False otherwise
        """
        self.reporter.print_step(1, "FETCHING MARKET DATA")
        
        # Set default date range if not provided
        if not from_date:
            from_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
        if not to_date:
            to_date = datetime.now().strftime('%Y-%m-%d')
        
        # Use default metrics if none configured
        if not self.market_metrics:
            self.market_metrics = self.get_default_metrics()
        
        self.reporter.info(f"Location ID: {location_id}")
        self.reporter.info(f"Period: {from_date} to {to_date}")
        self.reporter.info(f"Location Type: {location_type_id}, Property Type: {property_type_id}")
        
        self.raw_data = {"market_indicators": {}, "price_brackets": []}
        successful_metrics = 0
        
        # 1. Fetch price bracket data first (metricTypeGroupId=1)
        self.reporter.info("Fetching price bracket data...")
        
        try:
            price_bracket_payload = {
                "seriesRequestList": [{
                    "fromDate": from_date,
                    "toDate": to_date,
                    "interval": interval,
                    "locationId": location_id,
                    "locationTypeId": location_type_id,
                    "metricTypeGroupId": 1,  # Number Sold by Price brackets
                    "propertyTypeId": property_type_id
                }]
            }
            
            price_bracket_response = self._make_api_request("/statistics/v1/statistics.json", price_bracket_payload)
            
            if price_bracket_response:
                price_brackets = self._process_price_brackets(price_bracket_response)
                if price_brackets:
                    self.raw_data['price_brackets'] = price_brackets
                    self.reporter.success(f"Retrieved {len(price_brackets)} price bracket series")
                else:
                    self.reporter.warning("No price bracket data available")
            else:
                self.reporter.warning("Price bracket API request failed")
                
        except Exception as e:
            self.reporter.warning(f"Price bracket fetching failed: {e}")
        
        # 2. Fetch each individual market metric
        for metric in self.market_metrics:
            self.reporter.info(f"Fetching {metric['display_name']}...")
            
            try:
                payload = {
                    "seriesRequestList": [{
                        "fromDate": from_date,
                        "toDate": to_date,
                        "interval": interval,
                        "locationId": location_id,
                        "locationTypeId": location_type_id,
                        "metricTypeId": metric['metricTypeId'],
                        "propertyTypeId": property_type_id
                    }]
                }
                
                response = self._make_api_request("/statistics/v1/statistics.json", payload)
                
                if response:
                    processed_metric = self._process_metric_response(response, metric['name'])
                    if processed_metric:
                        self.raw_data['market_indicators'][metric['name']] = processed_metric
                        successful_metrics += 1
                        self.reporter.success(f"{metric['name']}: {len(processed_metric)} data points")
                    else:
                        self.reporter.error(f"{metric['name']}: No data returned")
                else:
                    self.reporter.error(f"{metric['name']}: API request failed")
                    
            except Exception as e:
                self.reporter.error(f"{metric['name']}: {e}")
        
        success = successful_metrics > 0
        self.reporter.info(f"Successfully fetched {successful_metrics}/{len(self.market_metrics)} market metrics")
        
        return success
    
    def _make_api_request(self, endpoint: str, payload: dict, debug: bool = True) -> Optional[dict]:
        """Make authenticated API request to CoreLogic."""
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            
            if debug:
                self.reporter.info(f"API Request: {url}")
                self.reporter.info(f"Payload: {payload}")
            
            response = requests.post(url, headers=self.api_client.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.reporter.error(f"API request failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.reporter.error(f"API request error: {e}")
            return None
    
    def _process_metric_response(self, response: dict, metric_name: str) -> List[Dict[str, Any]]:
        """Process API response for a single metric."""
        try:
            if not response or 'seriesResponseList' not in response:
                return []
            
            series_list = response['seriesResponseList']
            if not series_list or not series_list[0].get('seriesDataList'):
                return []
            
            data_points = []
            for data_point in series_list[0]['seriesDataList']:
                if data_point.get('value') is not None:
                    data_points.append({
                        'date': data_point.get('dateTime'),  # Use correct API field name
                        'value': data_point.get('value'),
                        'metric': metric_name
                    })
            
            return data_points
            
        except Exception as e:
            self.reporter.error(f"Error processing {metric_name} response: {e}")
            return []
    
    def _process_price_brackets(self, response: dict) -> List[Dict[str, Any]]:
        """Process price bracket API response into structured format."""
        try:
            if not response or 'seriesResponseList' not in response:
                return []
            
            processed_brackets = []
            
            for series in response['seriesResponseList']:
                bracket_info = {
                    'metric_type_id': series.get('metricTypeId'),
                    'metric_name': series.get('metricType', ''),
                    'metric_short': series.get('metricTypeShort', ''),
                    'location_name': series.get('localityName', ''),
                    'postcode': series.get('postcodeName', ''),
                    'series_data': []
                }
                
                # Process time series data points
                if series.get('seriesDataList'):
                    for data_point in series['seriesDataList']:
                        if data_point.get('value') is not None:
                            bracket_info['series_data'].append({
                                'date': data_point.get('dateTime'),
                                'value': data_point.get('value')
                            })
                
                processed_brackets.append(bracket_info)
            
            return processed_brackets
            
        except Exception as e:
            self.reporter.error(f"Error processing price brackets response: {e}")
            return []
    
    def create_market_dataframe(self) -> pd.DataFrame:
        """
        Create a combined DataFrame from all fetched market metrics.
        
        Returns:
            DataFrame with dates as index and metrics as columns
        """
        if not self.raw_data.get('market_indicators'):
            raise PipelineError("No market data available to create DataFrame")
        
        # Combine all metrics into a single DataFrame
        all_data = []
        
        for metric_name, data_points in self.raw_data['market_indicators'].items():
            for point in data_points:
                all_data.append({
                    'date': pd.to_datetime(point['date']),
                    'metric': metric_name,
                    'value': point['value']
                })
        
        if not all_data:
            raise PipelineError("No data points found in market indicators")
        
        # Create DataFrame and pivot to have metrics as columns
        df = pd.DataFrame(all_data)
        
        # Handle duplicate dates by taking the mean (or could use last/first)
        df = df.groupby(['date', 'metric'])['value'].mean().reset_index()
        df_pivoted = df.pivot(index='date', columns='metric', values='value')
        df_pivoted = df_pivoted.sort_index()
        
        self.processed_data = {'market_dataframe': df_pivoted}
        
        self.reporter.success(f"Created market DataFrame with {len(df_pivoted)} time periods and {len(df_pivoted.columns)} metrics")
        
        return df_pivoted
    
    def save_market_data(self, output_file: str = None, save_raw: bool = True) -> Tuple[str, Optional[str]]:
        """
        Save market data to files.
        
        Args:
            output_file: Output file path for CSV (auto-generated if None)
            save_raw: Whether to save raw JSON data as well
            
        Returns:
            Tuple of (csv_file_path, json_file_path)
        """
        # Create DataFrame if not already created
        if 'market_dataframe' not in self.processed_data:
            self.create_market_dataframe()
        
        df = self.processed_data['market_dataframe']
        
        # Save CSV
        if not output_file:
            csv_file = self.data_processor.generate_timestamped_filename(
                "market_data", suffix=".csv", directory="data"
            )
        else:
            csv_file = output_file
        
        self.data_processor.save_dataframe(df, csv_file)
        
        # Save raw JSON if requested
        json_file = None
        if save_raw and self.raw_data:
            json_file = self.data_processor.generate_timestamped_filename(
                "market_data_raw", suffix=".json", directory="data"
            )
            self.data_processor.save_json(self.raw_data, json_file)
        
        return str(csv_file), str(json_file) if json_file else None
    
    def get_market_summary(self) -> Dict[str, Any]:
        """Get summary of fetched market data."""
        if not self.raw_data.get('market_indicators'):
            return {"error": "No market data available"}
        
        summary = {
            "metrics_fetched": len(self.raw_data['market_indicators']),
            "metrics_requested": len(self.market_metrics),
            "success_rate": len(self.raw_data['market_indicators']) / len(self.market_metrics) * 100,
            "data_points_by_metric": {}
        }
        
        for metric_name, data_points in self.raw_data['market_indicators'].items():
            summary["data_points_by_metric"][metric_name] = len(data_points)
        
        return summary