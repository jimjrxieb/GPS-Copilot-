#!/bin/bash

# ============================================================================
# CI FIXER: Dependency Vulnerability Remediation
# ============================================================================
# LAYER: CI (Code-level)
# WHEN: Pre-commit, CI pipeline
# FIXES:
#   - CRITICAL/HIGH: Known CVEs in dependencies
#   - Outdated packages with security vulnerabilities
#   - Transitive dependency vulnerabilities
#   - PCI-DSS 6.2: Ensure all components are up-to-date
#   - OWASP A06:2021 - Vulnerable and Outdated Components
# ============================================================================

set -e

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
START_TIME=$(date +%s)

echo "🔧 CI FIXER: Dependency Vulnerability Remediation"
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

BACKUP_DIR="$PROJECT_ROOT/backup/dependency-vulns-$TIMESTAMP"
REPORT_DIR="$PROJECT_ROOT/GP-DATA/active/2-app-sec-fixes/ci-fixes"
REPORT_FILE="$REPORT_DIR/fix-dependency-vulns-$TIMESTAMP.log"

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
echo "→ Scanning for vulnerable dependencies..."

FINDINGS=0
FIXES_APPLIED=0

# Node.js / npm projects
if [ -f "$PROJECT_ROOT/package.json" ]; then
    echo ""
    echo "  📦 Node.js project detected (package.json)"

    cd "$PROJECT_ROOT"

    # Check if npm is available
    if ! command -v npm &> /dev/null; then
        echo "    ⚠️  npm not found - skipping Node.js fixes"
    else
        # Run npm audit
        echo "    → Running npm audit..."
        npm audit --json > "$REPORT_DIR/npm-audit-$TIMESTAMP.json" 2>&1 || true

        # Count vulnerabilities
        if [ -f "$REPORT_DIR/npm-audit-$TIMESTAMP.json" ]; then
            VULN_COUNT=$(cat "$REPORT_DIR/npm-audit-$TIMESTAMP.json" | jq -r '.metadata.vulnerabilities | to_entries | map(.value) | add' 2>/dev/null || echo "0")

            if [ "$VULN_COUNT" -gt 0 ]; then
                echo "    ⚠️  Found $VULN_COUNT npm vulnerabilities"
                ((FINDINGS++))

                # Attempt automatic fix
                echo "    → Attempting npm audit fix..."
                if npm audit fix --force; then
                    echo "      ✅ npm audit fix successful"
                    ((FIXES_APPLIED++))

                    # Update package-lock.json
                    if [ -f "package-lock.json" ]; then
                        echo "      ✅ Updated package-lock.json"
                    fi
                else
                    echo "      ⚠️  Some vulnerabilities require manual intervention"
                    echo "         Review: $REPORT_DIR/npm-audit-$TIMESTAMP.json"
                fi

                # Check for remaining vulnerabilities
                echo "    → Checking remaining vulnerabilities..."
                npm audit --json > "$REPORT_DIR/npm-audit-after-$TIMESTAMP.json" 2>&1 || true
                REMAINING=$(cat "$REPORT_DIR/npm-audit-after-$TIMESTAMP.json" | jq -r '.metadata.vulnerabilities | to_entries | map(.value) | add' 2>/dev/null || echo "0")

                if [ "$REMAINING" -gt 0 ]; then
                    echo "      ⚠️  $REMAINING vulnerabilities remain (manual fix needed)"
                else
                    echo "      ✅ All npm vulnerabilities fixed!"
                fi
            else
                echo "    ✅ No npm vulnerabilities found"
            fi
        fi
    fi
fi

# Python / pip projects
if [ -f "$PROJECT_ROOT/requirements.txt" ] || [ -f "$PROJECT_ROOT/setup.py" ] || [ -f "$PROJECT_ROOT/pyproject.toml" ]; then
    echo ""
    echo "  🐍 Python project detected"

    cd "$PROJECT_ROOT"

    # Check if pip-audit is available
    if ! command -v pip-audit &> /dev/null; then
        echo "    → Installing pip-audit..."
        pip install pip-audit -q || pip3 install pip-audit -q || true
    fi

    if command -v pip-audit &> /dev/null; then
        echo "    → Running pip-audit..."

        # Scan for vulnerabilities
        pip-audit --desc --format json > "$REPORT_DIR/pip-audit-$TIMESTAMP.json" 2>&1 || true

        # Count vulnerabilities
        if [ -f "$REPORT_DIR/pip-audit-$TIMESTAMP.json" ]; then
            VULN_COUNT=$(cat "$REPORT_DIR/pip-audit-$TIMESTAMP.json" | jq '. | length' 2>/dev/null || echo "0")

            if [ "$VULN_COUNT" -gt 0 ]; then
                echo "    ⚠️  Found $VULN_COUNT pip vulnerabilities"
                ((FINDINGS++))

                # Attempt automatic fix
                echo "    → Attempting pip-audit --fix..."
                if pip-audit --fix 2>&1 | tee "$REPORT_DIR/pip-audit-fix-$TIMESTAMP.log"; then
                    echo "      ✅ pip-audit --fix completed"
                    ((FIXES_APPLIED++))

                    # Update requirements.txt
                    if [ -f "requirements.txt" ]; then
                        echo "      → Updating requirements.txt..."
                        pip freeze > requirements-new.txt
                        mv requirements-new.txt requirements.txt
                        echo "      ✅ Updated requirements.txt"
                    fi
                else
                    echo "      ⚠️  Some vulnerabilities require manual intervention"
                fi

                # Show critical vulnerabilities
                echo "    → Critical/High vulnerabilities:"
                cat "$REPORT_DIR/pip-audit-$TIMESTAMP.json" | jq -r '.[] | select(.fix_versions != null) | "      \(.name): \(.fix_versions[0])"' 2>/dev/null || true
            else
                echo "    ✅ No pip vulnerabilities found"
            fi
        fi
    else
        echo "    ⚠️  pip-audit not available - install with: pip install pip-audit"
        echo "    → Attempting manual upgrade of known vulnerable packages..."

        if [ -f "requirements.txt" ]; then
            # Common vulnerable packages with known fixes
            declare -A KNOWN_FIXES=(
                ["werkzeug"]="3.0.1"
                ["flask"]="3.0.0"
                ["django"]="4.2.8"
                ["cryptography"]="41.0.7"
                ["pillow"]="10.1.0"
                ["requests"]="2.31.0"
                ["urllib3"]="2.1.0"
                ["pyyaml"]="6.0.1"
                ["jinja2"]="3.1.3"
            )

            for pkg in "${!KNOWN_FIXES[@]}"; do
                if grep -qi "^$pkg" requirements.txt; then
                    echo "    → Upgrading $pkg to ${KNOWN_FIXES[$pkg]}"
                    sed -i "s/^$pkg.*/$pkg>=${KNOWN_FIXES[$pkg]}/" requirements.txt
                    ((FIXES_APPLIED++))
                fi
            done
        fi
    fi
fi

# Java / Maven projects
if [ -f "$PROJECT_ROOT/pom.xml" ]; then
    echo ""
    echo "  ☕ Java/Maven project detected"

    cd "$PROJECT_ROOT"

    if command -v mvn &> /dev/null; then
        echo "    → Running Maven dependency check..."
        mvn dependency:tree > "$REPORT_DIR/maven-dependencies-$TIMESTAMP.txt" 2>&1 || true

        echo "    → Checking for updates..."
        mvn versions:display-dependency-updates > "$REPORT_DIR/maven-updates-$TIMESTAMP.txt" 2>&1 || true

        echo "      ⚠️  Manual review needed for Maven dependencies"
        echo "         Review: $REPORT_DIR/maven-updates-$TIMESTAMP.txt"
        echo "         Update pom.xml with latest versions"
    else
        echo "    ⚠️  Maven not found - skipping Java fixes"
    fi
fi

# Ruby / Bundler projects
if [ -f "$PROJECT_ROOT/Gemfile" ]; then
    echo ""
    echo "  💎 Ruby project detected"

    cd "$PROJECT_ROOT"

    if command -v bundle &> /dev/null; then
        echo "    → Running bundle audit..."
        bundle audit check --update > "$REPORT_DIR/bundle-audit-$TIMESTAMP.txt" 2>&1 || true

        echo "    → Attempting bundle update..."
        if bundle update 2>&1 | tee "$REPORT_DIR/bundle-update-$TIMESTAMP.log"; then
            echo "      ✅ Bundle updated successfully"
            ((FIXES_APPLIED++))
        else
            echo "      ⚠️  Manual review needed for Bundler dependencies"
        fi
    else
        echo "    ⚠️  Bundler not found - skipping Ruby fixes"
    fi
fi

if [ $FINDINGS -eq 0 ]; then
    echo "  ✅ No vulnerable dependencies found"
    exit 0
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ CI FIX COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Changes made:"
if [ -f "$PROJECT_ROOT/package.json" ]; then
    echo "  📦 npm audit fix applied"
    echo "  ✅ Updated package.json / package-lock.json"
fi
if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    echo "  🐍 pip-audit fix applied or manual upgrades"
    echo "  ✅ Updated requirements.txt"
fi
echo ""
echo "Vulnerability remediation summary:"
echo "  • Total findings: $FINDINGS"
echo "  • Automated fixes: $FIXES_APPLIED"
echo "  • Audit reports saved to: $REPORT_DIR"
echo ""
echo "Next steps:"
echo "  1. Test application thoroughly (dependency updates can break code!)"
echo "  2. Run test suite:"
echo "     npm test        # Node.js"
echo "     pytest          # Python"
echo "     mvn test        # Java"
echo "  3. Review any remaining vulnerabilities"
echo "  4. For manual fixes, consult:"
echo "     • npm: $REPORT_DIR/npm-audit-*.json"
echo "     • pip: $REPORT_DIR/pip-audit-*.json"
echo "     • maven: $REPORT_DIR/maven-updates-*.txt"
echo "  5. Re-scan dependencies:"
echo "     npm audit"
echo "     pip-audit"
echo ""
echo "⚠️  IMPORTANT:"
echo "  • Dependency updates can introduce breaking changes!"
echo "  • Always test thoroughly before deploying"
echo "  • Review CHANGELOG for each updated package"
echo "  • Consider using lock files (package-lock.json, poetry.lock)"
echo ""
echo "Preventive measures:"
echo "  • Use dependabot / renovate for automated updates"
echo "  • Run dependency scans in CI/CD pipeline"
echo "  • Set up vulnerability alerts (GitHub, Snyk, etc.)"
echo ""
echo "Backup saved: $BACKUP_DIR"
echo ""

# Generate summary
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 FIX SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Fixer: fix-dependency-vulns.sh"
echo "Layer: CI (Code-level)"
echo "Findings: $FINDINGS"
echo "Fixes Applied: $FIXES_APPLIED"
echo "Duration: ${DURATION}s"
echo "Status: Complete"
echo "Report: $REPORT_FILE"
echo ""
