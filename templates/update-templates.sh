#!/bin/bash
# Update Apprise Templates in your project
# Usage: ./update-templates.sh [target-directory]

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Apprise Templates Updater${NC}"
echo -e "${BLUE}================================================${NC}\n"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if we're in a git repository
if [ ! -d "$SCRIPT_DIR/.git" ]; then
    echo -e "${RED}Error: This script must be run from the templates repository${NC}"
    echo "Current directory: $SCRIPT_DIR"
    exit 1
fi

# Determine target directory
if [ -z "$1" ]; then
    echo -e "${YELLOW}No target directory specified${NC}"
    echo "Usage: ./update-templates.sh [target-directory]"
    echo ""
    echo "Example:"
    echo "  ./update-templates.sh ~/my-project"
    exit 1
fi

TARGET_DIR="$1"

# Validate target directory exists
if [ ! -d "$TARGET_DIR" ]; then
    echo -e "${RED}Error: Target directory does not exist: $TARGET_DIR${NC}"
    exit 1
fi

# Validate target has templates installed
if [ ! -d "$TARGET_DIR/.claude/prompts" ]; then
    echo -e "${RED}Error: Templates not found in target directory${NC}"
    echo "Run install-templates.sh first: ./install-templates.sh $TARGET_DIR"
    exit 1
fi

echo -e "${GREEN}Updating templates in:${NC} $TARGET_DIR\n"

# Step 1: Pull latest changes
echo -e "${BLUE}[1/2]${NC} Pulling latest template updates from repository..."
cd "$SCRIPT_DIR"
git pull origin main
echo -e "${GREEN}✓${NC} Repository updated\n"

# Step 2: Re-install to target
echo -e "${BLUE}[2/2]${NC} Installing updated templates..."
cd "$SCRIPT_DIR"

# Remove old templates
rm -rf "$TARGET_DIR/.claude/prompts"

# Copy new templates
cp -r "$SCRIPT_DIR/.claude" "$TARGET_DIR/"
echo -e "${GREEN}✓${NC} Templates updated in $TARGET_DIR/.claude/prompts/\n"

# Update security tools (but don't overwrite .claudeignore or .gitignore)
if [ -f "$SCRIPT_DIR/security-tools/pre-flight-check.sh" ]; then
    cp "$SCRIPT_DIR/security-tools/pre-flight-check.sh" "$TARGET_DIR/"
    chmod +x "$TARGET_DIR/pre-flight-check.sh"
    echo -e "${GREEN}✓${NC} Updated pre-flight-check.sh\n"
fi

# Show summary
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}  Update Complete!${NC}"
echo -e "${GREEN}================================================${NC}\n"

echo "Updated components:"
echo "  ✓ All templates in .claude/prompts/"
echo "  ✓ pre-flight-check.sh"
echo ""
echo "Preserved (not overwritten):"
echo "  • .claudeignore"
echo "  • .gitignore"
echo ""
echo -e "${BLUE}Next step:${NC} Run pre-flight check to verify security"
echo "  cd $TARGET_DIR && ./pre-flight-check.sh"
echo ""
echo -e "${GREEN}✨ Templates are now up to date!${NC}\n"
