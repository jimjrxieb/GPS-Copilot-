#!/usr/bin/env python3
"""
Generate PDFs from markdown reports (no LaTeX required)
Uses markdown2 + weasyprint for HTML->PDF conversion
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required tools are installed"""
    try:
        import markdown
        import weasyprint
        return True
    except ImportError:
        print("⚠️  Missing dependencies. Install with:")
        print("")
        print("  pip install markdown weasyprint")
        print("")
        print("Or use pandoc method:")
        print("  ./generate-pdfs.sh")
        print("")
        return False

def markdown_to_html(md_file, html_file):
    """Convert markdown to HTML"""
    try:
        import markdown

        with open(md_file, 'r') as f:
            md_content = f.read()

        # Convert markdown to HTML with extensions
        html_content = markdown.markdown(
            md_content,
            extensions=['tables', 'fenced_code', 'toc']
        )

        # Add CSS styling
        styled_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 5px;
            margin-top: 30px;
        }}
        h3 {{
            color: #7f8c8d;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            padding-left: 20px;
            color: #7f8c8d;
            font-style: italic;
        }}
        .page-break {{
            page-break-after: always;
        }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>
"""

        with open(html_file, 'w') as f:
            f.write(styled_html)

        return True
    except Exception as e:
        print(f"❌ Error converting {md_file}: {e}")
        return False

def html_to_pdf(html_file, pdf_file):
    """Convert HTML to PDF"""
    try:
        from weasyprint import HTML

        HTML(filename=html_file).write_pdf(pdf_file)
        return True
    except Exception as e:
        print(f"❌ Error generating PDF {pdf_file}: {e}")
        return False

def main():
    print("📄 Generating PDF Reports (Python method)...")
    print("═══════════════════════════════════════")
    print("")

    if not check_dependencies():
        return 1

    # Create output directories
    os.makedirs('compliance', exist_ok=True)
    os.makedirs('executive', exist_ok=True)
    os.makedirs('validation', exist_ok=True)

    # Reports to convert
    reports = [
        {
            'md': 'executive/EXECUTIVE-SUMMARY.md',
            'pdf': 'executive/EXECUTIVE-SUMMARY.pdf',
            'name': 'Executive Summary'
        },
        {
            'md': 'executive/ROI-ANALYSIS.md',
            'pdf': 'executive/ROI-ANALYSIS.pdf',
            'name': 'ROI Analysis'
        },
        {
            'md': '../2-findings/reports/SECURITY-AUDIT.md',
            'pdf': 'compliance/SECURITY-AUDIT.pdf',
            'name': 'Security Audit'
        },
        {
            'md': '../2-findings/reports/PCI-DSS-VIOLATIONS.md',
            'pdf': 'compliance/PCI-DSS-COMPLIANCE.pdf',
            'name': 'PCI-DSS Compliance'
        },
        {
            'md': '../5-validators/validation-report.md',
            'pdf': 'validation/VALIDATION-REPORT.pdf',
            'name': 'Validation Report'
        }
    ]

    success_count = 0

    for report in reports:
        md_file = report['md']
        pdf_file = report['pdf']
        name = report['name']

        if not os.path.exists(md_file):
            print(f"⏭️  Skipping {name} (source not found)")
            continue

        print(f"→ Generating {name}...")

        # Convert MD -> HTML -> PDF
        html_file = pdf_file.replace('.pdf', '.html')

        if markdown_to_html(md_file, html_file):
            if html_to_pdf(html_file, pdf_file):
                print(f"✅ {name} → {pdf_file}")
                success_count += 1
                # Clean up HTML
                os.remove(html_file)

    print("")
    print(f"✅ Generated {success_count} PDF reports!")
    print("")
    print("📁 PDFs saved to:")
    print("   ├── executive/EXECUTIVE-SUMMARY.pdf")
    print("   ├── executive/ROI-ANALYSIS.pdf")
    print("   ├── compliance/SECURITY-AUDIT.pdf")
    print("   ├── compliance/PCI-DSS-COMPLIANCE.pdf")
    print("   └── validation/VALIDATION-REPORT.pdf")
    print("")

    return 0

if __name__ == '__main__':
    sys.exit(main())
