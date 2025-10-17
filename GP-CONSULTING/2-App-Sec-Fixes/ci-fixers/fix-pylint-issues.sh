#!/bin/bash
# Pylint Auto-Fixer - Python Code Quality
#
# Automatically fixes common Pylint issues using autopep8 and autoflake:
# - Formatting (PEP 8 compliance)
# - Unused imports removal
# - Unused variables removal
# - Spacing and indentation
# - Line length normalization
#
# Usage:
#   ./fix-pylint-issues.sh /path/to/project
#
# Compliance:
# - PCI-DSS 6.5.1 (Code quality prevents injection flaws)
# - PEP 8 (Python style guide)

set -euo pipefail

TARGET_DIR="${1:-.}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
GP_DATA_DIR="${GP_DATA_DIR:-$HOME/linkops-industries/GP-copilot/GP-DATA}"
OUTPUT_DIR="$GP_DATA_DIR/active/2-app-sec-fixes/ci-fixes"
BACKUP_DIR="$TARGET_DIR/backup/pylint-fixes-$TIMESTAMP"

mkdir -p "$OUTPUT_DIR"
mkdir -p "$BACKUP_DIR"

echo "========================================"
echo "Pylint Auto-Fixer (autopep8 + autoflake)"
echo "========================================"
echo "Target:    $TARGET_DIR"
echo "Backup:    $BACKUP_DIR"
echo "Timestamp: $TIMESTAMP"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ python3 not found"
    exit 1
fi

# Install autopep8 and autoflake if needed
echo "Checking dependencies..."
if ! python3 -c "import autopep8" 2>/dev/null; then
    echo "Installing autopep8..."
    python3 -m pip install autopep8 --quiet
fi

if ! python3 -c "import autoflake" 2>/dev/null; then
    echo "Installing autoflake..."
    python3 -m pip install autoflake --quiet
fi

if ! python3 -c "import pylint" 2>/dev/null; then
    echo "Installing pylint..."
    python3 -m pip install pylint --quiet
fi

echo "✓ Dependencies ready"
echo ""

# Find Python files
echo "Finding Python files..."
PY_FILES=$(find "$TARGET_DIR" -type f -name "*.py" \
    -not -path "*/.git/*" \
    -not -path "*/__pycache__/*" \
    -not -path "*/.venv/*" \
    -not -path "*/venv/*" \
    -not -path "*/env/*" \
    -not -path "*/node_modules/*" \
    -not -path "*/.pytest_cache/*" 2>/dev/null || true)

if [ -z "$PY_FILES" ]; then
    echo "⚠️  No Python files found"
    exit 0
fi

FILE_COUNT=$(echo "$PY_FILES" | wc -l)
echo "✓ Found $FILE_COUNT Python files"
echo ""

# Backup all files before fixing
echo "Creating backup..."
for file in $PY_FILES; do
    rel_path="${file#$TARGET_DIR/}"
    backup_file="$BACKUP_DIR/$rel_path"
    backup_dir=$(dirname "$backup_file")
    mkdir -p "$backup_dir"
    cp "$file" "$backup_file"
done
echo "✓ Backup created: $BACKUP_DIR"
echo ""

# Create or use existing Pylint config
PYLINTRC="$TARGET_DIR/.pylintrc"
if [ ! -f "$PYLINTRC" ]; then
    echo "Creating default Pylint config..."
    cat > "$PYLINTRC" << 'EOF'
[MASTER]
ignore=CVS,.git,__pycache__,.venv,venv,env,node_modules

[MESSAGES CONTROL]
disable=C0114,C0115,C0116,  # Missing docstrings
        C0103,              # Invalid name
        R0903,              # Too few public methods
        R0913,              # Too many arguments
        W0212               # Protected member access

[REPORTS]
output-format=json

[FORMAT]
max-line-length=120
indent-string='    '

[BASIC]
good-names=i,j,k,x,y,z,ex,Run,_,id,db
EOF
    echo "✓ Created Pylint config: $PYLINTRC"
else
    echo "✓ Using existing Pylint config: $PYLINTRC"
fi
echo ""

# Scan before fixing
echo "Scanning before fixes..."
ISSUES_BEFORE=0
PYLINT_BEFORE=$(python3 -m pylint --output-format=json --rcfile="$PYLINTRC" $PY_FILES 2>/dev/null || true)
if [ -n "$PYLINT_BEFORE" ]; then
    ISSUES_BEFORE=$(echo "$PYLINT_BEFORE" | jq 'length // 0')
fi
echo "Issues found: $ISSUES_BEFORE"
echo ""

# Apply fixes
echo "Applying fixes..."
echo "Step 1: Remove unused imports and variables (autoflake)..."

for file in $PY_FILES; do
    autoflake --in-place \
        --remove-all-unused-imports \
        --remove-unused-variables \
        --remove-duplicate-keys \
        "$file" 2>/dev/null || true
done

echo "✓ Unused imports/variables removed"
echo ""

echo "Step 2: Fix PEP 8 formatting (autopep8)..."

for file in $PY_FILES; do
    autopep8 --in-place \
        --aggressive \
        --aggressive \
        --max-line-length=120 \
        "$file" 2>/dev/null || true
done

echo "✓ PEP 8 formatting applied"
echo ""

# Scan after fixing
echo "Scanning after fixes..."
ISSUES_AFTER=0
PYLINT_AFTER=$(python3 -m pylint --output-format=json --rcfile="$PYLINTRC" $PY_FILES 2>/dev/null || true)
if [ -n "$PYLINT_AFTER" ]; then
    ISSUES_AFTER=$(echo "$PYLINT_AFTER" | jq 'length // 0')
fi
echo "Issues remaining: $ISSUES_AFTER"
echo ""

# Calculate fixes
ISSUES_FIXED=$((ISSUES_BEFORE - ISSUES_AFTER))

# Summary
echo "========================================"
echo "Pylint Fix Summary"
echo "========================================"
echo "Files processed:   $FILE_COUNT"
echo "Issues before:     $ISSUES_BEFORE"
echo "Issues after:      $ISSUES_AFTER"
echo "Issues fixed:      $ISSUES_FIXED"
if [ $ISSUES_BEFORE -gt 0 ]; then
    FIX_RATE=$((ISSUES_FIXED * 100 / ISSUES_BEFORE))
    echo "Fix rate:          ${FIX_RATE}%"
fi
echo ""

# Generate report
REPORT_FILE="$OUTPUT_DIR/fix-pylint-issues-$TIMESTAMP.log"
cat > "$REPORT_FILE" << EOF
Pylint Auto-Fix Report
======================
Timestamp:         $TIMESTAMP
Target:            $TARGET_DIR
Backup Location:   $BACKUP_DIR

Files Processed:   $FILE_COUNT
Issues Before:     $ISSUES_BEFORE
Issues After:      $ISSUES_AFTER
Issues Fixed:      $ISSUES_FIXED

Fixes Applied:
- PEP 8 formatting (autopep8)
- Unused imports removed (autoflake)
- Unused variables removed (autoflake)
- Spacing and indentation normalized
- Line length compliance (max 120)

Tools Used:
- autopep8: PEP 8 auto-formatter
- autoflake: Unused import/variable remover
- pylint: Code quality checker

Next Steps:
1. Review changes: git diff
2. Test application: pytest
3. Address remaining issues manually
4. Commit fixes: git commit -m "fix(lint): Pylint auto-fixes"

Remaining Issues:
If issues remain, they likely require manual fixes. Run:
  python3 -m pylint --rcfile=$PYLINTRC $TARGET_DIR

Restore Backup (if needed):
  cp -r $BACKUP_DIR/* $TARGET_DIR/
EOF

echo "Report saved: $REPORT_FILE"
echo ""

# Show remaining issues if any
if [ $ISSUES_AFTER -gt 0 ]; then
    echo "⚠️  $ISSUES_AFTER issues require manual fixes"
    echo ""
    echo "Run this command to see remaining issues:"
    echo "  python3 -m pylint --rcfile=$PYLINTRC $TARGET_DIR"
    echo ""

    # Show top issues
    echo "Top remaining issues:"
    echo "$PYLINT_AFTER" | jq -r '.[:10] | .[] | "  - \(.symbol) (\(.message-id)): \(.message)"' 2>/dev/null || true
    echo ""
fi

echo "✓ Pylint auto-fix complete"
echo ""
echo "Next steps:"
echo "  1. Review changes:  git diff"
echo "  2. Test application: pytest"
echo "  3. Commit fixes:    git commit -m 'fix(lint): Pylint auto-fixes'"
echo ""

exit 0
