#!/bin/bash
#
# GP-Copilot Compliance Framework - Usage Examples
#
# This script demonstrates how to use the compliance framework for all three projects.
# Run individual sections or the entire script for testing.
#
# Author: GP-Copilot / Jade AI
# Date: 2025-10-13

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Base paths
COMPLIANCE_DIR="/home/jimmie/linkops-industries/GP-copilot/GP-CONSULTING/policies/compliance"
SECOPS_DIR="/home/jimmie/linkops-industries/GP-copilot/GP-CONSULTING/secops"
PROJECTS_DIR="/home/jimmie/linkops-industries/GP-copilot/GP-PROJECTS"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}GP-Copilot Compliance Framework${NC}"
echo -e "${BLUE}Usage Examples${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# =============================================================================
# Example 1: Generate PCI-DSS Report for FINANCE Project
# =============================================================================
function example_pci_dss() {
    echo -e "${GREEN}Example 1: PCI-DSS Compliance Report for FINANCE Project${NC}"
    echo ""

    echo -e "${YELLOW}Step 1: Run security scanners on FINANCE project...${NC}"
    if [ -d "$PROJECTS_DIR/FINANCE-project" ]; then
        echo "cd $SECOPS_DIR"
        echo "./run-secops.sh $PROJECTS_DIR/FINANCE-project"
    else
        echo -e "${RED}Warning: FINANCE-project directory not found${NC}"
    fi
    echo ""

    echo -e "${YELLOW}Step 2: Generate PCI-DSS compliance report...${NC}"
    echo "cd $COMPLIANCE_DIR"
    echo "python reports/generators/generate_compliance_report.py --framework pci-dss --project FINANCE"
    echo ""

    echo -e "${YELLOW}Step 3: View the report...${NC}"
    echo "ls -t reports/output/pci-dss/*.md | head -1 | xargs cat"
    echo ""

    echo -e "${GREEN}✅ Report generated at: reports/output/pci-dss/compliance-report-FINANCE-[timestamp].md${NC}"
    echo ""
    echo "---"
    echo ""
}

# =============================================================================
# Example 2: Generate HIPAA Report for HEALTHCARE Project
# =============================================================================
function example_hipaa() {
    echo -e "${GREEN}Example 2: HIPAA Compliance Report for HEALTHCARE Project${NC}"
    echo ""

    echo -e "${YELLOW}Step 1: Run security scanners on HEALTHCARE project...${NC}"
    if [ -d "$PROJECTS_DIR/HEALTHCARE-project" ]; then
        echo "cd $SECOPS_DIR"
        echo "./run-secops.sh $PROJECTS_DIR/HEALTHCARE-project"
    else
        echo -e "${RED}Warning: HEALTHCARE-project directory not found${NC}"
    fi
    echo ""

    echo -e "${YELLOW}Step 2: Generate HIPAA compliance report...${NC}"
    echo "cd $COMPLIANCE_DIR"
    echo "python reports/generators/generate_compliance_report.py --framework hipaa --project HEALTHCARE"
    echo ""

    echo -e "${YELLOW}Step 3: View the report...${NC}"
    echo "ls -t reports/output/hipaa/*.md | head -1 | xargs cat"
    echo ""

    echo -e "${GREEN}✅ Report generated at: reports/output/hipaa/compliance-report-HEALTHCARE-[timestamp].md${NC}"
    echo ""
    echo "---"
    echo ""
}

# =============================================================================
# Example 3: Generate NIST 800-53 Report for DEFENSE Project
# =============================================================================
function example_nist() {
    echo -e "${GREEN}Example 3: NIST 800-53 Compliance Report for DEFENSE Project${NC}"
    echo ""

    echo -e "${YELLOW}Step 1: Run security scanners on DEFENSE project...${NC}"
    if [ -d "$PROJECTS_DIR/DEFENSE-project" ]; then
        echo "cd $SECOPS_DIR"
        echo "./run-secops.sh $PROJECTS_DIR/DEFENSE-project"
    else
        echo -e "${RED}Warning: DEFENSE-project directory not found${NC}"
    fi
    echo ""

    echo -e "${YELLOW}Step 2: Generate NIST 800-53 compliance report...${NC}"
    echo "cd $COMPLIANCE_DIR"
    echo "python reports/generators/generate_compliance_report.py --framework nist-800-53 --project DEFENSE"
    echo ""

    echo -e "${YELLOW}Step 3: View the report...${NC}"
    echo "ls -t reports/output/nist-800-53/*.md | head -1 | xargs cat"
    echo ""

    echo -e "${GREEN}✅ Report generated at: reports/output/nist-800-53/compliance-report-DEFENSE-[timestamp].md${NC}"
    echo ""
    echo "---"
    echo ""
}

# =============================================================================
# Example 4: Generate All Reports at Once
# =============================================================================
function example_all_reports() {
    echo -e "${GREEN}Example 4: Generate All Compliance Reports${NC}"
    echo ""

    echo -e "${YELLOW}This will generate PCI-DSS, HIPAA, and NIST 800-53 reports in one command...${NC}"
    echo ""

    echo "cd $COMPLIANCE_DIR"
    echo "python reports/generators/generate_compliance_report.py --all"
    echo ""

    echo -e "${GREEN}✅ All reports generated:${NC}"
    echo "- reports/output/pci-dss/compliance-report-FINANCE-[timestamp].md"
    echo "- reports/output/hipaa/compliance-report-HEALTHCARE-[timestamp].md"
    echo "- reports/output/nist-800-53/compliance-report-DEFENSE-[timestamp].md"
    echo ""
    echo "---"
    echo ""
}

# =============================================================================
# Example 5: View Universal Control Mappings
# =============================================================================
function example_universal_controls() {
    echo -e "${GREEN}Example 5: View Universal Control Mappings${NC}"
    echo ""

    echo -e "${YELLOW}Universal controls provide cross-framework compliance...${NC}"
    echo ""

    echo "cd $COMPLIANCE_DIR"
    echo "cat mappings/universal-controls.json | jq '.universal_controls[] | {id, name, frameworks}'"
    echo ""

    echo -e "${GREEN}✅ 8 Universal Controls:${NC}"
    echo "UC-001: Database Encryption at Rest"
    echo "UC-002: IAM Wildcard Prevention"
    echo "UC-003: S3 Bucket Encryption"
    echo "UC-004: VPC Security Group Lockdown"
    echo "UC-005: CloudWatch Logging Enabled"
    echo "UC-006: Kubernetes RBAC Enforcement"
    echo "UC-007: Container Image Scanning"
    echo "UC-008: Automated Backup Verification"
    echo ""
    echo "---"
    echo ""
}

# =============================================================================
# Example 6: Complete Compliance Workflow
# =============================================================================
function example_complete_workflow() {
    echo -e "${GREEN}Example 6: Complete Compliance Workflow for FINANCE Project${NC}"
    echo ""

    echo -e "${YELLOW}This demonstrates the full scan → report → fix → verify workflow...${NC}"
    echo ""

    echo -e "${BLUE}Phase 1: Run Security Scans${NC}"
    echo "cd $SECOPS_DIR"
    echo "./run-secops.sh $PROJECTS_DIR/FINANCE-project"
    echo ""

    echo -e "${BLUE}Phase 2: Generate Initial Compliance Report${NC}"
    echo "cd $COMPLIANCE_DIR"
    echo "python reports/generators/generate_compliance_report.py --framework pci-dss --project FINANCE"
    echo ""

    echo -e "${BLUE}Phase 3: Review Non-Compliant Findings${NC}"
    echo "ls -t reports/output/pci-dss/*.md | head -1 | xargs cat"
    echo ""

    echo -e "${BLUE}Phase 4: Auto-Fix Issues${NC}"
    echo "cd $SECOPS_DIR/3-fixers"
    echo "./run-all-fixes.sh"
    echo ""

    echo -e "${BLUE}Phase 5: Re-scan to Verify Fixes${NC}"
    echo "cd $SECOPS_DIR"
    echo "./run-secops.sh $PROJECTS_DIR/FINANCE-project"
    echo ""

    echo -e "${BLUE}Phase 6: Generate Updated Compliance Report${NC}"
    echo "cd $COMPLIANCE_DIR"
    echo "python reports/generators/generate_compliance_report.py --framework pci-dss --project FINANCE"
    echo ""

    echo -e "${GREEN}✅ Compliance workflow complete!${NC}"
    echo ""
    echo "---"
    echo ""
}

# =============================================================================
# Example 7: Framework-Specific Requirements
# =============================================================================
function example_framework_details() {
    echo -e "${GREEN}Example 7: View Framework-Specific Requirements${NC}"
    echo ""

    echo -e "${YELLOW}View PCI-DSS v4.0 requirements...${NC}"
    echo "cd $COMPLIANCE_DIR"
    echo "cat frameworks/pci-dss/pci-dss-v4.json | jq '.requirements[] | {id: .requirement_id, title, priority}'"
    echo ""

    echo -e "${YELLOW}View HIPAA Security Rule requirements...${NC}"
    echo "cat frameworks/hipaa/hipaa-security-rule.json | jq '.requirements[] | {id: .requirement_id, title, implementation_spec}'"
    echo ""

    echo -e "${YELLOW}View NIST 800-53 Rev 5 controls...${NC}"
    echo "cat frameworks/nist-800-53/nist-800-53-rev5.json | jq '.requirements[] | {id: .control_id, title, family, baseline}'"
    echo ""

    echo -e "${GREEN}✅ Framework details displayed${NC}"
    echo ""
    echo "---"
    echo ""
}

# =============================================================================
# Example 8: Integration with CI/CD
# =============================================================================
function example_cicd_integration() {
    echo -e "${GREEN}Example 8: CI/CD Integration${NC}"
    echo ""

    echo -e "${YELLOW}This shows how to integrate compliance reporting into your CI/CD pipeline...${NC}"
    echo ""

    echo -e "${BLUE}GitHub Actions Example:${NC}"
    cat <<'EOF'
name: Compliance Check
on: [push, pull_request]

jobs:
  compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Security Scanners
        run: |
          cd GP-CONSULTING/secops
          ./run-secops.sh .

      - name: Generate PCI-DSS Report
        run: |
          cd GP-CONSULTING/policies/compliance
          python reports/generators/generate_compliance_report.py \
            --framework pci-dss --project FINANCE

      - name: Check Compliance Status
        run: |
          REPORT=$(ls -t GP-CONSULTING/policies/compliance/reports/output/pci-dss/*.md | head -1)
          if grep -q "NON-COMPLIANT" "$REPORT"; then
            echo "::error::PCI-DSS compliance check failed"
            exit 1
          fi

      - name: Upload Compliance Report
        uses: actions/upload-artifact@v3
        with:
          name: compliance-reports
          path: GP-CONSULTING/policies/compliance/reports/output/
EOF
    echo ""

    echo -e "${GREEN}✅ CI/CD integration example shown${NC}"
    echo ""
    echo "---"
    echo ""
}

# =============================================================================
# Main Menu
# =============================================================================
function show_menu() {
    echo -e "${BLUE}Select an example to run:${NC}"
    echo ""
    echo "1) PCI-DSS Report for FINANCE Project"
    echo "2) HIPAA Report for HEALTHCARE Project"
    echo "3) NIST 800-53 Report for DEFENSE Project"
    echo "4) Generate All Reports at Once"
    echo "5) View Universal Control Mappings"
    echo "6) Complete Compliance Workflow (FINANCE)"
    echo "7) View Framework-Specific Requirements"
    echo "8) CI/CD Integration Example"
    echo "9) Show All Examples"
    echo "0) Exit"
    echo ""
    read -p "Enter your choice [0-9]: " choice

    case $choice in
        1) example_pci_dss ;;
        2) example_hipaa ;;
        3) example_nist ;;
        4) example_all_reports ;;
        5) example_universal_controls ;;
        6) example_complete_workflow ;;
        7) example_framework_details ;;
        8) example_cicd_integration ;;
        9)
            example_pci_dss
            example_hipaa
            example_nist
            example_all_reports
            example_universal_controls
            example_complete_workflow
            example_framework_details
            example_cicd_integration
            ;;
        0)
            echo -e "${GREEN}Exiting...${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice. Please try again.${NC}"
            echo ""
            show_menu
            ;;
    esac
}

# =============================================================================
# Script Entry Point
# =============================================================================

# Check if running with --all flag
if [ "$1" == "--all" ]; then
    example_pci_dss
    example_hipaa
    example_nist
    example_all_reports
    example_universal_controls
    example_complete_workflow
    example_framework_details
    example_cicd_integration

    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}All examples displayed!${NC}"
    echo -e "${GREEN}================================${NC}"
    exit 0
fi

# Show interactive menu
while true; do
    show_menu
    echo ""
    read -p "Run another example? (y/n): " continue
    if [ "$continue" != "y" ] && [ "$continue" != "Y" ]; then
        echo -e "${GREEN}Exiting...${NC}"
        break
    fi
    echo ""
done
