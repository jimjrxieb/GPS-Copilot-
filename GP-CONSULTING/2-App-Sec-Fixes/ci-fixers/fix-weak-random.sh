#!/bin/bash

# ============================================================================
# CI FIXER: Weak Random Number Generation Remediation
# ============================================================================
# LAYER: CI (Code-level)
# WHEN: Pre-commit, CI pipeline
# FIXES:
#   - HIGH: Weak random number generation (Bandit B311)
#   - Security: Predictable randomness in security contexts
#   - PCI-DSS 6.5.3: Use cryptographically strong random values
#   - CWE-330: Use of Insufficiently Random Values
# ============================================================================

set -e

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
START_TIME=$(date +%s)

echo "🔧 CI FIXER: Weak Random Number Generation Remediation"
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

BACKUP_DIR="$PROJECT_ROOT/backup/weak-random-$TIMESTAMP"
REPORT_DIR="$PROJECT_ROOT/GP-DATA/active/2-app-sec-fixes/ci-fixes"
REPORT_FILE="$REPORT_DIR/fix-weak-random-$TIMESTAMP.log"

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
echo "→ Scanning for weak random number generation..."

FINDINGS=0
FIXES_APPLIED=0

# Python files
if find "$PROJECT_ROOT" -name "*.py" -type f | grep -q .; then
    echo ""
    echo "  📝 Analyzing Python files..."

    # random.random() usage
    if grep -rE "import random|from random import" "$PROJECT_ROOT" --include="*.py" | grep -q .; then
        echo "    ⚠️  Found usage of 'random' module (not cryptographically secure)"
        ((FINDINGS++))

        # Fix: random → secrets
        find "$PROJECT_ROOT" -name "*.py" -type f | while read -r file; do
            NEEDS_FIX=false

            # Check if file uses random for security-sensitive operations
            # Look for: tokens, passwords, keys, secrets, session, auth
            if grep -qE "random\.(random|randint|choice|randrange)" "$file"; then
                if grep -qiE "(token|password|key|secret|session|auth|salt|nonce)" "$file"; then
                    NEEDS_FIX=true
                fi
            fi

            if [ "$NEEDS_FIX" = true ]; then
                echo "      Fixing: $file"

                # Add secrets import if not present
                if ! grep -q "^import secrets" "$file"; then
                    # Add after existing imports
                    sed -i '/^import random/a import secrets  # Security: For cryptographically secure random' "$file"
                fi

                # Replace random functions with secrets equivalents
                # random.random() → secrets.SystemRandom().random()
                sed -i 's/random\.random()/secrets.SystemRandom().random()/g' "$file"

                # random.randint(a, b) → secrets.randbelow(b - a + 1) + a
                # This is complex, flag for manual review
                if grep -q "random\.randint" "$file"; then
                    echo "        ⚠️  Manual review needed: random.randint() → secrets.randbelow()"
                fi

                # random.choice() → secrets.choice()
                sed -i 's/random\.choice(/secrets.choice(/g' "$file"

                # Add comment explaining change
                if ! grep -q "# Security: Upgraded from random to secrets" "$file"; then
                    sed -i '1i # Security: Upgraded from random module to secrets module for cryptographic operations' "$file"
                fi

                ((FIXES_APPLIED++))
            fi
        done
    fi
fi

# JavaScript/Node.js files
if find "$PROJECT_ROOT" -name "*.js" -type f | grep -q .; then
    echo ""
    echo "  📝 Analyzing JavaScript files..."

    # Math.random() usage
    if grep -r "Math\.random()" "$PROJECT_ROOT" --include="*.js" | grep -q .; then
        echo "    ⚠️  Found Math.random() usage (not cryptographically secure)"
        ((FINDINGS++))

        # Check if used in security contexts
        find "$PROJECT_ROOT" -name "*.js" -type f | while read -r file; do
            if grep -q "Math\.random()" "$file"; then
                if grep -qiE "(token|password|key|secret|session|auth|salt|nonce)" "$file"; then
                    echo "      ⚠️  Manual fix needed: $file"
                    echo "         Replace Math.random() with crypto.randomBytes()"
                    echo "         const crypto = require('crypto');"
                    echo "         const token = crypto.randomBytes(32).toString('hex');"
                fi
            fi
        done
    fi
fi

# Java files
if find "$PROJECT_ROOT" -name "*.java" -type f | grep -q .; then
    echo ""
    echo "  📝 Analyzing Java files..."

    # java.util.Random usage
    if grep -r "new Random()" "$PROJECT_ROOT" --include="*.java" | grep -q .; then
        echo "    ⚠️  Found java.util.Random usage (not cryptographically secure)"
        ((FINDINGS++))

        find "$PROJECT_ROOT" -name "*.java" -type f | while read -r file; do
            if grep -q "new Random()" "$file"; then
                if grep -qiE "(token|password|key|secret|session|auth)" "$file"; then
                    echo "      ⚠️  Manual fix needed: $file"
                    echo "         Replace java.util.Random with SecureRandom:"
                    echo "         import java.security.SecureRandom;"
                    echo "         SecureRandom random = new SecureRandom();"
                fi
            fi
        done
    fi
fi

if [ $FINDINGS -eq 0 ]; then
    echo "  ✅ No weak random number generation found"
    exit 0
fi

# Create secure random helper for Python projects
if find "$PROJECT_ROOT" -name "*.py" -type f | grep -q .; then
    UTILS_DIR="$PROJECT_ROOT/utils"
    mkdir -p "$UTILS_DIR"

    cat > "$UTILS_DIR/secure_random.py" << 'EOF'
#!/usr/bin/env python3
"""
Secure Random Number Generation Helper
Provides cryptographically secure random values
"""

import secrets
import string


def generate_token(length=32):
    """
    Generate a cryptographically secure random token

    Args:
        length: Token length in bytes (default: 32)

    Returns:
        str: Hexadecimal token string

    Example:
        >>> token = generate_token(32)
        >>> len(token)
        64  # 32 bytes = 64 hex characters
    """
    return secrets.token_hex(length)


def generate_password(length=16, use_symbols=True):
    """
    Generate a cryptographically secure random password

    Args:
        length: Password length (default: 16)
        use_symbols: Include symbols in password (default: True)

    Returns:
        str: Random password

    Example:
        >>> password = generate_password(16)
        >>> len(password)
        16
    """
    alphabet = string.ascii_letters + string.digits
    if use_symbols:
        alphabet += string.punctuation

    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_api_key(length=32):
    """
    Generate a cryptographically secure API key

    Args:
        length: Key length in bytes (default: 32)

    Returns:
        str: URL-safe base64 API key

    Example:
        >>> api_key = generate_api_key(32)
        >>> len(api_key)  # Will vary due to base64 encoding
        43
    """
    return secrets.token_urlsafe(length)


def random_int(min_value, max_value):
    """
    Generate cryptographically secure random integer

    Args:
        min_value: Minimum value (inclusive)
        max_value: Maximum value (inclusive)

    Returns:
        int: Random integer in range [min_value, max_value]

    Example:
        >>> num = random_int(1, 100)
        >>> 1 <= num <= 100
        True
    """
    range_size = max_value - min_value + 1
    return min_value + secrets.randbelow(range_size)


def random_choice(sequence):
    """
    Choose a random element from a sequence

    Args:
        sequence: List, tuple, or string to choose from

    Returns:
        Element from sequence

    Example:
        >>> choice = random_choice(['apple', 'banana', 'cherry'])
        >>> choice in ['apple', 'banana', 'cherry']
        True
    """
    return secrets.choice(sequence)


def generate_salt(length=16):
    """
    Generate cryptographic salt for password hashing

    Args:
        length: Salt length in bytes (default: 16)

    Returns:
        bytes: Random salt

    Example:
        >>> salt = generate_salt(16)
        >>> len(salt)
        16
    """
    return secrets.token_bytes(length)
EOF

    echo "  ✅ Created: $UTILS_DIR/secure_random.py (cryptographic random helper)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ CI FIX COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Changes made:"
echo "  ✅ random module → secrets module (Python)"
echo "  ✅ Created utils/secure_random.py (helper functions)"
echo "  ⚠️  Flagged Math.random() for manual review (JavaScript)"
echo "  ⚠️  Flagged java.util.Random for manual review (Java)"
echo ""
echo "Security improvements:"
echo "  • random.random() (predictable) → secrets.SystemRandom() (cryptographic)"
echo "  • random.choice() → secrets.choice()"
echo "  • Manual review needed for complex cases"
echo ""
echo "Usage of secure helper:"
echo "  from utils.secure_random import generate_token, generate_password"
echo "  "
echo "  # Generate secure token"
echo "  session_token = generate_token(32)  # 64-character hex string"
echo "  "
echo "  # Generate secure password"
echo "  password = generate_password(16, use_symbols=True)"
echo "  "
echo "  # Generate API key"
echo "  api_key = generate_api_key(32)"
echo "  "
echo "  # Secure random integer"
echo "  random_num = random_int(1, 100)"
echo ""
echo "Next steps:"
echo "  1. Review flagged files for manual fixes"
echo "  2. For JavaScript, use:"
echo "     const crypto = require('crypto');"
echo "     const token = crypto.randomBytes(32).toString('hex');"
echo "  3. For Java, use:"
echo "     import java.security.SecureRandom;"
echo "     SecureRandom random = new SecureRandom();"
echo "  4. Re-run Bandit scanner:"
echo "     python3 ../../1-Security-Assessment/ci-scanners/bandit_scanner.py --target $PROJECT_ROOT"
echo ""
echo "⚠️  IMPORTANT:"
echo "  • Only use secrets/crypto modules for security-sensitive operations"
echo "  • For non-security uses (e.g., game logic), random module is fine"
echo "  • Never seed cryptographic RNGs with predictable values"
echo ""
echo "Backup saved: $BACKUP_DIR"
echo ""

# Generate summary
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 FIX SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Fixer: fix-weak-random.sh"
echo "Layer: CI (Code-level)"
echo "Findings: $FINDINGS"
echo "Fixes Applied: $FIXES_APPLIED"
echo "Duration: ${DURATION}s"
echo "Status: Complete"
echo "Report: $REPORT_FILE"
echo ""
