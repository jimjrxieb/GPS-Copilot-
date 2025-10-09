#!/bin/bash
set -e

echo "🤖 GP-JADE Environment Setup"
echo "============================"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
echo "Python version: $python_version"
if [[ $(echo "$python_version < 3.10" | bc) -eq 1 ]]; then
    echo "⚠️  Warning: Python 3.10+ recommended, you have $python_version"
fi

# 1. Create virtual environment
if [ ! -d "ai-env" ]; then
    echo ""
    echo "📦 Creating Python virtual environment..."
    python3 -m venv ai-env
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# 2. Activate and install dependencies
echo ""
echo "📥 Installing Python dependencies..."
source ai-env/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install requirements
echo "Installing from requirements.txt (this may take 5-10 minutes)..."
pip install -r requirements.txt

# 3. Download security tool binaries
echo ""
echo "🔧 Downloading security tools..."
if [ -f "GP-TOOLS/download-binaries.sh" ]; then
    cd GP-TOOLS
    bash download-binaries.sh
    cd ..
else
    echo "⚠️  GP-TOOLS/download-binaries.sh not found, skipping binary download"
fi

# 4. Verify bin symlinks
echo ""
echo "🔗 Verifying tool symlinks in bin/..."
ls -lh bin/ | grep -E "(gitleaks|trivy|semgrep|bandit|tfsec)" || echo "⚠️  Some tool symlinks missing"

# 5. Test installations
echo ""
echo "✅ Testing tool installations..."
test_tool() {
    tool=$1
    if command -v "$tool" &> /dev/null || [ -f "bin/$tool" ]; then
        echo "  ✓ $tool"
        return 0
    else
        echo "  ✗ $tool (not found)"
        return 1
    fi
}

test_tool "bin/gitleaks"
test_tool "bin/trivy"
test_tool "bin/semgrep"
test_tool "bin/bandit"
test_tool "bin/tfsec"
test_tool "bin/checkov"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Environment setup complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "1. Activate environment:     source ai-env/bin/activate"
echo "2. Download Qwen models:     bash setup-models.sh"
echo "3. Ingest knowledge base:    cd GP-RAG && python3 tools/ingest.py --stats"
echo "4. Test Jade:                python3 -c 'from GP_AI.jade_enhanced import JadeEnhanced; jade = JadeEnhanced()'"
echo ""
echo "Or use the unified CLI:"
echo "  bin/jade stats             # Show system statistics"
echo "  bin/jade query 'question'  # Query knowledge base"
echo "  bin/jade analyze PROJECT   # Run security analysis"
echo ""