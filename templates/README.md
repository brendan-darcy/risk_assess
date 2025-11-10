# Apprise P&T Team - Claude Code Templates

**Production-ready Claude Code templates, security tools, and workflows for Apprise Risk Solutions Product & Technology Team**

[![Compliance](https://img.shields.io/badge/ISO-27001:2022-blue)](https://www.iso.org/standard/27001)
[![AI Compliance](https://img.shields.io/badge/ISO-42001:2023-blue)](https://www.iso.org/standard/42001)
[![Status](https://img.shields.io/badge/Status-Production-green)](https://github.com/Apprisers/templates)

---

## 🚀 Quick Start

```bash
# 1. Clone this repository
git clone https://github.com/Apprisers/templates.git
cd templates

# 2. Install templates to your project (one command!)
./install-templates.sh ~/my-project

# 3. Run pre-flight security check
cd ~/my-project
./pre-flight-check.sh

# 4. Use templates with Claude Code
# Templates are now in ~/my-project/.claude/prompts/
```

**That's it!** The install script copies `.claude/prompts/`, security tools, and configuration files to your project.

For detailed instructions, see [QUICK_START.md](docs/QUICK_START.md)

---

## 📚 What's Included

### **16 Production-Ready Templates** (9,269 lines)

After installation, templates are in `.claude/prompts/` in your project:

#### **Domain-Specific Workflows** (Phase 0.5)
- **[data_analyst_csv.md](.claude/prompts/domain-specific/data_analyst_csv.md)** - CSV data analysis with Pandas
- **[data_engineer_etl.md](.claude/prompts/domain-specific/data_engineer_etl.md)** - ETL pipeline development
- **[data_services_api.md](.claude/prompts/domain-specific/data_services_api.md)** - REST API development

#### **Security Templates** (Phase 1)
- **[data_masking.md](.claude/prompts/security/data_masking.md)** - PII data masking for dev/UAT
- **[secrets_detection.md](.claude/prompts/security/secrets_detection.md)** - Scan for hardcoded credentials
- **[input_validation.md](.claude/prompts/security/input_validation.md)** - OWASP input validation
- **[security_review.md](.claude/prompts/security/security_review.md)** - Comprehensive security audit

#### **Core Workflows** (Phase 2)
- **[secure_feature_development.md](.claude/prompts/workflows/secure_feature_development.md)** - New feature with security, testing, docs
- **[bug_fix_workflow.md](.claude/prompts/workflows/bug_fix_workflow.md)** - Root cause analysis + TDD fix
- **[code_review_request.md](.claude/prompts/workflows/code_review_request.md)** - OWASP Top 10 scanning
- **[refactoring_workflow.md](.claude/prompts/workflows/refactoring_workflow.md)** - Technical debt reduction

#### **Language-Specific Templates** (Phase 3)
- **[apex_development.md](.claude/prompts/language-specific/apex_development.md)** - Salesforce APEX (triggers, batch, bulkification)
- **[lwc_component.md](.claude/prompts/language-specific/lwc_component.md)** - Lightning Web Components + Jest
- **[nodejs_lambda.md](.claude/prompts/language-specific/nodejs_lambda.md)** - AWS Lambda TypeScript functions
- **[databricks_notebook.md](.claude/prompts/language-specific/databricks_notebook.md)** - Databricks ETL pipelines
- **[r_analysis.md](.claude/prompts/language-specific/r_analysis.md)** - R statistical analysis (tidyverse)

#### **Autonomous Agents** (Phase 4)
- **[CSV_ETL_REFACTORING_AGENT_PROMPT.md](.claude/prompts/agent_prompts/CSV_ETL_REFACTORING_AGENT_PROMPT.md)** - Autonomous CSV ETL refactoring agent

---

## 🔒 Security Tools

### **Data Protection**
- **[mask_valuation_data.py](security-tools/mask_valuation_data.py)** - Mask PII while preserving analytics
- **[.claudeignore.template](security-tools/.claudeignore.template)** - Prevent Claude Code from accessing sensitive files
- **[.gitignore.template](security-tools/.gitignore.template)** - 537 patterns for Apprise data protection

### **Automated Security Checks**
- **[pre-flight-check.sh](security-tools/pre-flight-check.sh)** - Run before every Claude Code session
- **[verify_gitignore.sh](security-tools/verify_gitignore.sh)** - Validate .gitignore security

---

## 📖 Documentation

- **[Quick Start Guide](docs/QUICK_START.md)** - Get started in 5 minutes
- **[Security Checklist](docs/_security_checklist.md)** - Complete security requirements
- **[Pre-Flight Usage](docs/PRE_FLIGHT_USAGE.md)** - Security check automation
- **[Data Masking Guide](docs/MASKING_USAGE.md)** - Mask valuation data for dev/UAT
- **[.gitignore Security Review](docs/GITIGNORE_SECURITY_REVIEW.md)** - Protect sensitive data in Git
- **[Repository Structure](docs/STRUCTURE.md)** - Template organization

---

## 🎯 Use Cases

### **Data Analysis**
```bash
# After installing templates to your project:
cd ~/my-project
cat .claude/prompts/domain-specific/data_analyst_csv.md
# Use template in Claude Code to analyze masked CSV data
```

### **Secure Development**
```bash
# Develop new feature with security built-in
cat .claude/prompts/workflows/secure_feature_development.md
# Template includes OWASP controls, TDD, documentation
```

### **Platform Development**
```bash
# Salesforce APEX development
cat .claude/prompts/language-specific/apex_development.md

# AWS Lambda function
cat .claude/prompts/language-specific/nodejs_lambda.md
```

### **Security Review**
```bash
# Request Claude to review code for vulnerabilities
cat .claude/prompts/workflows/code_review_request.md
# Scans for OWASP Top 10, language-specific anti-patterns
```

---

## 🏢 Apprise-Specific Features

### **ARMATech Principles**
All templates align with Apprise's 6 core architecture principles:
- **Security** - OWASP compliance, data protection
- **Cloud First** - AWS, Salesforce, Databricks patterns
- **Modern** - Latest frameworks and best practices
- **API Integration** - RESTful API development
- **Distributed Computing** - Scalable, resilient systems
- **Data-Driven** - Analytics-focused workflows

### **SSDF Practice Groups**
Templates map to Secure Software Development Framework:
- **PO (Prepare Organization)** - Training, documentation
- **PS (Protect Software)** - Access control, data protection
- **PW (Produce Well-Secured Software)** - Secure coding, testing
- **RV (Respond to Vulnerabilities)** - Security scanning, reviews

### **Compliance**
- ISO 27001:2022 (Information Security)
- ISO/IEC 42001:2023 (AI Management)
- ISMS Policies (3, 16)
- Apprise AI Usage Policy

---

## 🛡️ Security-First Approach

Every template includes:
- ✅ **Pre-flight security checklist** - Verify before starting
- ✅ **Data safety protocol** - No real client data with AI tools
- ✅ **.claudeignore verification** - Sensitive files excluded
- ✅ **OWASP controls** - Injection prevention, authentication, authorization
- ✅ **Test coverage requirements** - 75% APEX, 80% LWC/Node.js, 70% Python/R
- ✅ **Post-session cleanup** - Delete Claude Code chat history

---

## 📊 Template Statistics

| Category | Templates | Lines | Status |
|----------|-----------|-------|--------|
| Workflows (Phase 0.5) | 3 | 2,600 | ✅ Complete |
| Security (Phase 1) | 4 | 2,700 | ✅ Complete |
| Core Workflows (Phase 2) | 4 | 2,668 | ✅ Complete |
| Language-Specific (Phase 3) | 5 | 4,001 | ✅ Complete |
| **Total** | **16** | **9,269** | **Production** |

---

## 🔧 Installation & Setup

### **1. Clone Repository**
```bash
git clone https://github.com/Apprisers/templates.git
cd templates
```

### **2. Install Templates to Your Project**
```bash
# One command installs everything
./install-templates.sh ~/my-project

# This copies:
# - .claude/prompts/ (all templates)
# - .gitignore (537 patterns)
# - .claudeignore (sensitive file exclusions)
# - pre-flight-check.sh (security checker)
```

### **3. Install Data Masking Tool** (if needed)
```bash
# Install dependencies
pip install -r security-tools/masking_requirements.txt

# Mask real data
python security-tools/mask_valuation_data.py \
  --input real_data.csv \
  --output masked_data.csv
```

### **4. Run Pre-Flight Check** (before every session)
```bash
cd ~/my-project
./pre-flight-check.sh
```

**That's it!** Your project now has:
- ✅ All templates in `.claude/prompts/`
- ✅ Security tools configured
- ✅ `.gitignore` and `.claudeignore` protecting sensitive data

---

## 🎓 Usage Examples

### **Example 1: CSV Data Analysis**

```bash
# 1. Install templates (if not done already)
cd ~/templates && ./install-templates.sh ~/my-project

# 2. Mask real data first
python ~/templates/security-tools/mask_valuation_data.py \
  --input survey_data.csv \
  --output masked_survey.csv

# 3. Run pre-flight check
cd ~/my-project && ./pre-flight-check.sh

# 4. Reference template in Claude Code
# "Using .claude/prompts/domain-specific/data_analyst_csv.md,
#  analyze masked_survey.csv and identify completion trends by territory"
```

### **Example 2: Secure Feature Development**

```bash
# 1. Run pre-flight check
cd ~/my-project && ./pre-flight-check.sh

# 2. Reference template in Claude Code
# "Using .claude/prompts/workflows/secure_feature_development.md,
#  implement a new valuer assignment algorithm with OWASP controls
#  and 80% test coverage"
```

### **Example 3: Code Security Review**

```bash
# 1. Reference template in Claude Code
# "Using .claude/prompts/workflows/code_review_request.md,
#  review this Lambda function for OWASP Top 10 vulnerabilities
#  and Salesforce best practices"
```

---

## 🔄 Updates & Maintenance

### **Update Templates in Your Project** (One Command!)
```bash
# From the templates repository directory:
cd ~/templates  # or wherever you cloned this repo
./update-templates.sh ~/my-project
```

This will:
1. Pull latest changes from GitHub
2. Update all templates in your project
3. Update security tools (pre-flight-check.sh)
4. Preserve your custom .claudeignore and .gitignore

**That's it!** No need to manually copy files or re-run installation.

### **Check for Updates**
Templates are versioned and updated regularly. Check:
- Release notes for new templates
- Security advisories for critical updates
- Template improvements and bug fixes

---

## 👥 Team Adoption

### **Recommended Workflow**
1. **Setup** - Clone repo, install security tools (one-time)
2. **Pre-Session** - Run pre-flight check (every session)
3. **During Session** - Use templates, follow security guidelines
4. **Post-Session** - Delete Claude Code chat history (mandatory)

### **Success Metrics**
- **Adoption**: 80%+ team usage within 3 months
- **Security**: Zero sensitive data exposure incidents
- **Quality**: Maintain test coverage (75% APEX, 80% LWC/Node.js, 70% Python)
- **Velocity**: 20% reduction in time to implement features

---

## 📞 Support

**Questions or Issues?**
- **Security Questions**: Contact InfoSec Team
- **Template Questions**: See [docs/](docs/) folder
- **Bug Reports**: Open issue in this repository
- **Feature Requests**: Discuss with P&T Team Lead

**Resources:**
- Apprise AI Usage Policy
- Product & Tech Handbook (October 2025)
- ISMS Policies (3, 16)
- Software Engineering Handbook (SEH)

---

## 🚧 Future Development

**Phase 4 (Pending)**:
- Testing templates (apex_test_generation, lwc_jest_tests, integration_tests, performance_tests)
- Documentation templates (technical_design_card, api_documentation, adr_generator, release_notes)
- Deployment templates (pre_deployment_checklist, environment_setup, cicd_pipeline)

**Enterprise AI Policy**:
- Comprehensive AI governance framework for all Apprise teams (beyond P&T)
- Integration with enterprise AI management systems
- Cross-team AI usage guidelines

---

## 📄 License

Internal use only - Apprise Risk Solutions Pty Ltd

---

## 🎯 Quick Links

- [Quick Start Guide](docs/QUICK_START.md)
- [Security Checklist](docs/_security_checklist.md)
- [All Templates](.claude/prompts/)
- [Security Tools](security-tools/)
- [Documentation](docs/)
- [Install Script](install-templates.sh)
- [Update Script](update-templates.sh)

---

**Apprise Risk Solutions - Product & Technology Team**

*Building secure, scalable, data-driven solutions with AI assistance*
