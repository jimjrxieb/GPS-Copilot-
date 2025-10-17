#!/bin/bash

# ============================================================================
# CI FIXER: SQL Injection Prevention
# ============================================================================
# LAYER: CI (Code-level)
# WHEN: Pre-commit, CI pipeline
# FIXES:
#   - CRITICAL: SQL injection vulnerabilities (string concatenation)
#   - HIGH: Unsanitized user input in queries
#   - PCI-DSS 6.5.1: Injection flaws
#   - OWASP A03:2021 - Injection
# ============================================================================

set -e

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
START_TIME=$(date +%s)

echo "🔧 CI FIXER: SQL Injection Prevention"
echo "═══════════════════════════════════════════════════════"
echo "Layer: CI (Code-level)"
echo "When: Pre-commit hook, CI pipeline"
echo ""

# Auto-detect project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CURRENT_DIR="$SCRIPT_DIR"
while [[ ! -d "$CURRENT_DIR/backend" && "$CURRENT_DIR" != "/" ]]; do
    CURRENT_DIR="$(dirname "$CURRENT_DIR")"
done
PROJECT_ROOT="$CURRENT_DIR"
BACKEND_DIR="$PROJECT_ROOT/backend"
BACKUP_DIR="$PROJECT_ROOT/backup/sql-injection-$TIMESTAMP"
REPORT_DIR="$PROJECT_ROOT/secops/6-reports/fixing/ci-fixes"
REPORT_FILE="$REPORT_DIR/fix-sql-injection-$TIMESTAMP.log"

# Create report directory
mkdir -p "$REPORT_DIR"

# Start logging
exec > >(tee -a "$REPORT_FILE") 2>&1

echo "Report: $REPORT_FILE"
echo "Timestamp: $(date -Iseconds)"
echo ""

# Validation
if [ ! -d "$BACKEND_DIR" ]; then
    echo "❌ ERROR: Backend directory not found: $BACKEND_DIR"
    exit 1
fi

echo "→ Creating backup..."
mkdir -p "$BACKUP_DIR"
cp -r "$BACKEND_DIR" "$BACKUP_DIR/"
echo "✅ Backup created: $BACKUP_DIR"

echo ""
echo "→ Scanning for SQL injection vulnerabilities..."

# Find vulnerable patterns
FINDINGS=0

# String concatenation in SQL (JavaScript)
if grep -r "execute.*[\`'\"].*\${" "$BACKEND_DIR" --include="*.js" | grep -q SELECT; then
    echo "  ⚠️  Found SQL string interpolation (JavaScript)"
    ((FINDINGS++))
fi

# String concatenation in SQL (Python)
if grep -r "execute.*['\"].*%s" "$BACKEND_DIR" --include="*.py" | grep -v "?" | grep -q SELECT; then
    echo "  ⚠️  Found SQL string formatting (Python)"
    ((FINDINGS++))
fi

# Direct query without parameterization
if grep -r "query.*+.*req\." "$BACKEND_DIR" --include="*.js" | grep -q .; then
    echo "  ⚠️  Found SQL concatenation with user input"
    ((FINDINGS++))
fi

if [ $FINDINGS -eq 0 ]; then
    echo "  ✅ No SQL injection vulnerabilities found"
    exit 0
fi

echo ""
echo "→ Fixing: Converting to parameterized queries..."

# Fix common patterns in JavaScript files
find "$BACKEND_DIR" -name "*.js" -type f | while read -r file; do
    FIXED=false

    # Pattern 1: String interpolation
    if grep -q "execute.*[\`'\"].*\${" "$file"; then
        # This is complex, create a reference file instead
        echo "  ⚠️  Manual review needed: $file"
        echo "     Replace string interpolation with parameterized queries"
        echo "     Example:"
        echo "       BAD:  db.execute(\`SELECT * FROM users WHERE id = \${userId}\`)"
        echo "       GOOD: db.execute('SELECT * FROM users WHERE id = ?', [userId])"
    fi

    # Pattern 2: Direct concatenation
    if grep -q "\"SELECT.*\+.*req\." "$file"; then
        echo "  ⚠️  Manual review needed: $file"
        echo "     Replace string concatenation with parameterized queries"
    fi
done

# Create sanitization helper module
cat > "$BACKEND_DIR/utils/sql-sanitizer.js" << 'EOF'
// SQL Injection Prevention Helper
// PCI-DSS 6.5.1 compliant

/**
 * Escape SQL identifier (table/column names)
 * Use for dynamic table/column names only, not for values
 */
function escapeIdentifier(identifier) {
  if (typeof identifier !== 'string') {
    throw new Error('Identifier must be a string');
  }

  // Only allow alphanumeric and underscore
  if (!/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(identifier)) {
    throw new Error(`Invalid identifier: ${identifier}`);
  }

  return `"${identifier}"`;
}

/**
 * Validate email format
 */
function validateEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Validate integer input
 */
function validateInteger(value) {
  const num = parseInt(value, 10);
  return !isNaN(num) && num.toString() === value.toString();
}

/**
 * Sanitize search input (remove SQL special characters)
 * Use for LIKE queries with parameterization
 */
function sanitizeSearchInput(input) {
  if (typeof input !== 'string') {
    return '';
  }

  // Remove SQL wildcards and special chars
  return input.replace(/[%_\\]/g, '\\$&');
}

module.exports = {
  escapeIdentifier,
  validateEmail,
  validateInteger,
  sanitizeSearchInput,
};
EOF
echo "  ✅ Created: backend/utils/sql-sanitizer.js"

# Create example of safe queries
cat > "$BACKEND_DIR/examples/safe-queries.js" << 'EOF'
// Example: Safe Parameterized Queries
// Always use placeholders (?, $1, etc.) for user input

const { Pool } = require('pg');
const pool = new Pool();

// ✅ SAFE: Parameterized query
async function getUserById(userId) {
  const result = await pool.query(
    'SELECT id, email, name FROM users WHERE id = $1',
    [userId]
  );
  return result.rows[0];
}

// ✅ SAFE: Multiple parameters
async function createTransaction(userId, amount, cardToken) {
  const result = await pool.query(
    'INSERT INTO transactions (user_id, amount, card_token) VALUES ($1, $2, $3) RETURNING id',
    [userId, amount, cardToken]
  );
  return result.rows[0].id;
}

// ✅ SAFE: LIKE query with sanitization
const { sanitizeSearchInput } = require('../utils/sql-sanitizer');

async function searchUsers(searchTerm) {
  const sanitized = sanitizeSearchInput(searchTerm);
  const result = await pool.query(
    'SELECT id, email, name FROM users WHERE name ILIKE $1',
    [`%${sanitized}%`]
  );
  return result.rows;
}

// ❌ UNSAFE: String interpolation (DO NOT USE)
async function unsafeQuery(userId) {
  // This allows SQL injection!
  const result = await pool.query(
    `SELECT * FROM users WHERE id = ${userId}`
  );
  return result.rows[0];
}

// ❌ UNSAFE: String concatenation (DO NOT USE)
async function unsafeSearch(searchTerm) {
  // This allows SQL injection!
  const result = await pool.query(
    "SELECT * FROM users WHERE name LIKE '%" + searchTerm + "%'"
  );
  return result.rows;
}

module.exports = {
  getUserById,
  createTransaction,
  searchUsers,
};
EOF
echo "  ✅ Created: backend/examples/safe-queries.js"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ CI FIX COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Changes made:"
echo "  ✅ Created SQL sanitization helper (utils/sql-sanitizer.js)"
echo "  ✅ Created safe query examples (examples/safe-queries.js)"
echo "  ⚠️  Manual review needed for existing queries"
echo ""
echo "Next steps:"
echo "  1. Review all SQL queries in codebase"
echo "  2. Replace string concatenation with parameterized queries"
echo "  3. Use placeholders: ? (MySQL) or \$1, \$2 (PostgreSQL)"
echo "  4. Validate user input before queries"
echo "  5. Run SAST tools: bandit, semgrep"
echo ""
echo "Example fix:"
echo "  BAD:  db.query(\`SELECT * FROM users WHERE email = '\${email}'\`)"
echo "  GOOD: db.query('SELECT * FROM users WHERE email = \$1', [email])"
echo ""
echo "Backup saved: $BACKUP_DIR"
echo ""

# Generate summary
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 FIX SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Fixer: fix-sql-injection.sh"
echo "Layer: CI (Code-level)"
echo "Duration: ${DURATION}s"
echo "Status: Complete"
echo "Report: $REPORT_FILE"
echo ""
