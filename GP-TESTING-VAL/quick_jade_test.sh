#!/bin/bash
# Quick Jade Chat Test - Run subset of tests for fast validation

echo "🧪 Quick Jade Chat Validation (10 critical tests)"
echo "=================================================="
echo ""

JADE_CHAT="GP-AI/cli/jade_chat.py"
PASSED=0
FAILED=0

run_test() {
    local name="$1"
    local command="$2"
    local expected="$3"

    echo -n "Testing: $name... "

    output=$(echo "$command" | timeout 5 python3 $JADE_CHAT 2>&1)

    if echo "$output" | grep -qi "$expected"; then
        echo "✅ PASS"
        ((PASSED++))
    else
        echo "❌ FAIL (expected: $expected)"
        ((FAILED++))
    fi
}

# Critical Tests
run_test "Help command" "help" "Available Commands"
run_test "Exit gracefully" "exit" "Goodbye"
run_test "Show results" "show results" "Scan Results"
run_test "List projects" "list projects" "GP-PROJECTS"
run_test "Invalid command" "xyz123" "not sure"
run_test "Case insensitive" "HELP" "Available Commands"
run_test "Natural language" "I want to scan my project" "scan"
run_test "Show latest" "show latest scan" "Scan Results"
run_test "View results variant" "view results" "Scan Results"
run_test "Display results variant" "display results" "Scan Results"

echo ""
echo "=================================================="
echo "Quick Test Results: $PASSED passed, $FAILED failed"
echo "=================================================="

if [ $FAILED -eq 0 ]; then
    echo "🎉 All critical tests passed!"
    exit 0
else
    echo "⚠️  Some tests failed. Run full suite for details:"
    echo "   python3 GP-TESTING-VAL/jade_chat_tests.py"
    exit 1
fi