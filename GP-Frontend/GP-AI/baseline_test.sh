#!/bin/bash
###############################################################################
# GP-COPILOT Baseline Test (Day 8)
# Tests core functionality end-to-end to identify what works vs broken
###############################################################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           GP-COPILOT BASELINE TEST (Day 8)                   ║"
echo "║          Testing what works vs what's broken                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Results tracking
PASSED=0
FAILED=0
TESTS_RUN=0

test_result() {
    local test_name="$1"
    local result="$2"
    TESTS_RUN=$((TESTS_RUN + 1))

    if [ "$result" = "PASS" ]; then
        echo -e "${GREEN}✅ PASS${NC}: $test_name"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}❌ FAIL${NC}: $test_name"
        FAILED=$((FAILED + 1))
    fi
}

###############################################################################
# Test 1: CLI Commands Exist
###############################################################################

echo -e "\n${YELLOW}[Test 1/8] CLI Commands Exist${NC}"

if [ -f "bin/jade" ] && [ -x "bin/jade" ]; then
    test_result "bin/jade executable" "PASS"
else
    test_result "bin/jade executable" "FAIL"
fi

if [ -f "GP-AI/cli/jade-cli.py" ]; then
    test_result "jade-cli.py exists" "PASS"
else
    test_result "jade-cli.py exists" "FAIL"
fi

###############################################################################
# Test 2: Python Environment
###############################################################################

echo -e "\n${YELLOW}[Test 2/8] Python Environment${NC}"

if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
    test_result "Python 3.10+ available" "PASS"
else
    test_result "Python 3.10+ available" "FAIL"
fi

# Test critical imports
if python3 -c "import chromadb" 2>/dev/null; then
    test_result "chromadb installed" "PASS"
else
    test_result "chromadb installed" "FAIL"
fi

if python3 -c "import networkx" 2>/dev/null; then
    test_result "networkx installed" "PASS"
else
    test_result "networkx installed" "FAIL"
fi

if python3 -c "import langchain" 2>/dev/null; then
    test_result "langchain installed" "PASS"
else
    test_result "langchain installed" "FAIL"
fi

###############################################################################
# Test 3: Directory Structure
###############################################################################

echo -e "\n${YELLOW}[Test 3/8] Directory Structure${NC}"

for dir in GP-AI GP-CONSULTING GP-RAG GP-DATA GP-PLATFORM GP-PROJECTS; do
    if [ -d "$dir" ]; then
        test_result "$dir/ exists" "PASS"
    else
        test_result "$dir/ exists" "FAIL"
    fi
done

###############################################################################
# Test 4: Scanners Available
###############################################################################

echo -e "\n${YELLOW}[Test 4/8] Security Scanners${NC}"

if [ -f "bin/trivy" ] && [ -x "bin/trivy" ]; then
    test_result "trivy binary" "PASS"
else
    test_result "trivy binary" "FAIL"
fi

if [ -f "bin/gitleaks" ] && [ -x "bin/gitleaks" ]; then
    test_result "gitleaks binary" "PASS"
else
    test_result "gitleaks binary" "FAIL"
fi

if python3 -c "import bandit" 2>/dev/null; then
    test_result "bandit installed" "PASS"
else
    test_result "bandit installed" "FAIL"
fi

if python3 -c "import semgrep" 2>/dev/null; then
    test_result "semgrep installed" "PASS"
else
    test_result "semgrep installed" "FAIL"
fi

###############################################################################
# Test 5: Knowledge Graph Files
###############################################################################

echo -e "\n${YELLOW}[Test 5/8] Knowledge Graph${NC}"

if [ -f "GP-AI/core/rag_graph_engine.py" ]; then
    test_result "rag_graph_engine.py exists" "PASS"
else
    test_result "rag_graph_engine.py exists" "FAIL"
fi

if [ -f "GP-AI/core/scan_graph_integrator.py" ]; then
    test_result "scan_graph_integrator.py exists" "PASS"
else
    test_result "scan_graph_integrator.py exists" "FAIL"
fi

# Check if graph has been initialized
if python3 -c "
import sys
sys.path.insert(0, 'GP-AI')
from core.rag_graph_engine import SecurityKnowledgeGraph
graph = SecurityKnowledgeGraph()
print(f'Nodes: {graph.graph.number_of_nodes()}')
sys.exit(0 if graph.graph.number_of_nodes() > 0 else 1)
" 2>/dev/null; then
    test_result "Knowledge graph initialized" "PASS"
else
    test_result "Knowledge graph initialized" "FAIL"
fi

###############################################################################
# Test 6: RAG System
###############################################################################

echo -e "\n${YELLOW}[Test 6/8] RAG System${NC}"

if [ -f "GP-RAG/jade_rag_langgraph.py" ]; then
    test_result "jade_rag_langgraph.py exists" "PASS"
else
    test_result "jade_rag_langgraph.py exists" "FAIL"
fi

if [ -f "GP-RAG/simple_learn.py" ]; then
    test_result "simple_learn.py exists" "PASS"
else
    test_result "simple_learn.py exists" "FAIL"
fi

# Test ChromaDB initialization
if python3 -c "
import sys
sys.path.insert(0, 'GP-DATA')
from simple_rag_query import SimpleRAGQuery
rag = SimpleRAGQuery()
collections = rag.client.list_collections()
print(f'Collections: {len(collections)}')
sys.exit(0 if len(collections) > 0 else 1)
" 2>/dev/null; then
    test_result "ChromaDB has collections" "PASS"
else
    test_result "ChromaDB has collections" "FAIL"
fi

###############################################################################
# Test 7: Jade CLI
###############################################################################

echo -e "\n${YELLOW}[Test 7/8] Jade CLI${NC}"

# Test jade --version
if ./bin/jade --version >/dev/null 2>&1; then
    test_result "jade --version" "PASS"
else
    test_result "jade --version" "FAIL"
fi

# Test jade stats (known issue - not blocking for demo)
export PYTHONPATH=GP-PLATFORM:$PYTHONPATH
if ./bin/jade stats >/dev/null 2>&1; then
    test_result "jade stats" "PASS"
else
    test_result "jade stats (non-critical)" "FAIL"
fi

###############################################################################
# Test 8: Automated Tests
###############################################################################

echo -e "\n${YELLOW}[Test 8/8] Automated Test Suite${NC}"

if [ -f "tests/test_gp_copilot_phase1.py" ]; then
    test_result "test_gp_copilot_phase1.py exists" "PASS"

    # Run pytest
    if pytest tests/test_gp_copilot_phase1.py -v --tb=short 2>&1 | grep -q "passed"; then
        test_result "pytest tests passing" "PASS"
    else
        test_result "pytest tests passing" "FAIL"
    fi
else
    test_result "test_gp_copilot_phase1.py exists" "FAIL"
fi

###############################################################################
# Summary
###############################################################################

echo -e "\n${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    BASELINE TEST RESULTS                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "Tests Run:    ${BLUE}$TESTS_RUN${NC}"
echo -e "Passed:       ${GREEN}$PASSED${NC}"
echo -e "Failed:       ${RED}$FAILED${NC}"
echo -e "Success Rate: ${YELLOW}$(( PASSED * 100 / TESTS_RUN ))%${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 ALL TESTS PASSED - GP-Copilot is ready!${NC}"
    exit 0
else
    echo -e "\n${RED}⚠️  $FAILED tests failed - Review and fix before demo${NC}"
    exit 1
fi
