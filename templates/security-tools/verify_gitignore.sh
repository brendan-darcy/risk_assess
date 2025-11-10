#!/bin/bash
#
# Verify .gitignore Security Configuration
# Apprise Risk Solutions - P&T Team
#
# Purpose: Verify that sensitive files are properly excluded by .gitignore
# Usage: ./verify_gitignore.sh

set -e

echo "========================================================================"
echo "🔍 .gitignore Security Verification"
echo "========================================================================"
echo ""

PASS=0
FAIL=0
WARN=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_pass() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASS++))
}

print_fail() {
    echo -e "${RED}❌ $1${NC}"
    ((FAIL++))
}

print_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARN++))
}

# Check if .gitignore exists
if [ ! -f .gitignore ]; then
    print_fail ".gitignore file not found!"
    exit 1
fi

echo "🔍 Checking critical patterns..."
echo ""

# Check 1: Project examples folder
echo "1. Checking if 'docs - project examples/' is excluded..."
if git check-ignore -q "docs - project examples/" 2>/dev/null || grep -q "docs - project examples/" .gitignore; then
    print_pass "Project examples folder excluded"
else
    print_fail "Project examples folder NOT excluded (CRITICAL)"
    echo "   Add: docs - project examples/"
fi

# Check 2: CSV files
echo "2. Checking if CSV files are excluded..."
if grep -q "^\*\.csv" .gitignore; then
    print_pass "CSV files excluded"
else
    print_fail "CSV files NOT excluded"
    echo "   Add: *.csv"
fi

# Check 3: Excel files
echo "3. Checking if Excel files are excluded..."
if grep -q "^\*\.xlsx" .gitignore || grep -q "^\*\.xls" .gitignore; then
    print_pass "Excel files excluded"
else
    print_fail "Excel files NOT excluded"
    echo "   Add: *.xlsx and *.xls"
fi

# Check 4: Environment files
echo "4. Checking if .env files are excluded..."
if grep -q "^\.env" .gitignore; then
    print_pass "Environment files excluded"
else
    print_fail "Environment files NOT excluded"
    echo "   Add: .env"
fi

# Check 5: Credentials
echo "5. Checking if credentials files are excluded..."
if grep -q "credentials" .gitignore; then
    print_pass "Credentials patterns present"
else
    print_warn "Credentials patterns missing"
    echo "   Consider adding: credentials.json, *credentials*"
fi

# Check 6: AWS/Cloud configs
echo "6. Checking if AWS configs are excluded..."
if grep -q "\.aws" .gitignore || grep -q "\.databrickscfg" .gitignore; then
    print_pass "Cloud config patterns present"
else
    print_warn "Cloud config patterns missing"
    echo "   Consider adding: .aws/, .databrickscfg"
fi

# Check 7: Salesforce
echo "7. Checking if Salesforce files are excluded..."
if grep -q "\.sfdx" .gitignore || grep -q "\.salesforce" .gitignore; then
    print_pass "Salesforce patterns present"
else
    print_warn "Salesforce patterns missing"
    echo "   Consider adding: .sfdx/, .salesforce/"
fi

# Check 8: Masking artifacts
echo "8. Checking if masking artifacts are excluded..."
if grep -q "masking_mappings" .gitignore || grep -q "\*_mappings\.json" .gitignore; then
    print_pass "Masking artifact patterns present"
else
    print_warn "Masking artifact patterns missing"
    echo "   Consider adding: masking_mappings.json, *_mappings.json"
fi

# Check 9: Parquet files
echo "9. Checking if Parquet files are excluded..."
if grep -q "^\*\.parquet" .gitignore; then
    print_pass "Parquet files excluded"
else
    print_warn "Parquet files not excluded"
    echo "   Consider adding: *.parquet"
fi

# Check 10: Database files
echo "10. Checking if database files are excluded..."
if grep -q "\.db" .gitignore || grep -q "\.sqlite" .gitignore; then
    print_pass "Database file patterns present"
else
    print_warn "Database file patterns missing"
    echo "   Consider adding: *.db, *.sqlite"
fi

echo ""
echo "========================================================================"
echo "🔍 Checking for sensitive files in working directory..."
echo "========================================================================"
echo ""

# Find CSV files
echo "Searching for CSV files..."
CSV_COUNT=$(find . -name "*.csv" -type f 2>/dev/null | grep -v ".git" | wc -l | tr -d ' ')
if [ "$CSV_COUNT" -gt 0 ]; then
    print_warn "Found $CSV_COUNT CSV file(s)"
    echo "   Run: find . -name '*.csv' -type f | grep -v '.git'"
    echo "   Verify these are masked/dummy data or excluded by .gitignore"
else
    print_pass "No CSV files found in working directory"
fi

# Find Excel files
echo "Searching for Excel files..."
EXCEL_COUNT=$(find . \( -name "*.xlsx" -o -name "*.xls" \) -type f 2>/dev/null | grep -v ".git" | wc -l | tr -d ' ')
if [ "$EXCEL_COUNT" -gt 0 ]; then
    print_warn "Found $EXCEL_COUNT Excel file(s)"
    echo "   Run: find . -name '*.xlsx' -o -name '*.xls' | grep -v '.git'"
    echo "   Verify these are excluded by .gitignore"
else
    print_pass "No Excel files found in working directory"
fi

# Check for project examples folder
echo "Checking if project examples folder exists..."
if [ -d "docs - project examples" ]; then
    print_warn "Project examples folder exists (contains real data)"
    # Check if it's properly ignored
    if git check-ignore -q "docs - project examples/" 2>/dev/null; then
        print_pass "Project examples is properly excluded by .gitignore"
    else
        print_fail "Project examples NOT excluded by .gitignore (CRITICAL)"
    fi
else
    print_pass "No project examples folder found"
fi

# Find potential credential files
echo "Searching for credential files..."
CRED_COUNT=$(find . \( -name "*credential*" -o -name "*secret*" -o -name "*.pem" -o -name ".env.*" \) -type f 2>/dev/null | grep -v ".git" | grep -v ".gitignore" | grep -v "node_modules" | wc -l | tr -d ' ')
if [ "$CRED_COUNT" -gt 0 ]; then
    print_warn "Found $CRED_COUNT potential credential file(s)"
    echo "   Run: find . \( -name '*credential*' -o -name '*secret*' \) | grep -v '.git'"
    echo "   Verify these are excluded by .gitignore"
else
    print_pass "No credential files found"
fi

echo ""
echo "========================================================================"
echo "🔍 Checking Git status..."
echo "========================================================================"
echo ""

# Check if there are untracked sensitive files
echo "Checking for untracked sensitive files..."
UNTRACKED=$(git status --porcelain 2>/dev/null | grep "^??" | grep -E "\.(csv|xlsx|xls|db|env|parquet)$" | wc -l | tr -d ' ')
if [ "$UNTRACKED" -gt 0 ]; then
    print_warn "Found $UNTRACKED untracked sensitive file(s)"
    echo "   Run: git status --porcelain | grep '^??'"
    echo "   Review these files before committing"
else
    print_pass "No untracked sensitive files"
fi

# Check if there are staged sensitive files
echo "Checking for staged sensitive files..."
STAGED=$(git status --porcelain 2>/dev/null | grep -E "^(A|M)" | grep -E "\.(csv|xlsx|xls|db|env|parquet)$" | wc -l | tr -d ' ')
if [ "$STAGED" -gt 0 ]; then
    print_fail "Found $STAGED staged sensitive file(s) (CRITICAL)"
    echo "   Run: git status"
    echo "   Unstage these files: git reset HEAD <file>"
else
    print_pass "No staged sensitive files"
fi

echo ""
echo "========================================================================"
echo "📊 Summary"
echo "========================================================================"
echo ""
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo "Warnings: $WARN"
echo ""

if [ $FAIL -gt 0 ]; then
    echo "========================================================================"
    echo -e "${RED}❌ VERIFICATION FAILED${NC}"
    echo "========================================================================"
    echo ""
    echo "Critical issues found. Review failures above and update .gitignore."
    echo ""
    echo "Recommended action:"
    echo "  1. Review .gitignore.recommended"
    echo "  2. Update .gitignore: cp .gitignore.recommended .gitignore"
    echo "  3. Run this script again"
    echo ""
    exit 1
elif [ $WARN -gt 0 ]; then
    echo "========================================================================"
    echo -e "${YELLOW}⚠️  VERIFICATION PASSED WITH WARNINGS${NC}"
    echo "========================================================================"
    echo ""
    echo "Review warnings above and consider updating .gitignore."
    echo ""
    exit 0
else
    echo "========================================================================"
    echo -e "${GREEN}✅ VERIFICATION PASSED${NC}"
    echo "========================================================================"
    echo ""
    echo ".gitignore appears to be properly configured!"
    echo ""
    exit 0
fi
