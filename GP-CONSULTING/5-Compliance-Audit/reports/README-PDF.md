# PDF Report Generation

Generate professional PDF reports from markdown files for stakeholder distribution.

## 🚀 Quick Start

```bash
# Automatic (tries both methods)
./generate-all-reports.sh

# Manual PDF generation
python3 generate-pdfs-simple.py  # Recommended (easier)
# OR
./generate-pdfs.sh               # Alternative (requires LaTeX)
```

## 📦 Installation

### Method 1: Python (Recommended)

**Easiest** - No LaTeX required:

```bash
pip install markdown weasyprint
```

**macOS additional step:**
```bash
brew install cairo pango gdk-pixbuf libffi
```

**Ubuntu additional step:**
```bash
sudo apt-get install libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0
```

### Method 2: Pandoc

**More powerful** - Requires LaTeX:

```bash
# macOS
brew install pandoc
brew install --cask mactex  # Large download (~4GB)

# Ubuntu
sudo apt-get install pandoc texlive-latex-base texlive-latex-extra
```

## 📄 Generated PDFs

The scripts generate these professional PDFs:

### Executive Reports
- **EXECUTIVE-SUMMARY.pdf** (1 page)
  - High-level overview for C-suite
  - Business impact, compliance status
  - Key metrics and ROI

- **ROI-ANALYSIS.pdf** (2-3 pages)
  - 5-year financial analysis
  - Cost savings breakdown
  - Scale impact calculations

### Compliance Reports
- **PCI-DSS-COMPLIANCE.pdf** (3-5 pages)
  - Violation mapping to PCI-DSS requirements
  - Remediation status
  - Audit readiness checklist

- **SECURITY-AUDIT.pdf** (5-8 pages)
  - Complete security findings
  - Prioritized by severity
  - Remediation recommendations

### Validation Reports
- **VALIDATION-REPORT.pdf** (2-3 pages)
  - Before/after comparison
  - Violation reduction metrics
  - Pass/fail status

## 🎨 PDF Features

✅ **Professional Formatting**
- Clean, modern layout
- Color-coded sections
- Table of contents
- Syntax highlighting for code

✅ **Print-Ready**
- Standard margins (1 inch)
- Readable fonts (11pt)
- Page breaks at sections

✅ **Stakeholder-Friendly**
- Executive summaries
- Visual metrics
- Clear action items

## 🔧 Customization

### Modify Styling (Python method)

Edit `generate-pdfs-simple.py`:

```python
# Change colors
th {{
    background-color: #3498db;  # Change header color
    color: white;
}}

# Change fonts
body {{
    font-family: 'Arial', sans-serif;  # Change font
}}
```

### Modify Styling (Pandoc method)

Edit `generate-pdfs.sh`:

```bash
# Add custom options
pandoc report.md -o report.pdf \
    -V geometry:margin=1in \
    -V fontsize=12pt \          # Larger font
    -V colorlinks=true \        # Colored links
    --toc                       # Add table of contents
```

## 📊 Example Usage

### Generate All PDFs

```bash
cd secops/6-reports
./generate-all-reports.sh
```

### Generate Single PDF

```bash
# Executive summary only
pandoc executive/EXECUTIVE-SUMMARY.md -o executive/EXECUTIVE-SUMMARY.pdf

# With Python
python3 -c "
from generate_pdfs_simple import markdown_to_html, html_to_pdf
markdown_to_html('executive/EXECUTIVE-SUMMARY.md', 'temp.html')
html_to_pdf('temp.html', 'executive/EXECUTIVE-SUMMARY.pdf')
"
```

### Batch Convert Custom Reports

```bash
# Convert all markdown files in a directory
for md in *.md; do
    pandoc "$md" -o "${md%.md}.pdf"
done
```

## 🐛 Troubleshooting

### Error: "weasyprint not found"

```bash
pip install weasyprint

# macOS
brew install cairo pango gdk-pixbuf

# Ubuntu
sudo apt-get install libcairo2 libpango-1.0-0
```

### Error: "pdflatex not found"

```bash
# macOS
brew install --cask mactex

# Ubuntu
sudo apt-get install texlive-latex-base texlive-latex-extra
```

### Error: "Permission denied"

```bash
chmod +x generate-pdfs.sh
chmod +x generate-pdfs-simple.py
```

### PDFs Have Broken Formatting

**Issue:** Tables or code blocks cut off

**Solution 1 (Python):** Reduce font size in CSS
```python
body {{ fontsize: 10pt; }}
```

**Solution 2 (Pandoc):** Adjust margins
```bash
-V geometry:margin=0.75in
```

### No PDFs Generated

The framework works fine **without PDFs** - all reports are available as markdown files:

```bash
# View markdown reports
cat executive/EXECUTIVE-SUMMARY.md
cat executive/ROI-ANALYSIS.md
```

## 💡 Tips

1. **For Email Distribution:** Use PDFs (professional, portable)
2. **For Version Control:** Keep markdown (diff-friendly, git-friendly)
3. **For Presentations:** Export to HTML first, then PDF
4. **For Editing:** Use markdown (easier to modify)

## 📚 Alternative Tools

If you prefer different tools:

### HTML Export (No installation needed)

```bash
# Convert to HTML (viewable in browser)
pandoc report.md -o report.html --standalone --self-contained
```

### Word/DOCX Export

```bash
pandoc report.md -o report.docx
```

### Presentation Slides

```bash
pandoc report.md -o presentation.pdf -t beamer
```

## ✅ Verification

Check if PDFs were generated successfully:

```bash
ls -lh executive/*.pdf compliance/*.pdf validation/*.pdf

# View PDF metadata
pdfinfo executive/EXECUTIVE-SUMMARY.pdf

# Open in viewer
open executive/EXECUTIVE-SUMMARY.pdf  # macOS
xdg-open executive/EXECUTIVE-SUMMARY.pdf  # Linux
```

---

**Note:** PDF generation is **optional**. All reports are available as markdown files which can be viewed, edited, and version-controlled easily.
