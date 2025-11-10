"""
Base API Client

Abstract base class for all API clients (CoreLogic, Google Places, Vicmap, etc.).
Provides consistent patterns for:
- Authentication management
- Request handling with retry logic
- Rate limiting
- Error handling
- Response caching
- Request logging

All API clients should inherit from this class to ensure DRY principles.

Author: Property Reporting System Refactoring
Date: 2025-11-10
"""

import time
import requests
import hashlib
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from pathlib import Path

from .exceptions import (
    APIException,
    AuthenticationException,
    RateLimitException,
    ConfigurationException
)


class BaseAPIClient(ABC):
    """
    Abstract base class for all API clients.

    Subclasses must implement:
    - authenticate(): Authentication logic
    - _get_base_url(): Base URL for API
    - _get_default_headers(): Default headers for requests

    Provides:
    - make_request(): Unified request handling
    - Rate limiting
    - Retry logic
    - Response caching
    - Error handling
    """

    def __init__(self, reporter=None, config: Dict[str, Any] = None):
        """
        Initialize base API client.

        Args:
            reporter: ProgressReporter for logging (optional)
            config: Configuration dictionary (optional)
        """
        self.reporter = reporter
        self.config = config or {}

        # Authentication state
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None

        # Rate limiting
        self._rate_limit_delay = self.config.get('rate_limit_delay', 0.1)
        self._last_request_time: Optional[datetime] = None

        # Retry configuration
        self._max_retries = self.config.get('max_retries', 3)
        self._retry_delay = self.config.get('retry_delay', 1.0)
        self._retry_backoff = self.config.get('retry_backoff', 2.0)

        # Request timeout
        self._timeout = self.config.get('timeout', 30)

        # Caching
        self._enable_cache = self.config.get('enable_cache', False)
        self._cache_dir = Path(self.config.get('cache_dir', '.cache/api'))
        if self._enable_cache:
            self._cache_dir.mkdir(parents=True, exist_ok=True)

        # Statistics
        self._request_count = 0
        self._error_count = 0
        self._cache_hits = 0

    @abstractmethod
    def authenticate(self) -> str:
        """
        Authenticate with the API and return access token.

        Must be implemented by subclasses.

        Returns:
            Access token string

        Raises:
            AuthenticationException: If authentication fails
        """
        pass

    @abstractmethod
    def _get_base_url(self) -> str:
        """
        Get base URL for API.

        Must be implemented by subclasses.

        Returns:
            Base URL string
        """
        pass

    def _get_default_headers(self) -> Dict[str, str]:
        """
        Get default headers for requests.

        Can be overridden by subclasses.

        Returns:
            Dictionary of HTTP headers
        """
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def get_access_token(self) -> str:
        """
        Get valid access token, refreshing if necessary.

        Returns:
            Valid access token

        Raises:
            AuthenticationException: If authentication fails
        """
        # Check if token is still valid
        if self._access_token and self._token_expiry:
            if datetime.now() < self._token_expiry:
                return self._access_token

        # Token expired or doesn't exist, authenticate
        try:
            self._access_token = self.authenticate()
            # Set expiry (default 1 hour if not set by authenticate())
            if not self._token_expiry:
                self._token_expiry = datetime.now() + timedelta(hours=1)

            if self.reporter:
                self.reporter.info("Authentication successful")

            return self._access_token

        except Exception as e:
            raise AuthenticationException(
                f"Failed to authenticate: {str(e)}",
                api_name=self.__class__.__name__
            )

    def _apply_rate_limit(self):
        """Apply rate limiting between requests."""
        if self._last_request_time:
            elapsed = (datetime.now() - self._last_request_time).total_seconds()
            if elapsed < self._rate_limit_delay:
                time.sleep(self._rate_limit_delay - elapsed)

        self._last_request_time = datetime.now()

    def _get_cache_key(self, endpoint: str, params: Dict = None,
                      data: Dict = None) -> str:
        """
        Generate cache key for request.

        Args:
            endpoint: API endpoint
            params: Query parameters
            data: Request body data

        Returns:
            Cache key (hex digest)
        """
        cache_str = f"{endpoint}_{params}_{data}"
        return hashlib.md5(cache_str.encode()).hexdigest()

    def _get_cached_response(self, cache_key: str) -> Optional[Dict]:
        """
        Get cached response if available.

        Args:
            cache_key: Cache key

        Returns:
            Cached response dict or None
        """
        if not self._enable_cache:
            return None

        cache_file = self._cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached = json.load(f)

                # Check if cache is still valid
                cache_time = datetime.fromisoformat(cached['timestamp'])
                cache_ttl = timedelta(seconds=self.config.get('cache_ttl', 3600))

                if datetime.now() - cache_time < cache_ttl:
                    self._cache_hits += 1
                    return cached['response']

            except Exception as e:
                if self.reporter:
                    self.reporter.warning(f"Cache read failed: {e}")

        return None

    def _save_to_cache(self, cache_key: str, response: Dict):
        """
        Save response to cache.

        Args:
            cache_key: Cache key
            response: Response to cache
        """
        if not self._enable_cache:
            return

        cache_file = self._cache_dir / f"{cache_key}.json"
        try:
            cached = {
                'timestamp': datetime.now().isoformat(),
                'response': response
            }
            with open(cache_file, 'w') as f:
                json.dump(cached, f, indent=2)

        except Exception as e:
            if self.reporter:
                self.reporter.warning(f"Cache write failed: {e}")

    def make_request(
        self,
        endpoint: str,
        method: str = 'GET',
        params: Dict[str, Any] = None,
        data: Dict[str, Any] = None,
        headers: Dict[str, str] = None,
        use_cache: bool = True,
        require_auth: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Make authenticated API request with retry logic.

        Args:
            endpoint: API endpoint (relative to base URL)
            method: HTTP method (GET, POST, PUT, DELETE)
            params: Query parameters
            data: Request body data
            headers: Additional headers
            use_cache: Whether to use caching
            require_auth: Whether authentication is required

        Returns:
            Response data as dictionary, or None on failure

        Raises:
            APIException: On API errors
            RateLimitException: On rate limit exceeded
        """
        # Check cache first
        if use_cache and method == 'GET':
            cache_key = self._get_cache_key(endpoint, params, data)
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                if self.reporter:
                    self.reporter.debug(f"Cache hit for {endpoint}")
                return cached_response

        # Apply rate limiting
        self._apply_rate_limit()

        # Build full URL
        base_url = self._get_base_url()
        url = f"{base_url}/{endpoint.lstrip('/')}"

        # Build headers
        request_headers = self._get_default_headers()
        if require_auth:
            token = self.get_access_token()
            request_headers['Authorization'] = f'Bearer {token}'
        if headers:
            request_headers.update(headers)

        # Retry logic
        last_exception = None
        for attempt in range(self._max_retries):
            try:
                self._request_count += 1

                # Make request
                response = requests.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    headers=request_headers,
                    timeout=self._timeout
                )

                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    raise RateLimitException(
                        f"Rate limit exceeded for {endpoint}",
                        retry_after=retry_after
                    )

                # Handle errors
                if response.status_code >= 400:
                    self._error_count += 1
                    raise APIException(
                        f"API request failed: {response.status_code}",
                        status_code=response.status_code,
                        response_text=response.text,
                        endpoint=endpoint
                    )

                # Parse response
                if response.status_code == 204:  # No content
                    response_data = {}
                else:
                    try:
                        response_data = response.json()
                    except ValueError:
                        response_data = {'raw_text': response.text}

                # Cache successful response
                if use_cache and method == 'GET':
                    cache_key = self._get_cache_key(endpoint, params, data)
                    self._save_to_cache(cache_key, response_data)

                return response_data

            except (requests.Timeout, requests.ConnectionError) as e:
                last_exception = e
                if attempt < self._max_retries - 1:
                    delay = self._retry_delay * (self._retry_backoff ** attempt)
                    if self.reporter:
                        self.reporter.warning(
                            f"Request failed (attempt {attempt + 1}/{self._max_retries}), "
                            f"retrying in {delay}s: {str(e)}"
                        )
                    time.sleep(delay)
                continue

            except RateLimitException as e:
                if attempt < self._max_retries - 1:
                    delay = e.retry_after or 60
                    if self.reporter:
                        self.reporter.warning(
                            f"Rate limited, retrying in {delay}s"
                        )
                    time.sleep(delay)
                    continue
                raise

            except APIException:
                # Don't retry on API errors
                raise

        # All retries exhausted
        raise APIException(
            f"Request failed after {self._max_retries} attempts: {str(last_exception)}",
            endpoint=endpoint
        )

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get API client statistics.

        Returns:
            Dictionary with request statistics
        """
        return {
            'request_count': self._request_count,
            'error_count': self._error_count,
            'cache_hits': self._cache_hits,
            'cache_hit_rate': (
                self._cache_hits / self._request_count
                if self._request_count > 0 else 0
            ),
            'error_rate': (
                self._error_count / self._request_count
                if self._request_count > 0 else 0
            )
        }

    def clear_cache(self):
        """Clear all cached responses."""
        if self._enable_cache and self._cache_dir.exists():
            for cache_file in self._cache_dir.glob('*.json'):
                cache_file.unlink()
            if self.reporter:
                self.reporter.info("API cache cleared")

    @classmethod
    def from_env(cls, reporter=None, config: Dict = None):
        """
        Create instance from environment variables.

        Must be implemented by subclasses to define which env vars to use.

        Args:
            reporter: ProgressReporter
            config: Additional configuration

        Returns:
            Instance of the API client
        """
        raise NotImplementedError(
            f"{cls.__name__} must implement from_env() class method"
        )
