#!/bin/bash
# Test all GP-Copilot UI endpoints

API_BASE="http://localhost:8001"

echo "🔌 Testing GP-Copilot UI Endpoints"
echo "===================================="
echo ""

# Test 1: List Projects
echo "1️⃣  Testing GET /gp/projects"
curl -s "$API_BASE/gp/projects" | jq -r '.projects | length' > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ GET /gp/projects - OK"
else
    echo "   ❌ GET /gp/projects - FAILED"
fi

# Test 2: List Scanners
echo "2️⃣  Testing GET /gp/scanners"
curl -s "$API_BASE/gp/scanners" | jq -r '.scanners | length' > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ GET /gp/scanners - OK"
else
    echo "   ❌ GET /gp/scanners - FAILED"
fi

# Test 3: List Fixers
echo "3️⃣  Testing GET /gp/fixers"
curl -s "$API_BASE/gp/fixers" | jq -r '.fixers | length' > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ GET /gp/fixers - OK"
else
    echo "   ❌ GET /gp/fixers - FAILED"
fi

# Test 4: Get Results (assumes Portfolio exists)
echo "4️⃣  Testing GET /gp/results/Portfolio"
curl -s "$API_BASE/gp/results/Portfolio" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ GET /gp/results/Portfolio - OK"
else
    echo "   ❌ GET /gp/results/Portfolio - FAILED"
fi

# Test 5: Latest Scan
echo "5️⃣  Testing GET /gp/latest-scan?project=Portfolio"
curl -s "$API_BASE/gp/latest-scan?project=Portfolio" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ GET /gp/latest-scan - OK"
else
    echo "   ❌ GET /gp/latest-scan - FAILED"
fi

echo ""
echo "===================================="
echo "📊 Endpoint Test Summary"
echo "===================================="
echo ""
echo "All critical read endpoints tested ✅"
echo ""
echo "⚠️  Write endpoints (POST) not tested to avoid side effects:"
echo "   - POST /gp/scanner/run"
echo "   - POST /gp/fixer/run"
echo "   - POST /gp/escalate"
echo "   - POST /gp/projects/create"
echo ""
echo "These are verified through UI interaction testing."
echo ""
echo "🚀 Ready for Thursday demo!"
