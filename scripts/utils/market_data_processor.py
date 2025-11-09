#!/usr/bin/env python3
"""
Simplified Market Data Processor

Streamlined version with only essential functionality:
- Market statistics retrieval from CoreLogic
- Time series data generation
- Basic configuration management
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from .pipeline_utils import AuthenticatedPipeline, PipelineError


class MarketDataProcessor(AuthenticatedPipeline):
    """Simplified processor for CoreLogic market data operations."""
    
    def __init__(self, config=None, reporter=None):
        super().__init__(config, reporter, "Market Data Processor")
        self.market_metrics = self._get_default_metrics()
    
    def validate_inputs(self) -> bool:
        """Validate that we have API access"""
        return self.api_client is not None
    
    def execute_pipeline(self) -> Dict[str, Any]:
        """Execute the market data pipeline (placeholder - use specific methods instead)"""
        return {"status": "use_specific_methods", "available_methods": ["fetch_comprehensive_market_data", "create_time_series_dataframe"]}
    
    def _get_default_metrics(self) -> List[Dict[str, Any]]:
        """Default set of market metrics to fetch"""
        return [
            {'name': 'sales_volume', 'metricTypeId': 11, 'interval': 2, 'description': 'Sales Volume'},
            {'name': 'median_sale_price', 'metricTypeId': 1, 'interval': 2, 'description': 'Median Sale Price'},
            {'name': 'median_value', 'metricTypeId': 8, 'interval': 1, 'description': 'Median Value'},
            {'name': 'vendor_discount', 'metricTypeId': 103, 'interval': 12, 'description': 'Median Vendor Discount'},
            {'name': 'total_listings', 'metricTypeId': 12, 'interval': 1, 'description': 'Total Listings'},
            {'name': 'days_on_market', 'metricTypeId': 19, 'interval': 12, 'description': 'Median Days on Market'},
            {'name': 'rental_yield', 'metricTypeId': 20, 'interval': 1, 'description': 'Rental Yield'},
            {'name': 'median_rent', 'metricTypeId': 25, 'interval': 2, 'description': 'Median Asking Rent'}
        ]
    
    def set_market_metrics(self, metrics: List[Dict[str, Any]]):
        """Set custom metrics configuration"""
        self.market_metrics = metrics
        if self.reporter:
            self.reporter.success(f"Configured {len(metrics)} market metrics")
    
    def fetch_comprehensive_market_data(self, location_id: int,
                                     location_type_id: int = 4, property_type_id: int = 1,
                                     from_date: str = None, to_date: str = None) -> Dict[str, Any]:
        """Fetch all configured market metrics for a location"""
        if self.reporter:
            self.reporter.info(f"Location: {location_id} (Type: {location_type_id}, Property: {property_type_id})")
            self.reporter.info(f"Period: {from_date} to {to_date}")
        
        market_indicators = {}
        success_count = 0
        
        # Fetch core metrics
        for metric_config in self.market_metrics:
            if self.reporter:
                description = metric_config.get('description') or metric_config.get('display_name', metric_config['name'])
                interval = metric_config.get('interval', 1)
                self.reporter.info(f"Fetching {description} ({interval} months)...")
            
            data_points = self._fetch_single_metric(
                location_id, metric_config, location_type_id, property_type_id, from_date, to_date
            )
            
            if data_points:
                market_indicators[metric_config['name']] = data_points
                success_count += 1
                if self.reporter:
                    self.reporter.success(f"{metric_config['name']}: {len(data_points)} data points")
            else:
                if self.reporter:
                    self.reporter.warning(f"{metric_config['name']}: No data returned")
        
        # Fetch price brackets
        if self.reporter:
            self.reporter.info("Fetching price bracket data...")
        
        price_brackets = self._fetch_price_brackets(location_id, location_type_id, property_type_id, from_date, to_date)
        if price_brackets:
            success_count += len(price_brackets)
            if self.reporter:
                self.reporter.success(f"Retrieved {len(price_brackets)} price bracket series")
        
        success_rate = (success_count / (len(self.market_metrics) + 6)) * 100 if self.market_metrics else 0
        
        if self.reporter:
            self.reporter.success(f"Market data fetch completed: {success_rate:.1f}% success rate")
        
        # Extract location name from any successful API response
        location_name = None
        if price_brackets and len(price_brackets) > 0:
            location_name = price_brackets[0].get('location_name', '')
        
        # If no location name from price brackets, try to get from first market indicator response
        if not location_name:
            for metric_data in market_indicators.values():
                if metric_data and len(metric_data) > 0:
                    # Try a single metric API call to get location name
                    break
        
        return {
            'metadata': {
                'location_id': location_id,
                'location_name': location_name or f"Location {location_id}",
                'location_type_id': location_type_id,
                'property_type_id': property_type_id,
                'from_date': from_date,
                'to_date': to_date,
                'fetch_timestamp': datetime.now().isoformat()
            },
            'market_indicators': market_indicators,
            'price_brackets': price_brackets,
            'summary': {
                'successful_metrics': success_count,
                'total_data_points': sum(len(points) for points in market_indicators.values()) + len(price_brackets)
            }
        }
    
    def _fetch_single_metric(self, location_id: int, metric_config: Dict[str, Any],
                           location_type_id: int, property_type_id: int, from_date: str, to_date: str) -> List[Dict[str, Any]]:
        """Fetch data for a single metric"""
        payload = {
            "seriesRequestList": [{
                "fromDate": from_date or (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d'),
                "toDate": to_date or datetime.now().strftime('%Y-%m-%d'),
                "interval": metric_config.get('interval', 1),
                "locationId": location_id,
                "locationTypeId": location_type_id,
                "metricTypeId": metric_config['metricTypeId'],
                "propertyTypeId": property_type_id
            }]
        }
        
        response = self.api_client.get_market_statistics(payload)
        
        if not response or 'seriesResponseList' not in response:
            return []
        
        series_list = response['seriesResponseList']
        if not series_list or not series_list[0].get('seriesDataList'):
            return []
        
        data_points = []
        for data_point in series_list[0]['seriesDataList']:
            if data_point.get('value') is not None:
                data_points.append({
                    'date': data_point.get('dateTime'),
                    'value': data_point.get('value'),
                    'metric': metric_config['name'],
                    'metric_id': metric_config['metricTypeId'],
                    'location_id': location_id,
                    'location_type_id': location_type_id,
                    'property_type_id': property_type_id
                })
        
        return data_points

    def fetch_avm_series_for_indexation(self, location_id: int, location_type_id: int, 
                                      property_type_id: int, from_date: str, to_date: str) -> List[Dict[str, Any]]:
        """
        Fetch only the median AVM series needed for indexation.
        Much more efficient than fetch_comprehensive_market_data().
        
        Args:
            location_id: Location identifier
            location_type_id: Location type (8 = suburb)
            property_type_id: Property type (1 = houses)
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            
        Returns:
            List of AVM data points formatted for indexation
        """
        if self.reporter:
            self.reporter.info(f"Fetching AVM series for location {location_id} ({from_date} to {to_date})")
        
        # Find the median_value metric config
        median_value_config = None
        for metric in self.market_metrics:
            if metric['name'] == 'median_value':
                median_value_config = metric
                break
        
        if not median_value_config:
            if self.reporter:
                self.reporter.error("median_value metric not found in configuration")
            return []
        
        # Fetch only the median AVM data
        data_points = self._fetch_single_metric(
            location_id, median_value_config, location_type_id, property_type_id, from_date, to_date
        )
        
        if not data_points:
            if self.reporter:
                self.reporter.warning("No AVM data returned")
            return []
        
        # Convert to the format expected by index_value_to_date()
        avm_series = [
            {
                'date': point['date'],
                'median_avm': point['value']
            } for point in data_points
        ]
        
        if self.reporter:
            self.reporter.success(f"Retrieved {len(avm_series)} AVM data points")
        
        return avm_series
    
    def _fetch_price_brackets(self, location_id: int, location_type_id: int, property_type_id: int,
                            from_date: str, to_date: str) -> List[Dict[str, Any]]:
        """Fetch price bracket data using single API call with metricTypeGroupId"""
        payload = {
            "seriesRequestList": [{
                "fromDate": from_date or (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d'),
                "toDate": to_date or datetime.now().strftime('%Y-%m-%d'),
                "interval": 2,  # Quarterly for price brackets
                "locationId": location_id,
                "locationTypeId": location_type_id,
                "metricTypeGroupId": 1,  # Price brackets group
                "propertyTypeId": property_type_id
            }]
        }
        
        response = self.api_client.get_market_statistics(payload)
        
        if not response or 'seriesResponseList' not in response:
            return []
        
        price_brackets = []
        for series in response['seriesResponseList']:
            bracket_info = {
                'metric_type_id': series.get('metricTypeId'),
                'metric_name': series.get('metricType', ''),
                'metric_short': series.get('metricTypeShort', ''),
                'location_name': series.get('localityName', ''),
                'postcode': series.get('postcodeName', ''),
                'location_id': location_id,
                'series_data': []
            }
            
            if series.get('seriesDataList'):
                for data_point in series['seriesDataList']:
                    if data_point.get('value') is not None:
                        bracket_info['series_data'].append({
                            'date': data_point.get('dateTime'),
                            'value': data_point.get('value')
                        })
            
            price_brackets.append(bracket_info)
        
        return price_brackets
    
    def create_time_series_dataframe(self, market_data: Dict[str, Any] = None) -> pd.DataFrame:
        """Create a pandas DataFrame from market data with proper structure for charting"""
        if not market_data or not market_data.get('market_indicators'):
            return pd.DataFrame()
        
        # Convert market_indicators and price_brackets to long format
        all_data = []
        
        # Add market indicators data
        for metric_name, data_points in market_data['market_indicators'].items():
            for point in data_points:
                all_data.append({
                    'date': point['date'],
                    'location_id': point['location_id'],
                    'metric_category': self._categorize_metric(metric_name),
                    'metric_name': metric_name,
                    'metric_id': point['metric_id'],
                    'value': point['value'],
                    'location_type_id': point['location_type_id'],
                    'property_type_id': point['property_type_id']
                })
        
        # Add price bracket data
        if 'price_brackets' in market_data:
            for bracket_info in market_data['price_brackets']:
                for point in bracket_info.get('series_data', []):
                    all_data.append({
                        'date': point['date'],
                        'location_id': bracket_info['location_id'],
                        'metric_category': 'price_bracket',
                        'metric_name': bracket_info['metric_short'],
                        'metric_id': bracket_info['metric_type_id'],
                        'value': point['value'],
                        'location_type_id': market_data['metadata']['location_type_id'],
                        'property_type_id': market_data['metadata']['property_type_id']
                    })
        
        # Create DataFrame
        df = pd.DataFrame(all_data)
        
        # Ensure date column is properly formatted
        if 'date' in df.columns and not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        
        return df
    
    def _categorize_metric(self, metric_name: str) -> str:
        """Categorize metrics for chart generation"""
        price_metrics = ['median_sale_price', 'median_value', 'median_rent']
        volume_metrics = ['sales_volume', 'total_listings']
        time_metrics = ['days_on_market']
        rate_metrics = ['vendor_discount', 'rental_yield']

        if metric_name in price_metrics:
            return 'price'
        elif metric_name in volume_metrics:
            return 'volume'
        elif metric_name in time_metrics:
            return 'time'
        elif metric_name in rate_metrics:
            return 'rate'
        elif '$' in metric_name:  # Price brackets
            return 'price_bracket'
        else:
            return 'other'

    def generate_market_metrics_summary(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive market metrics availability summary with metadata.

        Args:
            market_data: Output from fetch_comprehensive_market_data()

        Returns:
            Dict containing:
                - availability: Status and metadata for each metric
                - featured_metrics: Trend analysis for key metrics
        """
        if not market_data or 'market_indicators' not in market_data:
            return {
                'availability': {},
                'featured_metrics': {},
                'error': 'No market data available'
            }

        market_indicators = market_data.get('market_indicators', {})
        availability = {}
        featured_metrics = {}

        # Helper function to convert interval to human-readable format
        def interval_to_text(interval: int) -> str:
            if interval == 1:
                return "monthly"
            elif interval == 2:
                return "quarterly"
            elif interval == 12:
                return "yearly"
            else:
                return f"{interval}-month"

        # Analyze each default metric
        for metric_config in self.market_metrics:
            metric_name = metric_config['name']
            metric_description = metric_config['description']
            interval = metric_config.get('interval', 1)

            if metric_name in market_indicators:
                data_points = market_indicators[metric_name]

                if data_points and len(data_points) > 0:
                    # Sort by date to get first and last
                    sorted_points = sorted(data_points, key=lambda x: x['date'])
                    first_point = sorted_points[0]
                    last_point = sorted_points[-1]

                    # Format dates
                    try:
                        first_date = datetime.fromisoformat(first_point['date'].replace('Z', '+00:00'))
                        last_date = datetime.fromisoformat(last_point['date'].replace('Z', '+00:00'))
                        date_range = f"{first_date.strftime('%Y-%m')} to {last_date.strftime('%Y-%m')}"
                    except:
                        date_range = f"{first_point['date']} to {last_point['date']}"

                    # Base availability info
                    availability[metric_name] = {
                        'available': True,
                        'description': metric_description,
                        'data_points': len(data_points),
                        'date_range': date_range,
                        'interval': interval_to_text(interval)
                    }

                    # Calculate trend for value-based metrics (not percentages)
                    if metric_name not in ['vendor_discount', 'rental_yield']:
                        first_value = first_point['value']
                        last_value = last_point['value']

                        if first_value and first_value > 0:
                            growth_amount = last_value - first_value
                            growth_percent = (growth_amount / first_value) * 100

                            availability[metric_name].update({
                                'first_value': first_value,
                                'last_value': last_value,
                                'growth_amount': growth_amount,
                                'growth_percent': round(growth_percent, 1)
                            })

                            # Add to featured metrics if it's a key metric
                            if metric_name in ['median_value', 'median_sale_price', 'median_rent']:
                                featured_metrics[metric_name] = {
                                    'description': metric_description,
                                    'first_date': first_point['date'],
                                    'last_date': last_point['date'],
                                    'first_value': first_value,
                                    'last_value': last_value,
                                    'growth_amount': growth_amount,
                                    'growth_percent': round(growth_percent, 1),
                                    'data_points': len(data_points),
                                    'interval': interval_to_text(interval)
                                }
                    else:
                        # For percentage metrics, just store latest value
                        availability[metric_name].update({
                            'latest_value': last_point['value']
                        })

                        if metric_name == 'rental_yield':
                            featured_metrics['rental_market'] = {
                                'rental_yield': last_point['value'],
                                'rental_yield_date': last_point['date']
                            }
                            # Add median rent if available
                            if 'median_rent' in market_indicators and market_indicators['median_rent']:
                                rent_points = sorted(market_indicators['median_rent'], key=lambda x: x['date'])
                                featured_metrics['rental_market']['median_rent'] = rent_points[-1]['value']
                                featured_metrics['rental_market']['median_rent_date'] = rent_points[-1]['date']
                else:
                    availability[metric_name] = {
                        'available': False,
                        'description': metric_description,
                        'reason': 'Empty data returned from API'
                    }
            else:
                availability[metric_name] = {
                    'available': False,
                    'description': metric_description,
                    'reason': 'No data returned from API'
                }

        return {
            'availability': availability,
            'featured_metrics': featured_metrics,
            'summary': {
                'total_metrics': len(self.market_metrics),
                'available_metrics': sum(1 for m in availability.values() if m.get('available')),
                'unavailable_metrics': sum(1 for m in availability.values() if not m.get('available'))
            }
        }

    def generate_market_timeseries_csv(self, location_id: int, 
                                     location_type_id: int = 4, property_type_id: int = 1,
                                     from_date: str = None, to_date: str = None,
                                     output_dir: str = "outputs") -> tuple:
        """Generate market timeseries CSV file (for compatibility with existing scripts)"""
        # Fetch the data
        market_data = self.fetch_comprehensive_market_data(
            location_id, location_type_id, property_type_id, from_date, to_date
        )
        
        # Create DataFrame
        df = self.create_time_series_dataframe(market_data)
        
        if self.reporter:
            self.reporter.success(f"Market data generated: {len(df)} records")
        
        # Generate filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = f"{output_dir}/market_timeseries_{location_id}_{timestamp}.csv"
        metadata_file = f"{output_dir}/metadata_{location_id}_{timestamp}.json"
        
        # Save files
        df.to_csv(csv_file, index=False)
        
        with open(metadata_file, 'w') as f:
            import json
            json.dump(market_data['metadata'], f, indent=2)
        
        return csv_file, metadata_file