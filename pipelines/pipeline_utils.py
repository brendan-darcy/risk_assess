#!/usr/bin/env python3
"""
Pipeline Utilities

Base classes and utilities for all pipeline operations. Provides common patterns
for authentication, API requests, data processing, file operations, and error handling.

Author: Market Analysis Pipeline
Date: 2025-08-22
"""

import json
import os
import sys
import time
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple
from abc import ABC, abstractmethod

# Add pipelines to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'pipelines'))


class PipelineConfig:
    """Configuration manager for pipeline settings"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize with optional config file path"""
        self.config_path = Path(config_path) if config_path else None
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            "data_dir": "data/test_results",
            "rules_file": "data/rules/risk_rules_example.json",
            "location_id": 200840,
            "location_type_id": 4,  # Suburb
            "property_type_id": 1,  # Houses
            "from_date": "2021-01-01",
            "to_date": "2022-01-01",
            "interval": 1  # Monthly
        }
        
        if self.config_path and self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    file_config = json.load(f)
                    default_config.update(file_config)
            except Exception as e:
                print(f"⚠️  Warning: Could not load config file {self.config_path}: {e}")
                print("   Using default configuration")
        
        return default_config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value
    
    def save(self, path: Optional[str] = None):
        """Save current configuration to file"""
        save_path = Path(path) if path else self.config_path
        if save_path:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'w') as f:
                json.dump(self.config, f, indent=2)


class ProgressReporter:
    """Standardized progress reporting for all pipelines"""
    
    def __init__(self, title: str):
        """Initialize with pipeline title"""
        self.title = title
        self.start_time = datetime.now()
        
    def print_header(self):
        """Print pipeline header"""
        print("=" * 70)
        print(self.title)
        print("=" * 70)
        print(f"Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def print_step(self, step_number: int, step_name: str):
        """Print step header"""
        print(f"\n" + "=" * 50)
        print(f"STEP {step_number}: {step_name}")
        print("=" * 50)
    
    def success(self, message: str):
        """Print success message"""
        print(f"✅ {message}")
    
    def error(self, message: str):
        """Print error message"""
        print(f"❌ {message}")
    
    def warning(self, message: str):
        """Print warning message"""
        print(f"⚠️  {message}")
    
    def info(self, message: str):
        """Print info message"""
        print(f"📊 {message}")
    
    def file_info(self, message: str):
        """Print file-related message"""
        print(f"📁 {message}")
    
    def print_summary(self, **kwargs):
        """Print final summary"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        print(f"\n" + "=" * 50)
        print("PIPELINE COMPLETE")
        print("=" * 50)
        
        for key, value in kwargs.items():
            print(f"✅ {key.replace('_', ' ').title()}: {value}")
        
        print(f"⏱️  Duration: {duration.total_seconds():.1f} seconds")
        print(f"🏁 Completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")


class FileManager:
    """File management utilities"""
    
    @staticmethod
    def ensure_dir(path: Union[str, Path]) -> Path:
        """Ensure directory exists and return Path object"""
        path_obj = Path(path)
        path_obj.mkdir(parents=True, exist_ok=True)
        return path_obj
    
    @staticmethod
    def get_file_info(file_path: Union[str, Path]) -> Dict[str, Any]:
        """Get file information including size and modification time"""
        path_obj = Path(file_path)
        if not path_obj.exists():
            return {"exists": False}
        
        stat = path_obj.stat()
        return {
            "exists": True,
            "size_kb": stat.st_size / 1024,
            "size_mb": stat.st_size / (1024 * 1024),
            "modified": datetime.fromtimestamp(stat.st_mtime),
            "name": path_obj.name,
            "stem": path_obj.stem,
            "suffix": path_obj.suffix,
            "parent": str(path_obj.parent)
        }
    
    @staticmethod
    def find_files_by_pattern(directory: Union[str, Path], pattern: str, 
                            sort_by: str = "mtime") -> List[Path]:
        """Find files matching pattern, sorted by modification time or name"""
        dir_path = Path(directory)
        if not dir_path.exists():
            return []
        
        files = list(dir_path.glob(pattern))
        
        if sort_by == "mtime":
            files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        elif sort_by == "name":
            files.sort()
        
        return files
    
    @staticmethod
    def generate_timestamp() -> str:
        """Generate timestamp string for filenames"""
        return datetime.now().strftime('%Y%m%d_%H%M%S')
    
    @staticmethod
    def parse_filename_timestamp(filename: str) -> Optional[datetime]:
        """Parse timestamp from filename"""
        # Handle formats like: market_timeseries_200840_20250725_153419.csv
        parts = Path(filename).stem.split('_')
        if len(parts) >= 2:
            # Look for date_time pattern
            for i in range(len(parts) - 1):
                try:
                    date_str = parts[i]
                    time_str = parts[i + 1]
                    if len(date_str) == 8 and len(time_str) == 6:
                        datetime_str = f"{date_str}_{time_str}"
                        return datetime.strptime(datetime_str, '%Y%m%d_%H%M%S')
                except (ValueError, IndexError):
                    continue
        return None


class PipelineError(Exception):
    """Custom exception for pipeline errors"""
    
    def __init__(self, message: str, step: Optional[str] = None, 
                 cause: Optional[Exception] = None):
        """Initialize with message, optional step name and cause"""
        self.step = step
        self.cause = cause
        super().__init__(message)
    
    def __str__(self):
        """String representation with step information"""
        base_msg = super().__str__()
        if self.step:
            return f"[{self.step}] {base_msg}"
        return base_msg


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def validate_location_id(location_id: Union[str, int]) -> int:
    """Validate and convert location ID to integer"""
    try:
        loc_id = int(location_id)
        if loc_id <= 0:
            raise ValueError("Location ID must be positive")
        return loc_id
    except (ValueError, TypeError):
        raise PipelineError(f"Invalid location ID: {location_id}")


def validate_date_range(from_date: str, to_date: str) -> tuple[str, str]:
    """Validate date range format and order"""
    try:
        from_dt = datetime.strptime(from_date, '%Y-%m-%d')
        to_dt = datetime.strptime(to_date, '%Y-%m-%d')
        
        if from_dt >= to_dt:
            raise ValueError("from_date must be before to_date")
        
        return from_date, to_date
    except ValueError as e:
        raise PipelineError(f"Invalid date range: {e}")


# =============================================================================
# BASE PIPELINE ABSTRACTIONS
# =============================================================================

class DataProcessor:
    """Common data processing utilities"""
    
    @staticmethod
    def flatten_json_recursive(data: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
        """Flatten nested JSON structures recursively"""
        items = []
        
        if isinstance(data, dict):
            for k, v in data.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                
                if isinstance(v, dict):
                    items.extend(DataProcessor.flatten_json_recursive(v, new_key, sep=sep).items())
                elif isinstance(v, list) and v:
                    if isinstance(v[0], dict):
                        for i, item in enumerate(v):
                            items.extend(DataProcessor.flatten_json_recursive(item, f"{new_key}{sep}{i}", sep=sep).items())
                    else:
                        items.append((new_key, v))
                else:
                    items.append((new_key, v))
        
        return dict(items)
    
    @staticmethod
    def save_dataframe(df: pd.DataFrame, output_file: Union[str, Path], create_dirs: bool = True, verbose: bool = True) -> Path:
        """Save DataFrame with standard options"""
        output_path = Path(output_file)
        
        if create_dirs:
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        df.to_csv(output_path, index=False)
        
        if verbose:
            file_info = FileManager.get_file_info(output_path)
            print(f"📊 Results saved to: {output_path} ({file_info['size_kb']:.1f} KB)")
        
        return output_path
    
    @staticmethod
    def save_json(data: Dict[str, Any], output_file: Union[str, Path], create_dirs: bool = True, verbose: bool = True) -> Path:
        """Save JSON data with standard options"""
        output_path = Path(output_file)
        
        if create_dirs:
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        if verbose:
            file_info = FileManager.get_file_info(output_path)
            print(f"📄 JSON saved to: {output_path} ({file_info['size_kb']:.1f} KB)")
        
        return output_path
    
    @staticmethod
    def generate_timestamped_filename(base_name: str, suffix: str = '.csv', 
                                    timestamp_format: str = '%Y%m%d_%H%M%S', 
                                    directory: Union[str, Path] = 'data') -> Path:
        """Generate timestamped filenames"""
        timestamp = datetime.now().strftime(timestamp_format)
        filename = f"{base_name}_{timestamp}{suffix}"
        return Path(directory) / filename
    
    @staticmethod
    def read_text_file_lines(file_path: Union[str, Path], strip_empty: bool = True) -> List[str]:
        """Read text file as list of lines"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise PipelineError(f"File not found: {file_path}")
        
        with open(file_path, 'r') as f:
            lines = [line.strip() for line in f]
        
        if strip_empty:
            lines = [line for line in lines if line]
        
        return lines


class ErrorHandler:
    """Centralized error handling and tracking"""
    
    def __init__(self):
        self.processed = []
        self.failed = []
        self.errors = []
    
    def handle_item_error(self, item: str, error: Exception, continue_processing: bool = True) -> bool:
        """Handle individual item processing errors"""
        self.failed.append(item)
        error_msg = str(error)
        self.errors.append({"item": item, "error": error_msg, "type": type(error).__name__})
        
        print(f"❌ Error processing {item}: {error_msg}")
        
        return continue_processing
    
    def handle_item_success(self, item: str, result: Any = None):
        """Handle successful item processing"""
        self.processed.append(item)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get processing summary"""
        total = len(self.processed) + len(self.failed)
        success_rate = (len(self.processed) / total * 100) if total > 0 else 0
        
        return {
            "total_items": total,
            "processed_count": len(self.processed),
            "failed_count": len(self.failed),
            "success_rate": success_rate,
            "processed_items": self.processed,
            "failed_items": self.failed,
            "errors": self.errors
        }
    
    def print_summary(self):
        """Print processing summary"""
        summary = self.get_summary()
        
        print(f"\n📊 Processing Summary:")
        print(f"   ✅ Successfully processed: {summary['processed_count']} items")
        print(f"   ❌ Failed to process: {summary['failed_count']} items")
        
        if summary['total_items'] > 0:
            print(f"   📈 Success rate: {summary['success_rate']:.1f}%")
        
        if self.failed:
            print(f"\nFailed items:")
            for item in self.failed:
                print(f"   - {item}")


class CoreLogicAPIClient:
    """Enhanced API client for CoreLogic requests with comprehensive error handling"""
    
    def __init__(self, access_token: str, base_url: str = "https://api-uat.corelogic.asia"):
        self.access_token = access_token
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "accept": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def make_request(self, endpoint: str, params: dict = None, method: str = 'GET', 
                    payload: dict = None, retry_count: int = 3, delay: float = 0.1, 
                    debug: bool = False) -> Optional[dict]:
        """Enhanced API request with comprehensive error handling and retries"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        if debug:
            print(f"🔍 API Request: {method} {url}")
            if payload:
                print(f"🔍 Payload: {payload}")
            if params:
                print(f"🔍 Params: {params}")
        
        for attempt in range(retry_count):
            try:
                if delay > 0:
                    time.sleep(delay)
                
                if method.upper() == 'GET':
                    response = self.session.get(url, params=params, timeout=30)
                else:
                    response = self.session.post(url, json=payload, timeout=30)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    print(f"❌ Authentication failed - check credentials")
                    return None
                elif response.status_code == 429:
                    wait_time = delay * (2 ** attempt)  # Exponential backoff for rate limiting
                    print(f"⚠️ Rate limited (attempt {attempt + 1}/{retry_count}), waiting {wait_time:.1f}s")
                    time.sleep(wait_time)
                    continue
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                    if attempt < retry_count - 1:
                        print(f"⚠️ Request failed (attempt {attempt + 1}/{retry_count}): {error_msg}")
                        time.sleep(delay * (attempt + 1))
                        continue
                    else:
                        print(f"❌ API request failed after {retry_count} attempts: {error_msg}")
                        return None
            
            except requests.exceptions.Timeout:
                if attempt < retry_count - 1:
                    print(f"⚠️ Request timeout (attempt {attempt + 1}/{retry_count})")
                    time.sleep(delay * (attempt + 1))
                    continue
                else:
                    print(f"❌ API request timed out after {retry_count} attempts")
                    return None
            except Exception as e:
                if attempt < retry_count - 1:
                    print(f"⚠️ Request error (attempt {attempt + 1}/{retry_count}): {e}")
                    time.sleep(delay * (attempt + 1))
                    continue
                else:
                    print(f"❌ API request error after {retry_count} attempts: {e}")
                    return None
        
        return None
    
    def get_property_suggestions(self, address: str, limit: int = 3, offset: int = 0) -> List[dict]:
        """Get property suggestions for an address"""
        params = {
            "q": address,
            "suggestionTypes": "address",
            "limit": min(limit, 100),
            "offset": offset
        }
        
        response = self.make_request("/property/au/v2/suggest.json", params=params)
        if response and 'suggestions' in response:
            return response['suggestions']
        return []
    
    def get_property_details(self, property_id: str, endpoints_list: List[str] = None) -> Dict[str, Any]:
        """
        Get property details for a property ID
        
        Args:
            property_id: The property ID to fetch details for
            endpoints_list: List of specific endpoints to fetch (defaults to all if None)
        
        Returns:
            Dictionary with property details from requested endpoints
        """
        available_endpoints = {
            "location": f"/property-details/au/properties/{property_id}/location",
            "legal": f"/property-details/au/properties/{property_id}/legal",
            "site": f"/property-details/au/properties/{property_id}/site",
            "core_attributes": f"/property-details/au/properties/{property_id}/attributes/core",
            "additional_attributes": f"/property-details/au/properties/{property_id}/attributes/additional",
            "features": f"/property-details/au/properties/{property_id}/features",
            "occupancy": f"/property-details/au/properties/{property_id}/occupancy",
            "last_sale": f"/property-details/au/properties/{property_id}/sales/last",
            "sales": f"/property-details/au/properties/{property_id}/sales",
            "rent campaigns": f"/property-details/au/properties/{property_id}/otm/campaign/rent",
            "advertisements": f"/property/au/v1/property/{property_id}/advertisements.json",
            "timeline": f"/property-timeline/au/properties/{property_id}/timeline",
        }
        
        # Use all endpoints if none specified
        if endpoints_list is None:
            endpoints_to_fetch = available_endpoints
        else:
            # Filter to requested endpoints only
            endpoints_to_fetch = {
                key: available_endpoints[key] 
                for key in endpoints_list 
                if key in available_endpoints
            }
        
        results = {}
        for key, endpoint in endpoints_to_fetch.items():
            response = self.make_request(endpoint)
            if response:
                results[key] = response
            else:
                results[key] = {"error": "No data available"}
        
        return results
    
    def get_market_statistics(self, payload: dict, debug: bool = False) -> Optional[dict]:
        """Get market statistics data"""
        return self.make_request("/statistics/v1/statistics.json", method='POST', 
                               payload=payload, debug=debug)
    
    def search_comparable_properties(self, search_params: dict) -> Optional[dict]:
        """Search for comparable properties"""
        return self.make_request("/search/au/property/geo/radius/lastSale", params=search_params)
    
    def paginated_request(self, endpoint: str, params: dict = None, max_pages: int = None,
                         page_size: int = 100, delay: float = 0.1, 
                         response_data_key: str = 'data') -> List[dict]:
        """Enhanced paginated API responses with flexible data extraction"""
        all_results = []
        page = 0  # Start with 0 for CoreLogic APIs
        
        while True:
            request_params = params.copy() if params else {}
            request_params.update({
                'page': page,
                'size': min(page_size, 100)  # CoreLogic max is usually 100
            })
            
            response = self.make_request(endpoint, params=request_params, delay=delay)
            
            if not response:
                break
            
            # Handle different response structures
            if response_data_key in response:
                page_results = response[response_data_key]
            elif 'suggestions' in response:
                page_results = response['suggestions']
            elif '_embedded' in response:
                embedded = response['_embedded']
                if 'propertySummaryList' in embedded:
                    page_results = [item.get('propertySummary', item) for item in embedded['propertySummaryList']]
                else:
                    page_results = list(embedded.values())[0] if embedded else []
            elif isinstance(response, list):
                page_results = response
            else:
                page_results = [response]
            
            if not page_results:
                break
            
            all_results.extend(page_results)
            
            # Check pagination info
            page_info = response.get('page', {})
            total_pages = page_info.get('totalPages', 1)
            current_page = page_info.get('number', page)
            
            # Stop if we've reached the end or max pages
            if current_page >= total_pages - 1 or (max_pages and page >= max_pages - 1):
                break
            
            # Check if we got fewer results than requested (indicates end)
            if len(page_results) < page_size:
                break
            
            page += 1
        
        return all_results
    
    def close(self):
        """Close the session"""
        if self.session:
            self.session.close()


# Maintain backward compatibility
APIClient = CoreLogicAPIClient


class BasePipeline(ABC):
    """Base pipeline class with all common functionality"""
    
    def __init__(self, config: PipelineConfig = None, reporter: ProgressReporter = None, 
                 pipeline_name: str = None):
        self.config = config or PipelineConfig()
        self.pipeline_name = pipeline_name or self.__class__.__name__
        self.reporter = reporter or ProgressReporter(self.pipeline_name)
        self.file_ops = FileManager()
        self.data_processor = DataProcessor()
        self.error_handler = ErrorHandler()
    
    @abstractmethod
    def validate_inputs(self) -> bool:
        """Validate pipeline inputs - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def execute_pipeline(self) -> Dict[str, Any]:
        """Execute the main pipeline logic - must be implemented by subclasses"""
        pass
    
    def run(self) -> Dict[str, Any]:
        """Standard pipeline execution flow"""
        try:
            self.reporter.print_header()
            
            # Step 1: Validate inputs
            self.reporter.print_step(1, "VALIDATING INPUTS")
            if not self.validate_inputs():
                raise PipelineError("Input validation failed")
            self.reporter.success("Input validation completed")
            
            # Step 2: Execute main pipeline
            self.reporter.print_step(2, "EXECUTING PIPELINE")
            result = self.execute_pipeline()
            
            # Step 3: Generate summary
            self.reporter.print_step(3, "GENERATING SUMMARY")
            summary = self._generate_summary(result)
            
            self.reporter.print_summary(**summary)
            return result
            
        except PipelineError:
            raise
        except Exception as e:
            raise PipelineError(f"Pipeline execution failed: {e}")
    
    def _generate_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate pipeline summary - can be overridden by subclasses"""
        error_summary = self.error_handler.get_summary()
        return {
            "pipeline_name": self.pipeline_name,
            "items_processed": error_summary.get('processed_count', 0),
            "items_failed": error_summary.get('failed_count', 0),
            "success_rate": f"{error_summary.get('success_rate', 0):.1f}%"
        }


class AuthenticatedPipeline(BasePipeline):
    """Pipeline with CoreLogic authentication"""
    
    def __init__(self, config: PipelineConfig = None, reporter: ProgressReporter = None,
                 pipeline_name: str = None):
        super().__init__(config, reporter, pipeline_name)
        self.auth = None
        self.access_token = None
        self.api_client = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with CoreLogic API"""
        try:
            from corelogic_auth import CoreLogicAuth
            
            self.auth = CoreLogicAuth.from_env()
            # Always get a fresh token for each script run
            self.access_token = self.auth.refresh_token()
            self.api_client = CoreLogicAPIClient(self.access_token)
            
            self.reporter.success("Authentication successful")
            
        except ValueError as e:
            self.reporter.error(f"Authentication failed: {e}")
            self.reporter.error("Please ensure CORELOGIC_CLIENT_ID and CORELOGIC_CLIENT_SECRET are set")
            raise PipelineError(f"Authentication failed: {e}")
        except Exception as e:
            self.reporter.error(f"Failed to get access token: {e}")
            raise PipelineError(f"Authentication error: {e}")


class DataProcessingPipeline(AuthenticatedPipeline):
    """Pipeline for data processing operations"""
    
    def process_items(self, items: List[Any], processor_func, progress_label: str = "item") -> Tuple[List, List, List]:
        """Generic item processing with error handling and progress reporting"""
        self.error_handler = ErrorHandler()  # Reset for new processing
        
        for i, item in enumerate(items, 1):
            try:
                self.reporter.info(f"Processing {progress_label} {i}/{len(items)}: {item}")
                
                result = processor_func(item)
                
                if result:
                    self.error_handler.handle_item_success(item, result)
                    self.reporter.success(f"Successfully processed: {item}")
                else:
                    self.error_handler.handle_item_error(item, Exception("Processing returned no result"))
                
            except Exception as e:
                self.error_handler.handle_item_error(item, e)
        
        summary = self.error_handler.get_summary()
        return summary['processed_items'], summary['failed_items'], summary['errors']


# ===============================================================================
# INDEXATION UTILITIES
# ===============================================================================

def index_value_to_date(transaction_value: float,
                       transaction_date: str,
                       target_date: str,
                       index_series: List[Dict[str, Any]],
                       date_field: str = 'date',
                       value_field: str = 'median_avm',
                       match_by_month: bool = True) -> Dict[str, Any]:
    """
    Index a transaction value from one date to another using a time series.
    
    This function adjusts a historical transaction value to what it would be worth
    at a target date, using an index series (e.g., median AVM values).
    
    Args:
        transaction_value: Original transaction value (e.g., sale price)
        transaction_date: Date of the original transaction (YYYY-MM-DD)
        target_date: Date to index the value to (YYYY-MM-DD)
        index_series: List of dictionaries with date and value fields
        date_field: Field name for dates in the index series
        value_field: Field name for values in the index series
        match_by_month: If True, matches by year-month only (ignoring day)
        
    Returns:
        Dictionary containing:
        - indexed_value: The adjusted value at target_date
        - index_ratio: The ratio applied (target_index / transaction_index)
        - transaction_index: Index value at transaction date
        - target_index: Index value at target date
        - method: Indexation method used
        - status: 'success' or 'error'
        - error: Error message if status is 'error'
        
    Example:
        # Index a 2020 sale price of $800K to 2022 values using median AVM series
        result = index_value_to_date(
            transaction_value=800000,
            transaction_date="2020-06-30",
            target_date="2022-03-31", 
            index_series=median_avm_series
        )
        print(f"Indexed value: ${result['indexed_value']:,.0f}")
    """
    try:
        import pandas as pd
        from datetime import datetime
        
        # Convert index series to DataFrame for easier manipulation
        df = pd.DataFrame(index_series)
        
        if df.empty:
            return {
                'status': 'error',
                'error': 'Index series is empty'
            }
        
        # Ensure date column exists
        if date_field not in df.columns:
            return {
                'status': 'error', 
                'error': f"Date field '{date_field}' not found in index series"
            }
            
        if value_field not in df.columns:
            return {
                'status': 'error',
                'error': f"Value field '{value_field}' not found in index series"
            }
        
        # Convert dates to datetime and sort
        df[date_field] = pd.to_datetime(df[date_field])
        df = df.sort_values(date_field)
        
        # Parse input dates
        transaction_dt = pd.to_datetime(transaction_date)
        target_dt = pd.to_datetime(target_date)
        
        # Create month-year strings for matching if requested
        if match_by_month:
            df['month_year'] = df[date_field].dt.to_period('M').astype(str)
            transaction_month = transaction_dt.to_period('M').strftime('%Y-%m')
            target_month = target_dt.to_period('M').strftime('%Y-%m')
            
            # Find matching records by month-year
            transaction_matches = df[df['month_year'] == transaction_month]
            target_matches = df[df['month_year'] == target_month]
            
            if transaction_matches.empty:
                return {
                    'status': 'error',
                    'error': f"No index data found for transaction month {transaction_month}"
                }
                
            if target_matches.empty:
                return {
                    'status': 'error', 
                    'error': f"No index data found for target month {target_month}"
                }
            
            # Use the first match (or could use last/average)
            transaction_index = transaction_matches.iloc[0][value_field]
            target_index = target_matches.iloc[0][value_field]
            method = 'month_match'
            
        else:
            # Exact date matching
            transaction_matches = df[df[date_field] == transaction_dt]
            target_matches = df[df[date_field] == target_dt]
            
            if transaction_matches.empty:
                return {
                    'status': 'error',
                    'error': f"No index data found for transaction date {transaction_date}"
                }
                
            if target_matches.empty:
                return {
                    'status': 'error',
                    'error': f"No index data found for target date {target_date}"
                }
            
            transaction_index = transaction_matches.iloc[0][value_field]
            target_index = target_matches.iloc[0][value_field]
            method = 'exact_date'
        
        # Check for zero or negative index values
        if transaction_index <= 0:
            return {
                'status': 'error',
                'error': f"Invalid transaction index value: {transaction_index}"
            }
            
        if target_index <= 0:
            return {
                'status': 'error',
                'error': f"Invalid target index value: {target_index}"
            }
        
        # Calculate indexation
        index_ratio = target_index / transaction_index
        indexed_value = transaction_value * index_ratio
        
        return {
            'status': 'success',
            'indexed_value': indexed_value,
            'index_ratio': index_ratio,
            'transaction_index': transaction_index,
            'target_index': target_index,
            'transaction_date': transaction_date,
            'target_date': target_date,
            'original_value': transaction_value,
            'method': method
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': f"Indexation calculation failed: {str(e)}"
        }