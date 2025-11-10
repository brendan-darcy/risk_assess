# Quick Start Guide: Using Apprise Workflow Templates

**TL;DR**: Run security check → Use template → Generate code → Delete chat history

---

## The 4-Step Process

### ⚠️ Step 1: Run Pre-Flight Check (Every Session)

```bash
cd /your/project
./path/to/pre-flight-check.sh
```

**What it checks:**
- ✅ .claudeignore configured
- ✅ Not on main/master branch
- ✅ No sensitive files exposed
- ✅ Environment indicators

**Only proceed if you see:**
```
✅ PRE-FLIGHT CHECK PASSED
Safe to use Claude Code. Happy coding! 🚀
```

---

### 📖 Step 2: Choose Your Template

**For analyzing CSVs (valuation reports, survey data):**
→ Use [workflows/data_analyst_csv.md](workflows/data_analyst_csv.md)

**For building Databricks ETL pipelines:**
→ Use [workflows/data_engineer_etl.md](workflows/data_engineer_etl.md)

**For creating AWS Lambda APIs:**
→ Use [workflows/data_services_api.md](workflows/data_services_api.md)

**For security tasks (masking, validation, review):**
→ Use [security/](security/) folder templates

---

### 💬 Step 3: Prompt Claude Code

**Template format:**
```
Using [template_name], [your specific task].

[Additional requirements, context, specifications]
```

**Example prompts:**

**Data Analysis:**
```
Using data_analyst_csv.md template, analyze data/valuation_export_oct2025.csv.

Calculate completion rates by territory and valuer.
Generate visualizations for completion trends and territory comparison.
Use the modular pipeline pattern (SurveyAnalyzer style) for reusability.
```

**ETL Pipeline:**
```
Using data_engineer_etl.md template, create a Databricks pipeline.

Source: s3://apprise-raw-data/valuations/
Layers: Bronze → Silver → Gold
Transformations:
  - Bronze: Ingest with schema enforcement
  - Silver: Deduplicate, standardize, DQ checks (not null, range)
  - Gold: Daily metrics by territory (completion rate, validation rate, TAT)
```

**Lambda API:**
```
Using data_services_api.md template, create a Lambda API.

Endpoints:
  GET /valuations/metrics/daily?start_date=2025-01-01
  GET /valuations/metrics/territory?territory=NSW_ACT

Data source: s3://apprise-gold-data/gold/valuation_metrics_daily
Query engine: DuckDB
Include: Input validation, error handling, JSON responses
```

**Security:**
```
Using security/input_validation.md template, create validation functions.

Fields: property_address, valuation_amount, borrower_phone, borrower_email
Languages: APEX (server-side) + TypeScript (client-side)
Include: Type validation, format validation, business rules, unit tests
```

---

### 🗑️ Step 4: Delete Chat History

**After your session:**

1. In Claude Code, click **Settings** (gear icon)
2. Go to **Chat History**
3. **Delete** your session
4. Confirm deletion

**Why?** Prevents sensitive data from being retained in chat logs.

---

## Key Rules

### ✅ DO

- ✅ **Run pre-flight check** before every session
- ✅ **Provide file paths only** (not CSV contents)
  ```
  ✅ "Analyze data/valuation_export.csv"
  ❌ "Analyze this: jobNumber,address,amount,..."
  ```
- ✅ **Use synthetic data** for testing/examples
- ✅ **Work in dev/feature branches** (not main)
- ✅ **Delete chat history** after every session
- ✅ **Reference templates explicitly** in prompts

### ❌ DON'T

- ❌ **Don't paste CSV contents** into prompts (exposes PII)
- ❌ **Don't use on main/master branch**
- ❌ **Don't use with production data**
- ❌ **Don't skip pre-flight check**
- ❌ **Don't forget to delete chat history**

---

## Templates Overview

### Workflows (3 templates)

| Template | Use For | Output | Lines |
|----------|---------|--------|-------|
| [data_analyst_csv.md](workflows/data_analyst_csv.md) | Analyze valuation/survey CSVs | Pandas scripts or modular pipelines | 900 |
| [data_engineer_etl.md](workflows/data_engineer_etl.md) | Databricks ETL (Bronze→Silver→Gold) | PySpark notebooks | 900 |
| [data_services_api.md](workflows/data_services_api.md) | Lambda APIs with DuckDB | Lambda handler + query builder | 800 |

### Security (4 templates)

| Template | Use For | Output |
|----------|---------|--------|
| [data_masking.md](security/data_masking.md) | Mask PII in dev/UAT environments | Python masking script |
| [secrets_detection.md](security/secrets_detection.md) | Detect hardcoded credentials | Detection script + pre-commit hook |
| [input_validation.md](security/input_validation.md) | Prevent injection attacks | Validation functions (APEX/TypeScript/Python) |
| [security_review.md](security/security_review.md) | Comprehensive code security review | Security report with findings |

---

## Pattern Selection

Templates offer **two implementation patterns**:

### Simple Script (200 lines)
**When:**
- One-off analysis
- Quick tasks
- Simple transformations

**Example:** `analyze.py` - self-contained pandas script

### Modular Pipeline (1000+ lines)
**When:**
- Multiple analysis types
- Reusable code
- Complex business logic

**Example:** `SurveyAnalyzer` class with 30+ methods

**Claude Code decides automatically** based on your requirements.

---

## Data Safety

### ⚠️ CRITICAL: File Paths Only

**CORRECT:**
```
User: "Analyze data/valuation_export_oct2025.csv"
         ↓
Claude: Generates analysis script
         ↓
User: Runs script locally (CSV never sent to Claude)
         ↓
Results: Shown locally
```

**INCORRECT:**
```
User: "Analyze this CSV:
       jobNumber,address,borrower_name,valuation_amount
       00295677,29 Little Road BANKSTOWN,John Smith,$1400000
       ..."
         ↓
❌ PII EXPOSED TO CLAUDE!
```

### Synthetic Data for Testing

All templates include synthetic data generators:

```python
from faker import Faker
fake = Faker('en_AU')  # Australian locale

# Generate 1000 fake valuation records
df_synthetic = generate_synthetic_valuation_data(1000)
df_synthetic.to_csv('data/synthetic_valuations.csv', index=False)

# Now safe to test with
```

---

## Example Session

```bash
# 1. Navigate to project
cd ~/projects/valuation-analysis

# 2. Run pre-flight check
./templates/pt-team/pre-flight-check.sh
# ✅ PRE-FLIGHT CHECK PASSED

# 3. Open template for reference
code templates/pt-team/workflows/data_analyst_csv.md

# 4. Prompt Claude Code
# "Using data_analyst_csv.md template, analyze data/synthetic_valuations.csv..."

# 5. Claude generates code
# You get: pipelines/analyzer.py with 30+ reusable methods

# 6. Run locally
python scripts/generate_report.py

# 7. Review results (no PII exposed)

# 8. Delete Claude Code chat history
# Settings → Chat History → Delete
```

---

## Troubleshooting

### Pre-Flight Check Failed?

**Issue:** `.claudeignore not found`
```bash
cp templates/pt-team/.claudeignore.template .claudeignore
```

**Issue:** `On main branch`
```bash
git checkout -b dev/claude-code-session
```

**Issue:** `CSV files found`
- Verify they're dummy/synthetic data
- If real data: delete or add to .claudeignore

### Template Not Working?

**Issue:** Claude doesn't follow template
- Reference template explicitly: "Using data_analyst_csv.md template..."
- Provide specific requirements
- Specify pattern: "Use modular pipeline pattern"

**Issue:** Generated code has errors
- Verify Python/PySpark version compatibility
- Check dependencies installed
- Run tests on synthetic data first

---

## Getting Help

**Documentation:**
- [PRE_FLIGHT_USAGE.md](PRE_FLIGHT_USAGE.md) - Detailed pre-flight check guide
- [STRUCTURE.md](STRUCTURE.md) - Folder structure explanation
- [workflows/README.md](workflows/README.md) - Comprehensive workflow template guide
- [planning/phase_0.5_completion_report.md](../planning/phase_0.5_completion_report.md) - Full implementation details

**Real Project Examples:**
- `docs - project examples/survey/` - Survey analyzer pattern (modular pipeline)
- `docs - project examples/csv-analyser/` - CSV analyzer pattern (simple script)

**Issues?**
- Check pre-flight script output
- Review template security checklist
- Consult P&T Team Lead
- File issue in planning docs

---

## Remember

🔒 **Security is YOUR responsibility**

The templates and pre-flight script help, but you must:
- Verify data is dummy/synthetic
- Work in correct environment
- Delete chat history after sessions
- Follow Apprise security policies

**When in doubt, DON'T use Claude Code with the data.**

---

## Next Steps

1. **Run pre-flight check** in your project
2. **Generate synthetic data** for testing
3. **Try a simple template** (e.g., data_analyst_csv.md)
4. **Review generated code** before running
5. **Provide feedback** on what works/doesn't work

**Ready to start? Run `./pre-flight-check.sh` now!** 🚀

