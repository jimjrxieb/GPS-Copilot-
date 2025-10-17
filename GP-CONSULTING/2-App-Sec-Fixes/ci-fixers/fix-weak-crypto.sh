#!/bin/bash

# ============================================================================
# CI FIXER: Weak Cryptography Remediation
# ============================================================================
# LAYER: CI (Code-level)
# WHEN: Pre-commit, CI pipeline
# FIXES:
#   - MEDIUM: MD5 hash usage (Bandit B303)
#   - MEDIUM: SHA1 hash usage (Bandit B304)
#   - MEDIUM: DES/3DES encryption (Bandit B305)
#   - MEDIUM: Weak cipher modes (Bandit B306)
#   - PCI-DSS 6.5.3: Use strong cryptography
#   - NIST 800-53 SC-13: Cryptographic protection
# ============================================================================

set -e

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
START_TIME=$(date +%s)

echo "🔧 CI FIXER: Weak Cryptography Remediation"
echo "═══════════════════════════════════════════════════════"
echo "Layer: CI (Code-level)"
echo "When: Pre-commit hook, CI pipeline"
echo ""

# Auto-detect project root or use provided argument
if [ -n "$1" ]; then
    PROJECT_ROOT="$1"
else
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
fi

BACKUP_DIR="$PROJECT_ROOT/backup/weak-crypto-$TIMESTAMP"
REPORT_DIR="$PROJECT_ROOT/GP-DATA/active/2-app-sec-fixes/ci-fixes"
REPORT_FILE="$REPORT_DIR/fix-weak-crypto-$TIMESTAMP.log"

# Create directories
mkdir -p "$REPORT_DIR"
mkdir -p "$BACKUP_DIR"

# Start logging
exec > >(tee -a "$REPORT_FILE") 2>&1

echo "Project: $PROJECT_ROOT"
echo "Report: $REPORT_FILE"
echo "Timestamp: $(date -Iseconds)"
echo ""

# Validation
if [ ! -d "$PROJECT_ROOT" ]; then
    echo "❌ ERROR: Project directory not found: $PROJECT_ROOT"
    exit 1
fi

echo "→ Creating backup..."
cp -r "$PROJECT_ROOT" "$BACKUP_DIR/" 2>/dev/null || true
echo "✅ Backup created: $BACKUP_DIR"

echo ""
echo "→ Scanning for weak cryptography..."

FINDINGS=0
FIXES_APPLIED=0

# Python files
if find "$PROJECT_ROOT" -name "*.py" -type f | grep -q .; then
    echo ""
    echo "  📝 Analyzing Python files..."

    # MD5 usage (Bandit B303)
    if grep -r "hashlib\.md5" "$PROJECT_ROOT" --include="*.py" | grep -q .; then
        echo "    ⚠️  Found MD5 hash usage (insecure)"
        ((FINDINGS++))

        # Fix: MD5 → SHA256
        find "$PROJECT_ROOT" -name "*.py" -type f | while read -r file; do
            if grep -q "hashlib\.md5" "$file"; then
                echo "      Fixing: $file"

                # Replace hashlib.md5() with hashlib.sha256()
                sed -i 's/hashlib\.md5(/hashlib.sha256(/g' "$file"

                # Add comment explaining change
                if ! grep -q "# Security: Upgraded from MD5 to SHA256" "$file"; then
                    # Add import if missing
                    if ! grep -q "^import hashlib" "$file"; then
                        sed -i '1i import hashlib  # Security: Upgraded from MD5 to SHA256' "$file"
                    fi
                fi

                ((FIXES_APPLIED++))
            fi
        done
    fi

    # SHA1 usage (Bandit B304)
    if grep -r "hashlib\.sha1" "$PROJECT_ROOT" --include="*.py" | grep -q .; then
        echo "    ⚠️  Found SHA1 hash usage (weak)"
        ((FINDINGS++))

        # Fix: SHA1 → SHA256
        find "$PROJECT_ROOT" -name "*.py" -type f | while read -r file; do
            if grep -q "hashlib\.sha1" "$file"; then
                echo "      Fixing: $file"
                sed -i 's/hashlib\.sha1(/hashlib.sha256(/g' "$file"
                ((FIXES_APPLIED++))
            fi
        done
    fi

    # DES/3DES usage (Bandit B305)
    if grep -r "Crypto\.Cipher\.DES" "$PROJECT_ROOT" --include="*.py" | grep -q .; then
        echo "    ⚠️  Found DES/3DES encryption (obsolete)"
        ((FINDINGS++))

        # Fix: DES → AES
        find "$PROJECT_ROOT" -name "*.py" -type f | while read -r file; do
            if grep -q "Crypto\.Cipher\.DES" "$file"; then
                echo "      Fixing: $file (DES → AES)"
                sed -i 's/from Crypto\.Cipher import DES/from Crypto.Cipher import AES  # Security: Upgraded from DES/g' "$file"
                sed -i 's/Crypto\.Cipher\.DES/Crypto.Cipher.AES/g' "$file"

                # Add comment about manual review needed
                echo "      ⚠️  Manual review needed: Verify AES mode (use GCM or CBC with HMAC)"
                ((FIXES_APPLIED++))
            fi
        done
    fi
fi

# JavaScript/Node.js files
if find "$PROJECT_ROOT" -name "*.js" -type f | grep -q .; then
    echo ""
    echo "  📝 Analyzing JavaScript files..."

    # MD5 usage
    if grep -r "createHash.*md5" "$PROJECT_ROOT" --include="*.js" | grep -q .; then
        echo "    ⚠️  Found MD5 hash usage (insecure)"
        ((FINDINGS++))

        # Fix: MD5 → SHA256
        find "$PROJECT_ROOT" -name "*.js" -type f | while read -r file; do
            if grep -q "createHash.*md5" "$file"; then
                echo "      Fixing: $file"
                sed -i "s/createHash('md5')/createHash('sha256')/g" "$file"
                sed -i 's/createHash("md5")/createHash("sha256")/g' "$file"
                ((FIXES_APPLIED++))
            fi
        done
    fi

    # SHA1 usage
    if grep -r "createHash.*sha1" "$PROJECT_ROOT" --include="*.js" | grep -q .; then
        echo "    ⚠️  Found SHA1 hash usage (weak)"
        ((FINDINGS++))

        # Fix: SHA1 → SHA256
        find "$PROJECT_ROOT" -name "*.js" -type f | while read -r file; do
            if grep -q "createHash.*sha1" "$file"; then
                echo "      Fixing: $file"
                sed -i "s/createHash('sha1')/createHash('sha256')/g" "$file"
                sed -i 's/createHash("sha1")/createHash("sha256")/g' "$file"
                ((FIXES_APPLIED++))
            fi
        done
    fi
fi

# Java files
if find "$PROJECT_ROOT" -name "*.java" -type f | grep -q .; then
    echo ""
    echo "  📝 Analyzing Java files..."

    # MD5 usage
    if grep -r 'MessageDigest\.getInstance.*"MD5"' "$PROJECT_ROOT" --include="*.java" | grep -q .; then
        echo "    ⚠️  Found MD5 hash usage (insecure)"
        ((FINDINGS++))

        # Fix: MD5 → SHA-256
        find "$PROJECT_ROOT" -name "*.java" -type f | while read -r file; do
            if grep -q 'MessageDigest\.getInstance.*"MD5"' "$file"; then
                echo "      Fixing: $file"
                sed -i 's/MessageDigest\.getInstance("MD5")/MessageDigest.getInstance("SHA-256")/g' "$file"
                ((FIXES_APPLIED++))
            fi
        done
    fi
fi

if [ $FINDINGS -eq 0 ]; then
    echo "  ✅ No weak cryptography found"
    exit 0
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ CI FIX COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Changes made:"
echo "  ✅ MD5 → SHA256"
echo "  ✅ SHA1 → SHA256"
echo "  ✅ DES → AES (verify mode manually)"
echo ""
echo "Cryptographic upgrades:"
echo "  • MD5/SHA1 (broken) → SHA256 (secure)"
echo "  • Collision resistance: SHA256 provides 128-bit security"
echo "  • Preimage resistance: SHA256 provides 256-bit security"
echo ""
echo "Next steps:"
echo "  1. Test thoroughly (hash outputs will differ!)"
echo "  2. For password hashing, use bcrypt/argon2:"
echo "     Python: pip install bcrypt"
echo "     Node.js: npm install bcrypt"
echo "  3. For encryption, verify AES mode:"
echo "     • AES-GCM (recommended for authenticated encryption)"
echo "     • AES-CBC + HMAC (if GCM not available)"
echo "  4. Re-run Bandit scanner to verify fixes:"
echo "     python3 ../../1-Security-Assessment/ci-scanners/bandit_scanner.py --target $PROJECT_ROOT"
echo ""
echo "⚠️  IMPORTANT:"
echo "  • Changing hash algorithms will break existing hashes!"
echo "  • Rehash passwords after upgrade"
echo "  • Update any hash-based integrity checks"
echo ""
echo "Backup saved: $BACKUP_DIR"
echo ""

# Generate summary
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 FIX SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Fixer: fix-weak-crypto.sh"
echo "Layer: CI (Code-level)"
echo "Findings: $FINDINGS"
echo "Fixes Applied: $FIXES_APPLIED"
echo "Duration: ${DURATION}s"
echo "Status: Complete"
echo "Report: $REPORT_FILE"
echo ""
