#!/bin/bash
################################################################################
# GP-CONSULTING Master Orchestration Script
# Purpose: Run complete 6-phase security engagement workflow
# Version: 2.0 (Phase-Based Architecture)
################################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Emojis
CHECK="✅"
WARN="⚠️"
ERROR="❌"
INFO="ℹ️"
ROCKET="🚀"

################################################################################
# Configuration
################################################################################

PROJECT_PATH="${1:-}"
OUTPUT_DIR="${2:-GP-DATA/active}"
SKIP_PHASES="${3:-}"

if [ -z "$PROJECT_PATH" ]; then
    echo -e "${ERROR} ${RED}Usage: $0 /path/to/project [output-dir] [skip-phases]${NC}"
    echo ""
    echo "Examples:"
    echo "  $0 GP-PROJECTS/FINANCE-project"
    echo "  $0 GP-PROJECTS/FINANCE-project custom-output 2,3"
    echo ""
    echo "skip-phases: Comma-separated list of phases to skip (e.g., '2,3')"
    exit 1
fi

if [ ! -d "$PROJECT_PATH" ]; then
    echo -e "${ERROR} ${RED}Project path not found: $PROJECT_PATH${NC}"
    exit 1
fi

PROJECT_NAME=$(basename "$PROJECT_PATH")
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_DIR="$OUTPUT_DIR/reports/$PROJECT_NAME-$TIMESTAMP"

mkdir -p "$REPORT_DIR"

echo -e "${ROCKET} ${BLUE}GP-CONSULTING Security Engagement${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${INFO} Project: ${GREEN}$PROJECT_NAME${NC}"
echo -e "${INFO} Path: $PROJECT_PATH"
echo -e "${INFO} Output: $REPORT_DIR"
echo -e "${INFO} Timestamp: $TIMESTAMP"
echo ""

################################################################################
# Helper Functions
################################################################################

phase_header() {
    local phase=$1
    local title=$2
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${ROCKET} ${GREEN}PHASE $phase: $title${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

step() {
    echo -e "${INFO} $1..."
}

success() {
    echo -e "${CHECK} ${GREEN}$1${NC}"
}

warning() {
    echo -e "${WARN} ${YELLOW}$1${NC}"
}

error() {
    echo -e "${ERROR} ${RED}$1${NC}"
}

should_skip_phase() {
    local phase=$1
    if [[ ",$SKIP_PHASES," == *",$phase,"* ]]; then
        return 0  # true
    fi
    return 1  # false
}

################################################################################
# PHASE 1: Security Assessment
################################################################################

run_phase1() {
    if should_skip_phase 1; then
        warning "Skipping Phase 1 (Security Assessment)"
        return
    fi

    phase_header 1 "Security Assessment"

    local phase1_dir="1-Security-Assessment"
    local findings_dir="$OUTPUT_DIR/findings/raw"
    mkdir -p "$findings_dir/ci" "$findings_dir/cd"

    # CI Scanners
    step "Running CI scanners (Bandit, Semgrep, Gitleaks)"

    cd "$phase1_dir/ci-scanners/"

    # Bandit (Python SAST)
    if python3 bandit_scanner.py "$PROJECT_PATH/backend" --timeout 300 2>&1 | tee "$REPORT_DIR/bandit.log"; then
        success "Bandit scan complete"
    else
        warning "Bandit scan failed (non-zero exit)"
    fi

    # Semgrep (Multi-language SAST)
    if python3 semgrep_scanner.py --target "$PROJECT_PATH" --timeout 300 2>&1 | tee "$REPORT_DIR/semgrep.log"; then
        success "Semgrep scan complete"
    else
        warning "Semgrep scan failed"
    fi

    # Gitleaks (Secrets)
    if python3 gitleaks_scanner.py --target "$PROJECT_PATH" --no-git --timeout 300 2>&1 | tee "$REPORT_DIR/gitleaks.log"; then
        success "Gitleaks scan complete"
    else
        warning "Gitleaks scan failed"
    fi

    cd - > /dev/null

    # CD Scanners (if infrastructure exists)
    if [ -d "$PROJECT_PATH/infrastructure" ]; then
        step "Running CD scanners (Checkov, Trivy)"

        cd "$phase1_dir/cd-scanners/"

        # Checkov (IaC)
        if [ -d "$PROJECT_PATH/infrastructure/terraform" ]; then
            if python3 checkov_scanner.py --target "$PROJECT_PATH/infrastructure/terraform" --timeout 300 2>&1 | tee "$REPORT_DIR/checkov.log"; then
                success "Checkov scan complete"
            else
                warning "Checkov scan failed"
            fi
        fi

        # Trivy (IaC + Containers)
        if python3 trivy_scanner.py --mode config --target "$PROJECT_PATH/infrastructure" --timeout 300 2>&1 | tee "$REPORT_DIR/trivy.log"; then
            success "Trivy scan complete"
        else
            warning "Trivy scan failed"
        fi

        cd - > /dev/null
    else
        warning "No infrastructure/ directory found, skipping CD scanners"
    fi

    # Count findings
    local total_findings=0
    local critical=0
    local high=0

    for json_file in "$findings_dir"/ci/*.json "$findings_dir"/cd/*.json; do
        if [ -f "$json_file" ]; then
            local count=$(jq '.findings | length' "$json_file" 2>/dev/null || echo 0)
            total_findings=$((total_findings + count))

            local crit=$(jq '[.findings[] | select(.severity=="CRITICAL")] | length' "$json_file" 2>/dev/null || echo 0)
            critical=$((critical + crit))

            local hi=$(jq '[.findings[] | select(.severity=="HIGH")] | length' "$json_file" 2>/dev/null || echo 0)
            high=$((high + hi))
        fi
    done

    echo ""
    echo -e "${INFO} ${GREEN}Phase 1 Summary:${NC}"
    echo -e "   Total findings: $total_findings"
    echo -e "   Critical: $critical"
    echo -e "   High: $high"

    # Save baseline
    echo "$total_findings" > "$REPORT_DIR/baseline-total.txt"
    echo "$critical" > "$REPORT_DIR/baseline-critical.txt"
    echo "$high" > "$REPORT_DIR/baseline-high.txt"
}

################################################################################
# PHASE 2: Application Security Fixes
################################################################################

run_phase2() {
    if should_skip_phase 2; then
        warning "Skipping Phase 2 (Application Security Fixes)"
        return
    fi

    phase_header 2 "Application Security Fixes"

    local phase2_dir="2-App-Sec-Fixes"

    step "Applying automated CI-level fixes"

    cd "$phase2_dir/fixers/"

    # Fix hardcoded secrets
    if [ -f "fix-hardcoded-secrets.sh" ]; then
        step "Fixing hardcoded secrets"
        if bash fix-hardcoded-secrets.sh "$PROJECT_PATH" 2>&1 | tee "$REPORT_DIR/fix-secrets.log"; then
            success "Hardcoded secrets fixed"
        else
            warning "Secret fixing encountered issues"
        fi
    fi

    # Fix SQL injection
    if [ -f "fix-sql-injection.sh" ]; then
        step "Fixing SQL injection vulnerabilities"
        if bash fix-sql-injection.sh "$PROJECT_PATH/backend" 2>&1 | tee "$REPORT_DIR/fix-sqli.log"; then
            success "SQL injection vulnerabilities fixed"
        else
            warning "SQL injection fixes encountered issues"
        fi
    fi

    # Fix weak cryptography
    if [ -f "fix-weak-crypto.sh" ]; then
        step "Fixing weak cryptography"
        if bash fix-weak-crypto.sh "$PROJECT_PATH/backend" 2>&1 | tee "$REPORT_DIR/fix-crypto.log"; then
            success "Weak cryptography fixed"
        else
            warning "Cryptography fixes encountered issues"
        fi
    fi

    cd - > /dev/null

    success "Phase 2 complete"
}

################################################################################
# PHASE 3: Infrastructure Hardening
################################################################################

run_phase3() {
    if should_skip_phase 3; then
        warning "Skipping Phase 3 (Infrastructure Hardening)"
        return
    fi

    phase_header 3 "Infrastructure Hardening"

    local phase3_dir="3-Hardening"

    if [ ! -d "$PROJECT_PATH/infrastructure" ]; then
        warning "No infrastructure/ directory found, skipping Phase 3"
        return
    fi

    step "Applying CD-level infrastructure fixes"

    cd "$phase3_dir/fixers/"

    # S3 encryption
    if [ -f "fix-s3-encryption.sh" ] && [ -d "$PROJECT_PATH/infrastructure/terraform" ]; then
        step "Enabling S3 encryption"
        if bash fix-s3-encryption.sh "$PROJECT_PATH/infrastructure/terraform" 2>&1 | tee "$REPORT_DIR/fix-s3.log"; then
            success "S3 encryption enabled"
        else
            warning "S3 fixes encountered issues"
        fi
    fi

    # RDS SSL
    if [ -f "fix-rds-ssl.sh" ] && [ -d "$PROJECT_PATH/infrastructure/terraform" ]; then
        step "Enforcing RDS SSL"
        if bash fix-rds-ssl.sh "$PROJECT_PATH/infrastructure/terraform" 2>&1 | tee "$REPORT_DIR/fix-rds.log"; then
            success "RDS SSL enforced"
        else
            warning "RDS fixes encountered issues"
        fi
    fi

    # Kubernetes security
    if [ -f "fix-kubernetes-security.sh" ] && [ -d "$PROJECT_PATH/infrastructure/k8s" ]; then
        step "Hardening Kubernetes manifests"
        if bash fix-kubernetes-security.sh "$PROJECT_PATH/infrastructure/k8s" 2>&1 | tee "$REPORT_DIR/fix-k8s.log"; then
            success "Kubernetes manifests hardened"
        else
            warning "Kubernetes fixes encountered issues"
        fi
    fi

    cd - > /dev/null

    success "Phase 3 complete"
}

################################################################################
# PHASE 4: Cloud Migration (Optional)
################################################################################

run_phase4() {
    if should_skip_phase 4; then
        warning "Skipping Phase 4 (Cloud Migration)"
        return
    fi

    phase_header 4 "Cloud Migration"

    warning "Phase 4 requires manual configuration (AWS credentials, etc.)"
    warning "See: 4-Cloud-Migration/README.md for detailed instructions"

    # Placeholder for future automation
    success "Phase 4 documentation available"
}

################################################################################
# PHASE 5: Compliance Audit
################################################################################

run_phase5() {
    if should_skip_phase 5; then
        warning "Skipping Phase 5 (Compliance Audit)"
        return
    fi

    phase_header 5 "Compliance Audit & Validation"

    local phase5_dir="5-Compliance-Audit"

    step "Re-scanning after fixes"

    # Re-run Phase 1 scanners
    run_phase1

    step "Comparing before/after results"

    cd "$phase5_dir/validators/"

    if [ -f "compare-results.sh" ]; then
        if bash compare-results.sh \
            --before "$OUTPUT_DIR/findings/baseline" \
            --after "$OUTPUT_DIR/findings/raw" \
            2>&1 | tee "$REPORT_DIR/comparison.log"; then
            success "Results compared"
        else
            warning "Comparison encountered issues"
        fi
    fi

    cd - > /dev/null

    step "Generating compliance reports"

    cd "$phase5_dir/reports/compliance/"

    # PCI-DSS report
    if [ -f "pci-dss-report.py" ]; then
        if python3 pci-dss-report.py --project "$PROJECT_NAME" --output "$REPORT_DIR/pci-dss-report.pdf" 2>&1 | tee "$REPORT_DIR/pci-dss.log"; then
            success "PCI-DSS report generated"
        else
            warning "PCI-DSS report generation failed"
        fi
    fi

    cd - > /dev/null

    success "Phase 5 complete"
}

################################################################################
# PHASE 6: Continuous Automation (Setup)
################################################################################

run_phase6() {
    if should_skip_phase 6; then
        warning "Skipping Phase 6 (Continuous Automation)"
        return
    fi

    phase_header 6 "Continuous Automation Setup"

    local phase6_dir="6-Auto-Agents"

    warning "Phase 6 requires CI/CD pipeline configuration"
    warning "See: 6-Auto-Agents/README.md for setup instructions"

    # Copy CI/CD templates
    step "Preparing CI/CD templates"

    if [ -d "$phase6_dir/cicd-templates/github-actions" ]; then
        mkdir -p "$PROJECT_PATH/.github/workflows"
        cp "$phase6_dir/cicd-templates/github-actions"/*.yml "$PROJECT_PATH/.github/workflows/" 2>/dev/null || true
        success "GitHub Actions templates copied"
    fi

    success "Phase 6 setup complete"
}

################################################################################
# Main Execution
################################################################################

main() {
    local start_time=$(date +%s)

    # Create baseline directory
    mkdir -p "$OUTPUT_DIR/findings/baseline"

    # Run all phases
    run_phase1
    run_phase2
    run_phase3
    run_phase4
    run_phase5
    run_phase6

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    # Final summary
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${ROCKET} ${GREEN}ENGAGEMENT COMPLETE${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${INFO} Duration: ${duration}s"
    echo -e "${INFO} Reports: $REPORT_DIR"
    echo ""

    # Display key metrics
    if [ -f "$REPORT_DIR/baseline-total.txt" ]; then
        local baseline_total=$(cat "$REPORT_DIR/baseline-total.txt")
        local baseline_critical=$(cat "$REPORT_DIR/baseline-critical.txt")
        local baseline_high=$(cat "$REPORT_DIR/baseline-high.txt")

        echo -e "${GREEN}Key Metrics:${NC}"
        echo -e "   Total findings: $baseline_total"
        echo -e "   Critical: $baseline_critical"
        echo -e "   High: $baseline_high"
        echo ""
    fi

    echo -e "${CHECK} ${GREEN}Review reports in: $REPORT_DIR${NC}"
    echo ""
}

# Run main function
main
