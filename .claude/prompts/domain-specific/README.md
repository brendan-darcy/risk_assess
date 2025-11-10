# Apprise Workflow Templates

**Phase 0.5 Deliverables** - Comprehensive, production-ready templates based on real Apprise project patterns (survey analyzer, csv-analyser)

---

## Overview

These templates generate working code for Apprise P&T Team's three main workflows:

1. **[data_analyst_csv.md](data_analyst_csv.md)** - Analyze valuation/survey CSVs with pandas
2. **[data_engineer_etl.md](data_engineer_etl.md)** - Build Databricks ETL pipelines (Bronze-Silver-Gold)
3. **[data_services_api.md](data_services_api.md)** - Create AWS Lambda APIs with DuckDB

---

## Key Differences from Phase 0 (Awesome Prompts)

| Phase 0 (Replaced) | Phase 0.5 (New) |
|-------------------|-----------------|
| Generic personas ("act as...") | Real Apprise workflow patterns |
| Thin prompts (< 50 lines) | Comprehensive templates (800-900 lines) |
| No working code generated | Production-ready code output |
| Not aligned with P&T workflows | Based on survey/csv-analyser projects |
| No data safety protocols | File paths only, no CSV injection |
| No Apprise-specific examples | Valuation/survey examples throughout |

---

## Template Structure

Each template follows the security template pattern with:

- **Skills, SSDF, ARMATech headers**: Metadata for searchability
- **Security Checklist**: Mandatory pre-flight verification
- **Data Safety Protocol**: **CRITICAL** - Provide file paths, NOT CSV contents
- **Instructions**: When to use, how to implement, pattern selection
- **Output Examples**: Both simple scripts and modular pipelines
- **Apprise-Specific Patterns**: Real valuation/survey scenarios
- **Synthetic Data Generation**: Test without exposing real data

---

## Quick Start

### 1. Data Analyst (CSV Analysis)

**When to Use**: Analyze valuation reports, survey responses, operational exports

**Example Usage**:
```
User: "Please analyze the valuation completion report at data/valuation_export_oct2025.csv.

Calculate completion rates by territory and valuer.
Generate visualizations for:
- Completion rate trends over time
- Territory comparison
- Valuer performance

Use the modular pipeline pattern (like SurveyAnalyzer) for reusability."
```

**What You Get**:
- `pipelines/analyzer.py` - Modular class with 30+ reusable methods
- `scripts/generate_report.py` - Usage script
- Filtering, metrics calculation, aggregation, visualization methods
- Comprehensive report generation
- Data quality checks

**Key Feature**: **File path only** - CSV never sent to Claude, analyzed locally

---

### 2. Data Engineer (Databricks ETL)

**When to Use**: Transform valuation/survey data from S3 → Delta tables (Bronze → Silver → Gold)

**Example Usage**:
```
User: "Create a Databricks ETL pipeline for valuation data.

Source: s3://apprise-raw-data/valuations/export_*.csv
Target: bronze.valuations → silver.valuations_cleansed → gold.valuation_metrics_daily

Transformations:
- Bronze: Ingest with schema enforcement
- Silver: Deduplicate, standardize statuses/territories, calculate TAT
- Gold: Daily metrics (completion rate, validation rate, median TAT) by territory

Include data quality checks:
- Not null: jobNumber, territory
- Range: marketValueCeiling ($50K - $100M)
- Referential integrity: valuer exists in ref_valuers table

Use modular transformation functions for reusability."
```

**What You Get**:
- `01_bronze_ingestion.py` - S3 → Bronze Delta table
- `02_silver_cleansing.py` - Cleansing, standardization, DQ checks
- `03_gold_aggregations.py` - Business metrics
- `utils/transformations.py` - Reusable functions
- `utils/data_quality.py` - Modular DQ checks
- Databricks job configuration

---

### 3. Data Services (Lambda API)

**When to Use**: Serve Gold layer metrics via API (dashboards, mobile apps, external partners)

**Example Usage**:
```
User: "Create an AWS Lambda API to serve valuation metrics.

Endpoints needed:
1. GET /valuations/metrics/daily?start_date=2025-01-01&end_date=2025-01-31&territory=NSW_ACT
   Returns: Daily completion/validation rates

2. GET /valuations/metrics/territory?territory=QLD
   Returns: Territory-level metrics

3. GET /valuations/{job_number}
   Returns: Job details

4. POST /valuations/aggregate
   Request: { metrics: ["completion_rate"], group_by: ["territory"], filters: {...} }
   Returns: Custom aggregations

Data source: s3://apprise-gold-data/gold/valuation_metrics_daily (Delta table)
Query engine: DuckDB
Authentication: API Gateway API Key
Rate limit: 10,000 requests/day

Use modular query builder pattern for SQL generation.
Include input validation to prevent SQL injection."
```

**What You Get**:
- `lambda_function/handler.py` - Lambda entry point with routing
- `lambda_function/query_builder.py` - Modular DuckDB SQL generation
- `lambda_function/response_formatter.py` - Standardized JSON responses
- `lambda_function/error_handler.py` - Error handling
- `lambda_function/validators.py` - Input validation (SQL injection prevention)
- `serverless.yml` - Deployment configuration
- Unit tests

---

## Pattern Selection Guidance

### When to Use Complete Script vs Modular Pipeline

**Complete Script** (analyze.py pattern):
- ✅ One-off analysis
- ✅ Quick exploratory data analysis
- ✅ Simple transformations
- ✅ ~200 lines
- ✅ Fast to write and execute

**Modular Pipeline** (SurveyAnalyzer pattern):
- ✅ Multiple analysis types
- ✅ Reusable across datasets
- ✅ Complex business logic
- ✅ ~1000+ lines
- ✅ Composable methods (filter → calculate → aggregate)
- ✅ Testable (unit tests for each method)

**Claude will recommend the right pattern based on your requirements**

---

## Data Safety Protocol (CRITICAL)

### ⚠️ Prevent Sensitive Data Injection

**CORRECT - Provide File Path Only**:
```
✅ "Analyze data/valuation_export_oct2025.csv"
✅ "Read from s3://apprise-raw-data/valuations/"
✅ "Query gold.valuation_metrics_daily Delta table"
```

**INCORRECT - Pasting CSV Contents**:
```
❌ "Analyze this data:
    jobNumber,address,borrower_name,valuation_amount
    00295677,29 Little Road BANKSTOWN NSW 2200,John Smith,$1400000
    ..."

⚠️ This exposes PII (addresses, names, job numbers) to Claude!
```

### How It Works

1. User provides **file path** to Claude
2. Claude generates analysis script
3. User runs script **locally in VSCode**
4. Script reads CSV/S3/Delta table locally (data never sent to Claude)
5. Results shown locally
6. User can share **aggregated results** (not raw data)

### Synthetic Data for Examples

Templates include synthetic data generators:
- `generate_synthetic_valuation_data(1000)` - Realistic but fake valuation data
- `generate_synthetic_survey_data(500)` - Realistic but fake survey data
- Australian locale (addresses, phone numbers, territories)
- Use for testing, examples, documentation

---

## Examples from Real Apprise Projects

### Survey Analyzer Pattern

Templates based on `docs - project examples/survey/pipelines/survey_analyzer.py`:

**Modular Methods** (30+):
```python
class SurveyAnalyzer:
    # Categorization
    def _categorize_survey_type(row) -> str
    def _determine_response_status(row) -> str

    # Filtering
    def filter_by_category(category: str) -> DataFrame
    def filter_by_response_status(status: str) -> DataFrame

    # Metrics
    def calculate_completion_rate(df) -> Dict
    def calculate_validation_rate(df) -> Dict

    # Aggregation
    def get_metrics_by_category() -> DataFrame
    def get_interaction_sequences() -> DataFrame

    # Reporting
    def generate_comprehensive_report() -> str
```

**Usage**:
```python
df = pd.read_csv('data/survey_data.csv')
analyzer = SurveyAnalyzer(df)

# Flexible composition of methods
overall_metrics = analyzer.calculate_completion_rate()
category_metrics = analyzer.get_metrics_by_category()
sequences = analyzer.get_interaction_sequences(max_interactions=8)

analyzer.generate_comprehensive_report('report.txt')
```

### CSV Analyzer Pattern

Templates based on `docs - project examples/csv-analyser/analyze.py`:

**Complete Script** (self-contained):
```python
def summarize_csv(file_path: str):
    df = pd.read_csv(file_path)

    # Data overview
    print(f"Rows: {df.shape[0]:,} | Columns: {df.shape[1]}")

    # Statistical analysis
    print(df[numeric_cols].describe())

    # Visualizations
    plt.figure(figsize=(10, 8))
    sns.heatmap(df[numeric_cols].corr(), annot=True)
    plt.savefig('correlation_heatmap.png')

    # Time series
    df.groupby('date')[numeric_cols].mean().plot()
    plt.savefig('time_series.png')

    return summary

# Run
summarize_csv('data/valuation_report.csv')
```

---

## Testing Templates

Each template includes testing patterns:

### Unit Tests
```python
def test_completion_rate_calculation():
    test_df = pd.DataFrame({
        'status': ['COMPLETED', 'COMPLETED', 'IN_PROGRESS']
    })
    rate = (test_df['status'] == 'COMPLETED').mean() * 100
    assert rate == 66.67

def test_synthetic_data_generation():
    df = generate_synthetic_valuation_data(100)
    assert len(df) == 100
    assert 'jobNumber' in df.columns
    assert df['marketValueCeiling'].between(50000, 100000000).all()
```

### Integration Tests
```python
def test_full_pipeline():
    # Bronze ingestion
    bronze_df = ingest_from_s3(source_path)
    assert bronze_df.count() > 0

    # Silver cleansing
    silver_df = cleanse_and_standardize(bronze_df)
    assert silver_df.filter(col("_dq_failed") == True).count() == 0

    # Gold aggregations
    gold_df = calculate_metrics(silver_df)
    assert 'completion_rate' in gold_df.columns
```

---

## Compliance Alignment

All templates include:
- **SSDF Practice Groups**: PW (Produce Well-Secured Software), RV (Respond to Vulnerabilities)
- **ARMATech Principles**: Cloud First, Data-Driven, Security, Modern
- **Security Checklists**: Mandatory pre-flight verification
- **Data Protection**: .claudeignore, file paths only, synthetic data generation
- **OWASP Coverage**: SQL injection prevention, input validation, secure error handling

---

## Folder Structure

```
templates/pt-team/workflows/
├── README.md (this file)
├── data_analyst_csv.md (900 lines)
├── data_engineer_etl.md (900 lines)
├── data_services_api.md (800 lines)
└── _examples/ (future: concrete usage examples)
```

---

## Support

**Questions?** Check:
1. Security checklist in each template
2. "Apprise-Specific Patterns" section
3. "Common Recipes" section
4. Real project examples: `docs - project examples/survey/`, `docs - project examples/csv-analyser/`

**Issues?** Report in project planning docs or to P&T Team Lead

---

**Remember**:
- ⚠️ **Provide file paths, NOT CSV contents**
- ✅ **Use synthetic data** for testing
- ✅ **Choose the right pattern** (simple script vs modular pipeline)
- ✅ **Delete chat history** after session
- ✅ **Follow security checklist** before every use

