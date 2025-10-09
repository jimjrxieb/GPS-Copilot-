#!/bin/bash
#
# sync_wsl_to_windows.sh - Sync WSL GP-RAG back to Windows
#
# Usage: ./sync_wsl_to_windows.sh
#

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Paths
WSL_SOURCE="/home/jimmie/linkops-industries/GP-copilot/GP-RAG/unprocessed/windows-sync"
WINDOWS_TARGET="/mnt/c/Users/jimmi/OneDrive/Desktop/LLM-Training"

echo -e "${BLUE}🔄 Syncing WSL → Windows${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "Source: ${YELLOW}${WSL_SOURCE}${NC}"
echo -e "Target: ${YELLOW}${WINDOWS_TARGET}${NC}"
echo ""

# Check if source exists
if [ ! -d "$WSL_SOURCE" ]; then
    echo -e "${RED}❌ Error: WSL source directory not found!${NC}"
    echo "Expected: $WSL_SOURCE"
    exit 1
fi

# Create target if doesn't exist
mkdir -p "$WINDOWS_TARGET"

# Count files before sync
FILES_BEFORE=$(find "$WINDOWS_TARGET" -type f 2>/dev/null | wc -l)
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
    "$WSL_SOURCE/" "$WINDOWS_TARGET/"

# Count files after sync
FILES_AFTER=$(find "$WINDOWS_TARGET" -type f 2>/dev/null | wc -l)
FILES_ADDED=$((FILES_AFTER - FILES_BEFORE))

echo ""
echo -e "${GREEN}✅ Sync Complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}📊 Files in Windows directory: ${FILES_AFTER}${NC}"
if [ $FILES_ADDED -gt 0 ]; then
    echo -e "${GREEN}📈 Files added/updated: ${FILES_ADDED}${NC}"
else
    echo -e "${BLUE}📊 No new files (already in sync)${NC}"
fi

echo ""
echo -e "${BLUE}💡 Files are now accessible from Windows Explorer:${NC}"
echo "   C:\\Users\\jimmi\\OneDrive\\Desktop\\LLM-Training"
echo ""
