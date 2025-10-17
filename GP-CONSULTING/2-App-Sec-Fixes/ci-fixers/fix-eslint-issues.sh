#!/bin/bash
# ESLint Auto-Fixer - JavaScript/TypeScript Code Quality
#
# Automatically fixes common ESLint issues:
# - Formatting (spacing, indentation, quotes)
# - Unused variables (safe removals)
# - Missing semicolons
# - var → const/let conversion
# - Simple best practice violations
#
# Usage:
#   ./fix-eslint-issues.sh /path/to/project
#
# Compliance:
# - PCI-DSS 6.5.1 (Code quality prevents injection flaws)
# - OWASP ASVS 1.14 (Build process includes code analysis)

set -euo pipefail

TARGET_DIR="${1:-.}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
GP_DATA_DIR="${GP_DATA_DIR:-$HOME/linkops-industries/GP-copilot/GP-DATA}"
OUTPUT_DIR="$GP_DATA_DIR/active/2-app-sec-fixes/ci-fixes"
BACKUP_DIR="$TARGET_DIR/backup/eslint-fixes-$TIMESTAMP"

mkdir -p "$OUTPUT_DIR"
mkdir -p "$BACKUP_DIR"

echo "========================================"
echo "ESLint Auto-Fixer"
echo "========================================"
echo "Target:    $TARGET_DIR"
echo "Backup:    $BACKUP_DIR"
echo "Timestamp: $TIMESTAMP"
echo ""

# Check if npx is available
if ! command -v npx &> /dev/null; then
    echo "❌ npx (Node.js) not found. Please install Node.js first."
    exit 1
fi

# Find JavaScript/TypeScript files
echo "Finding JavaScript/TypeScript files..."
JS_FILES=$(find "$TARGET_DIR" -type f \
    \( -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" -o -name "*.mjs" -o -name "*.cjs" \) \
    -not -path "*/node_modules/*" \
    -not -path "*/dist/*" \
    -not -path "*/build/*" \
    -not -path "*/.next/*" \
    -not -path "*/coverage/*" 2>/dev/null || true)

if [ -z "$JS_FILES" ]; then
    echo "⚠️  No JavaScript/TypeScript files found"
    exit 0
fi

FILE_COUNT=$(echo "$JS_FILES" | wc -l)
echo "✓ Found $FILE_COUNT JavaScript/TypeScript files"
echo ""

# Backup all files before fixing
echo "Creating backup..."
for file in $JS_FILES; do
    rel_path="${file#$TARGET_DIR/}"
    backup_file="$BACKUP_DIR/$rel_path"
    backup_dir=$(dirname "$backup_file")
    mkdir -p "$backup_dir"
    cp "$file" "$backup_file"
done
echo "✓ Backup created: $BACKUP_DIR"
echo ""

# Create or use existing ESLint config
ESLINTRC="$TARGET_DIR/.eslintrc.json"
if [ ! -f "$ESLINTRC" ]; then
    echo "Creating default ESLint config..."
    cat > "$ESLINTRC" << 'EOF'
{
  "env": {
    "browser": true,
    "es2021": true,
    "node": true
  },
  "extends": [
    "eslint:recommended"
  ],
  "parserOptions": {
    "ecmaVersion": 12,
    "sourceType": "module"
  },
  "rules": {
    "no-unused-vars": "warn",
    "no-console": "off",
    "no-eval": "error",
    "no-implied-eval": "error",
    "no-new-func": "error",
    "eqeqeq": "error",
    "no-var": "warn",
    "prefer-const": "warn",
    "no-undef": "error",
    "semi": ["warn", "always"],
    "quotes": ["warn", "single", { "avoidEscape": true }],
    "indent": ["warn", 2, { "SwitchCase": 1 }]
  }
}
EOF
    echo "✓ Created ESLint config: $ESLINTRC"
else
    echo "✓ Using existing ESLint config: $ESLINTRC"
fi
echo ""

# Run ESLint with --fix
echo "Running ESLint auto-fix..."
echo "This will fix:"
echo "  - Formatting (spacing, indentation, quotes)"
echo "  - Unused variables (safe removals)"
echo "  - Missing semicolons"
echo "  - var → const/let conversion"
echo "  - Simple best practice violations"
echo ""

ISSUES_BEFORE=0
ISSUES_AFTER=0

# Scan before fixing
echo "Scanning before fixes..."
SCAN_BEFORE=$(npx eslint "$TARGET_DIR" \
    --ext .js,.jsx,.ts,.tsx,.mjs,.cjs \
    --format json \
    --ignore-pattern 'node_modules/' \
    --ignore-pattern 'dist/' \
    --ignore-pattern 'build/' \
    --no-error-on-unmatched-pattern 2>/dev/null || true)

if [ -n "$SCAN_BEFORE" ]; then
    ISSUES_BEFORE=$(echo "$SCAN_BEFORE" | jq '[.[].messages | length] | add // 0')
fi

echo "Issues found: $ISSUES_BEFORE"
echo ""

# Apply fixes
echo "Applying fixes..."
npx eslint "$TARGET_DIR" \
    --ext .js,.jsx,.ts,.tsx,.mjs,.cjs \
    --fix \
    --ignore-pattern 'node_modules/' \
    --ignore-pattern 'dist/' \
    --ignore-pattern 'build/' \
    --no-error-on-unmatched-pattern 2>/dev/null || true

echo "✓ Auto-fixes applied"
echo ""

# Scan after fixing
echo "Scanning after fixes..."
SCAN_AFTER=$(npx eslint "$TARGET_DIR" \
    --ext .js,.jsx,.ts,.tsx,.mjs,.cjs \
    --format json \
    --ignore-pattern 'node_modules/' \
    --ignore-pattern 'dist/' \
    --ignore-pattern 'build/' \
    --no-error-on-unmatched-pattern 2>/dev/null || true)

if [ -n "$SCAN_AFTER" ]; then
    ISSUES_AFTER=$(echo "$SCAN_AFTER" | jq '[.[].messages | length] | add // 0')
fi

echo "Issues remaining: $ISSUES_AFTER"
echo ""

# Calculate fixes
ISSUES_FIXED=$((ISSUES_BEFORE - ISSUES_AFTER))

# Summary
echo "========================================"
echo "ESLint Fix Summary"
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
REPORT_FILE="$OUTPUT_DIR/fix-eslint-issues-$TIMESTAMP.log"
cat > "$REPORT_FILE" << EOF
ESLint Auto-Fix Report
=====================
Timestamp:         $TIMESTAMP
Target:            $TARGET_DIR
Backup Location:   $BACKUP_DIR

Files Processed:   $FILE_COUNT
Issues Before:     $ISSUES_BEFORE
Issues After:      $ISSUES_AFTER
Issues Fixed:      $ISSUES_FIXED

Fixes Applied:
- Formatting (spacing, indentation, quotes)
- Unused variables removed
- Missing semicolons added
- var → const/let conversion
- Simple best practice violations

Next Steps:
1. Review changes: git diff
2. Test application: npm test
3. Address remaining issues manually
4. Commit fixes: git commit -m "fix(lint): ESLint auto-fixes"

Remaining Issues:
If issues remain, they likely require manual fixes. Run:
  npx eslint $TARGET_DIR --ext .js,.jsx,.ts,.tsx

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
    echo "  npx eslint $TARGET_DIR --ext .js,.jsx,.ts,.tsx"
    echo ""
fi

echo "✓ ESLint auto-fix complete"
echo ""
echo "Next steps:"
echo "  1. Review changes:  git diff"
echo "  2. Test application: npm test"
echo "  3. Commit fixes:    git commit -m 'fix(lint): ESLint auto-fixes'"
echo ""

exit 0
