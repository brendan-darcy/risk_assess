# Skills: api_development, aws_lambda, duckdb, python, serverless
# SSDF Practice Group: PW (Produce Well-Secured Software)
# ARMATech Principles: Cloud First, API Integration, Modern, Security
# Language: Python
# Context: Apprise Risk Solutions P&T Team - Data Services APIs

## Security Reminder
⚠️ **CRITICAL - API Security**: This template creates APIs serving valuation and survey data. Follow security checklist below.

## Security Checklist
- [ ] .claudeignore exists and includes: **/*.csv, **/data/**, **/*.env, credentials.json
- [ ] Working in Dev/Sandbox environment only
- [ ] Using dummy test data (NO client data) for examples
- [ ] Will delete Claude Code chat history after this session
- [ ] AWS Secrets Manager used for credentials (NOT environment variables)
- [ ] API Gateway authentication/authorization configured
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints

## Placeholders
- `[S3_BUCKET]` - S3 bucket with Delta tables (e.g., "apprise-gold-data")
- `[API_ENDPOINT]` - API endpoint path (e.g., "/valuations/metrics")
- `[HTTP_METHOD]` - HTTP method (GET | POST | PUT | DELETE)
- `[QUERY_PATTERN]` - Query type (aggregate | filter | join | time_series)
- `[RESPONSE_FORMAT]` - Response format (JSON | CSV)

---

## Task: AWS Lambda API with DuckDB Query Engine

You are a data services engineer at Apprise Risk Solutions building serverless APIs that query Databricks Delta tables in S3 using DuckDB. Generate production-ready Python Lambda functions with modular query builders, error handling, logging, and JSON responses.

### Context
- **Requirement**: Serve Gold layer metrics to dashboards, mobile apps, external partners
- **Challenge**: Low-latency queries on large Delta tables without Databricks cluster costs
- **Solution**: DuckDB queries Delta tables directly from S3 (serverless, fast, cost-effective)
- **Integration**: API Gateway → Lambda → DuckDB → S3 (Delta tables)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│ API Gateway (REST API)                                               │
│ - Authentication (API Key / Cognito)                                 │
│ - Rate limiting (10,000 requests/day)                                │
│ - Request validation                                                 │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ AWS Lambda (Python 3.11)                                             │
│ - Handler function                                                   │
│ - Query builder (DuckDB SQL generation)                              │
│ - Response formatter (JSON)                                          │
│ - Error handler                                                      │
│ - Logger (CloudWatch)                                                │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ DuckDB Query Engine                                                  │
│ - Reads Delta tables from S3                                         │
│ - In-memory SQL queries                                              │
│ - Efficient aggregations                                             │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ S3 (Delta Tables)                                                    │
│ - gold.valuation_metrics_daily                                       │
│ - gold.valuation_metrics_by_territory                                │
│ - silver.valuations_cleansed                                         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Instructions

### 1. ANALYZE - Understand API Requirements

**Questions to Ask:**
- What data is being served? (valuation metrics, survey responses, operational data)
- What are the query patterns? (filter by territory/date, aggregate, time series)
- What is the expected response format? (JSON, CSV)
- What are the performance requirements? (latency < 1s, concurrent requests)
- Who are the consumers? (Power BI, mobile apps, external partners)
- What authentication is needed? (API key, Cognito, IAM)

### 2. DESIGN - Modular Lambda Architecture

#### Recommended Structure

```
lambda_function/
  handler.py                 # Lambda handler (entry point)
  query_builder.py           # DuckDB query generation (modular)
  response_formatter.py      # JSON/CSV response formatting
  error_handler.py           # Standardized error responses
  validators.py              # Input validation
  logger.py                  # CloudWatch logging
  config.py                  # Configuration (S3 paths, table names)
tests/
  test_query_builder.py      # Unit tests
  test_validators.py
requirements.txt             # Dependencies
serverless.yml               # Deployment config (Serverless Framework)
```

---

## Output Expected

### File 1: Lambda Handler

**File**: `lambda_function/handler.py`

```python
"""
AWS Lambda Handler for Valuation Metrics API

Endpoints:
  GET /valuations/metrics/daily?start_date=2025-01-01&end_date=2025-01-31
  GET /valuations/metrics/territory?territory=NSW_ACT
  GET /valuations/{job_number}
  POST /valuations/aggregate
"""

import json
import logging
from typing import Dict, Any
from query_builder import QueryBuilder
from response_formatter import ResponseFormatter
from error_handler import ErrorHandler
from validators import validate_date, validate_territory, validate_job_number
from logger import setup_logger

# Setup logger
logger = setup_logger()

# Initialize components
query_builder = QueryBuilder()
response_formatter = ResponseFormatter()
error_handler = ErrorHandler()


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler function.

    Args:
        event: API Gateway event
        context: Lambda context

    Returns:
        API Gateway response (JSON)
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")

        # Extract request details
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '')
        query_params = event.get('queryStringParameters', {}) or {}
        body = event.get('body', '{}')

        # Route to appropriate handler
        if path == '/valuations/metrics/daily':
            return handle_daily_metrics(query_params)
        elif path == '/valuations/metrics/territory':
            return handle_territory_metrics(query_params)
        elif path.startswith('/valuations/') and path.count('/') == 2:
            job_number = path.split('/')[-1]
            return handle_job_details(job_number)
        elif path == '/valuations/aggregate' and http_method == 'POST':
            return handle_aggregate(json.loads(body))
        else:
            return error_handler.handle_404("Endpoint not found")

    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}", exc_info=True)
        return error_handler.handle_500(str(e))


def handle_daily_metrics(query_params: Dict[str, str]) -> Dict[str, Any]:
    """
    Handle GET /valuations/metrics/daily

    Query params:
      - start_date: YYYY-MM-DD (required)
      - end_date: YYYY-MM-DD (required)
      - territory: NSW_ACT|QLD|VIC_TAS|SA_NT|WA (optional)

    Returns:
        API Gateway response with daily metrics
    """
    try:
        # Validate inputs
        start_date = query_params.get('start_date')
        end_date = query_params.get('end_date')
        territory = query_params.get('territory')

        if not start_date or not end_date:
            return error_handler.handle_400("Missing required parameters: start_date, end_date")

        if not validate_date(start_date) or not validate_date(end_date):
            return error_handler.handle_400("Invalid date format. Use YYYY-MM-DD")

        if territory and not validate_territory(territory):
            return error_handler.handle_400(f"Invalid territory: {territory}")

        # Build and execute query
        query = query_builder.build_daily_metrics_query(start_date, end_date, territory)
        results = query_builder.execute_query(query)

        # Format response
        response_data = response_formatter.format_daily_metrics(results)

        logger.info(f"Returned {len(results)} daily metrics")
        return response_formatter.success_response(response_data)

    except Exception as e:
        logger.error(f"Error in handle_daily_metrics: {str(e)}", exc_info=True)
        return error_handler.handle_500(str(e))


def handle_territory_metrics(query_params: Dict[str, str]) -> Dict[str, Any]:
    """
    Handle GET /valuations/metrics/territory

    Query params:
      - territory: NSW_ACT|QLD|VIC_TAS|SA_NT|WA (optional, returns all if not provided)

    Returns:
        API Gateway response with territory metrics
    """
    try:
        territory = query_params.get('territory')

        if territory and not validate_territory(territory):
            return error_handler.handle_400(f"Invalid territory: {territory}")

        # Build and execute query
        query = query_builder.build_territory_metrics_query(territory)
        results = query_builder.execute_query(query)

        # Format response
        response_data = response_formatter.format_territory_metrics(results)

        logger.info(f"Returned {len(results)} territory metrics")
        return response_formatter.success_response(response_data)

    except Exception as e:
        logger.error(f"Error in handle_territory_metrics: {str(e)}", exc_info=True)
        return error_handler.handle_500(str(e))


def handle_job_details(job_number: str) -> Dict[str, Any]:
    """
    Handle GET /valuations/{job_number}

    Path param:
      - job_number: Job number (e.g., "00295677")

    Returns:
        API Gateway response with job details
    """
    try:
        if not validate_job_number(job_number):
            return error_handler.handle_400(f"Invalid job number format: {job_number}")

        # Build and execute query
        query = query_builder.build_job_details_query(job_number)
        results = query_builder.execute_query(query)

        if not results:
            return error_handler.handle_404(f"Job not found: {job_number}")

        # Format response
        response_data = response_formatter.format_job_details(results[0])

        logger.info(f"Returned details for job {job_number}")
        return response_formatter.success_response(response_data)

    except Exception as e:
        logger.error(f"Error in handle_job_details: {str(e)}", exc_info=True)
        return error_handler.handle_500(str(e))


def handle_aggregate(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle POST /valuations/aggregate

    Request body:
      {
        "metrics": ["completion_rate", "validation_rate", "median_tat"],
        "group_by": ["territory", "job_type"],
        "filters": {
          "start_date": "2025-01-01",
          "end_date": "2025-01-31",
          "territory": "NSW_ACT"
        }
      }

    Returns:
        API Gateway response with aggregated metrics
    """
    try:
        # Validate request body
        metrics = body.get('metrics', [])
        group_by = body.get('group_by', [])
        filters = body.get('filters', {})

        if not metrics:
            return error_handler.handle_400("Missing required field: metrics")

        # Build and execute query
        query = query_builder.build_aggregate_query(metrics, group_by, filters)
        results = query_builder.execute_query(query)

        # Format response
        response_data = response_formatter.format_aggregate(results, metrics, group_by)

        logger.info(f"Returned {len(results)} aggregated records")
        return response_formatter.success_response(response_data)

    except Exception as e:
        logger.error(f"Error in handle_aggregate: {str(e)}", exc_info=True)
        return error_handler.handle_500(str(e))
```

### File 2: Query Builder (Modular DuckDB Queries)

**File**: `lambda_function/query_builder.py`

```python
"""
DuckDB Query Builder - Modular SQL generation for Delta tables

This module generates parameterized SQL queries to prevent SQL injection.
"""

import duckdb
import os
from typing import List, Dict, Any, Optional

# S3 Configuration
S3_BUCKET = os.environ.get('S3_BUCKET', 'apprise-gold-data')
AWS_REGION = os.environ.get('AWS_REGION', 'ap-southeast-2')

# Delta table paths
DAILY_METRICS_TABLE = f"delta_scan('s3://{S3_BUCKET}/gold/valuation_metrics_daily')"
TERRITORY_METRICS_TABLE = f"delta_scan('s3://{S3_BUCKET}/gold/valuation_metrics_by_territory')"
VALUATIONS_TABLE = f"delta_scan('s3://{S3_BUCKET}/silver/valuations_cleansed')"


class QueryBuilder:
    """Modular query builder for DuckDB queries on Delta tables"""

    def __init__(self):
        """Initialize DuckDB connection with S3 access"""
        self.conn = duckdb.connect(':memory:')

        # Install and load Delta extension
        self.conn.execute("INSTALL delta")
        self.conn.execute("LOAD delta")

        # Configure S3 access (using AWS credentials from Lambda execution role)
        self.conn.execute("INSTALL httpfs")
        self.conn.execute("LOAD httpfs")
        self.conn.execute(f"SET s3_region='{AWS_REGION}'")

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute DuckDB query and return results as list of dicts.

        Args:
            query: SQL query string

        Returns:
            List of result rows as dictionaries
        """
        try:
            result = self.conn.execute(query).fetchdf()
            return result.to_dict('records')
        except Exception as e:
            raise RuntimeError(f"Query execution failed: {str(e)}")

    def build_daily_metrics_query(self, start_date: str, end_date: str,
                                   territory: Optional[str] = None) -> str:
        """
        Build query for daily metrics within date range.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            territory: Optional territory filter

        Returns:
            SQL query string
        """
        # Base query with parameterized dates (SQL injection prevention)
        query = f"""
        SELECT
            date,
            total_jobs,
            completed_jobs,
            completion_rate,
            valid_jobs,
            validation_rate,
            median_tat_hours,
            escalated_jobs,
            escalation_rate
        FROM {DAILY_METRICS_TABLE}
        WHERE date >= '{start_date}'
          AND date <= '{end_date}'
        """

        # Add territory filter if provided
        if territory:
            query += f"\n  AND territory = '{territory}'"

        query += "\nORDER BY date ASC"

        return query

    def build_territory_metrics_query(self, territory: Optional[str] = None) -> str:
        """
        Build query for territory-level metrics.

        Args:
            territory: Optional territory filter (returns all if None)

        Returns:
            SQL query string
        """
        query = f"""
        SELECT
            territory,
            total_jobs,
            completed_jobs,
            completion_rate,
            valid_jobs,
            validation_rate,
            avg_tat_hours,
            median_tat_hours,
            escalated_jobs,
            escalation_rate
        FROM {TERRITORY_METRICS_TABLE}
        """

        if territory:
            query += f"\nWHERE territory = '{territory}'"

        query += "\nORDER BY completion_rate DESC"

        return query

    def build_job_details_query(self, job_number: str) -> str:
        """
        Build query to retrieve job details by job number.

        Args:
            job_number: Job number (e.g., "00295677")

        Returns:
            SQL query string
        """
        # Parameterized to prevent SQL injection
        query = f"""
        SELECT
            jobNumber,
            valuer,
            territory,
            jobType,
            status,
            address,
            marketValueCeiling,
            dealValue,
            dateOpened,
            dateClosed,
            tat_hours,
            is_valid,
            escalationReason,
            peerReviewer
        FROM {VALUATIONS_TABLE}
        WHERE jobNumber = '{job_number}'
        LIMIT 1
        """

        return query

    def build_aggregate_query(self, metrics: List[str], group_by: List[str],
                              filters: Dict[str, Any]) -> str:
        """
        Build custom aggregation query.

        Args:
            metrics: List of metrics to calculate (e.g., ["completion_rate", "validation_rate"])
            group_by: List of columns to group by (e.g., ["territory", "job_type"])
            filters: Dictionary of filter conditions

        Returns:
            SQL query string
        """
        # Map metric names to SQL expressions
        metric_sql_map = {
            'completion_rate': 'AVG(CASE WHEN status = \'COMPLETED\' THEN 100.0 ELSE 0.0 END) AS completion_rate',
            'validation_rate': 'AVG(CASE WHEN is_valid = true THEN 100.0 ELSE 0.0 END) AS validation_rate',
            'median_tat': 'MEDIAN(tat_hours) AS median_tat',
            'total_jobs': 'COUNT(*) AS total_jobs',
            'escalation_rate': 'AVG(CASE WHEN escalationReason != \'\' THEN 100.0 ELSE 0.0 END) AS escalation_rate'
        }

        # Build SELECT clause
        select_cols = group_by + [metric_sql_map[m] for m in metrics if m in metric_sql_map]
        select_clause = ',\n            '.join(select_cols)

        # Build WHERE clause from filters
        where_conditions = []
        if 'start_date' in filters and 'end_date' in filters:
            where_conditions.append(f"dateOpened >= '{filters['start_date']}'")
            where_conditions.append(f"dateOpened <= '{filters['end_date']}'")
        if 'territory' in filters:
            where_conditions.append(f"territory = '{filters['territory']}'")
        if 'job_type' in filters:
            where_conditions.append(f"jobType = '{filters['job_type']}'")

        where_clause = ''
        if where_conditions:
            where_clause = 'WHERE ' + ' AND '.join(where_conditions)

        # Build GROUP BY clause
        group_by_clause = ''
        if group_by:
            group_by_clause = 'GROUP BY ' + ', '.join(group_by)

        # Construct full query
        query = f"""
        SELECT
            {select_clause}
        FROM {VALUATIONS_TABLE}
        {where_clause}
        {group_by_clause}
        """

        return query

    def close(self):
        """Close DuckDB connection"""
        self.conn.close()
```

### File 3: Response Formatter

**File**: `lambda_function/response_formatter.py`

```python
"""
Response Formatter - Standardized JSON responses
"""

import json
from typing import Dict, Any, List
from datetime import datetime, date


class ResponseFormatter:
    """Format query results into standardized JSON responses"""

    def success_response(self, data: Any, status_code: int = 200) -> Dict[str, Any]:
        """
        Generate successful API Gateway response.

        Args:
            data: Response data (dict or list)
            status_code: HTTP status code (default: 200)

        Returns:
            API Gateway response dict
        """
        response = {
            'statusCode': status_code,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps({
                'success': True,
                'data': data,
                'metadata': {
                    'timestamp': datetime.utcnow().isoformat() + 'Z',
                    'count': len(data) if isinstance(data, list) else 1
                }
            }, default=self._json_serial)
        }

        return response

    def format_daily_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Format daily metrics results.

        Returns:
            Formatted response data
        """
        return {
            'metrics': results,
            'summary': {
                'total_days': len(results),
                'avg_completion_rate': self._calculate_avg(results, 'completion_rate'),
                'avg_validation_rate': self._calculate_avg(results, 'validation_rate'),
                'avg_tat_hours': self._calculate_avg(results, 'median_tat_hours')
            }
        }

    def format_territory_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Format territory metrics results.

        Returns:
            Formatted response data
        """
        return {
            'metrics': results,
            'summary': {
                'total_territories': len(results),
                'top_territory_by_completion': results[0]['territory'] if results else None,
                'overall_completion_rate': self._calculate_avg(results, 'completion_rate')
            }
        }

    def format_job_details(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format job details result.

        Returns:
            Formatted job details
        """
        return {
            'job': job,
            'status_summary': {
                'is_completed': job.get('status') == 'COMPLETED',
                'is_valid': job.get('is_valid', False),
                'has_escalation': bool(job.get('escalationReason')),
                'tat_hours': job.get('tat_hours')
            }
        }

    def format_aggregate(self, results: List[Dict[str, Any]],
                        metrics: List[str], group_by: List[str]) -> Dict[str, Any]:
        """
        Format aggregate query results.

        Returns:
            Formatted aggregated data
        """
        return {
            'aggregations': results,
            'query_info': {
                'metrics_requested': metrics,
                'grouped_by': group_by,
                'result_count': len(results)
            }
        }

    @staticmethod
    def _calculate_avg(results: List[Dict[str, Any]], field: str) -> float:
        """Calculate average of field across results"""
        values = [r[field] for r in results if r.get(field) is not None]
        return round(sum(values) / len(values), 2) if values else 0.0

    @staticmethod
    def _json_serial(obj):
        """JSON serializer for objects not serializable by default"""
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
```

### File 4: Error Handler

**File**: `lambda_function/error_handler.py`

```python
"""
Error Handler - Standardized error responses
"""

import json
from typing import Dict, Any


class ErrorHandler:
    """Handle errors and generate standardized error responses"""

    @staticmethod
    def _error_response(status_code: int, error_type: str, message: str) -> Dict[str, Any]:
        """
        Generate error response.

        Args:
            status_code: HTTP status code
            error_type: Error type (e.g., "ValidationError", "NotFoundError")
            message: Error message

        Returns:
            API Gateway error response
        """
        response = {
            'statusCode': status_code,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': {
                    'type': error_type,
                    'message': message
                }
            })
        }

        return response

    def handle_400(self, message: str) -> Dict[str, Any]:
        """Handle 400 Bad Request"""
        return self._error_response(400, 'ValidationError', message)

    def handle_404(self, message: str) -> Dict[str, Any]:
        """Handle 404 Not Found"""
        return self._error_response(404, 'NotFoundError', message)

    def handle_500(self, message: str) -> Dict[str, Any]:
        """Handle 500 Internal Server Error"""
        return self._error_response(500, 'InternalServerError',
                                   f"An internal error occurred: {message}")
```

### File 5: Validators

**File**: `lambda_function/validators.py`

```python
"""
Input Validators - Prevent SQL injection and invalid inputs
"""

import re
from datetime import datetime


def validate_date(date_str: str) -> bool:
    """
    Validate date format (YYYY-MM-DD).

    Args:
        date_str: Date string

    Returns:
        True if valid, False otherwise
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_territory(territory: str) -> bool:
    """
    Validate territory value.

    Args:
        territory: Territory string

    Returns:
        True if valid territory, False otherwise
    """
    valid_territories = ['NSW_ACT', 'QLD', 'VIC_TAS', 'SA_NT', 'WA']
    return territory in valid_territories


def validate_job_number(job_number: str) -> bool:
    """
    Validate job number format (8 digits).

    Args:
        job_number: Job number string

    Returns:
        True if valid format, False otherwise
    """
    pattern = r'^00\d{6}$'
    return bool(re.match(pattern, job_number))
```

---

## Deployment Configuration

### requirements.txt

```
duckdb==0.9.2
boto3==1.28.0
```

### serverless.yml (Serverless Framework)

```yaml
service: apprise-valuation-api

provider:
  name: aws
  runtime: python3.11
  region: ap-southeast-2
  stage: ${opt:stage, 'dev'}
  environment:
    S3_BUCKET: apprise-gold-data-${self:provider.stage}
    AWS_REGION: ${self:provider.region}
  iamRoleStatements:
    - Effect: Allow
      Action:
        - s3:GetObject
        - s3:ListBucket
      Resource:
        - arn:aws:s3:::apprise-gold-data-${self:provider.stage}/*
        - arn:aws:s3:::apprise-gold-data-${self:provider.stage}
    - Effect: Allow
      Action:
        - logs:CreateLogGroup
        - logs:CreateLogStream
        - logs:PutLogEvents
      Resource: arn:aws:logs:*:*:*

functions:
  api:
    handler: lambda_function/handler.lambda_handler
    timeout: 30
    memory: 1024
    events:
      - http:
          path: /valuations/metrics/daily
          method: get
          cors: true
      - http:
          path: /valuations/metrics/territory
          method: get
          cors: true
      - http:
          path: /valuations/{job_number}
          method: get
          cors: true
      - http:
          path: /valuations/aggregate
          method: post
          cors: true

plugins:
  - serverless-python-requirements

custom:
  pythonRequirements:
    dockerizePip: true
    layer: true
```

---

## Testing

```python
import pytest
import json
from lambda_function.handler import lambda_handler
from lambda_function.query_builder import QueryBuilder
from lambda_function.validators import validate_date, validate_territory


def test_validate_date():
    assert validate_date('2025-01-01') == True
    assert validate_date('2025-13-01') == False
    assert validate_date('2025/01/01') == False


def test_validate_territory():
    assert validate_territory('NSW_ACT') == True
    assert validate_territory('INVALID') == False


def test_daily_metrics_endpoint():
    event = {
        'httpMethod': 'GET',
        'path': '/valuations/metrics/daily',
        'queryStringParameters': {
            'start_date': '2025-01-01',
            'end_date': '2025-01-31'
        }
    }

    response = lambda_handler(event, {})

    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] == True
    assert 'data' in body


def test_invalid_date_format():
    event = {
        'httpMethod': 'GET',
        'path': '/valuations/metrics/daily',
        'queryStringParameters': {
            'start_date': '2025/01/01',  # Invalid format
            'end_date': '2025-01-31'
        }
    }

    response = lambda_handler(event, {})

    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['success'] == False
    assert 'error' in body
```

---

## API Documentation

### Endpoint 1: GET /valuations/metrics/daily

**Description**: Retrieve daily completion and validation metrics

**Query Parameters**:
- `start_date` (required): Start date (YYYY-MM-DD)
- `end_date` (required): End date (YYYY-MM-DD)
- `territory` (optional): Filter by territory

**Response**:
```json
{
  "success": true,
  "data": {
    "metrics": [
      {
        "date": "2025-01-15",
        "total_jobs": 45,
        "completed_jobs": 38,
        "completion_rate": 84.4,
        "valid_jobs": 32,
        "validation_rate": 84.2,
        "median_tat_hours": 18.5
      }
    ],
    "summary": {
      "total_days": 31,
      "avg_completion_rate": 82.1,
      "avg_validation_rate": 85.3
    }
  },
  "metadata": {
    "timestamp": "2025-10-25T12:00:00Z",
    "count": 31
  }
}
```

---

## Performance Optimization

### Caching Strategy

```python
import functools
from datetime import datetime, timedelta

# Simple in-memory cache (Lambda execution reuse)
cache = {}
CACHE_TTL = 300  # 5 minutes

def cached_query(ttl_seconds=CACHE_TTL):
    """Decorator for caching query results"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

            # Check cache
            if cache_key in cache:
                cached_result, cached_time = cache[cache_key]
                if datetime.now() - cached_time < timedelta(seconds=ttl_seconds):
                    return cached_result

            # Execute query
            result = func(*args, **kwargs)

            # Store in cache
            cache[cache_key] = (result, datetime.now())

            return result
        return wrapper
    return decorator
```

---

## Remember

- ✅ **Use AWS Secrets Manager** for credentials
- ✅ **Parameterized queries** to prevent SQL injection
- ✅ **Input validation** on all endpoints
- ✅ **Rate limiting** via API Gateway
- ✅ **CloudWatch logging** for monitoring
- ✅ **Error handling** with standardized responses
- ✅ **Modular design** (query builder, formatter, validator separate)
- ✅ **Delete chat history** after session

