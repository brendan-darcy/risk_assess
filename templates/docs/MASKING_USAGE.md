# Valuation Data Masking - Quick Start Guide

## What It Does

Masks sensitive PII in valuation data files while preserving:
- ✅ **Real timestamps** (for TaT analysis)
- ✅ **Real values** (for variance/tolerance analysis)
- ✅ **Postcodes** (for geographic analysis)
- ✅ **States** (for regional analysis)
- ✅ **Referential integrity** (same valuer = same masked name across all rows)

Masks completely:
- ❌ Valuer names → Fake names
- ❌ Client/Account names → Generic bank names (Bank_Alpha, Bank_Beta, etc.)
- ❌ IDs → SHA256 hash (12 chars)
- ❌ Addresses → Fake addresses (preserving postcode)

---

## Installation

```bash
# Install dependencies
pip install -r masking_requirements.txt

# Make script executable (optional)
chmod +x mask_valuation_data.py
```

---

## Quick Usage

### **Step 1: Test with Sample First**

```bash
# Process first 1000 rows to test
python mask_valuation_data.py \
  --input "docs - project examples/survey/data/Extract.csv" \
  --output masked_sample.csv \
  --sample 1000

# Review the output
head -20 masked_sample.csv
```

### **Step 2: Validate the Sample**

```bash
# Check no real valuer names present
grep -i "monique\|carol\|kane\|jeremiah" masked_sample.csv
# Should return nothing

# Check postcodes are preserved
cut -d',' -f42 masked_sample.csv | head -20
# Should see real postcodes (2560, 3805, etc.)

# Check values are preserved
cut -d',' -f16 masked_sample.csv | head -20
# Should see real valuation amounts
```

### **Step 3: Process Full File**

```bash
# Process entire dataset
python mask_valuation_data.py \
  --input "docs - project examples/survey/data/Extract.csv" \
  --output masked_valuation_data.csv

# Optionally save mappings for reference (KEEP OFFLINE!)
python mask_valuation_data.py \
  --input "docs - project examples/survey/data/Extract.csv" \
  --output masked_valuation_data.csv \
  --save-mappings masking_mappings.json
```

### **Step 4: Add Real Data to .claudeignore**

```bash
# Protect real data files
echo "docs - project examples/**/*.csv" >> .claudeignore
echo "Extract.csv" >> .claudeignore
echo "report*.csv" >> .claudeignore
echo "masking_mappings.json" >> .claudeignore  # If you saved mappings

# Verify it worked
cat .claudeignore | grep -E "(Extract|report|docs -)"
```

### **Step 5: Now Safe to Use with Claude Code**

```bash
# Run pre-flight check
./templates/pt-team/pre-flight-check.sh

# Now use Claude Code with masked_valuation_data.csv
```

---

## Command Reference

### Basic Usage

```bash
# Mask entire file
python mask_valuation_data.py --input Extract.csv --output masked_data.csv
```

### Dry Run (Preview Only)

```bash
# See what would be masked without writing output
python mask_valuation_data.py \
  --input Extract.csv \
  --output masked_data.csv \
  --dry-run
```

### Process Sample for Testing

```bash
# Process first 1000 rows only
python mask_valuation_data.py \
  --input Extract.csv \
  --output masked_sample.csv \
  --sample 1000
```

### Save Mappings (Keep Offline!)

```bash
# Save valuer/account mappings for reference
python mask_valuation_data.py \
  --input Extract.csv \
  --output masked_data.csv \
  --save-mappings mappings.json

# ⚠️ Add to .claudeignore immediately!
echo "masking_mappings.json" >> .claudeignore
```

### Validate Existing Masked File

```bash
# Check if existing masked file is valid
python mask_valuation_data.py \
  --input Extract.csv \
  --output masked_data.csv \
  --validate-only
```

---

## File Format Support

### Extract.csv (Structured Format)

**Columns masked:**
- `jobNumber` → Hashed
- `valExID` → Hashed
- `valuer` → Fake name (deterministic)
- `valuerPeer` → Fake name (deterministic)
- `account` → Generic bank name
- `unit_number_c` → Fake number
- `street_number_c` → Fake number
- `street_name_c` → Fake name
- `suburb_c` → Fake suburb
- `state_c` → **PRESERVED**
- `postcode_c` → **PRESERVED**

**Columns preserved exactly:**
- `openedDate`, `closedDate`, `weeknum`, `month`
- `estimateValue`, `marketValueCeiling`, `loanAmount`
- `status`, `channelType`, `jobType`, `propertyType`
- `region_c`, `region_type`, `TaT`, `EscGroup`

### report*.csv (Raw Export Format)

**Columns masked:**
- `Job Number` → Hashed
- `ValEx Job ID` → Hashed
- `Job Owner` → Fake name
- `Job Original Valuer` → Fake name
- `Job Peer Reviewer` → Fake name
- `Account Name` → Generic bank name
- `Full Address` → Fake address (postcode preserved)

**Columns preserved:**
- All date/time fields
- `Market Value Ceiling`, `Deal Value`, `Loan Amount`
- `Territory`, `Status`, `Job Type`, `Escalation Reason`

---

## Understanding the Output

### Before Masking (Extract.csv)

```csv
jobNumber,valExID,valuer,account,street_number_c,street_name_c,suburb_c,state_c,postcode_c,estimateValue
215532,VXJ-000025461748,monique bourdon,anz,55B,Cortis,LANGFORD,WA,6147,650000
```

### After Masking

```csv
jobNumber,valExID,valuer,account,street_number_c,street_name_c,suburb_c,state_c,postcode_c,estimateValue
a3f5c8d1e9b2,b7e2a9c4f1d8,Jessica Miller,Bank_Alpha,142,Watson,RIVERWOOD,WA,6147,650000
```

**Notice:**
- IDs are hashed (unrecognizable)
- Valuer name is fake but consistent
- Account is generic bank name
- Address is fake BUT postcode (6147) and state (WA) are preserved
- Value (650000) is preserved exactly

---

## Deterministic Masking

**Important feature:** The same input always produces the same output.

**Example:**
- Real valuer: "monique bourdon"
- First occurrence: Masked as "Jessica Miller"
- Second occurrence: Also masked as "Jessica Miller"
- Third occurrence: Also masked as "Jessica Miller"

**Why this matters:**
- Preserves valuer workload analysis (count jobs per valuer)
- Preserves peer review relationships
- Maintains referential integrity across datasets

---

## Validation Checks

The script automatically validates:

1. ✅ **Row count preserved** (no data loss)
2. ✅ **Column count preserved**
3. ✅ **No original valuer names** in output
4. ✅ **No original account names** in output
5. ✅ **Postcodes preserved** exactly
6. ✅ **Values preserved** exactly
7. ✅ **Timestamps preserved** exactly

**Example validation output:**

```
🔍 Validating masked data...
  ✅ Row count preserved: 10000 rows
  ✅ Column count preserved: 61 columns
  ✅ No original valuer names detected (checked 5 samples)
  ✅ No original account names detected (checked 5 samples)
  ✅ Postcodes preserved: 847 unique postcodes
  ✅ estimateValue values preserved exactly
  ✅ marketValueCeiling values preserved exactly
  ✅ openedDate timestamps preserved exactly
```

---

## What Analysis Remains Possible

### ✅ Temporal Analysis (Fully Preserved)

```python
# TaT analysis by date
df.groupby('openedDate')['TaT'].mean()

# Peak hours analysis
df['hour'] = pd.to_datetime(df['openedDate']).dt.hour
df.groupby('hour').size()

# Week-over-week trends
df.groupby('weeknum')['status'].value_counts()
```

### ✅ Value Analysis (Fully Preserved)

```python
# Variance distribution
df['variance'] = (df['marketValueCeiling'] - df['estimateValue']) / df['estimateValue']

# LVR bands
df['lvrBand'] = pd.cut(df['loanAmount'] / df['marketValueCeiling'], bins=[0, 0.6, 0.8, 1.0])

# Price point analysis
df.groupby('LVRBand1')['marketValueCeiling'].describe()
```

### ✅ Geographic Analysis (Postcode-Level)

```python
# Performance by postcode
df.groupby('postcode_c')['TaT'].mean()

# Completion rate by state
df.groupby('state_c')['status'].value_counts()

# Metro vs rural
df.groupby('region_type')['val_variance_Tol'].describe()
```

### ✅ Workload Analysis (Masked Names)

```python
# Jobs per valuer (using masked names)
df.groupby('valuer').size().sort_values(ascending=False)

# Peer review patterns
df[df['peer'] == True].groupby('valuerPeer').size()

# Same valuer tracked across time (deterministic masking preserves this)
df.groupby(['valuer', 'weeknum']).size()
```

### ❌ Cannot Do (By Design)

- Cannot identify specific properties (addresses masked)
- Cannot identify specific valuers (names masked)
- Cannot identify specific clients (accounts masked)
- Cannot link to external systems (IDs hashed)

---

## Troubleshooting

### Issue: "Module not found: pandas"

```bash
# Install dependencies
pip install -r masking_requirements.txt
```

### Issue: "File not found"

```bash
# Check path is correct (use quotes for paths with spaces)
python mask_valuation_data.py \
  --input "docs - project examples/survey/data/Extract.csv" \
  --output masked_data.csv
```

### Issue: "Script runs but output looks wrong"

```bash
# Run with --dry-run first to preview
python mask_valuation_data.py \
  --input Extract.csv \
  --output masked_data.csv \
  --dry-run

# Process small sample first
python mask_valuation_data.py \
  --input Extract.csv \
  --output masked_sample.csv \
  --sample 100
```

### Issue: "Original names still in output"

```bash
# Validate the masking
python mask_valuation_data.py \
  --input Extract.csv \
  --output masked_data.csv \
  --validate-only

# If validation fails, check column names match
head -1 Extract.csv
```

---

## Security Checklist

Before using masked data with Claude Code:

- [ ] Run masking script on real data
- [ ] Validate output (no real names/addresses)
- [ ] Add real data files to .claudeignore
- [ ] Add mapping files to .claudeignore (if saved)
- [ ] Verify postcodes/values preserved for analysis
- [ ] Run pre-flight check
- [ ] NOW safe to use Claude Code with masked data

---

## Files Generated

| File | Purpose | Keep/Delete | Commit to Git? |
|------|---------|-------------|----------------|
| `masked_*.csv` | Masked data for analysis | Keep | ✅ Yes (safe) |
| `masking_mappings.json` | Valuer/account mappings | Keep offline | ❌ NO (add to .claudeignore) |
| `Extract.csv` | Real data (original) | Keep offline | ❌ NO (add to .claudeignore) |

---

## Performance

**Processing times (approximate):**
- 1,000 rows: ~2 seconds
- 10,000 rows: ~15 seconds
- 100,000 rows: ~2 minutes
- 1,000,000 rows: ~20 minutes

**Memory usage:**
- ~2-3x file size in memory
- 50MB file → ~150MB RAM
- Large files (>500MB): Process in chunks or use Databricks

---

## Support

**Issues with the script?**
- Check Python version: `python --version` (requires 3.7+)
- Check dependencies: `pip list | grep -E "(pandas|Faker)"`
- Try dry-run mode first: `--dry-run`
- Test with small sample: `--sample 100`

**Questions about masking approach?**
- See: [templates/pt-team/security/data_masking.md](templates/pt-team/security/data_masking.md)
- Contact: P&T Team or InfoSec

---

**Remember:**
- ⚠️ NEVER commit real data to Git
- ⚠️ ALWAYS verify masked output before use
- ⚠️ ALWAYS add real data to .claudeignore
- ⚠️ DELETE Claude Code chat history after session
