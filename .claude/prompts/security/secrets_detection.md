# Skills: security, code_review, debugging
# SSDF Practice Group: PS, RV (Protect the Software, Respond to Vulnerabilities)
# ARMATech Principles: Security
# Language: Python
# Context: Apprise Risk Solutions P&T Team - Secrets Detection

## Security Reminder
⚠️ **CRITICAL**: This template helps detect hardcoded secrets. If secrets are found, they must be rotated immediately.

## Security Checklist
- [ ] .claudeignore exists and includes: **/*.csv, **/data/**, **/*.env, credentials.json
- [ ] Working in Dev/Sandbox environment only
- [ ] Using dummy test data (NO client data)
- [ ] Will delete Claude Code chat history after this session

## Placeholders
- `[PROJECT_PATH]` - Path to scan (e.g., ".", "/path/to/project")
- `[FILE_PATTERNS]` - File patterns to scan (e.g., "*.js,*.py,*.apex,*.ts")
- `[EXCLUDE_PATTERNS]` - Patterns to exclude (e.g., "node_modules/,*.test.js")
- `[OUTPUT_FORMAT]` - JSON | MARKDOWN | HTML

---

## Task: Generate Secrets Detection Script

You are a security engineer at Apprise Risk Solutions implementing automated secrets scanning to comply with SSDF7 requirement: "Automated scanning for passwords in repos".

Create a Python script that scans code repositories for hardcoded credentials, API keys, tokens, and other secrets.

### Context
- **Requirement**: SSDF7 - Automated scanning for passwords in repos (SEH Section 3.2)
- **Compliance**: ISO 27001:2022, Apprise ISMS Section 5.1 (No plain text secrets in code)
- **Risk**: Hardcoded secrets can lead to unauthorized access, data breaches
- **Integration**: Should work with pre-commit hooks and CI/CD pipelines
- **Scope**: Scan APEX, LWC, Node.js, TypeScript, Python, SQL, R code

---

## Instructions

### 1. PLAN
Outline your approach (4-6 bullets):
- Secret detection patterns (regex patterns for different secret types)
- False positive reduction strategies
- File scanning approach (recursive, respect .gitignore)
- Integration points (pre-commit, GitHub Actions)
- Remediation guidance generation
- Performance optimization for large repos

### 2. BUILD
Generate a Python script with:

**Detection Patterns**:
Scan for these secret types:

1. **API Keys & Tokens**:
   - AWS access keys (AKIA...)
   - Salesforce tokens
   - GitHub tokens
   - Generic API keys (key=, apikey=, token=)
   - Bearer tokens
   - JWT tokens

2. **Passwords & Credentials**:
   - password = "..."
   - pwd = "..."
   - passwd = "..."
   - Database connection strings with passwords
   - JDBC URLs with credentials

3. **Private Keys**:
   - RSA private keys (-----BEGIN RSA PRIVATE KEY-----)
   - SSH private keys
   - Certificate files (.pem, .key)

4. **Cloud Provider Credentials**:
   - AWS secret access keys
   - Azure subscription keys
   - Databricks tokens
   - Salesforce credentials

5. **Database Credentials**:
   - Connection strings with passwords
   - MongoDB URIs
   - PostgreSQL connection strings

6. **High-Entropy Strings**:
   - Random-looking strings (potential secrets)
   - Base64-encoded credentials
   - Hex-encoded keys

**Requirements**:
- Configurable regex patterns via YAML/JSON
- Entropy calculation for generic secret detection
- Context extraction (show surrounding code lines)
- False positive filtering (test files, example configs)
- Severity levels (Critical, High, Medium, Low)
- Multiple output formats (JSON, Markdown, HTML)
- File type awareness (different patterns for different languages)
- Incremental scanning (only scan changed files)
- Performance: scan 10K+ files efficiently

**False Positive Reduction**:
- Exclude test files by default
- Exclude example configurations (.example, .template)
- Check for placeholder values ("your_key_here", "changeme")
- Ignore comments with example credentials
- Whitelist known safe patterns
- Entropy thresholds to reduce noise

**Integration Features**:
- **Pre-commit hook** integration
- **GitHub Actions** workflow generation
- **Exit codes** (0 = clean, 1 = secrets found)
- **CI/CD friendly** output formats

**Testing**:
- Test detection of each secret type
- Test false positive filtering
- Test large repo performance
- Test incremental scanning

### 3. EXPLAIN
Document:
- How to install and run the script
- How to configure custom patterns
- How to integrate with pre-commit hooks
- How to integrate with GitHub Actions
- How to handle detected secrets (rotation procedures)
- Performance tuning for large repositories
- Compliance alignment (SSDF7, ISMS 5.1)

---

## Output Expected

1. **Script**: `detect_secrets.py`
   - CLI with argparse
   - Multiple output formats
   - Configurable patterns
   - Performance optimized

2. **Config Template**: `secrets_detection_config.yaml`
   - Pre-configured patterns for Apprise tech stack
   - Whitelist examples
   - Severity mappings

3. **Pre-commit Hook**: `.pre-commit-config.yaml`
   - Ready-to-use pre-commit configuration
   - Blocks commits with secrets

4. **GitHub Actions Workflow**: `.github/workflows/secrets-scan.yml`
   - Runs on every push/PR
   - Posts results as PR comments

5. **Remediation Guide**: `SECRETS_REMEDIATION.md`
   - Step-by-step secret rotation procedures
   - Apprise-specific guidance (Salesforce, AWS, Databricks)
   - Who to contact (InfoSec, Lead Engineer)

6. **Tests**: `test_detect_secrets.py`
   - Test each detection pattern
   - Test false positive filtering

---

## Example Usage

### Command Line Usage

```bash
# Scan current directory
python detect_secrets.py

# Scan specific path
python detect_secrets.py --path /path/to/project

# Scan with custom config
python detect_secrets.py --config secrets_config.yaml

# Output as JSON (for CI/CD)
python detect_secrets.py --format json --output secrets_report.json

# Scan only changed files (for pre-commit)
python detect_secrets.py --staged-only

# Dry run (show what would be scanned)
python detect_secrets.py --dry-run

# Show high severity only
python detect_secrets.py --min-severity high

# Verbose output with context
python detect_secrets.py --verbose --context 3
```

### Configuration File Example

```yaml
# secrets_detection_config.yaml - Apprise Risk Solutions

# File patterns to scan
include:
  - "**/*.js"
  - "**/*.ts"
  - "**/*.apex"
  - "**/*.cls"
  - "**/*.py"
  - "**/*.sql"
  - "**/*.r"
  - "**/*.yml"
  - "**/*.yaml"
  - "**/*.json"
  - "**/*.xml"

# File patterns to exclude
exclude:
  - "**/node_modules/**"
  - "**/__pycache__/**"
  - "**/.venv/**"
  - "**/dist/**"
  - "**/build/**"
  - "**/*.test.js"
  - "**/*.spec.ts"
  - "**/*.example.*"
  - "**/*.template.*"
  - "**/.git/**"

# Detection patterns
patterns:
  # AWS Credentials
  - name: "AWS Access Key ID"
    pattern: "(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}"
    severity: CRITICAL
    description: "AWS Access Key detected"

  - name: "AWS Secret Access Key"
    pattern: "aws_secret_access_key\\s*=\\s*['\\\"]?([A-Za-z0-9/+=]{40})['\\\"]?"
    severity: CRITICAL
    description: "AWS Secret Access Key detected"

  # Salesforce
  - name: "Salesforce Access Token"
    pattern: "00D[a-zA-Z0-9]{15}![A-Za-z0-9.]+"
    severity: CRITICAL
    description: "Salesforce access token detected"

  # Generic Passwords
  - name: "Password in Code"
    pattern: "(password|passwd|pwd)\\s*=\\s*['\\\"]([^'\\\"]+)['\\\"]"
    severity: HIGH
    description: "Hardcoded password detected"
    exclude_values:
      - "your_password_here"
      - "changeme"
      - "password"
      - "test"

  # API Keys
  - name: "Generic API Key"
    pattern: "(api[_-]?key|apikey)\\s*[=:]\\s*['\\\"]([a-zA-Z0-9_\\-]{20,})['\\\"]"
    severity: HIGH
    description: "API key detected"

  # Databricks
  - name: "Databricks Token"
    pattern: "dapi[a-f0-9]{32}"
    severity: CRITICAL
    description: "Databricks personal access token"

  # Database Connection Strings
  - name: "Database Connection String with Password"
    pattern: "(jdbc|mongodb|postgresql):\\/\\/[^:]+:([^@]+)@"
    severity: CRITICAL
    description: "Database connection string with embedded password"

  # Private Keys
  - name: "Private Key"
    pattern: "-----BEGIN (RSA |EC )?PRIVATE KEY-----"
    severity: CRITICAL
    description: "Private key file detected"

  # JWT Tokens
  - name: "JWT Token"
    pattern: "eyJ[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+"
    severity: MEDIUM
    description: "JWT token detected"

  # High Entropy Strings (potential secrets)
  - name: "High Entropy String"
    pattern: "['\\\"](#[a-zA-Z0-9/+=]{32,})['\\\"]"
    severity: MEDIUM
    description: "High-entropy string (potential secret)"
    entropy_threshold: 4.5

# False positive filters
whitelist:
  - pattern: "example\\.com"
  - pattern: "test[_-]?key"
  - pattern: "dummy[_-]?password"
  - pattern: "changeme"
  - pattern: "your_.*_here"

# Output settings
output:
  show_context: true
  context_lines: 2
  show_line_numbers: true
  group_by_severity: true
```

### Pre-commit Hook Integration

`.pre-commit-config.yaml`:
```yaml
repos:
  - repo: local
    hooks:
      - id: detect-secrets
        name: Detect Secrets
        entry: python detect_secrets.py --staged-only
        language: python
        files: \\.(js|ts|py|apex|cls|sql|r|yml|yaml|json)$
        exclude: (test|spec|example|template)\\.(js|ts|py)$
```

Install pre-commit hook:
```bash
pip install pre-commit
pre-commit install
```

### GitHub Actions Integration

`.github/workflows/secrets-scan.yml`:
```yaml
name: Secrets Detection

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install pyyaml

      - name: Run Secrets Detection
        run: |
          python detect_secrets.py --format json --output secrets_report.json

      - name: Upload Results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: secrets-scan-results
          path: secrets_report.json

      - name: Fail on Critical Findings
        run: |
          if grep -q '"severity": "CRITICAL"' secrets_report.json; then
            echo "CRITICAL secrets detected!"
            cat secrets_report.json
            exit 1
          fi
```

---

## Apprise-Specific Detection Scenarios

### Scenario 1: Scanning APEX Code

**Common Issues**:
- Hardcoded Salesforce credentials in integration code
- API endpoints with embedded auth tokens
- Named Credentials referenced incorrectly (using literals instead of references)

**Detection Pattern**:
```yaml
- name: "Salesforce Hardcoded Credential"
  pattern: "String\\s+password\\s*=\\s*['\"]([^'\"]+)['\"]"
  severity: HIGH
  files: "**/*.apex,**/*.cls"
```

### Scenario 2: Scanning Node.js/TypeScript Lambda Functions

**Common Issues**:
- AWS credentials in environment variable assignments
- Database connection strings with passwords
- API keys for external services

**Detection Pattern**:
```yaml
- name: "AWS Credential in Lambda"
  pattern: "AWS_SECRET_ACCESS_KEY['\"]?\\s*:\\s*['\"]([^'\"]+)['\"]"
  severity: CRITICAL
  files: "**/*.js,**/*.ts"
```

### Scenario 3: Scanning Databricks Notebooks

**Common Issues**:
- Databricks personal access tokens
- Database connection strings
- API keys for data providers

**Detection Pattern**:
```yaml
- name: "Databricks Token in Notebook"
  pattern: "dbutils\\.secrets\\.get\\(['\"]scope['\"],\\s*['\"]key['\"]\\)|dapi[a-f0-9]{32}"
  severity: HIGH
  files: "**/*.py,**/*.sql"
```

---

## Remediation Procedures

### If Secrets are Detected:

**1. Immediate Actions** (within 1 hour):
- [ ] Stop using the compromised secret immediately
- [ ] Assess impact (what systems/data could be accessed?)
- [ ] Notify Lead Engineer and InfoSec team
- [ ] Document in incident log

**2. Secret Rotation** (within 4 hours):
- [ ] **Salesforce**: Rotate passwords, reset security tokens
  - Login to Salesforce → Setup → My Personal Information → Reset Security Token
- [ ] **AWS**: Rotate access keys
  - AWS Console → IAM → Users → Security Credentials → Make Inactive → Delete
- [ ] **Databricks**: Revoke and generate new personal access tokens
  - Workspace → User Settings → Access Tokens → Revoke
- [ ] **Database**: Change database passwords
  - Update credentials in AWS Secrets Manager / Salesforce Named Credentials

**3. Code Remediation** (within 8 hours):
- [ ] Remove hardcoded secret from code
- [ ] Replace with proper secret management:
  - **Salesforce**: Use Named Credentials
  - **AWS**: Use Secrets Manager or Parameter Store
  - **Local Dev**: Use .env files (in .gitignore)
- [ ] Update .claudeignore to prevent future commits
- [ ] Commit fix with message: "fix(security): remove hardcoded credentials"

**4. Git History Cleanup** (if committed):
- [ ] Use `git filter-branch` or BFG Repo-Cleaner to remove from history
- [ ] Force push cleaned history (coordinate with team)
- [ ] Notify all developers to re-clone repository

**5. Review & Prevention** (within 1 week):
- [ ] Run full secrets scan on entire repository
- [ ] Review other code by same author for similar issues
- [ ] Ensure pre-commit hooks installed
- [ ] Update secrets detection patterns if new type found
- [ ] Team training on secure credential management

**6. Compliance Documentation**:
- [ ] Create incident report (SEH Section 9)
- [ ] Update ISMS records
- [ ] Add to quarterly security review

---

## SSDF Compliance (SSDF7)

**SSDF7 Requirement**: "Automated scanning for passwords in repos"

This template satisfies SSDF7 by:
- ✅ **Automated Detection**: Script can run in CI/CD automatically
- ✅ **Repository Scanning**: Scans all code in repository
- ✅ **Password Detection**: Detects hardcoded passwords and credentials
- ✅ **Integration**: Pre-commit hooks prevent new secrets from being committed
- ✅ **Reporting**: Generates compliance-ready reports

**Evidence for Audits**:
- Secrets detection configuration file (secrets_detection_config.yaml)
- GitHub Actions workflow showing automated scans
- Pre-commit hook configuration
- Scan reports from CI/CD runs

---

## Performance Optimization

**For Large Repositories** (10K+ files):

1. **Incremental Scanning**:
   ```bash
   # Only scan files changed since last commit
   python detect_secrets.py --incremental --baseline secrets_baseline.json
   ```

2. **Parallel Processing**:
   ```python
   # Add to script: use multiprocessing.Pool
   with Pool(processes=4) as pool:
       results = pool.map(scan_file, files)
   ```

3. **File Type Filtering**:
   ```bash
   # Only scan code files, skip binaries
   python detect_secrets.py --file-types .js,.py,.apex
   ```

**Timing Estimates**:
- 100 files: ~2 seconds
- 1,000 files: ~15 seconds
- 10,000 files: ~2 minutes
- 100,000 files: ~20 minutes (use --incremental)

---

## Integration with Apprise SDLC

**Design Phase** (Module 2.2):
- Include secret management approach in Technical Design Card
- Specify which secrets are needed and how they'll be managed

**Development Phase** (Module 3):
- Run secrets detection before code review
- Verify pre-commit hook is active

**Code Review Phase** (Module 4.4):
- Reviewer checks for proper secret management
- Verify no hardcoded credentials

**Deployment Phase** (Module 6.5):
- Final secrets scan before production deployment
- CAB checklist includes "No hardcoded secrets" verification

---

**Remember**:
- ⚠️ If secrets are found, ROTATE IMMEDIATELY
- ⚠️ NEVER commit secrets to git
- ⚠️ Use Dashlane for credential storage (SEH Section 5.1)
- ⚠️ Use Named Credentials (Salesforce) or Secrets Manager (AWS)
- ⚠️ DELETE chat history after this session
