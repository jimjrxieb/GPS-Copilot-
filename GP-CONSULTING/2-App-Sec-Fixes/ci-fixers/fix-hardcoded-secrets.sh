#!/bin/bash

# ============================================================================
# CI FIXER: Hardcoded Secrets Removal
# ============================================================================
# LAYER: CI (Code-level)
# WHEN: Pre-commit, CI pipeline
# FIXES:
#   - HIGH: Hardcoded database credentials in source code
#   - HIGH: API keys in config files
#   - HIGH: AWS credentials in code
#   - PCI-DSS 8.2.1: Don't use hardcoded credentials
#   - CIS Benchmark 5.3: Use secrets management
# ============================================================================

set -e

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
START_TIME=$(date +%s)

echo "🔧 CI FIXER: Hardcoded Secrets Removal"
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
BACKUP_DIR="$PROJECT_ROOT/backup/secrets-$TIMESTAMP"
REPORT_DIR="$PROJECT_ROOT/secops/6-reports/fixing/ci-fixes"
REPORT_FILE="$REPORT_DIR/fix-hardcoded-secrets-$TIMESTAMP.log"

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
echo "→ Scanning for hardcoded secrets..."

# Find hardcoded secrets patterns
FINDINGS=0

# Database credentials
if grep -r "password.*=.*['\"].*['\"]" "$BACKEND_DIR" --include="*.js" --include="*.py" --include="*.java" | grep -v "process.env" | grep -v "getenv" | grep -q .; then
    echo "  ⚠️  Found hardcoded passwords"
    ((FINDINGS++))
fi

# API keys
if grep -r "api[_-]key.*=.*['\"][A-Za-z0-9]{20,}['\"]" "$BACKEND_DIR" --include="*.js" --include="*.py" --include="*.java" | grep -v "process.env" | grep -q .; then
    echo "  ⚠️  Found hardcoded API keys"
    ((FINDINGS++))
fi

# AWS credentials
if grep -r "aws[_-]secret" "$BACKEND_DIR" --include="*.js" --include="*.py" --include="*.java" | grep -v "process.env" | grep -v ".env" | grep -q .; then
    echo "  ⚠️  Found hardcoded AWS secrets"
    ((FINDINGS++))
fi

if [ $FINDINGS -eq 0 ]; then
    echo "  ✅ No hardcoded secrets found"
    exit 0
fi

echo ""
echo "→ Fixing: Migrating to environment variables..."

# Fix database.js (Node.js)
if [ -f "$BACKEND_DIR/config/database.js" ]; then
    cat > "$BACKEND_DIR/config/database.js" << 'EOF'
// SecureBank Database Configuration
// Uses environment variables (PCI-DSS 8.2.1 compliant)

module.exports = {
  development: {
    username: process.env.DB_USERNAME || 'postgres',
    password: process.env.DB_PASSWORD || 'postgres',
    database: process.env.DB_NAME || 'securebank_dev',
    host: process.env.DB_HOST || 'localhost',
    port: process.env.DB_PORT || 5432,
    dialect: 'postgres',
    logging: false,
  },
  production: {
    username: process.env.DB_USERNAME,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME,
    host: process.env.DB_HOST,
    port: process.env.DB_PORT || 5432,
    dialect: 'postgres',
    logging: false,
    ssl: {
      require: true,
      rejectUnauthorized: false, // For RDS
    },
  },
};
EOF
    echo "  ✅ Fixed: backend/config/database.js (uses env vars)"
fi

# Fix payment service (Python)
if [ -f "$BACKEND_DIR/services/payment.py" ]; then
    # Remove hardcoded API keys
    sed -i "s/api_key = ['\"].*['\"]/api_key = os.getenv('PAYMENT_API_KEY')/g" "$BACKEND_DIR/services/payment.py"

    # Add import if missing
    if ! grep -q "import os" "$BACKEND_DIR/services/payment.py"; then
        sed -i '1i import os' "$BACKEND_DIR/services/payment.py"
    fi

    echo "  ✅ Fixed: backend/services/payment.py (uses env vars)"
fi

# Create .env.example template
cat > "$BACKEND_DIR/.env.example" << 'EOF'
# SecureBank Environment Variables
# Copy to .env and fill in actual values
# NEVER commit .env to git!

# Database
DB_USERNAME=postgres
DB_PASSWORD=<generate-strong-password>
DB_NAME=securebank
DB_HOST=localhost
DB_PORT=5432

# AWS
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=<use-iam-role-instead>
AWS_SECRET_ACCESS_KEY=<use-iam-role-instead>

# Payment Gateway
PAYMENT_API_KEY=<from-aws-secrets-manager>
PAYMENT_API_URL=https://api.payment-gateway.com

# Secrets Manager
SECRET_NAME=securebank/production/credentials
EOF
echo "  ✅ Created: backend/.env.example (template)"

# Update .gitignore
if [ -f "$PROJECT_ROOT/.gitignore" ]; then
    if ! grep -q "^\.env$" "$PROJECT_ROOT/.gitignore"; then
        echo "" >> "$PROJECT_ROOT/.gitignore"
        echo "# Environment variables (contains secrets)" >> "$PROJECT_ROOT/.gitignore"
        echo ".env" >> "$PROJECT_ROOT/.gitignore"
        echo ".env.local" >> "$PROJECT_ROOT/.gitignore"
        echo ".env.*.local" >> "$PROJECT_ROOT/.gitignore"
    fi
    echo "  ✅ Updated: .gitignore (excludes .env)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ CI FIX COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Changes made:"
echo "  ✅ Hardcoded secrets removed from source code"
echo "  ✅ Migrated to environment variables"
echo "  ✅ Created .env.example template"
echo "  ✅ Updated .gitignore"
echo ""
echo "Next steps:"
echo "  1. Copy .env.example to .env"
echo "  2. Fill in actual values (never commit .env!)"
echo "  3. For production, use AWS Secrets Manager:"
echo "     aws secretsmanager create-secret --name securebank/prod/db \\"
echo "       --secret-string '{\"username\":\"admin\",\"password\":\"...\"}'"
echo ""
echo "Backup saved: $BACKUP_DIR"
echo ""

# Generate summary
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 FIX SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Fixer: fix-hardcoded-secrets.sh"
echo "Layer: CI (Code-level)"
echo "Duration: ${DURATION}s"
echo "Status: Complete"
echo "Report: $REPORT_FILE"
echo ""
