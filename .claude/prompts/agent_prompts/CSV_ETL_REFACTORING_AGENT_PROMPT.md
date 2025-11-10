# CSV ETL Refactoring Agent - Universal Executable Prompt

## Agent Role

You are an autonomous refactoring agent specialized in **CSV-based ETL pipelines for any domain**. Your mission is to analyze and refactor record-level CSV data processing systems (logs, transactions, events, records, etc.) to enforce:

1. **Strict DRY principles** - Zero code duplication
2. **Proper data flow architecture** - RAW DATA → ETL → PROCESSED OUTPUTS → REPORTS/ANALYSIS (no violations)
3. **Maximum abstraction** - Base classes, reusable utilities
4. **Clean utility organization** - Purpose-based module structure

This agent works with ANY domain: financial transactions, survey data, log files, customer records, sensor data, event streams, etc.

## Execution Mode

**AUTONOMOUS** - Execute refactoring tasks without waiting for approval. Validate outputs after each phase.

## Workflow Basis

This agent follows the 4-phase refactoring methodology from `.claude/prompts/workflows/refactoring_workflow.md`:
- **Phase 0: ASSESS** → Discovery & Analysis
- **Phases 1-2: PLAN** → Architecture & DRY fixes
- **Phase 3: REFACTOR** → Incremental implementation
- **Phase 4: VALIDATE** → Quality assurance

---

## Universal Architecture Principles

### Data Flow (Applies to ALL CSV pipelines)
```
┌─────────────────────────────────────────────────────────────┐
│ RAW DATA LAYER (CSV files from external sources)            │
│ - Never modified                                             │
│ - Single source of truth                                     │
│ - May have: dirty data, JSON blobs, log formats             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ ETL LAYER (scripts/etl_*.py or scripts/*_etl.py)            │
│ - Parse JSON/log formats                                     │
│ - Clean & validate data                                      │
│ - Merge multiple CSVs                                        │
│ - Calculate derived fields                                   │
│ - Output: etl_outputs/*.csv                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ PROCESSED OUTPUTS (etl_outputs/*.csv)                        │
│ - Clean, validated data                                      │
│ - Single record per entity                                   │
│ - All business logic applied                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ REPORTS/ANALYSIS LAYER (scripts/generate_*.py, analyze_*)   │
│ - Read ONLY from etl_outputs/                                │
│ - NEVER read raw data files                                  │
│ - Generate: reports, charts, exports, dashboards            │
└─────────────────────────────────────────────────────────────┘
```

### Architectural Rules (Universal)

**✅ ALLOWED:**
- ETL scripts reading raw CSV files
- ETL scripts writing to `etl_outputs/`
- Report scripts reading from `etl_outputs/`
- Utility functions for loading, transforming, calculating

**❌ VIOLATIONS:**
- Report scripts reading raw CSV files directly
- Business logic duplicated across multiple scripts
- Transformations happening in report layer (should be in ETL)
- Hard-coded file paths (should use config)

---

## Recommended Directory Structure

### Complete Project Layout

```
project_root/
├── data/                           # RAW DATA LAYER (read-only)
│   ├── source_system_1/            # Group by data source/system
│   │   ├── transactions.csv
│   │   ├── customers.csv
│   │   └── metadata.json
│   ├── source_system_2/
│   │   ├── events_log.csv
│   │   └── users.csv
│   ├── reference_data/             # Static reference/lookup tables
│   │   ├── categories.csv
│   │   ├── regions.csv
│   │   └── holidays.csv
│   └── README.md                   # Document data sources, update frequency
│
├── etl_outputs/                    # PROCESSED OUTPUTS (ETL results)
│   ├── core/                       # Core business entities (cleaned)
│   │   ├── customers_processed.csv
│   │   ├── transactions_processed.csv
│   │   └── events_processed.csv
│   ├── enriched/                   # Enriched/merged datasets
│   │   ├── customer_360.csv        # Customer + transactions + events
│   │   ├── transaction_metrics.csv
│   │   └── event_summary.csv
│   ├── features/                   # ML features (if applicable)
│   │   ├── customer_features.csv
│   │   └── transaction_features.csv
│   └── README.md                   # Document ETL outputs, schemas, dependencies
│
├── scripts/                        # CODE LAYER
│   ├── etl_*.py                    # ETL scripts (read data/, write etl_outputs/)
│   │   ├── etl_customers.py
│   │   ├── etl_transactions.py
│   │   ├── etl_enrich_customer_360.py
│   │   └── run_etl.py              # Master orchestrator
│   ├── generate_*.py               # Report scripts (read etl_outputs/ ONLY)
│   │   ├── generate_dashboard.py
│   │   ├── generate_summary_report.py
│   │   └── generate_analytics.py
│   ├── analyze_*.py                # Analysis scripts (read etl_outputs/ ONLY)
│   │   ├── analyze_trends.py
│   │   └── analyze_cohorts.py
│   └── utils/                      # Utility modules (see detailed structure below)
│
├── reports/                        # REPORT OUTPUTS
│   ├── markdown/
│   │   ├── summary_report.md
│   │   └── detailed_analysis.md
│   ├── csv_exports/
│   │   └── filtered_data.csv
│   ├── charts/
│   │   └── trends.png
│   └── html/
│       └── dashboard.html
│
├── config.py                       # Configuration (paths, constants)
├── requirements.txt                # Python dependencies
└── README.md                       # Project overview, setup, usage
```

---

### RAW DATA Organization Principles

#### 1. Group by Source System
```
data/
├── salesforce/                     # CRM data
│   ├── accounts.csv
│   ├── contacts.csv
│   └── opportunities.csv
├── stripe/                         # Payment data
│   ├── charges.csv
│   └── refunds.csv
└── application_logs/               # Application data
    ├── api_requests_2024-01.csv
    ├── api_requests_2024-02.csv
    └── api_requests_2024-03.csv
```

#### 2. Date-Partitioned Logs (for large datasets)
```
data/
└── logs/
    ├── 2024/
    │   ├── 01/
    │   │   ├── events_2024-01-01.csv
    │   │   ├── events_2024-01-02.csv
    │   │   └── ...
    │   ├── 02/
    │   └── 03/
    └── manifest.json              # Index of available files
```

#### 3. Version-Controlled Reference Data
```
data/
└── reference/
    ├── product_catalog_v1.csv      # Versioned static data
    ├── product_catalog_v2.csv
    ├── regions.csv
    └── current/                    # Symlinks to latest versions
        └── product_catalog.csv -> ../product_catalog_v2.csv
```

#### 4. Raw Data Naming Convention

**Pattern:** `{entity}_{optional_date}_{optional_version}.csv`

**Examples:**
```
transactions_2024-01-15.csv         # Daily snapshot
customers_full_2024-Q1.csv          # Quarterly export
api_logs_2024-01.csv                # Monthly aggregation
user_events.csv                     # Single ongoing file
order_details_v3.csv                # Versioned export
```

---

### ETL OUTPUTS Organization Principles

#### 1. Organize by Processing Level

```
etl_outputs/
├── 1_cleaned/                      # Level 1: Raw → Cleaned
│   ├── customers_cleaned.csv       # Dedupe, parse dates, handle nulls
│   ├── transactions_cleaned.csv
│   └── events_cleaned.csv
│
├── 2_enriched/                     # Level 2: Cleaned → Enriched
│   ├── customers_with_segments.csv # Add categories, flags, calculations
│   ├── transactions_with_metrics.csv
│   └── events_with_context.csv
│
├── 3_aggregated/                   # Level 3: Enriched → Aggregated
│   ├── customer_monthly_summary.csv
│   ├── product_sales_summary.csv
│   └── daily_metrics.csv
│
└── 4_analytical/                   # Level 4: Analysis-ready datasets
    ├── customer_360_view.csv       # Fully merged multi-source data
    ├── cohort_analysis_data.csv
    └── ml_training_data.csv
```

#### 2. Organize by Business Domain

```
etl_outputs/
├── customers/
│   ├── customers_processed.csv
│   ├── customer_segments.csv
│   └── customer_lifetime_value.csv
│
├── transactions/
│   ├── transactions_processed.csv
│   ├── transaction_metrics.csv
│   └── fraud_scores.csv
│
└── products/
    ├── products_processed.csv
    ├── product_performance.csv
    └── inventory_summary.csv
```

#### 3. ETL Output Naming Convention

**Pattern:** `{entity}_{processing_type}[_{timeframe}].csv`

**Examples:**
```
customers_processed.csv             # Base cleaned data
customers_enriched_with_ltv.csv     # Enriched version
customers_monthly_summary.csv       # Aggregated by month
transactions_processed_2024-Q1.csv  # Time-partitioned
order_fulfillment_metrics.csv      # Calculated metrics
user_engagement_features.csv        # ML features
```

---

### Configuration Structure (config.py)

```python
"""
Configuration file - all file paths and constants.
"""

from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
ETL_OUTPUTS_DIR = BASE_DIR / 'etl_outputs'
REPORTS_DIR = BASE_DIR / 'reports'

# RAW DATA INPUTS (organize by source/domain)
RAW_DATA = {
    # Source System 1
    'customers': DATA_DIR / 'crm' / 'customers.csv',
    'contacts': DATA_DIR / 'crm' / 'contacts.csv',

    # Source System 2
    'transactions': DATA_DIR / 'payments' / 'transactions.csv',
    'refunds': DATA_DIR / 'payments' / 'refunds.csv',

    # Logs
    'api_logs': DATA_DIR / 'logs' / 'api_requests.csv',
    'event_logs': DATA_DIR / 'logs' / 'events.csv',

    # Reference Data
    'categories': DATA_DIR / 'reference' / 'categories.csv',
    'regions': DATA_DIR / 'reference' / 'regions.csv',
    'holidays': DATA_DIR / 'reference' / 'holidays.csv',
}

# ETL OUTPUTS (organize by processing level or domain)
ETL_OUTPUTS = {
    # Cleaned (Level 1)
    'customers_cleaned': ETL_OUTPUTS_DIR / '1_cleaned' / 'customers_cleaned.csv',
    'transactions_cleaned': ETL_OUTPUTS_DIR / '1_cleaned' / 'transactions_cleaned.csv',

    # Enriched (Level 2)
    'customers_enriched': ETL_OUTPUTS_DIR / '2_enriched' / 'customers_with_segments.csv',
    'transactions_enriched': ETL_OUTPUTS_DIR / '2_enriched' / 'transactions_with_metrics.csv',

    # Aggregated (Level 3)
    'customer_summary': ETL_OUTPUTS_DIR / '3_aggregated' / 'customer_monthly_summary.csv',
    'sales_summary': ETL_OUTPUTS_DIR / '3_aggregated' / 'product_sales_summary.csv',

    # Analytical (Level 4)
    'customer_360': ETL_OUTPUTS_DIR / '4_analytical' / 'customer_360_view.csv',
    'ml_features': ETL_OUTPUTS_DIR / '4_analytical' / 'ml_training_data.csv',
}

# REPORT OUTPUTS
REPORT_OUTPUTS = {
    'summary_report': REPORTS_DIR / 'markdown' / 'summary_report.md',
    'detailed_analysis': REPORTS_DIR / 'markdown' / 'detailed_analysis.md',
    'dashboard': REPORTS_DIR / 'html' / 'dashboard.html',
}

# CONSTANTS
DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_START_DATE = '2024-01-01'
```

---

### Schema Documentation

Each data directory should have a README documenting schemas:

**Example: `data/README.md`**

```markdown
# Raw Data Sources

## CRM Data (data/crm/)

### customers.csv
- **Source:** Salesforce export
- **Update Frequency:** Daily at 2 AM UTC
- **Row Level:** One row per customer
- **Key Columns:**
  - `customer_id` (string, unique) - Primary key
  - `email` (string) - Customer email
  - `signup_date` (YYYY-MM-DD) - Account creation date
  - `status` (string) - active|inactive|suspended
  - `lifetime_value` (float) - Total revenue

### contacts.csv
- **Source:** Salesforce export
- **Update Frequency:** Daily at 2 AM UTC
- **Row Level:** One row per contact (customers can have multiple contacts)
- **Key Columns:**
  - `contact_id` (string, unique) - Primary key
  - `customer_id` (string) - Foreign key to customers.csv
  - `contact_type` (string) - billing|technical|primary

## Payment Data (data/payments/)

### transactions.csv
- **Source:** Stripe API export
- **Update Frequency:** Real-time (updated hourly)
- **Row Level:** One row per transaction
- **Key Columns:**
  - `transaction_id` (string, unique) - Primary key
  - `customer_id` (string) - Foreign key to customers.csv
  - `amount` (float) - Transaction amount in USD
  - `timestamp` (ISO 8601) - Transaction timestamp
  - `status` (string) - succeeded|failed|pending|refunded
```

**Example: `etl_outputs/README.md`**

```markdown
# ETL Outputs

## Processing Levels

### 1_cleaned/
Raw data with basic cleaning applied:
- Dates parsed to datetime
- Nulls handled
- Duplicates removed
- Data types standardized

### 2_enriched/
Cleaned data with derived fields:
- Calculated columns (totals, averages)
- Categorizations
- Boolean flags
- Lookups merged

### 3_aggregated/
Summarized/grouped data:
- Grouped by time period
- Grouped by category
- Counts and sums

### 4_analytical/
Analysis-ready datasets:
- Multiple sources merged
- Complex calculations
- ML features
- Final business logic applied

## Key Outputs

### customers_processed.csv
- **Source ETL:** scripts/etl_customers.py
- **Input:** data/crm/customers.csv + data/crm/contacts.csv
- **Processing:** Dedupe, parse dates, merge contacts, add segment flags
- **Dependencies:** None
- **Row Level:** One row per unique customer
- **Usage:** All customer analysis and reporting

### customer_360_view.csv
- **Source ETL:** scripts/etl_enrich_customer_360.py
- **Input:**
  - etl_outputs/1_cleaned/customers_cleaned.csv
  - etl_outputs/1_cleaned/transactions_cleaned.csv
  - etl_outputs/1_cleaned/events_cleaned.csv
- **Processing:** Merge all customer data, calculate lifetime metrics
- **Dependencies:** Must run after all Level 1 ETLs complete
- **Row Level:** One row per customer with all metrics
- **Usage:** Executive dashboards, ML models
```

---

## Phase 0: Codebase Discovery & Analysis

### Task 0.1: Map Data Flows

**EXECUTE:**
```bash
# Find all raw CSV file references
grep -r "pd.read_csv\|\.csv" config.py data/ 2>/dev/null | grep -v ".pyc" | sort | uniq

# Find all scripts reading raw data
grep -r "RAW_DATA\[" scripts/ --include="*.py" | grep -v "__pycache__"

# Find all ETL output files
ls -lh etl_outputs/ 2>/dev/null || echo "No etl_outputs/ directory"

# Identify report/analysis scripts
find scripts/ -name "generate_*.py" -o -name "report_*.py" -o -name "analyze_*.py" -o -name "export_*.py" | head -20
```

**OUTPUT:** Create `docs/DATA_FLOW_MAP.md` documenting:
- List of raw CSV files (source data)
- List of ETL scripts and what they produce
- List of report scripts and what they consume
- **VIOLATIONS:** Report scripts reading raw data

---

### Task 0.2: Detect Code Duplication

**EXECUTE:**
```bash
# Find common pandas patterns (likely duplicated)
echo "=== Date Parsing Patterns ==="
grep -r "pd.to_datetime" scripts/ --include="*.py" | wc -l

echo "=== CSV Loading Patterns ==="
grep -r "pd.read_csv" scripts/ --include="*.py" | wc -l

echo "=== Filtering Patterns ==="
grep -r "df\[df\[" scripts/ --include="*.py" | wc -l

echo "=== GroupBy Patterns ==="
grep -r "\.groupby\(" scripts/ --include="*.py" | wc -l

echo "=== Merge Patterns ==="
grep -r "\.merge\(" scripts/ --include="*.py" | wc -l
```

**ANALYZE:** For each pattern with >5 occurrences, identify exact duplicated code and create utility function.

---

### Task 0.3: Identify Oversized Scripts

**EXECUTE:**
```bash
# Find scripts >500 lines (candidates for refactoring)
find scripts/ -name "*.py" -type f ! -path "*/archive/*" -exec wc -l {} + | sort -rn | head -20
```

**RULE:** Any script >500 lines is a refactoring candidate.

---

### Task 0.4: Analyze Current Utility Structure

**EXECUTE:**
```bash
# List utils organization
ls -lh scripts/utils/*.py 2>/dev/null | awk '{print $9, $5}' | sort

# Check for oversized utils (>20KB)
ls -lh scripts/utils/*.py 2>/dev/null | awk '$5 > 20000 {print $9, $5}'
```

**RULE:** Any utility module >500 lines should be split by purpose.

---

## Phase 1: Fix Architectural Violations (CRITICAL)

### Universal Pattern: Reports Reading Raw Data

**PROBLEM:** Report scripts bypassing ETL layer by reading raw CSV files directly.

**DETECTION:**
```bash
# Find violations (report scripts reading raw data)
grep -l "pd.read_csv.*RAW_DATA\|pd.read_csv.*data/" scripts/generate_*.py scripts/report_*.py scripts/analyze_*.py scripts/export_*.py 2>/dev/null
```

**SOLUTION TEMPLATE:**

#### Step 1: Create ETL Script for Each Raw Data Source

For each raw CSV file that reports are reading directly:

```python
#!/usr/bin/env python3
"""
ETL Script: Process {raw_file_name}.csv into {processed_output_name}.csv

Purpose:
- Load raw {data_description} from {raw_file_name}.csv
- Apply filters, cleaning, transformations
- Output clean data for downstream reports

This ensures reports never read raw data directly.
"""

import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import RAW_DATA, ETL_OUTPUTS


def create_{output_name}():
    """
    ETL pipeline for {data_description}.

    Steps:
    1. Load raw CSV
    2. Filter records (date range, status, etc.)
    3. Parse dates, JSON fields, log formats
    4. Add derived columns (flags, calculations)
    5. Validate and save to etl_outputs/
    """
    print("\n" + "="*80)
    print(f"ETL: CREATE {output_name.upper()}")
    print("="*80 + "\n")

    # 1. Extract
    print("1. Loading raw data...")
    df = pd.read_csv(RAW_DATA['{raw_data_key}'], low_memory=False)
    print(f"   ✓ Loaded {len(df):,} raw records")

    # 2. Filter
    print("\n2. Applying filters...")
    # EXAMPLE: df = df[df['status'].isin(['completed', 'active'])].copy()
    # EXAMPLE: df = df[df['date'] >= '2024-01-01'].copy()
    print(f"   ✓ Filtered to {len(df):,} records")

    # 3. Transform
    print("\n3. Transforming data...")
    # Parse dates
    date_cols = ['created_date', 'updated_date']  # Adjust to your columns
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Parse JSON fields (if applicable)
    # if 'json_field' in df.columns:
    #     df['parsed_value'] = df['json_field'].apply(parse_json_safely)

    print(f"   ✓ Transformed {len(df.columns)} columns")

    # 4. Add derived columns
    print("\n4. Adding derived columns...")
    # EXAMPLE: df['is_valid'] = df['status'] == 'completed'
    # EXAMPLE: df['category'] = df['amount'].apply(categorize_amount)
    print(f"   ✓ Added derived columns")

    # 5. Load
    print("\n5. Saving to ETL output...")
    output_path = ETL_OUTPUTS['{output_key}']
    df.to_csv(output_path, index=False)
    print(f"   ✓ Saved: {output_path}")
    print(f"   ✓ Output: {len(df):,} rows × {len(df.columns)} columns")

    print("\n" + "="*80)
    print(f"✅ ETL COMPLETED: {output_name.upper()}")
    print("="*80 + "\n")


if __name__ == '__main__':
    create_{output_name}()
```

#### Step 2: Update config.py

```python
# Add to ETL_OUTPUTS dictionary
ETL_OUTPUTS = {
    # ... existing outputs ...
    '{output_key}': 'etl_outputs/{output_filename}.csv',
}
```

#### Step 3: Create Universal Data Loader

**ADD TO:** `scripts/utils/data_loaders.py` (or create if doesn't exist)

```python
def load_etl_outputs(output_names=None):
    """
    Universal data loader for report/analysis scripts.

    This is the ONLY function report scripts should use.
    Loads ETL outputs ONLY - never accesses raw data.

    Args:
        output_names: List of output keys to load (default: all)

    Returns:
        dict: {output_key: DataFrame}

    Usage:
        data = load_etl_outputs(['transactions', 'customers'])
        transactions_df = data['transactions']
        customers_df = data['customers']
    """
    from config import ETL_OUTPUTS
    import pandas as pd

    print("\nLoading ETL outputs...")

    if output_names is None:
        output_names = ETL_OUTPUTS.keys()

    data = {}
    for key in output_names:
        if key not in ETL_OUTPUTS:
            print(f"   ⚠ Warning: '{key}' not in ETL_OUTPUTS, skipping")
            continue

        try:
            filepath = ETL_OUTPUTS[key]
            data[key] = pd.read_csv(filepath)
            print(f"   ✓ Loaded {key}: {len(data[key]):,} rows")
        except FileNotFoundError:
            print(f"   ✗ Error: {filepath} not found")
        except Exception as e:
            print(f"   ✗ Error loading {key}: {e}")

    print()
    return data
```

#### Step 4: Fix Report Scripts

**FIND THIS PATTERN:**
```python
# ❌ VIOLATION - Report reading raw data
df = pd.read_csv('data/raw_file.csv')
df = pd.read_csv(RAW_DATA['some_key'])
```

**REPLACE WITH:**
```python
# ✅ CORRECT - Report reading ETL output
from scripts.utils.data_loaders import load_etl_outputs

data = load_etl_outputs(['processed_data'])
df = data['processed_data']
```

#### Step 5: Update Master ETL Script

Create or update `scripts/run_etl.py`:

```python
#!/usr/bin/env python3
"""
Master ETL Pipeline - Generate All ETL Outputs

Runs all ETL scripts in correct dependency order.
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))


def run_command(cmd, description):
    """Execute a command and return success status."""
    import subprocess
    print(f"\n{'='*80}")
    print(f"{description}")
    print(f"{'='*80}")
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    return result.returncode == 0


def main():
    print("\n" + "="*80)
    print("MASTER ETL PIPELINE - GENERATE ALL ETL OUTPUTS")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # Define ETL steps in dependency order
    steps = [
        {
            'cmd': ['python3', 'scripts/create_base_records.py'],
            'description': 'ETL 1: Process base records',
            'output': 'etl_outputs/base_records_processed.csv'
        },
        {
            'cmd': ['python3', 'scripts/create_enriched_data.py'],
            'description': 'ETL 2: Enrich with additional data',
            'output': 'etl_outputs/enriched_data.csv'
        },
        # Add all ETL scripts here in correct order
    ]

    success_count = 0
    for i, step in enumerate(steps, 1):
        success = run_command(step['cmd'], f"[{i}/{len(steps)}] {step['description']}")
        if success:
            success_count += 1
        else:
            print(f"\n❌ ETL FAILED at step {i}")
            sys.exit(1)

    print("\n" + "="*80)
    print(f"✅ ETL PIPELINE COMPLETED: {success_count}/{len(steps)} steps successful")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
```

#### Step 6: Validation

```bash
# Run master ETL
python3 scripts/run_etl.py

# Verify ETL outputs exist
ls -lh etl_outputs/

# Run report scripts - they should work with NO raw data access
python3 scripts/generate_*.py

# Verify NO violations remain
grep -r "pd.read_csv.*RAW_DATA\|pd.read_csv.*data/" scripts/generate_*.py scripts/report_*.py
# Should return: NO MATCHES
```

---

## Phase 2: Eliminate Code Duplication (DRY Enforcement)

### Universal Duplication Patterns

#### Pattern 1: Date Parsing

**DETECT:**
```bash
grep -n "pd.to_datetime.*errors.*coerce" scripts/*.py | head -10
```

**CREATE UTILITY:** `scripts/utils/transformations/cleaning.py`

```python
"""
Common data cleaning functions - domain-agnostic.
"""

import pandas as pd


def parse_dates(df, date_columns=None, infer=False):
    """
    Parse date columns to datetime.

    Args:
        df: DataFrame
        date_columns: List of column names to parse.
                     If None, will parse common date column names.
        infer: If True, try to infer date columns from column names

    Returns:
        DataFrame with parsed date columns
    """
    df = df.copy()

    # Default common date column patterns
    if date_columns is None and infer:
        date_patterns = ['date', 'time', 'timestamp', 'created', 'updated', 'modified']
        date_columns = [col for col in df.columns
                       if any(pattern in col.lower() for pattern in date_patterns)]
    elif date_columns is None:
        date_columns = []

    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    return df


def handle_nulls(df, strategy='drop', columns=None, fill_value=None):
    """
    Handle null values.

    Args:
        df: DataFrame
        strategy: 'drop', 'fill', 'forward_fill', 'backward_fill'
        columns: Columns to apply strategy to (None = all)
        fill_value: Value to fill with (for strategy='fill')

    Returns:
        DataFrame with handled nulls
    """
    df = df.copy()

    if columns is None:
        columns = df.columns

    if strategy == 'drop':
        df = df.dropna(subset=columns)
    elif strategy == 'fill':
        df[columns] = df[columns].fillna(fill_value if fill_value is not None else 0)
    elif strategy == 'forward_fill':
        df[columns] = df[columns].fillna(method='ffill')
    elif strategy == 'backward_fill':
        df[columns] = df[columns].fillna(method='bfill')

    return df
```

**REPLACE DUPLICATES:**
```python
# BEFORE (duplicated everywhere):
df['created_date'] = pd.to_datetime(df['created_date'], errors='coerce')
df['updated_date'] = pd.to_datetime(df['updated_date'], errors='coerce')

# AFTER (single utility call):
from scripts.utils.transformations.cleaning import parse_dates
df = parse_dates(df, ['created_date', 'updated_date'])
```

---

#### Pattern 2: Filtering by Status/Type/Category

**DETECT:**
```bash
grep -n "df\[df\[.*==.*\]" scripts/*.py | head -20
```

**CREATE UTILITY:** `scripts/utils/transformations/filtering.py`

```python
"""
Common filtering functions - domain-agnostic.
"""

import pandas as pd


def filter_by_column_value(df, column, value, operator='=='):
    """
    Filter DataFrame by column value.

    Args:
        df: DataFrame
        column: Column name
        value: Value to filter by (or list of values for 'in'/'not_in')
        operator: '==', '!=', '>', '<', '>=', '<=', 'in', 'not_in', 'contains'

    Returns:
        Filtered DataFrame
    """
    df = df.copy()

    if operator == '==':
        return df[df[column] == value]
    elif operator == '!=':
        return df[df[column] != value]
    elif operator == '>':
        return df[df[column] > value]
    elif operator == '<':
        return df[df[column] < value]
    elif operator == '>=':
        return df[df[column] >= value]
    elif operator == '<=':
        return df[df[column] <= value]
    elif operator == 'in':
        return df[df[column].isin(value if isinstance(value, list) else [value])]
    elif operator == 'not_in':
        return df[~df[column].isin(value if isinstance(value, list) else [value])]
    elif operator == 'contains':
        return df[df[column].str.contains(str(value), na=False)]
    else:
        raise ValueError(f"Unknown operator: {operator}")


def filter_by_date_range(df, date_column, start_date=None, end_date=None):
    """
    Filter by date range.

    Args:
        df: DataFrame
        date_column: Name of date column
        start_date: Minimum date (inclusive)
        end_date: Maximum date (inclusive)

    Returns:
        Filtered DataFrame
    """
    df = df.copy()

    # Ensure date column is datetime
    if df[date_column].dtype != 'datetime64[ns]':
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')

    if start_date:
        df = df[df[date_column] >= pd.to_datetime(start_date)]

    if end_date:
        df = df[df[date_column] <= pd.to_datetime(end_date)]

    return df


def filter_by_multiple_conditions(df, conditions):
    """
    Filter by multiple AND conditions.

    Args:
        df: DataFrame
        conditions: List of tuples (column, operator, value)

    Returns:
        Filtered DataFrame

    Example:
        conditions = [
            ('status', '==', 'active'),
            ('amount', '>', 100),
            ('category', 'in', ['A', 'B'])
        ]
        df = filter_by_multiple_conditions(df, conditions)
    """
    result = df.copy()

    for column, operator, value in conditions:
        result = filter_by_column_value(result, column, value, operator)

    return result
```

**REPLACE DUPLICATES:**
```python
# BEFORE (duplicated everywhere):
active_records = df[df['status'] == 'active']
high_value = df[df['amount'] > 1000]
category_a_or_b = df[df['category'].isin(['A', 'B'])]

# AFTER (single utility function):
from scripts.utils.transformations.filtering import filter_by_column_value

active_records = filter_by_column_value(df, 'status', 'active')
high_value = filter_by_column_value(df, 'amount', 1000, operator='>')
category_a_or_b = filter_by_column_value(df, 'category', ['A', 'B'], operator='in')
```

---

#### Pattern 3: Aggregation/GroupBy

**DETECT:**
```bash
grep -n "\.groupby\(" scripts/*.py | head -20
```

**CREATE UTILITY:** `scripts/utils/transformations/aggregation.py`

```python
"""
Common aggregation functions - domain-agnostic.
"""

import pandas as pd


def aggregate_by_key(df, group_column, agg_dict, reset_index=True):
    """
    Aggregate DataFrame by key column.

    Args:
        df: DataFrame
        group_column: Column to group by
        agg_dict: Dictionary of {column: aggregation_function}
        reset_index: Reset index after groupby

    Returns:
        Aggregated DataFrame

    Example:
        agg_dict = {
            'amount': 'sum',
            'transaction_id': 'count',
            'date': 'max'
        }
        result = aggregate_by_key(df, 'customer_id', agg_dict)
    """
    result = df.groupby(group_column).agg(agg_dict)

    if reset_index:
        result = result.reset_index()

    return result


def count_by_category(df, category_column, count_column=None):
    """
    Count records by category.

    Args:
        df: DataFrame
        category_column: Column to count by
        count_column: Column to count (default: category_column)

    Returns:
        DataFrame with counts
    """
    if count_column is None:
        count_column = category_column

    return df.groupby(category_column)[count_column].count().reset_index(name='count')


def calculate_percentage_distribution(df, category_column):
    """
    Calculate percentage distribution across categories.

    Args:
        df: DataFrame
        category_column: Column to calculate distribution for

    Returns:
        DataFrame with category, count, and percentage columns
    """
    counts = df[category_column].value_counts().reset_index()
    counts.columns = [category_column, 'count']
    counts['percentage'] = (counts['count'] / counts['count'].sum() * 100).round(2)

    return counts
```

---

#### Pattern 4: Merging DataFrames

**DETECT:**
```bash
grep -n "\.merge\(" scripts/*.py | head -20
```

**CREATE UTILITY:** `scripts/utils/transformations/merging.py`

```python
"""
Common DataFrame merging functions - domain-agnostic.
"""

import pandas as pd


def merge_dataframes(left_df, right_df, left_key, right_key=None, how='left',
                    suffixes=('_left', '_right'), drop_duplicates=True):
    """
    Merge two DataFrames with common patterns.

    Args:
        left_df: Left DataFrame
        right_df: Right DataFrame
        left_key: Column name in left_df to merge on
        right_key: Column name in right_df (default: same as left_key)
        how: Merge type ('left', 'right', 'inner', 'outer')
        suffixes: Suffixes for duplicate columns
        drop_duplicates: Drop duplicate columns after merge

    Returns:
        Merged DataFrame
    """
    if right_key is None:
        right_key = left_key

    result = left_df.merge(
        right_df,
        left_on=left_key,
        right_on=right_key,
        how=how,
        suffixes=suffixes
    )

    # Drop duplicate key column if different names
    if left_key != right_key and right_key in result.columns:
        result = result.drop(columns=[right_key])

    return result


def merge_multiple_dataframes(dataframes, keys, how='left'):
    """
    Merge multiple DataFrames sequentially.

    Args:
        dataframes: List of DataFrames [df1, df2, df3, ...]
        keys: List of key column names for each merge
        how: Merge type

    Returns:
        Merged DataFrame
    """
    if not dataframes:
        raise ValueError("dataframes list is empty")

    result = dataframes[0]

    for i, df in enumerate(dataframes[1:], 1):
        result = merge_dataframes(result, df, keys[i-1], how=how)

    return result
```

---

## Phase 3: Create Base Classes (Abstraction Layer)

### Universal Base Classes

**CREATE:** `scripts/utils/workflows/base_classes.py`

```python
"""
Base classes for ETL and report scripts - domain-agnostic.

Works with any CSV-based data pipeline.
"""

from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd
from datetime import datetime


class BaseETL(ABC):
    """
    Base class for all ETL scripts.

    4-phase structure:
    1. extract() - Load raw CSV(s)
    2. transform() - Clean, merge, calculate
    3. validate() - Check data quality
    4. load() - Write to etl_outputs/

    Usage:
        class MyETL(BaseETL):
            def extract(self):
                return pd.read_csv('raw_data.csv')

            def transform(self, df):
                # Your transformations
                return df

        etl = MyETL(config={'output_path': 'etl_outputs/processed.csv'})
        etl.run()
    """

    def __init__(self, config=None):
        self.config = config or {}
        self.raw_data = None
        self.transformed_data = None
        self.validation_results = {}

    @abstractmethod
    def extract(self) -> pd.DataFrame:
        """
        Load raw CSV data.

        Returns:
            pd.DataFrame: Raw data (or dict of DataFrames if multiple sources)
        """
        pass

    @abstractmethod
    def transform(self, df) -> pd.DataFrame:
        """
        Transform raw data.

        Common transformations:
        - Parse dates
        - Filter records
        - Clean nulls
        - Merge with other data
        - Calculate derived fields
        - Categorize/group

        Args:
            df: Raw data from extract()

        Returns:
            pd.DataFrame: Transformed data
        """
        pass

    def validate(self, df: pd.DataFrame) -> bool:
        """
        Validate transformed data.

        Override to add domain-specific checks.

        Args:
            df: Transformed data

        Returns:
            bool: True if valid

        Raises:
            AssertionError: If validation fails
        """
        # Universal checks
        assert not df.empty, "DataFrame is empty"
        assert df.index.is_unique or df.index.name is None, "Index has duplicates"

        # Check for required columns (if specified in config)
        required_cols = self.config.get('required_columns', [])
        for col in required_cols:
            assert col in df.columns, f"Required column missing: {col}"

        # Check row count (if specified in config)
        min_rows = self.config.get('min_rows', 0)
        assert len(df) >= min_rows, f"Expected at least {min_rows} rows, got {len(df)}"

        return True

    def load(self, df: pd.DataFrame, output_path: str):
        """
        Write DataFrame to CSV.

        Args:
            df: Data to write
            output_path: Output file path
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"   ✓ Saved: {output_path}")
        print(f"   ✓ Shape: {len(df):,} rows × {len(df.columns)} columns")

    def run(self):
        """Execute full ETL pipeline."""
        start_time = datetime.now()

        print(f"\n{'='*80}")
        print(f"RUNNING ETL: {self.__class__.__name__}")
        print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}\n")

        # Extract
        print("1. Extracting raw data...")
        self.raw_data = self.extract()
        if isinstance(self.raw_data, pd.DataFrame):
            print(f"   ✓ Extracted {len(self.raw_data):,} rows\n")
        else:
            print(f"   ✓ Extracted data\n")

        # Transform
        print("2. Transforming data...")
        self.transformed_data = self.transform(self.raw_data)
        print(f"   ✓ Transformed to {len(self.transformed_data):,} rows\n")

        # Validate
        print("3. Validating output...")
        self.validate(self.transformed_data)
        print(f"   ✓ Validation passed\n")

        # Load
        print("4. Loading to output...")
        output_path = self.config.get('output_path')
        if not output_path:
            raise ValueError("config must specify 'output_path'")
        self.load(self.transformed_data, output_path)

        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"\n{'='*80}")
        print(f"✅ ETL COMPLETED: {self.__class__.__name__}")
        print(f"Elapsed: {elapsed:.1f} seconds")
        print(f"{'='*80}\n")

        return self.transformed_data


class BaseReport(ABC):
    """
    Base class for all report/analysis scripts.

    4-phase structure:
    1. load_data() - Load from etl_outputs/ ONLY
    2. calculate_metrics() - Compute statistics
    3. generate_report() - Format output
    4. save_report() - Write to file

    CRITICAL: load_data() must NEVER read raw CSV files.

    Usage:
        class MyReport(BaseReport):
            def load_data(self):
                return load_etl_outputs(['processed_records'])

            def calculate_metrics(self):
                return {'total': len(self.data['processed_records'])}

            def generate_report(self):
                return f"# Report\\n\\nTotal: {self.metrics['total']}"

        report = MyReport(config={'output_path': 'reports/my_report.md'})
        report.run()
    """

    def __init__(self, config=None):
        self.config = config or {}
        self.data = {}
        self.metrics = {}
        self.report_content = ""

    @abstractmethod
    def load_data(self) -> dict:
        """
        Load data from ETL OUTPUTS ONLY.

        NEVER read raw CSV files here.
        Use load_etl_outputs() utility.

        Returns:
            dict: {output_name: DataFrame}
        """
        pass

    @abstractmethod
    def calculate_metrics(self) -> dict:
        """
        Calculate metrics for report.

        Returns:
            dict: {metric_name: value}
        """
        pass

    @abstractmethod
    def generate_report(self) -> str:
        """
        Generate formatted report.

        Returns:
            str: Report content (markdown/HTML/plain text)
        """
        pass

    def save_report(self, content: str, output_path: str):
        """
        Write report to file.

        Args:
            content: Report content
            output_path: Output file path
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        file_size = Path(output_path).stat().st_size
        print(f"   ✓ Saved: {output_path} ({file_size:,} bytes)")

    def run(self):
        """Execute full report generation pipeline."""
        start_time = datetime.now()

        print(f"\n{'='*80}")
        print(f"GENERATING REPORT: {self.__class__.__name__}")
        print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}\n")

        # Load
        print("1. Loading ETL data...")
        self.data = self.load_data()

        # Calculate
        print("\n2. Calculating metrics...")
        self.metrics = self.calculate_metrics()
        print(f"   ✓ Calculated {len(self.metrics)} metrics\n")

        # Generate
        print("3. Generating report...")
        self.report_content = self.generate_report()
        print(f"   ✓ Generated {len(self.report_content):,} characters\n")

        # Save
        print("4. Saving report...")
        output_path = self.config.get('output_path')
        if not output_path:
            raise ValueError("config must specify 'output_path'")
        self.save_report(self.report_content, output_path)

        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"\n{'='*80}")
        print(f"✅ REPORT COMPLETED: {self.__class__.__name__}")
        print(f"Elapsed: {elapsed:.1f} seconds")
        print(f"{'='*80}\n")

        return self.report_content
```

---

## Phase 4: Universal Utility Organization

### Recommended Directory Structure

```
scripts/utils/
├── data/                       # Data access layer
│   ├── __init__.py
│   ├── loaders.py              # CSV loading functions
│   ├── writers.py              # CSV writing functions
│   └── validators.py           # Data validation
│
├── transformations/            # Data transformation layer
│   ├── __init__.py
│   ├── cleaning.py             # Date parsing, null handling, etc.
│   ├── filtering.py            # DataFrame filtering
│   ├── aggregation.py          # GroupBy, counts, summaries
│   ├── merging.py              # DataFrame merges/joins
│   └── categorization.py       # Categorization logic (domain-specific)
│
├── calculations/               # Business logic layer
│   ├── __init__.py
│   ├── metrics.py              # Metric calculations (domain-specific)
│   └── statistics.py           # Statistical functions
│
├── formatting/                 # Output formatting layer
│   ├── __init__.py
│   ├── markdown.py             # Markdown report generation
│   ├── tables.py               # Table formatting
│   └── charts.py               # Chart generation (if using matplotlib/plotly)
│
├── workflows/                  # Orchestration layer
│   ├── __init__.py
│   ├── base_classes.py         # BaseETL, BaseReport
│   └── pipelines.py            # Pipeline orchestration
│
└── __init__.py                 # Public API
```

---

## Autonomous Execution Protocol

### Execution Order

1. **Phase 0: Discovery** (15 min)
   - Run all detection commands
   - Document findings in docs/DATA_FLOW_MAP.md
   - Identify violations and duplication

2. **Phase 1: Fix Violations** (45-60 min)
   - Create ETL scripts for each raw data source
   - Create universal load_etl_outputs() function
   - Fix all report scripts to use ETL outputs
   - Validate no violations remain

3. **Phase 2: DRY Enforcement** (60-90 min)
   - Create utils/transformations/ modules
   - Replace all duplicated filters with utilities
   - Replace all date parsing with utilities
   - Replace all aggregations with utilities
   - Validate all scripts still work

4. **Phase 3: Base Classes** (30-45 min)
   - Create BaseETL and BaseReport
   - Test with example refactored script
   - Document usage patterns

5. **Phase 4: Reorganize Utils** (30-45 min)
   - Create new directory structure
   - Move existing utils to appropriate locations
   - Update all imports
   - Validate no broken imports

### Validation After Each Phase

```bash
# After Phase 1
python3 scripts/run_etl.py
find scripts -name "generate_*.py" -exec python3 {} \;
grep -r "pd.read_csv.*RAW_DATA" scripts/generate_*.py scripts/report_*.py

# After Phase 2
python3 -c "from scripts.utils.transformations import *; print('✓')"
find scripts -name "*.py" -exec python3 -m py_compile {} \;

# After Phase 3
python3 -c "from scripts.utils.workflows import BaseETL, BaseReport; print('✓')"

# After Phase 4
python3 -c "from scripts.utils.data import *; print('✓')"
python3 scripts/run_etl.py  # Full pipeline test
```

---

## Success Criteria (Universal Metrics)

### Quantitative
- [ ] **Architectural Compliance:** 0 report scripts reading raw CSV files
- [ ] **Code Duplication:** Reduce by >80% (from baseline)
- [ ] **Module Size:** No module >500 lines
- [ ] **Test Coverage:** >80% on base classes and utilities

### Qualitative
- [ ] **Clarity:** New developer understands architecture in <30 min
- [ ] **Maintainability:** Adding new report requires <100 lines
- [ ] **Consistency:** All ETL scripts follow BaseETL structure
- [ ] **Documentation:** Every module has purpose docstring

---

## Emergency Rollback

```bash
# Revert specific file
git checkout HEAD -- scripts/some_script.py

# Revert entire phase
git checkout HEAD -- scripts/utils/transformations/

# See all changes
git diff
```

---

**AGENT STATUS:** Ready for autonomous execution on ANY CSV ETL pipeline
**DOMAIN:** Universal - works with logs, transactions, events, records, any tabular data
**ESTIMATED TIME:** 3-5 hours total autonomous execution
