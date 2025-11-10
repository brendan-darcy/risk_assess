# Skills: security, data_protection, data_engineering
# SSDF Practice Group: PS (Protect the Software)
# ARMATech Principles: Security
# Language: Python
# Context: Apprise Risk Solutions P&T Team - Data Protection

## Security Reminder
⚠️ **CRITICAL**: This template helps protect sensitive data. Ensure masked data NEVER contains real client information.

## Security Checklist
- [ ] .claudeignore exists and includes: **/*.csv, **/data/**, **/*.env, credentials.json
- [ ] Working in Dev/Sandbox environment only
- [ ] Using dummy test data (NO client data)
- [ ] Will delete Claude Code chat history after this session

## Placeholders
- `[INPUT_FILE]` - Source file with sensitive data (e.g., "raw_valuations.csv")
- `[OUTPUT_FILE]` - Destination for masked data (e.g., "masked_valuations.csv")
- `[SENSITIVE_COLUMNS]` - List of columns to mask (e.g., "borrower_name,property_address,email,phone")
- `[PRESERVE_COLUMNS]` - Columns to keep exactly (e.g., "timestamps,values,postcodes,states")
- `[MASKING_STRATEGY]` - REDACTED | TOKENIZED | HASHED | SYNTHETIC | PRESERVE
- `[DATA_FORMAT]` - CSV | PARQUET | JSON

---

## Quick Decision Guide: Which Masking Strategy?

**Use this guide to choose the right strategy for each column:**

| Data Type | Strategy | Reason | Example |
|-----------|----------|--------|---------|
| **Timestamps/Dates** | **PRESERVE** | Essential for temporal analysis | `openedDate`, `closedDate` |
| **Financial Values** | **PRESERVE** | Essential for value/variance analysis | `valuationAmount`, `loanAmount` |
| **Geographic (State/Postcode)** | **PRESERVE** | Needed for regional analysis | `state_c`, `postcode_c` |
| **Person Names** | **SYNTHETIC** (deterministic) | Realistic but fake, preserves relationships | `valuer`, `borrower_name` |
| **Addresses (Street)** | **SYNTHETIC** (deterministic) | Fake address, preserve postcode | `street_name`, `suburb` |
| **Account/Client Names** | **TOKENIZED** or **SYNTHETIC** | Generic names, preserves uniqueness | `account`, `lender` |
| **IDs (Job/Reference)** | **HASHED** | Complete anonymization | `jobNumber`, `valExID` |
| **Foreign Keys** | **TOKENIZED** | Preserves relationships | `propertyId`, `clientId` |
| **Comments/Notes** | **REDACTED** | Not needed for analysis | `internalNotes`, `comments` |

**Key principle:** Preserve what you need for analysis, mask what identifies individuals/properties.

### Before/After Example

**Before Masking:**
```csv
jobNumber,valuer,account,street_name_c,suburb_c,state_c,postcode_c,estimateValue,openedDate
215532,monique bourdon,anz,Cortis,LANGFORD,WA,6147,650000,2025-01-01
```

**After Masking:**
```csv
jobNumber,valuer,account,street_name_c,suburb_c,state_c,postcode_c,estimateValue,openedDate
a3f5c8d1e9b2,Jessica Miller,Bank_Alpha,Watson,RIVERWOOD,WA,6147,650000,2025-01-01
```

**Notice:**
- ID hashed (unrecognizable)
- Valuer name fake but consistent across all rows
- Account is generic bank name
- Address fake BUT postcode/state preserved
- Value and date preserved exactly

---

## Task: Generate Data Masking Script

You are a security engineer at Apprise Risk Solutions implementing data protection controls.

Create a Python script to mask sensitive data for development/UAT environments, ensuring compliance with Apprise's Information Security Management System (ISMS) and data protection policies.

### Context
- **Requirement**: Dev/UAT environments must use dummy data or masked production data
- **Compliance**: ISO 27001:2022, internal ISMS policies (ISMS 3, ISMS 16)
- **Risk**: Accidental exposure of client PII through Claude Code, logs, or commits
- **Protection**: .claudeignore should exclude sensitive files, but defense in depth requires masking at source
- **Data Types**: Property valuations, borrower information, sales evidence, financial data

---

## Instructions

### 1. PLAN
Outline your approach (3-5 bullets):
- Masking strategy selection rationale for each data type
- Columns to mask and method for each
- Data type preservation approach (maintain analytics accuracy)
- Validation checks to ensure masking succeeded
- Integration with existing data pipeline

### 2. BUILD
Generate a Python script with:

**Masking Functions**:
Support multiple masking strategies:

1. **REDACTED**: Replace with `[REDACTED]`
   - Use for: Low-value fields where preservation not needed
   - Example: Comments, notes, descriptions

2. **TOKENIZED**: Consistent hash-based tokenization (same input → same token)
   - Use for: Fields needing referential integrity
   - Example: Client IDs, property IDs (preserve relationships)

3. **HASHED**: One-way hash (SHA-256)
   - Use for: Fields not needing reversal
   - Example: Passwords, security answers

4. **SYNTHETIC**: Generate realistic fake data (using Faker library)
   - Use for: Fields needing realistic test data
   - Example: Names, addresses, emails, phone numbers
   - **IMPORTANT**: Use deterministic/seeded approach (same input → same fake output)
   - **Why**: Preserves relationships across rows (e.g., same valuer name throughout dataset)

5. **PRESERVE**: Keep data exactly as-is
   - Use for: Fields essential for analysis (timestamps, values, geographic codes)
   - Example: Dates, amounts, postcodes, states
   - **Why**: Analysis accuracy depends on these being real

**Requirements**:
- Preserve data types (string, int, date, float, etc.)
- Preserve data distributions where needed (for analytics accuracy)
- Handle null values appropriately
- Log masking summary (columns masked, row count, NO actual data logged)
- Include validation: compare row counts, detect if any original values leaked through
- Support CSV, Parquet, and JSON formats
- Configuration via YAML or JSON
- CLI interface for easy use
- Progress bar for large files

**Security Controls**:
- No logging of actual sensitive data
- Confirmation prompt before overwriting files
- Option to verify .claudeignore includes output path
- Clear warnings about proper usage
- Dry-run mode to preview changes

**Testing**:
- Unit tests using synthetic sensitive data
- Test each masking strategy
- Test that original data not present in output
- Test data type preservation
- Test null handling
- Test large file performance (1M+ rows)

### 3. EXPLAIN
Document:
- When to use each masking strategy
- How to configure for different file types
- How to integrate into data pipeline workflow
- .claudeignore patterns to add
- Compliance considerations (ISMS requirements)
- Performance characteristics (memory usage, processing time)

---

## Output Expected

1. **Script**: `mask_sensitive_data.py`
   - Command-line interface with argparse
   - Multiple masking strategies
   - Logging and validation
   - Progress tracking

2. **Config Template**: `masking_config.yaml.example`
   - Example configuration for Apprise use cases
   - Comments explaining each option
   - Sensitive column definitions

3. **Tests**: `test_mask_sensitive_data.py`
   - Test each masking strategy
   - Validation tests
   - Performance tests

4. **Documentation**: README section with:
   - Installation instructions (pip requirements)
   - Usage examples (common scenarios)
   - When to use each strategy
   - .claudeignore patterns
   - Compliance notes
   - Troubleshooting guide

---

## Example Usage

### Command Line Usage

```bash
# Basic usage with YAML config
python mask_sensitive_data.py \
  --input raw_valuations.csv \
  --output masked_valuations.csv \
  --config masking_config.yaml

# Dry run to preview changes
python mask_sensitive_data.py \
  --input raw_valuations.csv \
  --output masked_valuations.csv \
  --config masking_config.yaml \
  --dry-run

# Specify masking strategy inline
python mask_sensitive_data.py \
  --input raw_valuations.csv \
  --output masked_valuations.csv \
  --columns "borrower_name,property_address,email" \
  --strategy SYNTHETIC

# Verify .claudeignore includes output file
python mask_sensitive_data.py \
  --verify-claudeignore masked_valuations.csv

# Process Parquet file
python mask_sensitive_data.py \
  --input data.parquet \
  --output masked_data.parquet \
  --config masking_config.yaml \
  --format parquet
```

### Configuration File Example

```yaml
# masking_config.yaml - Apprise Risk Solutions
# Use for valuations, borrower data, sales evidence

input_format: csv  # csv, parquet, json
output_format: csv

# Columns to mask with strategies
sensitive_columns:
  # Borrower information
  - name: borrower_name
    strategy: SYNTHETIC
    data_type: person_name
    deterministic: true  # Same input → same output (preserves relationships)

  - name: borrower_email
    strategy: TOKENIZED  # Preserve uniqueness for testing
    salt: "apprise_dev_2025"

  - name: borrower_phone
    strategy: SYNTHETIC
    data_type: phone_number
    locale: en_AU  # Australian format
    deterministic: true

  - name: borrower_id
    strategy: TOKENIZED  # Preserve relationships

  # Property information
  - name: property_address
    strategy: SYNTHETIC
    data_type: address
    locale: en_AU
    deterministic: true

  - name: property_owner
    strategy: SYNTHETIC
    data_type: person_name
    deterministic: true

  - name: property_lot_plan
    strategy: TOKENIZED  # Preserve for testing

  # Financial information (PRESERVE for analytics)
  - name: valuation_amount
    strategy: PRESERVE  # Keep exact values

  - name: loan_amount
    strategy: PRESERVE  # Keep exact values

  # Temporal data (PRESERVE for TaT analysis)
  - name: opened_date
    strategy: PRESERVE  # Keep exact timestamps

  - name: closed_date
    strategy: PRESERVE  # Keep exact timestamps

  # Geographic data (PRESERVE for regional analysis)
  - name: state
    strategy: PRESERVE  # Keep state codes

  - name: postcode
    strategy: PRESERVE  # Keep postcodes

  # Sales evidence
  - name: comparable_address
    strategy: SYNTHETIC
    data_type: address

  # Low-value fields
  - name: internal_notes
    strategy: REDACTED

  - name: valuer_comments
    strategy: REDACTED

# Validation rules
validation:
  check_row_count: true
  check_no_original_data: true
  sample_size: 100  # Number of rows to validate

# Performance
performance:
  chunk_size: 10000  # Process in chunks for large files
  show_progress: true
```

### Python Integration Example

```python
from mask_sensitive_data import DataMasker

# Initialize masker
masker = DataMasker(config_file='masking_config.yaml')

# Load data
df = masker.load_data('raw_valuations.csv')

# Apply masking
masked_df = masker.mask_data(df)

# Validate
if masker.validate(masked_df, df):
    # Save
    masker.save_data(masked_df, 'masked_valuations.csv')
    print("✓ Data masked successfully")
else:
    print("✗ Validation failed - check logs")
```

---

## Apprise-Specific Scenarios

### Scenario 1: Masking Valuation Data for Dev Environment

**Input**: Production export of valuation orders with client PII

**Columns to Mask**:
- Borrower name, email, phone → SYNTHETIC
- Property address → SYNTHETIC (maintain suburb for analytics)
- Property owner → SYNTHETIC
- Valuer notes → REDACTED
- Valuation amount, loan amount → KEEP (needed for testing)

**Config**:
```yaml
sensitive_columns:
  - name: borrower_name
    strategy: SYNTHETIC
  - name: property_address
    strategy: SYNTHETIC
    preserve_suburb: true  # Keep suburb for location-based testing
```

### Scenario 2: Masking Sales Evidence for UAT

**Input**: Sales evidence data with property addresses and sale prices

**Columns to Mask**:
- Property address → SYNTHETIC (preserve suburb, postcode)
- Vendor name → SYNTHETIC
- Agent name → SYNTHETIC
- Sale price → ADD_NOISE (add ±10% random noise, preserve trends)
- Sale date → KEEP (needed for temporal analysis)

**Use Case**: UAT testers need realistic-looking data with preserved geographic and temporal patterns

### Scenario 3: Anonymizing Data for External Partner

**Input**: Valuation data to share with external analytics partner

**Columns to Mask**:
- All PII → SYNTHETIC or TOKENIZED
- Valuation amounts → ADD_NOISE (±15% for privacy)
- Property addresses → GENERALIZE (suburb level only, remove street addresses)

**Additional**: Remove columns not needed by partner (internal IDs, valuer names)

---

## Compliance Checklist

Before using masked data:

- [ ] Verify no real client names, addresses, or contact information in output
- [ ] Check that referential integrity preserved where needed (IDs, relationships)
- [ ] Confirm data distributions suitable for intended use (analytics, testing)
- [ ] Validate row counts match input (no data loss)
- [ ] Add masked files to .claudeignore
- [ ] Document masking approach in data lineage
- [ ] Obtain approval from InfoSec if sharing masked data externally

---

## Integration with .claudeignore

Add these patterns to your .claudeignore:

```
# Raw/unmasked data (NEVER commit)
**/raw_*.csv
**/production_*.csv
**/unmasked_*.csv
**/raw_data/**

# Masked data (safe to use in dev)
**/masked_*.csv
**/test_data/**
**/dev_data/**

# Masking configs (may contain field names - review before commit)
masking_config.yaml  # Review for sensitive field names
```

---

## ISMS Policy References

- **ISMS 3**: Information Classification & Handling Policy
  - Clause 7.1: Data protection requirements
  - Clause 8.2: Handling of sensitive information

- **ISMS 16**: Data Retention
  - Development data retention policies
  - Data disposal requirements

- **SEH Section 8.3**: Data Masking and Access
  - ARMATech data masking policy
  - User entitlements for data access

---

## Performance Guidelines

**File Size Recommendations**:
- < 100MB: Process in memory (fast)
- 100MB - 1GB: Use chunking (chunk_size: 10000)
- > 1GB: Consider Databricks for parallel processing

**Memory Usage**:
- CSV: ~2-3x file size in memory
- Parquet: ~1.5x file size (more efficient)
- Use `--chunk-size` for large files

**Timing Estimates**:
- 100K rows: ~10 seconds
- 1M rows: ~2 minutes
- 10M rows: ~20 minutes (consider Databricks)

---

## Troubleshooting

**Issue**: "Original data detected in output"
- **Cause**: Masking strategy not applied to all instances
- **Fix**: Check column name matching (case sensitivity), verify config

**Issue**: "Data types changed after masking"
- **Cause**: SYNTHETIC data generator type mismatch
- **Fix**: Specify `preserve_type: true` in config

**Issue**: "Referential integrity broken"
- **Cause**: Using SYNTHETIC instead of TOKENIZED for IDs
- **Fix**: Use TOKENIZED for foreign keys and IDs

**Issue**: "Performance very slow"
- **Cause**: Processing large file in memory
- **Fix**: Use `--chunk-size 10000` or switch to Parquet format

---

**Remember**:
- ⚠️ NEVER commit unmasked data
- ⚠️ ALWAYS verify .claudeignore before masking
- ⚠️ ALWAYS validate masked output before use
- ⚠️ DELETE chat history after session
