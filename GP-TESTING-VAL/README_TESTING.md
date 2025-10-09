# Jade Chat Testing Suite

Comprehensive testing for Jade chat functionality with 60+ automated tests.

## Quick Start

### Run Quick Validation (10 tests, ~30 seconds)
```bash
./GP-TESTING-VAL/quick_jade_test.sh
```

### Run Full Test Suite (60 tests, ~5 minutes)
```bash
python3 GP-TESTING-VAL/jade_chat_tests.py
```

### View Previous Results
```bash
cat GP-TESTING-VAL/jade_chat_test_results.json
```

---

## Test Coverage

### Category 1: Basic Functionality (10 tests)
- ✅ Help command and variants
- ✅ Exit/quit commands
- ✅ Welcome banner display
- ✅ Empty input handling
- ✅ Invalid command messages
- ✅ Case insensitivity
- ✅ Partial command matching
- ✅ Unicode character handling

### Category 2: Scan Results Display (10 tests)
- ✅ Show/view/display results commands
- ✅ Show latest scan
- ✅ Show findings
- ✅ Scanner names display
- ✅ Issue count display
- ✅ Total summary
- ✅ Actionable tips
- ✅ No scans graceful handling

### Category 3: Project Management (8 tests)
- ✅ List/show projects
- ✅ Set/use project commands
- ✅ Project extraction from commands
- ✅ Absolute path handling
- ✅ Relative path handling
- ✅ Project persistence (session)

### Category 4: Scanner Commands (10 tests)
- ✅ Scan my project
- ✅ Quick scan
- ✅ Check/analyze/test/audit variants
- ✅ Scan with advice
- ✅ Scan and fix
- ✅ Natural language: "I want to scan..."
- ✅ Conversational: "Can you scan...?"

### Category 5: Policy/OPA Commands (6 tests)
- ✅ Check/validate/test policy
- ✅ OPA commands
- ✅ Terraform validation
- ✅ Kubernetes policy checks

### Category 6: Fixer Commands (6 tests)
- ✅ Run/apply/execute fixers
- ✅ Fix issues/findings
- ✅ Remediate vulnerabilities

### Category 7: Edge Cases & Advanced (10 tests)
- ✅ Special characters
- ✅ Very long input
- ✅ Multiple words in command
- ✅ Typo tolerance
- ✅ GUI launch command
- ✅ Show stats
- ✅ AI analysis
- ✅ Summarize command
- ✅ Agent commands (conftest, gatekeeper)

---

## Test Examples

### Test 1: Help Command
```python
def test_01_help_command(self):
    """Test help command shows available commands"""
    result = self.run_jade_command("help")
    self.assert_contains(result['stdout'], "Security Scans", "Help shows categories")
```

**Expected Output:**
```
✅ PASS - Found: "Security Scans"
```

### Test 11: Show Results
```python
def test_11_show_results_command(self):
    """Test 'show results' displays scan summary"""
    result = self.run_jade_command("show results")
    self.assert_contains(result['stdout'], "Scan Results", "Shows results header")
```

**Expected Output:**
```
✅ PASS - Found: "Scan Results"
```

### Test 37: Natural Language
```python
def test_37_natural_language_scan(self):
    """Test natural language: 'I want to scan my project'"""
    result = self.run_jade_command("I want to scan my project quickly", timeout=30)
    self.assert_contains(result['success'], True, "Natural language scan works")
```

**Expected Output:**
```
✅ PASS - Natural language scan recognized
```

---

## Test Output Format

### Console Output
```
================================================================================
JADE CHAT COMPREHENSIVE TEST SUITE
================================================================================

Running 60 tests...

[1/60] Test 01 Help Command... ✓
[2/60] Test 02 Help Variant Question... ✓
[3/60] Test 03 Exit Command... ✓
...
[60/60] Test 60 Gatekeeper Agent... ✓

================================================================================
TEST RESULTS SUMMARY
================================================================================

Total Tests:  60
✅ Passed:    57
❌ Failed:    2
⚠️  Errors:    1
ℹ️  Info:      0

Pass Rate:    95.0%

================================================================================
🎉 EXCELLENT: Jade Chat is production-ready!
================================================================================
```

### JSON Output (`jade_chat_test_results.json`)
```json
{
  "timestamp": "2025-10-04 23:30:00",
  "total_tests": 60,
  "passed": 57,
  "failed": 2,
  "errors": 1,
  "results": [
    {
      "test": "test_01_help_command",
      "status": "PASS",
      "message": "Found: \"Security Scans\""
    },
    {
      "test": "test_11_show_results_command",
      "status": "PASS",
      "message": "Found: \"Scan Results\""
    },
    ...
  ]
}
```

---

## Pass Rate Interpretation

| Pass Rate | Status | Meaning |
|-----------|--------|---------|
| ≥ 90% | 🎉 EXCELLENT | Production-ready, all core features working |
| 75-89% | ✅ GOOD | Most functionality works, minor issues |
| 50-74% | ⚠️ FAIR | Core works, needs improvement |
| < 50% | ❌ NEEDS WORK | Major issues detected |

---

## Adding New Tests

### Step 1: Add test method to `jade_chat_tests.py`
```python
def test_XX_your_test_name(self):
    """Test description"""
    result = self.run_jade_command("your command")
    self.assert_contains(result['stdout'], "expected text", "Test name")
```

### Step 2: Run test suite
```bash
python3 GP-TESTING-VAL/jade_chat_tests.py
```

### Step 3: Check results
```bash
cat GP-TESTING-VAL/jade_chat_test_results.json | jq '.results[] | select(.status=="FAIL")'
```

---

## Test Utilities

### Run Specific Test Category
```bash
# Edit jade_chat_tests.py and comment out unwanted test methods
python3 GP-TESTING-VAL/jade_chat_tests.py
```

### Debug Failed Test
```bash
# Run command manually
echo "show results" | python3 GP-AI/cli/jade_chat.py

# Check output
echo "show results" | python3 GP-AI/cli/jade_chat.py 2>&1 | grep -i "scan results"
```

### Timeout Adjustment
For slow tests, increase timeout:
```python
result = self.run_jade_command("scan my project", timeout=60)  # 60 seconds
```

---

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Jade Chat Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Quick Tests
        run: ./GP-TESTING-VAL/quick_jade_test.sh
      - name: Run Full Suite
        run: python3 GP-TESTING-VAL/jade_chat_tests.py
      - name: Upload Results
        uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: GP-TESTING-VAL/jade_chat_test_results.json
```

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running Jade Chat quick tests..."
./GP-TESTING-VAL/quick_jade_test.sh

if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

---

## Troubleshooting

### Test Hangs
- Increase timeout: `timeout=60` in `run_jade_command()`
- Check for interactive prompts in jade_chat.py
- Verify EOF handling in jade_chat.py

### Tests Fail Locally But Pass in CI
- Check environment variables
- Verify file paths (relative vs absolute)
- Check Python version consistency

### High False Positive Rate
- Adjust `assert_contains()` to be more specific
- Use regex matching for flexible assertions
- Check for timing issues (add delays)

---

## Performance Benchmarks

| Test Category | Tests | Avg Time | Total Time |
|---------------|-------|----------|------------|
| Basic Functionality | 10 | 0.5s | 5s |
| Scan Results | 10 | 0.5s | 5s |
| Project Management | 8 | 0.5s | 4s |
| Scanner Commands | 10 | 2.0s | 20s |
| Policy Commands | 6 | 2.0s | 12s |
| Fixer Commands | 6 | 5.0s | 30s |
| Edge Cases | 10 | 1.0s | 10s |

**Total:** 60 tests in ~86 seconds (~1.4s per test)

---

## Known Issues

1. **Interactive prompts block tests** - Tests that trigger "Which project?" prompt will timeout
   - Fix: Provide project in command or set default project

2. **Long-running commands timeout** - Full scans can take > 60 seconds
   - Fix: Use mocked scan results for testing or increase timeout

3. **LLM tests require model** - AI analysis tests need LLM loaded
   - Fix: Skip LLM tests if model not available

---

## Future Enhancements

- [ ] Integration tests with real scan data
- [ ] Performance regression testing
- [ ] Load testing (concurrent requests)
- [ ] Security testing (injection, XSS)
- [ ] Accessibility testing
- [ ] Internationalization testing (i18n)
- [ ] Browser automation (if GUI added)
- [ ] API endpoint testing (if REST API added)

---

**Created:** October 4, 2025
**Version:** 1.0
**Total Tests:** 60