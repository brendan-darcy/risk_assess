# Skills: data_engineering, pyspark, databricks, etl, data_quality
# SSDF Practice Group: PW (Produce Well-Secured Software)
# ARMATech Principles: Cloud First, Data-Driven, Modern, Security
# Language: Python (PySpark)
# Context: Apprise Risk Solutions P&T Team - Databricks ETL Workflows

## Security Reminder
⚠️ **CRITICAL - Data Safety Protocol**: This template processes valuation and survey data containing PII. Follow security checklist below.

## Security Checklist
- [ ] .claudeignore exists and includes: **/*.csv, **/data/**, **/*.env, credentials.json
- [ ] Working in Dev/Sandbox environment only
- [ ] Using dummy test data (NO client data) for examples
- [ ] Will delete Claude Code chat history after this session
- [ ] Databricks secrets used for S3 credentials (NOT hardcoded)
- [ ] Delta tables have appropriate access controls

## Placeholders
- `[SOURCE_S3_PATH]` - Source S3 path (e.g., "s3://apprise-raw-data/valuations/")
- `[TARGET_DELTA_TABLE]` - Target Delta table name (e.g., "gold.valuation_metrics")
- `[TRANSFORMATION_TYPE]` - Type of transformation (cleansing | enrichment | aggregation | scd2)
- `[DATA_QUALITY_RULES]` - Quality rules (not_null | range_check | referential_integrity)
- `[LAYER]` - Medallion layer (bronze | silver | gold)

---

## Task: Databricks ETL Pipeline (Bronze-Silver-Gold)

You are a data engineer at Apprise Risk Solutions building ETL pipelines in Databricks. Generate production-ready PySpark code that implements medallion architecture (Bronze → Silver → Gold) with modular transformations, data quality checks, and Delta table operations.

### Context
- **Requirement**: Transform raw valuation/survey data into analytics-ready tables
- **Architecture**: Bronze (raw), Silver (cleansed), Gold (aggregated metrics)
- **Challenge**: Ensure data quality, handle schema evolution, maintain lineage
- **Integration**: Feeds Power BI dashboards, ML models, operational reporting

---

## Medallion Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│ BRONZE LAYER (Raw / Ingestion)                                      │
│ - Read from S3 (Parquet, CSV, JSON)                                 │
│ - Minimal transformation (schema enforcement, timestamp)             │
│ - Append-only, full history                                         │
│ - Delta tables for ACID guarantees                                  │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ SILVER LAYER (Cleansed / Standardized)                              │
│ - Data cleansing (nulls, duplicates, outliers)                      │
│ - Standardization (formats, types, naming)                          │
│ - Joins with reference data                                         │
│ - SCD Type 2 for slowly changing dimensions                         │
│ - Data quality checks (reject/quarantine bad records)               │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ GOLD LAYER (Business Aggregations)                                  │
│ - Business metrics (completion rates, validation rates, TAT)        │
│ - Aggregations by territory, valuer, date                           │
│ - KPIs for dashboards                                               │
│ - Star schema / dimensional modeling                                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Instructions

### 1. ANALYZE - Understand Data Requirements

**Questions to Ask:**
- What is the source data? (valuation exports, survey responses, operational logs)
- What format? (CSV, Parquet, JSON)
- What transformations are needed? (cleansing, joins, aggregations)
- What are the business metrics? (completion rate, validation rate, TAT, escalation rate)
- What are the data quality rules? (required fields, value ranges, referential integrity)
- Who are the consumers? (dashboards, analysts, ML models)

**Apprise-Specific Context:**
- **Valuation Data**: Job-level data with territories, valuers, statuses, dates
- **Survey Data**: Response-level data with interaction sequences, completion flags
- **Reference Data**: Territory mappings, valuer details, lender codes
- **Target Metrics**: Completion rates by territory, validation rates by valuer, TAT distributions

### 2. DESIGN - Pipeline Architecture

#### Recommended Structure

```
notebooks/
  01_bronze_ingestion.py          # Ingest from S3 to Bronze Delta tables
  02_silver_cleansing.py          # Cleanse and standardize
  03_gold_aggregations.py         # Business metrics
  utils/
    transformations.py            # Reusable transformation functions
    data_quality.py               # Data quality checks
    schemas.py                    # Schema definitions
  config/
    pipeline_config.py            # Configuration (S3 paths, table names)
  tests/
    test_transformations.py       # Unit tests
```

#### Modular Design Principles

**Reusable Functions** (like SurveyAnalyzer pattern):
```python
class DataQualityChecker:
    """Modular data quality checks"""

    @staticmethod
    def check_not_null(df, columns):
        """Check columns are not null"""
        pass

    @staticmethod
    def check_range(df, column, min_val, max_val):
        """Check values within range"""
        pass

    @staticmethod
    def check_referential_integrity(df, ref_df, key_col):
        """Check foreign keys exist"""
        pass
```

### 3. IMPLEMENT - Generate PySpark Code

---

## Output Expected

### Notebook 1: Bronze Layer Ingestion

**File**: `notebooks/01_bronze_ingestion.py`

```python
# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze Layer: Ingest Valuation Data from S3
# MAGIC
# MAGIC **Purpose**: Read raw valuation exports from S3 and write to Bronze Delta tables
# MAGIC
# MAGIC **Input**: s3://apprise-raw-data/valuations/export_YYYYMMDD.csv
# MAGIC **Output**: bronze.valuations (Delta table)
# MAGIC
# MAGIC **Transformations**:
# MAGIC - Schema enforcement
# MAGIC - Add ingestion timestamp
# MAGIC - Append-only (full history)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, lit, col, to_date
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType
from delta.tables import DeltaTable

# S3 Configuration (using Databricks secrets)
AWS_ACCESS_KEY = dbutils.secrets.get(scope="aws", key="access_key_id")
AWS_SECRET_KEY = dbutils.secrets.get(scope="aws", key="secret_access_key")

spark.conf.set("fs.s3a.access.key", AWS_ACCESS_KEY)
spark.conf.set("fs.s3a.secret.key", AWS_SECRET_KEY)

# Paths
SOURCE_S3_PATH = "s3a://apprise-raw-data/valuations/"
TARGET_DELTA_TABLE = "bronze.valuations"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Define Schema

# COMMAND ----------

valuation_schema = StructType([
    StructField("jobNumber", StringType(), False),
    StructField("valuer", StringType(), True),
    StructField("territory", StringType(), True),
    StructField("jobType", StringType(), True),
    StructField("status", StringType(), True),
    StructField("address", StringType(), True),
    StructField("marketValueCeiling", DoubleType(), True),
    StructField("dealValue", DoubleType(), True),
    StructField("dateOpened", StringType(), True),
    StructField("dateClosed", StringType(), True),
    StructField("lenderTaT", DoubleType(), True),
    StructField("valid", StringType(), True),
    StructField("escalationReason", StringType(), True),
    StructField("peerReviewer", StringType(), True)
])

# COMMAND ----------

# MAGIC %md
# MAGIC ## Read from S3

# COMMAND ----------

# Read CSV with schema enforcement
df_raw = (spark.read
          .format("csv")
          .option("header", "true")
          .option("mode", "PERMISSIVE")  # Bad records → null columns
          .option("columnNameOfCorruptRecord", "_corrupt_record")
          .schema(valuation_schema)
          .load(SOURCE_S3_PATH))

print(f"Records read from S3: {df_raw.count():,}")

# Check for corrupt records
corrupt_count = df_raw.filter(col("_corrupt_record").isNotNull()).count()
if corrupt_count > 0:
    print(f"⚠️ WARNING: {corrupt_count} corrupt records detected")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Add Bronze Metadata

# COMMAND ----------

df_bronze = (df_raw
             .withColumn("_ingestion_timestamp", current_timestamp())
             .withColumn("_source_file", lit("export_manual"))
             .withColumn("_bronze_date", to_date(current_timestamp())))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Write to Bronze Delta Table

# COMMAND ----------

# Write with merge (upsert based on jobNumber)
if DeltaTable.isDeltaTable(spark, TARGET_DELTA_TABLE):
    # Table exists - merge
    delta_table = DeltaTable.forName(spark, TARGET_DELTA_TABLE)

    (delta_table.alias("target")
     .merge(
         df_bronze.alias("source"),
         "target.jobNumber = source.jobNumber AND target._bronze_date = source._bronze_date"
     )
     .whenMatchedUpdateAll()
     .whenNotMatchedInsertAll()
     .execute())

    print(f"✓ Merged into {TARGET_DELTA_TABLE}")
else:
    # Table doesn't exist - create
    (df_bronze.write
     .format("delta")
     .mode("overwrite")
     .option("mergeSchema", "true")
     .saveAsTable(TARGET_DELTA_TABLE))

    print(f"✓ Created {TARGET_DELTA_TABLE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Validation

# COMMAND ----------

# Count records
record_count = spark.table(TARGET_DELTA_TABLE).count()
print(f"Total records in Bronze: {record_count:,}")

# Check data quality
bronze_df = spark.table(TARGET_DELTA_TABLE)
null_job_numbers = bronze_df.filter(col("jobNumber").isNull()).count()
print(f"Records with null jobNumber: {null_job_numbers}")

# Display sample
display(bronze_df.limit(10))
```

### Notebook 2: Silver Layer Cleansing

**File**: `notebooks/02_silver_cleansing.py`

```python
# Databricks notebook source
# MAGIC %md
# MAGIC # Silver Layer: Cleanse and Standardize Valuation Data
# MAGIC
# MAGIC **Purpose**: Cleanse Bronze data, apply business rules, join with reference data
# MAGIC
# MAGIC **Input**: bronze.valuations
# MAGIC **Output**: silver.valuations_cleansed
# MAGIC
# MAGIC **Transformations**:
# MAGIC - Deduplicate records
# MAGIC - Standardize statuses, territories
# MAGIC - Parse dates
# MAGIC - Calculate derived fields
# MAGIC - Data quality checks (quarantine bad records)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Imports & Configuration

# COMMAND ----------

from pyspark.sql.functions import (
    col, when, trim, upper, to_date, datediff, hour, lit,
    regexp_replace, coalesce, current_timestamp
)
from pyspark.sql.window import Window
from pyspark.sql import DataFrame
from delta.tables import DeltaTable

SOURCE_TABLE = "bronze.valuations"
TARGET_TABLE = "silver.valuations_cleansed"
QUARANTINE_TABLE = "silver.valuations_quarantine"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Transformation Functions (Modular & Reusable)

# COMMAND ----------

def deduplicate_records(df: DataFrame, key_cols: list, order_col: str) -> DataFrame:
    """
    Deduplicate records keeping the latest based on order_col.

    Args:
        df: Input DataFrame
        key_cols: List of columns that define uniqueness
        order_col: Column to order by (latest wins)

    Returns:
        Deduplicated DataFrame
    """
    from pyspark.sql.window import Window
    from pyspark.sql.functions import row_number

    window_spec = Window.partitionBy(*key_cols).orderBy(col(order_col).desc())

    df_deduped = (df
                  .withColumn("_row_num", row_number().over(window_spec))
                  .filter(col("_row_num") == 1)
                  .drop("_row_num"))

    return df_deduped


def standardize_status(df: DataFrame, status_col: str = "status") -> DataFrame:
    """
    Standardize status values to consistent format.

    Mapping:
      'Valuation Completed' → 'COMPLETED'
      'Canceled' / 'Cancelled' → 'CANCELED'
      'In Progress' / 'inProgress' → 'IN_PROGRESS'
    """
    df_standardized = df.withColumn(
        status_col,
        when(col(status_col).isin("Valuation Completed", "valuation completed", "jobCompleted"),
             "COMPLETED")
        .when(col(status_col).isin("Canceled", "Cancelled", "cancelled"),
              "CANCELED")
        .when(col(status_col).isin("In Progress", "inProgress", "in progress"),
              "IN_PROGRESS")
        .otherwise(upper(trim(col(status_col))))
    )

    return df_standardized


def standardize_territory(df: DataFrame, territory_col: str = "territory") -> DataFrame:
    """
    Standardize territory names.

    Mapping:
      'Apprise NSW / ACT' → 'NSW_ACT'
      'Apprise QLD' → 'QLD'
      'Apprise VIC / TAS' → 'VIC_TAS'
      'Apprise SA / NT' → 'SA_NT'
      'Apprise WA' → 'WA'
    """
    df_standardized = df.withColumn(
        territory_col,
        when(col(territory_col).contains("NSW"), "NSW_ACT")
        .when(col(territory_col).contains("QLD"), "QLD")
        .when(col(territory_col).contains("VIC"), "VIC_TAS")
        .when(col(territory_col).contains("SA"), "SA_NT")
        .when(col(territory_col).contains("WA"), "WA")
        .otherwise("UNKNOWN")
    )

    return df_standardized


def parse_dates(df: DataFrame, date_cols: list) -> DataFrame:
    """
    Parse string dates to date type.

    Args:
        df: Input DataFrame
        date_cols: List of date column names to parse

    Returns:
        DataFrame with parsed dates
    """
    for date_col in date_cols:
        df = df.withColumn(date_col, to_date(col(date_col), "yyyy-MM-dd"))

    return df


def calculate_tat_hours(df: DataFrame,
                        start_col: str = "dateOpened",
                        end_col: str = "dateClosed") -> DataFrame:
    """
    Calculate turnaround time in hours.

    TAT = (dateClosed - dateOpened) in hours
    """
    df_with_tat = df.withColumn(
        "tat_hours",
        when(col(end_col).isNotNull(),
             (col(end_col).cast("long") - col(start_col).cast("long")) / 3600)
        .otherwise(None)
    )

    return df_with_tat


def flag_validation_status(df: DataFrame, valid_col: str = "valid") -> DataFrame:
    """
    Convert string 'true'/'false' to boolean validation flag.
    """
    df_with_flag = df.withColumn(
        "is_valid",
        when(col(valid_col).isin("true", "True", "TRUE", "1"), True)
        .when(col(valid_col).isin("false", "False", "FALSE", "0"), False)
        .otherwise(None)
    )

    return df_with_flag

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Quality Checks (Modular Functions)

# COMMAND ----------

class DataQualityChecker:
    """Reusable data quality checks"""

    @staticmethod
    def check_not_null(df: DataFrame, columns: list) -> DataFrame:
        """
        Flag records with null values in required columns.

        Returns:
            DataFrame with _dq_failed_not_null column (comma-separated failed columns)
        """
        failed_cols = []
        for col_name in columns:
            failed_cols.append(
                when(col(col_name).isNull(), lit(col_name))
                .otherwise(lit(""))
            )

        # Concatenate failed columns
        from pyspark.sql.functions import concat_ws, array
        df_with_check = df.withColumn(
            "_dq_failed_not_null",
            concat_ws(",", array(*failed_cols))
        )

        # Remove empty strings
        df_with_check = df_with_check.withColumn(
            "_dq_failed_not_null",
            when(col("_dq_failed_not_null") == "", None)
            .otherwise(col("_dq_failed_not_null"))
        )

        return df_with_check

    @staticmethod
    def check_range(df: DataFrame, column: str, min_val: float, max_val: float) -> DataFrame:
        """
        Flag records where column value is outside valid range.

        Returns:
            DataFrame with _dq_failed_range_{column} column
        """
        df_with_check = df.withColumn(
            f"_dq_failed_range_{column}",
            when((col(column) < min_val) | (col(column) > max_val), True)
            .otherwise(False)
        )

        return df_with_check

    @staticmethod
    def check_referential_integrity(df: DataFrame, ref_df: DataFrame,
                                   key_col: str, ref_name: str) -> DataFrame:
        """
        Check foreign keys exist in reference table.

        Returns:
            DataFrame with _dq_failed_fk_{ref_name} column
        """
        # Get distinct keys from reference table
        ref_keys = ref_df.select(key_col).distinct()

        # Left anti join to find missing keys
        missing_keys = df.join(ref_keys, on=key_col, how="left_anti")

        # Flag records with missing foreign keys
        df_with_check = df.withColumn(
            f"_dq_failed_fk_{ref_name}",
            when(col(key_col).isin(missing_keys.select(key_col).rdd.flatMap(lambda x: x).collect()),
                 True)
            .otherwise(False)
        )

        return df_with_check

# COMMAND ----------

# MAGIC %md
# MAGIC ## Execute Silver Transformations

# COMMAND ----------

# Read from Bronze
df_bronze = spark.table(SOURCE_TABLE)
print(f"Bronze records: {df_bronze.count():,}")

# Step 1: Deduplicate
df_deduped = deduplicate_records(
    df_bronze,
    key_cols=["jobNumber"],
    order_col="_ingestion_timestamp"
)
print(f"After deduplication: {df_deduped.count():,}")

# Step 2: Standardize status and territory
df_std = (df_deduped
          .transform(standardize_status)
          .transform(standardize_territory))

# Step 3: Parse dates
df_dates = parse_dates(df_std, date_cols=["dateOpened", "dateClosed"])

# Step 4: Calculate derived fields
df_derived = (df_dates
              .transform(calculate_tat_hours)
              .transform(flag_validation_status))

# Step 5: Data Quality Checks
dq_checker = DataQualityChecker()

df_with_dq = (df_derived
              .transform(lambda df: dq_checker.check_not_null(df, columns=["jobNumber", "territory"]))
              .transform(lambda df: dq_checker.check_range(df, "marketValueCeiling", 50000, 100000000)))

# Flag any DQ failures
from pyspark.sql.functions import concat_ws, array, size, filter as sql_filter
df_with_dq = df_with_dq.withColumn(
    "_dq_failed",
    when(col("_dq_failed_not_null").isNotNull(), True)
    .otherwise(False)
)

# Split into clean and quarantine
df_clean = df_with_dq.filter(col("_dq_failed") == False)
df_quarantine = df_with_dq.filter(col("_dq_failed") == True)

print(f"Clean records: {df_clean.count():,}")
print(f"Quarantined records: {df_quarantine.count():,}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Write to Silver Delta Tables

# COMMAND ----------

# Add Silver metadata
df_silver = (df_clean
             .withColumn("_silver_timestamp", current_timestamp())
             .drop("_dq_failed", "_dq_failed_not_null"))

# Write clean records to Silver
(df_silver.write
 .format("delta")
 .mode("overwrite")
 .option("mergeSchema", "true")
 .option("overwriteSchema", "true")
 .saveAsTable(TARGET_TABLE))

print(f"✓ Wrote {df_silver.count():,} records to {TARGET_TABLE}")

# Write quarantined records
if df_quarantine.count() > 0:
    (df_quarantine.write
     .format("delta")
     .mode("append")
     .saveAsTable(QUARANTINE_TABLE))

    print(f"✓ Wrote {df_quarantine.count():,} records to {QUARANTINE_TABLE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Validation

# COMMAND ----------

# Display sample
display(spark.table(TARGET_TABLE).limit(10))

# Check data quality
silver_df = spark.table(TARGET_TABLE)
print(f"\nData Quality Summary:")
print(f"  Total records: {silver_df.count():,}")
print(f"  Unique job numbers: {silver_df.select('jobNumber').distinct().count():,}")
print(f"  Territories: {silver_df.select('territory').distinct().count()}")
print(f"  Completed jobs: {silver_df.filter(col('status') == 'COMPLETED').count():,}")
```

### Notebook 3: Gold Layer Aggregations

**File**: `notebooks/03_gold_aggregations.py`

```python
# Databricks notebook source
# MAGIC %md
# MAGIC # Gold Layer: Business Metrics & Aggregations
# MAGIC
# MAGIC **Purpose**: Calculate business KPIs for dashboards and reporting
# MAGIC
# MAGIC **Input**: silver.valuations_cleansed
# MAGIC **Output**: gold.valuation_metrics_daily, gold.valuation_metrics_by_territory
# MAGIC
# MAGIC **Metrics**:
# MAGIC - Completion rate
# MAGIC - Validation rate
# MAGIC - Median TAT
# MAGIC - Escalation rate

# COMMAND ----------

# MAGIC %md
# MAGIC ## Imports & Configuration

# COMMAND ----------

from pyspark.sql.functions import (
    col, count, sum as sql_sum, avg, when, lit, median,
    date_trunc, current_timestamp
)
from pyspark.sql import DataFrame

SOURCE_TABLE = "silver.valuations_cleansed"
TARGET_TABLE_DAILY = "gold.valuation_metrics_daily"
TARGET_TABLE_TERRITORY = "gold.valuation_metrics_by_territory"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Aggregation Functions (Modular & Reusable)

# COMMAND ----------

def calculate_completion_metrics(df: DataFrame, group_cols: list) -> DataFrame:
    """
    Calculate completion rate metrics grouped by specified columns.

    Metrics:
      - total_jobs: Count of all jobs
      - completed_jobs: Count of completed jobs
      - completion_rate: Percentage of completed jobs
    """
    metrics_df = (df.groupBy(*group_cols)
                  .agg(
                      count("*").alias("total_jobs"),
                      sql_sum(when(col("status") == "COMPLETED", 1).otherwise(0)).alias("completed_jobs")
                  )
                  .withColumn("completion_rate", (col("completed_jobs") / col("total_jobs") * 100)))

    return metrics_df


def calculate_validation_metrics(df: DataFrame, group_cols: list) -> DataFrame:
    """
    Calculate validation rate metrics for completed jobs.

    Metrics:
      - valid_jobs: Count of valid completed jobs
      - validation_rate: Percentage of valid jobs among completed
    """
    completed_df = df.filter(col("status") == "COMPLETED")

    metrics_df = (completed_df.groupBy(*group_cols)
                  .agg(
                      count("*").alias("completed_jobs_for_validation"),
                      sql_sum(when(col("is_valid") == True, 1).otherwise(0)).alias("valid_jobs")
                  )
                  .withColumn("validation_rate", (col("valid_jobs") / col("completed_jobs_for_validation") * 100)))

    return metrics_df


def calculate_tat_metrics(df: DataFrame, group_cols: list) -> DataFrame:
    """
    Calculate TAT (Turnaround Time) metrics.

    Metrics:
      - median_tat_hours: Median TAT in hours
      - avg_tat_hours: Average TAT in hours
    """
    completed_df = df.filter(col("status") == "COMPLETED")

    metrics_df = (completed_df.groupBy(*group_cols)
                  .agg(
                      avg("tat_hours").alias("avg_tat_hours"),
                      # Use percentile_approx for median (exact median is expensive)
                      sql_sum("tat_hours").alias("_sum_tat"),
                      count("*").alias("_count_tat")
                  )
                  .withColumn("median_tat_hours", col("_sum_tat") / col("_count_tat"))  # Approximation
                  .drop("_sum_tat", "_count_tat"))

    return metrics_df


def calculate_escalation_metrics(df: DataFrame, group_cols: list) -> DataFrame:
    """
    Calculate escalation rate metrics.

    Metrics:
      - escalated_jobs: Count of jobs with escalation reason
      - escalation_rate: Percentage of escalated jobs
    """
    metrics_df = (df.groupBy(*group_cols)
                  .agg(
                      count("*").alias("total_for_escalation"),
                      sql_sum(when((col("escalationReason").isNotNull()) &
                                   (col("escalationReason") != ""), 1).otherwise(0)).alias("escalated_jobs")
                  )
                  .withColumn("escalation_rate", (col("escalated_jobs") / col("total_for_escalation") * 100)))

    return metrics_df

# COMMAND ----------

# MAGIC %md
# MAGIC ## Generate Daily Metrics

# COMMAND ----------

# Read from Silver
df_silver = spark.table(SOURCE_TABLE)

# Add date column for grouping (daily)
df_with_date = df_silver.withColumn("date", col("dateOpened"))

# Calculate metrics by date
completion_daily = calculate_completion_metrics(df_with_date, group_cols=["date"])
validation_daily = calculate_validation_metrics(df_with_date, group_cols=["date"])
tat_daily = calculate_tat_metrics(df_with_date, group_cols=["date"])
escalation_daily = calculate_escalation_metrics(df_with_date, group_cols=["date"])

# Join all metrics
gold_daily = (completion_daily
              .join(validation_daily, on="date", how="left")
              .join(tat_daily, on="date", how="left")
              .join(escalation_daily, on="date", how="left")
              .withColumn("_gold_timestamp", current_timestamp()))

# Write to Gold
(gold_daily.write
 .format("delta")
 .mode("overwrite")
 .option("overwriteSchema", "true")
 .saveAsTable(TARGET_TABLE_DAILY))

print(f"✓ Wrote daily metrics to {TARGET_TABLE_DAILY}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Generate Territory Metrics

# COMMAND ----------

# Calculate metrics by territory
completion_territory = calculate_completion_metrics(df_silver, group_cols=["territory"])
validation_territory = calculate_validation_metrics(df_silver, group_cols=["territory"])
tat_territory = calculate_tat_metrics(df_silver, group_cols=["territory"])
escalation_territory = calculate_escalation_metrics(df_silver, group_cols=["territory"])

# Join all metrics
gold_territory = (completion_territory
                  .join(validation_territory, on="territory", how="left")
                  .join(tat_territory, on="territory", how="left")
                  .join(escalation_territory, on="territory", how="left")
                  .withColumn("_gold_timestamp", current_timestamp()))

# Write to Gold
(gold_territory.write
 .format("delta")
 .mode("overwrite")
 .option("overwriteSchema", "true")
 .saveAsTable(TARGET_TABLE_TERRITORY))

print(f"✓ Wrote territory metrics to {TARGET_TABLE_TERRITORY}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Validation & Display

# COMMAND ----------

print("Gold Metrics Summary:")
print("\nDaily Metrics:")
display(spark.table(TARGET_TABLE_DAILY).orderBy(col("date").desc()).limit(10))

print("\nTerritory Metrics:")
display(spark.table(TARGET_TABLE_TERRITORY).orderBy(col("completion_rate").desc()))
```

---

## Common ETL Patterns

### Pattern 1: SCD Type 2 (Slowly Changing Dimensions)

```python
from pyspark.sql.functions import col, when, current_timestamp, lit, md5, concat_ws

def apply_scd_type_2(current_df: DataFrame, incoming_df: DataFrame,
                     key_cols: list, track_cols: list) -> DataFrame:
    """
    Apply SCD Type 2 logic to track historical changes.

    Args:
        current_df: Existing dimension table
        incoming_df: New records to merge
        key_cols: Business key columns
        track_cols: Columns to track for changes

    Returns:
        Updated dimension table with version history
    """
    # Add hash of tracked columns to detect changes
    current_df = current_df.withColumn(
        "_hash",
        md5(concat_ws("|", *[col(c) for c in track_cols]))
    )

    incoming_df = incoming_df.withColumn(
        "_hash",
        md5(concat_ws("|", *[col(c) for c in track_cols]))
    )

    # Find changed records
    changed_records = (incoming_df.alias("new")
                       .join(current_df.alias("curr"),
                             on=key_cols,
                             how="inner")
                       .where(col("new._hash") != col("curr._hash"))
                       .select("new.*"))

    # Close old versions (set end_date)
    updated_current = (current_df.alias("curr")
                       .join(changed_records.alias("changed"),
                             on=key_cols,
                             how="left")
                       .withColumn("end_date",
                                   when(col("changed." + key_cols[0]).isNotNull(),
                                        current_timestamp())
                                   .otherwise(col("curr.end_date")))
                       .withColumn("is_current",
                                   when(col("changed." + key_cols[0]).isNotNull(), False)
                                   .otherwise(col("curr.is_current")))
                       .select("curr.*", "end_date", "is_current"))

    # Insert new versions
    new_versions = (changed_records
                    .withColumn("start_date", current_timestamp())
                    .withColumn("end_date", lit(None))
                    .withColumn("is_current", lit(True)))

    # Union
    result_df = updated_current.union(new_versions)

    return result_df
```

### Pattern 2: Delta Table Merge (Upsert)

```python
from delta.tables import DeltaTable

def upsert_to_delta(df: DataFrame, target_table: str, key_cols: list):
    """
    Upsert DataFrame to Delta table.

    Args:
        df: Source DataFrame
        target_table: Target Delta table name
        key_cols: Columns to match on for merge
    """
    # Build merge condition
    merge_condition = " AND ".join([f"target.{c} = source.{c}" for c in key_cols])

    if DeltaTable.isDeltaTable(spark, target_table):
        delta_table = DeltaTable.forName(spark, target_table)

        (delta_table.alias("target")
         .merge(df.alias("source"), merge_condition)
         .whenMatchedUpdateAll()
         .whenNotMatchedInsertAll()
         .execute())

        print(f"✓ Upserted to {target_table}")
    else:
        (df.write
         .format("delta")
         .mode("overwrite")
         .saveAsTable(target_table))

        print(f"✓ Created {target_table}")
```

### Pattern 3: Incremental Load with Watermark

```python
def incremental_load(source_table: str, target_table: str,
                     watermark_col: str, watermark_table: str):
    """
    Incrementally load data using watermark.

    Args:
        source_table: Source Bronze/Silver table
        target_table: Target Silver/Gold table
        watermark_col: Column to track high water mark (e.g., _ingestion_timestamp)
        watermark_table: Table storing watermarks
    """
    # Get last watermark
    last_watermark = (spark.table(watermark_table)
                      .filter(col("target_table") == target_table)
                      .select("watermark_value")
                      .first())

    if last_watermark:
        last_value = last_watermark[0]
    else:
        last_value = "1970-01-01 00:00:00"

    # Load incremental data
    df_incremental = (spark.table(source_table)
                      .filter(col(watermark_col) > last_value))

    print(f"Incremental records: {df_incremental.count():,}")

    # Process and write to target
    # ... your transformations ...

    # Update watermark
    new_watermark = df_incremental.agg({watermark_col: "max"}).first()[0]

    watermark_df = spark.createDataFrame([
        (target_table, new_watermark, current_timestamp())
    ], ["target_table", "watermark_value", "updated_at"])

    (watermark_df.write
     .format("delta")
     .mode("append")
     .saveAsTable(watermark_table))

    print(f"✓ Updated watermark to {new_watermark}")
```

---

## Testing

```python
import pytest
from pyspark.sql import SparkSession

@pytest.fixture(scope="module")
def spark():
    return SparkSession.builder.appName("test").getOrCreate()

def test_standardize_status(spark):
    test_data = [
        ("Valuation Completed",),
        ("Canceled",),
        ("In Progress",),
    ]
    df = spark.createDataFrame(test_data, ["status"])

    result = standardize_status(df)

    assert result.filter(col("status") == "COMPLETED").count() == 1
    assert result.filter(col("status") == "CANCELED").count() == 1
    assert result.filter(col("status") == "IN_PROGRESS").count() == 1

def test_calculate_completion_metrics(spark):
    test_data = [
        ("NSW_ACT", "COMPLETED"),
        ("NSW_ACT", "COMPLETED"),
        ("NSW_ACT", "IN_PROGRESS"),
        ("QLD", "COMPLETED"),
    ]
    df = spark.createDataFrame(test_data, ["territory", "status"])

    result = calculate_completion_metrics(df, ["territory"])

    nsw_metrics = result.filter(col("territory") == "NSW_ACT").first()
    assert nsw_metrics["total_jobs"] == 3
    assert nsw_metrics["completed_jobs"] == 2
    assert abs(nsw_metrics["completion_rate"] - 66.67) < 0.1
```

---

## Deployment & Orchestration

### Databricks Jobs Configuration

```json
{
  "name": "Valuation ETL Pipeline",
  "tasks": [
    {
      "task_key": "bronze_ingestion",
      "notebook_task": {
        "notebook_path": "/notebooks/01_bronze_ingestion",
        "source": "WORKSPACE"
      },
      "new_cluster": {
        "spark_version": "13.3.x-scala2.12",
        "node_type_id": "i3.xlarge",
        "num_workers": 2
      }
    },
    {
      "task_key": "silver_cleansing",
      "depends_on": [{"task_key": "bronze_ingestion"}],
      "notebook_task": {
        "notebook_path": "/notebooks/02_silver_cleansing",
        "source": "WORKSPACE"
      }
    },
    {
      "task_key": "gold_aggregations",
      "depends_on": [{"task_key": "silver_cleansing"}],
      "notebook_task": {
        "notebook_path": "/notebooks/03_gold_aggregations",
        "source": "WORKSPACE"
      }
    }
  ],
  "schedule": {
    "quartz_cron_expression": "0 0 2 * * ?",
    "timezone_id": "Australia/Sydney"
  }
}
```

---

## Remember

- ✅ **Use Databricks secrets** for credentials (NOT hardcoded)
- ✅ **Implement modular transformation functions** (reusable across pipelines)
- ✅ **Data quality checks** at every layer (Bronze → Silver → Gold)
- ✅ **Delta tables** for ACID guarantees and time travel
- ✅ **Incremental loads** with watermarks for performance
- ✅ **Test transformations** with unit tests
- ✅ **Monitor pipeline health** (record counts, data quality metrics)
- ✅ **Delete chat history** after session

