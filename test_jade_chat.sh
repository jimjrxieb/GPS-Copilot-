#!/bin/bash
# Test Jade Chat - Demo for Interview

echo "========================================="
echo "🤖 Jade Chat Test - Interview Demo"
echo "========================================="
echo ""

cd /home/jimmie/linkops-industries/GP-copilot

# Test 1: List projects
echo "Test 1: List Projects"
echo "---------------------"
ls -d GP-PROJECTS/*/
echo ""

# Test 2: Show scan results (if they exist)
echo "Test 2: Check for existing scan results"
echo "---------------------------------------"
if [ -d "GP-DATA/active/scans" ]; then
    ls -lh GP-DATA/active/scans/*_latest.json 2>/dev/null | head -5
    if [ $? -eq 0 ]; then
        echo "✅ Scan results found"
    else
        echo "⚠️  No scan results yet - run a scan first"
    fi
else
    echo "⚠️  Scans directory doesn't exist yet"
fi
echo ""

# Test 3: Verify gp-security script exists
echo "Test 3: Verify gp-security exists"
echo "----------------------------------"
if [ -f "./gp-security" ]; then
    echo "✅ gp-security script found"
    ls -lh ./gp-security
else
    echo "❌ gp-security NOT found"
fi
echo ""

# Test 4: Verify scanners exist
echo "Test 4: Verify scanners exist"
echo "-----------------------------"
SCANNERS=(
    "GP-CONSULTING-AGENTS/scanners/bandit_scanner.py"
    "GP-CONSULTING-AGENTS/scanners/trivy_scanner.py"
    "GP-CONSULTING-AGENTS/scanners/gitleaks_scanner.py"
    "GP-CONSULTING-AGENTS/scanners/semgrep_scanner.py"
)

for scanner in "${SCANNERS[@]}"; do
    if [ -f "$scanner" ]; then
        echo "✅ $scanner"
    else
        echo "❌ $scanner NOT FOUND"
    fi
done
echo ""

# Test 5: Verify fixers exist
echo "Test 5: Verify fixers exist"
echo "---------------------------"
FIXERS=(
    "GP-CONSULTING-AGENTS/fixers/bandit_fixer.py"
    "GP-CONSULTING-AGENTS/fixers/gitleaks_fixer.py"
    "GP-CONSULTING-AGENTS/fixers/trivy_fixer.py"
)

for fixer in "${FIXERS[@]}"; do
    if [ -f "$fixer" ]; then
        echo "✅ $fixer"
    else
        echo "❌ $fixer NOT FOUND"
    fi
done
echo ""

# Test 6: Test jade chat help
echo "Test 6: Jade Chat Help"
echo "----------------------"
echo "help" | timeout 5 python GP-AI/cli/jade_chat.py 2>&1 | grep -A 3 "Security Scans"
echo ""

echo "========================================="
echo "✅ Jade Chat Test Complete"
echo "========================================="
echo ""
echo "To run Jade Chat interactively:"
echo "  python GP-AI/cli/jade_chat.py"
echo ""
echo "Example conversation:"
echo "  You: list projects"
echo "  You: set project GP-PROJECTS/LinkOps-MLOps"
echo "  You: scan my project"
echo "  You: show results"
echo "  You: run fixers"
echo "  You: quit"
echo ""