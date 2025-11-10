# Template Folder Structure

## Current Structure (Phase 0.5, 1, 2, 3 Complete)

```
templates/pt-team/
├── README.md                       # Main template library guide
├── STRUCTURE.md                    # This file
├── QUICK_START.md                  # 4-step quick start guide
├── PRE_FLIGHT_USAGE.md             # Pre-flight script usage guide
├── .claudeignore.template          # Security ignore patterns
├── _security_checklist.md          # Pre-flight security verification
├── pre-flight-check.sh             # Automated security checks (executable)
│
├── workflows/                      # ✅ PHASE 0.5: DATA WORKFLOWS (3 templates, 2,600 lines)
│   ├── README.md                   # Comprehensive usage guide (700 lines)
│   ├── data_analyst_csv.md         # Analyze CSVs (pandas, 900 lines)
│   ├── data_engineer_etl.md        # Databricks ETL (PySpark, 900 lines)
│   └── data_services_api.md        # Lambda APIs (DuckDB, 800 lines)
│
├── security/                       # ✅ PHASE 1: SECURITY TEMPLATES (4 templates)
│   ├── data_masking.md             # Mask sensitive data
│   ├── secrets_detection.md        # Detect hardcoded credentials
│   ├── input_validation.md         # Prevent injection attacks
│   ├── security_review.md          # Comprehensive code review
│   └── _security_templates_testing.md  # Test report
│
├── core-workflows/                 # ✅ PHASE 2: CORE DEVELOPMENT WORKFLOWS (4 templates, 2,668 lines)
│   ├── secure_feature_development.md   # Build features with security & testing (724 lines)
│   ├── bug_fix_workflow.md             # Structured debugging & regression tests (627 lines)
│   ├── code_review_request.md          # Request Claude to review code (666 lines)
│   └── refactoring_workflow.md         # Technical debt reduction (651 lines)
│
├── language-specific/              # ✅ PHASE 3: PLATFORM-SPECIFIC TEMPLATES (5 templates, 4,001 lines)
│   ├── apex_development.md         # APEX triggers, batch, secure coding (860 lines)
│   ├── lwc_component.md            # Lightning Web Components (815 lines)
│   ├── nodejs_lambda.md            # AWS Lambda functions (802 lines)
│   ├── databricks_notebook.md      # Python/SQL notebooks (813 lines)
│   └── r_analysis.md               # R/POSIT statistical analysis (711 lines)
│
├── planning/                       # Planning and reporting documents
│   ├── pt_templates_plan.md        # Master plan (updated)
│   └── phase_0.5_completion_report.md
│
└── _extracted_archive/             # ❌ OLD PHASE 0 (archived, ignore)
    ├── _extracted/                 # Old awesome-prompts extracts
    ├── data-engineering/           # Old thin personas
    ├── _extraction_results.md
    └── _template_validation_and_usage.md
```

---

## What to Use

### For Data Workflows
- **CSV Analysis** → [workflows/data_analyst_csv.md](workflows/data_analyst_csv.md)
- **Databricks ETL** → [workflows/data_engineer_etl.md](workflows/data_engineer_etl.md)
- **Lambda APIs** → [workflows/data_services_api.md](workflows/data_services_api.md)

### For Daily Development
- **New Features** → [core-workflows/secure_feature_development.md](core-workflows/secure_feature_development.md)
- **Bug Fixes** → [core-workflows/bug_fix_workflow.md](core-workflows/bug_fix_workflow.md)
- **Code Review** → [core-workflows/code_review_request.md](core-workflows/code_review_request.md)
- **Refactoring** → [core-workflows/refactoring_workflow.md](core-workflows/refactoring_workflow.md)

### For Platform-Specific Development
- **Salesforce APEX** → [language-specific/apex_development.md](language-specific/apex_development.md)
- **Salesforce LWC** → [language-specific/lwc_component.md](language-specific/lwc_component.md)
- **AWS Lambda (Node.js)** → [language-specific/nodejs_lambda.md](language-specific/nodejs_lambda.md)
- **Databricks Notebooks** → [language-specific/databricks_notebook.md](language-specific/databricks_notebook.md)
- **R Analysis** → [language-specific/r_analysis.md](language-specific/r_analysis.md)

### For Security Tasks
- **All Security** → [security/](security/) folder (4 templates)
- **Pre-Flight** → Run `./pre-flight-check.sh` before any Claude Code session

---

## Ignore

❌ **_extracted_archive/** - Old Phase 0 templates that were replaced with Phase 0.5

---

## Summary

**4 folders with 16 production-ready templates** (9,269 lines total):
1. **workflows/** (Phase 0.5) - 3 data workflow templates
2. **security/** (Phase 1) - 4 security templates + pre-flight script
3. **core-workflows/** (Phase 2) - 4 core development templates
4. **language-specific/** (Phase 3) - 5 platform-specific templates

**Phase 4 Pending**: Testing, Documentation, and Deployment templates (planned)

Everything else is supporting documentation or archived.
