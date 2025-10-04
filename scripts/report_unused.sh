#!/bin/bash
#
# Report unused code using vulture and coverage analysis
# This script helps identify potential dead code for cleanup
#
# Usage:
#   bash scripts/report_unused.sh [--install]
#
# Options:
#   --install    Install vulture if not present

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "🔍 Unused Code Report for converSQL"
echo "===================================="
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for --install flag
if [[ "$1" == "--install" ]]; then
    echo "📦 Installing vulture..."
    pip install vulture
    echo "✅ vulture installed"
    echo ""
fi

# Check if vulture is available
if ! command_exists vulture; then
    echo "⚠️  vulture is not installed"
    echo "Install with: pip install vulture"
    echo "Or run: bash scripts/report_unused.sh --install"
    echo ""
    VULTURE_AVAILABLE=false
else
    VULTURE_AVAILABLE=true
fi

# Change to project root
cd "${PROJECT_ROOT}"

# Run vulture if available
if [ "$VULTURE_AVAILABLE" = true ]; then
    echo "📊 Running vulture static analysis..."
    echo "------------------------------------"
    
    # Run vulture with confidence threshold
    # Higher confidence = more likely to be actually unused
    vulture src/ --min-confidence 80 --sort-by-size 2>/dev/null || {
        echo "✅ No high-confidence unused code found (confidence >= 80%)"
    }
    echo ""
    
    echo "📊 Vulture summary (all confidence levels)..."
    echo "------------------------------------"
    vulture src/ --min-confidence 60 2>&1 | head -20 || {
        echo "✅ No unused code found (confidence >= 60%)"
    }
    echo ""
fi

# Run coverage analysis if pytest is available
if command_exists pytest; then
    echo "📊 Coverage analysis for untested code..."
    echo "----------------------------------------"
    
    # Run tests with coverage, focusing on source code
    pytest tests/unit/ --cov=src --cov-report=term-missing --cov-report=html -q 2>&1 | \
        grep -E "^src/" | \
        grep -E "0%" || echo "✅ All source files have some test coverage"
    
    echo ""
    echo "📁 Detailed coverage report available at: htmlcov/index.html"
    echo ""
else
    echo "⚠️  pytest not available for coverage analysis"
    echo ""
fi

# Check for common patterns that might indicate unused code
echo "🔍 Checking for potential cleanup patterns..."
echo "-------------------------------------------"

# Look for files with "_old" suffix
OLD_FILES=$(find src/ -type f -name "*_old.py" 2>/dev/null || true)
if [ -n "$OLD_FILES" ]; then
    echo "⚠️  Found files with '_old' suffix:"
    echo "$OLD_FILES"
else
    echo "✅ No '_old' backup files found"
fi

# Look for TODO/FIXME/DEPRECATED comments
TODO_COUNT=$(grep -r "TODO\|FIXME\|DEPRECATED" src/ --include="*.py" 2>/dev/null | wc -l || echo "0")
if [ "$TODO_COUNT" -gt 0 ]; then
    echo "📝 Found $TODO_COUNT TODO/FIXME/DEPRECATED comments in source code"
    echo "   Run: grep -rn 'TODO\|FIXME\|DEPRECATED' src/ --include='*.py'"
else
    echo "✅ No TODO/FIXME/DEPRECATED markers found"
fi

echo ""
echo "===================================="
echo "✅ Unused code report complete!"
echo ""
echo "💡 Tips:"
echo "  - Review vulture output carefully (false positives are common)"
echo "  - Focus on code with 0% coverage first"
echo "  - Check _old backup files for safe removal"
echo "  - Address TODO/FIXME comments before cleanup"
echo ""
echo "📖 See REPO_INVENTORY.md for cleanup recommendations"
