#!/bin/bash
set -e

echo "📄 SecOps Phase 6: DOCUMENT - Generating compliance reports..."
echo "═══════════════════════════════════════════════════════════"

# Create output directories
mkdir -p compliance/ executive/

echo ""
echo "→ Generating PCI-DSS compliance report..."
./generate-pci-dss-report.sh

echo ""
echo "→ Generating SOC2 readiness report..."
./generate-soc2-report.sh

echo ""
echo "→ Generating executive summary..."
./generate-executive-summary.sh

echo ""
echo "→ Generating ROI analysis..."
python3 generate-roi-analysis.py

echo ""
echo "✅ All markdown reports generated!"
echo ""

# Offer PDF generation
echo "→ Generate PDF versions? (Y/n)"
read -t 5 -n 1 -r 2>/dev/null || REPLY="y"
echo
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    echo ""
    echo "→ Generating PDFs..."

    # Try Python method first (easier, no LaTeX needed)
    if python3 generate-pdfs-simple.py 2>/dev/null; then
        echo "✅ PDFs generated successfully"
    elif bash generate-pdfs.sh 2>/dev/null; then
        echo "✅ PDFs generated with Pandoc"
    else
        echo "⚠️  PDF generation skipped (optional dependencies missing)"
        echo "   Install: pip install markdown weasyprint"
        echo "   Or: brew install pandoc"
    fi
fi

echo ""
echo "📁 Reports saved to:"
echo "   - Compliance: secops/6-reports/compliance/"
echo "   - Executive: secops/6-reports/executive/"
echo ""
echo "📊 Markdown Reports:"
echo "   - executive/EXECUTIVE-SUMMARY.md"
echo "   - executive/ROI-ANALYSIS.md"
echo "   - ../2-findings/reports/PCI-DSS-VIOLATIONS.md"
echo "   - ../2-findings/reports/SECURITY-AUDIT.md"
echo "   - ../5-validators/validation-report.md"
echo ""
echo "📄 PDF Reports (if generated):"
echo "   - executive/EXECUTIVE-SUMMARY.pdf"
echo "   - executive/ROI-ANALYSIS.pdf"
echo "   - compliance/PCI-DSS-COMPLIANCE.pdf"
echo "   - compliance/SECURITY-AUDIT.pdf"
echo "   - validation/VALIDATION-REPORT.pdf"
