# Skills: data_analysis, data_visualization, python, pandas, statistics
# SSDF Practice Group: PW (Produce Well-Secured Software)
# ARMATech Principles: Data-Driven, Modern, Security
# Language: Python
# Context: Apprise Risk Solutions P&T Team - Data Analysis Workflows

## Security Reminder
⚠️ **CRITICAL - Data Safety Protocol**: This template analyzes sensitive valuation, survey, and operational data. Follow security checklist below.

## Security Checklist
- [ ] .claudeignore exists and includes: **/*.csv, **/data/**, **/*.env, credentials.json
- [ ] Working in Dev/Sandbox environment only
- [ ] Using dummy test data (NO client data)
- [ ] Will delete Claude Code chat history after this session
- [ ] ⚠️ **CRITICAL**: Provide FILE PATHS only, NOT file contents (to avoid injecting sensitive data into prompt)

## Placeholders
- `[FILE_PATH]` - Path to CSV file (e.g., "data/valuation_report.csv")
- `[ANALYSIS_TYPE]` - Type of analysis (completion_rates | validation_metrics | interaction_sequences | comprehensive)
- `[GROUP_BY]` - Grouping columns (territory | valuer | category | date)
- `[OUTPUT_FORMAT]` - Output format (txt | markdown | html | json)
- `[COMPLEXITY]` - Implementation approach (simple_script | modular_pipeline)

---

## Task: Comprehensive CSV Data Analysis

You are a data analyst at Apprise Risk Solutions analyzing operational data from valuation and survey systems. Generate production-ready Python code that performs comprehensive analysis of CSV data with proper visualizations, statistical summaries, and business insights.

This template is based on **real Apprise project patterns**:
- **Modular Pipeline Pattern**: `survey/pipelines/survey_analyzer.py` (~1400 lines, 30+ reusable methods, OOP design)
- **Complete Script Pattern**: `csv-analyser/analyze.py` (~180 lines, self-contained, immediate results)

### Context
- **Requirement**: Analyze valuation reports, survey data, operational exports
- **Challenge**: Data contains PII (addresses, names, job numbers)
- **Solution**: Analyze locally without injecting sensitive data into Claude prompt
- **Integration**: Part of reporting workflows, dashboard data prep, business intelligence

---

## Critical: Data Safety Protocol

### ⚠️ Prevent Sensitive Data Injection

**CORRECT Approach - Reference File Path:**
```
User: "Please analyze the valuation completion report at data/valuation_export.csv.
Calculate completion rates by territory and valuer. Generate visualizations."
```

**INCORRECT Approach - Pasting CSV Contents:**
```
User: "Analyze this data:
job_number,address,borrower_name,valuation_amount
00295677,29 Little Road BANKSTOWN NSW 2200,John Smith,$1400000
00295676,6 HONEYEATER Court THORNLANDS QLD 4164,Jane Doe,$2100000
..."
❌ This exposes sensitive PII to Claude!
```

### Local Analysis Pattern

**How It Works:**
1. User provides **file path only** to Claude
2. Claude generates analysis script
3. User runs script **locally in VSCode**
4. Script reads CSV from disk (data never sent to Claude)
5. Results/visualizations shown locally
6. User can share **aggregated results** (not raw data)

**Example Workflow:**
```python
# ✅ CORRECT: Generated script reads from local file
import pandas as pd

# This runs locally - CSV content never sent to Claude
df = pd.read_csv('[FILE_PATH]')

# Analysis happens on your machine
completion_rate = (df['status'] == 'jobCompleted').mean() * 100
print(f"Completion Rate: {completion_rate:.2f}%")

# Only aggregated results shared (no PII)
```

---

## Instructions

### 1. ANALYZE - Understand Requirements

**Questions to Ask (Internally):**
- What type of analysis? (completion rates, validation metrics, interaction patterns, comprehensive)
- What is the data structure? (job-level, summary, time-series)
- What are the key metrics? (rates, counts, distributions, correlations)
- What groupings are needed? (territory, valuer, category, date)
- Simple one-off analysis or complex repeatable pipeline?

**Determine Complexity:**
- **Simple Script** (analyze.py pattern): One-off analysis, quick insights, <200 lines
- **Modular Pipeline** (SurveyAnalyzer pattern): Multiple analysis types, reusable methods, >1000 lines

### 2. DESIGN - Choose Implementation Pattern

#### Pattern A: Complete Script (Simple Analysis)

**When to Use:**
- One-off analysis
- Quick exploratory data analysis
- Simple transformations
- Immediate results needed
- Dataset structure well-known

**Structure:**
```python
# File: analyze.py (~150-250 lines)

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def summarize_data(file_path):
    """All-in-one analysis function"""
    df = pd.read_csv(file_path)

    # Data overview
    print_data_overview(df)

    # Statistical analysis
    print_statistics(df)

    # Generate visualizations
    create_visualizations(df)

    return summary_text

# Helper functions (5-10 functions)
def print_data_overview(df): ...
def print_statistics(df): ...
def create_visualizations(df): ...

if __name__ == '__main__':
    summarize_data('data/report.csv')
```

**Advantages:**
- Fast to write and execute
- Easy to understand
- Self-contained
- Good for prototyping

**Disadvantages:**
- Not reusable across projects
- Hard to test individual components
- Difficult to extend with new features

#### Pattern B: Modular Pipeline (Complex Analysis)

**When to Use:**
- Multiple analysis types needed
- Reusable across multiple datasets
- Complex business logic
- Need to filter and aggregate in various ways
- Building a reporting library

**Structure:**
```python
# File: pipelines/analyzer.py (~1000-1500 lines)

import pandas as pd
from typing import Dict, List, Optional

class DataAnalyzer:
    """Modular data analysis pipeline with reusable methods"""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self._prepare_data()

    def _prepare_data(self):
        """Prepare data by adding computed columns"""
        self.df['category'] = self.df.apply(self._categorize, axis=1)
        self.df['status'] = self.df.apply(self._determine_status, axis=1)

    # ==========================================
    # CATEGORIZATION METHODS (Pure Functions)
    # ==========================================

    @staticmethod
    def _categorize(row) -> str:
        """Categorize row based on business rules"""
        # Business logic here
        pass

    @staticmethod
    def _determine_status(row) -> str:
        """Determine status based on completion criteria"""
        # Business logic here
        pass

    # ==========================================
    # FILTERING METHODS
    # ==========================================

    def filter_by_category(self, category: str) -> pd.DataFrame:
        """Filter data by category"""
        return self.df[self.df['category'] == category].copy()

    def filter_by_date_range(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Filter data by date range"""
        mask = (self.df['date'] >= start_date) & (self.df['date'] <= end_date)
        return self.df[mask].copy()

    # ==========================================
    # METRIC CALCULATION METHODS
    # ==========================================

    def calculate_completion_rate(self, df: Optional[pd.DataFrame] = None) -> Dict:
        """Calculate completion rate for given data"""
        if df is None:
            df = self.df

        completed = (df['status'] == 'completed').sum()
        total = len(df)
        rate = (completed / total * 100) if total > 0 else 0

        return {
            'total': total,
            'completed': completed,
            'rate': round(rate, 2)
        }

    def calculate_validation_rate(self, df: Optional[pd.DataFrame] = None) -> Dict:
        """Calculate validation rate for completed jobs"""
        if df is None:
            df = self.df

        completed_df = df[df['status'] == 'completed']
        valid = (completed_df['valid'] == True).sum()
        total = len(completed_df)
        rate = (valid / total * 100) if total > 0 else 0

        return {
            'total': total,
            'valid': valid,
            'rate': round(rate, 2)
        }

    # ==========================================
    # AGGREGATION METHODS
    # ==========================================

    def get_metrics_by_category(self) -> pd.DataFrame:
        """Get metrics grouped by category"""
        results = []
        for category in self.df['category'].unique():
            cat_df = self.filter_by_category(category)
            completion = self.calculate_completion_rate(cat_df)
            validation = self.calculate_validation_rate(cat_df)

            results.append({
                'category': category,
                'total_jobs': completion['total'],
                'completed': completion['completed'],
                'completion_rate_%': completion['rate'],
                'valid': validation['valid'],
                'validation_rate_%': validation['rate']
            })

        return pd.DataFrame(results)

    # ==========================================
    # VISUALIZATION METHODS
    # ==========================================

    def generate_completion_chart(self, output_path: str = 'completion_rates.png'):
        """Generate completion rate visualization"""
        metrics = self.get_metrics_by_category()

        plt.figure(figsize=(12, 6))
        metrics.plot(x='category', y='completion_rate_%', kind='bar')
        plt.title('Completion Rates by Category')
        plt.ylabel('Completion Rate (%)')
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.close()

    # ==========================================
    # REPORTING METHODS
    # ==========================================

    def generate_comprehensive_report(self, output_path: str = 'report.txt'):
        """Generate comprehensive text report"""
        lines = []
        lines.append('=' * 80)
        lines.append('COMPREHENSIVE DATA ANALYSIS REPORT')
        lines.append('=' * 80)

        # Overall metrics
        overall_completion = self.calculate_completion_rate()
        overall_validation = self.calculate_validation_rate()

        lines.append(f"Total Jobs: {overall_completion['total']}")
        lines.append(f"Completion Rate: {overall_completion['rate']:.2f}%")
        lines.append(f"Validation Rate: {overall_validation['rate']:.2f}%")

        # Category breakdown
        lines.append('\nMetrics by Category:')
        metrics = self.get_metrics_by_category()
        lines.append(metrics.to_string(index=False))

        report = '\n'.join(lines)
        with open(output_path, 'w') as f:
            f.write(report)

        return report

# Usage Script
# File: scripts/generate_report.py

from pipelines.analyzer import DataAnalyzer
import pandas as pd

df = pd.read_csv('[FILE_PATH]')
analyzer = DataAnalyzer(df)

# Flexible usage of reusable methods
overall_metrics = analyzer.calculate_completion_rate()
category_metrics = analyzer.get_metrics_by_category()
analyzer.generate_completion_chart()
analyzer.generate_comprehensive_report()
```

**Advantages:**
- Highly reusable across projects
- Easy to test individual methods
- Composable (mix and match methods)
- Extensible (add new methods easily)
- Maintainable (single responsibility principle)

**Disadvantages:**
- More upfront development time
- Requires OOP understanding
- Overkill for simple one-off analyses

### 3. IMPLEMENT - Generate Code

Based on user requirements and complexity, generate either:
- **Pattern A**: Complete self-contained script
- **Pattern B**: Modular pipeline class with usage script
- **Hybrid**: Start with Pattern A, refactor to Pattern B when needed

---

## Output Expected

### Pattern A Output: Complete Script

**File Structure:**
```
analyze.py                 # Main analysis script (~200 lines)
requirements.txt           # Dependencies
README.md                  # Usage instructions
```

**Example: analyze.py**
```python
"""
Comprehensive CSV Data Analysis Script

Usage:
    python analyze.py data/report.csv
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

def summarize_csv(file_path: str):
    """
    Comprehensively analyzes a CSV file and generates visualizations.

    Args:
        file_path: Path to the CSV file

    Returns:
        str: Formatted comprehensive analysis
    """
    df = pd.read_csv(file_path)
    summary = []

    # Basic info
    summary.append("=" * 60)
    summary.append("📊 DATA OVERVIEW")
    summary.append("=" * 60)
    summary.append(f"Rows: {df.shape[0]:,} | Columns: {df.shape[1]}")
    summary.append(f"\nColumns: {', '.join(df.columns.tolist())}")

    # Data types
    summary.append(f"\n📋 DATA TYPES:")
    for col, dtype in df.dtypes.items():
        summary.append(f"  • {col}: {dtype}")

    # Missing data analysis
    missing = df.isnull().sum().sum()
    missing_pct = (missing / (df.shape[0] * df.shape[1])) * 100
    summary.append(f"\n🔍 DATA QUALITY:")
    if missing:
        summary.append(f"Missing values: {missing:,} ({missing_pct:.2f}%)")
    else:
        summary.append("✓ No missing values")

    # Numeric analysis
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    if numeric_cols:
        summary.append(f"\n📈 NUMERICAL ANALYSIS:")
        summary.append(str(df[numeric_cols].describe()))

        # Correlation heatmap
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()

            plt.figure(figsize=(10, 8))
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
            plt.title('Correlation Heatmap')
            plt.tight_layout()
            plt.savefig('correlation_heatmap.png', dpi=150)
            plt.close()
            summary.append("\n✓ Generated: correlation_heatmap.png")

    # Categorical analysis
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    if categorical_cols:
        summary.append(f"\n📊 CATEGORICAL ANALYSIS:")
        for col in categorical_cols[:5]:
            value_counts = df[col].value_counts()
            summary.append(f"\n{col}:")
            for val, count in value_counts.head(5).items():
                pct = (count / len(df)) * 100
                summary.append(f"  • {val}: {count:,} ({pct:.1f}%)")

    # Time series analysis (if date column detected)
    date_cols = [c for c in df.columns if 'date' in c.lower()]
    if date_cols and numeric_cols:
        date_col = date_cols[0]
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')

        fig, axes = plt.subplots(min(3, len(numeric_cols)), 1, figsize=(12, 8))
        if len(numeric_cols) == 1:
            axes = [axes]

        for idx, num_col in enumerate(numeric_cols[:3]):
            ax = axes[idx] if len(numeric_cols) > 1 else axes[0]
            daily_data = df.groupby(date_col)[num_col].mean()
            daily_data.plot(ax=ax, linewidth=2)
            ax.set_title(f'{num_col} Over Time')
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('time_series_analysis.png', dpi=150)
        plt.close()
        summary.append("\n✓ Generated: time_series_analysis.png")

    return "\n".join(summary)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        print("Usage: python analyze.py <file_path>")
        sys.exit(1)

    print(summarize_csv(file_path))
```

### Pattern B Output: Modular Pipeline

**File Structure:**
```
pipelines/
  __init__.py              # Package init
  analyzer.py              # Main analyzer class (~1200 lines)
  utils.py                 # Utility functions
  report_builder.py        # Report formatting
scripts/
  generate_report.py       # Usage script
  quick_analysis.py        # Quick metrics script
requirements.txt
README.md
```

**Example: pipelines/analyzer.py** (abbreviated - see SurveyAnalyzer pattern above for full implementation)

**Example: scripts/generate_report.py**
```python
"""
Generate Comprehensive Report using DataAnalyzer Pipeline

Usage:
    python scripts/generate_report.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipelines.analyzer import DataAnalyzer
import pandas as pd

def generate_report(file_path: str):
    # Load data
    df = pd.read_csv(file_path)
    analyzer = DataAnalyzer(df)

    # Get overall metrics
    overall = analyzer.calculate_completion_rate()
    print(f"Completion Rate: {overall['rate']:.2f}%")

    # Get metrics by category
    category_metrics = analyzer.get_metrics_by_category()
    print("\nCategory Breakdown:")
    print(category_metrics.to_string(index=False))

    # Generate visualizations
    analyzer.generate_completion_chart('completion_rates.png')

    # Generate comprehensive report
    analyzer.generate_comprehensive_report('report.txt')
    print("\n✓ Report generated: report.txt")

if __name__ == '__main__':
    generate_report('[FILE_PATH]')
```

---

## Apprise-Specific Analysis Patterns

### Pattern 1: Valuation Completion Analysis

**Business Context:**
- Analyze valuation job completion rates
- Group by territory, valuer, job type
- Calculate validation rates
- Identify bottlenecks

**Key Metrics:**
```python
def calculate_valuation_metrics(df):
    metrics = {
        'completion_rate': (df['status'] == 'jobCompleted').mean() * 100,
        'validation_rate': (df['valid'] == True).mean() * 100,
        'median_tat': df['lenderTaT'].median(),
        'escalation_rate': (df['escalation'] != '').mean() * 100
    }
    return metrics
```

**Grouping Dimensions:**
- Territory: NSW/ACT, QLD, VIC/TAS, SA/NT, WA
- Valuer: Individual valuer performance
- Job Type: Refinance vs Purchase
- Date Range: Daily, weekly, monthly trends

### Pattern 2: Survey Response Analysis

**Business Context:**
- Analyze survey response rates
- Track interaction sequences (initial → open → noContact)
- Measure completion by survey type (Questions, Images, Q&I)
- Identify optimal contact strategies

**Key Metrics:**
```python
def calculate_survey_metrics(df):
    metrics = {
        'response_rate': (df['total_complete'] > 0).mean() * 100,
        'full_response_rate': (df['response_status'] == 'Full Response').mean() * 100,
        'questions_completion': (df['standardQuestions_completed'] == 1).mean() * 100,
        'images_completion': (df['standardImages_completed'] == 1).mean() * 100
    }
    return metrics
```

**Interaction Sequence Analysis:**
```python
def categorize_interaction_sequence(sequence: str) -> str:
    """
    Categorize interaction sequences into meaningful groups.

    Examples:
      'initial' → 'Spoke then sent'
      'noContact -> initial' → 'Spoke then sent'
      'open -> initial' → 'Over the phone then sent'
      'noContact' → 'No contact'
      'open' → 'Over the phone'
    """
    if pd.isna(sequence) or sequence == '':
        return 'No interactions'

    if sequence == 'initial':
        return 'Spoke then sent'
    elif sequence == 'noContact -> initial':
        return 'Spoke then sent'
    elif 'open' in sequence and sequence.endswith('initial'):
        return 'Over the phone then sent'
    elif sequence == 'noContact':
        return 'No contact'
    elif sequence.endswith('open'):
        return 'Over the phone'
    else:
        return 'Other'
```

### Pattern 3: Operational Dashboard Data

**Business Context:**
- Prepare data for Power BI / Tableau dashboards
- Aggregate daily metrics
- Calculate rolling averages
- Flag anomalies

**Key Aggregations:**
```python
def prepare_dashboard_data(df):
    # Daily aggregations
    daily_metrics = df.groupby('date').agg({
        'jobNumber': 'count',  # Total jobs
        'status': lambda x: (x == 'jobCompleted').sum(),  # Completed
        'valid': lambda x: x.sum(),  # Valid
        'lenderTaT': 'median'  # Median TAT
    }).reset_index()

    daily_metrics.columns = ['date', 'total_jobs', 'completed_jobs',
                             'valid_jobs', 'median_tat']

    # Calculate rates
    daily_metrics['completion_rate'] = (
        daily_metrics['completed_jobs'] / daily_metrics['total_jobs'] * 100
    )
    daily_metrics['validation_rate'] = (
        daily_metrics['valid_jobs'] / daily_metrics['completed_jobs'] * 100
    )

    # Rolling 7-day average
    daily_metrics['completion_rate_7d_avg'] = (
        daily_metrics['completion_rate'].rolling(7).mean()
    )

    return daily_metrics
```

---

## Synthetic Data Generation

To test analysis code without exposing real data, generate synthetic datasets:

```python
from faker import Faker
import pandas as pd
import random

fake = Faker('en_AU')  # Australian locale

def generate_synthetic_valuation_data(n_rows: int = 1000) -> pd.DataFrame:
    """
    Generate synthetic valuation data for testing.
    Mimics real Apprise valuation exports.
    """
    territories = ['Apprise NSW / ACT', 'Apprise QLD', 'Apprise VIC / TAS',
                   'Apprise SA / NT', 'Apprise WA']
    job_types = ['Refinance', 'Purchase']
    statuses = ['Valuation Completed', 'Canceled', 'In Progress']
    escalation_reasons = ['', 'Under construction', 'Dual occupancy',
                         'Inadequate information on subject property']

    data = []
    for i in range(n_rows):
        job_number = f'00{295000 + i:06d}'
        valuer = fake.name()
        territory = random.choice(territories)
        job_type = random.choice(job_types)
        status = random.choices(statuses, weights=[0.8, 0.1, 0.1])[0]

        # Realistic property address (Sydney, Melbourne, Brisbane suburbs)
        address = fake.street_address() + ', ' + fake.city() + ', ' + \
                  random.choice(['NSW', 'VIC', 'QLD', 'SA', 'WA']) + ' ' + \
                  str(fake.random_int(2000, 6999))

        # Market value ceiling
        market_value = fake.random_int(50000, 2000000)
        deal_value = market_value + fake.random_int(-100000, 200000)

        # Dates
        date_opened = fake.date_time_between(start_date='-90d', end_date='now')
        date_closed = date_opened + pd.Timedelta(days=random.randint(1, 14))

        # TAT (Turnaround Time) in hours
        lender_tat = (date_closed - date_opened).total_seconds() / 3600

        # Validation (80% valid for completed jobs)
        valid = random.random() < 0.8 if status == 'Valuation Completed' else None

        # Escalation (10% of jobs)
        escalation_reason = random.choice(escalation_reasons) \
            if random.random() < 0.1 else ''

        data.append({
            'jobNumber': job_number,
            'valuer': valuer,
            'territory': territory,
            'jobType': job_type,
            'status': status,
            'address': address,
            'marketValueCeiling': market_value,
            'dealValue': deal_value,
            'dateOpened': date_opened,
            'dateClosed': date_closed if status == 'Valuation Completed' else None,
            'lenderTaT': lender_tat if status == 'Valuation Completed' else None,
            'valid': valid,
            'escalationReason': escalation_reason
        })

    return pd.DataFrame(data)


def generate_synthetic_survey_data(n_rows: int = 500) -> pd.DataFrame:
    """
    Generate synthetic survey response data for testing.
    Mimics real Apprise survey exports.
    """
    survey_types = ['Questions Only', 'Questions & Images', 'Images Only', 'None']
    response_statuses = ['complete', 'questions only', 'incomplete']

    data = []
    for i in range(n_rows):
        job_number = f'00{295000 + i:06d}'
        valuer = fake.name()

        # Survey requirements
        surveys_req_qtn_img = random.choice([0, 1, 2])
        surveys_req_std_img = random.choice([0, 1, 2])
        surveys_req_std_qtn = random.choice([0, 1, 2])

        # Completion (70% completion rate)
        completed = random.random() < 0.7
        qtn_img_completed = 1 if completed and surveys_req_qtn_img > 0 else 0
        std_img_completed = 1 if completed and surveys_req_std_img > 0 else 0
        std_qtn_completed = 1 if completed and surveys_req_std_qtn > 0 else 0

        total_complete = qtn_img_completed + std_img_completed + std_qtn_completed

        # Status
        status = 'jobCompleted' if completed else random.choice(['', 'inProgress'])

        # Validation (85% valid for completed)
        valid = random.random() < 0.85 if status == 'jobCompleted' else False

        # Interaction sequence
        interaction_types = ['initial', 'open', 'noContact']
        num_interactions = random.randint(0, 3)
        type_sent_1 = f"1:{random.choice(interaction_types)}:1:standardQuestions" \
            if num_interactions > 0 else ''
        type_sent_2 = f"2:{random.choice(interaction_types)}:2:standardImages" \
            if num_interactions > 1 else ''

        data.append({
            'jobNumber': job_number,
            'valuer': valuer,
            'status': status,
            'valid': 'true' if valid else 'false',
            'surveysReq_QtnImg': surveys_req_qtn_img,
            'surveysReq_StdImg': surveys_req_std_img,
            'surveysReq_StdQtn': surveys_req_std_qtn,
            'QtnImg_completed': qtn_img_completed,
            'standardImages_completed': std_img_completed,
            'standardQuestions_completed': std_qtn_completed,
            'total_complete': total_complete,
            'type_sent_1': type_sent_1,
            'type_sent_2': type_sent_2
        })

    return pd.DataFrame(data)


# Usage
if __name__ == '__main__':
    # Generate test data
    valuation_df = generate_synthetic_valuation_data(1000)
    valuation_df.to_csv('data/synthetic_valuation_data.csv', index=False)
    print("✓ Generated synthetic_valuation_data.csv")

    survey_df = generate_synthetic_survey_data(500)
    survey_df.to_csv('data/synthetic_survey_data.csv', index=False)
    print("✓ Generated synthetic_survey_data.csv")
```

---

## Data Masking for Results Sharing

If you need to share analysis results externally, mask sensitive fields:

```python
def mask_sensitive_fields(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mask sensitive fields for external sharing.
    """
    df_masked = df.copy()

    # Mask addresses (keep suburb only)
    if 'address' in df_masked.columns:
        df_masked['address'] = df_masked['address'].apply(
            lambda x: ', '.join(x.split(',')[-2:]) if pd.notna(x) else ''
        )

    # Mask valuer names
    if 'valuer' in df_masked.columns:
        df_masked['valuer'] = 'Valuer ' + (df_masked.groupby('valuer').ngroup() + 1).astype(str)

    # Mask job numbers (keep last 3 digits)
    if 'jobNumber' in df_masked.columns:
        df_masked['jobNumber'] = 'XXX-' + df_masked['jobNumber'].astype(str).str[-3:]

    return df_masked


# Usage
masked_results = mask_sensitive_fields(df)
masked_results.to_csv('results_masked.csv', index=False)
```

---

## Common Analysis Recipes

### Recipe 1: Completion Rate by Territory

```python
territory_metrics = df.groupby('territory').agg({
    'jobNumber': 'count',
    'status': lambda x: (x == 'Valuation Completed').sum()
}).reset_index()

territory_metrics['completion_rate'] = (
    territory_metrics['status'] / territory_metrics['jobNumber'] * 100
)

print(territory_metrics.to_string(index=False))
```

### Recipe 2: Validation Rate by Valuer

```python
completed_jobs = df[df['status'] == 'Valuation Completed']

valuer_metrics = completed_jobs.groupby('valuer').agg({
    'jobNumber': 'count',
    'valid': 'sum'
}).reset_index()

valuer_metrics['validation_rate'] = (
    valuer_metrics['valid'] / valuer_metrics['jobNumber'] * 100
)

# Sort by validation rate
valuer_metrics = valuer_metrics.sort_values('validation_rate', ascending=False)
print(valuer_metrics.to_string(index=False))
```

### Recipe 3: TAT (Turnaround Time) Distribution

```python
completed_jobs = df[df['status'] == 'Valuation Completed']

plt.figure(figsize=(12, 6))
plt.hist(completed_jobs['lenderTaT'], bins=50, edgecolor='black')
plt.xlabel('Turnaround Time (hours)')
plt.ylabel('Frequency')
plt.title('Distribution of Turnaround Times')
plt.axvline(completed_jobs['lenderTaT'].median(), color='red',
            linestyle='--', label=f"Median: {completed_jobs['lenderTaT'].median():.1f}h")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('tat_distribution.png', dpi=150)
```

### Recipe 4: Time Series - Daily Completions

```python
df['dateOpened'] = pd.to_datetime(df['dateOpened'])

daily_completions = df.groupby(df['dateOpened'].dt.date).agg({
    'jobNumber': 'count',
    'status': lambda x: (x == 'Valuation Completed').sum()
}).reset_index()

daily_completions['completion_rate'] = (
    daily_completions['status'] / daily_completions['jobNumber'] * 100
)

plt.figure(figsize=(14, 6))
plt.plot(daily_completions['dateOpened'], daily_completions['completion_rate'],
         marker='o', linewidth=2)
plt.xlabel('Date')
plt.ylabel('Completion Rate (%)')
plt.title('Daily Completion Rate Trend')
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('daily_completion_trend.png', dpi=150)
```

---

## Testing Your Analysis Code

```python
import pytest
import pandas as pd

def test_completion_rate_calculation():
    # Create test data
    test_df = pd.DataFrame({
        'status': ['jobCompleted', 'jobCompleted', 'inProgress', 'jobCompleted']
    })

    completion_rate = (test_df['status'] == 'jobCompleted').mean() * 100
    assert completion_rate == 75.0

def test_synthetic_data_generation():
    df = generate_synthetic_valuation_data(100)
    assert len(df) == 100
    assert 'jobNumber' in df.columns
    assert 'territory' in df.columns
    assert df['marketValueCeiling'].min() >= 50000
    assert df['marketValueCeiling'].max() <= 2000000

def test_data_masking():
    test_df = pd.DataFrame({
        'jobNumber': ['00295677', '00295678'],
        'address': ['29 Little Road, BANKSTOWN, NSW 2200',
                   '6 HONEYEATER Court, THORNLANDS, QLD 4164'],
        'valuer': ['John Smith', 'Jane Doe']
    })

    masked = mask_sensitive_fields(test_df)
    assert 'XXX-677' in masked['jobNumber'].values
    assert 'Little Road' not in masked['address'].values[0]
```

---

## Requirements

**requirements.txt**:
```
pandas>=2.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
faker>=19.0.0  # For synthetic data generation
pytest>=7.4.0  # For testing
```

**Installation**:
```bash
pip install -r requirements.txt
```

---

## Quick Start Examples

### Example 1: Simple One-Off Analysis

```bash
# User provides file path (not contents)
python analyze.py data/valuation_export_oct2025.csv
```

### Example 2: Comprehensive Report with Modular Pipeline

```python
from pipelines.analyzer import DataAnalyzer
import pandas as pd

# Load data locally (never sent to Claude)
df = pd.read_csv('data/valuation_export_oct2025.csv')

# Create analyzer
analyzer = DataAnalyzer(df)

# Get metrics by territory
territory_metrics = analyzer.get_metrics_by_category()  # Custom method
print(territory_metrics)

# Generate visualizations
analyzer.generate_completion_chart('territory_completion.png')

# Generate comprehensive report
analyzer.generate_comprehensive_report('report_oct2025.txt')
```

### Example 3: Survey Response Analysis

```python
from pipelines.survey_analyzer import SurveyAnalyzer
import pandas as pd

df = pd.read_csv('data/survey_responses_oct2025.csv')
analyzer = SurveyAnalyzer(df)

# Analyze interaction sequences
sequences = analyzer.get_interaction_sequences(max_interactions=8, include_metrics=True)
print(sequences.head(10))

# Group sequences into categories
grouped = analyzer.get_interaction_sequence_groups(sequences, include_samples=True)
print(grouped)
```

---

## Remember

- ⚠️ **Provide file paths, NOT CSV contents** to avoid sensitive data injection
- ✅ **Generate synthetic data** for testing and examples
- ✅ **Mask sensitive fields** before sharing results externally
- ✅ **Choose the right pattern**: Simple script for quick analysis, modular pipeline for complex/reusable workflows
- ✅ **Follow Apprise patterns**: Based on real production code (survey/csv-analyser projects)
- ✅ **Delete chat history** after session to prevent data retention

