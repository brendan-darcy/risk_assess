# P&T Team Claude Code Templates Library

**For**: Apprise Risk Solutions Product & Technology Team
**Purpose**: Best-practice templates for secure, compliant development with Claude Code
**Version**: 1.0
**Last Updated**: October 2025

---

## Overview

This library provides production-ready Claude Code templates designed specifically for Apprise's P&T team. Each template embeds:
- **Security controls** (OWASP, ISO 27001:2022 compliance)
- **SSDF framework** alignment (NIST-based secure development)
- **ARMATech principles** (Security, Cloud First, WFH, Distributed Computing, API Integration, Modern)
- **Testing requirements** (coverage targets, test scenarios)
- **Apprise-specific standards** (language conventions, ISMS policies)

---

## Quick Start

### 1. Security Setup (MANDATORY FIRST STEP)

Before using any template:

1. **Review the Security Checklist**: Read [`_security_checklist.md`](./_security_checklist.md)
2. **Create .claudeignore**: Copy [`.claudeignore.template`](./.claudeignore.template) to your project root as `.claudeignore`
3. **Verify Environment**: Ensure you're working in Dev/Sandbox (NOT Production)
4. **Use Dummy Data Only**: Never use real client data with Claude Code

### 2. Using a Template

1. **Select Template**: Browse folders below or use the Template Index
2. **Open in Editor**: Open the `.md` file in VS Code
3. **Copy Content**: Copy the template content
4. **Paste into Claude Code**: Paste into Claude Code chat
5. **Fill Placeholders**: Replace `[PLACEHOLDER_NAME]` with your specific values
6. **Generate Code**: Claude will produce code following Apprise standards
7. **Review & Test**: Always review generated code, run tests, verify security
8. **Delete Chat History**: After session, delete chat history per Apprise AI policy

---

## Template Index

**Legend**: ✅ Complete | 🔲 Pending (Phase 4)

### Workflows (Phase 0.5) ✅
**Use for data engineering workflows**

| Template | Purpose | Lines | Status |
|----------|---------|-------|--------|
| [`workflows/data_analyst_csv.md`](workflows/data_analyst_csv.md) | Analyze CSVs (valuation reports, surveys) | 900 | ✅ |
| [`workflows/data_engineer_etl.md`](workflows/data_engineer_etl.md) | Databricks ETL (Bronze → Silver → Gold) | 900 | ✅ |
| [`workflows/data_services_api.md`](workflows/data_services_api.md) | AWS Lambda APIs with DuckDB | 800 | ✅ |

### Core Workflows (Phase 2) ✅
**Use these for daily development tasks**

| Template | Purpose | SSDF | Languages | Lines | Status |
|----------|---------|------|-----------|-------|--------|
| [`core-workflows/secure_feature_development.md`](core-workflows/secure_feature_development.md) | Build new features with security & testing | PW | All | 724 | ✅ |
| [`core-workflows/bug_fix_workflow.md`](core-workflows/bug_fix_workflow.md) | Structured debugging & regression tests | PW, RV | All | 627 | ✅ |
| [`core-workflows/refactoring_workflow.md`](core-workflows/refactoring_workflow.md) | Technical debt reduction | PW | All | 651 | ✅ |
| [`core-workflows/code_review_request.md`](core-workflows/code_review_request.md) | Request Claude to review code | PW, RV | All | 666 | ✅ |

### Language-Specific (Phase 3) ✅
**Use for platform-specific development**

| Template | Purpose | Coverage Target | Lines | Status |
|----------|---------|----------------|-------|--------|
| [`language-specific/apex_development.md`](language-specific/apex_development.md) | APEX triggers, batch, secure coding | 75% | 860 | ✅ |
| [`language-specific/lwc_component.md`](language-specific/lwc_component.md) | Lightning Web Components with tests | 80% | 815 | ✅ |
| [`language-specific/nodejs_lambda.md`](language-specific/nodejs_lambda.md) | AWS Lambda functions | 80% | 802 | ✅ |
| [`language-specific/databricks_notebook.md`](language-specific/databricks_notebook.md) | Python/SQL notebooks | 70% | 813 | ✅ |
| [`language-specific/r_analysis.md`](language-specific/r_analysis.md) | R/POSIT statistical analysis | 70% | 711 | ✅ |

### Security (Phase 1) ✅
**Use for security-focused tasks**

| Template | Purpose | SSDF | Lines | Status |
|----------|---------|------|-------|--------|
| [`security/security_review.md`](security/security_review.md) | OWASP vulnerability scanning | RV | - | ✅ |
| [`security/secrets_detection.md`](security/secrets_detection.md) | Find hardcoded credentials | PS, RV | - | ✅ |
| [`security/input_validation.md`](security/input_validation.md) | Injection prevention | PW | - | ✅ |
| [`security/data_masking.md`](security/data_masking.md) | Mask sensitive data for dev/UAT | PS | - | ✅ |

**Pre-Flight Automation**: [`pre-flight-check.sh`](pre-flight-check.sh) - Automated security checks before Claude Code sessions ✅

### Testing (Phase 4) 🔲
**Coming Soon - Use to generate comprehensive tests**

| Template | Purpose | Test Type | Status |
|----------|---------|-----------|--------|
| `testing/apex_test_generation.md` | APEX test classes | Unit (75% coverage) | 🔲 Pending |
| `testing/lwc_jest_tests.md` | Jest tests for LWC | Unit (80% coverage) | 🔲 Pending |
| `testing/integration_tests.md` | SIT testing | Integration | 🔲 Pending |
| `testing/performance_tests.md` | Load & stress testing | Performance | 🔲 Pending |

### Documentation (Phase 4) 🔲
**Coming Soon - Use to generate technical documentation**

| Template | Purpose | Output | Status |
|----------|---------|--------|--------|
| `documentation/technical_design_card.md` | Design docs per Handbook 2.2 | Jira-compatible | 🔲 Pending |
| `documentation/api_documentation.md` | API documentation | OpenAPI/Swagger | 🔲 Pending |
| `documentation/adr_generator.md` | Architecture Decision Records | Markdown ADR | 🔲 Pending |
| `documentation/release_notes.md` | User-friendly release notes | CAB-ready | 🔲 Pending |

### Deployment (Phase 4) 🔲
**Coming Soon - Use for deployment preparation**

| Template | Purpose | Use Case | Status |
|----------|---------|----------|--------|
| `deployment/pre_deployment_checklist.md` | CAB requirements | All deployments | 🔲 Pending |
| `deployment/environment_setup.md` | Config & secrets management | New environments | 🔲 Pending |
| `deployment/cicd_pipeline.md` | GitHub Actions workflows | CI/CD automation | 🔲 Pending |

**Implementation Status**:
- **Phase 0.5 Complete** ✅: 3 workflow templates (2,600 lines)
- **Phase 1 Complete** ✅: 4 security templates + pre-flight automation
- **Phase 2 Complete** ✅: 4 core workflow templates (2,668 lines)
- **Phase 3 Complete** ✅: 5 language-specific templates (4,001 lines)
- **Phase 4 Pending** 🔲: Testing, Documentation, Deployment templates (planned)

---

## Security Best Practices

### Pre-Session Checklist
✅ `.claudeignore` exists in project root
✅ Working in Dev/Sandbox environment
✅ Using dummy data only (no client PII)
✅ Reviewed [`_security_checklist.md`](./_security_checklist.md)

### During Development
✅ Never share actual API keys, credentials, or tokens with Claude
✅ Use placeholders like `[API_KEY]` and reference environment variables
✅ Validate all generated code for security vulnerabilities
✅ Run tests with dummy data before deployment

### Post-Session
✅ Delete Claude Code chat history (Settings → Chat History)
✅ Review any files created for accidental sensitive data inclusion
✅ Verify `.claudeignore` prevented sensitive file exposure

---

## Template Structure

Every template follows this standard format:

```markdown
# Skills: [tags]
# SSDF Practice Group: [PO|PS|PW|RV]
# ARMATech Principles: [principles]
# Language: [language]
# Context: Apprise Risk Solutions P&T Team

## Security Checklist
[Pre-flight security checks]

## Placeholders
[List of placeholders with descriptions]

## Task Description
[What this template does]

## Instructions
1. PLAN — [Analysis & approach]
2. BUILD — [Implementation with security]
3. EXPLAIN — [Documentation]

## Output Expected
[Specific deliverables with filenames]

## Example Usage
[Concrete example with filled placeholders]
```

---

## Placeholder Conventions

All templates use consistent placeholder naming:

| Placeholder | Example | Description |
|-------------|---------|-------------|
| `[PROJECT_NAME]` | "ARMATech Valuation Platform" | Apprise project identifier |
| `[COMPONENT_NAME]` | "Sales Evidence Rating Algorithm" | Feature/module name |
| `[API_ENDPOINT]` | "https://api.proptrack.com/v1/properties" | External API URL |
| `[DB_TABLE]` | "valuation_orders" | Database table name |
| `[TEST_DATA]` | "Synthetic Melbourne properties" | Dummy data description |
| `[SECURITY_REQUIREMENT]` | "Input validation for addresses" | Security control |
| `[COVERAGE_TARGET]` | "75%" (APEX), "80%" (LWC) | Test coverage % |
| `[LANGUAGE]` | "APEX", "Python", "Node.js" | Programming language |

---

## Language-Specific Standards

### APEX (Salesforce)
- **Standards**: Salesforce naming, SFDX Prettier config
- **Patterns**: Bulkified design, trigger handlers
- **Testing**: 75% minimum coverage
- **Security**: SOQL injection prevention, FLS checks

### LWC (Lightning Web Components)
- **Standards**: SFDX naming, ESLint + Prettier
- **Patterns**: Lightning Data Service, wire adapters
- **Testing**: 80% minimum coverage (Jest)
- **Security**: XSS prevention, secure communication

### Node.js / TypeScript
- **Standards**: ESLint, TypeScript strict mode
- **Patterns**: Async/await, error handling
- **Testing**: 80% minimum coverage
- **Security**: Input validation, secrets management

### Python (Databricks)
- **Standards**: PEP 8, type hints
- **Patterns**: Databricks notebook structure
- **Testing**: 70% minimum coverage
- **Security**: SQL injection prevention, secrets scope

### SQL (Databricks)
- **Standards**: Databricks auto-formatting
- **Patterns**: Parameterized queries, CTEs
- **Testing**: Data validation, row counts
- **Security**: No dynamic SQL, input sanitization

### R (POSIT)
- **Standards**: Tidyverse conventions
- **Patterns**: Reproducible research
- **Testing**: testthat framework
- **Security**: Data validation, secure file handling

---

## SSDF Practice Groups

Templates support all four NIST SSDF practice groups:

- **PO (Prepare the Organization)**: Documentation, training, standards
- **PS (Protect the Software)**: Access control, secrets management, data protection
- **PW (Produce Well-Secured Software)**: Secure coding, testing, code review
- **RV (Respond to Vulnerabilities)**: Security scanning, vulnerability remediation

---

## ARMATech Architecture Principles

Templates align with Apprise's 6 core principles:

1. **Security**: Highest security standards, ISO27001 compliant
2. **Cloud First**: AWS, Salesforce (no physical servers)
3. **Work from Home**: 100% remote workforce support
4. **Distributed Computing**: Browser-based AI, workstation resources
5. **API Client Integration**: Valuation reports via API
6. **Modern**: Future-proof stack, minimal technical debt

---

## Compliance & Governance

### ISO Certifications
- **ISO 27001:2022**: Information Security Management
- **ISO/IEC 42001:2023**: AI Management Systems

### OWASP Top 10 Coverage
Templates embed controls for all OWASP Top 10 vulnerabilities:
- Injection, Authentication, Data Exposure, XXE, Access Control
- Security Misconfiguration, XSS, Deserialization, Logging, Known Vulnerabilities

### Apprise Policies
- Software Engineering Handbook (SEH)
- Information Security Management System (ISMS)
- AI Usage Policy (approved tools: Claude Code)

---

## Support & Resources

### Documentation
- **Detailed Plan**: [`/planning/pt_templates_plan.md`](../../planning/pt_templates_plan.md)
- **Security Checklist**: [`_security_checklist.md`](./_security_checklist.md)
- **Product & Tech Handbook**: `/docs - raw/Product and Tech Handbook (October 2025).md`

### Getting Help
- **P&T Team Slack**: #engineering-ai-templates
- **Template Issues**: Create issue in project repo
- **Security Concerns**: Contact Lead Engineer or InfoSec team

### Feedback
- Monthly template feedback sessions
- Template usage analytics reviewed quarterly
- Continuous improvement based on real-world usage

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | October 2025 | Initial template library release |

---

**Remember**:
🔒 Security first - always verify .claudeignore
🧪 Test with dummy data only
🗑️ Delete chat history after each session
📋 Follow the security checklist for every template
