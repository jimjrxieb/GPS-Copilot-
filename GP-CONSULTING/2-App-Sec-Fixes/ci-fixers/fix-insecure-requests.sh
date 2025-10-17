#!/bin/bash

# ============================================================================
# CI FIXER: Insecure HTTP Requests Remediation
# ============================================================================
# LAYER: CI (Code-level)
# WHEN: Pre-commit, CI pipeline
# FIXES:
#   - MEDIUM: Request without timeout (Bandit B113)
#   - DoS risk from hanging connections
#   - PCI-DSS 6.5.10: Protect against common coding vulnerabilities
# ============================================================================

set -e

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
START_TIME=$(date +%s)

echo "🔧 CI FIXER: Insecure HTTP Requests Remediation"
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

BACKUP_DIR="$PROJECT_ROOT/backup/insecure-requests-$TIMESTAMP"
REPORT_DIR="$PROJECT_ROOT/GP-DATA/active/2-app-sec-fixes/ci-fixes"
REPORT_FILE="$REPORT_DIR/fix-insecure-requests-$TIMESTAMP.log"

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
echo "→ Scanning for requests without timeout..."

FINDINGS=0
FIXES_APPLIED=0

# Python - requests library
if find "$PROJECT_ROOT" -name "*.py" -type f | grep -q .; then
    echo ""
    echo "  📝 Analyzing Python files (requests library)..."

    # requests.get() without timeout
    if grep -rE "requests\.(get|post|put|delete|patch|head|options)\(" "$PROJECT_ROOT" --include="*.py" | grep -v "timeout=" | grep -q .; then
        echo "    ⚠️  Found HTTP requests without timeout"
        ((FINDINGS++))

        # Fix: Add timeout parameter
        find "$PROJECT_ROOT" -name "*.py" -type f | while read -r file; do
            if grep -qE "requests\.(get|post|put|delete|patch|head|options)\(" "$file"; then
                # Check if file needs fixing (no timeout parameter)
                if grep -E "requests\.(get|post|put|delete|patch|head|options)\(" "$file" | grep -qv "timeout="; then
                    echo "      Fixing: $file"

                    # Add timeout parameter (30 seconds default)
                    # Pattern: requests.get(url) → requests.get(url, timeout=30)
                    # Pattern: requests.get(url, headers={}) → requests.get(url, headers={}, timeout=30)

                    # For requests with closing parenthesis on same line
                    sed -i -E 's/requests\.(get|post|put|delete|patch|head|options)\(([^)]+)\)/requests.\1(\2, timeout=30)/g' "$file"

                    # Remove duplicate timeout if already exists
                    sed -i 's/, timeout=[0-9]\+, timeout=[0-9]\+/, timeout=30/g' "$file"

                    ((FIXES_APPLIED++))
                fi
            fi
        done
    fi

    # urllib.request.urlopen() without timeout
    if grep -r "urllib\.request\.urlopen\(" "$PROJECT_ROOT" --include="*.py" | grep -v "timeout=" | grep -q .; then
        echo "    ⚠️  Found urllib requests without timeout"
        ((FINDINGS++))

        find "$PROJECT_ROOT" -name "*.py" -type f | while read -r file; do
            if grep -q "urllib\.request\.urlopen\(" "$file"; then
                if grep "urllib\.request\.urlopen\(" "$file" | grep -qv "timeout="; then
                    echo "      Fixing: $file"
                    sed -i -E 's/urllib\.request\.urlopen\(([^)]+)\)/urllib.request.urlopen(\1, timeout=30)/g' "$file"
                    sed -i 's/, timeout=[0-9]\+, timeout=[0-9]\+/, timeout=30/g' "$file"
                    ((FIXES_APPLIED++))
                fi
            fi
        done
    fi

    # socket operations without timeout
    if grep -r "socket\.create_connection\(" "$PROJECT_ROOT" --include="*.py" | grep -v "timeout=" | grep -q .; then
        echo "    ⚠️  Found socket connections without timeout"
        ((FINDINGS++))

        find "$PROJECT_ROOT" -name "*.py" -type f | while read -r file; do
            if grep -q "socket\.create_connection\(" "$file"; then
                if grep "socket\.create_connection\(" "$file" | grep -qv "timeout="; then
                    echo "      Fixing: $file"
                    sed -i -E 's/socket\.create_connection\(([^)]+)\)/socket.create_connection(\1, timeout=30)/g' "$file"
                    sed -i 's/, timeout=[0-9]\+, timeout=[0-9]\+/, timeout=30/g' "$file"
                    ((FIXES_APPLIED++))
                fi
            fi
        done
    fi
fi

# JavaScript/Node.js - axios, fetch, http
if find "$PROJECT_ROOT" -name "*.js" -type f | grep -q .; then
    echo ""
    echo "  📝 Analyzing JavaScript files..."

    # axios without timeout
    if grep -rE "axios\.(get|post|put|delete|patch|head|options)\(" "$PROJECT_ROOT" --include="*.js" | grep -v "timeout:" | grep -q .; then
        echo "    ⚠️  Found axios requests without timeout"
        ((FINDINGS++))

        # Note: axios timeout fix is more complex, flag for manual review
        echo "      ⚠️  Manual fix needed for axios timeout"
        echo "      Add timeout to axios config:"
        echo "        axios.get(url, { timeout: 30000 })"
        echo "        or create axios instance with default timeout"
    fi

    # fetch without timeout (harder to fix automatically)
    if grep -r "fetch\(" "$PROJECT_ROOT" --include="*.js" | grep -q .; then
        echo "    ⚠️  Found fetch() calls (may lack timeout)"
        echo "      ⚠️  Manual review needed for fetch timeout"
        echo "      Use AbortController with timeout or libraries like p-timeout"
    fi
fi

if [ $FINDINGS -eq 0 ]; then
    echo "  ✅ No requests without timeout found"
    exit 0
fi

# Create helper module for Python projects
if find "$PROJECT_ROOT" -name "*.py" -type f | grep -q .; then
    UTILS_DIR="$PROJECT_ROOT/utils"
    mkdir -p "$UTILS_DIR"

    cat > "$UTILS_DIR/http_client.py" << 'EOF'
#!/usr/bin/env python3
"""
Secure HTTP Client Helper
Provides safe defaults for HTTP requests
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Default timeout (30 seconds)
DEFAULT_TIMEOUT = 30

# Retry strategy
DEFAULT_RETRY = Retry(
    total=3,
    backoff_factor=0.3,
    status_forcelist=[500, 502, 503, 504]
)


class TimeoutHTTPAdapter(HTTPAdapter):
    """HTTP Adapter with default timeout"""

    def __init__(self, *args, **kwargs):
        self.timeout = kwargs.pop('timeout', DEFAULT_TIMEOUT)
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        kwargs.setdefault('timeout', self.timeout)
        return super().send(request, **kwargs)


def create_session(timeout=DEFAULT_TIMEOUT, max_retries=DEFAULT_RETRY):
    """
    Create a requests session with safe defaults

    Args:
        timeout: Request timeout in seconds (default: 30)
        max_retries: Retry configuration (default: 3 retries with backoff)

    Returns:
        requests.Session: Configured session

    Example:
        session = create_session()
        response = session.get('https://api.example.com/data')
    """
    session = requests.Session()

    # Mount adapter with timeout
    adapter = TimeoutHTTPAdapter(max_retries=max_retries, timeout=timeout)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session


# Convenience functions with timeout
def get(url, **kwargs):
    """GET request with default timeout"""
    kwargs.setdefault('timeout', DEFAULT_TIMEOUT)
    return requests.get(url, **kwargs)


def post(url, **kwargs):
    """POST request with default timeout"""
    kwargs.setdefault('timeout', DEFAULT_TIMEOUT)
    return requests.post(url, **kwargs)


def put(url, **kwargs):
    """PUT request with default timeout"""
    kwargs.setdefault('timeout', DEFAULT_TIMEOUT)
    return requests.put(url, **kwargs)


def delete(url, **kwargs):
    """DELETE request with default timeout"""
    kwargs.setdefault('timeout', DEFAULT_TIMEOUT)
    return requests.delete(url, **kwargs)
EOF

    echo "  ✅ Created: $UTILS_DIR/http_client.py (secure HTTP helper)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ CI FIX COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Changes made:"
echo "  ✅ Added timeout=30 to requests.get/post/put/delete/patch"
echo "  ✅ Added timeout=30 to urllib.request.urlopen()"
echo "  ✅ Added timeout=30 to socket.create_connection()"
echo "  ✅ Created utils/http_client.py (secure HTTP helper)"
echo ""
echo "Timeout recommendations:"
echo "  • API calls: 30 seconds (default)"
echo "  • File downloads: 300 seconds (5 minutes)"
echo "  • Health checks: 5 seconds"
echo "  • Critical operations: 60 seconds"
echo ""
echo "Next steps:"
echo "  1. Test all HTTP requests still work"
echo "  2. Adjust timeouts based on operation type"
echo "  3. For JavaScript, add timeout manually:"
echo "     • axios: { timeout: 30000 }"
echo "     • fetch: Use AbortController"
echo "  4. Re-run Bandit scanner to verify:"
echo "     python3 ../../1-Security-Assessment/ci-scanners/bandit_scanner.py --target $PROJECT_ROOT"
echo ""
echo "Usage of secure helper:"
echo "  from utils.http_client import create_session"
echo "  session = create_session(timeout=30)"
echo "  response = session.get('https://api.example.com/data')"
echo ""
echo "Backup saved: $BACKUP_DIR"
echo ""

# Generate summary
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 FIX SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Fixer: fix-insecure-requests.sh"
echo "Layer: CI (Code-level)"
echo "Findings: $FINDINGS"
echo "Fixes Applied: $FIXES_APPLIED"
echo "Duration: ${DURATION}s"
echo "Status: Complete"
echo "Report: $REPORT_FILE"
echo ""
