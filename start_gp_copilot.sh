#!/bin/bash
###############################################################################
# GP-COPILOT with JADE AI - Startup Script
# Launches FastAPI backend + Electron GUI
###############################################################################

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                   GP-COPILOT with JADE AI                    ║"
echo "║              AI-Powered Security Consulting Platform          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

###############################################################################
# 1. Environment Check
###############################################################################

echo -e "${YELLOW}[1/5] Checking environment...${NC}"

if [ ! -d "ai-env" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "Run: python3 -m venv ai-env && source ai-env/bin/activate && pip install -r requirements.txt"
    exit 1
fi

if [ ! -d "GP-GUI/node_modules" ]; then
    echo -e "${YELLOW}⚠️  Node modules not found. Installing...${NC}"
    cd GP-GUI
    npm install
    cd ..
fi

echo -e "${GREEN}✅ Environment OK${NC}"

###############################################################################
# 2. Activate Virtual Environment
###############################################################################

echo -e "${YELLOW}[2/5] Activating virtual environment...${NC}"
source ai-env/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"

###############################################################################
# 3. Verify Secrets
###############################################################################

echo -e "${YELLOW}[3/5] Verifying secrets configuration...${NC}"

python3 -c "
import sys
sys.path.insert(0, 'GP-PLATFORM')
from core.secrets_manager import JadeSecretsManager

sm = JadeSecretsManager()
secrets = ['github_token', 'aws_access_key', 'docker_username']
configured = sum(1 for s in secrets if sm.get_secret(s) is not None)

print(f'✅ Secrets configured: {configured}/{len(secrets)}')
if configured == 0:
    print('⚠️  No secrets configured. Use: python3 GP-PLATFORM/scripts/migrate_secrets.py')
"

###############################################################################
# 4. Start FastAPI Backend
###############################################################################

echo -e "${YELLOW}[4/5] Starting FastAPI backend...${NC}"

# Check if port 8000 is already in use
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}⚠️  Port 8000 already in use. Killing existing process...${NC}"
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Start FastAPI in background
cd GP-AI
export PYTHONPATH="${SCRIPT_DIR}/GP-PLATFORM:${PYTHONPATH}"
nohup uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload > ../logs/fastapi.log 2>&1 &
FASTAPI_PID=$!
cd ..

# Wait for FastAPI to start
echo "Waiting for FastAPI to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ FastAPI backend running on http://localhost:8000${NC}"
        echo -e "${BLUE}   API Docs: http://localhost:8000/docs${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ FastAPI failed to start. Check logs/fastapi.log${NC}"
        kill $FASTAPI_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
done

###############################################################################
# 5. Start Electron GUI
###############################################################################

echo -e "${YELLOW}[5/5] Starting Electron GUI...${NC}"

cd GP-GUI
export JADE_API_URL="http://localhost:8000"

# Start Electron (foreground)
echo -e "${GREEN}✅ Launching Electron GUI...${NC}"
npm start

###############################################################################
# Cleanup on Exit
###############################################################################

echo -e "${YELLOW}Shutting down...${NC}"
kill $FASTAPI_PID 2>/dev/null || true
echo -e "${GREEN}✅ GP-Copilot stopped${NC}"
