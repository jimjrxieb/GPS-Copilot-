#!/bin/bash

# SecOps Framework - Config-Aware Runner
# Reads secops-config.yaml from project and runs SecOps workflow with project-specific settings

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔒 SecOps Framework - Config-Aware Runner${NC}"
echo "═══════════════════════════════════════════════"
echo ""

# Find secops-config.yaml in current directory or parent
CONFIG_FILE=""
if [ -f "secops-config.yaml" ]; then
    CONFIG_FILE="secops-config.yaml"
elif [ -f "../secops-config.yaml" ]; then
    CONFIG_FILE="../secops-config.yaml"
elif [ -f "../../secops-config.yaml" ]; then
    CONFIG_FILE="../../secops-config.yaml"
else
    echo -e "${YELLOW}⚠️  No secops-config.yaml found. Using default settings.${NC}"
    # Fall back to original run-secops.sh
    exec ./run-secops.sh "$@"
fi

echo -e "${GREEN}✓${NC} Found config: $CONFIG_FILE"
echo ""

# Parse YAML config (simple parsing - requires yq for complex configs)
if command -v yq &> /dev/null; then
    PROJECT_NAME=$(yq eval '.project.name' "$CONFIG_FILE" 2>/dev/null || echo "Unknown")
    INDUSTRY=$(yq eval '.project.industry' "$CONFIG_FILE" 2>/dev/null || echo "unknown")
    COMPLIANCE=$(yq eval '.project.compliance_frameworks[]' "$CONFIG_FILE" 2>/dev/null | tr '\n' ',' | sed 's/,$//')

    echo -e "${BLUE}Project:${NC} $PROJECT_NAME"
    echo -e "${BLUE}Industry:${NC} $INDUSTRY"
    echo -e "${BLUE}Compliance:${NC} $COMPLIANCE"
    echo ""
else
    # Fallback: simple grep-based parsing
    PROJECT_NAME=$(grep 'name:' "$CONFIG_FILE" | head -1 | sed 's/.*name: *"\([^"]*\)".*/\1/')
    echo -e "${BLUE}Project:${NC} $PROJECT_NAME"
    echo -e "${YELLOW}⚠️  Install 'yq' for better config parsing: brew install yq${NC}"
    echo ""
fi

# Run the main SecOps workflow
exec ./run-secops.sh "$@"
