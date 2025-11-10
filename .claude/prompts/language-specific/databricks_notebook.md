# Skills: databricks, pyspark, sql, python, etl, data_engineering, delta_lake
# SSDF Practice Group: PW (Produce Well-Secured Software)
# ARMATech Principles: Cloud First, Data-Driven, Modern
# Language: Python (PySpark), SQL
# Context: Apprise Risk Solutions P&T Team - Databricks ETL Development

## Security Reminder
⚠️ **CRITICAL**: Databricks notebooks process sensitive valuation data. Use Databricks secrets for credentials, never hardcode secrets, and ensure proper Delta table permissions.

## Security Checklist
- [ ] .claudeignore exists and includes: **/*.csv, **/data/**, **/*.env, credentials.json
- [ ] Working in Dev/Sandbox environment only (NOT Production)
- [ ] Using dummy test data (NO client/production data)
- [ ] Will delete Claude Code chat history after this session
- [ ] Pre-flight check passed (`./pre-flight-check.sh`)

## Placeholders
- `[NOTEBOOK_NAME]` - Notebook name (e.g., "01_bronze_ingestion", "02_silver_cleansing")
- `[SOURCE_PATH]` - Source data location (e.g., "s3://apprise-raw-data/valuation_orders")
- `[TARGET_TABLE]` - Target Delta table name (e.g., "bronze.valuation_orders", "silver.valuation_orders_cleansed")
- `[FUNCTIONALITY]` - Notebook purpose (e.g., "Ingest raw valuation orders from S3 to Bronze Delta table")

---

## Task: Databricks Notebook Development

You are a data engineer at Apprise Risk Solutions developing Databricks notebooks for ETL pipelines on the ARMATech valuation platform. Generate production-ready, optimized, maintainable notebooks following Databricks best practices and Apprise coding standards.

### Context

**Company**: Apprise Risk Solutions
- Databricks lakehouse for data engineering
- Medallion architecture (Bronze → Silver → Gold)
- Delta Lake for ACID transactions
- ISO 27001:2022 compliant, minimum 70% test coverage

**Databricks Platform**:
- **Runtime**: DBR 13.3 LTS (Spark 3.4, Python 3.10)
- **Storage**: Delta tables in S3
- **Compute**: All-purpose clusters (dev) and Job clusters (prod)
- **Secrets**: Databricks Secrets scope

**Notebook Standards at Apprise**:
- **Organization**: Imports → Config → Functions → Execution
- **Naming**: Numbered prefix (01_, 02_, 03_) for pipeline order
- **Secrets**: Use dbutils.secrets.get() for credentials
- **Style**: PEP 8 for Python, modular functions, type hints
- **Testing**: pytest for functions, data quality checks in notebooks

---

## Databricks Development Specification

**Notebook Name**: [NOTEBOOK_NAME]

**Functionality**: [FUNCTIONALITY]

**Source**: [SOURCE_PATH]

**Target**: [TARGET_TABLE]

**Test Coverage Target**: 70% minimum (for extracted functions)

---

## Instructions

### Phase 1: DESIGN (Notebook Architecture)

**1. Medallion Architecture**

**Bronze Layer** (Raw Ingestion):
- Ingest raw data from source (S3, APIs, databases)
- Minimal transformation (cast types, add metadata columns)
- Schema validation
- Store as Delta table

**Silver Layer** (Cleansed & Standardized):
- Deduplicate records
- Standardize formats (dates, status values, territories)
- Data quality checks
- Join with reference data
- Store as Delta table

**Gold Layer** (Business-Level Aggregations):
- Aggregations by territory, valuer, date
- Calculated metrics (completion rates, average days)
- Business rules applied
- Optimized for reporting/dashboards
- Store as Delta table

**2. Notebook Cell Organization**

```
Notebook: [NOTEBOOK_NAME]
├── Cell 1: Notebook Configuration (imports, params, widgets)
├── Cell 2: Helper Functions (reusable logic)
├── Cell 3: Read Source Data
├── Cell 4: Transformations
├── Cell 5: Data Quality Checks
├── Cell 6: Write to Delta Table
└── Cell 7: Validation & Logging
```

**3. Secret Management**

```python
# Databricks Secrets (configured in Workspace)
# Scope: apprise-secrets
# Key: api-key, database-password, etc.

api_key = dbutils.secrets.get(scope="apprise-secrets", key="proptrack-api-key")
db_password = dbutils.secrets.get(scope="apprise-secrets", key="db-password")

# Never print secrets!
# print(api_key)  # ❌ DON'T DO THIS
```

**4. Performance Optimization**

**Partitioning**:
```python
# Partition by date for time-series queries
df.write.format("delta") \
    .mode("append") \
    .partitionBy("date_partition") \
    .save(target_path)
```

**Broadcast Joins** (small tables):
```python
from pyspark.sql.functions import broadcast

# Broadcast small reference table (< 10MB)
result = large_df.join(broadcast(small_df), "key")
```

**Caching** (for repeated access):
```python
# Cache intermediate results
df_cached = df.filter(...).cache()
df_cached.count()  # Trigger caching
```

---

### Phase 2: IMPLEMENT (Notebook Generation)

**1. Notebook Configuration Cell**

```python
# Databricks notebook source
# MAGIC %md
# MAGIC # [NOTEBOOK_NAME]: [FUNCTIONALITY]
# MAGIC
# MAGIC **Purpose**: [Detailed description]
# MAGIC
# MAGIC **Author**: P&T Team
# MAGIC **Date**: 2025-10-25
# MAGIC **Layer**: Bronze | Silver | Gold
# MAGIC **Schedule**: Daily | Hourly | On-demand
# MAGIC
# MAGIC **Inputs**:
# MAGIC - Source: [SOURCE_PATH]
# MAGIC - Format: JSON | CSV | Parquet | Delta
# MAGIC
# MAGIC **Outputs**:
# MAGIC - Target: [TARGET_TABLE]
# MAGIC - Format: Delta
# MAGIC - Partition: date_partition (YYYY-MM-DD)
# MAGIC
# MAGIC **Dependencies**:
# MAGIC - Upstream: [Previous notebooks]
# MAGIC - Downstream: [Next notebooks]

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 1: Configuration & Imports

# COMMAND ----------

# Imports
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.sql.window import Window
from delta.tables import DeltaTable
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import re

# Initialize Spark session
spark = SparkSession.builder.getOrCreate()

# COMMAND ----------

# Notebook parameters (can be passed from workflow)
dbutils.widgets.text("source_path", "[SOURCE_PATH]", "Source Path")
dbutils.widgets.text("target_table", "[TARGET_TABLE]", "Target Table")
dbutils.widgets.text("date_partition", datetime.now().strftime("%Y-%m-%d"), "Date Partition (YYYY-MM-DD)")

source_path = dbutils.widgets.get("source_path")
target_table = dbutils.widgets.get("target_table")
date_partition = dbutils.widgets.get("date_partition")

print(f"Source Path: {source_path}")
print(f"Target Table: {target_table}")
print(f"Date Partition: {date_partition}")

# COMMAND ----------

# Secrets (never print!)
api_key = dbutils.secrets.get(scope="apprise-secrets", key="api-key")  # Example

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 2: Helper Functions

# COMMAND ----------

def add_metadata_columns(df: DataFrame, source: str) -> DataFrame:
    """
    Add standard metadata columns to DataFrame.

    Args:
        df: Input DataFrame
        source: Source system name

    Returns:
        DataFrame with metadata columns added
    """
    return df.withColumn("_source", F.lit(source)) \
             .withColumn("_ingestion_timestamp", F.current_timestamp()) \
             .withColumn("_date_partition", F.lit(date_partition))

# COMMAND ----------

def deduplicate_records(df: DataFrame, key_cols: List[str], order_col: str = "_ingestion_timestamp") -> DataFrame:
    """
    Deduplicate records, keeping the latest based on order_col.

    Args:
        df: Input DataFrame
        key_cols: Columns that define uniqueness
        order_col: Column to order by (default: _ingestion_timestamp)

    Returns:
        Deduplicated DataFrame
    """
    window_spec = Window.partitionBy(*key_cols).orderBy(F.col(order_col).desc())

    return df.withColumn("_row_num", F.row_number().over(window_spec)) \
             .filter(F.col("_row_num") == 1) \
             .drop("_row_num")

# COMMAND ----------

def standardize_territory(df: DataFrame, territory_col: str = "territory") -> DataFrame:
    """
    Standardize territory values to consistent format.

    Args:
        df: Input DataFrame
        territory_col: Territory column name

    Returns:
        DataFrame with standardized territory values
    """
    return df.withColumn(
        territory_col,
        F.when(F.col(territory_col).isin("NSW", "ACT", "New South Wales", "Australian Capital Territory"), "NSW_ACT")
        .when(F.col(territory_col).isin("QLD", "Queensland"), "QLD")
        .when(F.col(territory_col).isin("VIC", "TAS", "Victoria", "Tasmania"), "VIC_TAS")
        .when(F.col(territory_col).isin("SA", "NT", "South Australia", "Northern Territory"), "SA_NT")
        .when(F.col(territory_col).isin("WA", "Western Australia"), "WA")
        .otherwise(F.upper(F.trim(F.col(territory_col))))
    )

# COMMAND ----------

def validate_schema(df: DataFrame, expected_schema: T.StructType) -> None:
    """
    Validate that DataFrame schema matches expected schema.

    Args:
        df: Input DataFrame
        expected_schema: Expected StructType schema

    Raises:
        ValueError: If schema doesn't match
    """
    actual_fields = {field.name: field.dataType for field in df.schema.fields}
    expected_fields = {field.name: field.dataType for field in expected_schema.fields}

    missing_fields = set(expected_fields.keys()) - set(actual_fields.keys())
    if missing_fields:
        raise ValueError(f"Missing required fields: {missing_fields}")

    for field_name in expected_fields:
        if field_name in actual_fields:
            if actual_fields[field_name] != expected_fields[field_name]:
                print(f"WARNING: Field '{field_name}' type mismatch: {actual_fields[field_name]} != {expected_fields[field_name]}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 3: Read Source Data

# COMMAND ----------

# Read source data
print(f"Reading from: {source_path}")

# Auto-detect schema for JSON/CSV (Bronze layer)
df_source = spark.read.format("json") \
    .option("inferSchema", "true") \
    .option("multiLine", "true") \
    .load(source_path)

print(f"Records read: {df_source.count()}")
print("Schema:")
df_source.printSchema()

# Display sample
display(df_source.limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 4: Transformations

# COMMAND ----------

# Add metadata columns
df_transformed = add_metadata_columns(df_source, source="S3_Raw_Data")

# Standardize territory
df_transformed = standardize_territory(df_transformed, territory_col="territory")

# Deduplicate (if applicable)
df_transformed = deduplicate_records(df_transformed, key_cols=["job_number"])

# Type casting (if needed)
df_transformed = df_transformed.withColumn("job_number", F.col("job_number").cast(T.StringType())) \
                               .withColumn("date_lodged", F.to_date(F.col("date_lodged"), "yyyy-MM-dd"))

print(f"Records after transformation: {df_transformed.count()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 5: Data Quality Checks

# COMMAND ----------

# Check 1: Null values in critical columns
critical_cols = ["job_number", "territory", "date_lodged"]

for col in critical_cols:
    null_count = df_transformed.filter(F.col(col).isNull()).count()
    if null_count > 0:
        print(f"WARNING: {null_count} null values in '{col}'")
    else:
        print(f"✓ No null values in '{col}'")

# COMMAND ----------

# Check 2: Duplicate job numbers
duplicate_count = df_transformed.groupBy("job_number").count().filter(F.col("count") > 1).count()
if duplicate_count > 0:
    print(f"WARNING: {duplicate_count} duplicate job numbers found")
else:
    print("✓ No duplicate job numbers")

# COMMAND ----------

# Check 3: Valid territory values
valid_territories = ["NSW_ACT", "QLD", "VIC_TAS", "SA_NT", "WA"]
invalid_territories = df_transformed.filter(~F.col("territory").isin(valid_territories))

if invalid_territories.count() > 0:
    print(f"WARNING: {invalid_territories.count()} invalid territories")
    display(invalid_territories.select("territory").distinct())
else:
    print("✓ All territories valid")

# COMMAND ----------

# Check 4: Date range validation
date_stats = df_transformed.select(
    F.min("date_lodged").alias("min_date"),
    F.max("date_lodged").alias("max_date")
).collect()[0]

print(f"Date range: {date_stats.min_date} to {date_stats.max_date}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 6: Write to Delta Table

# COMMAND ----------

# Write to Delta table
print(f"Writing to: {target_table}")

# Mode options: overwrite | append | merge
write_mode = "append"

df_transformed.write.format("delta") \
    .mode(write_mode) \
    .option("mergeSchema", "true") \
    .partitionBy("_date_partition") \
    .saveAsTable(target_table)

print(f"✓ Successfully wrote to {target_table}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 7: Validation & Logging

# COMMAND ----------

# Validate write
df_validation = spark.table(target_table).filter(F.col("_date_partition") == date_partition)

validation_count = df_validation.count()
expected_count = df_transformed.count()

print(f"Validation count: {validation_count}")
print(f"Expected count: {expected_count}")

if validation_count == expected_count:
    print("✓ Validation passed")
else:
    print(f"⚠ WARNING: Count mismatch ({validation_count} != {expected_count})")

# COMMAND ----------

# Log to audit table (optional)
audit_data = [(
    datetime.now(),
    "[NOTEBOOK_NAME]",
    source_path,
    target_table,
    expected_count,
    validation_count,
    "SUCCESS" if validation_count == expected_count else "WARNING"
)]

audit_schema = T.StructType([
    T.StructField("timestamp", T.TimestampType(), False),
    T.StructField("notebook_name", T.StringType(), False),
    T.StructField("source_path", T.StringType(), False),
    T.StructField("target_table", T.StringType(), False),
    T.StructField("records_processed", T.IntegerType(), False),
    T.StructField("records_written", T.IntegerType(), False),
    T.StructField("status", T.StringType(), False)
])

audit_df = spark.createDataFrame(audit_data, schema=audit_schema)
audit_df.write.format("delta").mode("append").saveAsTable("audit.notebook_runs")

print("✓ Audit log written")

# COMMAND ----------

# Display summary stats
print("\n=== Summary ===")
print(f"Source: {source_path}")
print(f"Target: {target_table}")
print(f"Date Partition: {date_partition}")
print(f"Records Processed: {expected_count}")
print(f"Status: SUCCESS")
```

**2. SQL Notebook (Alternative)** - For simple queries

```sql
-- Databricks notebook source
-- MAGIC %md
-- MAGIC # [NOTEBOOK_NAME]: [FUNCTIONALITY]

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Configuration

-- COMMAND ----------

-- Set variables
SET target_table = [TARGET_TABLE];
SET date_partition = current_date();

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Query & Insert

-- COMMAND ----------

INSERT INTO ${target_table}
SELECT
    job_number,
    territory,
    date_lodged,
    status,
    CASE
        WHEN territory IN ('NSW', 'ACT') THEN 'NSW_ACT'
        WHEN territory = 'QLD' THEN 'QLD'
        WHEN territory IN ('VIC', 'TAS') THEN 'VIC_TAS'
        WHEN territory IN ('SA', 'NT') THEN 'SA_NT'
        WHEN territory = 'WA' THEN 'WA'
        ELSE territory
    END AS territory_standardized,
    current_timestamp() AS _ingestion_timestamp,
    ${date_partition} AS _date_partition
FROM delta.`s3://apprise-raw-data/valuation_orders`
WHERE _date_partition = ${date_partition};

-- COMMAND ----------

-- Validation
SELECT
    COUNT(*) as total_records,
    COUNT(DISTINCT job_number) as unique_jobs,
    MIN(date_lodged) as min_date,
    MAX(date_lodged) as max_date
FROM ${target_table}
WHERE _date_partition = ${date_partition};
```

---

### Phase 3: TEST (70% Coverage Target)

**Extract Functions to Python Module** (`src/transformations.py`)

```python
"""
Data transformation functions for Databricks notebooks.
Extracted for unit testing.
"""
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from typing import List

def deduplicate_records(df: DataFrame, key_cols: List[str], order_col: str = "_ingestion_timestamp") -> DataFrame:
    """Deduplicate records."""
    # Implementation from notebook
    pass

def standardize_territory(df: DataFrame, territory_col: str = "territory") -> DataFrame:
    """Standardize territory values."""
    # Implementation from notebook
    pass

# ... other functions
```

**Unit Tests** (`tests/test_transformations.py`)

```python
import pytest
from pyspark.sql import SparkSession
from src.transformations import deduplicate_records, standardize_territory

@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder.master("local[1]").appName("unit-tests").getOrCreate()

def test_deduplicate_records(spark):
    # Arrange
    data = [
        ("001", "value1", "2025-10-01"),
        ("001", "value2", "2025-10-02"),  # Duplicate, newer
        ("002", "value3", "2025-10-01")
    ]
    df = spark.createDataFrame(data, ["id", "value", "date"])

    # Act
    result = deduplicate_records(df, key_cols=["id"], order_col="date")

    # Assert
    assert result.count() == 2
    assert result.filter(result.id == "001").collect()[0].value == "value2"

def test_standardize_territory(spark):
    # Arrange
    data = [
        ("NSW",),
        ("QLD",),
        ("Victoria",),
        ("WA",)
    ]
    df = spark.createDataFrame(data, ["territory"])

    # Act
    result = standardize_territory(df)

    # Assert
    territories = [row.territory for row in result.collect()]
    assert "NSW_ACT" in territories
    assert "QLD" in territories
    assert "VIC_TAS" in territories
    assert "WA" in territories
```

**Run Tests**:
```bash
pytest tests/ --cov=src --cov-report=html
```

---

## Output Expected

1. **Notebook**: `[NOTEBOOK_NAME].py` (exported from Databricks)
2. **Functions Module**: `src/transformations.py` (extracted functions)
3. **Tests**: `tests/test_transformations.py` (unit tests, 70%+ coverage)
4. **Documentation**: README with notebook description, dependencies, schedule

---

## Related Templates

- Use `../workflows/data_engineer_etl.md` for comprehensive ETL pipeline patterns
- Use `../core-workflows/secure_feature_development.md` for overall feature development
- Use `../core-workflows/code_review_request.md` for code review

---

**Template Version**: 1.0
**Last Updated**: October 2025
**Owner**: P&T Team / AI Approach Project
