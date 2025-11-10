# Batch Masking with Referential Integrity

## Problem Statement

When masking multiple related CSV files independently, **referential integrity is broken**:

```
personas_prototype.csv:  jobNumber = "12345"  →  masked: "a1b2c3d4e5f6"
job_id_lookup.csv:       job_id = "12345"      →  masked: "x9y8z7w6v5u4"  ❌ DIFFERENT!
raw_ext.csv:             job_c = "12345"       →  masked: "p0o9i8u7y6t5"  ❌ DIFFERENT!
```

This breaks joins and causes pipelines to fail silently (0 results).

## Solution: Batch Mode

The `mask_valuation_data.py` script now supports **batch mode** which maintains referential integrity by using a **shared mapping** for job IDs across all files:

```
personas_prototype.csv:  jobNumber = "12345"  →  masked: "a1b2c3d4e5f6"
job_id_lookup.csv:       job_id = "12345"      →  masked: "a1b2c3d4e5f6"  ✅ SAME!
raw_ext.csv:             job_c = "12345"       →  masked: "a1b2c3d4e5f6"  ✅ SAME!
```

## Usage

### 1. Create a Batch Configuration File

Create `batch_config.json`:

```json
{
  "files": [
    {
      "input": "personas_prototype.csv",
      "output": "personas_prototype_masked.csv"
    },
    {
      "input": "job_id_lookup.csv",
      "output": "job_id_lookup_masked.csv"
    },
    {
      "input": "raw_ext.csv",
      "output": "raw_ext_masked.csv"
    }
  ]
}
```

### 2. Run Batch Masking

```bash
python mask_valuation_data.py \\
  --batch-config batch_config.json \\
  --save-mappings job_id_mappings.json
```

### 3. Verify Referential Integrity

The script automatically validates that job IDs maintain consistency:

```
🔗 Validating referential integrity across files...
   personas_prototype.csv[jobNumber]: 145 unique IDs
   job_id_lookup.csv[job_id]: 145 unique IDs
   raw_ext.csv[job_c]: 145 unique IDs
   ✅ 145 overlapping IDs between personas_prototype.csv[jobNumber] and job_id_lookup.csv[job_id]
   ✅ 145 overlapping IDs between personas_prototype.csv[jobNumber] and raw_ext.csv[job_c]
   ✅ 145 overlapping IDs between job_id_lookup.csv[job_id] and raw_ext.csv[job_c]
```

## Supported Job ID Column Names

The script automatically detects these columns as job IDs:
- `jobNumber`
- `Job Number`
- `job_id`
- `job_c`

All will use the same mapping for referential integrity.

## Example: Dual Occupancy Pipeline

```bash
# 1. Create batch config
cat > batch_config.json <<EOF
{
  "files": [
    {"input": "personas_prototype.csv", "output": "personas_prototype_masked.csv"},
    {"input": "job_id_lookup.csv", "output": "job_id_lookup_masked.csv"},
    {"input": "raw_ext.csv", "output": "raw_ext_masked.csv"}
  ]
}
EOF

# 2. Mask all files while maintaining referential integrity
python mask_valuation_data.py \\
  --batch-config batch_config.json \\
  --save-mappings mappings.json

# 3. Run your pipeline with masked data
python dual_occupancy_pipeline.py \\
  --personas personas_prototype_masked.csv \\
  --lookup job_id_lookup_masked.csv \\
  --raw raw_ext_masked.csv
```

## Single File Mode (Still Supported)

For single files without referential integrity requirements:

```bash
python mask_valuation_data.py \\
  --input Extract.csv \\
  --output masked_Extract.csv
```

## Security Notes

1. **Mapping files** (`mappings.json`) contain real-to-fake ID mappings - **KEEP OFFLINE**
2. Add to `.claudeignore`:
   ```
   *mappings*.json
   batch_config.json
   ```
3. Original unmaksed files should already be in `.claudeignore`

## Benefits

✅ **Referential Integrity** - Joins work correctly
✅ **Pipeline Robustness** - No silent failures (0 results)
✅ **Data Consistency** - Same job ID always maps to same masked ID
✅ **Validation Built-in** - Automatic integrity checks
✅ **Audit Trail** - Mappings saved for reference (keep offline!)

## Troubleshooting

### No overlapping IDs detected

```
⚠️  No overlap between file1.csv[job_id] and file2.csv[job_id]
```

**Cause**: Files have different job IDs (not related)
**Solution**: This may be expected if files aren't meant to join

### Pipeline still returns 0 results

**Possible causes**:
1. Check column names match (e.g., `job_id` vs `job_c`)
2. Verify files processed in batch mode (not individually)
3. Check join keys in your pipeline code

### Mapping file too large

**Solution**: Batch mode processes files sequentially, keeping only necessary mappings in memory

## Advanced: Custom ID Columns

If you have custom ID column names, they'll be hashed individually (no referential integrity). To add support:

1. Edit `mask_valuation_data.py`
2. Add your column name to `job_id_columns` list:
   ```python
   job_id_columns = ['jobNumber', 'Job Number', 'job_id', 'job_c', 'YOUR_COLUMN_NAME']
   ```

## Support

For questions, contact the P&T Team or see [MASKING_USAGE.md](../docs/MASKING_USAGE.md) for general masking guidance.
