#!/bin/bash
# Install Apprise Templates to your project
# Usage: ./install-templates.sh [target-directory]

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Apprise Templates Installer${NC}"
echo -e "${BLUE}================================================${NC}\n"

# Determine target directory
if [ -z "$1" ]; then
    TARGET_DIR="$(pwd)"
else
    TARGET_DIR="$1"
fi

# Validate target directory
if [ ! -d "$TARGET_DIR" ]; then
    echo -e "${YELLOW}Warning: Target directory does not exist: $TARGET_DIR${NC}"
    read -p "Create it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mkdir -p "$TARGET_DIR"
    else
        echo "Aborting."
        exit 1
    fi
fi

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${GREEN}Installing templates to:${NC} $TARGET_DIR\n"

# Copy .claude directory
echo -e "${BLUE}[1/3]${NC} Copying Claude Code templates..."
cp -r "$SCRIPT_DIR/.claude" "$TARGET_DIR/"
echo -e "${GREEN}✓${NC} Templates copied to $TARGET_DIR/.claude/prompts/\n"

# Copy security tools (optional)
echo -e "${BLUE}[2/3]${NC} Copying security tools..."
if [ ! -f "$TARGET_DIR/.claudeignore" ]; then
    cp "$SCRIPT_DIR/security-tools/.claudeignore.template" "$TARGET_DIR/.claudeignore"
    echo -e "${GREEN}✓${NC} Created .claudeignore"
else
    echo -e "${YELLOW}⊘${NC} .claudeignore already exists (skipped)"
fi

if [ ! -f "$TARGET_DIR/.gitignore" ]; then
    cp "$SCRIPT_DIR/security-tools/.gitignore.template" "$TARGET_DIR/.gitignore"
    echo -e "${GREEN}✓${NC} Created .gitignore"
else
    echo -e "${YELLOW}⊘${NC} .gitignore already exists (skipped)"
fi

cp "$SCRIPT_DIR/security-tools/pre-flight-check.sh" "$TARGET_DIR/"
chmod +x "$TARGET_DIR/pre-flight-check.sh"
echo -e "${GREEN}✓${NC} Copied pre-flight-check.sh\n"

# Show summary
echo -e "${BLUE}[3/3]${NC} Installation complete!\n"

echo -e "${GREEN}Templates installed:${NC}"
echo "  📁 $TARGET_DIR/.claude/prompts/"
echo "     ├── agent_prompts/     (autonomous agents)"
echo "     ├── workflows/         (core workflows)"
echo "     ├── language-specific/ (language templates)"
echo "     ├── security/          (security templates)"
echo "     └── domain-specific/   (domain workflows)"
echo ""
echo -e "${GREEN}Security tools installed:${NC}"
echo "  📄 .claudeignore"
echo "  📄 .gitignore"
echo "  🔒 pre-flight-check.sh"
echo ""

# Next steps
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Next Steps${NC}"
echo -e "${BLUE}================================================${NC}\n"
echo "1. Run security check:"
echo "   cd $TARGET_DIR && ./pre-flight-check.sh"
echo ""
echo "2. Use templates with Claude Code:"
echo "   - Reference: .claude/prompts/workflows/refactoring_workflow.md"
echo "   - Invoke agents via Task tool"
echo ""
echo "3. Customize for your project:"
echo "   - Edit .claudeignore to add project-specific exclusions"
echo "   - Modify templates in .claude/prompts/ as needed"
echo ""
echo -e "${GREEN}✨ Happy coding!${NC}\n"
