#!/bin/bash
#
# sync_windows_to_wsl.sh - Sync Windows LLM-Training to WSL GP-RAG
#
# Usage: ./sync_windows_to_wsl.sh
#

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Paths
WINDOWS_SOURCE="/mnt/c/Users/jimmi/OneDrive/Desktop/LLM-Training"
WSL_TARGET="/home/jimmie/linkops-industries/GP-copilot/GP-RAG/unprocessed/windows-sync"

echo -e "${BLUE}🔄 Syncing Windows → WSL${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "Source: ${YELLOW}${WINDOWS_SOURCE}${NC}"
echo -e "Target: ${YELLOW}${WSL_TARGET}${NC}"
echo ""

# Check if source exists
if [ ! -d "$WINDOWS_SOURCE" ]; then
    echo -e "${YELLOW}⚠️  Warning: Windows source directory not found!${NC}"
    echo "Expected: $WINDOWS_SOURCE"
    exit 1
fi

# Create target if doesn't exist
mkdir -p "$WSL_TARGET"

# Count files before sync
FILES_BEFORE=$(find "$WSL_TARGET" -type f | wc -l)
echo -e "${BLUE}📁 Files in target before sync: ${FILES_BEFORE}${NC}"

# Sync files (preserving timestamps, only copying new/changed files)
echo -e "\n${BLUE}🔄 Copying files...${NC}"
rsync -av --progress \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.DS_Store' \
    --exclude='Thumbs.db' \
    "$WINDOWS_SOURCE/" "$WSL_TARGET/"

# Count files after sync
FILES_AFTER=$(find "$WSL_TARGET" -type f | wc -l)
FILES_ADDED=$((FILES_AFTER - FILES_BEFORE))

echo ""
echo -e "${GREEN}✅ Sync Complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}📊 Files in target: ${FILES_AFTER}${NC}"
if [ $FILES_ADDED -gt 0 ]; then
    echo -e "${GREEN}📈 Files added/updated: ${FILES_ADDED}${NC}"
else
    echo -e "${BLUE}📊 No new files (already in sync)${NC}"
fi

echo ""
echo -e "${BLUE}💡 Next Steps:${NC}"
echo "   1. Review files: ls -lh '$WSL_TARGET'"
echo "   2. Learn from files: python GP-RAG/simple_learn.py"
echo "   3. Or process manually from windows-sync/"
echo ""
