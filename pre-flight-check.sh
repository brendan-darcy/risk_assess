#!/bin/bash

# Claude Code Pre-Flight Security Check
# Run this before every Claude Code session to verify security requirements

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🔒  Claude Code Pre-Flight Security Check${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

CHECKS_PASSED=0
CHECKS_FAILED=0
WARNINGS=0

# Function to print success
print_pass() {
    echo -e "${GREEN}✅ $1${NC}"
    ((CHECKS_PASSED++))
}

# Function to print failure
print_fail() {
    echo -e "${RED}❌ $1${NC}"
    ((CHECKS_FAILED++))
}

# Function to print warning
print_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNINGS++))
}

# Function to print info
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

echo "Running security checks..."
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECK 1: .claudeignore file exists
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "🔍 Checking .claudeignore configuration..."

# Check both .claudeignore and .claude/.claudeignore
CLAUDEIGNORE_PATH=""
if [ -f .claude/.claudeignore ]; then
    CLAUDEIGNORE_PATH=".claude/.claudeignore"
elif [ -f .claudeignore ]; then
    CLAUDEIGNORE_PATH=".claudeignore"
fi

if [ -n "$CLAUDEIGNORE_PATH" ]; then
    print_pass ".claudeignore file exists at $CLAUDEIGNORE_PATH"

    # Check for required patterns
    REQUIRED_PATTERNS=(
        "**/*.csv"
        "**/data/**"
        "**/*.env"
        "credentials.json"
    )

    MISSING_PATTERNS=()

    for pattern in "${REQUIRED_PATTERNS[@]}"; do
        if grep -Fq "$pattern" "$CLAUDEIGNORE_PATH"; then
            print_pass "Pattern '$pattern' found in .claudeignore"
        else
            print_fail "Pattern '$pattern' MISSING from .claudeignore"
            MISSING_PATTERNS+=("$pattern")
        fi
    done

    if [ ${#MISSING_PATTERNS[@]} -gt 0 ]; then
        echo ""
        print_info "Add these patterns to your $CLAUDEIGNORE_PATH:"
        for pattern in "${MISSING_PATTERNS[@]}"; do
            echo "    $pattern"
        done
    fi
else
    print_fail ".claudeignore file NOT FOUND (checked .claude/.claudeignore and .claudeignore)"
    echo ""
    print_info "Create .claude/.claudeignore with these patterns:"
    echo "    **/*.csv"
    echo "    **/data/**"
    echo "    **/*.env"
    echo "    credentials.json"
    echo "    node_modules/"
    echo "    __pycache__/"
fi

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECK 2: .gitignore file exists
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "🔍 Checking .gitignore configuration..."

if [ -f .gitignore ]; then
    print_pass ".gitignore file exists"

    # Check for required patterns
    GITIGNORE_PATTERNS=(
        ".env"
        "*.csv"
        "credentials.json"
        "node_modules/"
        "__pycache__/"
    )

    MISSING_GIT_PATTERNS=()

    for pattern in "${GITIGNORE_PATTERNS[@]}"; do
        # Use grep -F for literal string matching, handle wildcards
        if grep -q "^${pattern}" .gitignore || grep -q "^${pattern//\*/.\*}" .gitignore; then
            print_pass "Pattern '$pattern' found in .gitignore"
        else
            print_warn "Pattern '$pattern' MISSING from .gitignore"
            MISSING_GIT_PATTERNS+=("$pattern")
        fi
    done

    if [ ${#MISSING_GIT_PATTERNS[@]} -gt 0 ]; then
        echo ""
        print_info "Consider adding these patterns to .gitignore:"
        for pattern in "${MISSING_GIT_PATTERNS[@]}"; do
            echo "    $pattern"
        done
    fi
else
    print_fail ".gitignore file NOT FOUND"
    echo ""
    print_info "Create .gitignore with these patterns:"
    echo "    .env"
    echo "    .env.*"
    echo "    *.csv"
    echo "    credentials.json"
    echo "    node_modules/"
    echo "    __pycache__/"
fi

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECK 3: Git branch (should not be on main/master)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "🔍 Checking Git branch..."

if git rev-parse --git-dir > /dev/null 2>&1; then
    BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")

    if [[ "$BRANCH" == "main" || "$BRANCH" == "master" ]]; then
        print_fail "Currently on '$BRANCH' branch - switch to dev/feature branch"
        print_info "Run: git checkout -b dev/claude-code-session"
    else
        print_pass "On '$BRANCH' branch (not main/master)"
    fi
else
    print_warn "Not a Git repository"
fi

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECK 4: Look for sensitive files in working directory
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "🔍 Checking for sensitive files..."

# Check for CSV files (potential PII)
CSV_COUNT=$(find . -type f -name "*.csv" ! -path "*/_extracted_archive/*" ! -path "*/node_modules/*" ! -path "*/.git/*" 2>/dev/null | wc -l | tr -d ' ')

if [ "$CSV_COUNT" -gt 0 ]; then
    print_warn "Found $CSV_COUNT CSV file(s) in working directory"
    print_info "Ensure these are dummy data ONLY (no client/production data)"
    echo ""
    print_info "Found CSV files:"
    find . -type f -name "*.csv" ! -path "*/_extracted_archive/*" ! -path "*/node_modules/*" ! -path "*/.git/*" 2>/dev/null | head -10 | while read file; do
        echo "    $file"
    done
else
    print_pass "No CSV files in working directory"
fi

echo ""

# Check for .env files (potential credentials)
ENV_COUNT=$(find . -type f -name ".env*" ! -path "*/node_modules/*" ! -path "*/.git/*" 2>/dev/null | wc -l | tr -d ' ')

if [ "$ENV_COUNT" -gt 0 ]; then
    print_warn "Found $ENV_COUNT .env file(s)"
    print_info "Verify these contain NO real credentials (use .env.example for templates)"
else
    print_pass "No .env files found"
fi

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECK 5: Environment indicators
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "🔍 Checking environment indicators..."

# Check for dev/sandbox indicators in directory name
PWD_LOWER=$(pwd | tr '[:upper:]' '[:lower:]')

if [[ "$PWD_LOWER" == *"dev"* || "$PWD_LOWER" == *"sandbox"* || "$PWD_LOWER" == *"test"* ]]; then
    print_pass "Working directory suggests dev/test environment"
elif [[ "$PWD_LOWER" == *"prod"* || "$PWD_LOWER" == *"production"* ]]; then
    print_fail "Working directory suggests PRODUCTION environment!"
    print_info "Do NOT use Claude Code in production directories"
else
    print_warn "Cannot determine environment from directory name"
    print_info "Manually verify you're in Dev/Sandbox environment"
fi

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECK 6: Check for credentials.json or similar
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "🔍 Checking for credential files..."

CRED_FILES=$(find . -type f \( -name "credentials.json" -o -name "credentials.yml" -o -name "secrets.json" \) ! -path "*/node_modules/*" ! -path "*/.git/*" 2>/dev/null | wc -l | tr -d ' ')

if [ "$CRED_FILES" -gt 0 ]; then
    print_fail "Found credential file(s) - ensure these are in .claudeignore!"
    find . -type f \( -name "credentials.json" -o -name "credentials.yml" -o -name "secrets.json" \) ! -path "*/node_modules/*" ! -path "*/.git/*" 2>/dev/null | while read file; do
        echo "    $file"
    done
else
    print_pass "No credential files found"
fi

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECK 7: Hardcoded secrets in code
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "🔍 Checking for hardcoded secrets in code..."

# Common secret patterns (case insensitive)
HARDCODED_SECRETS=$(grep -rniE "(api[_-]?key|password|secret|token|aws_access_key_id)\s*=\s*['\"][^'\"]{8,}['\"]" \
    --include="*.py" --include="*.js" --include="*.ts" --include="*.java" --include="*.go" --include="*.rb" --include="*.php" \
    ! -path "*/node_modules/*" ! -path "*/.git/*" ! -path "*/__pycache__/*" ! -path "*/venv/*" ! -path "*/.venv/*" \
    . 2>/dev/null | wc -l | tr -d ' ')

# Check for AWS keys
AWS_KEYS=$(grep -rE "AKIA[0-9A-Z]{16}" \
    --include="*.py" --include="*.js" --include="*.ts" --include="*.java" --include="*.go" --include="*.rb" --include="*.php" --include="*.txt" \
    ! -path "*/node_modules/*" ! -path "*/.git/*" \
    . 2>/dev/null | wc -l | tr -d ' ')

# Check for OpenAI/Anthropic API keys
AI_KEYS=$(grep -rE "(sk-[a-zA-Z0-9]{32,}|claude-[a-zA-Z0-9]{32,})" \
    --include="*.py" --include="*.js" --include="*.ts" --include="*.txt" \
    ! -path "*/node_modules/*" ! -path "*/.git/*" \
    . 2>/dev/null | wc -l | tr -d ' ')

TOTAL_SECRETS=$((HARDCODED_SECRETS + AWS_KEYS + AI_KEYS))

if [ "$TOTAL_SECRETS" -gt 0 ]; then
    print_fail "Found $TOTAL_SECRETS potential hardcoded secret(s) in code"

    if [ "$HARDCODED_SECRETS" -gt 0 ]; then
        echo "    ⚠️  $HARDCODED_SECRETS hardcoded API keys/passwords/tokens"
    fi
    if [ "$AWS_KEYS" -gt 0 ]; then
        echo "    ⚠️  $AWS_KEYS AWS access keys (AKIA...)"
    fi
    if [ "$AI_KEYS" -gt 0 ]; then
        echo "    ⚠️  $AI_KEYS AI API keys (sk-...)"
    fi

    echo ""
    print_info "Store secrets in .env file instead:"
    echo "    # .env"
    echo "    API_KEY=your_key_here"
    echo ""
    echo "    # code.py"
    echo "    import os"
    echo "    api_key = os.getenv('API_KEY')"
else
    print_pass "No obvious hardcoded secrets found"
fi

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECK 8: Database connection strings
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "🔍 Checking for hardcoded database connections..."

DB_STRINGS=$(grep -rniE "(postgres|mysql|mongodb|mssql)://[^:]+:[^@]+@|(host|server)\s*=.*(password|pwd)\s*=" \
    --include="*.py" --include="*.js" --include="*.ts" --include="*.java" --include="*.yml" --include="*.yaml" --include="*.conf" \
    ! -path "*/node_modules/*" ! -path "*/.git/*" ! -path "*/__pycache__/*" \
    . 2>/dev/null | wc -l | tr -d ' ')

if [ "$DB_STRINGS" -gt 0 ]; then
    print_fail "Found $DB_STRINGS potential hardcoded database connection(s)"
    print_info "Use environment variables for DB credentials"
    echo "    # .env"
    echo "    DATABASE_URL=postgres://user:pass@localhost/db"
    echo ""
    echo "    # code"
    echo "    db_url = os.getenv('DATABASE_URL')"
else
    print_pass "No hardcoded database connections found"
fi

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECK 9: .env.example file (best practice)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "🔍 Checking for .env.example (best practice)..."

if [ -f .env.example ] || [ -f .env.template ]; then
    print_pass ".env.example exists (good practice)"
elif [ -f .env ]; then
    print_warn ".env exists but no .env.example"
    print_info "Create .env.example with dummy values for team reference:"
    echo "    cp .env .env.example"
    echo "    # Then replace real values with placeholders"
else
    print_pass "No .env file (not needed for this project)"
fi

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECK 10: Uncommitted changes
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "🔍 Checking for uncommitted changes..."

if git rev-parse --git-dir > /dev/null 2>&1; then
    UNCOMMITTED=$(git status --porcelain | wc -l | tr -d ' ')

    if [ "$UNCOMMITTED" -gt 0 ]; then
        print_warn "You have $UNCOMMITTED uncommitted change(s)"
        print_info "Consider committing work before AI session (easier rollback)"
    else
        print_pass "Working directory clean"
    fi
fi

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECK 11: Large files
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "🔍 Checking for large files (>50MB)..."

LARGE_FILES=$(find . -type f -size +50M ! -path "*/.git/*" ! -path "*/node_modules/*" ! -path "*/__pycache__/*" 2>/dev/null | wc -l | tr -d ' ')

if [ "$LARGE_FILES" -gt 0 ]; then
    print_warn "Found $LARGE_FILES file(s) over 50MB"
    echo ""
    print_info "Large files found:"
    find . -type f -size +50M ! -path "*/.git/*" ! -path "*/node_modules/*" 2>/dev/null | head -5 | while read file; do
        size=$(du -h "$file" | cut -f1)
        echo "    $file ($size)"
    done
    echo ""
    print_info "Large files should be in .claudeignore to avoid sending to AI"
else
    print_pass "No large files found"
fi

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECK 12: Production URLs/IPs
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "🔍 Checking for production URLs/IPs..."

# Check for production-like URLs
PROD_URLS=$(grep -rniE "(prod|production)\..*\.(com|io|net|au)|api\..*\.com|https?://[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+" \
    --include="*.py" --include="*.js" --include="*.ts" --include="*.yml" --include="*.yaml" --include="*.json" --include="*.conf" \
    ! -path "*/node_modules/*" ! -path "*/.git/*" ! -path "*/__pycache__/*" ! -path "*/package-lock.json/*" \
    . 2>/dev/null | wc -l | tr -d ' ')

if [ "$PROD_URLS" -gt 0 ]; then
    print_warn "Found $PROD_URLS reference(s) to production-like URLs"
    print_info "Verify these are not pointing to live production systems"
    echo "    Use environment variables for environment-specific URLs"
else
    print_pass "No production URLs detected"
fi

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SUMMARY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📊 Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}Passed: $CHECKS_PASSED${NC}"
echo -e "${RED}Failed: $CHECKS_FAILED${NC}"
echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MANUAL CHECKLIST REMINDER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}✋ Manual Verification Required${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Before using Claude Code, verify:"
echo ""
echo "  [ ] Using dummy/synthetic data ONLY (no client/production data)"
echo "  [ ] Working in Dev/Sandbox environment (not production)"
echo "  [ ] Will delete Claude Code chat history after session"
echo "  [ ] Team members aware of AI tool usage (if applicable)"
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DECISION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if [ $CHECKS_FAILED -gt 0 ]; then
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ PRE-FLIGHT CHECK FAILED${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${RED}Fix the issues above before using Claude Code.${NC}"
    echo ""
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}⚠️  PRE-FLIGHT CHECK PASSED WITH WARNINGS${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${YELLOW}Review warnings above and proceed with caution.${NC}"
    echo ""
    exit 0
else
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ PRE-FLIGHT CHECK PASSED${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${GREEN}Safe to use Claude Code. Happy coding! 🚀${NC}"
    echo ""
    exit 0
fi
