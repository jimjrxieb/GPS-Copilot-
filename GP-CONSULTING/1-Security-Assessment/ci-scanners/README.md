# CI Scanners - Code Analysis Tools

**Purpose:** Scan application source code for security vulnerabilities and code quality issues

**When to use:** During CI (Continuous Integration) pipeline before merging code

---

## 🎯 Overview

CI scanners analyze source code to detect:
- **Security Vulnerabilities** (SQL injection, XSS, hardcoded secrets)
- **Code Quality Issues** (style violations, unused variables, complexity)
- **Best Practice Violations** (insecure APIs, weak crypto)

All scanners output JSON to `GP-DATA/active/1-sec-assessment/ci-findings/` for Phase 2 remediation.

---

## 📁 Available Scanners

### Security Scanners

| Scanner | Language | Detects | Severity |
|---------|----------|---------|----------|
| [bandit_scanner.py](bandit_scanner.py) | Python | Security issues, weak crypto, SQL injection | HIGH/MEDIUM/LOW |
| [semgrep_scanner.py](semgrep_scanner.py) | Multi-language | Injection flaws, XSS, insecure patterns | CRITICAL/HIGH/MEDIUM |
| [gitleaks_scanner.py](gitleaks_scanner.py) | All | Hardcoded secrets, API keys, passwords | CRITICAL |

### Code Quality (Linters)

| Scanner | Language | Detects | Auto-fixable |
|---------|----------|---------|--------------|
| [eslint_scanner.py](eslint_scanner.py) | JavaScript/TypeScript | Style violations, unused vars, best practices | ✅ Yes |
| [pylint_scanner.py](pylint_scanner.py) | Python | PEP 8 violations, code smells, complexity | ✅ Yes |

---

## 🔒 Security Scanners

### 1. Bandit Scanner (Python Security)

**File:** [bandit_scanner.py](bandit_scanner.py)

**Detects:**
- B105: Hardcoded passwords
- B113: Requests without timeout
- B201-B202: Flask debug mode
- B301-B302: Pickle usage (insecure)
- B303: MD5/SHA1 usage (weak crypto)
- B501: Weak SSL/TLS config
- B608: SQL injection (raw SQL)

**Usage:**
```bash
python3 bandit_scanner.py --target /path/to/project

# Output: GP-DATA/active/1-sec-assessment/ci-findings/bandit_TIMESTAMP.json
```

**Example Output:**
```json
{
  "summary": {
    "total_issues": 15,
    "HIGH": 3,
    "MEDIUM": 8,
    "LOW": 4
  },
  "findings": [
    {
      "file": "backend/auth.py",
      "line": 42,
      "severity": "HIGH",
      "test_id": "B105",
      "issue_text": "Hardcoded password string"
    }
  ]
}
```

---

### 2. Semgrep Scanner (Multi-language SAST)

**File:** [semgrep_scanner.py](semgrep_scanner.py)

**Languages:** Python, JavaScript, Java, Go, Ruby, PHP, TypeScript

**Detects:**
- SQL injection
- Command injection
- XSS (Cross-site scripting)
- Path traversal
- Insecure deserialization
- SSRF (Server-side request forgery)

**Rulesets:**
- `p/security-audit` - OWASP Top 10
- `p/owasp-top-ten` - OWASP security rules
- `p/cwe-top-25` - CWE/SANS Top 25

**Usage:**
```bash
python3 semgrep_scanner.py --target /path/to/project

# Output: GP-DATA/active/1-sec-assessment/ci-findings/semgrep_TIMESTAMP.json
```

---

### 3. Gitleaks Scanner (Secrets Detection)

**File:** [gitleaks_scanner.py](gitleaks_scanner.py)

**Detects:**
- AWS access keys (`AKIA...`)
- GitHub tokens (`ghp_...`)
- Slack tokens
- Private keys (RSA, SSH)
- Database connection strings
- Generic API keys (20+ chars)

**Usage:**
```bash
python3 gitleaks_scanner.py --target /path/to/project

# Output: GP-DATA/active/1-sec-assessment/ci-findings/gitleaks_TIMESTAMP.json
```

**Important:** Gitleaks scans git history, not just current files. Secrets in old commits will be detected.

---

## 🎨 Code Quality Scanners (Linters)

### 4. ESLint Scanner (JavaScript/TypeScript)

**File:** [eslint_scanner.py](eslint_scanner.py)

**Detects:**
- Unused variables/imports
- Missing semicolons
- Inconsistent quotes
- `var` usage (prefer `const`/`let`)
- Code complexity violations
- Best practice violations
- Security issues (`eval()`, `new Function()`)

**Auto-fixable:** 70-90% of issues (see Phase 2 fixer)

**Usage:**
```bash
python3 eslint_scanner.py --target /path/to/project

# Output: GP-DATA/active/1-sec-assessment/ci-findings/eslint_TIMESTAMP.json
```

**Example Output:**
```json
{
  "summary": {
    "total_issues": 127,
    "errors": 12,
    "warnings": 115
  },
  "findings": [
    {
      "file": "frontend/src/App.js",
      "line": 15,
      "severity": "WARNING",
      "rule_id": "no-unused-vars",
      "message": "'userId' is assigned a value but never used"
    }
  ]
}
```

---

### 5. Pylint Scanner (Python Code Quality)

**File:** [pylint_scanner.py](pylint_scanner.py)

**Detects:**
- PEP 8 violations (formatting)
- Unused imports/variables
- Code complexity (too many branches)
- Missing docstrings
- Potential bugs (undefined variables)
- Code smells (duplicate code)

**Auto-fixable:** 50-70% of issues (see Phase 2 fixer)

**Usage:**
```bash
python3 pylint_scanner.py --target /path/to/project

# Output: GP-DATA/active/1-sec-assessment/ci-findings/pylint_TIMESTAMP.json
```

**Example Output:**
```json
{
  "summary": {
    "total_issues": 89,
    "errors": 5,
    "warnings": 23,
    "refactor": 31,
    "convention": 30
  },
  "findings": [
    {
      "file": "backend/utils.py",
      "line": 42,
      "severity": "WARNING",
      "rule_id": "W0612",
      "rule_name": "unused-variable",
      "message": "Unused variable 'temp'"
    }
  ]
}
```

---

## 🔄 Complete Workflow

### Step 1: Run All Scanners

```bash
cd /home/jimmie/linkops-industries/GP-copilot/GP-CONSULTING/1-Security-Assessment/ci-scanners/

# Security scanners
python3 bandit_scanner.py --target /path/to/project
python3 semgrep_scanner.py --target /path/to/project
python3 gitleaks_scanner.py --target /path/to/project

# Code quality scanners
python3 eslint_scanner.py --target /path/to/project
python3 pylint_scanner.py --target /path/to/project
```

### Step 2: Review Results

```bash
# View all findings
ls -lh ~/linkops-industries/GP-copilot/GP-DATA/active/1-sec-assessment/ci-findings/

# Summary of critical issues
cat GP-DATA/active/1-sec-assessment/ci-findings/bandit_*.json | jq '.summary'
cat GP-DATA/active/1-sec-assessment/ci-findings/gitleaks_*.json | jq '.findings | length'

# Linting issues
cat GP-DATA/active/1-sec-assessment/ci-findings/eslint_*.json | jq '.summary'
cat GP-DATA/active/1-sec-assessment/ci-findings/pylint_*.json | jq '.summary'
```

### Step 3: Prioritize Fixes

**Priority Order:**
1. 🔴 **CRITICAL** - Secrets (Gitleaks), RCE (Semgrep)
2. 🔴 **HIGH** - SQL injection (Bandit), XSS (Semgrep)
3. 🟠 **MEDIUM** - Weak crypto (Bandit), code quality (Pylint/ESLint errors)
4. 🟡 **LOW** - Style violations (Pylint/ESLint warnings)

### Step 4: Fix Issues (Phase 2)

```bash
cd ../../2-App-Sec-Fixes/fixers/

# Security fixes
./fix-hardcoded-secrets.sh /path/to/project
./fix-sql-injection.sh /path/to/project

# Code quality fixes (auto-fixable)
./fix-eslint-issues.sh /path/to/project
./fix-pylint-issues.sh /path/to/project
```

### Step 5: Validate Fixes

Re-run scanners to verify issues are resolved:

```bash
cd ../../1-Security-Assessment/ci-scanners/

# Re-scan
python3 bandit_scanner.py --target /path/to/project
python3 eslint_scanner.py --target /path/to/project
python3 pylint_scanner.py --target /path/to/project

# Compare before/after
diff GP-DATA/active/1-sec-assessment/ci-findings/bandit_BEFORE.json \
     GP-DATA/active/1-sec-assessment/ci-findings/bandit_AFTER.json
```

---

## 🔗 Integration with Other Phases

### → Phase 2: App-Sec-Fixes

Security findings are remediated in Phase 2:
- [fix-hardcoded-secrets.sh](../../2-App-Sec-Fixes/fixers/fix-hardcoded-secrets.sh)
- [fix-sql-injection.sh](../../2-App-Sec-Fixes/fixers/fix-sql-injection.sh)

Linting findings are auto-fixed in Phase 2:
- [fix-eslint-issues.sh](../../2-App-Sec-Fixes/fixers/fix-eslint-issues.sh)
- [fix-pylint-issues.sh](../../2-App-Sec-Fixes/fixers/fix-pylint-issues.sh)

### → Phase 5: Compliance-Audit

Scan results are tracked for compliance:
```bash
cd ../../5-Compliance-Audit/validators/
./generate-compliance-report.sh --framework pci-dss --phase 1
```

---

## 📊 Metrics

### Security Issue Density
```
Issues per 1000 lines of code (KLOC)
```

### Linting Coverage
```
Files scanned / Total files × 100
```

### Fix Rate
```
Issues fixed / Total issues × 100
```

---

## 🛠️ Troubleshooting

### Scanner Not Found

**Problem:** `bandit: command not found`

**Solution:**
```bash
pip install bandit semgrep pylint autopep8 autoflake
npm install -g eslint
```

### False Positives

**Bandit:**
```python
password = "test123"  # nosec B105 - Test fixture only
```

**ESLint:**
```javascript
/* eslint-disable no-console */
console.log('Debug info');
/* eslint-enable no-console */
```

**Pylint:**
```python
# pylint: disable=unused-variable
temp = calculate_something()
```

---

## 📖 Additional Resources

- **Bandit:** https://bandit.readthedocs.io/
- **Semgrep:** https://semgrep.dev/docs/
- **Gitleaks:** https://github.com/gitleaks/gitleaks
- **ESLint:** https://eslint.org/docs/
- **Pylint:** https://pylint.readthedocs.io/

---

**Phase 1 CI Scanners Version:** 2.0
**Last Updated:** 2025-10-15
**Scanners:** 5 (3 security + 2 linting)
**Status:** ✅ Production-Ready
