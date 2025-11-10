#!/usr/bin/env python3
"""
Valuation Data Masking Script
Apprise Risk Solutions - P&T Team

Purpose: Mask PII in valuation data while preserving analytical utility
Compliance: ISO 27001:2022, ISMS 3, ISMS 16, Apprise AI Usage Policy

Usage:
    python mask_valuation_data.py --input Extract.csv --output masked_valuation_data.csv
    python mask_valuation_data.py --input Extract.csv --output masked_valuation_data.csv --dry-run
    python mask_valuation_data.py --input Extract.csv --output masked_valuation_data.csv --sample 1000
"""

import pandas as pd
import hashlib
import argparse
import sys
from pathlib import Path
from datetime import datetime
from faker import Faker
import json

# Initialize Faker with seed for deterministic results
fake = Faker()
Faker.seed(42)

# Global mapping dictionaries for deterministic masking
VALUER_MAP = {}
ACCOUNT_MAP = {}
ADDRESS_MAP = {}
JOB_ID_MAP = {}  # Track job ID mappings for referential integrity

# Generic bank names for account masking
GENERIC_BANKS = [
    'Bank_Alpha', 'Bank_Beta', 'Bank_Gamma', 'Bank_Delta',
    'Bank_Epsilon', 'Bank_Zeta', 'Bank_Eta', 'Bank_Theta',
    'Financial_Corp_A', 'Financial_Corp_B'
]


class ValuationDataMasker:
    """Masks sensitive PII in valuation data while preserving analytical value"""

    def __init__(self, preserve_mappings=True):
        """
        Initialize the masker

        Args:
            preserve_mappings: If True, saves mapping dictionaries to file (keep offline!)
        """
        self.preserve_mappings = preserve_mappings
        self.masked_count = 0
        self.error_count = 0

    def hash_id(self, id_value, use_job_map=False):
        """
        Completely hash IDs using SHA256

        When use_job_map=True, maintains referential integrity by using global JOB_ID_MAP

        Args:
            id_value: ID to hash (job number, ValEx ID, etc.)
            use_job_map: If True, uses JOB_ID_MAP for consistent mapping across files

        Returns:
            First 12 characters of SHA256 hash, or empty string if null
        """
        if pd.isna(id_value) or str(id_value).strip() == '':
            return ''

        id_clean = str(id_value).strip()

        # Use job map for referential integrity
        if use_job_map:
            if id_clean not in JOB_ID_MAP:
                # Create new mapping
                JOB_ID_MAP[id_clean] = hashlib.sha256(id_clean.encode()).hexdigest()[:12]
            return JOB_ID_MAP[id_clean]

        # SHA256 hash, take first 12 chars for readability
        return hashlib.sha256(id_clean.encode()).hexdigest()[:12]

    def mask_valuer_name(self, name):
        """
        Deterministically mask valuer names
        Same input always produces same output (preserves relationships)

        Args:
            name: Valuer name (e.g., "monique bourdon")

        Returns:
            Fake name (e.g., "Jessica Miller")
        """
        if pd.isna(name) or str(name).strip() == '':
            return ''

        name_clean = str(name).strip().lower()

        if name_clean not in VALUER_MAP:
            # Use hash of name to seed faker for consistency
            seed = int(hashlib.md5(name_clean.encode()).hexdigest()[:8], 16)
            fake_temp = Faker()
            fake_temp.seed(seed)
            VALUER_MAP[name_clean] = fake_temp.name()

        return VALUER_MAP[name_clean]

    def mask_account_name(self, account):
        """
        Deterministically mask account/client names to generic bank names

        Args:
            account: Account name (e.g., "anz", "westpac", "Commonwealth Bank of Australia")

        Returns:
            Generic bank name (e.g., "Bank_Alpha")
        """
        if pd.isna(account) or str(account).strip() == '':
            return ''

        account_clean = str(account).strip().lower()

        if account_clean not in ACCOUNT_MAP:
            # Use hash to deterministically select generic bank name
            seed = int(hashlib.md5(account_clean.encode()).hexdigest()[:8], 16)
            ACCOUNT_MAP[account_clean] = GENERIC_BANKS[seed % len(GENERIC_BANKS)]

        return ACCOUNT_MAP[account_clean]

    def mask_address_preserve_postcode(self, street_num, street_name, street_type,
                                        suburb, state, postcode):
        """
        Mask address components but preserve state and postcode for geographic analysis

        Args:
            street_num: Street number (e.g., "37")
            street_name: Street name (e.g., "CHAMBERLAIN")
            street_type: Street type (e.g., "Street")
            suburb: Suburb name (e.g., "CAMPBELLTOWN")
            state: State abbreviation (e.g., "NSW") - PRESERVED
            postcode: Postcode (e.g., "2560") - PRESERVED

        Returns:
            Tuple of (masked_street_num, masked_street_name, street_type, masked_suburb, state, postcode)
        """
        # Build key from identifiable parts
        address_key = f"{street_num}|{street_name}|{suburb}".lower()

        if address_key not in ADDRESS_MAP:
            # Generate consistent fake address components
            seed = int(hashlib.md5(address_key.encode()).hexdigest()[:8], 16)
            fake_temp = Faker()
            fake_temp.seed(seed)

            ADDRESS_MAP[address_key] = {
                'street_num': str(fake_temp.random_int(1, 999)),
                'street_name': fake_temp.last_name().upper(),  # Use surname as street name
                'suburb': fake_temp.city().upper()
            }

        masked = ADDRESS_MAP[address_key]

        return (
            masked['street_num'],
            masked['street_name'],
            street_type if not pd.isna(street_type) else '',  # Preserve street type (generic)
            masked['suburb'],
            state if not pd.isna(state) else '',  # PRESERVE state
            postcode if not pd.isna(postcode) else ''  # PRESERVE postcode
        )

    def mask_full_address(self, full_address, preserve_postcode=True):
        """
        Mask full address string while optionally preserving postcode

        Args:
            full_address: Full address string (e.g., "29 Little Road, BANKSTOWN, NSW 2200")
            preserve_postcode: If True, keeps the postcode at the end

        Returns:
            Masked address with postcode preserved
        """
        if pd.isna(full_address) or str(full_address).strip() == '':
            return ''

        addr_clean = str(full_address).strip()

        # Extract postcode (last 4 digits typically)
        import re
        postcode_match = re.search(r'\b(\d{4})\b(?!.*\d{4})', addr_clean)
        postcode = postcode_match.group(1) if postcode_match and preserve_postcode else None

        # Generate fake address
        address_key = addr_clean.lower()
        if address_key not in ADDRESS_MAP:
            seed = int(hashlib.md5(address_key.encode()).hexdigest()[:8], 16)
            fake_temp = Faker()
            fake_temp.seed(seed)
            fake_addr = fake_temp.address().replace('\n', ', ')
            ADDRESS_MAP[address_key] = fake_addr

        masked_addr = ADDRESS_MAP[address_key]

        # Append real postcode if preserving
        if postcode:
            # Remove any postcode from fake address and add real one
            masked_addr = re.sub(r'\b\d{4}\b', '', masked_addr).strip()
            masked_addr = f"{masked_addr} {postcode}"

        return masked_addr

    def validate_masking(self, original_df, masked_df):
        """
        Validate that masking was successful

        Args:
            original_df: Original dataframe
            masked_df: Masked dataframe

        Returns:
            Boolean indicating validation success
        """
        print("\n🔍 Validating masked data...")
        validation_passed = True

        # Check 1: Row count preserved
        if len(original_df) != len(masked_df):
            print(f"  ❌ Row count mismatch: {len(original_df)} → {len(masked_df)}")
            validation_passed = False
        else:
            print(f"  ✅ Row count preserved: {len(masked_df)} rows")

        # Check 2: Column count preserved
        if len(original_df.columns) != len(masked_df.columns):
            print(f"  ❌ Column count mismatch: {len(original_df.columns)} → {len(masked_df.columns)}")
            validation_passed = False
        else:
            print(f"  ✅ Column count preserved: {len(masked_df.columns)} columns")

        # Check 3: Sample original valuer names to ensure they're gone
        if 'valuer' in original_df.columns:
            sample_valuers = original_df['valuer'].dropna().unique()[:5]
            found_original = False
            for valuer in sample_valuers:
                if valuer and masked_df['valuer'].astype(str).str.contains(str(valuer), case=False, na=False).any():
                    print(f"  ❌ Original valuer name detected: {valuer}")
                    found_original = True
                    validation_passed = False

            if not found_original:
                print(f"  ✅ No original valuer names detected (checked {len(sample_valuers)} samples)")

        # Check 4: Sample original account names
        if 'account' in original_df.columns:
            sample_accounts = original_df['account'].dropna().unique()[:5]
            found_original = False
            for account in sample_accounts:
                if account and masked_df['account'].astype(str).str.contains(str(account), case=False, na=False).any():
                    print(f"  ❌ Original account name detected: {account}")
                    found_original = True
                    validation_passed = False

            if not found_original:
                print(f"  ✅ No original account names detected (checked {len(sample_accounts)} samples)")

        # Check 5: Verify postcodes are preserved
        if 'postcode_c' in original_df.columns and 'postcode_c' in masked_df.columns:
            orig_postcodes = set(original_df['postcode_c'].dropna().unique())
            masked_postcodes = set(masked_df['postcode_c'].dropna().unique())
            if orig_postcodes == masked_postcodes:
                print(f"  ✅ Postcodes preserved: {len(orig_postcodes)} unique postcodes")
            else:
                print(f"  ⚠️  Postcode sets differ (this may be intentional)")

        # Check 6: Verify values are preserved
        value_columns = ['estimateValue', 'marketValueCeiling', 'loanAmount']
        for col in value_columns:
            if col in original_df.columns:
                if original_df[col].equals(masked_df[col]):
                    print(f"  ✅ {col} values preserved exactly")
                else:
                    print(f"  ⚠️  {col} values differ (check if intentional)")

        # Check 7: Verify timestamps are preserved
        date_columns = ['openedDate', 'closedDate', 'weeknum', 'month']
        for col in date_columns:
            if col in original_df.columns:
                if original_df[col].equals(masked_df[col]):
                    print(f"  ✅ {col} timestamps preserved exactly")
                else:
                    print(f"  ⚠️  {col} dates differ (check if intentional)")

        return validation_passed

    def mask_dataframe(self, df):
        """
        Apply masking to entire dataframe

        Args:
            df: Input dataframe with sensitive data

        Returns:
            Masked dataframe
        """
        df_masked = df.copy()

        print("\n🔐 Masking sensitive fields...")

        # 1. Hash IDs (with referential integrity for job IDs)
        job_id_columns = ['jobNumber', 'Job Number', 'job_id', 'job_c']
        for col in job_id_columns:
            if col in df_masked.columns:
                print(f"  → Hashing {col} (maintaining referential integrity)...")
                df_masked[col] = df_masked[col].apply(lambda x: self.hash_id(x, use_job_map=True))

        if 'valExID' in df_masked.columns:
            print("  → Hashing valExID...")
            df_masked['valExID'] = df_masked['valExID'].apply(self.hash_id)

        # 2. Mask valuer names
        if 'valuer' in df_masked.columns:
            print("  → Masking valuer names...")
            df_masked['valuer'] = df_masked['valuer'].apply(self.mask_valuer_name)

        if 'valuerPeer' in df_masked.columns:
            print("  → Masking peer reviewer names...")
            df_masked['valuerPeer'] = df_masked['valuerPeer'].apply(self.mask_valuer_name)

        # 3. Mask account names
        if 'account' in df_masked.columns:
            print("  → Masking account names...")
            df_masked['account'] = df_masked['account'].apply(self.mask_account_name)

        # 4. Mask addresses (structured format - Extract.csv)
        address_cols = ['street_number_c', 'street_name_c', 'street_type_c',
                        'suburb_c', 'state_c', 'postcode_c']

        if all(col in df_masked.columns for col in address_cols):
            print("  → Masking structured addresses (preserving postcode & state)...")

            for idx, row in df_masked.iterrows():
                masked_addr = self.mask_address_preserve_postcode(
                    row['street_number_c'],
                    row['street_name_c'],
                    row['street_type_c'],
                    row['suburb_c'],
                    row['state_c'],
                    row['postcode_c']
                )

                df_masked.at[idx, 'street_number_c'] = masked_addr[0]
                df_masked.at[idx, 'street_name_c'] = masked_addr[1]
                df_masked.at[idx, 'street_type_c'] = masked_addr[2]
                df_masked.at[idx, 'suburb_c'] = masked_addr[3]
                df_masked.at[idx, 'state_c'] = masked_addr[4]
                df_masked.at[idx, 'postcode_c'] = masked_addr[5]

                # Progress indicator
                if (idx + 1) % 1000 == 0:
                    print(f"    ... processed {idx + 1} rows")

        # Also mask unit_number_c if present (part of address)
        if 'unit_number_c' in df_masked.columns:
            print("  → Masking unit numbers...")
            df_masked['unit_number_c'] = df_masked['unit_number_c'].apply(
                lambda x: str(fake.random_int(1, 999)) if not pd.isna(x) and str(x).strip() != '' else x
            )

        # 5. Mask full address field if present (report*.csv format)
        if 'Full Address' in df_masked.columns:
            print("  → Masking full addresses (preserving postcode)...")
            df_masked['Full Address'] = df_masked['Full Address'].apply(
                lambda x: self.mask_full_address(x, preserve_postcode=True)
            )

        # 6. Mask valuer names in other columns (report*.csv format)
        if 'Job Owner' in df_masked.columns:
            print("  → Masking Job Owner...")
            df_masked['Job Owner'] = df_masked['Job Owner'].apply(self.mask_valuer_name)

        if 'Job Original Valuer' in df_masked.columns:
            print("  → Masking Job Original Valuer...")
            df_masked['Job Original Valuer'] = df_masked['Job Original Valuer'].apply(self.mask_valuer_name)

        if 'Job Peer Reviewer' in df_masked.columns:
            print("  → Masking Job Peer Reviewer...")
            df_masked['Job Peer Reviewer'] = df_masked['Job Peer Reviewer'].apply(self.mask_valuer_name)

        # 7. Mask account in report format
        if 'Account Name' in df_masked.columns:
            print("  → Masking Account Name...")
            df_masked['Account Name'] = df_masked['Account Name'].apply(self.mask_account_name)

        # 8. Hash ValEx Job ID
        if 'ValEx Job ID' in df_masked.columns:
            print("  → Hashing ValEx Job ID...")
            df_masked['ValEx Job ID'] = df_masked['ValEx Job ID'].apply(self.hash_id)

        print(f"\n✅ Masking complete!")

        return df_masked

    def save_mappings(self, output_path):
        """
        Save mapping dictionaries to JSON file (KEEP OFFLINE!)

        Args:
            output_path: Path to save mappings
        """
        mappings = {
            'valuers': VALUER_MAP,
            'accounts': ACCOUNT_MAP,
            'job_ids': JOB_ID_MAP,
            'note': 'CONFIDENTIAL: Keep this file offline and secure. DO NOT commit to Git.',
            'created': datetime.now().isoformat()
        }

        with open(output_path, 'w') as f:
            json.dump(mappings, f, indent=2)

        print(f"\n💾 Mappings saved to: {output_path}")
        print("⚠️  WARNING: Keep this file offline and add to .claudeignore!")
        print(f"   Job IDs mapped: {len(JOB_ID_MAP)}")

    def mask_batch(self, file_configs):
        """
        Mask multiple related files while maintaining referential integrity

        Args:
            file_configs: List of dicts with 'input' and 'output' keys

        Returns:
            List of masked dataframes
        """
        print(f"\n🔗 BATCH MODE: Processing {len(file_configs)} related files")
        print("   Referential integrity will be maintained across all files")
        print()

        masked_dfs = []

        for i, config in enumerate(file_configs, 1):
            input_path = config['input']
            output_path = config['output']

            print(f"\n[{i}/{len(file_configs)}] Processing: {Path(input_path).name}")

            # Load data
            try:
                df = pd.read_csv(input_path, low_memory=False)
                print(f"   Loaded {len(df)} rows, {len(df.columns)} columns")
            except Exception as e:
                print(f"   ❌ Error loading: {e}")
                continue

            # Mask data (will use shared JOB_ID_MAP for referential integrity)
            df_masked = self.mask_dataframe(df)

            # Validate
            self.validate_masking(df, df_masked)

            # Save
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            df_masked.to_csv(output_path, index=False)
            print(f"   ✅ Saved to: {output_path}")

            masked_dfs.append(df_masked)

        print(f"\n✅ BATCH COMPLETE: {len(masked_dfs)} files processed")
        print(f"   Job ID mappings created: {len(JOB_ID_MAP)}")

        return masked_dfs

    def validate_referential_integrity(self, masked_dfs, df_names):
        """
        Validate that job IDs maintain referential integrity across masked files

        Args:
            masked_dfs: List of masked dataframes
            df_names: List of dataframe names for reporting

        Returns:
            Boolean indicating validation success
        """
        print("\n🔗 Validating referential integrity across files...")

        # Extract all job ID columns from all dataframes
        job_id_sets = {}
        job_id_columns = ['jobNumber', 'Job Number', 'job_id', 'job_c']

        for df, name in zip(masked_dfs, df_names):
            for col in job_id_columns:
                if col in df.columns:
                    job_ids = set(df[col].dropna().unique())
                    job_id_sets[f"{name}[{col}]"] = job_ids
                    print(f"   {name}[{col}]: {len(job_ids)} unique IDs")

        if len(job_id_sets) < 2:
            print("   ⚠️  Only one file with job IDs - cannot validate integrity")
            return True

        # Check for overlap
        keys = list(job_id_sets.keys())
        all_valid = True

        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                key1, key2 = keys[i], keys[j]
                set1, set2 = job_id_sets[key1], job_id_sets[key2]

                overlap = set1 & set2
                if overlap:
                    print(f"   ✅ {len(overlap)} overlapping IDs between {key1} and {key2}")
                else:
                    print(f"   ⚠️  No overlap between {key1} and {key2}")
                    all_valid = False

        return all_valid


def main():
    parser = argparse.ArgumentParser(
        description='Mask sensitive PII in valuation data files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python mask_valuation_data.py --input Extract.csv --output masked_data.csv

  # Dry run (preview only)
  python mask_valuation_data.py --input Extract.csv --output masked_data.csv --dry-run

  # Process sample only (for testing)
  python mask_valuation_data.py --input Extract.csv --output masked_sample.csv --sample 1000

  # Save mappings for reference (keep offline!)
  python mask_valuation_data.py --input Extract.csv --output masked_data.csv --save-mappings mappings.json

  # BATCH MODE: Maintain referential integrity across multiple files
  python mask_valuation_data.py --batch-config batch_config.json --save-mappings mappings.json

  # batch_config.json format:
  # {
  #   "files": [
  #     {"input": "personas_prototype.csv", "output": "personas_prototype_masked.csv"},
  #     {"input": "job_id_lookup.csv", "output": "job_id_lookup_masked.csv"},
  #     {"input": "raw_ext.csv", "output": "raw_ext_masked.csv"}
  #   ]
  # }
        """
    )

    parser.add_argument('--input', help='Input CSV file with sensitive data')
    parser.add_argument('--output', help='Output CSV file for masked data')
    parser.add_argument('--batch-config', help='JSON file with batch configuration for multiple related files')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without writing output')
    parser.add_argument('--sample', type=int, help='Process only first N rows (for testing)')
    parser.add_argument('--save-mappings', help='Save masking mappings to JSON file (keep offline!)')
    parser.add_argument('--validate-only', action='store_true', help='Only validate existing masked file')

    args = parser.parse_args()

    # Validate arguments
    if not args.batch_config and (not args.input or not args.output):
        parser.error("Either --batch-config OR (--input and --output) required")

    # BATCH MODE
    if args.batch_config:
        # Load batch configuration
        batch_config_path = Path(args.batch_config)
        if not batch_config_path.exists():
            print(f"❌ Error: Batch config file not found: {args.batch_config}")
            sys.exit(1)

        with open(batch_config_path, 'r') as f:
            batch_config = json.load(f)

        file_configs = batch_config.get('files', [])
        if not file_configs:
            print("❌ Error: No files specified in batch config")
            sys.exit(1)

        # Security warning
        print("=" * 70)
        print("🔒 VALUATION DATA MASKING TOOL - BATCH MODE")
        print("=" * 70)
        print("\n⚠️  SECURITY REMINDERS:")
        print("  1. Ensure .claudeignore excludes real data files")
        print("  2. DO NOT commit unmasked data to Git")
        print("  3. Verify masked output before use")
        print("  4. Delete Claude Code chat history after session")
        print("  5. Keep mapping files offline if generated")
        print()

        # Initialize masker
        masker = ValuationDataMasker()

        # Process batch
        masked_dfs = masker.mask_batch(file_configs)

        # Validate referential integrity
        df_names = [Path(config['input']).name for config in file_configs]
        integrity_valid = masker.validate_referential_integrity(masked_dfs, df_names)

        # Save mappings if requested
        if args.save_mappings:
            masker.save_mappings(args.save_mappings)

        # Final report
        print("\n" + "=" * 70)
        print("✅ BATCH MASKING COMPLETE")
        print("=" * 70)
        if integrity_valid:
            print("\n✅ Referential integrity maintained across all files")
        else:
            print("\n⚠️  WARNING: Some files have no overlapping job IDs")
        print(f"\n📋 NEXT STEPS:")
        print(f"  1. Verify masked data integrity")
        print(f"  2. Add unmasked files to .claudeignore")
        print(f"  3. NOW safe to use with Claude Code")
        print()

        sys.exit(0)

    # SINGLE FILE MODE
    # Check input file exists
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Error: Input file not found: {args.input}")
        sys.exit(1)

    # Security warning
    print("=" * 70)
    print("🔒 VALUATION DATA MASKING TOOL")
    print("=" * 70)
    print("\n⚠️  SECURITY REMINDERS:")
    print("  1. Ensure .claudeignore excludes real data files")
    print("  2. DO NOT commit unmasked data to Git")
    print("  3. Verify masked output before use")
    print("  4. Delete Claude Code chat history after session")
    print("  5. Keep mapping files offline if generated")
    print()

    # Load data
    print(f"📂 Loading data from: {args.input}")
    try:
        df = pd.read_csv(args.input, low_memory=False)
        print(f"  ✅ Loaded {len(df)} rows, {len(df.columns)} columns")
    except Exception as e:
        print(f"  ❌ Error loading file: {e}")
        sys.exit(1)

    # Sample if requested
    if args.sample:
        print(f"\n📊 Using sample: first {args.sample} rows")
        df = df.head(args.sample)

    # Show column preview
    print(f"\n📋 Columns in dataset:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i:2d}. {col}")

    # Initialize masker
    masker = ValuationDataMasker()

    # Mask data
    if not args.validate_only:
        df_masked = masker.mask_dataframe(df)

        # Validate
        validation_passed = masker.validate_masking(df, df_masked)

        if not validation_passed:
            print("\n⚠️  WARNING: Validation found issues. Review before using masked data.")

        # Show sample
        print("\n📊 Sample of masked data (first 3 rows, first 5 columns):")
        print(df_masked.head(3).iloc[:, :5].to_string())

        # Dry run check
        if args.dry_run:
            print("\n🔍 DRY RUN MODE: No files written")
            print(f"   Would have written {len(df_masked)} rows to: {args.output}")
        else:
            # Write output
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            print(f"\n💾 Writing masked data to: {args.output}")
            df_masked.to_csv(args.output, index=False)
            print(f"  ✅ Wrote {len(df_masked)} rows")

            # Save mappings if requested
            if args.save_mappings:
                masker.save_mappings(args.save_mappings)

            # Final reminders
            print("\n" + "=" * 70)
            print("✅ MASKING COMPLETE")
            print("=" * 70)
            print("\n📋 NEXT STEPS:")
            print(f"  1. Verify masked data: head {args.output}")
            print(f"  2. Add to .claudeignore: echo '{args.input}' >> .claudeignore")
            print(f"  3. Verify no PII: grep -i 'realname' {args.output}")
            print( "  4. NOW safe to use with Claude Code")
            print()

    else:
        # Validation only mode
        output_path = Path(args.output)
        if not output_path.exists():
            print(f"❌ Error: Output file not found for validation: {args.output}")
            sys.exit(1)

        df_masked = pd.read_csv(args.output, low_memory=False)
        validation_passed = masker.validate_masking(df, df_masked)

        if validation_passed:
            print("\n✅ Validation PASSED")
        else:
            print("\n❌ Validation FAILED")
            sys.exit(1)


if __name__ == '__main__':
    main()
