#!/bin/bash
# JADE Unified Startup Script - Start all JADE components

echo "🚀 Starting JADE Security Consultant System"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python package
python_package_exists() {
    python3 -c "import $1" 2>/dev/null
    return $?
}

# Check prerequisites
echo -e "\n${YELLOW}📋 Checking prerequisites...${NC}"

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Python 3 found${NC}"
fi

if ! command_exists npm; then
    echo -e "${YELLOW}⚠️  NPM not found - GUI will not be available${NC}"
    GUI_AVAILABLE=false
else
    echo -e "${GREEN}✅ NPM found${NC}"
    GUI_AVAILABLE=true
fi

# Check Python packages
MISSING_PACKAGES=""
for package in langchain flask transformers sentence_transformers; do
    if ! python_package_exists $package; then
        MISSING_PACKAGES="$MISSING_PACKAGES $package"
    fi
done

if [ ! -z "$MISSING_PACKAGES" ]; then
    echo -e "${YELLOW}⚠️  Missing Python packages:$MISSING_PACKAGES${NC}"
    echo "   Install with: pip install$MISSING_PACKAGES"
fi

# Start JADE components
echo -e "\n${YELLOW}🤖 Starting JADE Components...${NC}"

# 1. Start JADE API Server in background
echo -e "${YELLOW}Starting JADE API Server...${NC}"
python3 jade_unified_launcher.py > jade_api.log 2>&1 &
API_PID=$!
echo -e "${GREEN}✅ JADE API starting (PID: $API_PID)${NC}"

# Give API time to start
sleep 3

# 2. Check if API is running
if curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ JADE API is running at http://localhost:5000${NC}"
else
    echo -e "${YELLOW}⚠️  JADE API may still be starting...${NC}"
fi

# 3. Optionally start GUI
if [ "$GUI_AVAILABLE" = true ] && [ "$1" != "--no-gui" ]; then
    echo -e "\n${YELLOW}Starting GUI...${NC}"
    cd GP-GUI && npm run dev > ../jade_gui.log 2>&1 &
    GUI_PID=$!
    cd ..
    echo -e "${GREEN}✅ GUI starting (PID: $GUI_PID)${NC}"
fi

echo -e "\n${GREEN}=========================================="
echo "🎉 JADE System Started Successfully!"
echo "=========================================="
echo ""
echo "📍 Access Points:"
echo "   • API: http://localhost:5000"
echo "   • Query Endpoint: http://localhost:5000/query"
if [ "$GUI_AVAILABLE" = true ] && [ "$1" != "--no-gui" ]; then
    echo "   • GUI: Check Electron window"
fi
echo ""
echo "🧪 Test JADE's capabilities:"
echo "   python3 jade_quick_demo.py"
echo ""
echo "📝 Example queries you can ask JADE:"
echo '   • "Create a Gatekeeper constraint template that denies root containers"'
echo '   • "How do I secure Terraform state files?"'
echo '   • "Explain Kubernetes admission controllers"'
echo ""
echo "🛑 To stop JADE:"
echo "   kill $API_PID"
if [ "$GUI_AVAILABLE" = true ] && [ "$1" != "--no-gui" ]; then
    echo "   kill $GUI_PID"
fi
echo ""
echo "📋 Logs:"
echo "   • API: tail -f jade_api.log"
if [ "$GUI_AVAILABLE" = true ] && [ "$1" != "--no-gui" ]; then
    echo "   • GUI: tail -f jade_gui.log"
fi
echo -e "=========================================="
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down JADE services...${NC}"
    kill $API_PID 2>/dev/null
    if [ ! -z "$GUI_PID" ]; then
        kill $GUI_PID 2>/dev/null
    fi
    echo -e "${GREEN}✅ JADE services stopped${NC}"
    exit 0
}

# Set up signal handler
trap cleanup SIGINT SIGTERM

# Keep script running
while true; do
    sleep 1
done