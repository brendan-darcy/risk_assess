# Pre-Flight Security Check Usage

## What It Does

The `pre-flight-check.sh` script **automates the security checklist verification** before every Claude Code session. It checks for common security issues that could lead to data exposure.

---

## Quick Start

### 1. Run Before Every Claude Code Session

```bash
cd /path/to/your/project
./path/to/pre-flight-check.sh
```

**If you get "Permission denied":**
```bash
chmod +x pre-flight-check.sh
./pre-flight-check.sh
```

### 2. Fix Any Issues It Finds

The script will show you:
- ✅ What passed (green checkmarks)
- ❌ What failed (red X's) - **MUST FIX**
- ⚠️  Warnings (yellow) - **REVIEW**

### 3. Only Use Claude Code If Check Passes

- ✅ **Green "PRE-FLIGHT CHECK PASSED"** → Safe to proceed
- ⚠️  **Yellow "PASSED WITH WARNINGS"** → Review warnings, proceed with caution
- ❌ **Red "FAILED"** → **DO NOT use Claude Code** until fixed

---

## What It Checks

### ✅ Automated Checks

1. **`.claudeignore` exists** with required patterns:
   - `**/*.csv` (CSV files with potential PII)
   - `**/data/**` (data folders)
   - `**/*.env` (environment files)
   - `credentials.json` (credential files)

2. **Git branch** - Not on main/master (should be dev/feature branch)

3. **Sensitive files** in working directory:
   - CSV files (potential valuation/survey data with PII)
   - .env files (potential credentials)
   - credentials.json or similar

4. **Environment indicators** - Working directory suggests dev/test (not production)

### 🤚 Manual Verification (You Still Need To Check)

The script reminds you to verify:
- [ ] Using dummy/synthetic data ONLY (no client/production data)
- [ ] Working in Dev/Sandbox environment
- [ ] Will delete Claude Code chat history after session
- [ ] Team aware of AI tool usage (if applicable)

---

## Example Output

### ✅ PASS Example

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔒  Claude Code Pre-Flight Security Check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Running security checks...

🔍 Checking .claudeignore configuration...
✅ .claudeignore file exists
✅ Pattern '**/*.csv' found in .claudeignore
✅ Pattern '**/data/**' found in .claudeignore
✅ Pattern '**/*.env' found in .claudeignore
✅ Pattern 'credentials.json' found in .claudeignore

🔍 Checking Git branch...
✅ On 'dev/data-analysis' branch (not main/master)

🔍 Checking for sensitive files...
✅ No CSV files in working directory
✅ No .env files found

🔍 Checking environment indicators...
✅ Working directory suggests dev/test environment

🔍 Checking for credential files...
✅ No credential files found

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Passed: 10
Failed: 0
Warnings: 0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✋ Manual Verification Required
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Before using Claude Code, verify:

  [ ] Using dummy/synthetic data ONLY
  [ ] Working in Dev/Sandbox environment
  [ ] Will delete chat history after session

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ PRE-FLIGHT CHECK PASSED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Safe to use Claude Code. Happy coding! 🚀
```

### ❌ FAIL Example

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔒  Claude Code Pre-Flight Security Check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 Checking .claudeignore configuration...
❌ .claudeignore file NOT FOUND

ℹ️  Create .claudeignore with these patterns:
    **/*.csv
    **/data/**
    **/*.env
    credentials.json

🔍 Checking Git branch...
❌ Currently on 'main' branch - switch to dev/feature branch
ℹ️  Run: git checkout -b dev/claude-code-session

🔍 Checking for sensitive files...
⚠️  Found 3 CSV file(s) in working directory
ℹ️  Ensure these are dummy data ONLY

ℹ️  Found CSV files:
    ./data/valuation_export_oct2025.csv
    ./data/survey_responses.csv
    ./reports/completion_analysis.csv

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Passed: 2
Failed: 2
Warnings: 1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ PRE-FLIGHT CHECK FAILED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Fix the issues above before using Claude Code.
```

---

## Common Issues & Fixes

### Issue 1: `.claudeignore` Missing

**Error:**
```
❌ .claudeignore file NOT FOUND
```

**Fix:**
```bash
# Copy the template
cp templates/pt-team/.claudeignore.template .claudeignore

# Or create manually with required patterns:
cat > .claudeignore <<EOF
**/*.csv
**/data/**
**/*.env
credentials.json
node_modules/
__pycache__/
*.pyc
.DS_Store
EOF
```

### Issue 2: On main/master Branch

**Error:**
```
❌ Currently on 'main' branch
```

**Fix:**
```bash
# Create and switch to dev branch
git checkout -b dev/claude-code-session

# Or switch to existing dev branch
git checkout dev
```

### Issue 3: CSV Files Found

**Warning:**
```
⚠️  Found 3 CSV file(s) in working directory
```

**Fix:**

**Option A - If Dummy Data:**
- ✅ Proceed (it's safe if dummy/synthetic data)
- Verify these are NOT production exports

**Option B - If Real Data:**
- ❌ Delete or move to secure location
- Regenerate as synthetic data instead

**Option C - Add to .claudeignore:**
```bash
echo "data/*.csv" >> .claudeignore
```

### Issue 4: Environment Unclear

**Warning:**
```
⚠️  Cannot determine environment from directory name
```

**Fix:**
- Manually verify you're in Dev/Sandbox
- Rename directory to include "dev" or "sandbox" for clarity:
  ```bash
  cd ..
  mv myproject myproject-dev
  cd myproject-dev
  ```

---

## Integration with Workflow

### Recommended Workflow

```bash
# 1. Run pre-flight check
./templates/pt-team/pre-flight-check.sh

# 2. If passed, open template
code templates/pt-team/workflows/data_analyst_csv.md

# 3. Craft your prompt (reference template)
# Example:
# "Using data_analyst_csv.md template, analyze data/synthetic_valuations.csv..."

# 4. Use Claude Code

# 5. After session, delete chat history
```

### Make It Convenient

**Option 1: Add alias to your shell**

```bash
# Add to ~/.zshrc or ~/.bashrc
alias claude-check="./templates/pt-team/pre-flight-check.sh"

# Then just run:
claude-check
```

**Option 2: Create a wrapper script**

```bash
#!/bin/bash
# claude-code-start.sh

# Run pre-flight check
./templates/pt-team/pre-flight-check.sh

# If passed, open VS Code (optional)
if [ $? -eq 0 ]; then
    code .
fi
```

**Option 3: Git pre-commit hook** (prevent accidental commits)

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Check for sensitive files before commit
if [ -f templates/pt-team/pre-flight-check.sh ]; then
    ./templates/pt-team/pre-flight-check.sh --quiet
    if [ $? -ne 0 ]; then
        echo "Pre-flight check failed. Fix issues before committing."
        exit 1
    fi
fi
```

---

## Limitations

### What It CANNOT Check

- ❌ Whether CSVs contain real vs dummy data (you verify)
- ❌ Whether you're connected to production database (you verify)
- ❌ Whether you'll remember to delete chat history (you do it)
- ❌ Whether data is client data vs internal data (you know)

### What It DOES Check

- ✅ .claudeignore configuration
- ✅ Git branch
- ✅ File presence (CSVs, .env, credentials)
- ✅ Directory name indicators

---

## Customization

### Add Custom Checks

Edit `pre-flight-check.sh` and add your own checks:

```bash
# Example: Check for specific file patterns
echo "🔍 Checking for production config..."
if [ -f config/production.yml ]; then
    print_fail "production.yml found - should not exist in dev!"
else
    print_pass "No production config found"
fi
```

### Skip Specific Checks

Comment out checks you don't need:

```bash
# Skip CSV check if you frequently work with dummy CSVs
# CSV_COUNT=$(find . -type f -name "*.csv" ...)
```

---

## FAQ

**Q: Do I have to run this every time?**
A: Yes! It takes 2 seconds and prevents accidentally exposing sensitive data.

**Q: What if I get warnings but need to proceed?**
A: Review the warnings. If you're confident they're safe (e.g., dummy CSV files), you can proceed. Script exits with success code for warnings.

**Q: Can I automate the manual checks too?**
A: No - some things require human judgment (is this dummy data? am I in dev environment?).

**Q: What if I'm not using Git?**
A: The Git check will show a warning but won't fail. Other checks still run.

**Q: Can this replace the template security checklists?**
A: No - this automates what CAN be automated. You still verify the manual items.

---

## Support

**Issues with the script?**
- Check file permissions: `chmod +x pre-flight-check.sh`
- Check shell: Script requires bash (not sh)
- Check working directory: Run from project root

**Script doesn't detect something?**
- File an issue or add custom checks
- Remember: Some things require manual verification

---

## Remember

🔒 **The pre-flight check is a safety net, not a guarantee.**

**You are still responsible for**:
- Verifying data is dummy/synthetic
- Working in correct environment
- Deleting chat history after sessions
- Following Apprise security policies

**When in doubt, DON'T use Claude Code with the data.**

