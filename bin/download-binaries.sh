#!/bin/bash
# Download security scanning binaries
# Run this script to get the tools that are too large for git

set -e

BINARIES_DIR="$(dirname "$0")/binaries"
mkdir -p "$BINARIES_DIR"

echo "🔧 Downloading security scanning tools..."

# Gitleaks
if [ ! -f "$BINARIES_DIR/gitleaks" ]; then
    echo "📥 Downloading Gitleaks..."
    wget -qO /tmp/gitleaks.tar.gz https://github.com/gitleaks/gitleaks/releases/download/v8.18.0/gitleaks_8.18.0_linux_x64.tar.gz
    tar -xzf /tmp/gitleaks.tar.gz -C "$BINARIES_DIR" gitleaks
    rm /tmp/gitleaks.tar.gz
    chmod +x "$BINARIES_DIR/gitleaks"
    echo "✅ Gitleaks installed"
else
    echo "✅ Gitleaks already exists"
fi

# TFSec
if [ ! -f "$BINARIES_DIR/tfsec" ]; then
    echo "📥 Downloading TFSec..."
    wget -qO "$BINARIES_DIR/tfsec" https://github.com/aquasecurity/tfsec/releases/download/v1.28.1/tfsec-linux-amd64
    chmod +x "$BINARIES_DIR/tfsec"
    echo "✅ TFSec installed"
else
    echo "✅ TFSec already exists"
fi

# Kubescape
if [ ! -f "$BINARIES_DIR/kubescape" ]; then
    echo "📥 Downloading Kubescape..."
    wget -qO "$BINARIES_DIR/kubescape" https://github.com/kubescape/kubescape/releases/latest/download/kubescape-ubuntu-latest
    chmod +x "$BINARIES_DIR/kubescape"
    echo "✅ Kubescape installed"
else
    echo "✅ Kubescape already exists"
fi

echo ""
echo "✅ All security tools downloaded!"
echo ""
echo "Tools installed in: $BINARIES_DIR"
ls -lh "$BINARIES_DIR"