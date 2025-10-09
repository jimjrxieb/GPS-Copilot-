#!/bin/bash
set -e

echo "📄 Generating PDF Reports..."
echo "═══════════════════════════════════════"

# Check for pandoc
if ! command -v pandoc >/dev/null 2>&1; then
    echo "⚠️  Pandoc not installed. Installing..."
    echo ""
    echo "Install options:"
    echo "  macOS:   brew install pandoc"
    echo "  Ubuntu:  sudo apt-get install pandoc texlive-latex-base"
    echo "  Manual:  https://pandoc.org/installing.html"
    echo ""
    read -p "Would you like to continue without PDFs? (Y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    echo "✅ Continuing without PDF generation (markdown reports available)"
    exit 0
fi

# Create output directories
mkdir -p compliance/ executive/ validation/

echo ""
echo "→ Generating Executive Summary PDF..."
pandoc executive/EXECUTIVE-SUMMARY.md \
    -o executive/EXECUTIVE-SUMMARY.pdf \
    --pdf-engine=pdflatex \
    -V geometry:margin=1in \
    -V fontsize=11pt \
    --highlight-style=tango \
    2>/dev/null || echo "⚠️  Skipped (requires pdflatex)"

echo "→ Generating ROI Analysis PDF..."
pandoc executive/ROI-ANALYSIS.md \
    -o executive/ROI-ANALYSIS.pdf \
    --pdf-engine=pdflatex \
    -V geometry:margin=1in \
    -V fontsize=11pt \
    --highlight-style=tango \
    2>/dev/null || echo "⚠️  Skipped (requires pdflatex)"

echo "→ Generating PCI-DSS Compliance PDF..."
if [ -f "../2-findings/reports/PCI-DSS-VIOLATIONS.md" ]; then
    pandoc ../2-findings/reports/PCI-DSS-VIOLATIONS.md \
        -o compliance/PCI-DSS-COMPLIANCE.pdf \
        --pdf-engine=pdflatex \
        -V geometry:margin=1in \
        -V fontsize=11pt \
        --highlight-style=tango \
        2>/dev/null || echo "⚠️  Skipped (requires pdflatex)"
fi

echo "→ Generating Security Audit PDF..."
if [ -f "../2-findings/reports/SECURITY-AUDIT.md" ]; then
    pandoc ../2-findings/reports/SECURITY-AUDIT.md \
        -o compliance/SECURITY-AUDIT.pdf \
        --pdf-engine=pdflatex \
        -V geometry:margin=1in \
        -V fontsize=11pt \
        --highlight-style=tango \
        2>/dev/null || echo "⚠️  Skipped (requires pdflatex)"
fi

echo "→ Generating Validation Report PDF..."
if [ -f "../5-validators/validation-report.md" ]; then
    pandoc ../5-validators/validation-report.md \
        -o validation/VALIDATION-REPORT.pdf \
        --pdf-engine=pdflatex \
        -V geometry:margin=1in \
        -V fontsize=11pt \
        --highlight-style=tango \
        2>/dev/null || echo "⚠️  Skipped (requires pdflatex)"
fi

echo ""
echo "✅ PDF generation complete!"
echo ""
echo "📁 PDFs saved to:"
echo "   ├── executive/EXECUTIVE-SUMMARY.pdf"
echo "   ├── executive/ROI-ANALYSIS.pdf"
echo "   ├── compliance/PCI-DSS-COMPLIANCE.pdf"
echo "   ├── compliance/SECURITY-AUDIT.pdf"
echo "   └── validation/VALIDATION-REPORT.pdf"
echo ""
echo "💡 Tip: Open PDFs with:"
echo "   open executive/EXECUTIVE-SUMMARY.pdf (macOS)"
echo "   xdg-open executive/EXECUTIVE-SUMMARY.pdf (Linux)"
